"""
2D Technical Drawing: H-Stab Assembly (Master Reference)
========================================================
FROM DESIGN CONSENSUS v5 (aero+structural agent team, R3):

  Configuration: Fixed stabilizer + 35% chord elevator
  Planform: Superellipse n=2.3
  Blend: HT-13 (6.5%) root -> HT-12 (5.1%) tip
  430mm span | 115mm root chord | Superellipse taper
  Main spar: 3mm CF tube at 30.4% root chord (X=35.0mm, constant)
  Rear spar: 1.5mm CF rod at 60% chord (X=69.0mm)
  Elevator stiffener: 1mm CF rod at 80% chord (X=92.0mm)
  Hinge: 0.5mm music wire at 65% chord, interleaved PETG knuckles
  Mass: 33.65g | Vh=0.393

Views:
  1. PLANFORM (top view) -- full 430mm span, both halves + elevators
  2. ROOT CROSS-SECTION -- HT-13 airfoil at y=0
  3. HINGE DETAIL -- zoomed bevel geometry at 0 deg and +25 deg
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# ──────────────────────────────────────────────────────────────────────────────
# PARAMETERS FROM DESIGN CONSENSUS v3.1
# ──────────────────────────────────────────────────────────────────────────────
SPAN = 430.0
HALF_SPAN = SPAN / 2  # 215mm
ROOT_CHORD = 115.0
SUPERELLIPSE_N = 2.3
HINGE_FRAC = 0.65       # hinge line at 65% chord
TE_FRAC = 0.97           # TE truncation at 97% chord
MAIN_SPAR_DIA = 3.0      # 3mm CF tube (OD)
MAIN_SPAR_ID = 2.0       # 2mm ID
MAIN_SPAR_TUNNEL_ID = 3.1  # tunnel bore
REAR_SPAR_DIA = 1.5      # 1.5mm CF rod
REAR_SPAR_TUNNEL_ID = 1.6
STIFFENER_DIA = 1.0      # 1mm CF rod
STIFFENER_TUNNEL_ID = 1.1
HINGE_WIRE_DIA = 0.5     # 0.5mm music wire
HINGE_GAP = 0.3          # gap between stab TE and elevator LE
MAIN_SPAR_SPAN = 186.0   # spar ends at 186mm per half (v5 structural correction)
MAIN_SPAR_X = 35.0       # fixed X from root LE (30.4% root chord) -- v5
MAIN_SPAR_ROOT_FRAC = 0.304  # 30.4% root chord
REAR_SPAR_SPAN = 210.0   # per half (420mm total rod) -- v5
REAR_SPAR_X = 69.0       # fixed X from root LE (60% root chord) -- v5
STIFFENER_SPAN = 150.0   # per half (2x150mm rods, NOT through fin) -- v5
STIFFENER_X = 92.0       # fixed X from root LE (80% root chord) -- v5
HINGE_WIRE_LEN = 440.0   # full span
VSTAB_FIN_WIDTH = 7.0
ROOT_GAP_AT_HINGE = 8.0  # elevator root gap at hinge line
ROOT_GAP_AT_TE = 8.0     # elevator root gap at TE (same as hinge) -- v5
KNUCKLE_OD = 1.2
KNUCKLE_ID = 0.6
CONTROL_HORN_Y = 15.0    # 15mm from root, on left elevator
HORN_HEIGHT = 15.0
HORN_WIDTH_BASE = 8.0
HORN_WIDTH_TIP = 5.0
BRIDGE_SPAN = 25.0       # bridge joiner span
BRIDGE_HEIGHT = 5.0
BRIDGE_WIDTH = 12.0
WALL_THICKNESS_STAB = 0.45
WALL_THICKNESS_ELEV = 0.40
BEVEL_UPPER = 22.0  # degrees total
BEVEL_LOWER = 27.0
DEFL_UP = 25.0    # nose up, elevator TE rises
DEFL_DOWN = -20.0  # nose down, elevator TE drops

# HT-13 airfoil (6.5% t/c) - NACA 4-digit style approximation
THICKNESS_ROOT = 0.065  # 6.5%


# ──────────────────────────────────────────────────────────────────────────────
# GEOMETRY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def chord_at(y: float) -> float:
    """Superellipse chord distribution: c(y) = 115 * (1 - |y/215|^2.3)^(1/2.3)"""
    eta = abs(y) / HALF_SPAN
    if eta >= 1.0:
        return 0.0
    return ROOT_CHORD * (1.0 - eta ** SUPERELLIPSE_N) ** (1.0 / SUPERELLIPSE_N)


def spar_frac_at(y: float) -> float:
    """Spar chord fraction at span station y.

    The spar is at CONSTANT X=35.0mm from root LE (v5).
    The chord fraction changes because the planform tapers around it.
    At root: 35.0/115.0 = 30.4%. At y=186mm (termination): ~18.9%.
    """
    c = chord_at(y)
    if c <= 0:
        return MAIN_SPAR_ROOT_FRAC
    # LE position at this span station
    x_le = 51.75 - 0.45 * c  # from consensus planform formula
    # Spar is at fixed X=35.0mm from root LE
    frac = (MAIN_SPAR_X - x_le) / c
    return max(frac, 0.0)


def ht13_yt(xc: float, chord: float) -> float:
    """HT-13 approximate half-thickness at chord fraction xc.
    Uses NACA 4-digit thickness distribution scaled to 6.5% t/c."""
    if xc <= 0:
        return 0.0
    if xc > 1.0:
        xc = 1.0
    t = THICKNESS_ROOT
    # Standard NACA 4-digit thickness distribution
    yt = 5 * t * (
        0.2969 * xc**0.5
        - 0.1260 * xc
        - 0.3516 * xc**2
        + 0.2843 * xc**3
        - 0.1015 * xc**4
    ) * chord
    return max(yt, 0.0)


def planform_stations(half_span: float, n: int = 50) -> list[float]:
    """Generate span stations from 0 to half_span."""
    return [half_span * i / n for i in range(n + 1)]


# ──────────────────────────────────────────────────────────────────────────────
# DRAWING FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def draw_planform(msp, ox: float, oy: float):
    """View 1: Full planform (top view) of entire H-Stab assembly.

    Convention: LE on LEFT (small X), TE on RIGHT (large X).
    Root at BOTTOM (oy), tips at top (oy + half_span) and bottom (oy - half_span).
    The main spar is at a CONSTANT X position = structural datum.
    LE and hinge line CURVE relative to the straight spar.
    """
    # The spar at root is at 25% of 115mm = 28.75mm from LE.
    # We place the spar X at a fixed drawing X coordinate.
    spar_x_root = spar_frac_at(0) * chord_at(0)  # 0.25 * 115 = 28.75
    # In drawing coords, spar is at ox + spar_x_root (constant for all y)
    spar_draw_x = ox + spar_x_root

    stations = planform_stations(HALF_SPAN, 60)

    for sign in [1, -1]:  # +1 = right half (tip up), -1 = left half (tip down)
        le_pts = []
        hinge_pts = []
        te_pts = []

        for y in stations:
            c = chord_at(y)
            if c <= 0:
                break
            sf = spar_frac_at(y)
            # Spar is at constant X. LE is spar_x - sf*c from spar.
            le_x = spar_draw_x - sf * c
            hinge_x = spar_draw_x + (HINGE_FRAC - sf) * c
            te_x = spar_draw_x + (TE_FRAC - sf) * c

            draw_y = oy + sign * y
            le_pts.append((le_x, draw_y))
            hinge_pts.append((hinge_x, draw_y))
            te_pts.append((te_x, draw_y))

        # Draw LE outline (thick)
        for i in range(len(le_pts) - 1):
            msp.add_line(le_pts[i], le_pts[i + 1], dxfattribs={"layer": "OUTLINE"})

        # Draw TE outline (medium) -- elevator trailing edge
        for i in range(len(te_pts) - 1):
            msp.add_line(te_pts[i], te_pts[i + 1], dxfattribs={"layer": "OUTLINE"})

        # Draw hinge line (dashed)
        for i in range(len(hinge_pts) - 1):
            msp.add_line(hinge_pts[i], hinge_pts[i + 1],
                         dxfattribs={"layer": "HIDDEN", "linetype": "DASHED"})

        # Close tip (LE to TE at tip)
        if le_pts and te_pts:
            msp.add_line(le_pts[-1], te_pts[-1], dxfattribs={"layer": "OUTLINE"})

        # Label stab and elevator halves
        side_name = "RIGHT" if sign > 0 else "LEFT"
        mid_y = oy + sign * HALF_SPAN * 0.5
        c_mid = chord_at(HALF_SPAN * 0.5)
        sf_mid = spar_frac_at(HALF_SPAN * 0.5)
        stab_center_x = spar_draw_x - sf_mid * c_mid * 0.3
        elev_center_x = spar_draw_x + (0.80 - sf_mid) * c_mid

        msp.add_text(f"{side_name} STAB", height=2.0,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (stab_center_x, mid_y + sign * 3))
        msp.add_text(f"{side_name} ELEVATOR", height=1.8,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (elev_center_x, mid_y - sign * 3))

    # Root line (stab - from LE to hinge)
    c_root = chord_at(0)
    sf_root = spar_frac_at(0)
    le_root_x = spar_draw_x - sf_root * c_root
    hinge_root_x = spar_draw_x + (HINGE_FRAC - sf_root) * c_root
    te_root_x = spar_draw_x + (TE_FRAC - sf_root) * c_root
    msp.add_line((le_root_x, oy), (hinge_root_x, oy), dxfattribs={"layer": "OUTLINE"})

    # Root elevator lines (with gap for VStab fin)
    # Left elevator root: at oy - ROOT_GAP_AT_HINGE/2 (hinge end) to oy - ROOT_GAP_AT_TE/2 (TE end)
    # Right elevator root: at oy + ROOT_GAP_AT_HINGE/2 to oy + ROOT_GAP_AT_TE/2
    for sign in [1, -1]:
        gap_hinge = sign * ROOT_GAP_AT_HINGE / 2
        gap_te = sign * ROOT_GAP_AT_TE / 2
        msp.add_line((hinge_root_x, oy + gap_hinge),
                     (te_root_x, oy + gap_te),
                     dxfattribs={"layer": "OUTLINE"})

    # ── VStab fin outline at center ──
    # Simplified rectangle representing VStab fin cross-section at root
    fin_half = VSTAB_FIN_WIDTH / 2
    # The fin extends from roughly 25% chord area forward to TE
    fin_le_x = spar_draw_x - 10  # approximate fin LE position
    fin_te_x = te_root_x + 5      # fin extends slightly past elevator TE
    # Draw fin outline (thin dashed)
    for dy in [fin_half, -fin_half]:
        msp.add_line((fin_le_x, oy + dy), (fin_te_x, oy + dy),
                     dxfattribs={"layer": "HIDDEN", "linetype": "DASHED"})
    msp.add_line((fin_le_x, oy - fin_half), (fin_le_x, oy + fin_half),
                 dxfattribs={"layer": "HIDDEN", "linetype": "DASHED"})
    msp.add_line((fin_te_x, oy - fin_half), (fin_te_x, oy + fin_half),
                 dxfattribs={"layer": "HIDDEN", "linetype": "DASHED"})
    msp.add_text("VSTAB FIN", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (fin_le_x + 2, oy - 0.5))

    # ── Main spar: STRAIGHT vertical line at constant X ──
    # Spans from -195mm to +195mm
    msp.add_line((spar_draw_x, oy - MAIN_SPAR_SPAN),
                 (spar_draw_x, oy + MAIN_SPAR_SPAN),
                 dxfattribs={"layer": "SPAR"})
    # Spar thickness (show tube width)
    for dx in [-MAIN_SPAR_DIA / 2, MAIN_SPAR_DIA / 2]:
        msp.add_line((spar_draw_x + dx, oy - MAIN_SPAR_SPAN),
                     (spar_draw_x + dx, oy + MAIN_SPAR_SPAN),
                     dxfattribs={"layer": "SPAR"})

    # ── Rear spar: STRAIGHT vertical line ──
    # At root: 60% of 115mm chord = 69mm from LE = 69 - 28.75 = 40.25mm from spar
    rear_spar_x = spar_draw_x + (0.60 - spar_frac_at(0)) * chord_at(0)
    msp.add_line((rear_spar_x, oy - REAR_SPAR_SPAN),
                 (rear_spar_x, oy + REAR_SPAR_SPAN),
                 dxfattribs={"layer": "SPAR"})

    # ── Elevator stiffener: STRAIGHT vertical line ──
    # At root: 80% of 115mm = 92mm from LE = 92 - 28.75 = 63.25mm from spar
    stiffener_x = spar_draw_x + (0.80 - spar_frac_at(0)) * chord_at(0)
    msp.add_line((stiffener_x, oy - STIFFENER_SPAN),
                 (stiffener_x, oy + STIFFENER_SPAN),
                 dxfattribs={"layer": "SPAR"})

    # ── Hinge wire: along the hinge line, tip to tip (dashed green) ──
    # The hinge wire follows the hinge line curve (it bends to follow it)
    # Actually the wire is threaded through knuckles along the hinge line
    # For drawing purposes, show it coincident with hinge line but in SPAR layer
    # Already drawn as hinge line above, just label it

    # ── Control horn position ──
    horn_y = oy - CONTROL_HORN_Y  # left side, 15mm from root
    horn_x = hinge_root_x  # at hinge line
    # Small triangle symbol for horn
    msp.add_line((horn_x, horn_y), (horn_x + 3, horn_y - HORN_HEIGHT * 0.4),
                 dxfattribs={"layer": "SECTION"})
    msp.add_line((horn_x + 3, horn_y - HORN_HEIGHT * 0.4),
                 (horn_x - 3, horn_y - HORN_HEIGHT * 0.4),
                 dxfattribs={"layer": "SECTION"})
    msp.add_line((horn_x - 3, horn_y - HORN_HEIGHT * 0.4),
                 (horn_x, horn_y),
                 dxfattribs={"layer": "SECTION"})
    msp.add_text("CONTROL\nHORN", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (horn_x + 4, horn_y - HORN_HEIGHT * 0.3))

    # ── Bridge joiner at root ──
    bridge_y = oy
    bridge_x = hinge_root_x - 2  # just forward of hinge
    # U-channel symbol
    bw = BRIDGE_WIDTH * 0.15  # scaled for planform
    bh = BRIDGE_SPAN / 2
    msp.add_line((bridge_x, oy - bh), (bridge_x, oy + bh),
                 dxfattribs={"layer": "SECTION"})
    msp.add_line((bridge_x + bw, oy - bh), (bridge_x + bw, oy + bh),
                 dxfattribs={"layer": "SECTION"})
    msp.add_line((bridge_x, oy - bh), (bridge_x + bw, oy - bh),
                 dxfattribs={"layer": "SECTION"})
    msp.add_line((bridge_x, oy + bh), (bridge_x + bw, oy + bh),
                 dxfattribs={"layer": "SECTION"})
    msp.add_text("BRIDGE\nJOINER", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (bridge_x + bw + 2, oy - 2))

    # ── Rudder clearance zone (hatched area) ──
    # The rudder sweeps laterally at the TE overlap zone (X=983 to X=994 in fuselage coords)
    # In our drawing, this is near the TE of the elevator at root
    # Show as a cross-hatched rectangle near root TE
    rc_x1 = te_root_x - 11 * (TE_FRAC - sf_root) / (TE_FRAC - HINGE_FRAC)  # approximate
    rc_x2 = te_root_x
    rc_y1 = oy - ROOT_GAP_AT_TE / 2
    rc_y2 = oy + ROOT_GAP_AT_TE / 2
    # Draw rectangle outline
    msp.add_line((rc_x1, rc_y1), (rc_x2, rc_y1), dxfattribs={"layer": "HATCH"})
    msp.add_line((rc_x2, rc_y1), (rc_x2, rc_y2), dxfattribs={"layer": "HATCH"})
    msp.add_line((rc_x2, rc_y2), (rc_x1, rc_y2), dxfattribs={"layer": "HATCH"})
    msp.add_line((rc_x1, rc_y2), (rc_x1, rc_y1), dxfattribs={"layer": "HATCH"})
    # Cross-hatch lines
    n_hatch = 6
    for i in range(1, n_hatch):
        frac = i / n_hatch
        hx = rc_x1 + frac * (rc_x2 - rc_x1)
        msp.add_line((hx, rc_y1), (hx, rc_y2), dxfattribs={"layer": "HATCH"})
    msp.add_text("RUDDER\nCLEARANCE\nZONE", height=1.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (rc_x2 + 2, oy - 2))

    # ── Section cut lines ──
    # Section A-A through root (horizontal line at y=0)
    cut_x1 = le_root_x - 8
    cut_x2 = te_root_x + 8
    for ext_x, label_x_off in [(cut_x1, -5), (cut_x2, 2)]:
        msp.add_line((ext_x, oy), (ext_x, oy + 3), dxfattribs={"layer": "SECTION"})
        msp.add_line((ext_x, oy), (ext_x, oy - 3), dxfattribs={"layer": "SECTION"})
        msp.add_text("A", height=2.5, dxfattribs={"layer": "SECTION"}).set_placement(
            (ext_x + label_x_off, oy - 1))
    msp.add_line((cut_x1, oy), (le_root_x - 2, oy),
                 dxfattribs={"layer": "SECTION", "linetype": "DASHDOT"})
    msp.add_line((te_root_x + 2, oy), (cut_x2, oy),
                 dxfattribs={"layer": "SECTION", "linetype": "DASHDOT"})

    # Section B-B through hinge detail (vertical line at hinge X)
    cut_y1 = oy - HALF_SPAN * 0.3
    cut_y2 = oy + HALF_SPAN * 0.3
    for ext_y, label_y_off in [(cut_y1, -4), (cut_y2, 2)]:
        msp.add_line((hinge_root_x, ext_y), (hinge_root_x + 3, ext_y),
                     dxfattribs={"layer": "SECTION"})
        msp.add_line((hinge_root_x, ext_y), (hinge_root_x - 3, ext_y),
                     dxfattribs={"layer": "SECTION"})
        msp.add_text("B", height=2.5, dxfattribs={"layer": "SECTION"}).set_placement(
            (hinge_root_x + 4, ext_y + label_y_off))

    # ── Spar / structure labels ──
    label_y = oy + MAIN_SPAR_SPAN + 5
    msp.add_text("MAIN SPAR", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (spar_draw_x - 8, label_y))
    msp.add_text("3mm CF tube", height=1.2, dxfattribs={"layer": "TEXT"}).set_placement(
        (spar_draw_x - 8, label_y - 2.5))

    msp.add_text("REAR SPAR", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (rear_spar_x - 5, label_y))
    msp.add_text("1.5mm CF rod", height=1.2, dxfattribs={"layer": "TEXT"}).set_placement(
        (rear_spar_x - 5, label_y - 2.5))

    msp.add_text("STIFFENER", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (stiffener_x - 5, label_y))
    msp.add_text("1mm CF rod", height=1.2, dxfattribs={"layer": "TEXT"}).set_placement(
        (stiffener_x - 5, label_y - 2.5))

    # LE label
    msp.add_text("LE", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (le_root_x - 6, oy + HALF_SPAN * 0.85))

    # TE label
    msp.add_text("TE", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (te_root_x + 2, oy + HALF_SPAN * 0.85))

    # Hinge line label
    msp.add_text("HINGE LINE\n(65% chord)", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (hinge_root_x + 3, oy + HALF_SPAN * 0.8))

    # ── DIMENSIONS ──
    dim_style = "AEROFORGE"

    # Full span dimension (vertical, along LE side)
    dim = msp.add_linear_dim(
        base=(le_root_x - 15, oy),
        p1=(le_root_x, oy - HALF_SPAN),
        p2=(le_root_x, oy + HALF_SPAN),
        angle=90, dimstyle=dim_style)
    dim.render()

    # Half span dimension (right side only)
    dim = msp.add_linear_dim(
        base=(te_root_x + 12, oy),
        p1=(te_root_x, oy),
        p2=(te_root_x, oy + HALF_SPAN),
        angle=90, dimstyle=dim_style)
    dim.render()

    # Root chord dimension
    dim = msp.add_linear_dim(
        base=(le_root_x, oy + HALF_SPAN + 10),
        p1=(le_root_x, oy),
        p2=(te_root_x, oy),
        dimstyle=dim_style)
    dim.render()

    # Stab chord at root (LE to hinge)
    dim = msp.add_linear_dim(
        base=(le_root_x, oy + HALF_SPAN + 18),
        p1=(le_root_x, oy),
        p2=(hinge_root_x, oy),
        dimstyle=dim_style)
    dim.render()

    # Elevator chord at root (hinge to TE)
    dim = msp.add_linear_dim(
        base=(hinge_root_x, oy - HALF_SPAN - 10),
        p1=(hinge_root_x, oy),
        p2=(te_root_x, oy),
        dimstyle=dim_style)
    dim.render()

    # Main spar position from LE (at root)
    dim = msp.add_linear_dim(
        base=(le_root_x, oy + HALF_SPAN + 25),
        p1=(le_root_x, oy),
        p2=(spar_draw_x, oy),
        dimstyle=dim_style)
    dim.render()

    # Root gap dimension
    dim = msp.add_linear_dim(
        base=(hinge_root_x - 10, oy),
        p1=(hinge_root_x, oy - ROOT_GAP_AT_HINGE / 2),
        p2=(hinge_root_x, oy + ROOT_GAP_AT_HINGE / 2),
        angle=90, dimstyle=dim_style)
    dim.render()

    # Main spar span dimension
    dim = msp.add_linear_dim(
        base=(spar_draw_x - 10, oy),
        p1=(spar_draw_x, oy - MAIN_SPAR_SPAN),
        p2=(spar_draw_x, oy + MAIN_SPAR_SPAN),
        angle=90, dimstyle=dim_style)
    dim.render()

    # View title
    msp.add_text("VIEW 1: PLANFORM (TOP VIEW)", height=3.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox, oy + HALF_SPAN + 32))

    return spar_draw_x  # return for reference by other views


def draw_root_section(msp, ox: float, oy: float):
    """View 2: Root cross-section (A-A) showing full airfoil at y=0.

    Convention: LE on LEFT, TE on RIGHT. X = chordwise, Y = thickness.
    """
    chord = ROOT_CHORD
    n_pts = 80

    # Draw complete airfoil from LE to 97% chord (stab portion + elevator)
    # Stab: LE to 65% chord
    # Elevator: 65% to 97% chord (with gap)

    # ── Stab shell (thick outline) ──
    for i in range(n_pts):
        xc1 = HINGE_FRAC * i / n_pts
        xc2 = HINGE_FRAC * (i + 1) / n_pts
        x1 = ox + xc1 * chord
        x2 = ox + xc2 * chord
        yt1 = ht13_yt(xc1, chord)
        yt2 = ht13_yt(xc2, chord)
        # Upper surface
        msp.add_line((x1, oy + yt1), (x2, oy + yt2),
                     dxfattribs={"layer": "OUTLINE"})
        # Lower surface
        msp.add_line((x1, oy - yt1), (x2, oy - yt2),
                     dxfattribs={"layer": "OUTLINE"})

    # LE closure
    yt_le = ht13_yt(0.005, chord)
    msp.add_line((ox, oy + yt_le), (ox, oy - yt_le), dxfattribs={"layer": "OUTLINE"})

    # Stab TE face (at 65% chord) -- vertical line
    hinge_x = ox + HINGE_FRAC * chord
    yt_hinge = ht13_yt(HINGE_FRAC, chord)
    msp.add_line((hinge_x, oy + yt_hinge), (hinge_x, oy - yt_hinge),
                 dxfattribs={"layer": "OUTLINE"})

    # ── Elevator shell (medium outline, shifted right by gap) ──
    elev_offset = HINGE_GAP  # 0.3mm gap
    for i in range(n_pts):
        xc1 = HINGE_FRAC + (TE_FRAC - HINGE_FRAC) * i / n_pts
        xc2 = HINGE_FRAC + (TE_FRAC - HINGE_FRAC) * (i + 1) / n_pts
        x1 = ox + xc1 * chord + elev_offset
        x2 = ox + xc2 * chord + elev_offset
        yt1 = ht13_yt(xc1, chord)
        yt2 = ht13_yt(xc2, chord)
        # Upper surface
        msp.add_line((x1, oy + yt1), (x2, oy + yt2),
                     dxfattribs={"layer": "OUTLINE"})
        # Lower surface
        msp.add_line((x1, oy - yt1), (x2, oy - yt2),
                     dxfattribs={"layer": "OUTLINE"})

    # Elevator LE face
    elev_le_x = hinge_x + elev_offset
    msp.add_line((elev_le_x, oy + yt_hinge), (elev_le_x, oy - yt_hinge),
                 dxfattribs={"layer": "OUTLINE"})

    # Elevator TE closure (97% chord)
    te_x = ox + TE_FRAC * chord + elev_offset
    yt_te = ht13_yt(TE_FRAC, chord)
    msp.add_line((te_x, oy + yt_te), (te_x, oy - yt_te),
                 dxfattribs={"layer": "OUTLINE"})

    # ── Internal structure ──
    # Main spar tunnel at 25% chord
    spar_cx = ox + 0.25 * chord
    msp.add_circle((spar_cx, oy), MAIN_SPAR_TUNNEL_ID / 2,
                   dxfattribs={"layer": "SPAR"})
    # Spar tube
    msp.add_circle((spar_cx, oy), MAIN_SPAR_DIA / 2,
                   dxfattribs={"layer": "SPAR"})

    # Rear spar tunnel at 60% chord
    rspar_cx = ox + 0.60 * chord
    msp.add_circle((rspar_cx, oy), REAR_SPAR_TUNNEL_ID / 2,
                   dxfattribs={"layer": "SPAR"})
    msp.add_circle((rspar_cx, oy), REAR_SPAR_DIA / 2,
                   dxfattribs={"layer": "SPAR"})

    # Elevator stiffener tunnel at 80% chord (in elevator, so offset)
    stiff_cx = ox + 0.80 * chord + elev_offset
    msp.add_circle((stiff_cx, oy), STIFFENER_TUNNEL_ID / 2,
                   dxfattribs={"layer": "SPAR"})
    msp.add_circle((stiff_cx, oy), STIFFENER_DIA / 2,
                   dxfattribs={"layer": "SPAR"})

    # Hinge wire at hinge line (between stab and elevator)
    wire_cx = hinge_x + elev_offset / 2  # centered in gap
    msp.add_circle((wire_cx, oy), HINGE_WIRE_DIA / 2,
                   dxfattribs={"layer": "SPAR"})

    # ── Wall thickness indicators (inner profile offset) ──
    # Stab wall
    for i in range(0, n_pts, 4):
        xc = HINGE_FRAC * i / n_pts
        if xc < 0.03:
            continue
        x_draw = ox + xc * chord
        yt_out = ht13_yt(xc, chord)
        if yt_out > WALL_THICKNESS_STAB * 2:
            for sgn in [1, -1]:
                msp.add_circle((x_draw, oy + sgn * (yt_out - WALL_THICKNESS_STAB)),
                               0.15, dxfattribs={"layer": "WALL"})

    # ── Annotations ──
    # Wall thickness
    msp.add_text(f"Wall: {WALL_THICKNESS_STAB}mm (stab)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + 0.35 * chord, oy + ht13_yt(0.35, chord) + 2))
    msp.add_text(f"Wall: {WALL_THICKNESS_ELEV}mm (elev)", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + 0.80 * chord + elev_offset, oy + ht13_yt(0.80, chord) + 2))

    # Spar labels
    msp.add_text("MAIN SPAR\n3.1mm tunnel", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (spar_cx - 5, oy - ht13_yt(0.25, chord) - 4))
    msp.add_text("REAR SPAR\n1.6mm tunnel", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (rspar_cx - 5, oy - ht13_yt(0.60, chord) - 4))
    msp.add_text("STIFFENER\n1.1mm tunnel", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (stiff_cx - 5, oy - ht13_yt(0.80, chord) - 4))
    msp.add_text("HINGE\nWIRE 0.5mm", height=1.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (wire_cx - 4, oy + yt_hinge + 2))

    # LE / TE labels
    msp.add_text("LE", height=2.0, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox - 5, oy + 1))
    msp.add_text("TE (97%)", height=1.5, dxfattribs={"layer": "TEXT"}).set_placement(
        (te_x + 2, oy + 1))

    # Gap annotation
    msp.add_text(f"GAP {HINGE_GAP}mm", height=1.2,
                 dxfattribs={"layer": "DIMENSION"}).set_placement(
        (hinge_x - 3, oy + yt_hinge + 4))

    # Bevel angle annotations with leader lines
    bevel_y_upper = oy + yt_hinge + 1
    bevel_y_lower = oy - yt_hinge - 1
    msp.add_text(f"Bevel {int(BEVEL_UPPER)} deg (upper)", height=1.0,
                 dxfattribs={"layer": "DIMENSION"}).set_placement(
        (hinge_x - 12, bevel_y_upper + 1))
    msp.add_text(f"Bevel {int(BEVEL_LOWER)} deg (lower)", height=1.0,
                 dxfattribs={"layer": "DIMENSION"}).set_placement(
        (hinge_x - 12, bevel_y_lower - 2))

    # ── Dimensions ──
    dim_style = "AEROFORGE"

    # Full chord
    dim = msp.add_linear_dim(
        base=(ox, oy - ht13_yt(0.30, chord) - 10),
        p1=(ox, oy),
        p2=(te_x, oy),
        dimstyle=dim_style)
    dim.render()

    # Stab chord (LE to hinge)
    dim = msp.add_linear_dim(
        base=(ox, oy + ht13_yt(0.30, chord) + 8),
        p1=(ox, oy),
        p2=(hinge_x, oy),
        dimstyle=dim_style)
    dim.render()

    # Spar position
    dim = msp.add_linear_dim(
        base=(ox, oy + ht13_yt(0.30, chord) + 14),
        p1=(ox, oy),
        p2=(spar_cx, oy),
        dimstyle=dim_style)
    dim.render()

    # Airfoil thickness
    yt_max = ht13_yt(0.30, chord)
    dim = msp.add_linear_dim(
        base=(ox + 0.30 * chord - 8, oy),
        p1=(ox + 0.30 * chord, oy - yt_max),
        p2=(ox + 0.30 * chord, oy + yt_max),
        angle=90, dimstyle=dim_style)
    dim.render()

    # View title
    msp.add_text("VIEW 2: SECTION A-A (ROOT)", height=3.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox, oy - ht13_yt(0.30, chord) - 18))
    msp.add_text("HT-13 (6.5% t/c) | Chord 115mm", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox, oy - ht13_yt(0.30, chord) - 22))


def draw_hinge_detail(msp, ox: float, oy: float):
    """View 3: Hinge detail — zoomed cross-section at hinge line.

    Shows bevel geometry at 0 deg neutral and +25 deg deflection (side by side).
    Scale: 5:1 zoom for clarity.
    """
    chord = ROOT_CHORD
    scale = 5.0  # 5:1 magnification

    # At 65% chord, airfoil thickness
    yt_hinge_upper = ht13_yt(HINGE_FRAC, chord) * scale  # upper surface ordinate
    yt_hinge_lower = -ht13_yt(HINGE_FRAC, chord) * scale  # lower

    # Hinge wire radius (scaled)
    wire_r = HINGE_WIRE_DIA / 2 * scale

    # ── NEUTRAL (0 deg) ──
    nx = ox
    ny = oy

    # Draw a portion of the airfoil around the hinge
    # Show ~5mm of stab (left) and ~5mm of elevator (right), scaled
    extent = 5.0 * scale  # 25mm drawing extent each side

    # Stab TE face (left side of hinge)
    stab_te_x = nx  # hinge point
    # Upper surface approaching hinge from left (stab side)
    for i in range(20):
        xc1 = HINGE_FRAC - (0.05 * (20 - i) / 20)
        xc2 = HINGE_FRAC - (0.05 * (19 - i) / 20) if i < 19 else HINGE_FRAC
        x1 = nx - (HINGE_FRAC - xc1) * chord * scale
        x2 = nx - (HINGE_FRAC - xc2) * chord * scale
        yt1 = ht13_yt(xc1, chord) * scale
        yt2 = ht13_yt(xc2, chord) * scale
        msp.add_line((x1, ny + yt1), (x2, ny + yt2), dxfattribs={"layer": "OUTLINE"})
        msp.add_line((x1, ny - yt1), (x2, ny - yt2), dxfattribs={"layer": "OUTLINE"})

    # Stab TE face — beveled
    # Upper bevel: 11 deg from vertical (aft-chamfer)
    bevel_upper_half = BEVEL_UPPER / 2  # 11 deg on stab side
    bevel_lower_half = BEVEL_LOWER / 2 + 1  # ~14 deg on stab side (14 deg)
    # Draw beveled face: from hinge axis to upper surface
    bevel_upper_dx = yt_hinge_upper * math.tan(math.radians(bevel_upper_half))
    bevel_lower_dx = abs(yt_hinge_lower) * math.tan(math.radians(bevel_lower_half))

    # Stab bevel face (upper: angled back from wire to upper surface)
    msp.add_line((stab_te_x, ny), (stab_te_x - bevel_upper_dx, ny + yt_hinge_upper),
                 dxfattribs={"layer": "OUTLINE"})
    # Stab bevel face (lower: angled back from wire to lower surface)
    msp.add_line((stab_te_x, ny), (stab_te_x - bevel_lower_dx, ny + yt_hinge_lower),
                 dxfattribs={"layer": "OUTLINE"})

    # Gap
    gap_scaled = HINGE_GAP * scale

    # Elevator LE face — beveled (right side of hinge)
    elev_le_x = stab_te_x + gap_scaled
    # Upper surface from hinge rightward
    for i in range(20):
        xc1 = HINGE_FRAC + (0.05 * i / 20)
        xc2 = HINGE_FRAC + (0.05 * (i + 1) / 20)
        x1 = elev_le_x + (xc1 - HINGE_FRAC) * chord * scale
        x2 = elev_le_x + (xc2 - HINGE_FRAC) * chord * scale
        yt1 = ht13_yt(xc1, chord) * scale
        yt2 = ht13_yt(xc2, chord) * scale
        msp.add_line((x1, ny + yt1), (x2, ny + yt2), dxfattribs={"layer": "OUTLINE"})
        msp.add_line((x1, ny - yt1), (x2, ny - yt2), dxfattribs={"layer": "OUTLINE"})

    # Elevator bevel faces
    elev_bevel_upper = BEVEL_UPPER / 2  # 11 deg
    elev_bevel_lower = BEVEL_LOWER / 2 - 1  # ~13 deg (total 27 = 14+13)
    elev_upper_dx = yt_hinge_upper * math.tan(math.radians(elev_bevel_upper))
    elev_lower_dx = abs(yt_hinge_lower) * math.tan(math.radians(elev_bevel_lower))

    msp.add_line((elev_le_x, ny), (elev_le_x + elev_upper_dx, ny + yt_hinge_upper),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_line((elev_le_x, ny), (elev_le_x + elev_lower_dx, ny + yt_hinge_lower),
                 dxfattribs={"layer": "OUTLINE"})

    # Hinge wire (circle at center)
    msp.add_circle((stab_te_x + gap_scaled / 2, ny), wire_r,
                   dxfattribs={"layer": "SPAR"})

    # Knuckle (shown as small circles on lower surface)
    knuckle_r = KNUCKLE_OD / 2 * scale
    knuckle_y = ny + yt_hinge_lower  # on lower surface
    # Stab knuckle
    msp.add_circle((stab_te_x - 1, knuckle_y - knuckle_r), knuckle_r,
                   dxfattribs={"layer": "SECTION"})
    # Elevator knuckle
    msp.add_circle((elev_le_x + 1, knuckle_y - knuckle_r), knuckle_r,
                   dxfattribs={"layer": "SECTION"})

    # Annotations for neutral position
    msp.add_text("NEUTRAL (0 deg)", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (nx - extent * 0.6, ny + yt_hinge_upper + 8))
    msp.add_text(f"Gap: {HINGE_GAP}mm", height=1.5,
                 dxfattribs={"layer": "DIMENSION"}).set_placement(
        (stab_te_x - 2, ny + yt_hinge_upper + 4))

    # Bevel angle annotations
    msp.add_text(f"{int(BEVEL_UPPER)} deg", height=1.5,
                 dxfattribs={"layer": "DIMENSION"}).set_placement(
        (stab_te_x - bevel_upper_dx - 5, ny + yt_hinge_upper * 0.7))
    msp.add_text(f"{int(BEVEL_LOWER)} deg", height=1.5,
                 dxfattribs={"layer": "DIMENSION"}).set_placement(
        (stab_te_x - bevel_lower_dx - 5, ny + yt_hinge_lower * 0.7))

    # Knuckle labels
    msp.add_text("KNUCKLE", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (stab_te_x - 8, knuckle_y - knuckle_r * 2 - 3))
    msp.add_text("KNUCKLE", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (elev_le_x + 3, knuckle_y - knuckle_r * 2 - 3))

    # ── DEFLECTED (+25 deg, nose up) ──
    dx = ox + extent * 2.5  # offset to the right for the deflected view
    dy = oy

    # Draw stab TE portion (same as neutral — stab is fixed)
    for i in range(20):
        xc1 = HINGE_FRAC - (0.05 * (20 - i) / 20)
        xc2 = HINGE_FRAC - (0.05 * (19 - i) / 20) if i < 19 else HINGE_FRAC
        x1 = dx - (HINGE_FRAC - xc1) * chord * scale
        x2 = dx - (HINGE_FRAC - xc2) * chord * scale
        yt1 = ht13_yt(xc1, chord) * scale
        yt2 = ht13_yt(xc2, chord) * scale
        msp.add_line((x1, dy + yt1), (x2, dy + yt2), dxfattribs={"layer": "OUTLINE"})
        msp.add_line((x1, dy - yt1), (x2, dy - yt2), dxfattribs={"layer": "OUTLINE"})

    # Stab bevel face (same geometry)
    msp.add_line((dx, dy), (dx - bevel_upper_dx, dy + yt_hinge_upper),
                 dxfattribs={"layer": "OUTLINE"})
    msp.add_line((dx, dy), (dx - bevel_lower_dx, dy + yt_hinge_lower),
                 dxfattribs={"layer": "OUTLINE"})

    # Elevator — rotated by +25 deg about the hinge wire axis
    defl_rad = math.radians(DEFL_UP)  # +25 deg
    elev_pivot_x = dx + gap_scaled / 2
    elev_pivot_y = dy

    def rotate_point(px, py, cx, cy, angle):
        """Rotate (px,py) around (cx,cy) by angle (radians)."""
        dx_ = px - cx
        dy_ = py - cy
        rx = dx_ * math.cos(angle) - dy_ * math.sin(angle) + cx
        ry = dx_ * math.sin(angle) + dy_ * math.cos(angle) + cy
        return rx, ry

    # Draw rotated elevator profile
    elev_le_x_defl = dx + gap_scaled
    for i in range(20):
        xc1 = HINGE_FRAC + (0.05 * i / 20)
        xc2 = HINGE_FRAC + (0.05 * (i + 1) / 20)
        # Unrotated positions
        ux1 = elev_le_x_defl + (xc1 - HINGE_FRAC) * chord * scale
        ux2 = elev_le_x_defl + (xc2 - HINGE_FRAC) * chord * scale
        uyt1 = ht13_yt(xc1, chord) * scale
        uyt2 = ht13_yt(xc2, chord) * scale

        # Rotate upper surface
        rx1u, ry1u = rotate_point(ux1, dy + uyt1, elev_pivot_x, elev_pivot_y, defl_rad)
        rx2u, ry2u = rotate_point(ux2, dy + uyt2, elev_pivot_x, elev_pivot_y, defl_rad)
        msp.add_line((rx1u, ry1u), (rx2u, ry2u), dxfattribs={"layer": "HIDDEN"})

        # Rotate lower surface
        rx1l, ry1l = rotate_point(ux1, dy - uyt1, elev_pivot_x, elev_pivot_y, defl_rad)
        rx2l, ry2l = rotate_point(ux2, dy - uyt2, elev_pivot_x, elev_pivot_y, defl_rad)
        msp.add_line((rx1l, ry1l), (rx2l, ry2l), dxfattribs={"layer": "HIDDEN"})

    # Rotated elevator bevel faces
    ru1 = rotate_point(elev_le_x_defl + elev_upper_dx, dy + yt_hinge_upper,
                       elev_pivot_x, elev_pivot_y, defl_rad)
    rl1 = rotate_point(elev_le_x_defl + elev_lower_dx, dy + yt_hinge_lower,
                       elev_pivot_x, elev_pivot_y, defl_rad)
    re0 = rotate_point(elev_le_x_defl, dy, elev_pivot_x, elev_pivot_y, defl_rad)
    msp.add_line(re0, ru1, dxfattribs={"layer": "HIDDEN"})
    msp.add_line(re0, rl1, dxfattribs={"layer": "HIDDEN"})

    # Hinge wire (same position)
    msp.add_circle((elev_pivot_x, elev_pivot_y), wire_r,
                   dxfattribs={"layer": "SPAR"})

    # Deflection arc indicator
    arc_r = extent * 0.3
    msp.add_arc((elev_pivot_x, elev_pivot_y), arc_r,
                start_angle=0, end_angle=DEFL_UP,
                dxfattribs={"layer": "DIMENSION"})

    # Annotations for deflected position
    msp.add_text(f"+{int(DEFL_UP)} deg (NOSE UP)", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (dx - extent * 0.3, dy + yt_hinge_upper + 8))
    msp.add_text("Bevel clears\nwith 2 deg margin", height=1.3,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (dx - bevel_lower_dx - 15, dy + yt_hinge_lower * 0.5))

    # Deflection angle dimension
    msp.add_text(f"{int(DEFL_UP)} deg", height=1.8,
                 dxfattribs={"layer": "DIMENSION"}).set_placement(
        (elev_pivot_x + arc_r + 2, elev_pivot_y + 3))

    # View title
    msp.add_text("VIEW 3: HINGE DETAIL (SECTION B-B)", height=3.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox - extent * 0.6, ny + yt_hinge_upper + 14))
    msp.add_text("Scale 5:1", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox - extent * 0.6, ny + yt_hinge_upper + 10))


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    # Create drawing with professional template (A3 landscape)
    doc = setup_drawing(
        title="HStab_Assembly",
        drawing_number="AF-EMP-ASM-001",
        subtitle="Horizontal Stabilizer Assembly — Fixed Stab + 35% Elevator, Superellipse n=2.3",
        material="LW-PLA (shells) + CF tube/rod (spars) + Music wire (hinge) + CF-PLA (horn/bridge)",
        scale="1:1 (planform/section), 5:1 (hinge detail)",
        mass="34.2g",
        status="FOR APPROVAL",
        revision="A",
        sheet_size="A3",
        orientation_labels={"fwd": "FWD", "inbd": "INBD"},
    )

    msp = doc.modelspace()

    # ── A3 layout coordinates ──
    # A3 landscape: 420 x 297mm
    # Drawing area: x=20..410, y=10..287
    # Title block occupies bottom-right: x=240..410, y=10..46
    # Available area: roughly 390 x 277mm

    # View 1: PLANFORM — upper 2/3, centered
    # Place root at center-bottom of planform area
    # Planform needs ~115mm width (chord) and ~430mm height (span)
    # Scale 1:1 would need 430mm vertical -- too tall for A3 (277mm usable)
    # We need to fit 430mm span into ~180mm vertical space -> effective scale ~1:2.4
    # Actually let's use about 60% scale to fit nicely
    PLAN_SCALE = 0.55  # scale factor for planform view only
    # We'll apply this by scaling coordinates in the planform function

    # Alternative: use 1:1 but rotate planform 90 deg (span horizontal)
    # That would fit 430mm into 390mm horizontal space.
    # Let's do span-horizontal for better fit.

    # Actually, the task says "Root at bottom-center of drawing, tips at top-left and top-right"
    # This means span is VERTICAL (Y direction). We need to scale.

    # Plan: place planform centered, use scale factor for coordinates
    planform_ox = 60  # left margin for planform
    planform_oy = 155  # vertical center for root (span goes +-95mm at 0.55 scale)

    # We apply the scale by having the planform use scaled coordinates
    # Let's write a scaled wrapper instead of modifying draw_planform
    draw_planform_scaled(msp, planform_ox, planform_oy, PLAN_SCALE)

    # View 2: ROOT CROSS-SECTION — lower-left
    # Full airfoil at 1:1 scale, needs ~115mm width, ~8mm height
    section_ox = 25
    section_oy = 50
    draw_root_section(msp, section_ox, section_oy)

    # View 3: HINGE DETAIL — lower-right
    # 5:1 scale, needs ~50mm width, ~40mm height
    hinge_ox = 280
    hinge_oy = 55
    draw_hinge_detail(msp, hinge_ox, hinge_oy)

    # ── Assembly BOM (parts list) in available space ──
    bom_x = 25
    bom_y = 18
    msp.add_text("PARTS LIST:", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement((bom_x, bom_y))
    parts = [
        "1. HStab_Left (LW-PLA, 8.5g)",
        "2. HStab_Right (mirror, 8.5g)",
        "3. Elevator_Left (LW-PLA, 3.75g)",
        "4. Elevator_Right (mirror, 3.75g)",
        "5. Main Spar (3mm CF tube, 2.4g)",
        "6. Rear Spar (1.5mm CF rod, 1.2g)",
        "7. Stiffener (1mm CF rod, 0.44g)",
        "8. Hinge Wire (0.5mm music wire, 0.68g)",
        "9. 4x PETG Hinge Strips (2.0g)",
        "10. Control Horn (CF-PLA, 0.8g)",
        "11. Bridge Joiner (CF-PLA, 0.6g)",
        "12. Mass Balance (W putty, 1.0g)",
    ]
    for i, part in enumerate(parts):
        msp.add_text(part, height=1.3,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (bom_x, bom_y - 3 - i * 2.5))

    # Save
    out_path = "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf"
    dxf_out, png_out = save_dxf_and_png(doc, out_path)

    print(f"\nH-STAB ASSEMBLY DRAWING — FROM DESIGN CONSENSUS v3.1")
    print(f"  Superellipse n=2.3 | {SPAN:.0f}mm span | {ROOT_CHORD:.0f}mm root chord")
    print(f"  Fixed stab + 35% elevator | Music wire hinge")
    print(f"  Mass: 34.2g | 12 components")
    print(f"  DXF: {dxf_out}")
    print(f"  PNG: {png_out}")


def draw_planform_scaled(msp, ox: float, oy: float, sc: float):
    """Planform view with scale factor applied.

    COORDINATE SYSTEM (from DESIGN_CONSENSUS v5):
      ox = drawing X position of root LE (X=0 in local H-Stab coords)
      oy = drawing Y position of root (Y=0, VStab fin centerline)
      sc = scale factor (e.g. 0.5 for 1:2)

    Drawing X = ox + local_x * sc   (chordwise: LE at small X, TE at large X)
    Drawing Y = oy + local_y * sc   (spanwise: root at center, tips at edges)

    ALL RODS are STRAIGHT VERTICAL LINES at constant X positions.
    Only LE and TE curves (superellipse planform).
    """
    # ── Consensus v5 planform formulas ──
    # c(y) = 115 * (1 - |y/215|^2.3)^(1/2.3)
    # x_LE(y) = 51.75 - 0.45 * c(y)
    # x_TE(y) = x_LE(y) + 0.97 * c(y)  [at 97% truncation]
    #
    # ALL rods at FIXED X from root LE:
    #   Main spar X=35.0, Rear spar X=69.0, Hinge X=74.75, Stiffener X=92.0

    def dx(local_x):
        """Convert local X to drawing X."""
        return ox + local_x * sc

    def dy(local_y):
        """Convert local Y to drawing Y."""
        return oy + local_y * sc

    stations = planform_stations(HALF_SPAN, 60)

    # ── Planform outline (LE and TE curves) ──
    for sign in [1, -1]:
        le_pts = []
        te_pts = []

        for y in stations:
            c = chord_at(y)
            if c <= 0:
                break
            x_le = 51.75 - 0.45 * c
            x_te = x_le + TE_FRAC * c

            le_pts.append((dx(x_le), dy(sign * y)))
            te_pts.append((dx(x_te), dy(sign * y)))

        # LE outline
        for i in range(len(le_pts) - 1):
            msp.add_line(le_pts[i], le_pts[i + 1], dxfattribs={"layer": "OUTLINE"})

        # TE outline
        for i in range(len(te_pts) - 1):
            msp.add_line(te_pts[i], te_pts[i + 1], dxfattribs={"layer": "OUTLINE"})

        # Tip closure
        if le_pts and te_pts:
            msp.add_line(le_pts[-1], te_pts[-1], dxfattribs={"layer": "OUTLINE"})

        # Labels (placed at 45% span to avoid overlap)
        side_name = "RIGHT" if sign > 0 else "LEFT"
        label_y = dy(sign * HALF_SPAN * 0.45)
        msp.add_text(f"{side_name} STAB", height=1.8,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (dx(20), label_y))
        msp.add_text(f"{side_name} ELEVATOR", height=1.5,
                     dxfattribs={"layer": "TEXT"}).set_placement(
            (dx(80), label_y))

    # ── Root chord line (stab: LE to hinge) ──
    le_root_x = dx(0)        # LE at root = X=0
    hinge_dx = dx(74.75)     # hinge at fixed X=74.75
    te_root_x = dx(111.55)   # TE at 97% of 115mm
    spar_dx = dx(35.0)       # main spar at fixed X=35.0
    rear_dx = dx(69.0)       # rear spar at fixed X=69.0
    stiff_dx = dx(92.0)      # stiffener at fixed X=92.0

    msp.add_line((le_root_x, oy), (hinge_dx, oy), dxfattribs={"layer": "OUTLINE"})

    # ── Elevator root lines with gap for VStab fin ──
    gap_half_dy = ROOT_GAP_AT_HINGE / 2 * sc
    for sign in [1, -1]:
        msp.add_line((hinge_dx, oy + sign * gap_half_dy),
                     (te_root_x, oy + sign * gap_half_dy),
                     dxfattribs={"layer": "OUTLINE"})

    # ── VStab fin (dashed rectangle) ──
    fin_half = VSTAB_FIN_WIDTH / 2 * sc
    fin_x1 = dx(25)
    fin_x2 = te_root_x + 3 * sc
    for ddy in [fin_half, -fin_half]:
        msp.add_line((fin_x1, oy + ddy), (fin_x2, oy + ddy),
                     dxfattribs={"layer": "HIDDEN"})
    msp.add_line((fin_x1, oy - fin_half), (fin_x1, oy + fin_half),
                 dxfattribs={"layer": "HIDDEN"})
    msp.add_line((fin_x2, oy - fin_half), (fin_x2, oy + fin_half),
                 dxfattribs={"layer": "HIDDEN"})

    # ── ALL RODS: STRAIGHT VERTICAL LINES at constant X ──

    # Main spar: 3mm CF tube at X=35.0, ±186mm
    spar_span_sc = MAIN_SPAR_SPAN * sc
    msp.add_line((spar_dx, oy - spar_span_sc), (spar_dx, oy + spar_span_sc),
                 dxfattribs={"layer": "SPAR"})
    spar_hw = MAIN_SPAR_DIA / 2 * sc
    for ddx in [-spar_hw, spar_hw]:
        msp.add_line((spar_dx + ddx, oy - spar_span_sc),
                     (spar_dx + ddx, oy + spar_span_sc),
                     dxfattribs={"layer": "SPAR"})

    # Rear spar: 1.5mm CF rod at X=69.0, ±210mm
    rear_span_sc = REAR_SPAR_SPAN * sc
    msp.add_line((rear_dx, oy - rear_span_sc), (rear_dx, oy + rear_span_sc),
                 dxfattribs={"layer": "SPAR"})

    # Hinge wire: 0.5mm at X=74.75, ±203mm — STRAIGHT LINE (NOT curved!)
    hinge_span_sc = 203.0 * sc
    msp.add_line((hinge_dx, oy - hinge_span_sc), (hinge_dx, oy + hinge_span_sc),
                 dxfattribs={"layer": "HIDDEN"})

    # Stiffeners: 1mm at X=92.0, y=4..150mm each side (NOT through fin)
    stiff_root_dy = ROOT_GAP_AT_HINGE / 2 * sc
    stiff_tip_dy = STIFFENER_SPAN * sc
    for sign in [1, -1]:
        msp.add_line((stiff_dx, oy + sign * stiff_root_dy),
                     (stiff_dx, oy + sign * stiff_tip_dy),
                     dxfattribs={"layer": "SPAR"})

    # ── Section cut indicators ──
    cut_ext = 5 * sc
    # A-A at root
    for ext_x, lbl_off in [(le_root_x - cut_ext, -3), (te_root_x + cut_ext, 1.5)]:
        msp.add_line((ext_x, oy - 2), (ext_x, oy + 2),
                     dxfattribs={"layer": "SECTION"})
        msp.add_text("A", height=2.0, dxfattribs={"layer": "SECTION"}).set_placement(
            (ext_x + lbl_off, oy - 1))

    # ── Structure labels (above the top spar end, spaced to avoid overlap) ──
    label_y = oy + spar_span_sc + 5
    msp.add_text("MAIN SPAR\n3mm CF tube", height=1.1,
                 dxfattribs={"layer": "TEXT"}).set_placement((spar_dx - 6, label_y))
    msp.add_text("REAR SPAR\n1.5mm CF rod", height=1.1,
                 dxfattribs={"layer": "TEXT"}).set_placement((rear_dx - 5, label_y + 8))
    msp.add_text("HINGE WIRE\n0.5mm steel", height=1.1,
                 dxfattribs={"layer": "TEXT"}).set_placement((hinge_dx + 2, label_y + 8))
    msp.add_text("STIFFENER\n1mm CF rod", height=1.1,
                 dxfattribs={"layer": "TEXT"}).set_placement((stiff_dx + 2, label_y))

    # LE / TE labels
    tip_lbl_y = oy + HALF_SPAN * 0.85 * sc
    msp.add_text("LE", height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(
        (le_root_x - 5, tip_lbl_y))
    msp.add_text("TE", height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(
        (te_root_x + 2, tip_lbl_y))

    # ── DIMENSIONS ──
    dim_style = "AEROFORGE"
    tip_top = oy + HALF_SPAN * sc
    tip_bot = oy - HALF_SPAN * sc

    # Full span 430mm
    dim = msp.add_linear_dim(
        base=(le_root_x - 10, oy),
        p1=(le_root_x, tip_bot), p2=(le_root_x, tip_top),
        angle=90, dimstyle=dim_style, override={"dimlfac": 1.0 / sc})
    dim.render()

    # Half span 215mm
    dim = msp.add_linear_dim(
        base=(te_root_x + 8, oy),
        p1=(te_root_x, oy), p2=(te_root_x, tip_top),
        angle=90, dimstyle=dim_style, override={"dimlfac": 1.0 / sc})
    dim.render()

    # Root chord 111.55mm (at 97%)
    dim = msp.add_linear_dim(
        base=(le_root_x, tip_top + 7),
        p1=(le_root_x, oy), p2=(te_root_x, oy),
        dimstyle=dim_style, override={"dimlfac": 1.0 / sc})
    dim.render()

    # Hinge position 74.75mm from LE
    dim = msp.add_linear_dim(
        base=(le_root_x, tip_top + 13),
        p1=(le_root_x, oy), p2=(hinge_dx, oy),
        dimstyle=dim_style, override={"dimlfac": 1.0 / sc})
    dim.render()

    # Main spar position 35.0mm from LE
    dim = msp.add_linear_dim(
        base=(le_root_x, tip_top + 19),
        p1=(le_root_x, oy), p2=(spar_dx, oy),
        dimstyle=dim_style, override={"dimlfac": 1.0 / sc})
    dim.render()

    # Spar span 372mm
    dim = msp.add_linear_dim(
        base=(spar_dx - 8, oy),
        p1=(spar_dx, oy - spar_span_sc), p2=(spar_dx, oy + spar_span_sc),
        angle=90, dimstyle=dim_style, override={"dimlfac": 1.0 / sc})
    dim.render()

    # Root gap 8mm
    dim = msp.add_linear_dim(
        base=(hinge_dx - 6, oy),
        p1=(hinge_dx, oy - gap_half_dy), p2=(hinge_dx, oy + gap_half_dy),
        angle=90, dimstyle=dim_style, override={"dimlfac": 1.0 / sc})
    dim.render()

    # View title
    msp.add_text("VIEW 1: PLANFORM (TOP VIEW)", height=3.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox - 10, tip_top + 24))
    msp.add_text(f"Scale 1:{1/sc:.0f} | Span {SPAN:.0f}mm | Root chord {ROOT_CHORD:.0f}mm",
                 height=1.8, dxfattribs={"layer": "TEXT"}).set_placement(
        (ox - 10, tip_top + 20))


if __name__ == "__main__":
    main()
