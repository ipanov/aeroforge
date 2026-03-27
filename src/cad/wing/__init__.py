"""Parametric wing sections using Build123d.

This module handles:
- Wing planform generation (tapered, elliptical, etc.)
- Rib spacing and structure
- Spar placement
- Skin generation
"""

from dataclasses import dataclass
from typing import Optional, List
import math


@dataclass
class WingSectionSpec:
    """Specification for a wing section.

    All dimensions in mm.
    """
    root_chord: float = 200.0      # Root chord
    tip_chord: float = 100.0       # Tip chord
    span: float = 500.0            # Section span (half-wing)
    sweep_angle: float = 2.0       # Sweep angle in degrees
    dihedral: float = 3.0          # Dihedral angle in degrees
    twist: float = -2.0            # Washout (negative = tip nose down)
    airfoil_root: str = "RG-15"    # Root airfoil
    airfoil_tip: str = "RG-15"     # Tip airfoil (can differ)
    rib_count: int = 10            # Number of ribs
    rib_thickness: float = 2.0     # Rib wall thickness
    spar_diameter: float = 8.0     # Main spar diameter


class WingSection:
    """Parametric wing section generator."""

    def __init__(self, spec: WingSectionSpec):
        self.spec = spec
        self._validate_spec()

    def _validate_spec(self) -> None:
        """Validate wing specification."""
        if self.spec.root_chord <= 0:
            raise ValueError("Root chord must be positive")
        if self.spec.tip_chord <= 0:
            raise ValueError("Tip chord must be positive")
        if self.spec.span <= 0:
            raise ValueError("Span must be positive")
        if self.spec.rib_count < 2:
            raise ValueError("Need at least 2 ribs")

    def chord_at_position(self, y: float) -> float:
        """Calculate chord at span position y.

        Args:
            y: Span position (0 = root, span = tip)

        Returns:
            Chord length at position y
        """
        taper_ratio = self.spec.tip_chord / self.spec.root_chord
        return self.spec.root_chord * (1 - (1 - taper_ratio) * (y / self.spec.span))

    def twist_at_position(self, y: float) -> float:
        """Calculate twist (washout) at span position.

        Args:
            y: Span position (0 = root, span = tip)

        Returns:
            Twist angle in degrees
        """
        # Linear twist distribution
        return self.spec.twist * (y / self.spec.span)

    def rib_positions(self) -> List[float]:
        """Calculate rib positions along span.

        Returns:
            List of y-positions for each rib
        """
        # Evenly spaced ribs
        return [i * self.spec.span / (self.spec.rib_count - 1)
                for i in range(self.spec.rib_count)]

    def generate_rib(self, position: float) -> dict:
        """Generate rib specification at given span position.

        Args:
            position: Span position (0 = root)

        Returns:
            Dictionary with rib parameters
        """
        chord = self.chord_at_position(position)
        twist = self.twist_at_position(position)

        # Sweep offset
        sweep_offset = position * math.tan(math.radians(self.spec.sweep_angle))

        # Dihedral height
        dihedral_height = position * math.tan(math.radians(self.spec.dihedral))

        return {
            "position": position,
            "chord": chord,
            "twist": twist,
            "sweep_offset": sweep_offset,
            "dihedral_height": dihedral_height,
            "thickness": self.spec.rib_thickness,
            "spar_hole_diameter": self.spec.spar_diameter,
        }

    def generate_all_ribs(self) -> List[dict]:
        """Generate specifications for all ribs.

        Returns:
            List of rib specifications
        """
        return [self.generate_rib(pos) for pos in self.rib_positions()]

    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio (full wing)."""
        # AR = span² / area, for full wing multiply span by 2
        full_span = self.spec.span * 2
        avg_chord = (self.spec.root_chord + self.spec.tip_chord) / 2
        return full_span / avg_chord

    @property
    def taper_ratio(self) -> float:
        """Wing taper ratio (tip/root)."""
        return self.spec.tip_chord / self.spec.root_chord
