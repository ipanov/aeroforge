"""FEA Provider Protocol.

Any structural analysis solver must implement this interface to be
used by the AeroForge workflow engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol, runtime_checkable


@dataclass
class LoadCase:
    """A single load case for FEA analysis."""

    name: str
    load_factor_g: float
    speed_ms: float = 10.0
    description: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class StaticResult:
    """Results from a static FEA analysis."""

    load_case: str
    max_displacement_mm: float
    max_von_mises_mpa: float
    safety_factor: float
    mesh_nodes: int = 0
    mesh_elements: int = 0
    passed: bool = False
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModalResult:
    """Results from a modal (eigenvalue) analysis."""

    frequencies_hz: list[float] = field(default_factory=list)
    mode_shapes: list[str] = field(default_factory=list)
    flutter_speed_ms: Optional[float] = None
    flutter_margin: Optional[float] = None


@dataclass
class BucklingResult:
    """Results from a buckling analysis."""

    load_case: str
    buckling_factor: float
    critical_load_n: float
    passed: bool = False


@runtime_checkable
class FEAProvider(Protocol):
    """Protocol for structural analysis backends."""

    provider_id: str
    display_name: str

    def is_available(self) -> bool:
        """Return True if this provider can run on the current system."""
        ...

    def run_static(
        self,
        step_file: Path,
        load_cases: list[LoadCase],
        output_dir: Path,
    ) -> list[StaticResult]:
        """Run static analysis for given load cases."""
        ...

    def run_modal(
        self,
        step_file: Path,
        n_modes: int,
        output_dir: Path,
    ) -> ModalResult:
        """Run modal analysis to extract natural frequencies."""
        ...

    def run_buckling(
        self,
        step_file: Path,
        load_case: LoadCase,
        output_dir: Path,
    ) -> BucklingResult:
        """Run linear buckling analysis."""
        ...
