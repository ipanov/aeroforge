"""
HStab Tip Caps — Built from EXACT planform spec.
NO boolean cuts (OCCT corrupts thin geometry).
Pre-clipped sections with 200-point resampled Polyline.

The tip follows the superellipse + cubic cap from hstab_geometry.py.
Tip starts at Y=207 (3mm overlap for CA joint).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from build123d import *
from src.cad.airfoils import blend_airfoils, scale_airfoil
from scripts.hstab_geometry import (
    chord_at, le_x, te_x, HALF_SPAN, X_HINGE,
    Y_CAP_START, Y_CAP_END, TE_TRUNC
)

N_AF = 120   # airfoil points per surface for source data
N_RING = 200  # resampled points per section (Polyline, smooth at this density)


def resample(pts, n):
    """Arc-length resample to exactly n points."""
    pts = np.array(pts, dtype=np.float64)
    diffs = np.diff(pts, axis=0)
    segs = np.sqrt((diffs ** 2).sum(axis=1))
    cum = np.concatenate([[0], np.cumsum(segs)])
    total = cum[-1]
    if total < 1e-9:
        return [(float(pts[0, 0]), float(pts[0, 1]))] * n
    targets = np.linspace(0, total, n)
    x = np.interp(targets, cum, pts[:, 0])
    z = np.interp(targets, cum, pts[:, 1])
    return [(float(x[i]), float(z[i])) for i in range(n)]


def get_clipped_section(y, x_lo, x_hi):
    """Get airfoil section clipped to [x_lo, x_hi], resampled to N_RING points.

    Returns closed loop or None. Uses real HT-13/HT-12 blend.
    """
    c = chord_at(abs(y))
    if c < 2:
        return None
    lx = le_x(abs(y))
    blend = min(abs(y) / HALF_SPAN, 1.0)
    af = blend_airfoils("ht13", "ht12", blend, N_AF)
    sc = scale_airfoil(af, c)

    le_idx = int(np.argmin(sc[:, 0]))
    upper = sc[:le_idx + 1][::-1]  # LE -> TE
    lower = sc[le_idx:]             # LE -> TE

    # Convert to absolute X
    upper_abs = np.column_stack([lx + upper[:, 0], upper[:, 1]])
    lower_abs = np.column_stack([lx + lower[:, 0], lower[:, 1]])

    def clip(pts, xlo, xhi):
        """Clip curve to [xlo, xhi] with interpolated crossings."""
        out = []
        for i in range(len(pts)):
            x, z = pts[i]
            if xlo <= x <= xhi:
                # Interpolate entry if needed
                if not out and i > 0 and pts[i - 1, 0] < xlo:
                    prev = pts[i - 1]
                    t = (xlo - prev[0]) / (x - prev[0])
                    out.append([xlo, prev[1] + t * (z - prev[1])])
                out.append([x, z])
            elif x > xhi and out:
                # Interpolate exit
                prev = pts[i - 1]
                if prev[0] < xhi:
                    t = (xhi - prev[0]) / (x - prev[0])
                    out.append([xhi, prev[1] + t * (z - prev[1])])
                break
            elif x < xlo and i + 1 < len(pts) and pts[i + 1, 0] >= xlo:
                # About to enter
                nxt = pts[i + 1]
                t = (xlo - x) / (nxt[0] - x)
                out.append([xlo, z + t * (nxt[1] - z)])
        return out

    uc = clip(upper_abs, x_lo, x_hi)
    lc = clip(lower_abs, x_lo, x_hi)

    if len(uc) < 2 or len(lc) < 2:
        return None

    # Build closed loop: upper + end-face + lower-reversed + start-face
    loop = uc + [lc[-1]] + list(reversed(lc[:-1]))
    loop.append(loop[0])

    # Resample to fixed N_RING points
    return resample(loop, N_RING)


def build_tip(ys, x_lo, x_hi, label):
    """Build a tip cap from pre-clipped, resampled sections."""
    sections = []
    for y in ys:
        pts = get_clipped_section(y, x_lo, x_hi)
        if pts:
            sections.append((y, pts))
            # Compute chord in clipped region
            xs = [p[0] for p in pts]
            clipped_chord = max(xs) - min(xs)
            print(f"  y={y:5.1f}: {N_RING}pts  chord_clipped={clipped_chord:.1f}mm")

    if len(sections) < 2:
        print(f"  {label}: not enough sections")
        return None

    print(f"  Lofting {len(sections)} sections ({label})...")
    with BuildPart() as bp:
        for y, pts in sections:
            plane = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
            with BuildSketch(plane):
                with BuildLine():
                    Polyline(*pts)
                make_face()
        loft()

    part = bp.part
    bb = part.bounding_box()
    print(f"  {label}: {part.volume:.1f}mm3  X=[{bb.min.X:.1f},{bb.max.X:.1f}] Y=[{bb.min.Y:.1f},{bb.max.Y:.1f}]")
    return part


def main():
    print("=" * 60)
    print("HStab Tip Caps — pre-clipped, 200-point Polyline, NO booleans")
    print("=" * 60)

    ys = [207, 208, 209, 209.5, 210, 210.5, 211, 211.5, 212]

    # Stab tip: LE to hinge (x_lo = LE, x_hi = 60)
    print("\n--- Stab Tip Cap ---")
    stab_tip = build_tip(ys, x_lo=0, x_hi=X_HINGE, label="Stab")

    # Elevator tip: hinge to TE (x_lo = 60, x_hi = TE)
    print("\n--- Elevator Tip Cap ---")
    # For elevator, x_hi varies by station (TE moves inboard)
    # Use a large x_hi and let the clip handle it
    elev_ys = [y for y in ys if te_x(y) - X_HINGE > 1.5]
    elev_tip = build_tip(elev_ys, x_lo=X_HINGE, x_hi=200, label="Elev")

    # Export
    print("\nExporting...")
    for part, folder, fname in [
        (stab_tip, "cad/components/empennage/HStab_Tip_Cap", "HStab_Tip_Cap"),
        (elev_tip, "cad/components/empennage/Elevator_Tip_Cap", "Elevator_Tip_Cap"),
    ]:
        if part is None:
            continue
        os.makedirs(folder, exist_ok=True)
        export_step(part, f"{folder}/{fname}.step")
        export_stl(part, f"{folder}/{fname}.stl", tolerance=0.005, angular_tolerance=0.1)
        print(f"  {fname}: {os.path.getsize(f'{folder}/{fname}.step') / 1024:.0f}KB")

    # Show and screenshot
    print("\nDisplaying...")
    from ocp_vscode import show, save_screenshot
    import time

    stab_main = import_step("cad/components/empennage/HStab_Left/HStab_Left_MainBody.step")
    stab_r = import_step("cad/components/empennage/HStab_Right/HStab_Right.step")
    elev_main = import_step("cad/components/empennage/Elevator_Left/Elevator_Left.step")
    elev_r = import_step("cad/components/empennage/Elevator_Right/Elevator_Right.step")
    spar = import_step("cad/components/empennage/HStab_Main_Spar/HStab_Main_Spar.step")
    wire = import_step("cad/components/empennage/Hinge_Wire/Hinge_Wire.step")

    parts = [stab_main, stab_r, elev_main, elev_r, spar, wire]
    names = ["Stab_L", "Stab_R", "Elev_L", "Elev_R", "Spar", "Wire"]
    colors = ["mediumorchid", "mediumorchid", "hotpink", "hotpink", "dimgray", "silver"]
    alphas = [0.4, 0.4, 0.4, 0.4, 1.0, 1.0]

    if stab_tip:
        parts.extend([stab_tip, stab_tip.mirror(Plane.XZ)])
        names.extend(["StabTip_L", "StabTip_R"])
        colors.extend(["mediumorchid", "mediumorchid"])
        alphas.extend([0.7, 0.7])
    if elev_tip:
        parts.extend([elev_tip, elev_tip.mirror(Plane.XZ)])
        names.extend(["ElevTip_L", "ElevTip_R"])
        colors.extend(["hotpink", "hotpink"])
        alphas.extend([0.7, 0.7])

    show(*parts, names=names, colors=colors, alphas=alphas)
    time.sleep(2)
    save_screenshot("exports/validation/tip_caps_final.png")
    print("Screenshot saved")


if __name__ == "__main__":
    main()
