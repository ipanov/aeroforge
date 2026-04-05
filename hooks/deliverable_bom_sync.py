"""PostToolUse hook that keeps the living BOM in sync with deliverable updates."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.bom import BOMSyncReason  # noqa: E402
from src.core.bom_sync import DeliverableEvent, sync_deliverable_event  # noqa: E402


DELIVERABLE_TYPES = {
    ".3mf": "3mf_mesh",
    ".stl": "stl_mesh",
    ".step": "step_model",
    ".stp": "step_model",
    ".dxf": "technical_drawing",
}


def _load_project_context() -> tuple[dict, dict]:
    """Load project settings from the active project's aeroforge.yaml."""
    try:
        from src.orchestrator.project_manager import ProjectManager
        pm = ProjectManager()
        settings_path = pm.get_settings_path()
    except Exception:
        settings_path = PROJECT_ROOT / "aeroforge.yaml"
    if not settings_path.exists():
        return {}, {}
    with open(settings_path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data.get("project", {}), data


def _infer_component_name(path: Path) -> str:
    if path.stem in {"model", "COMPONENT_INFO"} and path.parent.name:
        return path.parent.name
    if path.suffix.lower() in {".3mf", ".stl", ".step", ".stp"} and path.parent.name:
        return path.parent.name
    return path.stem or "unnamed_component"


def _infer_category(path: Path) -> str:
    parts = [part.lower() for part in path.parts]
    for token in ("wing", "fuselage", "empennage", "propulsion", "electronics", "hardware"):
        if token in parts:
            return token
    if "assemblies" in parts:
        return "assembly"
    if "components" in parts:
        return "component"
    return "uncategorized"


def _infer_component_kind(path: Path) -> str:
    normalized = path.as_posix().lower()
    if "/components/" in normalized and path.suffix.lower() in {".yaml", ".yml"}:
        return "off_the_shelf"
    if path.name == "COMPONENT_INFO.md":
        return "off_the_shelf"
    return "custom"


def _infer_deliverable_type(path: Path) -> str:
    if path.name == "COMPONENT_INFO.md":
        return "component_metadata"
    if path.suffix.lower() in {".yaml", ".yml"} and "/components/" in path.as_posix().lower():
        return "procurement_record"
    return DELIVERABLE_TYPES.get(path.suffix.lower(), "")


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    if data.get("tool_name") not in {"Write", "Edit"}:
        return 0

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path")
    if not file_path:
        return 0

    target = Path(file_path)
    deliverable_type = _infer_deliverable_type(target)
    if not deliverable_type:
        return 0

    project_settings, _config = _load_project_context()
    event = DeliverableEvent(
        component_name=_infer_component_name(target),
        category=_infer_category(target),
        component_kind=_infer_component_kind(target),
        deliverable_path=str(target),
        deliverable_type=deliverable_type,
        material="",
        manufacturing_technique="deliverable_update_hook",
        production_strategy="procured_subsystem" if _infer_component_kind(target) == "off_the_shelf" else "in_house_custom",
        location_context=project_settings.get("location_context", {}),
        provider_preferences=project_settings.get("provider_preferences", []),
        sync_reason=(
            BOMSyncReason.PROCUREMENT_REFRESH
            if _infer_component_kind(target) == "off_the_shelf"
            else BOMSyncReason.GEOMETRY_UPDATE
        ),
        sync_basis={
            "hook": "post_tool_use",
            "synced_at": datetime.now(timezone.utc).isoformat(),
        },
        notes=f"Synchronized automatically after {data.get('tool_name')} updated {target.name}.",
    )

    try:
        sync_deliverable_event(
            event,
            project_name=project_settings.get("project_name", "AeroForge"),
        )
    except Exception as exc:
        print(f"[deliverable-bom-sync] warning: {exc}", file=sys.stderr)
        return 0

    print(
        f"[deliverable-bom-sync] synced BOM for {event.component_name} ({event.deliverable_type})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
