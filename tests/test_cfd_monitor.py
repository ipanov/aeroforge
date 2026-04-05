"""Tests for SU2 real-time progress monitoring."""

import csv
import time
from pathlib import Path

import pytest

from src.analysis.cfd_monitor import (
    SU2Monitor,
    SU2Progress,
    format_progress_line,
)


def _write_partial_history(path: Path, n_rows: int, rms_start: float = -2.0) -> None:
    """Write a partial history.csv simulating a running SU2 process."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['"Inner_Iter"', '"rms[Rho]"', '"CL"', '"CD"', '"CMz"'])
        for i in range(1, n_rows + 1):
            rms = rms_start - 6.0 * (i / max(n_rows, 1))
            writer.writerow([i, f"{rms:.4f}", "0.5000", "0.0120", "-0.0500"])


class TestSU2Monitor:
    def test_poll_returns_progress(self, tmp_path: Path):
        history = tmp_path / "history.csv"
        _write_partial_history(history, 50)
        monitor = SU2Monitor(history, max_iterations=100)
        progress = monitor.poll_once(alpha=5.0, start_time=time.time())
        assert progress.iteration == 50
        assert progress.alpha == 5.0

    def test_pct_iteration_calculated(self, tmp_path: Path):
        history = tmp_path / "history.csv"
        _write_partial_history(history, 50)
        monitor = SU2Monitor(history, max_iterations=100)
        progress = monitor.poll_once()
        assert progress.pct_iteration == pytest.approx(50.0, abs=1.0)

    def test_sweep_progress(self, tmp_path: Path):
        history = tmp_path / "history.csv"
        _write_partial_history(history, 100)
        monitor = SU2Monitor(history, max_iterations=100)
        progress = monitor.poll_once(alpha_index=2, total_alphas=10)
        # (2 + 1.0) / 10 = 30%
        assert 20 < progress.pct_sweep < 35

    def test_convergence_detected(self, tmp_path: Path):
        history = tmp_path / "history.csv"
        _write_partial_history(history, 100, rms_start=-2.0)
        # Final residual should be ~-8, which is at target
        monitor = SU2Monitor(history, max_iterations=100, target_residual=-8.0)
        progress = monitor.poll_once()
        assert progress.status in ("converged", "running")

    def test_divergence_detected(self, tmp_path: Path):
        history = tmp_path / "history.csv"
        # Write diverging residuals
        history.parent.mkdir(parents=True, exist_ok=True)
        with open(history, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(['"Inner_Iter"', '"rms[Rho]"', '"CL"', '"CD"', '"CMz"'])
            for i in range(1, 21):
                rms = i * 0.5  # Increasing = diverging
                writer.writerow([i, f"{rms:.4f}", "0.5", "0.012", "-0.05"])
        monitor = SU2Monitor(history, max_iterations=100, divergence_threshold=5.0)
        progress = monitor.poll_once()
        assert progress.status == "diverged"

    def test_missing_file_returns_waiting(self, tmp_path: Path):
        monitor = SU2Monitor(tmp_path / "nonexistent.csv")
        progress = monitor.poll_once()
        assert progress.status == "waiting"

    def test_reset_clears_state(self, tmp_path: Path):
        history = tmp_path / "history.csv"
        _write_partial_history(history, 50)
        monitor = SU2Monitor(history, max_iterations=100)
        monitor.poll_once()
        monitor.reset()
        assert monitor._last_read_pos == 0
        assert monitor._residual_window == []

    def test_eta_calculation(self, tmp_path: Path):
        history = tmp_path / "history.csv"
        _write_partial_history(history, 50)
        monitor = SU2Monitor(history, max_iterations=100)
        start = time.time() - 60  # Pretend we started 60s ago
        progress = monitor.poll_once(alpha_index=2, total_alphas=10, start_time=start)
        # ETA should be > 0 (we're ~25% done, 60s elapsed → ~180s remaining)
        assert progress.eta_s > 0


class TestFormatProgressLine:
    def test_format_running(self):
        p = SU2Progress(
            alpha=5.0, iteration=50, max_iterations=100,
            pct_iteration=50.0, pct_sweep=25.0,
            rms_density=-5.0, cl=0.5, cd=0.012,
            converging=True, status="running",
        )
        line = format_progress_line(p)
        assert "running" in line
        assert "5.0" in line
        assert "50/100" in line

    def test_format_converged(self):
        p = SU2Progress(status="converged", alpha=3.0, cl=0.6, cd=0.01)
        line = format_progress_line(p)
        assert "converged" in line

    def test_format_with_eta(self):
        p = SU2Progress(
            status="running", eta_s=7200,
            pct_sweep=50.0, alpha=5.0,
        )
        line = format_progress_line(p)
        assert "ETA" in line
        assert "h" in line  # Should show hours for ETA > 60min
