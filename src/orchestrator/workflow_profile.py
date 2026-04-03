"""Generic workflow profile loader.

The workflow profile is the deterministic contract that results from upstream
LLM/user decisions. The engine executes this profile without hardcoding aircraft
types, tooling strategies, manufacturing techniques, or material choices.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class SubAssemblyProfile:
    """A tracked sub-assembly definition from the project profile."""

    name: str
    level: int = 1
    parent: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    analysis_scope: str = "aero_structural"
    notes: str = ""
    deliverables: list[str] = field(default_factory=list)
    step_deliverables: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class WorkflowProfile:
    """Project-specific workflow definition."""

    aircraft_type: str
    project_scope: str
    top_object_name: str
    round_label: str
    sub_assemblies: list[SubAssemblyProfile] = field(default_factory=list)
    validation_criteria: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowProfile":
        """Construct a workflow profile from YAML data."""

        sub_assemblies = [
            SubAssemblyProfile(
                name=item["name"],
                level=int(item.get("level", 1)),
                parent=item.get("parent"),
                dependencies=list(item.get("dependencies", [])),
                analysis_scope=item.get("analysis_scope", "aero_structural"),
                notes=item.get("notes", ""),
                deliverables=list(item.get("deliverables", [])),
                step_deliverables=dict(item.get("step_deliverables", {})),
            )
            for item in data.get("sub_assemblies", [])
        ]
        return cls(
            aircraft_type=data.get("aircraft_type", "UNSPECIFIED"),
            project_scope=data.get("project_scope", "aircraft"),
            top_object_name=data.get("top_object_name", "top_object"),
            round_label=data.get("round_label", "R1"),
            sub_assemblies=sub_assemblies,
            validation_criteria=dict(data.get("validation_criteria", {})),
        )


def load_workflow_profile(path: Path) -> WorkflowProfile:
    """Load a workflow profile from the tracked YAML file."""

    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    profile_data = data.get("workflow_profile", {})
    return WorkflowProfile.from_dict(profile_data)
