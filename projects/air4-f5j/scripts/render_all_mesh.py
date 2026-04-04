"""
Render ALL H-Stab components + assembly from MESH (STL with geodesic ribs).
4 standard views: isometric, front, top, right.
Uses OCP Viewer Camera positions + save_screenshot.
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import trimesh
import numpy as np
from build123d import Compound, import_stl, import_step, Plane
from ocp_vscode import show, save_screenshot, Camera

# Map of view name -> Camera enum
VIEWS = {
    "isometric": Camera.ISO,
    "front": Camera.FRONT,
    "top": Camera.TOP,
    "right": Camera.RIGHT,
}

BASE = "D:/Repos/aeroforge"

def mirror_stl(src_path):
    """Mirror STL about Y=0 using trimesh (Build123d mirror doesn't work on STL).
    Returns path to temporary mirrored STL."""
    m = trimesh.load(src_path)
    m.vertices[:, 1] *= -1
    m.faces = m.faces[:, ::-1]  # flip normals
    dst = src_path.replace(".stl", "_mirrored.stl")
    m.export(dst)
    return dst

def render_mesh(objects, names, colors, alphas, render_dir, prefix="", delay=2.5):
    """Show objects in OCP and capture 4 views."""
    os.makedirs(render_dir, exist_ok=True)
    for vname, cam in VIEWS.items():
        show(*objects,
             names=names, colors=colors, alphas=alphas,
             reset_camera=cam)
        time.sleep(delay)
        fname = f"{prefix}{vname}.png" if prefix else f"{vname}.png"
        path = os.path.join(render_dir, fname)
        save_screenshot(path)
        print(f"  Saved {path}")
        time.sleep(0.5)


# ============================================================
# Load all mesh components
# ============================================================
print("Loading mesh components...")

# HStab (mesh with bores + ribs) — single component, mirrored for assembly
hl_stl = os.path.join(BASE, "cad/components/empennage/HStab/HStab_print.stl")
hl = import_stl(hl_stl)
print(f"  HStab: {hl_stl}")

# HStab mirrored (trimesh mirror — Build123d mirror doesn't work on STL)
hr_stl = mirror_stl(hl_stl)
hr = import_stl(hr_stl)
print(f"  HStab (mirrored): Y=[{hr.bounding_box().min.Y:.1f}, {hr.bounding_box().max.Y:.1f}]")

# Elevator (mesh with ribs) — single component, mirrored for assembly
el_stl = os.path.join(BASE, "cad/components/empennage/Elevator/Elevator_print.stl")
el = import_stl(el_stl)
print(f"  Elevator: {el_stl}")

# Elevator mirrored
er_stl = mirror_stl(el_stl)
er = import_stl(er_stl)
print(f"  Elevator (mirrored): Y=[{er.bounding_box().min.Y:.1f}, {er.bounding_box().max.Y:.1f}]")

# Tip caps (from STL)
tip_stl = os.path.join(BASE, "cad/components/empennage/HStab_Tip_Cap/HStab_Tip_Cap.stl")
tip_l = import_stl(tip_stl)
tip_r_stl = mirror_stl(tip_stl)
tip_r = import_stl(tip_r_stl)
print(f"  Tip caps loaded")

# Spar (STEP - it's a simple cylinder, no mesh needed)
spar = import_step(os.path.join(BASE, "cad/components/empennage/HStab_Main_Spar/HStab_Main_Spar.step"))
print(f"  Spar loaded")

# Hinge wire (STEP - simple cylinder)
wire = import_step(os.path.join(BASE, "cad/components/empennage/Hinge_Wire/Hinge_Wire.step"))
print(f"  Wire loaded")

# ============================================================
# 1. Individual component renders (mesh versions)
# ============================================================
print("\n" + "=" * 60)
print("COMPONENT RENDERS (from mesh)")
print("=" * 60)

components = [
    ("HStab", [hl], ["HStab"], ["mediumorchid"], [0.5],
     "cad/components/empennage/HStab/renders"),
    ("Elevator", [el], ["Elevator"], ["hotpink"], [0.5],
     "cad/components/empennage/Elevator/renders"),
    ("HStab_Tip_Cap", [tip_l], ["HStab_Tip_Cap"], ["plum"], [0.7],
     "cad/components/empennage/HStab_Tip_Cap/renders"),
    ("HStab_Main_Spar", [spar], ["HStab_Main_Spar"], ["dimgray"], [1.0],
     "cad/components/empennage/HStab_Main_Spar/renders"),
    ("Hinge_Wire", [wire], ["Hinge_Wire"], ["silver"], [1.0],
     "cad/components/empennage/Hinge_Wire/renders"),
]

for name, objs, nms, cols, alps, rdir in components:
    print(f"\n--- {name} ---")
    render_mesh(objs, nms, cols, alps, rdir)

# ============================================================
# 2. Assembly renders (all components together, mesh)
# ============================================================
print("\n" + "=" * 60)
print("ASSEMBLY RENDERS")
print("=" * 60)

asm_objects = [hl, hr, el, er, tip_l, tip_r, spar, wire]
asm_names = ["Stab_L", "Stab_R", "Elev_L", "Elev_R", "Tip_L", "Tip_R", "Spar", "Wire"]
asm_colors = ["mediumorchid", "mediumorchid", "hotpink", "hotpink",
              "plum", "plum", "dimgray", "silver"]
asm_alphas = [0.4, 0.4, 0.4, 0.4, 0.6, 0.6, 1.0, 1.0]

asm_render_dir = "cad/assemblies/empennage/HStab_Assembly/renders"
render_mesh(asm_objects, asm_names, asm_colors, asm_alphas, asm_render_dir)

print("\n" + "=" * 60)
print("ALL RENDERS COMPLETE")
print("=" * 60)
