"""Build H-Stab in FreeCAD via RPC."""
import xmlrpc.client

server = xmlrpc.client.ServerProxy('http://localhost:9875', allow_none=True)

code = '''
import FreeCAD, Part, FreeCADGui, math

doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("AeroForge")

def naca0009_pts(chord, y_pos, n=20):
    pts = []
    for i in range(n+1):
        beta = i * math.pi / n
        x = (1 - math.cos(beta)) / 2
        t = 0.09
        yt = 5*t*(0.2969*x**0.5 - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)
        pts.append(FreeCAD.Vector(x*chord, y_pos, yt*chord))
    for i in range(n, -1, -1):
        beta = i * math.pi / n
        x = (1 - math.cos(beta)) / 2
        t = 0.09
        yt = 5*t*(0.2969*x**0.5 - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)
        pts.append(FreeCAD.Vector(x*chord, y_pos, -yt*chord))
    return pts

chord = 95
half_span = 225

root_pts = naca0009_pts(chord, 0)
tip_r_pts = naca0009_pts(chord, half_span)
tip_l_pts = naca0009_pts(chord, -half_span)

root_bsp = Part.BSplineCurve()
root_bsp.interpolate(root_pts, PeriodicFlag=True)
root_w = Part.Wire([root_bsp.toShape()])

tip_r_bsp = Part.BSplineCurve()
tip_r_bsp.interpolate(tip_r_pts, PeriodicFlag=True)
tip_r_w = Part.Wire([tip_r_bsp.toShape()])

tip_l_bsp = Part.BSplineCurve()
tip_l_bsp.interpolate(tip_l_pts, PeriodicFlag=True)
tip_l_w = Part.Wire([tip_l_bsp.toShape()])

hr = Part.makeLoft([root_w, tip_r_w], True, False, False)
hl = Part.makeLoft([root_w, tip_l_w], True, False, False)
h = hr.fuse(hl)

o = doc.addObject("Part::Feature", "HStab")
o.Shape = h
o.Label = "HStab 450mm NACA0009"
o.ViewObject.ShapeColor = (0.85, 0.85, 0.95)
doc.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()

bb = h.BoundBox
print("HStab: " + str(round(bb.XLength,1)) + "x" + str(round(bb.YLength,1)) + "x" + str(round(bb.ZLength,1)) + "mm")
print("Volume: " + str(round(h.Volume)) + "mm3")
print("Mass LW-PLA: " + str(round(h.Volume/1000*0.54, 1)) + "g")
'''

result = server.execute_code(code)
print(result.get('message', '').strip())

# Take screenshots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from hooks.freecad_rpc_helper import FreecadRPC
rpc = FreecadRPC()
paths = rpc.take_validation_screenshots('HStab')
print(f'{len(paths)} screenshots saved')

bb = rpc.get_bounding_box('HStab')
if bb:
    print(f"Span={bb.get('Y',0):.0f}mm Chord={bb.get('X',0):.0f}mm")
