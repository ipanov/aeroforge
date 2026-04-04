"""Mock airfoil provider for testing."""

from __future__ import annotations

import math

from ..base import ProviderInfo, ProviderRegistry
from .protocol import AirfoilPolar, AirfoilProvider


class MockAirfoilProvider:
    """Thin-airfoil-theory approximation for testing."""

    provider_id: str = "mock"
    display_name: str = "Mock Airfoil (Thin Airfoil Theory)"

    def is_available(self) -> bool:
        return True

    def analyze(
        self,
        airfoil_name: str,
        alpha_range: tuple[float, float],
        alpha_step: float,
        reynolds: float,
        mach: float = 0.0,
    ) -> list[AirfoilPolar]:
        results = []
        a = alpha_range[0]
        while a <= alpha_range[1] + 0.001:
            results.append(self.get_polar(airfoil_name, a, reynolds, mach))
            a += alpha_step
        return results

    def get_polar(
        self,
        airfoil_name: str,
        alpha: float,
        reynolds: float,
        mach: float = 0.0,
    ) -> AirfoilPolar:
        alpha_rad = math.radians(alpha)
        cl = 2 * math.pi * alpha_rad
        cd = 0.006 + cl**2 / (math.pi * 8 * 0.92)
        cm = -0.05
        return AirfoilPolar(
            alpha=alpha, cl=round(cl, 5), cd=round(cd, 6),
            cm=cm, reynolds=reynolds, mach=mach,
        )


_instance = MockAirfoilProvider()
ProviderRegistry.register(
    AirfoilProvider,
    _instance,
    ProviderInfo(
        provider_id="mock",
        display_name="Mock Airfoil (Thin Airfoil Theory)",
        protocol_type=AirfoilProvider,
        description="Thin airfoil theory approximation for testing.",
    ),
)
