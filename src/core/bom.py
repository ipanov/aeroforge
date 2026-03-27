"""Bill of Materials (BOM) generator.

Automatically generates and maintains a BOM from the component DAG.
Each entry includes:
- Part name, type (printed/off-shelf), material
- Mass, quantity
- Procurement source, link, estimated cost
- Whether it's a fixed constraint (owner's inventory) or to-buy

The BOM updates automatically when components change in the DAG.

All costs in USD unless noted. All weights in grams.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProcurementSource(str, Enum):
    """Where to get the part."""
    INVENTORY = "inventory"           # Already owned
    PRINTED = "3d_printed"            # Print on Bambu A1/P1S
    ALIEXPRESS = "aliexpress"
    TEMU = "temu"
    HOBBYKING = "hobbyking"
    LOCAL_MK = "local_mk"            # Macedonia
    LOCAL_BG = "local_bg"            # Bulgaria (good RC shops)
    LOCAL_GR = "local_gr"            # Greece
    AMAZON = "amazon"
    OTHER = "other"


class BOMEntry(BaseModel):
    """A single entry in the Bill of Materials."""
    name: str
    description: str = ""
    category: str = ""                # wing, fuselage, electronics, hardware

    # Part classification
    is_printed: bool = False          # 3D printed part
    is_off_shelf: bool = False        # Bought component
    is_inventory: bool = False        # Already owned

    # Physical
    material: str = ""
    mass_grams: float = 0.0
    quantity: int = 1

    # Procurement
    source: ProcurementSource = ProcurementSource.OTHER
    source_url: str = ""              # Link to buy
    unit_cost_usd: float = 0.0
    notes: str = ""

    # For printed parts
    filament_grams: float = 0.0       # Estimated filament usage
    print_time_minutes: float = 0.0   # Estimated print time

    @property
    def total_mass(self) -> float:
        return self.mass_grams * self.quantity

    @property
    def total_cost(self) -> float:
        if self.is_inventory:
            return 0.0
        return self.unit_cost_usd * self.quantity

    @property
    def status(self) -> str:
        if self.is_inventory:
            return "HAVE"
        if self.is_printed:
            return "PRINT"
        return "BUY"


class BillOfMaterials(BaseModel):
    """Complete Bill of Materials for the sailplane."""
    entries: list[BOMEntry] = Field(default_factory=list)
    currency: str = "USD"

    def add(self, entry: BOMEntry) -> None:
        """Add an entry to the BOM."""
        # Check for duplicates by name
        for existing in self.entries:
            if existing.name == entry.name:
                existing.quantity += entry.quantity
                return
        self.entries.append(entry)

    def remove(self, name: str) -> None:
        """Remove an entry by name."""
        self.entries = [e for e in self.entries if e.name != name]

    def get(self, name: str) -> Optional[BOMEntry]:
        """Get an entry by name."""
        for e in self.entries:
            if e.name == name:
                return e
        return None

    def by_category(self, category: str) -> list[BOMEntry]:
        """Get all entries in a category."""
        return [e for e in self.entries if e.category == category]

    @property
    def total_mass(self) -> float:
        """Total mass of all components."""
        return sum(e.total_mass for e in self.entries)

    @property
    def total_cost(self) -> float:
        """Total cost (excluding inventory items)."""
        return sum(e.total_cost for e in self.entries)

    @property
    def printed_mass(self) -> float:
        """Total filament mass for all printed parts."""
        return sum(e.filament_grams * e.quantity for e in self.entries if e.is_printed)

    @property
    def items_to_buy(self) -> list[BOMEntry]:
        """Items that need to be purchased."""
        return [e for e in self.entries if not e.is_inventory and not e.is_printed]

    @property
    def items_to_print(self) -> list[BOMEntry]:
        """Items that need to be 3D printed."""
        return [e for e in self.entries if e.is_printed]

    @property
    def inventory_items(self) -> list[BOMEntry]:
        """Items already owned."""
        return [e for e in self.entries if e.is_inventory]

    def summary(self) -> str:
        """Human-readable BOM summary."""
        lines = [
            "=" * 70,
            "BILL OF MATERIALS - AeroForge Sailplane",
            "=" * 70,
            "",
        ]

        # Group by category
        categories = sorted(set(e.category for e in self.entries))
        for cat in categories:
            items = self.by_category(cat)
            if not items:
                continue
            lines.append(f"--- {cat.upper()} ---")
            for e in items:
                status = e.status
                cost_str = f"${e.total_cost:.2f}" if e.total_cost > 0 else "owned" if e.is_inventory else "print"
                lines.append(
                    f"  [{status:5s}] {e.quantity}x {e.name:<30s} "
                    f"{e.total_mass:6.1f}g  {cost_str}"
                )
            lines.append("")

        lines.append("-" * 70)
        lines.append(f"  Total mass:        {self.total_mass:.0f}g")
        lines.append(f"  Total cost:        ${self.total_cost:.2f}")
        lines.append(f"  Filament needed:   {self.printed_mass:.0f}g")
        lines.append(f"  Items to buy:      {len(self.items_to_buy)}")
        lines.append(f"  Items to print:    {len(self.items_to_print)}")
        lines.append(f"  Items from inv:    {len(self.inventory_items)}")
        lines.append("=" * 70)

        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Generate markdown table for documentation."""
        lines = [
            "# Bill of Materials",
            "",
            "| Status | Qty | Component | Category | Material | Mass (g) | Cost | Source |",
            "|--------|-----|-----------|----------|----------|----------|------|--------|",
        ]

        for e in sorted(self.entries, key=lambda x: (x.category, x.name)):
            source = f"[link]({e.source_url})" if e.source_url else e.source.value
            cost = f"${e.total_cost:.2f}" if e.total_cost > 0 else "-"
            lines.append(
                f"| {e.status} | {e.quantity} | {e.name} | {e.category} | "
                f"{e.material} | {e.total_mass:.1f} | {cost} | {source} |"
            )

        lines.extend([
            "",
            f"**Total mass: {self.total_mass:.0f}g** | "
            f"**Total cost: ${self.total_cost:.2f}** | "
            f"**Filament: {self.printed_mass:.0f}g**",
        ])

        return "\n".join(lines)

    def save_markdown(self, path: str) -> None:
        """Save BOM as markdown file."""
        from pathlib import Path
        Path(path).write_text(self.to_markdown(), encoding="utf-8")
