"""
Generate missing top-level assembly drawings for the current baseline geometry.

This restores the intended workflow order for the wing and fuselage:
assembly drawing first, then derived component drawings and 3D parts.

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


# Wing baseline from current assembly consensus
HALF_SPAN = 1280.0
FULL_SPAN = 2560.0
PANEL_SPAN = 256.0
ROOT_CHORD = 210.0
TIP_CHORD = 115.0

CHORD_SPANS = [0, 256, 512, 640, 768, 896, 1024, 1152, 1216, 1280]
CHORD_VALUES = [210, 204, 198, 192, 186, 180, 168, 156, 144, 115]
DIHEDRAL_JOINTS = [0, 256, 512, 768, 1024, 1280]
DIHEDRAL_LABELS = ["0.0°", "0.0°", "0.0°", "1.5°", "4.0°", "7.0° EDA"]

# Fuselage baseline from current fuselage consensus
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
            c0 = CHORD_VALUES[i]
            c1 = CHORD_VALUES[i + 1]
            return c0 + t * (c1 - c0)
    return CHORD_VALUES[-1]


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


def draw_wing_half_assembly() -> tuple[str, str]:
    doc = setup_drawing(
        title="Wing_Half_Assembly",
        subtitle="Canonical half-wing assembly baseline. Mirror this assembly for left/right aircraft integration.",
        material="LW-PLA shells + CF-PLA ribs + 8mm/5mm CF spars + spruce rear spar",
        mass="215g target with contingency",
        scale="1:2",
        sheet_size="A1",
        status="FOR ITERATION",
        revision="v0",
    )
    msp = doc.modelspace()

    top_x0 = 55.0
    top_y0 = 285.0
    sec_x0 = 600.0
    sec_y0 = 405.0

    msp.add_text("TOP VIEW — WING HALF ASSEMBLY (1:2)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((top_x0, top_y0 + 80))

    # Outline
    last_le = 0.0
    last_te = ROOT_CHORD
    for i in range(len(CHORD_SPANS) - 1):
        s0 = CHORD_SPANS[i]
        s1 = CHORD_SPANS[i + 1]
        c0 = chord_at_span(s0)
        c1 = chord_at_span(s1)
        le0 = 0.0
        le1 = 0.0
        te0 = le0 + c0
        te1 = le1 + c1
        msp.add_line((top_x0 + le0 / 2, top_y0 + s0 / 2),
                     (top_x0 + le1 / 2, top_y0 + s1 / 2),
                     dxfattribs={"layer": "OUTLINE"})
        msp.add_line((top_x0 + te0 / 2, top_y0 + s0 / 2),
                     (top_x0 + te1 / 2, top_y0 + s1 / 2),
                     dxfattribs={"layer": "OUTLINE"})
        last_le = le1
        last_te = te1

    msp.add_line((top_x0, top_y0), (top_x0 + ROOT_CHORD / 2, top_y0),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_line((top_x0 + last_le / 2, top_y0 + HALF_SPAN / 2),
                 (top_x0 + last_te / 2, top_y0 + HALF_SPAN / 2),
                 dxfattribs={"layer": "OUTLINE"})

    # Panel boundaries + labels
    for idx in range(6):
        span = idx * PANEL_SPAN
        chord = chord_at_span(span if span <= HALF_SPAN else HALF_SPAN)
        msp.add_line((top_x0, top_y0 + span / 2),
                     (top_x0 + chord / 2, top_y0 + span / 2),
                     dxfattribs={"layer": "SECTION"})
        if idx < 5:
            msp.add_text(f"P{idx + 1}", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
                (top_x0 + 8, top_y0 + (span + PANEL_SPAN / 2) / 2)
            )

    # Spars / hinge / controls
    for frac, layer, label in [
        (0.25, "SPAR", "MAIN SPAR"),
        (0.60, "SPAR", "REAR SPAR"),
        (0.72, "CENTERLINE", "HINGE"),
    ]:
        for i in range(len(CHORD_SPANS) - 1):
            s0 = CHORD_SPANS[i]
            s1 = CHORD_SPANS[i + 1]
            x0 = chord_at_span(s0) * frac
            x1 = chord_at_span(s1) * frac
            msp.add_line((top_x0 + x0 / 2, top_y0 + s0 / 2),
                         (top_x0 + x1 / 2, top_y0 + s1 / 2),
                         dxfattribs={"layer": layer})
        msp.add_text(label, height=2.2, dxfattribs={"layer": "TEXT"}).set_placement(
            (top_x0 + chord_at_span(350) * frac / 2 + 4, top_y0 + 180)
        )

    flap_root = chord_at_span(0) * 0.72 / 2
    flap_te = chord_at_span(0) / 2
    msp.add_text("FLAPS P1-P3", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (top_x0 + (flap_root + flap_te) / 2 - 18, top_y0 + 115)
    )
    msp.add_text("AILERONS P4-P5", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (top_x0 + (flap_root + flap_te) / 2 - 26, top_y0 + 500)
    )

    # Dihedral notes
    for span, note in zip(DIHEDRAL_JOINTS, DIHEDRAL_LABELS):
        msp.add_text(note, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
            (top_x0 + ROOT_CHORD / 2 + 10, top_y0 + span / 2 - 1)
        )

    # Dimensions
    msp.add_linear_dim(base=(top_x0 + ROOT_CHORD / 4, top_y0 - 25),
                       p1=(top_x0, top_y0 - 18),
                       p2=(top_x0 + ROOT_CHORD / 2, top_y0 - 18),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()
    msp.add_linear_dim(base=(top_x0 - 18, top_y0 + HALF_SPAN / 4),
                       p1=(top_x0 - 10, top_y0),
                       p2=(top_x0 - 10, top_y0 + HALF_SPAN / 2),
                       angle=90,
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()

    # Root and tip sections
    msp.add_text("SEC A — ROOT AG24 (1:1)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((sec_x0, sec_y0 + 30))
    msp.add_text("SEC B — TIP AG03 (1:1)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((sec_x0, sec_y0 - 95))

    for cx, cy, chord, thickness in [
        (sec_x0 + 70, sec_y0, ROOT_CHORD, ROOT_CHORD * 0.086),
        (sec_x0 + 70, sec_y0 - 125, TIP_CHORD, TIP_CHORD * 0.064),
    ]:
        a = chord / 2
        b = thickness / 2
        pts = []
        for i in range(91):
            theta = math.pi * i / 90
            x = cx - a + chord * i / 90
            y = cy + b * math.sin(theta)
            pts.append((x, y))
        for i in range(91):
            theta = math.pi * (90 - i) / 90
            x = cx + a - chord * i / 90
            y = cy - b * math.sin(theta)
            pts.append((x, y))
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "OUTLINE"})
        for frac, layer in [(0.25, "SPAR"), (0.60, "SPAR"), (0.72, "CENTERLINE")]:
            sx = cx - a + chord * frac
            msp.add_line((sx, cy - b - 3), (sx, cy + b + 3), dxfattribs={"layer": layer})

    out = ROOT / "cad/assemblies/wing/Wing_Half_Assembly/Wing_Half_Assembly_drawing.dxf"
    return save_dxf_and_png(doc, str(out), dpi=240)


def draw_wing_assembly() -> tuple[str, str]:
    doc = setup_drawing(
        title="Wing_Assembly",
        subtitle="Full wing baseline assembly drawing. Derived from current wing consensus before panel-level redesign.",
        material="Mirror of canonical half-wing assembly across fuselage centerline",
        mass="430g full wing target",
        scale="1:4",
        sheet_size="A1",
        status="FOR ITERATION",
        revision="v0",
        orientation_labels={"fwd": "FWD", "inbd": "CENTER"},
    )
    msp = doc.modelspace()

    top_x0 = 160.0
    top_y0 = 235.0

    msp.add_text("TOP VIEW — FULL WING ASSEMBLY (1:4)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((top_x0 - 45, top_y0 + 85))

    # Draw right and left halves mirrored around centerline
    for sign in (-1, 1):
        pts_le = []
        pts_te = []
        for span in CHORD_SPANS:
            y = top_y0 + sign * span / 4
            le = top_x0
            te = top_x0 + chord_at_span(span) / 4
            pts_le.append((le, y))
            pts_te.append((te, y))
        for i in range(len(pts_le) - 1):
            msp.add_line(pts_le[i], pts_le[i + 1], dxfattribs={"layer": "OUTLINE"})
            msp.add_line(pts_te[i], pts_te[i + 1], dxfattribs={"layer": "OUTLINE"})
        msp.add_line(pts_le[0], pts_te[0], dxfattribs={"layer": "OUTLINE"})
        msp.add_line(pts_le[-1], pts_te[-1], dxfattribs={"layer": "OUTLINE"})
        for idx in range(1, 5):
            s = idx * PANEL_SPAN
            chord = chord_at_span(s)
            msp.add_line((top_x0, top_y0 + sign * s / 4),
                         (top_x0 + chord / 4, top_y0 + sign * s / 4),
                         dxfattribs={"layer": "SECTION"})

    # Centerline
    msp.add_line((top_x0 - 20, top_y0), (top_x0 + ROOT_CHORD / 4 + 20, top_y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Overall dimensions
    msp.add_linear_dim(base=(top_x0 + ROOT_CHORD / 8, top_y0 - 170),
                       p1=(top_x0, top_y0 - 160),
                       p2=(top_x0 + ROOT_CHORD / 4, top_y0 - 160),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()
    msp.add_linear_dim(base=(top_x0 - 80, top_y0),
                       p1=(top_x0 - 68, top_y0 - FULL_SPAN / 8),
                       p2=(top_x0 - 68, top_y0 + FULL_SPAN / 8),
                       angle=90,
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()

    # Callouts
    msp.add_text("P1-P3 FLAP ZONE", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (top_x0 + 30, top_y0 + 90)
    )
    msp.add_text("P4-P5 AILERON ZONE", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (top_x0 + 30, top_y0 + 245)
    )
    msp.add_text("Progressive polyhedral starts at P3/P4", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((top_x0 + 95, top_y0 + 305))
    msp.add_text("This full-wing drawing is the top-down parent for panel decomposition.",
                 height=2.2, dxfattribs={"layer": "TEXT"}).set_placement((95, 72))

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
        revision="v0",
        orientation_labels={"fwd": "FWD", "inbd": "UP"},
    )
    msp = doc.modelspace()

    side_x0 = 45.0
    side_y0 = 430.0
    top_x0 = 45.0
    top_y0 = 270.0
    sec_x0 = 560.0
    sec_y0 = 435.0

    msp.add_text("SIDE VIEW — FUSELAGE ASSEMBLY (1:2)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((side_x0, side_y0 + 95))
    msp.add_text("TOP VIEW — FUSELAGE ASSEMBLY (1:2)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((top_x0, top_y0 + 75))

    # Side and top profile
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

    # Centerlines
    msp.add_line((side_x0 - 10, side_y0), (side_x0 + 540, side_y0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((top_x0 - 10, top_y0), (top_x0 + 540, top_y0),
                 dxfattribs={"layer": "CENTERLINE"})

    # Key stations
    key_stations = [
        (260, "Wing LE"),
        (350, "Servo bay"),
        (650, "Boom/fin blend"),
        (866, "Fin root"),
        (911, "HStab pivot"),
    ]
    for x_mm, label in key_stations:
        x = side_x0 + x_mm / 2
        top = side_y0 + fuselage_dim_at(x_mm, 2) / 4 + 12
        bot = side_y0 - fuselage_dim_at(x_mm, 2) / 4 - 12
        msp.add_line((x, bot), (x, top), dxfattribs={"layer": "SECTION"})
        msp.add_text(label, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
            (x - 8, top + 4)
        )

    # Battery and wing saddle callouts
    msp.add_text("Battery max section at X=150", height=2.4,
                 dxfattribs={"layer": "TEXT"}).set_placement((side_x0 + 62, side_y0 + 40))
    msp.add_text("Wing saddle / spar tunnel at X=260", height=2.4,
                 dxfattribs={"layer": "TEXT"}).set_placement((side_x0 + 130, side_y0 - 56))
    msp.add_text("Integrated fin from X=650-1046", height=2.4,
                 dxfattribs={"layer": "TEXT"}).set_placement((side_x0 + 330, side_y0 + 55))

    # Dimensions
    msp.add_linear_dim(base=(side_x0 + 260, side_y0 - 70),
                       p1=(side_x0, side_y0 - 60),
                       p2=(side_x0 + 1046 / 2, side_y0 - 60),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()
    msp.add_linear_dim(base=(sec_x0 + 20, sec_y0 - 16),
                       p1=(sec_x0, sec_y0 - 10),
                       p2=(sec_x0 + 50, sec_y0 - 10),
                       dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"}).render()

    # Three key sections
    for idx, (x_mm, title) in enumerate([(30, "A — Motor Face"), (150, "B — Max Section"), (260, "C — Wing LE Joint")]):
        cx = sec_x0 + (idx % 2) * 110
        cy = sec_y0 - (idx // 2) * 110
        w = fuselage_dim_at(x_mm, 1)
        h = fuselage_dim_at(x_mm, 2)
        msp.add_text(f"SEC {title}", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement((cx - 28, cy + h / 4 + 18))
        msp.add_ellipse((cx, cy), major_axis=(w / 4, 0), ratio=(h / w) if w else 1.0,
                        dxfattribs={"layer": "OUTLINE"})
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
