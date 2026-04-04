"""SU2 CFD provider with CUDA GPU acceleration.

Wraps the existing ``src.analysis.cfd_pipeline`` module, delegating
mesh generation and solver execution to the established SU2+Gmsh pipeline.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ..base import ProviderInfo, ProviderRegistry
from .protocol import CFDProvider, CFDResult, PolarSweepConfig


class SU2CudaProvider:
    """SU2 CFD with NVIDIA CUDA GPU acceleration."""

    provider_id: str = "su2_cuda"
    display_name: str = "SU2 (CUDA GPU)"
    requires_gpu: bool = True

    def is_available(self) -> bool:
        return shutil.which("SU2_CFD") is not None and shutil.which("gmsh") is not None

    def mesh_geometry(
        self,
        step_file: Path,
        output_dir: Path,
        *,
        farfield_mult: float = 20.0,
        mesh_size_factor: float = 1.0,
    ) -> Path:
        from src.analysis.cfd_pipeline import generate_mesh

        output_dir.mkdir(parents=True, exist_ok=True)
        mesh_path = output_dir / "mesh.su2"
        generate_mesh(
            step_file, mesh_path,
            farfield_mult=farfield_mult,
            mesh_size_factor=mesh_size_factor,
        )
        return mesh_path

    def run_polar_sweep(
        self,
        step_file: Path,
        output_dir: Path,
        config: PolarSweepConfig,
    ) -> list[CFDResult]:
        from src.analysis.cfd_pipeline import run_polar_sweep as _run

        raw_results = _run(
            step_file=step_file,
            output_dir=output_dir,
            alpha_range=config.alpha_range,
            alpha_step=config.alpha_step,
            solver_type=config.solver_type,
            reynolds_number=config.reynolds_number,
            chord=config.chord_m,
            speed=config.speed_ms,
        )
        return [
            CFDResult(
                alpha=r.alpha, cl=r.cl, cd=r.cd, cm=r.cm,
                l_d=r.l_d, convergence=r.convergence,
            )
            for r in raw_results
        ]

    def extract_results(self, output_dir: Path) -> list[CFDResult]:
        from src.analysis.cfd_pipeline import extract_polar

        history = output_dir / "history.csv"
        if not history.exists():
            return []
        raw = extract_polar(history)
        return [
            CFDResult(alpha=r.alpha, cl=r.cl, cd=r.cd, cm=r.cm, l_d=r.l_d)
            for r in raw
        ]


# Auto-register
_instance = SU2CudaProvider()
ProviderRegistry.register(
    CFDProvider,
    _instance,
    ProviderInfo(
        provider_id="su2_cuda",
        display_name="SU2 (CUDA GPU)",
        protocol_type=CFDProvider,
        requires_gpu=True,
        requires_software=["SU2_CFD", "gmsh"],
        description="SU2 CFD solver with NVIDIA CUDA GPU acceleration.",
    ),
)
