"""Tests for wing section generation."""

import pytest
from src.cad.wing import WingSection, WingSectionSpec


class TestWingSectionSpec:
    """Tests for wing specification validation."""

    def test_valid_spec(self):
        """Test that valid spec creates without error."""
        spec = WingSectionSpec()
        wing = WingSection(spec)
        assert wing.spec.root_chord == 200.0

    def test_negative_chord_raises(self):
        """Test that negative chord raises error."""
        spec = WingSectionSpec(root_chord=-100)
        with pytest.raises(ValueError):
            WingSection(spec)

    def test_negative_span_raises(self):
        """Test that negative span raises error."""
        spec = WingSectionSpec(span=-100)
        with pytest.raises(ValueError):
            WingSection(spec)


class TestWingSection:
    """Tests for wing section calculations."""

    @pytest.fixture
    def wing(self):
        """Create a standard wing section for testing."""
        spec = WingSectionSpec(
            root_chord=200.0,
            tip_chord=100.0,
            span=500.0,
        )
        return WingSection(spec)

    def test_chord_at_root(self, wing):
        """Test chord at root equals root chord."""
        chord = wing.chord_at_position(0)
        assert chord == 200.0

    def test_chord_at_tip(self, wing):
        """Test chord at tip equals tip chord."""
        chord = wing.chord_at_position(500.0)
        assert chord == 100.0

    def test_chord_linear_distribution(self, wing):
        """Test chord varies linearly."""
        chord_250 = wing.chord_at_position(250.0)
        # Should be halfway between 200 and 100
        assert abs(chord_250 - 150.0) < 0.1

    def test_rib_count(self, wing):
        """Test correct number of rib positions."""
        positions = wing.rib_positions()
        assert len(positions) == wing.spec.rib_count

    def test_rib_positions_span_range(self, wing):
        """Test rib positions cover full span."""
        positions = wing.rib_positions()
        assert positions[0] == 0.0
        assert abs(positions[-1] - wing.spec.span) < 0.1

    def test_aspect_ratio(self, wing):
        """Test aspect ratio calculation."""
        # AR = (2 * span) / avg_chord = 1000 / 150 = 6.67
        expected_ar = (2 * 500.0) / 150.0
        assert abs(wing.aspect_ratio - expected_ar) < 0.1

    def test_taper_ratio(self, wing):
        """Test taper ratio calculation."""
        # Taper = tip/root = 100/200 = 0.5
        assert wing.taper_ratio == 0.5

    def test_twist_distribution(self, wing):
        """Test twist varies from root to tip."""
        wing.spec.twist = -3.0  # 3° washout

        twist_root = wing.twist_at_position(0)
        twist_tip = wing.twist_at_position(wing.spec.span)

        assert twist_root == 0.0
        assert twist_tip == -3.0

    def test_all_ribs_generated(self, wing):
        """Test that all ribs are generated."""
        ribs = wing.generate_all_ribs()
        assert len(ribs) == wing.spec.rib_count

        # Each rib should have required fields
        for rib in ribs:
            assert "chord" in rib
            assert "twist" in rib
            assert "position" in rib
