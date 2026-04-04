"""Mock manufacturing provider for testing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..base import ProviderInfo, ProviderRegistry
from .protocol import CostEstimate, ManufacturingProvider, ValidationResult


class MockManufacturingProvider:
    """Always-valid manufacturing provider for testing."""

    provider_id: str = "mock"
    display_name: str = "Mock Manufacturing"

    def is_available(self) -> bool:
        return True

    def validate_geometry(
        self, step_file: Path, constraints: dict[str, Any],
    ) -> ValidationResult:
        return ValidationResult(valid=True)

    def generate_output(
        self, step_file: Path, output_dir: Path, **kwargs: Any,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / "mock_output.txt"
        out.write_text("Mock manufacturing output\n")
        return out

    def estimate_cost(self, step_file: Path) -> CostEstimate:
        return CostEstimate(material_cost=0.0, time_hours=0.0, notes="Mock estimate")


_instance = MockManufacturingProvider()
ProviderRegistry.register(
    ManufacturingProvider,
    _instance,
    ProviderInfo(
        provider_id="mock",
        display_name="Mock Manufacturing",
        protocol_type=ManufacturingProvider,
        description="Always-valid manufacturing provider for testing.",
    ),
)
