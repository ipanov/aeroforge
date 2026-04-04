"""
Technical drawings for off-shelf electronic hardware components.
Generates DXF + PNG for: Flysky FS-iA6B, LiPo 3S 1300mAh, XT60 Connector.

These are off-shelf components (not aerodynamic), so no aero-structural
consensus is needed. Drawings serve as dimensional reference for fuselage
cavity sizing and CG calculations.

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/draw_hardware_electronics.py
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ezdxf
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# ── Shared helpers ──────────────────────────────────────────────────────────


def _add_rect(msp, x, y, w, h, layer="OUTLINE"):
    """Add a rectangle outline."""
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    for i in range(4):
        msp.add_line(pts[i], pts[i + 1], dxfattribs={"layer": layer})


def _add_centerlines(msp, cx, cy, ext_x, ext_y, layer="CENTERLINE"):
    """Add horizontal and vertical centerlines."""
    msp.add_line((cx - ext_x, cy), (cx + ext_x, cy),
                 dxfattribs={"layer": layer, "linetype": "CENTER"})
    msp.add_line((cx, cy - ext_y), (cx, cy + ext_y),
                 dxfattribs={"layer": layer, "linetype": "CENTER"})


def _add_dim_h(msp, x1, x2, y, offset, dimstyle="AEROFORGE"):
    """Horizontal dimension."""
    dim = msp.add_linear_dim(
        base=(x1, y + offset), p1=(x1, y), p2=(x2, y), dimstyle=dimstyle
    )
    dim.render()


def _add_dim_v(msp, y1, y2, x, offset, dimstyle="AEROFORGE"):
    """Vertical dimension."""
    dim = msp.add_linear_dim(
        base=(x + offset, y1), p1=(x, y1), p2=(x, y2),
        angle=90, dimstyle=dimstyle
    )
    dim.render()


# ── 1. Flysky FS-iA6B Receiver ─────────────────────────────────────────────


def draw_receiver():
    """Flysky FS-iA6B receiver: 47.2 x 26.2 x 15mm, 18g."""
    L, W, H = 47.2, 26.2, 15.0
    antenna_len = 165.0

    doc = setup_drawing(
        title="Flysky FS-iA6B Receiver",
        drawing_number="HW-RX-001",
        subtitle="6ch receiver, compatible with Turnigy 9X V2 | 47.2 x 26.2 x 15mm",
        material="Off-shelf electronic component",
        mass="18g",
        scale="2:1",
        status="APPROVED",
        orientation_labels={"fwd": "FWD"},
    )
    msp = doc.modelspace()

    # ── Top view (plan) ──────────────────────────────────────────
    ox, oy = 60, 180
    s = 2.0  # scale factor for visibility

    sL, sW, sH = L * s, W * s, H * s

    # PCB outline with rounded corners (approximate with rectangle)
    _add_rect(msp, ox, oy, sL, sW)
    _add_centerlines(msp, ox + sL / 2, oy + sW / 2, sL / 2 + 5, sW / 2 + 5)

    # Bind button (small circle on top)
    bind_x = ox + sL * 0.75
    bind_y = oy + sW * 0.65
    msp.add_circle((bind_x, bind_y), 2.0 * s, dxfattribs={"layer": "OUTLINE"})
    msp.add_text("BIND", height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(
        (bind_x + 3 * s, bind_y - 1))

    # Antenna exit point (+X end, top center)
    ant_x = ox + sL
    ant_y = oy + sW * 0.5
    msp.add_line((ant_x, ant_y), (ant_x + 15, ant_y),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_text("ANT (165mm)", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((ant_x + 17, ant_y - 1))

    # Servo pin headers (-Y side, 6 x 3-pin)
    pin_start_x = ox + sL * 0.15
    pin_spacing = sL * 0.7 / 5
    for i in range(6):
        px = pin_start_x + i * pin_spacing
        py = oy
        for j in range(3):
            msp.add_circle((px, py - (j + 1) * 2.0), 0.6,
                           dxfattribs={"layer": "OUTLINE"})
    msp.add_text("6x 3-pin servo headers", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((pin_start_x, oy - 12))

    # Dimensions
    _add_dim_h(msp, ox, ox + sL, oy, -18)
    _add_dim_v(msp, oy, oy + sW, ox, -12)

    # Label
    msp.add_text("TOP VIEW (2:1)", height=3, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox, oy + sW + 12))

    # ── Front view (end view showing height) ────────────────────
    fx, fy = 260, 180
    _add_rect(msp, fx, fy, sW, sH)
    _add_centerlines(msp, fx + sW / 2, fy + sH / 2, sW / 2 + 5, sH / 2 + 5)

    # Dimension: height
    _add_dim_v(msp, fy, fy + sH, fx + sW, 10)
    # Dimension: width
    _add_dim_h(msp, fx, fx + sW, fy, -12)

    msp.add_text("FRONT VIEW (2:1)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((fx, fy + sH + 12))

    # ── Side view ────────────────────────────────────────────────
    sx, sy = 60, 80
    _add_rect(msp, sx, sy, sL, sH)
    _add_centerlines(msp, sx + sL / 2, sy + sH / 2, sL / 2 + 5, sH / 2 + 5)

    _add_dim_h(msp, sx, sx + sL, sy, -12)
    _add_dim_v(msp, sy, sy + sH, sx, -10)

    msp.add_text("SIDE VIEW (2:1)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((sx, sy + sH + 12))

    out = "cad/components/hardware/Flysky_FS_iA6B_Receiver/Flysky_FS_iA6B_Receiver_drawing.dxf"
    save_dxf_and_png(doc, out)
    print(f"  Receiver drawing saved: {out}")


# ── 2. LiPo 3S 1300mAh Battery ────────────────────────────────────────────


def draw_battery():
    """3S 1300mAh 75C LiPo: 78 x 38 x 28mm, 155g (165g w/ XT60)."""
    L, W, H = 78.0, 38.0, 28.0

    doc = setup_drawing(
        title="LiPo 3S 1300mAh 75C Racing",
        drawing_number="HW-BAT-001",
        subtitle="Racing LiPo pack | 78 x 38 x 28mm | XT60 connector",
        material="Off-shelf battery pack (Tattu/GNB/CNHL)",
        mass="155g (pack) / 165g (w/ XT60)",
        scale="2:1",
        status="APPROVED",
        orientation_labels={"fwd": "FWD"},
    )
    msp = doc.modelspace()

    s = 2.0

    # ── Top view ─────────────────────────────────────────────────
    ox, oy = 55, 175
    sL, sW, sH = L * s, W * s, H * s

    # Rounded rectangle (main body)
    r = 3.0  # corner radius in scaled mm
    _add_rect(msp, ox, oy, sL, sW)
    _add_centerlines(msp, ox + sL / 2, oy + sW / 2, sL / 2 + 8, sW / 2 + 8)

    # Wire exit (+X end)
    wire_y_pos = oy + sW * 0.6
    wire_y_neg = oy + sW * 0.4
    for wy, label, color_idx in [(wire_y_pos, "+", 1), (wire_y_neg, "-", 5)]:
        msp.add_line((ox + sL, wy), (ox + sL + 20, wy),
                     dxfattribs={"layer": "OUTLINE"})
        msp.add_text(label, height=3, dxfattribs={"layer": "TEXT"}).set_placement(
            (ox + sL + 22, wy - 1.5))

    # Balance plug (+X end, side)
    bal_x = ox + sL - 10
    bal_y = oy + sW
    msp.add_line((bal_x, bal_y), (bal_x + 8, bal_y + 5),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_text("BAL", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (bal_x + 9, bal_y + 3))

    # Label area on top
    lbl_x = ox + sL * 0.15
    lbl_y = oy + sW * 0.25
    lbl_w = sL * 0.7
    lbl_h = sW * 0.5
    for (x1, y1, x2, y2) in [
        (lbl_x, lbl_y, lbl_x + lbl_w, lbl_y),
        (lbl_x + lbl_w, lbl_y, lbl_x + lbl_w, lbl_y + lbl_h),
        (lbl_x + lbl_w, lbl_y + lbl_h, lbl_x, lbl_y + lbl_h),
        (lbl_x, lbl_y + lbl_h, lbl_x, lbl_y),
    ]:
        msp.add_line((x1, y1), (x2, y2),
                     dxfattribs={"layer": "HIDDEN", "linetype": "DASHED"})

    # Dimensions
    _add_dim_h(msp, ox, ox + sL, oy, -15)
    _add_dim_v(msp, oy, oy + sW, ox, -12)

    msp.add_text("TOP VIEW (2:1)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((ox, oy + sW + 12))

    # ── Front view ───────────────────────────────────────────────
    fx, fy = 280, 175
    _add_rect(msp, fx, fy, sW, sH)
    _add_centerlines(msp, fx + sW / 2, fy + sH / 2, sW / 2 + 5, sH / 2 + 5)

    _add_dim_v(msp, fy, fy + sH, fx + sW, 10)
    _add_dim_h(msp, fx, fx + sW, fy, -12)

    msp.add_text("FRONT VIEW (2:1)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((fx, fy + sH + 12))

    # ── Side view ────────────────────────────────────────────────
    sx, sy = 55, 75
    _add_rect(msp, sx, sy, sL, sH)
    _add_centerlines(msp, sx + sL / 2, sy + sH / 2, sL / 2 + 5, sH / 2 + 5)

    # 3 cell divisions (dashed internal lines)
    cell_w = sL / 3
    for i in range(1, 3):
        cx = sx + i * cell_w
        msp.add_line((cx, sy), (cx, sy + sH),
                     dxfattribs={"layer": "HIDDEN", "linetype": "DASHED"})

    _add_dim_h(msp, sx, sx + sL, sy, -12)
    _add_dim_v(msp, sy, sy + sH, sx, -10)

    msp.add_text("SIDE VIEW (2:1)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((sx, sy + sH + 12))

    out = "cad/components/hardware/LiPo_3S_1300mAh/LiPo_3S_1300mAh_drawing.dxf"
    save_dxf_and_png(doc, out)
    print(f"  Battery drawing saved: {out}")


# ── 3. XT60 Male Connector ────────────────────────────────────────────────


def draw_xt60():
    """XT60 male connector: 16 x 8 x 15.8mm, 5g (pair)."""
    L, W, H = 16.0, 8.0, 15.8

    doc = setup_drawing(
        title="XT60 Male Connector",
        drawing_number="HW-CON-001",
        subtitle="Amass XT60 male (battery side) | 16 x 8 x 15.8mm | Keyed",
        material="Off-shelf connector (nylon body, gold-plated pins)",
        mass="~5g (pair)",
        scale="5:1",
        status="APPROVED",
        orientation_labels={"fwd": "FWD"},
    )
    msp = doc.modelspace()

    s = 5.0  # larger scale for small component

    # ── Front view (mating face) ─────────────────────────────────
    fx, fy = 60, 175
    sL, sW, sH = L * s, W * s, H * s

    # Keyed shape: rectangle with one chamfered corner (top-right)
    chamfer = 3.0 * s  # 3mm chamfer scaled
    pts = [
        (fx, fy),                                    # bottom-left
        (fx + sW, fy),                               # bottom-right
        (fx + sW, fy + sH - chamfer),               # right side up to chamfer
        (fx + sW - chamfer, fy + sH),               # chamfer diagonal
        (fx, fy + sH),                               # top-left
    ]
    for i in range(len(pts)):
        msp.add_line(pts[i], pts[(i + 1) % len(pts)],
                     dxfattribs={"layer": "OUTLINE"})

    # Pin holes (2 x 3.5mm bullet pins)
    pin_r = 3.5 / 2 * s
    pin_spacing = 4.0 * s  # approximate center-to-center
    pin_cx = fx + sW / 2
    for py_off in [-pin_spacing / 2, pin_spacing / 2]:
        msp.add_circle((pin_cx, fy + sH / 2 + py_off), pin_r,
                       dxfattribs={"layer": "OUTLINE"})

    # Chamfer annotation
    msp.add_text("KEY", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (fx + sW - chamfer + 2, fy + sH + 3))

    _add_dim_h(msp, fx, fx + sW, fy, -15)
    _add_dim_v(msp, fy, fy + sH, fx, -12)

    msp.add_text("FRONT VIEW (5:1)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((fx, fy + sH + 12))

    # ── Side view ────────────────────────────────────────────────
    sx, sy = 200, 175
    sDepth = L * s  # depth along insertion axis

    _add_rect(msp, sx, sy, sDepth, sH)
    _add_centerlines(msp, sx + sDepth / 2, sy + sH / 2, sDepth / 2 + 5, sH / 2 + 5)

    # Pin protrusion from front face (~3mm)
    pin_protrude = 3.0 * s
    for py_off in [-pin_spacing / 2, pin_spacing / 2]:
        py = sy + sH / 2 + py_off
        msp.add_line((sx - pin_protrude, py - pin_r * 0.3),
                     (sx, py - pin_r * 0.3),
                     dxfattribs={"layer": "OUTLINE"})
        msp.add_line((sx - pin_protrude, py + pin_r * 0.3),
                     (sx, py + pin_r * 0.3),
                     dxfattribs={"layer": "OUTLINE"})

    # Solder tabs on back (~5mm)
    tab_len = 5.0 * s
    for py_off in [-pin_spacing / 2, pin_spacing / 2]:
        py = sy + sH / 2 + py_off
        msp.add_line((sx + sDepth, py - 1.5 * s), (sx + sDepth + tab_len, py - 1.5 * s),
                     dxfattribs={"layer": "OUTLINE"})
        msp.add_line((sx + sDepth, py + 1.5 * s), (sx + sDepth + tab_len, py + 1.5 * s),
                     dxfattribs={"layer": "OUTLINE"})

    _add_dim_h(msp, sx, sx + sDepth, sy, -15)
    _add_dim_v(msp, sy, sy + sH, sx + sDepth, 12)

    msp.add_text("SIDE VIEW (5:1)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((sx, sy + sH + 12))

    # ── Top view ─────────────────────────────────────────────────
    tx, ty = 60, 80
    _add_rect(msp, tx, ty, sDepth, sW)

    # Chamfer on top view (shows as angled corner)
    chamf_top = 3.0 * s
    msp.add_line((tx + sDepth - chamf_top, ty + sW),
                 (tx + sDepth, ty + sW - chamf_top),
                 dxfattribs={"layer": "OUTLINE"})

    _add_dim_h(msp, tx, tx + sDepth, ty, -12)
    _add_dim_v(msp, ty, ty + sW, tx, -10)

    msp.add_text("TOP VIEW (5:1)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((tx, ty + sW + 12))

    out = "cad/components/hardware/XT60_Connector/XT60_Connector_drawing.dxf"
    save_dxf_and_png(doc, out)
    print(f"  XT60 drawing saved: {out}")


# ── Main ──────────────────────────────────────────────────────────────────


def main():
    print("Generating hardware electronics drawings...")
    draw_receiver()
    draw_battery()
    draw_xt60()
    print("\nAll hardware drawings generated.")


if __name__ == "__main__":
    main()
