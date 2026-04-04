"""ZTW Spider 30A ESC - Build123d parametric model.

Off-the-shelf electronic speed controller for AeroForge sailplane propulsion.

Coordinate system:
- Origin = center of PCB body
- X = length (45mm), Y = width (25mm), Z = thickness (6mm)
- Motor wires exit +X end
- Battery+signal wires exit -X end

Joints:
- "battery_wire": battery lead exit point (-X end, for XT60 connection)
- "signal_wire": signal lead exit point (-X end, for receiver connection)
- "motor_wire_a": motor phase A wire exit (+X end)
- "motor_wire_b": motor phase B wire exit (+X end)
- "motor_wire_c": motor phase C wire exit (+X end)
- "mount_top": top face center (for mounting tape / strap)
- "mount_bottom": bottom face center (for mounting)

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python cad/components/propulsion/ZTW_Spider_30A_ESC/model.py
"""

from build123d import *
from ocp_vscode import show

# ── ESC body parameters (mm) ──────────────────────────────────
PCB_LENGTH = 45.0          # PCB + heat shrink length
PCB_WIDTH = 24.0           # PCB + heat shrink width
PCB_HEIGHT = 11.0          # Height including heat shrink, components

# Wire parameters
MOTOR_WIRE_COUNT = 3
MOTOR_WIRE_LENGTH = 200.0   # 200mm motor wires
MOTOR_WIRE_DIA = 1.5        # Approximate wire bundle diameter each
MOTOR_WIRE_SPACING = 5.0    # Spacing between motor wire exits

BATTERY_WIRE_LENGTH = 150.0  # 150mm battery lead
BATTERY_WIRE_DIA = 2.5       # Thicker gauge (positive + negative)
SIGNAL_WIRE_LENGTH = 200.0   # 200mm signal lead
SIGNAL_WIRE_DIA = 1.0        # Thin signal wire

WIRE_STUB_LENGTH = 12.0      # How much wire to model (visual stub)

# BEC
BEC_VOLTAGE = 5.0
BEC_CURRENT = 5.0            # 5V/5A switching BEC

# Colors
COLOR_ESC_BODY = Color(0.15, 0.15, 0.15)     # Black heat shrink
COLOR_MOTOR_WIRE = Color(0.8, 0.1, 0.1)      # Red motor wires
COLOR_BATTERY_WIRE_POS = Color(0.9, 0.1, 0.1) # Red positive
COLOR_BATTERY_WIRE_NEG = Color(0.1, 0.1, 0.1) # Black negative
COLOR_SIGNAL_WIRE = Color(0.9, 0.7, 0.0)     # Yellow/orange signal

# Mass
MASS_GRAMS = 16.0  # With wires
CURRENT_RATING = 30  # Amps


class ZTWSpider30AESC(Compound):
    """ZTW Spider 30A ESC with switching BEC.

    Simple rectangular body (heat-shrink wrapped PCB) with wire stubs
    protruding from each end. No internal PCB detail modeled.
    """

    def __init__(
        self,
        pcb_length: float = PCB_LENGTH,
        pcb_width: float = PCB_WIDTH,
        pcb_height: float = PCB_HEIGHT,
        wire_stub_length: float = WIRE_STUB_LENGTH,
        label_name: str = "ZTW_Spider_30A_ESC",
    ):
        half_len = pcb_length / 2

        # ── Main body (heat-shrink wrapped PCB) ──
        with BuildPart() as body:
            Box(
                pcb_length, pcb_width, pcb_height,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )
            fillet(body.part.edges(), radius=0.8)

        body.part.color = COLOR_ESC_BODY

        # ── Motor wire stubs (3x, exit +X end, along X axis) ──
        motor_wires = []
        for i in range(MOTOR_WIRE_COUNT):
            offset_y = (i - 1) * MOTOR_WIRE_SPACING
            with BuildPart() as mw:
                with Locations([(half_len, offset_y, 0)]):
                    Cylinder(
                        radius=MOTOR_WIRE_DIA / 2,
                        height=wire_stub_length,
                        rotation=(0, 90, 0),
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
            mw.part.color = COLOR_MOTOR_WIRE
            motor_wires.append(mw.part)

        # ── Battery positive wire (-X end) ──
        with BuildPart() as bp:
            with Locations([(-half_len, 3.0, 0)]):
                Cylinder(
                    radius=BATTERY_WIRE_DIA / 2,
                    height=wire_stub_length,
                    rotation=(0, -90, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
        bp.part.color = COLOR_BATTERY_WIRE_POS

        # ── Battery negative wire (-X end) ──
        with BuildPart() as bn:
            with Locations([(-half_len, -3.0, 0)]):
                Cylinder(
                    radius=BATTERY_WIRE_DIA / 2,
                    height=wire_stub_length,
                    rotation=(0, -90, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
        bn.part.color = COLOR_BATTERY_WIRE_NEG

        # ── Signal/BEC wire (-X end, offset to side) ──
        with BuildPart() as sw:
            with Locations([(-half_len, 8.0, 0)]):
                Cylinder(
                    radius=SIGNAL_WIRE_DIA / 2,
                    height=wire_stub_length,
                    rotation=(0, -90, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
        sw.part.color = COLOR_SIGNAL_WIRE

        # ── Fuse everything ──
        combined = body.part
        for w in motor_wires:
            combined = combined.fuse(w)
        combined = combined.fuse(bp.part)
        combined = combined.fuse(bn.part)
        combined = combined.fuse(sw.part)

        # ── Create with joints ──
        with BuildPart() as final:
            add(combined)

            # Battery wire exit point
            RigidJoint("battery_wire", joint_location=Location((-half_len, 0, 0)))
            # Signal wire exit
            RigidJoint("signal_wire", joint_location=Location((-half_len, 8.0, 0)))
            # Motor wire exits
            for i, label in enumerate(["motor_wire_a", "motor_wire_b", "motor_wire_c"]):
                offset_y = (i - 1) * MOTOR_WIRE_SPACING
                RigidJoint(label, joint_location=Location((half_len, offset_y, 0)))
            # Mount faces
            RigidJoint("mount_top", joint_location=Location((0, 0, pcb_height / 2)))
            RigidJoint("mount_bottom", joint_location=Location((0, 0, -pcb_height / 2)))

        super().__init__(final.part.wrapped, label=label_name, joints=final.joints)


if __name__ == "__main__":
    esc = ZTWSpider30AESC()

    bb = esc.bounding_box()

    show(esc, names=["ZTW Spider 30A ESC"])

    # Export STEP
    import os
    step_dir = "cad/components/propulsion/ZTW_Spider_30A_ESC"
    os.makedirs(step_dir, exist_ok=True)
    export_path = os.path.join(step_dir, "ZTW_Spider_30A_ESC.step")
    export_step(esc, export_path)
    print(f"STEP exported: {export_path}")

    print(f"\nZTW Spider 30A ESC")
    print(f"  Body: {PCB_LENGTH} x {PCB_WIDTH} x {PCB_HEIGHT}mm")
    print(f"  Weight: {MASS_GRAMS}g (with wires)")
    print(f"  Current rating: {CURRENT_RATING}A")
    print(f"  BEC: {BEC_VOLTAGE}V/{BEC_CURRENT}A switching BEC")
    print(f"  Motor wires: {MOTOR_WIRE_COUNT}x {MOTOR_WIRE_LENGTH}mm")
    print(f"  Battery wire: {BATTERY_WIRE_LENGTH}mm (with XT60)")
    print(f"  Signal wire: {SIGNAL_WIRE_LENGTH}mm (with JR connector)")
    print(f"  Joints: {list(esc.joints.keys())}")
    print(f"  Bounding box: {bb.min.X:.1f},{bb.min.Y:.1f},{bb.min.Z:.1f} to {bb.max.X:.1f},{bb.max.Y:.1f},{bb.max.Z:.1f}")
