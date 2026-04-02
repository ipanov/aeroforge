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

    # Horizontal stabilizer (Design Consensus v3, 2026-03-30)
    h_stab_type: str = "fixed_elevator"  # fixed stabilizer + 35% chord elevator
    h_stab_planform: str = "superellipse"  # n=2.3
    h_stab_planform_n: float = 2.3
    h_stab_span: float = 430.0  # mm
    h_stab_root_chord: float = 115.0  # Re 61,300 at 8 m/s
    h_stab_root_airfoil: str = "HT-13"  # 6.5% thickness
    h_stab_tip_airfoil: str = "HT-12"  # 5.1% thickness, linear blend
    h_stab_area: float = 4077.0  # mm² (~4.08 dm²)
    h_stab_ar: float = 4.53
    h_stab_oswald_e: float = 0.990
    h_stab_elevator_chord_ratio: float = 0.35  # 35% of local chord
    h_stab_hinge_frac: float = 0.65  # Hinge line at 65% chord
    h_stab_main_spar_frac: float = 0.25  # 3mm CF tube at 25% chord
    h_stab_rear_spar_frac: float = 0.60  # 1.5mm CF rod at 60% chord
    h_stab_elev_stiffener_frac: float = 0.80  # 1mm CF rod at 80% chord
    h_stab_main_spar_od: float = 3.0  # mm, tube OD
    h_stab_main_spar_id: float = 2.0  # mm, tube ID
    h_stab_main_spar_length: float = 390.0  # mm (terminates at 195mm/half)
    h_stab_rear_spar_dia: float = 1.5  # mm, solid rod
    h_stab_elev_stiffener_dia: float = 1.0  # mm, solid rod
    h_stab_hinge_wire_dia: float = 0.5  # mm, music wire
    h_stab_deflection_up: float = 25.0  # Degrees (nose up, elevator)
    h_stab_deflection_down: float = 20.0  # Degrees (nose down, elevator)
    h_stab_mass_target: float = 33.7  # grams (35g hard limit)
    h_stab_te_truncation: float = 0.97  # TE at 97% chord
    h_stab_wall_stab: float = 0.45  # mm, vase mode wall (stab)
    h_stab_wall_elevator: float = 0.40  # mm, vase mode wall (elevator)

    # Vertical stabilizer (integrated into fuselage)
    v_stab_height: float = 165.0
    v_stab_root_chord: float = 180.0
    v_stab_tip_chord: float = 95.0
    v_stab_root_airfoil: str = "HT-14"  # 7.5%
    v_stab_tip_airfoil: str = "HT-12"  # 5.1%
    rudder_ratio: float = 0.35  # Rudder as fraction of chord

    # Tail moment arm
    tail_moment: float = 651.0  # mm, from fuselage consensus

    # Control throws
    rudder_throw_left: float = 25.0
    rudder_throw_right: float = 25.0

    def chord_at(self, eta: float) -> float:
        """Superellipse chord at span fraction eta (0=root, 1=tip)."""
        n = self.h_stab_planform_n
        return self.h_stab_root_chord * (1.0 - abs(eta) ** n) ** (1.0 / n)

    def thickness_ratio_at(self, eta: float) -> float:
        """Blend HT-13 (6.5%) at root to HT-12 (5.1%) at tip."""
        t_root = 0.065  # HT-13
        t_tip = 0.051   # HT-12
        return t_root + (t_tip - t_root) * eta


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

        angle_rad = math.radians(getattr(self.spec, "v_tail_angle", 40.0))

        # Each V-tail panel contributes to both horizontal and vertical
        # Assuming symmetric V-tail
        panel_area = self.spec.h_stab_span * self.h_stab_mean_chord / 2

        return {
            "horizontal": 2 * panel_area * math.cos(angle_rad),
            "vertical": 2 * panel_area * math.sin(angle_rad),
        }
