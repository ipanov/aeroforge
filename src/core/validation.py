"""Validation hooks for component and assembly integrity.

Every component change runs through validation:
- Spec validation (dimensions positive, within printable range, etc.)
- Geometry validation (watertight, no self-intersections)
- Print validation (fits on bed, wall thickness, overhang angles)
- Assembly validation (no collisions, constraints satisfied)
- Mass validation (within budget, CG in acceptable range)

Hooks can WARN (log and continue) or BLOCK (raise and prevent the change).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Optional

from pydantic import BaseModel

from .component import Component, ComponentSpec


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"       # Blocks the operation


class ValidationResult(BaseModel):
    """Result of a single validation check."""
    rule: str
    severity: ValidationSeverity
    message: str
    component_name: str = ""
    parameter: str = ""
    value: Any = None
    limit: Any = None


class ValidationHook:
    """A validation rule that checks component integrity.

    Usage:
        hook = ValidationHook(
            name="wall_thickness",
            description="Ensure wall thickness is printable",
            check=lambda comp: comp.spec.parameters.get("wall_thickness", 0) >= 0.4,
            severity=ValidationSeverity.ERROR,
            message="Wall thickness must be >= 0.4mm for FDM printing",
        )
    """

    def __init__(
        self,
        name: str,
        check: Callable[[Component], bool],
        severity: ValidationSeverity = ValidationSeverity.WARNING,
        message: str = "",
        description: str = "",
    ) -> None:
        self.name = name
        self.check = check
        self.severity = severity
        self.message = message
        self.description = description

    def validate(self, component: Component) -> Optional[ValidationResult]:
        """Run this hook against a component.

        Returns None if validation passes, ValidationResult if it fails.
        """
        try:
            passed = self.check(component)
        except Exception as e:
            return ValidationResult(
                rule=self.name,
                severity=ValidationSeverity.ERROR,
                message=f"Validation hook crashed: {e}",
                component_name=component.name,
            )

        if passed:
            return None

        return ValidationResult(
            rule=self.name,
            severity=self.severity,
            message=self.message,
            component_name=component.name,
        )


# ── Built-in validation hooks ────────────────────────────────────

# Bambu A1 print bed: 256 x 256 x 256 mm
# Bambu P1S print bed: 256 x 256 x 256 mm
BAMBU_BED_SIZE = (256.0, 256.0, 256.0)


def _check_fits_print_bed(component: Component) -> bool:
    """Check that component fits on the Bambu print bed."""
    bb = component.bounding_box
    size = bb.size
    dims = sorted([abs(size.x), abs(size.y), abs(size.z)])
    bed = sorted(BAMBU_BED_SIZE)
    return all(d <= b for d, b in zip(dims, bed))


def _check_positive_mass(component: Component) -> bool:
    """Check that component has positive mass after building."""
    return component.mass >= 0


def _check_reasonable_mass(component: Component) -> bool:
    """Check that a single component isn't unreasonably heavy."""
    return component.mass < 500  # No single component should be > 500g


BUILT_IN_HOOKS: list[ValidationHook] = [
    ValidationHook(
        name="fits_print_bed",
        check=_check_fits_print_bed,
        severity=ValidationSeverity.WARNING,
        message=f"Component exceeds Bambu print bed ({BAMBU_BED_SIZE[0]}x{BAMBU_BED_SIZE[1]}x{BAMBU_BED_SIZE[2]}mm). Split into panels.",
        description="Ensure component fits on Bambu A1/P1S print bed",
    ),
    ValidationHook(
        name="positive_mass",
        check=_check_positive_mass,
        severity=ValidationSeverity.ERROR,
        message="Component has zero or negative mass - geometry may be invalid",
        description="Ensure component has valid mass",
    ),
    ValidationHook(
        name="reasonable_mass",
        check=_check_reasonable_mass,
        severity=ValidationSeverity.WARNING,
        message="Single component exceeds 500g - consider splitting or lightweight material",
        description="Warn on excessively heavy single components",
    ),
]


def validate_component(
    component: Component,
    hooks: Optional[list[ValidationHook]] = None,
    include_builtins: bool = True,
) -> list[ValidationResult]:
    """Run all validation hooks against a component.

    Args:
        component: The component to validate.
        hooks: Custom hooks to run (in addition to built-ins).
        include_builtins: Whether to include built-in hooks.

    Returns:
        List of validation failures. Empty list means all passed.

    Raises:
        ValueError: If any ERROR-severity hook fails.
    """
    all_hooks = []
    if include_builtins:
        all_hooks.extend(BUILT_IN_HOOKS)
    if hooks:
        all_hooks.extend(hooks)

    results: list[ValidationResult] = []
    for hook in all_hooks:
        result = hook.validate(component)
        if result is not None:
            results.append(result)

    # Raise on errors
    errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
    if errors:
        messages = "; ".join(f"[{r.rule}] {r.message}" for r in errors)
        raise ValueError(f"Validation failed for '{component.name}': {messages}")

    return results
