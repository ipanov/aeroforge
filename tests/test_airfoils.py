"""Tests for airfoil generation."""

import pytest
import math
from src.cad.airfoils import naca_4digit, naca_profile, AIRFOIL_DATABASE


class TestNACA4Digit:
    """Tests for NACA 4-digit airfoil generation."""

    def test_symmetric_airfoil(self):
        """Test symmetric airfoil (00xx) has zero camber."""
        upper, lower = naca_4digit(m=0, p=0, t=12, n_points=50)

        # Upper and lower should be symmetric
        for i, ((xu, yu), (xl, yl)) in enumerate(zip(upper, lower)):
            assert abs(xu - xl) < 0.001, f"X mismatch at point {i}"
            assert abs(yu + yl) < 0.001, f"Y not symmetric at point {i}"

    def test_thickness_scaling(self):
        """Test that thicker airfoils are actually thicker."""
        upper_12, _ = naca_4digit(m=0, p=0, t=12, n_points=50)
        upper_15, _ = naca_4digit(m=0, p=0, t=15, n_points=50)

        # Max thickness should scale
        max_y_12 = max(y for _, y in upper_12)
        max_y_15 = max(y for _, y in upper_15)

        assert max_y_15 > max_y_12, "15% thick should be thicker than 12%"

    def test_point_count(self):
        """Test correct number of points generated."""
        for n in [25, 50, 100]:
            upper, lower = naca_4digit(m=2, p=4, t=12, n_points=n)
            assert len(upper) == n + 1, f"Upper surface should have {n+1} points"
            assert len(lower) == n + 1, f"Lower surface should have {n+1} points"

    def test_trailing_edge_closed(self):
        """Test that trailing edge is at (1, 0)."""
        upper, lower = naca_4digit(m=2, p=4, t=12, n_points=50)

        # Trailing edge should be close to (1, 0)
        assert abs(upper[-1][0] - 1.0) < 0.001
        assert abs(lower[-1][0] - 1.0) < 0.001


class TestNACAProfile:
    """Tests for scaled NACA profile generation."""

    def test_chord_scaling(self):
        """Test that chord scaling works correctly."""
        profile_100 = naca_profile("2412", chord=100.0)
        profile_200 = naca_profile("2412", chord=200.0)

        # Max x should be chord length
        max_x_100 = max(x for x, _ in profile_100)
        max_x_200 = max(x for x, _ in profile_200)

        assert abs(max_x_100 - 100.0) < 0.1
        assert abs(max_x_200 - 200.0) < 0.1

    def test_invalid_code(self):
        """Test that invalid NACA codes raise error."""
        with pytest.raises(ValueError):
            naca_profile("12345")  # Too many digits

        with pytest.raises(ValueError):
            naca_profile("abc")  # Not digits

    def test_closed_profile(self):
        """Test that profile is closed (first and last points connect)."""
        profile = naca_profile("2412", chord=100.0)

        first = profile[0]
        last = profile[-1]

        # Should be at same position (trailing edge)
        assert abs(first[0] - last[0]) < 0.1
        assert abs(first[1] - last[1]) < 0.1


class TestAirfoilDatabase:
    """Tests for airfoil database."""

    def test_database_not_empty(self):
        """Test that database has airfoils."""
        assert len(AIRFOIL_DATABASE) > 0

    def test_database_structure(self):
        """Test that database entries have required fields."""
        for name, data in AIRFOIL_DATABASE.items():
            assert "thickness" in data, f"{name} missing thickness"
            assert "camber" in data, f"{name} missing camber"
            assert "description" in data, f"{name} missing description"
