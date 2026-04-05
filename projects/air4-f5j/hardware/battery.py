"""3S 1300mAh Racing LiPo Battery Pack - Off-the-shelf component.

Reference: components/reference_models/tattu_1300_reference.png

Coordinate system:
- Origin = center of battery body
- X = longest (78mm), Y = width (38mm), Z = height (28mm)
- Label on +Z face (top)
- Wire exit end = +X

Joints:
- "wire_exit_pos": where positive power lead exits (+X end, upper area)
- "wire_exit_neg": where negative power lead exits (+X end, upper area)
- "balance_exit": where balance lead exits (+X end, side)
- "bottom": bottom face center (for battery tray mounting)
- "top": top face center

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python src/cad/hardware/battery.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build123d import *
from ocp_vscode import show

from specs import SAILPLANE

SPEC = SAILPLANE.battery

POWER_WIRE_SPACING = 5.0  # mm between red/black wire centers

COLOR_PACK = Color(0.08, 0.08, 0.08)
COLOR_LABEL = Color(0.75, 0.65, 0.0)


class BatteryPack(Compound):
    """3S 1300mAh LiPo battery pack (bare, without XT60).

    Simplified but dimensionally accurate body with joints
    at all connection/mounting points.
    """

    def __init__(self):
        with BuildPart() as bp:
            Box(SPEC.length, SPEC.width, SPEC.height)
            fillet(bp.edges(), radius=1.5)

            # Label area on top (thin raised patch)
            with Locations([(0, 0, SPEC.height / 2)]):
                Box(SPEC.length * 0.65, SPEC.width * 0.85, 0.15,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

            # === JOINTS ===

            # Power lead exits: top area of +X face
            # Wires exit pointing in +X direction
            RigidJoint("wire_exit_pos",
                       joint_location=Location(
                           (SPEC.length / 2, POWER_WIRE_SPACING / 2, SPEC.height / 2 - 5)))
            RigidJoint("wire_exit_neg",
                       joint_location=Location(
                           (SPEC.length / 2, -POWER_WIRE_SPACING / 2, SPEC.height / 2 - 5)))

            # Balance lead exit: side of +X end, near bottom
            RigidJoint("balance_exit",
                       joint_location=Location(
                           (SPEC.length / 2 - 5, SPEC.width / 2, -SPEC.height / 2 + 5),
                           (0, 0, 90)))  # points in +Y direction

            # Mounting points
            RigidJoint("bottom",
                       joint_location=Location((0, 0, -SPEC.height / 2)))
            RigidJoint("top",
                       joint_location=Location((0, 0, SPEC.height / 2)))

        super().__init__(bp.part.wrapped, label="battery_3s_1300", joints=bp.joints)
        self.color = COLOR_PACK


class BatteryWithXT60(Compound):
    """Complete battery assembly: pack + XT60 connector.

    The XT60 is connected to the battery's wire exit points.
    In reality there are short power leads between them, but
    for bay sizing the connector position relative to the pack
    is what matters.
    """

    def __init__(self):
        from src.cad.hardware.xt60 import XT60Male

        battery = BatteryPack()
        xt60 = XT60Male()

        # Connect XT60 solder_positive to battery wire_exit_pos
        # This positions the XT60 at the wire exit end of the battery
        battery.joints["wire_exit_pos"].connect_to(xt60.joints["solder_positive"])

        super().__init__(label="battery_with_xt60", children=[battery, xt60])

        # Expose battery joints for further assembly (e.g., into fuselage)
        RigidJoint("bottom", to_part=self,
                   joint_location=Location((0, 0, -SPEC.height / 2)))
        RigidJoint("top", to_part=self,
                   joint_location=Location((0, 0, SPEC.height / 2)))


if __name__ == "__main__":
    # Show bare battery pack
    battery = BatteryPack()
    print(f"Battery Pack:")
    print(f"  Size: {SPEC.length}x{SPEC.width}x{SPEC.height}mm")
    print(f"  Joints: {list(battery.joints.keys())}")

    # Show battery + XT60 assembly
    assembly = BatteryWithXT60()
    bb = assembly.bounding_box()
    print(f"\nBattery + XT60 Assembly:")
    print(f"  Bounding box: {bb.max.X-bb.min.X:.1f} x {bb.max.Y-bb.min.Y:.1f} x {bb.max.Z-bb.min.Z:.1f}mm")
    print(f"  Joints: {list(assembly.joints.keys())}")

    show(assembly, names=["Battery + XT60 Assembly"])
