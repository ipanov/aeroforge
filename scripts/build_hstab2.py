"""Build H-Stab in FreeCAD via RPC - polygon wire approach."""
import xmlrpc.client
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

server = xmlrpc.client.ServerProxy('http://localhost:9875', allow_none=True)

code = (
    'import FreeCAD, Part, FreeCADGui, math\n'
    'doc = FreeCAD.ActiveDocument\n'
    '\n'
    'def naca0009_wire(chord, y_pos, n=30):\n'
    '    pts = []\n'
    '    for i in range(2*n + 1):\n'
    '        if i <= n:\n'
    '            beta = i * math.pi / n\n'
    '            x = (1 - math.cos(beta)) / 2\n'
    '            t = 0.09\n'
    '            yt = 5*t*(0.2969*x**0.5 - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)\n'
    '            pts.append(FreeCAD.Vector(x*chord, y_pos, yt*chord))\n'
    '        else:\n'
    '            j = 2*n - i\n'
    '            beta = j * math.pi / n\n'
    '            x = (1 - math.cos(beta)) / 2\n'
    '            t = 0.09\n'
    '            yt = 5*t*(0.2969*x**0.5 - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)\n'
    '            pts.append(FreeCAD.Vector(x*chord, y_pos, -yt*chord))\n'
    '    pts.append(pts[0])\n'
    '    edges = []\n'
    '    for i in range(len(pts)-1):\n'
    '        edges.append(Part.makeLine(pts[i], pts[i+1]))\n'
    '    return Part.Wire(edges)\n'
    '\n'
    'chord = 95\n'
    'half_span = 225\n'
    '\n'
    'root_w = naca0009_wire(chord, 0)\n'
    'tip_r_w = naca0009_wire(chord, half_span)\n'
    'tip_l_w = naca0009_wire(chord, -half_span)\n'
    '\n'
    'hr = Part.makeLoft([root_w, tip_r_w], True, False, False)\n'
    'hl = Part.makeLoft([root_w, tip_l_w], True, False, False)\n'
    'h = hr.fuse(hl)\n'
    '\n'
    'o = doc.addObject("Part::Feature", "HStab")\n'
    'o.Shape = h\n'
    'o.Label = "HStab 450mm NACA0009"\n'
    'o.ViewObject.ShapeColor = (0.85, 0.85, 0.95)\n'
    'doc.recompute()\n'
    'FreeCADGui.ActiveDocument.ActiveView.fitAll()\n'
    '\n'
    'bb = h.BoundBox\n'
    'print("HStab " + str(round(bb.XLength,1)) + "x" + str(round(bb.YLength,1)) + "x" + str(round(bb.ZLength,1)) + "mm")\n'
    'print("Vol " + str(round(h.Volume)) + "mm3")\n'
)

result = server.execute_code(code)
msg = result.get('message', '') if isinstance(result, dict) else str(result)
print(msg.strip())

# Screenshots and validation
from hooks.freecad_rpc_helper import FreecadRPC
rpc = FreecadRPC()
paths = rpc.take_validation_screenshots('HStab')
print(f'{len(paths)} screenshots')
bb = rpc.get_bounding_box('HStab')
if bb:
    print(f"Span={bb.get('Y',0):.0f}mm Chord={bb.get('X',0):.0f}mm Thick={bb.get('Z',0):.1f}mm")
else:
    print("HStab NOT FOUND - loft failed")
