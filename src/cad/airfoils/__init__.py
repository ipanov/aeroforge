"""Airfoil generators for sailplane wings.

This module provides parametric airfoil generation using:
- NACA 4-digit series
- NACA 5-digit series
- AG series (thermal soarers)
- Custom imported coordinates
"""

from typing import Tuple
import math

# Common sailplane airfoils
AIRFOIL_DATABASE = {
    # AG series - excellent for thermal soarers
    "AG03": {"thickness": 8.4, "camber": 3.5, "description": "Light thermal"},
    "AG09": {"thickness": 9.2, "camber": 3.8, "description": "All-around thermal"},
    "AG35": {"thickness": 9.5, "camber": 4.0, "description": "Heavy thermal"},

    # Competition proven
    "RG-15": {"thickness": 8.9, "camber": 2.8, "description": "F3B/F3J proven"},
    "S3021": {"thickness": 9.5, "camber": 3.0, "description": "Smooth stall"},
    "E387": {"thickness": 9.1, "camber": 3.8, "description": "Low Reynolds"},

    # NACA classics
    "NACA2412": {"thickness": 12.0, "camber": 2.0, "description": "Classic"},
    "NACA4412": {"thickness": 12.0, "camber": 4.0, "description": "More lift"},
}


def naca_4digit(m: float, p: float, t: float, n_points: int = 100) -> Tuple[list, list]:
    """Generate NACA 4-digit airfoil coordinates.

    Args:
        m: Maximum camber (0-9, as percentage of chord)
        p: Position of max camber (0-9, as tenths of chord)
        t: Thickness (0-99, as percentage of chord)
        n_points: Number of points per surface

    Returns:
        Tuple of (upper_surface, lower_surface) coordinate lists
    """
    m = m / 100  # Camber
    p = p / 10   # Position of max camber
    t = t / 100  # Thickness

    x_upper = []
    y_upper = []
    x_lower = []
    y_lower = []

    for i in range(n_points + 1):
        # Cosine spacing for better resolution at leading edge
        beta = i * math.pi / n_points
        x = (1 - math.cos(beta)) / 2

        # Thickness distribution
        yt = 5 * t * (0.2969 * math.sqrt(x) - 0.1260 * x -
                      0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)

        # Camber line
        if x < p and p > 0:
            yc = m * (2 * p * x - x**2) / p**2
            dyc = 2 * m * (p - x) / p**2
        elif p > 0:
            yc = m * (1 - 2 * p + 2 * p * x - x**2) / (1 - p)**2
            dyc = 2 * m * (p - x) / (1 - p)**2
        else:
            yc = 0
            dyc = 0

        theta = math.atan(dyc)

        x_upper.append(x - yt * math.sin(theta))
        y_upper.append(yc + yt * math.cos(theta))
        x_lower.append(x + yt * math.sin(theta))
        y_lower.append(yc - yt * math.cos(theta))

    return (list(zip(x_upper, y_upper)), list(zip(x_lower, y_lower)))


def naca_profile(code: str, chord: float = 100.0, n_points: int = 100) -> list:
    """Generate scaled NACA airfoil coordinates.

    Args:
        code: NACA designation (e.g., "2412", "4412")
        chord: Chord length in mm
        n_points: Number of points per surface

    Returns:
        List of (x, y) tuples scaled to chord length
    """
    if len(code) != 4:
        raise ValueError(f"Invalid NACA code: {code}")

    m = int(code[0])      # Max camber
    p = int(code[1])      # Position of max camber
    t = int(code[2:4])    # Thickness

    upper, lower = naca_4digit(m, p, t, n_points)

    # Combine into closed profile (trailing edge to leading edge to trailing edge)
    profile = []
    for x, y in reversed(upper):
        profile.append((x * chord, y * chord))
    for x, y in lower[1:]:  # Skip first point (same as last upper)
        profile.append((x * chord, y * chord))

    return profile


def ag_profile(variant: str = "AG09", chord: float = 100.0) -> list:
    """Generate AG series airfoil (placeholder - needs coordinate data).

    Args:
        variant: AG series variant (AG03, AG09, AG35)
        chord: Chord length in mm

    Returns:
        List of (x, y) tuples

    Note:
        This is a placeholder. Full implementation requires importing
        coordinate data from airfoil databases.
    """
    if variant not in AIRFOIL_DATABASE:
        raise ValueError(f"Unknown airfoil: {variant}")

    # TODO: Import actual AG coordinates from data file
    # For now, approximate with similar NACA
    if variant == "AG03":
        return naca_profile("2409", chord)
    elif variant == "AG09":
        return naca_profile("3410", chord)
    elif variant == "AG35":
        return naca_profile("4410", chord)

    return naca_profile("2412", chord)
