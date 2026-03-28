"""FreeCAD code generator for vase-mode-compatible wing panels.

Implements the slot technique used by 3DLabPrint/Eclipson/Vase-Wing:
- Single solid wing body (lofted between airfoil sections)
- Thin slot walls (0.01mm gap width) create internal structure
- Grid mode 2: spanwise spar walls + angled cross-ribs at 55°
- Spar tunnel for carbon tube
- When sliced in vase mode, the slicer traces internal walls continuously

The 0.01mm gaps are NOT physical gaps — they're geometric features that
tell the slicer to trace internal walls as part of the vase-mode path.

Convention: X=chordwise (LE=0), Y=spanwise (root=0), Z=up (thickness)
"""

from __future__ import annotations

import math
import numpy as np

from src.cad.airfoils import airfoil_at_station, scale_airfoil
from src.core.specs import SAILPLANE, WingSpec, SparSpec


def _get_profile(span_frac: float, wing: WingSpec) -> tuple[np.ndarray, float]:
    """Get scaled airfoil coords at span fraction."""
    airfoil = airfoil_at_station(
        span_frac,
        root_airfoil=wing.airfoil_root,
        mid_airfoil=wing.airfoil_mid,
        tip_airfoil=wing.airfoil_tip,
        n_points=60,
    )
    chord = wing.chord_at(span_frac)
    twist = wing.washout_at(span_frac)
    scaled = scale_airfoil(airfoil, chord, twist_deg=twist)
    if np.linalg.norm(scaled[0] - scaled[-1]) > 0.1:
        scaled = np.vstack([scaled, scaled[0:1]])
    return scaled, chord


def generate_vase_mode_panel_code(
    panel_index: int = 0,
    wing: WingSpec | None = None,
    spar: SparSpec | None = None,
    n_loft_sections: int = 9,
    n_spar_walls: int = 3,
    n_cross_ribs: int = 7,
    spar_wall_offset_pct: float = 10.0,
    cross_rib_angle_deg: float = 55.0,
    gap_width: float = 0.01,
) -> str:
    """Generate FreeCAD Python code for a vase-mode-compatible wing panel.

    Args:
        panel_index: 0 (root) to 4 (tip)
        wing: Wing spec
        spar: Spar spec
        n_loft_sections: Airfoil sections for smooth loft
        n_spar_walls: Spanwise internal spar walls
        n_cross_ribs: Angled cross-rib walls
        spar_wall_offset_pct: % chord offset from LE/TE for first/last spar wall
        cross_rib_angle_deg: Angle of cross-ribs from vertical
        gap_width: Slot width in mm (0.01mm standard for vase mode)
    """
    wing = wing or SAILPLANE.wing
    spar = spar or SAILPLANE.spar

    panel_span = wing.panel_span  # 256mm
    half_span = wing.half_span
    root_y = panel_index * panel_span
    root_frac = root_y / half_span
    tip_frac = (root_y + panel_span) / half_span

    root_chord = wing.chord_at(root_frac)
    tip_chord = wing.chord_at(tip_frac)
    max_chord = root_chord  # Root is always largest

    # Generate airfoil section data
    sections = []
    for i in range(n_loft_sections):
        y = i * panel_span / (n_loft_sections - 1)
        frac = (root_y + y) / half_span
        coords, chord = _get_profile(frac, wing)
        sections.append((y, frac, coords, chord))

    # Spar position (for tunnel subtraction)
    spar_x = root_chord * spar.main_position_chord_fraction
    root_coords = sections[0][2]
    le_idx = int(np.argmin(root_coords[:, 0]))
    upper = root_coords[:le_idx + 1][np.argsort(root_coords[:le_idx + 1, 0])]
    lower = root_coords[le_idx:][np.argsort(root_coords[le_idx:, 0])]
    spar_z_up = float(np.interp(spar_x, upper[:, 0], upper[:, 1]))
    spar_z_lo = float(np.interp(spar_x, lower[:, 0], lower[:, 1]))
    spar_z = (spar_z_up + spar_z_lo) / 2

    # ── Build FreeCAD code ──
    code_parts = []

    # Header
    code_parts.append(f"""
import FreeCAD
import Part
import FreeCADGui
import math
import time

t0 = time.time()

doc = FreeCAD.ActiveDocument
if doc is None:
    doc = FreeCAD.newDocument("AeroForge")

# ════════════════════════════════════════════════════════════
# WING PANEL {panel_index} — VASE MODE CONSTRUCTION
# ════════════════════════════════════════════════════════════
# Span: {root_y:.0f}-{root_y + panel_span:.0f}mm
# Chord: {root_chord:.0f}→{tip_chord:.0f}mm
# Airfoil: blended AG24→AG09→AG03
# Internal: {n_spar_walls} spar walls + {n_cross_ribs} cross-ribs @ {cross_rib_angle_deg:.0f}°
# Gap width: {gap_width}mm (vase-mode slot technique)
# ════════════════════════════════════════════════════════════

print(f"Building Panel {panel_index} (vase-mode)...")
""")

    # Step 1: Create airfoil wires and loft
    code_parts.append("""
# ── STEP 1: Loft wing solid from airfoil sections ──
print("  [1/4] Lofting airfoil sections...")
wires = []
""")

    for i, (y, frac, coords, chord) in enumerate(sections):
        pts_str = ",\n            ".join(
            f"FreeCAD.Vector({x:.4f}, {y:.4f}, {z:.4f})"
            for x, z in coords
        )
        code_parts.append(f"""
pts_{i} = [
            {pts_str}
]
bsp_{i} = Part.BSplineCurve()
bsp_{i}.interpolate(pts_{i}, PeriodicFlag=True)
wires.append(Part.Wire([bsp_{i}.toShape()]))
""")

    code_parts.append(f"""
wing_solid = Part.makeLoft(wires, True, False, False)
print(f"    Loft: vol={{wing_solid.Volume:.0f}}mm³, {{time.time()-t0:.1f}}s")
""")

    # Step 2: Create internal grid structure (spar walls + cross-ribs)
    spar_offset = max_chord * spar_wall_offset_pct / 100
    spar_spacing = (max_chord - 2 * spar_offset) / max(n_spar_walls - 1, 1)

    code_parts.append(f"""
# ── STEP 2: Create internal grid (spar walls + cross-ribs) ──
print("  [2/4] Creating internal grid structure...")

gap = {gap_width}  # mm — vase mode slot width
grid_parts = []
max_chord = {max_chord:.1f}
panel_span = {panel_span:.1f}

# Spanwise spar walls (run full panel span)
spar_positions = []
for i in range({n_spar_walls}):
    x_pos = {spar_offset:.1f} + i * {spar_spacing:.1f}
    spar_positions.append(x_pos)
    # Thin box: gap_width × airfoil_height × panel_span
    wall = Part.makeBox(gap, max_chord * 0.3, panel_span)
    wall.translate(FreeCAD.Vector(x_pos - gap/2, 0, -max_chord * 0.15))
    # Rotate to align: box is in XYZ, we need XY=chord plane, Z=span
    # Actually: X=chord, Y=span, Z=thickness
    # Wall runs along Y (span), thin in X (chord direction), tall in Z (thickness)
    wall2 = Part.makeBox(gap, panel_span, max_chord * 0.3)
    wall2.translate(FreeCAD.Vector(x_pos - gap/2, 0, -max_chord * 0.15))
    grid_parts.append(wall2)

print(f"    {{len(spar_positions)}} spar walls at: {{[f'{{p:.0f}}mm' for p in spar_positions]}}")

# Cross-ribs (angled walls, perpendicular-ish to span)
rib_spacing = panel_span / ({n_cross_ribs} + 1)
cross_rib_angle = {cross_rib_angle_deg}
for j in range({n_cross_ribs}):
    y_pos = (j + 1) * rib_spacing
    # Create a thin slab, then rotate by cross_rib_angle
    rib = Part.makeBox(max_chord * 1.5, gap, max_chord * 0.3)
    rib.translate(FreeCAD.Vector(-max_chord * 0.25, -gap/2, -max_chord * 0.15))
    # Rotate around Z axis by the rib angle
    rib.rotate(FreeCAD.Vector(max_chord/2, 0, 0), FreeCAD.Vector(0, 0, 1), cross_rib_angle)
    rib.translate(FreeCAD.Vector(0, y_pos, 0))
    grid_parts.append(rib)

print(f"    {n_cross_ribs} cross-ribs at {cross_rib_angle_deg:.0f}° angle")

# Fuse all grid elements
print("    Fusing grid elements...")
grid = grid_parts[0]
for g in grid_parts[1:]:
    grid = grid.fuse(g)

print(f"    Grid fused, {{time.time()-t0:.1f}}s")
""")

    # Step 3: Intersect grid with wing solid
    code_parts.append(f"""
# ── STEP 3: Intersect grid with wing (trim to airfoil shape) ──
print("  [3/4] Intersecting grid with wing solid...")
internal_structure = grid.common(wing_solid)
print(f"    Internal structure: vol={{internal_structure.Volume:.0f}}mm³")

# Fuse wing + internal structure
panel_shape = wing_solid.fuse(internal_structure)
print(f"    Combined: vol={{panel_shape.Volume:.0f}}mm³, {{time.time()-t0:.1f}}s")
""")

    # Step 4: Subtract spar tunnel
    code_parts.append(f"""
# ── STEP 4: Subtract spar tunnel ──
print("  [4/4] Cutting spar tunnel...")
spar_tunnel = Part.makeCylinder(
    {spar.main_od / 2 + 0.1:.1f},  # 0.1mm clearance
    panel_span + 4,
    FreeCAD.Vector({spar_x:.2f}, -2, {spar_z:.2f}),
    FreeCAD.Vector(0, 1, 0)  # Along Y (spanwise)
)
panel_shape = panel_shape.cut(spar_tunnel)

# Add to document
panel = doc.addObject("Part::Feature", "WingPanel_{panel_index}")
panel.Shape = panel_shape
panel.Label = "Wing Panel {panel_index} (vase-mode, {root_chord:.0f}→{tip_chord:.0f}mm)"
panel.ViewObject.ShapeColor = (0.85, 0.90, 0.95)  # Light blue
panel.ViewObject.Transparency = 0

# Add spar visualization (separate object for clarity)
spar_vis = Part.makeCylinder(
    {spar.main_od / 2},
    panel_span,
    FreeCAD.Vector({spar_x:.2f}, 0, {spar_z:.2f}),
    FreeCAD.Vector(0, 1, 0)
)
spar_inner = Part.makeCylinder(
    {spar.main_id / 2},
    panel_span + 2,
    FreeCAD.Vector({spar_x:.2f}, -1, {spar_z:.2f}),
    FreeCAD.Vector(0, 1, 0)
)
spar_tube = spar_vis.cut(spar_inner)
spar_obj = doc.addObject("Part::Feature", "CarbonSpar_{panel_index}")
spar_obj.Shape = spar_tube
spar_obj.Label = "Carbon Spar P{panel_index}"
spar_obj.ViewObject.ShapeColor = (0.1, 0.1, 0.1)

doc.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()

elapsed = time.time() - t0
vol_cm3 = panel_shape.Volume / 1000
mass_lwpla = vol_cm3 * 0.54  # LW-PLA foamed density

print(f"")
print(f"  ✓ Panel {panel_index} complete in {{elapsed:.1f}}s")
print(f"    Volume: {{vol_cm3:.1f}} cm³")
print(f"    Mass (LW-PLA foamed): {{mass_lwpla:.1f}}g")
print(f"    Chord: {root_chord:.0f}→{tip_chord:.0f}mm")
print(f"    Span: {panel_span:.0f}mm")
print(f"    Spar: 8mm carbon @ x={spar_x:.1f}mm, z={spar_z:.1f}mm")
""")

    return "\n".join(code_parts)


def generate_all_vase_panels_code() -> str:
    """Generate FreeCAD code for all 5 panels in sequence."""
    wing = SAILPLANE.wing
    all_code = []

    for i in range(wing.panels_per_half):
        code = generate_vase_mode_panel_code(i)
        all_code.append(code)

    # Summary at the end
    all_code.append("""
# ════════════════════════════════════════════════════════════
# HALF-WING SUMMARY
# ════════════════════════════════════════════════════════════
total_mass = 0
for obj in doc.Objects:
    if obj.Label.startswith("Wing Panel"):
        m = obj.Shape.Volume / 1000 * 0.54
        total_mass += m
        print(f"  {obj.Label}: {m:.1f}g")

print(f"")
print(f"  Half-wing total: {total_mass:.1f}g")
print(f"  Full wing (both halves): {total_mass * 2:.1f}g")
print(f"  + Carbon spars: ~30g")
print(f"  = Wing assembly: {total_mass * 2 + 30:.1f}g")
""")

    return "\n\n".join(all_code)


if __name__ == "__main__":
    # Test: generate and syntax-check panel 0
    code = generate_vase_mode_panel_code(0)
    print(f"Panel 0 code: {len(code)} chars")
    try:
        compile(code, '<panel_0>', 'exec')
        print("SYNTAX OK")
    except SyntaxError as e:
        print(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")

    # Test all panels
    all_code = generate_all_vase_panels_code()
    print(f"\nAll panels code: {len(all_code)} chars")
    try:
        compile(all_code, '<all_panels>', 'exec')
        print("ALL PANELS SYNTAX OK")
    except SyntaxError as e:
        print(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")
