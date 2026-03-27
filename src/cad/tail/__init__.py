"""Tail section design (empennage).

This module handles:
- Horizontal stabilizer
- Vertical stabilizer
- V-tail configuration
- T-tail configuration
- Control surface sizing
"""

from dataclasses import dataclass
from typing import Literal, Optional
import math


@dataclass
class TailSectionSpec:
    """Specification for tail section.

    All dimensions in mm.
    """
    # Configuration
    tail_type: Literal["conventional", "v_tail", "t_tail"] = "conventional"

    # Horizontal stabilizer
    h_stab_span: float = 300.0
    h_stab_chord: float = 60.0
    h_stab_airfoil: str = "NACA0010"
    elevator_ratio: float = 0.35  # Elevator as fraction of chord

    # Vertical stabilizer
    v_stab_height: float = 100.0
    v_stab_chord: float = 80.0
    v_stab_airfoil: str = "NACA0010"
    rudder_ratio: float = 0.40  # Rudder as fraction of chord

    # V-tail (if applicable)
    v_tail_angle: float = 40.0  # Degrees from horizontal

    # Tail moment arm (distance from CG to tail quarter-chord)
    tail_moment: float = 400.0

    # Control throws
    elevator_throw_up: float = 20.0  # Degrees
    elevator_throw_down: float = 15.0
    rudder_throw_left: float = 25.0
    rudder_throw_right: float = 25.0


class TailSection:
    """Parametric tail section generator."""

    def __init__(self, spec: TailSectionSpec):
        self.spec = spec

    @property
    def h_stab_area(self) -> float:
        """Horizontal stabilizer area in mm²."""
        return self.spec.h_stab_span * self.spec.h_stab_chord

    @property
    def v_stab_area(self) -> float:
        """Vertical stabilizer area in mm²."""
        return self.spec.v_stab_height * self.spec.v_stab_chord

    @property
    def elevator_area(self) -> float:
        """Elevator area in mm²."""
        return self.h_stab_area * self.spec.elevator_ratio

    @property
    def rudder_area(self) -> float:
        """Rudder area in mm²."""
        return self.v_stab_area * self.spec.rudder_ratio

    def calculate_tail_volume(self, wing_area: float, wing_chord: float) -> dict:
        """Calculate tail volume coefficients.

        Args:
            wing_area: Wing area in mm²
            wing_chord: Wing mean aerodynamic chord in mm

        Returns:
            Dictionary with tail volume coefficients
        """
        h_volume = (self.h_stab_area * self.spec.tail_moment) / (wing_area * wing_chord)
        v_volume = (self.v_stab_area * self.spec.tail_moment) / (wing_area * wing_chord)

        return {
            "horizontal_volume": h_volume,
            "vertical_volume": v_volume,
            "recommended_h_range": (0.3, 0.6),
            "recommended_v_range": (0.02, 0.05),
        }

    def get_v_tail_projected_areas(self) -> dict:
        """Calculate projected areas for V-tail configuration.

        Returns:
            Dictionary with horizontal and vertical projected areas
        """
        if self.spec.tail_type != "v_tail":
            return {"horizontal": self.h_stab_area, "vertical": self.v_stab_area}

        angle_rad = math.radians(self.spec.v_tail_angle)

        # Each V-tail panel contributes to both horizontal and vertical
        # Assuming symmetric V-tail
        panel_area = self.spec.h_stab_span * self.spec.h_stab_chord / 2

        return {
            "horizontal": 2 * panel_area * math.cos(angle_rad),
            "vertical": 2 * panel_area * math.sin(angle_rad),
        }
