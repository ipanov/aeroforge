"""Tests for the DXF drawing exporter."""
import os
import pytest
build123d = pytest.importorskip("build123d")
from build123d import Box


def test_export_produces_dxf_file(tmp_path):
    from src.cad.drawing.projector import project_standard_views, compute_2d_bounds
    from src.cad.drawing.layout import calculate_layout
    from src.cad.drawing.exporter import export_drawing

    box = Box(100, 50, 10)
    views = project_standard_views(box)

    view_bounds = {}
    for name in ["top", "front", "right"]:
        all_edges = views[name]["visible"] + views[name]["hidden"]
        view_bounds[name] = compute_2d_bounds(all_edges)

    layout = calculate_layout(view_bounds, sheet_size="A3")

    out_path = str(tmp_path / "test_drawing.dxf")
    export_drawing(views, layout, out_path)

    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 100  # not empty
