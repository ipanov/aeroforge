"""Persistent state manager for the design workflow orchestrator.

Tracks the state of every sub-assembly across design iterations and exposes a
single active step so the current execution point is always visible.
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
STATE_FILE = PROJECT_ROOT / ".claude" / "workflow_state.json"
DASHBOARD_FILE = PROJECT_ROOT / "exports" / "workflow_dashboard.html"
STATE_VERSION = 2


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


class WorkflowStep(str, Enum):
    """Canonical steps in the design workflow."""

    REQUIREMENTS = "REQUIREMENTS"
    RESEARCH = "RESEARCH"
    AERO_PROPOSAL = "AERO_PROPOSAL"
    STRUCTURAL_REVIEW = "STRUCTURAL_REVIEW"
    AERO_RESPONSE = "AERO_RESPONSE"
    CONSENSUS = "CONSENSUS"
    DRAWING_2D = "DRAWING_2D"
    MODEL_3D = "MODEL_3D"
    MESH = "MESH"
    VALIDATION = "VALIDATION"
    RELEASE = "RELEASE"


WORKFLOW_STEPS = list(WorkflowStep)
AGENT_ROUND_STEPS = {
    WorkflowStep.AERO_PROPOSAL.value,
    WorkflowStep.STRUCTURAL_REVIEW.value,
    WorkflowStep.AERO_RESPONSE.value,
    WorkflowStep.CONSENSUS.value,
}


# ---------------------------------------------------------------------------
# State factories
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """Current UTC time in ISO-8601."""

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _new_step(step: WorkflowStep) -> dict[str, Any]:
    """Create a fresh step record."""

    return {
        "name": step.value,
        "status": StepStatus.PENDING.value,
        "agent": None,
        "output_files": [],
        "expected_deliverables": [],
        "notes": "",
        "started_at": None,
        "completed_at": None,
    }


def _new_sub_assembly(name: str, level: int, parent: Optional[str] = None) -> dict[str, Any]:
    """Create a fresh sub-assembly record."""

    return {
        "name": name,
        "level": level,
        "parent": parent,
        "current_iteration": 1,
        "current_round_label": "R1",
        "max_agent_rounds": 5,
        "agent_round": 0,
        "steps": {s.value: _new_step(s) for s in WORKFLOW_STEPS},
        "current_step": WorkflowStep.REQUIREMENTS.value,
        "artifacts": [],
        "deliverables": [],
        "step_deliverables": {},
        "dependencies": [],
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


def _new_active_run() -> None:
    """Return an empty active run."""

    return None


def _new_state() -> dict[str, Any]:
    """Create a fresh top-level state document."""

    return {
        "version": STATE_VERSION,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "project": "AeroForge",
        "project_code": "UNSET",
        "project_scope": "aircraft",
        "aircraft_type": "UNSPECIFIED",
        "current_iteration": 1,
        "current_round_label": "R1",
        "active_run": _new_active_run(),
        "sub_assemblies": {},
        "analysis": {
            "policy": {
                "full_aircraft_only": True,
                "backend": "CUDA-capable GPU when available",
                "notes": (
                    "Synthetic wind tunnel and structural calculations run on the "
                    "assembled top object, not on isolated parts."
                ),
            },
            "cfd": _new_step(WorkflowStep.VALIDATION),
            "fea": _new_step(WorkflowStep.VALIDATION),
            "convergence": _convergence_defaults(),
        },
        "history": [],
    }


# ---------------------------------------------------------------------------
# StateManager
# ---------------------------------------------------------------------------


class StateManager:
    """Persistent workflow state manager with strict sequential execution."""

    def __init__(self, state_file: Optional[Path] = None) -> None:
        self._path = state_file or STATE_FILE
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
        """Initialize workflow state with the provided sub-assemblies."""

        self.load()

        if sub_assemblies is None:
            sub_assemblies = ["wing", "fuselage", "empennage"]

        level_map = level_map or {}
        parent_map = parent_map or {}

        for name in sub_assemblies:
            if name not in self._state["sub_assemblies"]:
                self._state["sub_assemblies"][name] = _new_sub_assembly(
                    name=name,
                    level=level_map.get(name, 1),
                    parent=parent_map.get(name),
                )

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
        """Rename the tracked round label for a sub-assembly."""

        self.load()
        sa = self.get_sub_assembly(name)
        sa["current_round_label"] = round_label
        active = self._state.get("active_run")
        if active and active.get("sub_assembly") == name:
            active["round_label"] = round_label
        self._append_history(f"Renamed round for {name} to {round_label}")
        self.save()

    def add_sub_assembly(
        self,
        name: str,
        level: int = 2,
        parent: Optional[str] = None,
    ) -> None:
        """Add a new sub-assembly to the workflow."""

        self.load()
        if name in self._state["sub_assemblies"]:
            raise ValueError(f"Sub-assembly '{name}' already exists")
        self._state["sub_assemblies"][name] = _new_sub_assembly(name, level, parent)
        self.save()

    # ── Query ──────────────────────────────────────────────────────

    def get_sub_assemblies(self) -> list[str]:
        return list(self.state.get("sub_assemblies", {}).keys())

    def get_sub_assembly(self, name: str) -> dict[str, Any]:
        sa = self.state["sub_assemblies"].get(name)
        if sa is None:
            raise KeyError(f"Sub-assembly '{name}' not found")
        return sa

    def get_current_step(self, name: str) -> str:
        return self.get_sub_assembly(name)["current_step"]

    def get_step(self, name: str, step: str) -> dict[str, Any]:
        steps = self.get_sub_assembly(name)["steps"]
        if step not in steps:
            raise KeyError(f"Step '{step}' not found in '{name}'")
        return steps[step]

    def get_status(self, name: str, step: str) -> str:
        return self.get_step(name, step)["status"]

    def get_active_run(self) -> Optional[dict[str, Any]]:
        return self.state.get("active_run")

    def get_progress(self, name: str) -> dict[str, Any]:
        sa = self.get_sub_assembly(name)
        steps = sa["steps"]
        done = sum(1 for s in steps.values() if s["status"] == StepStatus.DONE.value)
        failed = sum(1 for s in steps.values() if s["status"] == StepStatus.FAILED.value)
        total = len(steps)
        return {
            "name": name,
            "iteration": sa["current_iteration"],
            "round_label": sa.get("current_round_label", f"R{sa['current_iteration']}"),
            "agent_round": sa["agent_round"],
            "current_step": sa["current_step"],
            "deliverables": sa.get("deliverables", []),
            "done": done,
            "failed": failed,
            "total": total,
            "percent": round(done / total * 100, 1) if total else 0,
            "dependencies": sa.get("dependencies", []),
        }

    def get_full_progress(self) -> list[dict[str, Any]]:
        return [self.get_progress(name) for name in self.get_sub_assemblies()]

    def is_complete(self, name: str) -> bool:
        return self.get_status(name, WorkflowStep.RELEASE.value) == StepStatus.DONE.value

    def all_complete(self) -> bool:
        return all(self.is_complete(name) for name in self.get_sub_assemblies())

    # ── Mutation ───────────────────────────────────────────────────

    def start_step(
        self,
        name: str,
        step: str,
        agent: Optional[str] = None,
    ) -> None:
        """Mark a step as running, enforcing strict sequencing."""

        self.load()
        self._ensure_no_other_active_run(name, step)
        self._ensure_step_is_current(name, step)

        record = self.get_step(name, step)
        if record["status"] == StepStatus.DONE.value:
            raise RuntimeError(f"{name}:{step} is already complete")
        if record["status"] == StepStatus.RUNNING.value:
            return

        record["status"] = StepStatus.RUNNING.value
        record["started_at"] = _now_iso()
        record["completed_at"] = None
        record["agent"] = agent
        self._state["sub_assemblies"][name]["current_step"] = step

        if step == WorkflowStep.AERO_PROPOSAL.value:
            self._state["sub_assemblies"][name]["agent_round"] += 1

        sa = self._state["sub_assemblies"][name]
        self._state["active_run"] = {
            "sub_assembly": name,
            "step": step,
            "agent": agent,
            "iteration": sa["current_iteration"],
            "round_label": sa.get("current_round_label", f"R{sa['current_iteration']}"),
            "started_at": record["started_at"],
        }

        self._append_history(f"Started {step} for {name}", agent=agent)
        self.save()

    def complete_step(
        self,
        name: str,
        step: str,
        output_files: Optional[list[str]] = None,
        notes: str = "",
    ) -> None:
        """Mark a step as done, enforcing active step ownership."""

        self.load()
        self._ensure_active_run_matches(name, step)

        record = self.get_step(name, step)
        record["status"] = StepStatus.DONE.value
        record["completed_at"] = _now_iso()
        if output_files:
            record["output_files"] = output_files
            sa = self._state["sub_assemblies"][name]
            sa.setdefault("artifacts", []).extend(output_files)
        if notes:
            record["notes"] = notes

        self._state["active_run"] = None
        self._append_history(f"Completed {step} for {name}", output_files=output_files)
        self._advance_current_step(name, step)
        self.save()

    def fail_step(
        self,
        name: str,
        step: str,
        reason: str = "",
    ) -> None:
        """Mark a step as failed."""

        self.load()
        self._ensure_active_run_matches(name, step)
        record = self.get_step(name, step)
        record["status"] = StepStatus.FAILED.value
        record["completed_at"] = _now_iso()
        record["notes"] = reason
        self._state["sub_assemblies"][name]["current_step"] = step
        self._state["active_run"] = None
        self._append_history(f"FAILED {step} for {name}: {reason}")
        self.save()

    def skip_step(self, name: str, step: str, reason: str = "") -> None:
        """Mark a step as skipped."""

        self.load()
        record = self.get_step(name, step)
        record["status"] = StepStatus.SKIPPED.value
        record["completed_at"] = _now_iso()
        record["notes"] = reason

        active = self._state.get("active_run")
        if active and active.get("sub_assembly") == name and active.get("step") == step:
            self._state["active_run"] = None

        self._append_history(f"Skipped {step} for {name}: {reason}")
        self._advance_current_step(name, step)
        self.save()

    def reset_step(self, name: str, step: str) -> None:
        """Reset a step back to pending."""

        self.load()
        record = self.get_step(name, step)
        record["status"] = StepStatus.PENDING.value
        record["started_at"] = None
        record["completed_at"] = None
        record["notes"] = ""
        record["agent"] = None
        record["output_files"] = []

        active = self._state.get("active_run")
        if active and active.get("sub_assembly") == name and active.get("step") == step:
            self._state["active_run"] = None

        self._state["sub_assemblies"][name]["current_step"] = step
        self._append_history(f"Reset {step} for {name}")
        self.save()

    def start_new_iteration(self, name: str, round_label: Optional[str] = None) -> int:
        """Start a new design iteration for a sub-assembly."""

        self.load()
        sa = self._state["sub_assemblies"][name]
        sa["current_iteration"] += 1
        sa["current_round_label"] = round_label or f"R{sa['current_iteration']}"
        sa["agent_round"] = 0
        sa["steps"] = {s.value: _new_step(s) for s in WORKFLOW_STEPS}
        sa["current_step"] = WorkflowStep.REQUIREMENTS.value

        active = self._state.get("active_run")
        if active and active.get("sub_assembly") == name:
            self._state["active_run"] = None

        iteration = sa["current_iteration"]
        self._append_history(
            f"Started iteration {iteration} for {name} ({sa['current_round_label']})"
        )
        self.save()
        return iteration

    def set_convergence(self, criterion: str, met: bool) -> None:
        self.load()
        self._state.setdefault("analysis", {}).setdefault(
            "convergence", _convergence_defaults()
        )[criterion] = met
        self.save()

    def set_dependency(self, name: str, depends_on: list[str]) -> None:
        self.load()
        self._state["sub_assemblies"][name]["dependencies"] = depends_on
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
        sa = self._state["sub_assemblies"][name]
        if deliverables is not None:
            sa["deliverables"] = deliverables
        if step_deliverables is not None:
            sa["step_deliverables"] = step_deliverables
            for step_name, expected in step_deliverables.items():
                if step_name in sa["steps"]:
                    sa["steps"][step_name]["expected_deliverables"] = expected
        if notes:
            sa["notes"] = notes
        self.save()

    # ── Internal ───────────────────────────────────────────────────

    def _ensure_no_other_active_run(self, name: str, step: str) -> None:
        active = self._state.get("active_run")
        if active is None:
            return
        if active.get("sub_assembly") == name and active.get("step") == step:
            return
        raise RuntimeError(
            "Another workflow step is already running: "
            f"{active.get('sub_assembly')}:{active.get('step')}"
        )

    def _ensure_active_run_matches(self, name: str, step: str) -> None:
        active = self._state.get("active_run")
        if active is None:
            raise RuntimeError(f"No active workflow step to complete for {name}:{step}")
        if active.get("sub_assembly") != name or active.get("step") != step:
            raise RuntimeError(
                "Active workflow step mismatch: "
                f"expected {active.get('sub_assembly')}:{active.get('step')}, "
                f"got {name}:{step}"
            )

    def _ensure_step_is_current(self, name: str, step: str) -> None:
        current = self._state["sub_assemblies"][name]["current_step"]
        if current != step:
            raise RuntimeError(
                f"Cannot start {name}:{step}. Current required step is {current}."
            )

    def _advance_current_step(self, name: str, completed_step: str) -> None:
        steps = self._state["sub_assemblies"][name]["steps"]
        ordered_names = [step.value for step in WORKFLOW_STEPS]
        try:
            index = ordered_names.index(completed_step)
        except ValueError:
            return

        for next_step in ordered_names[index + 1:]:
            status = steps[next_step]["status"]
            if status in {StepStatus.PENDING.value, StepStatus.FAILED.value}:
                self._state["sub_assemblies"][name]["current_step"] = next_step
                return

        self._state["sub_assemblies"][name]["current_step"] = ordered_names[-1]

    def _append_history(
        self,
        event: str,
        agent: Optional[str] = None,
        output_files: Optional[list[str]] = None,
    ) -> None:
        entry: dict[str, Any] = {
            "timestamp": _now_iso(),
            "event": event,
        }
        if agent:
            entry["agent"] = agent
        if output_files:
            entry["output_files"] = output_files
        self._state.setdefault("history", []).append(entry)
        if len(self._state["history"]) > 500:
            self._state["history"] = self._state["history"][-500:]

    def _normalize_state(self, state: dict[str, Any]) -> dict[str, Any]:
        normalized = _new_state()
        normalized.update(state)
        normalized["version"] = STATE_VERSION
        normalized.setdefault("active_run", None)
        normalized.setdefault("project_code", "AIR4")
        normalized.setdefault("project_scope", "aircraft")
        normalized.setdefault("current_round_label", f"R{normalized.get('current_iteration', 1)}")
        normalized.setdefault("analysis", {})
        normalized["analysis"].setdefault(
            "policy",
            _new_state()["analysis"]["policy"],
        )
        normalized["analysis"].setdefault("cfd", _new_step(WorkflowStep.VALIDATION))
        normalized["analysis"].setdefault("fea", _new_step(WorkflowStep.VALIDATION))
        normalized["analysis"].setdefault("convergence", _convergence_defaults())
        normalized.setdefault("history", [])

        sub_assemblies = normalized.setdefault("sub_assemblies", {})
        for name, sa in list(sub_assemblies.items()):
            sub_assemblies[name] = self._normalize_sub_assembly(name, sa)

        if normalized.get("active_run") is None:
            normalized["active_run"] = self._derive_active_run(normalized["sub_assemblies"])

        return normalized

    def _normalize_sub_assembly(self, name: str, sa: dict[str, Any]) -> dict[str, Any]:
        normalized = _new_sub_assembly(
            name=name,
            level=sa.get("level", 1),
            parent=sa.get("parent"),
        )
        normalized.update(sa)
        normalized.setdefault("current_round_label", f"R{normalized.get('current_iteration', 1)}")
        normalized["max_agent_rounds"] = max(5, int(normalized.get("max_agent_rounds", 5)))
        normalized.setdefault("artifacts", [])
        normalized.setdefault("deliverables", [])
        normalized.setdefault("step_deliverables", {})
        normalized.setdefault("dependencies", [])

        existing_steps = normalized.get("steps", {})
        normalized["steps"] = {}
        for step in WORKFLOW_STEPS:
            step_state = _new_step(step)
            step_state.update(existing_steps.get(step.value, {}))
            if step.value in normalized.get("step_deliverables", {}):
                step_state["expected_deliverables"] = normalized["step_deliverables"][step.value]
            normalized["steps"][step.value] = step_state

        normalized["current_step"] = self._first_incomplete_step(normalized["steps"])
        return normalized

    def _first_incomplete_step(self, steps: dict[str, dict[str, Any]]) -> str:
        for step in WORKFLOW_STEPS:
            status = steps[step.value]["status"]
            if status in {StepStatus.PENDING.value, StepStatus.RUNNING.value, StepStatus.FAILED.value}:
                return step.value
        return WorkflowStep.RELEASE.value

    def _derive_active_run(
        self,
        sub_assemblies: dict[str, dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        running: list[dict[str, Any]] = []
        for name, sa in sub_assemblies.items():
            for step_name, step in sa.get("steps", {}).items():
                if step.get("status") == StepStatus.RUNNING.value:
                    running.append(
                        {
                            "sub_assembly": name,
                            "step": step_name,
                            "agent": step.get("agent"),
                            "iteration": sa.get("current_iteration", 1),
                            "round_label": sa.get(
                                "current_round_label",
                                f"R{sa.get('current_iteration', 1)}",
                            ),
                            "started_at": step.get("started_at"),
                        }
                    )

        if not running:
            return None

        running.sort(key=lambda item: item.get("started_at") or "", reverse=True)
        return running[0]

    # ── Export ─────────────────────────────────────────────────────

    def export_status_json(self, path: Optional[Path] = None) -> Path:
        out = path or (PROJECT_ROOT / "exports" / "workflow_status.json")
        out.parent.mkdir(parents=True, exist_ok=True)

        summary = {
            "project": self.state["project"],
            "project_code": self.state.get("project_code"),
            "updated_at": self.state.get("updated_at"),
            "iteration": self.state.get("current_iteration", 1),
            "current_round_label": self.state.get("current_round_label"),
            "active_run": self.state.get("active_run"),
            "sub_assemblies": {},
            "convergence": self.state.get("analysis", {}).get("convergence", {}),
        }

        for name in self.get_sub_assemblies():
            summary["sub_assemblies"][name] = self.get_progress(name)

        with open(out, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, ensure_ascii=False)

        return out
