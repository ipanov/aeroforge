"""2D airfoil polar analysis using AeroSandbox/NeuralFoil.

NeuralFoil is a neural-network surrogate trained on millions of XFOIL runs.
It provides fast, accurate Cl, Cd, Cm predictions across the full alpha/Re range
relevant to RC sailplanes (Re 40k-200k).

Usage:
    from src.analysis.airfoil_polars import analyze_airfoil, analyze_wing_stations

    # Single airfoil polar
    polar = analyze_airfoil("AG24", re=112000)

    # All wing stations
    results = analyze_wing_stations()

All dimensions in mm, weights in grams, angles in degrees.
"""

from __future__ import annotations

import numpy as np
import aerosandbox as asb
import aerosandbox.numpy as np_asb

from src.core.specs import SAILPLANE
from src.cad.airfoils import get_airfoil, blend_airfoils, resample_airfoil


def _coords_to_asb_airfoil(
    name: str,
    coords: np.ndarray,
) -> asb.Airfoil:
    """Convert our airfoil coordinates to an AeroSandbox Airfoil object."""
    # AeroSandbox expects coordinates in standard format: (N, 2)
    # upper surface first (TE to LE), then lower (LE to TE) - Selig format
    # which is exactly what our data already is.
    return asb.Airfoil(
        name=name,
        coordinates=coords,
    )


def analyze_airfoil(
    name: str,
    re: float = 100_000,
    alpha_range: tuple[float, float, float] = (-5, 15, 0.5),
    mach: float = 0.02,
) -> dict:
    """Run polar analysis on a single airfoil at given Reynolds number.

    Args:
        name: Airfoil name (e.g. "AG24", "NACA0009")
        re: Reynolds number
        alpha_range: (start, stop, step) in degrees
        mach: Mach number (default ~7 m/s at sea level)

    Returns:
        dict with keys: name, re, alpha, cl, cd, cm, cl_cd, cl_max, alpha_stall,
                        cl_at_zero_alpha, alpha_at_zero_cl, cd_min
    """
    coords = get_airfoil(name)
    airfoil = _coords_to_asb_airfoil(name, coords)

    alphas = np.arange(*alpha_range)

    # Use NeuralFoil via AeroSandbox
    aero = airfoil.get_aero_from_neuralfoil(
        alpha=alphas,
        Re=re,
        mach=mach,
    )

    cl = np.array(aero["CL"])
    cd = np.array(aero["CD"])
    cm = np.array(aero["CM"])
    cl_cd = cl / np.where(cd > 1e-6, cd, 1e-6)

    # Key performance metrics
    cl_max_idx = np.argmax(cl)
    cl_max = float(cl[cl_max_idx])
    alpha_stall = float(alphas[cl_max_idx])

    # Cl at alpha=0
    zero_idx = np.argmin(np.abs(alphas))
    cl_at_zero = float(cl[zero_idx])

    # Alpha at Cl=0 (interpolate)
    try:
        sign_changes = np.where(np.diff(np.sign(cl)))[0]
        if len(sign_changes) > 0:
            idx = sign_changes[0]
            alpha_zero_cl = float(
                alphas[idx] - cl[idx] * (alphas[idx + 1] - alphas[idx]) / (cl[idx + 1] - cl[idx])
            )
        else:
            alpha_zero_cl = float("nan")
    except (IndexError, ZeroDivisionError):
        alpha_zero_cl = float("nan")

    cd_min = float(np.min(cd))
    best_ld_idx = np.argmax(cl_cd)

    return {
        "name": name,
        "re": re,
        "alpha": alphas.tolist(),
        "cl": cl.tolist(),
        "cd": cd.tolist(),
        "cm": cm.tolist(),
        "cl_cd": cl_cd.tolist(),
        "cl_max": cl_max,
        "alpha_stall": alpha_stall,
        "cl_at_zero_alpha": cl_at_zero,
        "alpha_at_zero_cl": alpha_zero_cl,
        "cd_min": cd_min,
        "best_ld": float(cl_cd[best_ld_idx]),
        "alpha_best_ld": float(alphas[best_ld_idx]),
        "cl_best_ld": float(cl[best_ld_idx]),
    }


def analyze_blended_airfoil(
    span_fraction: float,
    re: float,
    root_airfoil: str = "AG24",
    mid_airfoil: str = "AG09",
    tip_airfoil: str = "AG03",
    **kwargs,
) -> dict:
    """Analyze the blended airfoil at a specific span station.

    Args:
        span_fraction: 0.0 = root, 1.0 = tip
        re: Reynolds number at this station
        root_airfoil, mid_airfoil, tip_airfoil: Airfoil names
        **kwargs: Passed to analyze_airfoil

    Returns:
        Polar results dict with span_fraction added.
    """
    # Get blended coordinates
    if span_fraction <= 0.5:
        t = span_fraction / 0.5
        coords = blend_airfoils(root_airfoil, mid_airfoil, t)
    else:
        t = (span_fraction - 0.5) / 0.5
        coords = blend_airfoils(mid_airfoil, tip_airfoil, t)

    name = f"blend_{span_fraction:.2f}"
    airfoil = _coords_to_asb_airfoil(name, coords)

    alphas = np.arange(*kwargs.get("alpha_range", (-5, 15, 0.5)))
    mach = kwargs.get("mach", 0.02)

    aero = airfoil.get_aero_from_neuralfoil(
        alpha=alphas,
        Re=re,
        mach=mach,
    )

    cl = np.array(aero["CL"])
    cd = np.array(aero["CD"])
    cm = np.array(aero["CM"])
    cl_cd = cl / np.where(cd > 1e-6, cd, 1e-6)

    cl_max_idx = np.argmax(cl)

    return {
        "name": name,
        "span_fraction": span_fraction,
        "re": re,
        "alpha": alphas.tolist(),
        "cl": cl.tolist(),
        "cd": cd.tolist(),
        "cm": cm.tolist(),
        "cl_cd": cl_cd.tolist(),
        "cl_max": float(cl[cl_max_idx]),
        "alpha_stall": float(alphas[cl_max_idx]),
        "cd_min": float(np.min(cd)),
        "best_ld": float(np.max(cl_cd)),
    }


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


def print_polar_summary(polar: dict) -> str:
    """Format a polar result as a readable summary."""
    lines = [
        f"Airfoil: {polar['name']}  Re={polar['re']:.0f}",
        f"  Cl_max = {polar['cl_max']:.3f} at alpha = {polar['alpha_stall']:.1f} deg",
        f"  Cd_min = {polar['cd_min']:.5f}",
        f"  Best L/D = {polar['best_ld']:.1f}",
    ]
    if "alpha_at_zero_cl" in polar:
        lines.append(f"  Alpha_0 = {polar.get('alpha_at_zero_cl', 'N/A')}")
    return "\n".join(lines)


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
