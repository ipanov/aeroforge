"""
Elevator_Left Drawing — v6
============================
COMPONENT = elevator shell ONLY (hinge face to TE).
Sections show ONLY elevator geometry — bull-nose LE to TE.
Uses real HT-13/HT-12 airfoil data.
Uses orientation module.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from hstab_geometry import *
from src.core.dxf_utils import setup_drawing, save_dxf_and_png
from src.cad.drawing.orientation import TopViewMapper, validate_orientation

PLAN_LEFT = 290.0
PLAN_TOP = 320.0

def main():
    doc = setup_drawing(
        title="Elevator_Left",
        subtitle="Left elevator ONLY (hinge face to TE). Bull-nose concealed saddle. Right = mirror.",
        material="LW-PLA | Vase 0.40mm (0.55mm bull-nose) | 230C | Print hinge face down",
        mass="5.05g", scale="1:1", sheet_size="A2", status="FOR APPROVAL", revision="v6",
    )
    msp = doc.modelspace()

    # Orientation
    m = TopViewMapper(center_x=PLAN_LEFT, center_y=PLAN_TOP)

    def D(cx, cy):
        """cx = chordwise from hinge (0=hinge, positive=toward TE, negative=bull-nose fwd).
        cy = spanwise."""
        # Map: X_HINGE + cx is the consensus X position
        return m.map_half(X_HINGE + cx, cy, "left")

    msp.add_text("TOP VIEW — ELEVATOR COMPONENT (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((D(0, Y_HINGE_END/2)[0] - 50, PLAN_TOP + 50))

    # FWD arrow
    rx, ry = D(10, 5)
    msp.add_line((rx, ry), (rx, ry + 25), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry+25), (rx-2.5, ry+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((rx, ry+25), (rx+2.5, ry+21), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("FWD", height=3.5, dxfattribs={"layer": "ORIENTATION"}).set_placement((rx-6, ry+27))

    def elev_chord_v6(y):
        tx = te_x(y)
        return max(0, tx - X_HINGE)

    root_ec = elev_chord_v6(0)  # ~51.5mm

    # === PLANFORM: hinge face to TE ===
    # Hinge face (straight line, the forward face of this component)
    msp.add_line(D(0, 0), D(0, Y_HINGE_END), dxfattribs={"layer": "OUTLINE"})

    # Root face
    msp.add_line(D(-2.5, 0), D(root_ec, 0), dxfattribs={"layer": "OUTLINE"})

    # Bull-nose (extends forward of hinge, 2.5mm at root tapering to 0 at y=206)
    n_bull = 80
    bull_pts = []
    for i in range(n_bull + 1):
        y = 206.0 * i / n_bull
        depth = 2.5 * max(0, 1.0 - y / 206.0)
        bull_pts.append(D(-depth, y))
    msp.add_line(D(-2.5, 0), bull_pts[0], dxfattribs={"layer": "OUTLINE"})
    for i in range(len(bull_pts) - 1):
        msp.add_line(bull_pts[i], bull_pts[i+1], dxfattribs={"layer": "OUTLINE"})
    msp.add_line(bull_pts[-1], D(0, 206), dxfattribs={"layer": "OUTLINE"})

    # TE curve
    n_te = 120
    te_pts = []
    for i in range(n_te + 1):
        y = Y_HINGE_END * i / n_te
        ec = elev_chord_v6(y)
        if ec >= 0.3:
            te_pts.append(D(ec, y))
    for i in range(len(te_pts) - 1):
        msp.add_line(te_pts[i], te_pts[i+1], dxfattribs={"layer": "OUTLINE"})

    # Tip closure (connect last TE point to hinge end)
    if te_pts:
        msp.add_line(te_pts[-1], D(0, Y_HINGE_END), dxfattribs={"layer": "OUTLINE"})

    # Pushrod hole at root face
    msp.add_circle(D(10, 1.5), 0.8, dxfattribs={"layer": "SPAR"})
    msp.add_text("PUSHROD D1.6  10mm aft of hinge", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(13, 5))

    # Labels
    msp.add_text("HINGE FACE (bull-nose forward)", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(2, 50))
    msp.add_text("TE", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement(D(root_ec + 3, 20))
    msp.add_text("BULL-NOSE\n(into stab saddle)", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(-5, 80))
    msp.add_text("ELEVATOR SHELL (LEFT)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(root_ec/2, 100))
    msp.add_text("ROOT", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(D(root_ec/2, -6))
    msp.add_text("TIP y=212", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(D(-3, Y_HINGE_END+3))
    msp.add_text("SADDLE ZONE (y=0-206)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(-6, 50))
    msp.add_text("WIRE-ONLY (y=206-212)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(-4, 208))

    # Dimensions
    root_hinge_d = D(0, 0)
    root_te_d = D(root_ec, 0)
    tip_d = D(0, Y_HINGE_END)
    msp.add_aligned_dim(p1=(root_hinge_d[0]+15, root_hinge_d[1]),
                        p2=(root_hinge_d[0]+15, root_te_d[1]),
                        distance=5, dimstyle="AEROFORGE").render()
    msp.add_aligned_dim(p1=(root_hinge_d[0], root_hinge_d[1]+8),
                        p2=(tip_d[0], tip_d[1]+8),
                        distance=5, dimstyle="AEROFORGE").render()

    # === SECTIONS: ELEVATOR ONLY (hinge face to TE), real HT airfoil data ===
    SX = 420.0
    for sy, ys, lab in [
        (340, 0,   "SEC A — ROOT y=0 (elev: hinge to TE)"),
        (280, 100, "SEC B — y=100 (elevator only)"),
        (220, 200, "SEC C — y=200 (elevator only)"),
    ]:
        c = chord_at(ys)
        if c < 1: continue
        lx = le_x(ys)
        hinge_frac = (X_HINGE - lx) / c
        te_frac = TE_TRUNC
        elev_chord = elev_chord_v6(ys)
        if elev_chord < 1: continue

        msp.add_text(lab, height=2.3, dxfattribs={"layer": "TEXT"}).set_placement((SX, sy + 10))
        msp.add_text(f"elev chord={elev_chord:.1f}mm", height=2.0,
                     dxfattribs={"layer": "TEXT"}).set_placement((SX, sy + 6))

        # Draw ONLY elevator portion: from hinge_frac to TE_TRUNC
        upper_pts, lower_pts = airfoil_section_points(
            ys, x_start_frac=hinge_frac, x_end_frac=te_frac, n_pts=50)

        if not upper_pts: continue

        # Offset so hinge face is at SX (left edge of section)
        x_offset = upper_pts[0][0]  # first point x (at hinge)
        for i in range(len(upper_pts) - 1):
            x1u = SX + upper_pts[i][0] - x_offset
            y1u = sy + upper_pts[i][1]
            x2u = SX + upper_pts[i+1][0] - x_offset
            y2u = sy + upper_pts[i+1][1]
            msp.add_line((x1u, y1u), (x2u, y2u), dxfattribs={"layer": "OUTLINE"})

            x1l = SX + lower_pts[i][0] - x_offset
            y1l = sy + lower_pts[i][1]
            x2l = SX + lower_pts[i+1][0] - x_offset
            y2l = sy + lower_pts[i+1][1]
            msp.add_line((x1l, y1l), (x2l, y2l), dxfattribs={"layer": "OUTLINE"})

        # Hinge face (left edge of elevator section — where bull-nose is)
        yu_h = upper_pts[0][1]
        yl_h = lower_pts[0][1]
        msp.add_line((SX, sy + yl_h), (SX, sy + yu_h), dxfattribs={"layer": "SECTION"})
        msp.add_text("hinge\nface", height=1.3, dxfattribs={"layer": "TEXT"}).set_placement(
            (SX - 8, sy + yu_h + 1))

        # TE closure
        yu_te = upper_pts[-1][1]
        yl_te = lower_pts[-1][1]
        x_te = SX + upper_pts[-1][0] - x_offset
        msp.add_line((x_te, sy + yl_te), (x_te, sy + yu_te), dxfattribs={"layer": "OUTLINE"})

        # Centerline
        msp.add_line((SX - 3, sy), (x_te + 3, sy), dxfattribs={"layer": "CENTERLINE"})

        # Elevator chord dimension
        msp.add_linear_dim(base=(SX + elev_chord/2, sy - 6),
                           p1=(SX, sy), p2=(x_te, sy),
                           dimstyle="AEROFORGE").render()

    # Notes
    notes = [
        "NOTES:",
        "1. All dims mm. 1:1. Right elevator = mirror.",
        "2. This component = ELEVATOR SHELL ONLY (hinge face to TE).",
        "   Does NOT include stab. Sections show elevator geometry only.",
        "3. Hinge at X=60.0 (52.2% root chord). Root elev chord = 51.5mm (45%).",
        "4. BULL-NOSE: extends 2.5mm forward of hinge at root. Tapers to 0 at y=206.",
        "   Convex profile nests into concave saddle in stab TE.",
        "5. No stiffener (removed in v6). No tip horn.",
        "6. PUSHROD: Z-bend at root face, 10mm aft of hinge.",
        "7. HINGE WIRE: 0.5mm music wire in PETG sleeves, concealed.",
        "8. Gap seal TBD. Zero visible gap.",
        "9. Sections use real HT-13/HT-12 blended airfoil coordinates.",
        "10. Wall: 0.40mm vase (main), 0.55mm bull-nose. Print hinge face down.",
    ]
    for i, n in enumerate(notes):
        msp.add_text(n, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((25, 165 - i * 4.3))

    save_dxf_and_png(doc, "cad/components/empennage/Elevator_Left/Elevator_Left_drawing.dxf", dpi=300)
    print("Elevator_Left v6 done — ELEVATOR ONLY, real airfoil sections.")

if __name__ == "__main__":
    main()
