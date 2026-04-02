"""
Wing Panel P2-P5 Component Drawings
=====================================
Generates 2D technical drawings (DXF + PNG) for wing panels P2 through P5.
Each panel gets its own folder, DXF, PNG, and COMPONENT_INFO.md.

All geometry from DESIGN_CONSENSUS.md (Wing Assembly).
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from src.cad.airfoils import get_airfoil, blend_airfoils, resample_airfoil, scale_airfoil, max_thickness
from src.core.dxf_utils import setup_drawing, save_dxf_and_png
from src.cad.drawing.orientation import TopViewMapper, validate_orientation
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════
# SHARED GEOMETRY (from DESIGN_CONSENSUS.md)
# ══════════════════════════════════════════════════════════════════════

HALF_SPAN = 1280.0
PANEL_SPAN = 256.0
ROOT_CHORD = 210.0
TIP_CHORD = 115.0

# Consensus chord schedule
_CHORD_SPANS = np.array([0, 256, 512, 640, 768, 896, 1024, 1152, 1216, 1280], dtype=float)
_CHORD_VALUES = np.array([210, 204, 198, 192, 186, 180, 168, 156, 144, 115], dtype=float)

# Consensus blend schedule (AG03 fraction)
_BLEND_SPANS = np.array([0, 256, 512, 640, 768, 896, 1024, 1152, 1216, 1280], dtype=float)
_BLEND_AG03  = np.array([0.00, 0.10, 0.20, 0.30, 0.45, 0.60, 0.75, 0.85, 0.92, 1.00])

# Spar
MAIN_SPAR_FRAC = 0.25
MAIN_SPAR_OD = 8.0
MAIN_SPAR_ID = 6.0
MAIN_SPAR_P5_FRAC = 0.27   # P5 spar offset to 27% chord
MAIN_SPAR_P5_DIA = 5.0     # P5: 5mm CF rod (solid)
REAR_SPAR_FRAC = 0.60
REAR_SPAR_W = 5.0
REAR_SPAR_H = 3.0

# Control surfaces
HINGE_FRAC = 0.72
FLAP_CHORD_FRAC = 0.28
DBOX_FRAC = 0.30

# Dihedral schedule (consensus)
DIHEDRAL_CHANGES = {
    # joint_name: (change_deg, cumulative_deg)
    "P1/P2": (0.0, 0.0),
    "P2/P3": (0.0, 0.0),
    "P3/P4": (1.5, 1.5),
    "P4/P5": (2.5, 4.0),
    "P5_tip": (3.0, 7.0),
}

# Servo (9g standard for P2-P4)
SERVO_W = 23.0
SERVO_H = 12.0
SERVO_D = 11.0

# Servo (5g low-profile for P5)
SERVO_P5_W = 20.0
SERVO_P5_H = 10.0
SERVO_P5_D = 7.0


def chord_at_span(span_mm):
    return float(np.interp(span_mm, _CHORD_SPANS, _CHORD_VALUES))

def ag03_blend_at_span(span_mm):
    return float(np.interp(span_mm, _BLEND_SPANS, _BLEND_AG03))

def twist_at_frac(eta):
    """twist(eta) = -4.0 * eta^2.5"""
    return -4.0 * eta ** 2.5

def twist_at_span(span_mm):
    return twist_at_frac(span_mm / HALF_SPAN)

def le_x_at_span(span_mm, spar_frac=MAIN_SPAR_FRAC):
    """LE position relative to root LE. Spar is straight datum."""
    c = chord_at_span(span_mm)
    root_spar_x = MAIN_SPAR_FRAC * ROOT_CHORD  # 52.5mm
    le = root_spar_x - spar_frac * c
    return le

def get_blended_airfoil(span_mm, n_points=150):
    blend_factor = ag03_blend_at_span(span_mm)
    return blend_airfoils("AG24", "AG03", blend_factor, n_points)

def airfoil_section_points(span_mm, chord, n_pts=80):
    span_frac = span_mm / HALF_SPAN
    coords = get_blended_airfoil(span_mm)
    scaled = scale_airfoil(coords, chord, twist_deg=twist_at_span(span_mm))
    le_idx = np.argmin(scaled[:, 0])
    upper = scaled[:le_idx + 1]
    lower = scaled[le_idx:]
    upper = upper[np.argsort(upper[:, 0])]
    lower = lower[np.argsort(lower[:, 0])]
    x_stations = np.linspace(0, chord, n_pts)
    y_upper = np.interp(x_stations, upper[:, 0], upper[:, 1])
    y_lower = np.interp(x_stations, lower[:, 0], lower[:, 1])
    return list(zip(x_stations, y_upper)), list(zip(x_stations, y_lower))

def y_at_x(scaled, x):
    le_idx = int(np.argmin(scaled[:, 0]))
    upper = scaled[:le_idx + 1][np.argsort(scaled[:le_idx + 1, 0])]
    lower = scaled[le_idx:][np.argsort(scaled[le_idx:, 0])]
    return (float(np.interp(x, upper[:, 0], upper[:, 1])),
            float(np.interp(x, lower[:, 0], lower[:, 1])))


# ══════════════════════════════════════════════════════════════════════
# PANEL SPECIFICATIONS
# ══════════════════════════════════════════════════════════════════════

PANELS = {
    "P2": {
        "name": "Wing_Panel_P2",
        "index": 2,
        "root_station": 256.0,
        "tip_station": 512.0,
        "description": "Second panel, flap continuation",
        "control_type": "Flap",
        "spar_type": "8mm CF tube",
        "spar_od": 8.0,
        "spar_id": 6.0,
        "spar_frac": 0.25,
        "has_rear_spar": True,
        "has_servo": False,  # No servo in P2 (flap driven from P1 or P3 servo)
        "servo_type": None,
        "dihedral_inboard": 0.0,
        "dihedral_outboard": 0.0,
        "mass_est": "14.2g",
    },
    "P3": {
        "name": "Wing_Panel_P3",
        "index": 3,
        "root_station": 512.0,
        "tip_station": 768.0,
        "description": "Third panel, flap outboard + polyhedral break at outboard face",
        "control_type": "Flap",
        "spar_type": "8mm CF tube",
        "spar_od": 8.0,
        "spar_id": 6.0,
        "spar_frac": 0.25,
        "has_rear_spar": True,
        "has_servo": True,
        "servo_type": "9g",
        "servo_pos_frac": 0.35,  # 35% chord
        "dihedral_inboard": 0.0,
        "dihedral_outboard": 1.5,
        "mass_est": "14.8g",
    },
    "P4": {
        "name": "Wing_Panel_P4",
        "index": 4,
        "root_station": 768.0,
        "tip_station": 1024.0,
        "description": "Fourth panel, aileron, 8mm spar with transition sleeve at outboard",
        "control_type": "Aileron",
        "spar_type": "8mm CF tube",
        "spar_od": 8.0,
        "spar_id": 6.0,
        "spar_frac": 0.25,
        "has_rear_spar": True,  # Rear spar terminates at P4/P5 joint
        "has_servo": True,
        "servo_type": "9g",
        "servo_pos_frac": 0.35,
        "dihedral_inboard": 1.5,
        "dihedral_outboard": 2.5,
        "mass_est": "13.5g",
    },
    "P5": {
        "name": "Wing_Panel_P5",
        "index": 5,
        "root_station": 1024.0,
        "tip_station": 1280.0,
        "description": "Tip panel, aileron, 5mm CF rod, no rear spar, tip closure",
        "control_type": "Aileron",
        "spar_type": "5mm CF rod",
        "spar_od": 5.0,
        "spar_id": 0.0,  # solid rod
        "spar_frac": 0.27,
        "has_rear_spar": False,
        "has_servo": True,
        "servo_type": "5g",
        "servo_pos_frac": 0.30,  # 30% chord (thickest point)
        "dihedral_inboard": 2.5,
        "dihedral_outboard": 3.0,
        "mass_est": "11.6g",
    },
}


def draw_panel(panel_key: str):
    """Generate DXF + PNG drawing for a wing panel."""
    p = PANELS[panel_key]
    name = p["name"]
    idx = p["index"]
    root_sta = p["root_station"]
    tip_sta = p["tip_station"]
    root_frac = root_sta / HALF_SPAN
    tip_frac = tip_sta / HALF_SPAN
    root_chord = chord_at_span(root_sta)
    tip_chord = chord_at_span(tip_sta)
    root_twist = twist_at_span(root_sta)
    tip_twist = twist_at_span(tip_sta)
    root_blend = ag03_blend_at_span(root_sta)
    tip_blend = ag03_blend_at_span(tip_sta)
    spar_frac = p["spar_frac"]

    # Blend labels
    root_ag24 = int(round((1 - root_blend) * 100))
    root_ag03 = int(round(root_blend * 100))
    tip_ag24 = int(round((1 - tip_blend) * 100))
    tip_ag03 = int(round(tip_blend * 100))

    # Control surface details
    ctrl = p["control_type"]
    root_flap_chord = FLAP_CHORD_FRAC * root_chord
    tip_flap_chord = FLAP_CHORD_FRAC * tip_chord
    root_hinge_x = HINGE_FRAC * root_chord
    tip_hinge_x = HINGE_FRAC * tip_chord

    subtitle = (
        f"Panel {idx} (right half). Span {int(root_sta)}-{int(tip_sta)}mm. "
        f"{root_ag24}/{root_ag03} AG24/AG03 root. {ctrl} 28% chord."
    )
    if p["has_servo"]:
        subtitle += f" Servo {p['servo_type']} mid-panel."

    doc = setup_drawing(
        title=name,
        subtitle=subtitle,
        material="LW-PLA | Vase mode 0.50mm (0.70mm D-box zone) | 230C | Print LE down",
        mass=p["mass_est"],
        scale="1:1",
        sheet_size="A2",
        status="FOR APPROVAL",
        revision="v1",
    )
    msp = doc.modelspace()

    # TopViewMapper - same layout as P1
    m = TopViewMapper(center_x=130, center_y=345)
    errors = validate_orientation(m, PANEL_SPAN, root_chord, side="right")
    assert not errors, f"Orientation validation FAILED: {errors}"

    def D(cx, cy):
        return m.map_half(cx, cy, "right")

    # ── Title ──
    msp.add_text(f"TOP VIEW — WING PANEL {panel_key} (1:1)", height=5.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(0, PANEL_SPAN / 2)[0] - 30, D(0, 0)[1] + 22))

    # ── Orientation arrows ──
    rx, ry = D(root_chord * 0.3, 5)
    msp.add_line((rx, ry), (rx, ry + 25), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry + 25), (rx - 2.5, ry + 21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry + 25), (rx + 2.5, ry + 21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("FWD", height=3.5, dxfattribs={"layer": "ORIENTATION"}).set_placement(
        (rx - 6, ry + 27))

    ix, iy = D(root_chord * 0.3, 5)
    msp.add_line((ix + 30, iy - 5), (ix + 5, iy - 5), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ix + 5, iy - 5), (ix + 9, iy - 3), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ix + 5, iy - 5), (ix + 9, iy - 7), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("INBD", height=2.5, dxfattribs={"layer": "ORIENTATION"}).set_placement(
        (ix + 3, iy - 12))

    # ── Planform outline ──
    n_span = 50
    le_pts_d = []
    te_pts_d = []
    for i in range(n_span + 1):
        y_local = i * PANEL_SPAN / n_span  # local spanwise coordinate within panel
        y_global = root_sta + y_local
        c = chord_at_span(y_global)
        le = le_x_at_span(y_global, spar_frac)
        te = le + c
        le_pts_d.append(D(le, y_local))
        te_pts_d.append(D(te, y_local))

    for i in range(len(le_pts_d) - 1):
        msp.add_line(le_pts_d[i], le_pts_d[i + 1], dxfattribs={"layer": "OUTLINE"})
    for i in range(len(te_pts_d) - 1):
        msp.add_line(te_pts_d[i], te_pts_d[i + 1], dxfattribs={"layer": "OUTLINE"})
    msp.add_line(le_pts_d[0], te_pts_d[0], dxfattribs={"layer": "OUTLINE"})
    msp.add_line(le_pts_d[-1], te_pts_d[-1], dxfattribs={"layer": "OUTLINE"})

    # ── Main spar line (straight at spar_frac chord) ──
    root_spar_x = MAIN_SPAR_FRAC * ROOT_CHORD  # 52.5mm, always from root datum
    # For P5, spar shifts to 27% chord but is still straight
    if panel_key == "P5":
        # P5 spar is at 27% chord - recalculate spar position
        # The spar is a separate 5mm rod, it runs at 27% chord fraction
        # We need to compute its X position at root and tip of P5
        p5_root_spar_x = spar_frac * root_chord + le_x_at_span(root_sta, spar_frac)
        p5_tip_spar_x = spar_frac * tip_chord + le_x_at_span(tip_sta, spar_frac)
        # Draw as two endpoint line (it's straight)
        root_le = le_x_at_span(root_sta, spar_frac)
        tip_le = le_x_at_span(tip_sta, spar_frac)
        # The spar X in planform = le + spar_frac * chord
        spar_root_planform = root_le + spar_frac * root_chord
        spar_tip_planform = tip_le + spar_frac * tip_chord
        # But actually we want the spar to be at a constant X in the global frame.
        # For P5, spar position = the transition sleeve connects at root.
        # The 5mm rod runs STRAIGHT, so pick X at P5 root = 27% of P5 root chord
        spar_x_root = root_le + spar_frac * root_chord
        spar_x_tip = tip_le + spar_frac * tip_chord
        # These are NOT the same X, because le moves and chord changes.
        # But the spar IS straight. Let's use global planform coordinates.
        # Actually, the spar position shifts from 25% to 27% at P4/P5 joint.
        # In the consensus, the 5mm rod is at 27% chord. Since the taper changes
        # chord, the spar line in planform is NOT at constant X. It follows 27% chord.
        spar_pts = []
        for i in range(n_span + 1):
            y_local = i * PANEL_SPAN / n_span
            y_global = root_sta + y_local
            c = chord_at_span(y_global)
            le = le_x_at_span(y_global, spar_frac)
            sx = le + spar_frac * c
            spar_pts.append(D(sx, y_local))
        for i in range(len(spar_pts) - 1):
            msp.add_line(spar_pts[i], spar_pts[i + 1], dxfattribs={"layer": "SPAR"})
        spar_label_frac = f"{int(spar_frac * 100)}%c"
    else:
        # For P1-P4, spar is at constant X = root_spar_x (straight datum)
        msp.add_line(D(root_spar_x, 0), D(root_spar_x, PANEL_SPAN),
                     dxfattribs={"layer": "SPAR"})
        spar_label_frac = "25%c"

    spar_label = f"MAIN SPAR {spar_label_frac}"
    spar_detail = p["spar_type"]
    spar_label_y = 50
    if panel_key == "P5":
        lbl_x = le_x_at_span(root_sta + 50, spar_frac) + spar_frac * chord_at_span(root_sta + 50)
        msp.add_text(spar_label, height=1.8,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(lbl_x, spar_label_y)[0] + 3, D(lbl_x, spar_label_y)[1]))
        msp.add_text(spar_detail, height=1.5,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(lbl_x, spar_label_y + 10)[0] + 3, D(lbl_x, spar_label_y + 10)[1]))
    else:
        msp.add_text(spar_label, height=1.8,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(root_spar_x, spar_label_y)[0] + 3, D(root_spar_x, spar_label_y)[1]))
        msp.add_text(spar_detail, height=1.5,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(root_spar_x, spar_label_y + 10)[0] + 3, D(root_spar_x, spar_label_y + 10)[1]))

    # ── Rear spar line (at 60% chord, curves with taper) ──
    if p["has_rear_spar"]:
        rear_pts = []
        for i in range(n_span + 1):
            y_local = i * PANEL_SPAN / n_span
            y_global = root_sta + y_local
            c = chord_at_span(y_global)
            le = le_x_at_span(y_global, spar_frac)
            rear_x = le + REAR_SPAR_FRAC * c
            rear_pts.append(D(rear_x, y_local))
        for i in range(len(rear_pts) - 1):
            msp.add_line(rear_pts[i], rear_pts[i + 1], dxfattribs={"layer": "SPAR"})
        rx_label = le_x_at_span(root_sta + 50, spar_frac) + REAR_SPAR_FRAC * chord_at_span(root_sta + 50)
        msp.add_text("REAR SPAR 60%c", height=1.8,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(rx_label, 50)[0] + 3, D(rx_label, 50)[1]))
        msp.add_text("5x3mm spruce", height=1.5,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(rx_label, 60)[0] + 3, D(rx_label, 60)[1]))
    elif panel_key == "P5":
        # Note: no rear spar in P5
        no_rear_x = le_x_at_span(root_sta + 50, spar_frac) + REAR_SPAR_FRAC * chord_at_span(root_sta + 50)
        msp.add_text("NO REAR SPAR", height=1.5,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(no_rear_x, 100)[0] + 3, D(no_rear_x, 100)[1]))

    # ── D-box closing web (at 30% chord) ──
    dbox_pts = []
    for i in range(n_span + 1):
        y_local = i * PANEL_SPAN / n_span
        y_global = root_sta + y_local
        c = chord_at_span(y_global)
        le = le_x_at_span(y_global, spar_frac)
        dbox_x = le + DBOX_FRAC * c
        dbox_pts.append(D(dbox_x, y_local))
    for i in range(len(dbox_pts) - 1):
        msp.add_line(dbox_pts[i], dbox_pts[i + 1], dxfattribs={"layer": "CENTERLINE"})
    db_label_x = le_x_at_span(root_sta + 120, spar_frac) + DBOX_FRAC * chord_at_span(root_sta + 120)
    msp.add_text("D-BOX 30%c", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(db_label_x, 120)[0] + 2, D(db_label_x, 120)[1]))

    # ── Hinge line (at 72% chord) ──
    hinge_pts = []
    for i in range(n_span + 1):
        y_local = i * PANEL_SPAN / n_span
        y_global = root_sta + y_local
        c = chord_at_span(y_global)
        le = le_x_at_span(y_global, spar_frac)
        hinge_x = le + HINGE_FRAC * c
        hinge_pts.append(D(hinge_x, y_local))
    for i in range(len(hinge_pts) - 1):
        msp.add_line(hinge_pts[i], hinge_pts[i + 1], dxfattribs={"layer": "SECTION"})
    hg_label_x = le_x_at_span(root_sta + 120, spar_frac) + HINGE_FRAC * chord_at_span(root_sta + 120)
    msp.add_text("HINGE 72%c", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(hg_label_x, 120)[0] + 3, D(hg_label_x, 120)[1]))
    fl_label_x = le_x_at_span(root_sta + 128, spar_frac) + 0.86 * chord_at_span(root_sta + 128)
    msp.add_text(f"{ctrl.upper()} (28%c)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(fl_label_x, 128)[0], D(fl_label_x, 128)[1]))

    # ── Transition sleeve (P4 only, at outboard end) ──
    if panel_key == "P4":
        # Transition sleeve: 10mm OD, 30mm long, inside P4 end-rib
        sleeve_len = 30.0
        sleeve_od = 10.0
        sleeve_start = PANEL_SPAN - sleeve_len
        # Draw rectangle at spar position
        sl_x = root_spar_x
        sl_pts = [
            D(sl_x - sleeve_od / 2, sleeve_start),
            D(sl_x + sleeve_od / 2, sleeve_start),
            D(sl_x + sleeve_od / 2, PANEL_SPAN),
            D(sl_x - sleeve_od / 2, PANEL_SPAN),
        ]
        for i in range(4):
            msp.add_line(sl_pts[i], sl_pts[(i + 1) % 4], dxfattribs={"layer": "HIDDEN"})
        msp.add_text("TRANSITION", height=1.3,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(sl_x, sleeve_start - 5)[0] + 6, D(sl_x, sleeve_start - 5)[1]))
        msp.add_text("SLEEVE 10mm", height=1.3,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(sl_x, sleeve_start - 10)[0] + 6, D(sl_x, sleeve_start - 10)[1]))

    # ── Servo pocket outline (dashed) ──
    if p["has_servo"]:
        servo_y = PANEL_SPAN / 2  # mid-panel
        servo_global = root_sta + servo_y
        servo_chord = chord_at_span(servo_global)
        servo_le = le_x_at_span(servo_global, spar_frac)
        servo_frac = p["servo_pos_frac"]
        servo_cx = servo_le + servo_frac * servo_chord
        if p["servo_type"] == "5g":
            sw, sd = SERVO_P5_W, SERVO_P5_D
            servo_label = "SERVO 5g"
        else:
            sw, sd = SERVO_W, SERVO_D
            servo_label = "SERVO 9g"
        s_pts = [
            D(servo_cx - sd / 2, servo_y - sw / 2),
            D(servo_cx + sd / 2, servo_y - sw / 2),
            D(servo_cx + sd / 2, servo_y + sw / 2),
            D(servo_cx - sd / 2, servo_y + sw / 2),
        ]
        for i in range(4):
            msp.add_line(s_pts[i], s_pts[(i + 1) % 4], dxfattribs={"layer": "HIDDEN"})
        msp.add_text(servo_label, height=1.5,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (D(servo_cx, servo_y + 15)[0], D(servo_cx, servo_y + 15)[1]))

    # ── Labels ──
    root_le_x = le_x_at_span(root_sta, spar_frac)
    msp.add_text("LE", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D(root_le_x - 8, PANEL_SPAN / 2))
    msp.add_text("TE", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D(root_le_x + root_chord + 5, PANEL_SPAN / 2))
    msp.add_text(f"ROOT (y={int(root_sta)})", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        D(root_le_x + root_chord / 2, -8))
    msp.add_text(f"OUTBOARD (y={int(tip_sta)})", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        D(le_x_at_span(tip_sta, spar_frac) + tip_chord / 2, PANEL_SPAN + 6))

    # ── Dimensions ──
    # Root chord
    root_le_pt = le_x_at_span(root_sta, spar_frac)
    root_te_pt = root_le_pt + root_chord
    msp.add_aligned_dim(
        p1=D(root_le_pt, 0), p2=D(root_te_pt, 0),
        distance=-8, dimstyle="AEROFORGE").render()

    # Outboard chord
    tip_le_pt = le_x_at_span(tip_sta, spar_frac)
    tip_te_pt = tip_le_pt + tip_chord
    msp.add_aligned_dim(
        p1=D(tip_le_pt, PANEL_SPAN), p2=D(tip_te_pt, PANEL_SPAN),
        distance=8, dimstyle="AEROFORGE").render()

    # Panel span
    msp.add_aligned_dim(
        p1=D(root_le_pt - 5, 0), p2=D(root_le_pt - 5, PANEL_SPAN),
        distance=8, dimstyle="AEROFORGE").render()

    # Flap chord at root
    hinge_root_abs = root_le_pt + HINGE_FRAC * root_chord
    msp.add_aligned_dim(
        p1=D(hinge_root_abs, -15), p2=D(root_te_pt, -15),
        distance=-12, dimstyle="AEROFORGE").render()

    # ══════════════════════════════════════════════════════════════════
    # CROSS-SECTIONS
    # ══════════════════════════════════════════════════════════════════

    SEC_X = 420.0

    sections = [
        (340, root_sta, f"SEC A - ROOT y={int(root_sta)} ({root_ag24}/{root_ag03} AG24/AG03)",
         root_chord),
        (270, tip_sta, f"SEC B - OUTBOARD y={int(tip_sta)} ({tip_ag24}/{tip_ag03} AG24/AG03)",
         tip_chord),
    ]

    for sy, span_mm, label, chord in sections:
        msp.add_text(label, height=2.3, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X, sy + 18))
        msp.add_text(f"chord={chord:.1f}mm", height=2.0,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X, sy + 14))

        upper_pts, lower_pts = airfoil_section_points(span_mm, chord)

        # Draw airfoil outline
        for i in range(len(upper_pts) - 1):
            msp.add_line(
                (SEC_X + upper_pts[i][0], sy + upper_pts[i][1]),
                (SEC_X + upper_pts[i + 1][0], sy + upper_pts[i + 1][1]),
                dxfattribs={"layer": "OUTLINE"})
            msp.add_line(
                (SEC_X + lower_pts[i][0], sy + lower_pts[i][1]),
                (SEC_X + lower_pts[i + 1][0], sy + lower_pts[i + 1][1]),
                dxfattribs={"layer": "OUTLINE"})

        # LE + TE closure
        msp.add_line(
            (SEC_X + upper_pts[0][0], sy + upper_pts[0][1]),
            (SEC_X + lower_pts[0][0], sy + lower_pts[0][1]),
            dxfattribs={"layer": "OUTLINE"})
        msp.add_line(
            (SEC_X + upper_pts[-1][0], sy + upper_pts[-1][1]),
            (SEC_X + lower_pts[-1][0], sy + lower_pts[-1][1]),
            dxfattribs={"layer": "OUTLINE"})

        # Centerline
        msp.add_line(
            (SEC_X - 5, sy), (SEC_X + chord + 10, sy),
            dxfattribs={"layer": "CENTERLINE"})

        # Main spar bore/rod
        local_spar_frac = p["spar_frac"]
        spar_x = local_spar_frac * chord
        coords_af = get_blended_airfoil(span_mm)
        scaled_af = scale_airfoil(coords_af, chord, twist_deg=twist_at_span(span_mm))
        yu, yl = y_at_x(scaled_af, spar_x)
        spar_cy = (yu + yl) / 2
        msp.add_circle(
            (SEC_X + spar_x, sy + spar_cy), p["spar_od"] / 2,
            dxfattribs={"layer": "SPAR"})
        if p["spar_id"] > 0:
            msp.add_circle(
                (SEC_X + spar_x, sy + spar_cy), p["spar_id"] / 2,
                dxfattribs={"layer": "SPAR"})

        # Spar label
        spar_lbl = p["spar_type"]
        msp.add_text(spar_lbl, height=1.2, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X + spar_x + 5, sy + spar_cy + 1))

        # Rear spar slot
        if p["has_rear_spar"]:
            rear_x = REAR_SPAR_FRAC * chord
            ryu, ryl = y_at_x(scaled_af, rear_x)
            rear_cy = (ryu + ryl) / 2
            rx0 = SEC_X + rear_x - REAR_SPAR_W / 2
            ry0 = sy + rear_cy - REAR_SPAR_H / 2
            msp.add_line((rx0, ry0), (rx0 + REAR_SPAR_W, ry0), dxfattribs={"layer": "SPAR"})
            msp.add_line((rx0 + REAR_SPAR_W, ry0), (rx0 + REAR_SPAR_W, ry0 + REAR_SPAR_H),
                         dxfattribs={"layer": "SPAR"})
            msp.add_line((rx0 + REAR_SPAR_W, ry0 + REAR_SPAR_H), (rx0, ry0 + REAR_SPAR_H),
                         dxfattribs={"layer": "SPAR"})
            msp.add_line((rx0, ry0 + REAR_SPAR_H), (rx0, ry0), dxfattribs={"layer": "SPAR"})
            msp.add_text("5x3 spruce", height=1.2, dxfattribs={"layer": "TEXT"}).set_placement(
                (SEC_X + rear_x + 5, sy + rear_cy + 1))

        # D-box closing web
        dbox_x = DBOX_FRAC * chord
        dyu, dyl = y_at_x(scaled_af, dbox_x)
        msp.add_line(
            (SEC_X + dbox_x, sy + dyl * 0.95),
            (SEC_X + dbox_x, sy + dyu * 0.95),
            dxfattribs={"layer": "CENTERLINE"})

        # Hinge line
        hinge_x = HINGE_FRAC * chord
        hyu, hyl = y_at_x(scaled_af, hinge_x)
        msp.add_line(
            (SEC_X + hinge_x, sy + hyl),
            (SEC_X + hinge_x, sy + hyu),
            dxfattribs={"layer": "SECTION"})
        msp.add_text("hinge", height=1.3, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X + hinge_x + 2, sy + hyu + 1))

        # Chord dimension
        msp.add_linear_dim(
            base=(SEC_X + chord / 2, sy - abs(yl) - 8),
            p1=(SEC_X, sy), p2=(SEC_X + chord, sy),
            dimstyle="AEROFORGE").render()

        # Max thickness annotation
        af = get_blended_airfoil(span_mm)
        t_max, t_pos = max_thickness(af)
        depth_mm = t_max * chord
        msp.add_text(f"t/c={t_max*100:.1f}% ({depth_mm:.1f}mm) @ {t_pos*100:.0f}%c",
                     height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X + chord + 5, sy + 4))

    # ══════════════════════════════════════════════════════════════════
    # NOTES
    # ══════════════════════════════════════════════════════════════════

    notes_x = 25.0
    notes_y = 120.0

    # Build panel-specific notes
    notes = ["NOTES:"]
    notes.append(f"1. All dims mm. Right half only; Left = mirror.")
    notes.append(f"2. Airfoil: {root_ag24}/{root_ag03} AG24/AG03 (root y={int(root_sta)}) "
                 f"to {tip_ag24}/{tip_ag03} (outboard y={int(tip_sta)}).")
    notes.append(f"3. MAIN SPAR: {p['spar_type']} at {int(p['spar_frac']*100)}% chord"
                 f"{' (straight)' if panel_key != 'P5' else ''}.")

    if p["has_rear_spar"]:
        rear_note = "4. REAR SPAR: 5x3mm spruce strip at 60% chord."
        if panel_key == "P4":
            rear_note += " Terminates at outboard face."
        notes.append(rear_note)
    else:
        notes.append("4. NO REAR SPAR in P5. D-box provides torsion alone.")

    notes.append(f"5. D-BOX: LE to 30% chord, wall 0.70mm. Rest 0.50mm vase.")
    notes.append(f"6. HINGE: TPU living hinge at 72% chord. {ctrl} chord = 28%.")

    if p["has_servo"]:
        servo_str = p["servo_type"]
        mid_y = int(root_sta + PANEL_SPAN / 2)
        sfrac = int(p["servo_pos_frac"] * 100)
        if servo_str == "5g":
            notes.append(f"7. SERVO: 5g low-profile (7mm height) at mid-panel (y={mid_y}), {sfrac}% chord.")
        else:
            notes.append(f"7. SERVO: 9g digital metal gear at mid-panel (y={mid_y}), {sfrac}% chord.")
    else:
        notes.append(f"7. NO SERVO in {panel_key}. {ctrl} driven from adjacent panel servo.")

    # Joint notes
    inbd_dih = p["dihedral_inboard"]
    outbd_dih = p["dihedral_outboard"]
    notes.append(f"8. JOINT INBOARD: {inbd_dih:.1f} deg dihedral. "
                 f"OUTBOARD: {outbd_dih:.1f} deg dihedral.")
    notes.append(f"9. TWIST: {root_twist:.1f} deg (root y={int(root_sta)}) to "
                 f"{tip_twist:.1f} deg (outboard y={int(tip_sta)}).")

    if panel_key == "P4":
        notes.append("10. TRANSITION SLEEVE: 10mm OD, 30mm long at outboard end-rib.")
    elif panel_key == "P5":
        notes.append(f"10. TIP CLOSURE: Integrated into P5 tip. Winglet attaches here.")
    else:
        notes.append(f"10. Panel fits Bambu 256x256mm bed (span=256mm, chord max={root_chord:.0f}mm).")

    for i, note in enumerate(notes):
        h = 2.0 if i == 0 else 1.8
        msp.add_text(note, height=h, dxfattribs={"layer": "TEXT"}).set_placement(
            (notes_x, notes_y - i * 5))

    # ══════════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════════

    folder = f"cad/components/wing/{name}"
    os.makedirs(folder, exist_ok=True)
    dxf_path = f"{folder}/{name}_drawing.dxf"
    save_dxf_and_png(doc, dxf_path, dpi=200)
    print(f"\n[{panel_key}] Drawing saved to {dxf_path}")

    return p


def write_component_info(panel_key: str, p: dict):
    """Write COMPONENT_INFO.md for a panel."""
    name = p["name"]
    idx = p["index"]
    root_sta = p["root_station"]
    tip_sta = p["tip_station"]
    root_chord = chord_at_span(root_sta)
    tip_chord = chord_at_span(tip_sta)
    root_twist = twist_at_span(root_sta)
    tip_twist = twist_at_span(tip_sta)
    root_blend = ag03_blend_at_span(root_sta)
    tip_blend = ag03_blend_at_span(tip_sta)
    root_ag24 = int(round((1 - root_blend) * 100))
    root_ag03 = int(round(root_blend * 100))
    tip_ag24 = int(round((1 - tip_blend) * 100))
    tip_ag03 = int(round(tip_blend * 100))
    ctrl = p["control_type"]

    # Compute flap/aileron chords
    root_ctrl_chord = FLAP_CHORD_FRAC * root_chord
    tip_ctrl_chord = FLAP_CHORD_FRAC * tip_chord
    root_hinge = HINGE_FRAC * root_chord
    tip_hinge = HINGE_FRAC * tip_chord

    # Spar bore size
    spar_bore = p["spar_od"] + 2 * 0.15  # 0.15mm clearance per side

    # Mass breakdown estimate (scale from P1)
    # P1 shell+dbox = 7.4g for 210mm chord, ~256mm span
    # Scale by chord ratio
    avg_chord = (root_chord + tip_chord) / 2
    p1_avg = (210 + 204) / 2
    shell_mass = 7.4 * (avg_chord / p1_avg)
    rib_mass = 5.5 * (avg_chord / p1_avg)
    servo_mass = 2.5 if p["has_servo"] else 0.0
    panel_mass = shell_mass + rib_mass + servo_mass

    # Position labels
    ordinal = {2: "Second", 3: "Third", 4: "Fourth", 5: "Tip"}[idx]
    wall_vase = "0.50"
    wall_dbox = "0.70"

    # Joint descriptions
    inbd_joint = f"{'Female groove 3.2mm' if idx > 1 else 'Fuselage saddle'}"
    outbd_joint = f"Male tongue 3.0mm, 2mm deep"
    inbd_dih = f"{p['dihedral_inboard']:.1f}"
    outbd_dih = f"{p['dihedral_outboard']:.1f}"

    # P5 specifics
    tip_note = ""
    if panel_key == "P5":
        tip_note = "\n6. Winglet attaches at tip face (80mm height, NACA 0006, 75 deg cant)."
        outbd_joint = "Tip closure (integrated). Winglet attach point."

    spar_tunnel_size = f"{spar_bore:.1f}mm bore ({p['spar_od']}mm + 0.15mm clearance/side)"
    if panel_key == "P5":
        spar_tunnel_size = f"{spar_bore:.1f}mm bore ({p['spar_od']}mm rod + 0.15mm clearance/side)"

    content = f"""# {name} -- Component Information

## Overview

{ordinal} panel of the right half-wing (Panel {idx} of 5). Span station
{int(root_sta)}-{int(tip_sta)}mm from wing root. The left wing uses a mirrored copy
of this component; no separate left-side component folder exists.

## Specifications

| Parameter | Value |
|-----------|-------|
| **Span station** | {int(root_sta)} - {int(tip_sta)}mm (from wing root) |
| **Span** | 256mm (exact Bambu bed fit) |
| **Root chord** | {root_chord:.0f}mm (at P{idx-1}/P{idx} joint) |
| **Outboard chord** | {tip_chord:.0f}mm (at {'P'+str(idx)+'/P'+str(idx+1)+' joint' if idx < 5 else 'wing tip'}) |
| **Root airfoil** | {root_ag24}% AG24 / {root_ag03}% AG03 blend |
| **Outboard airfoil** | {tip_ag24}% AG24 / {tip_ag03}% AG03 blend |
| **Twist** | {root_twist:.1f} deg (root) to {tip_twist:.1f} deg (outboard) |
| **Dihedral** | {inbd_dih} deg (inboard face) / {outbd_dih} deg (outboard face) |

## Structural Features

| Feature | Specification |
|---------|---------------|
| **Main spar** | {p['spar_type']} at {int(p['spar_frac']*100)}% chord |
| **Rear spar** | {'5x3mm spruce strip at 60% chord' if p['has_rear_spar'] else 'None (D-box provides torsion)'} |
| **D-box** | LE to 30% chord, {wall_dbox}mm wall thickness |
| **Shell wall** | {wall_vase}mm vase mode ({wall_dbox}mm in D-box zone) |
| **Ribs** | 5-6 ribs at ~32mm spacing, CF-PLA lattice |
| **Joint (inboard)** | {inbd_joint}. {inbd_dih} deg dihedral |
| **Joint (outboard)** | {outbd_joint}. {outbd_dih} deg dihedral |
| **Spar tunnel** | {spar_tunnel_size} |

## Control Surface

| Feature | Specification |
|---------|---------------|
| **Type** | {ctrl} |
| **Chord fraction** | 28% of local chord |
| **Hinge position** | 72% chord |
| **{ctrl} chord** | {root_ctrl_chord:.0f}mm (root) to {tip_ctrl_chord:.0f}mm (outboard) |
| **Hinge type** | TPU living hinge, 0.6mm, full span |
| **Gap seal** | 0.5mm TPU overlap on upper surface |
"""

    if p["has_servo"]:
        servo_y = int(root_sta + PANEL_SPAN / 2)
        sfrac = int(p["servo_pos_frac"] * 100)
        if p["servo_type"] == "5g":
            servo_desc = "5g low-profile digital (7mm height)"
            servo_pocket = "20mm x 10mm cutout in shell"
        else:
            servo_desc = "9g digital metal gear"
            servo_pocket = "23mm x 11mm cutout in shell, CF-PETG mount frame"
        content += f"""
## Servo

| Feature | Specification |
|---------|---------------|
| **Type** | {servo_desc} |
| **Position** | Mid-panel (y={servo_y}mm), {sfrac}% chord |
| **Drives** | {panel_key} {ctrl.lower()} via direct pushrod |
| **Pocket** | {servo_pocket} |
"""
    else:
        content += f"""
## Servo

No dedicated servo in {panel_key}. The {ctrl.lower()} is driven from the adjacent
panel servo via torque rod linkage.
"""

    content += f"""
## Mass Estimate

| Component | Mass (g) |
|-----------|----------|
| Shell + D-box | {shell_mass:.1f} |
| Ribs (CF-PLA) | {rib_mass:.1f} |
| Servo mount | {servo_mass:.1f} |
| **Panel total** | **{panel_mass:.1f}** |

(Spar, rear spar, servo, and joint hardware counted separately in wing budget.)

## Manufacturing

| Parameter | Value |
|-----------|-------|
| **Material** | LW-PLA (foamed at 230C) |
| **Print mode** | Vase mode {wall_vase}mm ({wall_dbox}mm in D-box zone) |
| **Orientation** | LE down (LE at build plate edge) |
| **Bed usage** | 256mm x {root_chord:.0f}mm (fits 256x256 bed) |
| **Print time** | ~2.5 hours |
| **Supports** | None required |

## Notes

1. This component represents the RIGHT half panel only. Left = mirror at assembly time.
2. The airfoil blend is continuous -- every rib station has a unique blended AG24/AG03 profile.
3. The main spar is a STRAIGHT datum line. The LE and TE curves follow the planform
   around the spar position.
4. Twist distribution follows twist(eta) = -4.0 * eta^2.5 (non-linear washout).
5. Dihedral is built into the joint face geometry, NOT bent into the spar.{tip_note}

## References

- Design consensus: `cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md`
- Airfoil data: `src/cad/airfoils/ag24.dat`, `src/cad/airfoils/ag03.dat`
- Panel builder: `src/cad/wing/panel.py`
- Drawing: `{name}_drawing.dxf` / `.png`

## Status

| Phase | Status |
|-------|--------|
| Design consensus | COMPLETE (Wing Assembly DESIGN_CONSENSUS.md) |
| 2D Drawing | COMPLETE (v1, FOR APPROVAL) |
| 3D Model | NOT STARTED |
| Mesh + 3MF | NOT STARTED |
| Renders | NOT STARTED |
| Validation | PENDING (drawing review) |
"""

    folder = f"cad/components/wing/{name}"
    os.makedirs(folder, exist_ok=True)
    info_path = os.path.join(folder, "COMPONENT_INFO.md")
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[{panel_key}] COMPONENT_INFO.md written to {info_path}")


def main():
    for key in ["P2", "P3", "P4", "P5"]:
        print(f"\n{'='*60}")
        print(f"  Drawing {key}")
        print(f"{'='*60}")
        p = draw_panel(key)
        write_component_info(key, p)

    print("\n\nAll 4 panel drawings complete.")


if __name__ == "__main__":
    main()
