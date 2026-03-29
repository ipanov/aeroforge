"""
DXF Drawing Utilities — Professional Engineering Drawing Template
=================================================================
Standards: ISO 5457 (borders), ISO 7200 (title blocks), ASME Y14.3 (third-angle projection)

Provides:
  - setup_drawing()      — create a properly formatted engineering drawing
  - save_dxf_and_png()   — export DXF + PNG

COORDINATE CONVENTION (MANDATORY — enforced by hooks):
  All views: LE (leading edge) on LEFT, TE (trailing edge) on RIGHT
  Planform:  X = chordwise (LE left, TE right), Y = spanwise (root bottom, tip top)
  Sections:  X = chordwise (LE left, TE right), Y = thickness (up positive)
  Spars are STRAIGHT rigid rods — the main spar is the structural datum.
  Orientation: "FWD" arrow always points LEFT (toward LE / nose).

DRAWING LAYOUT (third-angle projection):
  - Clean white background — NO grid/millimeter paper (per ISO standards)
  - Border with zone reference system (A-H vertical, 1-12 horizontal)
  - Title block bottom-right (ISO 7200 fields)
  - Third-angle projection symbol in title block
  - "FWD" arrow + "INBD" arrow for orientation
  - All dimensions in mm
"""

from pathlib import Path
from typing import Optional
import math
import ezdxf
from ezdxf.addons.drawing.matplotlib import qsave


# ─── Standard layers ──────────────────────────────────────────────────────────

STANDARD_LAYERS = {
    # Drawing frame
    "BORDER":      {"color": 7,   "lineweight": 70},   # frame + zone refs
    "TITLEBLOCK":  {"color": 7,   "lineweight": 35},   # title block text/lines
    "ORIENTATION": {"color": 7,   "lineweight": 25},   # FWD/INBD arrows
    # Geometry
    "OUTLINE":     {"color": 7,   "lineweight": 50},   # visible edges (thick)
    "HIDDEN":      {"color": 7,   "lineweight": 25},   # hidden edges (thin dashed)
    "CENTERLINE":  {"color": 5,   "lineweight": 18},   # center lines (blue, thin)
    "SPAR":        {"color": 3,   "lineweight": 35},   # spar lines (green)
    "WALL":        {"color": 6,   "lineweight": 18},   # inner wall offset (magenta)
    "SECTION":     {"color": 4,   "lineweight": 25},   # section cuts (cyan)
    "HATCH":       {"color": 252, "lineweight": 13},   # section hatching (light gray)
    # Annotation
    "DIMENSION":   {"color": 1,   "lineweight": 18},   # dimensions (red)
    "TEXT":        {"color": 7,   "lineweight": 18},   # labels
}


def setup_drawing(
    *,
    title: str,
    drawing_number: str = "",
    subtitle: str = "",
    material: str = "",
    scale: str = "1:1",
    mass: str = "",
    status: str = "FOR APPROVAL",
    revision: str = "A",
    sheet_size: str = "A3",
    orientation_labels: Optional[dict[str, str]] = None,
) -> ezdxf.document.Drawing:
    """Create a professionally formatted engineering drawing document.

    Returns an ezdxf document with:
      - ISO 5457 border with zone reference system
      - ISO 7200 title block (bottom-right)
      - Third-angle projection symbol
      - FWD/INBD orientation arrows
      - Standard layers and dimension style
      - Clean white background (no grid)

    The caller adds geometry to doc.modelspace() then calls save_dxf_and_png().
    """
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()

    # Sheet dimensions (landscape)
    sheets = {
        "A4": (297, 210),
        "A3": (420, 297),
        "A2": (594, 420),
        "A1": (841, 594),
    }
    sw, sh = sheets.get(sheet_size, (420, 297))

    # Margins (ISO 5457): left=20mm filing edge, others=10mm
    ml, mt, mr, mb = 20, 10, 10, 10
    # Drawing area
    fx0, fy0 = ml, mb          # frame bottom-left
    fx1, fy1 = sw - mr, sh - mt  # frame top-right
    fw, fh = fx1 - fx0, fy1 - fy0

    # Create layers
    for name, props in STANDARD_LAYERS.items():
        try:
            doc.layers.add(name, color=props["color"])
        except ezdxf.DXFTableEntryError:
            pass

    # Dimension style
    ds = doc.dimstyles.new("AEROFORGE")
    ds.dxf.dimtxt = 2.5
    ds.dxf.dimasz = 1.5
    ds.dxf.dimlfac = 1.0
    ds.dxf.dimexe = 0.8
    ds.dxf.dimexo = 0.5
    ds.dxf.dimgap = 0.6

    # ─── Border frame (ISO 5457) ──────────────────────────────────────────
    border_attr = {"layer": "BORDER"}
    msp.add_line((fx0, fy0), (fx1, fy0), dxfattribs=border_attr)
    msp.add_line((fx1, fy0), (fx1, fy1), dxfattribs=border_attr)
    msp.add_line((fx1, fy1), (fx0, fy1), dxfattribs=border_attr)
    msp.add_line((fx0, fy1), (fx0, fy0), dxfattribs=border_attr)

    # Centering marks (4 marks at midpoints, extending 5mm beyond frame)
    cx, cy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
    cm = 5
    for (x1, y1, x2, y2) in [
        (cx, fy0 - cm, cx, fy0),       # bottom
        (cx, fy1, cx, fy1 + cm),       # top
        (fx0 - cm, cy, fx0, cy),       # left
        (fx1, cy, fx1 + cm, cy),       # right
    ]:
        msp.add_line((x1, y1), (x2, y2), dxfattribs=border_attr)

    # Zone reference labels along border
    # Vertical: letters A-H from bottom to top
    n_vz = 8
    vz_h = fh / n_vz
    for i in range(n_vz):
        letter = chr(ord('A') + i)
        y_mid = fy0 + (i + 0.5) * vz_h
        # Tick marks
        msp.add_line((fx0, fy0 + (i + 1) * vz_h), (fx0 + 3, fy0 + (i + 1) * vz_h),
                     dxfattribs=border_attr)
        msp.add_line((fx1 - 3, fy0 + (i + 1) * vz_h), (fx1, fy0 + (i + 1) * vz_h),
                     dxfattribs=border_attr)
        # Labels
        msp.add_text(letter, height=2.5, dxfattribs={"layer": "BORDER"}).set_placement(
            (fx0 + 1, y_mid - 1))
        msp.add_text(letter, height=2.5, dxfattribs={"layer": "BORDER"}).set_placement(
            (fx1 - 3.5, y_mid - 1))

    # Horizontal: numbers 1-12 from left to right
    n_hz = 12
    hz_w = fw / n_hz
    for i in range(n_hz):
        num = str(i + 1)
        x_mid = fx0 + (i + 0.5) * hz_w
        msp.add_line((fx0 + (i + 1) * hz_w, fy0), (fx0 + (i + 1) * hz_w, fy0 + 3),
                     dxfattribs=border_attr)
        msp.add_line((fx0 + (i + 1) * hz_w, fy1 - 3), (fx0 + (i + 1) * hz_w, fy1),
                     dxfattribs=border_attr)
        msp.add_text(num, height=2.0, dxfattribs={"layer": "BORDER"}).set_placement(
            (x_mid - 1, fy0 + 0.5))
        msp.add_text(num, height=2.0, dxfattribs={"layer": "BORDER"}).set_placement(
            (x_mid - 1, fy1 - 3))

    # ─── Title block (ISO 7200, bottom-right) ─────────────────────────────
    tb_w = 170  # max width per ISO 7200
    tb_h = 36
    tb_x = fx1 - tb_w
    tb_y = fy0

    tb_attr = {"layer": "TITLEBLOCK"}
    # Outer box
    msp.add_line((tb_x, tb_y), (tb_x + tb_w, tb_y), dxfattribs=tb_attr)
    msp.add_line((tb_x, tb_y + tb_h), (tb_x + tb_w, tb_y + tb_h), dxfattribs=tb_attr)
    msp.add_line((tb_x, tb_y), (tb_x, tb_y + tb_h), dxfattribs=tb_attr)
    msp.add_line((tb_x + tb_w, tb_y), (tb_x + tb_w, tb_y + tb_h), dxfattribs=tb_attr)

    # Row dividers (4 rows: title, description, material, info)
    for row_y in [tb_y + 9, tb_y + 18, tb_y + 27]:
        msp.add_line((tb_x, row_y), (tb_x + tb_w, row_y), dxfattribs=tb_attr)

    # Row 4 (top): Title + drawing number
    title_text = f"AEROFORGE — {title}"
    if drawing_number:
        title_text += f"  [{drawing_number}]"
    msp.add_text(title_text, height=3.5, dxfattribs={"layer": "TITLEBLOCK"}).set_placement(
        (tb_x + 3, tb_y + 29))

    # Row 3: Subtitle / description
    if subtitle:
        msp.add_text(subtitle, height=2.0, dxfattribs={"layer": "TITLEBLOCK"}).set_placement(
            (tb_x + 3, tb_y + 20))

    # Row 2: Material
    if material:
        msp.add_text(material, height=2.0, dxfattribs={"layer": "TITLEBLOCK"}).set_placement(
            (tb_x + 3, tb_y + 11))

    # Row 1 (bottom): Scale, date, mass, rev, status
    info_parts = [f"Scale: {scale}", "Units: mm", "Date: 2026-03-30"]
    if mass:
        info_parts.append(f"Mass: {mass}")
    info_parts.append(f"Rev: {revision}")
    info_parts.append(f"Status: {status}")
    msp.add_text(" | ".join(info_parts), height=1.8,
                 dxfattribs={"layer": "TITLEBLOCK"}).set_placement((tb_x + 3, tb_y + 2))

    # Third-angle projection symbol (truncated cone icon)
    _draw_projection_symbol(msp, tb_x + tb_w - 20, tb_y + 2)

    # ─── Orientation arrows (FWD + INBD) ──────────────────────────────────
    if orientation_labels is None:
        orientation_labels = {"fwd": "FWD", "inbd": "INBD"}

    # Place in top-left corner of drawing area
    _draw_orientation_arrows(msp, fx0 + 10, fy1 - 15, orientation_labels)

    return doc


def _draw_projection_symbol(msp, x: float, y: float) -> None:
    """Draw third-angle projection symbol (truncated cone in two views)."""
    attr = {"layer": "TITLEBLOCK"}
    # Front view: trapezoid (wider at bottom)
    msp.add_line((x, y), (x + 8, y), dxfattribs=attr)           # bottom
    msp.add_line((x + 2, y + 6), (x + 6, y + 6), dxfattribs=attr)  # top
    msp.add_line((x, y), (x + 2, y + 6), dxfattribs=attr)       # left slant
    msp.add_line((x + 8, y), (x + 6, y + 6), dxfattribs=attr)   # right slant
    # Side view: circle (to the LEFT for third-angle)
    msp.add_circle((x - 4, y + 3), 3, dxfattribs=attr)
    # Horizontal line connecting them
    msp.add_line((x - 1, y + 3), (x, y + 3), dxfattribs=attr)


def _draw_orientation_arrows(
    msp, x: float, y: float, labels: dict[str, str]
) -> None:
    """Draw FWD and INBD orientation arrows."""
    attr = {"layer": "ORIENTATION"}
    arrow_len = 15
    ah = 2.0  # arrowhead size

    # FWD arrow: points LEFT (toward LE / nose)
    if "fwd" in labels:
        msp.add_line((x + arrow_len, y), (x, y), dxfattribs=attr)
        msp.add_line((x, y), (x + ah, y + ah * 0.5), dxfattribs=attr)
        msp.add_line((x, y), (x + ah, y - ah * 0.5), dxfattribs=attr)
        msp.add_text(labels["fwd"], height=2.5, dxfattribs={"layer": "ORIENTATION"}).set_placement(
            (x - 1, y + 2))

    # INBD arrow: points DOWN (toward root / fuselage) — for half-span parts
    if "inbd" in labels:
        msp.add_line((x + arrow_len + 5, y + arrow_len), (x + arrow_len + 5, y),
                     dxfattribs=attr)
        msp.add_line((x + arrow_len + 5, y),
                     (x + arrow_len + 5 - ah * 0.5, y + ah), dxfattribs=attr)
        msp.add_line((x + arrow_len + 5, y),
                     (x + arrow_len + 5 + ah * 0.5, y + ah), dxfattribs=attr)
        msp.add_text(labels["inbd"], height=2.0,
                     dxfattribs={"layer": "ORIENTATION"}).set_placement(
            (x + arrow_len + 7, y + 2))


def save_dxf_and_png(
    doc: ezdxf.document.Drawing,
    dxf_path: str,
    *,
    dpi: int = 200,
    bg_color: str = "#FFFFFF",
) -> tuple[str, str]:
    """Save an ezdxf document as both DXF and PNG side-by-side.

    Returns:
        Tuple of (dxf_path, png_path) as strings.
    """
    dxf_path = Path(dxf_path)
    dxf_path.parent.mkdir(parents=True, exist_ok=True)

    doc.saveas(str(dxf_path))

    png_path = dxf_path.with_suffix(".png")
    qsave(doc.modelspace(), str(png_path), dpi=dpi, bg=bg_color)

    print(f"DXF saved: {dxf_path}")
    print(f"PNG saved: {png_path}")

    return str(dxf_path), str(png_path)
