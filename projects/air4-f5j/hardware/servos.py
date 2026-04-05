"""F5J project-specific servo and receiver models.

JX PDI-1109MG (ailerons, elevator, rudder) - 10g, 2.5 kg-cm @ 6V
JX PDI-933MG (flaps) - 13g, 3.5 kg-cm @ 6V
FlyskyIA6B simplified receiver model

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python projects/air4-f5j/hardware/servos.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build123d import *
from ocp_vscode import show

from src.cad.hardware.servo import MicroServo, COLOR_SERVO, COLOR_RX
from specs import SAILPLANE


class JX_PDI_1109MG(MicroServo):
    """JX PDI-1109MG: 10g, 2.5 kg-cm @ 6V, for ailerons/elevator/rudder.

    Dimensions: 23.2 x 12.5 x 25.4mm, ear-to-ear 32.5mm
    21T spline, wire ~150mm with JR connector
    """
    def __init__(self):
        super().__init__(
            length=23.2, width=12.5, height=25.4,
            tab_thickness=1.5, ear_to_ear=32.5,
            shaft_diameter=4.8, shaft_height=3.5,
            spline_diameter=4.2,
            gear_cover_diameter=10.0, gear_cover_height=1.0,
            mount_hole_diameter=2.0,
            label_name="JX_PDI_1109MG",
        )


class JX_PDI_933MG(MicroServo):
    """JX PDI-933MG: 13g, 3.5 kg-cm @ 6V, for flaps (high torque).

    Dimensions: 23.0 x 12.2 x 29.0mm, ear-to-ear 32.0mm
    21T spline, wire ~150mm with JR connector
    """
    def __init__(self):
        super().__init__(
            length=23.0, width=12.2, height=29.0,
            tab_thickness=1.5, ear_to_ear=32.0,
            shaft_diameter=4.8, shaft_height=3.5,
            spline_diameter=4.2,
            gear_cover_diameter=10.0, gear_cover_height=1.0,
            mount_hole_diameter=2.0,
            label_name="JX_PDI_933MG",
        )


class FlyskyIA6B(Compound):
    """Flysky FS-iA6B Receiver - 18g, 47.2x26.2x15mm.

    Compatible with Turnigy 9X V2 transmitter.
    See projects/air4-f5j/hardware/receiver.py for the detailed model.
    """

    def __init__(self):
        spec = SAILPLANE.receiver
        L, W, H = spec.length, spec.width, spec.height

        with BuildPart() as bp:
            Box(L, W, H)
            fillet(bp.edges().filter_by(Axis.Z), radius=2.0)

            RigidJoint("bottom", joint_location=Location((0, 0, -H / 2)))
            RigidJoint("top", joint_location=Location((0, 0, H / 2)))
            # Antenna exit: top of +X face
            RigidJoint("antenna", joint_location=Location((L / 2, 0, H / 2 - 3)))
            # Servo pin headers: -Y side
            RigidJoint("pins", joint_location=Location((0, -W / 2, 0), (0, 0, -90)))

        super().__init__(bp.part.wrapped, label="Flysky_FS_iA6B", joints=bp.joints)
        self.color = COLOR_RX


# Backward compatibility alias
Turnigy9XReceiver = FlyskyIA6B


if __name__ == "__main__":
    servo_a = JX_PDI_1109MG()
    servo_f = JX_PDI_933MG()

    # Place side by side for viewing
    servo_f_show = JX_PDI_933MG()

    show(
        servo_a,
        servo_f_show.moved(Location((40, 0, 0))),
        names=["JX 1109MG (10g)", "JX 933MG (13g)"],
    )

    print(f"JX 1109MG bounding box: {servo_a.bounding_box()}")
    print(f"JX 1109MG joints: {list(servo_a.joints.keys())}")
    print(f"JX 933MG bounding box: {servo_f_show.bounding_box()}")
    print(f"JX 933MG joints: {list(servo_f_show.joints.keys())}")
