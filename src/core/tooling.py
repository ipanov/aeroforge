"""Schemas for project tooling decisions.

This module intentionally does not hardcode a tooling catalog. Tooling choice is
considered a non-deterministic project decision supplied by a user or an LLM,
then persisted and enforced by the workflow code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolingOption:
    """A single tooling choice captured in the project profile."""

    tooling_id: str
    display_name: str
    category: str
    process: str
    description: str
    strengths: list[str] = field(default_factory=list)
    tradeoffs: list[str] = field(default_factory=list)
    typical_materials: list[str] = field(default_factory=list)
    supports_custom_components: bool = True
    supports_off_the_shelf_components: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolingOption":
        """Construct a tooling option from persisted project data."""

        return cls(
            tooling_id=data["tooling_id"],
            display_name=data["display_name"],
            category=data.get("category", ""),
            process=data.get("process", ""),
            description=data.get("description", ""),
            strengths=list(data.get("strengths", [])),
            tradeoffs=list(data.get("tradeoffs", [])),
            typical_materials=list(data.get("typical_materials", [])),
            supports_custom_components=bool(data.get("supports_custom_components", True)),
            supports_off_the_shelf_components=bool(
                data.get("supports_off_the_shelf_components", True)
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain serializable dict."""

        return asdict(self)
