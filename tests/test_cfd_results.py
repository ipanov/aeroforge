"""Tests for CFD result extraction, analysis, and report generation.

These tests use synthetic SU2 output data to verify that the extraction
pipeline produces all required outputs. No actual SU2 binary is needed.

HARD STOP guarantee: if any required output is missing, the validation
step MUST NOT be marked as complete.
"""

import csv
import json
import math
from pathlib import Path

import pytest
import numpy as np

from src.analysis.cfd_results import (
    AlphaResult,
    AeroTestReport,
    CFDTestConfiguration,
    ConvergenceRecord,
    DragBreakdown,
    StabilityDerivatives,
    SurfacePoint,
    compute_drag_breakdown,
    compute_stability_derivatives,
    extract_alpha_result,
    extract_full_report,
    generate_markdown_report,
    parse_forces_breakdown,
    parse_history_csv,
    parse_surface_flow,
    validate_report_completeness,
    write_report,
)


# ---------------------------------------------------------------------------
# Fixtures: synthetic SU2 output files
# ---------------------------------------------------------------------------


def _write_history_csv(path: Path, iterations: int = 100, alpha: float = 5.0) -> None:
    """Write a synthetic SU2 history.csv with converging residuals."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            '"Inner_Iter"', '"rms[Rho]"', '"rms[RhoU]"', '"CL"', '"CD"', '"CMz"', '"Time(sec)"',
        ])
        for i in range(1, iterations + 1):
            rms = -2.0 - 6.0 * (i / iterations)  # -2 → -8 (converging)
            cl = 0.5 + 0.001 * i / iterations  # Slowly stabilize
            cd = 0.012 - 0.001 * i / iterations
            cm = -0.05
            writer.writerow([i, f"{rms:.4f}", f"{rms + 0.5:.4f}", f"{cl:.6f}", f"{cd:.6f}", f"{cm:.6f}", f"{i * 0.5:.1f}"])


def _write_surface_flow_csv(path: Path, n_points: int = 50) -> None:
    """Write a synthetic SU2 surface_flow.csv."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "x", "y", "z",
            "Pressure_Coefficient", "Pressure",
            "Skin_Friction_Coefficient_X", "Skin_Friction_Coefficient_Y", "Skin_Friction_Coefficient_Z",
            "Temperature", "Mach",
        ])
        for i in range(n_points):
            x = i / n_points  # 0 to 1 along chord
            y = 0.0
            z = 0.1 * math.sin(math.pi * x)  # Airfoil-like shape
            cp = 1.0 - 4.0 * x * (1.0 - x)  # Parabolic Cp distribution
            p = 101325.0 * (1 + 0.5 * cp)
            cfx = 0.003 * (1 - x)
            cfy = 0.0001
            cfz = 0.0
            writer.writerow([
                f"{x:.6f}", f"{y:.6f}", f"{z:.6f}",
                f"{cp:.6f}", f"{p:.1f}",
                f"{cfx:.6f}", f"{cfy:.6f}", f"{cfz:.6f}",
                "288.15", "0.03",
            ])


def _write_forces_breakdown(path: Path) -> None:
    """Write a synthetic forces_breakdown.dat."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "Total CL:    0.5010\n"
        "Pressure CL: 0.4900\n"
        "Friction CL: 0.0110\n"
        "Total CD:    0.0110\n"
        "Pressure CD: 0.0070\n"
        "Friction CD: 0.0040\n"
        "Total CMz:  -0.0500\n"
    )


@pytest.fixture
def alpha_dir(tmp_path: Path) -> Path:
    """Create a single alpha output directory with all SU2 files."""
    d = tmp_path / "alpha_5.0"
    _write_history_csv(d / "history.csv", iterations=100, alpha=5.0)
    _write_surface_flow_csv(d / "surface_flow.csv", n_points=50)
    _write_forces_breakdown(d / "forces_breakdown.dat")
    return d


@pytest.fixture
def sweep_dir(tmp_path: Path) -> Path:
    """Create a full alpha sweep directory."""
    alphas = [-5.0, -2.0, 0.0, 2.0, 5.0, 8.0, 10.0, 12.0, 15.0]
    for alpha in alphas:
        d = tmp_path / f"alpha_{alpha:.1f}"
        _write_history_csv(d / "history.csv", iterations=100)
        _write_surface_flow_csv(d / "surface_flow.csv", n_points=30)
        _write_forces_breakdown(d / "forces_breakdown.dat")
    return tmp_path


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------


class TestParseHistoryCSV:
    def test_parses_iterations(self, alpha_dir: Path):
        records = parse_history_csv(alpha_dir / "history.csv")
        assert len(records) == 100

    def test_convergence_trend(self, alpha_dir: Path):
        records = parse_history_csv(alpha_dir / "history.csv")
        # Residual should decrease
        assert records[-1].rms_density < records[0].rms_density

    def test_extracts_coefficients(self, alpha_dir: Path):
        records = parse_history_csv(alpha_dir / "history.csv")
        last = records[-1]
        assert last.cl != 0.0
        assert last.cd != 0.0

    def test_missing_file_returns_empty(self, tmp_path: Path):
        records = parse_history_csv(tmp_path / "nonexistent.csv")
        assert records == []


class TestParseSurfaceFlow:
    def test_parses_points(self, alpha_dir: Path):
        points = parse_surface_flow(alpha_dir / "surface_flow.csv")
        assert len(points) == 50

    def test_cp_values_populated(self, alpha_dir: Path):
        points = parse_surface_flow(alpha_dir / "surface_flow.csv")
        assert any(p.cp != 0.0 for p in points)

    def test_cf_magnitude_computed(self, alpha_dir: Path):
        points = parse_surface_flow(alpha_dir / "surface_flow.csv")
        for p in points:
            expected = math.sqrt(p.cf_x**2 + p.cf_y**2 + p.cf_z**2)
            assert abs(p.cf - expected) < 1e-10

    def test_missing_file_returns_empty(self, tmp_path: Path):
        points = parse_surface_flow(tmp_path / "nonexistent.csv")
        assert points == []


class TestParseForces:
    def test_parses_breakdown(self, alpha_dir: Path):
        forces = parse_forces_breakdown(alpha_dir / "forces_breakdown.dat")
        assert "total_cl" in forces
        assert "pressure_cd" in forces
        assert "friction_cd" in forces
        assert abs(forces["total_cl"] - 0.501) < 0.001

    def test_missing_file_returns_empty(self, tmp_path: Path):
        forces = parse_forces_breakdown(tmp_path / "nonexistent.dat")
        assert forces == {}


# ---------------------------------------------------------------------------
# Alpha result extraction
# ---------------------------------------------------------------------------


class TestExtractAlphaResult:
    def test_extracts_complete_result(self, alpha_dir: Path):
        result = extract_alpha_result(alpha_dir, alpha=5.0)
        assert result.alpha == 5.0
        assert result.cl != 0.0
        assert result.cd != 0.0
        assert result.iterations == 100

    def test_has_surface_points(self, alpha_dir: Path):
        result = extract_alpha_result(alpha_dir, alpha=5.0)
        assert len(result.surface_points) == 50

    def test_has_convergence_history(self, alpha_dir: Path):
        result = extract_alpha_result(alpha_dir, alpha=5.0)
        assert len(result.convergence_history) == 100

    def test_drag_breakdown_from_forces(self, alpha_dir: Path):
        result = extract_alpha_result(alpha_dir, alpha=5.0)
        assert result.cd_pressure > 0
        assert result.cd_friction > 0


# ---------------------------------------------------------------------------
# Stability derivatives
# ---------------------------------------------------------------------------


class TestStabilityDerivatives:
    def test_computes_cl_alpha(self):
        # Synthetic linear polar: CL = 0.1 * alpha + 0.3
        polar = [
            AlphaResult(alpha=-5, cl=-0.2, cd=0.02, cm=-0.03),
            AlphaResult(alpha=0, cl=0.3, cd=0.01, cm=-0.05),
            AlphaResult(alpha=5, cl=0.8, cd=0.015, cm=-0.07),
            AlphaResult(alpha=10, cl=1.3, cd=0.03, cm=-0.09),
            AlphaResult(alpha=15, cl=1.2, cd=0.08, cm=-0.10),  # Stall
        ]
        stab = compute_stability_derivatives(polar)
        # CL_alpha should be close to 0.1 per degree
        assert 0.08 < stab.cl_alpha < 0.12

    def test_finds_cl_max(self):
        polar = [
            AlphaResult(alpha=0, cl=0.3, cd=0.01, cm=0.0),
            AlphaResult(alpha=5, cl=0.8, cd=0.015, cm=0.0),
            AlphaResult(alpha=10, cl=1.3, cd=0.03, cm=0.0),
            AlphaResult(alpha=12, cl=1.35, cd=0.05, cm=0.0),  # CL_max
            AlphaResult(alpha=15, cl=1.1, cd=0.08, cm=0.0),   # Stall
        ]
        stab = compute_stability_derivatives(polar)
        assert stab.cl_max == 1.35
        assert stab.alpha_cl_max == 12.0

    def test_finds_ld_max(self):
        polar = [
            AlphaResult(alpha=0, cl=0.3, cd=0.01, cm=0.0),
            AlphaResult(alpha=3, cl=0.6, cd=0.008, cm=0.0),  # L/D = 75
            AlphaResult(alpha=5, cl=0.8, cd=0.015, cm=0.0),  # L/D = 53
            AlphaResult(alpha=10, cl=1.3, cd=0.03, cm=0.0),  # L/D = 43
        ]
        stab = compute_stability_derivatives(polar)
        assert stab.ld_max == 75.0
        assert stab.alpha_ld_max == 3.0

    def test_static_stability(self):
        polar = [
            AlphaResult(alpha=-5, cl=-0.2, cd=0.02, cm=0.05),
            AlphaResult(alpha=0, cl=0.3, cd=0.01, cm=0.0),
            AlphaResult(alpha=5, cl=0.8, cd=0.015, cm=-0.05),
            AlphaResult(alpha=10, cl=1.3, cd=0.03, cm=-0.10),
        ]
        stab = compute_stability_derivatives(polar)
        # CM_alpha should be negative (stable)
        assert stab.cm_alpha < 0

    def test_alpha_trim(self):
        polar = [
            AlphaResult(alpha=-5, cl=-0.2, cd=0.02, cm=0.10),
            AlphaResult(alpha=0, cl=0.3, cd=0.01, cm=0.02),
            AlphaResult(alpha=5, cl=0.8, cd=0.015, cm=-0.06),
        ]
        stab = compute_stability_derivatives(polar)
        # CM crosses zero between 0 and 5 degrees
        assert stab.alpha_trim is not None
        assert 0 < stab.alpha_trim < 5

    def test_too_few_points(self):
        polar = [AlphaResult(alpha=0, cl=0.3, cd=0.01, cm=0.0)]
        stab = compute_stability_derivatives(polar)
        assert stab.cl_alpha == 0.0  # Can't compute with 1 point


# ---------------------------------------------------------------------------
# Drag breakdown
# ---------------------------------------------------------------------------


class TestDragBreakdown:
    def test_computes_breakdown(self):
        polar = [
            AlphaResult(alpha=5, cl=0.8, cd=0.015, cm=0.0,
                        cd_pressure=0.007, cd_friction=0.004),
        ]
        breakdown = compute_drag_breakdown(polar, aspect_ratio=10.0)
        assert len(breakdown) == 1
        db = breakdown[0]
        assert db.cd_total == 0.015
        assert db.cd_pressure == 0.007
        assert db.cd_friction == 0.004
        assert db.cd_induced > 0  # CL=0.8, AR=10

    def test_induced_drag_formula(self):
        polar = [AlphaResult(alpha=5, cl=1.0, cd=0.02, cm=0.0)]
        breakdown = compute_drag_breakdown(polar, aspect_ratio=10.0, oswald_efficiency=1.0)
        # CD_i = CL^2 / (pi * AR * e) = 1 / (pi * 10 * 1) ≈ 0.0318
        expected = 1.0 / (math.pi * 10.0 * 1.0)
        assert abs(breakdown[0].cd_induced - expected) < 0.001

    def test_percentages_sum(self):
        polar = [
            AlphaResult(alpha=5, cl=0.8, cd=0.02, cm=0.0,
                        cd_pressure=0.012, cd_friction=0.008),
        ]
        breakdown = compute_drag_breakdown(polar)
        db = breakdown[0]
        # Pressure + friction should sum to ~100% (induced is additional)
        assert db.pct_pressure + db.pct_friction == pytest.approx(100.0, abs=0.1)


# ---------------------------------------------------------------------------
# Full report extraction
# ---------------------------------------------------------------------------


class TestExtractFullReport:
    def test_extracts_all_alphas(self, sweep_dir: Path):
        report = extract_full_report(sweep_dir, component_name="TestWing")
        assert len(report.polar) == 9  # 9 alpha points

    def test_alphas_sorted(self, sweep_dir: Path):
        report = extract_full_report(sweep_dir)
        alphas = [p.alpha for p in report.polar]
        assert alphas == sorted(alphas)

    def test_stability_computed(self, sweep_dir: Path):
        report = extract_full_report(sweep_dir)
        assert report.stability.cl_max != 0.0

    def test_drag_breakdown_computed(self, sweep_dir: Path):
        report = extract_full_report(sweep_dir)
        assert len(report.drag_breakdown) == 9

    def test_missing_dir_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            extract_full_report(tmp_path / "nonexistent")

    def test_empty_dir_raises(self, tmp_path: Path):
        tmp_path.mkdir(exist_ok=True)
        with pytest.raises(ValueError, match="HARD STOP"):
            extract_full_report(tmp_path)

    def test_component_name_stored(self, sweep_dir: Path):
        report = extract_full_report(sweep_dir, component_name="Wing", project_name="Test")
        assert report.component_name == "Wing"
        assert report.project_name == "Test"


# ---------------------------------------------------------------------------
# Report validation (hard-stop gate)
# ---------------------------------------------------------------------------


class TestReportValidation:
    def test_valid_report_passes(self, sweep_dir: Path):
        report = extract_full_report(sweep_dir)
        errors = validate_report_completeness(report)
        # May have warnings but no HARD STOPs
        hard_stops = [e for e in errors if "HARD STOP" in e]
        assert len(hard_stops) == 0

    def test_empty_polar_hard_stops(self):
        report = AeroTestReport(polar=[])
        errors = validate_report_completeness(report)
        assert any("HARD STOP" in e for e in errors)

    def test_no_drag_breakdown_hard_stops(self):
        report = AeroTestReport(
            polar=[AlphaResult(alpha=0, cl=0.3, cd=0.01, cm=0.0)],
            stability=StabilityDerivatives(cl_alpha=0.1, cl_max=1.0, cd_min=0.01, ld_max=30, alpha_zero_lift=-2.0),
            drag_breakdown=[],
        )
        errors = validate_report_completeness(report)
        assert any("HARD STOP" in e and "drag breakdown" in e for e in errors)


# ---------------------------------------------------------------------------
# Report generation (markdown + JSON + CSV)
# ---------------------------------------------------------------------------


class TestReportGeneration:
    def test_markdown_report_structure(self, sweep_dir: Path):
        report = extract_full_report(sweep_dir, component_name="Wing")
        md = generate_markdown_report(report)
        assert "# Aero Test Report: Wing" in md
        assert "## 1. Test Configuration" in md
        assert "## 2. Polar Results" in md
        assert "## 3. Key Aerodynamic Parameters" in md
        assert "## 4. Drag Breakdown" in md
        assert "## 5. Stability Assessment" in md
        assert "## 6. Convergence Diagnostics" in md
        assert "## 7. Artifacts" in md

    def test_write_report_creates_files(self, sweep_dir: Path, tmp_path: Path):
        report = extract_full_report(sweep_dir, component_name="Wing")
        output = tmp_path / "report_out"
        paths = write_report(report, output)

        assert "markdown_report" in paths
        assert paths["markdown_report"].exists()
        assert paths["markdown_report"].stat().st_size > 0

        assert "json_report" in paths
        assert paths["json_report"].exists()
        # JSON should be valid
        with open(paths["json_report"]) as f:
            data = json.load(f)
        assert "polar" in data
        assert "stability" in data

        assert "polar_csv" in paths
        assert paths["polar_csv"].exists()

    def test_json_excludes_bulky_data(self, sweep_dir: Path):
        report = extract_full_report(sweep_dir)
        d = report.to_dict()
        for entry in d["polar"]:
            assert "surface_points" not in entry
            assert "convergence_history" not in entry

    def test_surface_csv_per_alpha(self, sweep_dir: Path, tmp_path: Path):
        report = extract_full_report(sweep_dir)
        output = tmp_path / "report_out"
        paths = write_report(report, output)
        # Should have surface CSV for each alpha that has surface points
        surface_keys = [k for k in paths if k.startswith("surface_alpha_")]
        assert len(surface_keys) > 0
