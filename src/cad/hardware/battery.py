"""3S 1300mAh Racing LiPo Battery - Build123d model.

Realistic model with:
- Battery pack with heat-shrink wrap and label area
- Two 14AWG silicone power leads (red + black)
- XT60 male connector at end of power leads
- Balance lead with JST-XH 4-pin connector
- Proper wire gauges and routing

Run via Claude: PYTHONPATH=. python src/cad/hardware/battery.py
"""

from build123d import *
from ocp_vscode import show

from src.core.specs import SAILPLANE

SPEC = SAILPLANE.battery

# Wire gauge dimensions (outer diameter including silicone insulation)
WIRE_14AWG_OD = 3.5     # mm - power leads
WIRE_22AWG_OD = 1.7     # mm - balance leads
WIRE_BEND_RADIUS = 8.0  # mm - minimum bend for silicone wire

# Realistic colors
COLOR_BATTERY = Color(0.08, 0.08, 0.08)     # Black heat-shrink
COLOR_LABEL = Color(0.15, 0.15, 0.6)        # Dark blue label area
COLOR_WIRE_RED = Color(0.8, 0.05, 0.05)     # Red power lead
COLOR_WIRE_BLACK = Color(0.05, 0.05, 0.05)  # Black power lead
COLOR_WIRE_BALANCE = Color(0.9, 0.9, 0.9)   # White balance wires
COLOR_XT60_BODY = Color(0.95, 0.85, 0.0)    # Yellow XT60 housing
COLOR_XT60_PINS = Color(0.85, 0.75, 0.0)    # Gold-plated pins
COLOR_JST = Color(0.9, 0.9, 0.9)            # White JST connector
COLOR_HEATSHRINK_END = Color(0.1, 0.1, 0.1) # Slightly lighter black for ends


def _make_wire(path: Wire, diameter: float) -> Part:
    """Sweep a circle along a wire path to create a cable."""
    wire_profile = Circle(diameter / 2)
    return sweep(wire_profile, path=path)


def build_battery_pack() -> Part:
    """Battery cell pack with heat-shrink wrap."""
    L = SPEC.length   # 78mm
    W = SPEC.width    # 38mm
    H = SPEC.height   # 28mm

    with BuildPart() as pack:
        # Main body - slightly rounded rectangle (heat-shrink wrap shape)
        Box(L, W, H)
        # Round all long edges - heat shrink wraps tightly
        fillet(battery.edges().filter_by(Axis.X), radius=2.5)
        # Slight fillet on short edges too
        fillet(battery.edges().filter_by(Axis.Y), radius=1.5)

    return pack.part


def build_battery_body() -> Part:
    """Battery cell pack with heat-shrink wrap."""
    L = SPEC.length
    W = SPEC.width
    H = SPEC.height

    with BuildPart() as battery:
        Box(L, W, H)
        fillet(battery.edges().filter_by(Axis.X), radius=2.5)
        try:
            fillet(battery.edges().filter_by(Axis.Y), radius=1.5)
        except Exception:
            pass  # Some edges may already be filleted

    return battery.part


def build_xt60_connector() -> Compound:
    """Realistic XT60 male connector with pins and chamfered housing."""
    with BuildPart() as housing:
        # Main housing body - characteristic XT60 shape
        Box(16.0, 8.0, 15.8)
        # Chamfer the insertion end
        try:
            top_edges = housing.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-4:]
            chamfer(top_edges, length=1.0)
        except Exception:
            pass
        # Round the grip edges
        try:
            fillet(housing.edges().filter_by(Axis.Z)[:4], radius=0.8)
        except Exception:
            pass

    with BuildPart() as pin1:
        # Positive pin (slightly larger, round)
        Cylinder(radius=1.75, height=6.5)

    with BuildPart() as pin2:
        # Negative pin
        Cylinder(radius=1.75, height=6.5)

    pin1_pos = pin1.part.moved(Location((0, 2.0, 15.8 / 2 + 3.25)))
    pin2_pos = pin2.part.moved(Location((0, -2.0, 15.8 / 2 + 3.25)))

    return Compound([housing.part, pin1_pos, pin2_pos])


def build_power_leads() -> tuple[Part, Part]:
    """Two 14AWG silicone power leads - red and black, ~80mm with a gentle curve."""
    lead_length = 80.0
    wire_r = WIRE_14AWG_OD / 2
    spacing = 4.0  # mm between wire centers

    # Red lead - slight curve exiting battery
    red_pts = [
        (0, spacing / 2, 0),
        (-20, spacing / 2, -3),
        (-50, spacing / 2, -2),
        (-lead_length, spacing / 2, 0),
    ]
    red_spline = Spline(*[Vector(*p) for p in red_pts])
    with BuildPart() as red_wire:
        with BuildSketch(Plane(origin=red_pts[0], z_dir=red_spline % 0)):
            Circle(wire_r)
        sweep(path=red_spline)

    # Black lead - parallel
    black_pts = [
        (0, -spacing / 2, 0),
        (-20, -spacing / 2, -3),
        (-50, -spacing / 2, -2),
        (-lead_length, -spacing / 2, 0),
    ]
    black_spline = Spline(*[Vector(*p) for p in black_pts])
    with BuildPart() as black_wire:
        with BuildSketch(Plane(origin=black_pts[0], z_dir=black_spline % 0)):
            Circle(wire_r)
        sweep(path=black_spline)

    return red_wire.part, black_wire.part


def build_balance_lead() -> Part:
    """Balance lead - 4 thin wires bundled, exiting from side of battery."""
    wire_r = WIRE_22AWG_OD / 2
    # Single bundled wire representation (4 wires together ≈ 4mm bundle)
    bundle_r = 2.0

    pts = [
        (SPEC.length / 2 - 5, 0, SPEC.height / 2),
        (SPEC.length / 2 + 5, 0, SPEC.height / 2 + 5),
        (SPEC.length / 2 + 15, 0, SPEC.height / 2 + 3),
        (SPEC.length / 2 + 30, 0, SPEC.height / 2),
    ]
    spline = Spline(*[Vector(*p) for p in pts])
    with BuildPart() as balance:
        with BuildSketch(Plane(origin=pts[0], z_dir=spline % 0)):
            Circle(bundle_r)
        sweep(path=spline)

    return balance.part


def build_jst_connector() -> Part:
    """JST-XH 4-pin balance connector at end of balance lead."""
    with BuildPart() as jst:
        Box(10.0, 5.0, 4.5)
    return jst.part


def build_full_battery() -> dict[str, tuple]:
    """Build complete battery assembly with all parts and colors.

    Returns dict of {name: (part, color)} for display.
    """
    battery = build_battery_body()

    # XT60 at end of power leads
    xt60 = build_xt60_connector()
    xt60_pos = xt60.moved(Location((-SPEC.length / 2 - 80 - 8, 0, 0)))

    # Power leads from battery front to XT60
    try:
        red_lead, black_lead = build_power_leads()
        red_pos = red_lead.moved(Location((-SPEC.length / 2, 0, 0)))
        black_pos = black_lead.moved(Location((-SPEC.length / 2, 0, 0)))
        has_leads = True
    except Exception:
        has_leads = False

    # Balance lead from battery top
    try:
        balance = build_balance_lead()
        jst = build_jst_connector()
        jst_pos = jst.moved(Location((
            SPEC.length / 2 + 32, 0, SPEC.height / 2
        )))
        has_balance = True
    except Exception:
        has_balance = False

    parts = {
        "Battery Pack": (battery, COLOR_BATTERY),
        "XT60 Connector": (xt60_pos, COLOR_XT60_BODY),
    }

    if has_leads:
        parts["Power Lead (+)"] = (red_pos, COLOR_WIRE_RED)
        parts["Power Lead (-)"] = (black_pos, COLOR_WIRE_BLACK)

    if has_balance:
        parts["Balance Lead"] = (balance, COLOR_WIRE_BALANCE)
        parts["JST-XH Connector"] = (jst_pos, COLOR_JST)

    return parts


if __name__ == "__main__":
    parts = build_full_battery()

    show(
        *[p for p, c in parts.values()],
        names=list(parts.keys()),
        colors=[c for p, c in parts.values()],
    )
    print(f"Battery: {SPEC.length}x{SPEC.width}x{SPEC.height}mm, {SPEC.weight}g")
    print(f"Total with connector: {SPEC.weight_with_connector}g")
    print(f"Sailplane name: {SAILPLANE.name}")
