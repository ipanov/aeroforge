"""
HStab v5 Shared Geometry — Superellipse planform with C1-continuous tip cap.
=============================================================================
Used by all HStab drawing scripts.

The tip cap uses a cubic polynomial MATCHED to the superellipse slope at y=210mm,
ensuring C1 continuity (no kink at the transition). The cap closes to zero chord
at y=214mm with zero slope (smooth tip closure).

Cubic cap: c_cap(t) = 32.0 - 2.74t - 4.630t² + 0.829t³,  t = y - 210,  t ∈ [0, 4]
"""

import math
import os
import numpy as np
from numpy import interp as np_interp

# === v5 Consensus Parameters ===
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
N_EXP = 2.3
REF_FRAC = 0.45
REF_X = ROOT_CHORD * REF_FRAC   # 51.75mm

# v6 parameters (R4: single spar, forward hinge, concealed saddle)
X_MAIN_SPAR = 34.5   # 30.0% root chord — exact max-thickness point
X_HINGE = 60.0        # 52.2% root chord — concealed saddle hinge (was 74.75 in v5)

# v5 legacy (REMOVED in v6 — kept as comments for reference)
# X_REAR_SPAR = 69.0  # REMOVED: rear spar eliminated in v6
# X_STIFF = 92.0       # REMOVED: elevator stiffener eliminated in v6

D_MAIN = 3.1           # bore diameter for 3mm CF tube
D_HINGE = 0.6          # bore diameter for 0.5mm wire (PETG sleeve)

Y_MAIN_END = 189.0     # spar tube terminates (was 186 in v5)
Y_HINGE_END = 212.0    # hinge wire terminates (was 203 in v5)

T_ROOT = 0.065
T_TIP = 0.051
TE_TRUNC = 0.97

Y_CAP_START = 210.0
Y_CAP_END = 214.0
CAP_SPAN = Y_CAP_END - Y_CAP_START

FIN_HALF = 3.5    # VStab fin half-thickness (7mm total)
FIN_GAP = 0.5     # clearance each side

# Tip arc: polylines stop here, remaining tip closed with ellipse arc entity
Y_TIP_ARC_START = 210.0   # polylines STOP here; remaining 4mm closed with ellipse arc
                          # chord at y=210 is ~32mm — arc is 4mm × 16mm, clearly visible

# Horn parameters
Y_HORN_START = 195.0
Y_LAST_KNUCKLE = 200.0
POCKET_Y_CENTER = 200.0
POCKET_SPAN = 10.0
POCKET_CHORD = 6.5
POCKET_DEPTH = 1.5
POCKET_FWD_OF_HINGE = 8.0

# Tip cap: cubic polynomial computed at import time for exact C1 continuity.
_CAP_A = None
_CAP_B = None
_CAP_C = None
_CAP_D = None


def _superellipse_chord(y):
    """Raw superellipse chord (valid for y in [0, HALF_SPAN])."""
    if y >= HALF_SPAN or y < 0:
        return 0.0
    return ROOT_CHORD * (1.0 - (y / HALF_SPAN) ** N_EXP) ** (1.0 / N_EXP)


def _init_cap_coefficients():
    """Compute cubic cap coefficients for C1 continuity at y=Y_CAP_START."""
    global _CAP_A, _CAP_B, _CAP_C, _CAP_D
    # Exact chord value at cap start
    c0 = _superellipse_chord(Y_CAP_START)
    # Numerical derivative at cap start
    dy = 0.001
    c0_slope = (_superellipse_chord(Y_CAP_START) - _superellipse_chord(Y_CAP_START - dy)) / dy
    # Cubic: c(t) = A + B*t + C*t^2 + D*t^3
    # Constraints: c(0)=c0, c'(0)=c0_slope, c(4)=0, c'(4)=0
    _CAP_A = c0
    _CAP_B = c0_slope
    # From c(4)=0: A + 4B + 16C + 64D = 0
    # From c'(4)=0: B + 8C + 48D = 0  =>  C = (-B - 48D) / 8
    # Substituting: A + 4B + 16*(-B-48D)/8 + 64D = 0
    #   A + 4B - 2B - 96D + 64D = 0
    #   A + 2B - 32D = 0  =>  D = (A + 2B) / 32
    _CAP_D = (_CAP_A + 2 * _CAP_B) / 32
    _CAP_C = (-_CAP_B - 48 * _CAP_D) / 8


_init_cap_coefficients()


def chord_at(y):
    """Combined chord: superellipse for y<210, cubic cap for y=210→214, 0 beyond."""
    if y < 0:
        return chord_at(-y)
    if y <= Y_CAP_START:
        return _superellipse_chord(y)
    if y >= Y_CAP_END:
        return 0.0
    t = y - Y_CAP_START
    return max(0.0, _CAP_A + _CAP_B * t + _CAP_C * t**2 + _CAP_D * t**3)


def le_x(y):
    """Leading edge X position (consensus coords, from root LE)."""
    return REF_X - REF_FRAC * chord_at(y)


def te_x(y):
    """Trailing edge X position (truncated at 97% chord)."""
    return le_x(y) + chord_at(y) * TE_TRUNC


def t_ratio(y):
    """Thickness ratio (linear blend HT-13 → HT-12)."""
    return T_ROOT + (T_TIP - T_ROOT) * min(abs(y) / HALF_SPAN, 1.0)


def naca4_yt(xc, tr):
    """NACA 4-digit half-thickness at chord fraction xc with thickness ratio tr.
    DEPRECATED: Use airfoil_yt() for real HT-13/HT-12 sections."""
    if xc <= 0:
        return 0.0
    xc = min(xc, 1.0)
    return 5 * tr * (0.2969 * xc**0.5 - 0.1260 * xc - 0.3516 * xc**2
                     + 0.2843 * xc**3 - 0.1015 * xc**4)


# === Real Airfoil Data (HT-13, HT-12) ===

def _load_selig_dat(filename):
    """Load a Selig-format .dat airfoil and return (x_upper, y_upper, x_lower, y_lower)."""
    paths = [
        os.path.join(os.path.dirname(__file__), '..', 'src', 'cad', 'airfoils', filename),
        os.path.join(os.path.dirname(__file__), filename),
    ]
    dat_path = None
    for p in paths:
        if os.path.exists(p):
            dat_path = p
            break
    if dat_path is None:
        raise FileNotFoundError(f"Airfoil data not found: {filename}")

    with open(dat_path, 'r') as f:
        lines = f.readlines()

    # Skip header line
    coords = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) == 2:
            coords.append((float(parts[0]), float(parts[1])))

    # Find the split point (minimum x = LE)
    x_vals = [c[0] for c in coords]
    le_idx = x_vals.index(min(x_vals))

    # Upper surface: from TE to LE (indices 0..le_idx), reverse to go LE→TE
    upper = list(reversed(coords[:le_idx + 1]))
    # Lower surface: from LE to TE (indices le_idx..end)
    lower = coords[le_idx:]

    x_upper = [p[0] for p in upper]
    y_upper = [p[1] for p in upper]
    x_lower = [p[0] for p in lower]
    y_lower = [p[1] for p in lower]

    return x_upper, y_upper, x_lower, y_lower


# Pre-load airfoil data at import time
try:
    _HT13_XU, _HT13_YU, _HT13_XL, _HT13_YL = _load_selig_dat('ht13.dat')
    _HT13_LOADED = True
except FileNotFoundError:
    _HT13_LOADED = False

try:
    _HT12_XU, _HT12_YU, _HT12_XL, _HT12_YL = _load_selig_dat('ht12.dat')
    _HT12_LOADED = True
except FileNotFoundError:
    _HT12_LOADED = False


def airfoil_yt_upper(xc, y_span):
    """Real HT-13/HT-12 blended upper surface y/c at chord fraction xc and span y."""
    if xc <= 0 or xc > 1.0:
        return 0.0
    blend = min(abs(y_span) / HALF_SPAN, 1.0)  # 0=root(HT13), 1=tip(HT12)

    if _HT13_LOADED:
        y13 = float(np_interp(xc, _HT13_XU, _HT13_YU))
    else:
        y13 = naca4_yt(xc, T_ROOT)

    if _HT12_LOADED:
        y12 = float(np_interp(xc, _HT12_XU, _HT12_YU))
    else:
        y12 = naca4_yt(xc, T_TIP)

    return y13 * (1 - blend) + y12 * blend


def airfoil_yt_lower(xc, y_span):
    """Real HT-13/HT-12 blended lower surface y/c at chord fraction xc and span y."""
    if xc <= 0 or xc > 1.0:
        return 0.0
    blend = min(abs(y_span) / HALF_SPAN, 1.0)

    if _HT13_LOADED:
        y13 = float(np_interp(xc, _HT13_XL, _HT13_YL))
    else:
        y13 = -naca4_yt(xc, T_ROOT)

    if _HT12_LOADED:
        y12 = float(np_interp(xc, _HT12_XL, _HT12_YL))
    else:
        y12 = -naca4_yt(xc, T_TIP)

    return y13 * (1 - blend) + y12 * blend


def airfoil_section_points(y_span, x_start_frac=0.0, x_end_frac=1.0, n_pts=80):
    """Generate upper and lower surface points for a section at span station y.

    Returns (upper_pts, lower_pts) as lists of (x_mm, y_mm) in local coords.
    x_start_frac, x_end_frac: chord fraction range (e.g., 0 to 0.52 for stab only).
    Uses cosine spacing for smooth LE.
    """
    c = chord_at(abs(y_span))
    if c < 0.5:
        return [], []

    lx = le_x(abs(y_span))

    # Cosine spacing for smooth LE
    fracs = []
    for i in range(n_pts + 1):
        t = i / n_pts
        # Cosine spacing concentrates points at start (LE)
        frac = x_start_frac + (x_end_frac - x_start_frac) * (1 - math.cos(math.pi / 2 * t))
        fracs.append(min(frac, x_end_frac))

    upper_pts = []
    lower_pts = []
    for frac in fracs:
        x_mm = frac * c  # distance from LE in mm
        yu = airfoil_yt_upper(frac, y_span) * c
        yl = airfoil_yt_lower(frac, y_span) * c
        upper_pts.append((x_mm, yu))
        lower_pts.append((x_mm, yl))

    return upper_pts, lower_pts


def elev_chord_at(y):
    """Elevator chord (from hinge to TE truncated). 0 if hinge exits airfoil."""
    te = te_x(y)
    if X_HINGE >= te:
        return 0.0
    return te - X_HINGE


def horn_fwd_offset(y):
    """Horn forward extension (mm ahead of hinge line) at span y.
    Parabolic y=195→205 (0→15mm), then blends to full LE at y=210."""
    if y < Y_HORN_START:
        return 0.0
    if y <= 205.0:
        t = (y - Y_HORN_START) / (205.0 - Y_HORN_START)
        return 15.0 * t * t
    if y <= Y_CAP_START:
        t = (y - 205.0) / (Y_CAP_START - 205.0)
        fwd_205 = 15.0
        fwd_210 = X_HINGE - le_x(Y_CAP_START)
        return fwd_205 + (fwd_210 - fwd_205) * t
    if y <= Y_CAP_END:
        # In cap zone, horn IS the full LE
        return X_HINGE - le_x(y)
    return 0.0


def planform_points(n_pts=150, y_stop=None):
    """Generate LE and TE polyline points for the planform.

    The curves stop at y_stop (default: Y_TIP_ARC_START = 213mm) so the tip
    can be closed with a proper ellipse arc entity instead of line segments.

    Returns (le_pts, te_pts) as lists of (consensus_x, consensus_y) tuples.
    """
    if y_stop is None:
        y_stop = Y_TIP_ARC_START
    le_pts = []
    te_pts = []
    # Main portion: y=0 to min(Y_CAP_START, y_stop)
    y_main_end = min(Y_CAP_START, y_stop)
    n_main = int(n_pts * 0.75)
    for i in range(n_main + 1):
        y = y_main_end * i / n_main
        le_pts.append((le_x(y), y))
        te_pts.append((te_x(y), y))
    # Cap portion: Y_CAP_START to y_stop (if y_stop > Y_CAP_START)
    if y_stop > Y_CAP_START:
        n_cap = n_pts - n_main
        for i in range(1, n_cap + 1):
            y = Y_CAP_START + (y_stop - Y_CAP_START) * i / n_cap
            le_pts.append((le_x(y), y))
            te_pts.append((te_x(y), y))
    return le_pts, te_pts


def tip_arc_points(n_pts=80):
    """Generate polyline points for TANGENT-MATCHED tip closure (cubic Bezier).

    The old semi-elliptical arc had zero slope at endpoints, creating visible
    kinks where the LE/TE curves meet the arc. This version uses a cubic Bezier
    that matches the slope of both LE and TE curves at y=Y_TIP_ARC_START,
    ensuring C1 continuity (no visible kink).

    Returns list of (consensus_x, consensus_y) points from LE → tip → TE.
    """
    y0 = Y_TIP_ARC_START
    lx0 = le_x(y0)    # LE X at y=210 ≈ 37.36
    tx0 = te_x(y0)    # TE X at y=210 ≈ 68.38

    # Compute tangent slopes at y=210 (numerical derivative)
    dy = 0.01
    dle_dx_dy = (le_x(y0 + dy) - le_x(y0 - dy)) / (2 * dy)   # dLE_x/dy ≈ +1.23
    dte_dx_dy = (te_x(y0 + dy) - te_x(y0 - dy)) / (2 * dy)   # dTE_x/dy ≈ -1.42

    # Cubic Bezier: B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
    # P0 = LE endpoint, P3 = TE endpoint
    # B'(0) = 3(P1-P0) must match LE tangent direction
    # B'(1) = 3(P3-P2) must match TE tangent direction (reversed, arriving)
    #
    # LE tangent direction: (dle_dx_dy, 1) — curve goes outward
    # TE arrival direction: the curve arrives at TE going inward,
    #   so B'(1) ∝ (-dte_dx_dy, -1) = (1.42, -1)
    #   → P3 - P2 ∝ (1.42, -1) → P2 = P3 - k₂*(1.42, -1)

    # Choose k to make curve reach y ≈ Y_CAP_END at midpoint
    # B_y(0.5) = 0.125*y0 + 0.375*(y0+k₁) + 0.375*(y0+k₂) + 0.125*y0
    #          = y0 + 0.375*(k₁+k₂)
    # Want B_y(0.5) = Y_CAP_END = 214 → k₁+k₂ = (214-210)/0.375 = 10.667
    # Use k₁ = k₂ = 5.333
    k = (Y_CAP_END - y0) / 0.375 / 2.0   # ≈ 5.333

    P0 = (lx0, y0)
    P1 = (lx0 + k * dle_dx_dy, y0 + k)
    P2 = (tx0 + k * dte_dx_dy, y0 + k)    # dte_dx_dy is negative, so this moves left
    P3 = (tx0, y0)

    pts = []
    for i in range(n_pts + 1):
        t = i / n_pts
        u = 1.0 - t
        # Cubic Bezier formula
        bx = u**3 * P0[0] + 3*u**2*t * P1[0] + 3*u*t**2 * P2[0] + t**3 * P3[0]
        by = u**3 * P0[1] + 3*u**2*t * P1[1] + 3*u*t**2 * P2[1] + t**3 * P3[1]
        pts.append((bx, by))

    return pts
