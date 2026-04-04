"""
HStab_Left — Print-Ready Thin-Wall Shell (Build123d)
=====================================================
Full precision: 80-point spline airfoils, HT-13/HT-12 blend, 0.45mm wall.
Outer-inner loft subtraction (reliable shell method).

Features:
- Real HT-13 (root) → HT-12 (tip) blended airfoils, 80 pts per surface
- 0.45mm thin wall via outer-inner loft subtraction
- Spar bore: 3.1mm with reinforced boss (1.2mm wall ring)
- Hinge wire bore: 0.6mm
- Saddle groove: concave tapered channel on hinge face
- Root open (for spar insertion), tip closed
- High-res STL export (0.005mm tolerance)

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_hstab_left_print.py
"""
import sys
import os
import math
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from build123d import *
from src.cad.airfoils import blend_airfoils, scale_airfoil

# === DESIGN CONSENSUS v6 PARAMETERS ===
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
N_EXP = 2.3
REF_FRAC = 0.45
REF_X = ROOT_CHORD * REF_FRAC  # 51.75mm

X_MAIN_SPAR = 34.5    # 30% root chord
X_HINGE = 60.0         # 52.2% root chord
SPAR_BORE = 3.1        # 3mm CF tube + 0.1mm clearance
HINGE_BORE = 0.6       # 0.5mm wire + 0.1mm
Y_MAIN_END = 189.0     # spar terminates
Y_HINGE_END = 212.0    # hinge wire terminates
FIN_HALF = 3.5         # root start (VStab half-width)
WALL = 0.45            # shell wall thickness
Y_CAP_START = 210.0
Y_CAP_END = 214.0

# Spar boss reinforcement
SPAR_BOSS_OD = SPAR_BORE + 2 * 1.2  # 5.5mm OD ring around spar bore

# Saddle groove
SADDLE_DEPTH_ROOT = 2.5
SADDLE_DEPTH_TIP = 0.8
SADDLE_WIDTH_ROOT = 3.0
SADDLE_WIDTH_TIP = 1.2
Y_SADDLE_END = 206.0

# Airfoil precision
N_PTS = 80  # points per surface (upper or lower) — 161 total per section


def _se(y):
    """Superellipse chord."""
    if abs(y) >= HALF_SPAN or y < 0:
        return 0.0
    return ROOT_CHORD * (1.0 - (y / HALF_SPAN) ** N_EXP) ** (1.0 / N_EXP)


# Tip cap cubic (C1 continuous)
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


def get_airfoil_section(y_sta, offset=0.0):
    """Full airfoil section at span station y.

    offset > 0: inward offset for inner shell surface.
    Returns list of (x_abs, z) tuples, or None if too small.
    """
    c = chord_at(abs(y_sta))
    if c < 2.0:
        return None
    lx = le_x(abs(y_sta))
    blend = min(abs(y_sta) / HALF_SPAN, 1.0)

    af = blend_airfoils("ht13", "ht12", blend, N_PTS)
    sc = scale_airfoil(af, c)

    if offset > 0:
        # Normal-direction offset: compute tangent at each point,
        # offset perpendicular (inward)
        pts = np.array(sc, dtype=np.float64)
        n = len(pts)
        offset_pts = np.zeros_like(pts)
        for i in range(n):
            # Central differences for tangent
            p0 = pts[(i - 1) % n]
            p1 = pts[i]
            p2 = pts[(i + 1) % n]
            tx = p2[0] - p0[0]
            tz = p2[1] - p0[1]
            tlen = math.hypot(tx, tz)
            if tlen < 1e-12:
                offset_pts[i] = p1
                continue
            # Normal: rotate tangent 90° CCW (inward for CW-wound Selig airfoil)
            nx = -tz / tlen
            nz = tx / tlen
            offset_pts[i, 0] = p1[0] + nx * offset
            offset_pts[i, 1] = p1[1] + nz * offset

        # Convert to absolute X
        pts_out = [(lx + float(p[0]), float(p[1])) for p in offset_pts]
    else:
        pts_out = [(lx + float(p[0]), float(p[1])) for p in sc]

    # Ensure closed
    if math.dist(pts_out[0], pts_out[-1]) > 0.001:
        pts_out.append(pts_out[0])

    return pts_out


def clip_at_hinge(pts, x_hinge=X_HINGE):
    """Clip airfoil section at hinge plane X=x_hinge.
    Returns only the forward portion (stab body, X <= x_hinge).
    """
    clipped = []
    n = len(pts)
    for i in range(n):
        p = pts[i]
        if p[0] <= x_hinge:
            clipped.append(p)
        else:
            # Interpolate crossing point
            if i > 0 and pts[i-1][0] <= x_hinge:
                prev = pts[i-1]
                dx = p[0] - prev[0]
                if dx > 1e-9:
                    t = (x_hinge - prev[0]) / dx
                    z_cross = prev[1] + t * (p[1] - prev[1])
                    clipped.append((x_hinge, z_cross))
            # Find re-entry point
            for j in range(i+1, n):
                if pts[j][0] <= x_hinge:
                    prev = pts[j-1]
                    dx = pts[j][0] - prev[0]
                    if abs(dx) > 1e-9:
                        t = (x_hinge - prev[0]) / dx
                        z_cross = prev[1] + t * (pts[j][1] - prev[1])
                        clipped.append((x_hinge, z_cross))
                    break
            break

    # Add re-entry points and remaining
    re_entered = False
    for i in range(len(pts)):
        if re_entered:
            if pts[i][0] <= x_hinge:
                clipped.append(pts[i])
        elif pts[i][0] > x_hinge:
            re_entered = False
            # Find where it comes back
            pass

    # Simpler approach: just use all points <= hinge, with interpolated crossings
    return clipped


def loft_sections(sections, label):
    """Loft a set of (y, pts) sections using Spline curves."""
    t0 = time.time()
    with BuildPart() as bp:
        for y, pts in sections:
            plane = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
            with BuildSketch(plane) as sk:
                with BuildLine():
                    Spline(*[(p[0], p[1]) for p in pts])
                make_face()
        loft()
    vol = bp.part.volume
    dt = time.time() - t0
    print(f"  {label}: {vol:.0f} mm3 ({vol/1000:.2f} cm3) [{dt:.1f}s]")
    return bp.part


def main():
    t_start = time.time()
    print("=" * 60)
    print("HStab_Left — PRINT-READY Shell")
    print("  Real HT-13/HT-12 blended airfoils, 80 pts/surface")
    print("  0.45mm wall, spar boss, hinge bore, saddle groove")
    print("=" * 60)

    # Dense span stations for maximum print fidelity
    # Every ~10-15mm in main span, denser near tip
    ys = sorted(set([
        FIN_HALF,       # root
        10, 20, 35, 50, 65, 80, 95, 110, 125, 140, 155, 170,
        Y_MAIN_END,     # 189 - spar end
        195, 200, 205,
        Y_CAP_START,    # 210 - cap start
        212,            # near tip
    ]))

    print(f"\n--- Building {len(ys)} span stations ---")

    # Build outer sections (full airfoil, will cut at hinge)
    outer_sections = []
    for y in ys:
        pts = get_airfoil_section(y, offset=0.0)
        if pts is None:
            continue
        outer_sections.append((y, pts))
        c = chord_at(y)
        print(f"  y={y:6.1f}: chord={c:5.1f}mm  pts={len(pts)}")

    # Build inner sections (offset inward by WALL)
    # Stop before tip cap zone (inner closes earlier)
    inner_ys = [y for y in ys if y < Y_CAP_START - 2]
    inner_sections = []
    for y in inner_ys:
        pts = get_airfoil_section(y, offset=WALL)
        if pts is None:
            continue
        inner_sections.append((y, pts))

    print(f"\n  Outer: {len(outer_sections)} sections")
    print(f"  Inner: {len(inner_sections)} sections")

    # === LOFT FULL AIRFOIL (outer) ===
    print("\n--- Lofting outer airfoil ---")
    outer_solid = loft_sections(outer_sections, "Outer")

    # === CUT AT HINGE PLANE ===
    print(f"\n--- Cutting at hinge X={X_HINGE}mm ---")
    cut_box = Box(200, 260, 30, align=(Align.MIN, Align.CENTER, Align.CENTER))
    cut_box = Pos(X_HINGE, (FIN_HALF + 215) / 2, 0) * cut_box
    outer_cut = outer_solid - cut_box
    print(f"  Outer cut: {outer_cut.volume:.0f} mm3")

    # === LOFT INNER AIRFOIL ===
    print("\n--- Lofting inner airfoil ---")
    inner_solid = loft_sections(inner_sections, "Inner")
    inner_cut = inner_solid - cut_box
    print(f"  Inner cut: {inner_cut.volume:.0f} mm3")

    # === SHELL = OUTER - INNER ===
    print("\n--- Creating shell (outer - inner) ---")
    stab = outer_cut - inner_cut
    print(f"  Shell: {stab.volume:.0f} mm3 ({stab.volume/1000:.2f} cm3)")
    print(f"  Shell mass LW-PLA 0.75: {stab.volume * 0.75 / 1000:.2f}g")

    # === SPAR BORE ===
    print(f"\n--- Spar bore d={SPAR_BORE}mm ---")
    spar_len = Y_MAIN_END - FIN_HALF + 4
    spar_cy = (FIN_HALF + Y_MAIN_END) / 2
    spar_cyl = Location((X_MAIN_SPAR, spar_cy, 0), (90, 0, 0)) * Cylinder(
        SPAR_BORE / 2, spar_len
    )
    stab = stab - spar_cyl
    print(f"  After spar bore: {stab.volume:.0f} mm3")

    # === SPAR BOSS (reinforced tube around bore) ===
    print(f"\n--- Spar boss OD={SPAR_BOSS_OD}mm ---")
    boss_outer = Location((X_MAIN_SPAR, spar_cy, 0), (90, 0, 0)) * Cylinder(
        SPAR_BOSS_OD / 2, spar_len
    )
    boss_inner = Location((X_MAIN_SPAR, spar_cy, 0), (90, 0, 0)) * Cylinder(
        SPAR_BORE / 2, spar_len
    )
    boss_ring = boss_outer - boss_inner
    # Intersect boss with the outer_cut to keep only the part inside the airfoil
    boss_ring = boss_ring & outer_cut
    stab = stab + boss_ring
    print(f"  After spar boss: {stab.volume:.0f} mm3")

    # === HINGE WIRE BORE ===
    print(f"\n--- Hinge bore d={HINGE_BORE}mm ---")
    hinge_len = Y_HINGE_END - FIN_HALF + 4
    hinge_cy = (FIN_HALF + Y_HINGE_END) / 2
    hinge_cyl = Location((X_HINGE, hinge_cy, 0), (90, 0, 0)) * Cylinder(
        HINGE_BORE / 2, hinge_len
    )
    stab = stab - hinge_cyl
    print(f"  After hinge bore: {stab.volume:.0f} mm3")

    # === SADDLE GROOVE ===
    print(f"\n--- Saddle groove (concave, tapered) ---")
    saddle_ys = [FIN_HALF, 30, 60, 100, 140, Y_MAIN_END, Y_SADDLE_END]
    saddle_sections = []
    for y_s in saddle_ys:
        t = (y_s - FIN_HALF) / (Y_SADDLE_END - FIN_HALF)
        depth = SADDLE_DEPTH_ROOT + t * (SADDLE_DEPTH_TIP - SADDLE_DEPTH_ROOT)
        width = SADDLE_WIDTH_ROOT + t * (SADDLE_WIDTH_TIP - SADDLE_WIDTH_ROOT)
        hw = width / 2
        pts = []
        n_arc = 24
        for i in range(n_arc + 1):
            theta = math.pi * i / n_arc
            z = hw * math.cos(theta)
            x = X_HINGE - depth * math.sin(theta)
            pts.append((x, z))
        pts.append(pts[0])
        saddle_sections.append((y_s, pts))

    with BuildPart() as saddle_bp:
        for y_s, pts in saddle_sections:
            plane = Plane(origin=(0, y_s, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
            with BuildSketch(plane) as sk:
                with BuildLine():
                    Spline(*[(p[0], p[1]) for p in pts])
                make_face()
        loft()
    stab = stab - saddle_bp.part
    print(f"  After saddle: {stab.volume:.0f} mm3")

    # === FINAL STATS ===
    bb = stab.bounding_box()
    vol = stab.volume
    mass_lw = vol * 0.75 / 1000
    mass_foam = vol * 0.50 / 1000
    dt = time.time() - t_start

    print(f"\n{'=' * 60}")
    print(f"HStab_Left PRINT-READY")
    print(f"  Volume:  {vol:.0f} mm3 ({vol/1000:.2f} cm3)")
    print(f"  Mass LW-PLA solid 0.75: {mass_lw:.2f}g")
    print(f"  Mass LW-PLA foamed 0.50: {mass_foam:.2f}g")
    print(f"  Wall: {WALL}mm | Spar boss: {SPAR_BOSS_OD}mm OD")
    print(f"  BBox: X=[{bb.min.X:.1f}, {bb.max.X:.1f}]"
          f"  Y=[{bb.min.Y:.1f}, {bb.max.Y:.1f}]"
          f"  Z=[{bb.min.Z:.1f}, {bb.max.Z:.1f}]")
    print(f"  Build time: {dt:.1f}s")
    print(f"{'=' * 60}")

    # === EXPORT ===
    out_dir = "cad/components/empennage/HStab_Left"
    os.makedirs(out_dir, exist_ok=True)

    step_path = f"{out_dir}/HStab_Left.step"
    stl_path = f"{out_dir}/HStab_Left.stl"

    print(f"\nExporting STEP: {step_path}")
    export_step(stab, step_path)

    print(f"Exporting STL (high-res): {stl_path}")
    export_stl(stab, stl_path, tolerance=0.005, angular_tolerance=0.1)

    print(f"\nSTEP: {os.path.getsize(step_path)/1024:.0f} KB")
    print(f"STL:  {os.path.getsize(stl_path)/1024:.0f} KB")

    # Display in OCP Viewer
    try:
        from ocp_vscode import show, set_defaults
        set_defaults(transparent=True)
        show(stab, alphas=[0.5])
        print("\nDisplayed in OCP Viewer (transparent)")
    except Exception as e:
        print(f"\nOCP Viewer: {e}")


if __name__ == "__main__":
    main()
