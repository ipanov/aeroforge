"""
H-Stab Assembly 3D Sketch + Orthographic Drawing
==================================================
Builds lightweight 3D outlines of ALL H-Stab assembly components using Build123d,
projects to top/front/right orthographic views, and exports DXF + PNG.

Source: DESIGN_CONSENSUS.md v5

Components built:
  Shells: HStab_Left, HStab_Right, Elevator_Left, Elevator_Right
  Rods:   Main spar, Rear spar, Hinge wire, Stiffeners (2x)
  VStab:  Thin box placeholder at center
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from build123d import (
    Compound,
    Cylinder,
    Box,
    Axis,
    Location,
    Plane,
    Vector,
    Polyline,
    Spline,
    Wire,
    Face,
    Part,
    Solid,
    loft,
    make_face,
    Edge,
)

from src.cad.drawing.projector import project_standard_views, compute_2d_bounds
from src.cad.drawing.layout import calculate_layout
from src.cad.drawing.exporter import export_drawing


# ═══════════════════════════════════════════════════════════════════════════════
# PARAMETERS — from DESIGN_CONSENSUS.md v5
# ═══════════════════════════════════════════════════════════════════════════════

HALF_SPAN = 215.0
ROOT_CHORD = 115.0
N = 2.3  # superellipse exponent
ALIGN_X = 51.75  # 45% chord alignment point

# Rod positions (constant X from root LE)
MAIN_SPAR_X = 35.0
REAR_SPAR_X = 69.0
HINGE_X = 74.75
STIFFENER_X = 92.0

# Rod terminations (per half-span)
MAIN_SPAR_TERM = 186.0
REAR_SPAR_TERM = 210.0
HINGE_WIRE_TERM = 203.0
STIFFENER_TERM = 150.0

# Rod diameters
MAIN_SPAR_OD = 3.0
REAR_SPAR_DIA = 1.5
HINGE_WIRE_DIA = 0.5
STIFFENER_DIA = 1.0

# Airfoil
TC_ROOT = 0.065  # HT-13
TC_TIP = 0.051   # HT-12

# Other
VSTAB_FIN_THICK = 7.0
ROOT_GAP = 8.0
HINGE_GAP = 0.3
TE_TRUNC = 0.97

# Output
OUTPUT_DIR = "cad/assemblies/empennage/HStab_Assembly"
DXF_PATH = os.path.join(OUTPUT_DIR, "HStab_Assembly_drawing.dxf")
PNG_PATH = os.path.join(OUTPUT_DIR, "HStab_Assembly_drawing.png")


# ═══════════════════════════════════════════════════════════════════════════════
# PLANFORM GEOMETRY
# ═══════════════════════════════════════════════════════════════════════════════

def chord(y: float) -> float:
    """Superellipse chord at span station y (mm)."""
    eta = abs(y) / HALF_SPAN
    if eta >= 1.0:
        return 0.0
    return ROOT_CHORD * (1.0 - eta**N) ** (1.0 / N)


def x_le(y: float) -> float:
    """Leading edge X position at span station y."""
    return ALIGN_X - 0.45 * chord(y)


def x_te(y: float) -> float:
    """Trailing edge X position at span station y."""
    return ALIGN_X + 0.55 * chord(y)


# ═══════════════════════════════════════════════════════════════════════════════
# AIRFOIL SECTION GENERATION (NACA 4-digit thickness distribution)
# ═══════════════════════════════════════════════════════════════════════════════

def naca_thickness(x_frac: float) -> float:
    """NACA 4-digit thickness distribution (half-thickness / chord).

    Returns t/2 as fraction of chord at given x/c position.
    """
    t = x_frac  # local variable
    # Standard NACA formula
    return 5.0 * (
        0.2969 * math.sqrt(t)
        - 0.1260 * t
        - 0.3516 * t**2
        + 0.2843 * t**3
        - 0.1015 * t**4
    )


def airfoil_section_points(y_station: float, x_start: float, x_end: float,
                           n_pts: int = 30) -> list[tuple[float, float, float]]:
    """Generate airfoil cross-section points in the XZ plane at given Y.

    Returns a closed polygon of (X, Y, Z) points for the airfoil shape
    between x_start and x_end.

    The airfoil uses NACA thickness distribution scaled by the local t/c ratio
    (linearly blended from TC_ROOT at y=0 to TC_TIP at y=HALF_SPAN).
    """
    c = chord(y_station)
    if c <= 0.01:
        return []

    le = x_le(y_station)

    # Local t/c ratio (linear blend)
    eta = min(abs(y_station) / HALF_SPAN, 1.0)
    tc_local = TC_ROOT * (1.0 - eta) + TC_TIP * eta

    # Clamp x_start and x_end to be within [le, le+c]
    x_start = max(x_start, le)
    x_end = min(x_end, le + c)

    if x_end <= x_start:
        return []

    # Generate upper surface points (LE to TE)
    upper_pts = []
    for i in range(n_pts + 1):
        x = x_start + (x_end - x_start) * i / n_pts
        x_frac = (x - le) / c  # fraction along chord
        x_frac = max(0.0, min(1.0, x_frac))
        half_t = naca_thickness(x_frac) * tc_local / 0.12 * c  # scale to local t/c and chord
        upper_pts.append((x, y_station, half_t))

    # Generate lower surface points (TE to LE, reversed)
    lower_pts = []
    for i in range(n_pts, -1, -1):
        x = x_start + (x_end - x_start) * i / n_pts
        x_frac = (x - le) / c
        x_frac = max(0.0, min(1.0, x_frac))
        half_t = naca_thickness(x_frac) * tc_local / 0.12 * c
        lower_pts.append((x, y_station, -half_t))

    # Close the polygon: upper (LE->TE) + lower (TE->LE) back to start
    # Remove duplicate points at transitions
    all_pts = upper_pts + lower_pts[1:]  # skip first of lower (same as last of upper)
    # Close back to the first point
    if all_pts[0] != all_pts[-1]:
        all_pts.append(all_pts[0])

    return all_pts


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def build_shell_loft(y_stations: list[float], x_start_fn, x_end_fn,
                     label: str = "shell") -> Part | None:
    """Build a lofted shell between airfoil sections at given span stations.

    x_start_fn(y) and x_end_fn(y) return the chordwise X limits at each station.
    """
    faces = []
    for y in y_stations:
        pts = airfoil_section_points(y, x_start_fn(y), x_end_fn(y), n_pts=20)
        if len(pts) < 4:
            print(f"  [SKIP] {label} at y={y:.1f}: too few points ({len(pts)})")
            continue

        try:
            # Create a wire from the polygon points
            wire = Wire.make_polygon([Vector(*p) for p in pts])
            face = make_face(wire)
            faces.append(face)
        except Exception as e:
            print(f"  [SKIP] {label} at y={y:.1f}: wire/face failed: {e}")
            continue

    if len(faces) < 2:
        print(f"  [FAIL] {label}: need at least 2 sections, got {len(faces)}")
        return None

    try:
        solid = loft(faces, ruled=True)
        print(f"  [OK]   {label}: lofted {len(faces)} sections")
        return solid
    except Exception as e:
        print(f"  [FAIL] {label}: loft failed: {e}")
        # Fallback: just extrude the first section
        try:
            from build123d import extrude
            length = abs(y_stations[-1] - y_stations[0])
            direction = Vector(0, 1 if y_stations[-1] > y_stations[0] else -1, 0)
            solid = extrude(faces[0], amount=length, dir=direction)
            print(f"  [OK]   {label}: fallback extrude, length={length:.1f}")
            return solid
        except Exception as e2:
            print(f"  [FAIL] {label}: fallback extrude also failed: {e2}")
            return None


def build_rod(x_pos: float, half_length: float, diameter: float,
              label: str = "rod") -> Part | None:
    """Build a cylindrical rod centered at origin, aligned along Y axis."""
    try:
        rod = Cylinder(
            radius=diameter / 2.0,
            height=half_length * 2.0,
            align=None,
        )
        # Cylinder defaults to Z-axis. Rotate to Y-axis.
        rod = rod.rotate(Axis.X, 90)
        # Translate to correct X position
        rod = rod.moved(Location((x_pos, 0, 0)))
        print(f"  [OK]   {label}: d={diameter}mm, span=+/-{half_length}mm at X={x_pos}")
        return rod
    except Exception as e:
        print(f"  [FAIL] {label}: {e}")
        return None


def build_vstab_placeholder() -> Part | None:
    """Build a thin box representing the VStab fin at the center."""
    try:
        # Simple box: full chord width x 7mm thick x some height
        # Height ~ max airfoil thickness at root
        height = ROOT_CHORD * TC_ROOT  # ~7.5mm
        box = Box(ROOT_CHORD, VSTAB_FIN_THICK, height)
        # Position: centered at Y=0, X from 0 to ROOT_CHORD
        box = box.moved(Location((ROOT_CHORD / 2, 0, 0)))
        print(f"  [OK]   VStab fin placeholder: {ROOT_CHORD}x{VSTAB_FIN_THICK}x{height:.1f}mm")
        return box
    except Exception as e:
        print(f"  [FAIL] VStab placeholder: {e}")
        return None


def build_assembly() -> Compound:
    """Build the complete H-Stab assembly as a Compound of all components."""
    parts = []

    print("\n=== Building H-Stab Assembly Components ===\n")

    # --- Span stations for lofting ---
    # Use 5 stations per half for shells
    left_stations = [4.0, 50.0, 100.0, 150.0, 200.0]  # y > 0 = left
    right_stations = [-4.0, -50.0, -100.0, -150.0, -200.0]  # y < 0 = right

    # --- Stab shells (LE to hinge line) ---
    def stab_x_start(y):
        return x_le(y)

    def stab_x_end(y):
        return min(HINGE_X, x_te(y))

    p = build_shell_loft(left_stations, stab_x_start, stab_x_end, "HStab_Left")
    if p:
        parts.append(p)

    p = build_shell_loft(right_stations, stab_x_start, stab_x_end, "HStab_Right")
    if p:
        parts.append(p)

    # --- Elevator shells (hinge + gap to TE truncation) ---
    def elev_x_start(y):
        return HINGE_X + HINGE_GAP

    def elev_x_end(y):
        c = chord(y)
        le = x_le(y)
        return le + TE_TRUNC * c

    # Elevator stations: only where elevator chord > 0
    elev_left = [s for s in left_stations if elev_x_end(s) > elev_x_start(s)]
    elev_right = [s for s in right_stations if elev_x_end(s) > elev_x_start(s)]

    p = build_shell_loft(elev_left, elev_x_start, elev_x_end, "Elevator_Left")
    if p:
        parts.append(p)

    p = build_shell_loft(elev_right, elev_x_start, elev_x_end, "Elevator_Right")
    if p:
        parts.append(p)

    # --- Rods ---
    p = build_rod(MAIN_SPAR_X, MAIN_SPAR_TERM, MAIN_SPAR_OD, "Main_Spar")
    if p:
        parts.append(p)

    p = build_rod(REAR_SPAR_X, REAR_SPAR_TERM, REAR_SPAR_DIA, "Rear_Spar")
    if p:
        parts.append(p)

    p = build_rod(HINGE_X, HINGE_WIRE_TERM, HINGE_WIRE_DIA, "Hinge_Wire")
    if p:
        parts.append(p)

    # Stiffeners: two separate rods, one per side (y=4..150mm each)
    # Left stiffener
    try:
        stiff_len = STIFFENER_TERM - 4.0  # 146mm
        stiff = Cylinder(radius=STIFFENER_DIA / 2.0, height=stiff_len, align=None)
        stiff = stiff.rotate(Axis.X, 90)
        stiff = stiff.moved(Location((STIFFENER_X, 4.0 + stiff_len / 2.0, 0)))
        parts.append(stiff)
        print(f"  [OK]   Stiffener_Left: d={STIFFENER_DIA}mm, y=4..{STIFFENER_TERM}mm")
    except Exception as e:
        print(f"  [FAIL] Stiffener_Left: {e}")

    # Right stiffener
    try:
        stiff = Cylinder(radius=STIFFENER_DIA / 2.0, height=stiff_len, align=None)
        stiff = stiff.rotate(Axis.X, 90)
        stiff = stiff.moved(Location((STIFFENER_X, -(4.0 + stiff_len / 2.0), 0)))
        parts.append(stiff)
        print(f"  [OK]   Stiffener_Right: d={STIFFENER_DIA}mm, y=-4..{-STIFFENER_TERM}mm")
    except Exception as e:
        print(f"  [FAIL] Stiffener_Right: {e}")

    # --- VStab fin placeholder ---
    p = build_vstab_placeholder()
    if p:
        parts.append(p)

    print(f"\n=== Assembly: {len(parts)} components built ===\n")

    if not parts:
        raise RuntimeError("No components were built successfully!")

    return Compound(children=parts)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("Building H-Stab Assembly 3D sketch...")

    assembly = build_assembly()

    # Project to standard views
    print("Projecting to orthographic views...")
    views = project_standard_views(assembly)

    # Count edges per view
    for vname in ["top", "front", "right"]:
        nvis = len(views[vname]["visible"])
        nhid = len(views[vname]["hidden"])
        print(f"  {vname:6s}: {nvis} visible + {nhid} hidden edges")

    # Compute bounds for each view
    view_bounds = {}
    for vname in ["top", "front", "right"]:
        all_edges = views[vname]["visible"] + views[vname]["hidden"]
        if all_edges:
            view_bounds[vname] = compute_2d_bounds(all_edges)
            b = view_bounds[vname]
            w = b[2] - b[0]
            h = b[3] - b[1]
            print(f"  {vname:6s} bounds: {w:.1f} x {h:.1f} mm")
        else:
            print(f"  [WARN] {vname}: no edges!")
            # Provide a dummy bound so layout doesn't crash
            view_bounds[vname] = (0, 0, 1, 1)

    # Calculate layout
    print("\nCalculating A3 layout...")
    layout = calculate_layout(view_bounds, sheet_size="A3")
    print(f"  Scale: {layout['scale']:.4f}")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Export DXF
    print(f"\nExporting DXF to: {DXF_PATH}")
    export_drawing(views, layout, DXF_PATH)
    print("  DXF written.")

    # Export PNG preview using ezdxf
    try:
        import ezdxf
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing import matplotlib as mpl_backend

        doc = ezdxf.readfile(DXF_PATH)
        msp = doc.modelspace()

        fig = mpl_backend.qsave(
            doc.modelspace(),
            DXF_PATH.replace(".dxf", ".png"),
            size_inches=(16, 11),
            dpi=150,
            bg="#FFFFFF",
        )
        print(f"  PNG written: {PNG_PATH}")
    except Exception as e:
        print(f"  [WARN] PNG export failed: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
