"""
HStab Off-Shelf Components — 3D Models (Build123d)
====================================================
Three trivial off-shelf components:
  1. HStab_Main_Spar  — 3mm OD / 2mm ID carbon tube, 378mm long
  2. Hinge_Wire        — 0.5mm music wire, 424mm long, 90-deg bends at ends (8mm legs)
  3. PETG_Sleeve       — 1.2mm OD / 0.6mm ID sleeve, 3mm long

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_hstab_offshelf_v6.py
"""
import os
import math
from build123d import *
from ocp_vscode import show  # noqa: F401 — available if viewer is open

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_main_spar():
    """3mm OD / 2mm ID carbon tube, 378mm long, along Y axis."""
    OD, ID, LENGTH = 3.0, 2.0, 378.0
    with BuildPart() as spar:
        with BuildSketch():
            Circle(OD / 2)
            Circle(ID / 2, mode=Mode.SUBTRACT)
        extrude(amount=LENGTH)
    return spar.part


def build_hinge_wire():
    """0.5mm music wire, 424mm total, with 90-deg bends 8mm from each end."""
    DIAM = 0.5
    TOTAL = 424.0
    BEND_LEG = 8.0
    STRAIGHT = TOTAL - 2 * BEND_LEG  # 408mm center section

    # Build the wire path: three segments with right-angle bends
    # Path runs along Z for the straight section, bends down (-Y) at each end
    # Bend radius = 1mm (tight music-wire bend)
    R_BEND = 1.0

    # Build path as a series of edges
    path = (
        Line((0, 0, 0), (0, 0, BEND_LEG - R_BEND))
        + RadiusArc((0, 0, BEND_LEG - R_BEND), (0, R_BEND, BEND_LEG), R_BEND)
        + Line((0, R_BEND, BEND_LEG), (0, R_BEND, BEND_LEG + STRAIGHT))
        + RadiusArc((0, R_BEND, BEND_LEG + STRAIGHT), (0, 0, BEND_LEG + STRAIGHT + R_BEND), R_BEND)
        + Line((0, 0, BEND_LEG + STRAIGHT + R_BEND), (0, 0, TOTAL))
    )

    wire = Wire([e if isinstance(e, Edge) else e for e in path.edges()])

    with BuildPart() as hinge:
        with BuildSketch(Plane.XY):
            Circle(DIAM / 2)
        sweep(path=wire)
    return hinge.part


def build_petg_sleeve():
    """1.2mm OD / 0.6mm ID PETG sleeve, 3mm long."""
    OD, ID, LENGTH = 1.2, 0.6, 3.0
    with BuildPart() as sleeve:
        with BuildSketch():
            Circle(OD / 2)
            Circle(ID / 2, mode=Mode.SUBTRACT)
        extrude(amount=LENGTH)
    return sleeve.part


def save_step(part, rel_path):
    """Export a part to STEP, creating directories as needed."""
    full = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    export_step(part, full)
    print(f"  Exported: {rel_path}  ({os.path.getsize(full)} bytes)")


def main():
    print("=== Building HStab Off-Shelf Components ===\n")

    # 1. Main Spar
    print("[1/3] HStab_Main_Spar (3mm OD carbon tube, 378mm)...")
    spar = build_main_spar()
    save_step(spar, "cad/components/empennage/HStab_Main_Spar/HStab_Main_Spar.step")

    # 2. Hinge Wire
    print("[2/3] Hinge_Wire (0.5mm music wire, 424mm, bent ends)...")
    wire = build_hinge_wire()
    save_step(wire, "cad/components/empennage/Hinge_Wire/Hinge_Wire.step")

    # 3. PETG Sleeve
    print("[3/3] PETG_Sleeve (1.2mm OD, 3mm long)...")
    sleeve = build_petg_sleeve()
    save_step(sleeve, "cad/components/empennage/PETG_Sleeves/PETG_Sleeve.step")

    print("\n=== All 3 components exported successfully ===")


if __name__ == "__main__":
    main()
