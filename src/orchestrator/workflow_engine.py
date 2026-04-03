"""Core workflow engine for the AeroForge iterative design process.

Preferred mode: execute a project-specific workflow profile produced by a user
or an LLM. Legacy enum-based aircraft templates are retained only as fallback.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from .aircraft_types import AircraftType, AnalysisLevel, get_type_definition
from .workflow_profile import WorkflowProfile, load_workflow_profile
from .state_manager import StepStatus, StateManager, WorkflowStep


class WorkflowEngine:
    """Main orchestrator for the aircraft design workflow."""

    def __init__(
        self,
        state_file: Optional[Path] = None,
    ) -> None:
        self._sm = StateManager(state_file)
        self._type_def: Optional[Any] = None
        self._n8n_client: Any = None
        self._init_n8n()

    @property
    def n8n_available(self) -> bool:
        """Whether the n8n visibility layer is reachable."""
        return self._n8n_client is not None

    # ── Project lifecycle ──────────────────────────────────────────

    def create_project(
        self,
        aircraft_type: AircraftType,
        project_name: str,
        overrides: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Create a new project from an aircraft type template."""

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
            aircraft_type=aircraft_type.value,
            project_code=metadata.get("project_code", "AIR4"),
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

        if self._n8n_client:
            self._n8n_client.create_workflow(project_name, aircraft_type.value)
            self._n8n_client.sync_project(
                project_name=project_name,
                aircraft_type=aircraft_type.value,
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
            project_code=metadata.get("project_code", "AIR4"),
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
        if self._n8n_client:
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
                self._type_def = get_type_definition(AircraftType(ac_type_str))
            except (ValueError, KeyError):
                self._type_def = None
        return state

    # ── Step execution ─────────────────────────────────────────────

    def start_iteration(self, sub_assembly: str, round_label: Optional[str] = None) -> int:
        iteration = self._sm.start_new_iteration(sub_assembly, round_label=round_label)
        self._refresh_monitoring_assets()
        if self._n8n_client:
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

        if self._n8n_client:
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

        if self._n8n_client:
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

        if self._n8n_client:
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
            "project_code": state.get("project_code", "AIR4"),
            "project_scope": state.get("project_scope", "aircraft"),
            "aircraft_type": state.get("aircraft_type", "Unknown"),
            "iteration": state.get("current_iteration", 1),
            "round_label": state.get("current_round_label"),
            "updated_at": state.get("updated_at"),
            "active_run": self._sm.get_active_run(),
            "sub_assemblies": self._sm.get_full_progress(),
            "convergence": state.get("analysis", {}).get("convergence", {}),
            "analysis_policy": state.get("analysis", {}).get("policy", {}),
            "n8n_available": self.n8n_available,
            "all_complete": self._sm.all_complete(),
        }

        # RAG database status
        try:
            from src.rag.database import RAGDatabase
            from src.rag.config import RAGConfig

            db = RAGDatabase(RAGConfig())
            status["rag_database"] = db.get_collection_stats() if db.collection_exists() else None
        except Exception:
            status["rag_database"] = None

        return status

    def get_sub_assembly_status(self, name: str) -> dict[str, Any]:
        sa = self._sm.get_sub_assembly(name)
        progress = self._sm.get_progress(name)
        return {
            **progress,
            "steps": sa["steps"],
            "dependencies": sa.get("dependencies", []),
            "artifacts": sa.get("artifacts", []),
        }

    def get_next_action(self) -> Optional[dict[str, Any]]:
        if self._sm.get_active_run():
            active = self._sm.get_active_run()
            return {
                "sub_assembly": active["sub_assembly"],
                "step": active["step"],
                "action": "running",
            }

        if self._sm.all_complete():
            return self._check_final_validation()

        for name in self._sm.get_sub_assemblies():
            if self._sm.is_complete(name):
                continue
            current = self._sm.get_current_step(name)
            status = self._sm.get_status(name, current)
            if status in {StepStatus.PENDING.value, StepStatus.FAILED.value}:
                return {
                    "sub_assembly": name,
                    "step": current,
                    "action": "start" if status == StepStatus.PENDING.value else "retry",
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
        if not self._sm.all_complete():
            incomplete = [
                name for name in self._sm.get_sub_assemblies()
                if not self._sm.is_complete(name)
            ]
            raise RuntimeError(
                f"Cannot start final validation: {incomplete} not complete"
            )

        state = self._sm.state
        state.setdefault("analysis", {})
        state["analysis"]["cfd"] = {
            "name": "CFD_FULL_ASSEMBLY_VALIDATION",
            "status": StepStatus.RUNNING.value,
            "started_at": self._now_iso(),
            "notes": "Running synthetic wind tunnel analysis on the assembled top object.",
        }
        state["analysis"]["fea"] = {
            "name": "FEA_FULL_ASSEMBLY_VALIDATION",
            "status": StepStatus.RUNNING.value,
            "started_at": self._now_iso(),
            "notes": "Running structural analysis on the assembled top object.",
        }
        self._sm.save()
        self._refresh_monitoring_assets()

        return {
            "status": "started",
            "cfd": "running",
            "fea": "running",
            "message": (
                "Full-aircraft CFD and FEA validation started on the assembled top object."
            ),
        }

    def complete_cfd(
        self,
        passed: bool,
        results_files: Optional[list[str]] = None,
        notes: str = "",
    ) -> None:
        state = self._sm.state
        cfd = state.get("analysis", {}).get("cfd", {})
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
        fea = state.get("analysis", {}).get("fea", {})
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
        convergence = state.get("analysis", {}).get("convergence", {})
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
        cfd = state.get("analysis", {}).get("cfd", {})
        fea = state.get("analysis", {}).get("fea", {})

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
            return {
                "sub_assembly": "__aircraft__",
                "step": "DESIGN_REVISION",
                "action": "convergence_not_met",
                "failed_criteria": [
                    key for key, value in convergence["criteria"].items() if not value
                ],
            }

        return None

    def _serialize_criteria(self, criteria: Any) -> dict[str, Any]:
        from dataclasses import asdict

        return asdict(criteria)

    def _refresh_monitoring_assets(self) -> None:
        self.generate_dashboard()
        self.export_status()

    @staticmethod
    def _now_iso() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _init_n8n(self) -> None:
        try:
            from .n8n_client import N8nClient

            client = N8nClient()
            if client.health_check():
                self._n8n_client = client
            else:
                import logging
                logging.getLogger(__name__).warning(
                    "n8n not reachable at %s — workflow continues without live visibility",
                    client._base_url,
                )
                self._n8n_client = None
        except Exception:
            self._n8n_client = None
