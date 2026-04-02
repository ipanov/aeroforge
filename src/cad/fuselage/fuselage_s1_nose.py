"""Fuselage S1 Nose — Build123d parametric model.

Nose section X=0 to X=260mm of the AeroForge integrated fuselage.
Ogive nose transitioning to elliptical cross-section at wing LE station.

This script creates the OUTER MOLD LINE (OML) as a smooth lofted solid.
Internal features (motor bore, longeron channels, etc.) are NOT boolean-cut
from the loft — OCCT booleans on complex lofts hang or fail silently.
Instead, internal features are:
  - Motor mount ring: separate CF-PETG component (bonded into shell)
  - Longeron sleeves: printed as part of internal structure
  - Battery/ESC/Rx bays: slicer infill voids, not BREP cuts
  - M3 holes: drilled post-print through the PETG motor mount

The mesh pipeline (STEP -> STL -> geodesic ribs -> 3MF) handles shell
wall thickness via slicer settings (vase mode 0.6mm).

Cross-section schedule (from DESIGN_CONSENSUS v2):
  X=0:   point (spinner tip — approximated as tiny circle)
  X=30:  32mm dia circle (motor face / spinner base)
  X=55:  35mm dia circle (PETG zone)
  X=150: 50x44mm ellipse (max section, battery)
  X=260: 38x34mm ellipse (S1/S2 joint face)

All dimensions in mm.
"""

import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from build123d import (
    BuildPart,
    BuildSketch,
    Circle,
    Ellipse,
    Plane,
    export_step,
    export_stl,
    loft,
)

# ============================================================
# CROSS-SECTION SCHEDULE
# ============================================================
# Defines the outer mold line at discrete X stations.
# Ogive nose (X=0-30) uses closely spaced circular sections that
# follow the Haack series ogive equation for minimum drag.
# Body (X=30-260) transitions from circular to elliptical.

# Haack series ogive: r(x) = R * sqrt(theta - sin(2*theta)/2) / sqrt(pi)
# where theta = acos(1 - 2*x/L), R = nose radius, L = ogive length
OGIVE_LENGTH = 30.0  # length of nose cone region
OGIVE_RADIUS = 16.0  # radius at X=30 (32mm dia / 2)


def ogive_radius(x):
    """Haack series (LD-Haack, minimum drag) ogive radius at station x.

    Valid for 0 <= x <= OGIVE_LENGTH.
    Returns radius in mm.
    """
    if x <= 0:
        return 0.0
    if x >= OGIVE_LENGTH:
        return OGIVE_RADIUS
    theta = math.acos(1.0 - 2.0 * x / OGIVE_LENGTH)
    return OGIVE_RADIUS * math.sqrt(theta - math.sin(2.0 * theta) / 2.0) / math.sqrt(math.pi)


# Body cross-sections (X > 30): (X, width, height)
# Width and height define an ellipse (circle when W == H)
BODY_SECTIONS = [
    # X      W      H      Notes
    ( 30,   32.0,  32.0),  # spinner base (circle)
    ( 40,   34.0,  34.0),  # motor bay
    ( 55,   35.0,  35.0),  # PETG zone
    ( 70,   38.0,  36.0),  # transition circular -> elliptical
    ( 90,   42.0,  39.0),  # LW-PLA shell starts
    (120,   47.0,  42.0),  # battery fwd
    (150,   50.0,  44.0),  # MAX SECTION (battery center)
    (180,   48.0,  42.0),  # battery aft / receiver fwd
    (210,   42.0,  37.0),  # receiver aft
    (240,   39.0,  35.0),  # transition / taper
    (260,   38.0,  34.0),  # S1/S2 joint face
]


def build_fuselage_s1_nose():
    """Build the Fuselage S1 Nose outer mold line as a lofted solid.

    Returns a Build123d Part (solid body).
    """
    t0 = time.time()
    print("=" * 60)
    print("BUILDING FUSELAGE S1 NOSE — OUTER MOLD LINE")
    print("=" * 60)

    # ----------------------------------------------------------
    # Generate ogive nose sections (X=2 to X=30, closely spaced)
    # ----------------------------------------------------------
    print("\n  Generating ogive nose sections (Haack series)...")

    ogive_stations = [2, 4, 6, 8, 10, 13, 16, 20, 25, 30]
    all_sections = []

    for x in ogive_stations:
        r = ogive_radius(x)
        if r < 0.5:
            continue  # skip too-small sections
        plane = Plane(origin=(x, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
        with BuildSketch(plane) as sk:
            Circle(r)
        all_sections.append((x, sk.sketch.face()))
        print(f"    X={x:>3d}mm: circle dia={2*r:.1f}mm (ogive)")

    # ----------------------------------------------------------
    # Generate body sections (X=40 to X=260)
    # ----------------------------------------------------------
    print("\n  Generating body sections...")

    for x, w, h in BODY_SECTIONS:
        if x <= 30:
            continue  # already covered by ogive
        plane = Plane(origin=(x, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
        with BuildSketch(plane) as sk:
            if abs(w - h) < 0.1:
                Circle(w / 2.0)
            else:
                Ellipse(w / 2.0, h / 2.0)
        all_sections.append((x, sk.sketch.face()))
        shape = 'circle' if abs(w - h) < 0.1 else 'ellipse'
        print(f"    X={x:>3d}mm: {shape} {w:.0f}x{h:.0f}mm")

    # Sort by X station (should already be sorted, but ensure)
    all_sections.sort(key=lambda s: s[0])

    # Extract just the faces for lofting
    faces = [face for _, face in all_sections]

    # ----------------------------------------------------------
    # Loft through all sections
    # ----------------------------------------------------------
    print(f"\n  Lofting through {len(faces)} cross-sections...")

    with BuildPart() as oml:
        loft(faces, ruled=False)

    result = oml.part
    bb = result.bounding_box()
    vol = result.volume
    surface_area = sum(f.area for f in result.faces())

    # Shell mass estimate (vase mode, 0.6mm wall)
    shell_vol = surface_area * 0.6  # mm³
    shell_mass_lwpla = shell_vol * 0.00065  # LW-PLA foamed ~0.65 g/cm³
    shell_mass_petg = shell_vol * 0.00127   # PETG ~1.27 g/cm³

    dt = time.time() - t0

    print(f"\n{'=' * 60}")
    print("FUSELAGE S1 NOSE — BUILD COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Bounding box: {bb.max.X - bb.min.X:.1f} x "
          f"{bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f} mm")
    print(f"  OML solid volume: {vol:.0f} mm³ ({vol/1000:.1f} cm³)")
    print(f"  Surface area: {surface_area:.0f} mm²")
    print(f"  Est. shell (0.6mm LW-PLA): {shell_mass_lwpla:.1f}g ({shell_vol/1000:.1f} cm³)")
    print(f"  Est. shell (0.6mm PETG):   {shell_mass_petg:.1f}g")
    print(f"  Build time: {dt:.1f}s")

    # Validation checks
    print("\n  Validation:")
    length = bb.max.X - bb.min.X
    max_w = bb.max.Y - bb.min.Y
    max_h = bb.max.Z - bb.min.Z

    checks = [
        (abs(length - 258) < 5, f"Length {length:.1f}mm (expect ~258mm)"),
        (abs(max_w - 50) < 2, f"Max width {max_w:.1f}mm (expect ~50mm)"),
        (abs(max_h - 44) < 2, f"Max height {max_h:.1f}mm (expect ~44mm)"),
        (shell_mass_lwpla < 20, f"Shell mass {shell_mass_lwpla:.1f}g < 20g"),
    ]
    for ok, msg in checks:
        status = "PASS" if ok else "FAIL"
        print(f"    [{status}] {msg}")

    return result


# ============================================================
# MAIN: Build, export, display
# ============================================================

if __name__ == "__main__":
    result = build_fuselage_s1_nose()

    # Export STEP
    step_dir = "cad/components/fuselage/Fuselage_S1_Nose"
    step_path = os.path.join(step_dir, "Fuselage_S1_Nose.step")
    os.makedirs(step_dir, exist_ok=True)
    export_step(result, step_path)
    sz = os.path.getsize(step_path) // 1024
    print(f"\nSTEP exported: {step_path} ({sz}KB)")

    # Export STL (high quality for mesh pipeline)
    stl_path = os.path.join(step_dir, "Fuselage_S1_Nose.stl")
    export_stl(result, stl_path, tolerance=0.001, angular_tolerance=0.05)
    sz = os.path.getsize(stl_path) // 1024
    print(f"STL exported:  {stl_path} ({sz}KB)")

    # Display in OCP Viewer
    try:
        from ocp_vscode import show, save_screenshot
        import time as _t
        show(result,
             names=["Fuselage_S1_Nose"],
             colors=["mediumpurple"],
             alphas=[0.5])
        _t.sleep(2)
        save_screenshot("exports/validation/Fuselage_S1_Nose_ocp.png")
        print("OCP screenshot saved")
    except Exception as e:
        print(f"OCP Viewer: {e}")
