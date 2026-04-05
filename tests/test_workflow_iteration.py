"""Tests for workflow iteration, rejection, rework, and feedback flows.

Uses the new tree-based architecture with DesignStep per node.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.orchestrator.state_manager import (
    DesignStep,
    NodeType,
    StateManager,
    StepStatus,
)
from src.orchestrator.workflow_engine import WorkflowEngine


@pytest.fixture
def engine(tmp_path: Path) -> WorkflowEngine:
    """WorkflowEngine with isolated state and a simple project."""
    state_file = tmp_path / "workflow_state.json"
    e = WorkflowEngine(state_file=state_file)
    e.create_project(
        aircraft_type="SAILPLANE",
        project_name="Test Sailplane",
    )
    e._sm.set_project_phase("DESIGN", force=True)
    return e


@pytest.fixture
def sm(tmp_path: Path) -> StateManager:
    """StateManager with isolated state and two component nodes."""
    state_file = tmp_path / "state.json"
    s = StateManager(state_file)
    s.initialize([])
    s.add_node("wing", NodeType.COMPONENT)
    s.add_node("fuselage", NodeType.COMPONENT)
    s.set_project_phase("DESIGN", force=True)
    return s


class TestStepRejection:

    def test_reject_completed_step_resets_to_pending(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

        sm.start_step("wing", DesignStep.STRUCTURAL_REVIEW.value)
        sm.complete_step("wing", DesignStep.STRUCTURAL_REVIEW.value)

        sm.reject_step("wing", DesignStep.STRUCTURAL_REVIEW.value, reason="Insufficient data")
        record = sm.get_step("wing", DesignStep.STRUCTURAL_REVIEW.value)
        assert record["status"] == StepStatus.PENDING.value
        assert "REJECTED" in record["notes"]

    def test_rejection_preserves_history(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value, output_files=["proposal.md"])

        sm.reject_step("wing", DesignStep.AERO_PROPOSAL.value, reason="Missing constraints",
                        rework_notes="Add weight budget")

        history = sm.get_step_history("wing", DesignStep.AERO_PROPOSAL.value)
        assert len(history) == 1
        assert history[0]["action"] == "rejected"
        assert history[0]["reason"] == "Missing constraints"
        assert history[0]["rework_notes"] == "Add weight budget"

    def test_multiple_rejections_accumulate_history(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.reject_step("wing", DesignStep.AERO_PROPOSAL.value, reason="First rejection")

        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.reject_step("wing", DesignStep.AERO_PROPOSAL.value, reason="Second rejection")

        history = sm.get_step_history("wing", DesignStep.AERO_PROPOSAL.value)
        assert len(history) == 2

    def test_rejection_resets_current_step(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

        node = sm.get_node("wing")
        assert node["current_design_step"] == DesignStep.STRUCTURAL_REVIEW.value

        sm.reject_step("wing", DesignStep.AERO_PROPOSAL.value, reason="Redo it")
        node = sm.get_node("wing")
        assert node["current_design_step"] == DesignStep.AERO_PROPOSAL.value

    def test_rejection_clears_active_run(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        assert len(sm.get_active_runs()) == 1

        sm.reject_step("wing", DesignStep.AERO_PROPOSAL.value, reason="Wrong")
        assert len(sm.get_active_runs()) == 0


class TestUserFeedback:

    def test_record_feedback_preserves_step_status(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.record_user_feedback("wing", DesignStep.AERO_PROPOSAL.value, "I want higher AR")

        record = sm.get_step("wing", DesignStep.AERO_PROPOSAL.value)
        assert record["status"] == StepStatus.RUNNING.value

    def test_feedback_stored_in_history(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.record_user_feedback("wing", DesignStep.AERO_PROPOSAL.value, "Make it elliptical")

        history = sm.get_step_history("wing", DesignStep.AERO_PROPOSAL.value)
        assert len(history) == 1
        assert history[0]["action"] == "user_feedback"
        assert history[0]["feedback"] == "Make it elliptical"

    def test_multiple_feedback_entries(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.record_user_feedback("wing", DesignStep.AERO_PROPOSAL.value, "Higher AR")
        sm.record_user_feedback("wing", DesignStep.AERO_PROPOSAL.value, "Also thinner airfoil")

        history = sm.get_step_history("wing", DesignStep.AERO_PROPOSAL.value)
        assert len(history) == 2


class TestWorkflowEngineSummary:

    def test_get_workflow_summary_returns_string(self, engine: WorkflowEngine) -> None:
        summary = engine.get_workflow_summary()
        assert isinstance(summary, str)
        assert "Test Sailplane" in summary

    def test_summary_shows_step_statuses(self, engine: WorkflowEngine) -> None:
        engine.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        engine.complete_step("wing", DesignStep.AERO_PROPOSAL.value)
        summary = engine.get_workflow_summary()
        # Should contain status indicators
        assert len(summary) > 50


class TestNextRecommendedAction:

    def test_recommendation_includes_agent(self, engine: WorkflowEngine) -> None:
        action = engine.get_next_recommended_action()
        # First pending step should be AERO_PROPOSAL
        assert action.get("step") == DesignStep.AERO_PROPOSAL.value or "action" in action

    def test_recommendation_includes_rework_context(self, engine: WorkflowEngine) -> None:
        engine.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        engine.complete_step("wing", DesignStep.AERO_PROPOSAL.value)
        engine.reject_step("wing", DesignStep.AERO_PROPOSAL.value, reason="Missing data",
                           rework_notes="Add thermal requirements")

        action = engine.get_next_recommended_action()
        if "rework_context" in action:
            assert "Missing data" in action["rework_context"]

    def test_returns_recommendation_for_fresh_engine(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            e = WorkflowEngine(state_file=Path(td) / "state.json")
            action = e.get_next_recommended_action()
            assert "action" in action or "step" in action


class TestEngineRejectStep:

    def test_engine_reject_step(self, engine: WorkflowEngine) -> None:
        engine.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        engine.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

        engine.reject_step("wing", DesignStep.AERO_PROPOSAL.value,
                           reason="Too vague",
                           rework_notes="Add specific dimensions")

        state = engine.load_project()
        nodes = state.get("nodes", {})
        aero = nodes["wing"]["design_cycle"][DesignStep.AERO_PROPOSAL.value]
        assert aero["status"] == StepStatus.PENDING.value

    def test_engine_record_user_feedback(self, engine: WorkflowEngine) -> None:
        engine.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        engine.record_user_feedback("wing", DesignStep.AERO_PROPOSAL.value,
                                     "I want a 3m wingspan minimum")

        state = engine.load_project()
        nodes = state.get("nodes", {})
        aero = nodes["wing"]["design_cycle"][DesignStep.AERO_PROPOSAL.value]
        assert aero["status"] == StepStatus.RUNNING.value


class TestIteration:

    def test_start_iteration_resets_design_cycle(self, engine: WorkflowEngine) -> None:
        engine.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        engine.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

        engine.start_iteration("wing", round_label="R2")

        state = engine.load_project()
        nodes = state.get("nodes", {})
        wing = nodes["wing"]
        assert wing["iteration"] >= 2
        assert wing["design_cycle"][DesignStep.AERO_PROPOSAL.value]["status"] == StepStatus.PENDING.value


class TestDeliverableName:

    def test_basic_format(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        name = sm.deliverable_name("wing", DesignStep.AERO_PROPOSAL.value)
        assert name == "AERO_PROPOSAL_R1.md"

    def test_custom_extension(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        name = sm.deliverable_name("wing", DesignStep.AERO_PROPOSAL.value, ext=".dxf")
        assert name == "AERO_PROPOSAL_R1.dxf"

    def test_round_increments_after_new_iteration(self, sm: StateManager) -> None:
        # R1
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        assert sm.deliverable_name("wing", DesignStep.AERO_PROPOSAL.value) == "AERO_PROPOSAL_R1.md"
        sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

        # Structural review at R1
        sm.start_step("wing", DesignStep.STRUCTURAL_REVIEW.value)
        assert sm.deliverable_name("wing", DesignStep.STRUCTURAL_REVIEW.value) == "STRUCTURAL_REVIEW_R1.md"
        sm.complete_step("wing", DesignStep.STRUCTURAL_REVIEW.value)

        # New round via start_new_iteration (cascade or user rejection)
        # agent_round is NOT reset — keeps counting monotonically
        sm.start_new_iteration("wing")
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        # Was R1, now R2 (agent_round incremented on AERO_PROPOSAL start)
        assert sm.deliverable_name("wing", DesignStep.AERO_PROPOSAL.value) == "AERO_PROPOSAL_R2.md"

    def test_round_increments_after_validation_cascade(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)  # R1
        sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

        # Simulate validation cascade — start new iteration
        sm.start_new_iteration("wing")
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)  # R2 (monotonic)
        name = sm.deliverable_name("wing", DesignStep.AERO_PROPOSAL.value)
        assert name == "AERO_PROPOSAL_R2.md"  # round keeps counting up

    def test_structural_review_uses_same_round(self, sm: StateManager) -> None:
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.start_step("wing", DesignStep.STRUCTURAL_REVIEW.value)
        # Same round as the aero proposal that preceded it
        name = sm.deliverable_name("wing", DesignStep.STRUCTURAL_REVIEW.value)
        assert name == "STRUCTURAL_REVIEW_R1.md"

    def test_different_nodes_track_independently(self, sm: StateManager) -> None:
        # Wing R1
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        sm.complete_step("wing", DesignStep.AERO_PROPOSAL.value)
        # Wing cascade to R2
        sm.start_new_iteration("wing")
        sm.start_step("wing", DesignStep.AERO_PROPOSAL.value)

        # Fuselage still at R1
        sm.start_step("fuselage", DesignStep.AERO_PROPOSAL.value)

        assert sm.deliverable_name("wing", DesignStep.AERO_PROPOSAL.value) == "AERO_PROPOSAL_R2.md"
        assert sm.deliverable_name("fuselage", DesignStep.AERO_PROPOSAL.value) == "AERO_PROPOSAL_R1.md"


class TestValidationCascade:

    def test_cascade_increments_iteration(self, engine: WorkflowEngine) -> None:
        engine.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        engine.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

        result = engine.handle_validation_cascade(
            ["wing"], reason="CFD trim mismatch"
        )
        assert result["wing"] == 2  # iteration 1 -> 2

    def test_cascade_resets_steps(self, engine: WorkflowEngine) -> None:
        engine.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        engine.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

        engine.handle_validation_cascade(["wing"], reason="test")

        state = engine.load_project()
        wing = state["nodes"]["wing"]
        aero = wing["design_cycle"][DesignStep.AERO_PROPOSAL.value]
        assert aero["status"] == StepStatus.PENDING.value

    def test_cascade_rolls_back_phase(self, engine: WorkflowEngine) -> None:
        engine._sm.set_project_phase("VALIDATION", force=True)

        engine.handle_validation_cascade(["wing"], reason="test")

        state = engine.load_project()
        assert state["project_phase"] == "DESIGN"

    def test_cascade_preserves_other_nodes(self, engine: WorkflowEngine) -> None:
        engine.start_step("wing", DesignStep.AERO_PROPOSAL.value)
        engine.complete_step("wing", DesignStep.AERO_PROPOSAL.value)

        engine.start_step("fuselage", DesignStep.AERO_PROPOSAL.value)
        engine.complete_step("fuselage", DesignStep.AERO_PROPOSAL.value)

        engine.handle_validation_cascade(["wing"], reason="wing only")

        state = engine.load_project()
        # Wing reset
        assert state["nodes"]["wing"]["design_cycle"][DesignStep.AERO_PROPOSAL.value]["status"] == StepStatus.PENDING.value
        # Fuselage untouched
        assert state["nodes"]["fuselage"]["design_cycle"][DesignStep.AERO_PROPOSAL.value]["status"] == StepStatus.DONE.value

    def test_cascade_multiple_nodes(self, engine: WorkflowEngine) -> None:
        result = engine.handle_validation_cascade(
            ["wing", "fuselage"], reason="full redesign"
        )
        assert result["wing"] == 2
        assert result["fuselage"] == 2
