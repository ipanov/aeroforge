"""Bridge: Generate FreeCAD Python code from Build123d airfoil profiles.

This module does NOT run inside FreeCAD. It generates Python code strings
that will be executed inside FreeCAD via the MCP `execute_code` tool.

The workflow:
1. Build123d generates exact NURBS airfoil profiles (AG24/AG09/AG03 blended)
2. This module converts them to FreeCAD Python code
3. The code is sent to FreeCAD via MCP execute_code
4. FreeCAD creates the 3D geometry visually

Convention: X=chordwise (LE=0), Z=up (thickness), Y=spanwise
(FreeCAD convention differs from Build123d)
"""

from __future__ import annotations

import numpy as np

from src.cad.airfoils import (
    airfoil_at_station,
    scale_airfoil,
    get_airfoil,
    resample_airfoil,
)
from src.core.specs import SAILPLANE, WingSpec


def _airfoil_coords_at_station(
    span_fraction: float,
    wing: WingSpec | None = None,
    n_points: int = 60,
) -> tuple[np.ndarray, float, float]:
    """Get scaled airfoil coordinates at a span station.

    Returns:
        (coords, chord, twist) where coords is Nx2 array of (x, z) in mm.
    """
    wing = wing or SAILPLANE.wing
    airfoil = airfoil_at_station(
        span_fraction,
        root_airfoil=wing.airfoil_root,
        mid_airfoil=wing.airfoil_mid,
        tip_airfoil=wing.airfoil_tip,
        n_points=n_points,
    )
    chord = wing.chord_at(span_fraction)
    twist = wing.washout_at(span_fraction)
    scaled = scale_airfoil(airfoil, chord, twist_deg=twist)
    return scaled, chord, twist


def generate_airfoil_wire_code(
    span_fraction: float,
    y_position: float,
    wire_name: str = "AirfoilWire",
    wing: WingSpec | None = None,
) -> str:
    """Generate FreeCAD Python code to create an airfoil BSpline wire.

    The wire is placed at Y=y_position (spanwise), in the XZ plane.
    X = chordwise, Z = thickness direction.

    Args:
        span_fraction: 0.0 (root) to 1.0 (tip)
        y_position: Spanwise position in mm
        wire_name: Name for the FreeCAD wire object
        wing: Wing spec (defaults to SAILPLANE)

    Returns:
        Python code string to execute in FreeCAD.
    """
    coords, chord, twist = _airfoil_coords_at_station(span_fraction, wing)

    # Close the profile if not already closed
    if np.linalg.norm(coords[0] - coords[-1]) > 0.1:
        coords = np.vstack([coords, coords[0:1]])

    # Format points as FreeCAD Vectors (X=chord, Y=span, Z=thickness)
    points_str = ",\n        ".join(
        f"FreeCAD.Vector({x:.4f}, {y_position:.4f}, {z:.4f})"
        for x, z in coords
    )

    code = f"""
import FreeCAD
import Part

# Airfoil at {span_fraction*100:.0f}% span, chord={chord:.1f}mm, twist={twist:.2f}deg
points = [
        {points_str}
]

# Create BSpline through points
bspline = Part.BSplineCurve()
bspline.interpolate(points, PeriodicFlag=True)
wire = bspline.toShape()

# Add to document
doc = FreeCAD.ActiveDocument
if doc is None:
    doc = FreeCAD.newDocument("AeroForge")

obj = doc.addObject("Part::Feature", "{wire_name}")
obj.Shape = wire
obj.Label = "{wire_name} (span={span_fraction*100:.0f}%, chord={chord:.0f}mm)"
doc.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()
"""
    return code


def generate_wing_panel_code(
    panel_index: int = 0,
    n_sections: int = 5,
    wing: WingSpec | None = None,
) -> str:
    """Generate FreeCAD Python code to create a wing panel as a lofted solid.

    Creates airfoil wires at n_sections along the panel span,
    then lofts between them to create the outer aerodynamic surface.

    Args:
        panel_index: 0 (root) to 4 (tip) per half-wing
        n_sections: Number of airfoil sections for lofting
        wing: Wing spec

    Returns:
        Python code string to execute in FreeCAD.
    """
    wing = wing or SAILPLANE.wing
    panel_span = wing.panel_span  # 256mm
    half_span = wing.half_span
    root_y = panel_index * panel_span

    # Generate all section data
    sections = []
    for i in range(n_sections):
        y_local = i * panel_span / (n_sections - 1)
        y_global = root_y + y_local
        span_frac = y_global / half_span

        coords, chord, twist = _airfoil_coords_at_station(span_frac, wing)

        # Close profile
        if np.linalg.norm(coords[0] - coords[-1]) > 0.1:
            coords = np.vstack([coords, coords[0:1]])

        sections.append({
            'y': y_local,
            'span_frac': span_frac,
            'chord': chord,
            'twist': twist,
            'coords': coords,
        })

    # Build the code
    code_parts = [f"""
import FreeCAD
import Part
import FreeCADGui

doc = FreeCAD.ActiveDocument
if doc is None:
    doc = FreeCAD.newDocument("AeroForge")

# ════════════════════════════════════════════
# Wing Panel {panel_index} (span {root_y:.0f}-{root_y + panel_span:.0f}mm)
# ════════════════════════════════════════════

wires = []
"""]

    for i, sec in enumerate(sections):
        points_str = ",\n            ".join(
            f"FreeCAD.Vector({x:.4f}, {sec['y']:.4f}, {z:.4f})"
            for x, z in sec['coords']
        )

        code_parts.append(f"""
# Section {i}: {sec['span_frac']*100:.0f}% span, chord={sec['chord']:.1f}mm
points_{i} = [
            {points_str}
]
bsp_{i} = Part.BSplineCurve()
bsp_{i}.interpolate(points_{i}, PeriodicFlag=True)
wire_{i} = bsp_{i}.toShape()
wires.append(Part.Wire([wire_{i}]))
""")

    code_parts.append(f"""
# Loft between sections to create outer surface
print(f"Lofting {{len(wires)}} sections...")
loft_shape = Part.makeLoft(wires, True, False, False)

panel = doc.addObject("Part::Feature", "WingPanel_{panel_index}")
panel.Shape = loft_shape
panel.Label = "Wing Panel {panel_index} (outer surface)"

# Set visual properties
panel.ViewObject.ShapeColor = (0.85, 0.85, 0.95)  # Light blue
panel.ViewObject.Transparency = 30

doc.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()
print(f"Panel {panel_index}: vol={{loft_shape.Volume:.0f}}mm³, area={{loft_shape.Area:.0f}}mm²")
""")

    return "\n".join(code_parts)


def generate_spar_tunnel_code(
    panel_index: int = 0,
    wing: WingSpec | None = None,
) -> str:
    """Generate FreeCAD code to create the carbon spar tunnel through a panel.

    The spar tunnel is a cylinder at the correct chord position,
    running the full length of the panel.
    """
    wing = wing or SAILPLANE.wing
    spar = SAILPLANE.spar
    panel_span = wing.panel_span
    half_span = wing.half_span
    root_y = panel_index * panel_span

    # Spar position at panel root
    root_frac = root_y / half_span
    root_chord = wing.chord_at(root_frac)
    spar_x = root_chord * spar.main_position_chord_fraction

    # Get spar Y (vertical center in airfoil)
    coords, _, _ = _airfoil_coords_at_station(root_frac, wing)
    le_idx = int(np.argmin(coords[:, 0]))
    upper = coords[:le_idx + 1][np.argsort(coords[:le_idx + 1, 0])]
    lower = coords[le_idx:][np.argsort(coords[le_idx:, 0])]
    y_up = float(np.interp(spar_x, upper[:, 0], upper[:, 1]))
    y_lo = float(np.interp(spar_x, lower[:, 0], lower[:, 1]))
    spar_z = (y_up + y_lo) / 2

    code = f"""
import FreeCAD
import Part

doc = FreeCAD.ActiveDocument

# Carbon spar tunnel - 8mm OD tube at {spar.main_position_chord_fraction*100:.0f}% chord
spar_radius = {spar.main_od / 2 + 0.1:.1f}  # 0.1mm clearance
spar_x = {spar_x:.2f}  # chordwise position
spar_z = {spar_z:.2f}  # vertical center in airfoil

# Create cylinder along Y axis (spanwise)
spar_tunnel = Part.makeCylinder(
    spar_radius,
    {panel_span + 2:.1f},  # slightly longer than panel
    FreeCAD.Vector(spar_x, -1, spar_z),  # start slightly before panel
    FreeCAD.Vector(0, 1, 0)  # direction = Y axis (spanwise)
)

obj = doc.addObject("Part::Feature", "SparTunnel_{panel_index}")
obj.Shape = spar_tunnel
obj.Label = "Spar Tunnel P{panel_index} ({spar.main_od}mm)"
obj.ViewObject.ShapeColor = (0.2, 0.2, 0.2)  # Dark gray
obj.ViewObject.Transparency = 50

doc.recompute()
print(f"Spar tunnel at x={{spar_x:.1f}}, z={{spar_z:.1f}}, r={{spar_radius:.1f}}mm")
"""
    return code


def generate_all_panels_code(wing: WingSpec | None = None) -> list[str]:
    """Generate FreeCAD code for all 5 panels of one half-wing.

    Returns list of code strings, one per panel.
    """
    wing = wing or SAILPLANE.wing
    codes = []
    for i in range(wing.panels_per_half):
        panel_code = generate_wing_panel_code(i, wing=wing)
        spar_code = generate_spar_tunnel_code(i, wing=wing)
        codes.append(panel_code + "\n" + spar_code)
    return codes


if __name__ == "__main__":
    """Generate and print the FreeCAD code for panel 0 (for testing)."""
    code = generate_wing_panel_code(0)
    print("=" * 60)
    print("FreeCAD code for Wing Panel 0:")
    print("=" * 60)
    print(code)
    print()
    print("=" * 60)
    print("Spar tunnel code:")
    print("=" * 60)
    print(generate_spar_tunnel_code(0))
