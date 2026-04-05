"""
Build and export STEP files for off-shelf electronic hardware components.
Generates STEP for: Flysky FS-iA6B, LiPo 3S 1300mAh, XT60 Connector.

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_hardware_electronics.py
"""

import sys
import os
from pathlib import Path

# Add project root (projects/air4-f5j/) for local imports (hardware.*, specs, etc.)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Add repo root for framework imports (src.*)
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from build123d import *


def _export(part, step_path):
    """Export a Build123d part/compound to STEP."""
    export_step(part, str(step_path))


def build_receiver():
    """Build Flysky FS-iA6B receiver and export STEP."""
    from hardware.receiver import FlyskyIA6BReceiver

    rx = FlyskyIA6BReceiver()
    out_dir = Path("cad/components/hardware/Flysky_FS_iA6B_Receiver")
    out_dir.mkdir(parents=True, exist_ok=True)

    step_path = out_dir / "Flysky_FS_iA6B_Receiver.step"
    _export(rx, step_path)

    bb = rx.bounding_box()
    print(f"Flysky FS-iA6B Receiver:")
    print(f"  STEP: {step_path}")
    print(f"  Size: {bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f}mm")
    print(f"  Joints: {list(rx.joints.keys())}")
    return rx


def build_battery():
    """Build LiPo 3S 1300mAh battery and export STEP."""
    from hardware.battery import BatteryPack

    battery = BatteryPack()
    out_dir = Path("cad/components/hardware/LiPo_3S_1300mAh")
    out_dir.mkdir(parents=True, exist_ok=True)

    step_path = out_dir / "LiPo_3S_1300mAh.step"
    _export(battery, step_path)

    bb = battery.bounding_box()
    print(f"\nLiPo 3S 1300mAh Battery:")
    print(f"  STEP: {step_path}")
    print(f"  Size: {bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f}mm")
    print(f"  Joints: {list(battery.joints.keys())}")
    return battery


def build_xt60():
    """Build XT60 male connector and export STEP.

    Uses the KiCad reference model if available, otherwise builds parametric.
    """
    ref_step = Path("components/reference_models/xt60_male_kicad.step")

    if ref_step.exists():
        # Import reference model
        from src.cad.hardware.xt60 import XT60Male
        xt60 = XT60Male()
        print(f"\nXT60 Male Connector (from KiCad reference):")
    else:
        # Build parametric model
        xt60 = _build_xt60_parametric()
        print(f"\nXT60 Male Connector (parametric):")

    out_dir = Path("cad/components/hardware/XT60_Connector")
    out_dir.mkdir(parents=True, exist_ok=True)

    step_path = out_dir / "XT60_Connector.step"
    _export(xt60, step_path)

    bb = xt60.bounding_box()
    print(f"  STEP: {step_path}")
    print(f"  Size: {bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f}mm")
    print(f"  Joints: {list(xt60.joints.keys())}")
    return xt60


def _build_xt60_parametric():
    """Parametric XT60 male connector model."""
    L = 16.0    # depth (pin direction)
    W = 8.0     # width
    H = 15.8    # height
    chamfer_size = 3.0  # keying chamfer
    pin_dia = 3.5
    pin_spacing = 7.2   # center-to-center Y
    pin_protrude = 3.0  # how far pins stick out front

    with BuildPart() as bp:
        # Main body with keying chamfer
        Box(L, W, H)

        # Chamfer one corner for keying (top-right in Y-Z plane at +X face)
        # Use a subtracted wedge
        with Locations([(0, W / 2, H / 2)]):
            with BuildPart(mode=Mode.SUBTRACT):
                # Triangular prism to cut the corner
                Wedge(L + 0.1, chamfer_size, chamfer_size, 0, 0, 0, 0)

        # Pin holes (through the body along X axis)
        for y_off in [-pin_spacing / 2, pin_spacing / 2]:
            with Locations([(0, 0, y_off)]):
                Hole(radius=pin_dia / 2 + 0.1, depth=L + 0.1)

        # === JOINTS ===
        RigidJoint("mating_face",
                   joint_location=Location((0, 0, 0)))
        RigidJoint("solder_positive",
                   joint_location=Location((L / 2, 0, pin_spacing / 2), (0, 180, 0)))
        RigidJoint("solder_negative",
                   joint_location=Location((L / 2, 0, -pin_spacing / 2), (0, 180, 0)))
        RigidJoint("rear_face",
                   joint_location=Location((L / 2, 0, 0)))

    part = Compound(bp.part.wrapped, label="XT60_male", joints=bp.joints)
    part.color = Color(0.95, 0.85, 0.0)
    return part


def main():
    print("Building hardware electronics STEP files...\n")
    build_receiver()
    build_battery()
    build_xt60()
    print("\nAll hardware STEP files generated.")


if __name__ == "__main__":
    main()
