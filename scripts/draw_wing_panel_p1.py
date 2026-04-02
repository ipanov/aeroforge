"""
Wing_Panel_P1 Component Drawing
================================
Root panel of the right half-wing, span station 0-256mm.
Airfoil: AG24 (root, 100%) blending to 90/10 AG24/AG03 (outboard end).
Chord: 210mm (root) to 191mm (outboard end).
Spar: 8mm CF tube at 25% chord.
Rear spar: 5x3mm spruce at 60% chord.
Control surface: Flap (28% chord), hinge at 72% chord.
Servo: 9g digital metal gear at mid-panel, 35% chord.

Drawing layout (A2 sheet, 1:1 scale):
  - TOP VIEW (planform): LE at top, root at right, tip at left
  - Cross-sections at root (y=0) and outboard end (y=256)
  - Key dimensions, spar positions, control surface boundaries
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from src.cad.airfoils import get_airfoil, blend_airfoils, resample_airfoil, scale_airfoil, max_thickness
from src.core.dxf_utils import setup_drawing, save_dxf_and_png
from src.cad.drawing.orientation import TopViewMapper, validate_orientation

# ══════════════════════════════════════════════════════════════════════
# GEOMETRY PARAMETERS (from DESIGN_CONSENSUS.md)
# ══════════════════════════════════════════════════════════════════════

WINGSPAN = 2560.0          # mm total
HALF_SPAN = 1280.0         # mm per half
PANEL_SPAN = 256.0         # mm per panel
ROOT_CHORD = 210.0         # mm
TIP_CHORD = 115.0          # mm

# Consensus chord schedule (non-linear taper from DESIGN_CONSENSUS.md)
# Span positions in mm from root, corresponding chord in mm
_CHORD_SPANS = np.array([0, 256, 512, 640, 768, 896, 1024, 1152, 1216, 1280], dtype=float)
_CHORD_VALUES = np.array([210, 204, 198, 192, 186, 180, 168, 156, 144, 115], dtype=float)

# Panel P1: span station 0 to 256mm
P1_ROOT_STATION = 0.0
P1_TIP_STATION = 256.0
P1_ROOT_FRAC = P1_ROOT_STATION / HALF_SPAN  # 0.0
P1_TIP_FRAC = P1_TIP_STATION / HALF_SPAN    # 0.2

def chord_at_span(span_mm):
    """Chord at a span position in mm (uses consensus chord schedule)."""
    return float(np.interp(span_mm, _CHORD_SPANS, _CHORD_VALUES))

def chord_at(span_frac):
    """Chord at a half-span fraction (0=root, 1=tip)."""
    return chord_at_span(span_frac * HALF_SPAN)

P1_ROOT_CHORD = chord_at_span(P1_ROOT_STATION)  # 210.0
P1_TIP_CHORD = chord_at_span(P1_TIP_STATION)    # 204.0

# Spar positions
MAIN_SPAR_FRAC = 0.25     # 25% chord
MAIN_SPAR_OD = 8.0        # mm
MAIN_SPAR_ID = 6.0        # mm
REAR_SPAR_FRAC = 0.60     # 60% chord
REAR_SPAR_W = 5.0         # mm
REAR_SPAR_H = 3.0         # mm

# Control surface
HINGE_FRAC = 0.72         # 72% chord (flap chord = 28%)
FLAP_CHORD_FRAC = 0.28

# D-box
DBOX_FRAC = 0.30          # 30% chord

# Twist
def twist_at(span_frac):
    """twist(eta) = -4.0 * eta^2.5"""
    return -4.0 * span_frac ** 2.5

P1_ROOT_TWIST = twist_at(P1_ROOT_FRAC)  # 0.0
P1_TIP_TWIST = twist_at(P1_TIP_FRAC)    # -0.07 deg (negligible)

# Joint
JOINT_TONGUE = 3.0         # mm
JOINT_GROOVE = 3.2         # mm
SPAR_HOLE_CLEARANCE = 0.15 # mm per side

# Wall thickness
WALL_VASE = 0.50           # mm (standard vase)
WALL_DBOX = 0.70           # mm (D-box zone)

# Panel mass estimate
PANEL_MASS_EST = "15.4g"

# Servo dimensions (9g digital)
SERVO_W = 23.0
SERVO_H = 12.0
SERVO_D = 11.0

# ══════════════════════════════════════════════════════════════════════
# AIRFOIL FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

# Consensus blend schedule (AG03 percentage at each span station)
# "Span Fraction" in consensus = custom parameter (0.00 to 1.00)
# corresponding to span positions 0 to 1280mm
_BLEND_SPANS = np.array([0, 256, 512, 640, 768, 896, 1024, 1152, 1216, 1280], dtype=float)
_BLEND_AG03  = np.array([0.00, 0.10, 0.20, 0.30, 0.45, 0.60, 0.75, 0.85, 0.92, 1.00])

def ag03_blend_at_span(span_mm):
    """Get AG03 blend fraction at a span position (mm from root)."""
    return float(np.interp(span_mm, _BLEND_SPANS, _BLEND_AG03))

def get_blended_airfoil(span_frac, n_points=150):
    """Get AG24-AG03 blended airfoil at a half-span fraction.

    Uses the consensus non-linear blend schedule: at P1/P2 (256mm),
    blend is 90/10 AG24/AG03 (not 80/20 from linear half-span fraction).
    """
    span_mm = span_frac * HALF_SPAN
    blend_factor = ag03_blend_at_span(span_mm)
    return blend_airfoils("AG24", "AG03", blend_factor, n_points)


def airfoil_section_points(span_frac, chord, n_pts=80):
    """Get upper and lower surface points for a cross-section.

    Returns (upper_pts, lower_pts) as lists of (x, y) in mm,
    where x=chordwise, y=thickness.
    """
    coords = get_blended_airfoil(span_frac)
    scaled = scale_airfoil(coords, chord, twist_deg=twist_at(span_frac))

    # Split at LE (minimum x)
    le_idx = np.argmin(scaled[:, 0])
    upper = scaled[:le_idx + 1]  # TE to LE
    lower = scaled[le_idx:]       # LE to TE

    # Sort by x for clean plotting
    upper = upper[np.argsort(upper[:, 0])]
    lower = lower[np.argsort(lower[:, 0])]

    # Resample to uniform x
    x_stations = np.linspace(0, chord, n_pts)
    y_upper = np.interp(x_stations, upper[:, 0], upper[:, 1])
    y_lower = np.interp(x_stations, lower[:, 0], lower[:, 1])

    upper_pts = list(zip(x_stations, y_upper))
    lower_pts = list(zip(x_stations, y_lower))
    return upper_pts, lower_pts


def y_at_x(scaled, x):
    """Get upper and lower Y at a chordwise X position."""
    le_idx = int(np.argmin(scaled[:, 0]))
    upper = scaled[:le_idx + 1][np.argsort(scaled[:le_idx + 1, 0])]
    lower = scaled[le_idx:][np.argsort(scaled[le_idx:, 0])]
    return (float(np.interp(x, upper[:, 0], upper[:, 1])),
            float(np.interp(x, lower[:, 0], lower[:, 1])))


# ══════════════════════════════════════════════════════════════════════
# LE POSITION (planform geometry)
# ══════════════════════════════════════════════════════════════════════

def le_x_at_span(span_mm):
    """LE position at a span position in mm.

    The main spar at 25% chord is the STRAIGHT datum.
    Root spar position = 25% * 210 = 52.5mm from root LE.
    At any station, LE_x = spar_x - 25% * local_chord.
    Since spar_x is constant (straight spar), LE moves aft as chord shrinks.
    """
    c = chord_at_span(span_mm)
    root_spar_x = MAIN_SPAR_FRAC * ROOT_CHORD  # 52.5mm from root LE
    le = root_spar_x - MAIN_SPAR_FRAC * c
    return le  # mm aft of root LE

def le_x_at(span_frac):
    """LE position at a half-span fraction."""
    return le_x_at_span(span_frac * HALF_SPAN)


# ══════════════════════════════════════════════════════════════════════
# DRAWING
# ══════════════════════════════════════════════════════════════════════

def main():
    doc = setup_drawing(
        title="Wing_Panel_P1",
        subtitle="Root panel (right half). Span 0-256mm. AG24 root. Flap 28% chord. Servo P1 mid-panel.",
        material="LW-PLA | Vase mode 0.50mm (0.70mm D-box zone) | 230C | Print LE down",
        mass=PANEL_MASS_EST,
        scale="1:1",
        sheet_size="A2",
        status="FOR APPROVAL",
        revision="v1",
    )
    msp = doc.modelspace()

    # A2 sheet: 594 x 420 mm
    # Use TopViewMapper for the planform (right half: tip extends RIGHT)
    m = TopViewMapper(center_x=130, center_y=345)
    errors = validate_orientation(m, PANEL_SPAN, P1_ROOT_CHORD, side="right")
    assert not errors, f"Orientation validation FAILED: {errors}"

    def D(cx, cy):
        """Map consensus (chordwise, spanwise) to DXF for right-half panel."""
        return m.map_half(cx, cy, "right")

    # ══════════════════════════════════════════════════════════════════
    # TOP VIEW (PLANFORM)
    # ══════════════════════════════════════════════════════════════════

    msp.add_text("TOP VIEW — WING PANEL P1 (1:1)", height=5.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(0, PANEL_SPAN / 2)[0] - 30, D(0, 0)[1] + 22))

    # Orientation arrows
    rx, ry = D(P1_ROOT_CHORD * 0.3, 5)
    msp.add_line((rx, ry), (rx, ry + 25), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry + 25), (rx - 2.5, ry + 21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry + 25), (rx + 2.5, ry + 21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("FWD", height=3.5, dxfattribs={"layer": "ORIENTATION"}).set_placement(
        (rx - 6, ry + 27))

    # INBD arrow (pointing left toward fuselage for right half)
    ix, iy = D(P1_ROOT_CHORD * 0.3, 5)
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
        y = P1_ROOT_STATION + i * PANEL_SPAN / n_span
        frac = y / HALF_SPAN
        c = chord_at(frac)
        le = le_x_at(frac)
        te = le + c
        le_pts_d.append(D(le, y))
        te_pts_d.append(D(te, y))

    # Draw LE
    for i in range(len(le_pts_d) - 1):
        msp.add_line(le_pts_d[i], le_pts_d[i + 1], dxfattribs={"layer": "OUTLINE"})
    # Draw TE
    for i in range(len(te_pts_d) - 1):
        msp.add_line(te_pts_d[i], te_pts_d[i + 1], dxfattribs={"layer": "OUTLINE"})
    # Root chord line
    msp.add_line(le_pts_d[0], te_pts_d[0], dxfattribs={"layer": "OUTLINE"})
    # Outboard chord line
    msp.add_line(le_pts_d[-1], te_pts_d[-1], dxfattribs={"layer": "OUTLINE"})

    # ── Main spar line (straight at 25% chord) ──
    root_spar_x = MAIN_SPAR_FRAC * ROOT_CHORD  # 52.5mm from root LE
    # Spar is straight in planform, so at any station the spar
    # is at x = root_spar_x (relative to root LE origin)
    msp.add_line(D(root_spar_x, P1_ROOT_STATION),
                 D(root_spar_x, P1_TIP_STATION),
                 dxfattribs={"layer": "SPAR"})
    msp.add_text("MAIN SPAR 25%c", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(root_spar_x, 50)[0] + 3, D(root_spar_x, 50)[1]))
    msp.add_text("8mm CF tube", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(root_spar_x, 60)[0] + 3, D(root_spar_x, 60)[1]))

    # ── Rear spar line (at 60% chord — this curves with taper) ──
    rear_pts = []
    for i in range(n_span + 1):
        y = P1_ROOT_STATION + i * PANEL_SPAN / n_span
        frac = y / HALF_SPAN
        c = chord_at(frac)
        le = le_x_at(frac)
        rear_x = le + REAR_SPAR_FRAC * c
        rear_pts.append(D(rear_x, y))
    for i in range(len(rear_pts) - 1):
        msp.add_line(rear_pts[i], rear_pts[i + 1], dxfattribs={"layer": "SPAR"})
    msp.add_text("REAR SPAR 60%c", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(le_x_at(0.05) + REAR_SPAR_FRAC * chord_at(0.05), 50)[0] + 3,
         D(le_x_at(0.05) + REAR_SPAR_FRAC * chord_at(0.05), 50)[1]))
    msp.add_text("5x3mm spruce", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(le_x_at(0.05) + REAR_SPAR_FRAC * chord_at(0.05), 60)[0] + 3,
         D(le_x_at(0.05) + REAR_SPAR_FRAC * chord_at(0.05), 60)[1]))

    # ── D-box closing web (at 30% chord) ──
    dbox_pts = []
    for i in range(n_span + 1):
        y = P1_ROOT_STATION + i * PANEL_SPAN / n_span
        frac = y / HALF_SPAN
        c = chord_at(frac)
        le = le_x_at(frac)
        dbox_x = le + DBOX_FRAC * c
        dbox_pts.append(D(dbox_x, y))
    for i in range(len(dbox_pts) - 1):
        msp.add_line(dbox_pts[i], dbox_pts[i + 1], dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("D-BOX 30%c", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(le_x_at(0.05) + DBOX_FRAC * chord_at(0.05), 120)[0] + 2,
         D(le_x_at(0.05) + DBOX_FRAC * chord_at(0.05), 120)[1]))

    # ── Hinge line (at 72% chord) ──
    hinge_pts = []
    for i in range(n_span + 1):
        y = P1_ROOT_STATION + i * PANEL_SPAN / n_span
        frac = y / HALF_SPAN
        c = chord_at(frac)
        le = le_x_at(frac)
        hinge_x = le + HINGE_FRAC * c
        hinge_pts.append(D(hinge_x, y))
    for i in range(len(hinge_pts) - 1):
        msp.add_line(hinge_pts[i], hinge_pts[i + 1], dxfattribs={"layer": "SECTION"})
    msp.add_text("HINGE 72%c", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(le_x_at(0.05) + HINGE_FRAC * chord_at(0.05), 120)[0] + 3,
         D(le_x_at(0.05) + HINGE_FRAC * chord_at(0.05), 120)[1]))
    msp.add_text("FLAP (28%c)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(le_x_at(0.1) + 0.86 * chord_at(0.1), 128)[0],
         D(le_x_at(0.1) + 0.86 * chord_at(0.1), 128)[1]))

    # ── Servo pocket outline (dashed) ──
    servo_y = P1_ROOT_STATION + PANEL_SPAN / 2  # 128mm mid-panel
    servo_frac = servo_y / HALF_SPAN
    servo_chord = chord_at(servo_frac)
    servo_le = le_x_at(servo_frac)
    servo_cx = servo_le + 0.35 * servo_chord  # 35% chord
    servo_w2 = SERVO_W / 2
    servo_d2 = SERVO_D / 2
    # Servo pocket rectangle (in planform)
    s_pts = [
        D(servo_cx - servo_d2, servo_y - servo_w2),
        D(servo_cx + servo_d2, servo_y - servo_w2),
        D(servo_cx + servo_d2, servo_y + servo_w2),
        D(servo_cx - servo_d2, servo_y + servo_w2),
    ]
    for i in range(4):
        msp.add_line(s_pts[i], s_pts[(i + 1) % 4], dxfattribs={"layer": "HIDDEN"})
    msp.add_text("SERVO 9g", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D(servo_cx, servo_y + 15)[0], D(servo_cx, servo_y + 15)[1]))

    # ── Labels ──
    msp.add_text("LE", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D(-5, PANEL_SPAN / 2))
    msp.add_text("TE", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D(P1_ROOT_CHORD + 5, PANEL_SPAN / 2))
    msp.add_text("ROOT (y=0)", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        D(P1_ROOT_CHORD / 2, -8))
    msp.add_text("OUTBOARD (y=256)", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        D(P1_TIP_CHORD / 2, PANEL_SPAN + 6))

    # ── Dimensions ──
    # Root chord
    root_le_d = D(0, 0)
    root_te_d = D(P1_ROOT_CHORD, 0)
    msp.add_aligned_dim(
        p1=root_le_d, p2=root_te_d,
        distance=-8, dimstyle="AEROFORGE",
    ).render()

    # Outboard chord
    ob_le = le_x_at(P1_TIP_FRAC)
    ob_te = ob_le + P1_TIP_CHORD
    ob_le_d = D(ob_le, P1_TIP_STATION)
    ob_te_d = D(ob_te, P1_TIP_STATION)
    msp.add_aligned_dim(
        p1=ob_le_d, p2=ob_te_d,
        distance=8, dimstyle="AEROFORGE",
    ).render()

    # Panel span
    msp.add_aligned_dim(
        p1=D(-5, P1_ROOT_STATION), p2=D(-5, P1_TIP_STATION),
        distance=8, dimstyle="AEROFORGE",
    ).render()

    # Main spar position from LE at root
    msp.add_aligned_dim(
        p1=D(0, -15), p2=D(root_spar_x, -15),
        distance=-5, dimstyle="AEROFORGE",
    ).render()

    # Flap chord at root (28% chord)
    hinge_root_x = HINGE_FRAC * P1_ROOT_CHORD
    msp.add_aligned_dim(
        p1=D(hinge_root_x, -15), p2=D(P1_ROOT_CHORD, -15),
        distance=-12, dimstyle="AEROFORGE",
    ).render()

    # ══════════════════════════════════════════════════════════════════
    # CROSS-SECTIONS
    # ══════════════════════════════════════════════════════════════════

    SEC_X = 420.0  # DXF X position for sections

    sections = [
        (340, P1_ROOT_FRAC, "SEC A - ROOT y=0 (AG24 100%)", P1_ROOT_CHORD),
        (270, P1_TIP_FRAC, f"SEC B - OUTBOARD y=256 (90/10 AG24/AG03)", P1_TIP_CHORD),
    ]

    for sy, span_frac, label, chord in sections:
        msp.add_text(label, height=2.3, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X, sy + 18))
        msp.add_text(f"chord={chord:.1f}mm", height=2.0,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X, sy + 14))

        # Get airfoil section
        upper_pts, lower_pts = airfoil_section_points(span_frac, chord)

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

        # LE closure
        msp.add_line(
            (SEC_X + upper_pts[0][0], sy + upper_pts[0][1]),
            (SEC_X + lower_pts[0][0], sy + lower_pts[0][1]),
            dxfattribs={"layer": "OUTLINE"})
        # TE closure
        msp.add_line(
            (SEC_X + upper_pts[-1][0], sy + upper_pts[-1][1]),
            (SEC_X + lower_pts[-1][0], sy + lower_pts[-1][1]),
            dxfattribs={"layer": "OUTLINE"})

        # Centerline
        msp.add_line(
            (SEC_X - 5, sy), (SEC_X + chord + 10, sy),
            dxfattribs={"layer": "CENTERLINE"})

        # Main spar bore (circle at 25% chord)
        spar_x = MAIN_SPAR_FRAC * chord
        coords = get_blended_airfoil(span_frac)
        scaled = scale_airfoil(coords, chord, twist_deg=twist_at(span_frac))
        yu, yl = y_at_x(scaled, spar_x)
        spar_cy = (yu + yl) / 2
        msp.add_circle(
            (SEC_X + spar_x, sy + spar_cy), MAIN_SPAR_OD / 2,
            dxfattribs={"layer": "SPAR"})
        # Inner bore (tube wall)
        msp.add_circle(
            (SEC_X + spar_x, sy + spar_cy), MAIN_SPAR_ID / 2,
            dxfattribs={"layer": "SPAR"})

        # Rear spar slot (rectangle at 60% chord)
        rear_x = REAR_SPAR_FRAC * chord
        ryu, ryl = y_at_x(scaled, rear_x)
        rear_cy = (ryu + ryl) / 2
        rx0 = SEC_X + rear_x - REAR_SPAR_W / 2
        ry0 = sy + rear_cy - REAR_SPAR_H / 2
        msp.add_line((rx0, ry0), (rx0 + REAR_SPAR_W, ry0), dxfattribs={"layer": "SPAR"})
        msp.add_line((rx0 + REAR_SPAR_W, ry0), (rx0 + REAR_SPAR_W, ry0 + REAR_SPAR_H),
                     dxfattribs={"layer": "SPAR"})
        msp.add_line((rx0 + REAR_SPAR_W, ry0 + REAR_SPAR_H), (rx0, ry0 + REAR_SPAR_H),
                     dxfattribs={"layer": "SPAR"})
        msp.add_line((rx0, ry0 + REAR_SPAR_H), (rx0, ry0), dxfattribs={"layer": "SPAR"})

        # D-box closing web (vertical line at 30% chord)
        dbox_x = DBOX_FRAC * chord
        dyu, dyl = y_at_x(scaled, dbox_x)
        msp.add_line(
            (SEC_X + dbox_x, sy + dyl * 0.95),
            (SEC_X + dbox_x, sy + dyu * 0.95),
            dxfattribs={"layer": "CENTERLINE"})

        # Hinge line (vertical line at 72% chord)
        hinge_x = HINGE_FRAC * chord
        hyu, hyl = y_at_x(scaled, hinge_x)
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

        # Spar label
        msp.add_text("8mm tube", height=1.2, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X + spar_x + 5, sy + spar_cy + 1))

        # Rear spar label
        msp.add_text("5x3 spruce", height=1.2, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X + rear_x + 5, sy + rear_cy + 1))

        # Max thickness annotation
        af = get_blended_airfoil(span_frac)
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
    notes = [
        "NOTES:",
        f"1. All dims mm. Right half only; Left = mirror.",
        f"2. Airfoil: AG24 100% (root) to 90/10 AG24/AG03 (outboard y=256).",
        f"3. MAIN SPAR: 8mm CF tube OD, 6mm ID, at 25% chord (straight).",
        f"4. REAR SPAR: 5x3mm spruce strip at 60% chord.",
        f"5. D-BOX: LE to 30% chord, wall 0.70mm. Rest 0.50mm vase.",
        f"6. HINGE: TPU living hinge at 72% chord. Flap chord = 28%.",
        f"7. SERVO: 9g digital metal gear at mid-panel (y=128), 35% chord.",
        f"8. JOINT: Male tongue 3mm on outboard face. Flat joint (0 deg dihedral).",
        f"9. TWIST: 0.0 deg root to -0.07 deg outboard (negligible for P1).",
        f"10. Panel fits Bambu 256x256mm bed (span=256mm, chord max=210mm).",
    ]
    for i, note in enumerate(notes):
        h = 2.0 if i == 0 else 1.8
        msp.add_text(note, height=h, dxfattribs={"layer": "TEXT"}).set_placement(
            (notes_x, notes_y - i * 5))

    # ══════════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════════

    dxf_path = "cad/components/wing/Wing_Panel_P1/Wing_Panel_P1_drawing.dxf"
    save_dxf_and_png(doc, dxf_path, dpi=200)
    print(f"\nDrawing saved to {dxf_path}")


if __name__ == "__main__":
    main()
