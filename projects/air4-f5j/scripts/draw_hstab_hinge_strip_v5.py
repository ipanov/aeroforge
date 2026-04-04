"""
HStab Hinge Strip Drawing — v5 Design Consensus
================================================
PETG knuckle strip bonded to stab TE face (lower surface).
Same drawing covers all 4 strips (2 on stab, 2 on elevator — same dimensions).
Knuckle OD: 1.2mm, ID: 0.6mm. Spacing: 8mm c-t-c. Strip: 200mm x 2mm x 1.2mm.
Stab strips and elevator strips interleave when mated.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# === Hinge strip parameters (v5) ===
STRIP_LENGTH = 200.0   # mm (per half — spans from root to y=200mm)
STRIP_WIDTH = 2.0      # mm (span of flat base strip)
STRIP_THICK = 1.2      # mm (thickness of flat base)
KNUCKLE_OD = 1.2       # mm outer diameter
KNUCKLE_ID = 0.6       # mm inner diameter (wire bore)
KNUCKLE_SPACING = 8.0  # mm center-to-center
KNUCKLE_LENGTH = 4.0   # mm (each knuckle protrusion length)
N_KNUCKLES = int(STRIP_LENGTH / KNUCKLE_SPACING)  # ~25 knuckles


def main():
    doc = setup_drawing(
        title="HStab_Hinge_Strip",
        subtitle=(
            "PETG hinge knuckle strip. 4 strips total per assembly "
            "(2 on stab TE, 2 on elevator LE — all identical). "
            "Stab + elevator strips interleave when mated."
        ),
        material="PETG | 100% solid | No vase mode | 240°C | Flat, knuckles up",
        mass="0.50g each (2.00g total, 4 strips)",
        scale="2:1",
        sheet_size="A3",
        status="FOR APPROVAL",
        revision="v5",
    )
    msp = doc.modelspace()

    # =========================================================
    # SIDE VIEW (looking along hinge axis — shows cross-section)
    # Strip base: rectangle. Knuckle: circle (hollow).
    # =========================================================
    scale = 2.0   # draw at 2x for visibility
    sv_ox = 30.0
    sv_oy = 120.0

    msp.add_text("SIDE VIEW — CROSS-SECTION AT KNUCKLE (2:1 scale)",
                 height=4.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (sv_ox, sv_oy + KNUCKLE_OD * scale + 10))

    # Flat strip base (rectangle, side view)
    W = STRIP_WIDTH * scale
    T = STRIP_THICK * scale
    msp.add_lwpolyline(
        [(sv_ox, sv_oy), (sv_ox + W, sv_oy),
         (sv_ox + W, sv_oy + T), (sv_ox, sv_oy + T), (sv_ox, sv_oy)],
        dxfattribs={"layer": "OUTLINE"},
    )

    # Knuckle circle (on top of base strip)
    knuckle_cx = sv_ox + W / 2
    knuckle_cy = sv_oy + T + KNUCKLE_OD * scale / 2

    msp.add_circle((knuckle_cx, knuckle_cy), KNUCKLE_OD * scale / 2,
                   dxfattribs={"layer": "OUTLINE"})
    msp.add_circle((knuckle_cx, knuckle_cy), KNUCKLE_ID * scale / 2,
                   dxfattribs={"layer": "SPAR"})

    # Centerline through bore
    msp.add_line((knuckle_cx - KNUCKLE_OD * scale, knuckle_cy),
                 (knuckle_cx + KNUCKLE_OD * scale, knuckle_cy),
                 dxfattribs={"layer": "CENTERLINE"})

    # Dimensions
    msp.add_linear_dim(
        base=(sv_ox + W / 2, sv_oy - 8),
        p1=(sv_ox, sv_oy), p2=(sv_ox + W, sv_oy),
        dimstyle="AEROFORGE",
    ).render()
    msp.add_linear_dim(
        base=(sv_ox - 8, sv_oy + T / 2),
        p1=(sv_ox, sv_oy), p2=(sv_ox, sv_oy + T),
        angle=90,
        dimstyle="AEROFORGE",
    ).render()
    msp.add_aligned_dim(
        p1=(sv_ox + W + 8, knuckle_cy - KNUCKLE_OD * scale / 2),
        p2=(sv_ox + W + 8, knuckle_cy + KNUCKLE_OD * scale / 2),
        distance=4,
        dimstyle="AEROFORGE",
    ).render()
    msp.add_aligned_dim(
        p1=(sv_ox + W + 20, knuckle_cy - KNUCKLE_ID * scale / 2),
        p2=(sv_ox + W + 20, knuckle_cy + KNUCKLE_ID * scale / 2),
        distance=4,
        dimstyle="AEROFORGE",
    ).render()

    # Labels
    msp.add_text(f"Strip base\n{STRIP_WIDTH}×{STRIP_THICK}mm",
                 height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (sv_ox + W + 5, sv_oy + T / 2))
    msp.add_text(f"Knuckle\nOD={KNUCKLE_OD}mm\nID={KNUCKLE_ID}mm",
                 height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (sv_ox + W + 5, knuckle_cy + KNUCKLE_OD * scale / 2 + 2))
    msp.add_text("Wire bore\n(0.5mm music wire passes through)",
                 height=2.0, dxfattribs={"layer": "SPAR"}).set_placement(
        (knuckle_cx + KNUCKLE_ID * scale + 2, knuckle_cy - 2))

    # =========================================================
    # FRONT VIEW (looking from TE toward LE — shows strip length)
    # Strip: long rectangle. Knuckles: small rectangles at spacing.
    # =========================================================
    fv_ox = 30.0
    fv_oy = 60.0

    msp.add_text("FRONT VIEW — STRIP LENGTH (1:2 scale shown — strip is 200mm long)",
                 height=4.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (fv_ox, fv_oy + 14))

    draw_scale = 0.5  # 1:2 for length view
    L = STRIP_LENGTH * draw_scale
    T2 = STRIP_THICK * scale  # keep cross-section at 2x

    # Base strip
    msp.add_lwpolyline(
        [(fv_ox, fv_oy), (fv_ox + L, fv_oy),
         (fv_ox + L, fv_oy + T2), (fv_ox, fv_oy + T2), (fv_ox, fv_oy)],
        dxfattribs={"layer": "OUTLINE"},
    )

    # Knuckles (drawn as small rectangles on top)
    kh = KNUCKLE_LENGTH * draw_scale
    kw = KNUCKLE_OD * scale
    for k in range(N_KNUCKLES):
        kx = fv_ox + (k * KNUCKLE_SPACING + KNUCKLE_SPACING / 2) * draw_scale
        ky = fv_oy + T2
        msp.add_lwpolyline(
            [(kx - kw / 2, ky), (kx + kw / 2, ky),
             (kx + kw / 2, ky + kh), (kx - kw / 2, ky + kh),
             (kx - kw / 2, ky)],
            dxfattribs={"layer": "OUTLINE"},
        )
        # Bore hole center dot
        msp.add_circle((kx, ky + kh / 2), KNUCKLE_ID * scale / 2,
                       dxfattribs={"layer": "SPAR"})

    # Length dimension
    msp.add_linear_dim(
        base=(fv_ox + L / 2, fv_oy - 10),
        p1=(fv_ox, fv_oy), p2=(fv_ox + L, fv_oy),
        dimstyle="AEROFORGE",
    ).render()

    # Spacing dimension (first two knuckles)
    k0 = fv_ox + KNUCKLE_SPACING / 2 * draw_scale
    k1 = fv_ox + (KNUCKLE_SPACING + KNUCKLE_SPACING / 2) * draw_scale
    msp.add_linear_dim(
        base=((k0 + k1) / 2, fv_oy + T2 + kh + 10),
        p1=(k0, fv_oy), p2=(k1, fv_oy),
        dimstyle="AEROFORGE",
    ).render()
    msp.add_text(f"@ {KNUCKLE_SPACING}mm c-t-c ({N_KNUCKLES} knuckles)",
                 height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        ((k0 + k1) / 2 - 5, fv_oy + T2 + kh + 14))

    # =========================================================
    # INTERLEAVE DETAIL — mating stab + elevator strips
    # =========================================================
    id_ox = 30.0
    id_oy = 20.0

    msp.add_text("INTERLEAVE DETAIL — Stab strip (S) + Elevator strip (E) mated (4:1 scale)",
                 height=4.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (id_ox, id_oy + 18))

    is_scale = 4.0
    gap = 0.3  # mm gap between knuckles
    sp = KNUCKLE_SPACING * is_scale

    # Show 3 knuckle pairs
    for k in range(3):
        cx = id_ox + k * sp + sp / 2
        # Stab knuckle (S)
        msp.add_circle((cx, id_oy + 6), KNUCKLE_OD * is_scale / 2,
                       dxfattribs={"layer": "OUTLINE"})
        msp.add_circle((cx, id_oy + 6), KNUCKLE_ID * is_scale / 2,
                       dxfattribs={"layer": "SPAR"})
        msp.add_text("S", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
            (cx - 1, id_oy + 10))

        # Elevator knuckle (E) — offset by half spacing
        cx_e = id_ox + k * sp + sp
        if k < 2:
            msp.add_circle((cx_e, id_oy + 6), KNUCKLE_OD * is_scale / 2,
                           dxfattribs={"layer": "SECTION"})
            msp.add_circle((cx_e, id_oy + 6), KNUCKLE_ID * is_scale / 2,
                           dxfattribs={"layer": "SPAR"})
            msp.add_text("E", height=2.5, dxfattribs={"layer": "SECTION"}).set_placement(
                (cx_e - 1, id_oy + 10))

    # Wire centerline through all
    msp.add_line((id_ox, id_oy + 6),
                 (id_ox + 2.5 * sp, id_oy + 6),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("0.5mm music wire (continuous, both halves)",
                 height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (id_ox, id_oy - 4))

    # =========================================================
    # NOTES
    # =========================================================
    notes = [
        "NOTES:",
        "1. All dimensions in mm. Drawing shows ONE strip; 4 identical strips per assembly.",
        "2. Stab strips bond to stab TE face (lower surface). Elevator strips bond to elevator LE face.",
        "3. Bond with thin CA (cyanoacrylate). Clamp flat until cured.",
        "4. Interleave: stab and elevator knuckles alternate — gap 0.3mm between adjacent knuckles.",
        "5. Upper surface gap: 0.3mm (knuckle buried in turbulent BL — drag negligible).",
        "6. Lower surface protrusion: 1.2mm (42% of turbulent BL — <0.05 drag counts).",
        "7. Music wire (0.5mm, ASTM A228): thread from one tip through all knuckles to other tip.",
        "   Bend wire 90° at each tip (y=203mm) and tuck into elevator tip horn pocket.",
        "8. Material: PETG 100% solid (not vase mode). Print flat, knuckles up.",
        "9. Hinge OD=1.2mm / ID=0.6mm. Wire is 0.5mm — free rotation, essentially zero friction.",
    ]
    nx, ny = 30.0, -30.0
    for i, note in enumerate(notes):
        msp.add_text(note, height=2.2, dxfattribs={"layer": "TEXT"}).set_placement(
            (nx, ny - i * 5.5))

    out = "cad/components/empennage/HStab_Hinge_Strip_Left/HStab_Hinge_Strip_Left_drawing.dxf"
    save_dxf_and_png(doc, out)
    print("HStab_Hinge_Strip drawing complete.")


if __name__ == "__main__":
    main()
