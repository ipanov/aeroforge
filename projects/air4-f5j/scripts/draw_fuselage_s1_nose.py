"""
Fuselage_S1_Nose Component Drawing
====================================
Section S1 (X=0 to X=260mm) of the integrated fuselage.
Prints as LEFT/RIGHT halves (split along vertical centerline).

Views:
  - SIDE VIEW (profile): fuselage side silhouette, X axis horizontal
  - TOP VIEW (planform): fuselage top silhouette
  - FRONT VIEW: cross-section at X=0 (spinner tip) and X=30 (motor face)
  - REAR VIEW: cross-section at X=260 (S1/S2 joint face)
  - SECTION at X=150 (battery bay, max cross-section)

Dimensions from DESIGN_CONSENSUS.md v2 and AERO_PROPOSAL_FUSELAGE.md.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# ============================================================================
# S1 NOSE GEOMETRY DATA (from Design Consensus v2 + Aero Proposal)
# ============================================================================

# Cross-section schedule for S1 (X=0 to X=260mm)
# Each entry: (X_station, Width, Height, shape_description)
XSECTIONS = [
    (0,   0,    0,    "point"),       # spinner tip
    (10,  16,   16,   "circle"),      # spinner cone
    (20,  28,   28,   "circle"),      # spinner widening
    (30,  32,   32,   "circle"),      # spinner base / motor face
    (40,  33,   33,   "circle"),      # motor mount ring front
    (55,  35,   35,   "circle"),      # motor body (28mm dia)
    (70,  36,   36,   "circle"),      # motor mount ring rear
    (90,  40,   37,   "ellipse"),     # ESC bay
    (120, 46,   41,   "ellipse"),     # battery fwd
    (150, 50,   44,   "ellipse"),     # MAX SECTION - battery center
    (180, 50,   44,   "ellipse"),     # battery aft
    (200, 48,   42,   "ellipse"),     # receiver bay
    (230, 44,   38,   "ellipse"),     # receiver aft
    (250, 40,   35,   "egg"),         # pre-wing taper
    (260, 38,   34,   "egg"),         # wing LE station / S1-S2 joint
]

# Longeron positions at key S1 stations (from consensus)
# Format: (X_station, [(x_offset, y_offset), ...])
LONGERONS = {
    40:  [(+9, +9), (-9, +9), (+9, -9), (-9, -9)],   # 18x18
    150: [(+18, +16), (-18, +16), (+18, -16), (-18, -16)],  # 36x32
    260: [(+12, +10), (-12, +10), (+12, -10), (-12, -10)],  # 24x20 (at wing saddle, just beyond S1)
}

# Internal dimensions at key stations
# (X, internal_W, internal_H)
INTERNAL = [
    (40,  29, 29),   # motor mount area
    (55,  29, 29),   # motor body
    (70,  30, 30),   # motor mount ring rear
    (90,  34, 31),   # ESC bay
    (120, 40, 35),   # battery fwd
    (150, 44, 38),   # battery center
    (180, 44, 38),   # battery aft
    (200, 42, 36),   # receiver bay
    (230, 38, 32),   # receiver aft
]

# Key dimensions
S1_LENGTH = 260.0     # mm (X=0 to X=260)
SPINNER_TIP_LENGTH = 10.0  # separate nose cone insert
MOTOR_FACE_DIA = 32.0  # mm (at X=30)
MOTOR_BODY_DIA = 28.0  # mm
MAX_WIDTH = 50.0      # mm at X=150
MAX_HEIGHT = 44.0     # mm at X=150
SHELL_WALL = 0.6      # mm (LW-PLA)
PETG_ZONE = (30, 90)  # PETG motor bay zone
LONGERON_DIA = 2.0    # mm (2mm CF rods per structural review)
LONGERON_SLEEVE_DIA = 2.5  # mm (printed sleeve for 2mm rod)

# Hatch door
HATCH_X_START = 80.0
HATCH_X_END = 210.0
HATCH_WIDTH = 25.0   # mm (one side of fuselage)
HATCH_LENGTH = 130.0  # mm

# Battery bay
BATT_LENGTH = 78.0
BATT_WIDTH = 38.0
BATT_HEIGHT = 28.0


def interp_dim(x, dim_idx):
    """Interpolate width (dim_idx=1) or height (dim_idx=2) at station x."""
    for i in range(len(XSECTIONS) - 1):
        x0, w0, h0, _ = XSECTIONS[i]
        x1, w1, h1, _ = XSECTIONS[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0) if x1 != x0 else 0
            v0 = w0 if dim_idx == 1 else h0
            v1 = w1 if dim_idx == 1 else h1
            return v0 + t * (v1 - v0)
    return 0


def half_width(x):
    return interp_dim(x, 1) / 2.0


def half_height(x):
    return interp_dim(x, 2) / 2.0


def ellipse_points(cx, cy, a, b, n=80):
    """Generate points for an ellipse centered at (cx,cy) with semi-axes a,b."""
    pts = []
    for i in range(n + 1):
        theta = 2 * math.pi * i / n
        pts.append((cx + a * math.cos(theta), cy + b * math.sin(theta)))
    return pts


def draw_profile_polyline(msp, stations, dim_sign, y_offset, layer, x_offset=0):
    """Draw a side or top profile as a polyline of stations.
    dim_sign: +1 for top/right edge, -1 for bottom/left edge
    """
    for i in range(len(stations) - 1):
        x0, val0 = stations[i]
        x1, val1 = stations[i + 1]
        msp.add_line(
            (x_offset + x0, y_offset + dim_sign * val0 / 2),
            (x_offset + x1, y_offset + dim_sign * val1 / 2),
            dxfattribs={"layer": layer}
        )


# ============================================================================
# MAIN DRAWING
# ============================================================================

def main():
    doc = setup_drawing(
        title="Fuselage_S1_Nose",
        subtitle="Nose section X=0-260mm. Left/right halves (M2). PETG motor bay X=30-90mm (M3).",
        material="LW-PLA 0.6mm shell (X=90-260) | PETG shell (X=30-90) | Print: L/R halves flat",
        mass="~25g (shell+structure, excl. longerons)",
        scale="1:1",
        sheet_size="A1",
        status="FOR APPROVAL",
        revision="v1",
        orientation_labels={"fwd": "FWD", "inbd": "NOSE"},
    )
    msp = doc.modelspace()

    # A1 sheet: 841 x 594mm, drawing area: 821 x 574 after margins
    # Layout positions
    SIDE_X0 = 40.0     # side view left edge
    SIDE_Y0 = 420.0    # side view centerline Y
    TOP_X0 = 40.0      # top view left edge
    TOP_Y0 = 310.0     # top view centerline Y
    FRONT_X0 = 380.0   # front view center X
    FRONT_Y0 = 510.0   # front view center Y
    REAR_X0 = 560.0    # rear view center X
    REAR_Y0 = 510.0    # rear view center Y
    SEC_X0 = 470.0     # section view center X
    SEC_Y0 = 310.0     # section view center Y

    # =========================================================================
    # SIDE VIEW (profile) — shows height variation
    # =========================================================================
    msp.add_text("SIDE VIEW — PROFILE (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0, SIDE_Y0 + 40))

    # Build station list for height
    h_stations = [(xs[0], xs[2]) for xs in XSECTIONS]

    # Top profile
    draw_profile_polyline(msp, h_stations, +1, SIDE_Y0, "OUTLINE", SIDE_X0)
    # Bottom profile
    draw_profile_polyline(msp, h_stations, -1, SIDE_Y0, "OUTLINE", SIDE_X0)

    # Centerline
    msp.add_line((SIDE_X0 - 5, SIDE_Y0), (SIDE_X0 + 270, SIDE_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # PETG zone highlight
    petg_y_top = SIDE_Y0 + half_height(55)
    petg_y_bot = SIDE_Y0 - half_height(55)
    msp.add_text("PETG (M3)", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 45, SIDE_Y0 + 22))
    # PETG zone boundary lines (dashed)
    for px in [30, 90]:
        ht = half_height(px)
        msp.add_line((SIDE_X0 + px, SIDE_Y0 - ht - 3),
                     (SIDE_X0 + px, SIDE_Y0 + ht + 3),
                     dxfattribs={"layer": "SECTION"})

    # Hatch door outline (on left side = visible in side view)
    msp.add_line((SIDE_X0 + HATCH_X_START, SIDE_Y0 - 3),
                 (SIDE_X0 + HATCH_X_END, SIDE_Y0 - 3),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + HATCH_X_START, SIDE_Y0 - HATCH_WIDTH),
                 (SIDE_X0 + HATCH_X_END, SIDE_Y0 - HATCH_WIDTH),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + HATCH_X_START, SIDE_Y0 - 3),
                 (SIDE_X0 + HATCH_X_START, SIDE_Y0 - HATCH_WIDTH),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + HATCH_X_END, SIDE_Y0 - 3),
                 (SIDE_X0 + HATCH_X_END, SIDE_Y0 - HATCH_WIDTH),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("HATCH (mag. retained)", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SIDE_X0 + 120, SIDE_Y0 - HATCH_WIDTH - 5))

    # Longeron positions in side view (show as dots at key stations)
    for xst, longs in LONGERONS.items():
        if xst <= 260:
            for lx, ly in longs:
                msp.add_circle((SIDE_X0 + xst, SIDE_Y0 + ly),
                               LONGERON_DIA / 2,
                               dxfattribs={"layer": "SPAR"})

    # Battery outline (internal, shown dashed)
    batt_x_start = 150 - BATT_LENGTH / 2  # centered at X=150
    msp.add_line((SIDE_X0 + batt_x_start, SIDE_Y0 - BATT_HEIGHT / 2),
                 (SIDE_X0 + batt_x_start + BATT_LENGTH, SIDE_Y0 - BATT_HEIGHT / 2),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + batt_x_start, SIDE_Y0 + BATT_HEIGHT / 2),
                 (SIDE_X0 + batt_x_start + BATT_LENGTH, SIDE_Y0 + BATT_HEIGHT / 2),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + batt_x_start, SIDE_Y0 - BATT_HEIGHT / 2),
                 (SIDE_X0 + batt_x_start, SIDE_Y0 + BATT_HEIGHT / 2),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + batt_x_start + BATT_LENGTH, SIDE_Y0 - BATT_HEIGHT / 2),
                 (SIDE_X0 + batt_x_start + BATT_LENGTH, SIDE_Y0 + BATT_HEIGHT / 2),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("BATTERY 3S 1300mAh", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SIDE_X0 + batt_x_start + 5, SIDE_Y0 + 3))
    msp.add_text("78x38x28mm, 165g", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SIDE_X0 + batt_x_start + 5, SIDE_Y0 - 2))

    # Motor outline (internal at X=30-70)
    motor_r = MOTOR_BODY_DIA / 2
    msp.add_line((SIDE_X0 + 30, SIDE_Y0 - motor_r),
                 (SIDE_X0 + 70, SIDE_Y0 - motor_r),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SIDE_X0 + 30, SIDE_Y0 + motor_r),
                 (SIDE_X0 + 70, SIDE_Y0 + motor_r),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("MOTOR 28mm", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 35, SIDE_Y0 + 3))

    # Key dimensions on side view
    # Overall length
    msp.add_linear_dim(
        base=(SIDE_X0 + 130, SIDE_Y0 - 35),
        p1=(SIDE_X0, SIDE_Y0 - 30),
        p2=(SIDE_X0 + 260, SIDE_Y0 - 30),
        dimstyle="AEROFORGE",
    ).render()

    # Max height at X=150
    msp.add_linear_dim(
        base=(SIDE_X0 + 310, SIDE_Y0),
        p1=(SIDE_X0 + 280, SIDE_Y0 - 22),
        p2=(SIDE_X0 + 280, SIDE_Y0 + 22),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # Motor face diameter
    msp.add_linear_dim(
        base=(SIDE_X0 + 30, SIDE_Y0 + 25),
        p1=(SIDE_X0 + 25, SIDE_Y0 - 16),
        p2=(SIDE_X0 + 25, SIDE_Y0 + 16),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # Station labels
    for xst, label in [(0, "X=0"), (30, "X=30"), (90, "X=90"), (150, "X=150"), (260, "X=260")]:
        msp.add_line((SIDE_X0 + xst, SIDE_Y0 + half_height(xst) + 2),
                     (SIDE_X0 + xst, SIDE_Y0 + half_height(xst) + 8),
                     dxfattribs={"layer": "DIMENSION"})
        msp.add_text(label, height=1.8,
                     dxfattribs={"layer": "DIMENSION"}).set_placement(
            (SIDE_X0 + xst - 4, SIDE_Y0 + half_height(xst) + 9))

    # =========================================================================
    # TOP VIEW (planform) — shows width variation
    # =========================================================================
    msp.add_text("TOP VIEW — PLANFORM (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0, TOP_Y0 + 40))

    w_stations = [(xs[0], xs[1]) for xs in XSECTIONS]

    # Right profile (top in planform)
    draw_profile_polyline(msp, w_stations, +1, TOP_Y0, "OUTLINE", TOP_X0)
    # Left profile (bottom in planform)
    draw_profile_polyline(msp, w_stations, -1, TOP_Y0, "OUTLINE", TOP_X0)

    # Centerline
    msp.add_line((TOP_X0 - 5, TOP_Y0), (TOP_X0 + 270, TOP_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # L/R split line label
    msp.add_text("L/R SPLIT PLANE", height=1.8,
                 dxfattribs={"layer": "CENTERLINE"}).set_placement((TOP_X0 + 100, TOP_Y0 + 2))

    # Hatch door (on left side = bottom half in top view)
    msp.add_line((TOP_X0 + HATCH_X_START, TOP_Y0 - 3),
                 (TOP_X0 + HATCH_X_END, TOP_Y0 - 3),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((TOP_X0 + HATCH_X_START, TOP_Y0 - HATCH_WIDTH),
                 (TOP_X0 + HATCH_X_END, TOP_Y0 - HATCH_WIDTH),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((TOP_X0 + HATCH_X_START, TOP_Y0 - 3),
                 (TOP_X0 + HATCH_X_START, TOP_Y0 - HATCH_WIDTH),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((TOP_X0 + HATCH_X_END, TOP_Y0 - 3),
                 (TOP_X0 + HATCH_X_END, TOP_Y0 - HATCH_WIDTH),
                 dxfattribs={"layer": "HIDDEN"})

    # Max width dimension
    msp.add_linear_dim(
        base=(TOP_X0 + 320, TOP_Y0),
        p1=(TOP_X0 + 290, TOP_Y0 - 25),
        p2=(TOP_X0 + 290, TOP_Y0 + 25),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # Longeron positions in top view
    for xst, longs in LONGERONS.items():
        if xst <= 260:
            for lx, ly in longs:
                msp.add_circle((TOP_X0 + xst, TOP_Y0 + lx),
                               LONGERON_DIA / 2,
                               dxfattribs={"layer": "SPAR"})

    # Section cut lines for cross-sections
    for xcut, label in [(30, "A"), (150, "B"), (260, "C")]:
        hw = half_width(xcut) + 5
        msp.add_line((TOP_X0 + xcut, TOP_Y0 - hw),
                     (TOP_X0 + xcut, TOP_Y0 + hw),
                     dxfattribs={"layer": "SECTION"})
        msp.add_text(f"{label}", height=2.5,
                     dxfattribs={"layer": "SECTION"}).set_placement(
            (TOP_X0 + xcut - 2, TOP_Y0 + hw + 2))
        msp.add_text(f"{label}", height=2.5,
                     dxfattribs={"layer": "SECTION"}).set_placement(
            (TOP_X0 + xcut - 2, TOP_Y0 - hw - 5))

    # =========================================================================
    # FRONT VIEW — Cross-section at X=30 (motor mount face)
    # =========================================================================
    msp.add_text("SECTION A — X=30 (Motor Face)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((FRONT_X0 - 40, FRONT_Y0 + 35))
    msp.add_text("32mm dia circle", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((FRONT_X0 - 20, FRONT_Y0 + 28))

    # Outer circle at X=30 (32mm dia)
    r_outer = 16.0
    pts = ellipse_points(FRONT_X0, FRONT_Y0, r_outer, r_outer)
    for i in range(len(pts) - 1):
        msp.add_line(pts[i], pts[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Motor bore (28mm dia, internal)
    r_motor = MOTOR_BODY_DIA / 2
    pts_m = ellipse_points(FRONT_X0, FRONT_Y0, r_motor, r_motor)
    for i in range(len(pts_m) - 1):
        msp.add_line(pts_m[i], pts_m[i + 1], dxfattribs={"layer": "HIDDEN"})

    # Centerlines
    msp.add_line((FRONT_X0 - r_outer - 5, FRONT_Y0),
                 (FRONT_X0 + r_outer + 5, FRONT_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((FRONT_X0, FRONT_Y0 - r_outer - 5),
                 (FRONT_X0, FRONT_Y0 + r_outer + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Motor mount holes (M3 pattern, 4x at 90deg, 16mm PCD)
    pcd_r = 8.0  # 16mm PCD / 2
    m3_r = 1.5   # M3 hole radius
    for angle_deg in [45, 135, 225, 315]:
        rad = math.radians(angle_deg)
        cx = FRONT_X0 + pcd_r * math.cos(rad)
        cy = FRONT_Y0 + pcd_r * math.sin(rad)
        msp.add_circle((cx, cy), m3_r, dxfattribs={"layer": "SPAR"})
    msp.add_text("4x M3 holes", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((FRONT_X0 + 15, FRONT_Y0 + 12))
    msp.add_text("16mm PCD", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((FRONT_X0 + 15, FRONT_Y0 + 8))

    # Longeron positions at X=40 (closest available)
    for lx, ly in LONGERONS[40]:
        msp.add_circle((FRONT_X0 + lx, FRONT_Y0 + ly),
                       LONGERON_SLEEVE_DIA / 2,
                       dxfattribs={"layer": "SPAR"})
    msp.add_text("4x 2mm CF longerons", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((FRONT_X0 + 15, FRONT_Y0 - 15))

    # Diameter dimension
    msp.add_linear_dim(
        base=(FRONT_X0, FRONT_Y0 - r_outer - 8),
        p1=(FRONT_X0 - r_outer, FRONT_Y0 - r_outer - 5),
        p2=(FRONT_X0 + r_outer, FRONT_Y0 - r_outer - 5),
        dimstyle="AEROFORGE",
    ).render()

    # =========================================================================
    # REAR VIEW — Cross-section at X=260 (S1/S2 joint face)
    # =========================================================================
    msp.add_text("SECTION C — X=260 (S1/S2 Joint)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((REAR_X0 - 45, REAR_Y0 + 35))
    msp.add_text("38mm W x 34mm H egg shape", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((REAR_X0 - 30, REAR_Y0 + 28))

    # Outer egg shape at X=260 (38W x 34H, egg = wider at bottom)
    w260 = 38.0 / 2
    h260 = 34.0 / 2
    # Approximate egg shape: ellipse with slight bottom bias
    pts_rear = ellipse_points(REAR_X0, REAR_Y0, w260, h260)
    for i in range(len(pts_rear) - 1):
        msp.add_line(pts_rear[i], pts_rear[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Internal wall offset (0.6mm shell)
    iw = w260 - SHELL_WALL
    ih = h260 - SHELL_WALL
    pts_inner = ellipse_points(REAR_X0, REAR_Y0, iw, ih)
    for i in range(len(pts_inner) - 1):
        msp.add_line(pts_inner[i], pts_inner[i + 1], dxfattribs={"layer": "WALL"})

    # Centerlines
    msp.add_line((REAR_X0 - w260 - 5, REAR_Y0),
                 (REAR_X0 + w260 + 5, REAR_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((REAR_X0, REAR_Y0 - h260 - 5),
                 (REAR_X0, REAR_Y0 + h260 + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Longeron positions at X=260 (closest to wing saddle)
    for lx, ly in LONGERONS[260]:
        msp.add_circle((REAR_X0 + lx, REAR_Y0 + ly),
                       LONGERON_SLEEVE_DIA / 2,
                       dxfattribs={"layer": "SPAR"})

    # Interlocking teeth indicator (around perimeter)
    msp.add_text("INTERLOCKING TEETH (M4)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((REAR_X0 + 15, REAR_Y0 - 22))
    msp.add_text("1.5mm depth, 3mm pitch", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement((REAR_X0 + 15, REAR_Y0 - 26))

    # Width dimension
    msp.add_linear_dim(
        base=(REAR_X0, REAR_Y0 - h260 - 12),
        p1=(REAR_X0 - w260, REAR_Y0 - h260 - 8),
        p2=(REAR_X0 + w260, REAR_Y0 - h260 - 8),
        dimstyle="AEROFORGE",
    ).render()

    # Height dimension
    msp.add_linear_dim(
        base=(REAR_X0 + w260 + 12, REAR_Y0),
        p1=(REAR_X0 + w260 + 8, REAR_Y0 - h260),
        p2=(REAR_X0 + w260 + 8, REAR_Y0 + h260),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # =========================================================================
    # SECTION B — X=150 (Battery bay, MAX cross-section)
    # =========================================================================
    msp.add_text("SECTION B — X=150 (Max Section / Battery)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_X0 - 50, SEC_Y0 + 40))
    msp.add_text("50mm W x 44mm H ellipse", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_X0 - 25, SEC_Y0 + 33))

    # Outer ellipse at X=150 (50W x 44H)
    w150 = MAX_WIDTH / 2
    h150 = MAX_HEIGHT / 2
    pts_150 = ellipse_points(SEC_X0, SEC_Y0, w150, h150)
    for i in range(len(pts_150) - 1):
        msp.add_line(pts_150[i], pts_150[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Inner wall
    iw150 = w150 - SHELL_WALL
    ih150 = h150 - SHELL_WALL
    pts_i150 = ellipse_points(SEC_X0, SEC_Y0, iw150, ih150)
    for i in range(len(pts_i150) - 1):
        msp.add_line(pts_i150[i], pts_i150[i + 1], dxfattribs={"layer": "WALL"})

    # Battery cross-section (38W x 28H, centered)
    bw = BATT_WIDTH / 2
    bh = BATT_HEIGHT / 2
    batt_y_offset = -3  # battery sits slightly below center (on tray)
    msp.add_line((SEC_X0 - bw, SEC_Y0 + batt_y_offset - bh),
                 (SEC_X0 + bw, SEC_Y0 + batt_y_offset - bh),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SEC_X0 - bw, SEC_Y0 + batt_y_offset + bh),
                 (SEC_X0 + bw, SEC_Y0 + batt_y_offset + bh),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SEC_X0 - bw, SEC_Y0 + batt_y_offset - bh),
                 (SEC_X0 - bw, SEC_Y0 + batt_y_offset + bh),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((SEC_X0 + bw, SEC_Y0 + batt_y_offset - bh),
                 (SEC_X0 + bw, SEC_Y0 + batt_y_offset + bh),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("BATT", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_X0 - 6, SEC_Y0 + batt_y_offset - 2))

    # Centerlines
    msp.add_line((SEC_X0 - w150 - 5, SEC_Y0),
                 (SEC_X0 + w150 + 5, SEC_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_X0, SEC_Y0 - h150 - 5),
                 (SEC_X0, SEC_Y0 + h150 + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Longeron positions at X=150
    for lx, ly in LONGERONS[150]:
        msp.add_circle((SEC_X0 + lx, SEC_Y0 + ly),
                       LONGERON_SLEEVE_DIA / 2,
                       dxfattribs={"layer": "SPAR"})

    # Hatch door opening (on left side)
    msp.add_line((SEC_X0 - 3, SEC_Y0 - 3),
                 (SEC_X0 - 3, SEC_Y0 - HATCH_WIDTH),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("HATCH", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_X0 - 15, SEC_Y0 - HATCH_WIDTH - 4))

    # Width dimension
    msp.add_linear_dim(
        base=(SEC_X0, SEC_Y0 - h150 - 12),
        p1=(SEC_X0 - w150, SEC_Y0 - h150 - 8),
        p2=(SEC_X0 + w150, SEC_Y0 - h150 - 8),
        dimstyle="AEROFORGE",
    ).render()

    # Height dimension
    msp.add_linear_dim(
        base=(SEC_X0 + w150 + 15, SEC_Y0),
        p1=(SEC_X0 + w150 + 10, SEC_Y0 - h150),
        p2=(SEC_X0 + w150 + 10, SEC_Y0 + h150),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # =========================================================================
    # NOTES
    # =========================================================================
    notes = [
        "NOTES:",
        "1. All dims mm. Scale 1:1. S1 is the nose section X=0 to X=260mm.",
        "2. Prints as LEFT/RIGHT halves split along vertical centerline (M2).",
        "   Each half: ~260mm L x 25mm W x 44mm H. Flat on bed.",
        "3. Shell: 0.6mm LW-PLA (X=90-260), PETG (X=30-90, motor thermal M3).",
        "4. Spinner tip (X=0-10mm) is a separate nose cone insert.",
        "5. Motor mount: CF-PETG ring, 35mm OD, 28mm bore, 4x M3 at 16mm PCD.",
        "6. Battery bay: 78x38x28mm, adjustable +/-25mm via M3 nylon threaded rod.",
        "7. Access hatch: LEFT side, X=80-210mm, 130x25mm, 3x neodymium magnets.",
        "8. 4x 2mm CF longerons pass through entire section. Spacing per table.",
        "9. Joint face at X=260: interlocking teeth 1.5mm depth, 3mm pitch (M4).",
        "10. 2x 2mm steel alignment dowels at joint face.",
        "11. ESC bay at X=70-120mm (45x25x12mm ESC fits in 34x31mm internal).",
        "12. Receiver bay at X=190-230mm (52x35x15mm Rx in 42x36mm internal).",
    ]
    ny = 160
    for n in notes:
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((25, ny))
        ny -= 5

    # =========================================================================
    # INTERNAL LAYOUT TABLE
    # =========================================================================
    msp.add_text("INTERNAL LAYOUT (X stations):", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((25, 90))
    table_data = [
        "X=0-10: Spinner tip (ogive nose cone insert)",
        "X=10-30: Spinner cone (32mm dia at base)",
        "X=30-70: Motor bay (CF-PETG mount, PETG shell, 28mm motor)",
        "X=70-90: ESC bay (transition PETG->LW-PLA at X=90)",
        "X=90-120: Battery forward zone (CG adjust range start)",
        "X=120-180: Battery main bay (MAX section 50x44mm at X=150)",
        "X=180-210: Receiver bay (52x35x15mm Turnigy 9X V2)",
        "X=210-250: Transition / wiring routing",
        "X=250-260: Joint face to S2 (interlocking teeth + dowels)",
    ]
    ty = 84
    for line in table_data:
        msp.add_text(line, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((30, ty))
        ty -= 4.5

    # =========================================================================
    # SAVE
    # =========================================================================
    out_path = "cad/components/fuselage/Fuselage_S1_Nose/Fuselage_S1_Nose_drawing.dxf"
    save_dxf_and_png(doc, out_path, dpi=300)
    print("Fuselage_S1_Nose drawing complete.")


if __name__ == "__main__":
    main()
