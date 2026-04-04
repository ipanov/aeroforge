"""Manual manufacturing provider (hand tools, paper folding, etc.)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..base import ProviderInfo, ProviderRegistry
from .protocol import CostEstimate, ManufacturingProvider, ValidationResult


class ManualProvider:
    """Manual manufacturing — hand tools, paper folding, balsa cutting."""

    provider_id: str = "manual"
    display_name: str = "Manual (Hand Tools)"

    def is_available(self) -> bool:
        return True

    def validate_geometry(
        self, step_file: Path, constraints: dict[str, Any],
    ) -> ValidationResult:
        return ValidationResult(
            valid=True,
            warnings=["Manual manufacturing — geometry feasibility is user-assessed"],
        )

    def generate_output(
        self, step_file: Path, output_dir: Path, **kwargs: Any,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        instructions = output_dir / "manual_instructions.md"
        instructions.write_text(
            "# Manual Manufacturing Instructions\n\n"
            "Refer to the 2D drawing for dimensions and assembly sequence.\n"
        )
        return instructions

    def estimate_cost(self, step_file: Path) -> CostEstimate:
        return CostEstimate(
            material_cost=0.10,
            time_hours=0.5,
            notes="Manual build — cost depends on material choice",
        )


_instance = ManualProvider()
ProviderRegistry.register(
    ManufacturingProvider,
    _instance,
    ProviderInfo(
        provider_id="manual",
        display_name="Manual (Hand Tools)",
        protocol_type=ManufacturingProvider,
        description="Manual manufacturing with hand tools, paper folding, etc.",
    ),
)
