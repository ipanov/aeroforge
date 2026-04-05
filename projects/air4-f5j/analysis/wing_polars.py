"""F5J wing station polar analysis.

Analyzes blended airfoil performance at multiple span stations
using the F5J sailplane wing specification.

Usage:
    from projects.air4_f5j.analysis.wing_polars import analyze_wing_stations

    results = analyze_wing_stations()
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from specs import SAILPLANE

from src.analysis.airfoil_polars import analyze_blended_airfoil


def analyze_wing_stations(
    n_stations: int = 11,
    velocity: float = 8.0,
) -> list[dict]:
    """Analyze airfoil performance at multiple span stations.

    Uses the actual blended airfoil and Reynolds number at each station.

    Args:
        n_stations: Number of span stations to analyze (root to tip)
        velocity: Flight velocity in m/s

    Returns:
        List of polar dicts, one per station.
    """
    wing = SAILPLANE.wing
    stations = np.linspace(0, 1, n_stations)
    results = []

    for eta in stations:
        re = wing.reynolds_at(eta, velocity)
        result = analyze_blended_airfoil(
            span_fraction=eta,
            re=re,
            root_airfoil=wing.airfoil_root,
            mid_airfoil=wing.airfoil_mid,
            tip_airfoil=wing.airfoil_tip,
        )
        result["chord_mm"] = wing.chord_at(eta)
        result["velocity_ms"] = velocity
        results.append(result)

    return results


def print_wing_analysis(results: list[dict]) -> str:
    """Format wing station analysis as a table."""
    lines = [
        "Wing Station Analysis",
        "=" * 80,
        f"{'Station':>8} {'Chord':>7} {'Re':>8} {'Cl_max':>7} {'Cd_min':>8} {'L/D_max':>8} {'Stall':>6}",
        "-" * 80,
    ]

    for r in results:
        eta = r.get("span_fraction", 0)
        lines.append(
            f"{eta:>7.0%} {r.get('chord_mm', 0):>6.0f}mm "
            f"{r['re']:>8.0f} {r['cl_max']:>7.3f} {r['cd_min']:>8.5f} "
            f"{r['best_ld']:>8.1f} {r.get('alpha_stall', 0):>5.1f} deg"
        )

    return "\n".join(lines)
