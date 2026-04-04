"""
Elevator_Left 3D Model — v6 (Build123d)
=========================================
Elevator shell: hinge face (X=60.0mm) to TE, with convex bull-nose
extending forward of hinge line.

Lofted through HT-13 -> HT-12 blended airfoil sections.
Includes: hinge wire bore, pushrod hole.
Single-piece vase-mode print.

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_elevator_left_v6.py
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from build123d import *
from src.cad.airfoils import blend_airfoils

# ── v6 parameters ──
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
N_EXP = 2.3
REF_FRAC = 0.45
REF_X = ROOT_CHORD * REF_FRAC  # 51.75

X_HINGE = 60.0
HINGE_BORE_D = 0.6
PUSHROD_BORE_D = 1.6
PUSHROD_X = 70.0
PUSHROD_Z = 0.0
TE_TRUNC = 0.97

FIN_HALF = 3.5
FIN_GAP = 0.5
Y_ROOT = FIN_HALF + FIN_GAP  # 4.0
Y_TIP = 211.0   # last usable station (elev_chord ~5mm)

BULL_NOSE_ROOT = 2.5
BULL_NOSE_FADE_Y = 206.0

WALL = 0.40
Y_CAP_START = 210.0
Y_CAP_END = 214.0
LW_PLA_DENSITY = 0.75e-3  # g/mm^3


# ── Planform geometry ──

def _superellipse_chord(y):
    if abs(y) >= HALF_SPAN:
        return 0.0
    return ROOT_CHORD * (1.0 - (abs(y) / HALF_SPAN) ** N_EXP) ** (1.0 / N_EXP)

_c0 = _superellipse_chord(Y_CAP_START)
_dy = 0.001
_c0_slope = (_superellipse_chord(Y_CAP_START) - _superellipse_chord(Y_CAP_START - _dy)) / _dy
_CAP_A = _c0
_CAP_B = _c0_slope
_CAP_D = (_CAP_A + 2 * _CAP_B) / 32
_CAP_C = (-_CAP_B - 48 * _CAP_D) / 8

def chord_at(y):
    y = abs(y)
    if y <= Y_CAP_START:
        return _superellipse_chord(y)
    if y >= Y_CAP_END:
        return 0.0
    t = y - Y_CAP_START
    return max(0.0, _CAP_A + _CAP_B * t + _CAP_C * t**2 + _CAP_D * t**3)

def le_x(y):
    return REF_X - REF_FRAC * chord_at(abs(y))

def te_x(y):
    return le_x(y) + chord_at(abs(y)) * TE_TRUNC

def bull_nose_depth(y):
    if y >= BULL_NOSE_FADE_Y:
        return 0.0
    return BULL_NOSE_ROOT * max(0.0, 1.0 - y / BULL_NOSE_FADE_Y)


# ── Airfoil helpers ──

def get_blended_surfaces(y_span, n_pts=100):
    """Return (upper, lower) as arrays of (x_frac, y_frac), LE->TE order."""
    blend = min(abs(y_span) / HALF_SPAN, 1.0)
    airfoil = blend_airfoils("ht13", "ht12", blend, n_pts)
    le_idx = int(np.argmin(airfoil[:, 0]))
    upper = airfoil[:le_idx + 1][::-1].copy()
    lower = airfoil[le_idx:].copy()
    return upper, lower

def interp_surface(surface, x_frac):
    return float(np.interp(x_frac, surface[:, 0], surface[:, 1]))


N_HINGE_FACE = 8   # points on hinge face / bull-nose (FIXED count for all sections)
N_LOWER = 40        # points on lower surface hinge->TE
N_UPPER = 40        # points on upper surface TE->hinge
# Total points per section: N_HINGE_FACE+1 + N_LOWER + 1(TE) + N_UPPER + 1(close) = constant


def generate_section_2d(y_station):
    """Generate closed 2D profile points (x_abs, z_abs) for elevator at span y.

    Returns list of (x, z) tuples forming closed loop, or None.
    FIXED point count for all sections (critical for loft compatibility).
    """
    c = chord_at(y_station)
    if c < 1.0:
        return None

    lx = le_x(y_station)
    te = te_x(y_station)
    bn = bull_nose_depth(y_station)

    x_aft_abs = te
    elev_chord = x_aft_abs - X_HINGE
    if elev_chord < 1.0:
        return None

    hinge_frac = (X_HINGE - lx) / c
    x_aft_frac = min(1.0, (x_aft_abs - lx) / c)

    upper, lower = get_blended_surfaces(y_station, 120)

    z_upper_hinge = interp_surface(upper, hinge_frac) * c
    z_lower_hinge = interp_surface(lower, hinge_frac) * c

    points = []

    # 1. Hinge face / bull-nose: from upper-hinge around to lower-hinge
    #    Always N_HINGE_FACE+1 points regardless of bull-nose presence
    mid_z = (z_upper_hinge + z_lower_hinge) / 2.0
    r_z = abs(z_upper_hinge - z_lower_hinge) / 2.0

    for i in range(N_HINGE_FACE + 1):
        angle = math.pi / 2 - math.pi * i / N_HINGE_FACE
        if bn > 0.1:
            arc_x = X_HINGE - bn * math.cos(angle)
        else:
            arc_x = X_HINGE  # flat hinge face
        arc_z = mid_z + r_z * math.sin(angle)
        points.append((arc_x, arc_z))

    # 2. Lower surface: hinge -> TE
    for i in range(1, N_LOWER + 1):
        t = i / N_LOWER
        frac = hinge_frac + t * (x_aft_frac - hinge_frac)
        z = interp_surface(lower, frac) * c
        x = lx + frac * c
        points.append((x, z))

    # 3. TE closure: add upper TE point
    z_upper_te = interp_surface(upper, x_aft_frac) * c
    x_te = lx + x_aft_frac * c
    points.append((x_te, z_upper_te))

    # 4. Upper surface: TE -> hinge (skip the last point which equals first point)
    for i in range(1, N_UPPER):  # stop 1 early to avoid duplicating first point
        t = i / N_UPPER
        frac = x_aft_frac - t * (x_aft_frac - hinge_frac)
        z = interp_surface(upper, frac) * c
        x = lx + frac * c
        points.append((x, z))

    # Close back to first point
    points.append(points[0])

    return points


def main():
    print("=" * 60)
    print("Building Elevator_Left v6 3D model (Build123d)")
    print("=" * 60)

    # Stations — well-spaced for reliable loft (min ~20mm spacing in mid-span,
    # tighter near tip where shape changes rapidly)
    stations = [
        Y_ROOT,  # 4.0 — root face
        25, 50, 75, 100, 125, 150, 175,  # 25mm spacing main span
        200, BULL_NOSE_FADE_Y,            # 206 — bull-nose fade
        Y_CAP_START,                      # 210 — cap start
        Y_TIP,                            # 211 — elevator tip
    ]

    print(f"\nGenerating {len(stations)} airfoil sections...")
    valid_stations = []
    for y in stations:
        c = chord_at(y)
        te = te_x(y)
        elev_c = te - X_HINGE
        bn = bull_nose_depth(y)

        pts = generate_section_2d(y)
        if pts is not None and len(pts) > 10:
            valid_stations.append((y, pts))
            print(f"  y={y:6.1f}mm: chord={c:.1f}mm, elev_chord={elev_c:.1f}mm, bn={bn:.2f}mm  ({len(pts)} pts)")
        else:
            print(f"  y={y:6.1f}mm: chord={c:.1f}mm, elev_chord={elev_c:.1f}mm — SKIPPED")

    if len(valid_stations) < 3:
        print("ERROR: Not enough sections")
        return

    # ── Build using BuildPart + BuildSketch on offset planes ──
    print(f"\nBuilding solid via loft of {len(valid_stations)} sketches...")

    # Approach: use XZ plane offset along Y for each station.
    # In each sketch, draw the 2D profile in the local (X, Z) plane.
    # The sketch plane at each station maps local (u, v) to global (X, Z) at the correct Y.

    def clean_pts(pts, min_dist=0.02):
        """Remove consecutive near-duplicate points and ensure closure."""
        cleaned = [pts[0]]
        for p in pts[1:]:
            d = math.sqrt((p[0] - cleaned[-1][0])**2 + (p[1] - cleaned[-1][1])**2)
            if d > min_dist:
                cleaned.append(p)
        # Ensure closed
        d_close = math.sqrt((cleaned[-1][0] - cleaned[0][0])**2 + (cleaned[-1][1] - cleaned[0][1])**2)
        if d_close > min_dist:
            cleaned.append(cleaned[0])
        elif d_close > 1e-6:
            cleaned[-1] = cleaned[0]  # snap closure
        return cleaned

    with BuildPart() as builder:
        for idx, (y, pts_2d) in enumerate(valid_stations):
            pts_clean = clean_pts(pts_2d)
            if len(pts_clean) < 5:
                print(f"  WARNING: Section y={y} has too few points ({len(pts_clean)}), skipping")
                continue
            # Sketch plane: XZ plane offset along Y (normal = +Y)
            plane = Plane(
                origin=(0, y, 0),
                x_dir=(1, 0, 0),
                z_dir=(0, 1, 0),
            )
            with BuildSketch(plane) as sk:
                with BuildLine() as ln:
                    Polyline(*[(p[0], p[1]) for p in pts_clean])
                make_face()

        loft(ruled=True)

    elevator_solid = builder.part
    vol = elevator_solid.volume
    print(f"  Loft successful. Volume: {vol:.1f} mm^3 ({vol/1000:.2f} cm^3)")

    # ── Shell volume (analytical) ──
    # OCCT offset_3d fails on thin airfoil shapes with sharp TE.
    # For vase-mode print, shell_volume = surface_area * wall_thickness.
    # The STEP/STL represents the OML (outer mold line); slicer handles wall.
    print(f"\nComputing shell volume analytically (WALL={WALL}mm)...")
    outer_vol = elevator_solid.volume
    surface_area = elevator_solid.area
    # Subtract the root face area (open in vase mode)
    root_face = min(elevator_solid.faces(), key=lambda f: f.center().Y)
    root_area = root_face.area
    wetted_area = surface_area - root_area

    shell_vol = wetted_area * WALL
    print(f"  Outer volume:  {outer_vol:.1f} mm^3")
    print(f"  Total surface: {surface_area:.1f} mm^2")
    print(f"  Root face:     {root_area:.1f} mm^2")
    print(f"  Wetted area:   {wetted_area:.1f} mm^2")
    print(f"  Shell volume (area * {WALL}mm): {shell_vol:.1f} mm^3 ({shell_vol/1000:.2f} cm^3)")

    elevator_shell = elevator_solid  # Export the OML solid

    # ── Hinge bore ──
    print(f"\nCutting hinge wire bore D={HINGE_BORE_D}mm at X={X_HINGE}, Z=0...")
    try:
        bore_len = Y_TIP - Y_ROOT + 10
        bore = Cylinder(
            HINGE_BORE_D / 2, bore_len,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        bore = bore.rotate(Axis.X, 90).translate(Vector(X_HINGE, Y_ROOT - 2, 0))
        elevator_shell = elevator_shell - bore
        print("  Hinge bore OK.")
    except Exception as e:
        print(f"  Hinge bore failed: {e}")

    # ── Pushrod hole ──
    print(f"\nCutting pushrod hole D={PUSHROD_BORE_D}mm at X={PUSHROD_X}, Z={PUSHROD_Z}...")
    try:
        push = Cylinder(
            PUSHROD_BORE_D / 2, 12,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        push = push.rotate(Axis.X, 90).translate(Vector(PUSHROD_X, Y_ROOT - 2, PUSHROD_Z))
        elevator_shell = elevator_shell - push
        print("  Pushrod hole OK.")
    except Exception as e:
        print(f"  Pushrod hole failed: {e}")

    # ── Metrics ──
    solid_vol = elevator_shell.volume
    mass_solid = solid_vol * LW_PLA_DENSITY
    mass_shell = shell_vol * LW_PLA_DENSITY
    bb = elevator_shell.bounding_box()

    print("\n" + "=" * 60)
    print("ELEVATOR_LEFT v6 — FINAL METRICS")
    print("=" * 60)
    print(f"  Solid volume:  {solid_vol:.1f} mm^3  ({solid_vol / 1000:.2f} cm^3)")
    print(f"  Shell volume:  {shell_vol:.1f} mm^3  ({shell_vol / 1000:.2f} cm^3)")
    print(f"  Mass (solid):  {mass_solid:.2f} g")
    print(f"  Mass (shell, {WALL}mm wall): {mass_shell:.2f} g")
    print(f"  Target:        5.05 g (from DESIGN_CONSENSUS)")
    print(f"  Bounding box:")
    print(f"    X: {bb.min.X:.1f} to {bb.max.X:.1f} mm  ({bb.max.X - bb.min.X:.1f}mm)")
    print(f"    Y: {bb.min.Y:.1f} to {bb.max.Y:.1f} mm  ({bb.max.Y - bb.min.Y:.1f}mm)")
    print(f"    Z: {bb.min.Z:.1f} to {bb.max.Z:.1f} mm  ({bb.max.Z - bb.min.Z:.1f}mm)")

    # ── Export ──
    out_dir = os.path.join("cad", "components", "empennage", "Elevator_Left")
    os.makedirs(out_dir, exist_ok=True)

    step_path = os.path.join(out_dir, "Elevator_Left.step")
    stl_path = os.path.join(out_dir, "Elevator_Left.stl")

    export_step(elevator_shell, step_path)
    print(f"\n  STEP exported: {step_path}")

    export_stl(elevator_shell, stl_path, tolerance=0.01, angular_tolerance=0.1)
    print(f"  STL exported:  {stl_path}")

    print("\nElevator_Left v6 3D model complete.")


if __name__ == "__main__":
    main()
