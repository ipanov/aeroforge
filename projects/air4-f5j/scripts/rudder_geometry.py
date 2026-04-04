"""
Rudder Shared Geometry — VStab-based planform with HT-14/HT-12 airfoils.
==========================================================================
Used by rudder drawing and build scripts.

The rudder is the aft portion of the VStab airfoil, hinged at a line that
varies from 62% chord at root to 65% chord at tip. The VStab has zero LE
sweep (straight LE at fuselage X=866mm) with linear taper from 180mm root
to 95mm tip over 165mm height.

Coordinate convention for the RUDDER COMPONENT (local coords):
  Z = spanwise (0 at VStab root = fuselage bottom of fin, 165 at tip)
  X = chordwise (0 at hinge line, positive toward TE)
  Y = thickness direction

This is consistent with the elevator convention but oriented vertically.
"""

import math
import os
import numpy as np
from numpy import interp as np_interp

# === VStab Parameters (from Fuselage Consensus v2) ===
VSTAB_HEIGHT = 165.0       # mm, full fin height
VSTAB_ROOT_CHORD = 180.0   # mm
VSTAB_TIP_CHORD = 95.0     # mm
VSTAB_TAPER_RATE = (VSTAB_ROOT_CHORD - VSTAB_TIP_CHORD) / VSTAB_HEIGHT  # 0.5152 mm/mm

# Rudder hinge position (fraction of local VStab chord from LE)
HINGE_FRAC_ROOT = 0.62   # 62% chord at root
HINGE_FRAC_TIP = 0.65    # 65% chord at tip

# Rudder chord ratio
RUDDER_FRAC_ROOT = 0.38  # 38% of VStab chord at root
RUDDER_FRAC_TIP = 0.35   # 35% of VStab chord at tip

# Hinge/bore parameters
HINGE_BORE_D = 0.6         # bore diameter for 0.5mm wire (with PETG sleeve)
PUSHROD_BORE_D = 1.6       # pushrod hole diameter
PUSHROD_Z = 9.0            # pushrod hole height above root (Z=0)

# Bull-nose parameters
BULL_NOSE_ROOT = 2.5       # bull-nose overhang at root (mm forward of hinge)
BULL_NOSE_FADE_Z = 155.0   # bull-nose fades to zero before tip (airfoil gets thin)

# Rib positions (3 internal ribs)
RIB_POSITIONS = [41.0, 83.0, 124.0]  # Z positions (mm from root)

# Wall thickness
WALL = 0.40                # mm, vase mode
BULL_NOSE_WALL = 0.55      # mm, reinforced bull-nose zone

# TE truncation
TE_TRUNC = 0.97            # truncate at 97% chord

# Material
LW_PLA_DENSITY = 0.75e-3   # g/mm^3

# Thickness ratios
T_ROOT = 0.075             # HT-14: 7.5%
T_TIP = 0.051              # HT-12: 5.1%


def vstab_chord(z):
    """VStab local chord at height z (linear taper, 0=root, 165=tip)."""
    z = max(0, min(z, VSTAB_HEIGHT))
    return VSTAB_ROOT_CHORD - VSTAB_TAPER_RATE * z


def hinge_frac(z):
    """Hinge position as fraction of VStab chord (linear interpolation root->tip)."""
    t = z / VSTAB_HEIGHT
    return HINGE_FRAC_ROOT + (HINGE_FRAC_TIP - HINGE_FRAC_ROOT) * t


def rudder_frac(z):
    """Rudder chord as fraction of VStab chord (linear interpolation root->tip)."""
    t = z / VSTAB_HEIGHT
    return RUDDER_FRAC_ROOT + (RUDDER_FRAC_TIP - RUDDER_FRAC_ROOT) * t


def rudder_chord(z):
    """Rudder chord at height z (from hinge to TE, truncated)."""
    vc = vstab_chord(z)
    rf = rudder_frac(z)
    return vc * rf * TE_TRUNC


def rudder_chord_full(z):
    """Rudder chord at height z (from hinge to TE, full — no truncation)."""
    vc = vstab_chord(z)
    rf = rudder_frac(z)
    return vc * rf


def bull_nose_depth(z):
    """Bull-nose overhang at height z (mm forward of hinge)."""
    if z >= BULL_NOSE_FADE_Z:
        return 0.0
    return BULL_NOSE_ROOT * max(0.0, 1.0 - z / BULL_NOSE_FADE_Z)


def t_ratio(z):
    """Thickness ratio at height z (linear blend HT-14 -> HT-12)."""
    return T_ROOT + (T_TIP - T_ROOT) * min(z / VSTAB_HEIGHT, 1.0)


# === Real Airfoil Data (HT-14, HT-12) ===

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

    coords = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) == 2:
            coords.append((float(parts[0]), float(parts[1])))

    x_vals = [c[0] for c in coords]
    le_idx = x_vals.index(min(x_vals))

    upper = list(reversed(coords[:le_idx + 1]))
    lower = coords[le_idx:]

    x_upper = [p[0] for p in upper]
    y_upper = [p[1] for p in upper]
    x_lower = [p[0] for p in lower]
    y_lower = [p[1] for p in lower]

    return x_upper, y_upper, x_lower, y_lower


# Pre-load airfoil data at import time
try:
    _HT14_XU, _HT14_YU, _HT14_XL, _HT14_YL = _load_selig_dat('ht14.dat')
    _HT14_LOADED = True
except FileNotFoundError:
    _HT14_LOADED = False

try:
    _HT12_XU, _HT12_YU, _HT12_XL, _HT12_YL = _load_selig_dat('ht12.dat')
    _HT12_LOADED = True
except FileNotFoundError:
    _HT12_LOADED = False


def airfoil_yt_upper(xc, z_span):
    """Real HT-14/HT-12 blended upper surface y/c at chord fraction xc and span z."""
    if xc <= 0 or xc > 1.0:
        return 0.0
    blend = min(z_span / VSTAB_HEIGHT, 1.0)  # 0=root(HT14), 1=tip(HT12)

    if _HT14_LOADED:
        y14 = float(np_interp(xc, _HT14_XU, _HT14_YU))
    else:
        y14 = _naca4_yt(xc, T_ROOT)

    if _HT12_LOADED:
        y12 = float(np_interp(xc, _HT12_XU, _HT12_YU))
    else:
        y12 = _naca4_yt(xc, T_TIP)

    return y14 * (1 - blend) + y12 * blend


def airfoil_yt_lower(xc, z_span):
    """Real HT-14/HT-12 blended lower surface y/c at chord fraction xc and span z."""
    if xc <= 0 or xc > 1.0:
        return 0.0
    blend = min(z_span / VSTAB_HEIGHT, 1.0)

    if _HT14_LOADED:
        y14 = float(np_interp(xc, _HT14_XL, _HT14_YL))
    else:
        y14 = -_naca4_yt(xc, T_ROOT)

    if _HT12_LOADED:
        y12 = float(np_interp(xc, _HT12_XL, _HT12_YL))
    else:
        y12 = -_naca4_yt(xc, T_TIP)

    return y14 * (1 - blend) + y12 * blend


def _naca4_yt(xc, tr):
    """NACA 4-digit half-thickness (fallback if .dat not available)."""
    if xc <= 0:
        return 0.0
    xc = min(xc, 1.0)
    return 5 * tr * (0.2969 * xc**0.5 - 0.1260 * xc - 0.3516 * xc**2
                     + 0.2843 * xc**3 - 0.1015 * xc**4)


def airfoil_section_points(z_span, x_start_frac=0.0, x_end_frac=1.0, n_pts=80):
    """Generate upper and lower surface points for a section at height z.

    Returns (upper_pts, lower_pts) as lists of (x_mm, y_mm) in local coords.
    x_start_frac, x_end_frac: chord fraction range of the FULL VStab chord.
    Uses cosine spacing for smooth LE.
    """
    c = vstab_chord(z_span)
    if c < 0.5:
        return [], []

    fracs = []
    for i in range(n_pts + 1):
        t = i / n_pts
        frac = x_start_frac + (x_end_frac - x_start_frac) * (1 - math.cos(math.pi / 2 * t))
        fracs.append(min(frac, x_end_frac))

    upper_pts = []
    lower_pts = []
    for frac in fracs:
        x_mm = frac * c
        yu = airfoil_yt_upper(frac, z_span) * c
        yl = airfoil_yt_lower(frac, z_span) * c
        upper_pts.append((x_mm, yu))
        lower_pts.append((x_mm, yl))

    return upper_pts, lower_pts
