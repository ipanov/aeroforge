"""Aeronaut-compatible 30mm Aluminum Spinner - Build123d parametric model.

Off-the-shelf component for AeroForge sailplane propulsion.

Coordinate system:
- Origin = center of rear face (where spinner meets motor bell)
- Z = motor axis, +Z toward nose (forward / away from motor)
- Spinner tip at +Z

Joints:
- "rear_face": rear face center (mounts against prop hub / motor)
- "tip": front tip of spinner cone
- "shaft_center": center of shaft bore at rear face
- "blade_slot_a": center of blade slot A (at +X)
- "blade_slot_b": center of blade slot B (at -X)

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python cad/components/propulsion/Spinner_30mm/model.py
"""

from build123d import *
from ocp_vscode import show
import math

# ── Spinner parameters (mm) ────────────────────────────────────
SPINNER_DIAMETER = 30.0        # 30mm outer diameter
SPINNER_LENGTH = 28.0          # Overall length (tip to rear face)
WALL_THICKNESS = 1.2           # Aluminum wall thickness

SHAFT_HOLE_DIA = 4.0           # 4mm shaft bore
SET_SCREW_DIA = 3.0            # M3 set screw
SET_SCREW_Z = 8.0              # Set screw position from rear face

# Blade slot parameters
BLADE_SLOT_LENGTH = 18.0       # Slot length along spinner surface
BLADE_SLOT_WIDTH = 3.5         # Slot width (blade thickness clearance)
BLADE_SLOT_Z_START = 3.0       # Slot start from rear face

# Rear face parameters
REAR_FACE_RECESS_DIA = 22.0   # Internal bore diameter at rear (clears hub)
REAR_FACE_RECESS_DEPTH = 5.0  # Depth of rear recess

# Colors
COLOR_SPINNER = Color(0.78, 0.80, 0.82)   # Polished aluminum

# Mass
MASS_GRAMS = 5.0


class Spinner30mm(Compound):
    """30mm aluminum cone spinner for folding propeller.

    Aeronaut-compatible design with 2 blade slots and 4mm shaft bore.
    Cone profile with flat rear face.
    """

    def __init__(
        self,
        diameter: float = SPINNER_DIAMETER,
        length: float = SPINNER_LENGTH,
        label_name: str = "Spinner_30mm",
    ):
        radius = diameter / 2

        with BuildPart() as spinner:
            # ── Outer cone shape (revolved profile) ──
            with BuildSketch(Plane.XZ) as profile:
                with BuildLine():
                    # Profile: flat rear face -> parabolic cone -> tip
                    # Points from bottom (rear) to top (tip)
                    l1 = Line((0, 0), (radius, 0))             # rear face radius
                    l2 = Line((radius, 0), (radius, 2.0))      # short straight at base
                    # Parabolic taper to tip using spline
                    l3 = Spline(
                        (radius, 2.0),
                        (radius * 0.85, length * 0.3),
                        (radius * 0.55, length * 0.6),
                        (radius * 0.20, length * 0.85),
                        (0, length),                            # tip
                    )
                    l4 = Line((0, length), (0, 0))             # center axis back to start
                make_face()

            revolve(axis=Axis.Z, revolution_arc=360)

            # ── Hollow interior ──
            # Internal cavity follows the outer cone with wall thickness offset
            with BuildSketch(Plane.XZ) as cavity_profile:
                inner_r = radius - WALL_THICKNESS
                with BuildLine():
                    Line((0, WALL_THICKNESS), (inner_r, WALL_THICKNESS))
                    Spline(
                        (inner_r, WALL_THICKNESS + 1.0),
                        (inner_r * 0.85, length * 0.3),
                        (inner_r * 0.50, length * 0.6),
                        (inner_r * 0.15, length * 0.82),
                        (0, length - WALL_THICKNESS),
                    )
                    Line((0, length - WALL_THICKNESS), (0, WALL_THICKNESS))
                make_face()

            revolve(axis=Axis.Z, revolution_arc=360, mode=Mode.SUBTRACT)

            # ── Shaft bore (through entire length) ──
            Hole(radius=SHAFT_HOLE_DIA / 2, depth=length + 0.1)

            # ── Rear face recess (clears prop hub) ──
            with Locations([(0, 0, 0)]):
                Cylinder(
                    radius=REAR_FACE_RECESS_DIA / 2,
                    height=REAR_FACE_RECESS_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )

            # ── Blade slots (2, diametrically opposite) ──
            for angle in [0, 180]:
                rad = math.radians(angle)
                slot_x = math.cos(rad) * (radius - WALL_THICKNESS / 2)
                slot_y = math.sin(rad) * (radius - WALL_THICKNESS / 2)
                slot_z = BLADE_SLOT_Z_START + BLADE_SLOT_LENGTH / 2

                with Locations([(slot_x, slot_y, slot_z)]):
                    rot = (0, 0, angle)
                    Box(
                        BLADE_SLOT_WIDTH, WALL_THICKNESS * 3,
                        BLADE_SLOT_LENGTH,
                        align=(Align.CENTER, Align.CENTER, Align.CENTER),
                        rotation=rot,
                        mode=Mode.SUBTRACT,
                    )

            # ── Set screw hole (M3, radial) ──
            with Locations([(0, radius - WALL_THICKNESS / 2, SET_SCREW_Z)]):
                Cylinder(
                    radius=SET_SCREW_DIA / 2,
                    height=WALL_THICKNESS * 2,
                    rotation=(90, 0, 0),
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT,
                )

            # ── Joints ──
            RigidJoint("rear_face", joint_location=Location((0, 0, 0)))
            RigidJoint("tip", joint_location=Location((0, 0, length)))
            RigidJoint("shaft_center", joint_location=Location((0, 0, 0)))
            RigidJoint("blade_slot_a", joint_location=Location(
                (radius * 0.8, 0, BLADE_SLOT_Z_START + BLADE_SLOT_LENGTH / 2)))
            RigidJoint("blade_slot_b", joint_location=Location(
                (-radius * 0.8, 0, BLADE_SLOT_Z_START + BLADE_SLOT_LENGTH / 2)))

        super().__init__(spinner.part.wrapped, label=label_name, joints=spinner.joints)
        self.color = COLOR_SPINNER


if __name__ == "__main__":
    spinner = Spinner30mm()

    bb = spinner.bounding_box()

    show(spinner, names=["30mm Aluminum Spinner"])

    # Export STEP
    import os
    step_dir = "cad/components/propulsion/Spinner_30mm"
    os.makedirs(step_dir, exist_ok=True)
    export_path = os.path.join(step_dir, "Spinner_30mm.step")
    export_step(spinner, export_path)
    print(f"STEP exported: {export_path}")

    print(f"\n30mm Aluminum Spinner")
    print(f"  Diameter: {SPINNER_DIAMETER}mm")
    print(f"  Length: {SPINNER_LENGTH}mm")
    print(f"  Shaft bore: {SHAFT_HOLE_DIA}mm")
    print(f"  Set screw: M{SET_SCREW_DIA}")
    print(f"  Blade slots: 2x {BLADE_SLOT_LENGTH}x{BLADE_SLOT_WIDTH}mm")
    print(f"  Wall thickness: {WALL_THICKNESS}mm")
    print(f"  Weight: {MASS_GRAMS}g")
    print(f"  Joints: {list(spinner.joints.keys())}")
    print(f"  Bounding box: {bb.min.X:.1f},{bb.min.Y:.1f},{bb.min.Z:.1f} to {bb.max.X:.1f},{bb.max.Y:.1f},{bb.max.Z:.1f}")
