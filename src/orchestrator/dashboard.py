"""HTML dashboard generator for workflow status visualization."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from .project_settings import load_project_settings
from .state_manager import DASHBOARD_FILE, StepStatus, WORKFLOW_STEPS, StateManager


STATUS_COLORS: dict[str, str] = {
    StepStatus.DONE.value: "#0f9d58",
    StepStatus.RUNNING.value: "#fbbc04",
    StepStatus.FAILED.value: "#d93025",
    StepStatus.PENDING.value: "#5f6368",
    StepStatus.SKIPPED.value: "#9aa0a6",
}

STATUS_ICONS: dict[str, str] = {
    StepStatus.DONE.value: "&#10004;",
    StepStatus.RUNNING.value: "&#9654;",
    StepStatus.FAILED.value: "&#10008;",
    StepStatus.PENDING.value: "&#9675;",
    StepStatus.SKIPPED.value: "&#8212;",
}

STATUS_LABELS: dict[str, str] = {
    StepStatus.DONE.value: "Done",
    StepStatus.RUNNING.value: "Running",
    StepStatus.FAILED.value: "Failed",
    StepStatus.PENDING.value: "Pending",
    StepStatus.SKIPPED.value: "Skipped",
}


class DashboardGenerator:
    """Generates a self-contained HTML dashboard from workflow state."""

    def __init__(self, state_manager: StateManager) -> None:
        self._sm = state_manager

    def generate(self, output_path: Optional[Path] = None) -> Path:
        path = output_path or DASHBOARD_FILE
        path.parent.mkdir(parents=True, exist_ok=True)

        state = self._sm.state
        html = self._build_html(state)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(html)
        return path

    def _build_html(self, state: dict[str, Any]) -> str:
        project = state.get("project", "AeroForge")
        updated = state.get("updated_at", "N/A")
        iteration = state.get("current_iteration", 1)
        round_label = state.get("current_round_label", f"R{iteration}")
        project_code = state.get("project_code", "AIR4")
        ac_type = state.get("aircraft_type", "Unknown")
        active_run = state.get("active_run")

        sub_assemblies = state.get("sub_assemblies", {})
        analysis = state.get("analysis", {})
        convergence = analysis.get("convergence", {})
        dependency_graph = {
            name: sa.get("dependencies", [])
            for name, sa in sub_assemblies.items()
        }

        rows = [self._render_sub_assembly_row(name, sa, active_run) for name, sa in sub_assemblies.items()]
        summary_html = self._render_summary(sub_assemblies, iteration, active_run)
        active_html = self._render_active_run(active_run, analysis.get("policy", {}))
        flow_html = self._render_flow(active_run)
        dependency_html = self._render_dependency_graph(dependency_graph)
        convergence_html = self._render_convergence(convergence)
        analysis_html = self._render_analysis(analysis)
        history_html = self._render_history(state.get("history", [])[-20:])
        settings_html = self._render_project_settings()

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="10">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project} - Workflow Monitor</title>
    <style>
{self._css()}
    </style>
</head>
<body>
    <header>
        <div>
            <div class="eyebrow">{project_code} / {round_label}</div>
            <h1>{project}</h1>
            <div class="meta">
                <span class="badge">Iteration {iteration}</span>
                <span class="badge type-badge">{ac_type}</span>
                <span class="timestamp">Updated: {updated}</span>
            </div>
        </div>
    </header>

    <main>
        {active_html}
        <section class="summary">{summary_html}</section>
        <section class="flow">{flow_html}</section>
        <section class="settings">{settings_html}</section>
        <section class="workflow-grid">
            <h2>Tracked Sub-Assemblies</h2>
            <table>
                <thead>
                    <tr>
                        <th>Sub-Assembly</th>
                        <th>Iteration</th>
                        <th>Round</th>
                        <th>Progress</th>
                        {" ".join(f"<th>{step.value}</th>" for step in WORKFLOW_STEPS)}
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </section>
        <section class="dependency">{dependency_html}</section>
        <section class="convergence">{convergence_html}</section>
        <section class="analysis">{analysis_html}</section>
        <section class="history">{history_html}</section>
    </main>
</body>
</html>"""

    def _render_active_run(
        self,
        active_run: Optional[dict[str, Any]],
        analysis_policy: dict[str, Any],
    ) -> str:
        if not active_run:
            message = "No step is running right now. The next permitted step can be started from the orchestrator CLI."
            status = "Idle"
            detail = ""
        else:
            status = "Current Step"
            message = (
                f"{active_run['sub_assembly']} is executing {active_run['step']} "
                f"for {active_run.get('round_label', '-')}"
            )
            detail = (
                f"<div class='active-detail'>Agent: {active_run.get('agent') or 'system'} | "
                f"Started: {active_run.get('started_at', '-')}</div>"
            )

        policy_note = analysis_policy.get(
            "notes",
            "Final GPU validation is performed on the assembled top object only.",
        )

        return (
            "<section class='hero'>"
            f"<div class='hero-label'>{status}</div>"
            f"<div class='hero-title'>{message}</div>"
            f"{detail}"
            f"<div class='hero-note'>{policy_note}</div>"
            "</section>"
        )

    def _render_flow(self, active_run: Optional[dict[str, Any]]) -> str:
        active_step = active_run.get("step") if active_run else None
        boxes = []
        for step in WORKFLOW_STEPS:
            css = "flow-step active" if step.value == active_step else "flow-step"
            boxes.append(f"<div class='{css}'>{step.value}</div>")

        return (
            "<h2>Strict Workflow Chart</h2>"
            "<div class='flow-row'>"
            "<div class='flow-stage'><strong>Top-Down</strong><span>Requirements -> parent geometry -> assembly refinement</span></div>"
            "<div class='flow-stage'><strong>Drill-Down</strong><span>Components and details inherit from approved assemblies</span></div>"
            "<div class='flow-stage'><strong>Bottom-Up</strong><span>Rebuild dependent 3D outputs, then validate the assembled top object</span></div>"
            "</div>"
            f"<div class='flow-sequence'>{''.join(boxes)}</div>"
        )

    def _render_sub_assembly_row(
        self,
        name: str,
        sa: dict[str, Any],
        active_run: Optional[dict[str, Any]],
    ) -> str:
        iteration = sa.get("current_iteration", 1)
        round_label = sa.get("current_round_label", f"R{iteration}")
        agent_round = sa.get("agent_round", 0)
        steps = sa.get("steps", {})
        level = sa.get("level", 1)
        current_step = sa.get("current_step")

        done = sum(1 for step in steps.values() if step.get("status") == StepStatus.DONE.value)
        total = len(steps)
        pct = round(done / total * 100) if total else 0

        indent = "&nbsp;" * (level - 1) * 4
        prefix = "&#9492; " if level > 1 else ""
        row_class = "active-row" if active_run and active_run.get("sub_assembly") == name else ""

        cells = []
        for workflow_step in WORKFLOW_STEPS:
            step_data = steps.get(workflow_step.value, {})
            status = step_data.get("status", StepStatus.PENDING.value)
            color = STATUS_COLORS.get(status, STATUS_COLORS[StepStatus.PENDING.value])
            icon = STATUS_ICONS.get(status, STATUS_ICONS[StepStatus.PENDING.value])
            title_parts = [STATUS_LABELS.get(status, status)]
            if workflow_step.value == current_step:
                title_parts.append("Current required step")
            expected = step_data.get("expected_deliverables") or []
            if expected:
                title_parts.append(f"Deliverables: {', '.join(expected)}")
            if step_data.get("notes"):
                title_parts.append(step_data["notes"])
            title = " | ".join(title_parts)
            css = "step-cell highlighted-step" if workflow_step.value == current_step else "step-cell"
            cells.append(
                f'<td class="{css}" style="background:{color};" title="{title}">{icon}</td>'
            )

        bar_color = "#0f9d58" if pct == 100 else "#fbbc04" if pct > 0 else "#5f6368"
        bar_html = (
            f'<div class="progress-bar">'
            f'<div class="progress-fill" style="width:{pct}%;background:{bar_color};"></div>'
            f'<span class="progress-text">{pct}%</span>'
            f'</div>'
        )

        return (
            f'<tr class="{row_class}">'
            f'<td class="name-cell">{indent}{prefix}{name}</td>'
            f'<td class="center">{iteration}</td>'
            f'<td class="center">{round_label} / {agent_round}</td>'
            f'<td>{bar_html}</td>'
            f'{"".join(cells)}'
            f'</tr>'
        )

    def _render_summary(
        self,
        sub_assemblies: dict[str, Any],
        iteration: int,
        active_run: Optional[dict[str, Any]],
    ) -> str:
        total = len(sub_assemblies)
        released = sum(
            1
            for sa in sub_assemblies.values()
            if sa.get("steps", {}).get("RELEASE", {}).get("status") == StepStatus.DONE.value
        )
        running = 1 if active_run else 0
        blocked = sum(
            1
            for sa in sub_assemblies.values()
            if any(step.get("status") == StepStatus.FAILED.value for step in sa.get("steps", {}).values())
        )

        return f"""
        <div class="cards">
            <div class="card">
                <div class="card-value">{iteration}</div>
                <div class="card-label">Iteration</div>
            </div>
            <div class="card">
                <div class="card-value">{total}</div>
                <div class="card-label">Tracked Nodes</div>
            </div>
            <div class="card" style="border-color:#0f9d58;">
                <div class="card-value" style="color:#0f9d58;">{released}</div>
                <div class="card-label">Released</div>
            </div>
            <div class="card" style="border-color:#fbbc04;">
                <div class="card-value" style="color:#fbbc04;">{running}</div>
                <div class="card-label">Running</div>
            </div>
            <div class="card" style="border-color:#d93025;">
                <div class="card-value" style="color:#d93025;">{blocked}</div>
                <div class="card-label">Failed</div>
            </div>
        </div>"""

    def _render_project_settings(self) -> str:
        settings = load_project_settings()
        if not settings:
            return "<h2>Project Settings</h2><p>No persisted tooling profile yet.</p>"

        project = settings.get("project", {})
        available = ", ".join(project.get("available_tooling", []))
        manufacturing = ", ".join(project.get("manufacturing_strategy", []))
        materials = ", ".join(project.get("material_strategy", []))
        production = ", ".join(project.get("production_strategy", []))
        outputs = ", ".join(project.get("output_artifacts", []))
        return (
            "<h2>Project Settings</h2>"
            "<div class='settings-grid'>"
            f"<div class='settings-card'><strong>Top object</strong><span>{project.get('top_object', '-')}</span></div>"
            f"<div class='settings-card'><strong>Scope</strong><span>{project.get('project_scope', '-')}</span></div>"
            f"<div class='settings-card'><strong>Selected tooling</strong><span>{project.get('selected_tooling', '-')}</span></div>"
            f"<div class='settings-card'><strong>Available tooling</strong><span>{available}</span></div>"
            f"<div class='settings-card'><strong>Manufacturing</strong><span>{manufacturing}</span></div>"
            f"<div class='settings-card'><strong>Materials</strong><span>{materials}</span></div>"
            f"<div class='settings-card'><strong>Production</strong><span>{production}</span></div>"
            f"<div class='settings-card'><strong>Outputs</strong><span>{outputs}</span></div>"
            "</div>"
        )

    def _render_dependency_graph(self, dependency_graph: dict[str, list[str]]) -> str:
        if not dependency_graph:
            return "<h2>Dependency Graph</h2><p>No dependencies defined.</p>"

        items = []
        for name, dependencies in dependency_graph.items():
            deps = ", ".join(dependencies) if dependencies else "root node"
            items.append(f"<div class='dependency-item'><strong>{name}</strong><span>{deps}</span></div>")
        return "<h2>Dependency Graph</h2><div class='dependency-grid'>" + "".join(items) + "</div>"

    def _render_convergence(self, convergence: dict[str, bool]) -> str:
        if not convergence:
            return "<h2>Convergence Criteria</h2><p>No criteria defined yet.</p>"

        rows = []
        for key, met in convergence.items():
            icon = "&#10004;" if met else "&#10008;"
            color = "#0f9d58" if met else "#d93025"
            bg = "#d7f8e3" if met else "#fde4e1"
            label = key.replace("_", " ").title()
            rows.append(
                f'<div class="criterion" style="background:{bg};border-color:{color};">'
                f'<span style="color:{color};">{icon}</span> {label}</div>'
            )
        return "<h2>Convergence Criteria</h2><div class='criteria-grid'>" + "".join(rows) + "</div>"

    def _render_analysis(self, analysis: dict[str, Any]) -> str:
        cfd = analysis.get("cfd", {})
        fea = analysis.get("fea", {})

        def render_card(title: str, data: dict[str, Any]) -> str:
            status = data.get("status", StepStatus.PENDING.value)
            color = STATUS_COLORS.get(status, STATUS_COLORS[StepStatus.PENDING.value])
            label = STATUS_LABELS.get(status, status)
            notes = data.get("notes", "")
            return (
                f"<div class='analysis-card' style='border-color:{color};'>"
                f"<h3>{title}</h3>"
                f"<div class='status-line' style='color:{color};'>{label}</div>"
                f"<div class='detail'>Started: {data.get('started_at', '-')}</div>"
                f"<div class='detail'>Completed: {data.get('completed_at', '-')}</div>"
                f"<div class='detail'>{notes}</div>"
                "</div>"
            )

        return (
            "<h2>Final Top-Object Validation</h2>"
            "<div class='analysis-grid'>"
            f"{render_card('Synthetic Wind Tunnel / CFD', cfd)}"
            f"{render_card('Structural / Strength / FEM', fea)}"
            "</div>"
        )

    def _render_history(self, events: list[dict[str, Any]]) -> str:
        if not events:
            return "<h2>Recent History</h2><p>No events recorded.</p>"

        rows = []
        for event in reversed(events):
            rows.append(
                f"<tr><td class='mono'>{event.get('timestamp', '-')}</td><td>{event.get('event', '-')}</td></tr>"
            )
        return (
            "<h2>Recent History</h2>"
            "<table class='history-table'><thead><tr><th>Time</th><th>Event</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
        )

    @staticmethod
    def _css() -> str:
        return """
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: "Segoe UI", system-ui, sans-serif;
            background: linear-gradient(180deg, #08131f 0%, #0f1722 100%);
            color: #e8eaed;
            padding: 24px;
            line-height: 1.5;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.12);
        }
        .eyebrow { color: #8ab4f8; letter-spacing: 0.12em; text-transform: uppercase; font-size: 0.78rem; }
        h1 { font-size: 2rem; margin-top: 6px; }
        h2 { margin-bottom: 12px; font-size: 1.1rem; color: #9ec7ff; }
        .meta { display: flex; gap: 12px; align-items: center; margin-top: 10px; flex-wrap: wrap; }
        .badge {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 0.84rem;
        }
        .type-badge { color: #8ab4f8; }
        .timestamp { color: #94a3b8; font-size: 0.82rem; }
        main { display: grid; gap: 18px; }
        section {
            background: rgba(7, 14, 24, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 18px;
            backdrop-filter: blur(6px);
        }
        .hero {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(15, 157, 88, 0.12) 100%);
            border-color: rgba(138, 180, 248, 0.35);
        }
        .hero-label { color: #9ec7ff; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.12em; }
        .hero-title { font-size: 1.5rem; margin: 8px 0; font-weight: 700; }
        .hero-note, .active-detail { color: #cbd5e1; font-size: 0.92rem; }
        .cards { display: flex; gap: 16px; flex-wrap: wrap; }
        .card {
            min-width: 130px;
            padding: 14px 18px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .card-value { font-size: 1.8rem; font-weight: 700; }
        .card-label { color: #94a3b8; font-size: 0.85rem; margin-top: 4px; }
        .flow-row, .settings-grid, .dependency-grid, .analysis-grid {
            display: grid;
            gap: 12px;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        }
        .flow-stage, .settings-card, .dependency-item, .analysis-card {
            border-radius: 14px;
            padding: 14px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .flow-stage strong, .settings-card strong, .dependency-item strong {
            display: block;
            margin-bottom: 6px;
            color: #dbeafe;
        }
        .flow-stage span, .settings-card span, .dependency-item span, .detail {
            color: #cbd5e1;
            font-size: 0.9rem;
        }
        .flow-sequence {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(132px, 1fr));
            gap: 8px;
            margin-top: 14px;
        }
        .flow-step {
            padding: 10px 12px;
            text-align: center;
            border-radius: 999px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.03);
            font-size: 0.86rem;
        }
        .flow-step.active {
            border-color: #fbbc04;
            background: rgba(251, 188, 4, 0.18);
            color: #fff7d6;
            font-weight: 700;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.84rem;
        }
        th, td {
            padding: 8px 6px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        th {
            color: #9ec7ff;
            text-align: center;
            font-weight: 600;
        }
        .name-cell { font-weight: 600; white-space: nowrap; }
        .center { text-align: center; }
        .step-cell {
            text-align: center;
            color: #111827;
            font-size: 1rem;
            border-radius: 6px;
            min-width: 30px;
        }
        .highlighted-step { outline: 2px solid rgba(255, 255, 255, 0.9); }
        .active-row td { background-color: rgba(255, 255, 255, 0.035); }
        .progress-bar {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 999px;
            height: 18px;
            overflow: hidden;
            position: relative;
        }
        .progress-fill { height: 100%; }
        .progress-text {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .criteria-grid {
            display: grid;
            gap: 10px;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        }
        .criterion {
            padding: 12px;
            border: 1px solid;
            border-radius: 12px;
            color: #111827;
            font-weight: 600;
        }
        .status-line { font-weight: 700; margin-bottom: 8px; }
        .history-table { width: 100%; }
        .history-table td, .history-table th { text-align: left; }
        .mono { font-family: Consolas, monospace; color: #9ca3af; white-space: nowrap; }
        @media (max-width: 900px) {
            body { padding: 14px; }
            section { padding: 14px; }
            .hero-title { font-size: 1.2rem; }
            table { display: block; overflow-x: auto; white-space: nowrap; }
        }
        """
