"""Living Bill of Materials models.

The BOM is a synchronized project artifact. It should evolve when:
- custom-part geometry changes
- manufacturing technique changes
- material strategy changes
- supplier selection changes
- off-the-shelf component specifications change
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProcurementAction(str, Enum):
    """What the team needs to do to obtain the item."""

    INVENTORY = "inventory"
    BUY = "buy"
    PRINT = "print"
    QUOTE = "quote"
    FABRICATE = "fabricate"
    OUTSOURCE = "outsource"


class BOMSyncReason(str, Enum):
    """Why a BOM entry was last refreshed."""

    INITIALIZATION = "initialization"
    GEOMETRY_UPDATE = "geometry_update"
    PROCUREMENT_REFRESH = "procurement_refresh"
    MANUFACTURING_UPDATE = "manufacturing_update"
    MANUAL_OVERRIDE = "manual_override"


class SupplierCandidate(BaseModel):
    """One possible provider or supplier for an item."""

    provider_id: str
    provider_name: str
    provider_type: str = "marketplace"
    region: str = "global"
    url: str = ""
    sku: str = ""
    unit_cost_usd: float = 0.0
    currency: str = "USD"
    lead_time_days: Optional[int] = None
    notes: str = ""
    is_preferred: bool = False


class BOMEntry(BaseModel):
    """A single entry in the Bill of Materials."""

    name: str
    description: str = ""
    category: str = ""

    # Classification
    is_custom_part: bool = False
    is_off_shelf: bool = False
    is_inventory: bool = False

    # Physical and manufacturing
    material: str = ""
    manufacturing_technique: str = ""
    production_strategy: str = ""
    deliverable_type: str = ""
    mass_grams: float = 0.0
    quantity: int = 1
    filament_grams: float = 0.0
    print_time_minutes: float = 0.0

    # Procurement
    procurement_action: ProcurementAction = ProcurementAction.BUY
    preferred_provider_id: str = ""
    unit_cost_usd: float = 0.0
    quote_reference: str = ""
    source_url: str = ""
    supplier_candidates: list[SupplierCandidate] = Field(default_factory=list)
    notes: str = ""

    # Synchronization metadata
    last_synced_at: Optional[str] = None
    last_sync_reason: BOMSyncReason = BOMSyncReason.INITIALIZATION
    sync_basis: dict[str, Any] = Field(default_factory=dict)

    @property
    def total_mass(self) -> float:
        return self.mass_grams * self.quantity

    @property
    def selected_unit_cost(self) -> float:
        if self.unit_cost_usd > 0:
            return self.unit_cost_usd
        preferred = self.preferred_supplier
        if preferred:
            return preferred.unit_cost_usd
        for candidate in self.supplier_candidates:
            if candidate.unit_cost_usd > 0:
                return candidate.unit_cost_usd
        return 0.0

    @property
    def total_cost(self) -> float:
        if self.is_inventory or self.procurement_action == ProcurementAction.INVENTORY:
            return 0.0
        return self.selected_unit_cost * self.quantity

    @property
    def preferred_supplier(self) -> Optional[SupplierCandidate]:
        if self.preferred_provider_id:
            for candidate in self.supplier_candidates:
                if candidate.provider_id == self.preferred_provider_id:
                    return candidate
        for candidate in self.supplier_candidates:
            if candidate.is_preferred:
                return candidate
        return self.supplier_candidates[0] if self.supplier_candidates else None

    @property
    def status(self) -> str:
        if self.is_inventory or self.procurement_action == ProcurementAction.INVENTORY:
            return "HAVE"
        if self.procurement_action == ProcurementAction.PRINT:
            return "PRINT"
        if self.procurement_action == ProcurementAction.QUOTE:
            return "QUOTE"
        if self.procurement_action == ProcurementAction.FABRICATE:
            return "FABRICATE"
        if self.procurement_action == ProcurementAction.OUTSOURCE:
            return "OUTSOURCE"
        return "BUY"


class BillOfMaterials(BaseModel):
    """Complete living BOM for an AeroForge project."""

    entries: list[BOMEntry] = Field(default_factory=list)
    currency: str = "USD"
    project_name: str = "AeroForge"
    location_context: dict[str, Any] = Field(default_factory=dict)
    provider_preferences: list[str] = Field(default_factory=list)
    notes: str = ""

    def add(self, entry: BOMEntry) -> None:
        """Add an entry or merge with an existing item of the same name."""

        existing = self.get(entry.name)
        if existing is None:
            self.entries.append(entry)
            return

        existing.quantity += entry.quantity
        if entry.mass_grams:
            existing.mass_grams = entry.mass_grams
        if entry.unit_cost_usd:
            existing.unit_cost_usd = entry.unit_cost_usd
        if entry.source_url:
            existing.source_url = entry.source_url
        if entry.manufacturing_technique:
            existing.manufacturing_technique = entry.manufacturing_technique
        if entry.production_strategy:
            existing.production_strategy = entry.production_strategy
        if entry.deliverable_type:
            existing.deliverable_type = entry.deliverable_type
        if entry.supplier_candidates:
            existing.supplier_candidates = entry.supplier_candidates
        if entry.preferred_provider_id:
            existing.preferred_provider_id = entry.preferred_provider_id
        existing.last_synced_at = entry.last_synced_at or existing.last_synced_at
        existing.last_sync_reason = entry.last_sync_reason
        if entry.sync_basis:
            existing.sync_basis = entry.sync_basis

    def upsert(self, entry: BOMEntry) -> None:
        """Insert or replace a BOM entry by name."""

        existing = self.get(entry.name)
        if existing is None:
            self.entries.append(entry)
            return
        index = self.entries.index(existing)
        self.entries[index] = entry

    def sync_entry(
        self,
        name: str,
        *,
        mass_grams: Optional[float] = None,
        filament_grams: Optional[float] = None,
        manufacturing_technique: Optional[str] = None,
        material: Optional[str] = None,
        deliverable_type: Optional[str] = None,
        unit_cost_usd: Optional[float] = None,
        supplier_candidates: Optional[list[SupplierCandidate]] = None,
        preferred_provider_id: Optional[str] = None,
        sync_reason: BOMSyncReason = BOMSyncReason.GEOMETRY_UPDATE,
        synced_at: Optional[str] = None,
        sync_basis: Optional[dict[str, Any]] = None,
    ) -> BOMEntry:
        """Synchronize one entry after a project change."""

        entry = self.get(name)
        if entry is None:
            raise KeyError(f"BOM entry '{name}' not found")

        if mass_grams is not None:
            entry.mass_grams = mass_grams
        if filament_grams is not None:
            entry.filament_grams = filament_grams
        if manufacturing_technique is not None:
            entry.manufacturing_technique = manufacturing_technique
        if material is not None:
            entry.material = material
        if deliverable_type is not None:
            entry.deliverable_type = deliverable_type
        if unit_cost_usd is not None:
            entry.unit_cost_usd = unit_cost_usd
        if supplier_candidates is not None:
            entry.supplier_candidates = supplier_candidates
        if preferred_provider_id is not None:
            entry.preferred_provider_id = preferred_provider_id
        entry.last_sync_reason = sync_reason
        entry.last_synced_at = synced_at
        if sync_basis is not None:
            entry.sync_basis = sync_basis
        return entry

    def remove(self, name: str) -> None:
        self.entries = [entry for entry in self.entries if entry.name != name]

    def get(self, name: str) -> Optional[BOMEntry]:
        for entry in self.entries:
            if entry.name == name:
                return entry
        return None

    def by_category(self, category: str) -> list[BOMEntry]:
        return [entry for entry in self.entries if entry.category == category]

    @property
    def total_mass(self) -> float:
        return sum(entry.total_mass for entry in self.entries)

    @property
    def total_cost(self) -> float:
        return sum(entry.total_cost for entry in self.entries)

    @property
    def printed_mass(self) -> float:
        return sum(
            entry.filament_grams * entry.quantity
            for entry in self.entries
            if entry.procurement_action == ProcurementAction.PRINT
        )

    @property
    def items_to_buy(self) -> list[BOMEntry]:
        return [entry for entry in self.entries if entry.procurement_action == ProcurementAction.BUY]

    @property
    def items_to_print(self) -> list[BOMEntry]:
        return [entry for entry in self.entries if entry.procurement_action == ProcurementAction.PRINT]

    @property
    def items_to_quote(self) -> list[BOMEntry]:
        return [entry for entry in self.entries if entry.procurement_action in {ProcurementAction.QUOTE, ProcurementAction.OUTSOURCE}]

    @property
    def inventory_items(self) -> list[BOMEntry]:
        return [
            entry for entry in self.entries
            if entry.is_inventory or entry.procurement_action == ProcurementAction.INVENTORY
        ]

    def summary(self) -> str:
        lines = [
            "=" * 72,
            f"BILL OF MATERIALS - {self.project_name}",
            "=" * 72,
            "",
        ]
        categories = sorted(set(entry.category for entry in self.entries))
        for category in categories:
            items = self.by_category(category)
            if not items:
                continue
            lines.append(f"--- {category.upper()} ---")
            for entry in items:
                cost_str = f"${entry.total_cost:.2f}" if entry.total_cost > 0 else "-"
                supplier = entry.preferred_supplier.provider_name if entry.preferred_supplier else entry.preferred_provider_id or "-"
                lines.append(
                    f"  [{entry.status:9s}] {entry.quantity}x {entry.name:<28s} "
                    f"{entry.total_mass:6.1f}g  {cost_str:<10s} {supplier}"
                )
            lines.append("")

        lines.append("-" * 72)
        lines.append(f"  Total mass:      {self.total_mass:.1f}g")
        lines.append(f"  Total cost:      ${self.total_cost:.2f}")
        lines.append(f"  Filament mass:   {self.printed_mass:.1f}g")
        lines.append(f"  Buy items:       {len(self.items_to_buy)}")
        lines.append(f"  Quote/outsource: {len(self.items_to_quote)}")
        lines.append(f"  Inventory items: {len(self.inventory_items)}")
        lines.append("=" * 72)
        return "\n".join(lines)

    def to_markdown(self) -> str:
        lines = [
            "# Bill of Materials",
            "",
            "| Status | Qty | Component | Category | Technique | Deliverable | Mass (g) | Cost | Provider |",
            "|--------|-----|-----------|----------|-----------|-------------|----------|------|----------|",
        ]
        for entry in sorted(self.entries, key=lambda item: (item.category, item.name)):
            provider = entry.preferred_supplier.provider_name if entry.preferred_supplier else "-"
            cost = f"${entry.total_cost:.2f}" if entry.total_cost > 0 else "-"
            lines.append(
                f"| {entry.status} | {entry.quantity} | {entry.name} | {entry.category} | "
                f"{entry.manufacturing_technique or '-'} | {entry.deliverable_type or '-'} | "
                f"{entry.total_mass:.1f} | {cost} | {provider} |"
            )
        lines.extend(
            [
                "",
                f"**Total mass: {self.total_mass:.1f}g**",
                f"**Total cost: ${self.total_cost:.2f}**",
            ]
        )
        return "\n".join(lines)

    def save_markdown(self, path: str) -> None:
        from pathlib import Path

        Path(path).write_text(self.to_markdown(), encoding="utf-8")
