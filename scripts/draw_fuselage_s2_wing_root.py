"""
Fuselage_S2_Wing_Root Component Drawing
=========================================
Section S2 (X=260 to X=430mm) of the integrated fuselage.
Wing saddle cutout, servo bay, spar tunnel, pushrod exits.

Views:
  - SIDE VIEW (profile): fuselage side silhouette
  - TOP VIEW (planform): fuselage top silhouette with wing saddle
  - SECTION A at X=280 (wing saddle, spar tunnel)
  - SECTION B at X=350 (servo bay)
  - SECTION C at X=430 (S2/S3 joint face)

Dimensions from DESIGN_CONSENSUS.md v2 and STRUCTURAL_REVIEW_FUSELAGE.md.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# ============================================================================
# S2 WING ROOT GEOMETRY DATA
# ============================================================================

# Cross-section schedule for S2 (X=260 to X=430mm)
XSECTIONS = [
    (260, 38, 34, "egg"),        # wing LE station / S1-S2 joint
    (280, 36, 32, "egg"),        # wing saddle zone
    (300, 34, 30, "egg"),        # spar tunnel zone
    (320, 32, 28, "ellipse"),    # aft of spar tunnel
    (350, 30, 26, "ellipse"),    # servo bay
    (380, 27, 24, "ellipse"),    # post-servo taper
    (400, 25, 22, "ellipse"),    # taper continues
    (430, 22, 19, "ellipse"),    # S2/S3 joint face
]

LONGERONS = {
    280: [(+12, +10), (-12, +10), (+12, -10), (-12, -10)],  # 24x20
    350: [(+9, +8), (-9, +8), (+9, -8), (-9, -8)],          # 18x16
    430: [(+6, +5), (-6, +5), (+6, -5), (-6, -5)],          # 12x10
}

S2_LENGTH = 170.0
SHELL_WALL = 0.6
LONGERON_DIA = 2.0
LONGERON_SLEEVE_DIA = 2.5
SPAR_TUNNEL_ID = 8.1    # 8mm CF spar + clearance
SPAR_TUNNEL_OD = 11.0   # CF-PLA reinforced sleeve
WING_CHORD_ROOT = 210.0
WING_SADDLE_LENGTH = 60.0  # X=260-320 approx
FAIRING_FWD = 30.0
FAIRING_AFT = 60.0
FAIRING_RADIUS = 15.0
SERVO_LENGTH = 23.0   # micro servo body
SERVO_WIDTH = 12.0
SERVO_HEIGHT = 22.0
PUSHROD_OD = 3.0       # PTFE tube OD
DOWEL_DIA = 2.0
M3_BOLT_DIA = 3.0


def interp_dim(x, dim_idx):
    for i in range(len(XSECTIONS) - 1):
        x0, w0, h0, _ = XSECTIONS[i]
        x1, w1, h1, _ = XSECTIONS[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0) if x1 != x0 else 0
            v0 = w0 if dim_idx == 1 else h0
            v1 = w1 if dim_idx == 1 else h1
            return v0 + t * (v1 - v0)
    return XSECTIONS[-1][dim_idx] if dim_idx <= 2 else 0


def half_width(x):
    return interp_dim(x, 1) / 2.0


def half_height(x):
    return interp_dim(x, 2) / 2.0


def ellipse_points(cx, cy, a, b, n=80):
    pts = []
    for i in range(n + 1):
        theta = 2 * math.pi * i / n
        pts.append((cx + a * math.cos(theta), cy + b * math.sin(theta)))
    return pts


def draw_profile_polyline(msp, stations, dim_sign, y_offset, layer, x_offset=0):
    for i in range(len(stations) - 1):
        x0, val0 = stations[i]
        x1, val1 = stations[i + 1]
        msp.add_line(
            (x_offset + x0 - 260, y_offset + dim_sign * val0 / 2),
            (x_offset + x1 - 260, y_offset + dim_sign * val1 / 2),
            dxfattribs={"layer": layer}
        )


def main():
    doc = setup_drawing(
        title="Fuselage_S2_Wing_Root",
        subtitle="Wing root section X=260-430mm. Wing saddle, 8mm spar tunnel, 2x servo mounts.",
        material="LW-PLA 0.6mm shell | CF-PLA spar tunnel (M6) | Print: belly-down horizontal",
        mass="~18g (shell+structure, excl. longerons)",
        scale="1:1",
        sheet_size="A1",
        status="FOR APPROVAL",
        revision="v1",
        orientation_labels={"fwd": "FWD", "inbd": "NOSE"},
    )
    msp = doc.modelspace()

    # Layout positions (A1 sheet: 841 x 594mm)
    SIDE_X0 = 40.0
    SIDE_Y0 = 420.0
    TOP_X0 = 40.0
    TOP_Y0 = 310.0
    SEC_A_X0 = 380.0
    SEC_A_Y0 = 510.0
    SEC_B_X0 = 540.0
    SEC_B_Y0 = 510.0
    SEC_C_X0 = 700.0
    SEC_C_Y0 = 510.0

    # =========================================================================
    # SIDE VIEW (profile)
    # =========================================================================
    msp.add_text("SIDE VIEW — PROFILE (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0, SIDE_Y0 + 30))

    h_stations = [(xs[0], xs[2]) for xs in XSECTIONS]
    draw_profile_polyline(msp, h_stations, +1, SIDE_Y0, "OUTLINE", SIDE_X0)
    draw_profile_polyline(msp, h_stations, -1, SIDE_Y0, "OUTLINE", SIDE_X0)

    # Centerline
    msp.add_line((SIDE_X0 - 5, SIDE_Y0), (SIDE_X0 + 180, SIDE_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Spar tunnel (shown as hidden line at center)
    spar_y_top = SPAR_TUNNEL_OD / 2
    spar_y_bot = -SPAR_TUNNEL_OD / 2
    msp.add_line((SIDE_X0, SIDE_Y0 + spar_y_top),
                 (SIDE_X0 + 60, SIDE_Y0 + spar_y_top),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0, SIDE_Y0 + spar_y_bot),
                 (SIDE_X0 + 60, SIDE_Y0 + spar_y_bot),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("8mm CF SPAR TUNNEL", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 5, SIDE_Y0 + 8))

    # Wing saddle cutout (top opening)
    saddle_x_start = 0   # relative to S2 start
    saddle_x_end = 60    # X=260-320
    saddle_depth = 5.0   # cutout depth into top surface
    hw_start = half_height(260)
    hw_end = half_height(320)
    msp.add_line((SIDE_X0 + saddle_x_start, SIDE_Y0 + hw_start - saddle_depth),
                 (SIDE_X0 + saddle_x_end, SIDE_Y0 + hw_end - saddle_depth),
                 dxfattribs={"layer": "SECTION"})
    msp.add_text("WING SADDLE CUTOUT", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SIDE_X0 + 5, SIDE_Y0 + hw_start + 5))

    # Servo bay (2 servos side by side at X=340-370)
    servo_x = 80  # relative: X=340
    msp.add_line((SIDE_X0 + servo_x, SIDE_Y0 - 5),
                 (SIDE_X0 + servo_x + SERVO_LENGTH, SIDE_Y0 - 5),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + servo_x, SIDE_Y0 + 5),
                 (SIDE_X0 + servo_x + SERVO_LENGTH, SIDE_Y0 + 5),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + servo_x, SIDE_Y0 - 5),
                 (SIDE_X0 + servo_x, SIDE_Y0 + 5),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + servo_x + SERVO_LENGTH, SIDE_Y0 - 5),
                 (SIDE_X0 + servo_x + SERVO_LENGTH, SIDE_Y0 + 5),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("2x SERVO", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + servo_x + 2, SIDE_Y0 + 6))

    # Pushrod exits (at aft end, X~400-430)
    for py_off in [3, -3]:
        msp.add_circle((SIDE_X0 + 160, SIDE_Y0 + py_off),
                       PUSHROD_OD / 2,
                       dxfattribs={"layer": "HIDDEN"})
    msp.add_text("2x PUSHROD EXIT", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 140, SIDE_Y0 - 10))

    # Longeron positions in side view
    for xst, longs in LONGERONS.items():
        rel_x = xst - 260
        for lx, ly in longs:
            msp.add_circle((SIDE_X0 + rel_x, SIDE_Y0 + ly),
                           LONGERON_DIA / 2,
                           dxfattribs={"layer": "SPAR"})

    # Key dimensions
    msp.add_linear_dim(
        base=(SIDE_X0 + 85, SIDE_Y0 - 28),
        p1=(SIDE_X0, SIDE_Y0 - 23),
        p2=(SIDE_X0 + 170, SIDE_Y0 - 23),
        dimstyle="AEROFORGE",
    ).render()

    # Station labels
    for xst, label in [(260, "X=260"), (320, "X=320"), (350, "X=350"), (430, "X=430")]:
        rel_x = xst - 260
        ht = half_height(xst)
        msp.add_line((SIDE_X0 + rel_x, SIDE_Y0 + ht + 2),
                     (SIDE_X0 + rel_x, SIDE_Y0 + ht + 8),
                     dxfattribs={"layer": "DIMENSION"})
        msp.add_text(label, height=1.8,
                     dxfattribs={"layer": "DIMENSION"}).set_placement(
            (SIDE_X0 + rel_x - 6, SIDE_Y0 + ht + 9))

    # =========================================================================
    # TOP VIEW (planform)
    # =========================================================================
    msp.add_text("TOP VIEW — PLANFORM (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0, TOP_Y0 + 30))

    w_stations = [(xs[0], xs[1]) for xs in XSECTIONS]
    draw_profile_polyline(msp, w_stations, +1, TOP_Y0, "OUTLINE", TOP_X0)
    draw_profile_polyline(msp, w_stations, -1, TOP_Y0, "OUTLINE", TOP_X0)

    # Centerline
    msp.add_line((TOP_X0 - 5, TOP_Y0), (TOP_X0 + 180, TOP_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Wing root fairing outline (quartic polynomial blend)
    fairing_x_start = 0   # fwd extension from wing LE
    fairing_x_end = 90     # aft extension
    msp.add_text("WING ROOT FAIRING", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0 + 5, TOP_Y0 + 22))
    msp.add_text("Quartic polynomial, R15mm, C2 continuous", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0 + 5, TOP_Y0 + 19))

    # M3 wing bolt position (from bottom, at ~X=290)
    bolt_rel_x = 30  # X=290
    msp.add_circle((TOP_X0 + bolt_rel_x, TOP_Y0),
                   M3_BOLT_DIA / 2,
                   dxfattribs={"layer": "SPAR"})
    msp.add_text("M3 WING BOLT", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0 + bolt_rel_x + 3, TOP_Y0 - 5))

    # Dowel positions
    for dx in [15, 50]:  # at X=275 and X=310
        for dy in [5, -5]:
            msp.add_circle((TOP_X0 + dx, TOP_Y0 + dy),
                           DOWEL_DIA / 2,
                           dxfattribs={"layer": "SPAR"})
    msp.add_text("2x ALIGNMENT DOWELS", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0 + 55, TOP_Y0 + 8))

    # Section cut lines
    for xcut, label in [(280, "A"), (350, "B"), (430, "C")]:
        rel_x = xcut - 260
        hw = half_width(xcut) + 5
        msp.add_line((TOP_X0 + rel_x, TOP_Y0 - hw),
                     (TOP_X0 + rel_x, TOP_Y0 + hw),
                     dxfattribs={"layer": "SECTION"})
        msp.add_text(label, height=2.5,
                     dxfattribs={"layer": "SECTION"}).set_placement(
            (TOP_X0 + rel_x - 2, TOP_Y0 + hw + 2))
        msp.add_text(label, height=2.5,
                     dxfattribs={"layer": "SECTION"}).set_placement(
            (TOP_X0 + rel_x - 2, TOP_Y0 - hw - 5))

    # =========================================================================
    # SECTION A — X=280 (Wing saddle + spar tunnel)
    # =========================================================================
    msp.add_text("SECTION A — X=280 (Wing Saddle)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 45, SEC_A_Y0 + 30))
    msp.add_text("36mm W x 32mm H egg", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 20, SEC_A_Y0 + 24))

    w280 = 36.0 / 2
    h280 = 32.0 / 2
    pts = ellipse_points(SEC_A_X0, SEC_A_Y0, w280, h280)
    for i in range(len(pts) - 1):
        msp.add_line(pts[i], pts[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Inner wall
    iw = w280 - SHELL_WALL
    ih = h280 - SHELL_WALL
    pts_i = ellipse_points(SEC_A_X0, SEC_A_Y0, iw, ih)
    for i in range(len(pts_i) - 1):
        msp.add_line(pts_i[i], pts_i[i + 1], dxfattribs={"layer": "WALL"})

    # Spar tunnel bore (8.1mm ID, at center)
    msp.add_circle((SEC_A_X0, SEC_A_Y0), SPAR_TUNNEL_ID / 2,
                   dxfattribs={"layer": "SPAR"})
    msp.add_circle((SEC_A_X0, SEC_A_Y0), SPAR_TUNNEL_OD / 2,
                   dxfattribs={"layer": "SPAR"})
    msp.add_text("8.1mm SPAR BORE", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 + 8, SEC_A_Y0 + 2))
    msp.add_text("CF-PLA sleeve 11mm OD", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 + 8, SEC_A_Y0 - 2))

    # Centerlines
    msp.add_line((SEC_A_X0 - w280 - 5, SEC_A_Y0),
                 (SEC_A_X0 + w280 + 5, SEC_A_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_A_X0, SEC_A_Y0 - h280 - 5),
                 (SEC_A_X0, SEC_A_Y0 + h280 + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Longerons at X=280
    for lx, ly in LONGERONS[280]:
        msp.add_circle((SEC_A_X0 + lx, SEC_A_Y0 + ly),
                       LONGERON_SLEEVE_DIA / 2,
                       dxfattribs={"layer": "SPAR"})

    # Wing saddle opening (top cutout)
    saddle_w = 20  # half-width of saddle opening
    msp.add_line((SEC_A_X0 - saddle_w, SEC_A_Y0 + h280 - 3),
                 (SEC_A_X0 + saddle_w, SEC_A_Y0 + h280 - 3),
                 dxfattribs={"layer": "SECTION"})
    msp.add_text("SADDLE CUTOUT", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_A_X0 - 12, SEC_A_Y0 + h280 + 2))

    # Dimensions
    msp.add_linear_dim(
        base=(SEC_A_X0, SEC_A_Y0 - h280 - 12),
        p1=(SEC_A_X0 - w280, SEC_A_Y0 - h280 - 8),
        p2=(SEC_A_X0 + w280, SEC_A_Y0 - h280 - 8),
        dimstyle="AEROFORGE",
    ).render()
    msp.add_linear_dim(
        base=(SEC_A_X0 + w280 + 15, SEC_A_Y0),
        p1=(SEC_A_X0 + w280 + 10, SEC_A_Y0 - h280),
        p2=(SEC_A_X0 + w280 + 10, SEC_A_Y0 + h280),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # =========================================================================
    # SECTION B — X=350 (Servo bay)
    # =========================================================================
    msp.add_text("SECTION B — X=350 (Servo Bay)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 40, SEC_B_Y0 + 30))
    msp.add_text("30mm W x 26mm H ellipse", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 20, SEC_B_Y0 + 24))

    w350 = 30.0 / 2
    h350 = 26.0 / 2
    pts_b = ellipse_points(SEC_B_X0, SEC_B_Y0, w350, h350)
    for i in range(len(pts_b) - 1):
        msp.add_line(pts_b[i], pts_b[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Inner wall
    iw_b = w350 - SHELL_WALL
    ih_b = h350 - SHELL_WALL
    pts_ib = ellipse_points(SEC_B_X0, SEC_B_Y0, iw_b, ih_b)
    for i in range(len(pts_ib) - 1):
        msp.add_line(pts_ib[i], pts_ib[i + 1], dxfattribs={"layer": "WALL"})

    # 2x servo outlines (side by side, centered)
    servo_half_w = SERVO_WIDTH / 2
    for sx_off in [-servo_half_w - 0.5, +0.5]:
        msp.add_line((SEC_B_X0 + sx_off, SEC_B_Y0 - SERVO_HEIGHT / 2 + 4),
                     (SEC_B_X0 + sx_off + SERVO_WIDTH, SEC_B_Y0 - SERVO_HEIGHT / 2 + 4),
                     dxfattribs={"layer": "HIDDEN"})
        msp.add_line((SEC_B_X0 + sx_off, SEC_B_Y0 + SERVO_HEIGHT / 2 - 6),
                     (SEC_B_X0 + sx_off + SERVO_WIDTH, SEC_B_Y0 + SERVO_HEIGHT / 2 - 6),
                     dxfattribs={"layer": "HIDDEN"})
        msp.add_line((SEC_B_X0 + sx_off, SEC_B_Y0 - SERVO_HEIGHT / 2 + 4),
                     (SEC_B_X0 + sx_off, SEC_B_Y0 + SERVO_HEIGHT / 2 - 6),
                     dxfattribs={"layer": "HIDDEN"})
        msp.add_line((SEC_B_X0 + sx_off + SERVO_WIDTH, SEC_B_Y0 - SERVO_HEIGHT / 2 + 4),
                     (SEC_B_X0 + sx_off + SERVO_WIDTH, SEC_B_Y0 + SERVO_HEIGHT / 2 - 6),
                     dxfattribs={"layer": "HIDDEN"})
    msp.add_text("ELEV SERVO", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_B_X0 - servo_half_w - 0.5, SEC_B_Y0 - 1))
    msp.add_text("RUD SERVO", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_B_X0 + 1, SEC_B_Y0 - 1))

    # Pushrod channels (2x 3mm OD)
    msp.add_circle((SEC_B_X0 - 4, SEC_B_Y0 - 8), PUSHROD_OD / 2,
                   dxfattribs={"layer": "HIDDEN"})
    msp.add_circle((SEC_B_X0 + 4, SEC_B_Y0 - 8), PUSHROD_OD / 2,
                   dxfattribs={"layer": "HIDDEN"})
    msp.add_text("2x PUSHROD 3mm", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_B_X0 + 8, SEC_B_Y0 - 10))

    # Centerlines
    msp.add_line((SEC_B_X0 - w350 - 5, SEC_B_Y0),
                 (SEC_B_X0 + w350 + 5, SEC_B_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_B_X0, SEC_B_Y0 - h350 - 5),
                 (SEC_B_X0, SEC_B_Y0 + h350 + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Longerons
    for lx, ly in LONGERONS[350]:
        msp.add_circle((SEC_B_X0 + lx, SEC_B_Y0 + ly),
                       LONGERON_SLEEVE_DIA / 2,
                       dxfattribs={"layer": "SPAR"})

    # Dimensions
    msp.add_linear_dim(
        base=(SEC_B_X0, SEC_B_Y0 - h350 - 12),
        p1=(SEC_B_X0 - w350, SEC_B_Y0 - h350 - 8),
        p2=(SEC_B_X0 + w350, SEC_B_Y0 - h350 - 8),
        dimstyle="AEROFORGE",
    ).render()
    msp.add_linear_dim(
        base=(SEC_B_X0 + w350 + 15, SEC_B_Y0),
        p1=(SEC_B_X0 + w350 + 10, SEC_B_Y0 - h350),
        p2=(SEC_B_X0 + w350 + 10, SEC_B_Y0 + h350),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # =========================================================================
    # SECTION C — X=430 (S2/S3 joint face)
    # =========================================================================
    msp.add_text("SECTION C — X=430 (S2/S3 Joint)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 40, SEC_C_Y0 + 30))
    msp.add_text("22mm W x 19mm H ellipse", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 20, SEC_C_Y0 + 24))

    w430 = 22.0 / 2
    h430 = 19.0 / 2
    pts_c = ellipse_points(SEC_C_X0, SEC_C_Y0, w430, h430)
    for i in range(len(pts_c) - 1):
        msp.add_line(pts_c[i], pts_c[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Inner wall
    iw_c = w430 - SHELL_WALL
    ih_c = h430 - SHELL_WALL
    pts_ic = ellipse_points(SEC_C_X0, SEC_C_Y0, iw_c, ih_c)
    for i in range(len(pts_ic) - 1):
        msp.add_line(pts_ic[i], pts_ic[i + 1], dxfattribs={"layer": "WALL"})

    # Centerlines
    msp.add_line((SEC_C_X0 - w430 - 5, SEC_C_Y0),
                 (SEC_C_X0 + w430 + 5, SEC_C_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_C_X0, SEC_C_Y0 - h430 - 5),
                 (SEC_C_X0, SEC_C_Y0 + h430 + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Longerons at X=430
    for lx, ly in LONGERONS[430]:
        msp.add_circle((SEC_C_X0 + lx, SEC_C_Y0 + ly),
                       LONGERON_SLEEVE_DIA / 2,
                       dxfattribs={"layer": "SPAR"})

    # Pushrod channels (pass-through)
    msp.add_circle((SEC_C_X0 - 3, SEC_C_Y0 - 4), PUSHROD_OD / 2,
                   dxfattribs={"layer": "HIDDEN"})
    msp.add_circle((SEC_C_X0 + 3, SEC_C_Y0 - 4), PUSHROD_OD / 2,
                   dxfattribs={"layer": "HIDDEN"})

    # Interlocking teeth label
    msp.add_text("INTERLOCKING TEETH (M4)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 + 12, SEC_C_Y0 - 14))
    msp.add_text("1.5mm depth, 3mm pitch", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 + 12, SEC_C_Y0 - 18))

    # Dimensions
    msp.add_linear_dim(
        base=(SEC_C_X0, SEC_C_Y0 - h430 - 12),
        p1=(SEC_C_X0 - w430, SEC_C_Y0 - h430 - 8),
        p2=(SEC_C_X0 + w430, SEC_C_Y0 - h430 - 8),
        dimstyle="AEROFORGE",
    ).render()
    msp.add_linear_dim(
        base=(SEC_C_X0 + w430 + 15, SEC_C_Y0),
        p1=(SEC_C_X0 + w430 + 10, SEC_C_Y0 - h430),
        p2=(SEC_C_X0 + w430 + 10, SEC_C_Y0 + h430),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # =========================================================================
    # NOTES
    # =========================================================================
    notes = [
        "NOTES:",
        "1. All dims mm. Scale 1:1. S2 is the wing root section X=260 to X=430mm.",
        "2. Prints belly-down, horizontal. 170mm L x 38mm W x 34mm H. Fits bed easily.",
        "3. Shell: 0.6mm LW-PLA. Spar tunnel: CF-PLA reinforced (M6), 1.5mm wall min.",
        "4. Wing saddle cutout: AG24 root airfoil profile, 210mm chord, top of fuselage.",
        "5. 8mm CF spar tunnel: 8.1mm ID bore, 11mm OD CF-PLA sleeve (X=260-320mm).",
        "6. 2x servo mounts: elevator + rudder micro servos, side by side at X=340-370.",
        "7. 2x pushrod exits (3mm OD PTFE tube): elevator + rudder, bottom quadrant.",
        "8. Wing root fairing: quartic polynomial blend, 15mm radius, C2 continuous.",
        "9. 2x 2mm steel alignment dowels at X=275 and X=310 (30mm+ spacing).",
        "10. 1x M3 nylon wing bolt from bottom at X=290 (anti-lift retention).",
        "11. 4x 2mm CF longerons pass through. Spacing: 24x20mm to 12x10mm.",
        "12. Joint faces: interlocking teeth 1.5mm depth, 3mm pitch (M4).",
    ]
    ny = 160
    for n in notes:
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((25, ny))
        ny -= 5

    # =========================================================================
    # SAVE
    # =========================================================================
    out_path = "cad/components/fuselage/Fuselage_S2_Wing_Root/Fuselage_S2_Wing_Root_drawing.dxf"
    save_dxf_and_png(doc, out_path, dpi=300)
    print("Fuselage_S2_Wing_Root drawing complete.")


if __name__ == "__main__":
    main()
