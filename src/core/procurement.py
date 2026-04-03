"""Deterministic procurement helpers for the living BOM.

The system does not decide *what* aircraft is being designed or which
manufacturing path should be chosen. Those decisions come from the user/LLM
initialization step. Once a part is classified, however, procurement updates are
deterministic and should produce a stable provider shortlist for the BOM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .bom import SupplierCandidate


@dataclass(frozen=True)
class ProviderProfile:
    """A generic procurement provider that can surface BOM candidates."""

    provider_id: str
    provider_name: str
    provider_type: str
    categories: tuple[str, ...]
    regions: tuple[str, ...] = ("global",)
    default_url: str = ""
    notes: str = ""
    typical_lead_time_days: int | None = None

    def matches(self, category: str) -> bool:
        return "all" in self.categories or category in self.categories


DEFAULT_PROVIDER_CATALOG: tuple[ProviderProfile, ...] = (
    ProviderProfile(
        provider_id="temu",
        provider_name="Temu",
        provider_type="marketplace",
        categories=("electronics", "hardware", "propulsion", "rc", "all"),
        default_url="https://www.temu.com",
        notes="Default first-pass online marketplace for common RC and hardware items.",
        typical_lead_time_days=10,
    ),
    ProviderProfile(
        provider_id="aliexpress",
        provider_name="AliExpress",
        provider_type="marketplace",
        categories=("electronics", "hardware", "propulsion", "rc", "materials"),
        default_url="https://www.aliexpress.com",
        typical_lead_time_days=14,
    ),
    ProviderProfile(
        provider_id="amazon",
        provider_name="Amazon",
        provider_type="marketplace",
        categories=("electronics", "hardware", "materials"),
        default_url="https://www.amazon.com",
        typical_lead_time_days=3,
    ),
    ProviderProfile(
        provider_id="hobbyking",
        provider_name="HobbyKing",
        provider_type="specialist_rc",
        categories=("electronics", "propulsion", "rc"),
        default_url="https://hobbyking.com",
        typical_lead_time_days=7,
    ),
    ProviderProfile(
        provider_id="tme",
        provider_name="TME",
        provider_type="electronics_distributor",
        categories=("electronics",),
        default_url="https://www.tme.eu",
        typical_lead_time_days=5,
    ),
    ProviderProfile(
        provider_id="local_fabricator",
        provider_name="Local Fabricator",
        provider_type="local_quote",
        categories=("sheet_metal", "composites", "cnc", "fabrication"),
        default_url="",
        notes="Used when the project needs a location-aware quote from nearby suppliers.",
        typical_lead_time_days=7,
    ),
)


def build_supplier_candidates(
    *,
    component_name: str,
    category: str,
    location_context: dict[str, Any] | None = None,
    provider_preferences: Iterable[str] | None = None,
) -> list[SupplierCandidate]:
    """Build a stable shortlist of providers for one BOM item."""

    location_context = location_context or {}
    provider_preferences = [item.strip().lower() for item in (provider_preferences or []) if item]

    profiles = [profile for profile in DEFAULT_PROVIDER_CATALOG if profile.matches(category)]
    if provider_preferences:
        preferred_order = {provider_id: index for index, provider_id in enumerate(provider_preferences)}
        profiles.sort(key=lambda profile: preferred_order.get(profile.provider_id, 10_000))

    region = (
        location_context.get("country")
        or location_context.get("region")
        or location_context.get("city")
        or "global"
    )
    human_region = (
        location_context.get("city")
        or location_context.get("region")
        or location_context.get("country")
        or "global"
    )

    candidates: list[SupplierCandidate] = []
    for profile in profiles:
        is_preferred = bool(provider_preferences) and profile.provider_id == provider_preferences[0]
        url = profile.default_url
        notes = profile.notes
        if profile.provider_id == "local_fabricator" and human_region != "global":
            notes = f"Gather a quote from suppliers near {human_region}. {profile.notes}".strip()
        candidates.append(
            SupplierCandidate(
                provider_id=profile.provider_id,
                provider_name=profile.provider_name,
                provider_type=profile.provider_type,
                region=region,
                url=url,
                lead_time_days=profile.typical_lead_time_days,
                notes=notes,
                is_preferred=is_preferred,
            )
        )

    if not candidates:
        candidates.append(
            SupplierCandidate(
                provider_id="manual_research",
                provider_name="Manual Research",
                provider_type="manual",
                region=region,
                notes=f"No provider template matched '{component_name}'. Research manually.",
            )
        )

    return candidates
