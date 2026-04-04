"""
HStab_Left Component Drawing — v5 Consensus (v4 FINAL)
=======================================================
Uses shared geometry (C1-continuous tip cap).
Span HORIZONTAL, LE top, TE bottom. No grid. Clean ISO dims.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from hstab_geometry import *
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# Drawing layout
PLAN_LEFT = 70.0
PLAN_TOP = 365.0

def D(cx, cy):
    return (PLAN_LEFT + cy, PLAN_TOP - cx)

def main():
    doc = setup_drawing(
        title="HStab_Left",
        subtitle="Fixed stab half (LEFT). Superellipse n=2.3, HT-13→HT-12. C1 tip cap. Right = mirror.",
        material="LW-PLA | Vase mode 0.45mm wall | 230°C | Print flat, hinge face down",
        mass="8.50g", scale="1:1", sheet_size="A2", status="FOR APPROVAL", revision="v5",
    )
    msp = doc.modelspace()

    msp.add_text("TOP VIEW — PLANFORM (1:1)", height=5.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((PLAN_LEFT, PLAN_TOP + 22))

    # FWD arrow
    ax, ay = PLAN_LEFT - 25, PLAN_TOP - 50
    msp.add_line((ax, ay), (ax, ay + 25), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ax, ay+25), (ax-2.5, ay+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ax, ay+25), (ax+2.5, ay+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("FWD", height=3.5, dxfattribs={"layer": "ORIENTATION"}).set_placement((ax-6, ay+27))

    # ── Planform outline (polylines stop at y=213, tip closed with ellipse arc) ──
    le_pts, te_pts = planform_points(n_pts=200)
    le_d = [D(lx, ly) for lx, ly in le_pts]
    te_d = [D(tx, ty) for tx, ty in te_pts]

    # Root chord
    msp.add_line(le_d[0], te_d[0], dxfattribs={"layer": "OUTLINE"})
    # LE curve
    for i in range(len(le_d)-1):
        msp.add_line(le_d[i], le_d[i+1], dxfattribs={"layer": "OUTLINE"})
    # TE curve
    for i in range(len(te_d)-1):
        msp.add_line(te_d[i], te_d[i+1], dxfattribs={"layer": "OUTLINE"})

    # TIP ARC: semi-elliptical closure drawn as POLYLINE (ezdxf ELLIPSE not rendered by matplotlib)
    arc_pts = tip_arc_points(n_pts=50)
    arc_d = [D(cx, cy) for cx, cy in arc_pts]
    for i in range(len(arc_d) - 1):
        msp.add_line(arc_d[i], arc_d[i + 1], dxfattribs={"layer": "OUTLINE"})

    # ── Spar lines ──
    for x_rod, y_end, layer, label in [
        (X_MAIN_SPAR, Y_MAIN_END, "SPAR", "MAIN SPAR X=35.0  Ø3.1mm  (3mm CF tube)"),
        (X_REAR_SPAR, Y_REAR_END, "SPAR", "REAR SPAR X=69.0  Ø1.6mm  (1.5mm CF rod)"),
        (X_HINGE, Y_HINGE_END, "CENTERLINE", "HINGE LINE X=74.75  Ø0.6mm  (0.5mm wire)"),
    ]:
        msp.add_line(D(x_rod, 0), D(x_rod, y_end), dxfattribs={"layer": layer})
        msp.add_line(D(x_rod, y_end), D(x_rod, Y_CAP_END), dxfattribs={"layer": "HIDDEN"})
        # Tick at termination
        e = D(x_rod, y_end)
        msp.add_line((e[0]-1, e[1]-3), (e[0]-1, e[1]+3), dxfattribs={"layer": "DIMENSION"})
        # Label
        msp.add_text(label, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(
            (D(x_rod, 25)[0], D(x_rod, 25)[1]+2))

    # 45% ref line
    msp.add_line(D(REF_X, 0), D(REF_X, Y_CAP_END), dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("45% REF X=51.75 (straight)", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((D(REF_X, 10)[0], D(REF_X, 10)[1]+2))

    # Zone labels
    msp.add_text("STAB ZONE (this component)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(X_HINGE/2, 120))
    msp.add_text("ELEVATOR (separate)", height=3.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(D((X_HINGE+ROOT_CHORD*TE_TRUNC)/2, 90))

    # Edge labels
    msp.add_text("LE (LEADING EDGE — faces airflow, less sweep)", height=3.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(-6, 60))
    msp.add_text("TE (TRAILING EDGE — aft, more sweep)", height=3.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(ROOT_CHORD*TE_TRUNC+4, 60))
    msp.add_text("ROOT", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(D(ROOT_CHORD/2, -7))
    msp.add_text("TIP (C1 cap y=210→214)", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(REF_X-15, Y_CAP_END+3))

    # Section cut lines
    for y_cut, sid in [(0, "A-A"), (100, "B-B"), (186, "C-C")]:
        dx = PLAN_LEFT + y_cut
        lx, tx = le_x(y_cut), te_x(y_cut)
        msp.add_line((dx, PLAN_TOP-lx+10), (dx, PLAN_TOP-tx-10), dxfattribs={"layer": "SECTION"})
        msp.add_text(sid, height=3.0, dxfattribs={"layer": "SECTION"}).set_placement(
            (dx-3, PLAN_TOP-lx+12))
        msp.add_text(sid, height=3.0, dxfattribs={"layer": "SECTION"}).set_placement(
            (dx-3, PLAN_TOP-tx-16))

    # Dimensions
    msp.add_linear_dim(base=(PLAN_LEFT+Y_CAP_END/2, PLAN_TOP+12),
                       p1=(PLAN_LEFT, PLAN_TOP+5), p2=(PLAN_LEFT+Y_CAP_END, PLAN_TOP+5),
                       dimstyle="AEROFORGE").render()
    msp.add_aligned_dim(p1=(PLAN_LEFT-15, PLAN_TOP),
                        p2=(PLAN_LEFT-15, PLAN_TOP-ROOT_CHORD*TE_TRUNC),
                        distance=5, dimstyle="AEROFORGE").render()

    # ── Sections (right side) ──
    SX = 355.0
    for sy, ys, lab in [
        (350, 0,   "SECTION A-A — ROOT y=0 (HT-13 6.5%)"),
        (295, 100, "SECTION B-B — y=100mm (~6.1%)"),
        (240, 186, "SECTION C-C — y=186mm (spar end ~5.3%)"),
    ]:
        c = chord_at(ys); tr = t_ratio(ys); lx = le_x(ys)
        msp.add_text(lab, height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((SX, sy+10))
        msp.add_text(f"c={c:.1f}  t/c={tr*100:.1f}%  t={naca4_yt(0.3,tr)*c:.1f}mm",
                     height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((SX, sy+6))

        for i in range(80):
            xc1 = TE_TRUNC*i/80; xc2 = TE_TRUNC*(i+1)/80
            y1 = naca4_yt(xc1,tr)*c; y2 = naca4_yt(xc2,tr)*c
            msp.add_line((SX+xc1*c,sy+y1),(SX+xc2*c,sy+y2), dxfattribs={"layer":"OUTLINE"})
            msp.add_line((SX+xc1*c,sy-y1),(SX+xc2*c,sy-y2), dxfattribs={"layer":"OUTLINE"})

        yt0 = naca4_yt(0.005,tr)*c
        msp.add_line((SX,sy-yt0),(SX,sy+yt0), dxfattribs={"layer":"OUTLINE"})
        yte = naca4_yt(TE_TRUNC,tr)*c
        msp.add_line((SX+TE_TRUNC*c,sy-yte),(SX+TE_TRUNC*c,sy+yte), dxfattribs={"layer":"OUTLINE"})
        msp.add_line((SX-3,sy),(SX+TE_TRUNC*c+3,sy), dxfattribs={"layer":"CENTERLINE"})

        for xr,d,lay in [(X_MAIN_SPAR,D_MAIN,"SPAR"),(X_REAR_SPAR,D_REAR,"SPAR"),(X_HINGE,D_HINGE,"CENTERLINE")]:
            f = (xr-lx)/c if c>0 else 999
            if 0 < f < TE_TRUNC:
                msp.add_circle((SX+f*c,sy), d/2, dxfattribs={"layer":lay})

        hf = (X_HINGE-lx)/c if c>0 else 999
        if 0 < hf < TE_TRUNC:
            yth = naca4_yt(hf,tr)*c
            msp.add_line((SX+hf*c,sy-yth),(SX+hf*c,sy+yth), dxfattribs={"layer":"CENTERLINE"})

        msp.add_linear_dim(base=(SX+c/2, sy-naca4_yt(0.3,tr)*c-8),
                           p1=(SX,sy), p2=(SX+TE_TRUNC*c,sy),
                           dimstyle="AEROFORGE").render()

    # Notes
    notes = [
        "NOTES:",
        "1. All dims mm. 1:1 scale. HStab_Right = mirror.",
        "2. Planform: superellipse c(y)=115[1-|y/215|^2.3]^(1/2.3), y=0→210.",
        "   C1-continuous tip cap y=210→214 (matched-slope cubic polynomial).",
        "3. This component = stab shell (LE to hinge line X=74.75).",
        "4. MAIN SPAR: 3mm CF tube. Ø3.1 bore X=35.0. Tube to y=186. Total 372mm.",
        "5. REAR SPAR: 1.5mm CF rod. Ø1.6 bore X=69.0. To y=210. Total 420mm.",
        "6. HINGE WIRE: 0.5mm wire. Ø0.6 bore X=74.75. To y=203. Total 440mm.",
        "7. 45%-chord ref X=51.75 is straight. All rods straight + parallel.",
        "8. VStab dovetail at root. 9.2mm fillet (quartic, C2). Wall 0.45mm vase.",
        "9. LE has LESS sweep (0.45 factor). TE has MORE sweep (0.55 factor).",
        "   This is correct per 45%-chord alignment — see consensus §Planform.",
    ]
    for i, n in enumerate(notes):
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((25, 175-i*4.8))

    save_dxf_and_png(doc, "cad/components/empennage/HStab_Left/HStab_Left_drawing.dxf", dpi=300)
    print("HStab_Left done.")

if __name__ == "__main__":
    main()
