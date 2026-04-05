"""CFD result extraction, analysis, and industry-standard report generation.

Parses SU2 output files (history.csv, surface_flow.csv) to extract:
- Aerodynamic coefficients (CL, CD, CM) at each alpha
- Surface pressure distribution (Cp)
- Skin friction distribution (Cf)
- Drag breakdown (pressure drag vs friction drag)
- Stability derivatives (dCL/da, dCM/da, etc.)
- Convergence diagnostics

Generates structured report data suitable for:
- Markdown Aero Test Reports (industry standard)
- JSON feedback for the design iteration loop
- ParaView-compatible surface data for heatmap rendering

All units: SI (m, m/s, Pa, degrees). Output CL/CD/CM are dimensionless.
"""

from __future__ import annotations

import csv
import json
import logging
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SurfacePoint:
    """Single point on the CFD surface mesh with flow quantities."""

    x: float
    y: float
    z: float
    cp: float = 0.0         # Pressure coefficient
    cf: float = 0.0         # Skin friction coefficient (magnitude)
    cf_x: float = 0.0       # Skin friction x-component
    cf_y: float = 0.0       # Skin friction y-component
    cf_z: float = 0.0       # Skin friction z-component
    pressure: float = 0.0   # Static pressure (Pa)
    temperature: float = 0.0
    mach: float = 0.0


@dataclass
class ConvergenceRecord:
    """Single iteration from SU2 convergence history."""

    iteration: int
    rms_density: float = 0.0
    rms_momentum_x: float = 0.0
    rms_momentum_y: float = 0.0
    rms_momentum_z: float = 0.0
    rms_energy: float = 0.0
    cl: float = 0.0
    cd: float = 0.0
    cm: float = 0.0
    wall_time_s: float = 0.0


@dataclass
class AlphaResult:
    """Complete result for a single angle of attack."""

    alpha: float
    cl: float
    cd: float
    cm: float
    l_d: float = 0.0
    cd_pressure: float = 0.0
    cd_friction: float = 0.0
    cl_pressure: float = 0.0
    cl_friction: float = 0.0
    converged: bool = True
    iterations: int = 0
    final_residual: float = 0.0
    surface_points: list[SurfacePoint] = field(default_factory=list)
    convergence_history: list[ConvergenceRecord] = field(default_factory=list)


@dataclass
class StabilityDerivatives:
    """Linearized stability derivatives from polar sweep."""

    cl_alpha: float = 0.0       # dCL/da (per degree)
    cm_alpha: float = 0.0       # dCM/da (per degree) — negative = stable
    cl_max: float = 0.0
    alpha_cl_max: float = 0.0
    cl_zero: float = 0.0        # CL at alpha=0
    alpha_zero_lift: float = 0.0
    cd_min: float = 0.0
    alpha_cd_min: float = 0.0
    ld_max: float = 0.0
    alpha_ld_max: float = 0.0
    cl_at_ld_max: float = 0.0
    alpha_trim: Optional[float] = None  # Alpha where CM=0
    neutral_point_pct_mac: Optional[float] = None


@dataclass
class DragBreakdown:
    """Drag component breakdown at a given alpha."""

    alpha: float
    cd_total: float
    cd_pressure: float
    cd_friction: float
    cd_induced: float = 0.0      # Estimated from CL^2 / (pi * AR * e)
    pct_pressure: float = 0.0
    pct_friction: float = 0.0
    pct_induced: float = 0.0


@dataclass
class CFDTestConfiguration:
    """Records the exact test setup for reproducibility."""

    geometry_file: str = ""
    mesh_file: str = ""
    mesh_cells: int = 0
    solver_type: str = "EULER"
    turbulence_model: str = ""
    reynolds_number: float = 0.0
    reynolds_length_m: float = 0.0
    freestream_velocity_ms: float = 0.0
    freestream_temperature_k: float = 288.15
    alpha_range: tuple[float, float] = (-5.0, 15.0)
    alpha_step: float = 1.0
    reference_area_m2: float = 1.0
    symmetry_plane: bool = False
    wall_clock_seconds: float = 0.0


@dataclass
class AeroTestReport:
    """Complete aerodynamic test report — the top-level result object.

    This is the mandatory output of every CFD validation run. Every field
    must be populated; missing data is a hard-stop error.
    """

    # Metadata
    component_name: str = ""
    project_name: str = ""
    iteration: int = 1
    round_label: str = "R1"
    timestamp: str = ""

    # Configuration
    config: CFDTestConfiguration = field(default_factory=CFDTestConfiguration)

    # Polar results (one per alpha)
    polar: list[AlphaResult] = field(default_factory=list)

    # Derived quantities
    stability: StabilityDerivatives = field(default_factory=StabilityDerivatives)
    drag_breakdown: list[DragBreakdown] = field(default_factory=list)

    # Convergence diagnostics
    all_converged: bool = True
    worst_residual: float = 0.0
    mean_iterations: float = 0.0

    # Artifacts (file paths)
    artifacts: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict (for JSON export). Excludes bulky surface points."""
        d = asdict(self)
        # Strip surface_points from polar entries (too large for JSON)
        for entry in d.get("polar", []):
            entry.pop("surface_points", None)
            entry.pop("convergence_history", None)
        return d

    def to_json(self, path: Path) -> Path:
        """Write report as JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        return path


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_surface_flow(csv_path: Path) -> list[SurfacePoint]:
    """Parse SU2 surface_flow.csv into SurfacePoint objects.

    SU2 surface CSV typically contains columns like:
    "x", "y", "z", "Pressure", "Temperature", "Mach",
    "Pressure_Coefficient", "Skin_Friction_Coefficient_X/Y/Z"

    Column names vary by SU2 version and solver type. This parser
    handles common variants.
    """
    if not csv_path.exists():
        logger.warning("Surface flow file not found: %s", csv_path)
        return []

    points: list[SurfacePoint] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return []

        # Normalize column names (strip quotes/spaces, lowercase)
        col_map: dict[str, str] = {}
        for raw_name in reader.fieldnames:
            clean = raw_name.strip().strip('"').strip().lower()
            col_map[clean] = raw_name

        def _get(row: dict, *candidates: str) -> float:
            for c in candidates:
                key = col_map.get(c)
                if key and key in row:
                    try:
                        return float(row[key])
                    except (ValueError, TypeError):
                        pass
            return 0.0

        for row in reader:
            pt = SurfacePoint(
                x=_get(row, "x", "points:0", "coord_x"),
                y=_get(row, "y", "points:1", "coord_y"),
                z=_get(row, "z", "points:2", "coord_z"),
                cp=_get(row, "pressure_coefficient", "cp", "c_p"),
                pressure=_get(row, "pressure", "p", "static_pressure"),
                temperature=_get(row, "temperature", "t"),
                mach=_get(row, "mach", "mach_number"),
            )
            # Skin friction — SU2 outputs x/y/z components
            pt.cf_x = _get(row, "skin_friction_coefficient_x", "cf_x", "cfx")
            pt.cf_y = _get(row, "skin_friction_coefficient_y", "cf_y", "cfy")
            pt.cf_z = _get(row, "skin_friction_coefficient_z", "cf_z", "cfz")
            pt.cf = math.sqrt(pt.cf_x**2 + pt.cf_y**2 + pt.cf_z**2)
            points.append(pt)

    logger.info("Parsed %d surface points from %s", len(points), csv_path)
    return points


def parse_history_csv(csv_path: Path) -> list[ConvergenceRecord]:
    """Parse SU2 history.csv for convergence tracking.

    Columns vary by solver, but common ones include:
    "Inner_Iter", "rms[Rho]", "rms[RhoU]", "rms[RhoV]", "rms[RhoW]",
    "rms[RhoE]", "CL", "CD", "CMz", "Time(sec)"
    """
    if not csv_path.exists():
        return []

    records: list[ConvergenceRecord] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return []

        col_map: dict[str, str] = {}
        for raw_name in reader.fieldnames:
            clean = raw_name.strip().strip('"').strip().lower()
            col_map[clean] = raw_name

        def _get(row: dict, *candidates: str) -> float:
            for c in candidates:
                key = col_map.get(c)
                if key and key in row:
                    try:
                        return float(row[key])
                    except (ValueError, TypeError):
                        pass
            return 0.0

        for row in reader:
            rec = ConvergenceRecord(
                iteration=int(_get(row, "inner_iter", "iter", "iteration", "outer_iter")),
                rms_density=_get(row, "rms[rho]", "rms[p]", "rms_rho", "res[rho]"),
                rms_momentum_x=_get(row, "rms[rhou]", "rms_rhou"),
                rms_momentum_y=_get(row, "rms[rhov]", "rms_rhov"),
                rms_momentum_z=_get(row, "rms[rhow]", "rms_rhow"),
                rms_energy=_get(row, "rms[rhoe]", "rms_rhoe"),
                cl=_get(row, "cl", "lift"),
                cd=_get(row, "cd", "drag"),
                cm=_get(row, "cmz", "cm", "moment_z"),
                wall_time_s=_get(row, "time(sec)", "wall_time", "time"),
            )
            records.append(rec)

    return records


def parse_forces_breakdown(forces_path: Path) -> dict[str, float]:
    """Parse SU2 forces_breakdown.dat for pressure/friction split.

    SU2 writes this file with lines like:
      Total CL:    0.45678
      Pressure CL: 0.44123
      Friction CL: 0.01555
      Total CD:    0.01234
      Pressure CD: 0.00800
      Friction CD: 0.00434
    """
    result: dict[str, float] = {}
    if not forces_path.exists():
        return result

    with open(forces_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if ":" not in line:
                continue
            key_raw, _, val_raw = line.partition(":")
            key = key_raw.strip().lower().replace(" ", "_").replace("(", "").replace(")", "")
            try:
                result[key] = float(val_raw.strip().split()[0])
            except (ValueError, IndexError):
                pass

    return result


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------


def compute_stability_derivatives(
    polar: list[AlphaResult],
    ref_area_m2: float = 1.0,
    mac_m: float = 0.17,
) -> StabilityDerivatives:
    """Compute stability derivatives from a polar sweep using linear regression.

    Uses the linear portion of the CL-alpha curve (typically -5 to +8 deg)
    for derivative calculation. Non-linear stall region is excluded.
    """
    if len(polar) < 3:
        logger.warning("Need at least 3 alpha points for stability derivatives")
        return StabilityDerivatives()

    alphas = np.array([p.alpha for p in polar])
    cls = np.array([p.cl for p in polar])
    cds = np.array([p.cd for p in polar])
    cms = np.array([p.cm for p in polar])
    lds = np.array([p.cl / p.cd if p.cd > 1e-8 else 0.0 for p in polar])

    # Find linear region: use points where CL is roughly linear
    # Heuristic: exclude points beyond CL_max (stall region)
    cl_max_idx = int(np.argmax(cls))
    linear_end = min(cl_max_idx + 1, len(alphas))
    linear_start = 0

    # Need at least 3 points in linear range
    if linear_end - linear_start < 3:
        linear_end = len(alphas)

    alpha_lin = alphas[linear_start:linear_end]
    cl_lin = cls[linear_start:linear_end]
    cm_lin = cms[linear_start:linear_end]

    # Linear regression for CL-alpha
    if len(alpha_lin) >= 2:
        cl_fit = np.polyfit(alpha_lin, cl_lin, 1)
        cl_alpha = cl_fit[0]  # dCL/da in per-degree
        cl_zero = cl_fit[1]   # CL at alpha=0
        alpha_zero_lift = -cl_zero / cl_alpha if abs(cl_alpha) > 1e-10 else 0.0
    else:
        cl_alpha = 0.0
        cl_zero = 0.0
        alpha_zero_lift = 0.0

    # Linear regression for CM-alpha
    if len(alpha_lin) >= 2:
        cm_fit = np.polyfit(alpha_lin, cm_lin, 1)
        cm_alpha = cm_fit[0]  # dCM/da — negative = statically stable
    else:
        cm_alpha = 0.0

    # Key points
    cl_max = float(np.max(cls))
    alpha_cl_max = float(alphas[np.argmax(cls)])
    cd_min = float(np.min(cds))
    alpha_cd_min = float(alphas[np.argmin(cds)])
    ld_max = float(np.max(lds))
    alpha_ld_max = float(alphas[np.argmax(lds)])
    cl_at_ld_max = float(cls[np.argmax(lds)])

    # Trim alpha (where CM crosses zero)
    alpha_trim: Optional[float] = None
    for i in range(len(cms) - 1):
        if cms[i] * cms[i + 1] < 0:  # Sign change
            # Linear interpolation
            frac = cms[i] / (cms[i] - cms[i + 1])
            alpha_trim = float(alphas[i] + frac * (alphas[i + 1] - alphas[i]))
            break

    # Neutral point estimate: x_np/c = -dCM/dCL = -cm_alpha/cl_alpha
    neutral_point: Optional[float] = None
    if abs(cl_alpha) > 1e-10:
        np_frac = -cm_alpha / cl_alpha
        neutral_point = round(np_frac * 100, 1)  # as % MAC

    return StabilityDerivatives(
        cl_alpha=round(cl_alpha, 6),
        cm_alpha=round(cm_alpha, 6),
        cl_max=round(cl_max, 4),
        alpha_cl_max=round(alpha_cl_max, 2),
        cl_zero=round(cl_zero, 4),
        alpha_zero_lift=round(alpha_zero_lift, 2),
        cd_min=round(cd_min, 6),
        alpha_cd_min=round(alpha_cd_min, 2),
        ld_max=round(ld_max, 2),
        alpha_ld_max=round(alpha_ld_max, 2),
        cl_at_ld_max=round(cl_at_ld_max, 4),
        alpha_trim=round(alpha_trim, 2) if alpha_trim is not None else None,
        neutral_point_pct_mac=neutral_point,
    )


def compute_drag_breakdown(
    polar: list[AlphaResult],
    aspect_ratio: float = 10.0,
    oswald_efficiency: float = 0.85,
) -> list[DragBreakdown]:
    """Compute drag breakdown for each alpha point.

    If SU2 provided pressure/friction split, uses those directly.
    Otherwise, estimates induced drag from lifting-line theory:
        CD_induced = CL^2 / (pi * AR * e)
    """
    breakdowns: list[DragBreakdown] = []

    for pt in polar:
        cd_total = pt.cd
        cd_pressure = pt.cd_pressure
        cd_friction = pt.cd_friction

        # Estimate induced drag
        cd_induced = pt.cl**2 / (math.pi * aspect_ratio * oswald_efficiency)

        # If SU2 didn't provide pressure/friction split, estimate
        if cd_pressure < 1e-12 and cd_friction < 1e-12 and cd_total > 1e-12:
            # Rough estimate: friction ≈ CD_min, pressure ≈ remainder
            cd_friction = min(cd_total, 0.005)  # Typical flat-plate skin friction
            cd_pressure = max(0.0, cd_total - cd_friction)

        pct_p = (cd_pressure / cd_total * 100) if cd_total > 1e-12 else 0.0
        pct_f = (cd_friction / cd_total * 100) if cd_total > 1e-12 else 0.0
        pct_i = (cd_induced / cd_total * 100) if cd_total > 1e-12 else 0.0

        breakdowns.append(DragBreakdown(
            alpha=pt.alpha,
            cd_total=round(cd_total, 6),
            cd_pressure=round(cd_pressure, 6),
            cd_friction=round(cd_friction, 6),
            cd_induced=round(cd_induced, 6),
            pct_pressure=round(pct_p, 1),
            pct_friction=round(pct_f, 1),
            pct_induced=round(pct_i, 1),
        ))

    return breakdowns


# ---------------------------------------------------------------------------
# Report extraction — the main entry point
# ---------------------------------------------------------------------------


def extract_alpha_result(
    alpha_dir: Path,
    alpha: float,
) -> AlphaResult:
    """Extract complete results for one alpha from its SU2 output directory.

    Expected directory structure:
        alpha_dir/
            history.csv          — convergence history
            surface_flow.csv     — surface Cp/Cf data
            forces_breakdown.dat — pressure/friction split (optional)
    """
    history = parse_history_csv(alpha_dir / "history.csv")
    surface = parse_surface_flow(alpha_dir / "surface_flow.csv")
    forces = parse_forces_breakdown(alpha_dir / "forces_breakdown.dat")

    # Final coefficients from last history entry
    cl = cd = cm = 0.0
    iterations = 0
    final_residual = 0.0
    converged = False

    if history:
        last = history[-1]
        cl = last.cl
        cd = last.cd
        cm = last.cm
        iterations = last.iteration
        final_residual = last.rms_density

        # Convergence check: residual below -6 orders of magnitude
        converged = final_residual < -6.0 if final_residual < 0 else False

    # Drag breakdown from forces file
    cd_pressure = forces.get("pressure_cd", forces.get("pressure_drag", 0.0))
    cd_friction = forces.get("friction_cd", forces.get("friction_drag", 0.0))
    cl_pressure = forces.get("pressure_cl", forces.get("pressure_lift", 0.0))
    cl_friction = forces.get("friction_cl", forces.get("friction_lift", 0.0))

    l_d = cl / cd if cd > 1e-12 else 0.0

    return AlphaResult(
        alpha=alpha,
        cl=round(cl, 6),
        cd=round(cd, 6),
        cm=round(cm, 6),
        l_d=round(l_d, 2),
        cd_pressure=round(cd_pressure, 6),
        cd_friction=round(cd_friction, 6),
        cl_pressure=round(cl_pressure, 6),
        cl_friction=round(cl_friction, 6),
        converged=converged,
        iterations=iterations,
        final_residual=round(final_residual, 4),
        surface_points=surface,
        convergence_history=history,
    )


def extract_full_report(
    output_dir: Path,
    component_name: str = "",
    project_name: str = "",
    config: Optional[CFDTestConfiguration] = None,
    aspect_ratio: float = 10.0,
    oswald_efficiency: float = 0.85,
) -> AeroTestReport:
    """Extract a complete AeroTestReport from an SU2 output directory.

    Scans for alpha_*.* subdirectories, extracts each, computes stability
    derivatives and drag breakdown, then assembles the full report.

    Args:
        output_dir: Root directory containing alpha_-5.0/, alpha_0.0/, etc.
        component_name: Name of the tested component/assembly.
        project_name: Project name for the report header.
        config: Test configuration (if known).
        aspect_ratio: Wing aspect ratio for induced drag estimation.
        oswald_efficiency: Oswald span efficiency factor.

    Returns:
        Complete AeroTestReport with all fields populated.

    Raises:
        FileNotFoundError: If output_dir doesn't exist.
        ValueError: If no alpha results found (hard stop).
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"CFD output directory not found: {output_dir}")

    # Discover alpha directories
    alpha_dirs: list[tuple[float, Path]] = []
    for child in sorted(output_dir.iterdir()):
        if child.is_dir() and child.name.startswith("alpha_"):
            try:
                alpha_val = float(child.name.replace("alpha_", ""))
                alpha_dirs.append((alpha_val, child))
            except ValueError:
                continue

    if not alpha_dirs:
        raise ValueError(
            f"No alpha directories found in {output_dir}. "
            f"Expected directories named alpha_-5.0, alpha_0.0, etc. "
            f"CFD validation cannot proceed without results — HARD STOP."
        )

    # Extract each alpha
    polar: list[AlphaResult] = []
    for alpha_val, alpha_path in alpha_dirs:
        result = extract_alpha_result(alpha_path, alpha_val)
        polar.append(result)

    # Sort by alpha
    polar.sort(key=lambda r: r.alpha)

    # Stability derivatives
    stability = compute_stability_derivatives(polar)

    # Drag breakdown
    drag = compute_drag_breakdown(polar, aspect_ratio, oswald_efficiency)

    # Convergence diagnostics
    all_converged = all(p.converged for p in polar)
    worst_residual = max(p.final_residual for p in polar) if polar else 0.0
    mean_iters = sum(p.iterations for p in polar) / len(polar) if polar else 0.0

    # Collect artifact paths
    artifacts: dict[str, str] = {}
    mesh_file = output_dir / "mesh.su2"
    if mesh_file.exists():
        artifacts["mesh"] = str(mesh_file)
    # Add first config found
    for _, alpha_path in alpha_dirs:
        cfg = alpha_path / "config.cfg"
        if cfg.exists():
            artifacts["config"] = str(cfg)
            break

    import time
    report = AeroTestReport(
        component_name=component_name,
        project_name=project_name,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        config=config or CFDTestConfiguration(),
        polar=polar,
        stability=stability,
        drag_breakdown=drag,
        all_converged=all_converged,
        worst_residual=worst_residual,
        mean_iterations=round(mean_iters, 1),
        artifacts=artifacts,
    )

    return report


# ---------------------------------------------------------------------------
# Required outputs validation (HARD STOP gate)
# ---------------------------------------------------------------------------

REQUIRED_REPORT_FIELDS = [
    "polar",            # Must have at least 1 alpha point
    "stability",        # Stability derivatives computed
    "drag_breakdown",   # Drag breakdown computed
    "all_converged",    # Convergence status known
]

REQUIRED_STABILITY_FIELDS = [
    "cl_alpha",
    "cl_max",
    "cd_min",
    "ld_max",
    "alpha_zero_lift",
]

REQUIRED_PER_ALPHA_FIELDS = [
    "alpha",
    "cl",
    "cd",
    "cm",
    "l_d",
]


def validate_report_completeness(report: AeroTestReport) -> list[str]:
    """Validate that all required outputs are present.

    Returns a list of missing/invalid fields. Empty list = pass.
    This is the hard-stop gate — if any field is missing, the validation
    step MUST NOT be marked as complete.
    """
    errors: list[str] = []

    # Must have polar data
    if not report.polar:
        errors.append("HARD STOP: No polar data — zero alpha results extracted")
        return errors  # No point checking further

    # Check each alpha result
    for pt in report.polar:
        for f in REQUIRED_PER_ALPHA_FIELDS:
            val = getattr(pt, f, None)
            if val is None:
                errors.append(f"Alpha {pt.alpha}: missing field '{f}'")

    # Check stability derivatives
    stab = report.stability
    for f in REQUIRED_STABILITY_FIELDS:
        val = getattr(stab, f, None)
        if val is None or (isinstance(val, float) and val == 0.0 and f != "alpha_zero_lift"):
            errors.append(f"Stability: '{f}' is zero or missing — check polar data quality")

    # Must have drag breakdown
    if not report.drag_breakdown:
        errors.append("HARD STOP: No drag breakdown computed")

    # Convergence — warn but don't hard-stop (diverged runs are informative)
    if not report.all_converged:
        diverged = [p.alpha for p in report.polar if not p.converged]
        errors.append(
            f"WARNING: {len(diverged)} alpha point(s) did not converge: {diverged}. "
            f"Results at these angles may be unreliable."
        )

    return errors


# ---------------------------------------------------------------------------
# Markdown report generation
# ---------------------------------------------------------------------------


def generate_markdown_report(report: AeroTestReport) -> str:
    """Generate industry-standard Aero Test Report in Markdown.

    This is the primary human-readable output of every CFD run.
    """
    lines: list[str] = []
    cfg = report.config
    stab = report.stability

    lines.append(f"# Aero Test Report: {report.component_name}")
    lines.append("")
    lines.append(f"**Project**: {report.project_name} | "
                 f"**Iteration**: {report.iteration} | "
                 f"**Round**: {report.round_label} | "
                 f"**Date**: {report.timestamp}")
    lines.append("")

    # 1. Test Configuration
    lines.append("## 1. Test Configuration")
    lines.append("")
    lines.append(f"| Parameter | Value |")
    lines.append(f"|-----------|-------|")
    lines.append(f"| Geometry | `{cfg.geometry_file}` |")
    lines.append(f"| Mesh | `{cfg.mesh_file}` ({cfg.mesh_cells:,} cells) |")
    lines.append(f"| Solver | {cfg.solver_type} {cfg.turbulence_model} |")
    lines.append(f"| Reynolds | {cfg.reynolds_number:,.0f} (ref length {cfg.reynolds_length_m:.3f} m) |")
    lines.append(f"| Freestream | V = {cfg.freestream_velocity_ms:.1f} m/s, T = {cfg.freestream_temperature_k:.1f} K |")
    lines.append(f"| Alpha range | {cfg.alpha_range[0]:.1f} to {cfg.alpha_range[1]:.1f} deg, step {cfg.alpha_step:.1f} |")
    lines.append(f"| Ref area | {cfg.reference_area_m2:.4f} m\u00b2 |")
    lines.append(f"| Symmetry plane | {'Yes' if cfg.symmetry_plane else 'No'} |")
    lines.append(f"| Wall clock | {cfg.wall_clock_seconds:.0f} s ({cfg.wall_clock_seconds/60:.1f} min) |")
    lines.append("")

    # 2. Polar Results Table
    lines.append("## 2. Polar Results")
    lines.append("")
    lines.append("| \u03b1 (deg) | CL | CD | CM | L/D | CD_press | CD_fric |")
    lines.append("|---------|------|--------|--------|------|----------|---------|")
    for pt in report.polar:
        conv = "" if pt.converged else " \u26a0"
        lines.append(
            f"| {pt.alpha:+6.1f} | {pt.cl:+.4f} | {pt.cd:.6f} | {pt.cm:+.4f} "
            f"| {pt.l_d:+7.2f} | {pt.cd_pressure:.6f} | {pt.cd_friction:.6f}{conv} |"
        )
    lines.append("")

    # 3. Key Aerodynamic Parameters
    lines.append("## 3. Key Aerodynamic Parameters")
    lines.append("")
    lines.append(f"| Parameter | Value |")
    lines.append(f"|-----------|-------|")
    lines.append(f"| CL\u03b1 | {stab.cl_alpha:.4f} /deg |")
    lines.append(f"| CL_max | {stab.cl_max:.4f} at \u03b1 = {stab.alpha_cl_max:.1f}\u00b0 |")
    lines.append(f"| CL at \u03b1=0 | {stab.cl_zero:.4f} |")
    lines.append(f"| Zero-lift \u03b1 | {stab.alpha_zero_lift:.1f}\u00b0 |")
    lines.append(f"| CD_min | {stab.cd_min:.6f} at \u03b1 = {stab.alpha_cd_min:.1f}\u00b0 |")
    lines.append(f"| L/D_max | {stab.ld_max:.2f} at \u03b1 = {stab.alpha_ld_max:.1f}\u00b0 (CL = {stab.cl_at_ld_max:.4f}) |")
    if stab.alpha_trim is not None:
        lines.append(f"| Trim \u03b1 (CM=0) | {stab.alpha_trim:.1f}\u00b0 |")
    if stab.neutral_point_pct_mac is not None:
        lines.append(f"| Neutral point | {stab.neutral_point_pct_mac:.1f}% MAC |")
    lines.append("")

    # 4. Drag Breakdown
    lines.append("## 4. Drag Breakdown")
    lines.append("")
    lines.append("| \u03b1 (deg) | CD_total | CD_press | CD_fric | CD_ind | %Press | %Fric | %Ind |")
    lines.append("|---------|----------|----------|---------|--------|--------|-------|------|")
    for db in report.drag_breakdown:
        lines.append(
            f"| {db.alpha:+6.1f} | {db.cd_total:.6f} | {db.cd_pressure:.6f} "
            f"| {db.cd_friction:.6f} | {db.cd_induced:.6f} "
            f"| {db.pct_pressure:.0f}% | {db.pct_friction:.0f}% | {db.pct_induced:.0f}% |"
        )
    lines.append("")

    # 5. Stability Assessment
    lines.append("## 5. Stability Assessment")
    lines.append("")
    if stab.cm_alpha is not None and stab.cm_alpha < 0:
        lines.append(f"**Statically stable** (CM\u03b1 = {stab.cm_alpha:.4f} /deg < 0)")
    elif stab.cm_alpha is not None:
        lines.append(f"**\u26a0 Statically UNSTABLE** (CM\u03b1 = {stab.cm_alpha:.4f} /deg \u2265 0)")
    lines.append("")

    # 6. Convergence Diagnostics
    lines.append("## 6. Convergence Diagnostics")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| All converged | {'Yes' if report.all_converged else '**NO**'} |")
    lines.append(f"| Worst residual | {report.worst_residual:.2f} |")
    lines.append(f"| Mean iterations | {report.mean_iterations:.0f} |")
    lines.append("")
    if not report.all_converged:
        diverged = [p for p in report.polar if not p.converged]
        lines.append("**Diverged points:**")
        for p in diverged:
            lines.append(f"- \u03b1 = {p.alpha:.1f}\u00b0: residual = {p.final_residual:.2f}, "
                         f"{p.iterations} iterations")
        lines.append("")

    # 7. Artifacts
    lines.append("## 7. Artifacts")
    lines.append("")
    for name, path in report.artifacts.items():
        lines.append(f"- **{name}**: `{path}`")
    lines.append("")

    return "\n".join(lines)


def write_report(
    report: AeroTestReport,
    output_dir: Path,
    basename: str = "AERO_TEST_REPORT",
) -> dict[str, Path]:
    """Write all report artifacts to the output directory.

    Generates:
    - {basename}.md  — Human-readable markdown report
    - {basename}.json — Machine-readable JSON for iteration feedback
    - polar_data.csv — Raw polar data for plotting

    Returns dict mapping artifact name to path.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    # Markdown report
    md_path = output_dir / f"{basename}.md"
    md_path.write_text(generate_markdown_report(report), encoding="utf-8")
    paths["markdown_report"] = md_path

    # JSON report
    json_path = output_dir / f"{basename}.json"
    report.to_json(json_path)
    paths["json_report"] = json_path

    # Polar CSV
    csv_path = output_dir / "polar_data.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "alpha_deg", "CL", "CD", "CM", "L_D",
            "CD_pressure", "CD_friction", "converged", "iterations",
        ])
        for pt in report.polar:
            writer.writerow([
                pt.alpha, pt.cl, pt.cd, pt.cm, pt.l_d,
                pt.cd_pressure, pt.cd_friction, pt.converged, pt.iterations,
            ])
    paths["polar_csv"] = csv_path

    # Surface Cp/Cf data per alpha (for heatmap rendering)
    for pt in report.polar:
        if pt.surface_points:
            surface_csv = output_dir / f"surface_alpha_{pt.alpha:.1f}.csv"
            with open(surface_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["x", "y", "z", "Cp", "Cf", "Cf_x", "Cf_y", "Cf_z", "pressure"])
                for sp in pt.surface_points:
                    writer.writerow([
                        sp.x, sp.y, sp.z, sp.cp, sp.cf,
                        sp.cf_x, sp.cf_y, sp.cf_z, sp.pressure,
                    ])
            paths[f"surface_alpha_{pt.alpha:.1f}"] = surface_csv

    logger.info("Wrote %d report artifacts to %s", len(paths), output_dir)
    return paths
