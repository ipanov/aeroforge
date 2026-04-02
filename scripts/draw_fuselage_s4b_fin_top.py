"""
Fuselage_S4b_Fin_Top Component Drawing
=========================================
Section S4b (X=880 to X=1046mm) of the integrated fuselage.
Upper VStab: HT-14 -> HT-12 blend, tapering to tip.
HStab bearing mount, rudder hinge continuation, tip cap.

Views:
  - SIDE VIEW (profile): fin tapering to tip
  - FRONT VIEW: cross-section showing fin airfoil shape
  - SECTION A at X=880 (S4a/S4b joint face)
  - SECTION B at X=911 (HStab pivot station)
  - SECTION C at X=1000 (near tip)

Dimensions from DESIGN_CONSENSUS.md v2.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# ============================================================================
# S4b FIN TOP GEOMETRY DATA
# ============================================================================

X_OFFSET = 880

# Fin height at each station (from body center to fin tip)
FIN_HEIGHTS = [
    (880, 140),     # S4a/S4b joint, fin at ~140mm
    (911, 145),     # HStab pivot station (near max)
    (940, 150),     # approaching max
    (970, 155),     # near max
    (1000, 140),    # tapering
    (1020, 100),    # rapid taper
    (1040, 40),     # near tip
    (1046, 0),      # VStab TE (tip closure)
]

# Fin chord at each station (LE to TE)
FIN_CHORDS = [
    (880, 175),     # near-root
    (911, 165),     # HStab pivot
    (940, 150),     # tapering
    (970, 130),     # tapering
    (1000, 105),    # mid-upper
    (1020, 80),     # narrowing
    (1040, 40),     # near tip
    (1046, 0),      # tip closure
]

# Body tube remnant (passes into S4b from S4a)
BODY_DIA = 8.5  # mm at X=880, quickly merges into fin base

LONGERONS = {
    880: [(+2, +3), (-2, +3), (+2, -3), (-2, -3)],     # 4x6
}

S4B_LENGTH = 166.0
SHELL_WALL = 0.5     # vase mode fin skin
LONGERON_DIA = 2.0
LONGERON_SLEEVE_DIA = 2.5
REAR_SPAR_DIA = 1.5
PETG_SLEEVE_OD = 1.2
PETG_SLEEVE_ID = 0.6
HSTAB_BEARING_W = 30.0   # PETG block width
HSTAB_BEARING_H = 15.0   # PETG block height
HSTAB_BEARING_D = 15.0   # PETG block depth (chordwise)
BRASS_TUBE_OD = 4.0
BRASS_TUBE_ID = 3.0
BRASS_TUBE_SPACING = 28.0  # between bearing centers
HSTAB_PIVOT_X = 911.0     # fuselage station of HStab pivot


def interp_list(x, data):
    for i in range(len(data) - 1):
        x0, v0 = data[i]
        x1, v1 = data[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0) if x1 != x0 else 0
            return v0 + t * (v1 - v0)
    return data[-1][1]


def ellipse_points(cx, cy, a, b, n=80):
    pts = []
    for i in range(n + 1):
        theta = 2 * math.pi * i / n
        pts.append((cx + a * math.cos(theta), cy + b * math.sin(theta)))
    return pts


def main():
    doc = setup_drawing(
        title="Fuselage_S4b_Fin_Top",
        subtitle="Fin top section X=880-1046mm. HT-14->HT-12 blend. HStab bearing mount. Tip cap.",
        material="LW-PLA 0.5mm shell (vase mode) | PETG HStab bearing block | Print: fin flat",
        mass="~10g (shell+structure, excl. longerons, incl. PETG bearing)",
        scale="1:1",
        sheet_size="A1",
        status="FOR APPROVAL",
        revision="v1",
        orientation_labels={"fwd": "FWD", "inbd": "NOSE"},
    )
    msp = doc.modelspace()

    SIDE_X0 = 40.0
    SIDE_Y0 = 330.0
    TOP_X0 = 40.0
    TOP_Y0 = 180.0
    SEC_A_X0 = 350.0
    SEC_A_Y0 = 510.0
    SEC_B_X0 = 520.0
    SEC_B_Y0 = 510.0
    SEC_C_X0 = 700.0
    SEC_C_Y0 = 510.0

    # =========================================================================
    # SIDE VIEW — shows fin planform tapering to tip
    # =========================================================================
    msp.add_text("SIDE VIEW — FIN PROFILE (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0, SIDE_Y0 + 175))

    # Bottom edge (body tube base, essentially at Y=0 for the fin)
    # The body at this section is just the base of the fin
    body_half = BODY_DIA / 2
    msp.add_line((SIDE_X0, SIDE_Y0 - body_half),
                 (SIDE_X0 + 166, SIDE_Y0 - body_half),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_line((SIDE_X0, SIDE_Y0 + body_half),
                 (SIDE_X0 + 10, SIDE_Y0 + body_half),
                 dxfattribs={"layer": "OUTLINE"})

    # Fin top edge (LE sweep, tapering to tip)
    for i in range(len(FIN_HEIGHTS) - 1):
        x0, fh0 = FIN_HEIGHTS[i]
        x1, fh1 = FIN_HEIGHTS[i + 1]
        msp.add_line(
            (SIDE_X0 + (x0 - X_OFFSET), SIDE_Y0 + fh0),
            (SIDE_X0 + (x1 - X_OFFSET), SIDE_Y0 + fh1),
            dxfattribs={"layer": "OUTLINE"}
        )

    # Close the TE at X=1046
    msp.add_line(
        (SIDE_X0 + 166, SIDE_Y0 - body_half),
        (SIDE_X0 + 166, SIDE_Y0),
        dxfattribs={"layer": "OUTLINE"}
    )

    # Centerline (body axis)
    msp.add_line((SIDE_X0 - 5, SIDE_Y0), (SIDE_X0 + 175, SIDE_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Rudder hinge line (62% chord at root, 65% at tip)
    for i in range(len(FIN_HEIGHTS) - 1):
        x0, fh0 = FIN_HEIGHTS[i]
        x1, fh1 = FIN_HEIGHTS[i + 1]
        if fh0 > 5 and fh1 > 5:
            # Interpolate hinge fraction: 62% at root to 65% at tip
            t0 = (x0 - 880) / 166
            t1 = (x1 - 880) / 166
            hf0 = 0.62 + t0 * 0.03
            hf1 = 0.62 + t1 * 0.03
            msp.add_line(
                (SIDE_X0 + (x0 - X_OFFSET), SIDE_Y0 + fh0 * hf0),
                (SIDE_X0 + (x1 - X_OFFSET), SIDE_Y0 + fh1 * hf1),
                dxfattribs={"layer": "HIDDEN"}
            )
    msp.add_text("RUDDER HINGE LINE (62-65% chord)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 10, SIDE_Y0 + 100))

    # HStab pivot station marker
    pivot_rel = HSTAB_PIVOT_X - X_OFFSET  # 31mm from S4b start
    msp.add_line((SIDE_X0 + pivot_rel, SIDE_Y0 - body_half - 5),
                 (SIDE_X0 + pivot_rel, SIDE_Y0 - body_half - 15),
                 dxfattribs={"layer": "SECTION"})
    msp.add_text("HStab PIVOT X=911", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SIDE_X0 + pivot_rel - 10, SIDE_Y0 - body_half - 20))

    # PETG bearing block outline (at HStab pivot)
    bear_x = SIDE_X0 + pivot_rel - HSTAB_BEARING_D / 2
    bear_y = SIDE_Y0 - body_half
    msp.add_line((bear_x, bear_y), (bear_x + HSTAB_BEARING_D, bear_y),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((bear_x, bear_y - HSTAB_BEARING_H),
                 (bear_x + HSTAB_BEARING_D, bear_y - HSTAB_BEARING_H),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((bear_x, bear_y), (bear_x, bear_y - HSTAB_BEARING_H),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((bear_x + HSTAB_BEARING_D, bear_y),
                 (bear_x + HSTAB_BEARING_D, bear_y - HSTAB_BEARING_H),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("PETG BEARING BLOCK", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (bear_x - 5, bear_y - HSTAB_BEARING_H - 5))
    msp.add_text("30x15x15mm + 2x brass tubes", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (bear_x - 5, bear_y - HSTAB_BEARING_H - 9))

    # Brass tube circles on bearing block (side view = holes visible)
    for tube_x_off in [-BRASS_TUBE_SPACING / 2, +BRASS_TUBE_SPACING / 2]:
        msp.add_circle((SIDE_X0 + pivot_rel, bear_y - HSTAB_BEARING_H / 2),
                       BRASS_TUBE_OD / 2,
                       dxfattribs={"layer": "SPAR"})

    # 5x PETG hinge sleeves continuation
    msp.add_text("5x PETG HINGE SLEEVES (continuation)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 40, SIDE_Y0 + 115))
    msp.add_text("@ 20mm intervals in rudder zone", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 40, SIDE_Y0 + 111))

    # Tip cap closure annotation
    msp.add_text("TIP CAP CLOSURE", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 140, SIDE_Y0 + 25))

    # Overall length dimension
    msp.add_linear_dim(
        base=(SIDE_X0 + 83, SIDE_Y0 - 25),
        p1=(SIDE_X0, SIDE_Y0 - 20),
        p2=(SIDE_X0 + 166, SIDE_Y0 - 20),
        dimstyle="AEROFORGE",
    ).render()

    # Max fin height dimension
    max_fh = max(fh for _, fh in FIN_HEIGHTS)
    max_fh_x = [x for x, fh in FIN_HEIGHTS if fh == max_fh][0]
    rel_max = max_fh_x - X_OFFSET
    msp.add_linear_dim(
        base=(SIDE_X0 + rel_max + 15, SIDE_Y0 + max_fh / 2),
        p1=(SIDE_X0 + rel_max + 10, SIDE_Y0),
        p2=(SIDE_X0 + rel_max + 10, SIDE_Y0 + max_fh),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # Station labels
    for xst, label in [(880, "X=880"), (911, "X=911"), (1000, "X=1000"), (1046, "X=1046")]:
        rel_x = xst - X_OFFSET
        fh = interp_list(xst, FIN_HEIGHTS)
        top_y = max(fh, body_half)
        msp.add_line((SIDE_X0 + rel_x, SIDE_Y0 + top_y + 2),
                     (SIDE_X0 + rel_x, SIDE_Y0 + top_y + 8),
                     dxfattribs={"layer": "DIMENSION"})
        msp.add_text(label, height=1.8,
                     dxfattribs={"layer": "DIMENSION"}).set_placement(
            (SIDE_X0 + rel_x - 6, SIDE_Y0 + top_y + 9))

    # =========================================================================
    # TOP VIEW — shows fin chord tapering (planform from above)
    # =========================================================================
    msp.add_text("TOP VIEW — FIN PLANFORM (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0, TOP_Y0 + 55))

    # LE line (fin leading edge)
    for i in range(len(FIN_CHORDS) - 1):
        x0, c0 = FIN_CHORDS[i]
        x1, c1 = FIN_CHORDS[i + 1]
        # In top view: X axis is fuselage axis, Y axis shows chord
        # LE offset from some reference. Let's center the chord.
        msp.add_line(
            (TOP_X0 + (x0 - X_OFFSET), TOP_Y0 + c0 / 2),
            (TOP_X0 + (x1 - X_OFFSET), TOP_Y0 + c1 / 2),
            dxfattribs={"layer": "OUTLINE"}
        )
        msp.add_line(
            (TOP_X0 + (x0 - X_OFFSET), TOP_Y0 - c0 / 2),
            (TOP_X0 + (x1 - X_OFFSET), TOP_Y0 - c1 / 2),
            dxfattribs={"layer": "OUTLINE"}
        )

    # Close at tip
    msp.add_line((TOP_X0 + 166, TOP_Y0), (TOP_X0 + 166, TOP_Y0),
                 dxfattribs={"layer": "OUTLINE"})

    # Centerline
    msp.add_line((TOP_X0 - 5, TOP_Y0), (TOP_X0 + 175, TOP_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Rudder hinge line in planform
    for i in range(len(FIN_CHORDS) - 1):
        x0, c0 = FIN_CHORDS[i]
        x1, c1 = FIN_CHORDS[i + 1]
        if c0 > 0 and c1 > 0:
            t0 = (x0 - 880) / 166
            t1 = (x1 - 880) / 166
            hf0 = 0.62 + t0 * 0.03
            hf1 = 0.62 + t1 * 0.03
            # Hinge line offset from LE
            hy0 = c0 / 2 - c0 * hf0
            hy1 = c1 / 2 - c1 * hf1
            msp.add_line(
                (TOP_X0 + (x0 - X_OFFSET), TOP_Y0 + hy0),
                (TOP_X0 + (x1 - X_OFFSET), TOP_Y0 + hy1),
                dxfattribs={"layer": "HIDDEN"}
            )

    msp.add_text("LE", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0 - 2, TOP_Y0 + 90))
    msp.add_text("TE", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0 - 2, TOP_Y0 - 92))

    # HStab bearing position
    msp.add_text("HStab BEARING", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (TOP_X0 + pivot_rel - 5, TOP_Y0 - 95))

    # Section cut lines
    for xcut, label in [(880, "A"), (911, "B"), (1000, "C")]:
        rel_x = xcut - X_OFFSET
        chord = interp_list(xcut, FIN_CHORDS)
        hw = chord / 2 + 5
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
    # SECTION A — X=880 (S4a/S4b joint, HT-14 airfoil)
    # =========================================================================
    CS = 0.5
    msp.add_text("SECTION A — X=880 (S4a/S4b Joint)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 45, SEC_A_Y0 + 55))
    msp.add_text("HT-14, ~175mm chord, 140mm fin height", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 35, SEC_A_Y0 + 49))
    msp.add_text("(shown 0.5:1 scale)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 15, SEC_A_Y0 + 45))

    # Simplified HT-14 cross-section as elongated ellipse
    fin_h_a = 140 * CS
    fin_thick_a = 175 * 0.075 * CS  # 7.5% max thickness
    pts_a = ellipse_points(SEC_A_X0, SEC_A_Y0 + fin_h_a / 2, fin_thick_a / 2, fin_h_a / 2)
    for i in range(len(pts_a) - 1):
        msp.add_line(pts_a[i], pts_a[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Body circle at base
    body_r = BODY_DIA / 2 * CS
    pts_body = ellipse_points(SEC_A_X0, SEC_A_Y0, body_r * 2, body_r)
    for i in range(len(pts_body) - 1):
        msp.add_line(pts_body[i], pts_body[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Centerline
    msp.add_line((SEC_A_X0, SEC_A_Y0 - body_r - 5),
                 (SEC_A_X0, SEC_A_Y0 + fin_h_a + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Longerons
    for lx, ly in LONGERONS[880]:
        msp.add_circle((SEC_A_X0 + lx * CS * 2, SEC_A_Y0 + ly * CS * 2),
                       LONGERON_SLEEVE_DIA / 2 * CS * 2,
                       dxfattribs={"layer": "SPAR"})

    # =========================================================================
    # SECTION B — X=911 (HStab pivot station)
    # =========================================================================
    msp.add_text("SECTION B — X=911 (HStab Pivot)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 40, SEC_B_Y0 + 55))
    msp.add_text("HT-14/12 blend, 165mm chord", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 25, SEC_B_Y0 + 49))
    msp.add_text("(shown 0.5:1 scale)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 15, SEC_B_Y0 + 45))

    fin_h_b = 145 * CS
    fin_thick_b = 165 * 0.07 * CS  # blended thickness ratio

    pts_b = ellipse_points(SEC_B_X0, SEC_B_Y0 + fin_h_b / 2, fin_thick_b / 2, fin_h_b / 2)
    for i in range(len(pts_b) - 1):
        msp.add_line(pts_b[i], pts_b[i + 1], dxfattribs={"layer": "OUTLINE"})

    # PETG bearing block (at base of fin)
    bear_w = HSTAB_BEARING_W * CS
    bear_h = HSTAB_BEARING_H * CS
    bear_cx = SEC_B_X0
    bear_cy = SEC_B_Y0 - bear_h / 2
    msp.add_line((bear_cx - bear_w / 2, bear_cy - bear_h / 2),
                 (bear_cx + bear_w / 2, bear_cy - bear_h / 2),
                 dxfattribs={"layer": "SPAR"})
    msp.add_line((bear_cx - bear_w / 2, bear_cy + bear_h / 2),
                 (bear_cx + bear_w / 2, bear_cy + bear_h / 2),
                 dxfattribs={"layer": "SPAR"})
    msp.add_line((bear_cx - bear_w / 2, bear_cy - bear_h / 2),
                 (bear_cx - bear_w / 2, bear_cy + bear_h / 2),
                 dxfattribs={"layer": "SPAR"})
    msp.add_line((bear_cx + bear_w / 2, bear_cy - bear_h / 2),
                 (bear_cx + bear_w / 2, bear_cy + bear_h / 2),
                 dxfattribs={"layer": "SPAR"})

    # 2x brass tube bearings
    tube_spacing = BRASS_TUBE_SPACING * CS
    for tx_off in [-tube_spacing / 2, +tube_spacing / 2]:
        msp.add_circle((bear_cx + tx_off, bear_cy),
                       BRASS_TUBE_OD / 2 * CS,
                       dxfattribs={"layer": "SPAR"})
        msp.add_circle((bear_cx + tx_off, bear_cy),
                       BRASS_TUBE_ID / 2 * CS,
                       dxfattribs={"layer": "HIDDEN"})
    msp.add_text("PETG BEARING BLOCK", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (bear_cx + bear_w / 2 + 3, bear_cy + 3))
    msp.add_text("2x BRASS TUBE 4/3mm", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (bear_cx + bear_w / 2 + 3, bear_cy - 1))
    msp.add_text("28mm spacing", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (bear_cx + bear_w / 2 + 3, bear_cy - 5))

    # Centerline
    msp.add_line((SEC_B_X0, SEC_B_Y0 - bear_h - 5),
                 (SEC_B_X0, SEC_B_Y0 + fin_h_b + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Rear spar
    spar_y_b = SEC_B_Y0 + fin_h_b * 0.4  # approximate position at 60% chord height
    msp.add_circle((SEC_B_X0 + 1, spar_y_b),
                   REAR_SPAR_DIA * CS,
                   dxfattribs={"layer": "SPAR"})
    msp.add_text("1.5mm REAR SPAR", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_B_X0 + fin_thick_b / 2 + 3, spar_y_b))

    # =========================================================================
    # SECTION C — X=1000 (near tip)
    # =========================================================================
    CS_C = 0.8
    msp.add_text("SECTION C — X=1000 (Near Tip)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 35, SEC_C_Y0 + 55))
    msp.add_text("HT-12, ~105mm chord, 140mm fin height", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 35, SEC_C_Y0 + 49))
    msp.add_text("(shown 0.8:1 scale)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 15, SEC_C_Y0 + 45))

    fin_h_c = 140 * CS_C
    fin_thick_c = 105 * 0.051 * CS_C  # HT-12 at 5.1% thickness

    pts_c = ellipse_points(SEC_C_X0, SEC_C_Y0 + fin_h_c / 2, fin_thick_c / 2, fin_h_c / 2)
    for i in range(len(pts_c) - 1):
        msp.add_line(pts_c[i], pts_c[i + 1], dxfattribs={"layer": "OUTLINE"})

    msp.add_line((SEC_C_X0, SEC_C_Y0 - 5),
                 (SEC_C_X0, SEC_C_Y0 + fin_h_c + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Hinge line position
    msp.add_line((SEC_C_X0 + fin_thick_c / 4, SEC_C_Y0),
                 (SEC_C_X0 + fin_thick_c / 4, SEC_C_Y0 + fin_h_c),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("HINGE", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_C_X0 + fin_thick_c / 2 + 3, SEC_C_Y0 + fin_h_c / 2))

    # =========================================================================
    # NOTES
    # =========================================================================
    notes = [
        "NOTES:",
        "1. All dims mm. S4b is the fin top section X=880 to X=1046mm.",
        "2. Prints with fin flat on bed. 166mm L x 175mm chord x ~165mm height. Fits bed.",
        "3. Shell: 0.5mm LW-PLA vase mode fin skin. Tip cap integrated closure.",
        "4. VStab airfoil: HT-14 (7.5% t/c) at X=880 blending to HT-12 (5.1%) at tip.",
        "5. HStab bearing mount: PETG block 30x15x15mm at X=911 (HStab pivot station).",
        "6. 2x brass tubes (4mm OD / 3mm ID) pressed into PETG, 28mm spacing.",
        "7. Print PETG bearing with 2.8mm pilot holes, ream to 3.1mm after pressing brass (M5).",
        "8. 5x PETG rudder hinge sleeves (1.2mm OD / 0.6mm ID / 3mm) @ 20mm intervals.",
        "9. Rudder hinge line: 62% chord at root, 65% at tip.",
        "10. 1.5mm CF rear spar continues from S4a at 60% chord.",
        "11. VStab tip cap: printed closure, smooth faired tip.",
        "12. Bottom 2 longerons terminate at HStab bearing block (glued in).",
        "13. Top 2 longerons continue as VStab LE spar, terminate near fin tip.",
        "14. Joint face at X=880: interlocking teeth 1.5mm depth, 3mm pitch (M4).",
    ]
    ny = 120
    for n in notes:
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((25, ny))
        ny -= 5

    # =========================================================================
    # HSTAB BEARING DETAIL TABLE
    # =========================================================================
    msp.add_text("HSTAB BEARING DETAIL:", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((25, 45))
    table = [
        "PETG block: 30mm W x 15mm H x 15mm D (chordwise)",
        "2x brass tubes: 4mm OD / 3mm ID, pressed in with CA",
        "Tube spacing: 28mm center-to-center",
        "Pivot station: X=911mm (fuselage coordinate)",
        "Pilot holes: 2.8mm (undersized), reamed to 3.1mm (M5)",
        "3mm CF rod passes through both tubes (HStab pivot axis)",
    ]
    ty = 39
    for line in table:
        msp.add_text(line, height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((30, ty))
        ty -= 4

    # =========================================================================
    # SAVE
    # =========================================================================
    out_path = "cad/components/fuselage/Fuselage_S4b_Fin_Top/Fuselage_S4b_Fin_Top_drawing.dxf"
    save_dxf_and_png(doc, out_path, dpi=300)
    print("Fuselage_S4b_Fin_Top drawing complete.")


if __name__ == "__main__":
    main()
