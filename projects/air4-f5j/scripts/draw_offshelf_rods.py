"""
Quick drawings for off-shelf carbon rod components.
These are hardware (not aerodynamic), so no aero-structural consensus needed.
Generates: HStab_Joiner_Rod, Rear_Spar_Left, Rear_Spar_Right drawings.
"""
import ezdxf
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.dxf_utils import save_dxf_and_png


def draw_rod(name, diameter, length, material, purpose, out_path):
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()

    ds = doc.dimstyles.new("ROD")
    ds.dxf.dimtxt = 2.5
    ds.dxf.dimasz = 1.5
    ds.dxf.dimlfac = 1.0
    ds.dxf.dimexe = 0.8
    ds.dxf.dimexo = 0.5
    ds.dxf.dimgap = 0.6

    doc.layers.add("OUTLINE", color=7)
    doc.layers.add("DIMENSION", color=1)
    doc.layers.add("TEXT", color=7)
    doc.layers.add("CENTERLINE", color=5)

    r = diameter / 2
    ox, oy = 10, 30

    # Side view: rectangle
    msp.add_line((ox, oy + r), (ox + length, oy + r), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((ox + length, oy + r), (ox + length, oy - r), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((ox + length, oy - r), (ox, oy - r), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((ox, oy - r), (ox, oy + r), dxfattribs={"layer": "OUTLINE"})

    # Centerline
    msp.add_line((ox - 5, oy), (ox + length + 5, oy),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    # Length dimension
    dim = msp.add_linear_dim(base=(ox, oy - r - 8), p1=(ox, oy), p2=(ox + length, oy),
                              dimstyle="ROD")
    dim.render()

    # Diameter dimension
    dim = msp.add_linear_dim(base=(ox - 8, oy), p1=(ox, oy - r), p2=(ox, oy + r),
                              angle=90, dimstyle="ROD")
    dim.render()

    # End view: circle
    ex = ox + length + 30
    msp.add_circle((ex, oy), r, dxfattribs={"layer": "OUTLINE"})
    msp.add_line((ex - r - 2, oy), (ex + r + 2, oy),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})
    msp.add_line((ex, oy - r - 2), (ex, oy + r + 2),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    # Labels
    msp.add_text("SIDE VIEW", height=3, dxfattribs={"layer": "TEXT"}).set_placement((ox, oy + r + 8))
    msp.add_text("END VIEW", height=3, dxfattribs={"layer": "TEXT"}).set_placement((ex - 10, oy + r + 8))

    # Title block
    tbx, tby = 0, -5
    msp.add_line((tbx, tby), (tbx + 200, tby), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((tbx, tby - 18), (tbx + 200, tby - 18), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((tbx, tby), (tbx, tby - 18), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((tbx + 200, tby), (tbx + 200, tby - 18), dxfattribs={"layer": "OUTLINE"})

    msp.add_text(f"AEROFORGE — {name}", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((tbx + 5, tby - 5))
    msp.add_text(f"{material} | Dia: {diameter}mm | Length: {length}mm | {purpose}",
                 height=2, dxfattribs={"layer": "TEXT"}).set_placement((tbx + 5, tby - 11))
    msp.add_text("Off-shelf | Scale: 1:1 | Status: APPROVED (from assembly consensus)",
                 height=1.8, dxfattribs={"layer": "TEXT"}).set_placement((tbx + 5, tby - 16))

    save_dxf_and_png(doc, out_path)
    print(f"  {name}: {out_path}")


def main():
    print("Off-shelf rod component drawings:")

    draw_rod(
        name="HStab_Joiner_Rod",
        diameter=3.0,
        length=430,
        material="Pultruded Carbon Fiber",
        purpose="Pivot axis + joiner (connects both halves, rotates in brass bushings)",
        out_path="cad/components/empennage/HStab_Joiner_Rod/HStab_Joiner_Rod_drawing.dxf",
    )

    draw_rod(
        name="Rear_Spar_Left",
        diameter=2.0,
        length=200,
        material="Pultruded Carbon Fiber",
        purpose="Trailing edge stiffener at 65% chord (left half)",
        out_path="cad/components/empennage/Rear_Spar_Left/Rear_Spar_Left_drawing.dxf",
    )

    draw_rod(
        name="Rear_Spar_Right",
        diameter=2.0,
        length=200,
        material="Pultruded Carbon Fiber",
        purpose="Trailing edge stiffener at 65% chord (right half)",
        out_path="cad/components/empennage/Rear_Spar_Right/Rear_Spar_Right_drawing.dxf",
    )


if __name__ == "__main__":
    main()
