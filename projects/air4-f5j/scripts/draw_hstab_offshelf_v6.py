"""
HStab Off-Shelf Components — v6 Design Consensus
=================================================
Only two off-shelf rods remain in v6:
  - HStab_Main_Spar: 3mm CF tube (3/2mm OD/ID), 378mm
  - Hinge_Wire: 0.5mm music wire, 424mm
Plus PETG_Sleeves (printed, 48x).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.dxf_utils import setup_drawing, save_dxf_and_png


def draw_rod(doc, ox, oy, length, od, bore=None, label="", material="", notes=None, scale=1.0, dimstyle=None):
    msp = doc.modelspace()
    L = length * scale
    D = od * scale
    ds = dimstyle or "AEROFORGE"
    msp.add_lwpolyline(
        [(ox, oy - D/2), (ox+L, oy - D/2), (ox+L, oy + D/2), (ox, oy + D/2), (ox, oy - D/2)],
        dxfattribs={"layer": "OUTLINE"})
    msp.add_line((ox-5, oy), (ox+L+5, oy), dxfattribs={"layer": "CENTERLINE"})
    msp.add_linear_dim(base=(ox+L/2, oy-D/2-10), p1=(ox, oy-D/2), p2=(ox+L, oy-D/2),
                       dimstyle=ds).render()
    msp.add_aligned_dim(p1=(ox+L+12, oy-D/2), p2=(ox+L+12, oy+D/2),
                        distance=5, dimstyle=ds).render()
    cs_ox = ox + L + 35
    msp.add_circle((cs_ox, oy), od*scale/2, dxfattribs={"layer": "OUTLINE"})
    if bore:
        msp.add_circle((cs_ox, oy), bore*scale/2, dxfattribs={"layer": "SPAR"})
    msp.add_line((cs_ox-od*scale, oy), (cs_ox+od*scale, oy), dxfattribs={"layer": "CENTERLINE"})
    msp.add_line((cs_ox, oy-od*scale), (cs_ox, oy+od*scale), dxfattribs={"layer": "CENTERLINE"})
    msp.add_text("CROSS-SECTION", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((cs_ox-12, oy+od*scale+5))
    msp.add_text(f"Ø{od}mm OD", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((cs_ox+od*scale+3, oy+2))
    if bore:
        msp.add_text(f"Ø{bore}mm ID", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((cs_ox+od*scale+3, oy-4))
    msp.add_text(label, height=4.0, dxfattribs={"layer": "TEXT"}).set_placement((ox, oy+D/2+10))
    msp.add_text(material, height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((ox, oy+D/2+5))
    if notes:
        for i, note in enumerate(notes):
            msp.add_text(note, height=2.2, dxfattribs={"layer": "TEXT"}).set_placement((ox, oy-D/2-22-i*5.5))


def _add_scaled_dimstyle(doc, scale_factor):
    """Add a dimension style that compensates for drawing scale."""
    ds = doc.dimstyles.new(f"AEROFORGE_{scale_factor}X")
    ds.dxf.dimtxt = 2.5
    ds.dxf.dimasz = 1.5
    ds.dxf.dimlfac = scale_factor  # multiply measured values by this
    ds.dxf.dimexe = 0.8
    ds.dxf.dimexo = 0.5
    ds.dxf.dimgap = 0.6
    return f"AEROFORGE_{scale_factor}X"


def draw_main_spar():
    doc = setup_drawing(
        title="HStab_Main_Spar", subtitle="3mm CF tube (3.0/2.0mm). 378mm total. ONLY SPAR in v6.",
        material="Carbon fiber tube | 3/2mm OD/ID | Off-shelf",
        mass="2.38g", scale="1:2", sheet_size="A3", status="FOR APPROVAL", revision="v6")
    _add_scaled_dimstyle(doc, 2.0)  # 1:2 scale -> multiply dims by 2
    doc.modelspace().add_text("SIDE VIEW (1:2 scale)", height=3.5,
                              dxfattribs={"layer": "TEXT"}).set_placement((30, 200))
    draw_rod(doc, ox=30, oy=185, length=378, od=3.0, bore=2.0,
             label="HStab_Main_Spar — 3mm CF TUBE (ONLY SPAR)",
             material="Carbon fiber tube, 3.0mm OD / 2.0mm ID | 378mm overall",
             notes=[
                 "NOTES:",
                 "1. Off-shelf component. Cut to 378mm.",
                 "2. Passes through LEFT stab (189mm) + VStab fin hole + RIGHT stab (189mm).",
                 "3. Bore in stab: D3.1mm. Friction fit + CA.",
                 "4. Position: X=34.5mm from root LE (30.0% chord = max-thickness point).",
                 "5. Terminates at y=189mm each side (airfoil too thin beyond).",
                 "6. v6: This is the ONLY spar. Rear spar and stiffener removed.",
             ], scale=0.5, dimstyle="AEROFORGE_2.0X")
    save_dxf_and_png(doc, "cad/components/empennage/HStab_Main_Spar/HStab_Main_Spar_drawing.dxf")
    print("HStab_Main_Spar v6 done.")


def draw_hinge_wire():
    doc = setup_drawing(
        title="Hinge_Wire", subtitle="0.5mm music wire (ASTM A228). 424mm. Concealed saddle hinge.",
        material="Music wire | ASTM A228 spring steel | 0.5mm dia | Off-shelf",
        mass="0.65g", scale="1:2", sheet_size="A3", status="FOR APPROVAL", revision="v6")
    msp = doc.modelspace()
    s = 0.5; ox = 30.0; oy = 180.0; L = 424 * s; bend_len = 8 * s
    _add_scaled_dimstyle(doc, 2.0)
    msp.add_text("SIDE VIEW (1:2 scale) — WIRE AS-BENT", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((ox, oy + 15))
    msp.add_line((ox + bend_len, oy), (ox + L - bend_len, oy), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((ox + bend_len, oy), (ox + bend_len, oy + bend_len), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((ox + L - bend_len, oy), (ox + L - bend_len, oy + bend_len), dxfattribs={"layer": "OUTLINE"})
    msp.add_linear_dim(base=(ox+L/2, oy-12), p1=(ox+bend_len, oy), p2=(ox+L-bend_len, oy),
                       dimstyle="AEROFORGE_2.0X").render()
    msp.add_text("Ø0.5mm (ASTM A228)", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((ox+L/2-10, oy+4))
    msp.add_text("90° bend (flush into tip)", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((ox-15, oy+bend_len+2))
    msp.add_text("STRAIGHT — through PETG sleeves\nand VStab fin bore", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((ox+L/2-30, oy+8))
    cs_ox = ox + L + 40
    msp.add_circle((cs_ox, oy), 0.5*4, dxfattribs={"layer": "OUTLINE"})
    msp.add_text("CROSS-SECTION (4:1)", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((cs_ox-8, oy+5))
    msp.add_text("Ø0.5mm", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((cs_ox+3, oy))
    notes = [
        "NOTES:",
        "1. Music wire (ASTM A228). Ø0.5mm. Cut to 424mm. Bend 90° at each end (last 8mm).",
        "2. Thread through interleaved PETG sleeves in concealed saddle hinge.",
        "3. Through 0.6mm bore in VStab fin (PETG sleeve, 1.2mm OD).",
        "4. Wire rotates freely in sleeves. NOT glued — retained by 90° tip bends.",
        "5. Position: X=60.0mm from root LE (52.2% root chord). Concealed inside stab.",
        "6. Terminates at y=212mm each side (hinge exits TE at that station).",
        "7. Fatigue life: INFINITE (stress <1% of endurance limit at +/-18°).",
        "8. v6: Zero visible gap — wire fully concealed in saddle mechanism.",
    ]
    for i, note in enumerate(notes):
        msp.add_text(note, height=2.2, dxfattribs={"layer": "TEXT"}).set_placement((ox, oy-30-i*5.5))
    save_dxf_and_png(doc, "cad/components/empennage/Hinge_Wire/Hinge_Wire_drawing.dxf")
    print("Hinge_Wire v6 done.")


def draw_petg_sleeves():
    doc = setup_drawing(
        title="PETG_Sleeves", subtitle="48x PETG bearing sleeves for concealed saddle hinge. 1.2mm OD / 0.6mm ID / 3mm long.",
        material="PETG | 100% solid | 240C | Print flat",
        mass="0.10g total (48 sleeves)", scale="4:1", sheet_size="A4", status="FOR APPROVAL", revision="v6")
    msp = doc.modelspace()
    ox, oy = 100, 150; s = 4.0
    msp.add_text("SINGLE SLEEVE (4:1 scale)", height=4.0, dxfattribs={"layer": "TEXT"}).set_placement((ox-10, oy+20))
    L = 3.0 * s; od = 1.2 * s; iid = 0.6 * s
    msp.add_lwpolyline([(ox, oy-od/2), (ox+L, oy-od/2), (ox+L, oy+od/2), (ox, oy+od/2), (ox, oy-od/2)],
                       dxfattribs={"layer": "OUTLINE"})
    msp.add_lwpolyline([(ox, oy-iid/2), (ox+L, oy-iid/2), (ox+L, oy+iid/2), (ox, oy+iid/2), (ox, oy-iid/2)],
                       dxfattribs={"layer": "HIDDEN"})
    msp.add_line((ox-3, oy), (ox+L+3, oy), dxfattribs={"layer": "CENTERLINE"})
    cs_ox = ox + L + 30
    msp.add_circle((cs_ox, oy), od/2, dxfattribs={"layer": "OUTLINE"})
    msp.add_circle((cs_ox, oy), iid/2, dxfattribs={"layer": "SPAR"})
    msp.add_text("Ø1.2mm OD", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((cs_ox+od/2+3, oy+2))
    msp.add_text("Ø0.6mm ID", height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((cs_ox+od/2+3, oy-4))
    notes = [
        "NOTES:",
        "1. PETG, 100% solid infill, 240C. Print 48+ on one build plate.",
        "2. Dimensions: 1.2mm OD / 0.6mm ID / 3.0mm long.",
        "3. 24 per half-span. Alternating stab-fixed / elevator-fixed (interleaved).",
        "4. Pressed into printed pockets in stab saddle and elevator bull-nose. CA bond.",
        "5. 0.5mm music wire passes through all sleeves freely.",
        "6. Stab-fixed sleeves = bearing surfaces. Elevator-fixed = anti-slide.",
        "7. Spacing: ~17.5mm center-to-center along hinge line.",
        "8. Total mass: 0.10g (all 48 sleeves).",
    ]
    for i, n in enumerate(notes):
        msp.add_text(n, height=2.0, dxfattribs={"layer": "TEXT"}).set_placement((30, 100-i*5))
    save_dxf_and_png(doc, "cad/components/empennage/PETG_Sleeves/PETG_Sleeves_drawing.dxf")
    print("PETG_Sleeves v6 done.")


if __name__ == "__main__":
    draw_main_spar()
    draw_hinge_wire()
    draw_petg_sleeves()
    print("\nAll off-shelf v6 drawings complete.")
