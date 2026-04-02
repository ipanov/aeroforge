"""
2D Technical Drawing: HStab_Left Component
============================================
FROM DESIGN CONSENSUS v5 (aero+structural agent team, R3):

  Configuration: Fixed stabilizer LEFT half-shell
  Planform: Superellipse n=2.3, 215mm half-span
  Root chord: 115mm (HT-13, 6.5% t/c)
  Tip chord: ~50mm at 95% span (HT-12, 5.1%)
  Main spar: 3mm CF tube at X=35.0mm (30.4% root chord)
  Rear spar: 1.5mm CF rod at X=69.0mm (60.0% root chord)
  Wall: 0.45mm LW-PLA, vase mode
  Hinge strip: PETG at X=74.75mm (65% root chord)
  Root gap: 4mm from centerline (half of 8mm total)

Views:
  1. PLANFORM (top view) — outer shell outline + spar tunnels + hinge strip zone
  2. ROOT CROSS-SECTION — HT-13 airfoil with internal structure
  3. TIP CROSS-SECTION — at y=186mm (spar termination), blended airfoil
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

# ──────────────────────────────────────────────────────────────────────────────
# PARAMETERS FROM DESIGN CONSENSUS v5
# ──────────────────────────────────────────────────────────────────────────────
HALF_SPAN = 215.0            # mm per half
ROOT_CHORD = 115.0           # mm
SUPERELLIPSE_N = 2.3
HINGE_FRAC = 0.65            # hinge line at 65% root chord
HINGE_X = 74.75              # mm from root LE (fixed)
TE_FRAC = 0.97               # TE truncation at 97% chord

# Spar positions (FIXED X from root LE, perpendicular to fuselage CL)
MAIN_SPAR_X = 35.0           # mm (30.4% root chord)
MAIN_SPAR_OD = 3.0           # mm (CF tube OD)
MAIN_SPAR_ID = 2.0           # mm (CF tube ID)
MAIN_SPAR_TUNNEL = 3.1       # mm (bore in shell)
MAIN_SPAR_SPAN = 186.0       # mm per half (terminates here)

REAR_SPAR_X = 69.0           # mm (60.0% root chord)
REAR_SPAR_OD = 1.5           # mm (CF rod OD)
REAR_SPAR_TUNNEL = 1.6       # mm (bore in shell)
REAR_SPAR_SPAN = 215.0       # mm per half (full span)

# Wall thickness
WALL_STAB = 0.45             # mm (LW-PLA vase mode)

# Root gap
ROOT_GAP = 4.0               # mm from centerline (half of 8mm total)
VSTAB_FIN_HALF = 3.5         # mm (half of 7mm fin width)

# Airfoil
TC_ROOT = 0.065              # HT-13: 6.5%
TC_TIP = 0.051               # HT-12: 5.1%

# PETG hinge strip zone
HINGE_STRIP_HEIGHT = 1.2     # mm (knuckle OD)
HINGE_STRIP_WIDTH = 2.0      # mm (chordwise)
HINGE_STRIP_END = 200.0      # mm (last knuckle at y=200)

# 45%-chord alignment (straight line)
ALIGN_FRAC = 0.45
ALIGN_X = ALIGN_FRAC * ROOT_CHORD  # 51.75mm


# ──────────────────────────────────────────────────────────────────────────────
# GEOMETRY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def chord_at(y: float) -> float:
    """Superellipse chord at span station y (0 to 215mm)."""
    eta = abs(y) / HALF_SPAN
    if eta >= 1.0:
        return 0.0
    return ROOT_CHORD * (1.0 - eta ** SUPERELLIPSE_N) ** (1.0 / SUPERELLIPSE_N)


def le_x_at(y: float) -> float:
    """Leading edge X position at span station y.
    The 45%-chord line is straight, so LE moves forward as chord shrinks."""
    c = chord_at(y)
    return ALIGN_X - ALIGN_FRAC * c


def te_x_at(y: float) -> float:
    """Trailing edge X position (97% chord) at span station y."""
    c = chord_at(y)
    return ALIGN_X + (1.0 - ALIGN_FRAC) * TE_FRAC * c  # approx


def tc_blend_at(y: float) -> float:
    """Linearly blended t/c from HT-13 (root) to HT-12 (tip)."""
    eta = abs(y) / HALF_SPAN
    return TC_ROOT * (1.0 - eta) + TC_TIP * eta


def ht_thickness(xc: float, tc: float, chord: float) -> float:
    """Half-thickness at chord fraction xc for a symmetric airfoil with given t/c.
    Uses NACA 4-digit thickness distribution."""
    if xc <= 0:
        return 0.0
    if xc > 1.0:
        xc = 1.0
    yt = 5 * tc * (
        0.2969 * xc**0.5
        - 0.1260 * xc
        - 0.3516 * xc**2
        + 0.2843 * xc**3
        - 0.1015 * xc**4
    ) * chord
    return max(yt, 0.0)


# ──────────────────────────────────────────────────────────────────────────────
# DRAWING
# ──────────────────────────────────────────────────────────────────────────────

def draw(msp, ox: float, oy: float, sc: float = 0.7):
    """Draw the HStab_Left component views.

    Layout (A3 landscape):
    - Upper section: PLANFORM (top view), root at bottom, tip at top
    - Lower-left: ROOT CROSS-SECTION (Section A-A)
    - Lower-right: TIP CROSS-SECTION (Section B-B at y=186mm)
    """

    # ══════════════════════════════════════════════════════════════════════
    # VIEW 1: PLANFORM (Top View)
    # ══════════════════════════════════════════════════════════════════════
    # Convention: X increases right (chordwise, LE left, TE right)
    # Y increases up (spanwise, root at bottom, tip at top)
    # FWD is LEFT

    stations = [HALF_SPAN * i / 60 for i in range(61)]

    le_pts = []
    hinge_pts = []
    te_pts = []

    for y in stations:
        c = chord_at(y)
        if c <= 0:
            break
        le = le_x_at(y)
        hinge = HINGE_X  # fixed X
        te = te_x_at(y)

        draw_y = oy + y * sc
        le_pts.append((ox + le * sc, draw_y))
        hinge_pts.append((ox + hinge * sc, draw_y))
        te_pts.append((ox + te * sc, draw_y))

    # ── Outer shell (LE to hinge line) ──
    for i in range(len(le_pts) - 1):
        msp.add_line(le_pts[i], le_pts[i + 1], dxfattribs={"layer": "STAB"})
    # Root line (LE to hinge)
    if le_pts and hinge_pts:
        msp.add_line(le_pts[0], hinge_pts[0], dxfattribs={"layer": "STAB"})
    # Tip closure (last LE to last hinge point at spar end)
    # Find the station where main spar ends (y=186)
    tip_y = oy + MAIN_SPAR_SPAN * sc

    # ── Hinge strip zone (dashed, from root to y=200mm) ──
    hinge_end_y = oy + min(HINGE_STRIP_END, HALF_SPAN) * sc
    hinge_root_x = ox + HINGE_X * sc
    for i in range(len(hinge_pts) - 1):
        if hinge_pts[i][1] > hinge_end_y:
            break
        msp.add_line(hinge_pts[i], hinge_pts[i + 1],
                     dxfattribs={"layer": "HINGE"})

    # ── Main spar: STRAIGHT vertical line at constant X=35.0mm ──
    spar_x = ox + MAIN_SPAR_X * sc
    spar_y0 = oy  # root
    spar_y1 = oy + MAIN_SPAR_SPAN * sc  # terminates at y=186mm
    msp.add_line((spar_x, spar_y0), (spar_x, spar_y1),
                 dxfattribs={"layer": "SPAR"})
    # Show tube width
    hw = MAIN_SPAR_OD / 2 * sc
    msp.add_line((spar_x - hw, spar_y0), (spar_x - hw, spar_y1),
                 dxfattribs={"layer": "SPAR"})
    msp.add_line((spar_x + hw, spar_y0), (spar_x + hw, spar_y1),
                 dxfattribs={"layer": "SPAR"})

    # ── Rear spar: STRAIGHT vertical line at X=69.0mm ──
    rspar_x = ox + REAR_SPAR_X * sc
    rspar_y1 = oy + REAR_SPAR_SPAN * sc
    msp.add_line((rspar_x, spar_y0), (rspar_x, rspar_y1),
                 dxfattribs={"layer": "SPAR"})
    rhw = REAR_SPAR_OD / 2 * sc
    msp.add_line((rspar_x - rhw, spar_y0), (rspar_x - rhw, rspar_y1),
                 dxfattribs={"layer": "SPAR"})
    msp.add_line((rspar_x + rhw, spar_y0), (rspar_x + rhw, rspar_y1),
                 dxfattribs={"layer": "SPAR"})

    # ── Root face (gap line) ──
    # Root is at y=ROOT_GAP (4mm from centerline)
    root_y = oy + ROOT_GAP * sc
    c_root = chord_at(0)
    le_root_x = ox + le_x_at(0) * sc
    hinge_root_x_sc = ox + HINGE_X * sc
    msp.add_line((le_root_x, root_y), (hinge_root_x_sc, root_y),
                 dxfattribs={"layer": "STAB"})

    # ── VStab fin outline (dashed, at y=0 to y=ROOT_GAP) ──
    fin_y_top = oy + ROOT_GAP * sc
    fin_y_bot = oy - 1 * sc  # slightly below center
    fin_le = ox + (ALIGN_X - 10) * sc
    fin_te = ox + (HINGE_X + 5) * sc
    for dy in [fin_y_top, fin_y_bot]:
        msp.add_line((fin_le, dy), (fin_te, dy),
                     dxfattribs={"layer": "FIN"})
    msp.add_line((fin_le, fin_y_bot), (fin_le, fin_y_top),
                 dxfattribs={"layer": "FIN"})
    msp.add_line((fin_te, fin_y_bot), (fin_te, fin_y_top),
                 dxfattribs={"layer": "FIN"})
    msp.add_text("VSTAB FIN", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (fin_le + 2, oy - 0.5 * sc))

    # ── Tip cap zone (semi-elliptical, y=210-214mm) ──
    cap_start_y = oy + 210 * sc
    cap_end_y = oy + 214 * sc
    # Draw a small arc/ellipse hint at the tip
    c_210 = chord_at(210)
    if c_210 > 0:
        cap_le_x = ox + le_x_at(210) * sc
        cap_te_x = ox + te_x_at(210) * sc
        cap_mid_x = (cap_le_x + cap_te_x) / 2
        msp.add_line((cap_le_x, cap_start_y), (cap_te_x, cap_start_y),
                     dxfattribs={"layer": "STAB"})
        # Small ellipse arc hint for tip closure
        n_cap = 8
        for i in range(n_cap):
            frac1 = i / n_cap
            frac2 = (i + 1) / n_cap
            angle1 = math.pi * frac1
            angle2 = math.pi * frac2
            x1 = cap_mid_x + (cap_te_x - cap_mid_x) * math.cos(angle1)
            y1 = cap_start_y + (cap_end_y - cap_start_y) * math.sin(angle1)
            x2 = cap_mid_x + (cap_te_x - cap_mid_x) * math.cos(angle2)
            y2 = cap_start_y + (cap_end_y - cap_start_y) * math.sin(angle2)
            msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "STAB"})

    # ── Labels ──
    msp.add_text("HStab LEFT", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + 20 * sc, oy + HALF_SPAN * 0.5 * sc))
    msp.add_text("FWD", height=2.5,
                 dxfattribs={"layer": "ORIENT"}).set_placement(
        (ox - 8 * sc, oy + HALF_SPAN * sc + 5))
    msp.add_text("LE", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox - 4 * sc, oy + 170 * sc))
    msp.add_text("TE", height=1.8,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + te_x_at(100) * sc + 2, oy + 170 * sc))
    msp.add_text("HINGE LINE", height=1.1,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + HINGE_X * sc + 2, oy + 180 * sc))

    # Spar labels
    label_y = oy + (MAIN_SPAR_SPAN + 5) * sc
    msp.add_text("MAIN SPAR", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (spar_x - 5, label_y))
    msp.add_text(f"X={MAIN_SPAR_X}mm (30.4%)", height=1.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (spar_x - 5, label_y - 2))
    msp.add_text("REAR SPAR", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (rspar_x - 5, label_y))
    msp.add_text(f"X={REAR_SPAR_X}mm (60%)", height=1.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (rspar_x - 5, label_y - 2))

    # ── Section cut indicators ──
    # A-A at root
    cut_x1 = le_root_x - 3 * sc
    cut_x2 = ox + te_x_at(0) * sc + 3 * sc
    for cx, lo in [(cut_x1, -2), (cut_x2, 1.5)]:
        msp.add_line((cx, root_y - 2), (cx, root_y + 2),
                     dxfattribs={"layer": "SPAR"})
        msp.add_text("A", height=2.0,
                     dxfattribs={"layer": "SPAR"}).set_placement(
            (cx + lo, root_y - 1))

    # B-B at tip (y=186mm)
    bb_y = oy + 186 * sc
    c_186 = chord_at(186)
    if c_186 > 0:
        bb_le = ox + le_x_at(186) * sc
        bb_te = ox + te_x_at(186) * sc
        for by in [bb_y - 2, bb_y + 2]:
            msp.add_line((bb_le - 3 * sc, by), (bb_te + 3 * sc, by),
                         dxfattribs={"layer": "SPAR"})
        msp.add_text("B", height=2.0,
                     dxfattribs={"layer": "SPAR"}).set_placement(
            (bb_te + 4 * sc, bb_y - 1))

    # ── DIMENSIONS ──
    dim_style = "AEROFORGE"

    # Half span (215mm)
    dim = msp.add_linear_dim(
        base=(le_root_x - 10, oy),
        p1=(le_root_x, oy),
        p2=(le_root_x, oy + HALF_SPAN * sc),
        angle=90, dimstyle=dim_style,
        override={"dimlfac": 1.0 / sc})
    dim.render()

    # Root chord
    dim = msp.add_linear_dim(
        base=(le_root_x, oy + HALF_SPAN * sc + 8),
        p1=(le_root_x, oy),
        p2=(ox + te_x_at(0) * sc, oy),
        dimstyle=dim_style,
        override={"dimlfac": 1.0 / sc})
    dim.render()

    # Main spar from LE
    dim = msp.add_linear_dim(
        base=(le_root_x, oy + HALF_SPAN * sc + 14),
        p1=(le_root_x, oy),
        p2=(spar_x, oy),
        dimstyle=dim_style,
        override={"dimlfac": 1.0 / sc})
    dim.render()

    # Main spar span extent
    dim = msp.add_linear_dim(
        base=(spar_x - 8, oy),
        p1=(spar_x, oy),
        p2=(spar_x, spar_y1),
        angle=90, dimstyle=dim_style,
        override={"dimlfac": 1.0 / sc})
    dim.render()

    # Root gap
    dim = msp.add_linear_dim(
        base=(ox + HINGE_X * sc - 5, oy),
        p1=(ox + HINGE_X * sc, oy),
        p2=(ox + HINGE_X * sc, root_y),
        angle=90, dimstyle=dim_style,
        override={"dimlfac": 1.0 / sc})
    dim.render()

    # Wall thickness note
    msp.add_text(f"Wall: {WALL_STAB}mm LW-PLA (vase mode)", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox + 30 * sc, oy - 6))

    # View title
    msp.add_text("VIEW 1: PLANFORM (TOP VIEW)", height=2.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox - 5, oy + HALF_SPAN * sc + 20))
    msp.add_text(f"Scale ~1:{1/sc:.1f} | Left half only", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (ox - 5, oy + HALF_SPAN * sc + 17))

    # ══════════════════════════════════════════════════════════════════════
    # VIEW 2: ROOT CROSS-SECTION (Section A-A at y=0)
    # ══════════════════════════════════════════════════════════════════════
    sec_ox = ox - 15
    sec_oy = oy - 55
    chord = ROOT_CHORD
    sec_sc = 1.0  # 1:1 scale for section

    # Draw stab portion airfoil (LE to hinge at 65% chord)
    n_pts = 60
    for i in range(n_pts):
        xc1 = HINGE_FRAC * i / n_pts
        xc2 = HINGE_FRAC * (i + 1) / n_pts
        x1 = sec_ox + xc1 * chord * sec_sc
        x2 = sec_ox + xc2 * chord * sec_sc
        yt1 = ht_thickness(xc1, TC_ROOT, chord) * sec_sc
        yt2 = ht_thickness(xc2, TC_ROOT, chord) * sec_sc
        msp.add_line((x1, sec_oy + yt1), (x2, sec_oy + yt2),
                     dxfattribs={"layer": "STAB"})
        msp.add_line((x1, sec_oy - yt1), (x2, sec_oy - yt2),
                     dxfattribs={"layer": "STAB"})

    # LE closure
    yt_le = ht_thickness(0.005, TC_ROOT, chord) * sec_sc
    msp.add_line((sec_ox, sec_oy + yt_le), (sec_ox, sec_oy - yt_le),
                 dxfattribs={"layer": "STAB"})

    # Hinge face (vertical at 65% chord)
    hinge_sec_x = sec_ox + HINGE_FRAC * chord * sec_sc
    yt_hinge = ht_thickness(HINGE_FRAC, TC_ROOT, chord) * sec_sc
    msp.add_line((hinge_sec_x, sec_oy + yt_hinge), (hinge_sec_x, sec_oy - yt_hinge),
                 dxfattribs={"layer": "HINGE"})

    # Main spar tunnel
    spar_sec_x = sec_ox + (MAIN_SPAR_X / chord) * chord * sec_sc
    msp.add_circle((spar_sec_x, sec_oy), MAIN_SPAR_TUNNEL / 2 * sec_sc,
                   dxfattribs={"layer": "SPAR"})
    msp.add_circle((spar_sec_x, sec_oy), MAIN_SPAR_OD / 2 * sec_sc,
                   dxfattribs={"layer": "SPAR"})

    # Rear spar tunnel
    rspar_sec_x = sec_ox + (REAR_SPAR_X / chord) * chord * sec_sc
    msp.add_circle((rspar_sec_x, sec_oy), REAR_SPAR_TUNNEL / 2 * sec_sc,
                   dxfattribs={"layer": "SPAR"})
    msp.add_circle((rspar_sec_x, sec_oy), REAR_SPAR_OD / 2 * sec_sc,
                   dxfattribs={"layer": "SPAR"})

    # Wall thickness dots
    for i in range(2, n_pts, 5):
        xc = HINGE_FRAC * i / n_pts
        if xc < 0.05:
            continue
        x_draw = sec_ox + xc * chord * sec_sc
        yt_out = ht_thickness(xc, TC_ROOT, chord) * sec_sc
        if yt_out > WALL_STAB * 3:
            for sgn in [1, -1]:
                msp.add_circle((x_draw, sec_oy + sgn * (yt_out - WALL_STAB * sec_sc)),
                               0.12, dxfattribs={"layer": "WEIGHT"})

    # Section labels
    msp.add_text("MAIN SPAR", height=1.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (spar_sec_x - 4, sec_oy - yt_hinge - 3))
    msp.add_text("REAR SPAR", height=1.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (rspar_sec_x - 4, sec_oy - yt_hinge - 3))
    msp.add_text("HINGE\nFACE", height=0.9,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (hinge_sec_x + 1, sec_oy + yt_hinge + 1))
    msp.add_text("LE", height=1.5,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (sec_ox - 4, sec_oy + 1))
    msp.add_text(f"HT-13 ({TC_ROOT*100:.1f}% t/c)", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (sec_ox + 0.4 * chord, sec_oy - yt_hinge - 5))
    msp.add_text(f"Wall: {WALL_STAB}mm", height=1.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (sec_ox + 0.5 * chord, sec_oy + yt_hinge + 2))

    # Section view title
    msp.add_text("SECTION A-A (ROOT)", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (sec_ox - 5, sec_oy - yt_hinge - 12))
    msp.add_text("Scale 1:1", height=1.2,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (sec_ox - 5, sec_oy - yt_hinge - 15))

    # ══════════════════════════════════════════════════════════════════════
    # VIEW 3: TIP CROSS-SECTION (Section B-B at y=186mm)
    # ══════════════════════════════════════════════════════════════════════
    tip_sec_ox = ox + 55
    tip_sec_oy = sec_oy
    c_tip = chord_at(186)
    tc_tip = tc_blend_at(186)  # blended t/c at this station

    # Stab portion (LE to hinge)
    for i in range(n_pts):
        xc1 = HINGE_FRAC * i / n_pts
        xc2 = HINGE_FRAC * (i + 1) / n_pts
        x1 = tip_sec_ox + xc1 * c_tip * sec_sc
        x2 = tip_sec_ox + xc2 * c_tip * sec_sc
        yt1 = ht_thickness(xc1, tc_tip, c_tip) * sec_sc
        yt2 = ht_thickness(xc2, tc_tip, c_tip) * sec_sc
        msp.add_line((x1, tip_sec_oy + yt1), (x2, tip_sec_oy + yt2),
                     dxfattribs={"layer": "STAB"})
        msp.add_line((x1, tip_sec_oy - yt1), (x2, tip_sec_oy - yt2),
                     dxfattribs={"layer": "STAB"})

    # LE closure
    yt_le_tip = ht_thickness(0.005, tc_tip, c_tip) * sec_sc
    msp.add_line((tip_sec_ox, tip_sec_oy + yt_le_tip),
                 (tip_sec_ox, tip_sec_oy - yt_le_tip),
                 dxfattribs={"layer": "STAB"})

    # Hinge face
    hinge_tip_x = tip_sec_ox + HINGE_FRAC * c_tip * sec_sc
    yt_hinge_tip = ht_thickness(HINGE_FRAC, tc_tip, c_tip) * sec_sc
    msp.add_line((hinge_tip_x, tip_sec_oy + yt_hinge_tip),
                 (hinge_tip_x, tip_sec_oy - yt_hinge_tip),
                 dxfattribs={"layer": "HINGE"})

    # Main spar tunnel (at X=35mm from root LE = local chord fraction changes)
    # At y=186: local spar chord fraction = MAIN_SPAR_X / c_tip ... no.
    # Spar is at fixed X. LE at y=186 is at le_x_at(186).
    # So spar local position = MAIN_SPAR_X - le_x_at(186) relative to section LE
    spar_local_x = MAIN_SPAR_X - le_x_at(186)
    spar_tip_x = tip_sec_ox + spar_local_x / c_tip * c_tip * sec_sc  # = tip_sec_ox + spar_local_x
    msp.add_circle((tip_sec_ox + spar_local_x * sec_sc, tip_sec_oy),
                   MAIN_SPAR_TUNNEL / 2 * sec_sc,
                   dxfattribs={"layer": "SPAR"})
    msp.add_circle((tip_sec_ox + spar_local_x * sec_sc, tip_sec_oy),
                   MAIN_SPAR_OD / 2 * sec_sc,
                   dxfattribs={"layer": "SPAR"})

    # Rear spar tunnel
    rspar_local_x = REAR_SPAR_X - le_x_at(186)
    msp.add_circle((tip_sec_ox + rspar_local_x * sec_sc, tip_sec_oy),
                   REAR_SPAR_TUNNEL / 2 * sec_sc,
                   dxfattribs={"layer": "SPAR"})

    # Section view title
    msp.add_text("SECTION B-B (y=186mm)", height=2.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (tip_sec_ox - 5, tip_sec_oy - yt_hinge_tip - 12))
    msp.add_text(f"Blended HT ~{tc_tip*100:.1f}% t/c | Chord {c_tip:.1f}mm",
                 height=1.0,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (tip_sec_ox - 5, tip_sec_oy - yt_hinge_tip - 15))
    msp.add_text("SPAR ENDS HERE\n(29mm tip unsupported)",
                 height=0.9,
                 dxfattribs={"layer": "TEXT"}).set_placement(
        (tip_sec_ox + 10, tip_sec_oy + yt_hinge_tip + 3))


def main():
    doc = setup_drawing(
        title="HStab_Left",
        drawing_number="AF-EMP-CMP-001",
        subtitle="Horizontal Stabilizer Left Shell — Superellipse n=2.3, HT-13/HT-12 blend",
        material="LW-PLA 0.45mm vase mode",
        scale="~1:1.4 (planform), 1:1 (sections)",
        mass="8.50g",
        status="FOR APPROVAL",
        revision="A",
        sheet_size="A3",
        orientation_labels={"fwd": "FWD", "inbd": "INBD"},
    )

    msp = doc.modelspace()
    draw(msp, ox=60, oy=170, sc=0.7)

    out_path = "cad/components/empennage/HStab_Left/HStab_Left_drawing"
    dxf_out, png_out = save_dxf_and_png(doc, out_path)

    print(f"\nHSTAB LEFT DRAWING — v5 CONSENSUS")
    print(f"  Superellipse n=2.3 | {HALF_SPAN:.0f}mm half-span | {ROOT_CHORD:.0f}mm root chord")
    print(f"  Main spar X={MAIN_SPAR_X}mm ({MAIN_SPAR_X/ROOT_CHORD*100:.1f}%) | ±{MAIN_SPAR_SPAN:.0f}mm")
    print(f"  Rear spar X={REAR_SPAR_X}mm ({REAR_SPAR_X/ROOT_CHORD*100:.1f}%) | ±{REAR_SPAR_SPAN:.0f}mm")
    print(f"  Wall: {WALL_STAB}mm LW-PLA | Mass target: 8.50g")
    print(f"  DXF: {dxf_out}")
    print(f"  PNG: {png_out}")


if __name__ == "__main__":
    main()
