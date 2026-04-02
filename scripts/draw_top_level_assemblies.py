"""
Generate top-level assembly drawings with professional three-view layout.

Outputs:
  - cad/assemblies/wing/Wing_Assembly/Wing_Assembly_drawing.dxf/.png
  - cad/assemblies/wing/Wing_Half_Assembly/Wing_Half_Assembly_drawing.dxf/.png
  - cad/assemblies/fuselage/Fuselage_Assembly/Fuselage_Assembly_drawing.dxf/.png
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.dxf_utils import save_dxf_and_png, setup_drawing

ROOT = Path(__file__).resolve().parent.parent

HALF_SPAN = 1280.0
FULL_SPAN = 2560.0
PANEL_SPAN = 256.0
ROOT_CHORD = 210.0
TIP_CHORD = 115.0

CHORD_SPANS = [0, 256, 512, 640, 768, 896, 1024, 1152, 1216, 1280]
CHORD_VALUES = [210, 204, 198, 192, 186, 180, 168, 156, 144, 115]
PANEL_NAMES = ["P1", "P2", "P3", "P4", "P5"]
POLYHEDRAL_LABELS = ["0.0°", "0.0°", "1.5°", "2.5°", "7.0°"]

FUSELAGE_XSECTIONS = [
    (0, 0, 0),
    (30, 32, 32),
    (55, 35, 35),
    (150, 50, 44),
    (260, 38, 34),
    (350, 30, 26),
    (500, 18, 16),
    (650, 13, 13),
    (866, 8.5, 165),
    (911, 7, 145),
    (1046, 0, 0),
]


def chord_at_span(span_mm: float) -> float:
    for i in range(len(CHORD_SPANS) - 1):
        x0 = CHORD_SPANS[i]
        x1 = CHORD_SPANS[i + 1]
        if x0 <= span_mm <= x1:
            t = 0.0 if x1 == x0 else (span_mm - x0) / (x1 - x0)
            return CHORD_VALUES[i] + t * (CHORD_VALUES[i + 1] - CHORD_VALUES[i])
    return CHORD_VALUES[-1]


def wing_thickness_at_span(span_mm: float) -> float:
    frac = span_mm / HALF_SPAN
    thickness_ratio = 0.086 + frac * (0.064 - 0.086)
    return chord_at_span(span_mm) * thickness_ratio


def fuselage_dim_at(x_mm: float, dim_idx: int) -> float:
    for i in range(len(FUSELAGE_XSECTIONS) - 1):
        x0, w0, h0 = FUSELAGE_XSECTIONS[i]
        x1, w1, h1 = FUSELAGE_XSECTIONS[i + 1]
        if x0 <= x_mm <= x1:
            t = 0.0 if x1 == x0 else (x_mm - x0) / (x1 - x0)
            v0 = w0 if dim_idx == 1 else h0
            v1 = w1 if dim_idx == 1 else h1
            return v0 + t * (v1 - v0)
    return 0.0


def add_airfoil_outline(msp, cx: float, cy: float, chord: float, thickness: float, layer: str = "OUTLINE") -> None:
    a = chord / 2
    b = thickness / 2
    pts = []
    for i in range(61):
        theta = math.pi * i / 60
        x = cx - a + chord * i / 60
        y = cy + b * math.sin(theta)
        pts.append((x, y))
    for i in range(61):
        theta = math.pi * (60 - i) / 60
        x = cx + a - chord * i / 60
        y = cy - b * math.sin(theta)
        pts.append((x, y))
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})


def add_wing_top_view(msp, x0: float, y0: float, scale: float, full: bool) -> None:
    if full:
        for sign in (-1, 1):
            last_te = None
            for i in range(len(CHORD_SPANS) - 1):
                s0 = CHORD_SPANS[i]
                s1 = CHORD_SPANS[i + 1]
                c0 = chord_at_span(s0)
                c1 = chord_at_span(s1)
                yy0 = y0 + sign * s0 * scale
                yy1 = y0 + sign * s1 * scale
                msp.add_line((x0, yy0), (x0, yy1), dxfattribs={"layer": "OUTLINE"})
                msp.add_line((x0 + c0 * scale, yy0), (x0 + c1 * scale, yy1), dxfattribs={"layer": "OUTLINE"})
                last_te = (x0 + c1 * scale, yy1)
            msp.add_line((x0, y0), (x0 + ROOT_CHORD * scale, y0), dxfattribs={"layer": "OUTLINE"})
            if last_te is not None:
                msp.add_line((x0, y0 + sign * HALF_SPAN * scale), last_te, dxfattribs={"layer": "OUTLINE"})
            for idx in range(1, 5):
                s = idx * PANEL_SPAN
                yy = y0 + sign * s * scale
                chord = chord_at_span(s)
                msp.add_line((x0, yy), (x0 + chord * scale, yy), dxfattribs={"layer": "SECTION"})
    else:
        last_te = None
        for i in range(len(CHORD_SPANS) - 1):
            s0 = CHORD_SPANS[i]
            s1 = CHORD_SPANS[i + 1]
            c0 = chord_at_span(s0)
            c1 = chord_at_span(s1)
            yy0 = y0 + s0 * scale
            yy1 = y0 + s1 * scale
            msp.add_line((x0, yy0), (x0, yy1), dxfattribs={"layer": "OUTLINE"})
            msp.add_line((x0 + c0 * scale, yy0), (x0 + c1 * scale, yy1), dxfattribs={"layer": "OUTLINE"})
            last_te = (x0 + c1 * scale, yy1)
        msp.add_line((x0, y0), (x0 + ROOT_CHORD * scale, y0), dxfattribs={"layer": "OUTLINE"})
        if last_te is not None:
            msp.add_line((x0, y0 + HALF_SPAN * scale), last_te, dxfattribs={"layer": "OUTLINE"})
        for idx in range(1, 5):
            s = idx * PANEL_SPAN
            yy = y0 + s * scale
            chord = chord_at_span(s)
            msp.add_line((x0, yy), (x0 + chord * scale, yy), dxfattribs={"layer": "SECTION"})
            msp.add_text(PANEL_NAMES[idx - 1], height=2.3, dxfattribs={"layer": "TEXT"}).set_placement((x0 + 6, yy - 6))
        msp.add_text("P5", height=2.3, dxfattribs={"layer": "TEXT"}).set_placement((x0 + 6, y0 + (HALF_SPAN - 70) * scale))

    if full:
        msp.add_line((x0 - 18, y0), (x0 + ROOT_CHORD * scale + 18, y0), dxfattribs={"layer": "CENTERLINE"})


def add_wing_front_view(msp, x0: float, y0: float, scale: float, full: bool) -> None:
    # piecewise linear front elevation emphasizing polyhedral
    half_pts = [
        (0, 0),
        (256, 0),
        (512, 0),
        (768, 8),
        (1024, 24),
        (1280, 50),
    ]
    if full:
        pts = [(-x, y) for x, y in reversed(half_pts[1:])] + half_pts
    else:
        pts = half_pts
    mapped = [(x0 + x * scale, y0 + y) for x, y in pts]
    for i in range(len(mapped) - 1):
        msp.add_line(mapped[i], mapped[i + 1], dxfattribs={"layer": "OUTLINE"})
    for idx, (x, y) in enumerate(half_pts):
        mx = x0 + x * scale
        msp.add_line((mx, y0 - 10), (mx, y0 + y + 8), dxfattribs={"layer": "SECTION"})
        if idx < len(POLYHEDRAL_LABELS):
            msp.add_text(POLYHEDRAL_LABELS[idx], height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((mx + 2, y0 + y + 10))
        if full and x != 0:
            mmx = x0 - x * scale
            msp.add_line((mmx, y0 - 10), (mmx, y0 + y + 8), dxfattribs={"layer": "SECTION"})


def add_wing_side_view(msp, x0: float, y0: float, scale: float) -> None:
    root_t = wing_thickness_at_span(0)
    tip_t = wing_thickness_at_span(HALF_SPAN)
    # root section
    add_airfoil_outline(msp, x0 + ROOT_CHORD * scale / 2, y0, ROOT_CHORD * scale, root_t * scale)
    # tip section stacked below
    add_airfoil_outline(msp, x0 + TIP_CHORD * scale / 2, y0 - 55, TIP_CHORD * scale, tip_t * scale)
    msp.add_text("ROOT PROFILE", height=2.1, dxfattribs={"layer": "TEXT"}).set_placement((x0 + 10, y0 + 14))
    msp.add_text("TIP PROFILE", height=2.1, dxfattribs={"layer": "TEXT"}).set_placement((x0 + 10, y0 - 41))
    for frac, layer in [(0.25, "SPAR"), (0.60, "SPAR"), (0.72, "CENTERLINE")]:
        msp.add_line((x0 + ROOT_CHORD * scale * frac, y0 - root_t * scale / 2 - 4),
                     (x0 + ROOT_CHORD * scale * frac, y0 + root_t * scale / 2 + 4),
                     dxfattribs={"layer": layer})


def draw_wing_half_assembly() -> tuple[str, str]:
    doc = setup_drawing(
        title="Wing_Half_Assembly",
        subtitle="Canonical half-wing parent drawing. Use this before panel decomposition.",
        material="LW-PLA shells + CF-PLA ribs + 8mm/5mm CF spars + spruce rear spar",
        mass="215g target with contingency",
        scale="1:3 / 1:2 detail",
        sheet_size="A1",
        status="FOR ITERATION",
        revision="v1",
    )
    msp = doc.modelspace()

    top_scale = 1 / 3
    top_x0 = 120.0
    top_y0 = 75.0
    msp.add_text("TOP VIEW — WING HALF ASSEMBLY", height=4.2, dxfattribs={"layer": "TEXT"}).set_placement((top_x0, 540))
    add_wing_top_view(msp, top_x0, top_y0, top_scale, full=False)

    msp.add_text("FRONT VIEW — POLYHEDRAL / DIHEDRAL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((380, 250))
    add_wing_front_view(msp, 410, 180, 0.22, full=False)

    msp.add_text("SIDE VIEW — ROOT / TIP PROFILES", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((525, 540))
    add_wing_side_view(msp, 540, 470, 0.55)

    # Main dimensions
    msp.add_linear_dim(base=(top_x0 + ROOT_CHORD * top_scale / 2, 52),
                       p1=(top_x0, 58),
                       p2=(top_x0 + ROOT_CHORD * top_scale, 58),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()
    msp.add_linear_dim(base=(92, top_y0 + HALF_SPAN * top_scale / 2),
                       p1=(100, top_y0),
                       p2=(100, top_y0 + HALF_SPAN * top_scale),
                       angle=90,
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()

    # Notes
    msp.add_text("Main spar at 25% chord", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((160, 225))
    msp.add_text("Rear spar at 60% chord", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((160, 205))
    msp.add_text("Hinge line at 72% chord", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((160, 185))
    msp.add_text("Flaps P1-P3, Ailerons P4-P5", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((160, 165))

    out = ROOT / "cad/assemblies/wing/Wing_Half_Assembly/Wing_Half_Assembly_drawing.dxf"
    return save_dxf_and_png(doc, str(out), dpi=240)


def draw_wing_assembly() -> tuple[str, str]:
    doc = setup_drawing(
        title="Wing_Assembly",
        subtitle="Full-wing parent drawing. This sheet governs wing-level review before panel derivation.",
        material="Mirrored half-wing assemblies with progressive polyhedral",
        mass="430g full wing target",
        scale="1:5 / 1:3 front",
        sheet_size="A1",
        status="FOR ITERATION",
        revision="v1",
        orientation_labels={"fwd": "FWD", "inbd": "CL"},
    )
    msp = doc.modelspace()

    top_scale = 1 / 5
    top_x0 = 315.0
    top_y0 = 245.0
    msp.add_text("TOP VIEW — FULL WING ASSEMBLY", height=4.2, dxfattribs={"layer": "TEXT"}).set_placement((250, 532))
    add_wing_top_view(msp, top_x0, top_y0, top_scale, full=True)

    msp.add_text("FRONT VIEW — FULL SPAN POLYHEDRAL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((220, 145))
    add_wing_front_view(msp, 405, 92, 0.20, full=True)

    msp.add_text("SIDE VIEW — SECTION REFERENCE", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((560, 520))
    add_wing_side_view(msp, 585, 465, 0.42)

    msp.add_linear_dim(base=(top_x0 + ROOT_CHORD * top_scale / 2, 250),
                       p1=(top_x0, 258),
                       p2=(top_x0 + ROOT_CHORD * top_scale, 258),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()
    msp.add_linear_dim(base=(280, top_y0),
                       p1=(290, top_y0 - HALF_SPAN * top_scale),
                       p2=(290, top_y0 + HALF_SPAN * top_scale),
                       angle=90,
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()

    msp.add_text("Baseline assembly only. Re-open planform optimization before next panel generation.",
                 height=2.2, dxfattribs={"layer": "TEXT"}).set_placement((95, 72))
    msp.add_text("Flap zone: P1-P3", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((350, 390))
    msp.add_text("Aileron zone: P4-P5", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((350, 490))

    out = ROOT / "cad/assemblies/wing/Wing_Assembly/Wing_Assembly_drawing.dxf"
    return save_dxf_and_png(doc, str(out), dpi=240)


def draw_fuselage_assembly() -> tuple[str, str]:
    doc = setup_drawing(
        title="Fuselage_Assembly",
        subtitle="Full fuselage three-view baseline. This assembly drawing precedes section/component breakdown.",
        material="LW-PLA shell + PETG motor bay + 4x 2mm CF longerons",
        mass="~91g excl. VStab skin",
        scale="1:2",
        sheet_size="A1",
        status="FOR ITERATION",
        revision="v1",
        orientation_labels={"fwd": "FWD", "inbd": "UP"},
    )
    msp = doc.modelspace()

    side_x0 = 45.0
    side_y0 = 430.0
    top_x0 = 45.0
    top_y0 = 270.0
    sec_x0 = 595.0
    sec_y0 = 430.0

    msp.add_text("SIDE VIEW — FUSELAGE ASSEMBLY (1:2)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((side_x0, side_y0 + 78))
    msp.add_text("TOP VIEW — FUSELAGE ASSEMBLY (1:2)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((top_x0, top_y0 + 58))

    for i in range(len(FUSELAGE_XSECTIONS) - 1):
        x0, w0, h0 = FUSELAGE_XSECTIONS[i]
        x1, w1, h1 = FUSELAGE_XSECTIONS[i + 1]
        msp.add_line((side_x0 + x0 / 2, side_y0 + h0 / 4),
                     (side_x0 + x1 / 2, side_y0 + h1 / 4),
                     dxfattribs={"layer": "OUTLINE"})
        msp.add_line((side_x0 + x0 / 2, side_y0 - h0 / 4),
                     (side_x0 + x1 / 2, side_y0 - h1 / 4),
                     dxfattribs={"layer": "OUTLINE"})
        msp.add_line((top_x0 + x0 / 2, top_y0 + w0 / 4),
                     (top_x0 + x1 / 2, top_y0 + w1 / 4),
                     dxfattribs={"layer": "OUTLINE"})
        msp.add_line((top_x0 + x0 / 2, top_y0 - w0 / 4),
                     (top_x0 + x1 / 2, top_y0 - w1 / 4),
                     dxfattribs={"layer": "OUTLINE"})

    msp.add_line((side_x0 - 10, side_y0), (side_x0 + 540, side_y0), dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((top_x0 - 10, top_y0), (top_x0 + 540, top_y0), dxfattribs={"layer": "CENTERLINE"})

    for x_mm, label in [(260, "Wing LE"), (350, "Servo bay"), (650, "Boom/fin blend"), (866, "Fin root"), (911, "HStab pivot")]:
        x = side_x0 + x_mm / 2
        top = side_y0 + fuselage_dim_at(x_mm, 2) / 4 + 12
        bot = side_y0 - fuselage_dim_at(x_mm, 2) / 4 - 12
        msp.add_line((x, bot), (x, top), dxfattribs={"layer": "SECTION"})
        msp.add_text(label, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((x - 10, top + 5))

    msp.add_text("Battery max section at X=150", height=2.4, dxfattribs={"layer": "TEXT"}).set_placement((side_x0 + 60, side_y0 + 48))
    msp.add_text("Wing saddle / spar tunnel at X=260", height=2.4, dxfattribs={"layer": "TEXT"}).set_placement((side_x0 + 125, side_y0 - 64))
    msp.add_text("Integrated fin from X=650-1046", height=2.4, dxfattribs={"layer": "TEXT"}).set_placement((side_x0 + 318, side_y0 + 58))

    msp.add_linear_dim(base=(side_x0 + 260, side_y0 - 70),
                       p1=(side_x0, side_y0 - 60),
                       p2=(side_x0 + 1046 / 2, side_y0 - 60),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()

    for idx, (x_mm, title) in enumerate([(30, "A — Motor Face"), (150, "B — Max Section"), (260, "C — Wing LE Joint")]):
        cx = sec_x0 + (idx % 2) * 120
        cy = sec_y0 - (idx // 2) * 110
        w = fuselage_dim_at(x_mm, 1)
        h = fuselage_dim_at(x_mm, 2)
        msp.add_text(f"SEC {title}", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement((cx - 28, cy + h / 4 + 18))
        msp.add_ellipse((cx, cy), major_axis=(w / 4, 0), ratio=(h / w) if w else 1.0, dxfattribs={"layer": "OUTLINE"})
        msp.add_line((cx, cy - h / 4 - 5), (cx, cy + h / 4 + 5), dxfattribs={"layer": "CENTERLINE"})
        msp.add_line((cx - w / 4 - 5, cy), (cx + w / 4 + 5, cy), dxfattribs={"layer": "CENTERLINE"})

    msp.add_text("This three-view is the top-down fuselage parent before section/component derivation.",
                 height=2.2, dxfattribs={"layer": "TEXT"}).set_placement((95, 72))

    out = ROOT / "cad/assemblies/fuselage/Fuselage_Assembly/Fuselage_Assembly_drawing.dxf"
    return save_dxf_and_png(doc, str(out), dpi=240)


def main() -> None:
    draw_wing_half_assembly()
    draw_wing_assembly()
    draw_fuselage_assembly()


if __name__ == "__main__":
    main()
