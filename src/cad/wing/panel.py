"""Wing panel geometry - built-up structure approach.

Each 256mm panel contains:
- Solid ribs with lightening holes (every 32mm)
- D-box spar webs between ribs (30% chord)
- Main spar tunnel (8mm carbon tube)
- Rear spar slot (5x3mm spruce)
- Outer aerodynamic shape (for slicer → skin via perimeters)

The thin skin (0.5mm) is NOT modeled as separate CAD geometry.
It comes from the slicer's perimeter settings (2 perimeters × 0.25mm).
This is standard practice for 3D-printed wings.

Convention: X=chordwise (LE=0, TE=chord), Y=up, Z=spanwise (root=0)
"""

from __future__ import annotations

import time

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

from src.cad.airfoils import airfoil_at_station, scale_airfoil
from src.core.specs import SAILPLANE, WingSpec, SparSpec


def _y_at_x(scaled: np.ndarray, x: float) -> tuple[float, float]:
    """Get upper and lower Y at a chordwise X position."""
    le = int(np.argmin(scaled[:, 0]))
    u = scaled[:le + 1][np.argsort(scaled[:le + 1, 0])]
    l = scaled[le:][np.argsort(scaled[le:, 0])]
    return (float(np.interp(x, u[:, 0], u[:, 1])),
            float(np.interp(x, l[:, 0], l[:, 1])))


def _get_profile(z_local: float, wing: WingSpec, half_span: float) -> tuple[np.ndarray, float]:
    """Get scaled airfoil coordinates and chord at a local Z position."""
    frac = z_local / half_span
    chord = wing.chord_at(frac)
    airfoil = airfoil_at_station(
        frac,
        root_airfoil=wing.airfoil_root,
        mid_airfoil=wing.airfoil_mid,
        tip_airfoil=wing.airfoil_tip,
        n_points=40,
    )
    scaled = scale_airfoil(airfoil, chord, twist_deg=wing.washout_at(frac))
    if np.linalg.norm(scaled[0] - scaled[-1]) < 1.0:
        scaled = scaled[:-1]
    return scaled, chord


def _make_airfoil_face(scaled: np.ndarray, z: float = 0) -> Face:
    """Create Build123d Face from scaled airfoil coords at Z."""
    pts = [Vector(float(x), float(y), z) for x, y in scaled]
    return make_face(Spline(*pts, periodic=True))


def build_rib(
    z_local: float,
    wing: WingSpec,
    spar: SparSpec,
    half_span: float,
    rib_thick: float = 1.2,
) -> Part:
    """Build a single solid rib with lightening holes, spar holes, and D-box web.

    The rib is a SOLID airfoil-shaped plate with:
    - Circular hole for 8mm carbon spar (at 28% chord)
    - Rectangular slot for 5x3mm spruce rear spar (at 65% chord)
    - Elliptical lightening holes between structural areas
    - The D-box cutoff line is at 30% chord

    The remaining solid material provides continuous load paths:
    - LE → D-box web → main spar (torsion path)
    - Main spar → rear spar (shear web path)
    - All connected through upper and lower skins
    """
    scaled, chord = _get_profile(z_local, wing, half_span)

    # Full solid airfoil → extrude
    face = _make_airfoil_face(scaled)
    with BuildPart() as bp:
        with BuildSketch():
            add(face)
        extrude(amount=rib_thick)
    rib = bp.part

    # ── Spar hole ──
    sx = chord * spar.main_position_chord_fraction
    su, sl = _y_at_x(scaled, sx)
    sy = (su + sl) / 2
    spar_hole = Cylinder(
        spar.main_od / 2 + 0.1, rib_thick + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).locate(Location(Pos(sx, sy, -1)))
    rib = rib - spar_hole

    # ── Rear spar slot ──
    rx = chord * spar.rear_position_chord_fraction
    ru, rl = _y_at_x(scaled, rx)
    ry = (ru + rl) / 2
    rear_slot = Box(
        spar.rear_width + 0.2, spar.rear_height + 0.2, rib_thick + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).locate(Location(Pos(rx, ry, -1)))
    rib = rib - rear_slot

    # ── Lightening holes ──
    # IMPORTANT: Keep LE solid (0-10% chord) - no holes near LE!
    # Keep solid around D-box (28-32% chord) and around spars

    dbox_x = chord * wing.dbox_cutoff  # 30% chord

    # Hole 1: D-box forward bay (12% to 25% chord)
    # Between LE solid zone and main spar/D-box
    h1_cx = chord * 0.18  # Center
    h1_yu, h1_yl = _y_at_x(scaled, h1_cx)
    h1_h = (h1_yu - h1_yl) * 0.50  # 50% of local airfoil height
    h1_w = chord * 0.10   # 10% chord width
    if h1_h > 3 and h1_w > 3:
        with BuildPart() as hb:
            with BuildSketch(Plane.XY.offset(-1)):
                Ellipse(h1_w / 2, h1_h / 2).locate(
                    Location(Pos(h1_cx, (h1_yu + h1_yl) / 2)))
            extrude(amount=rib_thick + 2)
        rib = rib - hb.part

    # Hole 2: Main bay (35% to 60% chord)
    # Between main spar and rear spar - largest open area
    h2_cx = (sx + rx) / 2
    h2_yu, h2_yl = _y_at_x(scaled, h2_cx)
    h2_h = (h2_yu - h2_yl) * 0.55
    h2_w = (rx - sx) * 0.45
    if h2_h > 3 and h2_w > 3:
        with BuildPart() as hb2:
            with BuildSketch(Plane.XY.offset(-1)):
                Ellipse(h2_w / 2, h2_h / 2).locate(
                    Location(Pos(h2_cx, (h2_yu + h2_yl) / 2)))
            extrude(amount=rib_thick + 2)
        rib = rib - hb2.part

    # Hole 3: Aft bay (70% to 88% chord)
    # Behind rear spar, TE area
    h3_cx = chord * 0.79
    h3_yu, h3_yl = _y_at_x(scaled, h3_cx)
    h3_h = (h3_yu - h3_yl) * 0.45
    h3_w = chord * 0.10
    if h3_h > 2 and h3_w > 2:
        with BuildPart() as hb3:
            with BuildSketch(Plane.XY.offset(-1)):
                Ellipse(h3_w / 2, h3_h / 2).locate(
                    Location(Pos(h3_cx, (h3_yu + h3_yl) / 2)))
            extrude(amount=rib_thick + 2)
        rib = rib - hb3.part

    # Position at Z
    return rib.locate(Location(Pos(0, 0, z_local)))


def build_dbox_web(
    z1: float, z2: float,
    wing: WingSpec, half_span: float,
    thickness: float = 0.7,
) -> Part:
    """Build D-box spar web between two rib stations.

    This is a vertical wall at the D-box cutoff line (30% chord),
    spanning between two adjacent ribs. It provides torsional
    rigidity for the D-box (closed section: LE skin + web + upper/lower skin).
    """
    sc1, ch1 = _get_profile(z1, wing, half_span)
    sc2, ch2 = _get_profile(z2, wing, half_span)

    dx1 = ch1 * wing.dbox_cutoff
    dx2 = ch2 * wing.dbox_cutoff
    yu1, yl1 = _y_at_x(sc1, dx1)
    yu2, yl2 = _y_at_x(sc2, dx2)

    h1 = (yu1 - yl1) * 0.90
    h2 = (yu2 - yl2) * 0.90
    cy1 = (yu1 + yl1) / 2
    cy2 = (yu2 + yl2) / 2

    span = z2 - z1
    avg_h = (h1 + h2) / 2
    avg_x = (dx1 + dx2) / 2
    avg_y = (cy1 + cy2) / 2

    web = Box(thickness, avg_h, span,
              align=(Align.CENTER, Align.CENTER, Align.MIN))
    return web.locate(Location(Pos(avg_x, avg_y, z1)))


def build_panel(
    panel_index: int = 0,
    wing: WingSpec | None = None,
    spar: SparSpec | None = None,
    show_viewer: bool = False,
) -> dict:
    """Build a complete wing panel.

    Returns dict with:
        'outer': Outer aerodynamic shape (for slicer)
        'ribs': List of solid rib Parts
        'dbox_webs': List of D-box spar web Parts
        'spar': Carbon spar tube visualization
        'compound': All parts combined
        'stats': Mass and dimension statistics
    """
    wing = wing or SAILPLANE.wing
    spar = spar or SAILPLANE.spar
    t0 = time.time()

    panel_span = wing.panel_span
    half_span = wing.half_span
    root_y = panel_index * panel_span

    # ── 1. Outer shape ──
    outer_faces = []
    for i in range(5):
        z = root_y + i * panel_span / 4
        sc, _ = _get_profile(z, wing, half_span)
        outer_faces.append(_make_airfoil_face(sc, i * panel_span / 4))

    with BuildPart() as obp:
        loft(outer_faces)
    outer = obp.part

    # ── 2. Ribs ──
    rib_spacing = 32.0
    n_ribs = int(panel_span / rib_spacing) + 1
    rib_positions = [root_y + i * rib_spacing for i in range(n_ribs)]

    ribs = []
    for z in rib_positions:
        rib = build_rib(z - root_y, wing, spar, half_span)  # Local Z
        ribs.append(rib)

    # ── 3. D-box webs ──
    webs = []
    for i in range(len(rib_positions) - 1):
        z1 = rib_positions[i] - root_y
        z2 = rib_positions[i + 1] - root_y
        web = build_dbox_web(z1 + wing.rib_thickness, z2,
                             wing, half_span)
        webs.append(web)

    # ── 4. Carbon spar visualization ──
    sc0, ch0 = _get_profile(root_y, wing, half_span)
    sx = ch0 * spar.main_position_chord_fraction
    su, sl = _y_at_x(sc0, sx)
    sy = (su + sl) / 2

    spar_outer = Cylinder(
        spar.main_od / 2, panel_span,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).rotate(Axis.X, 90).locate(Location(Pos(sx, sy, 0)))
    spar_inner = Cylinder(
        spar.main_id / 2, panel_span + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).rotate(Axis.X, 90).locate(Location(Pos(sx, sy, -1)))
    spar_vis = spar_outer - spar_inner

    # ── 5. Statistics ──
    rib_vol = sum(r.volume for r in ribs)
    web_vol = sum(w.volume for w in webs)
    spar_vol = spar_vis.volume

    rib_mass = rib_vol / 1000 * 1.25   # CF-PLA
    web_mass = web_vol / 1000 * 0.80   # LW-PLA
    spar_mass = spar_vol / 1000 * 1.60  # Carbon
    # Skin mass estimated from slicer (2 perimeters × 0.25mm = 0.5mm wall)
    # Approximate: outer surface area × 0.5mm × LW-PLA density
    skin_area = outer.area  # mm²
    skin_vol = skin_area * wing.skin_thickness  # mm³ (rough)
    skin_mass = skin_vol / 1000 * 0.80

    total = rib_mass + web_mass + spar_mass + skin_mass

    bb = outer.bounding_box()
    elapsed = time.time() - t0

    stats = {
        'panel_index': panel_index,
        'build_time_s': elapsed,
        'rib_count': len(ribs),
        'rib_mass_g': rib_mass,
        'web_mass_g': web_mass,
        'spar_mass_g': spar_mass,
        'skin_mass_g': skin_mass,
        'total_mass_g': total,
        'chord_root_mm': wing.chord_at(root_y / half_span),
        'chord_tip_mm': wing.chord_at((root_y + panel_span) / half_span),
        'bb': bb,
    }

    print(f"  Panel {panel_index}: {elapsed:.1f}s | "
          f"ribs={rib_mass:.1f}g webs={web_mass:.1f}g skin≈{skin_mass:.1f}g "
          f"spar={spar_mass:.1f}g → total≈{total:.1f}g")

    # ── 6. Compound ──
    compound = Compound(children=ribs + webs + [outer, spar_vis])
    compound.label = f"WingPanel_{panel_index}"

    # Assembly joints
    RigidJoint("root", compound, Location(Pos(0, 0, 0)))
    RigidJoint("tip", compound, Location(Pos(0, 0, panel_span)))

    if show_viewer:
        _show_panel(ribs, webs, outer, spar_vis)

    return {
        'outer': outer,
        'ribs': ribs,
        'dbox_webs': webs,
        'spar': spar_vis,
        'compound': compound,
        'stats': stats,
    }


def _show_panel(ribs, webs, outer, spar_vis):
    """Display panel in OCP viewer with proper colors."""
    try:
        from ocp_vscode import show, set_port, Camera
        set_port(3939)
        parts = ribs + webs + [outer, spar_vis]
        names = ([f"rib_{i}" for i in range(len(ribs))] +
                 [f"dbox_{i}" for i in range(len(webs))] +
                 ["skin_outer", "carbon_spar"])
        colors = (["orange"] * len(ribs) +
                  ["green"] * len(webs) +
                  ["lightblue", "black"])
        alphas = ([1.0] * len(ribs) +
                  [1.0] * len(webs) +
                  [0.15, 1.0])
        show(*parts, names=names, colors=colors, alphas=alphas,
             reset_camera=Camera.RESET)
    except Exception as e:
        print(f"  OCP viewer error: {e}")


def build_all_panels(show_viewer: bool = False) -> list[dict]:
    """Build all 5 panels for one half-wing."""
    results = []
    for i in range(5):
        result = build_panel(i, show_viewer=(show_viewer and i == 0))
        results.append(result)

    total_mass = sum(r['stats']['total_mass_g'] for r in results)
    print(f"\nHalf-wing total: {total_mass:.1f}g × 2 = {total_mass * 2:.1f}g (both halves)")
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "all":
        results = build_all_panels(show_viewer=True)
    else:
        idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
        result = build_panel(idx, show_viewer=True)
        export_step(result['compound'], f"exports/step/wing_panel_{idx}.step")
