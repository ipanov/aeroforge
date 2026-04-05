"""Wing Panel P1 (root panel) — Build123d parametric model.

Panel P1 is the innermost wing panel (y=0 to y=256mm, right half).
Root chord 210mm (AG24), outboard chord 204mm (90% AG24 / 10% AG03).

Convention: X=chordwise (LE=0, TE=chord), Y=up (thickness), Z=spanwise (root=0).
Main spar at 25% chord is the STRAIGHT datum line.

Architecture:
- Solid lofted outer shell (aerodynamic mold)
- Solid ribs with lightening holes, spar bores, rear spar slots
- D-box spar webs between ribs
- Carbon spar tube visualization
- Rear spar strip visualization
- Servo pocket cutout in mid-panel rib
- Flap hinge line scored at 72% chord

NO OCCT booleans on the lofted shell. Cuts only on extruded ribs (safe).
The mesh pipeline (rebuild_all_meshes.py) handles shell hollowing,
geodesic ribs, and 3MF export separately.
"""

from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Compound,
    Cylinder,
    Ellipse,
    Face,
    Location,
    Part,
    Plane,
    Pos,
    RigidJoint,
    Rot,
    Spline,
    Vector,
    add,
    extrude,
    loft,
    make_face,
    export_step,
)

from src.cad.airfoils import (
    blend_airfoils,
    get_airfoil,
    scale_airfoil,
)


# ── Panel P1 parameters (from COMPONENT_INFO.md / DESIGN_CONSENSUS.md) ──

PANEL_SPAN = 256.0          # mm
ROOT_CHORD = 210.0          # mm (AG24 100%)
OUTBOARD_CHORD = 204.0      # mm (90% AG24 / 10% AG03)
HALF_SPAN = 1280.0          # mm (full half-wing)

# Airfoils
ROOT_AIRFOIL = "AG24"
TIP_AIRFOIL = "AG03"
ROOT_AG03_FRAC = 0.0        # 0% AG03 at root
OUTBOARD_AG03_FRAC = 0.10   # 10% AG03 at outboard

# Structural
MAIN_SPAR_CHORD_FRAC = 0.25    # 25% chord
MAIN_SPAR_OD = 8.0             # mm CF tube
MAIN_SPAR_ID = 6.0             # mm inner
SPAR_BORE_DIA = 8.3            # mm (0.15mm clearance per side)
REAR_SPAR_CHORD_FRAC = 0.60   # 60% chord
REAR_SPAR_W = 5.0              # mm width
REAR_SPAR_H = 3.0              # mm height
REAR_SPAR_SLOT_W = 5.3         # mm (0.15mm clearance per side)
REAR_SPAR_SLOT_H = 3.3         # mm
DBOX_CUTOFF = 0.30             # 30% chord
DBOX_WALL = 0.70               # mm
SHELL_WALL = 0.50              # mm

# Ribs
RIB_SPACING = 32.0             # mm
RIB_THICK = 1.2                # mm

# Flap hinge
HINGE_CHORD_FRAC = 0.72       # 72% chord
FLAP_CHORD_FRAC = 0.28        # 28% of local chord

# Servo
SERVO_Y = 128.0                # mm (mid-panel)
SERVO_CHORD_FRAC = 0.35       # 35% chord
SERVO_POCKET_W = 23.0         # mm (chordwise)
SERVO_POCKET_H = 11.0         # mm (spanwise)

# Joint
JOINT_TONGUE_DEPTH = 2.0      # mm
JOINT_TONGUE_THICK = 3.0      # mm

# Number of loft stations (more = smoother)
N_LOFT_STATIONS = 9           # y=0, 32, 64, 96, 128, 160, 192, 224, 256

# Airfoil point count for splines
N_AIRFOIL_PTS = 80


def _chord_at(y: float) -> float:
    """Linear chord interpolation across P1 span."""
    frac = y / PANEL_SPAN
    return ROOT_CHORD + (OUTBOARD_CHORD - ROOT_CHORD) * frac


def _ag03_fraction_at(y: float) -> float:
    """AG03 blend fraction at local span position y."""
    frac = y / PANEL_SPAN
    return ROOT_AG03_FRAC + (OUTBOARD_AG03_FRAC - ROOT_AG03_FRAC) * frac


def _get_airfoil_coords(y: float, n_points: int = N_AIRFOIL_PTS) -> np.ndarray:
    """Get blended, scaled airfoil coordinates at span station y.

    Returns physical (x, y_thickness) coordinates in mm.
    The airfoil is positioned so that the 25% chord point sits at x=0
    (spar datum line), but we actually keep LE at x=0 for consistency
    with the convention used in panel.py.
    """
    chord = _chord_at(y)
    ag03_frac = _ag03_fraction_at(y)

    # Blend AG24/AG03
    if ag03_frac < 0.001:
        blended = get_airfoil(ROOT_AIRFOIL)
    else:
        blended = blend_airfoils(ROOT_AIRFOIL, TIP_AIRFOIL, ag03_frac, n_points)

    # Scale to physical chord
    scaled = scale_airfoil(blended, chord, twist_deg=0.0)

    # Remove duplicate closing point if present
    if np.linalg.norm(scaled[0] - scaled[-1]) < 0.5:
        scaled = scaled[:-1]

    return scaled


def _y_at_x(scaled: np.ndarray, x: float) -> tuple[float, float]:
    """Get upper and lower Y at a chordwise X position from scaled coords."""
    le_idx = int(np.argmin(scaled[:, 0]))
    upper = scaled[:le_idx + 1][np.argsort(scaled[:le_idx + 1, 0])]
    lower = scaled[le_idx:][np.argsort(scaled[le_idx:, 0])]
    yu = float(np.interp(x, upper[:, 0], upper[:, 1]))
    yl = float(np.interp(x, lower[:, 0], lower[:, 1]))
    return yu, yl


def _make_airfoil_face(scaled: np.ndarray, z: float = 0.0) -> Face:
    """Create a Build123d Face from scaled airfoil coords at Z (spanwise)."""
    pts = [Vector(float(x), float(y), z) for x, y in scaled]
    spline = Spline(*pts, periodic=True)
    return make_face(spline)


def build_outer_shell() -> Part:
    """Loft through airfoil stations to create the solid outer mold.

    This is the full solid aerodynamic shape. The mesh pipeline will
    hollow it to shell wall thickness later.
    """
    faces = []
    stations = np.linspace(0, PANEL_SPAN, N_LOFT_STATIONS)

    for y in stations:
        coords = _get_airfoil_coords(y)
        face = _make_airfoil_face(coords, z=y)
        faces.append(face)

    with BuildPart() as bp:
        loft(faces)

    return bp.part


def build_rib(y: float, is_servo_rib: bool = False) -> Part:
    """Build a single solid rib with lightening holes and spar features.

    Args:
        y: Spanwise position (local, 0=root face, 256=outboard face)
        is_servo_rib: If True, add servo pocket cutout
    """
    chord = _chord_at(y)
    scaled = _get_airfoil_coords(y)
    face = _make_airfoil_face(scaled)

    with BuildPart() as bp:
        with BuildSketch():
            add(face)
        extrude(amount=RIB_THICK)
    rib = bp.part

    # ── Main spar bore (8.3mm hole at 25% chord) ──
    sx = chord * MAIN_SPAR_CHORD_FRAC
    su, sl = _y_at_x(scaled, sx)
    sy = (su + sl) / 2.0

    spar_hole = Cylinder(
        SPAR_BORE_DIA / 2, RIB_THICK + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).locate(Location(Pos(sx, sy, -1)))
    rib = rib - spar_hole

    # ── Rear spar slot (5.3 x 3.3mm at 60% chord) ──
    rx = chord * REAR_SPAR_CHORD_FRAC
    ru, rl = _y_at_x(scaled, rx)
    ry = (ru + rl) / 2.0

    rear_slot = Box(
        REAR_SPAR_SLOT_W, REAR_SPAR_SLOT_H, RIB_THICK + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).locate(Location(Pos(rx, ry, -1)))
    rib = rib - rear_slot

    # ── Lightening holes ──

    # Hole 1: D-box forward bay (12%-24% chord)
    h1_cx = chord * 0.18
    h1_yu, h1_yl = _y_at_x(scaled, h1_cx)
    h1_h = (h1_yu - h1_yl) * 0.50
    h1_w = chord * 0.09
    if h1_h > 3 and h1_w > 3:
        with BuildPart() as hb:
            with BuildSketch(Plane.XY.offset(-1)):
                Ellipse(h1_w / 2, h1_h / 2).locate(
                    Location(Pos(h1_cx, (h1_yu + h1_yl) / 2)))
            extrude(amount=RIB_THICK + 2)
        rib = rib - hb.part

    # Hole 2: Main bay (32%-55% chord, between main and rear spar)
    h2_cx = chord * 0.44
    h2_yu, h2_yl = _y_at_x(scaled, h2_cx)
    h2_h = (h2_yu - h2_yl) * 0.55
    h2_w = chord * 0.14
    if h2_h > 3 and h2_w > 3:
        with BuildPart() as hb2:
            with BuildSketch(Plane.XY.offset(-1)):
                Ellipse(h2_w / 2, h2_h / 2).locate(
                    Location(Pos(h2_cx, (h2_yu + h2_yl) / 2)))
            extrude(amount=RIB_THICK + 2)
        rib = rib - hb2.part

    # Hole 3: Aft bay (behind rear spar, 68%-85% chord)
    h3_cx = chord * 0.76
    h3_yu, h3_yl = _y_at_x(scaled, h3_cx)
    h3_h = (h3_yu - h3_yl) * 0.45
    h3_w = chord * 0.10
    if h3_h > 2 and h3_w > 2:
        with BuildPart() as hb3:
            with BuildSketch(Plane.XY.offset(-1)):
                Ellipse(h3_w / 2, h3_h / 2).locate(
                    Location(Pos(h3_cx, (h3_yu + h3_yl) / 2)))
            extrude(amount=RIB_THICK + 2)
        rib = rib - hb3.part

    # ── Servo pocket (only on servo rib) ──
    if is_servo_rib:
        servo_x = chord * SERVO_CHORD_FRAC
        servo_yu, servo_yl = _y_at_x(scaled, servo_x)
        servo_cy = (servo_yu + servo_yl) / 2.0
        pocket = Box(
            SERVO_POCKET_W, SERVO_POCKET_H, RIB_THICK + 2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ).locate(Location(Pos(servo_x, servo_cy, -1)))
        rib = rib - pocket

    # Position at spanwise station
    return rib.locate(Location(Pos(0, 0, y)))


def build_dbox_web(y1: float, y2: float, thickness: float = 0.7) -> Part:
    """Build D-box closing web at 30% chord between two rib stations."""
    chord1 = _chord_at(y1)
    chord2 = _chord_at(y2)
    sc1 = _get_airfoil_coords(y1)
    sc2 = _get_airfoil_coords(y2)

    dx1 = chord1 * DBOX_CUTOFF
    dx2 = chord2 * DBOX_CUTOFF
    yu1, yl1 = _y_at_x(sc1, dx1)
    yu2, yl2 = _y_at_x(sc2, dx2)

    h1 = (yu1 - yl1) * 0.90
    h2 = (yu2 - yl2) * 0.90
    cy1 = (yu1 + yl1) / 2
    cy2 = (yu2 + yl2) / 2

    span = y2 - y1
    avg_h = (h1 + h2) / 2
    avg_x = (dx1 + dx2) / 2
    avg_y = (cy1 + cy2) / 2

    web = Box(
        thickness, avg_h, span,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return web.locate(Location(Pos(avg_x, avg_y, y1)))


def build_spar_tube() -> Part:
    """Build the main carbon spar tube visualization (8mm OD, 6mm ID)."""
    # Spar position at root (25% chord)
    sc0 = _get_airfoil_coords(0)
    sx = ROOT_CHORD * MAIN_SPAR_CHORD_FRAC
    su, sl = _y_at_x(sc0, sx)
    sy = (su + sl) / 2.0

    outer = Cylinder(
        MAIN_SPAR_OD / 2, PANEL_SPAN,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    inner = Cylinder(
        MAIN_SPAR_ID / 2, PANEL_SPAN + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    tube = outer - inner

    # Rotate from Z-up to Z=spanwise and position
    tube = tube.locate(Location(Pos(sx, sy, 0)))
    return tube


def build_rear_spar() -> Part:
    """Build the rear spruce spar strip visualization (5x3mm)."""
    sc0 = _get_airfoil_coords(0)
    rx = ROOT_CHORD * REAR_SPAR_CHORD_FRAC
    ru, rl = _y_at_x(sc0, rx)
    ry = (ru + rl) / 2.0

    strip = Box(
        REAR_SPAR_W, REAR_SPAR_H, PANEL_SPAN,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return strip.locate(Location(Pos(rx, ry, 0)))


def build_hinge_score_line() -> Part:
    """Build a thin score line at 72% chord to mark the flap hinge.

    This is a shallow groove (0.3mm wide x 0.3mm deep) running full span.
    The mesh pipeline will handle the actual living hinge cut.
    """
    # Average hinge position
    root_hx = ROOT_CHORD * HINGE_CHORD_FRAC
    tip_hx = OUTBOARD_CHORD * HINGE_CHORD_FRAC
    avg_hx = (root_hx + tip_hx) / 2

    sc0 = _get_airfoil_coords(0)
    yu, yl = _y_at_x(sc0, avg_hx)

    score = Box(
        0.3, 0.3, PANEL_SPAN,
        align=(Align.CENTER, Align.MIN, Align.MIN),
    )
    return score.locate(Location(Pos(avg_hx, yl, 0)))


def build_panel_p1(show_viewer: bool = False) -> dict:
    """Build the complete Wing Panel P1.

    Returns dict with all parts, statistics, and compound.
    """
    t0 = time.time()
    print("Building Wing Panel P1 (root panel, y=0 to y=256mm)...")

    # ── 1. Outer aerodynamic shape ──
    print("  [1/6] Lofting outer shell...")
    outer = build_outer_shell()
    print(f"         Outer volume: {outer.volume:.0f} mm^3")

    # ── 2. Ribs ──
    print("  [2/6] Building ribs...")
    n_ribs = int(PANEL_SPAN / RIB_SPACING) + 1  # 0, 32, 64, ..., 256 = 9 ribs
    rib_positions = [i * RIB_SPACING for i in range(n_ribs)]

    ribs = []
    for y in rib_positions:
        is_servo = abs(y - SERVO_Y) < 1.0  # Servo at y=128
        rib = build_rib(y, is_servo_rib=is_servo)
        ribs.append(rib)
    print(f"         {len(ribs)} ribs built (spacing {RIB_SPACING}mm)")

    # ── 3. D-box webs ──
    print("  [3/6] Building D-box webs...")
    webs = []
    for i in range(len(rib_positions) - 1):
        y1 = rib_positions[i] + RIB_THICK
        y2 = rib_positions[i + 1]
        if y2 > y1:
            web = build_dbox_web(y1, y2)
            webs.append(web)
    print(f"         {len(webs)} D-box webs built")

    # ── 4. Spar visualizations ──
    print("  [4/6] Building spar visualizations...")
    spar_tube = build_spar_tube()
    rear_spar = build_rear_spar()

    # ── 5. Hinge score line ──
    print("  [5/6] Building hinge score line...")
    hinge_line = build_hinge_score_line()

    # ── 6. Statistics ──
    print("  [6/6] Computing statistics...")
    rib_vol = sum(r.volume for r in ribs)
    web_vol = sum(w.volume for w in webs)
    spar_vol = spar_tube.volume
    rear_vol = rear_spar.volume

    rib_mass = rib_vol / 1000 * 1.25     # CF-PLA density ~1.25 g/cm^3
    web_mass = web_vol / 1000 * 0.80     # LW-PLA density ~0.80 g/cm^3
    spar_mass = spar_vol / 1000 * 1.60   # Carbon ~1.60 g/cm^3
    rear_mass = rear_vol / 1000 * 0.45   # Spruce ~0.45 g/cm^3

    # Skin mass: surface area x wall thickness x LW-PLA density
    skin_area = outer.area  # mm^2
    skin_vol = skin_area * SHELL_WALL    # mm^3
    skin_mass = skin_vol / 1000 * 0.80   # LW-PLA

    # D-box extra wall (0.70 - 0.50 = 0.20mm extra in D-box zone, ~30% of surface)
    dbox_extra_mass = skin_area * 0.30 * 0.20 / 1000 * 0.80

    panel_mass = rib_mass + web_mass + skin_mass + dbox_extra_mass
    total_with_spars = panel_mass + spar_mass + rear_mass

    bb = outer.bounding_box()
    elapsed = time.time() - t0

    stats = {
        "panel": "P1",
        "span_mm": PANEL_SPAN,
        "root_chord_mm": ROOT_CHORD,
        "outboard_chord_mm": OUTBOARD_CHORD,
        "rib_count": len(ribs),
        "web_count": len(webs),
        "build_time_s": elapsed,
        "rib_mass_g": rib_mass,
        "web_mass_g": web_mass,
        "skin_mass_g": skin_mass,
        "dbox_extra_mass_g": dbox_extra_mass,
        "panel_mass_g": panel_mass,
        "spar_mass_g": spar_mass,
        "rear_spar_mass_g": rear_mass,
        "total_with_spars_g": total_with_spars,
        "outer_volume_mm3": outer.volume,
        "outer_area_mm2": outer.area,
        "bounding_box": f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm",
    }

    print(f"\n  Panel P1 Summary:")
    print(f"    Build time:       {elapsed:.1f}s")
    print(f"    Bounding box:     {stats['bounding_box']}")
    print(f"    Ribs:             {rib_mass:.1f}g ({len(ribs)} ribs)")
    print(f"    D-box webs:       {web_mass:.1f}g ({len(webs)} webs)")
    print(f"    Skin (est):       {skin_mass:.1f}g + {dbox_extra_mass:.1f}g D-box extra")
    print(f"    Panel total:      {panel_mass:.1f}g")
    print(f"    + Main spar:      {spar_mass:.1f}g")
    print(f"    + Rear spar:      {rear_mass:.1f}g")
    print(f"    TOTAL w/ spars:   {total_with_spars:.1f}g")

    # ── Compound ──
    all_parts = ribs + webs + [outer, spar_tube, rear_spar, hinge_line]
    compound = Compound(children=all_parts)
    compound.label = "Wing_Panel_P1"

    RigidJoint("root", compound, Location(Pos(0, 0, 0)))
    RigidJoint("outboard", compound, Location(Pos(0, 0, PANEL_SPAN)))

    if show_viewer:
        _show_in_viewer(ribs, webs, outer, spar_tube, rear_spar, hinge_line)

    return {
        "outer": outer,
        "ribs": ribs,
        "dbox_webs": webs,
        "spar_tube": spar_tube,
        "rear_spar": rear_spar,
        "hinge_line": hinge_line,
        "compound": compound,
        "stats": stats,
    }


def _show_in_viewer(ribs, webs, outer, spar_tube, rear_spar, hinge_line):
    """Display all parts in OCP Viewer with color coding."""
    try:
        from ocp_vscode import show, set_port, Camera
        set_port(3939)

        parts = ribs + webs + [outer, spar_tube, rear_spar, hinge_line]
        names = (
            [f"rib_{i}" for i in range(len(ribs))]
            + [f"dbox_web_{i}" for i in range(len(webs))]
            + ["skin_outer", "carbon_spar_8mm", "spruce_rear_5x3", "hinge_72pct"]
        )
        colors = (
            ["orange"] * len(ribs)
            + ["green"] * len(webs)
            + ["lightblue", "black", "burlywood", "red"]
        )
        alphas = (
            [1.0] * len(ribs)
            + [1.0] * len(webs)
            + [0.15, 1.0, 1.0, 1.0]
        )
        show(
            *parts,
            names=names,
            colors=colors,
            alphas=alphas,
            reset_camera=Camera.RESET,
        )
    except Exception as e:
        print(f"  OCP viewer: {e}")


def export_panel_p1():
    """Build and export Wing Panel P1 to STEP."""
    result = build_panel_p1(show_viewer=True)

    # Export STEP
    step_path = Path("cad/components/wing/Wing_Panel_P1/Wing_Panel_P1.step")
    step_path.parent.mkdir(parents=True, exist_ok=True)
    export_step(result["compound"], str(step_path))
    print(f"\n  STEP exported: {step_path}")

    return result


if __name__ == "__main__":
    export_panel_p1()
