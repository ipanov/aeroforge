"""Airfoil Analysis Provider Protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class AirfoilPolar:
    """Single-point airfoil analysis result."""

    alpha: float
    cl: float
    cd: float
    cm: float
    reynolds: float
    mach: float = 0.0


@runtime_checkable
class AirfoilProvider(Protocol):
    """Protocol for 2D airfoil analysis backends."""

    provider_id: str
    display_name: str

    def is_available(self) -> bool: ...

    def analyze(
        self,
        airfoil_name: str,
        alpha_range: tuple[float, float],
        alpha_step: float,
        reynolds: float,
        mach: float = 0.0,
    ) -> list[AirfoilPolar]:
        """Run 2D airfoil analysis and return polar data."""
        ...

    def get_polar(
        self,
        airfoil_name: str,
        alpha: float,
        reynolds: float,
        mach: float = 0.0,
    ) -> AirfoilPolar:
        """Get a single operating point."""
        ...
