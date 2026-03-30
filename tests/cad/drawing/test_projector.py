"""Tests for the 2D projection utility."""
import pytest
from build123d import Box


def test_project_standard_views_returns_three_views():
    from src.cad.drawing.projector import project_standard_views

    box = Box(100, 50, 10)
    views = project_standard_views(box)

    assert "top" in views
    assert "front" in views
    assert "right" in views
    for name in ["top", "front", "right"]:
        assert "visible" in views[name]
        assert "hidden" in views[name]
        assert len(views[name]["visible"]) > 0


def test_compute_2d_bounds_of_box():
    from src.cad.drawing.projector import project_standard_views, compute_2d_bounds

    box = Box(100, 50, 10)
    views = project_standard_views(box)
    xmin, ymin, xmax, ymax = compute_2d_bounds(
        views["top"]["visible"] + views["top"]["hidden"]
    )
    # Top view of 100x50x10 box → projected width ~100, height ~50
    assert abs((xmax - xmin) - 100) < 1.0
    assert abs((ymax - ymin) - 50) < 1.0
