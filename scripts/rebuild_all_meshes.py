"""Regenerate print meshes (with geodesic ribs) for ALL H-Stab components."""
import sys, os, math, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import trimesh, lib3mf
from build123d import import_step, export_stl, Plane
from ocp_vscode import show, save_screenshot
from src.cad.airfoils import blend_airfoils, scale_airfoil

t0 = time.time()

HALF_SPAN = 215.0; ROOT_CHORD = 115.0; N_EXP = 2.3; REF_FRAC = 0.45
REF_X = ROOT_CHORD * REF_FRAC; X_HINGE = 60.0; WALL = 0.45; N_AF = 80
Y_CAP_START = 210.0; Y_CAP_END = 214.0

def _se(y):
    if abs(y) >= HALF_SPAN or y < 0: return 0.0
    return ROOT_CHORD * (1 - (y / HALF_SPAN) ** N_EXP) ** (1 / N_EXP)
_c0 = _se(Y_CAP_START); _sl = (_se(Y_CAP_START) - _se(Y_CAP_START - 0.001)) / 0.001
_ca, _cb = _c0, _sl; _cd = (_ca + 2 * _cb) / 32; _cc = (-_cb - 48 * _cd) / 8

def chord_at(y):
    y = abs(y)
    if y <= Y_CAP_START: return _se(y)
    if y >= Y_CAP_END: return 0.0
    t = y - Y_CAP_START; return max(0, _ca + _cb * t + _cc * t**2 + _cd * t**3)

def le_x(y): return REF_X - REF_FRAC * chord_at(abs(y))

def get_z(y, x):
    c = chord_at(abs(y))
    if c < 2: return None
    lx = le_x(abs(y)); xl = x - lx
    if xl < 0.5 or xl > c - 0.5: return None
    blend = min(abs(y) / HALF_SPAN, 1.0)
    af = blend_airfoils("ht13", "ht12", blend, N_AF)
    sc = scale_airfoil(af, c)
    li = np.argmin(sc[:, 0])
    u = sc[:li + 1][::-1]; l = sc[li:]
    us = u[np.argsort(u[:, 0])]; ls = l[np.argsort(l[:, 0])]
    return float(np.interp(xl, us[:, 0], us[:, 1])) - WALL, float(np.interp(xl, ls[:, 0], ls[:, 1])) + WALL

def make_ribs(span_ys, xmin_fn, xmax_val, spacing=12.0):
    rv = []; rf = []
    for i in range(len(span_ys) - 1):
        ya, yb = span_ys[i], span_ys[i + 1]
        dy = yb - ya; xs = dy * math.tan(math.radians(45))
        xmin = max(xmin_fn(ya), xmin_fn(yb)) + 4; xmax = xmax_val - 2
        if xmax <= xmin: continue
        for s in [+1, -1]:
            x = xmin
            while x < xmax:
                xa, xb = x, x + s * xs
                if xmin <= xa <= xmax and xmin <= xb <= xmax:
                    ba = get_z(ya, xa); bb = get_z(yb, xb)
                    if ba and bb:
                        zua, zla = ba; zub, zlb = bb
                        if zua > zla + 0.3 and zub > zlb + 0.3:
                            b = len(rv)
                            rv.extend([[xa, ya, zua], [xa, ya, zla], [xb, yb, zub], [xb, yb, zlb]])
                            rf.extend([[b, b+2, b+3], [b, b+3, b+1]])
                x += spacing
    if not rv: return None
    return trimesh.Trimesh(vertices=np.array(rv, dtype=np.float32), faces=np.array(rf, dtype=np.int32))

def make_3mf(mesh, path, name, r, g, b, a=140):
    wrapper = lib3mf.get_wrapper(); model = wrapper.CreateModel()
    model.SetUnit(lib3mf.ModelUnit.MilliMeter)
    mo = model.AddMeshObject(); mo.SetName(name)
    for v in mesh.vertices:
        p = lib3mf.Position()
        p.Coordinates[0] = float(v[0]); p.Coordinates[1] = float(v[1]); p.Coordinates[2] = float(v[2])
        mo.AddVertex(p)
    for f in mesh.faces:
        if f[0] == f[1] or f[1] == f[2] or f[0] == f[2]: continue
        t = lib3mf.Triangle()
        t.Indices[0] = int(f[0]); t.Indices[1] = int(f[1]); t.Indices[2] = int(f[2])
        mo.AddTriangle(t)
    cg = model.AddColorGroup(); c = lib3mf.Color()
    c.Red = r; c.Green = g; c.Blue = b; c.Alpha = a
    ci = cg.AddColor(c); rid = cg.GetResourceID()
    for i in range(mo.GetTriangleCount()):
        tp = lib3mf.TriangleProperties()
        tp.ResourceID = rid; tp.PropertyIDs[0] = ci; tp.PropertyIDs[1] = ci; tp.PropertyIDs[2] = ci
        mo.SetTriangleProperties(i, tp)
    mo.SetObjectLevelProperty(rid, ci)
    model.AddBuildItem(mo, wrapper.GetIdentityTransform())
    writer = model.QueryWriter("3mf"); writer.WriteToFile(path)

def mirror_mesh(mesh):
    v = mesh.vertices.copy(); v[:, 1] *= -1
    return trimesh.Trimesh(vertices=v, faces=mesh.faces[:, ::-1])

# ============================================================
print("=" * 60)
print("REGENERATING ALL H-STAB PRINT MESHES")
print("=" * 60)

all_meshes = []
stab_ys = [3.5, 10, 20, 35, 50, 65, 80, 95, 110, 125, 140, 155, 170, 189, 195, 200]
elev_ys = [4, 15, 30, 50, 75, 100, 125, 150, 175, 195, 200]

# 1. HStab (tessellate from STEP — includes bores+saddle from v7)
print("\n1. HStab...")
hl_step = import_step("cad/components/empennage/HStab/HStab.step")
export_stl(hl_step, "cad/components/empennage/HStab/HStab_shell.stl", tolerance=0.001, angular_tolerance=0.05)
hl_shell = trimesh.load("cad/components/empennage/HStab/HStab_shell.stl")
hl_ribs = make_ribs(stab_ys, le_x, X_HINGE)
hl = trimesh.util.concatenate([hl_shell, hl_ribs]) if hl_ribs else hl_shell
hl.export("cad/components/empennage/HStab/HStab_print.stl")
make_3mf(hl, "cad/components/empennage/HStab/HStab.3mf", "HStab", 180, 60, 200)
all_meshes.append(hl)
print(f"   {len(hl.faces)} tris, {os.path.getsize('cad/components/empennage/HStab/HStab.3mf')//1024}KB")

# 2. HStab mirrored (generated at assembly time, no separate folder)
print("2. HStab (mirrored)...")
hr = mirror_mesh(hl)
all_meshes.append(hr)
print(f"   {len(hr.faces)} tris (mirror)")

# 3. Elevator
print("3. Elevator...")
el_part = import_step("cad/components/empennage/Elevator/Elevator.step")
export_stl(el_part, "D:/Repos/aeroforge/exports/el_shell.stl", tolerance=0.005, angular_tolerance=0.1)
el_shell = trimesh.load("D:/Repos/aeroforge/exports/el_shell.stl")
el_ribs = make_ribs(elev_ys, lambda y: X_HINGE + 2, 110)
el = trimesh.util.concatenate([el_shell, el_ribs]) if el_ribs else el_shell
el.export("cad/components/empennage/Elevator/Elevator_print.stl")
make_3mf(el, "cad/components/empennage/Elevator/Elevator.3mf", "Elevator", 255, 100, 180)
all_meshes.append(el)
print(f"   {len(el.faces)} tris")

# 4. Elevator mirrored (generated at assembly time, no separate folder)
print("4. Elevator (mirrored)...")
er = mirror_mesh(el)
all_meshes.append(er)
print(f"   {len(er.faces)} tris (mirror)")

# 5. Tip caps
print("5. Tip caps...")
tip = trimesh.load("cad/components/empennage/HStab_Tip_Cap/HStab_Tip_Cap.stl")
make_3mf(tip, "cad/components/empennage/HStab_Tip_Cap/HStab_Tip_Cap.3mf", "Tip_L", 200, 80, 220)
tip_r = mirror_mesh(tip)
all_meshes.extend([tip, tip_r])
print(f"   {len(tip.faces)} tris each")

# 6. Spar
print("6. Spar...")
spar_p = import_step("cad/components/empennage/HStab_Main_Spar/HStab_Main_Spar.step")
export_stl(spar_p, "D:/Repos/aeroforge/exports/spar.stl", tolerance=0.05)
spar_mesh = trimesh.load("D:/Repos/aeroforge/exports/spar.stl")
all_meshes.append(spar_mesh)

# 7. Wire
print("7. Wire...")
wire_p = import_step("cad/components/empennage/Hinge_Wire/Hinge_Wire.step")
export_stl(wire_p, "D:/Repos/aeroforge/exports/wire.stl", tolerance=0.05)
wire_mesh = trimesh.load("D:/Repos/aeroforge/exports/wire.stl")
all_meshes.append(wire_mesh)

# ============================================================
# FULL ASSEMBLY 3MF
# ============================================================
print("\nBuilding assembly...")
assembly = trimesh.util.concatenate(all_meshes)
print(f"Assembly: {len(assembly.vertices)} verts, {len(assembly.faces)} tris")

asm_path = "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly.3mf"
make_3mf(assembly, asm_path, "HStab_Assembly", 180, 60, 200, 140)
print(f"Assembly 3MF: {os.path.getsize(asm_path) // 1024}KB")

dt = time.time() - t0
print(f"\nAll meshes in {dt:.1f}s")

# ============================================================
# SHOW + SCREENSHOT
# ============================================================
print("\nDisplaying...")
hl_brep = import_step("cad/components/empennage/HStab/HStab.step")
hr_brep = hl_brep.mirror(Plane.XZ)
el_brep = import_step("cad/components/empennage/Elevator/Elevator.step")
er_brep = el_brep.mirror(Plane.XZ)
tip_brep = import_step("cad/components/empennage/HStab_Tip_Cap/HStab_Tip_Cap.step")
tip_r_brep = tip_brep.mirror(Plane.XZ)

show(hl_brep, hr_brep, el_brep, er_brep, tip_brep, tip_r_brep, spar_p, wire_p,
     names=["Stab_L", "Stab_R", "Elev_L", "Elev_R", "Tip_L", "Tip_R", "Spar", "Wire"],
     colors=["mediumorchid", "mediumorchid", "hotpink", "hotpink",
             "plum", "plum", "dimgray", "silver"],
     alphas=[0.4, 0.4, 0.4, 0.4, 0.6, 0.6, 1.0, 1.0])
time.sleep(2)
save_screenshot("exports/validation/hstab_full_assembly_final.png")
print("Assembly screenshot saved")
print("\nDONE")
