"""Aeronaut CAM Carbon 11x6 Folding Propeller Blades - Build123d parametric model.

Off-the-shelf component for AeroForge sailplane propulsion.
Simplified but dimensionally accurate envelope model for clearance checking and CG.

Coordinate system:
- Origin = center of hub (where blades pivot)
- Z = motor axis, +Z toward pilot (forward)
- X = blade span axis when deployed (blade tips at +/-X)
- Y = perpendicular to blade span

Joints:
- "hub_center": center of the yoke hub (Z=0)
- "hub_rear": rear face of hub (mounts against spinner)
- "blade_tip_a": tip of blade A (+X)
- "blade_tip_b": tip of blade B (-X)

Blade geometry:
- Each blade is ~139.5mm from hub center to tip
- Clark-Y style cross-section (flat bottom, cambered top)
- Twist from ~27 deg at root to ~11 deg at tip
- Width tapers from ~22mm at max to ~12mm at tip

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python cad/components/propulsion/Folding_Prop_11x6/model.py
"""

from build123d import *
from ocp_vscode import show
import math

# ── Prop parameters (mm) ── Aeronaut CAM Carbon 11x6 ────────
PROP_DIAMETER_IN = 11.0        # 11 inches
PROP_PITCH_IN = 6.0            # 6 inches
PROP_DIAMETER_MM = PROP_DIAMETER_IN * 25.4   # 279.4mm
BLADE_LENGTH = PROP_DIAMETER_MM / 2          # 139.7mm from hub center

# Hub/yoke parameters
HUB_LENGTH = 12.0              # Hub block length along Z
HUB_WIDTH = 22.0               # Yoke width (blade attachment direction)
HUB_HEIGHT = 8.0               # Yoke height (perpendicular to blade)
SHAFT_HOLE_DIA = 4.0           # 4mm shaft adapter
YOKE_SPACING = 8.0             # Distance between yoke arms

# Blade shape parameters
BLADE_ROOT_WIDTH = 18.0        # Chord at blade root (at hub edge)
BLADE_MAX_WIDTH = 22.0         # Maximum chord (at ~30% span)
BLADE_TIP_WIDTH = 8.0          # Chord at tip
BLADE_THICKNESS_ROOT = 3.0     # Thickness at root
BLADE_THICKNESS_MAX = 2.5      # Max thickness (at ~30% span)
BLADE_THICKNESS_TIP = 0.8      # Thickness at tip

# Twist (pitch angle at each station)
TWIST_ROOT_DEG = 27.0          # Pitch angle at root
TWIST_TIP_DEG = 11.0           # Pitch angle at tip

# Mass
MASS_GRAMS = 14.0              # Both blades + hardware
NUM_BLADES = 2

# Colors
COLOR_BLADE = Color(0.15, 0.15, 0.18)    # Carbon fiber dark
COLOR_HUB = Color(0.60, 0.62, 0.65)      # Aluminum hub


def _blade_section(span_frac: float) -> tuple[float, float, float]:
    """Return (chord, thickness, twist_deg) at a given span fraction [0..1]."""
    # Chord: rises to max at 30%, then tapers to tip
    if span_frac < 0.30:
        t = span_frac / 0.30
        chord = BLADE_ROOT_WIDTH + (BLADE_MAX_WIDTH - BLADE_ROOT_WIDTH) * t
    else:
        t = (span_frac - 0.30) / 0.70
        chord = BLADE_MAX_WIDTH + (BLADE_TIP_WIDTH - BLADE_MAX_WIDTH) * t

    # Thickness: rises to max at 30%, then tapers
    if span_frac < 0.30:
        t = span_frac / 0.30
        thick = BLADE_THICKNESS_ROOT + (BLADE_THICKNESS_MAX - BLADE_THICKNESS_ROOT) * t
    else:
        t = (span_frac - 0.30) / 0.70
        thick = BLADE_THICKNESS_MAX + (BLADE_THICKNESS_TIP - BLADE_THICKNESS_MAX) * t

    # Twist: linear from root to tip
    twist = TWIST_ROOT_DEG + (TWIST_TIP_DEG - TWIST_ROOT_DEG) * span_frac

    return chord, thick, twist


def _make_blade_section(chord: float, thickness: float) -> Face:
    """Create a simplified Clark-Y style airfoil section as a Face.

    Flat bottom, cambered top, rounded LE, sharp TE.
    Section is in XZ plane, centered at origin, chord along X.
    """
    half_c = chord / 2
    # Simplified: elliptical top, flat bottom
    pts = []
    n = 16

    # Bottom surface (flat, slight camber)
    for i in range(n + 1):
        x = -half_c + chord * i / n
        z = -thickness * 0.15  # slight offset below center
        pts.append((x, z))

    # Top surface (cambered)
    for i in range(n, -1, -1):
        x = -half_c + chord * i / n
        # Camber peaks at ~30% chord
        t_norm = (x + half_c) / chord
        camber = thickness * 0.85 * math.sin(math.pi * t_norm ** 0.6)
        z = camber - thickness * 0.15
        pts.append((x, z))

    # Close the profile
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine():
            Spline(*[(p[0], p[1]) for p in pts], periodic=True)
        make_face()

    return sk.sketch


class FoldingProp11x6(Compound):
    """Aeronaut CAM Carbon 11x6 folding propeller (2 blades + hub).

    Simplified lofted blade shape with twist for envelope/CG purposes.
    Both blades shown in deployed (running) position.
    """

    def __init__(
        self,
        blade_length: float = BLADE_LENGTH,
        label_name: str = "Folding_Prop_11x6",
    ):
        # ── Hub/yoke block ──
        with BuildPart() as hub:
            Box(
                HUB_WIDTH, HUB_HEIGHT, HUB_LENGTH,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )
            fillet(hub.part.edges().filter_by(Axis.X), radius=1.5)

            # Shaft hole (through Z axis)
            Hole(radius=SHAFT_HOLE_DIA / 2, depth=HUB_LENGTH + 0.1)

        hub.part.color = COLOR_HUB

        # ── Blades (lofted with twist) ──
        # Build blade A along +X axis
        n_sections = 8
        blade_start_x = HUB_WIDTH / 2  # blade starts at hub edge

        sections_a = []
        locs_a = []

        for i in range(n_sections + 1):
            span_frac = i / n_sections
            chord, thick, twist_deg = _blade_section(span_frac)
            x_pos = blade_start_x + (blade_length - HUB_WIDTH / 2) * span_frac

            # Create rectangular approximation for loft section
            # Blade sections are in YZ plane at each X station
            half_c = chord / 2
            half_t = thick / 2

            locs_a.append(Location(
                (x_pos, 0, 0),
                (0, 0, 0)  # twist applied via rotation
            ))

        # Use a simpler approach: build blade as a tapered, twisted box
        # since lofting arbitrary sections can be fragile
        with BuildPart() as blade_a:
            # Create blade using loft of elliptical sections
            planes = []
            sketches = []

            for i in range(n_sections + 1):
                span_frac = i / n_sections
                chord, thick, twist_deg = _blade_section(span_frac)
                x_pos = blade_start_x + (blade_length - HUB_WIDTH / 2) * span_frac

                twist_rad = math.radians(twist_deg)

                # Create a plane at this span station
                plane = Plane(
                    origin=(x_pos, 0, 0),
                    x_dir=(0, math.cos(twist_rad), math.sin(twist_rad)),
                    z_dir=(1, 0, 0),
                )

                with BuildSketch(plane) as sk:
                    Ellipse(chord / 2, thick / 2)

                sketches.append(sk.sketch)

            loft(sketches)

        blade_a.part.color = COLOR_BLADE

        # Blade B is mirrored (-X direction)
        blade_b_part = blade_a.part.mirror(Plane.YZ)
        blade_b_part.color = COLOR_BLADE

        # ── Combine ──
        combined = hub.part.fuse(blade_a.part).fuse(blade_b_part)

        # ── Joints ──
        with BuildPart() as final:
            add(combined)

            RigidJoint("hub_center", joint_location=Location((0, 0, 0)))
            RigidJoint("hub_rear", joint_location=Location((0, 0, -HUB_LENGTH / 2)))
            RigidJoint("blade_tip_a", joint_location=Location((blade_length, 0, 0)))
            RigidJoint("blade_tip_b", joint_location=Location((-blade_length, 0, 0)))

        super().__init__(final.part.wrapped, label=label_name, joints=final.joints)


if __name__ == "__main__":
    prop = FoldingProp11x6()

    bb = prop.bounding_box()

    show(prop, names=["Aeronaut CAM Carbon 11x6 Folding Prop"])

    # Export STEP
    import os
    step_dir = "cad/components/propulsion/Folding_Prop_11x6"
    os.makedirs(step_dir, exist_ok=True)
    export_path = os.path.join(step_dir, "Folding_Prop_11x6.step")
    export_step(prop, export_path)
    print(f"STEP exported: {export_path}")

    print(f"\nAeronaut CAM Carbon 11x6 Folding Propeller")
    print(f"  Diameter: {PROP_DIAMETER_MM:.1f}mm ({PROP_DIAMETER_IN}\")")
    print(f"  Pitch: {PROP_PITCH_IN}\" ({PROP_PITCH_IN * 25.4:.0f}mm)")
    print(f"  Blade length: {BLADE_LENGTH:.1f}mm (from hub center)")
    print(f"  Hub: {HUB_WIDTH} x {HUB_HEIGHT} x {HUB_LENGTH}mm")
    print(f"  Shaft hole: {SHAFT_HOLE_DIA}mm")
    print(f"  Weight: {MASS_GRAMS}g (both blades + hardware)")
    print(f"  Joints: {list(prop.joints.keys())}")
    print(f"  Bounding box: {bb.min.X:.1f},{bb.min.Y:.1f},{bb.min.Z:.1f} to {bb.max.X:.1f},{bb.max.Y:.1f},{bb.max.Z:.1f}")
