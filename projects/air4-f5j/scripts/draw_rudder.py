"""
Rudder Drawing — 2D Technical Drawing (DXF + PNG)
===================================================
COMPONENT = rudder shell ONLY (hinge face to TE).
Sections show ONLY rudder geometry — bull-nose LE to TE.
Uses real HT-14/HT-12 airfoil data.

The rudder is a vertical control surface on the VStab trailing edge.
Drawing shows:
  - Side view (planform): rudder outline from root (Z=0) to tip (Z=165)
  - Cross-sections at root, mid, and tip
  - Bull-nose / hinge saddle detail
  - Key dimensions and annotations

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/draw_rudder.py
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from rudder_geometry import *
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# Drawing layout positions
PLAN_LEFT = 50.0    # X offset for planform view
PLAN_BOT = 60.0     # Y offset for planform view (bottom)

SEC_X = 250.0       # X start for cross-sections
SEC_SCALE = 3.0     # Scale factor for cross-sections (they are small, need enlarging)


def main():
    doc = setup_drawing(
        title="Rudder",
        subtitle="Rudder shell (hinge face to TE). Bull-nose concealed hinge. VStab aft 35-38%.",
        material="LW-PLA | Vase 0.40mm (0.55mm bull-nose) | 230C | Print hinge face down",
        mass="5.96g", scale="1:1 (planform) / 3:1 (sections)", sheet_size="A2",
        status="FOR APPROVAL", revision="v1",
        orientation_labels={"fwd": "FWD", "inbd": "DOWN"},
    )
    msp = doc.modelspace()

    # ═══════════════════════════════════════════════════════════
    # SIDE VIEW (PLANFORM) — Rudder outline, 1:1 scale
    # ═══════════════════════════════════════════════════════════
    # Convention: X = chordwise (hinge at left, TE at right)
    #             Y_drawing = spanwise (root at bottom, tip at top)

    def P(cx, cz):
        """Map rudder local coords to drawing coords.
        cx = chordwise from hinge (0=hinge, positive=toward TE, negative=bull-nose fwd)
        cz = spanwise height (0=root, 165=tip)
        """
        return (PLAN_LEFT + cx, PLAN_BOT + cz)

    msp.add_text("SIDE VIEW — RUDDER COMPONENT (1:1)", height=4.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (PLAN_LEFT - 10, PLAN_BOT + VSTAB_HEIGHT + 15))

    # FWD arrow (points left toward VStab LE)
    ax, ay = P(10, 5)
    msp.add_line((ax + 20, ay), (ax, ay), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ax, ay), (ax + 3, ay + 2), dxfattribs={"layer": "ORIENTATION"})
    msp.add_line((ax, ay), (ax + 3, ay - 2), dxfattribs={"layer": "ORIENTATION"})
    msp.add_text("FWD", height=3.0, dxfattribs={"layer": "ORIENTATION"}).set_placement(
        (ax - 4, ay + 3))

    # === Planform outline ===

    # Hinge line (left edge of rudder component — straight vertical)
    msp.add_line(P(0, 0), P(0, VSTAB_HEIGHT), dxfattribs={"layer": "OUTLINE"})

    # Root face (bottom)
    root_rc = rudder_chord(0)
    root_bn = bull_nose_depth(0)
    msp.add_line(P(-root_bn, 0), P(root_rc, 0), dxfattribs={"layer": "OUTLINE"})

    # Bull-nose curve (extends forward of hinge, tapers to zero)
    n_bull = 100
    bull_pts = []
    for i in range(n_bull + 1):
        z = BULL_NOSE_FADE_Z * i / n_bull
        depth = bull_nose_depth(z)
        bull_pts.append(P(-depth, z))

    # Connect root face to bull-nose start
    msp.add_line(P(-root_bn, 0), bull_pts[0], dxfattribs={"layer": "OUTLINE"})
    for i in range(len(bull_pts) - 1):
        msp.add_line(bull_pts[i], bull_pts[i + 1], dxfattribs={"layer": "OUTLINE"})
    # Connect bull-nose end to hinge line
    msp.add_line(bull_pts[-1], P(0, BULL_NOSE_FADE_Z), dxfattribs={"layer": "OUTLINE"})

    # TE curve (trailing edge varies with taper)
    n_te = 120
    te_pts = []
    for i in range(n_te + 1):
        z = VSTAB_HEIGHT * i / n_te
        rc = rudder_chord(z)
        if rc >= 0.3:
            te_pts.append(P(rc, z))
    for i in range(len(te_pts) - 1):
        msp.add_line(te_pts[i], te_pts[i + 1], dxfattribs={"layer": "OUTLINE"})

    # Tip closure (connect last TE point to hinge line at tip)
    if te_pts:
        msp.add_line(te_pts[-1], P(0, VSTAB_HEIGHT), dxfattribs={"layer": "OUTLINE"})

    # === Internal features ===

    # Hinge wire bore (centerline along hinge)
    msp.add_line(P(0, 0), P(0, VSTAB_HEIGHT), dxfattribs={"layer": "CENTERLINE"})

    # Rib positions (dashed lines)
    for rz in RIB_POSITIONS:
        rc = rudder_chord(rz)
        msp.add_line(P(0, rz), P(rc, rz), dxfattribs={"layer": "SECTION"})
        msp.add_text(f"RIB Z={rz:.0f}", height=1.5,
                     dxfattribs={"layer": "TEXT"}).set_placement(P(rc + 3, rz - 1))

    # PETG sleeve positions (5 sleeves on rudder side, at 20mm intervals, interleaved)
    # Rudder sleeves at Z = 10, 30, 50, 70, 90 (approximately)
    sleeve_positions = [10, 30, 50, 70, 90]
    for sz in sleeve_positions:
        px, py = P(0, sz)
        msp.add_circle((px, py), 0.6, dxfattribs={"layer": "SPAR"})

    msp.add_text("PETG SLEEVES (5x)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(P(-8, 50))

    # Pushrod hole
    px, py = P(10, PUSHROD_Z)
    msp.add_circle((px, py), PUSHROD_BORE_D / 2, dxfattribs={"layer": "SPAR"})
    msp.add_text(f"PUSHROD D{PUSHROD_BORE_D}  Z={PUSHROD_Z:.0f}mm", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(P(13, PUSHROD_Z - 1))

    # === Labels ===
    msp.add_text("HINGE FACE\n(bull-nose forward)", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(P(-15, 120))
    msp.add_text("TE", height=3.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(P(root_rc + 5, 30))
    msp.add_text("BULL-NOSE\n(into VStab saddle)", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(P(-18, 80))
    msp.add_text("RUDDER SHELL", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(P(root_rc / 3, 100))
    msp.add_text("ROOT (Z=0)", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(P(root_rc / 3, -8))
    msp.add_text(f"TIP (Z={VSTAB_HEIGHT:.0f})", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(P(-5, VSTAB_HEIGHT + 3))

    # === Dimensions ===
    # Root chord dimension
    p1 = P(-root_bn, 0)
    p2 = P(root_rc, 0)
    msp.add_linear_dim(
        base=(PLAN_LEFT + root_rc / 2, PLAN_BOT - 10),
        p1=p1, p2=p2,
        dimstyle="AEROFORGE",
    ).render()

    # Height dimension
    p1h = P(root_rc + 8, 0)
    p2h = P(root_rc + 8, VSTAB_HEIGHT)
    msp.add_aligned_dim(p1=p1h, p2=p2h, distance=5,
                        dimstyle="AEROFORGE").render()

    # Tip chord dimension
    tip_rc = rudder_chord(VSTAB_HEIGHT)
    p1t = P(0, VSTAB_HEIGHT)
    p2t = P(tip_rc, VSTAB_HEIGHT)
    msp.add_linear_dim(
        base=(PLAN_LEFT + tip_rc / 2, PLAN_BOT + VSTAB_HEIGHT + 8),
        p1=p1t, p2=p2t,
        dimstyle="AEROFORGE",
    ).render()

    # Bull-nose depth at root
    msp.add_linear_dim(
        base=(PLAN_LEFT - root_bn / 2, PLAN_BOT - 18),
        p1=P(-root_bn, 0), p2=P(0, 0),
        dimstyle="AEROFORGE",
    ).render()

    # ═══════════════════════════════════════════════════════════
    # CROSS-SECTIONS at 3:1 scale (rudder portion only)
    # ═══════════════════════════════════════════════════════════

    sections = [
        (340, 0,    "SEC A -- ROOT Z=0 (rudder: hinge to TE)"),
        (260, 82,   "SEC B -- Z=82 (mid-height, rudder only)"),
        (180, 150,  "SEC C -- Z=150 (near tip, rudder only)"),
    ]

    for sy, zs, lab in sections:
        vc = vstab_chord(zs)
        if vc < 1:
            continue

        hf = hinge_frac(zs)
        te_frac = hf + rudder_frac(zs) * TE_TRUNC
        te_frac = min(te_frac, 1.0)
        rc = rudder_chord(zs)
        if rc < 1:
            continue

        msp.add_text(lab, height=2.3, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X, sy + 18))
        msp.add_text(f"rudder chord={rc:.1f}mm  VStab chord={vc:.1f}mm",
                     height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X, sy + 13))
        msp.add_text(f"(3:1 scale)", height=1.5,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X, sy + 10))

        # Get airfoil data for rudder portion only
        upper_pts, lower_pts = airfoil_section_points(
            zs, x_start_frac=hf, x_end_frac=te_frac, n_pts=60)

        if not upper_pts:
            continue

        # Offset so hinge face is at SEC_X
        x_offset = upper_pts[0][0]

        # Draw upper surface
        for i in range(len(upper_pts) - 1):
            x1 = SEC_X + (upper_pts[i][0] - x_offset) * SEC_SCALE
            y1 = sy + upper_pts[i][1] * SEC_SCALE
            x2 = SEC_X + (upper_pts[i + 1][0] - x_offset) * SEC_SCALE
            y2 = sy + upper_pts[i + 1][1] * SEC_SCALE
            msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "OUTLINE"})

        # Draw lower surface
        for i in range(len(lower_pts) - 1):
            x1 = SEC_X + (lower_pts[i][0] - x_offset) * SEC_SCALE
            y1 = sy + lower_pts[i][1] * SEC_SCALE
            x2 = SEC_X + (lower_pts[i + 1][0] - x_offset) * SEC_SCALE
            y2 = sy + lower_pts[i + 1][1] * SEC_SCALE
            msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "OUTLINE"})

        # Hinge face (left edge of section)
        yu_h = upper_pts[0][1] * SEC_SCALE
        yl_h = lower_pts[0][1] * SEC_SCALE
        msp.add_line((SEC_X, sy + yl_h), (SEC_X, sy + yu_h),
                     dxfattribs={"layer": "SECTION"})
        msp.add_text("hinge\nface", height=1.3, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X - 10, sy + yu_h + 1))

        # TE closure
        yu_te = upper_pts[-1][1] * SEC_SCALE
        yl_te = lower_pts[-1][1] * SEC_SCALE
        x_te = SEC_X + (upper_pts[-1][0] - x_offset) * SEC_SCALE
        msp.add_line((x_te, sy + yl_te), (x_te, sy + yu_te),
                     dxfattribs={"layer": "OUTLINE"})

        # Centerline
        msp.add_line((SEC_X - 5, sy), (x_te + 5, sy),
                     dxfattribs={"layer": "CENTERLINE"})

        # Chord dimension
        msp.add_linear_dim(
            base=(SEC_X + rc * SEC_SCALE / 2, sy - 10),
            p1=(SEC_X, sy), p2=(x_te, sy),
            dimstyle="AEROFORGE",
        ).render()

        # Thickness annotation
        thickness_mm = (upper_pts[len(upper_pts) // 4][1] -
                        lower_pts[len(lower_pts) // 4][1])
        msp.add_text(f"t={thickness_mm:.1f}mm at 25%c",
                     height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
            (SEC_X + rc * SEC_SCALE / 4, sy + yu_h + 5))

    # ═══════════════════════════════════════════════════════════
    # NOTES
    # ═══════════════════════════════════════════════════════════
    notes = [
        "NOTES:",
        "1. All dims mm. Planform 1:1, sections 3:1.",
        "2. This component = RUDDER SHELL ONLY (hinge face to TE).",
        "   Does NOT include VStab fixed fin. Sections show rudder geometry only.",
        "3. VStab airfoil: HT-14 (root) blending to HT-12 (tip).",
        f"4. Hinge at {HINGE_FRAC_ROOT*100:.0f}% root chord / "
        f"{HINGE_FRAC_TIP*100:.0f}% tip chord.",
        f"5. Root rudder chord = {rudder_chord(0):.1f}mm "
        f"({RUDDER_FRAC_ROOT*100:.0f}% of {VSTAB_ROOT_CHORD:.0f}mm VStab).",
        f"6. Tip rudder chord = {rudder_chord(VSTAB_HEIGHT):.1f}mm "
        f"({RUDDER_FRAC_TIP*100:.0f}% of {VSTAB_TIP_CHORD:.0f}mm VStab).",
        f"7. BULL-NOSE: extends {BULL_NOSE_ROOT:.1f}mm forward of hinge at root.",
        f"   Tapers to 0 at Z={BULL_NOSE_FADE_Z:.0f}mm. Mates with VStab saddle.",
        "8. HINGE WIRE: 0.5mm music wire in 5x PETG sleeves, concealed.",
        f"9. PUSHROD: D{PUSHROD_BORE_D}mm hole at Z={PUSHROD_Z:.0f}mm, "
        "Z-bend attachment.",
        "10. 3 internal ribs at Z=41, 83, 124mm (0.6mm LW-PLA).",
        "11. Gap seal: 0.05mm Mylar + 3M 468MP, 170x12mm.",
        f"12. Wall: {WALL}mm vase (main), {BULL_NOSE_WALL}mm bull-nose.",
        "    Print hinge face down.",
        "13. Deflection: +/-30 deg.",
    ]
    for i, n in enumerate(notes):
        msp.add_text(n, height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(
            (25, 50 - i * 4.3))

    # ═══════════════════════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════════════════════
    out_path = "cad/components/empennage/Rudder/Rudder_drawing.dxf"
    save_dxf_and_png(doc, out_path, dpi=300)
    print(f"\nRudder drawing complete.")
    print(f"  Root chord: {rudder_chord(0):.1f}mm (+ {bull_nose_depth(0):.1f}mm bull-nose)")
    print(f"  Tip chord:  {rudder_chord(VSTAB_HEIGHT):.1f}mm")
    print(f"  Height:     {VSTAB_HEIGHT:.0f}mm")
    print(f"  Planform area: ~{(rudder_chord(0) + rudder_chord(VSTAB_HEIGHT)) / 2 * VSTAB_HEIGHT / 100:.1f} cm^2")


if __name__ == "__main__":
    main()
