"""Tests for the living Bill of Materials system."""

from src.core.bom import (
    BillOfMaterials,
    BOMEntry,
    BOMSyncReason,
    ProcurementAction,
    SupplierCandidate,
)


class TestBOM:
    def test_empty_bom(self):
        bom = BillOfMaterials()
        assert bom.total_mass == 0
        assert bom.total_cost == 0

    def test_add_entry(self):
        bom = BillOfMaterials()
        bom.add(
            BOMEntry(
                name="Servo SG90",
                category="electronics",
                is_off_shelf=True,
                mass_grams=9.0,
                quantity=6,
                procurement_action=ProcurementAction.BUY,
                supplier_candidates=[
                    SupplierCandidate(
                        provider_id="temu",
                        provider_name="Temu",
                        unit_cost_usd=3.50,
                        is_preferred=True,
                    )
                ],
            )
        )
        assert bom.total_mass == 54.0
        assert bom.total_cost == 21.0

    def test_inventory_items_free(self):
        bom = BillOfMaterials()
        bom.add(
            BOMEntry(
                name="Battery 3S 1300mAh",
                category="electronics",
                is_inventory=True,
                mass_grams=115.0,
                unit_cost_usd=25.0,
                procurement_action=ProcurementAction.INVENTORY,
            )
        )
        assert bom.total_cost == 0.0
        assert bom.total_mass == 115.0

    def test_printed_parts(self):
        bom = BillOfMaterials()
        bom.add(
            BOMEntry(
                name="Wing Rib 1",
                category="wing",
                is_custom_part=True,
                manufacturing_technique="shell_printing",
                deliverable_type="3mf_mesh",
                mass_grams=3.0,
                filament_grams=4.0,
                quantity=1,
                procurement_action=ProcurementAction.PRINT,
            )
        )
        assert bom.printed_mass == 4.0
        assert len(bom.items_to_print) == 1

    def test_duplicate_increments_quantity(self):
        bom = BillOfMaterials()
        bom.add(BOMEntry(name="M2x8 screw", quantity=4, mass_grams=0.5))
        bom.add(BOMEntry(name="M2x8 screw", quantity=6, mass_grams=0.5))
        entry = bom.get("M2x8 screw")
        assert entry is not None
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

    def test_sync_entry_updates_latest_state(self):
        bom = BillOfMaterials()
        bom.add(
            BOMEntry(
                name="Wing Shell",
                category="wing",
                is_custom_part=True,
                procurement_action=ProcurementAction.PRINT,
                mass_grams=12.0,
                filament_grams=16.0,
                manufacturing_technique="shell_printing",
                deliverable_type="3mf_mesh",
            )
        )
        bom.sync_entry(
            "Wing Shell",
            mass_grams=14.0,
            filament_grams=19.0,
            sync_reason=BOMSyncReason.GEOMETRY_UPDATE,
            sync_basis={"volume_cm3": 22.5},
        )
        entry = bom.get("Wing Shell")
        assert entry is not None
        assert entry.mass_grams == 14.0
        assert entry.filament_grams == 19.0
        assert entry.last_sync_reason == BOMSyncReason.GEOMETRY_UPDATE

    def test_markdown_runs(self):
        bom = BillOfMaterials(project_name="Paper Aircraft")
        bom.add(
            BOMEntry(
                name="Fold Sheet",
                category="airframe",
                procurement_action=ProcurementAction.FABRICATE,
                deliverable_type="fold_instructions",
                manufacturing_technique="folding_by_hand",
                mass_grams=5,
            )
        )
        md = bom.to_markdown()
        assert "Fold Sheet" in md
        assert "| Status |" in md
