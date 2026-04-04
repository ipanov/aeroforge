"""Mock CFD provider for testing and simple projects (e.g., paper plane).

Returns synthetic polar data based on thin-airfoil theory approximations.
"""

from __future__ import annotations

import math
from pathlib import Path

from ..base import ProviderInfo, ProviderRegistry
from .protocol import CFDProvider, CFDResult, PolarSweepConfig


class MockCFDProvider:
    """Synthetic CFD results for testing and projects without CFD needs."""

    provider_id: str = "mock"
    display_name: str = "Mock CFD (Synthetic Polars)"
    requires_gpu: bool = False

    def is_available(self) -> bool:
        return True

    def mesh_geometry(
        self,
        step_file: Path,
        output_dir: Path,
        *,
        farfield_mult: float = 20.0,
        mesh_size_factor: float = 1.0,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        mesh_path = output_dir / "mock_mesh.su2"
        mesh_path.write_text("% Mock mesh - no actual geometry\n")
        return mesh_path

    def run_polar_sweep(
        self,
        step_file: Path,
        output_dir: Path,
        config: PolarSweepConfig,
    ) -> list[CFDResult]:
        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[CFDResult] = []

        alpha_min, alpha_max = config.alpha_range
        alpha = alpha_min
        while alpha <= alpha_max + 0.001:
            alpha_rad = math.radians(alpha)
            # Thin airfoil: CL ~ 2*pi*alpha, with stall at ~12 deg
            cl = 2 * math.pi * alpha_rad * (1 - 0.02 * abs(alpha))
            if abs(alpha) > 12:
                cl *= max(0.3, 1 - (abs(alpha) - 12) * 0.1)
            # Parabolic drag polar
            cd_min = 0.008
            cd = cd_min + cl**2 / (math.pi * 10 * 0.95)  # AR=10, e=0.95
            cm = -0.05 - 0.01 * alpha_rad
            l_d = cl / cd if cd > 0 else 0.0

            results.append(CFDResult(
                alpha=round(alpha, 2),
                cl=round(cl, 5),
                cd=round(cd, 6),
                cm=round(cm, 5),
                l_d=round(l_d, 2),
                convergence="converged",
            ))
            alpha += config.alpha_step

        return results

    def extract_results(self, output_dir: Path) -> list[CFDResult]:
        return []


# Auto-register
_instance = MockCFDProvider()
ProviderRegistry.register(
    CFDProvider,
    _instance,
    ProviderInfo(
        provider_id="mock",
        display_name="Mock CFD (Synthetic Polars)",
        protocol_type=CFDProvider,
        description="Returns synthetic polar data for testing and simple projects.",
    ),
)
