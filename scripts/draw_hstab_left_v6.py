"""
HStab_Left Component Drawing — v6
===================================
COMPONENT = fixed stab shell ONLY (LE to hinge face).
Does NOT contain the elevator.
Sections show ONLY this component's geometry — cut at hinge face.
Uses orientation module (no hand-coded coordinate transforms).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from hstab_geometry import *  # includes airfoil_section_points, airfoil_yt_upper, airfoil_yt_lower
from src.core.dxf_utils import setup_drawing, save_dxf_and_png
from src.cad.drawing.orientation import TopViewMapper, validate_orientation

def main():
    doc = setup_drawing(
        title="HStab_Left",
        subtitle="Fixed stab half (LEFT ONLY — LE to hinge face). Hinge@X=60. Right = mirror.",
        material="LW-PLA | Vase mode 0.45mm (0.6mm saddle zone) | 230C | Print saddle down",
        mass="6.89g", scale="1:1", sheet_size="A2", status="FOR APPROVAL", revision="v6",
    )
    msp = doc.modelspace()

    # Orientation: use tested module
    m = TopViewMapper(center_x=290, center_y=365)
    errors = validate_orientation(m, HALF_SPAN, ROOT_CHORD, side="left")
    assert not errors, f"Orientation validation FAILED: {errors}"

    def D(cx, cy):
        return m.map_half(cx, cy, "left")

    msp.add_text("TOP VIEW — STAB COMPONENT (1:1)", height=5.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((D(0, HALF_SPAN/2)[0] - 40, D(0, 0)[1] + 22))

    # FWD arrow (above root, pointing up)
    rx, ry = D(ROOT_CHORD * 0.3, 5)
    msp.add_line((rx, ry), (rx, ry + 25), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry+25), (rx-2.5, ry+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry+25), (rx+2.5, ry+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("FWD", height=3.5, dxfattribs={"layer": "ORIENTATION"}).set_placement((rx-6, ry+27))

    # === PLANFORM: LE to HINGE only (this component) ===
    # LE curve
    le_pts, _ = planform_points(n_pts=200)
    le_d = [D(lx, ly) for lx, ly in le_pts]
    for i in range(len(le_d)-1):
        msp.add_line(le_d[i], le_d[i+1], dxfattribs={"layer": "OUTLINE"})

    # Hinge line (the CUT FACE of this component — where elevator mates)
    # Hinge runs from root to where it exits the planform
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

    # Root chord (LE to hinge only — this is the STAB root face width)
    root_le = D(le_x(0), 0)
    root_hinge = D(X_HINGE, 0)
    msp.add_line(root_le, root_hinge, dxfattribs={"layer": "OUTLINE"})

    # Tip: LE curve closes toward hinge at the tip
    # The stab tip is where LE and hinge meet (or the cap zone)
    arc_pts = tip_arc_points(n_pts=50)
    # Only draw the portion of the tip that belongs to the stab (LE side of hinge)
    stab_arc = [(cx, cy) for cx, cy in arc_pts if cx <= X_HINGE]
    if stab_arc:
        stab_arc_d = [D(cx, cy) for cx, cy in stab_arc]
        for i in range(len(stab_arc_d)-1):
            msp.add_line(stab_arc_d[i], stab_arc_d[i+1], dxfattribs={"layer": "OUTLINE"})

    # Connect last LE point to first hinge point if needed
    if le_d and hinge_pts:
        # Close the planform outline at the tip
        pass  # The arc and hinge line should connect naturally

    # Main spar
    msp.add_line(D(X_MAIN_SPAR, 0), D(X_MAIN_SPAR, Y_MAIN_END), dxfattribs={"layer": "SPAR"})
    msp.add_line(D(X_MAIN_SPAR, Y_MAIN_END), D(X_MAIN_SPAR, Y_CAP_END), dxfattribs={"layer": "HIDDEN"})
    msp.add_text("MAIN SPAR X=34.5  Ø3.1  (3mm CF tube) — ONLY SPAR", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((D(X_MAIN_SPAR, 25)[0]+3, D(X_MAIN_SPAR, 25)[1]+2))

    # Hinge line label
    msp.add_text("HINGE FACE X=60.0 (saddle cavity here)", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((D(X_HINGE, 25)[0]+3, D(X_HINGE, 25)[1]+2))

    # 45% ref line
    msp.add_line(D(REF_X, 0), D(REF_X, Y_CAP_END), dxfattribs={"layer": "CENTERLINE"})

    # Zone and edge labels
    msp.add_text("STAB SHELL (this component)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D((X_MAIN_SPAR + X_HINGE)/2, 100))
    msp.add_text("LE", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(D(-5, 60))
    msp.add_text("HINGE FACE (open — elevator mates here)", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(X_HINGE + 3, 60))
    msp.add_text("ROOT", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(D(X_HINGE/2, -6))
    msp.add_text("TIP", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(D(X_HINGE/2, Y_CAP_END+3))

    # Dimensions
    root_le_d = D(0, 0)
    root_hinge_d = D(X_HINGE, 0)
    tip_d = D(0, Y_CAP_END)
    # Stab chord at root (LE to hinge)
    msp.add_aligned_dim(p1=(root_le_d[0]+15, root_le_d[1]),
                        p2=(root_le_d[0]+15, root_hinge_d[1]),
                        distance=5, dimstyle="AEROFORGE").render()
    # Half span
    msp.add_aligned_dim(p1=(root_le_d[0], root_le_d[1]+8),
                        p2=(tip_d[0], tip_d[1]+8),
                        distance=5, dimstyle="AEROFORGE").render()

    # === SECTIONS: show ONLY stab geometry (LE to hinge face) ===
    SX = 400.0
    for sy, ys, lab in [
        (350, 0,   "SEC A — ROOT y=0 (stab: LE to hinge)"),
        (290, 100, "SEC B — y=100 (stab portion only)"),
        (230, 189, "SEC C — y=189 (spar end)"),
    ]:
        c = chord_at(ys)
        if c < 1: continue
        tr = t_ratio(ys); lx = le_x(ys)
        hinge_frac = (X_HINGE - lx) / c  # chord fraction of hinge within this airfoil
        stab_chord = X_HINGE - lx  # the actual stab chord at this station

        if hinge_frac > TE_TRUNC or stab_chord < 1:
            continue  # hinge is outside the airfoil at this station

        msp.add_text(lab, height=2.3, dxfattribs={"layer": "TEXT"}).set_placement((SX, sy+10))
        msp.add_text(f"stab chord={stab_chord:.1f}mm", height=2.0,
                     dxfattribs={"layer": "TEXT"}).set_placement((SX, sy+6))

        # Draw REAL HT-13/HT-12 blended section from LE to hinge face
        upper_pts, lower_pts = airfoil_section_points(
            ys, x_start_frac=0.0, x_end_frac=hinge_frac, n_pts=60)
        for i in range(len(upper_pts) - 1):
            msp.add_line((SX + upper_pts[i][0], sy + upper_pts[i][1]),
                         (SX + upper_pts[i+1][0], sy + upper_pts[i+1][1]),
                         dxfattribs={"layer": "OUTLINE"})
            msp.add_line((SX + lower_pts[i][0], sy + lower_pts[i][1]),
                         (SX + lower_pts[i+1][0], sy + lower_pts[i+1][1]),
                         dxfattribs={"layer": "OUTLINE"})
        # LE closure (cosine spacing makes first points very close, smooth nose)
        msp.add_line((SX + upper_pts[0][0], sy + upper_pts[0][1]),
                     (SX + lower_pts[0][0], sy + lower_pts[0][1]),
                     dxfattribs={"layer": "OUTLINE"})

        # Hinge face (OPEN — this is where the elevator mates)
        yu_hinge = airfoil_yt_upper(hinge_frac, ys) * c
        yl_hinge = airfoil_yt_lower(hinge_frac, ys) * c
        yth = yu_hinge  # for saddle drawing below
        msp.add_line((SX + hinge_frac*c, sy + yl_hinge), (SX + hinge_frac*c, sy + yu_hinge),
                     dxfattribs={"layer": "SECTION"})
        msp.add_text("hinge\nface", height=1.3, dxfattribs={"layer": "TEXT"}).set_placement(
            (SX + hinge_frac*c + 2, sy + yth + 1))

        # Saddle cavity (small concave notch at hinge face)
        # Show as a small indentation at the hinge face
        saddle_depth = min(2.5, max(0, 2.5 * (1 - ys/206)))
        if saddle_depth > 0.3:
            sx_h = SX + hinge_frac * c
            msp.add_line((sx_h, sy + yth*0.3), (sx_h - saddle_depth, sy + yth*0.15),
                         dxfattribs={"layer": "SECTION"})
            msp.add_line((sx_h - saddle_depth, sy + yth*0.15), (sx_h - saddle_depth, sy - yth*0.15),
                         dxfattribs={"layer": "SECTION"})
            msp.add_line((sx_h - saddle_depth, sy - yth*0.15), (sx_h, sy - yth*0.3),
                         dxfattribs={"layer": "SECTION"})

        # Spar bore
        sf = (X_MAIN_SPAR - lx) / c if c > 0 else 999
        if 0 < sf < hinge_frac:
            msp.add_circle((SX + sf*c, sy), D_MAIN/2, dxfattribs={"layer": "SPAR"})

        # Centerline
        msp.add_line((SX - 3, sy), (SX + hinge_frac*c + 5, sy), dxfattribs={"layer": "CENTERLINE"})

        # Stab chord dimension
        msp.add_linear_dim(base=(SX + stab_chord/2, sy - yth - 6),
                           p1=(SX, sy), p2=(SX + stab_chord, sy),
                           dimstyle="AEROFORGE").render()

    # Notes
    notes = [
        "NOTES:",
        "1. All dims mm. 1:1. HStab_Right = mirror of this drawing.",
        "2. This component = STAB SHELL ONLY (LE to hinge face X=60.0).",
        "   Does NOT include elevator. Sections show stab geometry only.",
        "3. MAIN SPAR: 3mm CF tube, D3.1 bore, X=34.5. To y=189. 378mm total.",
        "   ONLY spar (rear spar + stiffener removed in v6).",
        "4. HINGE FACE: concave saddle channel at X=60.0.",
        "   Saddle tapers from 2.5mm depth at root to 0 at y=206.",
        "5. Sections show the CUT FACE at the hinge — open, with saddle cavity.",
        "6. Wall: 0.45mm vase (main), 0.6mm saddle zone (printed at 210C dense).",
        "7. v6: single spar, forward hinge, concealed mechanism. 29.3g assembly total.",
    ]
    for i, n in enumerate(notes):
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((25, 175-i*4.8))

    save_dxf_and_png(doc, "cad/components/empennage/HStab_Left/HStab_Left_drawing.dxf", dpi=300)
    print("HStab_Left v6 done — STAB ONLY, correct sections.")

if __name__ == "__main__":
    main()
