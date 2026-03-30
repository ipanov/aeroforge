"""Calculate view positions on a standard engineering drawing sheet.

Third-angle projection (ISO standard):
  - FRONT view: bottom-left
  - TOP view: directly above front view
  - RIGHT view: directly right of front view

Auto-scales all views with a single scale factor to fit the sheet.
"""

SHEETS = {
    "A4": (297, 210),
    "A3": (420, 297),
    "A2": (594, 420),
}


def calculate_layout(
    view_bounds: dict[str, tuple[float, float, float, float]],
    sheet_size: str = "A3",
    margin: float = 20.0,
    gap: float = 15.0,
    title_block_h: float = 42.0,
) -> dict:
    """Calculate view positions on sheet using third-angle projection.

    Args:
        view_bounds: {view_name: (xmin, ymin, xmax, ymax)} in model mm
        sheet_size: "A3" or "A4"
        margin: border margin in mm
        gap: minimum gap between views in mm
        title_block_h: title block height at bottom-right

    Returns:
        dict with "scale" and per-view (x_offset, y_offset) for bottom-left corner.
    """
    sw, sh = SHEETS[sheet_size]

    # Available drawing area
    avail_w = sw - 2 * margin
    avail_h = sh - 2 * margin - title_block_h

    # View dimensions in model space
    def dim(bb):
        return bb[2] - bb[0], bb[3] - bb[1]

    top_w, top_h = dim(view_bounds["top"])
    front_w, front_h = dim(view_bounds["front"])
    right_w, right_h = dim(view_bounds["right"])

    # Space needed (third-angle layout)
    col1_w = max(top_w, front_w)
    needed_w = col1_w + gap + right_w
    needed_h = top_h + gap + max(front_h, right_h)

    # Scale to fit (never scale up beyond 1:1)
    scale = min(avail_w / needed_w, avail_h / needed_h, 1.0)

    # Scaled dimensions
    s_col1_w = col1_w * scale
    s_front_h = front_h * scale
    s_top_h = top_h * scale

    # Position front view: bottom-left of available area
    front_x = margin
    front_y = margin + title_block_h

    # Top view: directly above front, left-aligned
    top_x = margin
    top_y = front_y + s_front_h + gap

    # Right view: right of front, bottom-aligned
    right_x = margin + s_col1_w + gap
    right_y = front_y

    return {
        "scale": scale,
        "sheet": (sw, sh),
        "top": (top_x, top_y),
        "front": (front_x, front_y),
        "right": (right_x, right_y),
    }
