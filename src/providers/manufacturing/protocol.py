"""Manufacturing Provider Protocol.

Any manufacturing technique (3D printing, CNC, manual, etc.) must
implement this interface to integrate with the AeroForge workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol, runtime_checkable


@dataclass
class ValidationResult:
    """Result of geometry validation for a manufacturing technique."""

    valid: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class CostEstimate:
    """Estimated cost for manufacturing a part."""

    material_cost: float = 0.0
    time_hours: float = 0.0
    currency: str = "EUR"
    notes: str = ""


@runtime_checkable
class ManufacturingProvider(Protocol):
    """Protocol for manufacturing technique backends."""

    provider_id: str
    display_name: str

    def is_available(self) -> bool:
        """Return True if this provider can run on the current system."""
        ...

    def validate_geometry(
        self,
        step_file: Path,
        constraints: dict[str, Any],
    ) -> ValidationResult:
        """Check if geometry is feasible for this manufacturing technique."""
        ...

    def generate_output(
        self,
        step_file: Path,
        output_dir: Path,
        **kwargs: Any,
    ) -> Path:
        """Generate manufacturing-ready output (toolpaths, fold diagram, etc.)."""
        ...

    def estimate_cost(
        self,
        step_file: Path,
    ) -> CostEstimate:
        """Estimate material cost and time."""
        ...
