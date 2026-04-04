"""
Elevator_Left Drawing — v5 Consensus (v3 CORRECTED HORN)
=========================================================
Uses shared geometry. Horn extends 90° forward from hinge line.
Tungsten pocket fully enclosed within horn structure.
Semi-elliptical tip cap properly integrated.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from hstab_geometry import *
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# Drawing layout: hinge at top, TE at bottom, horn extends ABOVE hinge
PLAN_LEFT = 80.0
PLAN_TOP = 320.0   # hinge line Y position

def D(x_from_hinge, y_span):
    """x_from_hinge: 0=hinge, +ive=toward TE, -ive=forward of hinge (horn)."""
    return (PLAN_LEFT + y_span, PLAN_TOP - x_from_hinge)


def main():
    doc = setup_drawing(
        title="Elevator_Left",
        subtitle="Left elevator with integral tip horn + tungsten balance pocket. Right = mirror.",
        material="LW-PLA | Vase 0.40mm (0.55mm horn zone) | 230°C | Print hinge face down",
        mass="4.00g", scale="1:1", sheet_size="A2", status="FOR APPROVAL", revision="v5",
    )
    msp = doc.modelspace()

    msp.add_text("TOP VIEW — ELEVATOR WITH TIP HORN (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((PLAN_LEFT-10, PLAN_TOP+60))

    # FWD arrow
    ax, ay = PLAN_LEFT - 25, PLAN_TOP + 10
    msp.add_line((ax,ay),(ax,ay+25), dxfattribs={"layer":"ORIENTATION"})
    msp.add_line((ax,ay+25),(ax-2.5,ay+21), dxfattribs={"layer":"ORIENTATION"})
    msp.add_line((ax,ay+25),(ax+2.5,ay+21), dxfattribs={"layer":"ORIENTATION"})
    msp.add_text("FWD", height=3.5, dxfattribs={"layer":"ORIENTATION"}).set_placement((ax-6,ay+27))

    root_ec = elev_chord_at(0)  # ~40.25mm

    # ═══════════════════════════════════════════════════════════════════════
    # ELEVATOR OUTLINE
    # ═══════════════════════════════════════════════════════════════════════

    # 1. ROOT FACE: perpendicular line from hinge (0) to TE (root_ec)
    msp.add_line(D(0, 0), D(root_ec, 0), dxfattribs={"layer": "OUTLINE"})

    # 2. HINGE LINE: straight from root to horn start (y=0 → y=195)
    msp.add_line(D(0, 0), D(0, Y_HORN_START), dxfattribs={"layer": "CENTERLINE"})

    # 3. TE CURVE: from root (y=0) to where elevator chord→0 (~y=204)
    n_te = 80
    te_pts = []
    for i in range(n_te + 1):
        y = 210.0 * i / n_te
        ec = elev_chord_at(y)
        if ec >= 0.3:
            te_pts.append(D(ec, y))
    for i in range(len(te_pts) - 1):
        msp.add_line(te_pts[i], te_pts[i+1], dxfattribs={"layer": "OUTLINE"})

    # 4. HORN STRUCTURE (y=195→214)
    # The horn extends FORWARD of hinge line (perpendicular at root of horn).
    # Per consensus: parabolic curve y=195→205 (0→15mm fwd), then blends to
    # full LE at y=210, then tip cap y=210→214.

    # Horn forward edge (above hinge line in drawing)
    n_horn = 60
    horn_fwd_pts = []

    # Phase 1: horn extension y=195→210 (hinge line to full LE)
    for i in range(n_horn + 1):
        y = Y_HORN_START + (Y_CAP_START - Y_HORN_START) * i / n_horn
        fwd = horn_fwd_offset(y)
        horn_fwd_pts.append(D(-fwd, y))

    # Connect hinge end to horn start
    msp.add_line(D(0, Y_HORN_START), horn_fwd_pts[0], dxfattribs={"layer": "OUTLINE"})

    # Draw horn forward edge
    for i in range(len(horn_fwd_pts) - 1):
        msp.add_line(horn_fwd_pts[i], horn_fwd_pts[i+1], dxfattribs={"layer": "OUTLINE"})

    # Phase 2: Tip cap y=210→214 (LE side = horn forward side)
    n_cap = 30
    cap_le_pts = []
    cap_te_pts = []
    for i in range(n_cap + 1):
        y = Y_CAP_START + CAP_SPAN * i / n_cap
        c_cap = chord_at(y)
        lx = le_x(y)
        tx = te_x(y)
        # In elevator coords (relative to hinge X=74.75)
        cap_le_pts.append(D(lx - X_HINGE, y))   # forward of hinge = negative
        cap_te_pts.append(D(tx - X_HINGE, y))   # also forward (hinge exits airfoil)

    # Connect horn end to cap LE start
    msp.add_line(horn_fwd_pts[-1], cap_le_pts[0], dxfattribs={"layer": "OUTLINE"})

    # Cap LE curve
    for i in range(n_cap):
        msp.add_line(cap_le_pts[i], cap_le_pts[i+1], dxfattribs={"layer": "OUTLINE"})
    # Cap TE curve
    for i in range(n_cap):
        msp.add_line(cap_te_pts[i], cap_te_pts[i+1], dxfattribs={"layer": "OUTLINE"})

    # Connect TE curve end to cap TE start
    # Bridge from where elevator TE ends (~y=204) to cap TE at y=210
    n_bridge = 20
    for i in range(n_bridge):
        y1 = 203.0 + (Y_CAP_START - 203.0) * i / n_bridge
        y2 = 203.0 + (Y_CAP_START - 203.0) * (i+1) / n_bridge
        t1 = te_x(y1) - X_HINGE
        t2 = te_x(y2) - X_HINGE
        msp.add_line(D(t1, y1), D(t2, y2), dxfattribs={"layer": "OUTLINE"})

    # 5. STIFFENER ROD
    stiff_off = X_STIFF - X_HINGE  # 17.25mm from hinge toward TE
    msp.add_line(D(stiff_off, 0), D(stiff_off, Y_STIFF_END), dxfattribs={"layer": "SPAR"})
    msp.add_line(D(stiff_off, Y_STIFF_END), D(stiff_off, 170), dxfattribs={"layer": "HIDDEN"})
    msp.add_text("STIFFENER 1mm CF  X=92.0", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement((D(stiff_off, 15)[0], D(stiff_off, 15)[1]-4))

    # 6. TUNGSTEN POCKET (inside horn, forward of hinge)
    py_min = POCKET_Y_CENTER - POCKET_SPAN/2   # 195
    py_max = POCKET_Y_CENTER + POCKET_SPAN/2   # 205
    # Pocket is 8mm forward of hinge, 6.5mm wide
    px_fwd = -(POCKET_FWD_OF_HINGE + POCKET_CHORD/2)   # -11.25
    px_aft = -(POCKET_FWD_OF_HINGE - POCKET_CHORD/2)   # -4.75
    msp.add_lwpolyline([
        D(px_fwd, py_min), D(px_aft, py_min),
        D(px_aft, py_max), D(px_fwd, py_max), D(px_fwd, py_min)
    ], dxfattribs={"layer": "SECTION"})

    # Cross-hatch the pocket
    for j in range(5):
        y_h = py_min + (py_max - py_min) * (j + 0.5) / 5
        msp.add_line(D(px_fwd, y_h), D(px_aft, y_h), dxfattribs={"layer": "HATCH"})

    msp.add_text("TUNGSTEN POCKET", height=2.5,
                 dxfattribs={"layer": "SECTION"}).set_placement(D(px_fwd-2, py_max+5))
    msp.add_text(f"{POCKET_SPAN}×{POCKET_CHORD}×{POCKET_DEPTH}mm  0.50g W putty",
                 height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(D(px_fwd-2, py_max+1))
    msp.add_text("snap-fit cap", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(px_fwd-2, py_max-3))

    # 7. PUSHROD HOLES
    for fwd, note in [(10,""), (12,"(primary)"), (14,"")]:
        msp.add_circle(D(-fwd, Y_LAST_KNUCKLE), 0.8, dxfattribs={"layer": "SPAR"})
    msp.add_text("PUSHROD HOLES Ø1.6  y=200", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(-17, Y_LAST_KNUCKLE+5))
    msp.add_text("10/12/14mm fwd of hinge", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(-17, Y_LAST_KNUCKLE+1))

    # 8. MARKERS
    for y_mark, label in [
        (Y_LAST_KNUCKLE, "LAST KNUCKLE y=200"),
        (Y_HORN_START, "HORN STARTS y=195"),
        (Y_HINGE_END, "WIRE BEND y=203"),
    ]:
        mk = D(0, y_mark)
        msp.add_line((mk[0]-2, mk[1]-3), (mk[0]-2, mk[1]+3), dxfattribs={"layer": "DIMENSION"})
        msp.add_text(label, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(
            (mk[0]+3, mk[1]+1))

    # 9. LABELS
    msp.add_text("HINGE LINE (X=74.75)", height=3.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(2, 50))
    msp.add_text("TE (aft)", height=3.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(root_ec+4, 20))
    msp.add_text("HORN", height=4.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(-8, 203))
    msp.add_text("ROOT", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(D(root_ec/2, -6))
    msp.add_text("TIP CAP y=210→214", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(D(-30, Y_CAP_END+3))

    # 10. DIMENSIONS
    msp.add_linear_dim(base=(PLAN_LEFT+Y_CAP_END/2, PLAN_TOP+50),
                       p1=(PLAN_LEFT, PLAN_TOP+42), p2=(PLAN_LEFT+Y_CAP_END, PLAN_TOP+42),
                       dimstyle="AEROFORGE").render()
    msp.add_aligned_dim(p1=(PLAN_LEFT-12, PLAN_TOP),
                        p2=(PLAN_LEFT-12, PLAN_TOP-root_ec),
                        distance=5, dimstyle="AEROFORGE").render()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTIONS
    # ═══════════════════════════════════════════════════════════════════════
    SX = 370.0
    for sy, ys, lab in [
        (350, 0,   "SEC A — ROOT y=0 (elev chord=40.2mm)"),
        (300, 100, "SEC B — y=100 (elev chord=32.1mm)"),
        (250, 200, "SEC C — y=200 (horn zone)"),
    ]:
        c_full = chord_at(ys)
        if c_full < 1: continue
        tr = t_ratio(ys); lx = le_x(ys)
        ec = elev_chord_at(ys)
        hf = (X_HINGE - lx) / c_full

        msp.add_text(lab, height=2.3, dxfattribs={"layer": "TEXT"}).set_placement((SX, sy+10))

        # Full airfoil context (fwd of hinge = thin/hidden)
        for i in range(60):
            xc1 = TE_TRUNC*i/60; xc2 = TE_TRUNC*(i+1)/60
            y1 = naca4_yt(xc1,tr)*c_full; y2 = naca4_yt(xc2,tr)*c_full
            lay = "OUTLINE" if xc1 >= hf else "HIDDEN"
            msp.add_line((SX+xc1*c_full,sy+y1),(SX+xc2*c_full,sy+y2), dxfattribs={"layer":lay})
            msp.add_line((SX+xc1*c_full,sy-y1),(SX+xc2*c_full,sy-y2), dxfattribs={"layer":lay})

        yt0 = naca4_yt(0.005,tr)*c_full
        msp.add_line((SX,sy-yt0),(SX,sy+yt0), dxfattribs={"layer":"HIDDEN"})
        yte = naca4_yt(TE_TRUNC,tr)*c_full
        msp.add_line((SX+TE_TRUNC*c_full,sy-yte),(SX+TE_TRUNC*c_full,sy+yte),
                     dxfattribs={"layer":"OUTLINE"})

        # Hinge line
        yth = naca4_yt(hf,tr)*c_full
        msp.add_line((SX+hf*c_full,sy-yth),(SX+hf*c_full,sy+yth),
                     dxfattribs={"layer":"CENTERLINE"})
        msp.add_text("hinge", height=1.3, dxfattribs={"layer":"TEXT"}).set_placement(
            (SX+hf*c_full-3, sy+yth+1.5))

        if ec > 0:
            msp.add_text(f"elev={ec:.1f}mm", height=1.8,
                         dxfattribs={"layer":"TEXT"}).set_placement((SX, sy-8))

        # Stiffener bore
        sf = (X_STIFF-lx)/c_full if c_full>0 else 999
        if hf < sf < TE_TRUNC and ys <= Y_STIFF_END:
            msp.add_circle((SX+sf*c_full, sy), 0.5, dxfattribs={"layer":"SPAR"})

    # ═══════════════════════════════════════════════════════════════════════
    # NOTES
    # ═══════════════════════════════════════════════════════════════════════
    notes = [
        "NOTES:",
        "1. All dims mm. 1:1. Right elevator = mirror.",
        "2. Hinge at X=74.75 (fixed, perpendicular to fuselage CL).",
        "3. Root chord 40.25mm, tapers to 0 at y≈204mm.",
        "4. STIFFENER: 1mm CF at X=92.0, 150mm from root face, CA. 2 separate rods.",
        "5. ROOT BEVEL: 22° upper / 27° lower (for -20°/+25° deflection).",
        "6. ROOT GAP: 4mm clearance each side from VStab fin (8mm total).",
        "7. TIP HORN (y=195→214): integral with elevator shell.",
        "   Forward extension: parabolic 0→15mm fwd (y=195→205), blends to full LE (y=210).",
        "   At y=210 horn IS the entire chord (32mm). C1 tip cap y=210→214.",
        "8. TUNGSTEN: 10×6.5×1.5mm pocket at y=195-205, 8mm fwd hinge. 0.50g W putty.",
        "9. PUSHROD: Z-bend Ø1.6mm hole at y=200, 12mm fwd hinge (10/14mm alternates).",
        "10. HINGE STRIP: PETG knuckle strip on LE face. Last knuckle y=200.",
        "    Wire bends 90° at y=203 into tip pocket.",
        "11. Wall: 0.40mm vase (main), 0.55mm horn zone. Print hinge face down.",
    ]
    for i, n in enumerate(notes):
        msp.add_text(n, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((25, 165-i*4.3))

    save_dxf_and_png(doc, "cad/components/empennage/Elevator_Left/Elevator_Left_drawing.dxf", dpi=300)
    print("Elevator_Left done.")

if __name__ == "__main__":
    main()
