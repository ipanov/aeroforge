"""XT60 Male Connector - Off-the-shelf component.

The XT60 (by Amass) is a keyed, polarized power connector.
Sold separately - user solders it onto battery leads.

Physical description (from datasheets and measurement):
- Rectangular nylon housing, keyed (one corner chamfered for polarity)
- Two gold-plated brass pins protrude from the FRONT (mating end)
- Two tubular solder cups at the REAR for wire attachment
- Housing has a slight lip/flange around the mating face

Coordinate system:
- X-axis = main axis (pin direction, wire direction) - LONGEST
- Y-axis = across the two pins (pin spacing direction)
- Z-axis = height
- Origin = center of mating face
- +X = toward solder cups (rear), -X = toward pins (front/mating)

Connection points:
- "mating_face": center of front face, -X direction (mates with female XT60)
- "solder_positive": center of positive solder cup, +X direction
- "solder_negative": center of negative solder cup, +X direction

Dimensions (Amass XT60, measured/datasheet):
- Housing: 15.8mm (X, depth) x 15.8mm (Z, height) x 8.0mm (Y, width across pins)
  Note: housing is roughly square in the YZ cross-section
- Pin diameter: 3.5mm
- Pin protrusion from housing face: 6.5mm
- Pin spacing: 8.0mm center-to-center (Y-axis)
- Solder cup length: 7.0mm (extending from rear of housing)
- Solder cup inner diameter: ~2.0mm (accepts up to 12AWG stripped wire)
- Solder cup outer diameter: ~3.5mm
- Overall length (pins to solder cup tips): 15.8 + 6.5 + 7.0 ≈ 29.3mm
- Weight: ~5g

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python src/cad/hardware/xt60.py
"""

from build123d import *
from ocp_vscode import show

# ── Dimensions (all mm) ──────────────────────────────────────────

HOUSING_DEPTH = 15.8     # X - from mating face to rear face
HOUSING_WIDTH = 8.0      # Y - across the two pins
HOUSING_HEIGHT = 15.8    # Z - roughly square cross-section

PIN_DIAMETER = 3.5
PIN_PROTRUSION = 6.5     # How far pins stick out from mating face (-X direction)
PIN_SPACING = 8.0        # Center-to-center in Y

SOLDER_CUP_LENGTH = 7.0  # Extends from rear face (+X direction)
SOLDER_CUP_OD = 3.5
SOLDER_CUP_ID = 2.0

KEY_CHAMFER = 2.5        # Corner chamfer for polarity keying

# Colors
COLOR_HOUSING = Color(0.95, 0.85, 0.0)    # Yellow nylon
COLOR_PIN = Color(0.85, 0.72, 0.0)        # Gold-plated brass
COLOR_SOLDER_CUP = Color(0.75, 0.65, 0.0) # Brass solder cup


def build_xt60_housing() -> Part:
    """XT60 housing - keyed rectangular nylon body.

    Origin at center of mating face. +X = toward rear/solder cups.
    """
    with BuildPart() as housing:
        # Main rectangular body, origin at center, extending in +X
        Box(HOUSING_DEPTH, HOUSING_WIDTH, HOUSING_HEIGHT,
            align=(Align.MIN, Align.CENTER, Align.CENTER))

        # Keying chamfer: cut one corner to prevent reverse insertion
        # The positive pin side (Y>0) at top (Z>0) gets the chamfer
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations([(HOUSING_DEPTH / 2, HOUSING_WIDTH / 2, HOUSING_HEIGHT / 2)]):
                Box(HOUSING_DEPTH + 1, KEY_CHAMFER * 2, KEY_CHAMFER * 2,
                    align=(Align.CENTER, Align.MAX, Align.MAX))
                # Rotate 45 degrees to create the chamfer
        # Simpler approach: just chamfer the edge
        try:
            # Find the top-right edge along X and chamfer it
            edges_to_chamfer = (
                housing.edges()
                .filter_by(Axis.X)
                .filter_by(lambda e: e.center().Y > 0 and e.center().Z > 0)
            )
            if edges_to_chamfer:
                chamfer(edges_to_chamfer, length=KEY_CHAMFER)
        except Exception:
            pass  # Chamfer may fail on some edge configurations

        # Slight fillet on remaining long edges for realism
        try:
            fillet(housing.edges().filter_by(Axis.X), radius=0.5)
        except Exception:
            pass

    return housing.part


def build_xt60_pins() -> tuple[Part, Part]:
    """Two gold-plated brass pins protruding from mating face.

    Pins extend in -X direction from the mating face (origin).
    """
    with BuildPart() as pin_pos:
        # Positive pin (Y > 0)
        with Locations([(0, PIN_SPACING / 2, 0)]):
            Cylinder(radius=PIN_DIAMETER / 2, height=PIN_PROTRUSION,
                     rotation=(0, 90, 0),  # Align along X
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

    with BuildPart() as pin_neg:
        # Negative pin (Y < 0)
        with Locations([(0, -PIN_SPACING / 2, 0)]):
            Cylinder(radius=PIN_DIAMETER / 2, height=PIN_PROTRUSION,
                     rotation=(0, 90, 0),
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Move pins to protrude from mating face in -X direction
    pin_pos_moved = pin_pos.part.moved(Location((-PIN_PROTRUSION, 0, 0)))
    pin_neg_moved = pin_neg.part.moved(Location((-PIN_PROTRUSION, 0, 0)))

    return pin_pos_moved, pin_neg_moved


def build_xt60_solder_cups() -> tuple[Part, Part]:
    """Two solder cups extending from rear face in +X direction.

    These are hollow tubes where stripped wire is inserted and soldered.
    """
    with BuildPart() as cup_pos:
        with Locations([(HOUSING_DEPTH, PIN_SPACING / 2, 0)]):
            Cylinder(radius=SOLDER_CUP_OD / 2, height=SOLDER_CUP_LENGTH,
                     rotation=(0, -90, 0),
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Hollow out the cup
            Cylinder(radius=SOLDER_CUP_ID / 2, height=SOLDER_CUP_LENGTH + 1,
                     rotation=(0, -90, 0),
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)

    with BuildPart() as cup_neg:
        with Locations([(HOUSING_DEPTH, -PIN_SPACING / 2, 0)]):
            Cylinder(radius=SOLDER_CUP_OD / 2, height=SOLDER_CUP_LENGTH,
                     rotation=(0, -90, 0),
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            Cylinder(radius=SOLDER_CUP_ID / 2, height=SOLDER_CUP_LENGTH + 1,
                     rotation=(0, -90, 0),
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)

    return cup_pos.part, cup_neg.part


def build_xt60_male() -> dict[str, tuple]:
    """Build complete XT60 male connector with all sub-parts.

    Returns dict of {name: (part, color)} for display and validation.

    Connection points (for assembly use):
        mating_face: (0, 0, 0) facing -X
        solder_positive: (HOUSING_DEPTH + SOLDER_CUP_LENGTH, PIN_SPACING/2, 0) facing +X
        solder_negative: (HOUSING_DEPTH + SOLDER_CUP_LENGTH, -PIN_SPACING/2, 0) facing +X
    """
    housing = build_xt60_housing()
    pin_pos, pin_neg = build_xt60_pins()
    cup_pos, cup_neg = build_xt60_solder_cups()

    return {
        "XT60 Housing": (housing, COLOR_HOUSING),
        "XT60 Pin (+)": (pin_pos, COLOR_PIN),
        "XT60 Pin (-)": (pin_neg, COLOR_PIN),
        "XT60 Solder Cup (+)": (cup_pos, COLOR_SOLDER_CUP),
        "XT60 Solder Cup (-)": (cup_neg, COLOR_SOLDER_CUP),
    }


# ── Connection Points (for assembly system) ──────────────────────

def get_xt60_connection_points() -> dict[str, tuple[float, float, float]]:
    """Named connection points for assembling XT60 with other components.

    Returns dict of {point_name: (x, y, z)} in the connector's local frame.
    """
    return {
        "mating_face": (0, 0, 0),
        "solder_positive": (HOUSING_DEPTH + SOLDER_CUP_LENGTH, PIN_SPACING / 2, 0),
        "solder_negative": (HOUSING_DEPTH + SOLDER_CUP_LENGTH, -PIN_SPACING / 2, 0),
        "rear_face": (HOUSING_DEPTH, 0, 0),
    }


if __name__ == "__main__":
    parts = build_xt60_male()

    show(
        *[p for p, c in parts.values()],
        names=list(parts.keys()),
        colors=[c for p, c in parts.values()],
    )

    print("XT60 Male Connector")
    print(f"  Housing: {HOUSING_DEPTH}x{HOUSING_WIDTH}x{HOUSING_HEIGHT}mm")
    print(f"  Pin protrusion: {PIN_PROTRUSION}mm")
    print(f"  Solder cup length: {SOLDER_CUP_LENGTH}mm")
    print(f"  Overall length: {PIN_PROTRUSION + HOUSING_DEPTH + SOLDER_CUP_LENGTH:.1f}mm")
    print(f"  Connection points: {get_xt60_connection_points()}")
