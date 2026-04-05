"""Tests for the n8n visual workflow builder."""

import pytest

from src.orchestrator.n8n_workflow_builder import N8nWorkflowBuilder


@pytest.fixture
def sample_state():
    """Minimal workflow state for testing."""
    return {
        "project": "Test Project",
        "project_phase": "DESIGN",
        "nodes": {
            "wing": {
                "type": "assembly",
                "level": 1,
                "parent": None,
                "children": ["wing_panel"],
                "iteration": 2,
                "round_label": "R2",
                "agent_round": 1,
                "design_cycle": {
                    "AERO_PROPOSAL": {"status": "done", "agent": "aerodynamicist", "history": []},
                    "STRUCTURAL_REVIEW": {"status": "done", "agent": "structural-engineer", "history": []},
                    "AERO_RESPONSE": {"status": "running", "agent": "aerodynamicist", "history": []},
                    "CONSENSUS": {"status": "pending", "history": []},
                    "DRAWING_2D": {"status": "pending", "history": []},
                    "MODEL_3D": {"status": "pending", "history": []},
                    "OUTPUT": {"status": "pending", "history": []},
                },
            },
            "wing_panel": {
                "type": "component",
                "level": 2,
                "parent": "wing",
                "children": [],
                "iteration": 1,
                "round_label": "R1",
                "agent_round": 0,
                "design_cycle": {
                    "AERO_PROPOSAL": {"status": "pending", "history": []},
                    "STRUCTURAL_REVIEW": {"status": "pending", "history": []},
                    "AERO_RESPONSE": {"status": "pending", "history": []},
                    "CONSENSUS": {"status": "pending", "history": []},
                    "DRAWING_2D": {"status": "pending", "history": []},
                    "MODEL_3D": {"status": "pending", "history": []},
                    "OUTPUT": {"status": "pending", "history": []},
                },
            },
            "fuselage": {
                "type": "component",
                "level": 1,
                "parent": None,
                "children": [],
                "iteration": 1,
                "round_label": "R1",
                "agent_round": 0,
                "design_cycle": {
                    "AERO_PROPOSAL": {
                        "status": "done",
                        "agent": "aerodynamicist",
                        "history": [{"action": "rejected", "reason": "too simple"}],
                    },
                    "STRUCTURAL_REVIEW": {"status": "pending", "history": []},
                    "AERO_RESPONSE": {"status": "pending", "history": []},
                    "CONSENSUS": {"status": "pending", "history": []},
                    "DRAWING_2D": {"status": "pending", "history": []},
                    "MODEL_3D": {"status": "pending", "history": []},
                    "OUTPUT": {"status": "pending", "history": []},
                },
            },
        },
        "active_runs": [
            {
                "node": "wing",
                "step": "AERO_RESPONSE",
                "agent": "aerodynamicist",
                "started_at": "2026-04-05T10:00:00Z",
            },
        ],
        "validation": {
            "cfd": {},
            "fea": {},
            "convergence": {
                "ld_ratio_met": False,
                "structural_sf_met": True,
            },
        },
    }


class TestSkeletonWorkflow:
    def test_skeleton_has_required_fields(self):
        builder = N8nWorkflowBuilder("Test")
        wf = builder.build_skeleton("REQUIREMENTS")
        assert wf["name"] == "AeroForge Dashboard - Test"
        assert "nodes" in wf
        assert "connections" in wf
        assert "settings" in wf

    def test_skeleton_has_trigger_node(self):
        builder = N8nWorkflowBuilder("Test")
        wf = builder.build_skeleton()
        trigger = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.manualTrigger"]
        assert len(trigger) == 1

    def test_skeleton_has_phase_stickies(self):
        builder = N8nWorkflowBuilder("Test")
        wf = builder.build_skeleton("RESEARCH")
        stickies = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.stickyNote"]
        # 6 phases + active banner + placeholder + validation
        assert len(stickies) >= 6

    def test_skeleton_marks_active_phase(self):
        builder = N8nWorkflowBuilder("Test")
        wf = builder.build_skeleton("RESEARCH")
        stickies = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.stickyNote"]
        active = [s for s in stickies if "ACTIVE" in s["parameters"]["content"] and "RESEARCH" in s["parameters"]["content"]]
        assert len(active) >= 1


class TestFullWorkflow:
    def test_full_has_required_fields(self, sample_state):
        builder = N8nWorkflowBuilder("Test Project")
        wf = builder.build_full(sample_state)
        assert wf["name"] == "AeroForge Dashboard - Test Project"
        assert len(wf["nodes"]) > 0

    def test_full_has_phase_row(self, sample_state):
        builder = N8nWorkflowBuilder("Test Project")
        wf = builder.build_full(sample_state)
        stickies = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.stickyNote"]
        phase_stickies = [s for s in stickies if "**DESIGN**" in s["parameters"]["content"]]
        assert len(phase_stickies) >= 1

    def test_full_highlights_active_step(self, sample_state):
        builder = N8nWorkflowBuilder("Test Project")
        wf = builder.build_full(sample_state)
        stickies = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.stickyNote"]
        # Active banner should mention wing and AERO_RESPONSE
        banners = [s for s in stickies if "ACTIVE NOW" in s["parameters"]["content"]]
        assert len(banners) == 1
        assert "wing" in banners[0]["parameters"]["content"]
        assert "AERO_RESPONSE" in banners[0]["parameters"]["content"]

    def test_full_shows_all_nodes(self, sample_state):
        builder = N8nWorkflowBuilder("Test Project")
        wf = builder.build_full(sample_state)
        stickies = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.stickyNote"]
        contents = " ".join(s["parameters"]["content"] for s in stickies)
        assert "wing" in contents
        assert "wing_panel" in contents
        assert "fuselage" in contents

    def test_full_shows_rejection_count(self, sample_state):
        builder = N8nWorkflowBuilder("Test Project")
        wf = builder.build_full(sample_state)
        stickies = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.stickyNote"]
        # Fuselage AERO_PROPOSAL has 1 rejection
        rejection_stickies = [s for s in stickies if "1R" in s["parameters"]["content"]]
        assert len(rejection_stickies) >= 1

    def test_full_shows_convergence(self, sample_state):
        builder = N8nWorkflowBuilder("Test Project")
        wf = builder.build_full(sample_state)
        stickies = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.stickyNote"]
        conv_stickies = [s for s in stickies if "Convergence" in s["parameters"]["content"]]
        assert len(conv_stickies) == 1

    def test_full_hierarchy_order(self, sample_state):
        builder = N8nWorkflowBuilder("Test Project")
        # wing_panel should come after wing (child under parent)
        order = builder._sort_by_hierarchy(sample_state["nodes"])
        assert order.index("wing") < order.index("wing_panel")

    def test_no_active_runs(self, sample_state):
        sample_state["active_runs"] = []
        builder = N8nWorkflowBuilder("Test Project")
        wf = builder.build_full(sample_state)
        stickies = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.stickyNote"]
        banners = [s for s in stickies if "ACTIVE NOW" in s["parameters"]["content"]]
        assert len(banners) == 0
        idle = [s for s in stickies if "No step running" in s["parameters"]["content"]]
        assert len(idle) == 1


class TestEdgeCases:
    def test_empty_nodes(self):
        builder = N8nWorkflowBuilder("Empty")
        state = {"project": "Empty", "project_phase": "REQUIREMENTS", "nodes": {}}
        wf = builder.build_full(state)
        assert len(wf["nodes"]) >= 1  # At least the trigger

    def test_off_shelf_node(self):
        builder = N8nWorkflowBuilder("Test")
        state = {
            "project": "Test",
            "project_phase": "DESIGN",
            "nodes": {
                "servo": {
                    "type": "off_shelf",
                    "level": 1,
                    "parent": None,
                    "children": [],
                    "design_cycle": None,
                    "iteration": 1,
                    "round_label": "R1",
                    "agent_round": 0,
                },
            },
            "active_runs": [],
            "validation": {},
        }
        wf = builder.build_full(state)
        stickies = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.stickyNote"]
        off_shelf = [s for s in stickies if "off-shelf" in s["parameters"]["content"]]
        assert len(off_shelf) == 1
