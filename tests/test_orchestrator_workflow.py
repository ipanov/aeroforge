"""Tests for the workflow orchestrator — tree-based architecture.

Tests the state manager, workflow engine, and project settings with
the hierarchical node tree (DesignStep per node, ProjectPhase at top).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from src.orchestrator.project_settings import build_default_settings
from src.orchestrator.state_manager import (
    DesignStep,
    NodeType,
    ProjectPhase,
    StateManager,
    StepStatus,
)
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


def test_state_manager_node_tree(tmp_path: Path) -> None:
    """Test that nodes form a proper tree with parent/children."""
    state_file = tmp_path / "state.json"
    sm = StateManager(state_file)
    sm.initialize([])  # Empty init

    sm.add_node("plane", NodeType.ASSEMBLY, children=["wing", "fuselage"])
    sm.add_node("wing", NodeType.COMPONENT, parent="plane")
    sm.add_node("fuselage", NodeType.COMPONENT, parent="plane")
    sm.add_node("servo", NodeType.OFF_SHELF, parent="wing")

    assert "wing" in sm.get_children("plane")
    assert "fuselage" in sm.get_children("plane")
    assert sm.get_parent("wing") == "plane"
    assert sm.get_node("servo")["type"] == NodeType.OFF_SHELF.value
    assert sm.get_node("servo").get("design_cycle") is None


def test_state_manager_design_step_sequencing(tmp_path: Path) -> None:
    """Test that design steps follow the correct order per node."""
    state_file = tmp_path / "state.json"
    sm = StateManager(state_file)
    sm.initialize([])
    sm.add_node("wing", NodeType.COMPONENT)

    # First design step should be AERO_PROPOSAL
    node = sm.get_node("wing")
    assert node["current_design_step"] == DesignStep.AERO_PROPOSAL.value

    # Start and complete AERO_PROPOSAL
    sm.start_step("wing", DesignStep.AERO_PROPOSAL.value, agent="aerodynamicist")
    assert len(sm.get_active_runs()) == 1

    sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value, notes="Proposal done")
    assert len(sm.get_active_runs()) == 0

    # Next step should be STRUCTURAL_REVIEW
    node = sm.get_node("wing")
    assert node["current_design_step"] == DesignStep.STRUCTURAL_REVIEW.value


def test_state_manager_parallel_active_runs(tmp_path: Path) -> None:
    """Test that multiple nodes can have active steps simultaneously."""
    state_file = tmp_path / "state.json"
    sm = StateManager(state_file)
    sm.initialize([])
    sm.add_node("wing", NodeType.COMPONENT)
    sm.add_node("fuselage", NodeType.COMPONENT)

    sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
    sm.start_step("fuselage", DesignStep.AERO_PROPOSAL.value)

    runs = sm.get_active_runs()
    assert len(runs) == 2
    run_nodes = {r["node"] for r in runs}
    assert "wing" in run_nodes
    assert "fuselage" in run_nodes


def test_state_manager_approve_drawing(tmp_path: Path) -> None:
    """Test drawing approval gate."""
    state_file = tmp_path / "state.json"
    sm = StateManager(state_file)
    sm.initialize([])
    sm.add_node("wing", NodeType.COMPONENT)

    # Complete through to DRAWING_2D
    for step in [DesignStep.AERO_PROPOSAL, DesignStep.STRUCTURAL_REVIEW,
                 DesignStep.AERO_RESPONSE, DesignStep.CONSENSUS]:
        sm.start_step("wing", step.value)
        sm.complete_step("wing", step.value)

    sm.start_step("wing", DesignStep.DRAWING_2D.value)
    sm.complete_step("wing", DesignStep.DRAWING_2D.value)

    assert not sm.is_drawing_approved("wing")
    sm.approve_drawing("wing")
    assert sm.is_drawing_approved("wing")


def test_state_manager_design_phase_complete(tmp_path: Path) -> None:
    """Test that design phase checks all non-off-shelf drawings."""
    state_file = tmp_path / "state.json"
    sm = StateManager(state_file)
    sm.initialize([])
    sm.add_node("wing", NodeType.COMPONENT)
    sm.add_node("servo", NodeType.OFF_SHELF, parent="wing")

    assert not sm.check_design_phase_complete()

    # Complete wing design cycle through DRAWING_2D and approve
    for step in DesignStep:
        if step == DesignStep.MODEL_3D:
            break  # Stop before implementation steps
        sm.start_step("wing", step.value)
        sm.complete_step("wing", step.value)

    sm.approve_drawing("wing")
    assert sm.check_design_phase_complete()


def test_state_manager_implementation_order(tmp_path: Path) -> None:
    """Test that implementation order is leaves-first."""
    state_file = tmp_path / "state.json"
    sm = StateManager(state_file)
    sm.initialize([])
    sm.add_node("plane", NodeType.ASSEMBLY, children=["wing", "fuselage"])
    sm.add_node("wing", NodeType.ASSEMBLY, parent="plane", children=["panel_1"])
    sm.add_node("panel_1", NodeType.COMPONENT, parent="wing")
    sm.add_node("fuselage", NodeType.COMPONENT, parent="plane")

    order = sm.get_implementation_order()
    # Leaves first: panel_1 and fuselage before wing, wing before plane
    assert order.index("panel_1") < order.index("wing")
    assert order.index("fuselage") < order.index("plane")
    assert order.index("wing") < order.index("plane")


def test_state_manager_invalidate_node(tmp_path: Path) -> None:
    """Test that invalidating a node resets its design cycle."""
    state_file = tmp_path / "state.json"
    sm = StateManager(state_file)
    sm.initialize([])
    sm.add_node("wing", NodeType.COMPONENT)

    # Complete some steps
    sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
    sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

    # Invalidate
    sm.invalidate_node("wing")
    node = sm.get_node("wing")
    assert node["current_design_step"] == DesignStep.AERO_PROPOSAL.value
    aero = node["design_cycle"][DesignStep.AERO_PROPOSAL.value]
    assert aero["status"] == StepStatus.PENDING.value


def test_engine_loads_profile_deliverables(tmp_path: Path) -> None:
    state_file = tmp_path / "workflow_state.json"
    profile_path = tmp_path / "profile.yaml"
    _write_profile(profile_path)

    engine = WorkflowEngine(state_file=state_file)
    state = engine.create_project_from_profile_file(profile_path, "Para Wing")

    # Profile creates nodes, not sub_assemblies
    assert "canopy" in state.get("nodes", {})


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
