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
FUSELAGE_GAP = 38.0
MAIN_SPAR_FRAC = 0.25
REAR_SPAR_FRAC = 0.60
HINGE_FRAC = 0.72
MAIN_SPAR_HALF_LEN = 1024.0
MAIN_SPAR_TIP_LEN = 256.0
REAR_SPAR_HALF_LEN = 1024.0
FLAP_END = 768.0
AILERON_START = 768.0
SERVO_STATIONS = [
    ("FLAP SERVO P1", 128.0, 0.35, 23.0, 11.0),
    ("FLAP SERVO P3", 640.0, 0.35, 23.0, 11.0),
    ("AILERON SERVO P4", 896.0, 0.35, 23.0, 11.0),
    ("AILERON SERVO P5", 1152.0, 0.30, 20.0, 10.0),
]

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


def _draw_single_half_top_view(msp, x_root: float, y_le: float, scale: float, direction: int, show_servos: bool) -> None:
    """Draw one wing half in plan view with span horizontal."""
    last_le = None
    last_te = None
    for i in range(len(CHORD_SPANS)):
        s = CHORD_SPANS[i]
        chord = chord_at_span(s)
        xx = x_root + direction * s * scale
        le = (xx, y_le)
        te = (xx, y_le - chord * scale)
        if i > 0:
            msp.add_line(last_le, le, dxfattribs={"layer": "OUTLINE"})
            msp.add_line(last_te, te, dxfattribs={"layer": "OUTLINE"})
        last_le = le
        last_te = te

    tip_x = x_root + direction * HALF_SPAN * scale
    msp.add_line((x_root, y_le), (x_root, y_le - ROOT_CHORD * scale), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((tip_x, y_le), (tip_x, y_le - TIP_CHORD * scale), dxfattribs={"layer": "OUTLINE"})

    # panel stations
    for idx in range(1, 5):
        s = idx * PANEL_SPAN
        xx = x_root + direction * s * scale
        chord = chord_at_span(s)
        msp.add_line((xx, y_le), (xx, y_le - chord * scale), dxfattribs={"layer": "SECTION"})
        label_x = xx - 12 if direction > 0 else xx + 4
        msp.add_text(PANEL_NAMES[idx - 1], height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((label_x, y_le - 9))
    tip_label_x = tip_x - 18 if direction > 0 else tip_x + 4
    msp.add_text("P5", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((tip_label_x, y_le - 9))

    # spar and hinge lines
    for frac, layer, end_span in [
        (MAIN_SPAR_FRAC, "SPAR", MAIN_SPAR_HALF_LEN),
        (REAR_SPAR_FRAC, "SPAR", REAR_SPAR_HALF_LEN),
        (HINGE_FRAC, "CENTERLINE", HALF_SPAN),
    ]:
        pts = []
        for s in CHORD_SPANS:
            if s > end_span:
                continue
            xx = x_root + direction * s * scale
            yy = y_le - chord_at_span(s) * frac * scale
            pts.append((xx, yy))
        for i in range(len(pts) - 1):
            msp.add_line(pts[i], pts[i + 1], dxfattribs={"layer": layer})

    # P5 stepped spar at 27%
    pts = []
    for s in [1024.0, 1152.0, 1216.0, 1280.0]:
        xx = x_root + direction * s * scale
        yy = y_le - chord_at_span(s) * 0.27 * scale
        pts.append((xx, yy))
    for i in range(len(pts) - 1):
        msp.add_line(pts[i], pts[i + 1], dxfattribs={"layer": "SPAR"})

    # control surfaces
    for start, end, text in [(0.0, FLAP_END, "FLAP"), (AILERON_START, HALF_SPAN, "AILERON")]:
        x1 = x_root + direction * start * scale
        x2 = x_root + direction * end * scale
        y1 = y_le - chord_at_span(start) * HINGE_FRAC * scale
        y2 = y_le - chord_at_span(end) * HINGE_FRAC * scale
        msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "CENTERLINE"})
        tx = (x1 + x2) / 2
        ty = (y1 + y2) / 2 - 12
        msp.add_text(text, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((tx - 8, ty))

    # servo envelopes
    if show_servos:
        for label, station, frac, w, h in SERVO_STATIONS:
            chord = chord_at_span(station)
            cx = x_root + direction * station * scale
            cy = y_le - chord * frac * scale
            hw = (w * scale) / 2
            hh = (h * scale) / 2
            x_a = cx - hw
            x_b = cx + hw
            y_a = cy - hh
            y_b = cy + hh
            msp.add_line((x_a, y_a), (x_b, y_a), dxfattribs={"layer": "HIDDEN"})
            msp.add_line((x_b, y_a), (x_b, y_b), dxfattribs={"layer": "HIDDEN"})
            msp.add_line((x_b, y_b), (x_a, y_b), dxfattribs={"layer": "HIDDEN"})
            msp.add_line((x_a, y_b), (x_a, y_a), dxfattribs={"layer": "HIDDEN"})
            msp.add_text(label, height=1.5, dxfattribs={"layer": "TEXT"}).set_placement((cx - 10, cy + 4))


def add_wing_top_view(msp, x0: float, y_le: float, scale: float, full: bool) -> tuple[float, float]:
    """Return (x_root_left, x_root_right) for gap-related annotations."""
    if full:
        x_root_left = x0 + HALF_SPAN * scale
        x_root_right = x_root_left + FUSELAGE_GAP * scale
        _draw_single_half_top_view(msp, x_root_left, y_le, scale, -1, False)
        _draw_single_half_top_view(msp, x_root_right, y_le, scale, +1, False)
        # fuselage gap
        msp.add_line((x_root_left, y_le + 10), (x_root_left, y_le - ROOT_CHORD * scale - 10), dxfattribs={"layer": "CENTERLINE"})
        msp.add_line((x_root_right, y_le + 10), (x_root_right, y_le - ROOT_CHORD * scale - 10), dxfattribs={"layer": "CENTERLINE"})
        return x_root_left, x_root_right
    x_root = x0
    _draw_single_half_top_view(msp, x_root, y_le, scale, +1, True)
    return x_root, x_root


def add_wing_front_view(msp, x0: float, y0: float, scale: float, full: bool) -> tuple[float, float]:
    # piecewise linear front elevation emphasizing polyhedral
    half_pts = [
        (0, 0),
        (256, 0),
        (512, 0),
        (768, 8),
        (1024, 24),
        (1280, 50),
    ]
    gap_half = (FUSELAGE_GAP / 2) * scale if full else 0.0
    if full:
        pts = [(-gap_half - x * scale, y0 + y) for x, y in half_pts[::-1]]
        pts += [(gap_half + x * scale, y0 + y) for x, y in half_pts]
        mapped = [(x0 + x, y) for x, y in pts]
    else:
        mapped = [(x0 + x * scale, y0 + y) for x, y in half_pts]
    for i in range(len(mapped) - 1):
        msp.add_line(mapped[i], mapped[i + 1], dxfattribs={"layer": "OUTLINE"})
    for idx, (x, y) in enumerate(half_pts):
        mx = x0 + (gap_half + x * scale if full else x * scale)
        msp.add_line((mx, y0 - 10), (mx, y0 + y + 8), dxfattribs={"layer": "SECTION"})
        if idx < len(POLYHEDRAL_LABELS):
            msp.add_text(POLYHEDRAL_LABELS[idx], height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((mx + 2, y0 + y + 10))
        if full and x != 0:
            mmx = x0 - (gap_half + x * scale)
            msp.add_line((mmx, y0 - 10), (mmx, y0 + y + 8), dxfattribs={"layer": "SECTION"})
    return x0 - gap_half, x0 + gap_half


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

    wing_scale = 0.28  # common scale across top/front/profile
    top_x0 = 85.0
    top_y_le = 505.0
    msp.add_text("TOP VIEW — WING HALF ASSEMBLY", height=4.2, dxfattribs={"layer": "TEXT"}).set_placement((top_x0, 530))
    add_wing_top_view(msp, top_x0, top_y_le, wing_scale, full=False)

    msp.add_text("FRONT VIEW — POLYHEDRAL / DIHEDRAL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((top_x0, 260))
    add_wing_front_view(msp, top_x0, 205, wing_scale, full=False)

    msp.add_text("PROFILE DETAILS — ROOT / TIP AIRFOIL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((500, 260))
    add_wing_side_view(msp, 525, 215, wing_scale)

    # Main dimensions
    msp.add_linear_dim(base=(top_x0 + HALF_SPAN * wing_scale / 2, 110),
                       p1=(top_x0, 118),
                       p2=(top_x0 + HALF_SPAN * wing_scale, 118),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()
    msp.add_linear_dim(base=(60, top_y_le - ROOT_CHORD * wing_scale / 2),
                       p1=(68, top_y_le),
                       p2=(68, top_y_le - ROOT_CHORD * wing_scale),
                       angle=90,
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()

    # Notes
    msp.add_text("Main spar 8mm tube to P4/P5, 5mm rod in P5", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((460, 175))
    msp.add_text("Rear spar 5x3 spruce to P4/P5 only", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((460, 155))
    msp.add_text("Hinge line at 72% chord; flap P1-P3, aileron P4-P5", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((460, 135))
    msp.add_text("Servo envelopes shown per current consensus only", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((460, 115))

    out = ROOT / "cad/assemblies/wing/Wing_Half_Assembly/Wing_Half_Assembly_drawing.dxf"
    return save_dxf_and_png(doc, str(out), dpi=240)


def draw_wing_assembly() -> tuple[str, str]:
    doc = setup_drawing(
        title="Wing_Assembly",
        subtitle="Full-wing parent drawing. This sheet governs wing-level review before panel derivation.",
        material="Mirrored half-wing assemblies with progressive polyhedral",
        mass="430g full wing target",
        scale="1:6 common",
        sheet_size="A1",
        status="FOR ITERATION",
        revision="v1",
        orientation_labels={"fwd": "FWD", "inbd": "CL"},
    )
    msp = doc.modelspace()

    wing_scale = 0.27
    top_x0 = 55.0
    top_y_le = 505.0
    msp.add_text("TOP VIEW — FULL WING ASSEMBLY", height=4.2, dxfattribs={"layer": "TEXT"}).set_placement((top_x0, 530))
    x_left_root, x_right_root = add_wing_top_view(msp, top_x0, top_y_le, wing_scale, full=True)

    msp.add_text("FRONT VIEW — FULL SPAN POLYHEDRAL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((top_x0, 255))
    gap_left, gap_right = add_wing_front_view(msp, top_x0 + HALF_SPAN * wing_scale + (FUSELAGE_GAP * wing_scale) / 2, 205, wing_scale, full=True)

    msp.add_text("PROFILE DETAILS — ROOT / TIP AIRFOIL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((625, 255))
    add_wing_side_view(msp, 635, 210, wing_scale)

    total_width = FULL_SPAN * wing_scale + FUSELAGE_GAP * wing_scale
    msp.add_linear_dim(base=(top_x0 + total_width / 2, 105),
                       p1=(top_x0, 113),
                       p2=(top_x0 + total_width, 113),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()
    msp.add_linear_dim(base=(58, top_y_le - ROOT_CHORD * wing_scale / 2),
                       p1=(66, top_y_le),
                       p2=(66, top_y_le - ROOT_CHORD * wing_scale),
                       angle=90,
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()
    msp.add_linear_dim(base=((x_left_root + x_right_root) / 2, top_y_le + 18),
                       p1=(x_left_root, top_y_le + 10),
                       p2=(x_right_root, top_y_le + 10),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()

    msp.add_text("Baseline assembly only. Re-open planform optimization before next panel generation.",
                 height=2.2, dxfattribs={"layer": "TEXT"}).set_placement((95, 72))
    msp.add_text("Flap zone: P1-P3", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((250, 145))
    msp.add_text("Aileron zone: P4-P5", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((430, 145))
    msp.add_text("Fuselage center gap shown between root faces", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((285, 125))
    msp.add_text("8mm main spar visible to root; carry-through/joiner region at center", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((250, 105))

    # root detail showing gap and spar ends
    detail_x = 600.0
    detail_y = 485.0
    msp.add_text("ROOT DETAIL — CENTER GAP / SPAR REGION", height=2.8, dxfattribs={"layer": "TEXT"}).set_placement((detail_x - 10, detail_y + 20))
    chord = ROOT_CHORD * wing_scale * 1.25
    gap = FUSELAGE_GAP * wing_scale * 1.25
    left_x = detail_x
    right_x = detail_x + 70 + gap
    y_top = detail_y
    y_bot = detail_y - chord
    # root faces
    msp.add_line((left_x, y_top), (left_x, y_bot), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((right_x, y_top), (right_x, y_bot), dxfattribs={"layer": "OUTLINE"})
    # spar stubs
    for frac, layer, text in [(MAIN_SPAR_FRAC, "SPAR", "8mm MAIN"), (REAR_SPAR_FRAC, "SPAR", "REAR 5x3"), (HINGE_FRAC, "CENTERLINE", "HINGE")]:
        yy = y_top - ROOT_CHORD * frac * wing_scale * 1.25
        msp.add_line((left_x - 28, yy), (left_x, yy), dxfattribs={"layer": layer})
        msp.add_line((right_x, yy), (right_x + 28, yy), dxfattribs={"layer": layer})
        msp.add_text(text, height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((right_x + 32, yy - 1))

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
