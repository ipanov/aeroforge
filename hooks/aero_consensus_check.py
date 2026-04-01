"""
PreToolUse hook: checks that DESIGN_CONSENSUS.md exists before
creating drawing files for aerodynamic components.

Runs before Write when the target path contains a drawing
file in an aerodynamic component/assembly folder.
"""
import sys
import os
import json

AERO_CATEGORIES = ["empennage", "wing", "fuselage"]


def main():
    input_data = json.loads(sys.stdin.read())
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    target = ""
    if tool_name == "Write":
        target = tool_input.get("file_path", "")
    elif tool_name == "Bash":
        target = tool_input.get("command", "")

    is_drawing = "_drawing.dxf" in target or "_drawing.py" in target
    is_aero = any(
        f"/{cat}/" in target.replace("\\", "/") or f"\\{cat}\\" in target
        for cat in AERO_CATEGORIES
    )

    if not (is_drawing and is_aero):
        print(json.dumps({"decision": "approve"}))
        return

    if tool_name == "Write":
        folder = os.path.dirname(target)
    else:
        print(json.dumps({
            "decision": "approve",
            "message": "WARNING: Creating aerodynamic drawing via Bash. "
                       "Ensure DESIGN_CONSENSUS.md exists in the target folder."
        }))
        return

    consensus_path = os.path.join(folder, "DESIGN_CONSENSUS.md")
    if os.path.exists(consensus_path):
        print(json.dumps({
            "decision": "approve",
            "message": f"DESIGN_CONSENSUS.md found in {folder}. Proceeding."
        }))
    else:
        print(json.dumps({
            "decision": "block",
            "reason": f"DESIGN_CONSENSUS.md not found in {folder}. "
                      "The aero-structural agent team must review this component "
                      "before any drawing is created. Run the aerodynamicist + "
                      "structural engineer feedback loop first."
        }))


if __name__ == "__main__":
    main()
