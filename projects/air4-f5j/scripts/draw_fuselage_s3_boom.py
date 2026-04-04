"""
Fuselage_S3_Boom Component Drawing
=====================================
Section S3 (X=430 to X=660mm) of the integrated fuselage.
Simple tapered tube, modified Sears-Haack profile, lightest section.

Views:
  - SIDE VIEW (profile): fuselage side silhouette
  - TOP VIEW (planform): fuselage top silhouette
  - SECTION A at X=430 (S2/S3 joint face, entry)
  - SECTION B at X=550 (mid-boom)
  - SECTION C at X=660 (S3/S4a joint face, exit)

Dimensions from DESIGN_CONSENSUS.md v2.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# ============================================================================
# S3 BOOM GEOMETRY DATA
# ============================================================================

XSECTIONS = [
    (430, 22, 19, "ellipse"),    # S2/S3 joint
    (460, 21, 18, "ellipse"),    # early taper
    (500, 18, 16, "ellipse"),    # pushrod zone
    (550, 16, 15, "ellipse"),    # mid-boom
    (600, 14, 14, "circle"),     # approaching circular
    (630, 13.5, 13.5, "circle"), # near-circular
    (660, 13, 13, "circle"),     # S3/S4a joint (circular)
]

LONGERONS = {
    430: [(+6, +5), (-6, +5), (+6, -5), (-6, -5)],   # 12x10
    500: [(+6, +5), (-6, +5), (+6, -5), (-6, -5)],   # 12x10 (interpolated)
    550: [(+5, +4.5), (-5, +4.5), (+5, -4.5), (-5, -4.5)],  # interpolated
    660: [(+4, +4), (-4, +4), (+4, -4), (-4, -4)],   # 8x8
}

S3_LENGTH = 230.0
SHELL_WALL = 0.6
LONGERON_DIA = 2.0
LONGERON_SLEEVE_DIA = 2.5
LONGERON_CHANNEL_DIA = 2.2  # printed channel for 2mm rod
PUSHROD_OD = 3.0
PUSHROD_TUBE_OD = 2.0  # 2mm OD PTFE tube (1mm wire inside)
X_OFFSET = 430  # S3 starts at X=430


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
            (x_offset + x0 - X_OFFSET, y_offset + dim_sign * val0 / 2),
            (x_offset + x1 - X_OFFSET, y_offset + dim_sign * val1 / 2),
            dxfattribs={"layer": layer}
        )


def main():
    doc = setup_drawing(
        title="Fuselage_S3_Boom",
        subtitle="Boom section X=430-660mm. Modified Sears-Haack taper. Lightest section (~5g).",
        material="LW-PLA 0.6mm shell | Print: horizontal, belly-down (vase mode candidate)",
        mass="~5g (shell only, excl. longerons)",
        scale="1:1",
        sheet_size="A1",
        status="FOR APPROVAL",
        revision="v1",
        orientation_labels={"fwd": "FWD", "inbd": "NOSE"},
    )
    msp = doc.modelspace()

    SIDE_X0 = 40.0
    SIDE_Y0 = 420.0
    TOP_X0 = 40.0
    TOP_Y0 = 310.0
    SEC_A_X0 = 380.0
    SEC_A_Y0 = 510.0
    SEC_B_X0 = 530.0
    SEC_B_Y0 = 510.0
    SEC_C_X0 = 680.0
    SEC_C_Y0 = 510.0

    # =========================================================================
    # SIDE VIEW
    # =========================================================================
    msp.add_text("SIDE VIEW — PROFILE (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0, SIDE_Y0 + 22))

    h_stations = [(xs[0], xs[2]) for xs in XSECTIONS]
    draw_profile_polyline(msp, h_stations, +1, SIDE_Y0, "OUTLINE", SIDE_X0)
    draw_profile_polyline(msp, h_stations, -1, SIDE_Y0, "OUTLINE", SIDE_X0)

    # Centerline
    msp.add_line((SIDE_X0 - 5, SIDE_Y0), (SIDE_X0 + 240, SIDE_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Pushrod channels (2x internal, shown dashed)
    for py in [2.5, -2.5]:
        msp.add_line((SIDE_X0, SIDE_Y0 + py),
                     (SIDE_X0 + 230, SIDE_Y0 + py),
                     dxfattribs={"layer": "HIDDEN"})
    msp.add_text("2x PUSHROD CHANNEL (3mm PTFE)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 50, SIDE_Y0 + 5))

    # Longeron positions
    for xst, longs in LONGERONS.items():
        rel_x = xst - X_OFFSET
        if 0 <= rel_x <= 230:
            for lx, ly in longs:
                msp.add_circle((SIDE_X0 + rel_x, SIDE_Y0 + ly),
                               LONGERON_DIA / 2,
                               dxfattribs={"layer": "SPAR"})

    # Overall length dimension
    msp.add_linear_dim(
        base=(SIDE_X0 + 115, SIDE_Y0 - 20),
        p1=(SIDE_X0, SIDE_Y0 - 16),
        p2=(SIDE_X0 + 230, SIDE_Y0 - 16),
        dimstyle="AEROFORGE",
    ).render()

    # Station labels
    for xst, label in [(430, "X=430"), (500, "X=500"), (550, "X=550"), (660, "X=660")]:
        rel_x = xst - X_OFFSET
        ht = half_height(xst)
        msp.add_line((SIDE_X0 + rel_x, SIDE_Y0 + ht + 2),
                     (SIDE_X0 + rel_x, SIDE_Y0 + ht + 8),
                     dxfattribs={"layer": "DIMENSION"})
        msp.add_text(label, height=1.8,
                     dxfattribs={"layer": "DIMENSION"}).set_placement(
            (SIDE_X0 + rel_x - 6, SIDE_Y0 + ht + 9))

    # Sears-Haack annotation
    msp.add_text("MODIFIED SEARS-HAACK TAPER", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 50, SIDE_Y0 + 15))
    msp.add_text("Ellipse -> Circle transition", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 50, SIDE_Y0 + 12))

    # =========================================================================
    # TOP VIEW
    # =========================================================================
    msp.add_text("TOP VIEW — PLANFORM (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0, TOP_Y0 + 22))

    w_stations = [(xs[0], xs[1]) for xs in XSECTIONS]
    draw_profile_polyline(msp, w_stations, +1, TOP_Y0, "OUTLINE", TOP_X0)
    draw_profile_polyline(msp, w_stations, -1, TOP_Y0, "OUTLINE", TOP_X0)

    msp.add_line((TOP_X0 - 5, TOP_Y0), (TOP_X0 + 240, TOP_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Longeron channels in top view
    for xst, longs in LONGERONS.items():
        rel_x = xst - X_OFFSET
        if 0 <= rel_x <= 230:
            for lx, ly in longs:
                msp.add_circle((TOP_X0 + rel_x, TOP_Y0 + lx),
                               LONGERON_DIA / 2,
                               dxfattribs={"layer": "SPAR"})

    # Section cut lines
    for xcut, label in [(430, "A"), (550, "B"), (660, "C")]:
        rel_x = xcut - X_OFFSET
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
    # SECTION A — X=430 (entry)
    # =========================================================================
    msp.add_text("SECTION A — X=430 (S2/S3 Joint)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 45, SEC_A_Y0 + 25))
    msp.add_text("22mm W x 19mm H ellipse", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 20, SEC_A_Y0 + 19))

    w_a = 22.0 / 2
    h_a = 19.0 / 2

    # Scale cross-sections up 2x for visibility (small sections)
    CS = 2.0  # cross-section scale factor for display
    w_a_s = w_a * CS
    h_a_s = h_a * CS
    msp.add_text("(shown 2:1 scale)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 15, SEC_A_Y0 + 15))

    pts_a = ellipse_points(SEC_A_X0, SEC_A_Y0, w_a_s, h_a_s)
    for i in range(len(pts_a) - 1):
        msp.add_line(pts_a[i], pts_a[i + 1], dxfattribs={"layer": "OUTLINE"})

    iw_a = (w_a - SHELL_WALL) * CS
    ih_a = (h_a - SHELL_WALL) * CS
    pts_ia = ellipse_points(SEC_A_X0, SEC_A_Y0, iw_a, ih_a)
    for i in range(len(pts_ia) - 1):
        msp.add_line(pts_ia[i], pts_ia[i + 1], dxfattribs={"layer": "WALL"})

    # Centerlines
    msp.add_line((SEC_A_X0 - w_a_s - 5, SEC_A_Y0),
                 (SEC_A_X0 + w_a_s + 5, SEC_A_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_A_X0, SEC_A_Y0 - h_a_s - 5),
                 (SEC_A_X0, SEC_A_Y0 + h_a_s + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Longerons (scaled)
    for lx, ly in LONGERONS[430]:
        msp.add_circle((SEC_A_X0 + lx * CS, SEC_A_Y0 + ly * CS),
                       LONGERON_SLEEVE_DIA / 2 * CS,
                       dxfattribs={"layer": "SPAR"})

    # Pushrod channels (scaled)
    msp.add_circle((SEC_A_X0 - 3 * CS, SEC_A_Y0 - 4 * CS), PUSHROD_OD / 2 * CS,
                   dxfattribs={"layer": "HIDDEN"})
    msp.add_circle((SEC_A_X0 + 3 * CS, SEC_A_Y0 - 4 * CS), PUSHROD_OD / 2 * CS,
                   dxfattribs={"layer": "HIDDEN"})

    # =========================================================================
    # SECTION B — X=550 (mid-boom)
    # =========================================================================
    msp.add_text("SECTION B — X=550 (Mid-Boom)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 40, SEC_B_Y0 + 25))
    msp.add_text("16mm W x 15mm H ellipse", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 20, SEC_B_Y0 + 19))

    w_b = 16.0 / 2
    h_b = 15.0 / 2
    w_b_s = w_b * CS
    h_b_s = h_b * CS
    msp.add_text("(shown 2:1 scale)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 15, SEC_B_Y0 + 15))

    pts_b = ellipse_points(SEC_B_X0, SEC_B_Y0, w_b_s, h_b_s)
    for i in range(len(pts_b) - 1):
        msp.add_line(pts_b[i], pts_b[i + 1], dxfattribs={"layer": "OUTLINE"})

    iw_b = (w_b - SHELL_WALL) * CS
    ih_b = (h_b - SHELL_WALL) * CS
    pts_ib = ellipse_points(SEC_B_X0, SEC_B_Y0, iw_b, ih_b)
    for i in range(len(pts_ib) - 1):
        msp.add_line(pts_ib[i], pts_ib[i + 1], dxfattribs={"layer": "WALL"})

    msp.add_line((SEC_B_X0 - w_b_s - 5, SEC_B_Y0),
                 (SEC_B_X0 + w_b_s + 5, SEC_B_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_B_X0, SEC_B_Y0 - h_b_s - 5),
                 (SEC_B_X0, SEC_B_Y0 + h_b_s + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    for lx, ly in LONGERONS[550]:
        msp.add_circle((SEC_B_X0 + lx * CS, SEC_B_Y0 + ly * CS),
                       LONGERON_SLEEVE_DIA / 2 * CS,
                       dxfattribs={"layer": "SPAR"})

    # Pushrod channels
    msp.add_circle((SEC_B_X0 - 2 * CS, SEC_B_Y0 - 3 * CS), PUSHROD_OD / 2 * CS,
                   dxfattribs={"layer": "HIDDEN"})
    msp.add_circle((SEC_B_X0 + 2 * CS, SEC_B_Y0 - 3 * CS), PUSHROD_OD / 2 * CS,
                   dxfattribs={"layer": "HIDDEN"})
    msp.add_text("PUSHRODS", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_B_X0 + 5 * CS, SEC_B_Y0 - 4 * CS))

    # =========================================================================
    # SECTION C — X=660 (exit, circular)
    # =========================================================================
    msp.add_text("SECTION C — X=660 (S3/S4a Joint)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 45, SEC_C_Y0 + 25))
    msp.add_text("13mm dia circle", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 15, SEC_C_Y0 + 19))

    r_c = 13.0 / 2
    r_c_s = r_c * CS
    msp.add_text("(shown 2:1 scale)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 15, SEC_C_Y0 + 15))

    pts_c = ellipse_points(SEC_C_X0, SEC_C_Y0, r_c_s, r_c_s)
    for i in range(len(pts_c) - 1):
        msp.add_line(pts_c[i], pts_c[i + 1], dxfattribs={"layer": "OUTLINE"})

    ri_c = (r_c - SHELL_WALL) * CS
    pts_ic = ellipse_points(SEC_C_X0, SEC_C_Y0, ri_c, ri_c)
    for i in range(len(pts_ic) - 1):
        msp.add_line(pts_ic[i], pts_ic[i + 1], dxfattribs={"layer": "WALL"})

    msp.add_line((SEC_C_X0 - r_c_s - 5, SEC_C_Y0),
                 (SEC_C_X0 + r_c_s + 5, SEC_C_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_C_X0, SEC_C_Y0 - r_c_s - 5),
                 (SEC_C_X0, SEC_C_Y0 + r_c_s + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    for lx, ly in LONGERONS[660]:
        msp.add_circle((SEC_C_X0 + lx * CS, SEC_C_Y0 + ly * CS),
                       LONGERON_SLEEVE_DIA / 2 * CS,
                       dxfattribs={"layer": "SPAR"})

    # Pushrod channels
    msp.add_circle((SEC_C_X0 - 1.5 * CS, SEC_C_Y0 - 2.5 * CS), PUSHROD_OD / 2 * CS,
                   dxfattribs={"layer": "HIDDEN"})
    msp.add_circle((SEC_C_X0 + 1.5 * CS, SEC_C_Y0 - 2.5 * CS), PUSHROD_OD / 2 * CS,
                   dxfattribs={"layer": "HIDDEN"})

    msp.add_text("INTERLOCKING TEETH (M4)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 + r_c_s + 5, SEC_C_Y0 - 5))

    # =========================================================================
    # NOTES
    # =========================================================================
    notes = [
        "NOTES:",
        "1. All dims mm. Scale 1:1 (cross-sections shown 2:1). S3 is boom X=430-660mm.",
        "2. Prints horizontal, belly-down. 230mm L x 22mm W x 19mm H. Vase mode candidate.",
        "3. Shell: 0.6mm LW-PLA. Lightest section at ~5g (shell only).",
        "4. Modified Sears-Haack profile: ellipse (22x19) -> circle (13mm) transition.",
        "5. 4x longeron channels (2.2mm ID for 2mm CF rods), spacing 12x10mm to 8x8mm.",
        "6. 2x pushrod channels (3mm OD PTFE tube): elevator + rudder, bottom quadrant.",
        "7. Vase mode printing possible but longeron/pushrod channels need multi-perimeter.",
        "8. Recommend: 0.6mm wall vase mode with printed longeron+pushrod inserts bonded in.",
        "9. Joint faces at X=430 and X=660: interlocking teeth 1.5mm depth, 3mm pitch (M4).",
        "10. 2x 2mm steel alignment dowels at each joint face.",
        "11. No internal bulkheads needed — longerons provide all structural stiffness.",
        "12. Total mass budget: ~5g shell + portion of 21.1g longerons passing through.",
    ]
    ny = 160
    for n in notes:
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((25, ny))
        ny -= 5

    # =========================================================================
    # LONGERON SPACING TABLE
    # =========================================================================
    msp.add_text("LONGERON SPACING (4x 2mm CF rods):", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((25, 85))
    table = [
        "X=430: 12mm W x 10mm H (entry, matches S2 exit)",
        "X=500: 12mm W x 10mm H (pushrod zone)",
        "X=550: 10mm W x 9mm H (mid-boom)",
        "X=660: 8mm W x 8mm H (exit, square layout, pre-fin)",
    ]
    ty = 79
    for line in table:
        msp.add_text(line, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((30, ty))
        ty -= 4.5

    # =========================================================================
    # SAVE
    # =========================================================================
    out_path = "cad/components/fuselage/Fuselage_S3_Boom/Fuselage_S3_Boom_drawing.dxf"
    save_dxf_and_png(doc, out_path, dpi=300)
    print("Fuselage_S3_Boom drawing complete.")


if __name__ == "__main__":
    main()
