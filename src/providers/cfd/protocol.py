"""CFD Provider Protocol.

Any CFD solver that can mesh geometry and run polar sweeps must
implement this interface to be used by the AeroForge workflow engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol, runtime_checkable


@dataclass
class CFDResult:
    """Single data point from a CFD analysis."""

    alpha: float
    cl: float
    cd: float
    cm: float
    cl_alpha: Optional[float] = None
    l_d: Optional[float] = None
    cd_induced: Optional[float] = None
    cd_parasitic: Optional[float] = None
    convergence: Optional[str] = None
    iterations: Optional[int] = None


@dataclass
class PolarSweepConfig:
    """Configuration for a polar sweep."""

    alpha_range: tuple[float, float] = (-5.0, 15.0)
    alpha_step: float = 1.0
    reynolds_number: float = 100_000.0
    chord_m: float = 0.17
    speed_ms: float = 10.0
    solver_type: str = "EULER"  # EULER, RANS
    turbulence_model: str = "SA"
    use_gpu: bool = False
    num_processors: int = 1
    extra: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class CFDProvider(Protocol):
    """Protocol for CFD analysis backends."""

    provider_id: str
    display_name: str
    requires_gpu: bool

    def is_available(self) -> bool:
        """Return True if this provider can run on the current system."""
        ...

    def mesh_geometry(
        self,
        step_file: Path,
        output_dir: Path,
        *,
        farfield_mult: float = 20.0,
        mesh_size_factor: float = 1.0,
    ) -> Path:
        """Generate a mesh from STEP geometry. Returns path to mesh file."""
        ...

    def run_polar_sweep(
        self,
        step_file: Path,
        output_dir: Path,
        config: PolarSweepConfig,
    ) -> list[CFDResult]:
        """Run a complete alpha sweep. Returns polar results."""
        ...

    def extract_results(self, output_dir: Path) -> list[CFDResult]:
        """Extract results from a previous run's output directory."""
        ...
