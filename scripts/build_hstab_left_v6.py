"""
HStab_Left 3D Model — v6 (Build123d)
======================================
Fixed stab shell: LE to hinge face (X=60.0mm).
Loft through HT-13->HT-12 blended sections.
Thin-wall via outer-inner loft subtraction.

Key: both outer and inner sections use IDENTICAL fixed point counts
via resampling to arc-length parameterization.

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_hstab_left_v6.py
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from build123d import *
from src.cad.airfoils import blend_airfoils, scale_airfoil

# v6 parameters
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
N_EXP = 2.3
REF_FRAC = 0.45
REF_X = ROOT_CHORD * REF_FRAC

X_MAIN_SPAR = 34.5
X_HINGE = 60.0
SPAR_BORE = 3.1
HINGE_BORE = 0.6
Y_MAIN_END = 189.0
Y_HINGE_END = 212.0
FIN_HALF = 3.5
WALL = 0.45
Y_CAP_START = 210.0
Y_CAP_END = 214.0

# Fixed point counts per segment
N_UPPER = 30   # upper surface LE->hinge
N_HINGE = 2    # hinge face points (excluding endpoints)
N_LOWER = 30   # lower surface hinge->LE


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


def resample_curve(pts, n_out):
    """Resample a polyline to exactly n_out+1 points using arc-length."""
    pts = np.array(pts, dtype=np.float64)
    diffs = np.diff(pts, axis=0)
    segs = np.sqrt(diffs[:, 0] ** 2 + diffs[:, 1] ** 2)
    cum = np.concatenate([[0], np.cumsum(segs)])
    total = cum[-1]
    if total < 1e-12:
        return [tuple(pts[0])] * (n_out + 1)
    targets = np.linspace(0, total, n_out + 1)
    x_out = np.interp(targets, cum, pts[:, 0])
    z_out = np.interp(targets, cum, pts[:, 1])
    return [(float(x_out[i]), float(z_out[i])) for i in range(n_out + 1)]


def get_section(y_sta, wall_offset=0.0, n_raw=120):
    """Get stab cross-section clipped at hinge, optionally offset inward.

    Returns exactly (N_UPPER+1 + N_HINGE + N_LOWER+1) points forming
    a closed loop, or None if section is too small.
    """
    c = chord_at(abs(y_sta))
    if c < 2:
        return None
    lx = le_x(abs(y_sta))
    hloc = X_HINGE - lx
    if hloc < 1:
        return None

    blend = min(abs(y_sta) / HALF_SPAN, 1.0)
    af = blend_airfoils("ht13", "ht12", blend, n_raw)
    sc = scale_airfoil(af, c)

    li = int(np.argmin(sc[:, 0]))
    upper = sc[:li + 1][::-1]  # LE->TE
    lower = sc[li:]             # LE->TE

    def clip(pts, xmax):
        out = []
        for p in pts:
            if p[0] <= xmax + 0.001:
                out.append([float(p[0]), float(p[1])])
            else:
                if out:
                    pr = out[-1]
                    dx = float(p[0]) - pr[0]
                    if dx > 1e-9:
                        t = (xmax - pr[0]) / dx
                        out.append([xmax, pr[1] + t * (float(p[1]) - pr[1])])
                break
        return out

    uc = clip(upper, hloc)
    lc = clip(lower, hloc)
    if len(uc) < 3 or len(lc) < 3:
        return None

    if wall_offset > 0:
        def offset_curve(pts, d, sign):
            """Offset curve inward by d.
            sign=+1: push toward negative z (upper surface inward)
            sign=-1: push toward positive z (lower surface inward)
            """
            n = len(pts)
            result = []
            for i in range(n):
                p0 = pts[max(0, i - 1)]
                p1 = pts[i]
                p2 = pts[min(n - 1, i + 1)]
                dx = p2[0] - p0[0]
                dz = p2[1] - p0[1]
                ln = math.hypot(dx, dz)
                if ln < 1e-9:
                    result.append(list(p1))
                    continue
                # Right-hand normal of (dx, dz): (dz, -dx)
                # For upper surface LE->TE: tangent ~(1,0), right normal ~(0,-1) = downward = inward
                # For lower surface LE->TE: tangent ~(1,0), right normal ~(0,-1) = downward = outward
                # So sign=+1 uses right-hand normal (good for upper)
                # sign=-1 uses left-hand normal (good for lower)
                nx = sign * dz / ln
                nz = sign * (-dx) / ln
                result.append([p1[0] + nx * d, p1[1] + nz * d])
            return result

        uc = offset_curve(uc, wall_offset, +1)
        lc = offset_curve(lc, wall_offset, -1)

    # Resample to fixed point counts
    uc_r = resample_curve(uc, N_UPPER)    # N_UPPER+1 points
    lc_r = resample_curve(lc, N_LOWER)    # N_LOWER+1 points

    # Build closed loop in absolute coordinates
    pts = []

    # Upper: LE -> hinge (N_UPPER+1 points)
    for x, z in uc_r:
        pts.append((lx + x, z))

    # Hinge face: upper endpoint -> lower endpoint (N_HINGE interior points)
    hu_z = uc_r[-1][1]
    hl_z = lc_r[-1][1]
    hx_abs = lx + hloc if wall_offset == 0 else lx + float(uc_r[-1][0])
    for i in range(1, N_HINGE + 1):
        t = i / (N_HINGE + 1)
        pts.append((hx_abs, hu_z + t * (hl_z - hu_z)))

    # Lower: hinge -> LE (N_LOWER+1 points, reversed)
    for x, z in reversed(lc_r):
        pts.append((lx + x, z))

    # Close: last point = first point
    pts[-1] = pts[0]

    return pts


def do_loft(sections, label):
    """Loft through sections."""
    with BuildPart() as bp:
        for y, pts in sections:
            plane = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
            with BuildSketch(plane) as sk:
                with BuildLine():
                    Polyline(*[(p[0], p[1]) for p in pts])
                make_face()
        loft()
    vol = bp.part.volume
    print(f"  {label}: {vol:.0f} mm3 ({vol / 1000:.2f} cm3)")
    return bp.part


def main():
    print("=" * 60)
    print("HStab_Left v6 -- Build123d")
    print("=" * 60)

    ys = sorted(set([
        FIN_HALF, 10, 25, 50, 75, 100, 125, 150, 170,
        Y_MAIN_END, 195, 200, 205, Y_CAP_START,
    ]))

    outer = []
    inner = []
    for y in ys:
        pts = get_section(y, wall_offset=0.0)
        if pts is None:
            continue
        c = chord_at(y)
        sc = X_HINGE - le_x(y)
        outer.append((y, pts))

        if y < Y_CAP_START - 3:
            ip = get_section(y, wall_offset=WALL)
            if ip:
                inner.append((y, ip))

        print(f"  y={y:6.1f}: chord={c:5.1f} stab={sc:5.1f} pts={len(pts)}")

    total_pts = N_UPPER + 1 + N_HINGE + N_LOWER + 1
    print(f"\nAll sections: {total_pts} pts each")
    print(f"Outer: {len(outer)} secs, Inner: {len(inner)} secs")

    # Verify point counts
    for y, pts in outer:
        assert len(pts) == total_pts, f"y={y}: got {len(pts)}, expected {total_pts}"

    print("\nLofting outer...")
    outer_solid = do_loft(outer, "Outer")

    stab = outer_solid
    if len(inner) >= 3:
        print("Lofting inner...")
        try:
            inner_solid = do_loft(inner, "Inner")
            if inner_solid.volume < outer_solid.volume:
                stab = outer_solid - inner_solid
                sv = stab.volume
                print(f"  Shell: {sv:.0f} mm3 ({sv * 0.75 / 1000:.2f}g @ 0.75 g/cm3)")
            else:
                print(f"  Inner vol ({inner_solid.volume:.0f}) >= outer ({outer_solid.volume:.0f})")
                print("  Offset direction wrong -- exporting solid.")
        except Exception as e:
            print(f"  Inner subtract failed: {e}")
            print("  Exporting solid.")

    # Spar bore
    print(f"\nSpar bore d={SPAR_BORE}mm...")
    try:
        slen = Y_MAIN_END - FIN_HALF + 4
        scy = (FIN_HALF + Y_MAIN_END) / 2
        spar = Location((X_MAIN_SPAR, scy, 0), (90, 0, 0)) * Cylinder(
            SPAR_BORE / 2, slen
        )
        stab = stab - spar
        print("  OK")
    except Exception as e:
        print(f"  Failed: {e}")

    # Hinge bore
    print(f"Hinge bore d={HINGE_BORE}mm...")
    try:
        hlen = Y_HINGE_END - FIN_HALF + 4
        hcy = (FIN_HALF + Y_HINGE_END) / 2
        hw = Location((X_HINGE, hcy, 0), (90, 0, 0)) * Cylinder(
            HINGE_BORE / 2, hlen
        )
        stab = stab - hw
        print("  OK")
    except Exception as e:
        print(f"  Failed: {e}")

    # Export
    d = "cad/components/empennage/HStab_Left"
    os.makedirs(d, exist_ok=True)
    print(f"\nExporting STEP: {d}/HStab_Left.step")
    export_step(stab, f"{d}/HStab_Left.step")
    print(f"Exporting STL: {d}/HStab_Left.stl")
    export_stl(stab, f"{d}/HStab_Left.stl")

    bb = stab.bounding_box()
    fv = stab.volume
    print(f"\n{'=' * 60}")
    print(f"HStab_Left v6 FINAL")
    print(f"  Volume: {fv:.0f} mm3 ({fv / 1000:.2f} cm3)")
    print(f"  Mass (LW-PLA 0.75): {fv * 0.75 / 1000:.2f}g")
    print(f"  Mass (LW-PLA 0.50 foamed): {fv * 0.50 / 1000:.2f}g")
    print(f"  BBox: X=[{bb.min.X:.1f}, {bb.max.X:.1f}]"
          f"  Y=[{bb.min.Y:.1f}, {bb.max.Y:.1f}]"
          f"  Z=[{bb.min.Z:.1f}, {bb.max.Z:.1f}]")
    print(f"{'=' * 60}")

    try:
        from ocp_vscode import show
        show(stab)
    except Exception:
        pass


if __name__ == "__main__":
    main()
