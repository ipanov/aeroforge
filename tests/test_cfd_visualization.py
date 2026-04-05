"""Tests for CFD heatmap visualization pipeline."""

import csv
from pathlib import Path

import pytest

from src.analysis.cfd_visualization import (
    HeatmapConfig,
    paraview_available,
    surface_csv_to_vtk,
    render_heatmaps,
)


def _write_surface_csv(path: Path, n_points: int = 100) -> None:
    """Write a synthetic surface CSV for testing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "z", "Cp", "Cf", "Cf_x", "Cf_y", "Cf_z", "pressure"])
        import math
        for i in range(n_points):
            x = i / n_points
            z = 0.1 * math.sin(math.pi * x)
            cp = 1.0 - 4.0 * x * (1.0 - x)
            cf = 0.003 * (1 - x)
            writer.writerow([
                f"{x:.6f}", "0.0", f"{z:.6f}",
                f"{cp:.6f}", f"{cf:.6f}",
                f"{cf:.6f}", "0.0001", "0.0",
                "101325.0",
            ])


class TestSurfaceCSVToVTK:
    def test_creates_vtk_file(self, tmp_path: Path):
        csv_path = tmp_path / "surface.csv"
        _write_surface_csv(csv_path)
        vtk_path = tmp_path / "output.vtk"
        result = surface_csv_to_vtk(csv_path, vtk_path)
        assert result.exists()
        assert result.stat().st_size > 0

    def test_vtk_has_correct_header(self, tmp_path: Path):
        csv_path = tmp_path / "surface.csv"
        _write_surface_csv(csv_path, n_points=10)
        vtk_path = tmp_path / "output.vtk"
        surface_csv_to_vtk(csv_path, vtk_path)
        content = vtk_path.read_text()
        assert "vtk DataFile Version 3.0" in content
        assert "POLYDATA" in content
        assert "POINTS 10 float" in content
        assert "SCALARS Cp float" in content
        assert "SCALARS Cf float" in content
        assert "SCALARS Pressure float" in content

    def test_empty_csv_raises(self, tmp_path: Path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("x,y,z,Cp,Cf\n")
        with pytest.raises(ValueError, match="No valid points"):
            surface_csv_to_vtk(csv_path, tmp_path / "output.vtk")


class TestRenderHeatmaps:
    def test_missing_csv_hard_stop(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match="HARD STOP"):
            render_heatmaps(tmp_path / "nonexistent.csv", tmp_path / "output")

    def test_matplotlib_fallback_produces_pngs(self, tmp_path: Path):
        """Test that matplotlib fallback renders heatmaps when ParaView is unavailable."""
        pytest.importorskip("matplotlib")

        csv_path = tmp_path / "surface.csv"
        _write_surface_csv(csv_path)
        output_dir = tmp_path / "heatmaps"

        # Force matplotlib fallback by calling the internal function directly
        from src.analysis.cfd_visualization import _render_matplotlib_fallback
        config = HeatmapConfig()
        outputs = _render_matplotlib_fallback(csv_path, output_dir, config)

        # Should produce: Cp_side, Cp_front, Cp_top, Cf_side, Cf_front, Cf_top = 6 images
        assert len(outputs) == 6
        for p in outputs:
            assert p.exists()
            assert p.stat().st_size > 0
            assert p.suffix == ".png"

    def test_heatmap_config_defaults(self):
        config = HeatmapConfig()
        assert len(config.views) == 4
        assert config.image_width == 1920
        assert config.cp_range == (-2.0, 1.0)


class TestParaViewAvailability:
    def test_paraview_check_returns_bool(self):
        result = paraview_available()
        assert isinstance(result, bool)
