"""PreToolUse hook that enforces workflow-step-to-artifact alignment.

The deterministic system does not decide the aircraft type or tooling, but it
does enforce that artifact creation follows the currently active workflow step.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / ".claude" / "workflow_state.json"


def infer_required_step(file_path: str) -> Optional[str]:
    """Map artifact targets to the workflow step that must be active."""

    normalized = file_path.replace("\\", "/").lower()
    basename = os.path.basename(normalized)

    if normalized.endswith(".dxf") or basename.endswith("_drawing.png") or basename.startswith("draw_"):
        return "DRAWING_2D"
    if normalized.endswith(".step") or basename == "model.py" or basename.startswith("build_"):
        return "MODEL_3D"
    if normalized.endswith(".stl") or normalized.endswith(".3mf") or basename.startswith("render_"):
        return "MESH"
    if "analysis" in normalized and normalized.endswith(".md"):
        return "VALIDATION"
    return None


def infer_subassembly(file_path: str, state: dict) -> Optional[str]:
    """Infer the sub-assembly name from the target path."""

    normalized = file_path.replace("\\", "/").lower()
    for name in state.get("sub_assemblies", {}).keys():
        token = f"/{name.lower()}/"
        if token in normalized:
            return name
    return None


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "approve"}))
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name not in {"Write", "Edit"}:
        print(json.dumps({"decision": "approve"}))
        return 0

    file_path = data.get("tool_input", {}).get("file_path", "")
    required_step = infer_required_step(file_path)
    if required_step is None:
        print(json.dumps({"decision": "approve"}))
        return 0

    if not STATE_FILE.exists():
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        "workflow_state.json is missing. Start the workflow and activate "
                        f"{required_step} before editing {file_path}."
                    ),
                }
            )
        )
        return 0

    with open(STATE_FILE, "r", encoding="utf-8") as handle:
        state = json.load(handle)

    active = state.get("active_run")
    if not active:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        f"{file_path} belongs to {required_step}, but no workflow step is "
                        "currently active. Start the matching step first."
                    ),
                }
            )
        )
        return 0

    if active.get("step") != required_step:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        f"{file_path} belongs to {required_step}, but the active step is "
                        f"{active.get('sub_assembly')}:{active.get('step')}."
                    ),
                }
            )
        )
        return 0

    target_subassembly = infer_subassembly(file_path, state)
    if target_subassembly and active.get("sub_assembly") != target_subassembly:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        f"{file_path} appears to belong to {target_subassembly}, but the "
                        f"active sub-assembly is {active.get('sub_assembly')}."
                    ),
                }
            )
        )
        return 0

    print(
        json.dumps(
            {
                "decision": "approve",
                "message": (
                    f"Workflow guard approved {file_path} under "
                    f"{active.get('sub_assembly')}:{active.get('step')}."
                ),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
