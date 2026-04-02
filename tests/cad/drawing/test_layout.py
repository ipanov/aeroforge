"""Tests for the sheet layout calculator."""
import pytest


def test_layout_fits_on_a3_sheet():
    from src.cad.drawing.layout import calculate_layout

    # Simulate view bounding boxes (model-space mm)
    view_bounds = {
        "top": (0, 0, 115, 430),      # planform: 115mm chord x 430mm span
        "front": (0, -4, 115, 4),      # root section: 115mm x 8mm
        "right": (0, -4, 430, 4),      # side view: 430mm x 8mm
    }

    layout = calculate_layout(view_bounds, sheet_size="A3")

    assert layout["scale"] > 0
    assert layout["scale"] <= 1.0  # never scale up

    # All view origins must be inside the sheet (with margins)
    sw, sh = 420, 297
    for view_name in ["top", "front", "right"]:
        ox, oy = layout[view_name]
        assert ox >= 15, f"{view_name} left edge outside margin"
        assert oy >= 15, f"{view_name} bottom edge outside margin"


def test_top_view_is_above_front_view():
    from src.cad.drawing.layout import calculate_layout

    view_bounds = {
        "top": (0, 0, 100, 200),
        "front": (0, -5, 100, 5),
        "right": (0, -5, 200, 5),
    }

    layout = calculate_layout(view_bounds, sheet_size="A3")

    # Third-angle: top view Y > front view Y
    assert layout["top"][1] > layout["front"][1]
    # Right view X > front view X
    assert layout["right"][0] > layout["front"][0]
