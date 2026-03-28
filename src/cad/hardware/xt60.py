"""XT60 Male Connector - Off-the-shelf component.

Uses KiCad/Amass reference STEP model for accurate geometry.
Defines joints at connection points for constraint-based assembly.

Coordinate system (after import and centering):
- Origin at center of mating face
- X = longitudinal (pin direction)
- +X = toward rear (solder cups / wire attachment)
- -X = toward front (pins protrude)

Joints:
- "mating_face": front face center, for mating with female XT60
- "solder_positive": positive solder cup entry, for red wire connection
- "solder_negative": negative solder cup entry, for black wire connection

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python src/cad/hardware/xt60.py
"""

from pathlib import Path

from build123d import *
from ocp_vscode import show

REFERENCE_STEP = Path(__file__).parent.parent.parent.parent / "components" / "reference_models" / "xt60_male_kicad.step"

PIN_SPACING_Y = 7.2  # mm center-to-center (from KiCad filename)

COLOR_XT60 = Color(0.95, 0.85, 0.0)


class XT60Male(Compound):
    """XT60 male connector with joints for assembly.

    Imported from KiCad Amass reference STEP model.
    """

    def __init__(self):
        ref = import_step(str(REFERENCE_STEP))

        # Center: origin at mating face center
        bb = ref.bounding_box()
        center_y = (bb.min.Y + bb.max.Y) / 2
        center_z = (bb.min.Z + bb.max.Z) / 2
        depth = bb.max.X - bb.min.X  # ~15.9mm

        centered = ref.moved(Location((-bb.min.X, -center_y, -center_z)))

        # Initialize Compound with geometry
        super().__init__(centered.wrapped, label="XT60_male")
        self.color = COLOR_XT60

        # Define joints
        # Mating face: front, pins protrude in -X
        RigidJoint("mating_face", to_part=self,
                   joint_location=Location((0, 0, 0)))

        # Solder cups: rear face, where wires attach
        # Wire comes in along -X direction (into the cup)
        RigidJoint("solder_positive", to_part=self,
                   joint_location=Location((depth, PIN_SPACING_Y / 2, 0), (0, 180, 0)))

        RigidJoint("solder_negative", to_part=self,
                   joint_location=Location((depth, -PIN_SPACING_Y / 2, 0), (0, 180, 0)))

        # Rear face center (for general attachment)
        RigidJoint("rear_face", to_part=self,
                   joint_location=Location((depth, 0, 0)))


if __name__ == "__main__":
    xt60 = XT60Male()

    bb = xt60.bounding_box()
    show(xt60, names=["XT60 Male"])

    print(f"XT60 Male Connector")
    print(f"  Size: {bb.max.X-bb.min.X:.1f} x {bb.max.Y-bb.min.Y:.1f} x {bb.max.Z-bb.min.Z:.1f}mm")
    print(f"  Joints: {list(xt60.joints.keys())}")
