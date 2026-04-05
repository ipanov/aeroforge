"""
Drawing Orientation Tests
=========================
Tests for the generic coordinate-transform module used by all drawings.
Enforces:
  1. Left half extends LEFT, right half extends RIGHT
  2. LE is forward (top), TE is aft (bottom)
"""
import pytest

from src.cad.drawing.orientation import (
    TopViewMapper,
    validate_orientation,
    make_component_mapper,
    make_assembly_mapper,
)


class TestTopViewMapper:
    """Test the coordinate transform module."""

    def test_root_le_at_center(self):
        m = TopViewMapper(center_x=300, center_y=400)
        x, y = m.map(0, 0)
        assert x == 300
        assert y == 400

    def test_aft_goes_down(self):
        """Positive cons_x (aft) must produce lower DXF Y."""
        m = TopViewMapper(center_x=300, center_y=400)
        le = m.map(0, 0)
        te = m.map(100, 0)
        assert te[1] < le[1], f"TE y={te[1]} should be below LE y={le[1]}"

    def test_left_half_extends_left(self):
        """Positive cons_y (left) must produce lower DXF X for left half."""
        m = TopViewMapper(center_x=300, center_y=400)
        root = m.map_half(0, 0, "left")
        tip = m.map_half(0, 200, "left")
        assert tip[0] < root[0], f"Left tip x={tip[0]} should be LEFT of root x={root[0]}"

    def test_right_half_extends_right(self):
        """Positive cons_y must produce higher DXF X for right half."""
        m = TopViewMapper(center_x=300, center_y=400)
        root = m.map_half(0, 0, "right")
        tip = m.map_half(0, 200, "right")
        assert tip[0] > root[0], f"Right tip x={tip[0]} should be RIGHT of root x={root[0]}"

    def test_left_and_right_are_mirrored(self):
        """Left and right tips should be equidistant from center."""
        m = TopViewMapper(center_x=300, center_y=400)
        ltip = m.map_half(0, 200, "left")
        rtip = m.map_half(0, 200, "right")
        assert abs((300 - ltip[0]) - (rtip[0] - 300)) < 0.01

    def test_validate_orientation_passes_correct(self):
        m = TopViewMapper(center_x=300, center_y=400)
        errors = validate_orientation(m, 215, 115, "left")
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_validate_orientation_catches_flipped(self):
        """A mapper with wrong sign should fail validation."""
        class BadMapper:
            center_x = 300
            center_y = 400
            def map_half(self, cx, cy, side):
                # WRONG: left half extends right
                return (self.center_x + cy, self.center_y - cx)
        m = BadMapper()
        errors = validate_orientation(m, 215, 115, "left")
        assert len(errors) > 0, "Should catch flipped orientation"
        assert any("LEFT tip is RIGHT" in e for e in errors)

    def test_invalid_side_raises(self):
        m = TopViewMapper(center_x=300, center_y=400)
        with pytest.raises(ValueError):
            m.map_half(0, 0, "center")
