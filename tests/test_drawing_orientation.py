"""
Drawing Orientation & Component Integrity Tests
=================================================
These tests are BLOCKING — they run before any drawing is committed.
They enforce:
  1. Left half extends LEFT, right half extends RIGHT
  2. LE is forward (top), TE is aft (bottom)
  3. Component sections show ONLY that component's geometry
  4. No component contains geometry from another component
  5. Dimension values match real-world specs (not scaled)
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cad.drawing.orientation import (
    TopViewMapper,
    validate_orientation,
    make_component_mapper,
    make_assembly_mapper,
)
from scripts.hstab_geometry import (
    HALF_SPAN, ROOT_CHORD, X_MAIN_SPAR, X_HINGE,
    le_x, te_x, chord_at, Y_MAIN_END, Y_HINGE_END,
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


class TestComponentIntegrity:
    """Verify that component geometry respects single-part rules."""

    def test_stab_chord_is_le_to_hinge(self):
        """Stab component chord = LE to hinge, NOT LE to TE."""
        for y in [0, 50, 100, 150]:
            c = chord_at(y)
            lx = le_x(y)
            stab_chord = X_HINGE - lx
            full_chord = te_x(y) - lx
            assert stab_chord < full_chord, (
                f"At y={y}: stab chord {stab_chord} must be less than full chord {full_chord}"
            )
            assert stab_chord > 0, f"At y={y}: stab chord must be positive"

    def test_elevator_chord_is_hinge_to_te(self):
        """Elevator component chord = hinge to TE, NOT LE to TE."""
        for y in [0, 50, 100, 150, 200]:
            tx = te_x(y)
            elev_chord = tx - X_HINGE
            if elev_chord <= 0:
                continue  # hinge past TE at this station
            full_chord = tx - le_x(y)
            assert elev_chord < full_chord, (
                f"At y={y}: elevator chord {elev_chord} must be less than full chord {full_chord}"
            )

    def test_stab_plus_elevator_equals_full_chord(self):
        """Stab chord + elevator chord = full chord at every station."""
        for y in [0, 50, 100, 150]:
            lx = le_x(y)
            tx = te_x(y)
            stab_chord = X_HINGE - lx
            elev_chord = tx - X_HINGE
            full_chord = tx - lx
            assert abs(stab_chord + elev_chord - full_chord) < 0.01, (
                f"At y={y}: stab({stab_chord:.1f}) + elev({elev_chord:.1f}) "
                f"!= full({full_chord:.1f})"
            )

    def test_spar_inside_stab_not_elevator(self):
        """Main spar must be inside stab zone (between LE and hinge)."""
        for y in range(0, int(Y_MAIN_END), 10):
            lx = le_x(y)
            assert X_MAIN_SPAR > lx, f"Spar at X={X_MAIN_SPAR} must be aft of LE at y={y} (LE={lx})"
            assert X_MAIN_SPAR < X_HINGE, f"Spar at X={X_MAIN_SPAR} must be forward of hinge X={X_HINGE}"

    def test_hinge_wire_at_component_boundary(self):
        """Hinge wire is at the boundary between stab and elevator."""
        assert X_HINGE == 60.0, f"v6 hinge should be at X=60.0, got {X_HINGE}"

    def test_no_rear_spar_in_v6(self):
        """v6 removed the rear spar — ensure it's not referenced."""
        import scripts.hstab_geometry as geo
        assert not hasattr(geo, 'X_REAR_SPAR') or 'X_REAR_SPAR' not in dir(geo), (
            "X_REAR_SPAR should not be an active variable in v6"
        )

    def test_no_stiffener_in_v6(self):
        """v6 removed the stiffener — ensure it's not referenced."""
        import scripts.hstab_geometry as geo
        assert not hasattr(geo, 'X_STIFF') or 'X_STIFF' not in dir(geo), (
            "X_STIFF should not be an active variable in v6"
        )


class TestDimensionValues:
    """Verify that spec values are consistent."""

    def test_main_spar_position(self):
        assert X_MAIN_SPAR == 34.5, f"v6 spar at X=34.5, got {X_MAIN_SPAR}"

    def test_hinge_position(self):
        assert X_HINGE == 60.0, f"v6 hinge at X=60.0, got {X_HINGE}"

    def test_spar_terminates_correctly(self):
        assert Y_MAIN_END == 189.0, f"v6 spar ends at y=189, got {Y_MAIN_END}"

    def test_hinge_terminates_correctly(self):
        assert Y_HINGE_END == 212.0, f"v6 hinge ends at y=212, got {Y_HINGE_END}"

    def test_root_chord(self):
        assert ROOT_CHORD == 115.0

    def test_half_span(self):
        assert HALF_SPAN == 215.0

    def test_spar_fits_airfoil_at_termination(self):
        """At spar termination, airfoil must be thick enough for 3.1mm bore."""
        from scripts.hstab_geometry import naca4_yt, t_ratio
        y = Y_MAIN_END
        c = chord_at(y)
        lx = le_x(y)
        frac = (X_MAIN_SPAR - lx) / c
        tr = t_ratio(y)
        thickness = 2 * naca4_yt(frac, tr) * c
        assert thickness >= 3.1, (
            f"Airfoil thickness at spar termination y={y}: {thickness:.2f}mm < 3.1mm bore"
        )


class TestDxfFileIntegrity:
    """Check generated DXF files for basic correctness."""

    @pytest.fixture
    def load_dxf(self):
        """Helper to load a DXF and return its text entities."""
        import ezdxf
        def _load(path):
            if not os.path.exists(path):
                pytest.skip(f"{path} not found")
            doc = ezdxf.readfile(path)
            msp = doc.modelspace()
            texts = [e.dxf.text for e in msp if e.dxftype() == "TEXT"]
            return doc, msp, texts
        return _load

    def test_hstab_left_no_elevator_geometry(self, load_dxf):
        """HStab_Left must NOT contain elevator-related text."""
        _, _, texts = load_dxf("cad/components/empennage/HStab_Left/HStab_Left_drawing.dxf")
        texts_lower = [t.lower() for t in texts]
        # Should NOT contain "elevator" as a component (context mentions are OK)
        assert not any("elevator (this component)" in t for t in texts_lower), (
            "HStab_Left drawing claims elevator is this component!"
        )

    def test_hstab_left_says_stab(self, load_dxf):
        """HStab_Left must identify as stab component."""
        _, _, texts = load_dxf("cad/components/empennage/HStab_Left/HStab_Left_drawing.dxf")
        texts_lower = [t.lower() for t in texts]
        assert any("stab" in t and "component" in t for t in texts_lower), (
            "HStab_Left should say 'stab component'"
        )

    def test_elevator_left_no_full_airfoil(self, load_dxf):
        """Elevator_Left sections must NOT show the full airfoil."""
        _, _, texts = load_dxf("cad/components/empennage/Elevator_Left/Elevator_Left_drawing.dxf")
        texts_lower = [t.lower() for t in texts]
        # Should NOT have "stab zone" or "this component = stab"
        assert not any("stab zone (this component)" in t for t in texts_lower), (
            "Elevator_Left drawing claims stab zone is this component!"
        )

    def test_assembly_has_both_zones(self, load_dxf):
        """Assembly must show both STAB and ELEVATOR zones."""
        _, _, texts = load_dxf(
            "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf"
        )
        texts_lower = [t.lower() for t in texts]
        assert any("stab" in t for t in texts_lower), "Assembly should mention STAB"
        assert any("elevator" in t for t in texts_lower), "Assembly should mention ELEVATOR"

    def test_no_v5_rear_spar_references(self, load_dxf):
        """No drawing should reference the rear spar as an active component."""
        for path in [
            "cad/components/empennage/HStab_Left/HStab_Left_drawing.dxf",
            "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf",
        ]:
            _, _, texts = load_dxf(path)
            for t in texts:
                if "rear spar" in t.lower() and "removed" not in t.lower():
                    pytest.fail(f"{path}: mentions rear spar without 'removed': '{t}'")
