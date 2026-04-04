"""
HStab_Assembly Drawing — v6 Consensus
=======================================
Full-span top view. Single spar at X=34.5, hinge at X=60.0.
No rear spar, no stiffener. Concealed saddle hinge.
Standard top view: left=left, right=right (CX - cons_y).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from hstab_geometry import *
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

CX = 430.0
CY = 420.0

def D_assy(cons_x, cons_y):
    """Standard top view: left half LEFT, right half RIGHT."""
    return (CX - cons_y, CY - cons_x)


def draw_half(msp, sign):
    le_pts_c, te_pts_c = planform_points(n_pts=200)
    le_d = [D_assy(lx, sign * ly) for lx, ly in le_pts_c]
    te_d = [D_assy(tx, sign * ty) for tx, ty in te_pts_c]

    root_le = D_assy(le_x(0), sign * FIN_HALF)
    root_te = D_assy(te_x(0), sign * FIN_HALF)
    msp.add_line(root_le, root_te, dxfattribs={"layer": "OUTLINE"})

    for i in range(len(le_d) - 1):
        _, ly1 = le_pts_c[i]; _, ly2 = le_pts_c[i + 1]
        if ly1 >= FIN_HALF or ly2 >= FIN_HALF:
            msp.add_line(le_d[i], le_d[i + 1], dxfattribs={"layer": "OUTLINE"})
    for i in range(len(te_d) - 1):
        _, ty1 = te_pts_c[i]; _, ty2 = te_pts_c[i + 1]
        if ty1 >= FIN_HALF or ty2 >= FIN_HALF:
            msp.add_line(te_d[i], te_d[i + 1], dxfattribs={"layer": "OUTLINE"})

    le_at_fin = D_assy(le_x(FIN_HALF), sign * FIN_HALF)
    te_at_fin = D_assy(te_x(FIN_HALF), sign * FIN_HALF)
    msp.add_line(root_le, le_at_fin, dxfattribs={"layer": "OUTLINE"})
    msp.add_line(root_te, te_at_fin, dxfattribs={"layer": "OUTLINE"})

    arc_pts = tip_arc_points(n_pts=50)
    arc_d = [D_assy(cx, sign * cy) for cx, cy in arc_pts]
    for i in range(len(arc_d) - 1):
        msp.add_line(arc_d[i], arc_d[i + 1], dxfattribs={"layer": "OUTLINE"})


def main():
    doc = setup_drawing(
        title="HStab_Assembly",
        subtitle="Full H-Stab integration candidate: single spar, concealed hinge@X=60, 45% elevator. 430mm span.",
        material="See component drawings for individual materials",
        mass="31-33g candidate", scale="1:1", sheet_size="A1", status="FOR APPROVAL", revision="v6a",
    )
    msp = doc.modelspace()

    msp.add_text("TOP VIEW — FULL ASSEMBLY (1:1)", height=5.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((CX - 60, CY + 25))

    # FWD arrow
    ax, ay = CX - HALF_SPAN - 25, CY - 50
    msp.add_line((ax, ay), (ax, ay + 25), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ax, ay+25), (ax-2.5, ay+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ax, ay+25), (ax+2.5, ay+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("FWD", height=3.5, dxfattribs={"layer": "ORIENTATION"}).set_placement((ax-6, ay+27))

    draw_half(msp, +1)
    draw_half(msp, -1)

    # VStab fin
    fin_top = D_assy(le_x(0), +FIN_HALF)
    fin_bot = D_assy(le_x(0), -FIN_HALF)
    fin_top_te = D_assy(te_x(0), +FIN_HALF)
    fin_bot_te = D_assy(te_x(0), -FIN_HALF)
    msp.add_lwpolyline([fin_top, fin_top_te, fin_bot_te, fin_bot, fin_top],
                       dxfattribs={"layer": "HIDDEN"})
    fin_le = D_assy(le_x(0), 0)
    msp.add_text("VStab FIN\n7mm thick", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((fin_le[0] - 20, fin_le[1] - 3))

    # Centerline
    msp.add_line(D_assy(le_x(0) - 10, 0), D_assy(te_x(0) + 10, 0),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("FIN CL", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(te_x(0) + 12, 0))

    # Main spar (only spar in v6)
    for sign_s in [+1, -1]:
        msp.add_line(D_assy(X_MAIN_SPAR, sign_s * FIN_HALF),
                     D_assy(X_MAIN_SPAR, sign_s * Y_MAIN_END),
                     dxfattribs={"layer": "SPAR"})
        msp.add_line(D_assy(X_MAIN_SPAR, sign_s * Y_MAIN_END),
                     D_assy(X_MAIN_SPAR, sign_s * Y_CAP_END),
                     dxfattribs={"layer": "HIDDEN"})
    msp.add_line(D_assy(X_MAIN_SPAR, -FIN_HALF), D_assy(X_MAIN_SPAR, +FIN_HALF),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("MAIN SPAR  3mm CF tube  X=34.5  385mm (ONLY SPAR)", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D_assy(X_MAIN_SPAR, Y_CAP_END + 5)[0], D_assy(X_MAIN_SPAR, Y_CAP_END + 5)[1] + 2))

    # Hinge wire (concealed)
    for sign_s in [+1, -1]:
        msp.add_line(D_assy(X_HINGE, sign_s * FIN_HALF),
                     D_assy(X_HINGE, sign_s * Y_HINGE_END),
                     dxfattribs={"layer": "CENTERLINE"})
    msp.add_line(D_assy(X_HINGE, -FIN_HALF), D_assy(X_HINGE, +FIN_HALF),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_text("HINGE  0.5mm wire  X=60.0  concealed saddle  440mm", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (D_assy(X_HINGE, Y_CAP_END + 5)[0], D_assy(X_HINGE, Y_CAP_END + 5)[1] + 2))

    # Labels
    msp.add_text("LE", height=4.0, dxfattribs={"layer": "TEXT"}).set_placement(D_assy(-8, 80))
    msp.add_text("TE", height=4.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(ROOT_CHORD * TE_TRUNC + 5, 80))
    msp.add_text("LEFT TIP", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(REF_X, Y_CAP_END + 3))
    msp.add_text("RIGHT TIP", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(REF_X, -(Y_CAP_END + 3)))

    # Zone labels
    msp.add_text("STAB", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy(X_HINGE/2, 100))
    msp.add_text("ELEVATOR", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(
        D_assy((X_HINGE + ROOT_CHORD*TE_TRUNC)/2, 100))

    # Termination annotations (left half)
    for y_end, label in [
        (Y_MAIN_END,  f"spar tube ends y={Y_MAIN_END:.0f}"),
        (Y_HINGE_END, f"wire ends y={Y_HINGE_END:.0f}"),
    ]:
        pt = D_assy(ROOT_CHORD + 5, y_end)
        msp.add_text(label, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(pt)

    # Dimensions (all via D_assy)
    lt = D_assy(0, Y_CAP_END)
    rt = D_assy(0, -Y_CAP_END)
    msp.add_aligned_dim(p1=(lt[0], lt[1] + 15), p2=(rt[0], lt[1] + 15),
                        distance=10, dimstyle="AEROFORGE").render()

    fin_face = D_assy(0, FIN_HALF)
    msp.add_aligned_dim(p1=(fin_face[0], fin_face[1] + 8), p2=(lt[0], lt[1] + 8),
                        distance=5, dimstyle="AEROFORGE").render()

    root_le = D_assy(0, -(Y_CAP_END + 10))
    root_te = D_assy(ROOT_CHORD * TE_TRUNC, -(Y_CAP_END + 10))
    msp.add_aligned_dim(p1=root_le, p2=root_te, distance=8, dimstyle="AEROFORGE").render()

    fin_l = D_assy(ROOT_CHORD * TE_TRUNC + 10, FIN_HALF)
    fin_r = D_assy(ROOT_CHORD * TE_TRUNC + 10, -FIN_HALF)
    msp.add_aligned_dim(p1=fin_l, p2=fin_r, distance=5, dimstyle="AEROFORGE").render()

    # Root cross-section
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
    msp.add_line((sc_x - 3, sc_y), (sc_x + TE_TRUNC*c + 3, sc_y), dxfattribs={"layer": "CENTERLINE"})

    # Spar bore in section
    msp.add_circle((sc_x + X_MAIN_SPAR, sc_y), D_MAIN / 2, dxfattribs={"layer": "SPAR"})
    sf = X_MAIN_SPAR / c
    yts = naca4_yt(sf, tr) * c
    msp.add_text(f"Ø{D_MAIN} (3mm tube)", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (sc_x + X_MAIN_SPAR - 5, sc_y + yts + 2))

    # Hinge line in section
    hf = X_HINGE / c
    yth = naca4_yt(hf, tr) * c
    msp.add_line((sc_x + X_HINGE, sc_y - yth), (sc_x + X_HINGE, sc_y + yth),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("hinge X=60", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (sc_x + X_HINGE - 5, sc_y + yth + 2))

    # Zone labels in section
    msp.add_text("STAB", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (sc_x + X_HINGE / 2 - 5, sc_y - 2))
    msp.add_text("ELEV", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (sc_x + X_HINGE + 8, sc_y - 2))

    msp.add_linear_dim(base=(sc_x + c / 2, sc_y - 14),
                       p1=(sc_x, sc_y), p2=(sc_x + TE_TRUNC * c, sc_y),
                       dimstyle="AEROFORGE").render()

    # VStab junction detail
    jx = sc_x + ROOT_CHORD + 60; jy = sc_y
    msp.add_text("VSTAB JUNCTION DETAIL (schematic)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((jx, jy + 30))
    msp.add_lwpolyline([(jx, jy-25), (jx+7, jy-25), (jx+7, jy+25), (jx, jy+25), (jx, jy-25)],
                       dxfattribs={"layer": "OUTLINE"})
    msp.add_text("VStab fin\n7mm", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((jx+8, jy+1))
    msp.add_lwpolyline([(jx+7, jy-3.75), (jx+40, jy-3.75), (jx+40, jy+3.75), (jx+7, jy+3.75), (jx+7, jy-3.75)],
                       dxfattribs={"layer": "OUTLINE"})
    msp.add_text("HStab root", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((jx+42, jy))
    fr = 9.2
    msp.add_arc(center=(jx+7+fr, jy+3.75+fr), radius=fr, start_angle=180, end_angle=270,
                dxfattribs={"layer": "SECTION"})
    msp.add_arc(center=(jx+7+fr, jy-3.75-fr), radius=fr, start_angle=90, end_angle=180,
                dxfattribs={"layer": "SECTION"})
    msp.add_text(f"R={fr}mm fillet\n(quartic, C2)", height=2.0,
                 dxfattribs={"layer": "SECTION"}).set_placement((jx+7+fr+2, jy+6))
    msp.add_text("Dovetail + CA", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((jx-5, jy-22))

    # Notes
    notes = [
        "NOTES:",
        "1. Approved v6 baseline: 430mm span (215mm half-span + 7mm fin gap zone). All dims mm.",
        "2. Superellipse n=2.3 planform with C1-continuous tip cap y=210-214.",
        "3. 45%-chord ref X=53.1 is straight. Spar straight + perpendicular to fin CL.",
        "4. SINGLE SPAR: 3mm CF tube, X=34.5, 385mm total. No rear spar, no stiffener.",
        "5. HINGE: Concealed saddle at X=60.0. 0.5mm wire, 440mm. Bull-nose nests into stab TE channel.",
        "6. Root chord 118mm. Area ~4.21 dm^2. Active aircraft tail-volume target ~0.42.",
        "7. Gap seal TBD. No visible gap at any deflection angle.",
        "8. VStab junction: 9.2mm fillet, quartic, C2. Dovetail interlock + CA.",
        "9. Candidate mass target: 31-33g with same construction family.",
    ]
    nx = sc_x; ny = sc_y - 40
    for i, n in enumerate(notes):
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((nx, ny - i * 4.8))

    save_dxf_and_png(doc, "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf", dpi=300)
    print("HStab_Assembly v6 done.")

if __name__ == "__main__":
    main()
