"""Structured CFD feedback for the design iteration loop.

The CFD validation step produces this feedback object. The ORCHESTRATOR
(not the CFD analyst) decides which nodes in the dependency graph need
rework based on this feedback.

Separation of concerns:
- CFD analyst: tests the whole aircraft, reports quantified results
- This module: structures the output in a format the orchestrator can consume
- Orchestrator: compares results to convergence criteria, decides what to cascade

The CFD analyst does NOT know about the node hierarchy or dependency graph.
It only knows about aerodynamic surfaces, coefficients, and pass/fail criteria.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class CriterionResult:
    """Result of checking a single convergence criterion."""

    name: str
    measured: float
    target: float
    tolerance: float = 0.0
    passed: bool = False
    unit: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if self.tolerance > 0:
            self.passed = abs(self.measured - self.target) <= self.tolerance
        else:
            self.passed = self.measured >= self.target


@dataclass
class CriterionRangeResult:
    """Result of checking a criterion against a valid range."""

    name: str
    measured: float
    range_min: float
    range_max: float
    passed: bool = False
    unit: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        self.passed = self.range_min <= self.measured <= self.range_max


@dataclass
class CFDFeedback:
    """Structured feedback from CFD validation for the orchestrator.

    This is the contract between the CFD validation step and the
    workflow engine. The orchestrator reads this to decide:
    1. Whether validation passed or failed
    2. Which convergence criteria were not met
    3. What the aerodynamic data says (for agents to interpret)

    The CFD step populates this. The orchestrator consumes it.
    Agents (aerodynamicist, structural engineer) read the details
    when rework is triggered.
    """

    # Pass/fail verdict
    passed: bool = False
    verdict: str = ""  # Human-readable summary

    # Individual criteria results
    criteria: list[CriterionResult | CriterionRangeResult] = field(default_factory=list)

    # Summary aerodynamic data (for agents to read)
    cl_alpha: float = 0.0
    cl_max: float = 0.0
    cd_min: float = 0.0
    ld_max: float = 0.0
    alpha_zero_lift: float = 0.0
    cm_alpha: float = 0.0
    neutral_point_pct_mac: Optional[float] = None
    alpha_trim: Optional[float] = None
    statically_stable: bool = False

    # Drag budget
    cd_total_at_cruise: float = 0.0
    cd_pressure_at_cruise: float = 0.0
    cd_friction_at_cruise: float = 0.0
    cd_induced_at_cruise: float = 0.0

    # Deltas from previous iteration (if available)
    delta_ld_max: Optional[float] = None
    delta_cd_min: Optional[float] = None
    delta_cl_max: Optional[float] = None
    improving: Optional[bool] = None  # True if trending better

    # Artifact paths (for agents and dashboard)
    report_path: str = ""
    polar_csv_path: str = ""
    heatmap_paths: list[str] = field(default_factory=list)

    # Raw issues list (for agents to interpret)
    issues: list[str] = field(default_factory=list)

    def failed_criteria_names(self) -> list[str]:
        """Return names of criteria that did not pass."""
        return [c.name for c in self.criteria if not c.passed]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, path: Path) -> Path:
        """Write feedback as JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        return path


def build_feedback_from_report(
    report: Any,  # AeroTestReport from cfd_results
    validation_criteria: dict[str, Any],
    cruise_alpha: float = 3.0,
    previous_feedback: Optional[CFDFeedback] = None,
) -> CFDFeedback:
    """Build CFDFeedback from an AeroTestReport and project validation criteria.

    Args:
        report: AeroTestReport from cfd_results.extract_full_report()
        validation_criteria: From workflow_state.json validation_criteria dict
        cruise_alpha: Alpha for cruise condition drag budget
        previous_feedback: Previous iteration's feedback for delta calculation

    Returns:
        CFDFeedback ready for the orchestrator to consume.
    """
    stab = report.stability
    fb = CFDFeedback()

    # Populate summary aero data
    fb.cl_alpha = stab.cl_alpha
    fb.cl_max = stab.cl_max
    fb.cd_min = stab.cd_min
    fb.ld_max = stab.ld_max
    fb.alpha_zero_lift = stab.alpha_zero_lift
    fb.cm_alpha = stab.cm_alpha
    fb.neutral_point_pct_mac = stab.neutral_point_pct_mac
    fb.alpha_trim = stab.alpha_trim
    fb.statically_stable = stab.cm_alpha < 0 if stab.cm_alpha else False

    # Drag budget at cruise alpha
    cruise_pt = None
    for pt in report.polar:
        if abs(pt.alpha - cruise_alpha) < 0.5:
            cruise_pt = pt
            break
    if cruise_pt:
        fb.cd_total_at_cruise = cruise_pt.cd
        fb.cd_pressure_at_cruise = cruise_pt.cd_pressure
        fb.cd_friction_at_cruise = cruise_pt.cd_friction
    # Induced drag at cruise from breakdown
    for db in report.drag_breakdown:
        if abs(db.alpha - cruise_alpha) < 0.5:
            fb.cd_induced_at_cruise = db.cd_induced
            break

    # Check convergence criteria
    criteria = validation_criteria or {}

    # L/D ratio target
    if "ld_ratio_target" in criteria and criteria["ld_ratio_target"]:
        target = float(criteria["ld_ratio_target"])
        fb.criteria.append(CriterionResult(
            name="ld_ratio",
            measured=stab.ld_max,
            target=target,
            unit="",
            notes=f"L/D max at alpha={stab.alpha_ld_max:.1f} deg",
        ))

    # Interference drag
    if "interference_drag_pct" in criteria and criteria["interference_drag_pct"]:
        target = float(criteria["interference_drag_pct"])
        # Estimate interference drag as (total - sum of component drags)
        # This requires component-level data — use 0 if not available
        fb.criteria.append(CriterionResult(
            name="interference_drag",
            measured=0.0,
            target=target,
            notes="Requires component-level drag data for accurate measurement",
        ))

    # Static margin
    if "static_margin_range" in criteria and criteria["static_margin_range"]:
        sm_range = criteria["static_margin_range"]
        if isinstance(sm_range, (list, tuple)) and len(sm_range) == 2:
            np_val = stab.neutral_point_pct_mac or 0.0
            fb.criteria.append(CriterionRangeResult(
                name="static_margin",
                measured=np_val,
                range_min=float(sm_range[0]),
                range_max=float(sm_range[1]),
                unit="% MAC",
                notes=f"Neutral point at {np_val:.1f}% MAC",
            ))

    # Structural safety factor (not CFD's job, but track if provided)
    if "structural_sf" in criteria and criteria["structural_sf"]:
        fb.criteria.append(CriterionResult(
            name="structural_sf",
            measured=0.0,
            target=float(criteria["structural_sf"]),
            notes="Evaluated by FEA, not CFD",
        ))

    # AUW target
    if "auw_target_g" in criteria and criteria["auw_target_g"]:
        tol_pct = float(criteria.get("auw_tolerance_pct", 5.0))
        target = float(criteria["auw_target_g"])
        fb.criteria.append(CriterionResult(
            name="auw",
            measured=0.0,
            target=target,
            tolerance=target * tol_pct / 100,
            unit="g",
            notes="Mass evaluated by structural analysis, not CFD",
        ))

    # Deltas from previous iteration
    if previous_feedback:
        fb.delta_ld_max = stab.ld_max - previous_feedback.ld_max
        fb.delta_cd_min = stab.cd_min - previous_feedback.cd_min
        fb.delta_cl_max = stab.cl_max - previous_feedback.cl_max
        # Improving = L/D going up and CD going down
        fb.improving = (
            (fb.delta_ld_max or 0) > 0 and (fb.delta_cd_min or 0) < 0
        )

    # Issues from convergence
    if not report.all_converged:
        diverged = [p.alpha for p in report.polar if not p.converged]
        fb.issues.append(f"CFD diverged at alpha = {diverged}")

    # Overall verdict
    cfd_criteria = [c for c in fb.criteria if "structural" not in c.name and "auw" not in c.name]
    fb.passed = all(c.passed for c in cfd_criteria) if cfd_criteria else True

    if fb.passed:
        fb.verdict = f"CFD PASSED — L/D_max = {stab.ld_max:.1f}, CD_min = {stab.cd_min:.6f}"
    else:
        failed = [c.name for c in cfd_criteria if not c.passed]
        fb.verdict = f"CFD FAILED — criteria not met: {', '.join(failed)}"

    return fb
