"""Slicer Provider Protocol.

Any 3D printing slicer must implement this interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass
class SliceResult:
    """Result from slicing a 3D model."""

    output_file: Path
    estimated_time_hours: float = 0.0
    estimated_material_g: float = 0.0
    layer_count: int = 0
    details: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class SlicerProvider(Protocol):
    """Protocol for 3D printing slicer backends."""

    provider_id: str
    display_name: str

    def is_available(self) -> bool: ...

    def slice(
        self,
        mesh_file: Path,
        output_dir: Path,
        profile: dict[str, Any],
    ) -> SliceResult:
        """Slice a mesh file and return the result."""
        ...

    def estimate_time(
        self,
        mesh_file: Path,
        profile: dict[str, Any],
    ) -> float:
        """Estimate print time in hours without full slicing."""
        ...

    def estimate_material(
        self,
        mesh_file: Path,
        profile: dict[str, Any],
    ) -> float:
        """Estimate material usage in grams."""
        ...
