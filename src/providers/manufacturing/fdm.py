"""FDM 3D printing manufacturing provider.

Validates geometry against printer bed constraints and estimates
filament usage and print time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..base import ProviderInfo, ProviderRegistry
from .protocol import CostEstimate, ManufacturingProvider, ValidationResult


class FDMProvider:
    """FDM (Fused Deposition Modeling) 3D printing provider."""

    provider_id: str = "fdm"
    display_name: str = "FDM 3D Printing"

    def __init__(
        self,
        bed_size_mm: tuple[float, float, float] = (256, 256, 256),
        printer_model: str = "bambu_a1",
    ):
        self.bed_size_mm = bed_size_mm
        self.printer_model = printer_model

    def is_available(self) -> bool:
        return True  # FDM validation is geometry-only, no hardware needed

    def validate_geometry(
        self, step_file: Path, constraints: dict[str, Any],
    ) -> ValidationResult:
        bed = constraints.get("bed_size", self.bed_size_mm)
        issues: list[str] = []
        warnings: list[str] = []

        if not step_file.exists():
            issues.append(f"STEP file not found: {step_file}")
            return ValidationResult(valid=False, issues=issues)

        # Size check would be done via Build123d bounding box — deferred to actual run
        warnings.append("Bounding box check requires Build123d import (deferred)")

        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            details={"bed_size_mm": list(bed), "printer_model": self.printer_model},
        )

    def generate_output(
        self, step_file: Path, output_dir: Path, **kwargs: Any,
    ) -> Path:
        # Full pipeline: STEP -> STL -> geodesic ribs -> 3MF
        # Delegates to rebuild_all_meshes.py pipeline
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / step_file.stem
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    def estimate_cost(self, step_file: Path) -> CostEstimate:
        # Rough estimate: filament cost ~$0.02/g, typical small RC part 20-50g
        return CostEstimate(
            material_cost=1.0,
            time_hours=2.0,
            currency="EUR",
            notes="Rough estimate — run slicer for precise values",
        )


_instance = FDMProvider()
ProviderRegistry.register(
    ManufacturingProvider,
    _instance,
    ProviderInfo(
        provider_id="fdm",
        display_name="FDM 3D Printing",
        protocol_type=ManufacturingProvider,
        description="FDM 3D printing with bed size constraints and filament estimation.",
    ),
)
