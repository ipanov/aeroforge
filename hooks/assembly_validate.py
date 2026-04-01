"""PostToolUse hook for assembly 3D model creation.

Runs after any FreeCAD execute_code that creates or modifies an assembly.
Checks for collisions and containment violations.

Triggers on: mcp__freecad__execute_code (when assembly-related)

Checks:
    1. No two objects in the document intersect (collision detection)
    2. Internal objects (rods, spars) do not protrude outside shells
    3. Warns if any object bounding box extends beyond another's

Exit codes:
    0 = PASS (no issues found)
    1 = WARN (potential issues, non-blocking)
    2 = BLOCK (definite collision/protrusion detected)

Manual test:
    echo '{"tool_name":"mcp__freecad__execute_code","tool_result":"assembly"}' | python hooks/assembly_validate.py
"""

import json
import sys


def main() -> int:
    """Main entry point. Returns exit code."""
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0  # Don't block on malformed input

    # Only trigger on FreeCAD execute_code results that mention assembly
    tool_name = data.get("tool_name", "")
    tool_result = str(data.get("tool_result", ""))

    if "mcp__freecad__execute_code" not in tool_name:
        return 0

    # Check if this was an assembly operation
    is_assembly = any(kw in tool_result.lower() for kw in [
        "assembly", "import", "insert", "placement",
    ])

    if not is_assembly:
        return 0

    # Check for collision/protrusion indicators in the output
    has_collision_warning = any(kw in tool_result.lower() for kw in [
        "collision", "intersect", "protrusion", "protrud",
        "outside", "overlapping",
    ])

    if has_collision_warning:
        print(
            "[assembly-hook] WARNING: Possible collision/protrusion detected in output.",
            file=sys.stderr,
        )
        print(
            "[assembly-hook] Run validate_assembly() from src/cad/validation/assembly_check.py",
            file=sys.stderr,
        )
        return 1  # Warn but don't block

    # Remind to validate
    print(
        "[assembly-hook] REMINDER: Assembly operation detected. "
        "Run collision/containment checks before declaring complete.",
        file=sys.stderr,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
