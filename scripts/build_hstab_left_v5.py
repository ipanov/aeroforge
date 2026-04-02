"""
Build123d: HStab_Left Shell (3D Model) — v5 Consensus
=====================================================
Fixed horizontal stabilizer LEFT half-shell.
Superellipse planform, HT-13→HT-12 blend, spar tunnels.
"""

import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from build123d import *
from ocp_vscode import show
import numpy as np
from src.cad.airfoils import get_airfoil

# ── V5 PARAMETERS ──
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
SE_N = 2.3
HINGE_X = 74.75
MAIN_SPAR_X = 35.0
REAR_SPAR_X = 69.0
MAIN_SPAR_BORE = 3.1
REAR_SPAR_BORE = 1.6
MAIN_SPAR_END = 186.0
ALIGN_FRAC = 0.45
ALIGN_X = ALIGN_FRAC * ROOT_CHORD  # 51.75
TC_ROOT = 0.065
TC_TIP = 0.051
ROOT_GAP = 4.0

ht13 = get_airfoil('ht13')
TC13 = ht13[:, 1].max() - ht13[:, 1].min()

def chord_at(y):
    eta = abs(y) / HALF_SPAN
    return ROOT_CHORD * (1.0 - eta ** SE_N) ** (1.0 / SE_N) if eta < 1 else 0.0

def le_x_at(y):
    return ALIGN_X - ALIGN_FRAC * chord_at(y)

def tc_at(y):
    return TC_ROOT * (1.0 - abs(y)/HALF_SPAN) + TC_TIP * (abs(y)/HALF_SPAN)

def make_section_wire(y):
    """Build a closed wire for the stab cross-section at span station y.
    Stab goes from LE to hinge line (65% chord at root)."""
    c = chord_at(y)
    if c < 2.0:
        return None
    tc = tc_at(y)
    le_x = le_x_at(y)
    hinge_local = HINGE_X - le_x  # local x of hinge from section LE

    # Scale HT-13 profile to desired t/c and chord
    prof = ht13.copy()
    prof[:, 1] *= tc / TC13
    prof[:, 0] *= c
    prof[:, 1] *= c

    le_idx = np.argmin(prof[:, 0])
    upper = prof[:le_idx+1]   # TE→LE
    lower = prof[le_idx:]      # LE→TE

    # Clip to stab portion (x <= hinge_local)
    def clip_surface(pts, hinge_x):
        result = []
        for i in range(len(pts)):
            if pts[i, 0] <= hinge_x:
                result.append(pts[i])
            else:
                # Interpolate with previous point
                if i > 0 and pts[i-1, 0] <= hinge_x:
                    t = (hinge_x - pts[i-1, 0]) / (pts[i, 0] - pts[i-1, 0])
                    yi = pts[i-1, 1] + t * (pts[i, 1] - pts[i-1, 1])
                    result.append(np.array([hinge_x, yi]))
                break
        return result

    upper_c = clip_surface(upper, hinge_local)
    # For lower, clip in reverse (it goes LE→TE)
    lower_c = []
    for i in range(len(lower)):
        if lower[i, 0] <= hinge_local:
            lower_c.append(lower[i])
        else:
            if lower[i-1, 0] <= hinge_local:
                t = (hinge_local - lower[i-1, 0]) / (lower[i, 0] - lower[i-1, 0])
                yi = lower[i-1, 1] + t * (lower[i, 1] - lower[i-1, 1])
                lower_c.append(np.array([hinge_local, yi]))
            break

    if len(upper_c) < 2 or len(lower_c) < 2:
        return None

    # Build closed wire: upper (hinge→LE) + lower (LE→hinge) + close
    pts = []
    for p in upper_c:
        pts.append(Vector(le_x + p[0], y, p[1]))
    for p in lower_c[1:]:  # skip LE duplicate
        pts.append(Vector(le_x + p[0], y, p[1]))

    if len(pts) < 3:
        return None

    edges = [Edge.make_line(pts[i], pts[i+1]) for i in range(len(pts)-1)]
    edges.append(Edge.make_line(pts[-1], pts[0]))  # close

    try:
        w = Wire(edges)
        if w.is_valid:
            return w
    except:
        pass
    return None


def build():
    # Generate span stations (denser near root/tip)
    stations = sorted(set(
        [ROOT_GAP + (HALF_SPAN - ROOT_GAP) * i / 30 for i in range(31)]
        + [50, 100, 150, MAIN_SPAR_END, 200, 205, 210, 212, 214]
    ))
    stations = [y for y in stations if ROOT_GAP <= y <= HALF_SPAN]

    wires = []
    for y in stations:
        w = make_section_wire(y)
        if w is not None:
            wires.append(w)

    print(f"Lofting {len(wires)} sections...")
    if len(wires) < 2:
        raise ValueError("Need >= 2 wires for loft")

    shell = loft(wires)

    # ── Spar tunnels ──
    main_cyl = Pos(MAIN_SPAR_X, ROOT_GAP, 0) * Cylinder(
        MAIN_SPAR_BORE/2, MAIN_SPAR_END - ROOT_GAP,
        align=(Align.CENTER, Align.MIN, Align.CENTER))
    rear_cyl = Pos(REAR_SPAR_X, ROOT_GAP, 0) * Cylinder(
        REAR_SPAR_BORE/2, HALF_SPAN - ROOT_GAP,
        align=(Align.CENTER, Align.MIN, Align.CENTER))

    result = shell - main_cyl - rear_cyl
    return result


if __name__ == "__main__":
    print("Building HStab_Left (v5)...")
    result = build()
    show(result, names=["HStab_Left"])

    step_path = "cad/components/empennage/HStab_Left/HStab_Left.step"
    export_step(result, step_path)
    print(f"STEP: {step_path}")

    bb = result.bounding_box
    print(f"BBox: X[{bb.min.X:.1f}..{bb.max.X:.1f}] Y[{bb.min.Y:.1f}..{bb.max.Y:.1f}] Z[{bb.min.Z:.1f}..{bb.max.Z:.1f}]")
    print(f"Volume: {result.volume:.0f} mm³")
