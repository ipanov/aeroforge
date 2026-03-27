"""Tests for the Bill of Materials system."""

from src.core.bom import BillOfMaterials, BOMEntry, ProcurementSource


class TestBOM:

    def test_empty_bom(self):
        bom = BillOfMaterials()
        assert bom.total_mass == 0
        assert bom.total_cost == 0

    def test_add_entry(self):
        bom = BillOfMaterials()
        bom.add(BOMEntry(
            name="Servo SG90",
            category="electronics",
            is_off_shelf=True,
            mass_grams=9.0,
            quantity=6,
            unit_cost_usd=3.50,
            source=ProcurementSource.ALIEXPRESS,
        ))
        assert bom.total_mass == 54.0
        assert bom.total_cost == 21.0

    def test_inventory_items_free(self):
        bom = BillOfMaterials()
        bom.add(BOMEntry(
            name="Battery 3S 1300mAh",
            category="electronics",
            is_inventory=True,
            mass_grams=115.0,
            unit_cost_usd=25.0,  # Has a price but cost is 0 (owned)
        ))
        assert bom.total_cost == 0.0
        assert bom.total_mass == 115.0

    def test_printed_parts(self):
        bom = BillOfMaterials()
        bom.add(BOMEntry(
            name="Wing Rib 1",
            category="wing",
            is_printed=True,
            material="PLA",
            mass_grams=3.0,
            filament_grams=4.0,
            quantity=1,
        ))
        assert bom.printed_mass == 4.0
        assert len(bom.items_to_print) == 1

    def test_duplicate_increments_quantity(self):
        bom = BillOfMaterials()
        bom.add(BOMEntry(name="M2x8 screw", quantity=4, mass_grams=0.5))
        bom.add(BOMEntry(name="M2x8 screw", quantity=6, mass_grams=0.5))
        entry = bom.get("M2x8 screw")
        assert entry.quantity == 10

    def test_by_category(self):
        bom = BillOfMaterials()
        bom.add(BOMEntry(name="Servo", category="electronics"))
        bom.add(BOMEntry(name="Rib", category="wing"))
        bom.add(BOMEntry(name="ESC", category="electronics"))
        assert len(bom.by_category("electronics")) == 2
        assert len(bom.by_category("wing")) == 1

    def test_remove(self):
        bom = BillOfMaterials()
        bom.add(BOMEntry(name="test_part"))
        bom.remove("test_part")
        assert bom.get("test_part") is None

    def test_summary_runs(self):
        bom = BillOfMaterials()
        bom.add(BOMEntry(name="Part A", category="wing", mass_grams=10))
        text = bom.summary()
        assert "Part A" in text
        assert "BILL OF MATERIALS" in text

    def test_markdown_runs(self):
        bom = BillOfMaterials()
        bom.add(BOMEntry(name="Part B", category="electronics", mass_grams=5))
        md = bom.to_markdown()
        assert "Part B" in md
        assert "| Status |" in md
