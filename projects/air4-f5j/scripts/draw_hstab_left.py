"""
3-View Technical Drawing: HStab_Left Component
===============================================
FROM DESIGN CONSENSUS v2:
  One half of the all-moving H-stab (printed in LW-PLA, vase mode)
  Airfoil blend: HT-14 (root, 7.5%) → HT-13 (tip, 6.5%)
  215mm span, 115mm root chord, 75mm tip chord (60mm at swept tip)
  3mm pivot rod channel at 25% chord
  2mm rear spar channel at 65% chord
  Internal diagonal rib grid (vase-mode slot technique)

This drawing shows the INTERNAL STRUCTURE — spar channels, rib layout,
wall thickness, print features. The assembly drawing shows only the outer form.
"""

import ezdxf
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.dxf_utils import save_dxf_and_png

# === FROM CONSENSUS ===
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
TIP_CHORD = 75.0
TIP_END_CHORD = 60.0
TAPER = TIP_CHORD / ROOT_CHORD
T_ROOT = 0.075  # HT-14
T_TIP = 0.065   # HT-13
PIVOT_FRAC = 0.25
RSPAR_FRAC = 0.65
PIVOT_DIA = 3.0
RSPAR_DIA = 2.0
TE_FRAC = 0.97
WALL = 0.45  # mm, vase mode
SWEEP_START = 0.93  # 200mm


def chord_at(eta):
    return ROOT_CHORD * (1 - eta * (1 - TAPER))


def thickness_ratio_at(eta):
    """Blend from HT-14 (7.5%) at root to HT-13 (6.5%) at tip."""
    return T_ROOT + (T_TIP - T_ROOT) * eta


def ht_yt(xc, chord, t_ratio):
    """Half-thickness for blended airfoil."""
    if xc <= 0:
        return 0.0
    return 5 * t_ratio * (
        0.2969 * xc**0.5 - 0.1260 * xc - 0.3516 * xc**2
        + 0.2843 * xc**3 - 0.1015 * xc**4
    ) * chord


def main():
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()

    ds = doc.dimstyles.new("COMP")
    ds.dxf.dimtxt = 2.5
    ds.dxf.dimasz = 1.5
    ds.dxf.dimlfac = 1.0
    ds.dxf.dimexe = 0.8
    ds.dxf.dimexo = 0.5
    ds.dxf.dimgap = 0.6

    doc.layers.add("OUTLINE", color=7)
    doc.layers.add("STRUCTURE", color=3)
    doc.layers.add("DIMENSION", color=1)
    doc.layers.add("CENTERLINE", color=5)
    doc.layers.add("SPAR", color=6)
    doc.layers.add("HIDDEN", color=8)
    doc.layers.add("TEXT", color=7)
    doc.layers.add("RIB", color=4)

    # =============================================
    # TOP VIEW — Internal structure visible
    # X = chord, Y = span (0=root, 215=tip)
    # =============================================
    ox, oy = 30, 280

    # Outer planform
    n = 30
    le_pts = []
    te_pts = []
    for i in range(n + 1):
        eta = SWEEP_START * i / n
        y = oy - eta * HALF_SPAN
        c = chord_at(eta)
        le_pts.append((ox, y))
        te_pts.append((ox + c * TE_FRAC, y))

    # Swept tip
    tip_y0 = oy - SWEEP_START * HALF_SPAN
    main_c = chord_at(SWEEP_START)
    for i in range(1, 6):
        f = i / 5
        dy = 15 * f
        y = tip_y0 - dy
        le_x = ox + f * (main_c - TIP_END_CHORD) * TE_FRAC * 0.7
        te_x = ox + main_c * TE_FRAC - f * (main_c - TIP_END_CHORD) * 0.3 * TE_FRAC
        le_pts.append((le_x, y))
        te_pts.append((te_x, y))

    for i in range(len(le_pts) - 1):
        msp.add_line(le_pts[i], le_pts[i+1], dxfattribs={"layer": "OUTLINE"})
        msp.add_line(te_pts[i], te_pts[i+1], dxfattribs={"layer": "OUTLINE"})
    # Root line
    msp.add_line(le_pts[0], te_pts[0], dxfattribs={"layer": "OUTLINE"})
    # Tip closure
    msp.add_line(le_pts[-1], te_pts[-1], dxfattribs={"layer": "OUTLINE"})

    # Pivot rod channel at 25% chord
    for i in range(n):
        eta1 = SWEEP_START * i / n
        eta2 = SWEEP_START * (i + 1) / n
        c1 = chord_at(eta1) * PIVOT_FRAC
        c2 = chord_at(eta2) * PIVOT_FRAC
        y1 = oy - eta1 * HALF_SPAN
        y2 = oy - eta2 * HALF_SPAN
        msp.add_line((ox + c1, y1), (ox + c2, y2), dxfattribs={"layer": "SPAR"})

    # Rear spar channel at 65% chord
    for i in range(n):
        eta1 = SWEEP_START * i / n
        eta2 = SWEEP_START * (i + 1) / n
        c1 = chord_at(eta1) * RSPAR_FRAC
        c2 = chord_at(eta2) * RSPAR_FRAC
        y1 = oy - eta1 * HALF_SPAN
        y2 = oy - eta2 * HALF_SPAN
        msp.add_line((ox + c1, y1), (ox + c2, y2), dxfattribs={"layer": "STRUCTURE"})

    # Internal diagonal rib grid (vase-mode slot technique)
    # Forward diagonal set (~55° from spanwise)
    rib_spacing = 40  # mm along span
    for y_start in range(0, int(HALF_SPAN * SWEEP_START), rib_spacing):
        eta_s = y_start / HALF_SPAN
        eta_e = min(eta_s + 0.25, SWEEP_START)
        c_s = chord_at(eta_s)
        c_e = chord_at(eta_e)
        y1 = oy - y_start
        y2 = oy - eta_e * HALF_SPAN
        # Diagonal from LE area to TE area
        msp.add_line((ox + c_s * 0.10, y1), (ox + c_e * 0.55, y2), dxfattribs={"layer": "RIB"})

    # Reverse diagonal set
    for y_start in range(20, int(HALF_SPAN * SWEEP_START), rib_spacing):
        eta_s = y_start / HALF_SPAN
        eta_e = min(eta_s + 0.25, SWEEP_START)
        c_s = chord_at(eta_s)
        c_e = chord_at(eta_e)
        y1 = oy - y_start
        y2 = oy - eta_e * HALF_SPAN
        msp.add_line((ox + c_s * 0.55, y1), (ox + c_e * 0.10, y2), dxfattribs={"layer": "RIB"})

    # Cross ribs at key stations (perpendicular)
    for eta_rib in [0.0, 0.25, 0.50, 0.75, SWEEP_START]:
        c = chord_at(eta_rib)
        y = oy - eta_rib * HALF_SPAN
        msp.add_line((ox + 2, y), (ox + c * TE_FRAC - 2, y), dxfattribs={"layer": "RIB"})

    # Pivot rod circles at root and near-tip
    msp.add_circle((ox + ROOT_CHORD * PIVOT_FRAC, oy), PIVOT_DIA / 2 + 0.5,
                   dxfattribs={"layer": "SPAR"})
    near_tip_y = oy - 0.90 * HALF_SPAN
    near_tip_c = chord_at(0.90)
    msp.add_circle((ox + near_tip_c * PIVOT_FRAC, near_tip_y), PIVOT_DIA / 2 + 0.3,
                   dxfattribs={"layer": "SPAR"})

    # === DIMENSIONS ===
    dim = msp.add_linear_dim(base=(ox - 15, oy), p1=(ox, oy), p2=(ox, oy - HALF_SPAN),
                              angle=90, dimstyle="COMP")
    dim.render()

    dim = msp.add_linear_dim(base=(ox, oy + 10), p1=(ox, oy), p2=(ox + ROOT_CHORD * TE_FRAC, oy),
                              dimstyle="COMP")
    dim.render()

    tip_y = oy - SWEEP_START * HALF_SPAN
    dim = msp.add_linear_dim(base=(ox, tip_y - 10),
                              p1=(le_pts[-3][0], le_pts[-3][1]),
                              p2=(te_pts[-3][0], te_pts[-3][1]),
                              dimstyle="COMP")
    dim.render()

    # Labels
    msp.add_text("TOP VIEW — INTERNAL STRUCTURE", height=4,
                 dxfattribs={"layer": "TEXT"}).set_placement((ox, oy + 20))
    msp.add_text(f"PIVOT CHANNEL\n({PIVOT_DIA}mm CF)", height=2,
                 dxfattribs={"layer": "SPAR"}).set_placement(
        (ox + ROOT_CHORD * PIVOT_FRAC + 3, oy - 15))
    msp.add_text(f"REAR SPAR\nCHANNEL\n({RSPAR_DIA}mm CF)", height=1.8,
                 dxfattribs={"layer": "STRUCTURE"}).set_placement(
        (ox + ROOT_CHORD * RSPAR_FRAC + 3, oy - 40))
    msp.add_text("DIAGONAL\nRIB GRID\n(vase-mode\nslot technique)", height=1.8,
                 dxfattribs={"layer": "RIB"}).set_placement(
        (ox + ROOT_CHORD * 0.35, oy - HALF_SPAN * 0.4))
    msp.add_text("ROOT", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((ox + 40, oy + 4))
    msp.add_text("TIP", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + 20, oy - HALF_SPAN - 5))
    msp.add_text("CROSS RIBS\nat 0, 25, 50,\n75, 93% span", height=1.5,
                 dxfattribs={"layer": "RIB"}).set_placement(
        (ox + ROOT_CHORD * TE_FRAC + 5, oy - HALF_SPAN * 0.5))

    # =============================================
    # FRONT VIEW — Root cross-section with internals
    # =============================================
    fx, fy = 30, 15

    # Outer airfoil (HT-14 at root)
    n_af = 50
    for i in range(n_af):
        xc1 = TE_FRAC * i / n_af
        xc2 = TE_FRAC * (i + 1) / n_af
        for sign in [1, -1]:
            msp.add_line(
                (fx + xc1 * ROOT_CHORD, fy + sign * ht_yt(xc1, ROOT_CHORD, T_ROOT)),
                (fx + xc2 * ROOT_CHORD, fy + sign * ht_yt(xc2, ROOT_CHORD, T_ROOT)),
                dxfattribs={"layer": "OUTLINE"}
            )

    # LE and TE closures
    yt0 = ht_yt(0.005, ROOT_CHORD, T_ROOT)
    msp.add_line((fx, fy + yt0), (fx, fy - yt0), dxfattribs={"layer": "OUTLINE"})
    yt_te = ht_yt(TE_FRAC, ROOT_CHORD, T_ROOT)
    msp.add_line((fx + TE_FRAC * ROOT_CHORD, fy - yt_te),
                 (fx + TE_FRAC * ROOT_CHORD, fy + yt_te), dxfattribs={"layer": "OUTLINE"})

    # Inner wall (0.45mm offset — simplified as slightly smaller airfoil)
    wall_scale = 1 - 2 * WALL / (T_ROOT * ROOT_CHORD)
    for i in range(n_af):
        xc1 = TE_FRAC * i / n_af
        xc2 = TE_FRAC * (i + 1) / n_af
        if xc1 < 0.03 or xc1 > 0.94:
            continue
        for sign in [1, -1]:
            y1 = sign * ht_yt(xc1, ROOT_CHORD, T_ROOT) * wall_scale
            y2 = sign * ht_yt(xc2, ROOT_CHORD, T_ROOT) * wall_scale
            msp.add_line((fx + xc1 * ROOT_CHORD, fy + y1),
                         (fx + xc2 * ROOT_CHORD, fy + y2),
                         dxfattribs={"layer": "HIDDEN"})

    # Spar circles
    px = fx + ROOT_CHORD * PIVOT_FRAC
    msp.add_circle((px, fy), PIVOT_DIA / 2, dxfattribs={"layer": "SPAR"})
    # Spar tube (printed channel around rod)
    msp.add_circle((px, fy), PIVOT_DIA / 2 + 0.5, dxfattribs={"layer": "SPAR"})

    rx = fx + ROOT_CHORD * RSPAR_FRAC
    msp.add_circle((rx, fy), RSPAR_DIA / 2, dxfattribs={"layer": "STRUCTURE"})
    msp.add_circle((rx, fy), RSPAR_DIA / 2 + 0.4, dxfattribs={"layer": "STRUCTURE"})

    # Internal rib webs (vertical lines at cross-rib positions)
    for xc_rib in [0.15, 0.40, 0.55, 0.80]:
        yt = ht_yt(xc_rib, ROOT_CHORD, T_ROOT) * wall_scale
        msp.add_line((fx + xc_rib * ROOT_CHORD, fy - yt),
                     (fx + xc_rib * ROOT_CHORD, fy + yt),
                     dxfattribs={"layer": "RIB"})

    # Dimensions
    yt_max = ht_yt(0.30, ROOT_CHORD, T_ROOT)
    dim = msp.add_linear_dim(base=(fx + 0.30 * ROOT_CHORD - 10, fy),
                              p1=(fx + 0.30 * ROOT_CHORD, fy - yt_max),
                              p2=(fx + 0.30 * ROOT_CHORD, fy + yt_max),
                              angle=90, dimstyle="COMP", override={"dimtxt": 2})
    dim.render()

    dim = msp.add_linear_dim(base=(fx, fy - 10), p1=(fx, fy), p2=(fx + ROOT_CHORD * TE_FRAC, fy),
                              dimstyle="COMP")
    dim.render()

    # Wall thickness callout
    msp.add_text(f"{WALL}mm wall\n(vase mode)", height=1.5,
                 dxfattribs={"layer": "HIDDEN"}).set_placement(
        (fx + ROOT_CHORD * 0.42, fy + yt_max * 0.7))

    msp.add_text("ROOT SECTION — HT-14 (7.5%)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((fx, fy - 20))
    msp.add_text(f"Pivot: {PIVOT_DIA}mm CF\n+ 0.5mm tube", height=1.5,
                 dxfattribs={"layer": "SPAR"}).set_placement((px + 4, fy + 2))
    msp.add_text(f"Rear: {RSPAR_DIA}mm CF", height=1.5,
                 dxfattribs={"layer": "STRUCTURE"}).set_placement((rx + 3, fy + 2))

    # =============================================
    # TIP SECTION
    # =============================================
    sx = fx + ROOT_CHORD * TE_FRAC + 35
    sy = fy

    for i in range(n_af):
        xc1 = TE_FRAC * i / n_af
        xc2 = TE_FRAC * (i + 1) / n_af
        for sign in [1, -1]:
            msp.add_line(
                (sx + xc1 * TIP_CHORD, sy + sign * ht_yt(xc1, TIP_CHORD, T_TIP)),
                (sx + xc2 * TIP_CHORD, sy + sign * ht_yt(xc2, TIP_CHORD, T_TIP)),
                dxfattribs={"layer": "OUTLINE"}
            )

    yt0_t = ht_yt(0.005, TIP_CHORD, T_TIP)
    msp.add_line((sx, sy + yt0_t), (sx, sy - yt0_t), dxfattribs={"layer": "OUTLINE"})
    yt_te_t = ht_yt(TE_FRAC, TIP_CHORD, T_TIP)
    msp.add_line((sx + TE_FRAC * TIP_CHORD, sy - yt_te_t),
                 (sx + TE_FRAC * TIP_CHORD, sy + yt_te_t), dxfattribs={"layer": "OUTLINE"})

    # Spar circles at tip
    msp.add_circle((sx + TIP_CHORD * PIVOT_FRAC, sy), PIVOT_DIA / 2, dxfattribs={"layer": "SPAR"})
    msp.add_circle((sx + TIP_CHORD * RSPAR_FRAC, sy), RSPAR_DIA / 2, dxfattribs={"layer": "STRUCTURE"})

    dim = msp.add_linear_dim(base=(sx, sy - 10), p1=(sx, sy), p2=(sx + TIP_CHORD * TE_FRAC, sy),
                              dimstyle="COMP")
    dim.render()

    msp.add_text("TIP SECTION — HT-13 (6.5%)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((sx, sy - 20))

    # =============================================
    # TITLE BLOCK
    # =============================================
    tbx, tby = 0, -30
    w, h = 260, 25
    msp.add_line((tbx, tby), (tbx + w, tby), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((tbx, tby - h), (tbx + w, tby - h), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((tbx, tby), (tbx, tby - h), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((tbx + w, tby), (tbx + w, tby - h), dxfattribs={"layer": "OUTLINE"})

    msp.add_text("AEROFORGE — HStab_Left (PRINTED COMPONENT)", height=4,
                 dxfattribs={"layer": "TEXT"}).set_placement((tbx + 5, tby - 6))
    msp.add_text(
        f"Blend: HT-14 root → HT-13 tip | Span: {HALF_SPAN}mm | "
        f"Root: {ROOT_CHORD}mm | Tip: {TIP_CHORD}mm | Wall: {WALL}mm vase mode",
        height=2, dxfattribs={"layer": "TEXT"}
    ).set_placement((tbx + 5, tby - 12))
    msp.add_text(
        f"LW-PLA 230°C | Pivot: {PIVOT_DIA}mm channel | Rear spar: {RSPAR_DIA}mm channel | "
        f"Mass target: 10-12g | Status: FOR APPROVAL",
        height=2, dxfattribs={"layer": "TEXT"}
    ).set_placement((tbx + 5, tby - 18))

    out = "cad/components/empennage/HStab_Left/HStab_Left_drawing.dxf"
    save_dxf_and_png(doc, out)
    print(f"\nHStab_Left component drawing generated")
    print(f"  Shows: internal diagonal rib grid, spar channels, wall thickness, airfoil blend")


if __name__ == "__main__":
    main()
