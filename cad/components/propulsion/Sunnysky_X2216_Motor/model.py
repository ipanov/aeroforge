"""Sunnysky X2216 880KV Brushless Outrunner Motor - Build123d parametric model.

Off-the-shelf component for AeroForge sailplane propulsion.

Coordinate system:
- Origin = center of mounting face (back plate rear face)
- Z = motor axis, +Z toward propeller (shaft protrudes in +Z)
- Shaft tip at +Z

Joints:
- "mount_face": rear face center, for mounting to firewall/nose
- "shaft_tip": front shaft tip, for propeller attachment
- "shaft_prop": prop mounting position on shaft (at M5 thread start)
- "mount_fl": front-left M3 hole
- "mount_fr": front-right M3 hole
- "mount_bl": back-left M3 hole
- "mount_br": back-right M3 hole

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python cad/components/propulsion/Sunnysky_X2216_Motor/model.py
"""

from build123d import *
from ocp_vscode import show

# ── Motor parameters (mm) ── Sunnysky X2216 880KV ────────────
STATOR_OD = 28.0           # Stator outer diameter
BELL_OD = 27.5             # Bell (rotating can) outer diameter
BELL_HEIGHT = 26.0         # Bell height (can height)

STATOR_HEIGHT = 20.0       # Stator lamination stack height
BACK_PLATE_OD = 28.0       # Back plate diameter (mounting face)
BACK_PLATE_THICKNESS = 2.5 # Back plate thickness

SHAFT_DIAMETER = 4.0       # 4mm shaft (Sunnysky X2216 spec)
SHAFT_PROTRUSION = 14.0    # Shaft sticking out beyond bell top

# X-mount plate (cross-mount on back)
XMOUNT_SIZE = 25.0         # Square plate side
XMOUNT_THICKNESS = 2.0     # Plate thickness
MOUNT_HOLE_DIA = 3.0       # M3 mounting holes
MOUNT_BOLT_CIRCLE = 19.0   # 19mm bolt circle diameter

# Overall length with shaft
OVERALL_LENGTH = BACK_PLATE_THICKNESS + BELL_HEIGHT + SHAFT_PROTRUSION  # ~42.5mm

# Colors
COLOR_BELL = Color(0.25, 0.25, 0.28)       # Dark gray (rotating can)
COLOR_STATOR = Color(0.55, 0.55, 0.58)     # Lighter gray (stationary base)
COLOR_SHAFT = Color(0.80, 0.80, 0.82)      # Silver shaft
COLOR_XMOUNT = Color(0.40, 0.42, 0.40)     # Aluminum gray

# Mass & electrical
MASS_GRAMS = 56.0
KV_RATING = 880
MAX_CURRENT = 18  # Amps
MAX_POWER = 250   # Watts


class SunnyskyX2216Motor(Compound):
    """Sunnysky X2216 880KV brushless outrunner motor.

    Parametric Build123d model with joints for assembly integration.
    Includes bell, stator base, shaft, and X-mount plate.
    """

    def __init__(
        self,
        bell_od: float = BELL_OD,
        bell_height: float = BELL_HEIGHT,
        stator_od: float = STATOR_OD,
        shaft_diameter: float = SHAFT_DIAMETER,
        shaft_protrusion: float = SHAFT_PROTRUSION,
        xmount_size: float = XMOUNT_SIZE,
        label_name: str = "Sunnysky_X2216_880KV",
    ):
        with BuildPart() as motor:
            # ── Back plate (mounting face, at Z=0 plane) ──
            with BuildPart() as back_plate:
                Cylinder(
                    radius=BACK_PLATE_OD / 2,
                    height=BACK_PLATE_THICKNESS,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            back_plate.part.color = COLOR_STATOR

            # ── Stator stack (visible through bell gap) ──
            with BuildPart() as stator_part:
                with Locations([(0, 0, BACK_PLATE_THICKNESS)]):
                    Cylinder(
                        radius=stator_od / 2 - 2.0,
                        height=STATOR_HEIGHT,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                # Bearing hub center
                with Locations([(0, 0, BACK_PLATE_THICKNESS)]):
                    Cylinder(
                        radius=5.0,
                        height=bell_height - 1.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
            stator_part.part.color = COLOR_STATOR

            # ── Rotating bell (outer can) ──
            with BuildPart() as bell_part:
                Cylinder(
                    radius=bell_od / 2,
                    height=bell_height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                # Hollow out inside (leave ~1.2mm wall)
                with Locations([(0, 0, 1.0)]):
                    Cylinder(
                        radius=bell_od / 2 - 1.2,
                        height=bell_height - 1.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                        mode=Mode.SUBTRACT,
                    )
                # Bell top cap (solid disc at top)
                with Locations([(0, 0, bell_height - 2.0)]):
                    Cylinder(
                        radius=bell_od / 2 - 0.3,
                        height=2.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                # Shaft bore
                Hole(
                    radius=shaft_diameter / 2 + 0.2,
                    depth=bell_height + 0.1,
                )
            bell_part.part.color = COLOR_BELL

            # Move bell up to sit on back plate
            bell_offset = Location((0, 0, BACK_PLATE_THICKNESS))
            moved_bell = bell_part.part.moved(bell_offset)
            moved_bell.color = COLOR_BELL

            # ── Shaft (full length from Z=0) ──
            with BuildPart() as shaft_part:
                Cylinder(
                    radius=shaft_diameter / 2,
                    height=BACK_PLATE_THICKNESS + bell_height + shaft_protrusion,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            shaft_part.part.color = COLOR_SHAFT

            # ── X-mount plate (at rear, Z < 0) ──
            with BuildPart() as xmount_part:
                with Locations([(0, 0, -XMOUNT_THICKNESS)]):
                    Box(
                        xmount_size, xmount_size, XMOUNT_THICKNESS,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    # Center bore for shaft pass-through
                    Hole(radius=shaft_diameter / 2 + 0.5, depth=XMOUNT_THICKNESS + 0.1)
                    # 4x M3 mounting holes on 19mm bolt circle (cross pattern)
                    r_bolt = MOUNT_BOLT_CIRCLE / 2
                    for x, y in [(r_bolt, 0), (-r_bolt, 0), (0, r_bolt), (0, -r_bolt)]:
                        with Locations([(x, y, 0)]):
                            Hole(radius=MOUNT_HOLE_DIA / 2, depth=XMOUNT_THICKNESS + 0.1)
                    fillet(xmount_part.part.edges().filter_by(Axis.Z), radius=0.5)
            xmount_part.part.color = COLOR_XMOUNT

            # ── Combine all parts ──
            motor_body = back_plate.part
            motor_body = motor_body.fuse(stator_part.part)
            motor_body = motor_body.fuse(moved_bell)
            motor_body = motor_body.fuse(shaft_part.part)
            motor_body = motor_body.fuse(xmount_part.part)

            # ── Joints ──
            RigidJoint(
                "mount_face",
                joint_location=Location((0, 0, -XMOUNT_THICKNESS)),
            )
            shaft_tip_z = BACK_PLATE_THICKNESS + bell_height + shaft_protrusion
            RigidJoint(
                "shaft_tip",
                joint_location=Location((0, 0, shaft_tip_z)),
            )
            prop_z = BACK_PLATE_THICKNESS + bell_height + 2.0
            RigidJoint(
                "shaft_prop",
                joint_location=Location((0, 0, prop_z)),
            )
            r_bolt = MOUNT_BOLT_CIRCLE / 2
            RigidJoint("mount_fr", joint_location=Location((r_bolt, 0, -XMOUNT_THICKNESS / 2)))
            RigidJoint("mount_fl", joint_location=Location((-r_bolt, 0, -XMOUNT_THICKNESS / 2)))
            RigidJoint("mount_br", joint_location=Location((0, r_bolt, -XMOUNT_THICKNESS / 2)))
            RigidJoint("mount_bl", joint_location=Location((0, -r_bolt, -XMOUNT_THICKNESS / 2)))

        super().__init__(motor.part.wrapped, label=label_name, joints=motor.joints)


if __name__ == "__main__":
    motor = SunnyskyX2216Motor()

    bb = motor.bounding_box()
    total_height = bb.max.Z - bb.min.Z
    total_diameter = max(bb.max.X - bb.min.X, bb.max.Y - bb.min.Y)

    show(motor, names=["Sunnysky X2216 880KV Motor"])

    # Export STEP
    import os
    step_dir = "cad/components/propulsion/Sunnysky_X2216_Motor"
    os.makedirs(step_dir, exist_ok=True)
    export_path = os.path.join(step_dir, "Sunnysky_X2216_Motor.step")
    export_step(motor, export_path)
    print(f"STEP exported: {export_path}")

    print(f"\nSunnysky X2216 880KV Brushless Motor")
    print(f"  Total height: {total_height:.1f}mm (expected ~{OVERALL_LENGTH:.1f}mm)")
    print(f"  Bell diameter: {BELL_OD}mm")
    print(f"  Stator diameter: {STATOR_OD}mm")
    print(f"  Shaft diameter: {SHAFT_DIAMETER}mm")
    print(f"  Weight: {MASS_GRAMS}g")
    print(f"  KV: {KV_RATING}")
    print(f"  Max current: {MAX_CURRENT}A / Max power: {MAX_POWER}W")
    print(f"  Bolt circle: {MOUNT_BOLT_CIRCLE}mm (M3)")
    print(f"  Joints: {list(motor.joints.keys())}")
    print(f"  Bounding box: {bb.min.X:.1f},{bb.min.Y:.1f},{bb.min.Z:.1f} to {bb.max.X:.1f},{bb.max.Y:.1f},{bb.max.Z:.1f}")
