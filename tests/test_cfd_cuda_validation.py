"""Tests for SU2 CUDA provider validation.

Covers:
- CUDA detection in SU2 binary
- CPU time estimation
- Provider availability with/without CUDA
- GPU accessibility checks
"""

from __future__ import annotations

from unittest.mock import patch, MagicMock
import subprocess

import pytest

from src.providers.cfd.su2_cuda import (
    SU2CudaProvider,
    _check_cuda_in_binary,
    estimate_cpu_time,
)


# ---------------------------------------------------------------------------
# Unit tests — no hardware required
# ---------------------------------------------------------------------------


class TestCudaDetection:
    """Tests for _check_cuda_in_binary()."""

    def test_detects_cuda_in_su2_output(self) -> None:
        mock_su2 = MagicMock()
        mock_su2.stdout = "SU2 v8.4.0 Harrier\nCompiled with CUDA support\n"
        mock_su2.stderr = ""

        mock_nvsmi = MagicMock()
        mock_nvsmi.returncode = 0
        mock_nvsmi.stdout = "NVIDIA GeForce RTX 3070\n"

        with patch("shutil.which", return_value="/usr/bin/SU2_CFD"), \
             patch("subprocess.run", side_effect=[mock_su2, mock_nvsmi]):
            assert _check_cuda_in_binary() is True

    def test_detects_gpu_keyword_in_su2_output(self) -> None:
        mock_su2 = MagicMock()
        mock_su2.stdout = "SU2 v8.4.0\n  GPU acceleration enabled\n"
        mock_su2.stderr = ""

        mock_nvsmi = MagicMock()
        mock_nvsmi.returncode = 0
        mock_nvsmi.stdout = "RTX 3070\n"

        with patch("shutil.which", return_value="/usr/bin/SU2_CFD"), \
             patch("subprocess.run", side_effect=[mock_su2, mock_nvsmi]):
            assert _check_cuda_in_binary() is True

    def test_rejects_cpu_only_binary(self) -> None:
        mock_su2 = MagicMock()
        mock_su2.stdout = "SU2 v8.4.0 Harrier\nOptions: MPI, OpenMP\n"
        mock_su2.stderr = ""

        mock_nvsmi = MagicMock()
        mock_nvsmi.returncode = 0
        mock_nvsmi.stdout = "RTX 3070\n"

        with patch("shutil.which", return_value="/usr/bin/SU2_CFD"), \
             patch("subprocess.run", side_effect=[mock_su2, mock_nvsmi]):
            assert _check_cuda_in_binary() is False

    def test_rejects_when_no_gpu_available(self) -> None:
        mock_su2 = MagicMock()
        mock_su2.stdout = "SU2 with CUDA\n"
        mock_su2.stderr = ""

        mock_nvsmi = MagicMock()
        mock_nvsmi.returncode = 1
        mock_nvsmi.stdout = ""

        with patch("shutil.which", return_value="/usr/bin/SU2_CFD"), \
             patch("subprocess.run", side_effect=[mock_su2, mock_nvsmi]):
            assert _check_cuda_in_binary() is False

    def test_rejects_when_su2_not_found(self) -> None:
        with patch("shutil.which", return_value=None):
            assert _check_cuda_in_binary() is False

    def test_handles_su2_timeout(self) -> None:
        with patch("shutil.which", return_value="/usr/bin/SU2_CFD"), \
             patch("subprocess.run", side_effect=subprocess.TimeoutExpired("SU2_CFD", 10)):
            assert _check_cuda_in_binary() is False

    def test_handles_nvidia_smi_not_found(self) -> None:
        mock_su2 = MagicMock()
        mock_su2.stdout = "CUDA enabled\n"
        mock_su2.stderr = ""

        with patch("shutil.which", return_value="/usr/bin/SU2_CFD"), \
             patch("subprocess.run", side_effect=[mock_su2, FileNotFoundError]):
            assert _check_cuda_in_binary() is False


class TestCpuTimeEstimate:
    """Tests for estimate_cpu_time()."""

    def test_basic_estimate(self) -> None:
        # 50k elements, 7 alphas, 300 iters
        est = estimate_cpu_time(50_000, 7, 300)
        assert est > 0
        # ~525 seconds = ~8.75 minutes
        assert 400 < est < 700

    def test_scales_with_elements(self) -> None:
        est_small = estimate_cpu_time(10_000, 1)
        est_large = estimate_cpu_time(100_000, 1)
        assert est_large == pytest.approx(est_small * 10, rel=0.01)

    def test_scales_with_alphas(self) -> None:
        est_1 = estimate_cpu_time(50_000, 1)
        est_7 = estimate_cpu_time(50_000, 7)
        assert est_7 == pytest.approx(est_1 * 7, rel=0.01)

    def test_zero_elements_returns_zero(self) -> None:
        assert estimate_cpu_time(0, 7) == 0.0


class TestSU2CudaProviderAvailability:
    """Tests for SU2CudaProvider.is_available() and validate_or_raise()."""

    def test_available_with_cuda(self) -> None:
        provider = SU2CudaProvider()
        with patch("shutil.which", return_value="/usr/bin/SU2_CFD"), \
             patch(
                 "src.providers.cfd.su2_cuda._check_cuda_in_binary",
                 return_value=True,
             ):
            provider._cuda_checked = False
            assert provider.is_available() is True

    def test_not_available_without_cuda(self) -> None:
        provider = SU2CudaProvider()
        with patch("shutil.which", return_value="/usr/bin/SU2_CFD"), \
             patch(
                 "src.providers.cfd.su2_cuda._check_cuda_in_binary",
                 return_value=False,
             ):
            provider._cuda_checked = False
            assert provider.is_available() is False

    def test_not_available_without_su2(self) -> None:
        provider = SU2CudaProvider()
        with patch("shutil.which", return_value=None):
            provider._cuda_checked = False
            assert provider.is_available() is False

    def test_validate_passes_with_cuda(self) -> None:
        provider = SU2CudaProvider()
        provider._cuda_checked = True
        provider._cuda_available = True
        provider.validate_or_raise()  # should not raise

    def test_validate_raises_without_cuda(self) -> None:
        provider = SU2CudaProvider()
        provider._cuda_checked = True
        provider._cuda_available = False
        with pytest.raises(RuntimeError, match="CUDA GPU acceleration is NOT available"):
            provider.validate_or_raise(mesh_elements=50_000, n_alphas=7)

    def test_validate_error_includes_time_estimate(self) -> None:
        provider = SU2CudaProvider()
        provider._cuda_checked = True
        provider._cuda_available = False
        with pytest.raises(RuntimeError, match="minutes"):
            provider.validate_or_raise(mesh_elements=50_000, n_alphas=7)

    def test_validate_error_suggests_fix(self) -> None:
        provider = SU2CudaProvider()
        provider._cuda_checked = True
        provider._cuda_available = False
        with pytest.raises(RuntimeError, match="rebuild SU2"):
            provider.validate_or_raise()


# ---------------------------------------------------------------------------
# Integration test — requires actual hardware
# ---------------------------------------------------------------------------


@pytest.mark.hardware
class TestSU2CudaReal:
    """Integration tests that run the actual SU2 binary."""

    def test_su2_binary_exists(self) -> None:
        import shutil
        path = shutil.which("SU2_CFD")
        assert path is not None, "SU2_CFD not found in PATH"

    def test_su2_has_cuda_support(self) -> None:
        assert _check_cuda_in_binary(), (
            "SU2_CFD binary does not have CUDA support. "
            "Rebuild with: meson setup build -Denable-cuda=true && ninja -C build"
        )
