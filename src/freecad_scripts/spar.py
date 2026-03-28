"""FreeCAD script to generate a hollow carbon spar tube.

Creates a MainSpar object: hollow cylinder along Y axis matching
SAILPLANE spec dimensions.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.specs import SAILPLANE


def generate_spar_code(length_mm: float | None = None) -> str:
    """Generate FreeCAD Python code for a hollow carbon spar tube.

    Args:
        length_mm: Spar length in mm. Defaults to SAILPLANE.wing.panel_span.

    Returns:
        FreeCAD-executable Python code string.
    """
    spar = SAILPLANE.spar
    if length_mm is None:
        length_mm = SAILPLANE.wing.panel_span

    outer_radius = spar.main_od / 2.0
    inner_radius = spar.main_id / 2.0

    return f"""
import FreeCAD
import Part

doc = FreeCAD.ActiveDocument
if doc is None:
    doc = FreeCAD.newDocument("SparTest")

# Remove existing MainSpar if present
old = doc.getObject("MainSpar")
if old is not None:
    doc.removeObject("MainSpar")

# Create outer cylinder along Y axis
outer = Part.makeCylinder({outer_radius}, {length_mm}, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0))

# Create inner cylinder (bore) along Y axis
inner = Part.makeCylinder({inner_radius}, {length_mm}, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0))

# Cut inner from outer to make hollow tube
hollow = outer.cut(inner)

# Add to document
spar_obj = doc.addObject("Part::Feature", "MainSpar")
spar_obj.Shape = hollow

doc.recompute()

# Print bounding box for verification
bb = spar_obj.Shape.BoundBox
print(f"MainSpar created successfully")
print(f"BB_X:{{bb.XLength:.6f}}")
print(f"BB_Y:{{bb.YLength:.6f}}")
print(f"BB_Z:{{bb.ZLength:.6f}}")
print(f"Volume: {{spar_obj.Shape.Volume:.2f}} mm³")
"""


if __name__ == "__main__":
    print(generate_spar_code())
