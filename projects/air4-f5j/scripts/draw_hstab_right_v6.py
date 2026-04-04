"""
HStab_Right Component Drawing — v6 (MIRROR of Left)
=====================================================
Uses orientation module with side='right' so tip extends RIGHT.
All geometry and sections are identical to Left but mirrored.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

# Import the Left drawing script and override only the side/title
import draw_hstab_left_v6 as left_script
from hstab_geometry import *
from src.core.dxf_utils import setup_drawing, save_dxf_and_png
from src.cad.drawing.orientation import TopViewMapper, validate_orientation

def main():
    doc = setup_drawing(
        title="HStab_Right",
        subtitle="Fixed stab half (RIGHT — mirror of Left). LE to hinge face. Hinge@X=60.",
        material="LW-PLA | Vase mode 0.45mm (0.6mm saddle zone) | 230C | Print saddle down",
        mass="6.89g", scale="1:1", sheet_size="A2", status="FOR APPROVAL", revision="v6",
    )
    msp = doc.modelspace()

    # RIGHT side: tip extends RIGHT
    m = TopViewMapper(center_x=290, center_y=365)
    errors = validate_orientation(m, HALF_SPAN, ROOT_CHORD, side="right")
    assert not errors, f"Orientation validation FAILED: {errors}"

    def D(cx, cy):
        return m.map_half(cx, cy, "right")

    msp.add_text("TOP VIEW — STAB COMPONENT (1:1)", height=5.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((D(0, HALF_SPAN/2)[0] - 40, D(0, 0)[1] + 22))

    # FWD arrow
    rx, ry = D(ROOT_CHORD * 0.3, 5)
    msp.add_line((rx, ry), (rx, ry + 25), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry+25), (rx-2.5, ry+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry+25), (rx+2.5, ry+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("FWD", height=3.5, dxfattribs={"layer": "ORIENTATION"}).set_placement((rx-6, ry+27))

    # === PLANFORM: LE to HINGE only ===
    le_pts, _ = planform_points(n_pts=200)
    le_d = [D(lx, ly) for lx, ly in le_pts]
    for i in range(len(le_d)-1):
        msp.add_line(le_d[i], le_d[i+1], dxfattribs={"layer": "OUTLINE"})

    # Hinge line
    hinge_pts = []
    for i in range(200):
        y = Y_HINGE_END * i / 199
        c = chord_at(y)
        lx = le_x(y)
        if X_HINGE < lx + c * TE_TRUNC and X_HINGE > lx:
            hinge_pts.append(D(X_HINGE, y))
    if hinge_pts:
        for i in range(len(hinge_pts)-1):
            msp.add_line(hinge_pts[i], hinge_pts[i+1], dxfattribs={"layer": "OUTLINE"})

    # Root chord
    msp.add_line(D(le_x(0), 0), D(X_HINGE, 0), dxfattribs={"layer": "OUTLINE"})

    # Tip arc (stab portion only)
    arc_pts = tip_arc_points(n_pts=50)
    stab_arc = [(cx, cy) for cx, cy in arc_pts if cx <= X_HINGE]
    if stab_arc:
        stab_arc_d = [D(cx, cy) for cx, cy in stab_arc]
        for i in range(len(stab_arc_d)-1):
            msp.add_line(stab_arc_d[i], stab_arc_d[i+1], dxfattribs={"layer": "OUTLINE"})

    # Main spar
    msp.add_line(D(X_MAIN_SPAR, 0), D(X_MAIN_SPAR, Y_MAIN_END), dxfattribs={"layer": "SPAR"})
    msp.add_line(D(X_MAIN_SPAR, Y_MAIN_END), D(X_MAIN_SPAR, Y_CAP_END), dxfattribs={"layer": "HIDDEN"})
    msp.add_text("MAIN SPAR X=34.5 (ONLY SPAR)", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((D(X_MAIN_SPAR, 25)[0]-35, D(X_MAIN_SPAR, 25)[1]+2))

    # Hinge face label
    msp.add_text("HINGE FACE X=60.0", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((D(X_HINGE, 25)[0]-25, D(X_HINGE, 25)[1]+2))

    # 45% ref
    msp.add_line(D(REF_X, 0), D(REF_X, Y_CAP_END), dxfattribs={"layer": "CENTERLINE"})

    # Labels
    msp.add_text("STAB SHELL (RIGHT)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D((X_MAIN_SPAR + X_HINGE)/2, 100))
    msp.add_text("ROOT", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(D(X_HINGE/2, -6))
    msp.add_text("TIP", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(D(X_HINGE/2, Y_CAP_END+3))

    # Dimensions
    root_le_d = D(0, 0)
    root_hinge_d = D(X_HINGE, 0)
    tip_d = D(0, Y_CAP_END)
    msp.add_aligned_dim(p1=(root_le_d[0]-15, root_le_d[1]),
                        p2=(root_le_d[0]-15, root_hinge_d[1]),
                        distance=5, dimstyle="AEROFORGE").render()
    msp.add_aligned_dim(p1=(root_le_d[0], root_le_d[1]+8),
                        p2=(tip_d[0], tip_d[1]+8),
                        distance=5, dimstyle="AEROFORGE").render()

    # Sections (same geometry as Left — real HT airfoil data)
    SX = 400.0
    for sy, ys, lab in [
        (350, 0,   "SEC A — ROOT y=0 (stab: LE to hinge)"),
        (290, 100, "SEC B — y=100 (stab portion only)"),
        (230, 189, "SEC C — y=189 (spar end)"),
    ]:
        c = chord_at(ys)
        if c < 1: continue
        lx = le_x(ys)
        hinge_frac = (X_HINGE - lx) / c
        stab_chord = X_HINGE - lx
        if hinge_frac > TE_TRUNC or stab_chord < 1:
            continue

        msp.add_text(lab, height=2.3, dxfattribs={"layer": "TEXT"}).set_placement((SX, sy+10))
        msp.add_text(f"stab chord={stab_chord:.1f}mm", height=2.0,
                     dxfattribs={"layer": "TEXT"}).set_placement((SX, sy+6))

        upper_pts, lower_pts = airfoil_section_points(ys, 0.0, hinge_frac, 60)
        for i in range(len(upper_pts) - 1):
            msp.add_line((SX + upper_pts[i][0], sy + upper_pts[i][1]),
                         (SX + upper_pts[i+1][0], sy + upper_pts[i+1][1]),
                         dxfattribs={"layer": "OUTLINE"})
            msp.add_line((SX + lower_pts[i][0], sy + lower_pts[i][1]),
                         (SX + lower_pts[i+1][0], sy + lower_pts[i+1][1]),
                         dxfattribs={"layer": "OUTLINE"})
        msp.add_line((SX + upper_pts[0][0], sy + upper_pts[0][1]),
                     (SX + lower_pts[0][0], sy + lower_pts[0][1]),
                     dxfattribs={"layer": "OUTLINE"})

        yu_h = airfoil_yt_upper(hinge_frac, ys) * c
        yl_h = airfoil_yt_lower(hinge_frac, ys) * c
        msp.add_line((SX + hinge_frac*c, sy + yl_h), (SX + hinge_frac*c, sy + yu_h),
                     dxfattribs={"layer": "SECTION"})
        msp.add_text("hinge\nface", height=1.3, dxfattribs={"layer": "TEXT"}).set_placement(
            (SX + hinge_frac*c + 2, sy + yu_h + 1))

        sf = (X_MAIN_SPAR - lx) / c if c > 0 else 999
        if 0 < sf < hinge_frac:
            msp.add_circle((SX + sf*c, sy), D_MAIN/2, dxfattribs={"layer": "SPAR"})
        msp.add_line((SX - 3, sy), (SX + hinge_frac*c + 5, sy), dxfattribs={"layer": "CENTERLINE"})
        msp.add_linear_dim(base=(SX + stab_chord/2, sy - 6),
                           p1=(SX, sy), p2=(SX + stab_chord, sy),
                           dimstyle="AEROFORGE").render()

    # Notes
    notes = [
        "NOTES:",
        "1. All dims mm. 1:1. Mirror of HStab_Left.",
        "2. This component = STAB SHELL ONLY (LE to hinge face X=60.0).",
        "3. Sections show stab geometry only — real HT-13/HT-12 airfoil data.",
        "4. MAIN SPAR: 3mm CF tube, D3.1, X=34.5. ONLY spar.",
        "5. v6: single spar, forward hinge, concealed saddle mechanism.",
    ]
    for i, n in enumerate(notes):
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((25, 175-i*4.8))

    save_dxf_and_png(doc, "cad/components/empennage/HStab_Right/HStab_Right_drawing.dxf", dpi=300)
    print("HStab_Right v6 done — STAB ONLY, tip extends RIGHT.")

if __name__ == "__main__":
    main()
