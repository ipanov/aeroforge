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

    # Horizontal stabilizer (Design Consensus v2, 2026-03-29)
    h_stab_span: float = 430.0  # mm, all-moving
    h_stab_root_chord: float = 115.0  # Re 61,300 at 8 m/s
    h_stab_tip_chord: float = 75.0  # Tapers to 60mm in last 15mm (swept LE tip)
    h_stab_root_airfoil: str = "HT-14"  # 7.5% thickness
    h_stab_tip_airfoil: str = "HT-13"  # 6.5% thickness, linear blend
    h_stab_area: float = 4080.0  # mm² (~4.08 dm²)
    h_stab_ar: float = 4.53
    h_stab_taper_ratio: float = 0.652
    h_stab_pivot_frac: float = 0.25  # Pivot axis at 25% MAC
    h_stab_rear_spar_frac: float = 0.65  # 2mm CF rod at 65% chord
    h_stab_deflection_up: float = 12.0  # Degrees (nose up)
    h_stab_deflection_down: float = 20.0  # Degrees (nose down)
    h_stab_mass_target: float = 25.0  # grams (22-28g range)

    # Vertical stabilizer (TBD — pending aero/structural consensus)
    v_stab_height: float = 120.0
    v_stab_root_chord: float = 100.0
    v_stab_tip_chord: float = 60.0
    v_stab_airfoil: str = "NACA0010"
    rudder_ratio: float = 0.35  # Rudder as fraction of chord

    # V-tail (if applicable)
    v_tail_angle: float = 40.0  # Degrees from horizontal

    # Tail moment arm (distance from CG to tail quarter-chord)
    # ~660mm for AeroForge (boom ~650mm + pod offset)
    tail_moment: float = 660.0

    # Control throws (H-stab is all-moving, so throws = deflection limits)
    rudder_throw_left: float = 25.0
    rudder_throw_right: float = 25.0


class TailSection:
    """Parametric tail section generator."""

    def __init__(self, spec: TailSectionSpec):
        self.spec = spec

    @property
    def h_stab_mean_chord(self) -> float:
        """H-stab mean aerodynamic chord in mm (trapezoidal approximation)."""
        return (self.spec.h_stab_root_chord + self.spec.h_stab_tip_chord) / 2

    @property
    def h_stab_area_calc(self) -> float:
        """Horizontal stabilizer area in mm² (trapezoidal)."""
        return self.spec.h_stab_span * self.h_stab_mean_chord

    @property
    def v_stab_mean_chord(self) -> float:
        """V-stab mean chord in mm."""
        return (self.spec.v_stab_root_chord + self.spec.v_stab_tip_chord) / 2

    @property
    def v_stab_area(self) -> float:
        """Vertical stabilizer area in mm²."""
        return self.spec.v_stab_height * self.v_stab_mean_chord

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
        h_volume = (self.h_stab_area_calc * self.spec.tail_moment) / (wing_area * wing_chord)
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
        panel_area = self.spec.h_stab_span * self.h_stab_mean_chord / 2

        return {
            "horizontal": 2 * panel_area * math.cos(angle_rad),
            "vertical": 2 * panel_area * math.sin(angle_rad),
        }
