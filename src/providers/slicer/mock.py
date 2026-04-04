"""Mock slicer provider for testing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..base import ProviderInfo, ProviderRegistry
from .protocol import SlicerProvider, SliceResult


class MockSlicerProvider:
    """Synthetic slicer results for testing."""

    provider_id: str = "mock"
    display_name: str = "Mock Slicer"

    def is_available(self) -> bool:
        return True

    def slice(
        self, mesh_file: Path, output_dir: Path, profile: dict[str, Any],
    ) -> SliceResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / "mock_sliced.gcode"
        out.write_text("; Mock G-code\n")
        return SliceResult(
            output_file=out, estimated_time_hours=1.5,
            estimated_material_g=25.0, layer_count=200,
        )

    def estimate_time(self, mesh_file: Path, profile: dict[str, Any]) -> float:
        return 1.5

    def estimate_material(self, mesh_file: Path, profile: dict[str, Any]) -> float:
        return 25.0


_instance = MockSlicerProvider()
ProviderRegistry.register(
    SlicerProvider,
    _instance,
    ProviderInfo(
        provider_id="mock",
        display_name="Mock Slicer",
        protocol_type=SlicerProvider,
        description="Returns synthetic slicer results for testing.",
    ),
)
