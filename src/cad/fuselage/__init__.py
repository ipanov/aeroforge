"""Fuselage pod and boom design.

This module handles:
- Nose cone design
- Pod geometry (motor, battery, servos)
- Tail boom (carbon tube or 3D printed)
- CG adjustment features
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FuselagePodSpec:
    """Specification for fuselage pod.

    All dimensions in mm.
    """
    # Pod dimensions
    pod_length: float = 300.0
    pod_max_diameter: float = 45.0
    nose_length: float = 80.0

    # Boom
    boom_diameter: float = 12.0
    boom_length: float = 600.0

    # Component bays
    motor_bay_length: float = 40.0
    battery_bay_length: float = 60.0
    receiver_bay_length: float = 30.0
    servo_bay_length: float = 50.0

    # Wall thickness
    wall_thickness: float = 1.5

    # CG adjustment
    cg_position: float = 150.0  # mm from nose


class FuselagePod:
    """Parametric fuselage pod generator."""

    def __init__(self, spec: FuselagePodSpec):
        self.spec = spec

    def get_cg_position(self) -> float:
        """Get CG position from nose in mm."""
        return self.spec.cg_position

    def get_component_positions(self) -> dict:
        """Calculate component bay positions.

        Returns:
            Dictionary with component positions (start, end)
        """
        pos = 0.0
        positions = {}

        # Nose cone
        pos = self.spec.nose_length

        # Motor bay (right behind spinner)
        positions["motor"] = {
            "start": pos,
            "end": pos + self.spec.motor_bay_length,
        }
        pos += self.spec.motor_bay_length

        # Battery bay (adjustable for CG)
        positions["battery"] = {
            "start": pos,
            "end": pos + self.spec.battery_bay_length,
        }
        pos += self.spec.battery_bay_length

        # Receiver bay
        positions["receiver"] = {
            "start": pos,
            "end": pos + self.spec.receiver_bay_length,
        }
        pos += self.spec.receiver_bay_length

        # Servo bay (wing servos)
        positions["servos"] = {
            "start": pos,
            "end": pos + self.spec.servo_bay_length,
        }

        return positions
