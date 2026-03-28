"""FreeCAD code generator for empennage (tail surfaces).

Creates:
- Horizontal stabilizer (450mm span, 95mm chord, NACA0009)
- Vertical stabilizer (140mm height, 110→60mm chord taper, NACA0009)
- Elevator hinge line (33% chord)
- Rudder hinge line (35% chord)

Positioned at end of boom (250mm pod + 650mm boom = 900mm from nose).
"""

from __future__ import annotations

import math
import numpy as np

from src.cad.airfoils import naca_4digit, scale_airfoil
from src.core.specs import SAILPLANE


def _naca0009_coords(chord: float, n_points: int = 40) -> np.ndarray:
    """Get NACA 0009 coordinates scaled to chord."""
    coords = naca_4digit(0, 0, 9, n_points)
    return coords * chord


def generate_hstab_code() -> str:
    """Generate FreeCAD code for horizontal stabilizer."""
    emp = SAILPLANE.empennage
    boom_end_x = 250 + SAILPLANE.spar.boom_length  # 900mm from nose

    # H-stab: symmetric, constant chord, NACA 0009
    half_span = emp.h_stab_span / 2  # 225mm per side
    chord = emp.h_stab_chord  # 95mm

    coords = _naca0009_coords(chord, 40)
    if np.linalg.norm(coords[0] - coords[-1]) > 0.1:
        coords = np.vstack([coords, coords[0:1]])

    # Create points at root and tip
    root_pts = ",\n            ".join(
        f"FreeCAD.Vector({boom_end_x + x:.4f}, 0, {z:.4f})"
        for x, z in coords
    )
    tip_r_pts = ",\n            ".join(
        f"FreeCAD.Vector({boom_end_x + x:.4f}, {half_span:.4f}, {z:.4f})"
        for x, z in coords
    )
    tip_l_pts = ",\n            ".join(
        f"FreeCAD.Vector({boom_end_x + x:.4f}, {-half_span:.4f}, {z:.4f})"
        for x, z in coords
    )

    code = f"""
import FreeCAD
import Part
import FreeCADGui

doc = FreeCAD.ActiveDocument
if doc is None:
    doc = FreeCAD.newDocument("AeroForge")

# ════════════════════════════════════════════
# HORIZONTAL STABILIZER
# {emp.h_stab_span}mm span, {emp.h_stab_chord}mm chord, NACA 0009
# ════════════════════════════════════════════

# Root section (at boom)
root_pts = [
            {root_pts}
]
root_bsp = Part.BSplineCurve()
root_bsp.interpolate(root_pts, PeriodicFlag=True)
root_wire = Part.Wire([root_bsp.toShape()])

# Right tip
tip_r_pts = [
            {tip_r_pts}
]
tip_r_bsp = Part.BSplineCurve()
tip_r_bsp.interpolate(tip_r_pts, PeriodicFlag=True)
tip_r_wire = Part.Wire([tip_r_bsp.toShape()])

# Left tip
tip_l_pts = [
            {tip_l_pts}
]
tip_l_bsp = Part.BSplineCurve()
tip_l_bsp.interpolate(tip_l_pts, PeriodicFlag=True)
tip_l_wire = Part.Wire([tip_l_bsp.toShape()])

# Loft right half
hstab_r = Part.makeLoft([root_wire, tip_r_wire], True, False, False)
# Loft left half
hstab_l = Part.makeLoft([root_wire, tip_l_wire], True, False, False)

# Combine
hstab_shape = hstab_r.fuse(hstab_l)

hstab = doc.addObject("Part::Feature", "HStab")
hstab.Shape = hstab_shape
hstab.Label = "H-Stab ({emp.h_stab_span}mm, NACA0009)"
hstab.ViewObject.ShapeColor = (0.90, 0.90, 0.95)
hstab.ViewObject.Transparency = 20

doc.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()
print(f"H-Stab: vol={{hstab_shape.Volume:.0f}}mm³, mass≈{{hstab_shape.Volume/1000*0.8:.1f}}g")
"""
    return code


def generate_vstab_code() -> str:
    """Generate FreeCAD code for vertical stabilizer."""
    emp = SAILPLANE.empennage
    boom_end_x = 250 + SAILPLANE.spar.boom_length  # 900mm

    height = emp.v_stab_height  # 140mm
    root_chord = emp.v_stab_root_chord  # 110mm
    tip_chord = emp.v_stab_tip_chord  # 60mm

    # Root airfoil (at boom, larger chord)
    root_coords = _naca0009_coords(root_chord, 40)
    if np.linalg.norm(root_coords[0] - root_coords[-1]) > 0.1:
        root_coords = np.vstack([root_coords, root_coords[0:1]])

    # Tip airfoil (smaller chord)
    tip_coords = _naca0009_coords(tip_chord, 40)
    if np.linalg.norm(tip_coords[0] - tip_coords[-1]) > 0.1:
        tip_coords = np.vstack([tip_coords, tip_coords[0:1]])

    # V-stab is in the XZ plane (X=chord, Z=height, Y=0)
    root_pts = ",\n            ".join(
        f"FreeCAD.Vector({boom_end_x + x:.4f}, {y:.4f}, 0)"
        for x, y in root_coords  # y from airfoil becomes Y in FreeCAD (lateral=thickness)
    )

    # Tip is offset upward in Z and swept slightly aft
    sweep_offset = height * math.tan(math.radians(5))  # 5 deg sweep
    tip_pts = ",\n            ".join(
        f"FreeCAD.Vector({boom_end_x + sweep_offset + x:.4f}, {y:.4f}, {height:.4f})"
        for x, y in tip_coords
    )

    code = f"""
import FreeCAD
import Part
import FreeCADGui

doc = FreeCAD.ActiveDocument

# ════════════════════════════════════════════
# VERTICAL STABILIZER
# {height}mm height, {root_chord}→{tip_chord}mm chord, NACA 0009
# ════════════════════════════════════════════

root_pts = [
            {root_pts}
]
root_bsp = Part.BSplineCurve()
root_bsp.interpolate(root_pts, PeriodicFlag=True)
root_wire = Part.Wire([root_bsp.toShape()])

tip_pts = [
            {tip_pts}
]
tip_bsp = Part.BSplineCurve()
tip_bsp.interpolate(tip_pts, PeriodicFlag=True)
tip_wire = Part.Wire([tip_bsp.toShape()])

vstab_shape = Part.makeLoft([root_wire, tip_wire], True, False, False)

vstab = doc.addObject("Part::Feature", "VStab")
vstab.Shape = vstab_shape
vstab.Label = "V-Stab ({height}mm, NACA0009)"
vstab.ViewObject.ShapeColor = (0.90, 0.95, 0.90)
vstab.ViewObject.Transparency = 20

doc.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()
print(f"V-Stab: vol={{vstab_shape.Volume:.0f}}mm³, mass≈{{vstab_shape.Volume/1000*0.8:.1f}}g")
"""
    return code


def generate_empennage_code() -> str:
    """Generate complete empennage code (H-stab + V-stab)."""
    return generate_hstab_code() + "\n\n" + generate_vstab_code()


if __name__ == "__main__":
    code = generate_empennage_code()
    print(f"Empennage code: {len(code)} chars")
    try:
        compile(code, '<empennage>', 'exec')
        print("SYNTAX OK")
    except SyntaxError as e:
        print(f"SYNTAX ERROR: {e}")
