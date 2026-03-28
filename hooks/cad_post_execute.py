"""PostToolUse hook for mcp__freecad__execute_code.

Runs after every FreeCAD MCP execute_code call. Checks the response for
error patterns and blocks (exit 2) if any are found. On success, attempts
to take an auto-screenshot and print object dimensions (failures are
non-blocking warnings).

Manual test commands:
    # Should ALLOW (exit 0):
    echo '{"tool_input":{"code":"print(1)"},"tool_response":{"success":true,"message":"Output: 1\\n"}}' | python hooks/cad_post_execute.py

    # Should BLOCK (exit 2):
    echo '{"tool_input":{"code":"x"},"tool_response":{"success":true,"message":"Output: Failed to create object\\n"}}' | python hooks/cad_post_execute.py
"""

import json
import re
import sys
import os

# Ensure project root is on sys.path so we can import from hooks/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

ERROR_PATTERNS = [
    r"Failed to",
    r"Invalid",
    r"Error:",
    r"Traceback",
    r"Exception",
    r"Volume:\s*-",
    r"Volume:\s*0\.0",
    r"nan",
    r"BoundBox.*inf",
]

# Compile into a single case-insensitive regex for efficiency
_ERROR_RE = re.compile("|".join(f"(?:{p})" for p in ERROR_PATTERNS), re.IGNORECASE)


def check_errors(message: str) -> list[str]:
    """Return list of matched error patterns found in the message."""
    return [m.group() for m in _ERROR_RE.finditer(message)]


def auto_screenshot_and_dims() -> None:
    """Try to take a screenshot and print object dimensions. Non-blocking."""
    try:
        from hooks.freecad_rpc_helper import FreecadRPC

        rpc = FreecadRPC()
        if not rpc.ping():
            print("[hook] FreeCAD RPC not available, skipping screenshot", file=sys.stderr)
            return

        # Screenshot
        screenshot_dir = os.path.join(PROJECT_ROOT, "exports", "validation")
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, "post_execute_auto.png").replace("\\", "/")
        try:
            rpc.take_screenshot(screenshot_path, view="isometric", width=1280, height=720)
            print(f"[hook] Screenshot saved: {screenshot_path}", file=sys.stderr)
        except Exception as exc:
            print(f"[hook] Screenshot failed (non-blocking): {exc}", file=sys.stderr)

        # Dimensions
        try:
            objects_info = rpc.get_all_objects()
            if objects_info and "NO_ACTIVE_DOCUMENT" not in objects_info:
                print(f"[hook] Objects:\n{objects_info}", file=sys.stderr)
        except Exception as exc:
            print(f"[hook] Dimension query failed (non-blocking): {exc}", file=sys.stderr)

    except ImportError as exc:
        print(f"[hook] Cannot import FreecadRPC (non-blocking): {exc}", file=sys.stderr)
    except Exception as exc:
        print(f"[hook] Unexpected error in auto-screenshot (non-blocking): {exc}", file=sys.stderr)


def main() -> int:
    """Main entry point. Returns exit code: 0=ALLOW, 2=BLOCK."""
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"[hook] Failed to parse stdin JSON: {exc}", file=sys.stderr)
        return 0  # Don't block on malformed input

    tool_response = data.get("tool_response", {})
    message = tool_response.get("message", "")
    success = tool_response.get("success", True)

    # Check for explicit failure
    if not success:
        print(f"[hook] BLOCKED: FreeCAD reported failure", file=sys.stderr)
        print(f"[hook] Message: {message}", file=sys.stderr)
        return 2

    # Check for error patterns in message
    errors = check_errors(message)
    if errors:
        print(f"[hook] BLOCKED: Error patterns detected in output", file=sys.stderr)
        print(f"[hook] Matched: {errors}", file=sys.stderr)
        print(f"[hook] Full message: {message}", file=sys.stderr)
        return 2

    # No errors - try auto-screenshot (non-blocking)
    auto_screenshot_and_dims()
    return 0


if __name__ == "__main__":
    sys.exit(main())
