"""3S 1300mAh Racing LiPo Battery - Build123d model.

Simplified box model with rounded edges, balance connector tab,
and XT60 power leads. Used for CG calculation, bay sizing, and
collision checking in the fuselage assembly.

Run this file directly to view in OCP CAD Viewer:
    python src/cad/hardware/battery.py
"""

from build123d import *
from ocp_vscode import show

from src.core.specs import SAILPLANE

# Pull dimensions from single source of truth
SPEC = SAILPLANE.battery


def build_battery() -> Part:
    """Build a 3D model of the racing LiPo battery pack."""
    L = SPEC.length   # 78mm
    W = SPEC.width    # 38mm
    H = SPEC.height   # 28mm

    with BuildPart() as battery:
        # Main battery body - rounded box
        Box(L, W, H)
        # Round the long edges (typical LiPo heat-shrink shape)
        fillet(battery.edges().filter_by(Axis.X), radius=3.0)

        # Balance connector tab (JST-XH) on one end
        with Locations([(L / 2 - 2, 0, H / 2)]):
            Box(5, 10, 4, align=(Align.MAX, Align.CENTER, Align.MIN))

    return battery.part


def build_xt60_male() -> Part:
    """Build a simplified XT60 male connector."""
    with BuildPart() as connector:
        # Main body
        Box(16, 8, 15.8)
        fillet(connector.edges().filter_by(Axis.Z), radius=1.0)

        # Two pins
        with Locations([(0, -4, 0), (0, 4, 0)]):
            Cylinder(radius=1.75, height=6.5,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

    return connector.part


def build_battery_with_connector() -> Compound:
    """Build battery + XT60 connector as an assembly."""
    battery = build_battery()
    xt60 = build_xt60_male()

    # Position XT60 at the front of the battery
    xt60_positioned = xt60.moved(
        Location((-SPEC.length / 2 - 8, 0, 0))
    )

    return Compound([battery, xt60_positioned])


if __name__ == "__main__":
    assembly = build_battery_with_connector()
    show(assembly, names=["Battery + XT60"])
    print(f"Battery: {SPEC.length}x{SPEC.width}x{SPEC.height}mm, {SPEC.weight}g")
    print(f"Total with connector: {SPEC.weight_with_connector}g")
