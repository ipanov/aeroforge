"""
Build HStab_Right using Build123d (mirror of HStab_Left)
=========================================================
Mirrors the left half across Y=0 to create the right half.
Uses identical airfoil blend and spar channels.

From Design Consensus v2:
  Blend: HT-14 (root) -> HT-13 (tip)
  430mm total span (215mm per half)
  115mm root / 75mm tip chord
  3mm pivot rod at 25% chord
  2mm rear spar at 65% chord
"""

import os
import sys

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build123d import *

# Import the left-half builder
from scripts.build_hstab_left import load_dat, blend_coords, chord_at, make_airfoil_wire
from scripts.build_hstab_left import HALF_SPAN, ROOT_CHORD, PIVOT_FRAC, RSPAR_FRAC
from scripts.build_hstab_left import PIVOT_BORE, RSPAR_BORE


def main():
    print("Loading airfoil data...")
    ht14 = load_dat("ht14")
    ht13 = load_dat("ht13")
    print(f"  HT-14: {len(ht14)} points")
    print(f"  HT-13: {len(ht13)} points")

    # Create airfoil profiles at span stations (mirrored: negative Y)
    etas = [0.0, 0.15, 0.30, 0.50, 0.70, 0.85, 1.0]
    print(f"\nCreating {len(etas)} airfoil profiles (right half, -Y)...")

    profiles = []
    for eta in etas:
        y = -(eta * HALF_SPAN)  # Mirror: negative Y
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

    # Pivot rod channel (runs along -Y axis)
    pivot_cyl = Solid.make_cylinder(
        PIVOT_BORE, HALF_SPAN + 4,
        Plane(origin=(pivot_x, 2, 0), z_dir=(0, -1, 0))
    )
    result = stab_solid - pivot_cyl

    # Rear spar channel
    rspar_cyl = Solid.make_cylinder(
        RSPAR_BORE, HALF_SPAN + 4,
        Plane(origin=(rspar_x, 2, 0), z_dir=(0, -1, 0))
    )
    result = result - rspar_cyl

    print(f"  Final solid: volume={result.volume:.0f} mm3")
    bb = result.bounding_box()
    print(f"  Dims: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")

    # Export
    out_dir = "cad/components/empennage/HStab_Right"
    out_step = f"{out_dir}/HStab_Right.step"
    out_stl = f"{out_dir}/HStab_Right.stl"
    os.makedirs(out_dir, exist_ok=True)

    export_step(result, out_step)
    print(f"\n  STEP exported: {out_step}")

    export_stl(result, out_stl)
    print(f"  STL exported: {out_stl}")

    print("\nDone. HStab_Right is the mirror of HStab_Left.")


if __name__ == "__main__":
    main()
