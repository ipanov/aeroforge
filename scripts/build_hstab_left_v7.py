"""
HStab 3D Model — v7 (Build123d)
======================================
FULL PRECISION: Spline curves (not Polyline), full airfoil loft, boolean cut.
- HT-13 (root) → HT-12 (tip) blended via arc-length resampling
- Full airfoil lofted first, then cut at hinge plane X=60
- Spar bore: 3.1mm diameter along main spar line
- Hinge groove: concave saddle channel on hinge face
- Bezier tip cap from assembly planform

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_hstab_left_v7.py
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from build123d import *
from src.cad.airfoils import blend_airfoils, scale_airfoil

# === PARAMETERS (from design consensus v6) ===
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
N_EXP = 2.3
REF_FRAC = 0.45
REF_X = ROOT_CHORD * REF_FRAC

X_MAIN_SPAR = 34.5
X_HINGE = 60.0
SPAR_BORE = 3.1      # 3mm CF tube + 0.1mm clearance
HINGE_BORE = 0.6     # 0.5mm piano wire + 0.1mm clearance
Y_MAIN_END = 189.0
Y_HINGE_END = 212.0
FIN_HALF = 3.5
WALL = 0.45
Y_CAP_START = 210.0
Y_CAP_END = 214.0

# Airfoil precision: points per surface (upper or lower)
# 60 cosine-spaced points per surface = smooth BSpline with minimal patch edges
# The BSpline interpolation gives sub-micron accuracy at this density
N_PTS = 60  # 121 total points per airfoil


def _se(y):
    """Superellipse chord distribution."""
    if abs(y) >= HALF_SPAN or y < 0:
        return 0.0
    return ROOT_CHORD * (1.0 - (y / HALF_SPAN) ** N_EXP) ** (1.0 / N_EXP)


# Tip cap cubic polynomial (C1 continuous at Y_CAP_START)
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


def get_full_airfoil_section(y_sta):
    """Get FULL airfoil (LE to TE) as 2D points at span station y.

    Uses properly resampled HT-13/HT-12 blend.
    Returns list of (x_abs, z) tuples in absolute X coordinates.
    """
    c = chord_at(abs(y_sta))
    if c < 3.0:
        return None
    lx = le_x(abs(y_sta))
    blend = min(abs(y_sta) / HALF_SPAN, 1.0)

    # Blend and resample to common parameterization
    af = blend_airfoils("ht13", "ht12", blend, N_PTS)
    sc = scale_airfoil(af, c)

    # Convert to absolute X coordinates
    pts = [(lx + float(p[0]), float(p[1])) for p in sc]

    # Ensure closed
    if math.dist(pts[0], pts[-1]) > 0.001:
        pts.append(pts[0])

    return pts


def main():
    print("=" * 60)
    print("HStab v7 — Build123d FULL PRECISION")
    print("  Spline curves, full airfoil loft, boolean cut")
    print("=" * 60)

    # === STEP 1: Build full airfoil sections ===
    # Dense stations from root to tip
    # NO TIP — stop at Y_CAP_START (y=210). Tip is separate replaceable component.
    ys = sorted(set([
        FIN_HALF, 15, 40, 75, 110, 150, 180,
        Y_MAIN_END, 200, Y_CAP_START,
    ]))

    sections = []
    for y in ys:
        pts = get_full_airfoil_section(y)
        if pts is None:
            continue
        sections.append((y, pts))
        c = chord_at(y)
        print(f"  y={y:6.1f}: chord={c:5.1f}  pts={len(pts)}")

    print(f"\n  {len(sections)} sections, {len(sections[0][1])} pts each (Spline)")

    # === STEP 2: Loft full airfoil using Spline curves ===
    print("\nLofting full airfoil (Spline sections)...")
    with BuildPart() as bp:
        for y, pts in sections:
            plane = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
            with BuildSketch(plane) as sk:
                with BuildLine():
                    Spline(*[(p[0], p[1]) for p in pts])
                make_face()
        loft()

    full_airfoil = bp.part
    print(f"  Full airfoil: {full_airfoil.volume:.0f} mm3")

    # === STEP 3: Cut at hinge plane X=60 ===
    print(f"\nCutting at hinge plane X={X_HINGE}...")
    # Create a large box on the elevator side (X > X_HINGE) and subtract
    cut_box = Box(200, 250, 30, align=(Align.MIN, Align.CENTER, Align.CENTER))
    cut_box = Pos(X_HINGE, (FIN_HALF + 213) / 2, 0) * cut_box
    stab = full_airfoil - cut_box
    print(f"  Stab (cut): {stab.volume:.0f} mm3")

    # === STEP 4: Spar bore ===
    print(f"\nSpar bore d={SPAR_BORE}mm (y={FIN_HALF} to {Y_MAIN_END})...")
    spar_len = Y_MAIN_END - FIN_HALF + 4
    spar_cy = (FIN_HALF + Y_MAIN_END) / 2
    spar_cyl = Location((X_MAIN_SPAR, spar_cy, 0), (90, 0, 0)) * Cylinder(
        SPAR_BORE / 2, spar_len
    )
    stab = stab - spar_cyl
    print(f"  After spar bore: {stab.volume:.0f} mm3")

    # === STEP 5: Hinge wire bore ===
    print(f"\nHinge wire bore d={HINGE_BORE}mm (y={FIN_HALF} to {Y_HINGE_END})...")
    hinge_len = Y_HINGE_END - FIN_HALF + 4
    hinge_cy = (FIN_HALF + Y_HINGE_END) / 2
    hinge_cyl = Location((X_HINGE, hinge_cy, 0), (90, 0, 0)) * Cylinder(
        HINGE_BORE / 2, hinge_len
    )
    stab = stab - hinge_cyl
    print(f"  After hinge bore: {stab.volume:.0f} mm3")

    # === STEP 5b: Hinge saddle groove ===
    # Concave semi-elliptical channel on hinge face (X=60)
    # The elevator bull-nose nests into this groove
    # Tapers from root (deeper) to tip (shallower)
    SADDLE_DEPTH_ROOT = 2.5   # mm into stab body at root
    SADDLE_DEPTH_TIP = 0.05   # mm at y=206 — effectively zero (was 0.8, caused visible indentation)
    SADDLE_WIDTH_ROOT = 3.0   # mm in Z direction at root
    SADDLE_WIDTH_TIP = 0.1    # mm at tip — effectively zero (spline needs non-degenerate shape)
    Y_SADDLE_END = 206.0      # saddle stops before airfoil gets too thin

    print(f"\nHinge saddle groove (concave, tapered to zero at tip)...")
    saddle_sections = []
    saddle_ys = [FIN_HALF, 50, 100, 150, Y_MAIN_END, 200, Y_SADDLE_END]
    for y_s in saddle_ys:
        t = (y_s - FIN_HALF) / (Y_SADDLE_END - FIN_HALF)
        depth = SADDLE_DEPTH_ROOT + t * (SADDLE_DEPTH_TIP - SADDLE_DEPTH_ROOT)
        width = SADDLE_WIDTH_ROOT + t * (SADDLE_WIDTH_TIP - SADDLE_WIDTH_ROOT)
        hw = width / 2
        # Semi-ellipse opening toward -X (into stab body)
        pts = []
        n_arc = 20
        for i in range(n_arc + 1):
            theta = math.pi * i / n_arc
            z = hw * math.cos(theta)
            x = X_HINGE - depth * math.sin(theta)
            pts.append((x, z))
        # Close with straight line across opening
        pts.append(pts[0])
        saddle_sections.append((y_s, pts))

    # Loft the saddle groove shape
    with BuildPart() as saddle_bp:
        for y_s, pts in saddle_sections:
            plane = Plane(origin=(0, y_s, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
            with BuildSketch(plane) as sk:
                with BuildLine():
                    Spline(*[(p[0], p[1]) for p in pts])
                make_face()
        loft()
    saddle_solid = saddle_bp.part
    stab = stab - saddle_solid
    print(f"  After saddle groove: {stab.volume:.0f} mm3")
    print(f"  Saddle: depth {SADDLE_DEPTH_ROOT}->{SADDLE_DEPTH_TIP}mm, width {SADDLE_WIDTH_ROOT}->{SADDLE_WIDTH_TIP}mm")

    # === STEP 6: Export ===
    d = "cad/components/empennage/HStab"
    os.makedirs(d, exist_ok=True)

    step_path = f"{d}/HStab.step"
    stl_path = f"{d}/HStab.stl"
    print(f"\nExporting STEP: {step_path}")
    export_step(stab, step_path)
    print(f"Exporting STL: {stl_path}")
    export_stl(stab, stl_path)

    bb = stab.bounding_box()
    fv = stab.volume
    print(f"\n{'=' * 60}")
    print(f"HStab v7 FINAL")
    print(f"  Volume: {fv:.0f} mm3 ({fv / 1000:.2f} cm3)")
    print(f"  Mass (LW-PLA 0.75): {fv * 0.75 / 1000:.2f}g")
    print(f"  Mass (LW-PLA 0.50 foamed): {fv * 0.50 / 1000:.2f}g")
    print(f"  Spar bore: {SPAR_BORE}mm at X={X_MAIN_SPAR}")
    print(f"  Hinge bore: {HINGE_BORE}mm at X={X_HINGE}")
    print(f"  BBox: X=[{bb.min.X:.1f}, {bb.max.X:.1f}]"
          f"  Y=[{bb.min.Y:.1f}, {bb.max.Y:.1f}]"
          f"  Z=[{bb.min.Z:.1f}, {bb.max.Z:.1f}]")
    print(f"{'=' * 60}")

    try:
        from ocp_vscode import show
        show(stab)
        print("Displayed in OCP Viewer")
    except Exception:
        pass


if __name__ == "__main__":
    main()
