"""Micro Servo Models - Build123d Compound with joints.

JX PDI-1109MG (ailerons, elevator, rudder) - 10g
JX PDI-933MG (flaps) - 13g

Coordinate system:
- Origin = center of servo body
- X = length (23mm), Y = width (12mm), Z = height (25.5mm)
- Output shaft on +Z top, offset toward +X
- Mounting tabs at ~60% height

Joints:
- "bottom": bottom face center (for mounting in pocket)
- "shaft": output shaft top (for horn/arm attachment)
- "mount_left", "mount_right": screw hole centers on mounting tabs

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python src/cad/hardware/servo.py
"""

from build123d import *
from ocp_vscode import show

COLOR_SERVO = Color(0.12, 0.15, 0.30)   # Dark blue JX servo
COLOR_SHAFT = Color(0.75, 0.75, 0.75)   # Silver output shaft
COLOR_RX = Color(0.1, 0.1, 0.1)         # Black receiver


class MicroServo(Compound):
    """Generic micro servo with mounting tabs and output shaft."""

    def __init__(self, length=23.2, width=12.0, height=25.5,
                 tab_thickness=1.5, tab_extension=5.0,
                 shaft_diameter=5.0, shaft_height=4.0,
                 label_name="servo"):

        with BuildPart() as bp:
            # Main body
            Box(length, width, height)

            # Mounting tabs (flanges)
            tab_z = height * 0.3 - height / 2  # 60% from bottom, in local coords
            with Locations([(0, 0, tab_z)]):
                Box(length + tab_extension * 2, width, tab_thickness)

            # Mounting screw holes
            for x_sign in [1, -1]:
                with Locations([(x_sign * (length / 2 + tab_extension / 2), 0, tab_z)]):
                    Hole(radius=1.0, depth=tab_thickness + 0.1)

            # Output shaft cylinder on top
            shaft_x = length / 4  # offset toward +X like real servos
            with Locations([(shaft_x, 0, height / 2)]):
                Cylinder(shaft_diameter / 2, shaft_height,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))

            # === JOINTS ===

            # Bottom face - for mounting into servo pocket
            RigidJoint("bottom",
                       joint_location=Location((0, 0, -height / 2)))

            # Shaft top - for control horn attachment
            RigidJoint("shaft",
                       joint_location=Location((shaft_x, 0, height / 2 + shaft_height)))

            # Mounting screw holes
            RigidJoint("mount_left",
                       joint_location=Location(
                           (-length / 2 - tab_extension / 2, 0, tab_z)))
            RigidJoint("mount_right",
                       joint_location=Location(
                           (length / 2 + tab_extension / 2, 0, tab_z)))

        super().__init__(bp.part.wrapped, label=label_name, joints=bp.joints)
        self.color = COLOR_SERVO


class JX_PDI_1109MG(MicroServo):
    """JX PDI-1109MG: 10g, 2.5 kg-cm, for ailerons/elevator/rudder."""
    def __init__(self):
        super().__init__(length=23.2, width=12.0, height=25.5,
                         label_name="JX_PDI_1109MG")


class JX_PDI_933MG(MicroServo):
    """JX PDI-933MG: 13g, 3.5 kg-cm, for flaps (high torque)."""
    def __init__(self):
        super().__init__(length=23.0, width=12.0, height=25.5,
                         label_name="JX_PDI_933MG")


class Turnigy9XReceiver(Compound):
    """Turnigy 9X V2 8ch Receiver - 18g, 52x35x15mm."""

    def __init__(self):
        with BuildPart() as bp:
            Box(52, 35, 15)
            fillet(bp.edges().filter_by(Axis.Z), radius=2.0)

            RigidJoint("bottom", joint_location=Location((0, 0, -7.5)))
            RigidJoint("top", joint_location=Location((0, 0, 7.5)))

        super().__init__(bp.part.wrapped, label="Turnigy_9X_Rx", joints=bp.joints)
        self.color = COLOR_RX


if __name__ == "__main__":
    servo_a = JX_PDI_1109MG()
    servo_f = JX_PDI_933MG()
    rx = Turnigy9XReceiver()

    # Place side by side for viewing
    servo_f_pos = JX_PDI_933MG()
    servo_a.joints["bottom"].connect_to(servo_f_pos.joints["bottom"])
    # That would stack them - instead just show separately
    servo_f_show = JX_PDI_933MG()
    rx_show = Turnigy9XReceiver()

    show(
        servo_a,
        servo_f_show.moved(Location((40, 0, 0))),
        rx_show.moved(Location((85, 0, 0))),
        names=["JX 1109MG (10g)", "JX 933MG (13g)", "Turnigy 9X Rx (18g)"],
    )

    print(f"JX 1109MG joints: {list(servo_a.joints.keys())}")
    print(f"JX 933MG joints: {list(servo_f_show.joints.keys())}")
    print(f"Receiver joints: {list(rx_show.joints.keys())}")
