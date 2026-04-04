"""
Rudder 3D Model — v1 (Build123d)
==================================
Rudder shell: hinge face to TE, with convex bull-nose extending forward
of hinge line. Lofted through HT-14 -> HT-12 blended airfoil sections.

The rudder is a VERTICAL control surface on the VStab trailing edge.
Orientation in Build123d:
  X = chordwise (0 at hinge, positive toward TE)
  Y = spanwise/height (0 at root, 165 at tip)
  Z = thickness direction

Includes: hinge wire bore, pushrod hole.
Single-piece vase-mode print.

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_rudder.py
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from build123d import *
from src.cad.airfoils import blend_airfoils

# ── Parameters ──
from rudder_geometry import (
    VSTAB_HEIGHT, VSTAB_ROOT_CHORD, VSTAB_TIP_CHORD, VSTAB_TAPER_RATE,
    HINGE_FRAC_ROOT, HINGE_FRAC_TIP, RUDDER_FRAC_ROOT, RUDDER_FRAC_TIP,
    HINGE_BORE_D, PUSHROD_BORE_D, PUSHROD_Z,
    BULL_NOSE_ROOT, BULL_NOSE_FADE_Z,
    TE_TRUNC, WALL, LW_PLA_DENSITY,
    vstab_chord, hinge_frac, rudder_frac, rudder_chord, bull_nose_depth,
)

# Root and tip face clearances
Y_ROOT = 0.0      # root face
Y_TIP = 165.0     # tip

N_HINGE_FACE = 8   # points on hinge face / bull-nose arc
N_LOWER = 40        # points on lower surface hinge->TE
N_UPPER = 40        # points on upper surface TE->hinge


def get_blended_surfaces(z_height, n_pts=100):
    """Return (upper, lower) arrays of (x_frac, y_frac), LE->TE order.
    Uses HT-14 at root, HT-12 at tip."""
    blend = min(z_height / VSTAB_HEIGHT, 1.0)
    airfoil = blend_airfoils("ht14", "ht12", blend, n_pts)
    le_idx = int(np.argmin(airfoil[:, 0]))
    upper = airfoil[:le_idx + 1][::-1].copy()
    lower = airfoil[le_idx:].copy()
    return upper, lower


def interp_surface(surface, x_frac):
    """Interpolate surface y/c at a given x/c fraction."""
    return float(np.interp(x_frac, surface[:, 0], surface[:, 1]))


def generate_section_2d(z_station):
    """Generate closed 2D profile points (x_local, thickness) for rudder at height z.

    x_local = 0 at hinge line, positive toward TE.
    Returns list of (x, z_thickness) tuples forming closed loop, or None.
    FIXED point count for all sections (critical for loft compatibility).
    """
    vc = vstab_chord(z_station)
    if vc < 1.0:
        return None

    hf = hinge_frac(z_station)
    rf = rudder_frac(z_station)
    te_frac = min(hf + rf * TE_TRUNC, 1.0)

    rc = (te_frac - hf) * vc  # rudder chord in mm
    if rc < 1.0:
        return None

    bn = bull_nose_depth(z_station)

    upper, lower = get_blended_surfaces(z_station, 120)

    z_upper_hinge = interp_surface(upper, hf) * vc
    z_lower_hinge = interp_surface(lower, hf) * vc

    points = []

    # 1. Hinge face / bull-nose: from upper-hinge around to lower-hinge
    mid_z = (z_upper_hinge + z_lower_hinge) / 2.0
    r_z = abs(z_upper_hinge - z_lower_hinge) / 2.0

    for i in range(N_HINGE_FACE + 1):
        angle = math.pi / 2 - math.pi * i / N_HINGE_FACE
        if bn > 0.1:
            arc_x = -bn * math.cos(angle)  # negative = forward of hinge
        else:
            arc_x = 0.0  # flat hinge face
        arc_z = mid_z + r_z * math.sin(angle)
        points.append((arc_x, arc_z))

    # 2. Lower surface: hinge -> TE
    for i in range(1, N_LOWER + 1):
        t = i / N_LOWER
        frac = hf + t * (te_frac - hf)
        z = interp_surface(lower, frac) * vc
        x = (frac - hf) * vc  # distance from hinge
        points.append((x, z))

    # 3. TE closure: add upper TE point
    z_upper_te = interp_surface(upper, te_frac) * vc
    x_te = (te_frac - hf) * vc
    points.append((x_te, z_upper_te))

    # 4. Upper surface: TE -> hinge
    for i in range(1, N_UPPER):
        t = i / N_UPPER
        frac = te_frac - t * (te_frac - hf)
        z = interp_surface(upper, frac) * vc
        x = (frac - hf) * vc
        points.append((x, z))

    # Close back to first point
    points.append(points[0])

    return points


def main():
    print("=" * 60)
    print("Building Rudder v1 3D model (Build123d)")
    print("=" * 60)

    # Stations — well-spaced for reliable loft
    stations = [
        Y_ROOT,          # 0 — root face
        10, 25, 41,      # near root, first rib
        60, 83,          # second rib
        100, 124,        # third rib
        140, BULL_NOSE_FADE_Z,  # 155 — bull-nose fades
        160, Y_TIP,      # tip
    ]

    print(f"\nGenerating {len(stations)} airfoil sections...")
    valid_stations = []
    for z in stations:
        vc = vstab_chord(z)
        rc = rudder_chord(z)
        bn = bull_nose_depth(z)

        pts = generate_section_2d(z)
        if pts is not None and len(pts) > 10:
            valid_stations.append((z, pts))
            print(f"  z={z:6.1f}mm: VStab_chord={vc:.1f}mm, rudder_chord={rc:.1f}mm, "
                  f"bn={bn:.2f}mm  ({len(pts)} pts)")
        else:
            print(f"  z={z:6.1f}mm: VStab_chord={vc:.1f}mm, rudder_chord={rc:.1f}mm — SKIPPED")

    if len(valid_stations) < 3:
        print("ERROR: Not enough sections")
        return

    # ── Build using BuildPart + BuildSketch on offset planes ──
    print(f"\nBuilding solid via loft of {len(valid_stations)} sketches...")

    def clean_pts(pts, min_dist=0.02):
        """Remove consecutive near-duplicate points and ensure closure."""
        cleaned = [pts[0]]
        for p in pts[1:]:
            d = math.sqrt((p[0] - cleaned[-1][0])**2 + (p[1] - cleaned[-1][1])**2)
            if d > min_dist:
                cleaned.append(p)
        d_close = math.sqrt(
            (cleaned[-1][0] - cleaned[0][0])**2 + (cleaned[-1][1] - cleaned[0][1])**2)
        if d_close > min_dist:
            cleaned.append(cleaned[0])
        elif d_close > 1e-6:
            cleaned[-1] = cleaned[0]
        return cleaned

    with BuildPart() as builder:
        for idx, (z, pts_2d) in enumerate(valid_stations):
            pts_clean = clean_pts(pts_2d)
            if len(pts_clean) < 5:
                print(f"  WARNING: Section z={z} has too few points ({len(pts_clean)}), skipping")
                continue

            # Sketch plane: XZ plane offset along Y (Y = height/span)
            # Each section is drawn in the local XZ plane at Y = z
            plane = Plane(
                origin=(0, z, 0),
                x_dir=(1, 0, 0),
                z_dir=(0, 1, 0),
            )
            with BuildSketch(plane) as sk:
                with BuildLine() as ln:
                    Polyline(*[(p[0], p[1]) for p in pts_clean])
                make_face()

        loft(ruled=True)

    rudder_solid = builder.part
    vol = rudder_solid.volume
    print(f"  Loft successful. Volume: {vol:.1f} mm^3 ({vol / 1000:.2f} cm^3)")

    # ── Shell volume (analytical) ──
    print(f"\nComputing shell volume analytically (WALL={WALL}mm)...")
    outer_vol = rudder_solid.volume
    surface_area = rudder_solid.area
    root_face = min(rudder_solid.faces(), key=lambda f: f.center().Y)
    root_area = root_face.area
    wetted_area = surface_area - root_area
    shell_vol = wetted_area * WALL

    print(f"  Outer volume:  {outer_vol:.1f} mm^3")
    print(f"  Total surface: {surface_area:.1f} mm^2")
    print(f"  Root face:     {root_area:.1f} mm^2")
    print(f"  Wetted area:   {wetted_area:.1f} mm^2")
    print(f"  Shell volume (area * {WALL}mm): {shell_vol:.1f} mm^3 ({shell_vol / 1000:.2f} cm^3)")

    rudder_shell = rudder_solid

    # ── Hinge bore ──
    print(f"\nCutting hinge wire bore D={HINGE_BORE_D}mm at X=0, Z=0...")
    try:
        bore_len = Y_TIP + 10
        bore = Cylinder(
            HINGE_BORE_D / 2, bore_len,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        # Bore runs along Y axis (height) at X=0, Z=0 (hinge line)
        bore = bore.rotate(Axis.X, 90).translate(Vector(0, -2, 0))
        rudder_shell = rudder_shell - bore
        print("  Hinge bore OK.")
    except Exception as e:
        print(f"  Hinge bore failed: {e}")

    # ── Pushrod hole ──
    print(f"\nCutting pushrod hole D={PUSHROD_BORE_D}mm at X=10, Y={PUSHROD_Z}...")
    try:
        push = Cylinder(
            PUSHROD_BORE_D / 2, 12,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        # Pushrod hole goes through the root face (Y direction) at X=10, near root
        push = push.rotate(Axis.X, 90).translate(Vector(10, -2, 0))
        rudder_shell = rudder_shell - push
        print("  Pushrod hole OK.")
    except Exception as e:
        print(f"  Pushrod hole failed: {e}")

    # ── Metrics ──
    solid_vol = rudder_shell.volume
    mass_solid = solid_vol * LW_PLA_DENSITY
    mass_shell = shell_vol * LW_PLA_DENSITY
    bb = rudder_shell.bounding_box()

    print("\n" + "=" * 60)
    print("RUDDER v1 — FINAL METRICS")
    print("=" * 60)
    print(f"  Solid volume:  {solid_vol:.1f} mm^3  ({solid_vol / 1000:.2f} cm^3)")
    print(f"  Shell volume:  {shell_vol:.1f} mm^3  ({shell_vol / 1000:.2f} cm^3)")
    print(f"  Mass (solid):  {mass_solid:.2f} g")
    print(f"  Mass (shell, {WALL}mm wall): {mass_shell:.2f} g")
    print(f"  Target:        5.22 g shell (from DESIGN_CONSENSUS)")
    print(f"  Bounding box:")
    print(f"    X: {bb.min.X:.1f} to {bb.max.X:.1f} mm  ({bb.max.X - bb.min.X:.1f}mm)")
    print(f"    Y: {bb.min.Y:.1f} to {bb.max.Y:.1f} mm  ({bb.max.Y - bb.min.Y:.1f}mm)")
    print(f"    Z: {bb.min.Z:.1f} to {bb.max.Z:.1f} mm  ({bb.max.Z - bb.min.Z:.1f}mm)")

    # ── Export ──
    out_dir = os.path.join("cad", "components", "empennage", "Rudder")
    os.makedirs(out_dir, exist_ok=True)

    step_path = os.path.join(out_dir, "Rudder.step")
    stl_path = os.path.join(out_dir, "Rudder.stl")

    export_step(rudder_shell, step_path)
    print(f"\n  STEP exported: {step_path}")

    export_stl(rudder_shell, stl_path, tolerance=0.01, angular_tolerance=0.1)
    print(f"  STL exported:  {stl_path}")

    print("\nRudder v1 3D model complete.")


if __name__ == "__main__":
    main()
