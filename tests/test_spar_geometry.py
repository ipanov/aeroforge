"""TDD tests for MainSpar geometry in FreeCAD.

Validates that the carbon spar tube exists and has correct dimensions
matching SAILPLANE spec values.
"""

import math
import re

from src.core.specs import SAILPLANE


def _parse_bb(output: str) -> dict[str, float]:
    """Parse bounding box values from FreeCAD RPC output."""
    result = {}
    for match in re.finditer(r"BB_(X|Y|Z|VOL):([\d.]+)", output):
        result[match.group(1)] = float(match.group(2))
    return result


def _query_spar(freecad_rpc) -> dict:
    """Query MainSpar object properties from FreeCAD."""
    code = """
import FreeCAD
obj = FreeCAD.ActiveDocument.getObject("MainSpar")
if obj is None:
    print("NOT_FOUND")
else:
    bb = obj.Shape.BoundBox
    print(f"BB_X:{bb.XLength:.6f}")
    print(f"BB_Y:{bb.YLength:.6f}")
    print(f"BB_Z:{bb.ZLength:.6f}")
    print(f"VOLUME:{obj.Shape.Volume:.6f}")
"""
    return freecad_rpc.execute(code)


class TestMainSparGeometry:
    """Test suite for MainSpar FreeCAD object."""

    def test_main_spar_exists(self, freecad_rpc):
        """MainSpar object must exist in the active FreeCAD document."""
        output = _query_spar(freecad_rpc)
        assert "NOT_FOUND" not in output, "MainSpar object not found in FreeCAD document"

    def test_main_spar_outer_diameter(self, freecad_rpc):
        """Outer diameter must match SAILPLANE.spar.main_od (8.0mm)."""
        output = _query_spar(freecad_rpc)
        bb = _parse_bb(output)
        # Cylinder along Y axis: OD = max(X, Z)
        od = max(bb["X"], bb["Z"])
        expected_od = SAILPLANE.spar.main_od
        assert od == pytest.approx(expected_od, abs=0.01), (
            f"OD={od:.3f}mm, expected {expected_od}mm"
        )

    def test_main_spar_length(self, freecad_rpc):
        """Length must match SAILPLANE.wing.panel_span (256.0mm)."""
        output = _query_spar(freecad_rpc)
        bb = _parse_bb(output)
        # Cylinder along Y axis: length = Y
        length = bb["Y"]
        expected_length = SAILPLANE.wing.panel_span
        assert length == pytest.approx(expected_length, abs=0.1), (
            f"Length={length:.3f}mm, expected {expected_length}mm"
        )

    def test_main_spar_volume_positive(self, freecad_rpc):
        """Spar must have positive volume."""
        output = _query_spar(freecad_rpc)
        volume = float(re.search(r"VOLUME:([\d.]+)", output).group(1))
        assert volume > 0, "MainSpar volume must be positive"

    def test_main_spar_is_hollow(self, freecad_rpc):
        """Spar must be hollow: volume < 80% of solid cylinder volume."""
        output = _query_spar(freecad_rpc)
        volume = float(re.search(r"VOLUME:([\d.]+)", output).group(1))
        bb = _parse_bb(output)
        od = max(bb["X"], bb["Z"])
        length = bb["Y"]
        solid_volume = math.pi * (od / 2) ** 2 * length
        ratio = volume / solid_volume
        assert ratio < 0.80, (
            f"Spar volume ratio={ratio:.2f}, expected < 0.80 (must be hollow)"
        )


# Need pytest import for approx
import pytest
