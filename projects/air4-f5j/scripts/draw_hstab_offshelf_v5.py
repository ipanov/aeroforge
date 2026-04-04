"""
HStab Off-Shelf Components — v5 Design Consensus
=================================================
Creates individual DXF drawings for:
  - HStab_Main_Spar: 3mm CF tube (3/2mm OD/ID), 372mm
  - HStab_Rear_Spar: 1.5mm CF rod, 420mm
  - Elevator_Stiffener_Left (and Right): 1mm CF rod, 150mm
  - Hinge_Wire: 0.5mm music wire, 440mm + 90° bends at both tips
Each is saved to its own component folder.
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.dxf_utils import setup_drawing, save_dxf_and_png


def draw_rod(doc, ox, oy, length, od, bore=None, label="", material="", notes=None, scale=1.0):
    """Draw a simple rod (rectangle in side view + cross-section circle)."""
    msp = doc.modelspace()
    L = length * scale
    D = od * scale

    # Side view: rectangle
    msp.add_lwpolyline(
        [(ox, oy - D / 2), (ox + L, oy - D / 2),
         (ox + L, oy + D / 2), (ox, oy + D / 2), (ox, oy - D / 2)],
        dxfattribs={"layer": "OUTLINE"},
    )

    # Centerline
    msp.add_line((ox - 5, oy), (ox + L + 5, oy),
                 dxfattribs={"layer": "CENTERLINE"})

    # Length dimension
    msp.add_linear_dim(
        base=(ox + L / 2, oy - D / 2 - 10),
        p1=(ox, oy - D / 2), p2=(ox + L, oy - D / 2),
        dimstyle="AEROFORGE",
    ).render()

    # OD dimension
    msp.add_aligned_dim(
        p1=(ox + L + 12, oy - D / 2),
        p2=(ox + L + 12, oy + D / 2),
        distance=5,
        dimstyle="AEROFORGE",
    ).render()

    # Cross-section circle (at right end)
    cs_ox = ox + L + 35
    msp.add_circle((cs_ox, oy), od * scale / 2, dxfattribs={"layer": "OUTLINE"})
    if bore:
        msp.add_circle((cs_ox, oy), bore * scale / 2, dxfattribs={"layer": "SPAR"})
    msp.add_line((cs_ox - od * scale, oy), (cs_ox + od * scale, oy),
                 dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((cs_ox, oy - od * scale), (cs_ox, oy + od * scale),
                 dxfattribs={"layer": "CENTERLINE"})

    msp.add_text("CROSS-SECTION", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (cs_ox - 12, oy + od * scale + 5))
    msp.add_text(f"Ø{od}mm OD", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (cs_ox + od * scale + 3, oy + 2))
    if bore:
        msp.add_text(f"Ø{bore}mm ID", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
            (cs_ox + od * scale + 3, oy - 4))

    msp.add_text(label, height=4.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox, oy + D / 2 + 10))
    msp.add_text(material, height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox, oy + D / 2 + 5))

    if notes:
        for i, note in enumerate(notes):
            msp.add_text(note, height=2.2, dxfattribs={"layer": "TEXT"}).set_placement(
                (ox, oy - D / 2 - 22 - i * 5.5))


# ─────────────────────────────────────────────────────────────────────────────
# HStab_Main_Spar: 3mm CF tube, 372mm
# ─────────────────────────────────────────────────────────────────────────────
def draw_main_spar():
    doc = setup_drawing(
        title="HStab_Main_Spar",
        subtitle="3mm CF tube (3.0mm OD / 2.0mm ID). Full assembly = 372mm (both halves share single tube).",
        material="Carbon fiber tube | 3/2mm OD/ID | Off-shelf",
        mass="2.29g",
        scale="1:2",
        sheet_size="A3",
        status="FOR APPROVAL",
        revision="v5",
    )
    msp = doc.modelspace()
    msp.add_text("SIDE VIEW (1:2 scale)", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (30, 200))

    draw_rod(
        doc, ox=30, oy=185, length=372, od=3.0, bore=2.0,
        label="HStab_Main_Spar — 3mm CF TUBE",
        material="Carbon fiber tube, 3.0mm OD / 2.0mm ID | 372mm overall",
        notes=[
            "NOTES:",
            "1. Off-shelf component. Do not modify. Cut to 372mm.",
            "2. Passes through LEFT stab (186mm) + VStab fin hole + RIGHT stab (186mm) = 372mm total.",
            "3. Bore in stab: Ø3.1mm (0.1mm clearance). Friction fit; tapers to Ø3.05mm at bore end.",
            "4. VStab fin hole: Ø3.1mm bore with PETG sleeve.",
            "5. Spar position: X=35.0mm from root LE (30.4% root chord).",
            "6. Terminates at y=186mm each side (airfoil too thin for 3mm tube beyond this point).",
            "7. Tip (y=186-215mm per side) is shell-only — no spar.",
        ],
        scale=0.5,
    )

    save_dxf_and_png(doc, "cad/components/empennage/HStab_Main_Spar/HStab_Main_Spar_drawing.dxf")
    print("HStab_Main_Spar drawing complete.")


# ─────────────────────────────────────────────────────────────────────────────
# HStab_Rear_Spar: 1.5mm CF rod, 420mm
# ─────────────────────────────────────────────────────────────────────────────
def draw_rear_spar():
    doc = setup_drawing(
        title="HStab_Rear_Spar",
        subtitle="1.5mm CF rod, 420mm (both halves, single rod through VStab fin).",
        material="Carbon fiber rod | 1.5mm OD | Off-shelf",
        mass="1.15g",
        scale="1:2",
        sheet_size="A3",
        status="FOR APPROVAL",
        revision="v5",
    )
    msp = doc.modelspace()
    msp.add_text("SIDE VIEW (1:2 scale)", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (30, 200))

    draw_rod(
        doc, ox=30, oy=185, length=420, od=1.5, bore=None,
        label="HStab_Rear_Spar — 1.5mm CF ROD",
        material="Carbon fiber rod, 1.5mm OD | 420mm overall | Solid",
        notes=[
            "NOTES:",
            "1. Off-shelf component. Do not modify. Cut to 420mm.",
            "2. Passes through LEFT stab (210mm) + VStab fin hole + RIGHT stab (210mm) = 420mm total.",
            "3. Bore in stab: Ø1.6mm (0.1mm clearance). Friction fit + CA at entry.",
            "4. Spar position: X=69.0mm from root LE (60.0% root chord at root).",
            "5. Terminates at y=210mm each side (airfoil too thin for 1.5mm rod beyond y=205mm).",
        ],
        scale=0.5,
    )

    save_dxf_and_png(doc, "cad/components/empennage/HStab_Rear_Spar/HStab_Rear_Spar_drawing.dxf")
    print("HStab_Rear_Spar drawing complete.")


# ─────────────────────────────────────────────────────────────────────────────
# Elevator_Stiffener_Left (and Right): 1mm CF rod, 150mm each
# ─────────────────────────────────────────────────────────────────────────────
def draw_elevator_stiffener():
    doc = setup_drawing(
        title="Elevator_Stiffener_Left",
        subtitle=(
            "1mm CF rod, 150mm. One per elevator half (2 total). "
            "Right stiffener = identical. Does NOT pass through VStab fin."
        ),
        material="Carbon fiber rod | 1.0mm OD | Off-shelf",
        mass="0.19g each (0.38g total)",
        scale="1:1",
        sheet_size="A3",
        status="FOR APPROVAL",
        revision="v5",
    )
    msp = doc.modelspace()
    msp.add_text("SIDE VIEW (1:1 scale)", height=3.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (30, 200))

    draw_rod(
        doc, ox=30, oy=185, length=150, od=1.0, bore=None,
        label="Elevator_Stiffener_Left — 1mm CF ROD",
        material="Carbon fiber rod, 1.0mm OD | 150mm | Solid",
        notes=[
            "NOTES:",
            "1. Off-shelf component. Do not modify. Cut to 150mm.",
            "2. TWO separate rods — one per elevator half. Does NOT pass through VStab fin.",
            "3. Inserted from ROOT FACE of each elevator half (push in 150mm from root face).",
            "4. Position: X=92.0mm from root LE = 17.25mm from hinge line toward TE.",
            "   At root: 80.0% chord. Rod terminates at y=150mm (airfoil too thin beyond).",
            "5. Bond with thin CA. Wipe any excess before insertion.",
            "6. Rod is at 80% chord at root — deep in elevator, provides torsional stiffness.",
        ],
        scale=1.0,
    )

    save_dxf_and_png(
        doc,
        "cad/components/empennage/Elevator_Stiffener_Left/Elevator_Stiffener_Left_drawing.dxf",
    )
    print("Elevator_Stiffener_Left drawing complete.")


# ─────────────────────────────────────────────────────────────────────────────
# Hinge_Wire: 0.5mm music wire, 440mm + 90° bends at tips
# ─────────────────────────────────────────────────────────────────────────────
def draw_hinge_wire():
    doc = setup_drawing(
        title="Hinge_Wire",
        subtitle=(
            "0.5mm music wire (ASTM A228). 440mm length. "
            "90° bends at both tips, tucked into elevator tip horn pockets."
        ),
        material="Music wire | ASTM A228 spring steel | 0.5mm dia | Off-shelf",
        mass="0.68g",
        scale="1:2",
        sheet_size="A3",
        status="FOR APPROVAL",
        revision="v5",
    )
    msp = doc.modelspace()

    # =========================================================
    # SIDE VIEW: straight wire with 90° bends at tips (1:2 scale)
    # =========================================================
    s = 0.5   # drawing scale
    ox = 30.0
    oy = 180.0
    L = 440 * s
    bend_len = 10 * s   # 10mm bent portion tucked into pocket

    msp.add_text("SIDE VIEW (1:2 scale) — WIRE AS-BENT",
                 height=3.5, dxfattribs={"layer": "TEXT"}).set_placement((ox, oy + 15))

    # Straight portion
    msp.add_line((ox + bend_len, oy), (ox + L - bend_len, oy),
                 dxfattribs={"layer": "OUTLINE"})

    # Left bend (90° upward into tip pocket)
    msp.add_line((ox + bend_len, oy), (ox + bend_len, oy + bend_len),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_arc(
        center=(ox + bend_len + 2 * s, oy),
        radius=2 * s,
        start_angle=90, end_angle=180,
        dxfattribs={"layer": "OUTLINE"},
    )

    # Right bend (90° upward)
    msp.add_line((ox + L - bend_len, oy), (ox + L - bend_len, oy + bend_len),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_arc(
        center=(ox + L - bend_len - 2 * s, oy),
        radius=2 * s,
        start_angle=0, end_angle=90,
        dxfattribs={"layer": "OUTLINE"},
    )

    # Overall length dim
    msp.add_linear_dim(
        base=(ox + L / 2, oy - 12),
        p1=(ox + bend_len, oy), p2=(ox + L - bend_len, oy),
        dimstyle="AEROFORGE",
    ).render()

    # Bend length callout
    msp.add_linear_dim(
        base=(ox + bend_len / 2, oy - 20),
        p1=(ox, oy), p2=(ox + bend_len, oy),
        dimstyle="AEROFORGE",
    ).render()

    # Wire dia callout
    msp.add_text("Ø0.5mm (ASTM A228)", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + L / 2 - 10, oy + 4))

    # Labels
    msp.add_text("90° bend\n(into tip horn pocket)", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((ox - 15, oy + bend_len + 2))
    msp.add_text("STRAIGHT — passes through all knuckles\nand VStab fin bore",
                 height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + L / 2 - 30, oy + 8))
    msp.add_text("90° bend\n(into tip horn pocket)", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + L - bend_len + 3, oy + bend_len + 2))

    # =========================================================
    # CROSS-SECTION
    # =========================================================
    cs_ox = ox + L + 40
    cs_oy = oy
    msp.add_circle((cs_ox, cs_oy), 0.5 * 4, dxfattribs={"layer": "OUTLINE"})  # 4x scale
    msp.add_text("CROSS-SECTION (4:1)", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (cs_ox - 8, cs_oy + 5))
    msp.add_text("Ø0.5mm", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (cs_ox + 3, cs_oy))

    # Notes
    notes = [
        "NOTES:",
        "1. Off-shelf component. Music wire (spring steel, ASTM A228). Ø0.5mm.",
        "2. Cut to 440mm total length. Bend 90° at each end (last 10mm).",
        "3. THREADING SEQUENCE: insert wire from one tip, through all LEFT knuckles,",
        "   through 0.6mm bore in VStab fin (PETG sleeve), through all RIGHT knuckles,",
        "   to right tip. Then bend both ends 90° and tuck into tip horn pockets.",
        "4. Wire is NOT glued — retained by 90° bends in tip pockets.",
        "5. Hinge bore in VStab fin: Ø0.6mm with PETG sleeve (1.2mm OD, CA bonded in fin).",
        "6. Wire must rotate freely in knuckle bores for smooth elevator deflection.",
        "7. Fatigue life: INFINITE (stress <1% of endurance limit at max deflection ±25°).",
        "8. Upper surface gap at hinge: 0.3mm (knuckles buried in turbulent boundary layer).",
    ]
    for i, note in enumerate(notes):
        msp.add_text(note, height=2.2, dxfattribs={"layer": "TEXT"}).set_placement(
            (ox, oy - 30 - i * 5.5))

    save_dxf_and_png(doc, "cad/components/empennage/Hinge_Wire/Hinge_Wire_drawing.dxf")
    print("Hinge_Wire drawing complete.")


if __name__ == "__main__":
    draw_main_spar()
    draw_rear_spar()
    draw_elevator_stiffener()
    draw_hinge_wire()
    print("\nAll off-shelf component drawings complete.")
