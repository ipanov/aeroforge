"""Synchronization helpers for the living BOM and procurement layer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from .bom import BOMEntry, BOMSyncReason, BillOfMaterials, ProcurementAction
from .component import CustomComponent, OffShelfComponent
from .procurement import build_supplier_candidates

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOM_STATE_PATH = PROJECT_ROOT / "aeroforge.bom.yaml"
DEFAULT_BOM_MARKDOWN_PATH = PROJECT_ROOT / "docs" / "BOM.md"

FILAMENT_COST_PER_KG_USD: dict[str, float] = {
    "lw_pla": 42.0,
    "pla": 24.0,
    "cf_pla": 45.0,
    "petg": 28.0,
    "cf_petg": 48.0,
    "tpu": 36.0,
    "default": 30.0,
}
DEFAULT_MACHINE_RATE_PER_HOUR_USD = 1.25


class DeliverableEvent(BaseModel):
    """Normalized event emitted after a deliverable or component state changes."""

    component_name: str
    category: str = "uncategorized"
    component_kind: str = "custom"
    quantity: int = 1
    deliverable_path: str = ""
    deliverable_type: str = ""
    material: str = ""
    manufacturing_technique: str = ""
    production_strategy: str = ""
    mass_grams: float | None = None
    filament_grams: float | None = None
    print_time_minutes: float | None = None
    unit_cost_usd: float | None = None
    quote_reference: str = ""
    source_url: str = ""
    preferred_provider_id: str = ""
    notes: str = ""
    location_context: dict[str, Any] = Field(default_factory=dict)
    provider_preferences: list[str] = Field(default_factory=list)
    sync_reason: BOMSyncReason = BOMSyncReason.GEOMETRY_UPDATE
    sync_basis: dict[str, Any] = Field(default_factory=dict)


def load_bill_of_materials(
    path: Path | None = None,
    *,
    project_name: str = "AeroForge",
) -> BillOfMaterials:
    """Load the current BOM state, or create an empty one if missing."""

    target = path or DEFAULT_BOM_STATE_PATH
    if not target.exists():
        return BillOfMaterials(project_name=project_name)

    with open(target, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if "project_name" not in data:
        data["project_name"] = project_name
    return BillOfMaterials.model_validate(data)


def save_bill_of_materials(
    bom: BillOfMaterials,
    *,
    path: Path | None = None,
    markdown_path: Path | None = None,
) -> Path:
    """Persist both the machine-readable and markdown BOM views."""

    target = path or DEFAULT_BOM_STATE_PATH
    markdown_target = markdown_path or DEFAULT_BOM_MARKDOWN_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    markdown_target.parent.mkdir(parents=True, exist_ok=True)

    with open(target, "w", encoding="utf-8") as handle:
        yaml.safe_dump(bom.model_dump(mode="json"), handle, sort_keys=False, allow_unicode=False)

    bom.save_markdown(str(markdown_target))
    return target


def estimate_custom_part_cost(
    *,
    material: str,
    filament_grams: float | None,
    print_time_minutes: float | None,
) -> float:
    """Estimate a deterministic unit cost for printed/custom parts."""

    grams = filament_grams or 0.0
    minutes = print_time_minutes or 0.0
    material_key = material.strip().lower() if material else "default"
    kg_cost = FILAMENT_COST_PER_KG_USD.get(material_key, FILAMENT_COST_PER_KG_USD["default"])
    material_cost = (grams / 1000.0) * kg_cost
    machine_cost = (minutes / 60.0) * DEFAULT_MACHINE_RATE_PER_HOUR_USD
    return round(material_cost + machine_cost, 2)


def determine_procurement_action(event: DeliverableEvent) -> ProcurementAction:
    """Translate a project event into a deterministic procurement action."""

    technique = event.manufacturing_technique.lower()
    strategy = event.production_strategy.lower()
    deliverable_type = event.deliverable_type.lower()

    if event.component_kind == "off_the_shelf":
        if "quote" in strategy or "quote" in technique:
            return ProcurementAction.QUOTE
        if "outsource" in strategy or "supplier" in strategy:
            return ProcurementAction.OUTSOURCE
        return ProcurementAction.BUY

    if any(token in strategy for token in ("outsource", "supplier")):
        return ProcurementAction.OUTSOURCE
    if any(token in strategy for token in ("quote", "local_fabricator")):
        return ProcurementAction.QUOTE
    if any(token in technique for token in ("print", "fdm", "sla", "sls", "additive")):
        return ProcurementAction.PRINT
    if deliverable_type in {"3mf_mesh", "stl_mesh"}:
        return ProcurementAction.PRINT
    if any(token in technique for token in ("sheet", "cnc", "composite", "stitch", "laser")):
        return ProcurementAction.FABRICATE
    return ProcurementAction.FABRICATE


def sync_deliverable_event(
    event: DeliverableEvent,
    *,
    bom_path: Path | None = None,
    markdown_path: Path | None = None,
    project_name: str = "AeroForge",
) -> BOMEntry:
    """Update the living BOM from one deliverable event."""

    bom = load_bill_of_materials(bom_path, project_name=project_name)
    existing = bom.get(event.component_name)
    procurement_action = determine_procurement_action(event)

    if event.component_kind == "off_the_shelf" or procurement_action in {
        ProcurementAction.BUY,
        ProcurementAction.QUOTE,
        ProcurementAction.OUTSOURCE,
    }:
        supplier_candidates = build_supplier_candidates(
            component_name=event.component_name,
            category=event.category,
            location_context=event.location_context,
            provider_preferences=event.provider_preferences,
        )
    else:
        supplier_candidates = existing.supplier_candidates if existing else []

    unit_cost = event.unit_cost_usd
    if unit_cost is None and procurement_action == ProcurementAction.PRINT:
        unit_cost = estimate_custom_part_cost(
            material=event.material,
            filament_grams=event.filament_grams,
            print_time_minutes=event.print_time_minutes,
        )
    elif unit_cost is None and existing is not None:
        unit_cost = existing.unit_cost_usd
    else:
        unit_cost = unit_cost or 0.0

    entry = BOMEntry(
        name=event.component_name,
        description=existing.description if existing else "",
        category=event.category or (existing.category if existing else "uncategorized"),
        is_custom_part=event.component_kind == "custom",
        is_off_shelf=event.component_kind == "off_the_shelf",
        is_inventory=existing.is_inventory if existing else False,
        material=event.material or (existing.material if existing else ""),
        manufacturing_technique=event.manufacturing_technique or (
            existing.manufacturing_technique if existing else ""
        ),
        production_strategy=event.production_strategy or (existing.production_strategy if existing else ""),
        deliverable_type=event.deliverable_type or (existing.deliverable_type if existing else ""),
        mass_grams=event.mass_grams if event.mass_grams is not None else (existing.mass_grams if existing else 0.0),
        quantity=event.quantity or (existing.quantity if existing else 1),
        filament_grams=event.filament_grams if event.filament_grams is not None else (
            existing.filament_grams if existing else 0.0
        ),
        print_time_minutes=event.print_time_minutes if event.print_time_minutes is not None else (
            existing.print_time_minutes if existing else 0.0
        ),
        procurement_action=procurement_action,
        preferred_provider_id=event.preferred_provider_id or (
            existing.preferred_provider_id if existing else ""
        ),
        unit_cost_usd=float(unit_cost),
        quote_reference=event.quote_reference or (existing.quote_reference if existing else ""),
        source_url=event.source_url or (existing.source_url if existing else event.deliverable_path),
        supplier_candidates=supplier_candidates,
        notes=event.notes or (existing.notes if existing else ""),
        last_sync_reason=event.sync_reason,
        last_synced_at=event.sync_basis.get("synced_at"),
        sync_basis={
            **(existing.sync_basis if existing else {}),
            **event.sync_basis,
            "deliverable_path": event.deliverable_path or (existing.sync_basis.get("deliverable_path") if existing else ""),
            "component_kind": event.component_kind,
        },
    )
    bom.upsert(entry)

    if event.location_context:
        bom.location_context = event.location_context
    if event.provider_preferences:
        bom.provider_preferences = event.provider_preferences

    save_bill_of_materials(bom, path=bom_path, markdown_path=markdown_path)
    return entry


def sync_component_rebuild(
    component: Any,
    *,
    bom_path: Path | None = None,
    markdown_path: Path | None = None,
    project_name: str = "AeroForge",
    location_context: dict[str, Any] | None = None,
    provider_preferences: list[str] | None = None,
) -> BOMEntry:
    """Sync a component directly after a deterministic rebuild hook fires."""

    material = getattr(getattr(component, "spec", None), "material", "")
    material_value = getattr(material, "value", str(material or ""))
    component_kind = "off_the_shelf" if isinstance(component, OffShelfComponent) else "custom"

    event = DeliverableEvent(
        component_name=component.name,
        category=component.__class__.__name__.lower(),
        component_kind=component_kind,
        deliverable_type="step_model",
        manufacturing_technique="parametric_model_rebuild",
        material=material_value,
        mass_grams=float(getattr(component, "mass", 0.0) or 0.0),
        production_strategy="procured_subsystem" if component_kind == "off_the_shelf" else "in_house_custom",
        location_context=location_context or {},
        provider_preferences=provider_preferences or [],
        sync_reason=BOMSyncReason.GEOMETRY_UPDATE,
        sync_basis={"component_id": getattr(component, "id", ""), "hook": "dependency_rebuild"},
    )
    return sync_deliverable_event(
        event,
        bom_path=bom_path,
        markdown_path=markdown_path,
        project_name=project_name,
    )


def attach_bom_sync_hooks(
    graph: Any,
    *,
    bom_path: Path | None = None,
    markdown_path: Path | None = None,
    project_name: str = "AeroForge",
    location_context: dict[str, Any] | None = None,
    provider_preferences: list[str] | None = None,
) -> None:
    """Register deterministic BOM updates on component rebuilds."""

    def _hook(component: Any) -> None:
        sync_component_rebuild(
            component,
            bom_path=bom_path,
            markdown_path=markdown_path,
            project_name=project_name,
            location_context=location_context,
            provider_preferences=provider_preferences,
        )

    graph.on_rebuild(_hook)
