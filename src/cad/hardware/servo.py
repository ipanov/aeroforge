"""Micro Servo Models - Build123d Compound with joints.

JX PDI-1109MG (ailerons, elevator, rudder) - 10g, 2.5 kg-cm @ 6V
JX PDI-933MG (flaps) - 13g, 3.5 kg-cm @ 6V

Coordinate system:
- Origin = center of servo body (excluding tabs and shaft)
- X = length (23mm), Y = width (12.5mm), Z = height
- Output shaft on +Z top, offset toward +X
- Mounting tabs at ~60% height from bottom

Joints:
- "bottom": bottom face center (for mounting in pocket)
- "shaft": output shaft top (for horn/arm attachment)
- "mount_left", "mount_right": screw hole centers on mounting tabs

Reference dimensions from JX Servo datasheets:
  1109MG: 23.2 x 12.5 x 25.4mm, ear-to-ear ~32.5mm
  933MG:  23.0 x 12.2 x 29.0mm, ear-to-ear ~32.0mm

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python src/cad/hardware/servo.py
"""

from build123d import *
from ocp_vscode import show

COLOR_SERVO = Color(0.12, 0.15, 0.30)   # Dark blue JX servo
COLOR_SHAFT = Color(0.75, 0.75, 0.75)   # Silver output shaft
COLOR_GEAR_COVER = Color(0.20, 0.22, 0.25)  # Dark gear cover
COLOR_RX = Color(0.1, 0.1, 0.1)         # Black receiver


class MicroServo(Compound):
    """Generic micro servo with mounting tabs, output shaft, and gear cover.

    Features modeled:
    - Rectangular main body with small edge fillets
    - Mounting ears/tabs with M2 through-holes
    - Circular gear cover boss on top face
    - Output shaft with spline cylinder
    - Wire exit channel on bottom-rear
    """

    def __init__(self, length=23.2, width=12.5, height=25.4,
                 tab_thickness=1.5, ear_to_ear=32.5,
                 shaft_diameter=4.8, shaft_height=3.5,
                 spline_diameter=4.2,
                 gear_cover_diameter=10.0, gear_cover_height=1.0,
                 wire_exit_width=4.0, wire_exit_height=2.0,
                 mount_hole_diameter=2.0,
                 label_name="servo"):

        tab_extension = (ear_to_ear - length) / 2  # per side

        with BuildPart() as bp:
            # --- Main body ---
            Box(length, width, height)
            # Small fillets on vertical edges for realism
            fillet(bp.edges().filter_by(Axis.Z), radius=0.8)

            # --- Mounting tabs (flanges) ---
            # Tabs are at ~60% from bottom = 40% from top
            tab_z = height * 0.3 - height / 2  # local Z coord
            with Locations([(0, 0, tab_z)]):
                Box(ear_to_ear, width, tab_thickness)

            # Mounting screw holes (M2)
            for x_sign in [1, -1]:
                hole_x = x_sign * (length / 2 + tab_extension / 2)
                with Locations([(hole_x, 0, tab_z)]):
                    Hole(radius=mount_hole_diameter / 2, depth=tab_thickness + 0.1)

            # --- Gear cover boss on top ---
            gear_x = length * 0.08  # slightly offset toward +X
            with Locations([(gear_x, 0, height / 2)]):
                Cylinder(gear_cover_diameter / 2, gear_cover_height,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))

            # --- Output shaft ---
            shaft_x = gear_x  # shaft centered on gear cover
            with Locations([(shaft_x, 0, height / 2 + gear_cover_height)]):
                Cylinder(shaft_diameter / 2, shaft_height,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))

            # --- Wire exit notch on bottom-rear ---
            wire_x = -length / 2 + wire_exit_width / 2 + 1.0  # rear of servo
            with Locations([(wire_x, 0, -height / 2)]):
                Box(wire_exit_width, wire_exit_height, 1.5,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT)

            # === JOINTS ===

            # Bottom face - for mounting into servo pocket
            RigidJoint("bottom",
                       joint_location=Location((0, 0, -height / 2)))

            # Shaft top - for control horn attachment
            shaft_top_z = height / 2 + gear_cover_height + shaft_height
            RigidJoint("shaft",
                       joint_location=Location((shaft_x, 0, shaft_top_z)))

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
    See src/cad/hardware/receiver.py for the detailed model.
    """

    def __init__(self):
        from src.core.specs import SAILPLANE
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
