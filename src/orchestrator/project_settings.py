"""Project bootstrap settings and initialization helpers.

Important boundary: aircraft type, tooling, manufacturing technique, and
material strategy are intentionally NOT derived in deterministic code here.
They are captured as explicit project decisions and then enforced downstream.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_SETTINGS_FILE = PROJECT_ROOT / "aeroforge.yaml"  # Legacy default


def _resolve_settings_path() -> Path:
    """Resolve the settings file path through the project manager.

    Falls back to the legacy root-level aeroforge.yaml if no active project.
    """
    try:
        from .project_manager import ProjectManager
        pm = ProjectManager()
        return pm.get_settings_path()
    except Exception:
        return PROJECT_SETTINGS_FILE


class ProjectScope(str, Enum):
    """The entry-point scope being designed."""

    COMPONENT = "component"
    ASSEMBLY = "assembly"
    AIRCRAFT = "aircraft"


@dataclass
class ProjectSettings:
    """Tracked project-wide settings for workflow generation."""

    project_name: str
    design_family: str
    current_round: str
    next_round: str
    heavier_than_air: bool
    project_scope: str
    top_object: str
    aircraft_type: str
    mission_prompt: str
    selected_tooling: str
    available_tooling: list[str] = field(default_factory=list)
    manufacturing_strategy: list[str] = field(default_factory=list)
    material_strategy: list[str] = field(default_factory=list)
    production_strategy: list[str] = field(default_factory=list)
    output_artifacts: list[str] = field(default_factory=list)
    location_context: dict[str, Any] = field(default_factory=dict)
    provider_preferences: list[str] = field(default_factory=list)
    workflow_backend: str = "n8n"
    workflow_monitor_port: int = 8787
    n8n_port: int = 5678
    full_aircraft_validation_only: bool = True
    validation_backend: str = "CUDA-capable GPU when available"
    aircraft_type_source: str = "llm_or_user"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to YAML-serializable dict."""

        return asdict(self)


def build_default_settings(
    project_name: str,
    mission_prompt: str,
    aircraft_type: Optional[str] = None,
    project_scope: ProjectScope = ProjectScope.AIRCRAFT,
    top_object: str = "Iva_Aeroforge",
    design_family: str = "AIR4",
    current_round: str = "R4",
    next_round: str = "R5",
    selected_tooling: str = "UNSPECIFIED",
    available_tooling: Optional[list[str]] = None,
    manufacturing_strategy: Optional[list[str]] = None,
    material_strategy: Optional[list[str]] = None,
    production_strategy: Optional[list[str]] = None,
    output_artifacts: Optional[list[str]] = None,
    location_context: Optional[dict[str, Any]] = None,
    provider_preferences: Optional[list[str]] = None,
) -> ProjectSettings:
    """Create a default project settings object for the current project."""

    selected_aircraft_type = aircraft_type or "UNSPECIFIED"
    available = available_tooling or ([selected_tooling] if selected_tooling != "UNSPECIFIED" else [])

    return ProjectSettings(
        project_name=project_name,
        design_family=design_family,
        current_round=current_round,
        next_round=next_round,
        heavier_than_air=True,
        project_scope=project_scope.value,
        top_object=top_object,
        aircraft_type=selected_aircraft_type,
        mission_prompt=mission_prompt,
        selected_tooling=selected_tooling,
        available_tooling=available,
        manufacturing_strategy=manufacturing_strategy or [],
        material_strategy=material_strategy or [],
        production_strategy=production_strategy or [],
        output_artifacts=output_artifacts or [],
        location_context=location_context or {},
        provider_preferences=provider_preferences or [],
        notes=[
            "Aircraft type must be supplied by a user or LLM classification step.",
            "Tooling and manufacturing strategy must be supplied by a user or LLM decision step.",
            "Location context should be captured during initialization to guide procurement.",
            "The workflow must expose the currently running step at all times.",
            "Synthetic wind tunnel and structural validation are run on the assembled top object only.",
        ],
    )


def save_project_settings(
    settings: ProjectSettings,
    path: Optional[Path] = None,
) -> Path:
    """Persist project settings to the tracked YAML file."""

    target = path or _resolve_settings_path()
    existing: dict[str, Any] = {}
    if target.exists():
        with open(target, "r", encoding="utf-8") as handle:
            existing = yaml.safe_load(handle) or {}
    data = {**existing, "project": settings.to_dict()}
    with open(target, "w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)
    return target


def load_project_settings(path: Optional[Path] = None) -> Optional[dict[str, Any]]:
    """Load project settings if present."""

    target = path or _resolve_settings_path()
    if not target.exists():
        return None
    with open(target, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)
