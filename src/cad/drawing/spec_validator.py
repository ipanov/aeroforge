"""
Pre-Generation Spec Validator — Catches consensus contradictions BEFORE drawing.
================================================================================

This module validates that a component's design parameters are geometrically
self-consistent. It catches issues like:
  - Pocket placed outside its enclosing structure
  - Rod diameter exceeding airfoil thickness at any span station
  - Features referencing impossible chord fractions
  - Overlapping or conflicting structural elements

Run this BEFORE generating any DXF. If it fails, the consensus needs revision,
not the drawing script.
"""

from dataclasses import dataclass, field
from typing import Callable
import math


@dataclass
class ValidationIssue:
    severity: str  # "CRITICAL", "WARNING", "INFO"
    component: str
    check_name: str
    message: str
    details: dict = field(default_factory=dict)


class SpecValidator:
    """Validates geometric feasibility of a component spec against its envelope."""

    def __init__(self):
        self.issues: list[ValidationIssue] = []

    def check_containment_along_span(
        self,
        component: str,
        feature_name: str,
        span_range: tuple[float, float],
        feature_bounds_fn: Callable[[float], tuple[float, float]],
        envelope_bounds_fn: Callable[[float], tuple[float, float]],
        step: float = 1.0,
    ) -> bool:
        """Check that a feature stays inside its envelope at every span station.

        Args:
            component: Component name for reporting
            feature_name: Human-readable name of the feature being checked
            span_range: (y_start, y_end) span extent to check
            feature_bounds_fn: y -> (fwd_extent, aft_extent) of the feature
                (distances from a reference, e.g., hinge line)
            envelope_bounds_fn: y -> (fwd_limit, aft_limit) of the enclosing envelope
            step: Check interval in mm

        Returns:
            True if all stations pass, False if any fail.
        """
        y_start, y_end = span_range
        all_ok = True
        failed_stations = []

        y = y_start
        while y <= y_end + 0.001:
            feat_fwd, feat_aft = feature_bounds_fn(y)
            env_fwd, env_aft = envelope_bounds_fn(y)

            if feat_fwd > env_fwd + 0.01:
                failed_stations.append({
                    "y": round(y, 1),
                    "edge": "forward",
                    "feature": round(feat_fwd, 2),
                    "envelope": round(env_fwd, 2),
                    "overshoot_mm": round(feat_fwd - env_fwd, 2),
                })
                all_ok = False
            if feat_aft > env_aft + 0.01:
                failed_stations.append({
                    "y": round(y, 1),
                    "edge": "aft",
                    "feature": round(feat_aft, 2),
                    "envelope": round(env_aft, 2),
                    "overshoot_mm": round(feat_aft - env_aft, 2),
                })
                all_ok = False
            y += step

        if not all_ok:
            self.issues.append(ValidationIssue(
                severity="CRITICAL",
                component=component,
                check_name="containment",
                message=f"{feature_name} extends outside its envelope at {len(failed_stations)} stations",
                details={"failed_stations": failed_stations},
            ))
        return all_ok

    def check_rod_fits_airfoil(
        self,
        component: str,
        rod_name: str,
        rod_x: float,
        rod_diameter: float,
        y_range: tuple[float, float],
        le_x_fn: Callable[[float], float],
        chord_fn: Callable[[float], float],
        thickness_fn: Callable[[float, float], float],
        te_trunc: float = 0.97,
        step: float = 2.0,
    ) -> bool:
        """Check that a rod (spar, wire, stiffener) fits inside the airfoil.

        Verifies both:
        1. Rod X position is between LE and TE
        2. Airfoil thickness at rod position >= rod diameter + clearance
        """
        y_start, y_end = y_range
        all_ok = True
        failed = []

        y = y_start
        while y <= y_end + 0.001:
            c = chord_fn(y)
            if c < 0.5:
                y += step
                continue
            lx = le_x_fn(y)
            tx = lx + c * te_trunc

            # Check if rod is inside chord
            if rod_x < lx or rod_x > tx:
                failed.append({
                    "y": round(y, 1), "reason": "outside_chord",
                    "rod_x": rod_x, "le": round(lx, 2), "te": round(tx, 2),
                })
                all_ok = False
            else:
                # Check thickness
                frac = (rod_x - lx) / c
                half_thickness = thickness_fn(frac, y)
                full_thickness = 2 * half_thickness
                if full_thickness < rod_diameter:
                    failed.append({
                        "y": round(y, 1), "reason": "too_thin",
                        "thickness_mm": round(full_thickness, 2),
                        "rod_dia_mm": rod_diameter,
                        "frac": round(frac, 3),
                    })
                    all_ok = False
            y += step

        if not all_ok:
            sev = "CRITICAL" if any(f["reason"] == "outside_chord" for f in failed) else "WARNING"
            self.issues.append(ValidationIssue(
                severity=sev,
                component=component,
                check_name="rod_fit",
                message=f"{rod_name} (Ø{rod_diameter}mm at X={rod_x}) fails at {len(failed)} stations",
                details={"failed_stations": failed},
            ))
        return all_ok

    def check_dimension_positive(
        self, component: str, name: str, value: float,
    ) -> bool:
        """Basic sanity: a dimension must be positive."""
        if value <= 0:
            self.issues.append(ValidationIssue(
                severity="CRITICAL", component=component,
                check_name="positive_dim",
                message=f"{name} = {value} (must be > 0)",
            ))
            return False
        return True

    def check_range(
        self, component: str, name: str, value: float,
        min_val: float, max_val: float,
    ) -> bool:
        """Check a value is within expected range."""
        if not (min_val <= value <= max_val):
            self.issues.append(ValidationIssue(
                severity="WARNING", component=component,
                check_name="range",
                message=f"{name} = {value}, expected [{min_val}, {max_val}]",
            ))
            return False
        return True

    def report(self) -> str:
        """Generate a human-readable validation report."""
        if not self.issues:
            return "✓ All checks passed. Spec is geometrically consistent."

        lines = [f"{'='*70}", "SPEC VALIDATION REPORT", f"{'='*70}", ""]

        criticals = [i for i in self.issues if i.severity == "CRITICAL"]
        warnings = [i for i in self.issues if i.severity == "WARNING"]

        if criticals:
            lines.append(f"CRITICAL ISSUES ({len(criticals)}) — MUST FIX BEFORE DRAWING:")
            lines.append("-" * 50)
            for issue in criticals:
                lines.append(f"  [{issue.component}] {issue.check_name}: {issue.message}")
                if "failed_stations" in issue.details:
                    stations = issue.details["failed_stations"]
                    for s in stations[:5]:
                        lines.append(f"    → y={s['y']}: {s}")
                    if len(stations) > 5:
                        lines.append(f"    ... and {len(stations)-5} more stations")
            lines.append("")

        if warnings:
            lines.append(f"WARNINGS ({len(warnings)}):")
            lines.append("-" * 50)
            for issue in warnings:
                lines.append(f"  [{issue.component}] {issue.check_name}: {issue.message}")
            lines.append("")

        lines.append(f"Total: {len(criticals)} critical, {len(warnings)} warnings")
        if criticals:
            lines.append("⛔ DO NOT GENERATE DRAWINGS until critical issues are resolved.")
        return "\n".join(lines)

    @property
    def has_critical(self) -> bool:
        return any(i.severity == "CRITICAL" for i in self.issues)
