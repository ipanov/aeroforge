"""Airfoil generators for sailplane wings.

Supports:
- Real AG series coordinate data (from UIUC database)
- NACA 4-digit series (parametric)
- Continuous airfoil blending between any two profiles
- Chord scaling and rotation (for twist/washout)

All coordinates are normalized (0-1 chord fraction) internally,
scaled to physical dimensions on output.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

import numpy as np

# Directory containing .dat airfoil files
_DATA_DIR = Path(__file__).parent

# Cache for loaded airfoil coordinates
_AIRFOIL_CACHE: dict[str, np.ndarray] = {}

# Airfoil metadata (for reference/selection)
AIRFOIL_DATABASE = {
    "AG03": {"thickness": 6.4, "camber": 5.1, "re_range": "40k-80k",
             "description": "Light thermal, thin tips, high camber"},
    "AG09": {"thickness": 5.4, "camber": 4.2, "re_range": "60k-120k",
             "description": "Ultra-thin thermal, reflexed lower surface"},
    "AG24": {"thickness": 8.6, "camber": 6.2, "re_range": "80k-200k",
             "description": "Bubble Dancer DLG, thickest AG, excellent low-speed"},
    "AG25": {"thickness": 8.4, "camber": 3.9, "re_range": "60k-150k",
             "description": "AG24 companion, thinner"},
    "AG35": {"thickness": 9.5, "camber": 4.0, "re_range": "50k-100k",
             "description": "Heavy thermal, lower Re optimized"},
    "AG36": {"thickness": 8.0, "camber": 3.3, "re_range": "40k-80k",
             "description": "AG35 tip companion"},
    "AG44ct": {"thickness": 8.5, "camber": 4.1, "re_range": "60k-120k",
               "description": "Aileron glider with camber-changing flaps"},
    "RG-15": {"thickness": 8.9, "camber": 2.8, "re_range": "100k-300k",
              "description": "F3B/F3J competition proven"},
    "NACA0009": {"thickness": 9.0, "camber": 0.0, "re_range": "any",
                 "description": "Symmetric, tail surfaces"},
}


def load_dat_airfoil(name: str) -> np.ndarray:
    """Load airfoil coordinates from a .dat file (Selig format).

    The Selig format lists coordinates from trailing edge, around the
    upper surface to the leading edge, then back along the lower surface
    to the trailing edge.

    Returns:
        np.ndarray of shape (N, 2) with normalized (x, y) coordinates.
    """
    if name in _AIRFOIL_CACHE:
        return _AIRFOIL_CACHE[name]

    dat_file = _DATA_DIR / f"{name.lower()}.dat"
    if not dat_file.exists():
        raise FileNotFoundError(f"Airfoil data file not found: {dat_file}")

    coords = []
    with open(dat_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 2:
                try:
                    x, y = float(parts[0]), float(parts[1])
                    coords.append([x, y])
                except ValueError:
                    continue  # Skip header line

    result = np.array(coords, dtype=np.float64)
    _AIRFOIL_CACHE[name] = result
    return result


def naca_4digit(m: float, p: float, t: float, n_points: int = 100) -> np.ndarray:
    """Generate NACA 4-digit airfoil in Selig format.

    Args:
        m: Max camber digit (0-9)
        p: Position of max camber digit (0-9)
        t: Thickness as 2-digit percentage (00-99)
        n_points: Points per surface

    Returns:
        np.ndarray of shape (2*n_points+1, 2) in Selig format.
    """
    mc = m / 100.0
    pc = p / 10.0
    tc = t / 100.0

    upper_x, upper_y = [], []
    lower_x, lower_y = [], []

    for i in range(n_points + 1):
        beta = i * math.pi / n_points
        x = (1 - math.cos(beta)) / 2

        yt = 5 * tc * (0.2969 * math.sqrt(x) - 0.1260 * x -
                        0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)

        if x < pc and pc > 0:
            yc = mc * (2 * pc * x - x**2) / pc**2
            dyc = 2 * mc * (pc - x) / pc**2
        elif pc > 0:
            yc = mc * (1 - 2 * pc + 2 * pc * x - x**2) / (1 - pc)**2
            dyc = 2 * mc * (pc - x) / (1 - pc)**2
        else:
            yc = 0.0
            dyc = 0.0

        theta = math.atan(dyc)
        upper_x.append(x - yt * math.sin(theta))
        upper_y.append(yc + yt * math.cos(theta))
        lower_x.append(x + yt * math.sin(theta))
        lower_y.append(yc - yt * math.cos(theta))

    # Selig format: upper surface reversed (TE to LE), then lower (LE to TE)
    coords = []
    for i in range(n_points, -1, -1):
        coords.append([upper_x[i], upper_y[i]])
    for i in range(1, n_points + 1):
        coords.append([lower_x[i], lower_y[i]])

    return np.array(coords, dtype=np.float64)


def naca_profile(code: str, n_points: int = 100) -> np.ndarray:
    """Generate NACA airfoil coordinates (normalized).

    Args:
        code: NACA designation (e.g., "0009", "2412")
        n_points: Points per surface

    Returns:
        np.ndarray of shape (N, 2), normalized coordinates.
    """
    if len(code) != 4:
        raise ValueError(f"Only NACA 4-digit supported, got: {code}")
    return naca_4digit(int(code[0]), int(code[1]), int(code[2:4]), n_points)


def get_airfoil(name: str, n_points: int = 100) -> np.ndarray:
    """Get airfoil coordinates by name (AG series or NACA).

    Returns normalized (0-1) coordinates in Selig format.
    """
    name_upper = name.upper().replace("-", "")
    if name_upper.startswith("NACA"):
        return naca_profile(name_upper[4:], n_points)
    else:
        return load_dat_airfoil(name_upper)


def resample_airfoil(coords: np.ndarray, n_points: int = 150) -> np.ndarray:
    """Resample airfoil to uniform point count using arc-length parameterization.

    Essential for blending - both airfoils must have the same number of points
    at corresponding positions.

    Returns:
        np.ndarray of shape (2*n_points+1, 2)
    """
    # Find leading edge (minimum x)
    le_idx = np.argmin(coords[:, 0])

    # Split into upper and lower surfaces
    upper = coords[:le_idx + 1]  # TE to LE
    lower = coords[le_idx:]       # LE to TE

    def resample_surface(pts: np.ndarray, n: int) -> np.ndarray:
        """Resample a surface to n+1 points using arc-length."""
        # Compute cumulative arc length
        diffs = np.diff(pts, axis=0)
        seg_lengths = np.sqrt(diffs[:, 0]**2 + diffs[:, 1]**2)
        cum_length = np.concatenate([[0], np.cumsum(seg_lengths)])
        total = cum_length[-1]

        if total < 1e-12:
            return np.tile(pts[0], (n + 1, 1))

        # Uniform arc-length targets
        targets = np.linspace(0, total, n + 1)

        # Interpolate
        x_interp = np.interp(targets, cum_length, pts[:, 0])
        y_interp = np.interp(targets, cum_length, pts[:, 1])
        return np.column_stack([x_interp, y_interp])

    upper_r = resample_surface(upper, n_points)
    lower_r = resample_surface(lower, n_points)

    # Combine: upper (TE→LE) + lower (LE→TE, skip first point = LE)
    return np.vstack([upper_r, lower_r[1:]])


def blend_airfoils(
    airfoil_a: str | np.ndarray,
    airfoil_b: str | np.ndarray,
    blend_factor: float,
    n_points: int = 150,
) -> np.ndarray:
    """Blend two airfoils by linear interpolation.

    Args:
        airfoil_a: Name or coordinates of first airfoil (at blend_factor=0)
        airfoil_b: Name or coordinates of second airfoil (at blend_factor=1)
        blend_factor: 0.0 = pure A, 1.0 = pure B
        n_points: Points per surface for resampling

    Returns:
        np.ndarray of blended, normalized coordinates.
    """
    if isinstance(airfoil_a, str):
        airfoil_a = get_airfoil(airfoil_a)
    if isinstance(airfoil_b, str):
        airfoil_b = get_airfoil(airfoil_b)

    # Resample both to same point count
    a = resample_airfoil(airfoil_a, n_points)
    b = resample_airfoil(airfoil_b, n_points)

    # Linear interpolation
    t = np.clip(blend_factor, 0.0, 1.0)
    return a * (1 - t) + b * t


def airfoil_at_station(
    span_fraction: float,
    root_airfoil: str = "AG24",
    mid_airfoil: str = "AG09",
    tip_airfoil: str = "AG03",
    mid_station: float = 0.5,
    n_points: int = 150,
) -> np.ndarray:
    """Get the blended airfoil at any span station.

    Uses piecewise blending: root→mid from 0 to mid_station,
    mid→tip from mid_station to 1.0.

    Args:
        span_fraction: 0.0 = root, 1.0 = tip
        root_airfoil: Airfoil name at root
        mid_airfoil: Airfoil name at mid-span
        tip_airfoil: Airfoil name at tip
        mid_station: Span fraction where mid airfoil is pure
        n_points: Points per surface

    Returns:
        Blended airfoil coordinates (normalized).
    """
    if span_fraction <= mid_station:
        t = span_fraction / mid_station
        return blend_airfoils(root_airfoil, mid_airfoil, t, n_points)
    else:
        t = (span_fraction - mid_station) / (1.0 - mid_station)
        return blend_airfoils(mid_airfoil, tip_airfoil, t, n_points)


def scale_airfoil(
    coords: np.ndarray,
    chord: float,
    twist_deg: float = 0.0,
    twist_center: float = 0.25,
) -> np.ndarray:
    """Scale airfoil to physical dimensions and apply twist.

    Args:
        coords: Normalized (0-1) airfoil coordinates
        chord: Physical chord length in mm
        twist_deg: Twist angle in degrees (positive = leading edge up)
        twist_center: Chord fraction about which to rotate (0.25 = quarter-chord)

    Returns:
        np.ndarray of physical (x, y) coordinates in mm.
    """
    # Scale
    scaled = coords * chord

    if abs(twist_deg) > 1e-6:
        # Rotate about twist center
        cx = twist_center * chord
        cy = 0.0
        angle = math.radians(twist_deg)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        translated = scaled - np.array([cx, cy])
        rotated = np.column_stack([
            translated[:, 0] * cos_a - translated[:, 1] * sin_a,
            translated[:, 0] * sin_a + translated[:, 1] * cos_a,
        ])
        scaled = rotated + np.array([cx, cy])

    return scaled


def airfoil_to_build123d_wire(
    coords: np.ndarray,
    chord: float,
    twist_deg: float = 0.0,
    z_position: float = 0.0,
) -> list[tuple[float, float, float]]:
    """Convert airfoil coordinates to 3D points for Build123d.

    The airfoil lies in the XZ plane at the given Y position (spanwise).
    X = chordwise (nose at 0), Z = thickness direction, Y = spanwise.

    Wait - for wing convention:
    X = spanwise, Y = chordwise (LE forward), Z = up

    Actually, for Build123d lofting:
    We place each rib in the XY plane at a Z position (span).
    X = chordwise, Y = up (thickness), Z = spanwise.

    Args:
        coords: Normalized airfoil coordinates
        chord: Physical chord in mm
        twist_deg: Twist in degrees
        z_position: Spanwise position in mm

    Returns:
        List of (x, y, z) tuples for Build123d.
    """
    scaled = scale_airfoil(coords, chord, twist_deg)
    return [(pt[0], pt[1], z_position) for pt in scaled]


def max_thickness(coords: np.ndarray) -> tuple[float, float]:
    """Calculate maximum thickness and its chordwise position.

    Returns:
        (max_thickness_fraction, position_fraction) both as fraction of chord.
    """
    le_idx = np.argmin(coords[:, 0])
    upper = coords[:le_idx + 1]
    lower = coords[le_idx:]

    # Resample to common x stations
    x_stations = np.linspace(0, 1, 200)

    upper_sorted = upper[np.argsort(upper[:, 0])]
    lower_sorted = lower[np.argsort(lower[:, 0])]

    y_upper = np.interp(x_stations, upper_sorted[:, 0], upper_sorted[:, 1])
    y_lower = np.interp(x_stations, lower_sorted[:, 0], lower_sorted[:, 1])

    thickness = y_upper - y_lower
    max_idx = np.argmax(thickness)
    return float(thickness[max_idx]), float(x_stations[max_idx])
