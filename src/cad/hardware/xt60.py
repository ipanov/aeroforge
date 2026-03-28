"""XT60 Male Connector - Off-the-shelf component.

Uses the KiCad/Amass reference STEP model for accurate geometry.
The model is imported from components/reference_models/xt60_male_kicad.step.

Reference model dimensions (from KiCad Amass library):
  15.9 x 8.1 x 20.5mm (X x Y x Z in KiCad orientation)

We re-orient to our standard coordinate system:
  X = longitudinal (pin direction, the direction wires come out)
  Y = lateral
  Z = up

Connection points:
  solder_positive: rear face, positive solder cup entry
  solder_negative: rear face, negative solder cup entry
  mating_face: front face center

Run via Claude: cd D:/Repos/aeroforge && PYTHONPATH=. python src/cad/hardware/xt60.py
"""

from pathlib import Path

from build123d import *
from ocp_vscode import show

REFERENCE_STEP = Path(__file__).parent.parent.parent.parent / "components" / "reference_models" / "xt60_male_kicad.step"

# Pin spacing from KiCad model (7.2mm per the filename)
PIN_SPACING_Y = 7.2  # mm center-to-center

# Color
COLOR_XT60 = Color(0.95, 0.85, 0.0)  # Yellow


def build_xt60_male() -> Part:
    """Import the accurate XT60 male STEP model.

    Returns the geometry centered and oriented in our coordinate system.
    """
    ref = import_step(str(REFERENCE_STEP))

    # Center it so origin is at the mating face center
    bb = ref.bounding_box()
    center_y = (bb.min.Y + bb.max.Y) / 2
    center_z = (bb.min.Z + bb.max.Z) / 2

    # Move so mating face (min X, where pins are) is at origin
    centered = ref.moved(Location((-bb.min.X, -center_y, -center_z)))

    return centered


def get_xt60_connection_points() -> dict[str, tuple[float, float, float]]:
    """Named connection points for assembly.

    Based on reference model dimensions.
    """
    ref = import_step(str(REFERENCE_STEP))
    bb = ref.bounding_box()
    depth = bb.max.X - bb.min.X  # ~15.9mm

    return {
        "mating_face": (0, 0, 0),
        "solder_positive": (depth, PIN_SPACING_Y / 2, 0),
        "solder_negative": (depth, -PIN_SPACING_Y / 2, 0),
        "rear_face": (depth, 0, 0),
    }


if __name__ == "__main__":
    xt60 = build_xt60_male()

    bb = xt60.bounding_box()
    show(xt60, names=["XT60 Male (Amass reference)"], colors=[COLOR_XT60])

    print(f"XT60 Male Connector (from KiCad Amass STEP)")
    print(f"  Size: {bb.max.X-bb.min.X:.1f} x {bb.max.Y-bb.min.Y:.1f} x {bb.max.Z-bb.min.Z:.1f}mm")
    print(f"  Connection points: {get_xt60_connection_points()}")
