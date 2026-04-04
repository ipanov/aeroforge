"""Interactive project initialization wizard.

The wizard captures user/LLM decisions about aircraft type, tooling,
manufacturing, materials, and production strategy. It also detects local
hardware to auto-suggest system-level providers (CFD, FEA, airfoil).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import yaml

from .project_settings import ProjectScope, ProjectSettings, build_default_settings

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WIZARD_CATALOG = PROJECT_ROOT / "config" / "project_init_options.yaml"


def load_wizard_catalog(path: Optional[Path] = None) -> dict[str, Any]:
    """Load the data-driven wizard catalog."""

    target = path or WIZARD_CATALOG
    with open(target, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _print_options(title: str, options: list[dict[str, Any]]) -> None:
    print(f"\n{title}")
    for item in options:
        print(f"  - {item['id']}: {item['label']}")
        pros = "; ".join(item.get("pros", []))
        cons = "; ".join(item.get("cons", []))
        if pros:
            print(f"    pros: {pros}")
        if cons:
            print(f"    cons: {cons}")


def _ask_value(prompt: str, default: Optional[str] = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    if not value and default is not None:
        return default
    return value


def _ask_list(prompt: str, default: Optional[list[str]] = None) -> list[str]:
    default_text = ",".join(default or [])
    value = _ask_value(prompt, default_text)
    return [item.strip() for item in value.split(",") if item.strip()]


def run_project_init_wizard(
    *,
    project_name: str,
    mission_prompt: str,
    aircraft_type: Optional[str] = None,
    tooling: Optional[str] = None,
    manufacturing: Optional[list[str]] = None,
    materials: Optional[list[str]] = None,
    production: Optional[list[str]] = None,
    outputs: Optional[list[str]] = None,
    scope: str = ProjectScope.AIRCRAFT.value,
    top_object: str = "Aircraft",
    project_code: str = "PRJ1",
    current_round: str = "R1",
    next_round: str = "R2",
) -> ProjectSettings:
    """Guide the user through initialization without auto-deciding project strategy."""

    # -- Hardware detection (system-level providers) -------------------------
    try:
        from src.providers.hardware import detect_hardware
        hw = detect_hardware()
        print(f"\n--- Detected Hardware ---\n{hw.summary()}\n")
        logger.info("Hardware detection: %s", hw.summary())
    except Exception as exc:
        logger.debug("Hardware detection failed: %s", exc)
        hw = None

    catalog = load_wizard_catalog()
    _print_options("Tooling options", catalog.get("tooling_options", []))
    _print_options("Manufacturing technique options", catalog.get("manufacturing_techniques", []))
    _print_options("Material options", catalog.get("materials", []))
    _print_options("Production strategy options", catalog.get("production_modes", []))
    _print_options("Output artifact options", catalog.get("output_artifacts", []))

    selected_aircraft_type = aircraft_type or _ask_value(
        "Aircraft type already decided by user/LLM",
        "UNSPECIFIED",
    )
    selected_tooling = tooling or _ask_value("Preferred tooling", "UNSPECIFIED")
    selected_manufacturing = manufacturing or _ask_list(
        "Preferred manufacturing techniques (comma separated)",
        [],
    )
    selected_materials = materials or _ask_list(
        "Preferred material strategy (comma separated)",
        [],
    )
    selected_production = production or _ask_list(
        "Production strategy (comma separated)",
        [],
    )
    selected_outputs = outputs or _ask_list(
        "Output artifacts to generate (comma separated)",
        [],
    )

    return build_default_settings(
        project_name=project_name,
        mission_prompt=mission_prompt,
        aircraft_type=selected_aircraft_type,
        project_scope=ProjectScope(scope),
        top_object=top_object,
        design_family=project_code,
        current_round=current_round,
        next_round=next_round,
        selected_tooling=selected_tooling,
        available_tooling=[selected_tooling] if selected_tooling and selected_tooling != "UNSPECIFIED" else [],
        manufacturing_strategy=selected_manufacturing,
        material_strategy=selected_materials,
        production_strategy=selected_production,
        output_artifacts=selected_outputs,
    )
