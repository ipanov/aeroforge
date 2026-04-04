"""Mock FEA provider for testing and simple projects."""

from __future__ import annotations

from pathlib import Path

from ..base import ProviderInfo, ProviderRegistry
from .protocol import (
    BucklingResult,
    FEAProvider,
    LoadCase,
    ModalResult,
    StaticResult,
)


class MockFEAProvider:
    """Synthetic FEA results for testing and projects without FEA needs."""

    provider_id: str = "mock"
    display_name: str = "Mock FEA (Synthetic Results)"

    def is_available(self) -> bool:
        return True

    def run_static(
        self,
        step_file: Path,
        load_cases: list[LoadCase],
        output_dir: Path,
    ) -> list[StaticResult]:
        output_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for lc in load_cases:
            # Synthetic: displacement proportional to load factor
            disp = 2.5 * lc.load_factor_g
            stress = 120.0 * lc.load_factor_g
            sf = 1500.0 / stress if stress > 0 else 99.0
            results.append(StaticResult(
                load_case=lc.name,
                max_displacement_mm=round(disp, 2),
                max_von_mises_mpa=round(stress, 1),
                safety_factor=round(sf, 2),
                mesh_nodes=5000,
                mesh_elements=12000,
                passed=sf > 1.5,
            ))
        return results

    def run_modal(
        self,
        step_file: Path,
        n_modes: int,
        output_dir: Path,
    ) -> ModalResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        freqs = [12.5 * (i + 1) for i in range(n_modes)]
        return ModalResult(
            frequencies_hz=freqs,
            mode_shapes=[f"Mode {i+1}" for i in range(n_modes)],
            flutter_speed_ms=45.0,
            flutter_margin=1.5,
        )

    def run_buckling(
        self,
        step_file: Path,
        load_case: LoadCase,
        output_dir: Path,
    ) -> BucklingResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        return BucklingResult(
            load_case=load_case.name,
            buckling_factor=2.1,
            critical_load_n=150.0,
            passed=True,
        )


_instance = MockFEAProvider()
ProviderRegistry.register(
    FEAProvider,
    _instance,
    ProviderInfo(
        provider_id="mock",
        display_name="Mock FEA (Synthetic Results)",
        protocol_type=FEAProvider,
        description="Returns synthetic structural results for testing.",
    ),
)
