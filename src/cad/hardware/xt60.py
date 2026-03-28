"""XT60 Male Connector - Off-the-shelf component.

Coordinate system:
- Origin = center of mating face
- X-axis = longitudinal (main axis). -X = pins protrude, +X = solder cups
- Y-axis = lateral (across the two pins)
- Z-axis = up

Real XT60 anatomy:
- Yellow nylon housing, roughly 16x8x16mm
- One corner chamfered for polarity keying (positive side)
- Two 3.5mm gold pins protrude ~6.5mm from the FRONT face (mating end)
- Two hollow solder cups extend ~7mm from the REAR face (wire end)
- Pins spaced ~7.5mm center-to-center
- Total length from pin tips to solder cup ends: ~29mm

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python src/cad/hardware/xt60.py
"""

from build123d import *
from ocp_vscode import show

# ── Dimensions (all mm) ──────────────────────────────────────────

HOUSING_DEPTH = 15.8     # X dimension
HOUSING_WIDTH = 8.0      # Y dimension (across pins)
HOUSING_HEIGHT = 15.8    # Z dimension

PIN_DIAMETER = 3.5
PIN_LENGTH = 6.5         # Protrusion from front face
PIN_SPACING_Y = 4.5      # Center-to-center in Y (pins must fit inside 8mm housing)

SOLDER_CUP_LENGTH = 7.0
SOLDER_CUP_OD = 3.5
SOLDER_CUP_ID = 2.0

KEY_CHAMFER = 2.5

# Colors
COLOR_HOUSING = Color(0.95, 0.85, 0.0)
COLOR_PIN = Color(0.85, 0.72, 0.0)
COLOR_SOLDER_CUP = Color(0.75, 0.65, 0.0)


def build_xt60_housing() -> Part:
    """Keyed rectangular housing. Origin at center of mating face, body extends in +X."""
    with BuildPart() as housing:
        Box(HOUSING_DEPTH, HOUSING_WIDTH, HOUSING_HEIGHT,
            align=(Align.MIN, Align.CENTER, Align.CENTER))

        # Pin holes through the housing (for visual accuracy)
        for y_offset in [PIN_SPACING_Y / 2, -PIN_SPACING_Y / 2]:
            with Locations([(HOUSING_DEPTH / 2, y_offset, 0)]):
                Cylinder(PIN_DIAMETER / 2 + 0.2, HOUSING_DEPTH,
                         rotation=(0, 90, 0), mode=Mode.SUBTRACT)

    # Chamfer for keying (positive corner)
    try:
        key_edges = housing.edges().filter_by(Axis.X).group_by(Axis.Y)[-1].group_by(Axis.Z)[-1]
        chamfer(key_edges, length=KEY_CHAMFER)
    except Exception:
        pass

    return housing.part


def _make_pin(y_pos: float) -> Part:
    """Single pin protruding from mating face in -X direction."""
    with BuildPart() as pin:
        with Locations([(- PIN_LENGTH / 2, y_pos, 0)]):
            Cylinder(PIN_DIAMETER / 2, PIN_LENGTH, rotation=(0, 90, 0))
    return pin.part


def _make_solder_cup(y_pos: float) -> Part:
    """Single hollow solder cup extending from rear face in +X direction."""
    x_center = HOUSING_DEPTH + SOLDER_CUP_LENGTH / 2
    with BuildPart() as cup:
        with Locations([(x_center, y_pos, 0)]):
            Cylinder(SOLDER_CUP_OD / 2, SOLDER_CUP_LENGTH, rotation=(0, 90, 0))
            Cylinder(SOLDER_CUP_ID / 2, SOLDER_CUP_LENGTH + 0.1,
                     rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    return cup.part


def build_xt60_male() -> dict[str, tuple]:
    """Complete XT60 male connector.

    Connection points (local frame):
        mating_face:     (0, 0, 0) normal = -X
        pin_positive:    (-PIN_LENGTH, +PIN_SPACING_Y/2, 0)
        pin_negative:    (-PIN_LENGTH, -PIN_SPACING_Y/2, 0)
        solder_positive: (HOUSING_DEPTH + SOLDER_CUP_LENGTH, +PIN_SPACING_Y/2, 0)
        solder_negative: (HOUSING_DEPTH + SOLDER_CUP_LENGTH, -PIN_SPACING_Y/2, 0)
        rear_face:       (HOUSING_DEPTH, 0, 0)
    """
    housing = build_xt60_housing()
    pin_pos = _make_pin(PIN_SPACING_Y / 2)
    pin_neg = _make_pin(-PIN_SPACING_Y / 2)
    cup_pos = _make_solder_cup(PIN_SPACING_Y / 2)
    cup_neg = _make_solder_cup(-PIN_SPACING_Y / 2)

    return {
        "XT60 Housing": (housing, COLOR_HOUSING),
        "XT60 Pin (+)": (pin_pos, COLOR_PIN),
        "XT60 Pin (-)": (pin_neg, COLOR_PIN),
        "XT60 Solder Cup (+)": (cup_pos, COLOR_SOLDER_CUP),
        "XT60 Solder Cup (-)": (cup_neg, COLOR_SOLDER_CUP),
    }


def get_xt60_connection_points() -> dict[str, tuple[float, float, float]]:
    """Named connection points for assembly."""
    return {
        "mating_face": (0, 0, 0),
        "pin_positive_tip": (-PIN_LENGTH, PIN_SPACING_Y / 2, 0),
        "pin_negative_tip": (-PIN_LENGTH, -PIN_SPACING_Y / 2, 0),
        "solder_positive": (HOUSING_DEPTH + SOLDER_CUP_LENGTH, PIN_SPACING_Y / 2, 0),
        "solder_negative": (HOUSING_DEPTH + SOLDER_CUP_LENGTH, -PIN_SPACING_Y / 2, 0),
        "rear_face": (HOUSING_DEPTH, 0, 0),
    }


if __name__ == "__main__":
    parts = build_xt60_male()

    show(
        *[p for p, c in parts.values()],
        names=list(parts.keys()),
        colors=[c for p, c in parts.values()],
    )

    # Self-validation
    for name, (part, color) in parts.items():
        bb = part.bounding_box()
        print(f"{name}: X=[{bb.min.X:.1f},{bb.max.X:.1f}] Y=[{bb.min.Y:.1f},{bb.max.Y:.1f}] Z=[{bb.min.Z:.1f},{bb.max.Z:.1f}]")

    print(f"\nConnection points: {get_xt60_connection_points()}")
