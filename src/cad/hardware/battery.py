"""3S 1300mAh Racing LiPo Battery Pack - Off-the-shelf component.

Reference: Tattu 1300mAh 3S 45C (GrabCAD model + photo)
See: components/reference_models/tattu_1300_reference.png

From the reference image:
- Black rectangular body with rounded edges (heat-shrink wrap)
- Gold/yellow label on top face with specs text
- XT60 connector sits directly at one end (short leads, ~20mm)
- Power leads (red+black) exit from the TOP of one end, loop tightly
  up to the XT60 which sits on top of the battery
- Balance lead (white JST-XH) exits from the SIDE near the same end,
  near the bottom edge
- Overall very compact - connector doesn't dangle on long wires

NOTE: User has soldered XT60 connectors themselves, so leads may be
longer. But the bare pack wire exits are the same.

Coordinate system:
- Origin = center of battery body
- X = longest dimension (78mm)
- Y = width (38mm)
- Z = height (28mm), label on +Z face
- Wire exit end = +X

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python src/cad/hardware/battery.py
"""

from build123d import *
from ocp_vscode import show

from src.core.specs import SAILPLANE

SPEC = SAILPLANE.battery

# Wire dimensions
POWER_WIRE_OD = 3.5       # 14AWG with silicone
POWER_WIRE_SPACING = 5.0  # between red and black centers
POWER_LEAD_LENGTH = 25.0  # short leads to XT60 area

# Colors
COLOR_PACK = Color(0.08, 0.08, 0.08)
COLOR_LABEL = Color(0.75, 0.65, 0.0)        # Gold label
COLOR_WIRE_RED = Color(0.85, 0.05, 0.05)
COLOR_WIRE_BLACK = Color(0.06, 0.06, 0.06)
COLOR_BALANCE = Color(0.9, 0.9, 0.9)
COLOR_JST = Color(0.92, 0.92, 0.92)


def build_battery_body() -> Part:
    """Battery cell pack - rounded block with heat-shrink wrap."""
    with BuildPart() as body:
        Box(SPEC.length, SPEC.width, SPEC.height)
        fillet(body.edges(), radius=1.5)
    return body.part


def build_label() -> Part:
    """Gold label/sticker on top face."""
    with BuildPart() as label:
        with Locations([(0, 0, SPEC.height / 2)]):
            Box(SPEC.length * 0.65, SPEC.width * 0.85, 0.15,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    return label.part


def _power_lead(y_offset: float) -> Part:
    """Short power lead exiting from +X end, curving upward."""
    x0 = SPEC.length / 2
    z0 = SPEC.height / 2 - 5  # exits near top of +X face
    pts = [
        Vector(x0, y_offset, z0),
        Vector(x0 + 8, y_offset, z0 + 8),
        Vector(x0 + 15, y_offset, z0 + 14),
        Vector(x0 + POWER_LEAD_LENGTH, y_offset, z0 + 16),
    ]
    path = Spline(*pts)
    with BuildPart() as wire:
        with BuildSketch(Plane(origin=pts[0], z_dir=path % 0)):
            Circle(POWER_WIRE_OD / 2)
        sweep(path=path)
    return wire.part


def build_balance_lead() -> Part:
    """Balance ribbon exiting from side of +X end, near bottom."""
    x0 = SPEC.length / 2
    y0 = SPEC.width / 2  # exits from the +Y side face
    z0 = -SPEC.height / 2 + 5  # near bottom
    pts = [
        Vector(x0 - 5, y0, z0),
        Vector(x0 - 5, y0 + 8, z0 - 2),
        Vector(x0 - 10, y0 + 15, z0 - 5),
    ]
    path = Spline(*pts)
    with BuildPart() as ribbon:
        with BuildSketch(Plane(origin=pts[0], z_dir=path % 0)):
            Rectangle(6, 2)
        sweep(path=path)
    return ribbon.part


def build_jst_connector() -> Part:
    """JST-XH 4-pin at end of balance lead."""
    x0 = SPEC.length / 2 - 12
    y0 = SPEC.width / 2 + 17
    z0 = -SPEC.height / 2
    with BuildPart() as jst:
        with Locations([(x0, y0, z0)]):
            Box(10, 6, 4)
    return jst.part


def build_battery_pack() -> dict[str, tuple]:
    """Complete battery pack with leads.

    Connection points:
        power_positive_end: tip of red wire (for XT60 solder joint)
        power_negative_end: tip of black wire
        balance_connector: JST-XH location
        bottom_center: battery tray mounting
    """
    parts = {
        "Battery Pack": (build_battery_body(), COLOR_PACK),
        "Label": (build_label(), COLOR_LABEL),
    }

    try:
        parts["Power Lead (+)"] = (_power_lead(POWER_WIRE_SPACING / 2), COLOR_WIRE_RED)
        parts["Power Lead (-)"] = (_power_lead(-POWER_WIRE_SPACING / 2), COLOR_WIRE_BLACK)
    except Exception as e:
        print(f"  Power leads: {e}")

    try:
        parts["Balance Lead"] = (build_balance_lead(), COLOR_BALANCE)
        parts["JST-XH"] = (build_jst_connector(), COLOR_JST)
    except Exception as e:
        print(f"  Balance: {e}")

    return parts


def get_battery_connection_points() -> dict[str, tuple[float, float, float]]:
    """Connection points for assembly."""
    x_end = SPEC.length / 2 + POWER_LEAD_LENGTH
    z_top = SPEC.height / 2 + 11  # where wire tips end up (above battery)
    return {
        "power_positive_end": (x_end, POWER_WIRE_SPACING / 2, z_top),
        "power_negative_end": (x_end, -POWER_WIRE_SPACING / 2, z_top),
        "balance_connector": (SPEC.length / 2 - 12, SPEC.width / 2 + 17, -SPEC.height / 2),
        "bottom_center": (0, 0, -SPEC.height / 2),
    }


if __name__ == "__main__":
    parts = build_battery_pack()

    show(
        *[p for p, c in parts.values()],
        names=list(parts.keys()),
        colors=[c for p, c in parts.values()],
    )

    for name, (part, color) in parts.items():
        bb = part.bounding_box()
        print(f"{name}: {bb.max.X-bb.min.X:.1f} x {bb.max.Y-bb.min.Y:.1f} x {bb.max.Z-bb.min.Z:.1f}mm")

    print(f"\nConnection points: {get_battery_connection_points()}")
    print(f"Weight: {SPEC.weight}g ({SPEC.weight_with_connector}g with XT60)")
