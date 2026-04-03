from __future__ import annotations

from pathlib import Path

from src.core.bom import ProcurementAction
from src.core.bom_sync import DeliverableEvent, load_bill_of_materials, sync_deliverable_event


def test_custom_part_deliverable_sync_updates_living_bom(tmp_path: Path) -> None:
    bom_path = tmp_path / "bom.yaml"
    markdown_path = tmp_path / "BOM.md"

    entry = sync_deliverable_event(
        DeliverableEvent(
            component_name="Wing Shell",
            category="wing",
            component_kind="custom",
            deliverable_path="cad/components/wing/Wing_Shell/wing_shell.3mf",
            deliverable_type="3mf_mesh",
            material="lw_pla",
            manufacturing_technique="thin_wall_fdm_printing",
            production_strategy="hybrid_in_house_and_procured",
            mass_grams=14.2,
            filament_grams=18.0,
            print_time_minutes=72.0,
        ),
        bom_path=bom_path,
        markdown_path=markdown_path,
        project_name="AIR4",
    )

    assert entry.procurement_action == ProcurementAction.PRINT
    assert entry.unit_cost_usd > 0
    assert markdown_path.exists()
    assert "Wing Shell" in markdown_path.read_text(encoding="utf-8")


def test_off_shelf_deliverable_sync_refreshes_procurement_candidates(tmp_path: Path) -> None:
    bom_path = tmp_path / "bom.yaml"

    entry = sync_deliverable_event(
        DeliverableEvent(
            component_name="Flight Controller",
            category="electronics",
            component_kind="off_the_shelf",
            deliverable_path="components/electronics/flight_controller.yaml",
            deliverable_type="procurement_record",
            production_strategy="procured_subsystem",
            provider_preferences=["temu", "amazon"],
            location_context={"country": "North Macedonia", "region": "Skopje"},
        ),
        bom_path=bom_path,
        markdown_path=tmp_path / "BOM.md",
        project_name="AIR4",
    )

    assert entry.procurement_action == ProcurementAction.BUY
    assert entry.supplier_candidates
    assert entry.supplier_candidates[0].provider_id == "temu"

    bom = load_bill_of_materials(bom_path, project_name="AIR4")
    persisted = bom.get("Flight Controller")
    assert persisted is not None
    assert persisted.supplier_candidates[0].provider_id == "temu"
