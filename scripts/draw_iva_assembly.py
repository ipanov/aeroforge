"""
Generate the top-level Iva Aeroforge aircraft assembly drawing.

This sheet is the top-down aircraft parent drawing. The plan view uses wingspan
horizontal on the sheet, the fuselage runs vertically through the plan, and the
side view stays horizontal below it.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from draw_top_level_assemblies import (
    COMPONENT_LAYOUT,
    FULL_SPAN,
    FUSELAGE_GAP,
    FUSELAGE_LENGTH,
    FUSELAGE_PLAN_HALF,
    FUSELAGE_SIDE_BODY_BOTTOM,
    FUSELAGE_SIDE_BODY_TOP,
    HALF_SPAN,
    HSTAB_HALF_SPAN,
    HSTAB_ROOT_CHORD,
    HSTAB_ROOT_LE,
    HSTAB_REF_FRAC,
    HSTAB_REF_X,
    HSTAB_SUPERELLIPSE_N,
    HSTAB_TE_FRAC,
    ROOT_CHORD,
    add_aircraft_wing_planform_horizontal,
    add_airfoil_outline_from_dat,
    add_fuselage_side_outline,
    add_hstab_attach_marker_side,
    add_tip_cap,
    add_rect_outline,
    add_wing_front_view,
    fuselage_dim_at,
    hstab_attach_station_x,
    schedule_value,
    save_dxf_and_png,
    setup_drawing,
    wing_thickness_at_span,
)

ROOT = Path(__file__).resolve().parent.parent
IVA_OUT = ROOT / "cad/assemblies/Iva_Aeroforge/Iva_Aeroforge_drawing.dxf"


def add_rotated_fuselage_top_outline(msp, center_x: float, top_y: float, scale: float) -> None:
    right = [(center_x + half_w * scale, top_y + x_mm * scale) for x_mm, half_w in FUSELAGE_PLAN_HALF]
    left = [(center_x - half_w * scale, top_y + x_mm * scale) for x_mm, half_w in FUSELAGE_PLAN_HALF]
    msp.add_lwpolyline(right, dxfattribs={"layer": "OUTLINE"})
    msp.add_lwpolyline(left, dxfattribs={"layer": "OUTLINE"})
    msp.add_line((center_x, top_y - 10), (center_x, top_y + (FUSELAGE_LENGTH + 14) * scale), dxfattribs={"layer": "CENTERLINE"})


def add_rotated_hstab_top_view(msp, center_x: float, top_y: float, scale: float) -> None:
    half_span = HSTAB_HALF_SPAN
    root_le = HSTAB_ROOT_LE
    left_le = []
    left_te = []
    right_le = []
    right_te = []
    for idx in range(17):
        y_local = half_span * idx / 16
        eta = min(1.0, y_local / half_span)
        chord = HSTAB_ROOT_CHORD * (1.0 - eta**HSTAB_SUPERELLIPSE_N) ** (1.0 / HSTAB_SUPERELLIPSE_N) if eta < 1.0 else 0.0
        x_le = HSTAB_REF_X - HSTAB_REF_FRAC * chord
        x_te = HSTAB_REF_X + (1.0 - HSTAB_REF_FRAC) * chord * HSTAB_TE_FRAC
        left_le.append((center_x - y_local * scale, top_y + (root_le + x_le) * scale))
        left_te.append((center_x - y_local * scale, top_y + (root_le + x_te) * scale))
        if idx > 0:
            right_le.append((center_x + y_local * scale, top_y + (root_le + x_le) * scale))
            right_te.append((center_x + y_local * scale, top_y + (root_le + x_te) * scale))

    msp.add_lwpolyline(left_le[::-1] + right_le, dxfattribs={"layer": "OUTLINE"})
    msp.add_lwpolyline(left_te[::-1] + right_te, dxfattribs={"layer": "OUTLINE"})
    tip_chord = HSTAB_ROOT_CHORD * (1.0 - ((half_span - 4.0) / half_span) ** HSTAB_SUPERELLIPSE_N) ** (1.0 / HSTAB_SUPERELLIPSE_N)
    tip_upper = top_y + (root_le + HSTAB_REF_X - HSTAB_REF_FRAC * tip_chord) * scale
    tip_lower = top_y + (root_le + HSTAB_REF_X + (1.0 - HSTAB_REF_FRAC) * tip_chord * HSTAB_TE_FRAC) * scale
    add_tip_cap(msp, center_x + half_span * scale, tip_upper, tip_lower, 1)
    add_tip_cap(msp, center_x - half_span * scale, tip_upper, tip_lower, -1)
    hinge_y = top_y + (root_le + 60.0) * scale
    msp.add_line((center_x - (half_span - 3) * scale, hinge_y), (center_x + (half_span - 3) * scale, hinge_y), dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("HSTAB 446 span", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement((center_x + 232 * scale, top_y + 935 * scale))


def add_rotated_component_envelope_top(msp, center_x: float, top_y: float, scale: float, key: str) -> None:
    item = COMPONENT_LAYOUT[key]
    y_start = top_y + float(item["x"]) * scale
    y_end = top_y + (float(item["x"]) + float(item["length"])) * scale
    half_w = float(item["width"]) * scale / 2
    cx = center_x + float(item["y"]) * scale
    add_rect_outline(msp, cx - half_w, y_start, cx + half_w, y_end, "HIDDEN")
    msp.add_text(str(item["label"]), height=1.25, dxfattribs={"layer": "TEXT"}).set_placement((cx + half_w + 2, y_start + 2))


def add_aircraft_component_envelopes_top(msp, center_x: float, top_y: float, scale: float) -> None:
    for key in ["motor", "esc", "xt60", "battery", "receiver", "elev_servo", "rudd_servo"]:
        add_rotated_component_envelope_top(msp, center_x, top_y, scale, key)


def add_aircraft_component_envelopes_side(msp, x0: float, y0: float, scale: float) -> None:
    for key in ["spinner", "motor", "esc", "xt60", "battery", "receiver", "elev_servo", "rudd_servo"]:
        item = COMPONENT_LAYOUT[key]
        x_start = x0 + float(item["x"]) * scale
        x_end = x0 + (float(item["x"]) + float(item["length"])) * scale
        half_h = float(item["height"]) * scale / 2
        cy = y0 + float(item["z"]) * scale
        add_rect_outline(msp, x_start, cy - half_h, x_end, cy + half_h, "HIDDEN")
        msp.add_text(str(item["label"]), height=1.2, dxfattribs={"layer": "TEXT"}).set_placement((x_start + 1, cy + half_h + 1.5))


def rotate_point(px: float, py: float, ox: float, oy: float, angle_deg: float) -> tuple[float, float]:
    ang = math.radians(angle_deg)
    dx = px - ox
    dy = py - oy
    return (
        ox + dx * math.cos(ang) - dy * math.sin(ang),
        oy + dx * math.sin(ang) + dy * math.cos(ang),
    )


def add_wing_root_fairing_side(msp, x0: float, y0: float, scale: float, wing_le_station: float = 260.0, incidence_deg: float = 1.5) -> None:
    chord = ROOT_CHORD * scale
    thickness = wing_thickness_at_span(0.0) * scale
    le_x = x0 + wing_le_station * scale
    cy = y0 + 3.0
    qcx = le_x + 0.25 * chord
    add_airfoil_outline_from_dat(msp, le_x, cy, chord, "ag24", rotation_deg=incidence_deg, layer="OUTLINE")

    upper_fair = [
        (x0 + (wing_le_station - 28) * scale, y0 + schedule_value(FUSELAGE_SIDE_BODY_TOP, wing_le_station - 28) * scale),
        (x0 + (wing_le_station - 8) * scale, cy + thickness * 0.22),
        (x0 + (wing_le_station + 56) * scale, cy + thickness * 0.34),
        (x0 + (wing_le_station + 112) * scale, y0 + schedule_value(FUSELAGE_SIDE_BODY_TOP, wing_le_station + 112) * scale),
    ]
    lower_fair = [
        (x0 + (wing_le_station - 20) * scale, y0 + schedule_value(FUSELAGE_SIDE_BODY_BOTTOM, wing_le_station - 20) * scale),
        (x0 + (wing_le_station + 4) * scale, cy - thickness * 0.24),
        (x0 + (wing_le_station + 70) * scale, cy - thickness * 0.32),
        (x0 + (wing_le_station + 120) * scale, y0 + schedule_value(FUSELAGE_SIDE_BODY_BOTTOM, wing_le_station + 120) * scale),
    ]
    msp.add_lwpolyline(upper_fair, dxfattribs={"layer": "OUTLINE"})
    msp.add_lwpolyline(lower_fair, dxfattribs={"layer": "OUTLINE"})

    chord_line_start = rotate_point(le_x, cy, qcx, cy, incidence_deg)
    chord_line_end = rotate_point(le_x + chord, cy, qcx, cy, incidence_deg)
    msp.add_line(chord_line_start, chord_line_end, dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("AG24 ROOT AIRFOIL / FAIRING  +1.5deg", height=1.4, dxfattribs={"layer": "TEXT"}).set_placement((le_x - 8, cy + thickness * 0.9))


def draw_iva_assembly() -> tuple[str, str]:
    doc = setup_drawing(
        title="Iva_Aeroforge",
        subtitle="Aircraft parent sheet. Plan view span horizontal; side view and front view orthographic companions.",
        material="LW-PLA printed airframe + CF spars/longerons + off-the-shelf power/electronics",
        mass="Top-level integration baseline",
        scale="plan 1:6, side 1:3",
        sheet_size="A1",
        status="TOP-DOWN REFINEMENT",
        revision="v4",
        orientation_labels={"fwd": "FWD", "inbd": "CL"},
    )
    msp = doc.modelspace()

    plan_scale = 0.22
    side_scale = 0.24
    front_scale = 0.17

    plan_center_x = 350.0
    plan_top_y = 170.0
    front_center_x = 350.0
    front_y0 = 298.0
    side_x0 = 210.0
    side_y0 = 112.0

    msp.add_text("TOP VIEW — AIRCRAFT PLANFORM", height=4.0, dxfattribs={"layer": "TEXT"}).set_placement((82, 424))
    add_rotated_fuselage_top_outline(msp, plan_center_x, plan_top_y, plan_scale)
    add_aircraft_wing_planform_horizontal(msp, plan_center_x, plan_top_y, plan_scale, show_upper_servos=False)
    add_rotated_hstab_top_view(msp, plan_center_x, plan_top_y, plan_scale)
    add_aircraft_component_envelopes_top(msp, plan_center_x, plan_top_y, plan_scale)
    attach_y = plan_top_y + hstab_attach_station_x() * plan_scale
    msp.add_line((plan_center_x - 12, attach_y), (plan_center_x + 12, attach_y), dxfattribs={"layer": "SECTION"})
    msp.add_text("HSTAB ATTACH", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement((plan_center_x + 16, attach_y - 3))

    wing_gap_y = plan_top_y + 260 * plan_scale
    msp.add_text("Center gap 38", height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((plan_center_x + 18, wing_gap_y - 6))
    msp.add_line((plan_center_x - (FUSELAGE_GAP / 2) * plan_scale, wing_gap_y), (plan_center_x + (FUSELAGE_GAP / 2) * plan_scale, wing_gap_y), dxfattribs={"layer": "SECTION"})

    msp.add_text("FRONT VIEW — DIHEDRAL / FUSELAGE STACK", height=3.7, dxfattribs={"layer": "TEXT"}).set_placement((260, 332))
    add_wing_front_view(msp, front_center_x, front_y0, front_scale, full=True)
    saddle_w = fuselage_dim_at(260.0, 1) * front_scale
    saddle_h = fuselage_dim_at(260.0, 2) * front_scale
    msp.add_ellipse((front_center_x, front_y0), major_axis=(saddle_w / 2, 0), ratio=(saddle_h / saddle_w) if saddle_w else 1.0, dxfattribs={"layer": "OUTLINE"})
    msp.add_line((front_center_x, front_y0 - saddle_h / 2 - 8), (front_center_x, front_y0 + saddle_h / 2 + 8), dxfattribs={"layer": "CENTERLINE"})
    add_rect_outline(msp, front_center_x - 9, front_y0 - 70, front_center_x + 9, front_y0 - 20, "OUTLINE")
    msp.add_line((front_center_x, front_y0 - 70), (front_center_x, front_y0 - 20), dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((front_center_x - 48, front_y0 - 30), (front_center_x + 48, front_y0 - 30), dxfattribs={"layer": "OUTLINE"})
    msp.add_text("Fuselage @ wing station", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement((front_center_x - 42, front_y0 + 20))

    msp.add_text("SIDE VIEW — FUSELAGE / FIN / TAIL", height=4.0, dxfattribs={"layer": "TEXT"}).set_placement((side_x0, side_y0 + 58))
    add_fuselage_side_outline(msp, side_x0, side_y0, side_scale)
    add_hstab_attach_marker_side(msp, side_x0, side_y0, side_scale)
    add_aircraft_component_envelopes_side(msp, side_x0, side_y0, side_scale)
    add_wing_root_fairing_side(msp, side_x0, side_y0, side_scale)

    msp.add_linear_dim(
        base=(side_x0 + 126, 92),
        p1=(side_x0, 84),
        p2=(side_x0 + FUSELAGE_LENGTH * side_scale, 84),
        dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"},
    ).render()
    msp.add_linear_dim(
        base=(plan_center_x, 452),
        p1=(plan_center_x - FULL_SPAN * plan_scale / 2 - FUSELAGE_GAP * plan_scale / 2, 444),
        p2=(plan_center_x + FULL_SPAN * plan_scale / 2 + FUSELAGE_GAP * plan_scale / 2, 444),
        dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"},
    ).render()

    msp.add_text("Aircraft datum: nose tip = X0 | Wing LE = X260 | HStab c/4 = X946 | fuselage TE = X1088", height=1.9, dxfattribs={"layer": "TEXT"}).set_placement((45, 24))
    msp.add_text("Active wing candidate: span 2816 | root chord 170 | tip chord 85 | tighter superelliptic taper.", height=1.9, dxfattribs={"layer": "TEXT"}).set_placement((45, 38))
    msp.add_text("Active tail candidate: span 446 | root chord 118 | area ~4.21 dm^2 | higher / aft mount.", height=1.9, dxfattribs={"layer": "TEXT"}).set_placement((45, 52))
    msp.add_text("Benchmark packaging pass: motor + ESC + LiPo stay in the forward pod; receiver moves under the wing; fuse servos stay central.", height=1.9, dxfattribs={"layer": "TEXT"}).set_placement((45, 66))
    msp.add_text("Major component envelopes shown for packaging and CG sanity only; vendor geometry is still not owned here.", height=1.9, dxfattribs={"layer": "TEXT"}).set_placement((45, 80))

    return save_dxf_and_png(doc, str(IVA_OUT), dpi=240)


if __name__ == "__main__":
    draw_iva_assembly()
