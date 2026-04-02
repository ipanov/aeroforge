"""Flysky FS-iA6B Receiver - Off-the-shelf component.

Compatible with Turnigy 9X V2 transmitter.
6 channels, AFHDS 2A protocol, single antenna.

Coordinate system:
- Origin = center of receiver body
- X = length (47.2mm), Y = width (26.2mm), Z = height (15mm)
- Antenna exits from +X end, top
- Servo pin headers on -Y side (6 x 3-pin)
- Bind button on +Z face (top)

Joints:
- "bottom": bottom face center (for mounting in receiver bay)
- "top": top face center
- "antenna": antenna wire exit point (+X end, top)
- "pins": servo header center (-Y side)

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python src/cad/hardware/receiver.py
"""

from pathlib import Path

from build123d import *
from ocp_vscode import show

from src.core.specs import SAILPLANE

SPEC = SAILPLANE.receiver

COLOR_CASE = Color(0.08, 0.08, 0.08)        # Black plastic case
COLOR_PCB = Color(0.0, 0.35, 0.0)           # Green PCB
COLOR_ANTENNA = Color(0.15, 0.15, 0.15)     # Dark wire

# Receiver body dimensions from spec
L = SPEC.length       # 47.2mm
W = SPEC.width        # 26.2mm
H = SPEC.height       # 15.0mm

# Feature dimensions
BIND_BUTTON_DIA = 3.0     # mm
BIND_BUTTON_HEIGHT = 1.0  # mm protrusion
FILLET_RADIUS = 1.5       # mm edge radius
PIN_HEADER_WIDTH = 2.54   # mm standard pin spacing
PIN_HEADER_LENGTH = 40.0  # mm (6 headers x ~6.5mm)
PIN_HEADER_HEIGHT = 8.5   # mm (pins + plastic housing)
ANTENNA_WIRE_DIA = 1.0    # mm
ANTENNA_LENGTH = SPEC.antenna_length  # 165mm


class FlyskyIA6BReceiver(Compound):
    """Flysky FS-iA6B 6-channel receiver with joints for assembly.

    Dimensionally accurate body for fuselage bay sizing and CG calculation.
    """

    def __init__(self):
        with BuildPart() as bp:
            # Main body
            Box(L, W, H)
            # Round the vertical edges
            fillet(bp.edges().filter_by(Axis.Z), radius=FILLET_RADIUS)

            # Bind button on top face
            bind_x = L * 0.25   # offset from center toward +X
            bind_y = W * 0.15   # offset toward +Y
            with Locations([(bind_x, bind_y, H / 2)]):
                Cylinder(BIND_BUTTON_DIA / 2, BIND_BUTTON_HEIGHT,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))

            # PCB window (thin recessed area on bottom showing PCB)
            with Locations([(0, 0, -H / 2)]):
                Box(L * 0.6, W * 0.5, 0.3,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT)

            # Antenna stub (short cylinder at +X end)
            with Locations([(L / 2, 0, H / 2 - 3)]):
                Cylinder(ANTENNA_WIRE_DIA / 2 + 0.5, 3.0,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))

            # Pin header block (-Y side, 6 groups of 3 pins)
            header_z = -H / 2 + PIN_HEADER_HEIGHT / 2 - 2
            with Locations([(0, -W / 2, header_z)]):
                Box(PIN_HEADER_LENGTH, 2.5, PIN_HEADER_HEIGHT,
                    align=(Align.CENTER, Align.MAX, Align.CENTER))

            # === JOINTS ===

            # Bottom face - for mounting in receiver tray/bay
            RigidJoint("bottom",
                       joint_location=Location((0, 0, -H / 2)))

            # Top face center
            RigidJoint("top",
                       joint_location=Location((0, 0, H / 2)))

            # Antenna exit point
            RigidJoint("antenna",
                       joint_location=Location((L / 2, 0, H / 2 - 3)))

            # Servo pin headers center (-Y side)
            RigidJoint("pins",
                       joint_location=Location((0, -W / 2, 0), (0, 0, -90)))

        super().__init__(bp.part.wrapped, label="Flysky_FS_iA6B", joints=bp.joints)
        self.color = COLOR_CASE


def export_step(output_dir: str | Path | None = None) -> Path:
    """Build receiver and export STEP file.

    Returns path to the exported STEP file.
    """
    rx = FlyskyIA6BReceiver()

    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent.parent / \
            "cad" / "components" / "hardware" / "Flysky_FS_iA6B_Receiver"

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    step_path = output_dir / "Flysky_FS_iA6B_Receiver.step"
    export_step(rx, str(step_path))

    print(f"STEP exported: {step_path}")
    bb = rx.bounding_box()
    print(f"  Size: {bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f}mm")
    print(f"  Joints: {list(rx.joints.keys())}")

    return step_path


if __name__ == "__main__":
    rx = FlyskyIA6BReceiver()

    bb = rx.bounding_box()
    print(f"Flysky FS-iA6B Receiver")
    print(f"  Size: {bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f}mm")
    print(f"  Joints: {list(rx.joints.keys())}")

    show(rx, names=["Flysky FS-iA6B"])

    # Export STEP
    export_step()
