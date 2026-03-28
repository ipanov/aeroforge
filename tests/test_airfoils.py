"""Tests for airfoil generation."""

import pytest
import numpy as np
from src.cad.airfoils import (
    naca_4digit, naca_profile, get_airfoil, load_dat_airfoil,
    blend_airfoils, airfoil_at_station, resample_airfoil,
    scale_airfoil, max_thickness, AIRFOIL_DATABASE,
)


class TestNACA4Digit:
    """Tests for NACA 4-digit airfoil generation."""

    def test_symmetric_airfoil(self):
        """Test symmetric airfoil (00xx) has zero camber."""
        coords = naca_4digit(m=0, p=0, t=12, n_points=50)
        assert isinstance(coords, np.ndarray)
        # Find LE index
        le_idx = np.argmin(coords[:, 0])
        upper = coords[:le_idx + 1]
        lower = coords[le_idx:]

        # Upper and lower max y should be symmetric
        assert abs(upper[:, 1].max() + lower[:, 1].min()) < 0.001

    def test_thickness_scaling(self):
        """Test that thicker airfoils are actually thicker."""
        coords_12 = naca_4digit(m=0, p=0, t=12, n_points=50)
        coords_15 = naca_4digit(m=0, p=0, t=15, n_points=50)

        t12, _ = max_thickness(coords_12)
        t15, _ = max_thickness(coords_15)
        assert t15 > t12, "15% thick should be thicker than 12%"

    def test_point_count(self):
        """Test correct number of points generated."""
        for n in [25, 50, 100]:
            coords = naca_4digit(m=2, p=4, t=12, n_points=n)
            # Selig format: n+1 upper + n lower = 2n+1
            assert coords.shape[0] == 2 * n + 1
            assert coords.shape[1] == 2

    def test_trailing_edge_closed(self):
        """Test that trailing edge x is near 1.0."""
        coords = naca_4digit(m=2, p=4, t=12, n_points=50)
        assert abs(coords[0, 0] - 1.0) < 0.01
        assert abs(coords[-1, 0] - 1.0) < 0.01


class TestNACAProfile:
    """Tests for scaled NACA profile generation."""

    def test_chord_scaling(self):
        """Test that chord scaling works correctly."""
        coords = naca_profile("2412")
        max_x = coords[:, 0].max()
        assert abs(max_x - 1.0) < 0.01  # Normalized coordinates

    def test_invalid_code(self):
        """Test that invalid NACA codes raise error."""
        with pytest.raises(ValueError):
            naca_profile("12345")

    def test_closed_profile(self):
        """Test that profile is closed."""
        coords = naca_profile("2412")
        # First and last points at trailing edge
        assert abs(coords[0, 0] - coords[-1, 0]) < 0.01


class TestAGAirfoils:
    """Tests for real AG airfoil data."""

    def test_load_ag24(self):
        coords = load_dat_airfoil("AG24")
        assert coords.shape[0] > 100
        assert coords.shape[1] == 2
        t, _ = max_thickness(coords)
        assert 0.07 < t < 0.10  # ~8.4% thick

    def test_load_ag09(self):
        coords = load_dat_airfoil("AG09")
        assert coords.shape[0] > 100
        t, _ = max_thickness(coords)
        assert 0.04 < t < 0.07  # ~5.4% thick

    def test_load_ag03(self):
        coords = load_dat_airfoil("AG03")
        assert coords.shape[0] > 100
        t, _ = max_thickness(coords)
        assert 0.05 < t < 0.08  # ~6.4% thick

    def test_get_airfoil_by_name(self):
        for name in ["AG24", "AG09", "AG03"]:
            coords = get_airfoil(name)
            assert coords.shape[0] > 50

    def test_missing_airfoil_raises(self):
        with pytest.raises(FileNotFoundError):
            load_dat_airfoil("AG_NONEXISTENT")


class TestBlending:
    """Tests for airfoil blending."""

    def test_blend_endpoints(self):
        """blend_factor=0 gives airfoil A, =1 gives airfoil B."""
        a = get_airfoil("AG24")
        b = get_airfoil("AG03")
        blend_0 = blend_airfoils(a, b, 0.0, n_points=80)
        blend_1 = blend_airfoils(a, b, 1.0, n_points=80)
        a_r = resample_airfoil(a, 80)
        b_r = resample_airfoil(b, 80)
        assert np.allclose(blend_0, a_r, atol=1e-6)
        assert np.allclose(blend_1, b_r, atol=1e-6)

    def test_blend_midpoint(self):
        """50% blend should be between the two airfoils."""
        t_a, _ = max_thickness(get_airfoil("AG24"))
        t_b, _ = max_thickness(get_airfoil("AG03"))
        blended = blend_airfoils("AG24", "AG03", 0.5)
        t_blend, _ = max_thickness(blended)
        # Thickness should be between the two
        assert min(t_a, t_b) <= t_blend <= max(t_a, t_b) + 0.01

    def test_airfoil_at_station(self):
        """Test span-station blending."""
        root = airfoil_at_station(0.0)
        mid = airfoil_at_station(0.5)
        tip = airfoil_at_station(1.0)
        t_root, _ = max_thickness(root)
        t_mid, _ = max_thickness(mid)
        t_tip, _ = max_thickness(tip)
        # All should have reasonable thickness
        assert t_root > 0.03
        assert t_mid > 0.03
        assert t_tip > 0.03


class TestScaling:
    """Tests for airfoil scaling and twist."""

    def test_scale_chord(self):
        coords = get_airfoil("AG24")
        scaled = scale_airfoil(coords, chord=200.0)
        assert abs(scaled[:, 0].max() - 200.0) < 1.0
        assert scaled[:, 1].max() > 10.0  # Physical mm

    def test_twist_rotation(self):
        coords = get_airfoil("AG24")
        no_twist = scale_airfoil(coords, chord=200.0, twist_deg=0.0)
        twisted = scale_airfoil(coords, chord=200.0, twist_deg=-5.0)
        # Twisted should have different y values
        assert not np.allclose(no_twist[:, 1], twisted[:, 1])


class TestAirfoilDatabase:
    """Tests for airfoil database."""

    def test_database_not_empty(self):
        assert len(AIRFOIL_DATABASE) > 0

    def test_database_structure(self):
        for name, data in AIRFOIL_DATABASE.items():
            assert "thickness" in data, f"{name} missing thickness"
            assert "description" in data, f"{name} missing description"
