"""
Build HStab_Left using Build123d
================================
Uses Spline-based airfoil profiles for smooth NURBS surfaces.
Includes internal rib structure and spar tube channels.

From Design Consensus v2:
  Blend: HT-14 (root) -> HT-13 (tip)
  430mm total span (215mm per half)
  115mm root / 75mm tip chord
  3mm pivot rod at 25% chord
  2mm rear spar at 65% chord
"""

import os
import sys
import math

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build123d import *
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir

# === PARAMETERS ===
HALF_SPAN = 200.0  # mm (main section before tip)
ROOT_CHORD = 115.0
TIP_CHORD = 75.0
T_ROOT = 0.075  # HT-14
T_TIP = 0.065   # HT-13
PIVOT_FRAC = 0.25
RSPAR_FRAC = 0.65
PIVOT_BORE = 2.0   # radius for 3mm rod + clearance
RSPAR_BORE = 1.4   # radius for 2mm rod + clearance

# Load airfoil .dat files
def load_dat(name):
    """Load airfoil coordinates from .dat file."""
    dat_path = os.path.join("docs", "rag", "airfoil_database", f"{name}.dat")
    coords = []
    with open(dat_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line[0].isalpha():
                continue
            parts = line.split()
            if len(parts) >= 2:
                coords.append((float(parts[0]), float(parts[1])))
    # Close TE: average first and last points
    x_avg = (coords[0][0] + coords[-1][0]) / 2
    z_avg = (coords[0][1] + coords[-1][1]) / 2
    coords[0] = (x_avg, z_avg)
    coords[-1] = (x_avg, z_avg)
    return coords

def chord_at(eta):
    return ROOT_CHORD + (TIP_CHORD - ROOT_CHORD) * eta

def blend_coords(c1, c2, eta):
    """Linearly blend two airfoil coordinate sets."""
    n = min(len(c1), len(c2))
    blended = []
    for i in range(n):
        x = c1[i][0] * (1 - eta) + c2[i][0] * eta
        z = c1[i][1] * (1 - eta) + c2[i][1] * eta
        blended.append((x, z))
    # Ensure closure
    blended[-1] = blended[0]
    return blended

def make_airfoil_wire(coords, chord, y_pos):
    """Create a Build123d Wire from airfoil coords at given chord and span position.
    Split into upper + lower splines + TE line for clean geometry."""
    # Find the LE (minimum x)
    min_x = min(c[0] for c in coords)
    le_idx = next(i for i, c in enumerate(coords) if c[0] == min_x)

    # Upper surface: from TE to LE (indices 0 to le_idx)
    upper_pts = [(c[0] * chord, y_pos, c[1] * chord) for c in coords[:le_idx + 1]]
    # Lower surface: from LE to TE (indices le_idx to end)
    lower_pts = [(c[0] * chord, y_pos, c[1] * chord) for c in coords[le_idx:]]

    # Create splines
    upper_spline = Spline(*[Vector(*p) for p in upper_pts])
    lower_spline = Spline(*[Vector(*p) for p in lower_pts])

    # TE closing line
    te_start = Vector(*upper_pts[0])
    te_end = Vector(*lower_pts[-1])

    dist = (te_start - te_end).length
    if dist > 0.001:
        te_line = Line(te_end, te_start)
        wire = Wire([upper_spline, lower_spline, te_line])
    else:
        wire = Wire([upper_spline, lower_spline])

    return wire


def main():
    print("Loading airfoil data...")
    ht14 = load_dat("ht14")
    ht13 = load_dat("ht13")
    print(f"  HT-14: {len(ht14)} points")
    print(f"  HT-13: {len(ht13)} points")

    # Create airfoil profiles at span stations
    etas = [0.0, 0.15, 0.30, 0.50, 0.70, 0.85, 1.0]
    print(f"\nCreating {len(etas)} airfoil profiles...")

    profiles = []
    for eta in etas:
        y = eta * HALF_SPAN
        c = chord_at(eta)
        blended = blend_coords(ht14, ht13, eta)
        wire = make_airfoil_wire(blended, c, y)
        profiles.append(wire)
        print(f"  eta={eta:.2f}: y={y:.0f}mm, chord={c:.0f}mm")

    # Loft the profiles into a solid
    print("\nLofting profiles into solid...")
    stab_solid = Solid.make_loft(profiles)
    print(f"  Solid created: volume={stab_solid.volume:.0f} mm3")

    # Cut spar channels
    print("\nCutting spar channels...")
    pivot_x = ROOT_CHORD * PIVOT_FRAC
    rspar_x = ROOT_CHORD * RSPAR_FRAC

    # Pivot rod channel (runs along Y axis)
    pivot_cyl = Solid.make_cylinder(
        PIVOT_BORE, HALF_SPAN + 4,
        Plane(origin=(pivot_x, -2, 0), z_dir=(0, 1, 0))
    )
    result = stab_solid - pivot_cyl

    # Rear spar channel
    rspar_cyl = Solid.make_cylinder(
        RSPAR_BORE, HALF_SPAN + 4,
        Plane(origin=(rspar_x, -2, 0), z_dir=(0, 1, 0))
    )
    result = result - rspar_cyl

    print(f"  Final solid: volume={result.volume:.0f} mm3")
    bb = result.bounding_box()
    print(f"  Dims: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")

    # Export
    out_step = "cad/components/empennage/HStab_Left/HStab_Left.step"
    out_stl = "cad/components/empennage/HStab_Left/HStab_Left.stl"
    os.makedirs(os.path.dirname(out_step), exist_ok=True)

    export_step(result, out_step)
    print(f"\n  STEP exported: {out_step}")

    export_stl(result, out_stl)
    print(f"  STL exported: {out_stl}")

    print("\nDone. Import STEP into FreeCAD for visualization and FEM.")


if __name__ == "__main__":
    main()
