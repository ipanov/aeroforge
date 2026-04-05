"""SU2 CFD provider with CUDA GPU acceleration.

Wraps the existing ``src.analysis.cfd_pipeline`` module, delegating
mesh generation and solver execution to the established SU2+Gmsh pipeline.

CUDA validation: the provider checks that the SU2 binary was compiled with
CUDA support before reporting itself as available. If CUDA is missing,
``is_available()`` returns False and the CPU-only fallback provider should
be used instead.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..base import ProviderInfo, ProviderRegistry
from .protocol import CFDProvider, CFDResult, PolarSweepConfig


def _check_cuda_in_binary() -> bool:
    """Check whether the installed SU2_CFD binary has CUDA support.

    Runs ``SU2_CFD --help`` and looks for CUDA-related strings in output.
    Also checks nvidia-smi to confirm a GPU is accessible.
    """
    su2_path = shutil.which("SU2_CFD")
    if su2_path is None:
        return False

    # Check SU2 binary for CUDA indicators
    try:
        result = subprocess.run(
            [su2_path, "--help"],
            capture_output=True, text=True, timeout=10,
        )
        output = (result.stdout + result.stderr).upper()
        has_cuda_binary = "CUDA" in output or "GPU" in output
    except (subprocess.TimeoutExpired, OSError):
        has_cuda_binary = False

    # Also check that nvidia-smi sees a GPU
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        )
        has_gpu = result.returncode == 0 and len(result.stdout.strip()) > 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        has_gpu = False

    return has_cuda_binary and has_gpu


def estimate_cpu_time(mesh_elements: int, n_alphas: int, iters: int = 300) -> float:
    """Estimate wall-clock seconds for a CPU-only SU2 run.

    Rough empirical formula: ~0.005 s per element per iteration for Euler.
    """
    time_per_alpha = mesh_elements * iters * 5e-6  # seconds
    return time_per_alpha * n_alphas


class SU2CudaProvider:
    """SU2 CFD with NVIDIA CUDA GPU acceleration."""

    provider_id: str = "su2_cuda"
    display_name: str = "SU2 (CUDA GPU)"
    requires_gpu: bool = True

    _cuda_checked: bool = False
    _cuda_available: bool = False

    def _ensure_cuda_checked(self) -> bool:
        if not self._cuda_checked:
            self._cuda_available = _check_cuda_in_binary()
            self._cuda_checked = True
        return self._cuda_available

    def is_available(self) -> bool:
        has_tools = (
            shutil.which("SU2_CFD") is not None
            and shutil.which("gmsh") is not None
        )
        if not has_tools:
            return False
        return self._ensure_cuda_checked()

    def validate_or_raise(self, mesh_elements: int = 50_000, n_alphas: int = 7) -> None:
        """Validate CUDA availability or raise with CPU time estimate.

        Call this before starting a CFD run. If CUDA is not available,
        raises RuntimeError with an estimated CPU wall time so the caller
        can decide whether to fall back to CPU.
        """
        if self._ensure_cuda_checked():
            return

        est = estimate_cpu_time(mesh_elements, n_alphas)
        minutes = est / 60
        raise RuntimeError(
            f"SU2 CUDA GPU acceleration is NOT available. "
            f"The installed SU2_CFD binary was compiled without CUDA support. "
            f"Estimated CPU-only time: {minutes:.0f} minutes "
            f"({mesh_elements:,} elements x {n_alphas} alphas x 300 iters). "
            f"To fix: rebuild SU2 with -Denable-cuda=true. "
            f"To proceed on CPU anyway, use the 'su2_cpu' provider."
        )

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
