"""
Technical drawings for the 5 off-shelf H-Stab components.

Components:
  1. HStab_Main_Spar       — 3mm CF tube (OD 3 / ID 2), 390mm
  2. HStab_Rear_Spar       — 1.5mm CF solid rod, 440mm
  3. Elevator_Stiffener    — 1mm CF solid rod, 440mm
  4. Hinge_Wire            — 0.5mm music wire, 440mm (bent ends)
  5. Mass_Balance          — ~1g tungsten putty blob (schematic)

All off-shelf hardware — no aero/structural consensus required.
Uses the same layer / dimstyle / save pattern as draw_offshelf_rods.py.
"""
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ezdxf
from src.core.dxf_utils import save_dxf_and_png


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _base_doc():
    """Create a fresh doc with the four standard layers and 'ROD' dimstyle."""
    doc = ezdxf.new("R2010", setup=True)
    doc.layers.add("OUTLINE",    color=7)
    doc.layers.add("DIMENSION",  color=1)
    doc.layers.add("TEXT",       color=7)
    doc.layers.add("CENTERLINE", color=5)
    doc.layers.add("HATCH",      color=6)

    ds = doc.dimstyles.new("ROD")
    ds.dxf.dimtxt  = 2.5
    ds.dxf.dimasz  = 1.5
    ds.dxf.dimlfac = 1.0
    ds.dxf.dimexe  = 0.8
    ds.dxf.dimexo  = 0.5
    ds.dxf.dimgap  = 0.6

    return doc


def _title_block(msp, name, material, diameter_str, length_mm, purpose):
    """Draw the standard title block at y = -5…-23."""
    tbx, tby = 0, -5
    for p1, p2 in [
        ((tbx, tby),      (tbx + 260, tby)),
        ((tbx, tby - 18), (tbx + 260, tby - 18)),
        ((tbx, tby),      (tbx, tby - 18)),
        ((tbx + 260, tby),(tbx + 260, tby - 18)),
    ]:
        msp.add_line(p1, p2, dxfattribs={"layer": "OUTLINE"})

    msp.add_text(
        f"AEROFORGE — {name}",
        height=3.5,
        dxfattribs={"layer": "TEXT"},
    ).set_placement((tbx + 5, tby - 5))

    msp.add_text(
        f"{material} | {diameter_str} | Length: {length_mm}mm | {purpose}",
        height=2,
        dxfattribs={"layer": "TEXT"},
    ).set_placement((tbx + 5, tby - 11))

    msp.add_text(
        "Off-shelf | Scale: 1:1 | Status: APPROVED (from assembly consensus)",
        height=1.8,
        dxfattribs={"layer": "TEXT"},
    ).set_placement((tbx + 5, tby - 16))


# ---------------------------------------------------------------------------
# 1. Solid rod (HStab_Rear_Spar, Elevator_Stiffener)
# ---------------------------------------------------------------------------

def draw_solid_rod(name, diameter, length, material, purpose, out_path):
    """Standard solid rod: rectangular side view + filled-circle end view."""
    doc = _base_doc()
    msp = doc.modelspace()

    r = diameter / 2
    ox, oy = 10, 30

    # ---- Side view --------------------------------------------------------
    msp.add_lwpolyline(
        [(ox, oy - r), (ox + length, oy - r),
         (ox + length, oy + r), (ox, oy + r)],
        close=True,
        dxfattribs={"layer": "OUTLINE"},
    )

    # Centerline
    msp.add_line((ox - 5, oy), (ox + length + 5, oy),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    # Length dim
    dim = msp.add_linear_dim(
        base=(ox, oy - r - 8),
        p1=(ox, oy), p2=(ox + length, oy),
        dimstyle="ROD",
    )
    dim.render()

    # Diameter dim
    dim = msp.add_linear_dim(
        base=(ox - 8, oy),
        p1=(ox, oy - r), p2=(ox, oy + r),
        angle=90, dimstyle="ROD",
    )
    dim.render()

    # View label
    msp.add_text("SIDE VIEW", height=3, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox, oy + r + 8))

    # ---- End view: filled circle ------------------------------------------
    ex = ox + length + 35
    # Hatch first (filled appearance) — use edge path with a full arc
    hatch = msp.add_hatch(color=7, dxfattribs={"layer": "HATCH"})
    ep = hatch.paths.add_edge_path()
    ep.add_arc(center=(ex, oy), radius=r, start_angle=0, end_angle=360, ccw=True)
    hatch.set_solid_fill()
    # Outline circle on top
    msp.add_circle((ex, oy), r, dxfattribs={"layer": "OUTLINE"})
    # Crosshairs
    msp.add_line((ex - r - 2, oy), (ex + r + 2, oy),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})
    msp.add_line((ex, oy - r - 2), (ex, oy + r + 2),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    msp.add_text("END VIEW (SOLID)", height=3, dxfattribs={"layer": "TEXT"}).set_placement(
        (ex - 14, oy + r + 8))

    # ---- Title block ------------------------------------------------------
    _title_block(msp, name, material,
                 f"Dia: {diameter}mm solid", length, purpose)

    save_dxf_and_png(doc, out_path)
    print(f"  {name}: {out_path}")


# ---------------------------------------------------------------------------
# 2. Tube (HStab_Main_Spar) — annular end view
# ---------------------------------------------------------------------------

def draw_tube(name, od, id_, length, material, purpose, out_path):
    """CF tube: rectangular side view (with inner bore indicated) + annular end view."""
    doc = _base_doc()
    msp = doc.modelspace()

    ro = od / 2          # outer radius
    ri = id_ / 2         # inner radius
    ox, oy = 10, 30

    # ---- Side view: outer rectangle ---------------------------------------
    msp.add_lwpolyline(
        [(ox, oy - ro), (ox + length, oy - ro),
         (ox + length, oy + ro), (ox, oy + ro)],
        close=True,
        dxfattribs={"layer": "OUTLINE"},
    )
    # Inner bore dashed lines
    msp.add_line((ox, oy + ri), (ox + length, oy + ri),
                 dxfattribs={"layer": "OUTLINE", "linetype": "DASHED"})
    msp.add_line((ox, oy - ri), (ox + length, oy - ri),
                 dxfattribs={"layer": "OUTLINE", "linetype": "DASHED"})

    # Centerline
    msp.add_line((ox - 5, oy), (ox + length + 5, oy),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    # Length dim
    dim = msp.add_linear_dim(
        base=(ox, oy - ro - 8),
        p1=(ox, oy), p2=(ox + length, oy),
        dimstyle="ROD",
    )
    dim.render()

    # OD dim
    dim = msp.add_linear_dim(
        base=(ox - 8, oy),
        p1=(ox, oy - ro), p2=(ox, oy + ro),
        angle=90, dimstyle="ROD",
    )
    dim.render()

    # ID dim (further out)
    dim = msp.add_linear_dim(
        base=(ox - 16, oy),
        p1=(ox, oy - ri), p2=(ox, oy + ri),
        angle=90, dimstyle="ROD",
    )
    dim.render()

    msp.add_text("SIDE VIEW", height=3, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox, oy + ro + 8))

    # ---- End view: annulus ------------------------------------------------
    ex = ox + length + 40
    # Outer circle
    msp.add_circle((ex, oy), ro, dxfattribs={"layer": "OUTLINE"})
    # Inner circle
    msp.add_circle((ex, oy), ri, dxfattribs={"layer": "OUTLINE"})
    # Hatch the annular ring — two separate edge paths (outer + inner hole)
    hatch = msp.add_hatch(color=7, dxfattribs={"layer": "HATCH"})
    ep_outer = hatch.paths.add_edge_path()
    ep_outer.add_arc(center=(ex, oy), radius=ro, start_angle=0, end_angle=360, ccw=True)
    ep_inner = hatch.paths.add_edge_path(flags=ezdxf.const.BOUNDARY_PATH_OUTERMOST)
    ep_inner.add_arc(center=(ex, oy), radius=ri, start_angle=0, end_angle=360, ccw=True)
    hatch.set_solid_fill()
    # Crosshairs
    msp.add_line((ex - ro - 2, oy), (ex + ro + 2, oy),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})
    msp.add_line((ex, oy - ro - 2), (ex, oy + ro + 2),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    msp.add_text("END VIEW (TUBE)", height=3, dxfattribs={"layer": "TEXT"}).set_placement(
        (ex - 12, oy + ro + 8))

    # ---- Title block ------------------------------------------------------
    _title_block(msp, name, material,
                 f"OD: {od}mm / ID: {id_}mm", length, purpose)

    save_dxf_and_png(doc, out_path)
    print(f"  {name}: {out_path}")


# ---------------------------------------------------------------------------
# 3. Hinge wire — bent ends
# ---------------------------------------------------------------------------

def draw_hinge_wire(name, diameter, length, bend_length, material, purpose, out_path):
    """Music wire with 90° bends at each end.

    The main span runs from (ox, oy) to (ox+length, oy).
    Each end has a bend_length stub pointing downward.
    """
    doc = _base_doc()
    msp = doc.modelspace()

    r = diameter / 2
    ox, oy = 10, 30

    # ---- Side view --------------------------------------------------------
    # Wire body (thin rectangle)
    msp.add_lwpolyline(
        [(ox, oy - r), (ox + length, oy - r),
         (ox + length, oy + r), (ox, oy + r)],
        close=True,
        dxfattribs={"layer": "OUTLINE"},
    )
    # Left bend stub (90°, pointing downward)
    msp.add_lwpolyline(
        [(ox - r, oy), (ox - r, oy - bend_length),
         (ox + r, oy - bend_length), (ox + r, oy)],
        close=False,
        dxfattribs={"layer": "OUTLINE"},
    )
    # Right bend stub
    msp.add_lwpolyline(
        [(ox + length - r, oy), (ox + length - r, oy - bend_length),
         (ox + length + r, oy - bend_length), (ox + length + r, oy)],
        close=False,
        dxfattribs={"layer": "OUTLINE"},
    )
    # Centerline
    msp.add_line((ox - bend_length - 2, oy), (ox + length + bend_length + 2, oy),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    # Overall length dim (tip to tip of bends)
    total = length
    dim = msp.add_linear_dim(
        base=(ox, oy - r - 12),
        p1=(ox, oy), p2=(ox + total, oy),
        dimstyle="ROD",
    )
    dim.render()

    # Diameter dim
    dim = msp.add_linear_dim(
        base=(ox - 10, oy),
        p1=(ox, oy - r), p2=(ox, oy + r),
        angle=90, dimstyle="ROD",
    )
    dim.render()

    # Bend length annotation
    dim = msp.add_linear_dim(
        base=(ox - r - 14, oy - bend_length / 2),
        p1=(ox - r, oy), p2=(ox - r, oy - bend_length),
        angle=90, dimstyle="ROD",
    )
    dim.render()

    msp.add_text("SIDE VIEW  (90° bend each end)", height=3,
                 dxfattribs={"layer": "TEXT"}).set_placement((ox, oy + r + 8))

    # ---- End view: filled circle ------------------------------------------
    ex = ox + length + 40
    hatch = msp.add_hatch(color=7, dxfattribs={"layer": "HATCH"})
    ep = hatch.paths.add_edge_path()
    ep.add_arc(center=(ex, oy), radius=r, start_angle=0, end_angle=360, ccw=True)
    hatch.set_solid_fill()
    msp.add_circle((ex, oy), r, dxfattribs={"layer": "OUTLINE"})
    msp.add_line((ex - r - 2, oy), (ex + r + 2, oy),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})
    msp.add_line((ex, oy - r - 2), (ex, oy + r + 2),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    msp.add_text("END VIEW", height=3, dxfattribs={"layer": "TEXT"}).set_placement(
        (ex - 8, oy + r + 8))

    # ---- Title block ------------------------------------------------------
    _title_block(msp, name, material,
                 f"Dia: {diameter}mm  Bends: {bend_length}mm each end", length, purpose)

    save_dxf_and_png(doc, out_path)
    print(f"  {name}: {out_path}")


# ---------------------------------------------------------------------------
# 4. Mass balance — schematic putty blob
# ---------------------------------------------------------------------------

def draw_mass_balance(name, approx_dia, mass_g, material, purpose, out_path):
    """Schematic circle with crosshatch representing a tungsten putty blob."""
    doc = _base_doc()
    msp = doc.modelspace()

    r = approx_dia / 2
    cx, cy = 40, 30

    # ---- Blob outline: circle --------------------------------------------
    msp.add_circle((cx, cy), r, dxfattribs={"layer": "OUTLINE"})

    # ---- Crosshatch fill -------------------------------------------------
    hatch = msp.add_hatch(color=6, dxfattribs={"layer": "HATCH"})
    ep = hatch.paths.add_edge_path()
    ep.add_arc(center=(cx, cy), radius=r, start_angle=0, end_angle=360, ccw=True)
    hatch.set_pattern_fill("ANSI31", scale=0.5, angle=45)

    # ---- Diameter dimension ----------------------------------------------
    dim = msp.add_linear_dim(
        base=(cx, cy - r - 8),
        p1=(cx - r, cy), p2=(cx + r, cy),
        dimstyle="ROD",
    )
    dim.render()

    # ---- Centerlines ------------------------------------------------------
    msp.add_line((cx - r - 3, cy), (cx + r + 3, cy),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})
    msp.add_line((cx, cy - r - 3), (cx, cy + r + 3),
                 dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    # ---- Labels -----------------------------------------------------------
    msp.add_text("SCHEMATIC (not to precise scale)", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((cx - 25, cy + r + 10))
    msp.add_text(f"~{approx_dia}mm dia   ~{mass_g}g total", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((cx - 10, cy + r + 5))

    # ---- Arrow leader to blob --------------------------------------------
    msp.add_text("TUNGSTEN PUTTY BLOB", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement((cx + r + 5, cy + 2))
    msp.add_line((cx + r, cy), (cx + r + 4, cy),
                 dxfattribs={"layer": "DIMENSION"})

    # ---- Title block ------------------------------------------------------
    _title_block(msp, name, material,
                 f"~{approx_dia}mm sphere (approx)", 0, purpose)

    save_dxf_and_png(doc, out_path)
    print(f"  {name}: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

BASE = "cad/components/empennage"


def main():
    print("H-Stab off-shelf component drawings:")

    # 1. Main spar — CF tube OD 3 / ID 2, 390 mm
    draw_tube(
        name="HStab_Main_Spar",
        od=3.0,
        id_=2.0,
        length=390,
        material="Pultruded Carbon Fiber Tube",
        purpose="Main bending spar at 25% chord — threads through both stab halves + VStab fin",
        out_path=f"{BASE}/HStab_Main_Spar/HStab_Main_Spar_drawing.dxf",
    )

    # 2. Rear spar — CF solid rod 1.5 mm, 440 mm
    draw_solid_rod(
        name="HStab_Rear_Spar",
        diameter=1.5,
        length=440,
        material="Pultruded Carbon Fiber Solid Rod",
        purpose="Anti-rotation spar at 60% chord (fixed stab only)",
        out_path=f"{BASE}/HStab_Rear_Spar/HStab_Rear_Spar_drawing.dxf",
    )

    # 3. Elevator stiffener — CF solid rod 1 mm, 440 mm
    draw_solid_rod(
        name="Elevator_Stiffener",
        diameter=1.0,
        length=440,
        material="Pultruded Carbon Fiber Solid Rod",
        purpose="Flutter prevention stiffener at 80% chord (elevator)",
        out_path=f"{BASE}/Elevator_Stiffener/Elevator_Stiffener_drawing.dxf",
    )

    # 4. Hinge wire — 0.5 mm music wire, 440 mm, 3 mm bends
    draw_hinge_wire(
        name="Hinge_Wire",
        diameter=0.5,
        length=440,
        bend_length=3.0,
        material="ASTM A228 Spring Steel (Music Wire)",
        purpose="Pin hinge axis — threads through PETG knuckle bores",
        out_path=f"{BASE}/Hinge_Wire/Hinge_Wire_drawing.dxf",
    )

    # 5. Mass balance — tungsten putty ~5 mm dia, ~1 g
    draw_mass_balance(
        name="Mass_Balance",
        approx_dia=5.0,
        mass_g=1.0,
        material="Tungsten Putty (e.g., Dynamite DYN5415)",
        purpose="Elevator flutter prevention — applied to control horn forward extension",
        out_path=f"{BASE}/Mass_Balance/Mass_Balance_drawing.dxf",
    )

    print("\nAll 5 drawings complete.")


if __name__ == "__main__":
    main()
