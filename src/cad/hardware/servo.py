"""Micro Servo Models - Build123d.

JX PDI-1109MG (ailerons, elevator, rudder) and JX PDI-933MG (flaps).
Accurate external dimensions for bay/pocket design and collision checking.

Run this file directly to view in OCP CAD Viewer:
    python src/cad/hardware/servo.py
"""

from build123d import *
from ocp_vscode import show


def build_servo(
    length: float = 23.2,
    width: float = 12.0,
    height: float = 25.5,
    tab_thickness: float = 1.5,
    tab_width: float = 5.0,
    shaft_diameter: float = 5.0,
    shaft_height: float = 4.0,
    wire_diameter: float = 3.0,
    name: str = "Servo",
) -> Part:
    """Build a generic micro servo model.

    Standard form factor with mounting tabs, output shaft, and wire exit.
    """
    with BuildPart() as servo:
        # Main body
        Box(length, width, height)

        # Mounting tabs (flanges on each side at ~60% height)
        tab_z = height * 0.3  # Tab position from bottom
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

        # Wire exit notch at bottom-rear
        with Locations([(-length / 2, 0, -height / 2 + 2)]):
            Cylinder(radius=wire_diameter / 2, height=5,
                     rotation=(0, 90, 0),
                     align=(Align.CENTER, Align.CENTER, Align.CENTER))

    return servo.part


def build_jx_1109mg() -> Part:
    """JX PDI-1109MG - 10g digital metal gear (ailerons, elevator, rudder)."""
    return build_servo(
        length=23.2, width=12.0, height=25.5,
        name="JX PDI-1109MG",
    )


def build_jx_933mg() -> Part:
    """JX PDI-933MG - 13g digital metal gear high torque (flaps)."""
    return build_servo(
        length=23.0, width=12.0, height=25.5,
        name="JX PDI-933MG",
    )


def build_turnigy_9x_receiver() -> Part:
    """Turnigy 9X V2 8ch Receiver - simple box model."""
    with BuildPart() as rx:
        Box(52, 35, 15)
        fillet(rx.edges().filter_by(Axis.Z), radius=2.0)
    return rx.part


if __name__ == "__main__":
    servo_1109 = build_jx_1109mg()
    servo_933 = build_jx_933mg()
    receiver = build_turnigy_9x_receiver()

    # Position them side by side for viewing
    servo_933_pos = servo_933.moved(Location((35, 0, 0)))
    receiver_pos = receiver.moved(Location((70, 0, 0)))

    show(
        servo_1109, servo_933_pos, receiver_pos,
        names=["JX 1109MG (10g)", "JX 933MG (13g)", "Turnigy 9X Rx"],
    )
