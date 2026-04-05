"""Dynamic n8n workflow builder for AeroForge visual status.

Generates an n8n workflow JSON that visually represents the current
state of the AeroForge design process using sticky notes arranged
as a dashboard in the n8n editor canvas.

Two modes:
1. Skeleton: Created by /aeroforge-init — project phases with placeholder
2. Full: Created/updated by /aeroforge — complete component hierarchy

The visual workflow is SEPARATE from the event webhook workflow.
Events use REST webhooks; the visual is rebuilt on every state change.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Layout constants (n8n canvas coordinates)
# ---------------------------------------------------------------------------

X_START = 100
Y_PHASES = 100
COL_SPACING = 240
ROW_SPACING = 90
CELL_W = 210
CELL_H = 65
LABEL_W = 200
PHASE_W = 210
PHASE_H = 75
BANNER_H = 100
HEADER_H = 50

# n8n sticky note color indices
_CLR_GRAY = 1
_CLR_BLUE = 2
_CLR_GREEN = 3
_CLR_YELLOW = 4
_CLR_ORANGE = 5
_CLR_RED = 6
_CLR_PINK = 7

_STATUS_COLOR = {
    "done": _CLR_GREEN,
    "running": _CLR_YELLOW,
    "pending": _CLR_GRAY,
    "failed": _CLR_RED,
    "skipped": _CLR_GRAY,
    "rejected": _CLR_ORANGE,
}

_STATUS_ICON = {
    "done": "\u2713",       # ✓
    "running": "\u25b6",    # ▶
    "pending": "\u25cb",    # ○
    "failed": "\u2717",     # ✗
    "skipped": "\u2014",    # —
    "rejected": "\u21ba",   # ↺
}

PHASE_LIST = [
    "REQUIREMENTS", "RESEARCH", "DESIGN",
    "IMPLEMENTATION", "VALIDATION", "RELEASE",
]

DESIGN_STEPS = [
    "AERO_PROPOSAL", "STRUCTURAL_REVIEW", "AERO_RESPONSE",
    "CONSENSUS", "DRAWING_2D", "MODEL_3D", "OUTPUT",
]

_TYPE_ICON = {
    "component": "\u2b21",   # ⬡
    "assembly": "\u2b22",    # ⬢
    "off_shelf": "\u25c7",   # ◇
}


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class N8nWorkflowBuilder:
    """Builds n8n workflow JSON from AeroForge workflow state."""

    def __init__(self, project_name: str) -> None:
        self._project_name = project_name
        self._nodes: list[dict[str, Any]] = []
        self._connections: dict[str, Any] = {}
        self._counter = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_skeleton(self, current_phase: str = "REQUIREMENTS") -> dict[str, Any]:
        """Build skeleton workflow for /aeroforge-init.

        Shows project phases with a placeholder for the component hierarchy.
        Used before RESEARCH is complete and the component tree is known.
        """
        self._reset()
        y = Y_PHASES

        # Phase row
        self._render_phase_row(y, current_phase)

        # Active banner
        y += PHASE_H + 30
        self._sticky(
            "\u25b6 **ACTIVE PHASE: " + current_phase + "**",
            X_START, y, width=len(PHASE_LIST) * COL_SPACING, height=50,
            color=_CLR_YELLOW,
        )

        # Placeholder for hierarchy
        y += 80
        self._sticky(
            "## Component Hierarchy\n\n"
            "Will be populated after **RESEARCH** phase completes.\n\n"
            "Run `/aeroforge` to continue the workflow.",
            X_START, y, width=700, height=130, color=_CLR_BLUE,
        )

        # Validation placeholder
        y += 170
        self._render_validation_section(y, {}, {})

        return self._assemble()

    def build_full(self, state: dict[str, Any]) -> dict[str, Any]:
        """Build full visual workflow from current state.

        Shows project phases, component hierarchy with per-step status,
        active work banner, and validation section.
        """
        self._reset()

        current_phase = state.get("project_phase", "DESIGN")
        nodes = state.get("nodes", state.get("sub_assemblies", {}))
        active_runs = state.get("active_runs", [])
        active_node = None
        active_step = None
        if active_runs:
            ar0 = active_runs[0]
            active_node = ar0.get("node", ar0.get("sub_assembly"))
            active_step = ar0.get("step")
        validation = state.get("validation", {})

        y = Y_PHASES

        # ── Phase row ─────────────────────────────────────────────
        self._render_phase_row(y, current_phase)
        y += PHASE_H + 20

        # ── Active-work banner ────────────────────────────────────
        if active_runs:
            ar = active_runs[0]
            node_name = ar.get("node", ar.get("sub_assembly", "?"))
            step_name = ar.get("step", "?")
            agent = ar.get("agent", "system")
            started = ar.get("started_at", "?")
            banner = (
                f"## \u25b6 ACTIVE NOW\n\n"
                f"**{node_name}** \u2192 **{step_name}**\n\n"
                f"Agent: `{agent}` | Started: `{started}`"
            )
            banner_w = max(len(DESIGN_STEPS) * (CELL_W + 10) + LABEL_W, 700)
            self._sticky(banner, X_START, y, width=banner_w, height=BANNER_H, color=_CLR_YELLOW)
            y += BANNER_H + 20
        else:
            self._sticky(
                "**No step running.** Waiting for `/aeroforge` to drive next action.",
                X_START, y, width=600, height=50, color=_CLR_GRAY,
            )
            y += 70

        # ── Column headers ────────────────────────────────────────
        self._sticky("**Component**", X_START, y, width=LABEL_W, height=HEADER_H, color=_CLR_BLUE)
        for col, step_name in enumerate(DESIGN_STEPS):
            x = X_START + LABEL_W + 10 + col * (CELL_W + 10)
            short = step_name.replace("_", " ")
            self._sticky(f"**{short}**", x, y, width=CELL_W, height=HEADER_H, color=_CLR_BLUE)
        y += HEADER_H + 10

        # ── Component rows ────────────────────────────────────────
        sorted_names = self._sort_by_hierarchy(nodes)
        for node_name in sorted_names:
            node_data = nodes.get(node_name, {})
            y = self._render_node_row(
                y, node_name, node_data,
                active_node=active_node, active_step=active_step,
            )

        # ── Validation section ────────────────────────────────────
        y += 30
        cfd = validation.get("cfd", {})
        fea = validation.get("fea", {})
        self._render_validation_section(y, cfd, fea)
        y += 120

        # ── Convergence criteria ──────────────────────────────────
        convergence = validation.get("convergence", {})
        if convergence:
            self._render_convergence(y, convergence)

        return self._assemble()

    # ------------------------------------------------------------------
    # Section renderers
    # ------------------------------------------------------------------

    def _render_phase_row(self, y: int, current_phase: str) -> None:
        """Render the top-level project phase sticky notes."""
        current_idx = PHASE_LIST.index(current_phase) if current_phase in PHASE_LIST else 0
        for i, phase in enumerate(PHASE_LIST):
            x = X_START + i * COL_SPACING
            if i < current_idx:
                color, icon = _CLR_GREEN, "\u2713"
                label = "Done"
            elif i == current_idx:
                color, icon = _CLR_YELLOW, "\u25b6"
                label = "ACTIVE"
            else:
                color, icon = _CLR_GRAY, "\u25cb"
                label = "Pending"
            self._sticky(
                f"**{phase}**\n{icon} {label}",
                x, y, width=PHASE_W, height=PHASE_H, color=color,
            )

    def _render_node_row(
        self,
        y: int,
        node_name: str,
        node_data: dict[str, Any],
        active_node: Optional[str] = None,
        active_step: Optional[str] = None,
    ) -> int:
        """Render one component/assembly row. Returns next y position."""
        node_type = node_data.get("type", "component")
        level = node_data.get("level", 1)
        iteration = node_data.get("iteration", node_data.get("current_iteration", 1))
        round_label = node_data.get("round_label", node_data.get("current_round_label", f"R{iteration}"))
        agent_round = node_data.get("agent_round", 0)
        is_active_node = (node_name == active_node)

        # Design cycle data (handle both formats)
        dc = node_data.get("design_cycle", node_data.get("steps", {}))

        # Node label
        indent = "\u00a0\u00a0" * max(0, level - 1)
        icon = _TYPE_ICON.get(node_type, "?")
        label_color = _CLR_YELLOW if is_active_node else _CLR_BLUE
        self._sticky(
            f"{indent}{icon} **{node_name}**\n{round_label} / I{iteration} / Rd{agent_round}",
            X_START, y, width=LABEL_W, height=CELL_H, color=label_color,
        )

        # Design cycle cells
        if dc is None:
            # Off-shelf node — single gray cell spanning all columns
            x = X_START + LABEL_W + 10
            total_w = len(DESIGN_STEPS) * (CELL_W + 10) - 10
            self._sticky("_off-shelf — no design cycle_", x, y, width=total_w, height=CELL_H, color=_CLR_GRAY)
        else:
            for col, step_name in enumerate(DESIGN_STEPS):
                x = X_START + LABEL_W + 10 + col * (CELL_W + 10)
                step_data = dc.get(step_name, {})

                if isinstance(step_data, dict):
                    status = step_data.get("status", "pending")
                    agent = step_data.get("agent")
                    history = step_data.get("history", [])
                else:
                    status = "pending"
                    agent = None
                    history = []

                # Active step override
                is_active_step = is_active_node and step_name == active_step
                if is_active_step:
                    color = _CLR_YELLOW
                    status_icon = "\u25b6\u25b6"  # ▶▶
                else:
                    color = _STATUS_COLOR.get(status, _CLR_GRAY)
                    status_icon = _STATUS_ICON.get(status, "?")

                # Build cell content
                parts = [status_icon]
                if agent and status == "running":
                    parts.append(f"`{agent}`")

                # Rejection count
                rejections = [h for h in history if isinstance(h, dict) and h.get("action") == "rejected"]
                if rejections:
                    parts.append(f"\u26a0 {len(rejections)}R")

                content = " ".join(parts)
                self._sticky(content, x, y, width=CELL_W, height=CELL_H, color=color)

        return y + CELL_H + 10

    def _render_validation_section(
        self,
        y: int,
        cfd: dict[str, Any],
        fea: dict[str, Any],
    ) -> None:
        """Render the final validation (CFD + FEA) section."""
        self._sticky(
            "## Final Validation",
            X_START, y, width=300, height=HEADER_H, color=_CLR_BLUE,
        )
        y += HEADER_H + 10

        # CFD card
        cfd_status = cfd.get("status", "pending")
        cfd_icon = _STATUS_ICON.get(cfd_status, "\u25cb")
        cfd_color = _STATUS_COLOR.get(cfd_status, _CLR_GRAY)
        cfd_extra = ""
        if cfd.get("passed") is True:
            cfd_extra = " **PASSED**"
        elif cfd.get("passed") is False:
            cfd_extra = " **FAILED**"
        cfd_notes = cfd.get("notes", "")
        self._sticky(
            f"**CFD \u2014 Synthetic Wind Tunnel**\n{cfd_icon} {cfd_status.upper()}{cfd_extra}\n{cfd_notes}",
            X_START, y, width=350, height=90, color=cfd_color,
        )

        # FEA card
        fea_status = fea.get("status", "pending")
        fea_icon = _STATUS_ICON.get(fea_status, "\u25cb")
        fea_color = _STATUS_COLOR.get(fea_status, _CLR_GRAY)
        fea_extra = ""
        if fea.get("passed") is True:
            fea_extra = " **PASSED**"
        elif fea.get("passed") is False:
            fea_extra = " **FAILED**"
        fea_notes = fea.get("notes", "")
        self._sticky(
            f"**FEA \u2014 Structural Analysis**\n{fea_icon} {fea_status.upper()}{fea_extra}\n{fea_notes}",
            X_START + 370, y, width=350, height=90, color=fea_color,
        )

    def _render_convergence(self, y: int, convergence: dict[str, bool]) -> None:
        """Render convergence criteria summary."""
        all_met = all(convergence.values()) if convergence else False
        lines = ["## Convergence Criteria\n"]
        for key, met in convergence.items():
            icon = "\u2713" if met else "\u2717"
            label = key.replace("_met", "").replace("_", " ").title()
            lines.append(f"{icon} {label}")

        color = _CLR_GREEN if all_met else _CLR_GRAY
        self._sticky(
            "\n".join(lines),
            X_START, y, width=400, height=50 + len(convergence) * 24, color=color,
        )

    # ------------------------------------------------------------------
    # Node helpers
    # ------------------------------------------------------------------

    def _sticky(
        self,
        content: str,
        x: int,
        y: int,
        width: int = 200,
        height: int = 80,
        color: int = _CLR_GRAY,
    ) -> str:
        """Add a sticky note to the workflow."""
        nid = f"sticky-{self._counter}"
        self._counter += 1
        self._nodes.append({
            "id": nid,
            "name": f"Note {self._counter}",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [x, y],
            "parameters": {
                "content": content,
                "color": color,
                "width": width,
                "height": height,
            },
        })
        return nid

    def _sort_by_hierarchy(self, nodes: dict[str, Any]) -> list[str]:
        """Sort nodes: roots first, then children nested under parents."""
        result: list[str] = []
        roots = [n for n, d in nodes.items() if d.get("parent") is None]

        def _walk(name: str) -> None:
            if name in result:
                return
            result.append(name)
            children = nodes.get(name, {}).get("children", [])
            for child in children:
                if child in nodes:
                    _walk(child)

        for root in sorted(roots):
            _walk(root)
        # Orphans
        for name in nodes:
            if name not in result:
                result.append(name)
        return result

    def _reset(self) -> None:
        self._nodes = []
        self._connections = {}
        self._counter = 0

    def _assemble(self) -> dict[str, Any]:
        """Assemble the final n8n workflow JSON."""
        # n8n requires at least one trigger node for a valid workflow
        self._nodes.insert(0, {
            "id": "trigger-0",
            "name": "AeroForge Dashboard",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [X_START - 250, Y_PHASES],
            "parameters": {},
        })
        return {
            "name": f"AeroForge Dashboard - {self._project_name}",
            "active": False,
            "nodes": self._nodes,
            "connections": self._connections,
            "settings": {
                "saveManualExecutions": False,
                "callerPolicy": "workflowsFromSameOwner",
            },
            "tags": [
                {"name": "aeroforge"},
                {"name": "dashboard"},
            ],
        }
