"""Tests for the AeroForge provider system.

Covers:
- ProviderRegistry CRUD and auto-selection
- Protocol compliance for all mock providers
- Hardware detection (mocked)
- System vs project provider hierarchy
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from src.providers.base import ProviderInfo, ProviderRegistry
from src.providers.hardware import HardwareProfile


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestProviderRegistry:
    """Tests for ProviderRegistry class operations."""

    def setup_method(self) -> None:
        ProviderRegistry.clear()

    def test_register_and_get(self) -> None:
        class DummyProtocol:
            pass

        class DummyProvider:
            provider_id = "test_dummy"

        provider = DummyProvider()
        ProviderRegistry.register(DummyProtocol, provider)

        result = ProviderRegistry.get(DummyProtocol, "test_dummy")
        assert result is provider

    def test_get_raises_key_error_for_unknown(self) -> None:
        class UnknownProtocol:
            pass

        with pytest.raises(KeyError):
            ProviderRegistry.get(UnknownProtocol, "nonexistent")

    def test_list_available(self) -> None:
        class Proto:
            pass

        class P1:
            provider_id = "p1"

        class P2:
            provider_id = "p2"

        ProviderRegistry.register(Proto, P1())
        ProviderRegistry.register(Proto, P2())

        available = ProviderRegistry.list_available(Proto)
        assert "p1" in available
        assert "p2" in available

    def test_register_without_provider_id_raises(self) -> None:
        class Proto:
            pass

        class BadProvider:
            pass

        with pytest.raises(ValueError, match="provider_id"):
            ProviderRegistry.register(Proto, BadProvider())

    def test_auto_select_prefers_gpu_when_available(self) -> None:
        class Proto:
            pass

        class CpuProvider:
            provider_id = "cpu"
            requires_gpu = False

        class GpuProvider:
            provider_id = "gpu"
            requires_gpu = True

        ProviderRegistry.register(Proto, CpuProvider())
        ProviderRegistry.register(Proto, GpuProvider())

        hw = HardwareProfile(cuda_available=True, gpu_name="RTX 3070")
        result = ProviderRegistry.auto_select(Proto, hw)
        assert result.provider_id == "gpu"

    def test_auto_select_skips_gpu_when_no_hardware(self) -> None:
        class Proto:
            pass

        class CpuProvider:
            provider_id = "cpu"
            requires_gpu = False

        class GpuProvider:
            provider_id = "gpu"
            requires_gpu = True

        ProviderRegistry.register(Proto, CpuProvider())
        ProviderRegistry.register(Proto, GpuProvider())

        hw = HardwareProfile(cuda_available=False)
        result = ProviderRegistry.auto_select(Proto, hw)
        assert result.provider_id == "cpu"

    def test_auto_select_prefers_non_mock(self) -> None:
        class Proto:
            pass

        class MockProvider:
            provider_id = "mock"

        class RealProvider:
            provider_id = "real_thing"

        ProviderRegistry.register(Proto, MockProvider())
        ProviderRegistry.register(Proto, RealProvider())

        result = ProviderRegistry.auto_select(Proto)
        assert result.provider_id == "real_thing"

    def test_resolve_from_config(self) -> None:
        class Proto:
            pass

        class P1:
            provider_id = "p1"

        class P2:
            provider_id = "p2"

        ProviderRegistry.register(Proto, P1())
        ProviderRegistry.register(Proto, P2())

        config = {"my_category": {"selected": "p2"}}
        result = ProviderRegistry.resolve_from_config(Proto, config, "my_category")
        assert result.provider_id == "p2"

    def test_resolve_from_config_falls_back_to_auto(self) -> None:
        class Proto:
            pass

        class P1:
            provider_id = "p1"

        ProviderRegistry.register(Proto, P1())

        config = {"my_category": {"selected": "nonexistent"}}
        result = ProviderRegistry.resolve_from_config(Proto, config, "my_category")
        assert result.provider_id == "p1"

    def test_clear(self) -> None:
        class Proto:
            pass

        class P1:
            provider_id = "p1"

        ProviderRegistry.register(Proto, P1())
        assert len(ProviderRegistry.list_available(Proto)) == 1

        ProviderRegistry.clear()
        assert len(ProviderRegistry.list_available(Proto)) == 0

    def test_list_info(self) -> None:
        class Proto:
            pass

        class P1:
            provider_id = "p1"

        info = ProviderInfo(
            provider_id="p1",
            display_name="Provider One",
            protocol_type=Proto,
            description="Test provider",
        )
        ProviderRegistry.register(Proto, P1(), info)

        infos = ProviderRegistry.list_info(Proto)
        assert len(infos) == 1
        assert infos[0].display_name == "Provider One"


# ---------------------------------------------------------------------------
# Mock CFD Provider tests
# ---------------------------------------------------------------------------


class TestMockCFDProvider:
    """Tests for MockCFDProvider protocol compliance and behavior."""

    def test_is_available(self) -> None:
        from src.providers.cfd.mock import MockCFDProvider
        provider = MockCFDProvider()
        assert provider.is_available() is True

    def test_mesh_geometry_creates_file(self, tmp_path: Path) -> None:
        from src.providers.cfd.mock import MockCFDProvider
        provider = MockCFDProvider()
        mesh = provider.mesh_geometry(
            Path("dummy.step"), tmp_path / "mesh_out",
        )
        assert mesh.exists()

    def test_run_polar_sweep_returns_results(self, tmp_path: Path) -> None:
        from src.providers.cfd.mock import MockCFDProvider
        from src.providers.cfd.protocol import PolarSweepConfig

        provider = MockCFDProvider()
        config = PolarSweepConfig(
            alpha_range=(-2.0, 10.0),
            alpha_step=2.0,
        )
        results = provider.run_polar_sweep(
            Path("dummy.step"), tmp_path / "results", config,
        )
        assert len(results) > 0
        # Check all results have required fields
        for r in results:
            assert hasattr(r, "alpha")
            assert hasattr(r, "cl")
            assert hasattr(r, "cd")
            assert hasattr(r, "cm")

    def test_polar_sweep_physics_sanity(self, tmp_path: Path) -> None:
        from src.providers.cfd.mock import MockCFDProvider
        from src.providers.cfd.protocol import PolarSweepConfig

        provider = MockCFDProvider()
        config = PolarSweepConfig(alpha_range=(0.0, 8.0), alpha_step=2.0)
        results = provider.run_polar_sweep(
            Path("dummy.step"), tmp_path / "out", config,
        )
        # CL should increase with alpha in the linear range
        cls = [r.cl for r in results]
        for i in range(1, len(cls)):
            assert cls[i] > cls[i - 1], f"CL should increase: {cls}"

        # CD should always be positive
        for r in results:
            assert r.cd > 0

    def test_protocol_compliance(self) -> None:
        from src.providers.cfd.mock import MockCFDProvider
        from src.providers.cfd.protocol import CFDProvider

        provider = MockCFDProvider()
        assert isinstance(provider, CFDProvider)


# ---------------------------------------------------------------------------
# Mock FEA Provider tests
# ---------------------------------------------------------------------------


class TestMockFEAProvider:
    """Tests for MockFEAProvider protocol compliance and behavior."""

    def test_is_available(self) -> None:
        from src.providers.fea.mock import MockFEAProvider
        provider = MockFEAProvider()
        assert provider.is_available() is True

    def test_run_static(self, tmp_path: Path) -> None:
        from src.providers.fea.mock import MockFEAProvider
        from src.providers.fea.protocol import LoadCase

        provider = MockFEAProvider()
        load_cases = [
            LoadCase(name="cruise", load_factor_g=1.0),
            LoadCase(name="pullout", load_factor_g=5.0),
        ]
        results = provider.run_static(
            Path("dummy.step"), load_cases, tmp_path / "fea_out",
        )
        assert len(results) == 2
        # Higher load factor should produce higher stress
        assert results[1].max_von_mises_mpa > results[0].max_von_mises_mpa

    def test_run_modal(self, tmp_path: Path) -> None:
        from src.providers.fea.mock import MockFEAProvider
        provider = MockFEAProvider()
        result = provider.run_modal(Path("dummy.step"), 5, tmp_path / "modal")
        assert len(result.frequencies_hz) == 5
        # Frequencies should be increasing
        for i in range(1, len(result.frequencies_hz)):
            assert result.frequencies_hz[i] > result.frequencies_hz[i - 1]

    def test_run_buckling(self, tmp_path: Path) -> None:
        from src.providers.fea.mock import MockFEAProvider
        from src.providers.fea.protocol import LoadCase
        provider = MockFEAProvider()
        lc = LoadCase(name="test", load_factor_g=3.0)
        result = provider.run_buckling(Path("dummy.step"), lc, tmp_path / "buck")
        assert result.buckling_factor > 0

    def test_protocol_compliance(self) -> None:
        from src.providers.fea.mock import MockFEAProvider
        from src.providers.fea.protocol import FEAProvider
        assert isinstance(MockFEAProvider(), FEAProvider)


# ---------------------------------------------------------------------------
# Mock Manufacturing Provider tests
# ---------------------------------------------------------------------------


class TestMockManufacturingProvider:

    def test_validate_geometry(self, tmp_path: Path) -> None:
        from src.providers.manufacturing.mock import MockManufacturingProvider
        provider = MockManufacturingProvider()
        result = provider.validate_geometry(Path("dummy.step"), {})
        assert result.valid is True

    def test_generate_output(self, tmp_path: Path) -> None:
        from src.providers.manufacturing.mock import MockManufacturingProvider
        provider = MockManufacturingProvider()
        out = provider.generate_output(Path("dummy.step"), tmp_path / "mfg")
        assert out.exists()

    def test_protocol_compliance(self) -> None:
        from src.providers.manufacturing.mock import MockManufacturingProvider
        from src.providers.manufacturing.protocol import ManufacturingProvider
        assert isinstance(MockManufacturingProvider(), ManufacturingProvider)


# ---------------------------------------------------------------------------
# Mock Slicer Provider tests
# ---------------------------------------------------------------------------


class TestMockSlicerProvider:

    def test_slice(self, tmp_path: Path) -> None:
        from src.providers.slicer.mock import MockSlicerProvider
        provider = MockSlicerProvider()
        result = provider.slice(Path("dummy.3mf"), tmp_path / "sliced", {})
        assert result.output_file.exists()
        assert result.estimated_time_hours > 0

    def test_protocol_compliance(self) -> None:
        from src.providers.slicer.mock import MockSlicerProvider
        from src.providers.slicer.protocol import SlicerProvider
        assert isinstance(MockSlicerProvider(), SlicerProvider)


# ---------------------------------------------------------------------------
# Mock Airfoil Provider tests
# ---------------------------------------------------------------------------


class TestMockAirfoilProvider:

    def test_get_polar(self) -> None:
        from src.providers.airfoil.mock import MockAirfoilProvider
        provider = MockAirfoilProvider()
        result = provider.get_polar("naca0012", 5.0, 100000)
        assert result.cl > 0
        assert result.cd > 0

    def test_analyze_returns_sweep(self) -> None:
        from src.providers.airfoil.mock import MockAirfoilProvider
        provider = MockAirfoilProvider()
        results = provider.analyze("ag24", (-5.0, 10.0), 1.0, 80000)
        assert len(results) == 16  # -5 to 10 inclusive

    def test_protocol_compliance(self) -> None:
        from src.providers.airfoil.mock import MockAirfoilProvider
        from src.providers.airfoil.protocol import AirfoilProvider
        assert isinstance(MockAirfoilProvider(), AirfoilProvider)


# ---------------------------------------------------------------------------
# FDM Provider tests
# ---------------------------------------------------------------------------


class TestFDMProvider:

    def test_validate_geometry_missing_file(self, tmp_path: Path) -> None:
        from src.providers.manufacturing.fdm import FDMProvider
        provider = FDMProvider()
        result = provider.validate_geometry(
            tmp_path / "nonexistent.step", {},
        )
        assert result.valid is False
        assert any("not found" in i for i in result.issues)

    def test_estimate_cost(self, tmp_path: Path) -> None:
        from src.providers.manufacturing.fdm import FDMProvider
        provider = FDMProvider()
        cost = provider.estimate_cost(Path("dummy.step"))
        assert cost.material_cost >= 0


# ---------------------------------------------------------------------------
# Manual Provider tests
# ---------------------------------------------------------------------------


class TestManualProvider:

    def test_generate_output_creates_instructions(self, tmp_path: Path) -> None:
        from src.providers.manufacturing.manual import ManualProvider
        provider = ManualProvider()
        out = provider.generate_output(Path("dummy.step"), tmp_path / "manual")
        assert out.exists()
        content = out.read_text()
        assert "Manual Manufacturing" in content

    def test_always_available(self) -> None:
        from src.providers.manufacturing.manual import ManualProvider
        assert ManualProvider().is_available() is True


# ---------------------------------------------------------------------------
# Hardware detection tests (mocked)
# ---------------------------------------------------------------------------


class TestHardwareProfile:

    def test_summary_no_gpu(self) -> None:
        hw = HardwareProfile(os_platform="win32")
        summary = hw.summary()
        assert "None detected" in summary

    def test_summary_with_gpu(self) -> None:
        hw = HardwareProfile(
            os_platform="win32",
            gpu_type="nvidia_cuda",
            gpu_name="RTX 3070",
            gpu_vram_mb=8192,
            cuda_available=True,
            installed_software={"su2": "8.1.0", "freecad": "1.0"},
        )
        summary = hw.summary()
        assert "RTX 3070" in summary
        assert "su2" in summary
