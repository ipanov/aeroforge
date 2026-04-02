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
AIRFOIL_DIR = ROOT / "src/cad/airfoils"

HALF_SPAN = 1408.0
FULL_SPAN = 2816.0
PANEL_SPAN = 256.0
ROOT_CHORD = 170.0
TIP_CHORD = 85.0
WING_PLANFORM_N = 2.15
WING_REF_FRAC = 0.43
HSTAB_HALF_SPAN = 223.0
HSTAB_ROOT_CHORD = 118.0
HSTAB_REF_FRAC = 0.45
HSTAB_REF_X = HSTAB_ROOT_CHORD * HSTAB_REF_FRAC
HSTAB_TE_FRAC = 0.97
HSTAB_SUPERELLIPSE_N = 2.3
HSTAB_ROOT_LE = 893.0
FUSELAGE_LENGTH = 1088.0
FIN_HEIGHT = 170.0
FIN_ROOT_CHORD = 116.0
FIN_TIP_CHORD = 44.0
FIN_PLANFORM_N = 1.95
FIN_REF_FRAC = 0.45
FIN_ROOT_LE = 938.0
FIN_ROOT_REF_X = FIN_ROOT_LE + FIN_REF_FRAC * FIN_ROOT_CHORD

CHORD_SPANS = [0, 256, 512, 768, 1024, 1280, 1408]
CHORD_VALUES = [170, 161, 150, 137, 122, 99, 85]
PANEL_NAMES = ["P1", "P2", "P3", "P4", "P5", "P6"]
POLYHEDRAL_LABELS = ["0.0°", "0.0°", "1.0°", "2.0°", "3.5°", "5.0°"]
FUSELAGE_GAP = 38.0
MAIN_SPAR_FRAC = 0.25
REAR_SPAR_FRAC = 0.60
HINGE_FRAC = 0.72
MAIN_SPAR_HALF_LEN = 1152.0
MAIN_SPAR_TIP_LEN = 256.0
REAR_SPAR_HALF_LEN = 1152.0
FLAP_END = 768.0
AILERON_START = 768.0
SERVO_STATIONS = [
    ("FLAP SERVO P1", 128.0, 0.35, 23.0, 11.0),
    ("FLAP SERVO P3", 640.0, 0.35, 23.0, 11.0),
    ("AILERON SERVO P4", 928.0, 0.35, 20.0, 10.0),
    ("AILERON SERVO P5", 1184.0, 0.30, 20.0, 10.0),
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
    (760, 11.0, 18.0),
    (888, 9.0, 176.0),
    (946, 7.5, 156.0),
    (1036, 3.0, 48.0),
    (1088, 0, 0),
]

FUSELAGE_PLAN_HALF = [
    (0, 0.0),
    (12, 5.5),
    (30, 16.0),
    (55, 17.5),
    (90, 21.5),
    (130, 23.8),
    (170, 24.8),
    (210, 24.2),
    (245, 22.4),
    (280, 19.8),
    (320, 16.8),
    (380, 13.6),
    (460, 10.5),
    (560, 8.2),
    (700, 6.3),
    (820, 5.0),
    (900, 4.1),
    (980, 3.4),
    (1060, 2.0),
    (1088, 0.0),
]

FUSELAGE_SIDE_BODY_TOP = [
    (0, 0.0),
    (12, 8.0),
    (30, 16.0),
    (55, 17.5),
    (90, 21.0),
    (150, 22.0),
    (210, 20.0),
    (260, 17.0),
    (320, 15.0),
    (350, 13.0),
    (430, 10.0),
    (500, 8.0),
    (650, 6.5),
    (760, 5.8),
    (840, 5.0),
    (888, 4.5),
    (946, 3.9),
    (1036, 2.2),
    (1088, 0.0),
]

FUSELAGE_SIDE_BODY_BOTTOM = [
    (0, 0.0),
    (12, -8.0),
    (30, -16.0),
    (55, -17.5),
    (90, -21.0),
    (150, -22.0),
    (210, -20.5),
    (260, -17.0),
    (320, -15.5),
    (350, -14.0),
    (430, -11.0),
    (500, -8.0),
    (650, -6.5),
    (760, -5.8),
    (840, -5.0),
    (888, -4.5),
    (946, -3.9),
    (1036, -2.2),
    (1088, 0.0),
]

WING_STATIONS = [
    ("WING LE", 260.0),
    ("SPAR TUNNEL", 280.0),
    ("SERVO BAY", 350.0),
    ("BOOM BLEND", 650.0),
    ("FIN ROOT", 888.0),
    ("HSTAB C/4", 946.0),
]

COMPONENT_LAYOUT = {
    "spinner": {"x": 0.0, "length": 28.0, "width": 30.0, "height": 30.0, "y": 0.0, "z": 0.0, "label": "30 SPINNER"},
    "motor": {"x": 30.0, "length": 42.5, "width": 27.5, "height": 27.5, "y": 0.0, "z": 0.0, "label": "X2216 MOTOR"},
    "esc": {"x": 76.0, "length": 44.0, "width": 24.0, "height": 11.0, "y": 10.0, "z": -5.0, "label": "30A ESC"},
    "xt60": {"x": 118.0, "length": 20.0, "width": 16.0, "height": 12.0, "y": 0.0, "z": 3.0, "label": "XT60"},
    "battery": {"x": 102.0, "length": 78.0, "width": 38.0, "height": 28.0, "y": 0.0, "z": 0.0, "label": "3S 1300 BAT / SLIDE"},
    "receiver": {"x": 265.0, "length": 47.2, "width": 26.2, "height": 15.0, "y": -8.0, "z": -2.0, "label": "FS-iA6B RX"},
    "wing_carry": {"x": 254.0, "length": 62.0, "width": 32.0, "height": 22.0, "y": 0.0, "z": 0.0, "label": "SPAR / BOLT"},
    "elev_servo": {"x": 330.0, "length": 23.2, "width": 12.5, "height": 25.4, "y": -8.0, "z": 3.0, "label": "ELEV SERVO"},
    "rudd_servo": {"x": 330.0, "length": 23.2, "width": 12.5, "height": 25.4, "y": 8.0, "z": -8.0, "label": "RUDD SERVO"},
}

_AIRFOIL_CACHE: dict[str, list[tuple[float, float]]] = {}


def chord_at_span(span_mm: float) -> float:
    return wing_superellipse_chord(span_mm)


def superellipse_family_chord(span_mm: float, total_span: float, root_chord: float, tip_chord: float, exponent: float) -> float:
    eta = max(0.0, min(1.0, span_mm / total_span))
    return tip_chord + (root_chord - tip_chord) * (1.0 - eta**exponent) ** (1.0 / exponent)


def wing_superellipse_chord(span_mm: float) -> float:
    return superellipse_family_chord(span_mm, HALF_SPAN, ROOT_CHORD, TIP_CHORD, WING_PLANFORM_N)


def wing_le_at_span(span_mm: float) -> float:
    chord = wing_superellipse_chord(span_mm)
    return WING_REF_FRAC * (ROOT_CHORD - chord)


def wing_te_at_span(span_mm: float) -> float:
    return wing_le_at_span(span_mm) + wing_superellipse_chord(span_mm)


def hstab_superellipse_chord(span_mm: float) -> float:
    eta = max(0.0, min(1.0, span_mm / HSTAB_HALF_SPAN))
    if eta >= 1.0:
        return 0.0
    return HSTAB_ROOT_CHORD * (1.0 - eta**HSTAB_SUPERELLIPSE_N) ** (1.0 / HSTAB_SUPERELLIPSE_N)


def fin_superellipse_chord(height_mm: float) -> float:
    return superellipse_family_chord(height_mm, FIN_HEIGHT, FIN_ROOT_CHORD, FIN_TIP_CHORD, FIN_PLANFORM_N)


def fin_le_at_height(height_mm: float) -> float:
    chord = fin_superellipse_chord(height_mm)
    return FIN_ROOT_REF_X - FIN_REF_FRAC * chord


def fin_te_at_height(height_mm: float) -> float:
    return fin_le_at_height(height_mm) + fin_superellipse_chord(height_mm)


def rudder_hinge_at_height(height_mm: float) -> float:
    eta = max(0.0, min(1.0, height_mm / FIN_HEIGHT))
    chord = fin_superellipse_chord(height_mm)
    hinge_frac = 0.73 + 0.03 * eta
    return fin_le_at_height(height_mm) + hinge_frac * chord


def hstab_attach_station_x() -> float:
    return HSTAB_ROOT_LE + HSTAB_ROOT_CHORD * 0.36


def hstab_attach_height_mm() -> float:
    return schedule_value(FUSELAGE_SIDE_BODY_TOP, HSTAB_ROOT_LE) + FIN_HEIGHT * 0.38


def load_airfoil_points(name: str) -> list[tuple[float, float]]:
    key = name.lower()
    if key in _AIRFOIL_CACHE:
        return _AIRFOIL_CACHE[key]
    path = AIRFOIL_DIR / f"{key}.dat"
    pts: list[tuple[float, float]] = []
    if path.exists():
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            parts = raw.strip().split()
            if len(parts) < 2:
                continue
            try:
                x = float(parts[0])
                y = float(parts[1])
            except ValueError:
                continue
            pts.append((x, y))
    _AIRFOIL_CACHE[key] = pts
    return pts


def wing_thickness_at_span(span_mm: float) -> float:
    frac = span_mm / HALF_SPAN
    thickness_ratio = 0.078 + frac * (0.058 - 0.078)
    return wing_superellipse_chord(span_mm) * thickness_ratio


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


def schedule_value(schedule: list[tuple[float, float]], x_mm: float) -> float:
    for idx in range(len(schedule) - 1):
        x0, y0 = schedule[idx]
        x1, y1 = schedule[idx + 1]
        if x0 <= x_mm <= x1:
            t = 0.0 if x1 == x0 else (x_mm - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return schedule[-1][1]


def schedule_points(schedule: list[tuple[float, float]], x0: float, y0: float, scale: float) -> list[tuple[float, float]]:
    return [(x0 + x_mm * scale, y0 + y_mm * scale) for x_mm, y_mm in schedule]


def add_open_polyline(msp, points: list[tuple[float, float]], layer: str = "OUTLINE") -> None:
    if len(points) >= 2:
        msp.add_lwpolyline(points, dxfattribs={"layer": layer})


def add_rect_outline(msp, x1: float, y1: float, x2: float, y2: float, layer: str) -> None:
    msp.add_line((x1, y1), (x2, y1), dxfattribs={"layer": layer})
    msp.add_line((x2, y1), (x2, y2), dxfattribs={"layer": layer})
    msp.add_line((x2, y2), (x1, y2), dxfattribs={"layer": layer})
    msp.add_line((x1, y2), (x1, y1), dxfattribs={"layer": layer})


def add_tip_cap(msp, x_tip: float, y_upper: float, y_lower: float, direction: int, layer: str = "OUTLINE") -> None:
    radius = max(abs(y_upper - y_lower) * 0.38, 2.0)
    cy = (y_upper + y_lower) / 2
    points = []
    for idx in range(9):
        theta = -math.pi / 2 + idx * math.pi / 8
        px = x_tip + direction * radius * math.cos(theta)
        py = cy + (y_upper - y_lower) * 0.5 * math.sin(theta)
        points.append((px, py))
    add_open_polyline(msp, points, layer=layer)


def add_component_envelope_top(msp, x0: float, y0: float, scale: float, item: dict[str, float | str]) -> None:
    x_start = x0 + float(item["x"]) * scale
    x_end = x0 + (float(item["x"]) + float(item["length"])) * scale
    half_w = float(item["width"]) * scale / 2
    cy = y0 + float(item["y"]) * scale
    add_rect_outline(msp, x_start, cy - half_w, x_end, cy + half_w, "HIDDEN")
    msp.add_text(str(item["label"]), height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((x_start + 1.5, cy + half_w + 2.0))


def add_component_envelope_side(msp, x0: float, y0: float, scale: float, item: dict[str, float | str]) -> None:
    x_start = x0 + float(item["x"]) * scale
    x_end = x0 + (float(item["x"]) + float(item["length"])) * scale
    half_h = float(item["height"]) * scale / 2
    cy = y0 + float(item["z"]) * scale
    add_rect_outline(msp, x_start, cy - half_h, x_end, cy + half_h, "HIDDEN")
    msp.add_text(str(item["label"]), height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((x_start + 1.5, cy + half_h + 2.0))


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


def add_airfoil_outline_from_dat(
    msp,
    x_le: float,
    cy: float,
    chord: float,
    airfoil_name: str,
    rotation_deg: float = 0.0,
    layer: str = "OUTLINE",
) -> None:
    pts = load_airfoil_points(airfoil_name)
    if not pts:
        add_airfoil_outline(msp, x_le + chord / 2, cy, chord, chord * 0.065, layer=layer)
        return
    qcx = x_le + 0.25 * chord
    rad = math.radians(rotation_deg)
    out: list[tuple[float, float]] = []
    for x_n, y_n in pts:
        px = x_le + x_n * chord
        py = cy + y_n * chord
        dx = px - qcx
        dy = py - cy
        rx = qcx + dx * math.cos(rad) - dy * math.sin(rad)
        ry = cy + dx * math.sin(rad) + dy * math.cos(rad)
        out.append((rx, ry))
    msp.add_lwpolyline(out, close=True, dxfattribs={"layer": layer})


def add_fuselage_top_outline(msp, x0: float, y0: float, scale: float, include_centerline: bool = True) -> None:
    upper = schedule_points(FUSELAGE_PLAN_HALF, x0, y0, scale)
    lower = schedule_points([(x, -y) for x, y in FUSELAGE_PLAN_HALF], x0, y0, scale)
    add_open_polyline(msp, upper)
    add_open_polyline(msp, lower)
    if include_centerline:
        msp.add_line((x0 - 10, y0), (x0 + (FUSELAGE_LENGTH + 14) * scale, y0), dxfattribs={"layer": "CENTERLINE"})


def add_fuselage_top_outline_horizontal(msp, x0: float, y0: float, scale: float, include_centerline: bool = True) -> None:
    right = [(x0 + half_w * scale, y0 + x_mm * scale) for x_mm, half_w in FUSELAGE_PLAN_HALF]
    left = [(x0 - half_w * scale, y0 + x_mm * scale) for x_mm, half_w in FUSELAGE_PLAN_HALF]
    add_open_polyline(msp, left[::-1] + right)
    if include_centerline:
        msp.add_line((x0, y0 - 10), (x0, y0 + (FUSELAGE_LENGTH + 14) * scale), dxfattribs={"layer": "CENTERLINE"})


def add_fuselage_side_outline(msp, x0: float, y0: float, scale: float, include_centerline: bool = True) -> None:
    blend_start_x = FIN_ROOT_LE - 68.0
    top_pts = [(x0 + x_mm * scale, y0 + y_mm * scale) for x_mm, y_mm in FUSELAGE_SIDE_BODY_TOP if x_mm <= blend_start_x]
    bot_pts = schedule_points(FUSELAGE_SIDE_BODY_BOTTOM, x0, y0, scale)
    add_open_polyline(msp, top_pts)
    add_open_polyline(msp, bot_pts)
    fin_base = schedule_value(FUSELAGE_SIDE_BODY_TOP, FIN_ROOT_LE)
    exposed_base = fin_base + 5.5
    le_blend = [
        (x0 + blend_start_x * scale, y0 + schedule_value(FUSELAGE_SIDE_BODY_TOP, blend_start_x) * scale),
        (x0 + (FIN_ROOT_LE - 36.0) * scale, y0 + (fin_base + 2.4) * scale),
        (x0 + FIN_ROOT_LE * scale, y0 + exposed_base * scale),
    ]
    te_blend = [
        (x0 + fin_te_at_height(0.0) * scale, y0 + exposed_base * scale),
        (x0 + (FIN_ROOT_LE + FIN_ROOT_CHORD * 0.92) * scale, y0 + (fin_base + 2.0) * scale),
        (x0 + FUSELAGE_LENGTH * scale, y0),
    ]
    add_open_polyline(msp, le_blend)
    add_open_polyline(msp, te_blend)
    fin_le = []
    fin_te = []
    fin_base_le = x0 + fin_le_at_height(0.0) * scale
    fin_base_te = x0 + fin_te_at_height(0.0) * scale
    for idx in range(17):
        z_mm = FIN_HEIGHT * idx / 16
        y_fin = y0 + (exposed_base + z_mm) * scale
        fin_te.append((x0 + fin_te_at_height(z_mm) * scale, y_fin))
        fin_le.append((x0 + fin_le_at_height(z_mm) * scale, y_fin))
    hinge_root_x = fin_base_le + 0.75 * (fin_base_te - fin_base_le)
    hinge_tip_x = x0 + rudder_hinge_at_height(FIN_HEIGHT) * scale
    add_open_polyline(msp, fin_le + fin_te[::-1])
    msp.add_line((hinge_root_x, y0 + exposed_base * scale), (hinge_tip_x, y0 + (exposed_base + FIN_HEIGHT) * scale), dxfattribs={"layer": "CENTERLINE"})
    if include_centerline:
        msp.add_line((x0 - 10, y0), (x0 + (FUSELAGE_LENGTH + 14) * scale, y0), dxfattribs={"layer": "CENTERLINE"})


def add_hstab_attach_marker_side(msp, x0: float, y0: float, scale: float, label_offset: float = 0.0) -> None:
    attach_x = x0 + hstab_attach_station_x() * scale
    attach_y = y0 + hstab_attach_height_mm() * scale
    x_le = x0 + HSTAB_ROOT_LE * scale
    add_airfoil_outline_from_dat(msp, x_le, attach_y, HSTAB_ROOT_CHORD * scale, "ht13", layer="OUTLINE")
    add_rect_outline(msp, attach_x - 6.5 * scale, attach_y - 2.6 * scale, attach_x + 6.5 * scale, attach_y + 2.6 * scale, "HIDDEN")
    msp.add_text("HSTAB ROOT / ATTACH", height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((attach_x + 10, attach_y + 6 + label_offset))


def add_installation_envelopes_top(msp, x0: float, y0: float, scale: float, include_prop_disk: bool = False) -> None:
    for key in ["battery", "xt60", "esc", "receiver", "wing_carry", "elev_servo", "rudd_servo"]:
        add_component_envelope_top(msp, x0, y0, scale, COMPONENT_LAYOUT[key])
    if include_prop_disk:
        msp.add_circle((x0 + 12 * scale, y0), radius=139.5 * scale, dxfattribs={"layer": "HIDDEN"})
        msp.add_text("11x6 FOLDING PROP DISK", height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((x0 + 24 * scale, y0 + 143 * scale))


def add_installation_envelopes_side(msp, x0: float, y0: float, scale: float, include_prop_disk: bool = False) -> None:
    for key in ["spinner", "motor", "battery", "xt60", "esc", "receiver", "wing_carry", "elev_servo", "rudd_servo"]:
        add_component_envelope_side(msp, x0, y0, scale, COMPONENT_LAYOUT[key])

    for x_mm in [350.0, 420.0, 500.0, 650.0, FIN_ROOT_LE]:
        xt = x0 + x_mm * scale
        yt = y0 + schedule_value(FUSELAGE_SIDE_BODY_TOP, x_mm) * scale
        yb = y0 + schedule_value(FUSELAGE_SIDE_BODY_BOTTOM, x_mm) * scale
        msp.add_line((xt, yb), (xt, yt), dxfattribs={"layer": "HIDDEN"})
    if include_prop_disk:
        msp.add_circle((x0 + 12 * scale, y0), radius=139.5 * scale, dxfattribs={"layer": "HIDDEN"})


def add_hstab_top_view(msp, x0: float, y0: float, scale: float) -> None:
    half_span = HSTAB_HALF_SPAN
    root_le = HSTAB_ROOT_LE
    left_le: list[tuple[float, float]] = []
    left_te: list[tuple[float, float]] = []
    right_le: list[tuple[float, float]] = []
    right_te: list[tuple[float, float]] = []

    for idx in range(17):
        y_local = half_span * idx / 16
        chord = hstab_superellipse_chord(y_local)
        x_le = HSTAB_REF_X - HSTAB_REF_FRAC * chord
        x_te = HSTAB_REF_X + (1.0 - HSTAB_REF_FRAC) * chord * HSTAB_TE_FRAC
        left_le.append((x0 + (root_le + x_le) * scale, y0 + y_local * scale))
        left_te.append((x0 + (root_le + x_te) * scale, y0 + y_local * scale))
        if idx > 0:
            right_le.append((x0 + (root_le + x_le) * scale, y0 - y_local * scale))
            right_te.append((x0 + (root_le + x_te) * scale, y0 - y_local * scale))

    add_open_polyline(msp, right_le[::-1] + left_le)
    add_open_polyline(msp, right_te[::-1] + left_te)

    hinge_x = x0 + (root_le + 60.0) * scale
    msp.add_line((hinge_x, y0 - (half_span - 3) * scale), (hinge_x, y0 + (half_span - 3) * scale), dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("HSTAB 446 span | area ~4.21 dm^2", height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((x0 + (root_le + 10) * scale, y0 + (half_span + 10) * scale))


def add_hstab_top_view_horizontal(msp, x0: float, y0: float, scale: float) -> None:
    half_span = HSTAB_HALF_SPAN
    root_le = HSTAB_ROOT_LE
    right_le: list[tuple[float, float]] = []
    right_te: list[tuple[float, float]] = []
    left_le: list[tuple[float, float]] = []
    left_te: list[tuple[float, float]] = []

    for idx in range(17):
        y_local = half_span * idx / 16
        chord = hstab_superellipse_chord(y_local)
        x_le = HSTAB_REF_X - HSTAB_REF_FRAC * chord
        x_te = HSTAB_REF_X + (1.0 - HSTAB_REF_FRAC) * chord * HSTAB_TE_FRAC
        right_le.append((x0 + y_local * scale, y0 + (root_le + x_le) * scale))
        right_te.append((x0 + y_local * scale, y0 + (root_le + x_te) * scale))
        if idx > 0:
            left_le.append((x0 - y_local * scale, y0 + (root_le + x_le) * scale))
            left_te.append((x0 - y_local * scale, y0 + (root_le + x_te) * scale))

    add_open_polyline(msp, left_le[::-1] + right_le)
    add_open_polyline(msp, left_te[::-1] + right_te)
    tip_chord = hstab_superellipse_chord(half_span - 4.0)
    tip_y_upper = y0 + (root_le + HSTAB_REF_X - HSTAB_REF_FRAC * tip_chord) * scale
    tip_y_lower = y0 + (root_le + HSTAB_REF_X + (1.0 - HSTAB_REF_FRAC) * tip_chord * HSTAB_TE_FRAC) * scale
    add_tip_cap(msp, x0 + half_span * scale, tip_y_upper, tip_y_lower, 1)
    add_tip_cap(msp, x0 - half_span * scale, tip_y_upper, tip_y_lower, -1)
    hinge_y = y0 + (root_le + 60.0) * scale
    msp.add_line((x0 - (half_span - 3) * scale, hinge_y), (x0 + (half_span - 3) * scale, hinge_y), dxfattribs={"layer": "CENTERLINE"})


def add_aircraft_wing_planform_vertical(
    msp,
    x0: float,
    y0: float,
    scale: float,
    wing_le_station: float = 260.0,
    show_right_servos: bool = True,
) -> None:
    semigap = FUSELAGE_GAP / 2

    right_le = []
    right_te = []
    left_le = []
    left_te = []
    for span_mm in CHORD_SPANS:
        y_span = semigap + span_mm
        right_le.append((x0 + (wing_le_station + wing_le_at_span(span_mm)) * scale, y0 + y_span * scale))
        right_te.append((x0 + (wing_le_station + wing_te_at_span(span_mm)) * scale, y0 + y_span * scale))
        left_le.append((x0 + (wing_le_station + wing_le_at_span(span_mm)) * scale, y0 - y_span * scale))
        left_te.append((x0 + (wing_le_station + wing_te_at_span(span_mm)) * scale, y0 - y_span * scale))

    add_open_polyline(msp, left_le[::-1] + right_le)
    add_open_polyline(msp, left_te[::-1] + right_te)
    root_te = wing_le_station + wing_te_at_span(0)
    msp.add_line((x0 + wing_le_station * scale, y0 - semigap * scale), (x0 + root_te * scale, y0 - semigap * scale), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((x0 + wing_le_station * scale, y0 + semigap * scale), (x0 + root_te * scale, y0 + semigap * scale), dxfattribs={"layer": "OUTLINE"})

    for frac, layer, span_limit in [
        (MAIN_SPAR_FRAC, "SPAR", MAIN_SPAR_HALF_LEN),
        (REAR_SPAR_FRAC, "SPAR", REAR_SPAR_HALF_LEN),
        (HINGE_FRAC, "CENTERLINE", HALF_SPAN),
    ]:
        right_pts = []
        left_pts = []
        for span_mm in CHORD_SPANS:
            if span_mm > span_limit:
                continue
            chord = wing_superellipse_chord(span_mm)
            x_mm = wing_le_station + wing_le_at_span(span_mm) + chord * frac
            y_span = semigap + span_mm
            right_pts.append((x0 + x_mm * scale, y0 + y_span * scale))
            left_pts.append((x0 + x_mm * scale, y0 - y_span * scale))
        add_open_polyline(msp, left_pts[::-1] + right_pts, layer=layer)

    for span_mm, label in [(256.0, "P2"), (512.0, "P3"), (768.0, "P4"), (1024.0, "P5"), (1280.0, "P6")]:
        x_le = wing_le_station + wing_le_at_span(span_mm)
        x_te = wing_le_station + wing_te_at_span(span_mm)
        y_right = y0 + (semigap + span_mm) * scale
        y_left = y0 - (semigap + span_mm) * scale
        msp.add_line((x0 + x_le * scale, y_right), (x0 + x_te * scale, y_right), dxfattribs={"layer": "SECTION"})
        msp.add_line((x0 + x_le * scale, y_left), (x0 + x_te * scale, y_left), dxfattribs={"layer": "SECTION"})
        msp.add_text(label, height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((x0 + (x_te + 8) * scale, y_right - 2))

    if show_right_servos:
        for label, station, frac, length_mm, width_mm in SERVO_STATIONS:
            chord = wing_superellipse_chord(station)
            x_mid = wing_le_station + wing_le_at_span(station) + frac * chord
            y_mid = semigap + station
            add_rect_outline(
                msp,
                x0 + (x_mid - length_mm / 2) * scale,
                y0 + (y_mid - width_mm / 2) * scale,
                x0 + (x_mid + length_mm / 2) * scale,
                y0 + (y_mid + width_mm / 2) * scale,
                "HIDDEN",
            )
            msp.add_text(label, height=1.4, dxfattribs={"layer": "TEXT"}).set_placement((x0 + (x_mid + 5) * scale, y0 + (y_mid + 4) * scale))

    msp.add_text("Wing LE @ X=260", height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((x0 + (wing_le_station - 20) * scale, y0 + (semigap + 90) * scale))
    msp.add_text("Right-half servo envelopes shown", height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((x0 + 335 * scale, y0 + 490 * scale))


def add_aircraft_wing_planform_horizontal(
    msp,
    x0: float,
    y0: float,
    scale: float,
    wing_le_station: float = 260.0,
    show_upper_servos: bool = True,
) -> None:
    semigap = FUSELAGE_GAP / 2
    upper_le = []
    upper_te = []
    lower_le = []
    lower_te = []
    for span_mm in CHORD_SPANS:
        x_span = semigap + span_mm
        chord = wing_superellipse_chord(span_mm)
        le = wing_le_station + wing_le_at_span(span_mm)
        te = wing_le_station + wing_te_at_span(span_mm)
        upper_le.append((x0 + x_span * scale, y0 + le * scale))
        upper_te.append((x0 + x_span * scale, y0 + te * scale))
        lower_le.append((x0 - x_span * scale, y0 + le * scale))
        lower_te.append((x0 - x_span * scale, y0 + te * scale))

    add_open_polyline(msp, lower_le[::-1] + upper_le)
    add_open_polyline(msp, lower_te[::-1] + upper_te)
    root_te = wing_le_station + wing_te_at_span(0)
    msp.add_line((x0 - semigap * scale, y0 + wing_le_station * scale), (x0 - semigap * scale, y0 + root_te * scale), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((x0 + semigap * scale, y0 + wing_le_station * scale), (x0 + semigap * scale, y0 + root_te * scale), dxfattribs={"layer": "OUTLINE"})
    tip_upper = y0 + (wing_le_station + wing_le_at_span(HALF_SPAN)) * scale
    tip_lower = y0 + (wing_le_station + wing_te_at_span(HALF_SPAN)) * scale
    add_tip_cap(msp, x0 + (semigap + HALF_SPAN) * scale, tip_upper, tip_lower, 1)
    add_tip_cap(msp, x0 - (semigap + HALF_SPAN) * scale, tip_upper, tip_lower, -1)

    sample_spans = [i * HALF_SPAN / 20 for i in range(21)]
    for frac, layer, span_limit in [
        (MAIN_SPAR_FRAC, "SPAR", MAIN_SPAR_HALF_LEN),
        (REAR_SPAR_FRAC, "SPAR", REAR_SPAR_HALF_LEN),
        (HINGE_FRAC, "CENTERLINE", HALF_SPAN),
    ]:
        pts = []
        for span_mm in sample_spans:
            if span_mm > span_limit:
                continue
            chord = wing_superellipse_chord(span_mm)
            x_span = semigap + span_mm
            y_line = wing_le_station + wing_le_at_span(span_mm) + chord * frac
            pts.append((x0 + x_span * scale, y0 + y_line * scale))
        mirror = [(2 * x0 - px, py) for px, py in pts[::-1]]
        add_open_polyline(msp, mirror + pts, layer=layer)

    for span_mm, label in [(256.0, "P2"), (512.0, "P3"), (768.0, "P4"), (1024.0, "P5"), (1280.0, "P6")]:
        x_span = semigap + span_mm
        le = wing_le_station + wing_le_at_span(span_mm)
        te = wing_le_station + wing_te_at_span(span_mm)
        msp.add_line((x0 + x_span * scale, y0 + le * scale), (x0 + x_span * scale, y0 + te * scale), dxfattribs={"layer": "SECTION"})
        msp.add_line((x0 - x_span * scale, y0 + le * scale), (x0 - x_span * scale, y0 + te * scale), dxfattribs={"layer": "SECTION"})
        msp.add_text(label, height=1.4, dxfattribs={"layer": "TEXT"}).set_placement((x0 + x_span * scale + 3, y0 + le * scale - 4))

    if show_upper_servos:
        for label, station, frac, width_mm, depth_mm in SERVO_STATIONS:
            x_span = semigap + station
            chord = wing_superellipse_chord(station)
            y_mid = wing_le_station + wing_le_at_span(station) + frac * chord
            add_rect_outline(
                msp,
                x0 + (x_span - width_mm / 2) * scale,
                y0 + (y_mid - depth_mm / 2) * scale,
                x0 + (x_span + width_mm / 2) * scale,
                y0 + (y_mid + depth_mm / 2) * scale,
                "HIDDEN",
            )
            msp.add_text(label, height=1.2, dxfattribs={"layer": "TEXT"}).set_placement((x0 + (x_span + 6) * scale, y0 + (y_mid + 4) * scale))


def _draw_single_half_top_view(msp, x_root: float, y_le: float, scale: float, direction: int, show_servos: bool) -> None:
    """Draw one wing half in plan view with span horizontal."""
    outline_spans = [i * HALF_SPAN / 32 for i in range(33)]
    y_ref = y_le - WING_REF_FRAC * ROOT_CHORD * scale
    last_le = None
    last_te = None
    for i, s in enumerate(outline_spans):
        chord = wing_superellipse_chord(s)
        xx = x_root + direction * s * scale
        local_le_y = y_ref + WING_REF_FRAC * chord * scale
        le = (xx, local_le_y)
        te = (xx, local_le_y - chord * scale)
        if i > 0:
            msp.add_line(last_le, le, dxfattribs={"layer": "OUTLINE"})
            msp.add_line(last_te, te, dxfattribs={"layer": "OUTLINE"})
        last_le = le
        last_te = te

    tip_x = x_root + direction * HALF_SPAN * scale
    tip_le_y = y_ref + WING_REF_FRAC * TIP_CHORD * scale
    tip_te_y = tip_le_y - TIP_CHORD * scale
    msp.add_line((x_root, y_le), (x_root, y_le - ROOT_CHORD * scale), dxfattribs={"layer": "OUTLINE"})
    add_tip_cap(msp, tip_x, tip_le_y, tip_te_y, direction)

    for idx in range(1, 6):
        s = idx * PANEL_SPAN
        xx = x_root + direction * s * scale
        chord = wing_superellipse_chord(s)
        local_le_y = y_ref + WING_REF_FRAC * chord * scale
        msp.add_line((xx, local_le_y), (xx, local_le_y - chord * scale), dxfattribs={"layer": "SECTION"})
        label_x = xx - 12 if direction > 0 else xx + 4
        msp.add_text(PANEL_NAMES[idx - 1], height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((label_x, local_le_y - 9))
    tip_label_x = tip_x - 18 if direction > 0 else tip_x + 4
    msp.add_text("TIP", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((tip_label_x, tip_le_y - 9))

    for frac, layer, end_span in [
        (MAIN_SPAR_FRAC, "SPAR", MAIN_SPAR_HALF_LEN),
        (REAR_SPAR_FRAC, "SPAR", REAR_SPAR_HALF_LEN),
        (HINGE_FRAC, "CENTERLINE", HALF_SPAN),
    ]:
        pts = []
        for s in outline_spans:
            if s > end_span:
                continue
            xx = x_root + direction * s * scale
            chord = wing_superellipse_chord(s)
            local_le_y = y_ref + WING_REF_FRAC * chord * scale
            yy = local_le_y - chord * frac * scale
            pts.append((xx, yy))
        for i in range(len(pts) - 1):
            msp.add_line(pts[i], pts[i + 1], dxfattribs={"layer": layer})

    pts = []
    for s in [1152.0, 1280.0, 1344.0, 1408.0]:
        xx = x_root + direction * s * scale
        chord = wing_superellipse_chord(s)
        local_le_y = y_ref + WING_REF_FRAC * chord * scale
        yy = local_le_y - chord * 0.27 * scale
        pts.append((xx, yy))
    for i in range(len(pts) - 1):
        msp.add_line(pts[i], pts[i + 1], dxfattribs={"layer": "SPAR"})

    for start, end, text in [(0.0, FLAP_END, "FLAP"), (AILERON_START, HALF_SPAN, "AILERON")]:
        x1 = x_root + direction * start * scale
        x2 = x_root + direction * end * scale
        chord1 = wing_superellipse_chord(start)
        chord2 = wing_superellipse_chord(end)
        le1 = y_ref + WING_REF_FRAC * chord1 * scale
        le2 = y_ref + WING_REF_FRAC * chord2 * scale
        y1 = le1 - chord1 * HINGE_FRAC * scale
        y2 = le2 - chord2 * HINGE_FRAC * scale
        msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "CENTERLINE"})
        tx = (x1 + x2) / 2
        ty = (y1 + y2) / 2 - 12
        msp.add_text(text, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((tx - 8, ty))

    if show_servos:
        for label, station, frac, w, h in SERVO_STATIONS:
            chord = wing_superellipse_chord(station)
            cx = x_root + direction * station * scale
            local_le_y = y_ref + WING_REF_FRAC * chord * scale
            cy = local_le_y - chord * frac * scale
            hw = (w * scale) / 2
            hh = (h * scale) / 2
            add_rect_outline(msp, cx - hw, cy - hh, cx + hw, cy + hh, "HIDDEN")
            msp.add_text(label, height=1.5, dxfattribs={"layer": "TEXT"}).set_placement((cx - 10, cy + 4))


def add_wing_top_view_at_roots(
    msp,
    x_root_left: float,
    x_root_right: float,
    y_le: float,
    scale: float,
    show_right_servos: bool = False,
) -> tuple[float, float]:
    _draw_single_half_top_view(msp, x_root_left, y_le, scale, -1, False)
    _draw_single_half_top_view(msp, x_root_right, y_le, scale, +1, show_right_servos)
    msp.add_line((x_root_left, y_le + 10), (x_root_left, y_le - ROOT_CHORD * scale - 10), dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((x_root_right, y_le + 10), (x_root_right, y_le - ROOT_CHORD * scale - 10), dxfattribs={"layer": "CENTERLINE"})
    return x_root_left, x_root_right


def add_wing_top_view(msp, x0: float, y_le: float, scale: float, full: bool) -> tuple[float, float]:
    """Return (x_root_left, x_root_right) for gap-related annotations."""
    if full:
        x_root_left = x0 + HALF_SPAN * scale
        x_root_right = x_root_left + FUSELAGE_GAP * scale
        return add_wing_top_view_at_roots(msp, x_root_left, x_root_right, y_le, scale, show_right_servos=True)
    x_root = x0
    _draw_single_half_top_view(msp, x_root, y_le, scale, +1, True)
    return x_root, x_root


def add_wing_front_view(msp, x0: float, y0: float, scale: float, full: bool) -> tuple[float, float]:
    half_pts = [
        (0, 0),
        (256, 0),
        (512, 0),
        (768, 3),
        (1024, 9),
        (1280, 17),
        (1408, 22),
    ]
    gap_half = (FUSELAGE_GAP / 2) * scale if full else 0.0
    if full:
        pts = [(-gap_half - x * scale, y0 + y * scale) for x, y in half_pts[::-1]]
        pts += [(gap_half + x * scale, y0 + y * scale) for x, y in half_pts]
        mapped = [(x0 + x, y) for x, y in pts]
    else:
        mapped = [(x0 + x * scale, y0 + y * scale) for x, y in half_pts]
    for i in range(len(mapped) - 1):
        msp.add_line(mapped[i], mapped[i + 1], dxfattribs={"layer": "OUTLINE"})
    for idx, (x, y) in enumerate(half_pts):
        mx = x0 + (gap_half + x * scale if full else x * scale)
        msp.add_line((mx, y0 - 10), (mx, y0 + y * scale + 8), dxfattribs={"layer": "SECTION"})
        if idx < len(POLYHEDRAL_LABELS):
            msp.add_text(POLYHEDRAL_LABELS[idx], height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((mx + 2, y0 + y * scale + 10))
        if full and x != 0:
            mmx = x0 - (gap_half + x * scale)
            msp.add_line((mmx, y0 - 10), (mmx, y0 + y * scale + 8), dxfattribs={"layer": "SECTION"})
    return x0 - gap_half, x0 + gap_half


def add_wing_side_view(msp, x0: float, y0: float, scale: float) -> None:
    root_t = wing_thickness_at_span(0)
    tip_t = wing_thickness_at_span(HALF_SPAN)
    add_airfoil_outline(msp, x0 + ROOT_CHORD * scale / 2, y0, ROOT_CHORD * scale, root_t * scale)
    add_airfoil_outline(msp, x0 + TIP_CHORD * scale / 2, y0 - 55, TIP_CHORD * scale, tip_t * scale)
    msp.add_text("ROOT PROFILE", height=2.1, dxfattribs={"layer": "TEXT"}).set_placement((x0 + 10, y0 + 14))
    msp.add_text("TIP PROFILE", height=2.1, dxfattribs={"layer": "TEXT"}).set_placement((x0 + 10, y0 - 41))
    for frac, layer in [(0.25, "SPAR"), (0.60, "SPAR"), (0.72, "CENTERLINE")]:
        msp.add_line(
            (x0 + ROOT_CHORD * scale * frac, y0 - root_t * scale / 2 - 4),
            (x0 + ROOT_CHORD * scale * frac, y0 + root_t * scale / 2 + 4),
            dxfattribs={"layer": layer},
        )


def draw_wing_half_assembly() -> tuple[str, str]:
    doc = setup_drawing(
        title="Wing_Half_Assembly",
        subtitle="Canonical half-wing parent drawing. Use this before panel decomposition.",
        material="LW-PLA shells + CF-PLA ribs + 8mm/5mm CF spars + spruce rear spar",
        mass="215g target with contingency",
        scale="1:3 / 1:2 detail",
        sheet_size="A1",
        status="FOR ITERATION",
        revision="v2",
    )
    msp = doc.modelspace()

    wing_scale = 0.28
    top_x0 = 85.0
    top_y_le = 505.0
    msp.add_text("TOP VIEW — WING HALF ASSEMBLY", height=4.2, dxfattribs={"layer": "TEXT"}).set_placement((top_x0, 530))
    add_wing_top_view(msp, top_x0, top_y_le, wing_scale, full=False)

    msp.add_text("FRONT VIEW — POLYHEDRAL / DIHEDRAL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((top_x0, 260))
    add_wing_front_view(msp, top_x0, 205, wing_scale, full=False)

    msp.add_text("PROFILE DETAILS — ROOT / TIP AIRFOIL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((500, 260))
    add_wing_side_view(msp, 525, 215, wing_scale)

    msp.add_linear_dim(
        base=(top_x0 + HALF_SPAN * wing_scale / 2, 110),
        p1=(top_x0, 118),
        p2=(top_x0 + HALF_SPAN * wing_scale, 118),
        dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"},
    ).render()
    msp.add_linear_dim(
        base=(60, top_y_le - ROOT_CHORD * wing_scale / 2),
        p1=(68, top_y_le),
        p2=(68, top_y_le - ROOT_CHORD * wing_scale),
        angle=90,
        dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"},
    ).render()

    msp.add_text("Main spar 8mm tube to P5, 4mm rod in P6 tip section", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((430, 175))
    msp.add_text("Rear spar 5x3 spruce to P5 only; short tip uses D-box + rod", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((430, 155))
    msp.add_text("Hinge line at 72% chord; flap P1-P3, aileron P4-P6", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((430, 135))
    msp.add_text("Servo envelopes shown at current packaging baseline", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((460, 115))

    out = ROOT / "cad/assemblies/wing/Wing_Half_Assembly/Wing_Half_Assembly_drawing.dxf"
    return save_dxf_and_png(doc, str(out), dpi=240)


def draw_wing_assembly() -> tuple[str, str]:
    candidate_area_dm2 = 43.7
    candidate_ar = 18.2
    doc = setup_drawing(
        title="Wing_Assembly",
        subtitle="Full-wing parent drawing. Candidate higher-AR wing for aircraft R4 closure before panel derivation.",
        material="Mirrored half-wing assemblies with moderate stretch, tighter taper, and shorter tip section",
        mass="420-455g full wing candidate",
        scale="1:6 common",
        sheet_size="A1",
        status="FOR ITERATION",
        revision="v2",
        orientation_labels={"fwd": "FWD", "inbd": "CL"},
    )
    msp = doc.modelspace()

    wing_scale = 0.29
    top_x0 = 46.0
    top_y_le = 505.0
    msp.add_text("TOP VIEW — FULL WING ASSEMBLY", height=4.2, dxfattribs={"layer": "TEXT"}).set_placement((top_x0, 530))
    x_left_root, x_right_root = add_wing_top_view(msp, top_x0, top_y_le, wing_scale, full=True)

    front_center_x = top_x0 + HALF_SPAN * wing_scale + (FUSELAGE_GAP * wing_scale) / 2
    front_y0 = 246.0
    msp.add_text("FRONT VIEW — FULL SPAN POLYHEDRAL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((top_x0 + 70, 286))
    add_wing_front_view(msp, front_center_x, front_y0, wing_scale, full=True)

    detail_x = 650.0
    detail_y = 250.0
    msp.add_text("PROFILE DETAILS — ROOT / TIP AIRFOIL", height=3.4, dxfattribs={"layer": "TEXT"}).set_placement((detail_x - 10, 286))
    add_wing_side_view(msp, detail_x, detail_y, wing_scale)

    total_width = FULL_SPAN * wing_scale + FUSELAGE_GAP * wing_scale
    msp.add_linear_dim(
        base=(top_x0 + total_width / 2, 105),
        p1=(top_x0, 113),
        p2=(top_x0 + total_width, 113),
        dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"},
    ).render()
    msp.add_linear_dim(
        base=(58, top_y_le - ROOT_CHORD * wing_scale / 2),
        p1=(66, top_y_le),
        p2=(66, top_y_le - ROOT_CHORD * wing_scale),
        angle=90,
        dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"},
    ).render()
    msp.add_linear_dim(
        base=((x_left_root + x_right_root) / 2, top_y_le + 18),
        p1=(x_left_root, top_y_le + 10),
        p2=(x_right_root, top_y_le + 10),
        dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"},
    ).render()

    msp.add_text("Panel hierarchy retained; this is the parent sheet before panel generation.", height=2.1, dxfattribs={"layer": "TEXT"}).set_placement((95, 72))
    msp.add_text("Right half shows servo envelopes. Left half remains clean for planform review.", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((95, 58))
    msp.add_text("Candidate span 2816 | root chord 170 | tip chord 85 | superelliptic taper", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((180, 180))
    msp.add_text(f"Area ~{candidate_area_dm2:.1f} dm^2 | Aspect ratio ~{candidate_ar:.1f} | flap P1-P3 | aileron P4-P6", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((180, 162))
    msp.add_text("Root gap is fuselage packaging space, not an aero dead zone.", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((180, 144))

    detail_x = 620.0
    detail_y = 485.0
    msp.add_text("ROOT DETAIL — CENTER GAP / SPAR / SYSTEMS", height=2.8, dxfattribs={"layer": "TEXT"}).set_placement((detail_x - 10, detail_y + 20))
    chord = ROOT_CHORD * wing_scale * 1.25
    gap = FUSELAGE_GAP * wing_scale * 1.25
    left_x = detail_x
    right_x = detail_x + 70 + gap
    y_top = detail_y
    y_bot = detail_y - chord
    msp.add_line((left_x, y_top), (left_x, y_bot), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((right_x, y_top), (right_x, y_bot), dxfattribs={"layer": "OUTLINE"})
    for frac, layer, text in [(MAIN_SPAR_FRAC, "SPAR", "8mm MAIN"), (REAR_SPAR_FRAC, "SPAR", "REAR 5x3"), (HINGE_FRAC, "CENTERLINE", "HINGE")]:
        yy = y_top - ROOT_CHORD * frac * wing_scale * 1.25
        msp.add_line((left_x - 28, yy), (left_x, yy), dxfattribs={"layer": layer})
        msp.add_line((right_x, yy), (right_x + 28, yy), dxfattribs={"layer": layer})
        msp.add_text(text, height=1.6, dxfattribs={"layer": "TEXT"}).set_placement((right_x + 32, yy - 1))
    add_rect_outline(msp, left_x - 12, y_top - 32, left_x + 2, y_top - 18, "HIDDEN")
    add_rect_outline(msp, right_x - 2, y_top - 32, right_x + 12, y_top - 18, "HIDDEN")
    msp.add_text("ROOT WIRING", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement((right_x + 24, y_top - 31))
    msp.add_text("ANTI-CRUSH / BOLT PAD", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement((right_x + 24, y_top - 45))

    out = ROOT / "cad/assemblies/wing/Wing_Assembly/Wing_Assembly_drawing.dxf"
    return save_dxf_and_png(doc, str(out), dpi=240)


def draw_fuselage_assembly() -> tuple[str, str]:
    doc = setup_drawing(
        title="Fuselage_Assembly",
        subtitle="Plain top-level fuselage OML concept. Clean parent sheet for aerodynamic shape review.",
        material="Top-level outer mold line concept only",
        mass="Concept review",
        scale="1:2",
        sheet_size="A1",
        status="TOP-LEVEL REVIEW",
        revision="v4",
        orientation_labels={"fwd": "FWD", "inbd": "UP"},
    )
    msp = doc.modelspace()

    side_x0 = 50.0
    side_y0 = 430.0
    top_x0 = 50.0
    top_y0 = 235.0
    sec_x0 = 660.0
    sec_y0 = 430.0
    scale = 0.54

    msp.add_text("SIDE VIEW — FUSELAGE OML REFERENCE", height=4.2, dxfattribs={"layer": "TEXT"}).set_placement((side_x0, side_y0 + 98))
    add_fuselage_side_outline(msp, side_x0, side_y0, scale)
    add_hstab_attach_marker_side(msp, side_x0, side_y0, scale, label_offset=2.0)

    msp.add_text("TOP VIEW — FUSELAGE OML / WING FAIRING IDEA", height=4.2, dxfattribs={"layer": "TEXT"}).set_placement((top_x0, top_y0 + 58))
    add_fuselage_top_outline(msp, top_x0, top_y0, scale)
    for label, x_mm in [("NOSE", 55.0), ("MAX POD", 170.0), ("WING LE", 260.0), ("TAIL START", 760.0), ("HSTAB ATTACH", hstab_attach_station_x())]:
        xs = top_x0 + x_mm * scale
        half_w = schedule_value(FUSELAGE_PLAN_HALF, x_mm) * scale
        msp.add_line((xs, top_y0 - half_w - 8), (xs, top_y0 + half_w + 8), dxfattribs={"layer": "SECTION"})
        msp.add_text(label, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((xs - 10, top_y0 + half_w + 12))

    msp.add_text("Plain top-view aerodynamic idea only. Internal architecture is intentionally omitted here.", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((90, 72))
    msp.add_text("Wing-root fairing is shown as a smoother OML shoulder instead of the older stepped blend.", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((90, 58))
    msp.add_text("Tail architecture and side-view internals stay with the fuselage aero/structural review.", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((90, 44))

    msp.add_linear_dim(
        base=(side_x0 + FUSELAGE_LENGTH * scale / 2, 120),
        p1=(side_x0, 128),
        p2=(side_x0 + FUSELAGE_LENGTH * scale, 128),
        dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"},
    ).render()
    msp.add_linear_dim(
        base=(60, top_y0),
        p1=(68, top_y0 + 25),
        p2=(68, top_y0 - 25),
        angle=90,
        dxfattribs={"dimstyle": "AEROFORGE", "layer": "DIMENSION"},
    ).render()

    for idx, (x_mm, title) in enumerate([(30, "A — MOTOR FACE"), (170, "B — MAX POD"), (260, "C — WING LE"), (760, "D — TAIL START")]):
        cx = sec_x0
        cy = sec_y0 - idx * 88
        w = fuselage_dim_at(x_mm, 1)
        h = fuselage_dim_at(x_mm, 2)
        if w >= h:
            major_axis = (max(w / 4, 2), 0)
            ratio = (h / w) if w else 1.0
        else:
            major_axis = (0, max(h / 4, 2))
            ratio = (w / h) if h else 1.0
        msp.add_text(f"SEC {title}", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement((cx - 35, cy + max(h / 4, 12) + 18))
        msp.add_ellipse((cx, cy), major_axis=major_axis, ratio=ratio, dxfattribs={"layer": "OUTLINE"})
        msp.add_line((cx, cy - max(h / 4, 6) - 5), (cx, cy + max(h / 4, 6) + 5), dxfattribs={"layer": "CENTERLINE"})
        msp.add_line((cx - max(w / 4, 6) - 5, cy), (cx + max(w / 4, 6) + 5, cy), dxfattribs={"layer": "CENTERLINE"})

    out = ROOT / "cad/assemblies/fuselage/Fuselage_Assembly/Fuselage_Assembly_drawing.dxf"
    return save_dxf_and_png(doc, str(out), dpi=240)


def main() -> None:
    draw_wing_half_assembly()
    draw_wing_assembly()
    draw_fuselage_assembly()


if __name__ == "__main__":
    main()
