"""Consistency tests that ENFORCE single source of truth.

These tests compare the Python spec (src/core/specs.py) against
documentation files. If anyone changes a spec without updating docs,
or changes docs without updating specs, these tests FAIL.

Run after every change: pytest tests/test_spec_consistency.py
"""

import re
from pathlib import Path

import pytest

from src.core.specs import SAILPLANE
from src.core.validation import BAMBU_BED_SIZE


PROJECT_ROOT = Path(__file__).parent.parent


def _read_file(relative_path: str) -> str:
    """Read a project file as text."""
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def _find_number_after(text: str, label: str) -> float | None:
    """Find a number after a label in text (e.g., 'Wingspan | 2100')."""
    patterns = [
        rf"{label}[^\d]*?(\d+(?:\.\d+)?)\s*mm",     # "Wingspan ... 2100mm"
        rf"{label}[^\d]*?(\d+(?:\.\d+)?)\s*m\b",     # "Wingspan ... 2.1m"
        rf"\| \*?\*?{label}\*?\*? \|[^|]*?(\d+(?:\.\d+)?)",  # table row
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


class TestSpecVsDocumentation:
    """Verify specs.py matches documentation files."""

    def test_wingspan_in_claude_md(self):
        text = _read_file("CLAUDE.md")
        ws = SAILPLANE.wing.wingspan
        assert str(int(ws)) in text or \
               f"{ws/1000:.1f}m" in text or \
               f"{ws/1000:.2f}m" in text, \
               f"CLAUDE.md doesn't contain wingspan {ws}mm"

    def test_wingspan_in_specifications(self):
        text = _read_file("docs/specifications.md")
        assert str(int(SAILPLANE.wing.wingspan)) in text, \
               f"specifications.md doesn't contain wingspan {SAILPLANE.wing.wingspan}mm"

    def test_root_chord_in_specifications(self):
        text = _read_file("docs/specifications.md")
        assert str(int(SAILPLANE.wing.root_chord)) in text, \
               f"specifications.md doesn't contain root chord {SAILPLANE.wing.root_chord}mm"

    def test_tip_chord_in_specifications(self):
        text = _read_file("docs/specifications.md")
        assert str(int(SAILPLANE.wing.tip_chord)) in text, \
               f"specifications.md doesn't contain tip chord {SAILPLANE.wing.tip_chord}mm"

    def test_panel_count_in_specifications(self):
        text = _read_file("docs/specifications.md")
        total = SAILPLANE.wing.total_panels
        per_half = SAILPLANE.wing.panels_per_half
        assert str(total) in text, f"specifications.md doesn't contain {total} total panels"
        assert str(per_half) in text, f"specifications.md doesn't contain {per_half} panels per half"

    def test_airfoils_in_specifications(self):
        text = _read_file("docs/specifications.md")
        assert SAILPLANE.wing.airfoil_root in text, \
               f"specifications.md missing root airfoil {SAILPLANE.wing.airfoil_root}"
        assert SAILPLANE.wing.airfoil_tip in text, \
               f"specifications.md missing tip airfoil {SAILPLANE.wing.airfoil_tip}"

    def test_battery_weight_in_specifications(self):
        text = _read_file("docs/specifications.md")
        assert str(int(SAILPLANE.battery.weight)) in text, \
               f"specifications.md doesn't contain battery weight {SAILPLANE.battery.weight}g"

    def test_receiver_weight_in_specifications(self):
        text = _read_file("docs/specifications.md")
        assert str(int(SAILPLANE.receiver.weight)) in text, \
               f"specifications.md doesn't contain receiver weight {SAILPLANE.receiver.weight}g"

    def test_spar_size_in_specifications(self):
        text = _read_file("docs/specifications.md")
        assert str(int(SAILPLANE.spar.main_od)) in text, \
               f"specifications.md doesn't contain main spar OD {SAILPLANE.spar.main_od}mm"

    def test_servo_count_in_specifications(self):
        text = _read_file("docs/specifications.md")
        assert str(SAILPLANE.controls.servo_count) in text, \
               f"specifications.md doesn't contain servo count {SAILPLANE.controls.servo_count}"


class TestSpecVsCLAUDEmd:
    """Verify specs.py matches CLAUDE.md quick reference."""

    def test_root_chord_in_claude_md(self):
        text = _read_file("CLAUDE.md")
        assert str(int(SAILPLANE.wing.root_chord)) in text

    def test_tip_chord_in_claude_md(self):
        text = _read_file("CLAUDE.md")
        assert str(int(SAILPLANE.wing.tip_chord)) in text

    def test_airfoil_root_in_claude_md(self):
        text = _read_file("CLAUDE.md")
        assert SAILPLANE.wing.airfoil_root in text

    def test_airfoil_tip_in_claude_md(self):
        text = _read_file("CLAUDE.md")
        assert SAILPLANE.wing.airfoil_tip in text

    def test_battery_in_claude_md(self):
        text = _read_file("CLAUDE.md")
        assert "1300" in text, "CLAUDE.md missing battery capacity 1300mAh"

    def test_panel_count_in_claude_md(self):
        text = _read_file("CLAUDE.md")
        assert str(SAILPLANE.wing.total_panels) in text


class TestSpecVsCode:
    """Verify specs.py matches code constants."""

    def test_print_bed_size_matches(self):
        """Validation.py bed size must match print spec."""
        bed = SAILPLANE.printing
        assert BAMBU_BED_SIZE == (bed.bed_x, bed.bed_y, bed.bed_z), \
               f"validation.py BAMBU_BED_SIZE {BAMBU_BED_SIZE} != " \
               f"specs.py ({bed.bed_x}, {bed.bed_y}, {bed.bed_z})"

    def test_panel_fits_on_bed(self):
        """Each wing panel must fit on the print bed."""
        panel_span = SAILPLANE.wing.panel_span
        max_chord = SAILPLANE.wing.root_chord
        bed = min(SAILPLANE.printing.bed_x, SAILPLANE.printing.bed_y)
        assert panel_span <= bed or max_chord <= bed, \
               f"Panel {panel_span:.0f}mm span or {max_chord:.0f}mm chord " \
               f"doesn't fit on {bed:.0f}mm bed"


class TestSpecInternalConsistency:
    """Verify the spec itself is self-consistent."""

    def test_taper_ratio_range(self):
        assert 0.3 <= SAILPLANE.wing.taper_ratio <= 0.8, \
               f"Taper ratio {SAILPLANE.wing.taper_ratio} outside reasonable range"

    def test_aspect_ratio_range(self):
        assert 8 <= SAILPLANE.wing.aspect_ratio <= 20, \
               f"Aspect ratio {SAILPLANE.wing.aspect_ratio} outside reasonable range"

    def test_spar_fits_in_airfoil(self):
        """Main spar must fit inside the airfoil at 28% chord."""
        min_chord = SAILPLANE.wing.tip_chord  # smallest chord
        airfoil_thickness_fraction = 0.084     # AG03 = 8.4% (thinnest)
        internal_height = min_chord * airfoil_thickness_fraction
        spar_od = SAILPLANE.spar.main_od
        assert spar_od < internal_height, \
               f"Spar {spar_od}mm doesn't fit in {internal_height:.1f}mm airfoil height at tip"

    def test_electronics_weight_budget(self):
        """Electronics should not exceed half the target AUW."""
        assert SAILPLANE.electronics_weight < 450, \
               f"Electronics {SAILPLANE.electronics_weight}g exceeds 450g limit"

    def test_wing_loading_reasonable(self):
        """Wing loading at 800g should be under 30 g/dm²."""
        wl = SAILPLANE.wing_loading_at_auw
        assert wl["at_800g"] < 30, \
               f"Wing loading {wl['at_800g']:.1f} g/dm² too high at 800g AUW"

    def test_reynolds_number_adequate(self):
        """Reynolds at tip should be above 50,000 for AG airfoils."""
        re_tip = SAILPLANE.wing.reynolds_at(1.0)
        assert re_tip > 50000, \
               f"Reynolds {re_tip:.0f} at tip too low for AG airfoils"
