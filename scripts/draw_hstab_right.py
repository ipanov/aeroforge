"""
3-View Technical Drawing: HStab_Right Component
================================================
Mirror of HStab_Left. Identical geometry reflected across the Y=0 plane.

FROM DESIGN CONSENSUS v2:
  One half of the all-moving H-stab (printed in LW-PLA, vase mode)
  Airfoil blend: HT-14 (root, 7.5%) -> HT-13 (tip, 6.5%)
  215mm span, 115mm root chord, 75mm tip chord (60mm at swept tip)
  3mm pivot rod channel at 25% chord
  2mm rear spar channel at 65% chord
  Internal diagonal rib grid (vase-mode slot technique)

The drawing is structurally identical to HStab_Left — same planform,
same internal structure — just labeled as the right half.
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
    # X = chord, Y = span (0=root, -215=tip for RIGHT half)
    # =============================================
    ox, oy = 30, 280

    n = 30
    le_pts = []
    te_pts = []
    for i in range(n + 1):
        eta = SWEEP_START * i / n
        y = oy + eta * HALF_SPAN  # +Y for right half (mirrored)
        c = chord_at(eta)
        le_pts.append((ox, y))
        te_pts.append((ox + c * TE_FRAC, y))

    # Swept tip
    tip_y0 = oy + SWEEP_START * HALF_SPAN
    tip_y1 = oy + HALF_SPAN
    tip_le_x = ox + (ROOT_CHORD - TIP_END_CHORD) * 0.6
    le_pts.append((tip_le_x, tip_y1))
    te_pts.append((tip_le_x + TIP_END_CHORD * TE_FRAC, tip_y1))

    # Draw outlines
    for i in range(len(le_pts) - 1):
        msp.add_line(le_pts[i], le_pts[i + 1], dxfattribs={"layer": "OUTLINE"})
        msp.add_line(te_pts[i], te_pts[i + 1], dxfattribs={"layer": "OUTLINE"})
    msp.add_line(le_pts[0], te_pts[0], dxfattribs={"layer": "OUTLINE"})
    msp.add_line(le_pts[-1], te_pts[-1], dxfattribs={"layer": "OUTLINE"})

    # Spar lines
    for eta_s in [0.0, 0.25, 0.5, 0.75, SWEEP_START]:
        y = oy + eta_s * HALF_SPAN
        c = chord_at(eta_s)
        px = ox + c * PIVOT_FRAC
        rx = ox + c * RSPAR_FRAC
        msp.add_circle((px, y), PIVOT_DIA / 2, dxfattribs={"layer": "SPAR"})
        msp.add_circle((rx, y), RSPAR_DIA / 2, dxfattribs={"layer": "SPAR"})

    # Pivot and rear spar centerlines
    msp.add_line(
        (ox + ROOT_CHORD * PIVOT_FRAC, oy),
        (ox + chord_at(SWEEP_START) * PIVOT_FRAC, tip_y0),
        dxfattribs={"layer": "CENTERLINE"},
    )
    msp.add_line(
        (ox + ROOT_CHORD * RSPAR_FRAC, oy),
        (ox + chord_at(SWEEP_START) * RSPAR_FRAC, tip_y0),
        dxfattribs={"layer": "CENTERLINE"},
    )

    # Diagonal rib grid
    rib_spacing = 25
    n_ribs = int(HALF_SPAN * SWEEP_START / rib_spacing)
    for i in range(n_ribs + 1):
        y = oy + i * rib_spacing
        eta = min(i * rib_spacing / HALF_SPAN, SWEEP_START)
        c = chord_at(eta)
        msp.add_line(
            (ox + WALL, y), (ox + c * TE_FRAC - WALL, y),
            dxfattribs={"layer": "RIB"},
        )

    # =============================================
    # FRONT VIEW — Root cross-section (HT-14)
    # =============================================
    fx, fy = 30, 70
    c = ROOT_CHORD
    t = T_ROOT

    pts_upper = []
    pts_lower = []
    for i in range(51):
        xc = i / 50.0 * TE_FRAC
        yt = ht_yt(xc, c, t)
        pts_upper.append((fx + xc * c, fy + yt))
        pts_lower.append((fx + xc * c, fy - yt))

    for i in range(len(pts_upper) - 1):
        msp.add_line(pts_upper[i], pts_upper[i + 1], dxfattribs={"layer": "OUTLINE"})
        msp.add_line(pts_lower[i], pts_lower[i + 1], dxfattribs={"layer": "OUTLINE"})
    msp.add_line(pts_upper[-1], pts_lower[-1], dxfattribs={"layer": "OUTLINE"})

    # Inner wall (offset by WALL)
    for i in range(51):
        xc = i / 50.0 * TE_FRAC
        yt = ht_yt(xc, c, t)
        inner_yt = max(yt - WALL, 0)
        if i > 0:
            msp.add_line(
                (fx + (i - 1) / 50.0 * TE_FRAC * c, fy + max(ht_yt((i - 1) / 50.0 * TE_FRAC, c, t) - WALL, 0)),
                (fx + xc * c, fy + inner_yt),
                dxfattribs={"layer": "STRUCTURE"},
            )
            msp.add_line(
                (fx + (i - 1) / 50.0 * TE_FRAC * c, fy - max(ht_yt((i - 1) / 50.0 * TE_FRAC, c, t) - WALL, 0)),
                (fx + xc * c, fy - inner_yt),
                dxfattribs={"layer": "STRUCTURE"},
            )

    # Spar holes
    px = fx + c * PIVOT_FRAC
    rx = fx + c * RSPAR_FRAC
    msp.add_circle((px, fy), PIVOT_DIA / 2, dxfattribs={"layer": "SPAR"})
    msp.add_circle((rx, fy), RSPAR_DIA / 2, dxfattribs={"layer": "SPAR"})

    # =============================================
    # TITLE BLOCK
    # =============================================
    msp.add_text(
        "HStab_Right — Component Drawing",
        dxfattribs={"layer": "TEXT", "height": 5, "insert": (ox, 10)},
    )
    msp.add_text(
        "Mirror of HStab_Left | HT-14 root → HT-13 tip | 215mm span | 115/75mm chord",
        dxfattribs={"layer": "TEXT", "height": 2.5, "insert": (ox, 3)},
    )
    msp.add_text(
        "SCALE 1:1 | ALL DIMS IN mm | LW-PLA 0.45mm vase mode",
        dxfattribs={"layer": "TEXT", "height": 2, "insert": (ox, -3)},
    )

    # Dimensions
    dim1 = msp.add_linear_dim(
        base=(ox - 10, oy),
        p1=(ox, oy),
        p2=(ox, oy + HALF_SPAN),
        angle=90,
        dimstyle="COMP",
    )
    dim1.render()
    dim2 = msp.add_linear_dim(
        base=(ox, oy + HALF_SPAN + 15),
        p1=(ox, oy),
        p2=(ox + ROOT_CHORD * TE_FRAC, oy),
        dimstyle="COMP",
    )
    dim2.render()

    # Save
    out = "cad/components/empennage/HStab_Right/HStab_Right_drawing.dxf"
    save_dxf_and_png(doc, out)
    print("HStab_Right drawing complete.")


if __name__ == "__main__":
    main()
