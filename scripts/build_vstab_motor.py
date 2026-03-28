"""Build V-Stab and motor in FreeCAD via RPC."""
import xmlrpc.client
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

server = xmlrpc.client.ServerProxy('http://localhost:9875', allow_none=True)

# ═══ V-STAB ═══
vstab_code = (
    'import FreeCAD, Part, FreeCADGui, math\n'
    'doc = FreeCAD.ActiveDocument\n'
    'try:\n'
    '    def naca0009_wire(chord, y, z_off, n=25):\n'
    '        pts = []\n'
    '        for i in range(n+1):\n'
    '            beta = i * 3.14159265 / n\n'
    '            x = (1 - math.cos(beta)) / 2\n'
    '            yt = 5*0.09*(0.2969*x**0.5 - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)\n'
    '            pts.append(FreeCAD.Vector(x*chord, yt*chord, z_off))\n'
    '        for i in range(n-1, 0, -1):\n'
    '            beta = i * 3.14159265 / n\n'
    '            x = (1 - math.cos(beta)) / 2\n'
    '            yt = 5*0.09*(0.2969*x**0.5 - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)\n'
    '            pts.append(FreeCAD.Vector(x*chord, -yt*chord, z_off))\n'
    '        pts.append(pts[0])\n'
    '        edges = []\n'
    '        for i in range(len(pts)-1):\n'
    '            if pts[i].distanceToPoint(pts[i+1]) > 0.001:\n'
    '                edges.append(Part.makeLine(pts[i], pts[i+1]))\n'
    '        return Part.Wire(edges)\n'
    '    root_w = naca0009_wire(110, 0, 0)\n'
    '    tip_w = naca0009_wire(60, 0, 140)\n'
    '    vs = Part.makeLoft([root_w, tip_w], True, False, False)\n'
    '    o = doc.addObject("Part::Feature", "VStab")\n'
    '    o.Shape = vs\n'
    '    o.Label = "VStab 140mm NACA0009"\n'
    '    o.ViewObject.ShapeColor = (0.85, 0.95, 0.85)\n'
    '    doc.recompute()\n'
    '    bb = vs.BoundBox\n'
    '    print("VStab " + str(round(bb.XLength,1)) + "x" + str(round(bb.YLength,1)) + "x" + str(round(bb.ZLength,1)) + "mm")\n'
    '    print("Vol " + str(round(vs.Volume)) + "mm3")\n'
    'except Exception as e:\n'
    '    import traceback; print("ERROR: " + str(e)); traceback.print_exc()\n'
)

r = server.execute_code(vstab_code)
print("VStab:", r.get('message', '').strip())

# ═══ MOTOR (Hacker A20-22L EVO) ═══
motor_code = (
    'import FreeCAD, Part, FreeCADGui\n'
    'doc = FreeCAD.ActiveDocument\n'
    'try:\n'
    '    # Motor can: 28mm dia, 34mm long\n'
    '    can = Part.makeCylinder(14, 34, FreeCAD.Vector(0,0,0), FreeCAD.Vector(-1,0,0))\n'
    '    # Shaft: 3mm dia, 15mm protruding\n'
    '    shaft = Part.makeCylinder(1.5, 15, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))\n'
    '    # Back plate: 28mm dia, 2mm thick\n'
    '    back = Part.makeCylinder(14, 2, FreeCAD.Vector(-34,0,0), FreeCAD.Vector(-1,0,0))\n'
    '    # Mount ring: 22mm bolt circle, 3mm thick\n'
    '    mount = Part.makeCylinder(11, 3, FreeCAD.Vector(-36,0,0), FreeCAD.Vector(-1,0,0))\n'
    '    motor = can.fuse(shaft).fuse(back).fuse(mount)\n'
    '    o = doc.addObject("Part::Feature", "Motor")\n'
    '    o.Shape = motor\n'
    '    o.Label = "Hacker A20-22L EVO kv924"\n'
    '    o.ViewObject.ShapeColor = (0.3, 0.3, 0.35)\n'
    '    doc.recompute()\n'
    '    bb = motor.BoundBox\n'
    '    print("Motor " + str(round(bb.XLength,1)) + "x" + str(round(bb.YLength,1)) + "x" + str(round(bb.ZLength,1)) + "mm")\n'
    '    print("Vol " + str(round(motor.Volume)) + "mm3")\n'
    'except Exception as e:\n'
    '    import traceback; print("ERROR: " + str(e)); traceback.print_exc()\n'
)

r = server.execute_code(motor_code)
print("Motor:", r.get('message', '').strip())

# ═══ SPINNER (30mm) ═══
spinner_code = (
    'import FreeCAD, Part, FreeCADGui\n'
    'doc = FreeCAD.ActiveDocument\n'
    'try:\n'
    '    # Spinner: 30mm base dia, ~25mm long, ogive shape\n'
    '    # Approximate as cone + fillet\n'
    '    spinner = Part.makeCone(15, 2, 25, FreeCAD.Vector(15,0,0), FreeCAD.Vector(1,0,0))\n'
    '    # Round the tip\n'
    '    tip = Part.makeSphere(2, FreeCAD.Vector(40,0,0))\n'
    '    spinner = spinner.fuse(tip)\n'
    '    o = doc.addObject("Part::Feature", "Spinner")\n'
    '    o.Shape = spinner\n'
    '    o.Label = "Spinner 30mm"\n'
    '    o.ViewObject.ShapeColor = (0.9, 0.9, 0.9)\n'
    '    doc.recompute()\n'
    '    bb = spinner.BoundBox\n'
    '    print("Spinner " + str(round(bb.XLength,1)) + "x" + str(round(bb.YLength,1)) + "x" + str(round(bb.ZLength,1)) + "mm")\n'
    'except Exception as e:\n'
    '    import traceback; print("ERROR: " + str(e)); traceback.print_exc()\n'
)

r = server.execute_code(spinner_code)
print("Spinner:", r.get('message', '').strip())

# ═══ FIT VIEW ═══
server.execute_code('import FreeCADGui; FreeCADGui.ActiveDocument.ActiveView.fitAll()')

# ═══ SCREENSHOTS + VALIDATION ═══
from hooks.freecad_rpc_helper import FreecadRPC
rpc = FreecadRPC()

for name in ['VStab', 'Motor', 'Spinner']:
    paths = rpc.take_validation_screenshots(name)
    bb = rpc.get_bounding_box(name)
    if bb:
        print(f"{name}: X={bb.get('X',0):.1f} Y={bb.get('Y',0):.1f} Z={bb.get('Z',0):.1f}mm — {len(paths)} screenshots")
    else:
        print(f"{name}: NOT FOUND")

# List all objects
print("\nAll objects:")
print(rpc.get_all_objects())
