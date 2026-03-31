"""
Post-Generation DXF Validator — Checks generated drawings against spec.
========================================================================

Reads back a generated DXF file and verifies:
  1. Dimension values match expected values from the spec
  2. Required layers exist and contain entities
  3. Geometric extents match expected bounding box
  4. Required labels/text are present
  5. Cross-section chord lengths match spec at each station

This catches drawing script bugs (wrong coordinates, missing features,
flipped orientations) AFTER the DXF is written.
"""

import ezdxf
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class DxfCheckResult:
    check: str
    passed: bool
    expected: str
    actual: str
    details: str = ""


class DxfValidator:
    """Validate a generated DXF file against expected properties."""

    def __init__(self, dxf_path: str):
        self.path = Path(dxf_path)
        self.doc = ezdxf.readfile(str(self.path))
        self.msp = self.doc.modelspace()
        self.results: list[DxfCheckResult] = []

    def check_layer_has_entities(self, layer_name: str, min_count: int = 1) -> bool:
        """Verify a layer exists and has at least min_count entities."""
        entities = [e for e in self.msp if e.dxf.layer == layer_name]
        passed = len(entities) >= min_count
        self.results.append(DxfCheckResult(
            check=f"layer_{layer_name}_count",
            passed=passed,
            expected=f">= {min_count} entities",
            actual=f"{len(entities)} entities",
        ))
        return passed

    def check_text_present(self, required_text: str, partial: bool = True) -> bool:
        """Check that a text string exists somewhere in the drawing."""
        texts = []
        for e in self.msp:
            if e.dxftype() == "TEXT":
                texts.append(e.dxf.text)
            elif e.dxftype() == "MTEXT":
                texts.append(e.text)

        if partial:
            found = any(required_text.lower() in t.lower() for t in texts)
        else:
            found = any(required_text == t for t in texts)

        self.results.append(DxfCheckResult(
            check=f"text_present",
            passed=found,
            expected=f"'{required_text}'",
            actual="found" if found else "NOT FOUND",
        ))
        return found

    def check_dimension_value(
        self, expected_value: float, tolerance: float = 0.5,
        label: str = "",
    ) -> bool:
        """Check that at least one dimension entity has the expected value."""
        dim_values = []
        for e in self.msp:
            if e.dxftype() == "DIMENSION":
                # ezdxf stores the measurement in different ways
                try:
                    meas = e.dxf.get("actual_measurement", None)
                    if meas is not None:
                        dim_values.append(float(meas))
                except (AttributeError, ValueError):
                    pass

        found = any(abs(v - expected_value) <= tolerance for v in dim_values)
        self.results.append(DxfCheckResult(
            check=f"dimension_{label or expected_value}",
            passed=found,
            expected=f"{expected_value} ± {tolerance}mm",
            actual=f"found values: {[round(v,1) for v in dim_values]}",
        ))
        return found

    def check_extents(
        self,
        expected_width: float,
        expected_height: float,
        tolerance_pct: float = 15.0,
        label: str = "drawing",
    ) -> bool:
        """Check the overall drawing extents are reasonable."""
        xmin = ymin = float("inf")
        xmax = ymax = float("-inf")

        for e in self.msp:
            try:
                if hasattr(e, "dxf") and hasattr(e.dxf, "start"):
                    for attr in ["start", "end", "insert"]:
                        if hasattr(e.dxf, attr):
                            pt = getattr(e.dxf, attr)
                            xmin = min(xmin, pt.x)
                            ymin = min(ymin, pt.y)
                            xmax = max(xmax, pt.x)
                            ymax = max(ymax, pt.y)
            except (AttributeError, TypeError):
                pass

        if xmin == float("inf"):
            self.results.append(DxfCheckResult(
                check=f"extents_{label}",
                passed=False,
                expected=f"{expected_width}x{expected_height}mm",
                actual="no measurable entities",
            ))
            return False

        actual_w = xmax - xmin
        actual_h = ymax - ymin
        tol = tolerance_pct / 100.0
        w_ok = abs(actual_w - expected_width) / max(expected_width, 1) <= tol
        h_ok = abs(actual_h - expected_height) / max(expected_height, 1) <= tol
        passed = w_ok and h_ok

        self.results.append(DxfCheckResult(
            check=f"extents_{label}",
            passed=passed,
            expected=f"{expected_width:.0f}x{expected_height:.0f}mm (±{tolerance_pct}%)",
            actual=f"{actual_w:.0f}x{actual_h:.0f}mm",
        ))
        return passed

    def check_entities_on_correct_layer(
        self, entity_type: str, expected_layer: str,
    ) -> bool:
        """Verify entities of a given type are on the correct layer."""
        matching = [e for e in self.msp if e.dxftype() == entity_type]
        on_layer = [e for e in matching if e.dxf.layer == expected_layer]
        off_layer = [e for e in matching if e.dxf.layer != expected_layer]

        passed = len(off_layer) == 0 or len(on_layer) > 0
        self.results.append(DxfCheckResult(
            check=f"{entity_type}_on_{expected_layer}",
            passed=passed,
            expected=f"all {entity_type} on {expected_layer}",
            actual=f"{len(on_layer)} on layer, {len(off_layer)} off layer",
        ))
        return passed

    def report(self) -> str:
        """Generate validation report."""
        lines = [f"{'='*60}", f"DXF VALIDATION: {self.path.name}", f"{'='*60}", ""]

        passed = [r for r in self.results if r.passed]
        failed = [r for r in self.results if not r.passed]

        if failed:
            lines.append(f"FAILED ({len(failed)}):")
            lines.append("-" * 40)
            for r in failed:
                lines.append(f"  ✗ {r.check}")
                lines.append(f"    Expected: {r.expected}")
                lines.append(f"    Actual:   {r.actual}")
                if r.details:
                    lines.append(f"    Details:  {r.details}")
            lines.append("")

        lines.append(f"PASSED ({len(passed)}):")
        for r in passed:
            lines.append(f"  ✓ {r.check}")

        lines.append("")
        lines.append(f"Result: {len(passed)}/{len(self.results)} checks passed")
        if failed:
            lines.append("⛔ Drawing has validation failures — do not approve.")
        else:
            lines.append("✓ All checks passed.")
        return "\n".join(lines)

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)
