"""Rebuild Elevator with Splines, fix spar/wire position, colored assembly."""
import sys, os, math, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from build123d import *
from src.cad.airfoils import blend_airfoils, scale_airfoil

t0 = time.time()

HALF_SPAN = 215.0; ROOT_CHORD = 115.0; N_EXP = 2.3
REF_FRAC = 0.45; REF_X = ROOT_CHORD * REF_FRAC
X_HINGE = 60.0; TE_TRUNC = 0.97; FIN_HALF = 3.5
BULL_NOSE_ROOT = 2.5; BULL_NOSE_FADE_Y = 206.0
Y_CAP_START = 210.0; Y_CAP_END = 214.0; N_PTS = 80

def _se(y):
    if abs(y) >= HALF_SPAN or y < 0: return 0.0
    return ROOT_CHORD * (1.0 - (y / HALF_SPAN) ** N_EXP) ** (1.0 / N_EXP)

_c0 = _se(Y_CAP_START)
_sl = (_se(Y_CAP_START) - _se(Y_CAP_START - 0.001)) / 0.001
_ca, _cb = _c0, _sl
_cd = (_ca + 2 * _cb) / 32
_cc = (-_cb - 48 * _cd) / 8

def chord_at(y):
    y = abs(y)
    if y <= Y_CAP_START: return _se(y)
    if y >= Y_CAP_END: return 0.0
    t = y - Y_CAP_START
    return max(0.0, _ca + _cb * t + _cc * t ** 2 + _cd * t ** 3)

def le_x(y): return REF_X - REF_FRAC * chord_at(abs(y))
def te_x(y): return le_x(y) + chord_at(abs(y)) * TE_TRUNC

def bull_nose_depth(y):
    if y >= BULL_NOSE_FADE_Y: return 0.0
    return BULL_NOSE_ROOT * max(0.0, 1.0 - y / BULL_NOSE_FADE_Y)

def get_elevator_section(y_sta):
    c = chord_at(abs(y_sta))
    if c < 2: return None
    lx = le_x(abs(y_sta))
    te = te_x(abs(y_sta))
    elev_chord = te - X_HINGE
    if elev_chord < 1.0: return None

    blend = min(abs(y_sta) / HALF_SPAN, 1.0)
    af = blend_airfoils("ht13", "ht12", blend, N_PTS)
    sc = scale_airfoil(af, c)
    le_idx = int(np.argmin(sc[:, 0]))
    upper = sc[:le_idx + 1][::-1]
    lower = sc[le_idx:]

    hinge_local = X_HINGE - lx
    te_local = te - lx

    def interp_z(surface, x_local):
        s = surface[np.argsort(surface[:, 0])]
        return float(np.interp(x_local, s[:, 0], s[:, 1]))

    zu_hinge = interp_z(upper, hinge_local)
    zl_hinge = interp_z(lower, hinge_local)
    bn = bull_nose_depth(abs(y_sta))

    pts = []
    mid_z = (zu_hinge + zl_hinge) / 2
    r_z = abs(zu_hinge - zl_hinge) / 2

    # Bull-nose arc
    for i in range(13):
        angle = math.pi / 2 - math.pi * i / 12
        arc_x = (X_HINGE - bn * math.cos(angle)) if bn > 0.05 else X_HINGE
        pts.append((arc_x, mid_z + r_z * math.sin(angle)))

    # Lower: hinge -> TE
    for i in range(1, 41):
        t = 0.5 * (1 - math.cos(math.pi * i / 40))
        xl = hinge_local + t * (te_local - hinge_local)
        pts.append((lx + xl, interp_z(lower, min(xl, te_local))))

    # Upper: TE -> hinge
    for i in range(1, 40):
        t = 0.5 * (1 - math.cos(math.pi * i / 40))
        xl = te_local - t * (te_local - hinge_local)
        pts.append((lx + xl, interp_z(upper, max(xl, hinge_local))))

    pts.append(pts[0])
    return pts


print("=" * 60)
print("Elevator_Left v7 — SPLINE loft")
print("=" * 60)

stations = [4.0, 15, 30, 50, 75, 100, 125, 150, 175, 195, 206, 210, 211]
sections = []
for y in stations:
    pts = get_elevator_section(y)
    if pts and len(pts) > 10:
        sections.append((y, pts))
        print(f"  y={y:6.1f}: elev={te_x(y)-X_HINGE:.1f}mm bn={bull_nose_depth(y):.2f}mm {len(pts)}pts")

print(f"\nLofting {len(sections)} Spline sections...")
with BuildPart() as bp:
    for y, pts in sections:
        plane = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
        with BuildSketch(plane) as sk:
            with BuildLine():
                Spline(*[(p[0], p[1]) for p in pts])
            make_face()
    loft()

elevator = bp.part
print(f"  Volume: {elevator.volume:.0f} mm3")

# Bores
elevator = elevator - Location((X_HINGE, 107.5, 0), (90, 0, 0)) * Cylinder(0.3, 215)
elevator = elevator - Location((70.0, 6, 0), (90, 0, 0)) * Cylinder(0.8, 12)

# Export Left
out_el = "cad/components/empennage/Elevator_Left"
os.makedirs(out_el, exist_ok=True)
export_step(elevator, f"{out_el}/Elevator_Left.step")
export_stl(elevator, f"{out_el}/Elevator_Left.stl", tolerance=0.001, angular_tolerance=0.05)

# Mirror Right
elev_r = elevator.mirror(Plane.XZ)
out_er = "cad/components/empennage/Elevator_Right"
os.makedirs(out_er, exist_ok=True)
export_step(elev_r, f"{out_er}/Elevator_Right.step")
export_stl(elev_r, f"{out_er}/Elevator_Right.stl", tolerance=0.001, angular_tolerance=0.05)
print("  Elevator L+R exported")

# Fix Spar position (was at origin, needs X=34.5 along Y)
print("\nRebuilding Spar at X=34.5 along Y...")
spar = Location((34.5, 0, 0), (90, 0, 0)) * Cylinder(1.5, 378)
spar_bore = Location((34.5, 0, 0), (90, 0, 0)) * Cylinder(1.0, 378)
spar = spar - spar_bore
export_step(spar, "cad/components/empennage/HStab_Main_Spar/HStab_Main_Spar.step")

# Fix Wire position
print("Rebuilding Wire at X=60.0 along Y...")
wire = Location((60.0, 0, 0), (90, 0, 0)) * Cylinder(0.25, 424)
export_step(wire, "cad/components/empennage/Hinge_Wire/Hinge_Wire.step")

dt = time.time() - t0
print(f"\nAll rebuilt in {dt:.1f}s")

# === COLORED ASSEMBLY in OCP Viewer ===
print("\nDisplaying colored assembly...")
from ocp_vscode import show, Color as OcpColor

hl = import_step("cad/components/empennage/HStab_Left/HStab_Left_MainBody.step")
hr = import_step("cad/components/empennage/HStab_Right/HStab_Right.step")

show(
    hl, hr, elevator, elev_r, spar, wire,
    names=["HStab_L", "HStab_R", "Elev_L", "Elev_R", "Spar", "Wire"],
    colors=[
        "mediumorchid",    # HStab_L - purple
        "mediumorchid",    # HStab_R - purple
        "hotpink",         # Elev_L - pink
        "hotpink",         # Elev_R - pink
        "dimgray",         # Spar - dark gray (carbon)
        "silver",          # Wire - silver (steel)
    ],
    alphas=[0.5, 0.5, 0.5, 0.5, 1.0, 1.0],  # printed parts transparent, hardware solid
    reset_camera="RESET",
)
print("Colored transparent assembly in OCP Viewer")

# Assembly 3MF
print("Building assembly 3MF...")
import trimesh, lib3mf
meshes = []
for p in [f"{out_el}/Elevator_Left.stl", f"{out_er}/Elevator_Right.stl",
          "cad/components/empennage/HStab_Left/HStab_Left_shell.stl",
          "cad/components/empennage/HStab_Right/HStab_Right.stl"]:
    meshes.append(trimesh.load(p))
combined = trimesh.util.concatenate(meshes)

asm_path = "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly.3mf"
wrapper = lib3mf.get_wrapper()
model = wrapper.CreateModel()
model.SetUnit(lib3mf.ModelUnit.MilliMeter)
mo = model.AddMeshObject()
mo.SetName("HStab_Assembly")
for v in combined.vertices:
    p = lib3mf.Position()
    p.Coordinates[0] = float(v[0]); p.Coordinates[1] = float(v[1]); p.Coordinates[2] = float(v[2])
    mo.AddVertex(p)
for f in combined.faces:
    if f[0] == f[1] or f[1] == f[2] or f[0] == f[2]: continue
    t = lib3mf.Triangle()
    t.Indices[0] = int(f[0]); t.Indices[1] = int(f[1]); t.Indices[2] = int(f[2])
    mo.AddTriangle(t)
cg = model.AddColorGroup()
c = lib3mf.Color(); c.Red = 180; c.Green = 60; c.Blue = 200; c.Alpha = 140
ci = cg.AddColor(c); rid = cg.GetResourceID()
for i in range(mo.GetTriangleCount()):
    tp = lib3mf.TriangleProperties()
    tp.ResourceID = rid; tp.PropertyIDs[0] = ci; tp.PropertyIDs[1] = ci; tp.PropertyIDs[2] = ci
    mo.SetTriangleProperties(i, tp)
mo.SetObjectLevelProperty(rid, ci)
model.AddBuildItem(mo, wrapper.GetIdentityTransform())
writer = model.QueryWriter("3mf")
writer.WriteToFile(asm_path)
print(f"Assembly 3MF: {os.path.getsize(asm_path)/1024:.0f} KB")

os.startfile(os.path.abspath(asm_path))
print("OrcaSlicer launched")


if __name__ == "__main__":
    pass  # already executed at module level
