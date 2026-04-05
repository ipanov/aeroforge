"""Core workflow engine for the AeroForge iterative design process.

Preferred mode: execute a project-specific workflow profile produced by a user
or an LLM. Legacy enum-based aircraft templates are retained only as fallback.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

import logging

from .aircraft_types import AnalysisLevel, get_type_definition
from .workflow_profile import WorkflowProfile, load_workflow_profile
from .state_manager import (
    StepStatus, StateManager, WorkflowStep,
    ProjectPhase, DesignStep, PHASE_ALLOWED_STEPS, PHASE_ORDER,
)

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Main orchestrator for the aircraft design workflow."""

    def __init__(
        self,
        state_file: Optional[Path] = None,
    ) -> None:
        self._sm = StateManager(state_file)
        self._type_def: Optional[Any] = None
        self._n8n_client: Any = None
        self._n8n_process: Any = None
        self._init_n8n()

    @property
    def n8n_available(self) -> bool:
        """Whether n8n is reachable."""
        return self._n8n_client is not None

    # ── Project lifecycle ──────────────────────────────────────────

    def create_project(
        self,
        aircraft_type: str,
        project_name: str,
        overrides: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Create a new project from an aircraft type template.

        The aircraft_type is a free-form string. If it matches a reference
        template, that template is used for sub-assembly defaults.
        """
        self._type_def = get_type_definition(aircraft_type)
        overrides = overrides or {}
        metadata = metadata or {}

        sa_names: list[str] = []
        level_map: dict[str, int] = {}
        parent_map: dict[str, Optional[str]] = {}

        for sa_tmpl in self._type_def.sub_assemblies:
            sa_names.append(sa_tmpl.name)
            level_map[sa_tmpl.name] = sa_tmpl.level
            parent_map[sa_tmpl.name] = sa_tmpl.parent

        self._sm.initialize(sa_names, level_map, parent_map)
        self._sm.set_project_metadata(
            project=project_name,
            aircraft_type=aircraft_type,
            project_code=metadata.get("project_code", "PRJ1"),
            project_scope=metadata.get("project_scope", "aircraft"),
            round_label=metadata.get("round_label", "R1"),
        )

        state = self._sm.state
        state["current_iteration"] = 1

        for sa_tmpl in self._type_def.sub_assemblies:
            if sa_tmpl.depends_on:
                self._sm.set_dependency(sa_tmpl.name, sa_tmpl.depends_on)
            if sa_tmpl.analysis_level == AnalysisLevel.NONE:
                self._skip_aero_steps(sa_tmpl.name)
            elif sa_tmpl.analysis_level == AnalysisLevel.STRUCTURAL_ONLY:
                self._skip_aero_steps(sa_tmpl.name, keep_research=True)

        state["validation_criteria"] = self._serialize_criteria(
            self._type_def.validation_criteria
        )
        self._sm.save()
        self._refresh_monitoring_assets()
        final_state = self._sm.state

        ac_str = aircraft_type.value if hasattr(aircraft_type, "value") else str(aircraft_type)
        self._n8n_client.create_workflow(project_name, ac_str)
        self._n8n_client.sync_project(
                project_name=project_name,
                aircraft_type=ac_str,
                project_scope=metadata.get("project_scope", "aircraft"),
                round_label=metadata.get("round_label", "R1"),
                workflow_profile={"sub_assemblies": sa_names},
            )

        return final_state

    def create_project_from_profile(
        self,
        profile: WorkflowProfile,
        project_name: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Create a project from an external workflow profile."""

        metadata = metadata or {}
        sa_names = [item.name for item in profile.sub_assemblies]
        level_map = {item.name: item.level for item in profile.sub_assemblies}
        parent_map = {item.name: item.parent for item in profile.sub_assemblies}

        self._sm.initialize(sa_names, level_map, parent_map)
        self._sm.set_project_metadata(
            project=project_name,
            aircraft_type=profile.aircraft_type,
            project_code=metadata.get("project_code", "PRJ1"),
            project_scope=profile.project_scope,
            round_label=profile.round_label,
        )

        state = self._sm.state
        state["validation_criteria"] = profile.validation_criteria
        state["top_object_name"] = profile.top_object_name

        for item in profile.sub_assemblies:
            if item.dependencies:
                self._sm.set_dependency(item.name, item.dependencies)
            self._sm.set_sub_assembly_profile(
                item.name,
                deliverables=item.deliverables,
                step_deliverables=item.step_deliverables,
                notes=item.notes,
            )
            if item.analysis_scope in {"none", "off_the_shelf"}:
                self._skip_aero_steps(item.name)
            elif item.analysis_scope in {"structural_only", "procurement_only"}:
                self._skip_aero_steps(item.name, keep_research=True)

        self._sm.save()
        self._refresh_monitoring_assets()
        final_state = self._sm.state
        self._n8n_client.sync_project(
            project_name=project_name,
            aircraft_type=profile.aircraft_type,
            project_scope=profile.project_scope,
            round_label=profile.round_label,
            workflow_profile={
                "top_object_name": profile.top_object_name,
                "sub_assemblies": [
                    {
                        "name": item.name,
                        "dependencies": item.dependencies,
                        "analysis_scope": item.analysis_scope,
                        "deliverables": item.deliverables,
                        "step_deliverables": item.step_deliverables,
                    }
                    for item in profile.sub_assemblies
                ],
            },
        )
        return final_state

    def create_project_from_profile_file(
        self,
        profile_path: Path,
        project_name: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Load a profile from disk and create a project from it."""

        profile = load_workflow_profile(profile_path)
        return self.create_project_from_profile(profile, project_name, metadata=metadata)

    def load_project(self) -> dict[str, Any]:
        state = self._sm.load()
        ac_type_str = state.get("aircraft_type")
        if ac_type_str:
            try:
                self._type_def = get_type_definition(ac_type_str)
            except (ValueError, KeyError):
                self._type_def = None
        self._cleanup_stale_runs()
        return state

    def _cleanup_stale_runs(self) -> None:
        """Detect and clean up active runs that are stale after a restart.

        A run is stale if the corresponding step status is not RUNNING,
        or the run has been active for more than 1 hour.
        """
        import calendar
        import time as _time

        STALE_THRESHOLD_SECONDS = 3600

        state = self._sm.state
        active_runs = state.get("active_runs", [])
        if not active_runs:
            return

        now_utc = calendar.timegm(_time.gmtime())
        cleaned = []
        kept = []

        for run in active_runs:
            node_name = run.get("node", run.get("sub_assembly", ""))
            step_name = run.get("step", "")
            started_at = run.get("started_at", "")

            # Check: does the step actually have RUNNING status?
            is_actually_running = False
            try:
                record = self._sm.get_step(node_name, step_name)
                is_actually_running = record.get("status") == StepStatus.RUNNING.value
            except (KeyError, RuntimeError):
                pass

            # Check: has it been running too long?
            is_stale_by_time = False
            if started_at:
                try:
                    started_ts = calendar.timegm(
                        _time.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ")
                    )
                    is_stale_by_time = (now_utc - started_ts) > STALE_THRESHOLD_SECONDS
                except (ValueError, OverflowError):
                    is_stale_by_time = True

            if not is_actually_running or is_stale_by_time:
                cleaned.append(run)
                if is_actually_running:
                    try:
                        self._sm.reset_step(node_name, step_name)
                    except Exception:
                        pass
            else:
                kept.append(run)

        if cleaned:
            state["active_runs"] = kept
            self._sm.save()
            logger.warning(
                "Cleaned up %d stale active run(s): %s",
                len(cleaned),
                [(r.get("node"), r.get("step")) for r in cleaned],
            )

    # ── Step execution ─────────────────────────────────────────────

    def start_iteration(self, sub_assembly: str, round_label: Optional[str] = None) -> int:
        iteration = self._sm.start_new_iteration(sub_assembly, round_label=round_label)
        self._refresh_monitoring_assets()
        self._n8n_client.execute_step(sub_assembly, "start_iteration", {"iteration": iteration})
        return iteration

    def rename_round(self, sub_assembly: str, round_label: str) -> None:
        self._sm.set_round_label(sub_assembly, round_label)
        self._refresh_monitoring_assets()

    def start_step(
        self,
        sub_assembly: str,
        step: str | WorkflowStep,
        agent: Optional[str] = None,
    ) -> None:
        step_name = step.value if isinstance(step, WorkflowStep) else step
        self._sm.start_step(sub_assembly, step_name, agent=agent)
        self._refresh_monitoring_assets()

        self._n8n_client.execute_step(sub_assembly, step_name)

    def complete_step(
        self,
        sub_assembly: str,
        step: str | WorkflowStep,
        output_files: Optional[list[str]] = None,
        notes: str = "",
    ) -> None:
        step_name = step.value if isinstance(step, WorkflowStep) else step
        self._sm.complete_step(
            sub_assembly,
            step_name,
            output_files=output_files,
            notes=notes,
        )
        self._refresh_monitoring_assets()

        self._n8n_client.update_status(sub_assembly, step_name, "done", notes=notes)

    def fail_step(
        self,
        sub_assembly: str,
        step: str | WorkflowStep,
        reason: str = "",
    ) -> None:
        step_name = step.value if isinstance(step, WorkflowStep) else step
        self._sm.fail_step(sub_assembly, step_name, reason=reason)
        self._refresh_monitoring_assets()

        self._n8n_client.update_status(sub_assembly, step_name, "failed", notes=reason)

    def reset_step(self, sub_assembly: str, step: str | WorkflowStep) -> None:
        step_name = step.value if isinstance(step, WorkflowStep) else step
        self._sm.reset_step(sub_assembly, step_name)
        self._refresh_monitoring_assets()

    def run_round(
        self,
        sub_assembly: str,
        agent_proposal: str = "aerodynamicist",
    ) -> dict[str, Any]:
        """Start a new aero-structural round by launching the proposal step."""

        sa = self._sm.get_sub_assembly(sub_assembly)
        next_round = sa.get("agent_round", 0) + 1
        max_rounds = sa.get("max_agent_rounds", 5)
        if next_round > max_rounds:
            raise RuntimeError(
                f"Max agent rounds ({max_rounds}) exceeded for '{sub_assembly}'."
            )

        self.start_step(sub_assembly, WorkflowStep.AERO_PROPOSAL, agent=agent_proposal)
        active = self._sm.get_active_run()
        return {
            "sub_assembly": sub_assembly,
            "round": next_round,
            "max_rounds": max_rounds,
            "active_run": active,
        }

    def complete_round(
        self,
        sub_assembly: str,
        proposal_files: Optional[list[str]] = None,
        review_notes: str = "",
        response_notes: str = "",
        consensus_reached: bool = False,
    ) -> dict[str, Any]:
        """Record the agent loop in strict sequence."""

        self.complete_step(
            sub_assembly,
            WorkflowStep.AERO_PROPOSAL,
            output_files=proposal_files,
            notes="Aero proposal completed",
        )
        self.start_step(sub_assembly, WorkflowStep.STRUCTURAL_REVIEW, agent="structural_engineer")
        self.complete_step(sub_assembly, WorkflowStep.STRUCTURAL_REVIEW, notes=review_notes)
        self.start_step(sub_assembly, WorkflowStep.AERO_RESPONSE, agent="aerodynamicist")
        self.complete_step(sub_assembly, WorkflowStep.AERO_RESPONSE, notes=response_notes)

        if consensus_reached:
            self.start_step(sub_assembly, WorkflowStep.CONSENSUS, agent="consensus")
            self.complete_step(sub_assembly, WorkflowStep.CONSENSUS, notes="All agents agreed")

        sa = self._sm.get_sub_assembly(sub_assembly)
        return {
            "sub_assembly": sub_assembly,
            "round": sa.get("agent_round", 0),
            "consensus_reached": consensus_reached,
            "current_step": sa["current_step"],
        }

    # ── Status queries ─────────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        state = self._sm.state
        status: dict[str, Any] = {
            "project": state.get("project", "Unknown"),
            "project_code": state.get("project_code", "PRJ1"),
            "project_scope": state.get("project_scope", "aircraft"),
            "aircraft_type": state.get("aircraft_type", "Unknown"),
            "project_phase": state.get("project_phase", "DESIGN"),
            "updated_at": state.get("updated_at"),
            "active_runs": self._sm.get_active_runs(),
            "nodes": state.get("nodes", {}),
            "root_node": state.get("root_node"),
            "validation": state.get("validation", {}),
            "n8n_available": self.n8n_available,
            "design_phase_complete": self._sm.check_design_phase_complete(),
        }
        return status

    def get_node_status(self, name: str) -> dict[str, Any]:
        node = self._sm.get_node(name)
        return {
            "name": name,
            "type": node.get("type"),
            "parent": node.get("parent"),
            "children": node.get("children", []),
            "design_cycle": node.get("design_cycle"),
            "current_design_step": node.get("current_design_step"),
            "iteration": node.get("iteration", 1),
            "drawing_approved": node.get("drawing_approved", False),
            "artifacts": node.get("artifacts", []),
        }

    def get_next_action(self) -> Optional[dict[str, Any]]:
        """Return the next recommended action, respecting project phase.

        Phase-aware: only recommends actions valid for the current phase.
        Uses dependency order (leaves-first) for IMPLEMENTATION phase.
        """
        # Check for already-running steps first
        active_runs = self._sm.get_active_runs()
        if active_runs:
            ar = active_runs[0]
            return {
                "sub_assembly": ar.get("node", ar.get("sub_assembly", "")),
                "step": ar.get("step", ""),
                "action": "running",
            }

        current_phase = self._sm.get_project_phase()

        # REQUIREMENTS phase — complete requirements before anything else
        if current_phase == ProjectPhase.REQUIREMENTS.value:
            if not self._sm.is_phase_complete(current_phase):
                return {
                    "sub_assembly": "__project__",
                    "step": "REQUIREMENTS",
                    "action": "complete_requirements",
                    "message": "Complete project requirements before proceeding.",
                }
            return {
                "sub_assembly": "__project__",
                "step": "REQUIREMENTS",
                "action": "advance_phase",
                "message": "Requirements complete. Advance to RESEARCH phase.",
            }

        # RESEARCH phase — populate RAG, gather domain data
        if current_phase == ProjectPhase.RESEARCH.value:
            if not self._sm.is_phase_complete(current_phase):
                return {
                    "sub_assembly": "__project__",
                    "step": "RESEARCH",
                    "action": "populate_rag",
                    "message": "Populate RAG database with domain research before design.",
                }
            return {
                "sub_assembly": "__project__",
                "step": "RESEARCH",
                "action": "advance_phase",
                "message": "Research complete. Advance to DESIGN phase.",
            }

        # VALIDATION / RELEASE — delegate to existing logic
        if current_phase == ProjectPhase.VALIDATION.value:
            if self._sm.all_complete():
                return self._check_final_validation()
            return {
                "sub_assembly": "__project__",
                "step": "VALIDATION",
                "action": "run_validation",
                "message": "Run CFD + FEA validation on assembled top object.",
            }

        if current_phase == ProjectPhase.RELEASE.value:
            return None  # Terminal — nothing to do

        # DESIGN or IMPLEMENTATION — find next pending step within allowed set
        allowed = PHASE_ALLOWED_STEPS.get(current_phase, set())
        if not allowed:
            return None

        # Use implementation order (leaves-first) for IMPLEMENTATION phase
        if current_phase == ProjectPhase.IMPLEMENTATION.value:
            try:
                node_order = self._sm.get_implementation_order()
            except Exception:
                node_order = self._sm.get_sub_assemblies()
        else:
            node_order = self._sm.get_sub_assemblies()

        for name in node_order:
            node = self._sm.get_node(name)
            dc = node.get("design_cycle")
            if dc is None:
                continue  # Off-shelf, skip
            if self._sm.is_complete(name):
                continue
            current = node.get("current_design_step", "")
            if not current or current not in dc:
                continue
            # Only recommend steps allowed in the current phase
            if current not in allowed:
                continue
            status = dc[current].get("status", StepStatus.PENDING.value)
            if status in {StepStatus.PENDING.value, StepStatus.FAILED.value}:
                return {
                    "sub_assembly": name,
                    "step": current,
                    "action": "start" if status == StepStatus.PENDING.value else "retry",
                }

        # All nodes done for this phase — suggest advancing
        if self._sm.is_phase_complete(current_phase):
            return {
                "sub_assembly": "__project__",
                "step": current_phase,
                "action": "advance_phase",
                "message": f"Phase {current_phase} complete. Ready to advance.",
            }
        return None

    def get_dependency_graph(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for name in self._sm.get_sub_assemblies():
            sa = self._sm.get_sub_assembly(name)
            result[name] = sa.get("dependencies", [])
        return result

    # ── Final validation ───────────────────────────────────────────

    def start_final_validation(self) -> dict[str, Any]:
        state = self._sm.state
        state.setdefault("validation", {})
        state["validation"]["cfd"] = {
            "name": "CFD_FULL_ASSEMBLY_VALIDATION",
            "status": StepStatus.RUNNING.value,
            "started_at": self._now_iso(),
            "notes": "Running synthetic wind tunnel analysis on the assembled top object.",
        }
        state["validation"]["fea"] = {
            "name": "FEA_FULL_ASSEMBLY_VALIDATION",
            "status": StepStatus.RUNNING.value,
            "started_at": self._now_iso(),
            "notes": "Running structural analysis on the assembled top object.",
        }
        self._sm.set_project_phase("VALIDATION")
        self._sm.save()
        self._refresh_monitoring_assets()

        return {
            "status": "started",
            "cfd": "running",
            "fea": "running",
            "message": "Full-aircraft CFD and FEA validation started on the assembled top object.",
        }

    def complete_cfd(
        self,
        passed: bool,
        results_files: Optional[list[str]] = None,
        notes: str = "",
    ) -> None:
        state = self._sm.state
        cfd = state.get("validation", {}).get("cfd", {})
        cfd["status"] = StepStatus.DONE.value if passed else StepStatus.FAILED.value
        cfd["completed_at"] = self._now_iso()
        cfd["passed"] = passed
        if results_files:
            cfd["output_files"] = results_files
        if notes:
            cfd["notes"] = notes
        self._sm.save()
        self._refresh_monitoring_assets()

    def complete_fea(
        self,
        passed: bool,
        results_files: Optional[list[str]] = None,
        notes: str = "",
    ) -> None:
        state = self._sm.state
        fea = state.get("validation", {}).get("fea", {})
        fea["status"] = StepStatus.DONE.value if passed else StepStatus.FAILED.value
        fea["completed_at"] = self._now_iso()
        fea["passed"] = passed
        if results_files:
            fea["output_files"] = results_files
        if notes:
            fea["notes"] = notes
        self._sm.save()
        self._refresh_monitoring_assets()

    def check_convergence(self) -> dict[str, Any]:
        state = self._sm.state
        convergence = state.get("validation", {}).get("convergence", {})
        all_met = all(convergence.values()) if convergence else False
        return {
            "criteria": convergence,
            "all_met": all_met,
            "ready_for_release": all_met,
        }

    # ── Dashboard / export ────────────────────────────────────────

    def generate_dashboard(self, output_path: Optional[Path] = None) -> Path:
        from .dashboard import DashboardGenerator

        generator = DashboardGenerator(self._sm)
        return generator.generate(output_path)

    def export_status(self, path: Optional[Path] = None) -> Path:
        return self._sm.export_status_json(path)

    # ── Internal helpers ───────────────────────────────────────────

    def _skip_aero_steps(self, name: str, keep_research: bool = False) -> None:
        skip_steps = [
            WorkflowStep.AERO_PROPOSAL,
            WorkflowStep.STRUCTURAL_REVIEW,
            WorkflowStep.AERO_RESPONSE,
            WorkflowStep.CONSENSUS,
        ]
        if not keep_research:
            skip_steps.append(WorkflowStep.RESEARCH)

        for step in skip_steps:
            self._sm.skip_step(name, step.value, reason="Not applicable for this component type")

    def _check_final_validation(self) -> Optional[dict[str, Any]]:
        state = self._sm.state
        cfd = state.get("validation", {}).get("cfd", {})
        fea = state.get("validation", {}).get("fea", {})

        cfd_status = cfd.get("status", StepStatus.PENDING.value)
        fea_status = fea.get("status", StepStatus.PENDING.value)

        if cfd_status == StepStatus.PENDING.value and fea_status == StepStatus.PENDING.value:
            return {
                "sub_assembly": "__aircraft__",
                "step": "FINAL_VALIDATION",
                "action": "start_cfd_fea",
            }

        if cfd_status == StepStatus.DONE.value and fea_status == StepStatus.DONE.value:
            convergence = self.check_convergence()
            if convergence["all_met"]:
                return None
            failed = [
                key for key, value in convergence["criteria"].items() if not value
            ]
            # Suggest nodes that likely need redesign based on failed criteria
            nodes = list(self._sm.state.get("nodes", {}).keys())
            return {
                "sub_assembly": "__aircraft__",
                "step": "DESIGN_REVISION",
                "action": "convergence_not_met",
                "failed_criteria": failed,
                "recommended_nodes": nodes,
                "message": (
                    f"Validation failed on {failed}. "
                    f"Call engine.handle_validation_cascade(affected_nodes, reason) "
                    f"to restart design for affected nodes."
                ),
            }

        return None

    def handle_validation_cascade(
        self,
        affected_nodes: list[str],
        reason: str,
        notes: str = "",
    ) -> dict[str, int]:
        """Cascade validation failure back to design phase.

        Called when CFD/FEA validation reveals issues that require
        redesigning specific nodes.  Each affected node gets its
        iteration counter incremented (I1 → I2, etc.), its design
        cycle reset to AERO_PROPOSAL, and its agent_round reset.
        The project phase rolls back to DESIGN.

        This is the **automated** path.  For user-driven rejections
        (e.g. rejecting a drawing), use ``reject_step()`` instead —
        that stays within the same iteration.

        Returns:
            Mapping ``{node_name: new_iteration_number}``.
        """
        result: dict[str, int] = {}
        for name in affected_nodes:
            new_iter = self._sm.start_new_iteration(name)
            result[name] = new_iter

        self._sm.set_project_phase(ProjectPhase.DESIGN, force=True)
        self._sm._append_history(
            f"Validation cascade: {reason}. "
            f"Affected nodes: {list(result.keys())}. "
            f"New iterations: {result}. {notes}".rstrip()
        )
        self._sm.save()
        return result

    def _serialize_criteria(self, criteria: Any) -> dict[str, Any]:
        from dataclasses import asdict

        return asdict(criteria)

    def _refresh_monitoring_assets(self) -> None:
        self.generate_dashboard()
        self.export_status()
        self._sync_n8n_visual()

    def _sync_n8n_visual(self) -> None:
        """Rebuild the n8n visual dashboard workflow from current state.

        Called on every state change. If n8n is unavailable, logs a warning
        but does not raise — the HTML dashboard is still the primary asset.
        """
        if self._n8n_client is None:
            return
        try:
            from .n8n_workflow_builder import N8nWorkflowBuilder

            state = self._sm.state
            project_name = state.get("project", "AeroForge")
            builder = N8nWorkflowBuilder(project_name)

            # If no nodes/sub_assemblies exist yet, build skeleton
            nodes = state.get("nodes", state.get("sub_assemblies", {}))
            if not nodes:
                current_phase = state.get("project_phase", "REQUIREMENTS")
                workflow_json = builder.build_skeleton(current_phase)
            else:
                workflow_json = builder.build_full(state)

            self._n8n_client.sync_visual_workflow(workflow_json)
        except Exception as exc:
            logger.warning("Failed to sync n8n visual dashboard: %s", exc)

    @staticmethod
    def _now_iso() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def sync_n8n_skeleton(self, project_name: str, current_phase: str = "REQUIREMENTS") -> None:
        """Push a skeleton visual workflow to n8n (for /aeroforge-init).

        Call this early in the init process, before the component hierarchy
        is known, to give the user immediate visual feedback in n8n.
        """
        if self._n8n_client is None:
            from .n8n_client import N8nUnavailableError
            raise N8nUnavailableError(
                "n8n is required but not available. Cannot create workflow."
            )
        from .n8n_workflow_builder import N8nWorkflowBuilder

        builder = N8nWorkflowBuilder(project_name)
        workflow_json = builder.build_skeleton(current_phase)
        self._n8n_client.sync_visual_workflow(workflow_json)
        logger.info("n8n skeleton workflow synced for '%s'", project_name)

    # ── LLM-facing summaries ─────────────────────────────────────────

    def get_workflow_summary(self) -> str:
        """Return a formatted text summary the LLM reads to understand current state."""
        state = self._sm.load()
        project = state.get("project", "Unknown")
        ac_type = state.get("aircraft_type", "Unknown")
        phase = state.get("project_phase", "DESIGN")

        lines = [
            f"# Workflow Status: {project}",
            f"Aircraft type: {ac_type} | Phase: {phase}",
            "",
        ]

        active_runs = state.get("active_runs", [])
        if active_runs:
            for ar in active_runs:
                lines.append(
                    f"**ACTIVE**: {ar.get('node', '?')}:{ar.get('step', '?')} "
                    f"(agent: {ar.get('agent', 'system')})"
                )
        else:
            lines.append("**No step currently running.**")
        lines.append("")

        # Render node tree
        nodes = state.get("nodes", {})
        root = state.get("root_node")

        def _render_node(name: str, indent: int = 0) -> None:
            node = nodes.get(name, {})
            prefix = "  " * indent
            ntype = node.get("type", "?")
            dc = node.get("design_cycle")
            if dc is None:
                lines.append(f"{prefix}{name} [{ntype}] (off-shelf)")
                return
            step_line = []
            for s_name, s_info in dc.items():
                status = s_info.get("status", "pending") if isinstance(s_info, dict) else "?"
                icon = {"done": "+", "running": ">", "failed": "X",
                        "pending": "o", "skipped": "-"}.get(status, "?")
                abbrev = s_name[:3]
                cell = f"{icon}{abbrev}"
                if isinstance(s_info, dict):
                    history = s_info.get("history", [])
                    rejections = [h for h in history if h.get("action") == "rejected"]
                    if rejections:
                        cell += f"({len(rejections)}R)"
                step_line.append(cell)
            approved = "APPROVED" if node.get("drawing_approved") else ""
            lines.append(f"{prefix}{name} [{ntype}] {' '.join(step_line)} {approved}")

            for child in node.get("children", []):
                _render_node(child, indent + 1)

        if root and root in nodes:
            _render_node(root)
        else:
            for name in nodes:
                if nodes[name].get("parent") is None:
                    _render_node(name)

        return "\n".join(lines)

    def get_next_recommended_action(self) -> dict[str, Any]:
        """Return a detailed recommendation for what the LLM should do next.

        More detailed than get_next_action() — includes context about
        why this action is recommended and what agent to use.
        """
        basic = self.get_next_action()
        if not basic:
            return {"action": "idle", "message": "All work complete or no pending steps."}

        result = {**basic}
        sa_name = basic.get("sub_assembly", "")
        step = basic.get("step", "")

        # Add agent recommendation
        agent_map = {
            "AERO_PROPOSAL": "aerodynamicist",
            "STRUCTURAL_REVIEW": "structural-engineer",
            "AERO_RESPONSE": "aerodynamicist",
            "CONSENSUS": "system",
            "VALIDATION": "wind-tunnel-engineer + structures-analyst",
        }
        result["recommended_agent"] = agent_map.get(step, "system")

        # Add step history (rejections, feedback)
        if sa_name and sa_name != "__aircraft__":
            try:
                history = self._sm.get_step_history(sa_name, step)
                if history:
                    result["step_history"] = history
                    rejections = [h for h in history if h.get("action") == "rejected"]
                    if rejections:
                        last = rejections[-1]
                        result["rework_context"] = (
                            f"This step was rejected {len(rejections)} time(s). "
                            f"Last reason: {last.get('reason', 'no reason given')}. "
                            f"Rework notes: {last.get('rework_notes', 'none')}"
                        )
            except Exception:
                pass

        return result

    def reject_step(
        self,
        sub_assembly: str,
        step: str | WorkflowStep,
        reason: str = "",
        rework_notes: str = "",
    ) -> None:
        """Reject a step's deliverable and reset for rework."""
        step_name = step.value if isinstance(step, WorkflowStep) else step
        self._sm.reject_step(sub_assembly, step_name, reason=reason, rework_notes=rework_notes)
        self._refresh_monitoring_assets()

        self._n8n_client.update_status(
            sub_assembly, step_name, "rejected",
            notes=f"REJECTED: {reason}",
        )

    def record_user_feedback(
        self,
        sub_assembly: str,
        step: str | WorkflowStep,
        feedback: str,
    ) -> None:
        """Record user design feedback without changing step status."""
        step_name = step.value if isinstance(step, WorkflowStep) else step
        self._sm.record_user_feedback(sub_assembly, step_name, feedback)

    # ── Provider resolution ─────────────────────────────────────────

    def resolve_provider(self, category: str) -> Any:
        """Resolve a provider for the given category using project config.

        System-level categories (cfd, fea, airfoil) use system_providers.yaml.
        Project-level categories (manufacturing, slicer) use the project's
        aeroforge.yaml.

        Args:
            category: Provider category (e.g., "cfd", "fea", "manufacturing").

        Returns:
            The resolved provider instance, or None if not available.
        """
        try:
            import src.providers  # noqa: F401 — triggers auto-registration
            from .project_manager import ProjectManager
            from src.providers.base import ProviderRegistry
            from src.providers.hardware import HardwareProfile

            pm = ProjectManager()
            merged = pm.get_merged_providers()

            # Map categories to protocol types
            protocol_map: dict[str, type] = {}
            try:
                from src.providers.cfd.protocol import CFDProvider
                protocol_map["cfd"] = CFDProvider
            except ImportError:
                pass
            try:
                from src.providers.fea.protocol import FEAProvider
                protocol_map["fea"] = FEAProvider
            except ImportError:
                pass
            try:
                from src.providers.manufacturing.protocol import ManufacturingProvider
                protocol_map["manufacturing"] = ManufacturingProvider
            except ImportError:
                pass
            try:
                from src.providers.slicer.protocol import SlicerProvider
                protocol_map["slicer"] = SlicerProvider
            except ImportError:
                pass
            try:
                from src.providers.airfoil.protocol import AirfoilProvider
                protocol_map["airfoil"] = AirfoilProvider
            except ImportError:
                pass

            proto = protocol_map.get(category)
            if proto is None:
                logger.warning("Unknown provider category: %s", category)
                return None

            # Load hardware profile from system config
            sys_cfg = pm.load_system_providers()
            hw_cfg = sys_cfg.get("hardware", {})
            hw = HardwareProfile(
                cuda_available=hw_cfg.get("cuda_available", False),
                gpu_name=hw_cfg.get("gpu_name"),
            )

            return ProviderRegistry.resolve_from_config(
                proto, merged, category, hardware=hw,
            )
        except Exception as exc:
            logger.debug("Provider resolution failed for %s: %s", category, exc)
            return None

    def get_provider_status(self) -> dict[str, Any]:
        """Return the status of all provider categories."""
        categories = ["cfd", "fea", "airfoil", "manufacturing", "slicer"]
        status: dict[str, Any] = {}
        for cat in categories:
            provider = self.resolve_provider(cat)
            if provider:
                status[cat] = {
                    "provider_id": getattr(provider, "provider_id", "unknown"),
                    "display_name": getattr(provider, "display_name", "unknown"),
                    "available": provider.is_available() if hasattr(provider, "is_available") else True,
                }
            else:
                status[cat] = {"provider_id": None, "available": False}
        return status

    def _init_n8n(self) -> None:
        """Connect to n8n. Auto-launch if not running. Hard-fail if unreachable.

        n8n is a MANDATORY component — no workflow operations proceed without it.
        """
        from .n8n_client import N8nClient, N8nUnavailableError

        client = N8nClient()
        if client.health_check():
            self._n8n_client = client
            return

        # n8n not running — auto-launch it
        logger.info("n8n not reachable — auto-launching...")
        try:
            from .server import launch_n8n_process
            self._n8n_process = launch_n8n_process()
        except Exception as exc:
            raise N8nUnavailableError(
                f"n8n is not running and auto-launch failed: {exc}\n"
                "Start n8n manually with: n8n start"
            ) from exc

        # Wait for n8n to become reachable (up to 30s)
        import time as _time
        for attempt in range(30):
            _time.sleep(1)
            if client.health_check():
                self._n8n_client = client
                logger.info("n8n is now reachable after auto-launch.")
                return

        # Still not reachable after 30s — hard stop
        if self._n8n_process and self._n8n_process.poll() is not None:
            detail = f"n8n process exited with code {self._n8n_process.returncode}"
        else:
            detail = "n8n process running but health check fails"

        raise N8nUnavailableError(
            f"n8n did not become reachable within 30 seconds ({detail}).\n"
            f"URL: {client._base_url}\n"
            "Start n8n manually with: n8n start"
        )
