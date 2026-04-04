"""Persistent state manager for the design workflow orchestrator.

Tracks the state of every node (component / assembly / off-shelf) across
design iterations using a hierarchical tree.  Multiple independent nodes
may run in parallel.

State version 3 — hierarchical node tree with split enums.
"""

from __future__ import annotations

import json
import time
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = PROJECT_ROOT / ".claude" / "workflow_state.json"  # Legacy default
DASHBOARD_FILE = PROJECT_ROOT / "exports" / "workflow_dashboard.html"  # Legacy default
STATE_VERSION = 3


def _resolve_state_path() -> Path:
    """Resolve the state file path through the project manager.

    Falls back to the legacy .claude/workflow_state.json if no active project.
    """
    try:
        from .project_manager import ProjectManager
        pm = ProjectManager()
        return pm.get_state_path()
    except Exception:
        return STATE_FILE


def _resolve_dashboard_path() -> Path:
    """Resolve the dashboard path through the project manager."""
    try:
        from .project_manager import ProjectManager
        pm = ProjectManager()
        return pm.get_dashboard_path()
    except Exception:
        return DASHBOARD_FILE


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class StepStatus(str, Enum):
    """Status of a single workflow step."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


class DesignStep(str, Enum):
    """Per-node design cycle steps."""

    AERO_PROPOSAL = "AERO_PROPOSAL"
    STRUCTURAL_REVIEW = "STRUCTURAL_REVIEW"
    AERO_RESPONSE = "AERO_RESPONSE"
    CONSENSUS = "CONSENSUS"
    DRAWING_2D = "DRAWING_2D"
    MODEL_3D = "MODEL_3D"
    OUTPUT = "OUTPUT"


class ProjectPhase(str, Enum):
    """Top-level project phases."""

    REQUIREMENTS = "REQUIREMENTS"
    RESEARCH = "RESEARCH"
    DESIGN = "DESIGN"
    IMPLEMENTATION = "IMPLEMENTATION"
    VALIDATION = "VALIDATION"
    RELEASE = "RELEASE"


class NodeType(str, Enum):
    """Classification for tree nodes."""

    COMPONENT = "component"
    ASSEMBLY = "assembly"
    OFF_SHELF = "off_shelf"


# ---------------------------------------------------------------------------
# Backward-compatibility aliases
# ---------------------------------------------------------------------------


class WorkflowStep(str, Enum):
    """Legacy alias — maps old 11-step enum onto new split enums.

    Kept so that existing imports (``from state_manager import WorkflowStep``)
    continue to work without immediate refactor.
    """

    # Project phases
    REQUIREMENTS = "REQUIREMENTS"
    RESEARCH = "RESEARCH"
    VALIDATION = "VALIDATION"
    RELEASE = "RELEASE"

    # Design cycle steps
    AERO_PROPOSAL = "AERO_PROPOSAL"
    STRUCTURAL_REVIEW = "STRUCTURAL_REVIEW"
    AERO_RESPONSE = "AERO_RESPONSE"
    CONSENSUS = "CONSENSUS"
    DRAWING_2D = "DRAWING_2D"
    MODEL_3D = "MODEL_3D"
    MESH = "OUTPUT"  # renamed


WORKFLOW_STEPS = list(WorkflowStep)

DESIGN_STEPS = list(DesignStep)

DESIGN_STEP_ORDER = [s.value for s in DesignStep]

AGENT_ROUND_STEPS = {
    DesignStep.AERO_PROPOSAL.value,
    DesignStep.STRUCTURAL_REVIEW.value,
    DesignStep.AERO_RESPONSE.value,
    DesignStep.CONSENSUS.value,
}


# ---------------------------------------------------------------------------
# State factories
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """Current UTC time in ISO-8601."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _new_design_step(step: DesignStep) -> dict[str, Any]:
    """Create a fresh design-cycle step record."""
    return {
        "name": step.value,
        "status": StepStatus.PENDING.value,
        "agent": None,
        "output_files": [],
        "expected_deliverables": [],
        "notes": "",
        "started_at": None,
        "completed_at": None,
        "history": [],
    }


def _new_design_cycle() -> dict[str, dict[str, Any]]:
    """Return a full design cycle (7 steps) with all steps pending."""
    return {s.value: _new_design_step(s) for s in DesignStep}


def _new_phase_record() -> dict[str, Any]:
    """Create a fresh project-phase record (requirements, research, etc.)."""
    return {
        "status": StepStatus.PENDING.value,
        "started_at": None,
        "completed_at": None,
        "output_files": [],
        "notes": "",
        "history": [],
    }


def _new_node(
    name: str,
    node_type: NodeType,
    parent: Optional[str] = None,
    children: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Create a fresh node record."""
    has_design_cycle = node_type != NodeType.OFF_SHELF

    return {
        "name": name,
        "type": node_type.value,
        "parent": parent,
        "children": children or [],
        "design_cycle": _new_design_cycle() if has_design_cycle else None,
        "current_design_step": DesignStep.AERO_PROPOSAL.value if has_design_cycle else None,
        "iteration": 1,
        "max_agent_rounds": 3,
        "agent_round": 0,
        "artifacts": [],
        "deliverables": [],
        "step_deliverables": {},
    }


def _convergence_defaults() -> dict[str, Any]:
    """Default convergence criteria and their status."""
    return {
        "ld_ratio_met": False,
        "interference_drag_met": False,
        "static_margin_met": False,
        "control_authority_met": False,
        "structural_sf_met": False,
        "flutter_margin_met": False,
        "auw_met": False,
        "no_collisions_met": False,
    }


def _new_state() -> dict[str, Any]:
    """Create a fresh top-level state document (version 3)."""
    return {
        "version": STATE_VERSION,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "project": "AeroForge",
        "project_code": "UNSET",
        "project_scope": "aircraft",
        "aircraft_type": "UNSPECIFIED",
        "project_phase": ProjectPhase.REQUIREMENTS.value,
        "root_node": None,
        "nodes": {},
        "requirements": _new_phase_record(),
        "research": _new_phase_record(),
        "validation": {
            "policy": {
                "full_aircraft_only": True,
                "backend": "CUDA-capable GPU when available",
                "notes": (
                    "Synthetic wind tunnel and structural calculations run on the "
                    "assembled top object, not on isolated parts."
                ),
            },
            "cfd": _new_phase_record(),
            "fea": _new_phase_record(),
            "convergence": _convergence_defaults(),
        },
        "active_runs": [],
        "history": [],
    }


# ---------------------------------------------------------------------------
# StateManager
# ---------------------------------------------------------------------------


class StateManager:
    """Persistent workflow state manager with hierarchical node tree.

    Nodes form a tree (assemblies have children, components/off-shelf are
    leaves).  Each non-off-shelf node carries an independent 7-step design
    cycle.  Multiple nodes may be active in parallel.
    """

    def __init__(self, state_file: Optional[Path] = None) -> None:
        self._path = state_file or _resolve_state_path()
        self._state: dict[str, Any] = {}
        self._ensure_dirs()

    # ── Persistence ────────────────────────────────────────────────

    def _ensure_dirs(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        """Load state from disk, migrating older versions if needed."""
        if self._path.exists():
            with open(self._path, "r", encoding="utf-8") as handle:
                self._state = json.load(handle)
        else:
            self._state = _new_state()
            self.save()

        self._state = self._normalize_state(self._state)
        return self._state

    def save(self) -> None:
        """Persist current state to disk."""
        self._state["updated_at"] = _now_iso()
        with open(self._path, "w", encoding="utf-8") as handle:
            json.dump(self._state, handle, indent=2, ensure_ascii=False)

    @property
    def state(self) -> dict[str, Any]:
        """Return current state, loading if needed."""
        if not self._state:
            self.load()
        return self._state

    # ── Initialization ─────────────────────────────────────────────

    def initialize(
        self,
        sub_assemblies: Optional[list[str]] = None,
        level_map: Optional[dict[str, int]] = None,
        parent_map: Optional[dict[str, Optional[str]]] = None,
    ) -> None:
        """Initialize workflow state with the provided nodes.

        This is the backward-compatible entry point.  ``level_map`` values
        are used heuristically: level 0 → assembly (root), level 1 →
        assembly, level 2+ → component.  Override with ``add_node()`` for
        explicit control.
        """
        self.load()

        if sub_assemblies is None:
            sub_assemblies = ["wing", "fuselage", "empennage"]

        level_map = level_map or {}
        parent_map = parent_map or {}

        for name in sub_assemblies:
            if name not in self._state["nodes"]:
                level = level_map.get(name, 1)
                if level <= 1:
                    ntype = NodeType.ASSEMBLY
                else:
                    ntype = NodeType.COMPONENT
                parent = parent_map.get(name)
                self.add_node(name, ntype, parent=parent)

        self.save()

    def set_project_metadata(
        self,
        *,
        project: Optional[str] = None,
        aircraft_type: Optional[str] = None,
        project_code: Optional[str] = None,
        project_scope: Optional[str] = None,
        round_label: Optional[str] = None,
    ) -> None:
        """Update top-level project metadata."""
        self.load()
        if project is not None:
            self._state["project"] = project
        if aircraft_type is not None:
            self._state["aircraft_type"] = aircraft_type
        if project_code is not None:
            self._state["project_code"] = project_code
        if project_scope is not None:
            self._state["project_scope"] = project_scope
        if round_label is not None:
            self._state["current_round_label"] = round_label
        self.save()

    def set_round_label(self, name: str, round_label: str) -> None:
        """Rename the tracked round label for a node."""
        self.load()
        node = self.get_node(name)
        node["current_round_label"] = round_label
        # Update matching active runs
        for run in self._state.get("active_runs", []):
            if run.get("node") == name:
                run["round_label"] = round_label
        self._append_history(f"Renamed round for {name} to {round_label}")
        self.save()

    # ── Node tree management ──────────────────────────────────────

    def add_node(
        self,
        name: str,
        node_type: NodeType | str,
        parent: Optional[str] = None,
        children: Optional[list[str]] = None,
    ) -> None:
        """Add a new node to the tree."""
        self.load()
        if name in self._state["nodes"]:
            raise ValueError(f"Node '{name}' already exists")

        if isinstance(node_type, str):
            node_type = NodeType(node_type)

        node = _new_node(name, node_type, parent=parent, children=children)
        self._state["nodes"][name] = node

        # Wire up parent's children list
        if parent and parent in self._state["nodes"]:
            parent_children = self._state["nodes"][parent]["children"]
            if name not in parent_children:
                parent_children.append(name)

        # Set root if this is the first parentless assembly
        if parent is None and node_type == NodeType.ASSEMBLY:
            if self._state.get("root_node") is None:
                self._state["root_node"] = name

        self._append_history(f"Added node {name} (type={node_type.value}, parent={parent})")
        self.save()

    def get_node(self, name: str) -> dict[str, Any]:
        """Return the node record, raising KeyError if missing."""
        node = self.state["nodes"].get(name)
        if node is None:
            raise KeyError(f"Node '{name}' not found")
        return node

    def get_children(self, name: str) -> list[str]:
        """Return child node names."""
        return list(self.get_node(name).get("children", []))

    def get_parent(self, name: str) -> Optional[str]:
        """Return parent node name or None."""
        return self.get_node(name).get("parent")

    def get_descendants(self, name: str) -> list[str]:
        """Return all descendants (recursive) in breadth-first order."""
        result: list[str] = []
        queue = list(self.get_children(name))
        while queue:
            child = queue.pop(0)
            result.append(child)
            queue.extend(self.get_children(child))
        return result

    def get_leaves(self, name: Optional[str] = None) -> list[str]:
        """Return leaf nodes (no children) under a subtree, or all leaves."""
        if name is not None:
            candidates = [name] + self.get_descendants(name)
        else:
            candidates = list(self.state["nodes"].keys())
        return [n for n in candidates if not self.get_children(n)]

    # ── Backward-compatibility aliases ────────────────────────────

    def add_sub_assembly(
        self,
        name: str,
        level: int = 2,
        parent: Optional[str] = None,
    ) -> None:
        """Legacy alias for ``add_node``."""
        ntype = NodeType.ASSEMBLY if level <= 1 else NodeType.COMPONENT
        self.add_node(name, ntype, parent=parent)

    def get_sub_assemblies(self) -> list[str]:
        """Legacy alias — return all node names."""
        return list(self.state.get("nodes", {}).keys())

    def get_sub_assembly(self, name: str) -> dict[str, Any]:
        """Legacy alias for ``get_node``."""
        return self.get_node(name)

    # ── Project phase management ──────────────────────────────────

    def set_project_phase(self, phase: ProjectPhase | str) -> None:
        """Set the current top-level project phase."""
        if isinstance(phase, str):
            phase = ProjectPhase(phase)
        self.load()
        old = self._state.get("project_phase")
        self._state["project_phase"] = phase.value
        self._append_history(f"Project phase: {old} → {phase.value}")
        self.save()

    def get_project_phase(self) -> str:
        """Return current project phase value."""
        return self.state.get("project_phase", ProjectPhase.REQUIREMENTS.value)

    # ── Design cycle query ────────────────────────────────────────

    def get_current_step(self, name: str) -> str:
        """Return the current design step for a node."""
        node = self.get_node(name)
        return node.get("current_design_step") or node.get("current_step", "")

    def get_step(self, name: str, step: str) -> dict[str, Any]:
        """Return a specific design-cycle step record."""
        node = self.get_node(name)
        cycle = node.get("design_cycle")
        if cycle is None:
            raise RuntimeError(f"Node '{name}' is off-shelf and has no design cycle")
        if step not in cycle:
            raise KeyError(f"Step '{step}' not found in '{name}'")
        return cycle[step]

    def get_status(self, name: str, step: str) -> str:
        """Return the status string for a specific step."""
        return self.get_step(name, step)["status"]

    def get_active_run(self) -> Optional[dict[str, Any]]:
        """Return the most recent active run, or None.

        Legacy callers expect a single dict.  Returns the first entry from
        ``active_runs`` for backward compatibility.
        """
        runs = self.state.get("active_runs", [])
        return runs[0] if runs else None

    def get_active_runs(self) -> list[dict[str, Any]]:
        """Return all currently active runs."""
        return list(self.state.get("active_runs", []))

    def get_progress(self, name: str) -> dict[str, Any]:
        """Return a progress summary for a node."""
        node = self.get_node(name)
        cycle = node.get("design_cycle")

        if cycle is None:
            # Off-shelf — always 100 %
            return {
                "name": name,
                "type": node.get("type", "off_shelf"),
                "iteration": 1,
                "round_label": "N/A",
                "agent_round": 0,
                "current_step": None,
                "deliverables": [],
                "done": 0,
                "failed": 0,
                "total": 0,
                "percent": 100.0,
                "children": node.get("children", []),
            }

        done = sum(1 for s in cycle.values() if s["status"] == StepStatus.DONE.value)
        failed = sum(1 for s in cycle.values() if s["status"] == StepStatus.FAILED.value)
        total = len(cycle)

        return {
            "name": name,
            "type": node.get("type", "component"),
            "iteration": node.get("iteration", 1),
            "round_label": node.get(
                "current_round_label",
                f"R{node.get('iteration', 1)}",
            ),
            "agent_round": node.get("agent_round", 0),
            "current_step": node.get("current_design_step"),
            "deliverables": node.get("deliverables", []),
            "done": done,
            "failed": failed,
            "total": total,
            "percent": round(done / total * 100, 1) if total else 0,
            "children": node.get("children", []),
        }

    def get_full_progress(self) -> list[dict[str, Any]]:
        """Return progress for every node."""
        return [self.get_progress(name) for name in self.get_sub_assemblies()]

    def is_complete(self, name: str) -> bool:
        """Check if a node's design cycle is fully done."""
        node = self.get_node(name)
        cycle = node.get("design_cycle")
        if cycle is None:
            return True  # off-shelf is always "complete"
        return all(
            s["status"] in {StepStatus.DONE.value, StepStatus.SKIPPED.value}
            for s in cycle.values()
        )

    def all_complete(self) -> bool:
        """Check if every node is complete."""
        return all(self.is_complete(name) for name in self.get_sub_assemblies())

    # ── Drawing approval ──────────────────────────────────────────

    def approve_drawing(self, name: str) -> None:
        """Mark the DRAWING_2D step as approved for a node."""
        self.load()
        step_record = self.get_step(name, DesignStep.DRAWING_2D.value)
        step_record["approved"] = True
        step_record["approved_at"] = _now_iso()
        self._append_history(f"Drawing approved for {name}")
        self.save()

    def is_drawing_approved(self, name: str) -> bool:
        """Check whether DRAWING_2D has been approved."""
        node = self.get_node(name)
        cycle = node.get("design_cycle")
        if cycle is None:
            return True  # off-shelf has no drawing
        drawing = cycle.get(DesignStep.DRAWING_2D.value, {})
        return bool(drawing.get("approved", False))

    def check_design_phase_complete(self) -> bool:
        """Return True if all non-off-shelf nodes have approved drawings."""
        for name, node in self.state.get("nodes", {}).items():
            if node.get("type") == NodeType.OFF_SHELF.value:
                continue
            if not self.is_drawing_approved(name):
                return False
        return True

    # ── Topological ordering ──────────────────────────────────────

    def get_implementation_order(self) -> list[str]:
        """Return nodes in implementation order (leaves first, root last).

        Off-shelf nodes are excluded since they need no implementation.
        """
        nodes = self.state.get("nodes", {})
        # Build adjacency: parent → children
        # We want reverse topological order (leaves first)
        result: list[str] = []
        visited: set[str] = set()

        def _visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            node = nodes.get(name, {})
            for child in node.get("children", []):
                _visit(child)
            if node.get("type") != NodeType.OFF_SHELF.value:
                result.append(name)

        # Start from root(s)
        root = self.state.get("root_node")
        if root and root in nodes:
            _visit(root)
        else:
            for name in nodes:
                _visit(name)

        return result

    # ── Invalidation ──────────────────────────────────────────────

    def invalidate_node(self, name: str) -> None:
        """Reset a node's design cycle back to AERO_PROPOSAL for re-run."""
        self.load()
        node = self._state["nodes"][name]
        if node.get("design_cycle") is None:
            return  # off-shelf

        node["design_cycle"] = _new_design_cycle()
        node["current_design_step"] = DesignStep.AERO_PROPOSAL.value
        node["agent_round"] = 0

        # Remove any active runs for this node
        self._state["active_runs"] = [
            r for r in self._state.get("active_runs", [])
            if r.get("node") != name
        ]

        self._append_history(f"Invalidated node {name} — design cycle reset")
        self.save()

    def invalidate_subtree(self, name: str) -> None:
        """Reset a node and all its descendants."""
        self.load()
        targets = [name] + self.get_descendants(name)
        for target in targets:
            node = self._state["nodes"].get(target)
            if node and node.get("design_cycle") is not None:
                node["design_cycle"] = _new_design_cycle()
                node["current_design_step"] = DesignStep.AERO_PROPOSAL.value
                node["agent_round"] = 0

        # Remove active runs for all affected nodes
        target_set = set(targets)
        self._state["active_runs"] = [
            r for r in self._state.get("active_runs", [])
            if r.get("node") not in target_set
        ]

        self._append_history(f"Invalidated subtree rooted at {name} ({len(targets)} nodes)")
        self.save()

    # ── Step mutation ─────────────────────────────────────────────

    def start_step(
        self,
        name: str,
        step: str,
        agent: Optional[str] = None,
    ) -> None:
        """Mark a design-cycle step as running.

        Multiple nodes can run in parallel — only the *same* node+step
        combination is rejected if already running.
        """
        self.load()
        self._ensure_step_is_current(name, step)

        record = self.get_step(name, step)
        if record["status"] == StepStatus.DONE.value:
            raise RuntimeError(f"{name}:{step} is already complete")
        if record["status"] == StepStatus.RUNNING.value:
            return  # idempotent

        record["status"] = StepStatus.RUNNING.value
        record["started_at"] = _now_iso()
        record["completed_at"] = None
        record["agent"] = agent
        self._state["nodes"][name]["current_design_step"] = step

        if step == DesignStep.AERO_PROPOSAL.value:
            self._state["nodes"][name]["agent_round"] += 1

        node = self._state["nodes"][name]
        run_entry = {
            "node": name,
            "sub_assembly": name,  # backward compat key
            "step": step,
            "agent": agent,
            "iteration": node.get("iteration", 1),
            "round_label": node.get(
                "current_round_label",
                f"R{node.get('iteration', 1)}",
            ),
            "started_at": record["started_at"],
        }
        self._state.setdefault("active_runs", []).append(run_entry)

        self._append_history(f"Started {step} for {name}", agent=agent)
        self.save()

    def complete_step(
        self,
        name: str,
        step: str,
        output_files: Optional[list[str]] = None,
        notes: str = "",
    ) -> None:
        """Mark a design-cycle step as done."""
        self.load()
        self._ensure_active_run_matches(name, step)

        record = self.get_step(name, step)
        record["status"] = StepStatus.DONE.value
        record["completed_at"] = _now_iso()
        if output_files:
            record["output_files"] = output_files
            node = self._state["nodes"][name]
            node.setdefault("artifacts", []).extend(output_files)
        if notes:
            record["notes"] = notes

        self._remove_active_run(name, step)
        self._append_history(f"Completed {step} for {name}", output_files=output_files)
        self._advance_current_step(name, step)
        self.save()

    def fail_step(
        self,
        name: str,
        step: str,
        reason: str = "",
    ) -> None:
        """Mark a design-cycle step as failed."""
        self.load()
        self._ensure_active_run_matches(name, step)

        record = self.get_step(name, step)
        record["status"] = StepStatus.FAILED.value
        record["completed_at"] = _now_iso()
        record["notes"] = reason
        self._state["nodes"][name]["current_design_step"] = step

        self._remove_active_run(name, step)
        self._append_history(f"FAILED {step} for {name}: {reason}")
        self.save()

    def skip_step(self, name: str, step: str, reason: str = "") -> None:
        """Mark a design-cycle step as skipped."""
        self.load()
        record = self.get_step(name, step)
        record["status"] = StepStatus.SKIPPED.value
        record["completed_at"] = _now_iso()
        record["notes"] = reason

        self._remove_active_run(name, step)
        self._append_history(f"Skipped {step} for {name}: {reason}")
        self._advance_current_step(name, step)
        self.save()

    def reset_step(self, name: str, step: str) -> None:
        """Reset a design-cycle step back to pending."""
        self.load()
        record = self.get_step(name, step)
        record["status"] = StepStatus.PENDING.value
        record["started_at"] = None
        record["completed_at"] = None
        record["notes"] = ""
        record["agent"] = None
        record["output_files"] = []

        self._remove_active_run(name, step)
        self._state["nodes"][name]["current_design_step"] = step
        self._append_history(f"Reset {step} for {name}")
        self.save()

    def reject_step(
        self,
        name: str,
        step: str,
        reason: str = "",
        rework_notes: str = "",
    ) -> None:
        """Reject a completed step and reset it for rework.

        This is called when the user (or an agent reviewing deliverables)
        rejects the output.  The step goes back to PENDING with rejection
        context preserved in history and step notes.
        """
        self.load()
        record = self.get_step(name, step)

        # Store rejection in step history
        rejection = {
            "action": "rejected",
            "timestamp": _now_iso(),
            "reason": reason,
            "rework_notes": rework_notes,
            "previous_status": record["status"],
            "previous_output": record.get("output_files", []),
        }
        record.setdefault("history", []).append(rejection)

        # Reset the step
        record["status"] = StepStatus.PENDING.value
        record["started_at"] = None
        record["completed_at"] = None
        record["notes"] = f"REJECTED: {reason}" if reason else "Rejected by user"
        record["agent"] = None

        # Clear matching active runs
        self._remove_active_run(name, step)

        # Set current step back to this one
        self._state["nodes"][name]["current_design_step"] = step

        self._append_history(
            f"REJECTED {step} for {name}: {reason}",
            notes=rework_notes,
        )
        self.save()

    def record_user_feedback(
        self,
        name: str,
        step: str,
        feedback: str,
    ) -> None:
        """Record user design feedback on a step.

        This does NOT change step status — it stores the feedback for
        the LLM to consider when re-running or continuing the step.
        """
        self.load()
        record = self.get_step(name, step)
        entry = {
            "action": "user_feedback",
            "timestamp": _now_iso(),
            "feedback": feedback,
        }
        record.setdefault("history", []).append(entry)
        self._append_history(f"User feedback on {step} for {name}: {feedback[:100]}")
        self.save()

    def get_step_history(self, name: str, step: str) -> list[dict[str, Any]]:
        """Return the full history of a step (rejections, feedback, rework)."""
        record = self.get_step(name, step)
        return record.get("history", [])

    def start_new_iteration(self, name: str, round_label: Optional[str] = None) -> int:
        """Start a new design iteration for a node."""
        self.load()
        node = self._state["nodes"][name]
        node["iteration"] = node.get("iteration", 1) + 1
        node["current_round_label"] = round_label or f"R{node['iteration']}"
        node["agent_round"] = 0

        if node.get("design_cycle") is not None:
            node["design_cycle"] = _new_design_cycle()
            node["current_design_step"] = DesignStep.AERO_PROPOSAL.value

        # Clear active runs for this node
        self._state["active_runs"] = [
            r for r in self._state.get("active_runs", [])
            if r.get("node") != name
        ]

        iteration = node["iteration"]
        self._append_history(
            f"Started iteration {iteration} for {name} ({node['current_round_label']})"
        )
        self.save()
        return iteration

    # ── Convergence / analysis ────────────────────────────────────

    def set_convergence(self, criterion: str, met: bool) -> None:
        """Set a convergence criterion flag."""
        self.load()
        self._state.setdefault("validation", {}).setdefault(
            "convergence", _convergence_defaults()
        )[criterion] = met
        self.save()

    # ── Legacy helpers ────────────────────────────────────────────

    def set_dependency(self, name: str, depends_on: list[str]) -> None:
        """Legacy: store dependency list on a node.

        In v3 dependencies are expressed via parent/children.  This method
        stores the list under a compat key for callers that still use it.
        """
        self.load()
        self._state["nodes"][name]["dependencies"] = depends_on
        self.save()

    def set_sub_assembly_profile(
        self,
        name: str,
        *,
        deliverables: Optional[list[str]] = None,
        step_deliverables: Optional[dict[str, list[str]]] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Persist profile details for one tracked node."""
        self.load()
        node = self._state["nodes"][name]
        if deliverables is not None:
            node["deliverables"] = deliverables
        if step_deliverables is not None:
            node["step_deliverables"] = step_deliverables
            cycle = node.get("design_cycle")
            if cycle:
                for step_name, expected in step_deliverables.items():
                    if step_name in cycle:
                        cycle[step_name]["expected_deliverables"] = expected
        if notes:
            node["notes"] = notes
        self.save()

    # ── Internal ──────────────────────────────────────────────────

    def _ensure_active_run_matches(self, name: str, step: str) -> None:
        """Verify that the given node+step is currently running."""
        runs = self._state.get("active_runs", [])
        for run in runs:
            if run.get("node") == name and run.get("step") == step:
                return
            # Backward compat: check sub_assembly key too
            if run.get("sub_assembly") == name and run.get("step") == step:
                return
        raise RuntimeError(f"No active run for {name}:{step}")

    def _remove_active_run(self, name: str, step: str) -> None:
        """Remove the matching active run entry (if any)."""
        self._state["active_runs"] = [
            r for r in self._state.get("active_runs", [])
            if not (
                (r.get("node") == name or r.get("sub_assembly") == name)
                and r.get("step") == step
            )
        ]

    def _ensure_step_is_current(self, name: str, step: str) -> None:
        """Verify the step is the node's current design step."""
        current = self._state["nodes"][name].get("current_design_step")
        if current is None:
            raise RuntimeError(f"Node '{name}' has no design cycle (off-shelf?)")
        if current != step:
            raise RuntimeError(
                f"Cannot start {name}:{step}. Current required step is {current}."
            )

    def _advance_current_step(self, name: str, completed_step: str) -> None:
        """Move current_design_step to the next pending/failed step."""
        node = self._state["nodes"][name]
        cycle = node.get("design_cycle")
        if cycle is None:
            return

        try:
            index = DESIGN_STEP_ORDER.index(completed_step)
        except ValueError:
            return

        for next_step in DESIGN_STEP_ORDER[index + 1:]:
            status = cycle[next_step]["status"]
            if status in {StepStatus.PENDING.value, StepStatus.FAILED.value}:
                node["current_design_step"] = next_step
                return

        # All done — keep pointing at the last step
        node["current_design_step"] = DESIGN_STEP_ORDER[-1]

    def _append_history(
        self,
        event: str,
        agent: Optional[str] = None,
        output_files: Optional[list[str]] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Append an event to the global history log."""
        entry: dict[str, Any] = {
            "timestamp": _now_iso(),
            "event": event,
        }
        if agent:
            entry["agent"] = agent
        if output_files:
            entry["output_files"] = output_files
        if notes:
            entry["notes"] = notes
        self._state.setdefault("history", []).append(entry)
        if len(self._state["history"]) > 500:
            self._state["history"] = self._state["history"][-500:]

    # ── State normalization / migration ───────────────────────────

    def _normalize_state(self, state: dict[str, Any]) -> dict[str, Any]:
        """Ensure all expected keys exist, migrating v1/v2 data to v3."""
        old_version = state.get("version", 1)

        normalized = _new_state()
        normalized.update(state)
        normalized["version"] = STATE_VERSION

        # Carry forward top-level metadata
        normalized.setdefault("project_code", "UNSET")
        normalized.setdefault("project_scope", "aircraft")
        normalized.setdefault("project_phase", ProjectPhase.REQUIREMENTS.value)
        normalized.setdefault("root_node", None)
        normalized.setdefault("history", [])
        normalized.setdefault("requirements", _new_phase_record())
        normalized.setdefault("research", _new_phase_record())

        # Migrate validation / analysis
        if "analysis" in state and "validation" not in state:
            # v2 used "analysis"; v3 uses "validation"
            normalized["validation"] = state["analysis"]
        normalized.setdefault("validation", {})
        normalized["validation"].setdefault(
            "policy", _new_state()["validation"]["policy"]
        )
        normalized["validation"].setdefault("cfd", _new_phase_record())
        normalized["validation"].setdefault("fea", _new_phase_record())
        normalized["validation"].setdefault("convergence", _convergence_defaults())

        # ── Migrate sub_assemblies → nodes ────────────────────────
        if old_version < 3 and "sub_assemblies" in state and "nodes" not in state:
            normalized["nodes"] = {}
            for sa_name, sa in state["sub_assemblies"].items():
                normalized["nodes"][sa_name] = self._migrate_sub_assembly(sa_name, sa)
        else:
            nodes = normalized.setdefault("nodes", {})
            for name, node in list(nodes.items()):
                nodes[name] = self._normalize_node(name, node)

        # ── Migrate active_run → active_runs ──────────────────────
        if "active_run" in state and "active_runs" not in state:
            old_run = state.get("active_run")
            if old_run is not None:
                old_run.setdefault("node", old_run.get("sub_assembly", ""))
                normalized["active_runs"] = [old_run]
            else:
                normalized["active_runs"] = []
        normalized.setdefault("active_runs", [])

        # Derive active runs from node state if list is empty
        if not normalized["active_runs"]:
            normalized["active_runs"] = self._derive_active_runs(normalized["nodes"])

        # Clean up legacy keys
        normalized.pop("active_run", None)
        normalized.pop("sub_assemblies", None)
        normalized.pop("analysis", None)
        normalized.pop("current_iteration", None)
        normalized.pop("current_round_label", None)

        return normalized

    def _migrate_sub_assembly(
        self,
        name: str,
        sa: dict[str, Any],
    ) -> dict[str, Any]:
        """Migrate a v2 sub-assembly record into a v3 node."""
        node = _new_node(
            name=name,
            node_type=NodeType.ASSEMBLY,
            parent=sa.get("parent"),
        )
        node["iteration"] = sa.get("current_iteration", 1)
        node["current_round_label"] = sa.get(
            "current_round_label", f"R{node['iteration']}"
        )
        node["max_agent_rounds"] = max(3, int(sa.get("max_agent_rounds", 3)))
        node["agent_round"] = sa.get("agent_round", 0)
        node["artifacts"] = sa.get("artifacts", [])
        node["deliverables"] = sa.get("deliverables", [])
        node["step_deliverables"] = sa.get("step_deliverables", {})
        node["dependencies"] = sa.get("dependencies", [])

        # Migrate steps → design_cycle (map old 11-step to new 7-step)
        old_steps = sa.get("steps", {})
        cycle = _new_design_cycle()
        step_name_map = {
            "MESH": "OUTPUT",
        }
        for old_name, step_data in old_steps.items():
            mapped = step_name_map.get(old_name, old_name)
            if mapped in cycle:
                cycle[mapped].update(step_data)
                cycle[mapped]["name"] = mapped

        node["design_cycle"] = cycle
        node["current_design_step"] = self._first_incomplete_design_step(cycle)

        return node

    def _normalize_node(self, name: str, node: dict[str, Any]) -> dict[str, Any]:
        """Ensure a v3 node has all required fields."""
        node.setdefault("name", name)
        node.setdefault("type", NodeType.COMPONENT.value)
        node.setdefault("parent", None)
        node.setdefault("children", [])
        node.setdefault("iteration", 1)
        node.setdefault("max_agent_rounds", 3)
        node.setdefault("agent_round", 0)
        node.setdefault("artifacts", [])
        node.setdefault("deliverables", [])
        node.setdefault("step_deliverables", {})

        if node.get("type") == NodeType.OFF_SHELF.value:
            node["design_cycle"] = None
            node["current_design_step"] = None
        else:
            existing_cycle = node.get("design_cycle") or {}
            cycle = _new_design_cycle()
            for step in DesignStep:
                step_state = cycle[step.value]
                step_state.update(existing_cycle.get(step.value, {}))
                step_state["name"] = step.value
                step_state.setdefault("history", [])
                if step.value in node.get("step_deliverables", {}):
                    step_state["expected_deliverables"] = node["step_deliverables"][step.value]
                cycle[step.value] = step_state
            node["design_cycle"] = cycle
            node["current_design_step"] = self._first_incomplete_design_step(cycle)

        return node

    def _first_incomplete_design_step(self, cycle: dict[str, dict[str, Any]]) -> str:
        """Return the first pending/running/failed step in the design cycle."""
        for step in DesignStep:
            status = cycle[step.value]["status"]
            if status in {StepStatus.PENDING.value, StepStatus.RUNNING.value, StepStatus.FAILED.value}:
                return step.value
        return DesignStep.OUTPUT.value

    def _derive_active_runs(
        self,
        nodes: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Scan nodes for RUNNING steps and build the active_runs list."""
        runs: list[dict[str, Any]] = []
        for name, node in nodes.items():
            cycle = node.get("design_cycle")
            if cycle is None:
                continue
            for step_name, step in cycle.items():
                if step.get("status") == StepStatus.RUNNING.value:
                    runs.append({
                        "node": name,
                        "sub_assembly": name,
                        "step": step_name,
                        "agent": step.get("agent"),
                        "iteration": node.get("iteration", 1),
                        "round_label": node.get(
                            "current_round_label",
                            f"R{node.get('iteration', 1)}",
                        ),
                        "started_at": step.get("started_at"),
                    })

        runs.sort(key=lambda item: item.get("started_at") or "", reverse=True)
        return runs

    # ── Export ─────────────────────────────────────────────────────

    def export_status_json(self, path: Optional[Path] = None) -> Path:
        """Export a JSON summary suitable for dashboards and tooling."""
        out = path or (PROJECT_ROOT / "exports" / "workflow_status.json")
        out.parent.mkdir(parents=True, exist_ok=True)

        summary: dict[str, Any] = {
            "project": self.state["project"],
            "project_code": self.state.get("project_code"),
            "project_phase": self.state.get("project_phase"),
            "updated_at": self.state.get("updated_at"),
            "root_node": self.state.get("root_node"),
            "active_runs": self.state.get("active_runs", []),
            "nodes": {},
            "convergence": self.state.get("validation", {}).get("convergence", {}),
        }

        for name in self.get_sub_assemblies():
            summary["nodes"][name] = self.get_progress(name)

        # Backward compat key
        summary["sub_assemblies"] = summary["nodes"]

        with open(out, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, ensure_ascii=False)

        return out
