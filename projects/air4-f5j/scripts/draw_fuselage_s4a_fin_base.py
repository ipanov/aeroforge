"""
Fuselage_S4a_Fin_Base Component Drawing
==========================================
Section S4a (X=660 to X=880mm) of the integrated fuselage.
VStab fin grows from fuselage body. Superelliptical blend from
13mm circle to HT-14 airfoil. Rudder hinge pockets.

Views:
  - SIDE VIEW (profile): shows fin growth from body
  - TOP VIEW (planform): shows fin chord growth
  - SECTION A at X=660 (entry, 13mm circle)
  - SECTION B at X=770 (mid-blend, partial fin)
  - SECTION C at X=880 (S4a/S4b joint, full fin root)

Dimensions from DESIGN_CONSENSUS.md v2.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# ============================================================================
# S4a FIN BASE GEOMETRY DATA
# ============================================================================

# This section is complex: the body tube shrinks while a fin grows upward.
# At X=660: 13mm circle (body only, no fin)
# At X=880: body merges into fin root. HT-14 airfoil, 180mm chord approx.
#           Fin height at X=880 ~140mm

# Body tube cross-sections (shrinking as fin grows)
BODY_XSECTIONS = [
    (660, 13, 13),      # circular body
    (700, 12, 12),      # body shrinking
    (750, 10, 10),      # body merging into fin
    (800, 9, 9),        # body nearly gone
    (850, 8.5, 8.5),    # very small body remnant
    (880, 8.5, 8.5),    # body at fin root
]

# Fin height growth (measured from body top to fin tip)
FIN_HEIGHTS = [
    (660, 0),       # no fin yet
    (700, 20),      # fin beginning
    (750, 60),      # fin growing
    (800, 100),     # fin substantial
    (850, 130),     # fin nearly full
    (880, 140),     # fin at S4a/S4b joint
]

# Fin chord at each station (LE to TE)
FIN_CHORDS = [
    (660, 0),
    (700, 30),      # nascent fin
    (750, 80),      # growing
    (800, 130),     # large
    (850, 160),     # near-full
    (880, 175),     # approaching root chord (180mm at X=866)
]

LONGERONS = {
    660: [(+4, +4), (-4, +4), (+4, -4), (-4, -4)],     # 8x8, all in body
    750: [(+3, +4), (-3, +4), (+3, -3), (-3, -3)],     # top pair starting to rise
    880: [(+2, +3), (-2, +3), (+2, -3), (-2, -3)],     # 4x6, top pair in fin LE
}

S4A_LENGTH = 220.0
X_OFFSET = 660
SHELL_WALL = 0.6
LONGERON_DIA = 2.0
LONGERON_SLEEVE_DIA = 2.5
REAR_SPAR_DIA = 1.5       # 1.5mm CF rear spar
REAR_SPAR_SLEEVE = 2.0    # printed sleeve
RUDDER_HINGE_CHORD = 0.62  # 62% chord from LE
PETG_SLEEVE_OD = 1.2
PETG_SLEEVE_ID = 0.6
HINGE_INTERVAL = 20.0     # mm between sleeves
PUSHROD_OD = 3.0


def interp_list(x, data):
    """Interpolate from a list of (x, value) tuples."""
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
        title="Fuselage_S4a_Fin_Base",
        subtitle="Fin base section X=660-880mm. VStab grows from body. Superelliptical blend to HT-14.",
        material="LW-PLA 0.6mm shell | Print: fin flat on bed, body tube vertical",
        mass="~12g (shell+structure, excl. longerons)",
        scale="1:2",
        sheet_size="A1",
        status="FOR APPROVAL",
        revision="v1",
        orientation_labels={"fwd": "FWD", "inbd": "NOSE"},
    )
    msp = doc.modelspace()

    # Scale 1:2 for this section (220mm long, fin up to 140mm tall)
    SC = 0.5  # half scale for profile views (they're big)

    SIDE_X0 = 40.0
    SIDE_Y0 = 380.0
    TOP_X0 = 40.0
    TOP_Y0 = 250.0
    SEC_A_X0 = 380.0
    SEC_A_Y0 = 500.0
    SEC_B_X0 = 530.0
    SEC_B_Y0 = 500.0
    SEC_C_X0 = 680.0
    SEC_C_Y0 = 500.0

    # =========================================================================
    # SIDE VIEW — shows fin growing from body
    # =========================================================================
    msp.add_text("SIDE VIEW — PROFILE (1:2)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0, SIDE_Y0 + 95))

    # Body bottom profile
    for i in range(len(BODY_XSECTIONS) - 1):
        x0, w0, h0 = BODY_XSECTIONS[i]
        x1, w1, h1 = BODY_XSECTIONS[i + 1]
        msp.add_line(
            (SIDE_X0 + (x0 - X_OFFSET), SIDE_Y0 - h0 / 2),
            (SIDE_X0 + (x1 - X_OFFSET), SIDE_Y0 - h1 / 2),
            dxfattribs={"layer": "OUTLINE"}
        )

    # Body top profile (where fin meets body)
    for i in range(len(BODY_XSECTIONS) - 1):
        x0, w0, h0 = BODY_XSECTIONS[i]
        x1, w1, h1 = BODY_XSECTIONS[i + 1]
        msp.add_line(
            (SIDE_X0 + (x0 - X_OFFSET), SIDE_Y0 + h0 / 2),
            (SIDE_X0 + (x1 - X_OFFSET), SIDE_Y0 + h1 / 2),
            dxfattribs={"layer": "OUTLINE"}
        )

    # Fin top edge (LE to tip)
    for i in range(len(FIN_HEIGHTS) - 1):
        x0, fh0 = FIN_HEIGHTS[i]
        x1, fh1 = FIN_HEIGHTS[i + 1]
        bh0 = interp_list(x0, [(x, h) for x, w, h in BODY_XSECTIONS]) / 2
        bh1 = interp_list(x1, [(x, h) for x, w, h in BODY_XSECTIONS]) / 2
        msp.add_line(
            (SIDE_X0 + (x0 - X_OFFSET), SIDE_Y0 + bh0 + fh0),
            (SIDE_X0 + (x1 - X_OFFSET), SIDE_Y0 + bh1 + fh1),
            dxfattribs={"layer": "OUTLINE"}
        )

    # Centerline (body axis)
    msp.add_line((SIDE_X0 - 5, SIDE_Y0), (SIDE_X0 + 230, SIDE_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Rudder hinge line (62% chord, shown dashed)
    # The hinge runs vertically on the fin
    for i in range(len(FIN_HEIGHTS) - 1):
        x0, fh0 = FIN_HEIGHTS[i]
        x1, fh1 = FIN_HEIGHTS[i + 1]
        if fh0 > 0 and fh1 > 0:
            bh0 = interp_list(x0, [(x, h) for x, w, h in BODY_XSECTIONS]) / 2
            bh1 = interp_list(x1, [(x, h) for x, w, h in BODY_XSECTIONS]) / 2
            # Hinge at 62% of fin height
            msp.add_line(
                (SIDE_X0 + (x0 - X_OFFSET), SIDE_Y0 + bh0 + fh0 * 0.62),
                (SIDE_X0 + (x1 - X_OFFSET), SIDE_Y0 + bh1 + fh1 * 0.62),
                dxfattribs={"layer": "HIDDEN"}
            )

    # Longeron sweep annotation
    msp.add_text("TOP 2 LONGERONS SWEEP UP INTO FIN LE", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 30, SIDE_Y0 + 50))

    # PETG hinge sleeve positions (5x at 20mm intervals, starting ~Z=10mm)
    msp.add_text("5x PETG HINGE SLEEVES @ 20mm intervals", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 140, SIDE_Y0 + 70))

    # Pushrod channels
    msp.add_text("2x PUSHROD CHANNELS", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SIDE_X0 + 10, SIDE_Y0 - 12))

    # Station labels
    for xst, label in [(660, "X=660"), (770, "X=770"), (880, "X=880")]:
        rel_x = xst - X_OFFSET
        bh = interp_list(xst, [(x, h) for x, w, h in BODY_XSECTIONS]) / 2
        fh = interp_list(xst, FIN_HEIGHTS)
        top = bh + fh if fh > 0 else bh
        msp.add_line((SIDE_X0 + rel_x, SIDE_Y0 + top + 2),
                     (SIDE_X0 + rel_x, SIDE_Y0 + top + 8),
                     dxfattribs={"layer": "DIMENSION"})
        msp.add_text(label, height=1.8,
                     dxfattribs={"layer": "DIMENSION"}).set_placement(
            (SIDE_X0 + rel_x - 6, SIDE_Y0 + top + 9))

    # Overall length dimension
    msp.add_linear_dim(
        base=(SIDE_X0 + 110, SIDE_Y0 - 18),
        p1=(SIDE_X0, SIDE_Y0 - 14),
        p2=(SIDE_X0 + 220, SIDE_Y0 - 14),
        dimstyle="AEROFORGE",
    ).render()

    # Fin height at X=880
    bh_880 = interp_list(880, [(x, h) for x, w, h in BODY_XSECTIONS]) / 2
    fh_880 = interp_list(880, FIN_HEIGHTS)
    msp.add_linear_dim(
        base=(SIDE_X0 + 230, SIDE_Y0 + bh_880 + fh_880 / 2),
        p1=(SIDE_X0 + 225, SIDE_Y0),
        p2=(SIDE_X0 + 225, SIDE_Y0 + bh_880 + fh_880),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()

    # =========================================================================
    # TOP VIEW — shows fin chord growth (planform)
    # =========================================================================
    msp.add_text("TOP VIEW — PLANFORM (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0, TOP_Y0 + 50))

    # Body width profile (symmetric about centerline)
    for i in range(len(BODY_XSECTIONS) - 1):
        x0, w0, h0 = BODY_XSECTIONS[i]
        x1, w1, h1 = BODY_XSECTIONS[i + 1]
        msp.add_line(
            (TOP_X0 + (x0 - X_OFFSET), TOP_Y0 + w0 / 2),
            (TOP_X0 + (x1 - X_OFFSET), TOP_Y0 + w1 / 2),
            dxfattribs={"layer": "OUTLINE"}
        )
        msp.add_line(
            (TOP_X0 + (x0 - X_OFFSET), TOP_Y0 - w0 / 2),
            (TOP_X0 + (x1 - X_OFFSET), TOP_Y0 - w1 / 2),
            dxfattribs={"layer": "OUTLINE"}
        )

    # Centerline
    msp.add_line((TOP_X0 - 5, TOP_Y0), (TOP_X0 + 230, TOP_Y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Fin chord shown as dashed (above body in top view = along body axis)
    # In top view the fin appears as a projection above the body
    # Show fin LE and TE lines
    for i in range(len(FIN_CHORDS) - 1):
        x0, c0 = FIN_CHORDS[i]
        x1, c1 = FIN_CHORDS[i + 1]
        if c0 > 0 or c1 > 0:
            # Fin LE (forward)
            msp.add_line(
                (TOP_X0 + (x0 - X_OFFSET), TOP_Y0 + 10 + c0 * 0.02),
                (TOP_X0 + (x1 - X_OFFSET), TOP_Y0 + 10 + c1 * 0.02),
                dxfattribs={"layer": "HIDDEN"}
            )
    msp.add_text("FIN CHORD GROWTH", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0 + 60, TOP_Y0 + 16))

    # Rear spar at 60% chord (dashed)
    msp.add_text("1.5mm CF REAR SPAR @ 60% CHORD", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((TOP_X0 + 100, TOP_Y0 - 10))

    # Section cut lines
    for xcut, label in [(660, "A"), (770, "B"), (880, "C")]:
        rel_x = xcut - X_OFFSET
        hw = 15
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
    # SECTION A — X=660 (entry, 13mm circle)
    # =========================================================================
    CS = 2.5  # cross-section scale for visibility
    msp.add_text("SECTION A — X=660 (Pre-Fin Entry)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 40, SEC_A_Y0 + 30))
    msp.add_text("13mm dia circle (body only)", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 20, SEC_A_Y0 + 24))
    msp.add_text("(shown 2.5:1 scale)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_A_X0 - 15, SEC_A_Y0 + 20))

    r660 = 6.5 * CS
    pts_a = ellipse_points(SEC_A_X0, SEC_A_Y0, r660, r660)
    for i in range(len(pts_a) - 1):
        msp.add_line(pts_a[i], pts_a[i + 1], dxfattribs={"layer": "OUTLINE"})

    ri = (6.5 - SHELL_WALL) * CS
    pts_ai = ellipse_points(SEC_A_X0, SEC_A_Y0, ri, ri)
    for i in range(len(pts_ai) - 1):
        msp.add_line(pts_ai[i], pts_ai[i + 1], dxfattribs={"layer": "WALL"})

    # Centerlines
    msp.add_line((SEC_A_X0 - r660 - 5, SEC_A_Y0),
                 (SEC_A_X0 + r660 + 5, SEC_A_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_A_X0, SEC_A_Y0 - r660 - 5),
                 (SEC_A_X0, SEC_A_Y0 + r660 + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Longerons
    for lx, ly in LONGERONS[660]:
        msp.add_circle((SEC_A_X0 + lx * CS, SEC_A_Y0 + ly * CS),
                       LONGERON_SLEEVE_DIA / 2 * CS,
                       dxfattribs={"layer": "SPAR"})

    # Pushrod channels
    msp.add_circle((SEC_A_X0 - 1.5 * CS, SEC_A_Y0 - 2.5 * CS), PUSHROD_OD / 2 * CS,
                   dxfattribs={"layer": "HIDDEN"})
    msp.add_circle((SEC_A_X0 + 1.5 * CS, SEC_A_Y0 - 2.5 * CS), PUSHROD_OD / 2 * CS,
                   dxfattribs={"layer": "HIDDEN"})

    # =========================================================================
    # SECTION B — X=770 (mid-blend)
    # =========================================================================
    CS_B = 1.5  # less zoom needed, fin is bigger
    msp.add_text("SECTION B — X=770 (Mid-Blend)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 40, SEC_B_Y0 + 65))
    msp.add_text("Superelliptical body + ~75mm fin", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 25, SEC_B_Y0 + 59))
    msp.add_text("(shown 1.5:1 scale)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_B_X0 - 15, SEC_B_Y0 + 55))

    # Body circle at X=770: ~10.5mm dia
    body_r = 5.25 * CS_B
    pts_b_body = ellipse_points(SEC_B_X0, SEC_B_Y0, body_r, body_r)
    for i in range(len(pts_b_body) - 1):
        msp.add_line(pts_b_body[i], pts_b_body[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Fin outline above body (simplified as narrow ellipse)
    fin_h_770 = 75 * CS_B  # fin height
    fin_thick = 5 * CS_B   # fin thickness at this station (thin)
    fin_cx = SEC_B_X0
    fin_cy = SEC_B_Y0 + body_r + fin_h_770 / 2
    pts_fin = ellipse_points(fin_cx, fin_cy, fin_thick / 2, fin_h_770 / 2)
    for i in range(len(pts_fin) - 1):
        msp.add_line(pts_fin[i], pts_fin[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Blend zone (connecting body top to fin base)
    msp.add_line((SEC_B_X0 - fin_thick / 2, SEC_B_Y0 + body_r),
                 (SEC_B_X0 - fin_thick / 2, fin_cy - fin_h_770 / 2),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_line((SEC_B_X0 + fin_thick / 2, SEC_B_Y0 + body_r),
                 (SEC_B_X0 + fin_thick / 2, fin_cy - fin_h_770 / 2),
                 dxfattribs={"layer": "OUTLINE"})

    # Centerlines
    msp.add_line((SEC_B_X0 - body_r - 5, SEC_B_Y0),
                 (SEC_B_X0 + body_r + 5, SEC_B_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_B_X0, SEC_B_Y0 - body_r - 5),
                 (SEC_B_X0, SEC_B_Y0 + body_r + fin_h_770 + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # Rudder hinge line position annotation
    msp.add_text("RUDDER HINGE @ 62% CHORD", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_B_X0 + fin_thick / 2 + 3, fin_cy))

    # =========================================================================
    # SECTION C — X=880 (full fin root section)
    # =========================================================================
    CS_C = 0.6  # scale down (fin is 140mm tall + body)
    msp.add_text("SECTION C — X=880 (S4a/S4b Joint)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 45, SEC_C_Y0 + 70))
    msp.add_text("HT-14 airfoil, ~170mm chord, 140mm fin height", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 35, SEC_C_Y0 + 64))
    msp.add_text("(shown 0.6:1 scale)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((SEC_C_X0 - 15, SEC_C_Y0 + 60))

    # Body circle (8.5mm dia)
    body_r_c = 4.25 * CS_C
    pts_c_body = ellipse_points(SEC_C_X0, SEC_C_Y0, body_r_c * 2, body_r_c)
    for i in range(len(pts_c_body) - 1):
        msp.add_line(pts_c_body[i], pts_c_body[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Fin (HT-14 airfoil shape, simplified as elongated ellipse)
    fin_h_880 = 140 * CS_C
    fin_chord_880 = 170 * CS_C
    fin_thick_880 = 170 * 0.075 * CS_C  # HT-14 max thickness 7.5%
    fin_cx_c = SEC_C_X0
    fin_cy_c = SEC_C_Y0 + body_r_c + fin_h_880 / 2
    pts_fin_c = ellipse_points(fin_cx_c, fin_cy_c, fin_thick_880 / 2, fin_h_880 / 2)
    for i in range(len(pts_fin_c) - 1):
        msp.add_line(pts_fin_c[i], pts_fin_c[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Blend connection
    msp.add_line((SEC_C_X0 - fin_thick_880 / 2, SEC_C_Y0 + body_r_c),
                 (SEC_C_X0 - fin_thick_880 / 2, fin_cy_c - fin_h_880 / 2),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_line((SEC_C_X0 + fin_thick_880 / 2, SEC_C_Y0 + body_r_c),
                 (SEC_C_X0 + fin_thick_880 / 2, fin_cy_c - fin_h_880 / 2),
                 dxfattribs={"layer": "OUTLINE"})

    # Rudder hinge line at 62% chord (dashed)
    hinge_y = 0.62 * fin_thick_880 / 2  # approximate offset
    msp.add_line((SEC_C_X0 + hinge_y, fin_cy_c - fin_h_880 / 2),
                 (SEC_C_X0 + hinge_y, fin_cy_c + fin_h_880 / 2),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("HINGE", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_C_X0 + hinge_y + 2, fin_cy_c + fin_h_880 / 2 - 5))

    # Rear spar at 60% chord
    spar_y = 0.60 * fin_thick_880 / 2
    msp.add_circle((SEC_C_X0 + spar_y - 1, fin_cy_c),
                   REAR_SPAR_DIA / 2 * CS_C * 3,  # visible at this scale
                   dxfattribs={"layer": "SPAR"})
    msp.add_text("1.5mm REAR SPAR", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_C_X0 + fin_thick_880 / 2 + 3, fin_cy_c - 3))

    # Centerlines
    msp.add_line((SEC_C_X0 - body_r_c * 2 - 5, SEC_C_Y0),
                 (SEC_C_X0 + body_r_c * 2 + 5, SEC_C_Y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((SEC_C_X0, SEC_C_Y0 - body_r_c - 5),
                 (SEC_C_X0, fin_cy_c + fin_h_880 / 2 + 5),
                 dxfattribs={"layer": "CENTERLINE"})

    # PETG sleeve positions
    msp.add_text("5x PETG SLEEVES", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_C_X0 + fin_thick_880 / 2 + 3, fin_cy_c + 10))
    msp.add_text("1.2mm OD / 0.6mm ID", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (SEC_C_X0 + fin_thick_880 / 2 + 3, fin_cy_c + 6))

    # =========================================================================
    # NOTES
    # =========================================================================
    notes = [
        "NOTES:",
        "1. All dims mm. S4a is the fin base section X=660 to X=880mm.",
        "2. Prints with fin flat on bed, body tube vertical. 220mm L x 175mm chord x 140mm fin H.",
        "3. Shell: 0.6mm LW-PLA. Fin skin: 0.5mm LW-PLA (vase mode).",
        "4. VStab fin grows from fuselage body via superelliptical blend (X=660-880).",
        "5. Body: 13mm circle at X=660 shrinks to 8.5mm at X=880 as fin envelops it.",
        "6. Top 2 longerons sweep upward into VStab LE spar channel over 220mm span.",
        "7. Bottom 2 longerons continue straight to S4b (carry to HStab bearing mount).",
        "8. 1.5mm CF rear spar channel at 60% chord of fin (HT-14 airfoil).",
        "9. 5x PETG rudder hinge sleeves (1.2mm OD / 0.6mm ID / 3mm long) at 20mm intervals.",
        "10. Rudder hinge line at 62% chord from LE (per consensus v2).",
        "11. 2x pushrod channels continue from S3 through body/fin base.",
        "12. Joint faces: interlocking teeth at X=660 and X=880, 1.5mm depth, 3mm pitch.",
        "13. Longeron spacing transitions from 8x8mm (X=660) to 4x6mm (X=880).",
    ]
    ny = 140
    for n in notes:
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((25, ny))
        ny -= 5

    # =========================================================================
    # FIN GROWTH TABLE
    # =========================================================================
    msp.add_text("FIN GROWTH SCHEDULE:", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((25, 68))
    table = [
        "Station    Body Dia    Fin Height    Fin Chord    Shape",
        "X=660      13mm        0mm           0mm          Circle (body only)",
        "X=700      12mm        20mm          30mm         Superelliptical blend",
        "X=750      10mm        60mm          80mm         Blend continues",
        "X=800      9mm         100mm         130mm        Fin dominant",
        "X=850      8.5mm       130mm         160mm        Near-full fin",
        "X=880      8.5mm       140mm         175mm        HT-14 root (S4a/S4b joint)",
    ]
    ty = 62
    for line in table:
        msp.add_text(line, height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((30, ty))
        ty -= 4

    # =========================================================================
    # SAVE
    # =========================================================================
    out_path = "cad/components/fuselage/Fuselage_S4a_Fin_Base/Fuselage_S4a_Fin_Base_drawing.dxf"
    save_dxf_and_png(doc, out_path, dpi=300)
    print("Fuselage_S4a_Fin_Base drawing complete.")


if __name__ == "__main__":
    main()
