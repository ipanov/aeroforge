"""
HStab_Assembly Drawing — v5 Consensus (v2 CORRECTED)
=====================================================
Full-span top view: both halves separated by 7mm VStab fin gap.
All rods shown as continuous lines through both halves and fin.
Root cross-section. VStab junction detail.
Uses shared geometry with C1-continuous tip cap.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from hstab_geometry import *
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# Assembly layout: full span horizontal, center at VStab fin CL
# Standard top view: left half extends LEFT, right half extends RIGHT.
# LE at top (forward), TE at bottom (aft).

CX = 430.0    # center X (fin CL) — centered in A1 drawing area
CY = 420.0    # chord reference Y (LE line) — upper part of sheet

def D_assy(cons_x, cons_y):
    """Convert consensus coords to assembly drawing coords.
    cons_y positive = left half (LEFT in drawing), negative = right half (RIGHT).
    cons_x = chordwise (LE at top = small X)."""
    return (CX - cons_y, CY - cons_x)


def draw_half(msp, sign):
    """Draw one half of the planform. sign=+1 for left, -1 for right.
    Uses ellipse arc for smooth tip closure."""
    import math as _math
    le_pts_c, te_pts_c = planform_points(n_pts=200)

    le_d = [D_assy(lx, sign * ly) for lx, ly in le_pts_c]
    te_d = [D_assy(tx, sign * ty) for tx, ty in te_pts_c]

    # Root chord (offset by fin half-width)
    root_le = D_assy(le_x(0), sign * FIN_HALF)
    root_te = D_assy(te_x(0), sign * FIN_HALF)
    msp.add_line(root_le, root_te, dxfattribs={"layer": "OUTLINE"})

    # LE and TE curves (only points beyond fin face)
    for i in range(len(le_d) - 1):
        _, ly1 = le_pts_c[i]
        _, ly2 = le_pts_c[i + 1]
        if ly1 >= FIN_HALF or ly2 >= FIN_HALF:
            msp.add_line(le_d[i], le_d[i + 1], dxfattribs={"layer": "OUTLINE"})
    for i in range(len(te_d) - 1):
        _, ty1 = te_pts_c[i]
        _, ty2 = te_pts_c[i + 1]
        if ty1 >= FIN_HALF or ty2 >= FIN_HALF:
            msp.add_line(te_d[i], te_d[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Connect root chord to LE/TE at fin face
    le_at_fin = D_assy(le_x(FIN_HALF), sign * FIN_HALF)
    te_at_fin = D_assy(te_x(FIN_HALF), sign * FIN_HALF)
    msp.add_line(root_le, le_at_fin, dxfattribs={"layer": "OUTLINE"})
    msp.add_line(root_te, te_at_fin, dxfattribs={"layer": "OUTLINE"})

    # TIP ARC: semi-elliptical closure as POLYLINE (matplotlib doesn't render ELLIPSE)
    arc_pts = tip_arc_points(n_pts=50)
    arc_d = [D_assy(cx, sign * cy) for cx, cy in arc_pts]
    for i in range(len(arc_d) - 1):
        msp.add_line(arc_d[i], arc_d[i + 1], dxfattribs={"layer": "OUTLINE"})


def main():
    doc = setup_drawing(
        title="HStab_Assembly",
        subtitle="Full H-Stab assembly: both halves + elevator + hinge. 430mm span. Superellipse n=2.3.",
        material="See component drawings for individual materials",
        mass="33.65g total", scale="1:1", sheet_size="A1", status="FOR APPROVAL", revision="v5",
    )
    msp = doc.modelspace()

    # ═══════════════════════════════════════════════════════════════════════
    # TOP VIEW — FULL ASSEMBLY
    # ═══════════════════════════════════════════════════════════════════════
    msp.add_text("TOP VIEW — FULL ASSEMBLY (1:1)", height=5.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((CX - 60, CY + 25))

    # FWD arrow
    ax, ay = CX - HALF_SPAN - 25, CY - 50
    msp.add_line((ax, ay), (ax, ay + 25), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ax, ay + 25), (ax - 2.5, ay + 21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ax, ay + 25), (ax + 2.5, ay + 21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("FWD", height=3.5, dxfattribs={"layer": "ORIENTATION"}).set_placement(
        (ax - 6, ay + 27))

    # ── Draw both halves ──
    draw_half(msp, +1)  # left half (up)
    draw_half(msp, -1)  # right half (down)

    # ── VStab fin (central gap) ──
    # Fin is 7mm wide, shown as a rectangle at the root
    fin_le = D_assy(le_x(0), 0)
    fin_te = D_assy(te_x(0), 0)
    # Fin boundaries
    fin_top = D_assy(le_x(0), +FIN_HALF)
    fin_bot = D_assy(le_x(0), -FIN_HALF)
    fin_top_te = D_assy(te_x(0), +FIN_HALF)
    fin_bot_te = D_assy(te_x(0), -FIN_HALF)

    # Fin outline (dashed, represents the VStab fin cross-section)
    msp.add_lwpolyline([fin_top, fin_top_te, fin_bot_te, fin_bot, fin_top],
                       dxfattribs={"layer": "HIDDEN"})
    msp.add_text("VStab FIN\n7mm thick", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (fin_le[0] - 20, fin_le[1] - 3))

    # ── Centerline (fin CL) ──
    msp.add_line(D_assy(le_x(0) - 10, 0), D_assy(te_x(0) + 10, 0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("FIN CL", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(te_x(0) + 12, 0))

    # ── Spar lines (continuous through both halves + fin) ──
    spar_info = [
        (X_MAIN_SPAR, Y_MAIN_END, "SPAR",
         "MAIN SPAR  3mm CF tube  X=35.0  372mm total"),
        (X_REAR_SPAR, Y_REAR_END, "SPAR",
         "REAR SPAR  1.5mm CF rod  X=69.0  420mm total"),
        (X_HINGE, Y_HINGE_END, "CENTERLINE",
         "HINGE WIRE  0.5mm music wire  X=74.75  440mm total"),
    ]
    for x_rod, y_end, layer, label in spar_info:
        # Left half: from fin face to termination
        msp.add_line(D_assy(x_rod, +FIN_HALF), D_assy(x_rod, +y_end),
                     dxfattribs={"layer": layer})
        # Through fin (dashed)
        msp.add_line(D_assy(x_rod, -FIN_HALF), D_assy(x_rod, +FIN_HALF),
                     dxfattribs={"layer": "HIDDEN"})
        # Right half
        msp.add_line(D_assy(x_rod, -FIN_HALF), D_assy(x_rod, -y_end),
                     dxfattribs={"layer": layer})
        # Dashed beyond termination (both sides)
        msp.add_line(D_assy(x_rod, +y_end), D_assy(x_rod, +Y_CAP_END),
                     dxfattribs={"layer": "HIDDEN"})
        msp.add_line(D_assy(x_rod, -y_end), D_assy(x_rod, -Y_CAP_END),
                     dxfattribs={"layer": "HIDDEN"})

        # Label (at top, left half)
        msp.add_text(label, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(
            (D_assy(x_rod, Y_CAP_END + 5)[0], D_assy(x_rod, Y_CAP_END + 5)[1] + 2))

    # Stiffener (elevator zone, does NOT pass through fin)
    for sign in [+1, -1]:
        msp.add_line(D_assy(X_STIFF, sign * (FIN_HALF + FIN_GAP)),
                     D_assy(X_STIFF, sign * Y_STIFF_END),
                     dxfattribs={"layer": "SECTION"})

    msp.add_text("STIFFENER  1mm CF  X=92.0  (2×150mm, does NOT pass through fin)",
                 height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(
        (D_assy(X_STIFF, Y_CAP_END + 5)[0], D_assy(X_STIFF, Y_CAP_END + 5)[1] + 2))

    # ── Termination annotations (left half) ──
    for y_end, label in [
        (Y_STIFF_END, f"stiffener ends y={Y_STIFF_END:.0f}"),
        (Y_MAIN_END,  f"spar tube ends y={Y_MAIN_END:.0f}"),
        (Y_HINGE_END, f"hinge wire ends y={Y_HINGE_END:.0f}"),
        (Y_REAR_END,  f"rear spar ends y={Y_REAR_END:.0f}"),
    ]:
        pt = D_assy(ROOT_CHORD + 5, y_end)
        msp.add_text(label, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(pt)

    # ── Edge labels ──
    msp.add_text("LE", height=4.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(-8, 80))
    msp.add_text("TE", height=4.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(ROOT_CHORD * TE_TRUNC + 5, 80))
    msp.add_text("LEFT TIP", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(REF_X, Y_CAP_END + 3))
    msp.add_text("RIGHT TIP", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(REF_X, -(Y_CAP_END + 3)))

    # ── Dimensions (all computed via D_assy for consistency) ──
    # Full span: left tip to right tip (horizontal)
    lt = D_assy(0, Y_CAP_END)       # left tip LE
    rt = D_assy(0, -Y_CAP_END)      # right tip LE
    msp.add_aligned_dim(
        p1=(lt[0], lt[1] + 15), p2=(rt[0], lt[1] + 15),
        distance=10, dimstyle="AEROFORGE",
    ).render()

    # Half span: fin face to left tip (horizontal)
    fin_face = D_assy(0, FIN_HALF)
    msp.add_aligned_dim(
        p1=(fin_face[0], fin_face[1] + 8), p2=(lt[0], lt[1] + 8),
        distance=5, dimstyle="AEROFORGE",
    ).render()

    # Root chord (vertical, alongside left tip)
    root_le = D_assy(0, -(Y_CAP_END + 10))
    root_te = D_assy(ROOT_CHORD * TE_TRUNC, -(Y_CAP_END + 10))
    msp.add_aligned_dim(
        p1=root_le, p2=root_te,
        distance=8, dimstyle="AEROFORGE",
    ).render()

    # Fin width (horizontal, below TE)
    fin_l = D_assy(ROOT_CHORD * TE_TRUNC + 10, FIN_HALF)
    fin_r = D_assy(ROOT_CHORD * TE_TRUNC + 10, -FIN_HALF)
    msp.add_aligned_dim(
        p1=fin_l, p2=fin_r,
        distance=5, dimstyle="AEROFORGE",
    ).render()

    # ═══════════════════════════════════════════════════════════════════════
    # ROOT CROSS-SECTION
    # ═══════════════════════════════════════════════════════════════════════
    sc_x = 50.0
    sc_y = CY - HALF_SPAN - 100

    msp.add_text("ROOT CROSS-SECTION (y=0, HT-13 6.5%, 1:1)", height=4.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((sc_x, sc_y + 14))

    c = ROOT_CHORD; tr = T_ROOT
    for i in range(80):
        xc1 = TE_TRUNC * i / 80; xc2 = TE_TRUNC * (i + 1) / 80
        y1 = naca4_yt(xc1, tr) * c; y2 = naca4_yt(xc2, tr) * c
        msp.add_line((sc_x + xc1*c, sc_y + y1), (sc_x + xc2*c, sc_y + y2),
                     dxfattribs={"layer": "OUTLINE"})
        msp.add_line((sc_x + xc1*c, sc_y - y1), (sc_x + xc2*c, sc_y - y2),
                     dxfattribs={"layer": "OUTLINE"})

    yt0 = naca4_yt(0.005, tr) * c
    msp.add_line((sc_x, sc_y - yt0), (sc_x, sc_y + yt0), dxfattribs={"layer": "OUTLINE"})
    yte = naca4_yt(TE_TRUNC, tr) * c
    msp.add_line((sc_x + TE_TRUNC*c, sc_y - yte), (sc_x + TE_TRUNC*c, sc_y + yte),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_line((sc_x - 3, sc_y), (sc_x + TE_TRUNC*c + 3, sc_y),
                 dxfattribs={"layer": "CENTERLINE"})

    # Bore holes + labels
    for x_rod, dia, label, layer in [
        (X_MAIN_SPAR, D_MAIN, f"Ø{D_MAIN} (3mm tube)", "SPAR"),
        (X_REAR_SPAR, D_REAR, f"Ø{D_REAR} (1.5mm rod)", "SPAR"),
        (X_HINGE, D_HINGE, f"Ø{D_HINGE} (wire+sleeve)", "CENTERLINE"),
    ]:
        frac = x_rod / c
        msp.add_circle((sc_x + x_rod, sc_y), dia / 2, dxfattribs={"layer": layer})
        yth = naca4_yt(frac, tr) * c
        msp.add_text(label, height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
            (sc_x + x_rod - 5, sc_y + yth + 2))

    # Hinge divider
    hf = X_HINGE / c
    yth = naca4_yt(hf, tr) * c
    msp.add_line((sc_x + X_HINGE, sc_y - yth), (sc_x + X_HINGE, sc_y + yth),
                 dxfattribs={"layer": "CENTERLINE"})

    # Zone labels
    msp.add_text("STAB", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (sc_x + X_HINGE / 2 - 5, sc_y - 2))
    msp.add_text("ELEV", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (sc_x + X_HINGE + 8, sc_y - 2))

    # Chord dimension
    msp.add_linear_dim(
        base=(sc_x + c / 2, sc_y - 14),
        p1=(sc_x, sc_y), p2=(sc_x + TE_TRUNC * c, sc_y),
        dimstyle="AEROFORGE",
    ).render()

    # ═══════════════════════════════════════════════════════════════════════
    # VSTAB JUNCTION DETAIL
    # ═══════════════════════════════════════════════════════════════════════
    jx = sc_x + ROOT_CHORD + 60
    jy = sc_y

    msp.add_text("VSTAB JUNCTION DETAIL (schematic)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((jx, jy + 30))

    # Fin rectangle
    msp.add_lwpolyline([
        (jx, jy - 25), (jx + 7, jy - 25), (jx + 7, jy + 25), (jx, jy + 25), (jx, jy - 25)
    ], dxfattribs={"layer": "OUTLINE"})
    msp.add_text("VStab fin\n7mm", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (jx + 8, jy + 1))

    # HStab root
    msp.add_lwpolyline([
        (jx + 7, jy - 3.75), (jx + 40, jy - 3.75),
        (jx + 40, jy + 3.75), (jx + 7, jy + 3.75), (jx + 7, jy - 3.75)
    ], dxfattribs={"layer": "OUTLINE"})
    msp.add_text("HStab root", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (jx + 42, jy))

    # Fillet arcs
    fr = 9.2
    msp.add_arc(center=(jx + 7 + fr, jy + 3.75 + fr), radius=fr,
                start_angle=180, end_angle=270, dxfattribs={"layer": "SECTION"})
    msp.add_arc(center=(jx + 7 + fr, jy - 3.75 - fr), radius=fr,
                start_angle=90, end_angle=180, dxfattribs={"layer": "SECTION"})
    msp.add_text(f"R={fr}mm fillet\n(quartic, C2)", height=2.0,
                 dxfattribs={"layer": "SECTION"}).set_placement((jx + 7 + fr + 2, jy + 6))
    msp.add_text("Dovetail + CA", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((jx - 5, jy - 22))

    # ═══════════════════════════════════════════════════════════════════════
    # NOTES
    # ═══════════════════════════════════════════════════════════════════════
    notes = [
        "NOTES:",
        "1. Full span: 430mm (214mm tip-to-tip each half + 7mm fin). All dims mm.",
        "2. Superellipse n=2.3 planform with C1-continuous tip cap y=210→214.",
        "3. 45%-chord ref X=51.75 is straight. All 4 rods straight + perpendicular to fin CL.",
        "4. Main spar: 3mm CF tube, 372mm. Through left stab + fin + right stab.",
        "   Rear spar: 1.5mm CF rod, 420mm. Hinge wire: 0.5mm music wire, 440mm.",
        "5. Stiffener: 2×150mm (does NOT pass through fin). One in each elevator half.",
        "6. VStab junction: 9.2mm fillet, quartic, C2. Dovetail interlock + CA.",
        "7. Elevator bridge joiner (CF-PLA U-channel, ~0.6g) TBD in integration.",
        "8. Target mass: 33.65g. Hard limit: 35g.",
        "9. Assembly sequence: see DESIGN_CONSENSUS.md.",
    ]
    nx = sc_x
    ny = sc_y - 40
    for i, n in enumerate(notes):
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
            (nx, ny - i * 4.8))

    save_dxf_and_png(doc, "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf",
                     dpi=300)
    print("HStab_Assembly done.")


if __name__ == "__main__":
    main()
