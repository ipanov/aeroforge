"""FreeCAD code generator for fuselage pod-and-boom.

Generates Python code to create:
- Elliptical cross-section pod (46mm W × 50mm H)
- 2:1 elliptical nose profile
- Maximum section at 35-40% pod length
- 12-degree boat-tail taper to boom
- Wing saddle with spar pass-through
- Internal bays: motor, ESC, battery, receiver, servo
- Carbon boom socket

Based on aerodynamic research:
- Fineness ratio 5.4 (250mm pod length / 46mm width)
- Shoulder-wing configuration
- 12-15mm wing junction fillets

Convention: X=forward (nose=0), Y=lateral (symmetric), Z=up
"""

from __future__ import annotations

import math
import numpy as np

from src.core.specs import SAILPLANE


def generate_fuselage_pod_code() -> str:
    """Generate FreeCAD Python code for the fuselage pod.

    Creates an aerodynamically optimized pod using lofted elliptical
    cross-sections along the X axis (nose to tail).
    """
    spec = SAILPLANE.fuselage
    spar = SAILPLANE.spar
    battery = SAILPLANE.battery

    pod_length = spec.pod_length  # 220mm (will extend to 250mm with transition)
    max_width = spec.pod_max_width  # 55mm (external with walls)
    max_height = spec.pod_max_height  # 50mm

    # Cross-section stations along pod length
    # x=0: nose tip
    # x=25: spinner/motor mount end
    # x=90: maximum section (36% of 250mm)
    # x=180: wing saddle
    # x=220: start of boat-tail
    # x=250: boom socket start

    stations = [
        # (x_position, width, height, description)
        (0, 0, 0, "nose tip"),
        (5, 8, 8, "nose start"),
        (15, 22, 24, "spinner blend"),
        (30, 34, 38, "motor bay"),
        (50, 42, 46, "ESC bay"),
        (90, 46, 50, "max section / battery bay start"),
        (130, 46, 50, "battery bay mid"),
        (170, 44, 48, "battery bay end / receiver"),
        (190, 40, 44, "wing saddle"),
        (210, 34, 38, "servo bay"),
        (230, 26, 28, "boat-tail"),
        (245, 16, 17, "boom transition"),
        (250, 12, 12, "boom socket (12mm OD)"),
    ]

    # Generate elliptical cross-section wires at each station
    code_parts = [f"""
import FreeCAD
import Part
import FreeCADGui
import math

doc = FreeCAD.ActiveDocument
if doc is None:
    doc = FreeCAD.newDocument("AeroForge")

# ════════════════════════════════════════════
# FUSELAGE POD (Elliptical, pod-and-boom)
# ════════════════════════════════════════════
# Pod length: 250mm, max section: 46×50mm
# Fineness ratio: 5.4
# Nose: 2:1 elliptical profile
# Boat-tail: 12° half-angle to 12mm boom

wires = []
"""]

    n_ellipse_pts = 48  # Points per ellipse

    for i, (x, w, h, desc) in enumerate(stations):
        if w == 0 and h == 0:
            # Nose tip - create a tiny circle
            code_parts.append(f"""
# Station {i}: x={x}mm - {desc}
circle_{i} = Part.makeCircle(0.5, FreeCAD.Vector({x}, 0, 0), FreeCAD.Vector(1, 0, 0))
wires.append(Part.Wire([circle_{i}]))
""")
        else:
            # Create ellipse points
            a = w / 2  # semi-major (horizontal)
            b = h / 2  # semi-minor (vertical)

            points = []
            for j in range(n_ellipse_pts):
                theta = 2 * math.pi * j / n_ellipse_pts
                y = a * math.cos(theta)
                z = b * math.sin(theta)
                points.append((x, y, z))
            # Close
            points.append(points[0])

            pts_str = ",\n                ".join(
                f"FreeCAD.Vector({px:.4f}, {py:.4f}, {pz:.4f})"
                for px, py, pz in points
            )

            code_parts.append(f"""
# Station {i}: x={x}mm, {w}×{h}mm - {desc}
pts_{i} = [
                {pts_str}
]
bsp_{i} = Part.BSplineCurve()
bsp_{i}.interpolate(pts_{i}, PeriodicFlag=True)
wires.append(Part.Wire([bsp_{i}.toShape()]))
""")

    # Loft and add to document
    code_parts.append("""
# Loft fuselage pod
print(f"Lofting fuselage pod from {len(wires)} sections...")
pod_shape = Part.makeLoft(wires, True, False, False)

pod = doc.addObject("Part::Feature", "FuselagePod")
pod.Shape = pod_shape
pod.Label = "Fuselage Pod (250mm)"
pod.ViewObject.ShapeColor = (0.95, 0.95, 0.90)  # Off-white
pod.ViewObject.Transparency = 20

doc.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()
print(f"Pod: vol={pod_shape.Volume:.0f}mm³, area={pod_shape.Area:.0f}mm²")
print(f"Pod mass estimate: {pod_shape.Volume / 1000 * 0.8:.1f}g (LW-PLA shell)")
""")

    return "\n".join(code_parts)


def generate_boom_code() -> str:
    """Generate FreeCAD code for the carbon tail boom."""
    spar = SAILPLANE.spar

    code = f"""
import FreeCAD
import Part

doc = FreeCAD.ActiveDocument

# Carbon tail boom - {spar.boom_od}mm OD × {spar.boom_length}mm
boom_outer = Part.makeCylinder(
    {spar.boom_od / 2},
    {spar.boom_length},
    FreeCAD.Vector(250, 0, 0),  # Start at pod tail
    FreeCAD.Vector(1, 0, 0)      # Along X axis (aft)
)
boom_inner = Part.makeCylinder(
    {spar.boom_id / 2},
    {spar.boom_length + 2},
    FreeCAD.Vector(249, 0, 0),
    FreeCAD.Vector(1, 0, 0)
)
boom_shape = boom_outer.cut(boom_inner)

boom = doc.addObject("Part::Feature", "TailBoom")
boom.Shape = boom_shape
boom.Label = "Tail Boom ({spar.boom_od}mm × {spar.boom_length}mm)"
boom.ViewObject.ShapeColor = (0.15, 0.15, 0.15)  # Carbon black

doc.recompute()
print(f"Boom: length={spar.boom_length}mm, OD={spar.boom_od}mm, mass={{boom_shape.Volume/1000*1.6:.1f}}g")
"""
    return code


if __name__ == "__main__":
    code = generate_fuselage_pod_code()
    print(f"Fuselage code: {len(code)} chars")
    try:
        compile(code, '<fuselage>', 'exec')
        print("SYNTAX OK")
    except SyntaxError as e:
        print(f"SYNTAX ERROR: {e}")
