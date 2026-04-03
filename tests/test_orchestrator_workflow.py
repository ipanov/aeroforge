from __future__ import annotations

from pathlib import Path

import yaml

from src.orchestrator.project_settings import build_default_settings
from src.orchestrator.state_manager import StateManager, WorkflowStep
from src.orchestrator.workflow_engine import WorkflowEngine


def _write_profile(path: Path) -> None:
    data = {
        "workflow_profile": {
            "aircraft_type": "paraglider_wing",
            "project_scope": "assembly",
            "top_object_name": "Paraglider_Wing",
            "round_label": "R1",
            "sub_assemblies": [
                {
                    "name": "canopy",
                    "level": 1,
                    "analysis_scope": "aero_structural",
                    "deliverables": ["stitching_plans"],
                    "step_deliverables": {
                        "DRAWING_2D": ["panel_pattern", "three_view"],
                        "VALIDATION": ["validation_report"],
                    },
                }
            ],
            "validation_criteria": {"no_collisions": True},
        }
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_state_manager_enforces_single_active_step(tmp_path: Path) -> None:
    state_file = tmp_path / "workflow_state.json"
    sm = StateManager(state_file)
    sm.initialize(["wing", "fuselage"])

    sm.start_step("wing", WorkflowStep.REQUIREMENTS.value, agent="planner")
    active = sm.get_active_run()
    assert active is not None
    assert active["sub_assembly"] == "wing"

    try:
        sm.start_step("fuselage", WorkflowStep.REQUIREMENTS.value, agent="planner")
    except RuntimeError as exc:
        assert "already running" in str(exc)
    else:
        raise AssertionError("Expected second active step to be blocked")


def test_engine_loads_profile_deliverables(tmp_path: Path) -> None:
    state_file = tmp_path / "workflow_state.json"
    profile_path = tmp_path / "profile.yaml"
    _write_profile(profile_path)

    engine = WorkflowEngine(state_file=state_file)
    state = engine.create_project_from_profile_file(profile_path, "Para Wing")

    canopy = state["sub_assemblies"]["canopy"]
    assert canopy["deliverables"] == ["stitching_plans"]
    assert canopy["steps"]["DRAWING_2D"]["expected_deliverables"] == ["panel_pattern", "three_view"]


def test_project_settings_capture_non_deterministic_choices() -> None:
    settings = build_default_settings(
        project_name="Paper Wing",
        mission_prompt="Design a folded hand-launched paper aircraft",
        aircraft_type="paper_aircraft",
        selected_tooling="hand_tools",
        manufacturing_strategy=["folding_by_hand"],
        material_strategy=["paper"],
        production_strategy=["in_house_build"],
        output_artifacts=["fold_instructions", "crease_pattern"],
    )

    assert settings.aircraft_type == "paper_aircraft"
    assert settings.selected_tooling == "hand_tools"
    assert settings.output_artifacts == ["fold_instructions", "crease_pattern"]
