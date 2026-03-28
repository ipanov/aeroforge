"""Micro Servo Models - Build123d.

JX PDI-1109MG (ailerons, elevator, rudder) and JX PDI-933MG (flaps).
Accurate external dimensions for bay/pocket design and collision checking.

Run via Claude: PYTHONPATH=. python src/cad/hardware/servo.py
"""

from build123d import *
from ocp_vscode import show, Color

# Realistic component colors
COLOR_SERVO_BODY = Color(0.15, 0.18, 0.35)   # Dark blue (JX servo color)
COLOR_SERVO_SHAFT = Color(0.7, 0.7, 0.7)     # Silver aluminum
COLOR_RECEIVER = Color(0.1, 0.1, 0.1)         # Black


def build_servo(
    length: float = 23.2,
    width: float = 12.0,
    height: float = 25.5,
    tab_thickness: float = 1.5,
    tab_width: float = 5.0,
    shaft_diameter: float = 5.0,
    shaft_height: float = 4.0,
) -> Part:
    """Build a generic micro servo model."""
    with BuildPart() as servo:
        # Main body
        Box(length, width, height)

        # Mounting tabs
        tab_z = height * 0.3
        with Locations([(0, 0, tab_z)]):
            Box(length + tab_width * 2, width, tab_thickness,
                align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Mounting screw holes in tabs
        with Locations([
            (length / 2 + tab_width / 2, 0, tab_z),
            (-length / 2 - tab_width / 2, 0, tab_z),
        ]):
            Hole(radius=1.0, depth=tab_thickness)

        # Output shaft on top
        with Locations([(length / 4, 0, height / 2)]):
            Cylinder(radius=shaft_diameter / 2, height=shaft_height,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

    return servo.part


def build_jx_1109mg() -> Part:
    """JX PDI-1109MG - 10g, 2.5 kg-cm, metal gear (ailerons/elevator/rudder)."""
    return build_servo(length=23.2, width=12.0, height=25.5)


def build_jx_933mg() -> Part:
    """JX PDI-933MG - 13g, 3.5 kg-cm, metal gear high torque (flaps)."""
    return build_servo(length=23.0, width=12.0, height=25.5)


def build_turnigy_9x_receiver() -> Part:
    """Turnigy 9X V2 8ch Receiver - 18g, 52x35x15mm."""
    with BuildPart() as rx:
        Box(52, 35, 15)
        fillet(rx.edges().filter_by(Axis.Z), radius=2.0)
    return rx.part


if __name__ == "__main__":
    servo_1109 = build_jx_1109mg()
    servo_933 = build_jx_933mg().moved(Location((40, 0, 0)))
    receiver = build_turnigy_9x_receiver().moved(Location((85, 0, 0)))

    show(
        servo_1109, servo_933, receiver,
        names=["JX 1109MG (10g)", "JX 933MG (13g)", "Turnigy 9X Rx (18g)"],
        colors=[COLOR_SERVO_BODY, COLOR_SERVO_BODY, COLOR_RECEIVER],
    )
