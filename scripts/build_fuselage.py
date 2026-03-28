"""Build aerodynamic fuselage with integrated tail in FreeCAD.

All 3D-printed, slides onto 4x 1mm carbon rod longerons.
No separate carbon boom tube.

Cross-section stations (X = forward, nose at X=0):
  X=0:     Nose tip (spinner interface, ~5mm)
  X=25:    Spinner blend (22mm wide)
  X=50:    Motor bay (34mm wide)
  X=90:    Max section (46x50mm ellipse) - battery bay start
  X=170:   Battery bay end / receiver area
  X=200:   Wing saddle (spar pass-through)
  X=250:   Aft of wing, servo bay
  X=350:   Mid-taper
  X=500:   Rear fuselage (narrowing)
  X=700:   Tail section start
  X=850:   H-stab root
  X=900:   V-stab root / tail tip
"""
import xmlrpc.client
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

server = xmlrpc.client.ServerProxy('http://localhost:9875', allow_none=True)


def ellipse_wire_code(x_pos, width, height, n=24):
    """Generate FreeCAD code for an ellipse wire at X position.

    The ellipse is in the YZ plane at X=x_pos.
    Y = lateral (width), Z = vertical (height).
    """
    pts = []
    a = width / 2   # semi-width
    b = height / 2  # semi-height
    for i in range(n):
        theta = 2 * math.pi * i / n
        y = a * math.cos(theta)
        z = b * math.sin(theta)
        pts.append(f'FreeCAD.Vector({x_pos:.1f},{y:.3f},{z:.3f})')
    pts.append(pts[0])  # close
    return ', '.join(pts)


# Define fuselage stations: (x_pos, width, height)
stations = [
    (0,    2,    2),      # Nose tip
    (8,    12,   12),     # Nose start
    (20,   24,   26),     # Spinner blend
    (40,   36,   40),     # Motor bay
    (70,   44,   48),     # Expanding
    (100,  46,   50),     # Max section - battery start
    (140,  46,   50),     # Battery mid
    (175,  46,   50),     # Battery end / receiver
    (210,  44,   48),     # Wing saddle area
    (250,  38,   42),     # Aft of wing
    (320,  28,   30),     # Tapering
    (420,  20,   22),     # Mid-rear
    (550,  14,   16),     # Narrowing
    (700,  10,   12),     # Tail section
    (800,  8,    10),     # Near tail
    (870,  6,    8),      # H-stab root area
    (920,  4,    5),      # Tail tip
    (940,  2,    2),      # Tail end
]

# Step 1: Create all ellipse wires
print("Creating fuselage cross-sections...")
for i, (x, w, h) in enumerate(stations):
    pts_str = ellipse_wire_code(x, w, h)
    code = (
        'import FreeCAD, Part\n'
        'doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("AeroForge")\n'
        f'pts = [{pts_str}]\n'
        'edges = []\n'
        'for j in range(len(pts)-1):\n'
        '    if pts[j].distanceToPoint(pts[j+1]) > 0.001:\n'
        '        edges.append(Part.makeLine(pts[j], pts[j+1]))\n'
        'w = Part.Wire(edges)\n'
        f'doc.addObject("Part::Feature", "fs_{i}").Shape = w\n'
        'doc.recompute()\n'
        f'print("Station {i}: x={x} w={w} h={h}")\n'
    )
    r = server.execute_code(code)
    msg = r.get('message', '')
    if 'ERROR' in msg or 'Error' in msg:
        print(f"FAILED station {i}: {msg}")
        break
    else:
        print(f"  Station {i}: x={x}mm, {w}x{h}mm")

# Step 2: Loft all sections into fuselage body
print("\nLofting fuselage...")
wire_names = ', '.join(f'"fs_{i}"' for i in range(len(stations)))
loft_code = (
    'import FreeCAD, Part, FreeCADGui\n'
    'doc = FreeCAD.ActiveDocument\n'
    'try:\n'
    f'    names = [{wire_names}]\n'
    '    wires = [Part.Wire(doc.getObject(n).Shape.Edges) for n in names]\n'
    '    fuse = Part.makeLoft(wires, True, False, False)\n'
    '    o = doc.addObject("Part::Feature", "Fuselage")\n'
    '    o.Shape = fuse\n'
    '    o.Label = "Fuselage Pod"\n'
    '    o.ViewObject.ShapeColor = (0.92, 0.92, 0.88)\n'
    '    o.ViewObject.Transparency = 30\n'
    '    for n in names:\n'
    '        doc.removeObject(n)\n'
    '    doc.recompute()\n'
    '    FreeCADGui.ActiveDocument.ActiveView.fitAll()\n'
    '    bb = fuse.BoundBox\n'
    '    print("Fuselage: " + str(round(bb.XLength)) + "x" + str(round(bb.YLength)) + "x" + str(round(bb.ZLength)) + "mm")\n'
    '    print("Volume: " + str(round(fuse.Volume)) + "mm3")\n'
    'except Exception as e:\n'
    '    import traceback; print("LOFT ERROR: " + str(e)); traceback.print_exc()\n'
)
r = server.execute_code(loft_code)
print(r.get('message', ''))

# Step 3: Add 4 longeron channels (1mm carbon rods)
print("Adding longeron channels...")
longeron_code = (
    'import FreeCAD, Part\n'
    'doc = FreeCAD.ActiveDocument\n'
    'fuse_obj = doc.getObject("Fuselage")\n'
    'if fuse_obj:\n'
    '    fuse_shape = fuse_obj.Shape\n'
    '    # 4 longerons at 45-degree positions in the cross-section\n'
    '    # At max section (46x50mm), longerons at ~15mm from center\n'
    '    positions = [\n'
    '        (10, 12),    # top-right\n'
    '        (-10, 12),   # top-left\n'
    '        (10, -12),   # bottom-right\n'
    '        (-10, -12),  # bottom-left\n'
    '    ]\n'
    '    rod_r = 0.6  # 1mm rod + 0.1mm clearance = 0.6mm radius channel\n'
    '    for idx, (y, z) in enumerate(positions):\n'
    '        rod = Part.makeCylinder(rod_r, 940, FreeCAD.Vector(0, y, z), FreeCAD.Vector(1, 0, 0))\n'
    '        fuse_shape = fuse_shape.cut(rod)\n'
    '    fuse_obj.Shape = fuse_shape\n'
    '    doc.recompute()\n'
    '    print("4 longeron channels cut")\n'
    'else:\n'
    '    print("ERROR: Fuselage not found")\n'
)
r = server.execute_code(longeron_code)
print(r.get('message', ''))

# Step 4: Screenshots + validation
print("\nValidating...")
from hooks.freecad_rpc_helper import FreecadRPC
rpc = FreecadRPC()

# Fit view
server.execute_code('import FreeCADGui; FreeCADGui.ActiveDocument.ActiveView.fitAll()')

paths = rpc.take_validation_screenshots('Fuselage')
bb = rpc.get_bounding_box('Fuselage')
if bb:
    print(f"Fuselage: {bb.get('X',0):.0f}x{bb.get('Y',0):.0f}x{bb.get('Z',0):.0f}mm")
    print(f"Volume: {bb.get('VOL',0):.0f}mm3")
    print(f"Mass (LW-PLA): {bb.get('VOL',0)/1000*0.8:.1f}g")
    print(f"{len(paths)} screenshots saved")
else:
    print("FUSELAGE NOT FOUND")
