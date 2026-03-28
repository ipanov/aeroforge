"""PreToolUse hook for mcp__freecad__execute_code.

Runs before every FreeCAD MCP execute_code call. Checks the code for
known anti-patterns and blocks (exit 2) if any are found.

Rules:
    1. BLOCK if code contains .scale( or .Scale = — scaling destroys dimensions.
    2. BLOCK if code is longer than 500 lines — forces incremental building.
    3. WARN if code > 5 lines and doesn't contain "recompute" — geometry may not update.

Manual test commands:
    # ALLOW (exit 0):
    echo '{"tool_input":{"code":"Part.makeBox(10,20,30)\\ndoc.recompute()"}}' | python hooks/cad_pre_execute.py

    # BLOCK (scaling):
    echo '{"tool_input":{"code":"obj.Shape = obj.Shape.scale(2.0)"}}' | python hooks/cad_pre_execute.py

    # BLOCK (too long):
    python -c "import json; print(json.dumps({'tool_input':{'code': 'x\\n'*501}}))" | python hooks/cad_pre_execute.py
"""

import json
import re
import sys

# Anti-pattern: scaling operations that destroy absolute dimensions
_SCALE_RE = re.compile(r"\.scale\s*\(|\.Scale\s*=", re.IGNORECASE)

MAX_LINES = 500
RECOMPUTE_WARN_THRESHOLD = 5


def main() -> int:
    """Main entry point. Returns exit code: 0=ALLOW, 2=BLOCK."""
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"[pre-hook] Failed to parse stdin JSON: {exc}", file=sys.stderr)
        return 0  # Don't block on malformed input

    code = data.get("tool_input", {}).get("code", "")

    # Rule 1: Block scaling operations
    match = _SCALE_RE.search(code)
    if match:
        print(
            f"[pre-hook] BLOCKED: Scaling operation detected: '{match.group()}'",
            file=sys.stderr,
        )
        print(
            "[pre-hook] Scaling destroys absolute dimensions. "
            "Use explicit dimensions instead.",
            file=sys.stderr,
        )
        return 2

    # Rule 2: Block overly long code
    lines = code.split("\n")
    line_count = len(lines)
    if line_count > MAX_LINES:
        print(
            f"[pre-hook] BLOCKED: Code is {line_count} lines (limit: {MAX_LINES})",
            file=sys.stderr,
        )
        print(
            "[pre-hook] Break the code into smaller incremental steps.",
            file=sys.stderr,
        )
        return 2

    # Rule 3: Warn if no recompute in non-trivial code
    if line_count > RECOMPUTE_WARN_THRESHOLD and "recompute" not in code.lower():
        print(
            f"[pre-hook] WARNING: Code is {line_count} lines but has no recompute() call.",
            file=sys.stderr,
        )
        print(
            "[pre-hook] Geometry may not update. Consider adding doc.recompute().",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
