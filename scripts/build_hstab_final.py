"""
HStab_Left — FINAL Print-Ready Model
=====================================
Perfect NURBS outer surface from Build123d + internal geodesic ribs.
Outer skin is smooth, uninterrupted airfoil. Ribs are INSIDE only.

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_hstab_final.py
"""
import sys, os, math, time, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from build123d import *
from src.cad.airfoils import blend_airfoils, scale_airfoil

# Parameters
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
N_EXP = 2.3
REF_FRAC = 0.45
REF_X = ROOT_CHORD * REF_FRAC
X_MAIN_SPAR = 34.5
X_HINGE = 60.0
SPAR_BORE = 3.1
SPAR_BOSS_OD = 4.3
HINGE_BORE = 0.6
Y_MAIN_END = 189.0
Y_HINGE_END = 212.0
FIN_HALF = 3.5
WALL = 0.45
Y_CAP_START = 210.0
Y_CAP_END = 214.0
Y_SADDLE_END = 206.0
N_AIRFOIL = 80
RIB_SPACING = 12.0
RIB_ANGLE = 45.0


def _se(y):
    if abs(y) >= HALF_SPAN or y < 0:
        return 0.0
    return ROOT_CHORD * (1.0 - (y / HALF_SPAN) ** N_EXP) ** (1.0 / N_EXP)

_c0 = _se(Y_CAP_START)
_sl = (_se(Y_CAP_START) - _se(Y_CAP_START - 0.001)) / 0.001
_ca, _cb = _c0, _sl
_cd = (_ca + 2 * _cb) / 32
_cc = (-_cb - 48 * _cd) / 8

def chord_at(y):
    y = abs(y)
    if y <= Y_CAP_START:
        return _se(y)
    if y >= Y_CAP_END:
        return 0.0
    t = y - Y_CAP_START
    return max(0.0, _ca + _cb * t + _cc * t ** 2 + _cd * t ** 3)

def le_x(y):
    return REF_X - REF_FRAC * chord_at(abs(y))


def get_z_bounds(y_sta, x_pos):
    """Get airfoil Z bounds at given X for rib placement."""
    c = chord_at(abs(y_sta))
    if c < 2:
        return None
    lx = le_x(abs(y_sta))
    x_local = x_pos - lx
    if x_local < 0.5 or x_local > c - 0.5:
        return None
    blend = min(abs(y_sta) / HALF_SPAN, 1.0)
    af = blend_airfoils("ht13", "ht12", blend, N_AIRFOIL)
    sc = scale_airfoil(af, c)
    le_idx = np.argmin(sc[:, 0])
    upper = sc[:le_idx + 1][::-1]
    lower = sc[le_idx:]
    u_sorted = upper[np.argsort(upper[:, 0])]
    l_sorted = lower[np.argsort(lower[:, 0])]
    zu = float(np.interp(x_local, u_sorted[:, 0], u_sorted[:, 1]))
    zl = float(np.interp(x_local, l_sorted[:, 0], l_sorted[:, 1]))
    # Inner bounds (offset by wall thickness)
    return zu - WALL, zl + WALL


def main():
    t0 = time.time()
    print("=" * 60)
    print("HStab_Left FINAL — NURBS shell + internal geodesic ribs")
    print("=" * 60)

    # ============================================================
    # STEP 1: Build123d NURBS shell (perfect smooth surface)
    # ============================================================
    print("\n--- Step 1: Build123d NURBS shell ---")
    print("Loading MainBody STEP...")
    solid = import_step("cad/components/empennage/HStab_Left/HStab_Left_MainBody.step")
    print(f"  Solid: {solid.volume:.0f} mm3")

    root_face = min(solid.faces(), key=lambda f: f.center().Y)
    print("Shelling (0.45mm wall, root open)...")
    shell = solid.offset_3d(openings=[root_face], thickness=-WALL)
    print(f"  Shell: {shell.volume:.0f} mm3 ({shell.volume * 0.75 / 1000:.2f}g)")

    # Spar boss — root zone
    print("Spar boss root (3.5-30mm, OD=4.3mm)...")
    bl_root = 30.0 - FIN_HALF + 2
    cy_root = (FIN_HALF + 30.0) / 2
    bo_r = Location((X_MAIN_SPAR, cy_root, 0), (90, 0, 0)) * Cylinder(SPAR_BOSS_OD / 2, bl_root)
    bi_r = Location((X_MAIN_SPAR, cy_root, 0), (90, 0, 0)) * Cylinder(SPAR_BORE / 2, bl_root)
    shell = shell + ((bo_r - bi_r) & solid)

    # Spar boss — tip zone
    print("Spar boss tip (170-189mm)...")
    bl_tip = Y_MAIN_END - 170.0 + 2
    cy_tip = (170.0 + Y_MAIN_END) / 2
    bo_t = Location((X_MAIN_SPAR, cy_tip, 0), (90, 0, 0)) * Cylinder(SPAR_BOSS_OD / 2, bl_tip)
    bi_t = Location((X_MAIN_SPAR, cy_tip, 0), (90, 0, 0)) * Cylinder(SPAR_BORE / 2, bl_tip)
    shell = shell + ((bo_t - bi_t) & solid)

    # Spar bore
    print("Spar bore d=3.1mm...")
    slen = Y_MAIN_END - FIN_HALF + 4
    scy = (FIN_HALF + Y_MAIN_END) / 2
    shell = shell - Location((X_MAIN_SPAR, scy, 0), (90, 0, 0)) * Cylinder(SPAR_BORE / 2, slen)

    # Hinge bore
    print("Hinge bore d=0.6mm...")
    hlen = Y_HINGE_END - FIN_HALF + 4
    hcy = (FIN_HALF + Y_HINGE_END) / 2
    shell = shell - Location((X_HINGE, hcy, 0), (90, 0, 0)) * Cylinder(HINGE_BORE / 2, hlen)

    # Saddle groove
    print("Saddle groove...")
    ss = []
    for y_s in [FIN_HALF, 30, 60, 100, 140, 189, Y_SADDLE_END]:
        t = (y_s - FIN_HALF) / (Y_SADDLE_END - FIN_HALF)
        depth = 2.5 + t * (0.8 - 2.5)
        width = 3.0 + t * (1.2 - 3.0)
        hw = width / 2
        pts = []
        for j in range(25):
            theta = math.pi * j / 24
            pts.append((X_HINGE - depth * math.sin(theta), hw * math.cos(theta)))
        pts.append(pts[0])
        ss.append((y_s, pts))
    with BuildPart() as sbp:
        for y_s, pts in ss:
            plane = Plane(origin=(0, y_s, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
            with BuildSketch(plane) as sk:
                with BuildLine():
                    Spline(*[(p[0], p[1]) for p in pts])
                make_face()
        loft()
    shell = shell - sbp.part

    vol = shell.volume
    bb = shell.bounding_box()
    print(f"\nShell FINAL: {vol:.0f} mm3 ({vol * 0.75 / 1000:.2f}g)")

    # Export shell STL at maximum precision (1 micron)
    out = "cad/components/empennage/HStab_Left"
    shell_stl = os.path.join(out, "HStab_Left_shell.stl")
    print(f"Exporting shell STL (1 micron tolerance)...")
    export_stl(shell, shell_stl, tolerance=0.001, angular_tolerance=0.05)
    export_step(shell, os.path.join(out, "HStab_Left.step"))
    print(f"  Shell STL: {os.path.getsize(shell_stl) / 1024:.0f} KB")

    dt1 = time.time() - t0
    print(f"  Build123d time: {dt1:.1f}s")

    # Show in OCP Viewer immediately
    try:
        from ocp_vscode import show
        show(shell)
        print("  Shell displayed in OCP Viewer")
    except Exception as e:
        print(f"  OCP: {e}")

    # ============================================================
    # STEP 2: Internal geodesic ribs (mesh, inside only)
    # ============================================================
    print(f"\n--- Step 2: Internal geodesic ribs ---")

    span_ys = sorted(set([
        FIN_HALF, 10, 20, 35, 50, 65, 80, 95, 110, 125,
        140, 155, 170, 189, 195, 200
    ]))

    rib_verts = []
    rib_faces = []
    rib_count = 0

    for i in range(len(span_ys) - 1):
        y_a, y_b = span_ys[i], span_ys[i + 1]
        dy = y_b - y_a
        x_shift = dy * math.tan(math.radians(RIB_ANGLE))
        x_min = max(le_x(y_a), le_x(y_b)) + 4
        x_max = X_HINGE - 2

        if x_max <= x_min:
            continue

        for sign in [+1, -1]:
            x = x_min
            while x < x_max:
                x_a, x_b = x, x + sign * x_shift
                if x_min <= x_a <= x_max and x_min <= x_b <= x_max:
                    ba = get_z_bounds(y_a, x_a)
                    bb_z = get_z_bounds(y_b, x_b)
                    if ba is not None and bb_z is not None:
                        ziu_a, zil_a = ba
                        ziu_b, zil_b = bb_z
                        if ziu_a > zil_a + 0.3 and ziu_b > zil_b + 0.3:
                            base = len(rib_verts)
                            rib_verts.extend([
                                [x_a, y_a, ziu_a],
                                [x_a, y_a, zil_a],
                                [x_b, y_b, ziu_b],
                                [x_b, y_b, zil_b],
                            ])
                            rib_faces.extend([
                                [base, base + 2, base + 3],
                                [base, base + 3, base + 1],
                            ])
                            rib_count += 1
                x += RIB_SPACING

    print(f"  {rib_count} ribs, {len(rib_verts)} verts, {len(rib_faces)} tris")

    # ============================================================
    # STEP 3: Merge and export 3MF
    # ============================================================
    print(f"\n--- Step 3: Merge into 3MF ---")

    import trimesh

    shell_mesh = trimesh.load(shell_stl)
    rib_mesh = trimesh.Trimesh(
        vertices=np.array(rib_verts, dtype=np.float32),
        faces=np.array(rib_faces, dtype=np.int32)
    )
    combined = trimesh.util.concatenate([shell_mesh, rib_mesh])
    print(f"  Combined: {len(combined.vertices)} verts, {len(combined.faces)} tris")

    # Save combined STL
    combined_stl = os.path.join(out, "HStab_Left.stl")
    combined.export(combined_stl)
    print(f"  STL: {os.path.getsize(combined_stl) / 1024:.0f} KB")

    # Build 3MF with transparent violet
    import lib3mf
    wrapper = lib3mf.get_wrapper()
    model = wrapper.CreateModel()
    model.SetUnit(lib3mf.ModelUnit.MilliMeter)
    m3 = model.AddMeshObject()
    m3.SetName("HStab_Left_Geodesic")

    for v in combined.vertices:
        p = lib3mf.Position()
        p.Coordinates[0] = float(v[0])
        p.Coordinates[1] = float(v[1])
        p.Coordinates[2] = float(v[2])
        m3.AddVertex(p)

    skipped = 0
    for f in combined.faces:
        if f[0] == f[1] or f[1] == f[2] or f[0] == f[2]:
            skipped += 1
            continue
        t = lib3mf.Triangle()
        t.Indices[0] = int(f[0])
        t.Indices[1] = int(f[1])
        t.Indices[2] = int(f[2])
        m3.AddTriangle(t)

    # Transparent violet
    cg = model.AddColorGroup()
    c = lib3mf.Color()
    c.Red = 180
    c.Green = 60
    c.Blue = 200
    c.Alpha = 128
    ci = cg.AddColor(c)
    rid = cg.GetResourceID()
    for i in range(m3.GetTriangleCount()):
        tp = lib3mf.TriangleProperties()
        tp.ResourceID = rid
        tp.PropertyIDs[0] = ci
        tp.PropertyIDs[1] = ci
        tp.PropertyIDs[2] = ci
        m3.SetTriangleProperties(i, tp)
    m3.SetObjectLevelProperty(rid, ci)

    model.AddBuildItem(m3, wrapper.GetIdentityTransform())
    threemf_path = os.path.join(out, "HStab_Left.3mf")
    writer = model.QueryWriter("3mf")
    writer.WriteToFile(threemf_path)
    print(f"  3MF: {os.path.getsize(threemf_path) / 1024:.0f} KB (skipped {skipped} degenerate)")

    # ============================================================
    # DONE
    # ============================================================
    dt = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"HStab_Left FINAL")
    print(f"  Shell: {vol:.0f} mm3, {vol * 0.75 / 1000:.2f}g LW-PLA")
    print(f"  Surface: Build123d NURBS (1 micron STL)")
    print(f"  Ribs: {rib_count} geodesic internal (do not touch outer surface)")
    print(f"  Total time: {dt:.1f}s")
    print(f"{'=' * 60}")

    # Open OrcaSlicer
    print("\nOpening OrcaSlicer...")
    os.startfile(os.path.abspath(threemf_path))


if __name__ == "__main__":
    main()
