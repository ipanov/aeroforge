"""Tests for CFD iteration feedback format."""

from pathlib import Path

import pytest

from src.analysis.cfd_feedback import (
    CFDFeedback,
    CriterionResult,
    CriterionRangeResult,
    build_feedback_from_report,
)
from src.analysis.cfd_results import (
    AlphaResult,
    AeroTestReport,
    DragBreakdown,
    StabilityDerivatives,
)


@pytest.fixture
def sample_report() -> AeroTestReport:
    """Minimal report for feedback testing."""
    return AeroTestReport(
        component_name="TestAircraft",
        polar=[
            AlphaResult(alpha=-5, cl=-0.2, cd=0.02, cm=0.05),
            AlphaResult(alpha=0, cl=0.3, cd=0.01, cm=0.02),
            AlphaResult(alpha=3, cl=0.6, cd=0.008, cm=-0.01,
                        cd_pressure=0.005, cd_friction=0.003),
            AlphaResult(alpha=5, cl=0.8, cd=0.015, cm=-0.04),
            AlphaResult(alpha=10, cl=1.3, cd=0.03, cm=-0.08),
            AlphaResult(alpha=15, cl=1.1, cd=0.08, cm=-0.10),
        ],
        stability=StabilityDerivatives(
            cl_alpha=0.09,
            cm_alpha=-0.01,
            cl_max=1.3,
            alpha_cl_max=10.0,
            cl_zero=0.3,
            alpha_zero_lift=-3.3,
            cd_min=0.008,
            alpha_cd_min=3.0,
            ld_max=75.0,
            alpha_ld_max=3.0,
            cl_at_ld_max=0.6,
            alpha_trim=1.0,
            neutral_point_pct_mac=35.0,
        ),
        drag_breakdown=[
            DragBreakdown(alpha=3, cd_total=0.008, cd_pressure=0.005,
                          cd_friction=0.003, cd_induced=0.002),
        ],
    )


@pytest.fixture
def validation_criteria() -> dict:
    return {
        "ld_ratio_target": 15.0,
        "interference_drag_pct": 5.0,
        "static_margin_range": [5.0, 15.0],
        "structural_sf": 1.5,
        "auw_target_g": 800.0,
        "auw_tolerance_pct": 5.0,
    }


class TestCriterionResult:
    def test_pass_when_above_target(self):
        c = CriterionResult(name="ld", measured=20.0, target=15.0)
        assert c.passed is True

    def test_fail_when_below_target(self):
        c = CriterionResult(name="ld", measured=10.0, target=15.0)
        assert c.passed is False

    def test_tolerance(self):
        c = CriterionResult(name="mass", measured=810, target=800, tolerance=50)
        assert c.passed is True

    def test_out_of_tolerance(self):
        c = CriterionResult(name="mass", measured=900, target=800, tolerance=50)
        assert c.passed is False


class TestCriterionRangeResult:
    def test_in_range(self):
        c = CriterionRangeResult(name="sm", measured=10.0, range_min=5.0, range_max=15.0)
        assert c.passed is True

    def test_below_range(self):
        c = CriterionRangeResult(name="sm", measured=3.0, range_min=5.0, range_max=15.0)
        assert c.passed is False

    def test_above_range(self):
        c = CriterionRangeResult(name="sm", measured=20.0, range_min=5.0, range_max=15.0)
        assert c.passed is False


class TestBuildFeedback:
    def test_basic_feedback(self, sample_report, validation_criteria):
        fb = build_feedback_from_report(sample_report, validation_criteria)
        assert fb.cl_alpha == 0.09
        assert fb.cl_max == 1.3
        assert fb.ld_max == 75.0

    def test_ld_criterion_passes(self, sample_report, validation_criteria):
        fb = build_feedback_from_report(sample_report, validation_criteria)
        ld_criteria = [c for c in fb.criteria if c.name == "ld_ratio"]
        assert len(ld_criteria) == 1
        assert ld_criteria[0].passed is True  # 75 > 15

    def test_static_margin_out_of_range(self, sample_report, validation_criteria):
        fb = build_feedback_from_report(sample_report, validation_criteria)
        sm_criteria = [c for c in fb.criteria if c.name == "static_margin"]
        assert len(sm_criteria) == 1
        # NP = 35% MAC, range = 5-15% → should fail
        assert sm_criteria[0].passed is False

    def test_overall_verdict(self, sample_report, validation_criteria):
        fb = build_feedback_from_report(sample_report, validation_criteria)
        # Static margin fails, so overall should fail
        assert "FAILED" in fb.verdict or not fb.passed

    def test_cruise_drag_budget(self, sample_report, validation_criteria):
        fb = build_feedback_from_report(sample_report, validation_criteria, cruise_alpha=3.0)
        assert fb.cd_total_at_cruise == 0.008
        assert fb.cd_pressure_at_cruise == 0.005
        assert fb.cd_friction_at_cruise == 0.003

    def test_stability_flag(self, sample_report, validation_criteria):
        fb = build_feedback_from_report(sample_report, validation_criteria)
        assert fb.statically_stable is True  # cm_alpha = -0.01 < 0

    def test_failed_criteria_names(self, sample_report, validation_criteria):
        fb = build_feedback_from_report(sample_report, validation_criteria)
        failed = fb.failed_criteria_names()
        assert "static_margin" in failed

    def test_deltas_from_previous(self, sample_report, validation_criteria):
        prev = CFDFeedback(ld_max=70.0, cd_min=0.010, cl_max=1.2)
        fb = build_feedback_from_report(sample_report, validation_criteria, previous_feedback=prev)
        assert fb.delta_ld_max == pytest.approx(5.0)
        assert fb.delta_cd_min == pytest.approx(-0.002)
        assert fb.delta_cl_max == pytest.approx(0.1)
        assert fb.improving is True

    def test_no_criteria_means_pass(self, sample_report):
        fb = build_feedback_from_report(sample_report, {})
        assert fb.passed is True

    def test_json_serialization(self, sample_report, validation_criteria, tmp_path):
        fb = build_feedback_from_report(sample_report, validation_criteria)
        path = tmp_path / "feedback.json"
        fb.to_json(path)
        assert path.exists()
        import json
        data = json.loads(path.read_text())
        assert "passed" in data
        assert "criteria" in data
        assert "verdict" in data


class TestSeparationOfConcerns:
    """Verify that CFD feedback does NOT reference node hierarchy or dependency graph."""

    def test_no_node_references(self, sample_report, validation_criteria):
        fb = build_feedback_from_report(sample_report, validation_criteria)
        d = fb.to_dict()
        serialized = str(d)
        # CFD feedback should NOT contain workflow/orchestration terms
        assert "node" not in serialized.lower() or "neutral_point" in serialized.lower()
        assert "dependency" not in serialized.lower()
        assert "cascade" not in serialized.lower()
        assert "sub_assembly" not in serialized.lower()

    def test_feedback_is_purely_aerodynamic(self, sample_report, validation_criteria):
        fb = build_feedback_from_report(sample_report, validation_criteria)
        # Should have aerodynamic data
        assert fb.cl_alpha != 0
        assert fb.cl_max != 0
        assert fb.ld_max != 0
        # Should NOT have orchestration data
        assert not hasattr(fb, "affected_nodes")
        assert not hasattr(fb, "cascade_targets")
