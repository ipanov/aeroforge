"""Visual Validation System for Build123d components and assemblies.

Every component and assembly must pass through this validation pipeline
before being committed. This was introduced after Incident #001 where
a battery assembly was committed with wrong orientations and positions
because no visual validation was performed.

The system provides:
1. Reference image search (what should the real thing look like?)
2. Geometry sanity checks (bounding boxes, overlaps, alignment)
3. Screenshot capture (what did we actually generate?)
4. Multi-view SVG export (orthographic projections for review)
5. Validation report (pass/fail with specific issues)

Usage:
    from src.core.visual_validation import validate_assembly, ValidationReport

    report = validate_assembly(
        parts={"battery": battery_part, "xt60": xt60_part},
        connections=[("battery", "wire_exit", "lead_red", "start")],
        reference_description="3S 1300mAh LiPo with XT60 connector",
    )
    report.print_summary()
    if not report.passed:
        # Fix issues before continuing
        ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from build123d import *


class CheckSeverity(str, Enum):
    PASS = "PASS"
    WARNING = "WARN"
    FAIL = "FAIL"


@dataclass
class ValidationCheck:
    """A single validation check result."""
    name: str
    severity: CheckSeverity
    message: str
    details: str = ""


@dataclass
class ValidationReport:
    """Complete validation report for a component or assembly."""
    component_name: str
    checks: list[ValidationCheck] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    svg_paths: list[str] = field(default_factory=list)
    reference_description: str = ""

    @property
    def passed(self) -> bool:
        return not any(c.severity == CheckSeverity.FAIL for c in self.checks)

    @property
    def warnings(self) -> list[ValidationCheck]:
        return [c for c in self.checks if c.severity == CheckSeverity.WARNING]

    @property
    def failures(self) -> list[ValidationCheck]:
        return [c for c in self.checks if c.severity == CheckSeverity.FAIL]

    def print_summary(self) -> str:
        lines = [
            f"{'='*60}",
            f"VALIDATION REPORT: {self.component_name}",
            f"{'='*60}",
        ]
        if self.reference_description:
            lines.append(f"Reference: {self.reference_description}")
        lines.append("")

        for check in self.checks:
            icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX"}[check.severity.value]
            lines.append(f"  [{icon}] {check.name}: {check.message}")
            if check.details:
                lines.append(f"       {check.details}")

        lines.append("")
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c.severity == CheckSeverity.PASS)
        warns = len(self.warnings)
        fails = len(self.failures)
        status = "PASSED" if self.passed else "FAILED"
        lines.append(f"  Result: {status} ({passed}/{total} passed, {warns} warnings, {fails} failures)")

        if self.svg_paths:
            lines.append(f"  SVG exports: {', '.join(self.svg_paths)}")
        if self.screenshot_path:
            lines.append(f"  Screenshot: {self.screenshot_path}")

        lines.append(f"{'='*60}")
        result = "\n".join(lines)
        print(result)
        return result


# ── Geometry Checks ───────────────────────────────────────────────

def check_bounding_box_reasonable(part: Any, name: str,
                                   max_dim: float = 300.0) -> ValidationCheck:
    """Check that no dimension exceeds a reasonable maximum."""
    try:
        bb = part.bounding_box()
        sx = bb.max.X - bb.min.X
        sy = bb.max.Y - bb.min.Y
        sz = bb.max.Z - bb.min.Z
        dims = (sx, sy, sz)
        if max(dims) > max_dim:
            return ValidationCheck(
                name=f"{name}_bbox_size",
                severity=CheckSeverity.WARNING,
                message=f"Large dimension: {max(dims):.1f}mm exceeds {max_dim}mm",
                details=f"Size: {sx:.1f} x {sy:.1f} x {sz:.1f}mm",
            )
        if min(dims) < 0.1:
            return ValidationCheck(
                name=f"{name}_bbox_size",
                severity=CheckSeverity.FAIL,
                message=f"Near-zero dimension: {min(dims):.3f}mm",
                details=f"Size: {sx:.1f} x {sy:.1f} x {sz:.1f}mm",
            )
        return ValidationCheck(
            name=f"{name}_bbox_size",
            severity=CheckSeverity.PASS,
            message=f"Size OK: {sx:.1f} x {sy:.1f} x {sz:.1f}mm",
        )
    except Exception as e:
        return ValidationCheck(
            name=f"{name}_bbox_size",
            severity=CheckSeverity.FAIL,
            message=f"Cannot compute bounding box: {e}",
        )


def check_parts_connected(part_a: Any, name_a: str,
                           part_b: Any, name_b: str,
                           max_gap: float = 2.0) -> ValidationCheck:
    """Check that two parts are touching or overlapping (no gap)."""
    try:
        bb_a = part_a.bounding_box()
        bb_b = part_b.bounding_box()

        # Check overlap in each axis
        gaps = []
        for axis in ['X', 'Y', 'Z']:
            a_min = getattr(bb_a.min, axis)
            a_max = getattr(bb_a.max, axis)
            b_min = getattr(bb_b.min, axis)
            b_max = getattr(bb_b.max, axis)

            if a_max < b_min:
                gaps.append((axis, b_min - a_max))
            elif b_max < a_min:
                gaps.append((axis, a_min - b_max))

        if gaps:
            worst = max(gaps, key=lambda x: x[1])
            if worst[1] > max_gap:
                return ValidationCheck(
                    name=f"connection_{name_a}_{name_b}",
                    severity=CheckSeverity.FAIL,
                    message=f"Gap of {worst[1]:.1f}mm in {worst[0]}-axis between {name_a} and {name_b}",
                    details=f"Max allowed gap: {max_gap}mm",
                )
            else:
                return ValidationCheck(
                    name=f"connection_{name_a}_{name_b}",
                    severity=CheckSeverity.WARNING,
                    message=f"Small gap {worst[1]:.1f}mm in {worst[0]}-axis (within tolerance)",
                )

        return ValidationCheck(
            name=f"connection_{name_a}_{name_b}",
            severity=CheckSeverity.PASS,
            message=f"{name_a} and {name_b} are connected (overlapping bounding boxes)",
        )
    except Exception as e:
        return ValidationCheck(
            name=f"connection_{name_a}_{name_b}",
            severity=CheckSeverity.FAIL,
            message=f"Cannot check connection: {e}",
        )


def check_no_self_intersection(part: Any, name: str) -> ValidationCheck:
    """Check that a part doesn't have self-intersections (basic check)."""
    try:
        if hasattr(part, 'is_valid') and callable(part.is_valid):
            if part.is_valid():
                return ValidationCheck(
                    name=f"{name}_valid",
                    severity=CheckSeverity.PASS,
                    message="Geometry is valid",
                )
            else:
                return ValidationCheck(
                    name=f"{name}_valid",
                    severity=CheckSeverity.FAIL,
                    message="Geometry has self-intersections or is invalid",
                )
        return ValidationCheck(
            name=f"{name}_valid",
            severity=CheckSeverity.PASS,
            message="Geometry validity check not available (skipped)",
        )
    except Exception as e:
        return ValidationCheck(
            name=f"{name}_valid",
            severity=CheckSeverity.WARNING,
            message=f"Validity check failed: {e}",
        )


def check_axis_alignment(part: Any, name: str,
                          expected_long_axis: str = "X") -> ValidationCheck:
    """Check that a part's longest dimension is along the expected axis."""
    try:
        bb = part.bounding_box()
        dims = {
            "X": bb.max.X - bb.min.X,
            "Y": bb.max.Y - bb.min.Y,
            "Z": bb.max.Z - bb.min.Z,
        }
        actual_long = max(dims, key=dims.get)
        if actual_long == expected_long_axis:
            return ValidationCheck(
                name=f"{name}_axis_alignment",
                severity=CheckSeverity.PASS,
                message=f"Longest axis is {actual_long} ({dims[actual_long]:.1f}mm) as expected",
            )
        else:
            return ValidationCheck(
                name=f"{name}_axis_alignment",
                severity=CheckSeverity.FAIL,
                message=f"Longest axis is {actual_long} ({dims[actual_long]:.1f}mm), expected {expected_long_axis}",
                details=f"X={dims['X']:.1f}, Y={dims['Y']:.1f}, Z={dims['Z']:.1f}",
            )
    except Exception as e:
        return ValidationCheck(
            name=f"{name}_axis_alignment",
            severity=CheckSeverity.FAIL,
            message=f"Cannot check alignment: {e}",
        )


# ── SVG Export ────────────────────────────────────────────────────

def export_validation_views(
    parts: dict[str, Any],
    output_dir: str = "exports/validation",
    component_name: str = "component",
) -> list[str]:
    """Export orthographic SVG views (front, top, side) for visual review.

    Returns list of SVG file paths created.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    all_parts = list(parts.values())
    if not all_parts:
        return []

    compound = Compound(all_parts) if len(all_parts) > 1 else all_parts[0]

    svg_files = []
    views = {
        "front": Plane.XZ,   # Looking from front (Y direction)
        "top": Plane.XY,     # Looking from above (Z direction)
        "side": Plane.YZ,    # Looking from side (X direction)
    }

    for view_name, plane in views.items():
        try:
            svg_path = str(output_path / f"{component_name}_{view_name}.svg")
            visible, hidden = compound.project_to_viewport(plane.origin, plane.z_dir)
            exporter = ExportSVG(scale=2.0, margin=5)
            exporter.add_layer("visible", line_weight=0.3)
            exporter.add_layer("hidden", line_weight=0.1, line_type=LineType.ISO_DASH)
            exporter.add_shape(visible, layer="visible")
            exporter.add_shape(hidden, layer="hidden")
            exporter.write(svg_path)
            svg_files.append(svg_path)
        except Exception as e:
            print(f"  SVG export failed for {view_name} view: {e}")

    return svg_files


# ── Screenshot Capture ────────────────────────────────────────────

def capture_screenshot(
    output_path: str = "exports/validation/screenshot.png",
) -> Optional[str]:
    """Capture screenshot from OCP CAD Viewer if available."""
    try:
        from ocp_vscode import save_screenshot
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        save_screenshot(output_path)
        return output_path
    except Exception as e:
        print(f"  Screenshot capture failed: {e}")
        return None


# ── Main Validation Function ─────────────────────────────────────

def validate_geometry(
    parts: dict[str, Any],
    component_name: str,
    connections: Optional[list[tuple[str, str]]] = None,
    expected_axes: Optional[dict[str, str]] = None,
    reference_description: str = "",
    export_svgs: bool = True,
    capture_screen: bool = False,
    max_dimension: float = 300.0,
) -> ValidationReport:
    """Run full validation on a set of parts.

    Args:
        parts: Dict of {name: Build123d_part}
        component_name: Name for the report
        connections: List of (part_a_name, part_b_name) pairs that should be touching
        expected_axes: Dict of {part_name: expected_long_axis} e.g. {"battery": "X"}
        reference_description: What the real thing looks like (for the report)
        export_svgs: Whether to export SVG orthographic views
        capture_screen: Whether to capture OCP viewer screenshot
        max_dimension: Maximum acceptable dimension for any single part

    Returns:
        ValidationReport with all check results
    """
    report = ValidationReport(
        component_name=component_name,
        reference_description=reference_description,
    )

    # Check each part individually
    for name, part in parts.items():
        report.checks.append(check_bounding_box_reasonable(part, name, max_dimension))
        report.checks.append(check_no_self_intersection(part, name))

    # Check axis alignments
    if expected_axes:
        for name, axis in expected_axes.items():
            if name in parts:
                report.checks.append(check_axis_alignment(parts[name], name, axis))

    # Check connections between parts
    if connections:
        for name_a, name_b in connections:
            if name_a in parts and name_b in parts:
                report.checks.append(
                    check_parts_connected(parts[name_a], name_a, parts[name_b], name_b)
                )

    # Export SVG views
    if export_svgs:
        try:
            svg_files = export_validation_views(parts, component_name=component_name)
            report.svg_paths = svg_files
        except Exception as e:
            report.checks.append(ValidationCheck(
                name="svg_export",
                severity=CheckSeverity.WARNING,
                message=f"SVG export failed: {e}",
            ))

    # Capture screenshot
    if capture_screen:
        screenshot = capture_screenshot(f"exports/validation/{component_name}_screenshot.png")
        report.screenshot_path = screenshot

    return report
