"""NeuralFoil airfoil analysis provider.

Wraps AeroSandbox's NeuralFoil for fast 2D airfoil polar computation.
"""

from __future__ import annotations

from ..base import ProviderInfo, ProviderRegistry
from .protocol import AirfoilPolar, AirfoilProvider


class NeuralFoilProvider:
    """NeuralFoil via AeroSandbox for 2D airfoil analysis."""

    provider_id: str = "neuralfoil"
    display_name: str = "NeuralFoil (AeroSandbox)"

    def is_available(self) -> bool:
        try:
            import aerosandbox  # noqa: F401
            return True
        except ImportError:
            return False

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
        import aerosandbox as asb

        af = asb.Airfoil(airfoil_name)
        result = af.get_aero_from_neuralfoil(alpha=alpha, Re=reynolds, mach=mach)
        return AirfoilPolar(
            alpha=alpha,
            cl=float(result["CL"]),
            cd=float(result["CD"]),
            cm=float(result["CM"]),
            reynolds=reynolds,
            mach=mach,
        )


_instance = NeuralFoilProvider()
ProviderRegistry.register(
    AirfoilProvider,
    _instance,
    ProviderInfo(
        provider_id="neuralfoil",
        display_name="NeuralFoil (AeroSandbox)",
        protocol_type=AirfoilProvider,
        description="NeuralFoil via AeroSandbox for fast 2D airfoil analysis.",
    ),
)
