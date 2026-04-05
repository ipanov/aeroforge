"""Real-time SU2 process monitor with convergence polling.

Replaces the fire-and-forget subprocess.run() with a monitored execution
that polls the SU2 history.csv during the run to track:
- Residual convergence (are we getting closer to the target?)
- Aerodynamic coefficients at each iteration (CL, CD, CM evolution)
- ETA based on convergence rate
- Early divergence detection (hard stop if residuals blow up)

Progress is reported through a callback function that the workflow engine
uses to update the n8n visual dashboard and HTML dashboard.
"""

from __future__ import annotations

import csv
import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class SU2Progress:
    """Snapshot of SU2 solver progress at a point in time."""

    # Run identification
    alpha: float = 0.0
    alpha_index: int = 0        # Which alpha in the sweep (0-based)
    total_alphas: int = 1       # Total alpha points in sweep

    # Per-alpha progress
    iteration: int = 0
    max_iterations: int = 1000
    pct_iteration: float = 0.0  # iteration / max_iterations * 100

    # Overall sweep progress
    pct_sweep: float = 0.0     # (alpha_index + pct_iteration/100) / total_alphas * 100

    # Convergence
    rms_density: float = 0.0
    target_residual: float = -8.0
    converging: bool = True     # Residuals trending down?

    # Current coefficients
    cl: float = 0.0
    cd: float = 0.0
    cm: float = 0.0

    # Timing
    elapsed_s: float = 0.0
    eta_s: float = 0.0          # Estimated seconds remaining

    # Status
    status: str = "running"     # running, converged, diverged, failed, complete


ProgressCallback = Callable[[SU2Progress], None]


# ---------------------------------------------------------------------------
# Monitor
# ---------------------------------------------------------------------------


class SU2Monitor:
    """Monitors a running SU2 process by polling its history.csv output."""

    def __init__(
        self,
        history_path: Path,
        max_iterations: int = 1000,
        target_residual: float = -8.0,
        poll_interval_s: float = 5.0,
        divergence_threshold: float = 5.0,
        callback: Optional[ProgressCallback] = None,
    ) -> None:
        self._history_path = Path(history_path)
        self._max_iters = max_iterations
        self._target_residual = target_residual
        self._poll_interval = poll_interval_s
        self._divergence_threshold = divergence_threshold
        self._callback = callback
        self._stop_event = threading.Event()
        self._last_read_pos = 0
        self._residual_window: list[float] = []

    def poll_once(self, alpha: float = 0.0, alpha_index: int = 0, total_alphas: int = 1,
                  start_time: float = 0.0) -> SU2Progress:
        """Read the latest state from history.csv and return a progress snapshot."""
        progress = SU2Progress(
            alpha=alpha,
            alpha_index=alpha_index,
            total_alphas=total_alphas,
            max_iterations=self._max_iters,
            target_residual=self._target_residual,
        )

        if not self._history_path.exists():
            progress.status = "waiting"
            return progress

        try:
            rows = self._read_new_rows()
        except Exception as exc:
            logger.debug("Failed to read history: %s", exc)
            progress.status = "running"
            return progress

        if not rows:
            progress.status = "running"
            return progress

        last = rows[-1]
        progress.iteration = last.get("iteration", 0)
        progress.rms_density = last.get("rms_density", 0.0)
        progress.cl = last.get("cl", 0.0)
        progress.cd = last.get("cd", 0.0)
        progress.cm = last.get("cm", 0.0)

        # Iteration progress
        progress.pct_iteration = min(
            progress.iteration / self._max_iters * 100, 100.0
        ) if self._max_iters > 0 else 0.0

        # Sweep progress
        alpha_frac = (alpha_index + progress.pct_iteration / 100) / total_alphas
        progress.pct_sweep = round(alpha_frac * 100, 1) if total_alphas > 0 else 0.0

        # Convergence check — add all new rows to the residual window
        for row in rows:
            rms = row.get("rms_density", 0.0)
            if rms != 0.0:
                self._residual_window.append(rms)
        if len(self._residual_window) > 50:
            self._residual_window = self._residual_window[-50:]

        if progress.rms_density <= self._target_residual:
            progress.status = "converged"
            progress.converging = True
        elif len(self._residual_window) >= 5:
            trend = self._residual_window[-1] - self._residual_window[-5]
            progress.converging = trend < 0
            if progress.rms_density > self._divergence_threshold:
                progress.status = "diverged"
            else:
                progress.status = "running"
        else:
            progress.status = "running"

        # Timing
        progress.elapsed_s = time.time() - start_time if start_time > 0 else 0.0
        if progress.pct_sweep > 1.0 and progress.elapsed_s > 0:
            total_estimated = progress.elapsed_s / (progress.pct_sweep / 100)
            progress.eta_s = max(0, total_estimated - progress.elapsed_s)

        return progress

    def _read_new_rows(self) -> list[dict[str, Any]]:
        """Read new rows from history.csv since last read."""
        rows: list[dict[str, Any]] = []

        with open(self._history_path, "r", encoding="utf-8") as f:
            f.seek(self._last_read_pos)
            content = f.read()
            self._last_read_pos = f.tell()

        if not content.strip():
            return rows

        # If this is the first read, parse the full file
        if self._last_read_pos == len(content):
            self._last_read_pos = 0
            with open(self._history_path, "r", encoding="utf-8") as f:
                content = f.read()
                self._last_read_pos = f.tell()

        lines = content.strip().split("\n")
        if not lines:
            return rows

        # Parse header if present
        header: Optional[list[str]] = None
        for line in lines:
            cells = [c.strip().strip('"').strip().lower() for c in line.split(",")]
            if any(c in cells for c in ("inner_iter", "iter", "iteration", "outer_iter")):
                header = cells
                continue
            if header is None:
                continue

            row: dict[str, Any] = {}
            vals = line.split(",")
            for i, h in enumerate(header):
                if i < len(vals):
                    try:
                        row[h] = float(vals[i].strip())
                    except ValueError:
                        row[h] = vals[i].strip()

            # Normalize keys
            parsed: dict[str, Any] = {}
            for key in ("inner_iter", "iter", "iteration", "outer_iter"):
                if key in row:
                    parsed["iteration"] = int(row[key])
                    break
            for key in ("rms[rho]", "rms[p]", "rms_rho", "res[rho]"):
                if key in row:
                    parsed["rms_density"] = row[key]
                    break
            for key in ("cl", "lift"):
                if key in row:
                    parsed["cl"] = row[key]
                    break
            for key in ("cd", "drag"):
                if key in row:
                    parsed["cd"] = row[key]
                    break
            for key in ("cmz", "cm", "moment_z"):
                if key in row:
                    parsed["cm"] = row[key]
                    break

            if "iteration" in parsed:
                rows.append(parsed)

        return rows

    def reset(self) -> None:
        """Reset monitor state for next alpha point."""
        self._last_read_pos = 0
        self._residual_window = []


# ---------------------------------------------------------------------------
# Monitored SU2 execution
# ---------------------------------------------------------------------------


def run_su2_monitored(
    config_file: Path,
    history_file: Path,
    su2_executable: str = "SU2_CFD",
    timeout: int = 3600,
    max_iterations: int = 1000,
    target_residual: float = -8.0,
    poll_interval_s: float = 5.0,
    alpha: float = 0.0,
    alpha_index: int = 0,
    total_alphas: int = 1,
    callback: Optional[ProgressCallback] = None,
) -> dict[str, Any]:
    """Run SU2 with real-time progress monitoring.

    Launches SU2 as a subprocess and polls history.csv in a background thread,
    reporting progress through the callback.

    Returns:
        Dict with returncode, converged, final_progress, wall_time_s.
    """
    config_file = Path(config_file)
    history_file = Path(history_file)
    start_time = time.time()

    monitor = SU2Monitor(
        history_path=history_file,
        max_iterations=max_iterations,
        target_residual=target_residual,
        poll_interval_s=poll_interval_s,
        callback=callback,
    )

    # Launch SU2
    process = subprocess.Popen(
        [su2_executable, str(config_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(config_file.parent),
    )

    # Polling loop
    final_progress = SU2Progress(status="running")
    try:
        while process.poll() is None:
            progress = monitor.poll_once(
                alpha=alpha,
                alpha_index=alpha_index,
                total_alphas=total_alphas,
                start_time=start_time,
            )
            final_progress = progress

            if callback:
                callback(progress)

            if progress.status == "diverged":
                logger.warning("SU2 diverged at alpha=%.1f — killing process", alpha)
                process.kill()
                break

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                logger.warning("SU2 timed out after %.0fs at alpha=%.1f", elapsed, alpha)
                process.kill()
                final_progress.status = "failed"
                break

            time.sleep(poll_interval_s)

    except KeyboardInterrupt:
        process.kill()
        final_progress.status = "failed"

    # Read remaining output
    stdout, stderr = process.communicate(timeout=10)
    wall_time = time.time() - start_time

    # Final poll
    final_progress = monitor.poll_once(
        alpha=alpha, alpha_index=alpha_index,
        total_alphas=total_alphas, start_time=start_time,
    )
    final_progress.elapsed_s = wall_time

    if process.returncode != 0 and final_progress.status not in ("diverged", "failed"):
        final_progress.status = "failed"
    elif final_progress.status == "running":
        final_progress.status = "complete"

    # Report final state
    if callback:
        callback(final_progress)

    return {
        "returncode": process.returncode,
        "converged": final_progress.status == "converged",
        "final_progress": final_progress,
        "wall_time_s": round(wall_time, 1),
        "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
        "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
    }


def format_progress_line(progress: SU2Progress) -> str:
    """Format a human-readable progress line for logging/display."""
    eta_str = ""
    if progress.eta_s > 0:
        eta_min = progress.eta_s / 60
        if eta_min > 60:
            eta_str = f" | ETA: {eta_min/60:.1f}h"
        else:
            eta_str = f" | ETA: {eta_min:.0f}min"

    converging = "\u2193" if progress.converging else "\u2191"  # ↓ or ↑

    return (
        f"[{progress.status:>9s}] "
        f"\u03b1={progress.alpha:+5.1f}\u00b0 "
        f"iter {progress.iteration}/{progress.max_iterations} "
        f"({progress.pct_iteration:.0f}%) "
        f"| sweep {progress.pct_sweep:.0f}% "
        f"| res={progress.rms_density:.2f}{converging} "
        f"| CL={progress.cl:+.4f} CD={progress.cd:.6f}"
        f"{eta_str}"
    )
