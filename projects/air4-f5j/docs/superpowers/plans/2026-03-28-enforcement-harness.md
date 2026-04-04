# Enforcement Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a three-layer hook system that BLOCKS bad CAD output, enforces visual validation, and runs dimensional assertion tests — validated end-to-end with a carbon spar tube test case.

**Architecture:** Claude Code hooks (PreToolUse, PostToolUse, PreCommit) read JSON from stdin, inspect tool input/output, and exit with code 2 to block or 0 to allow. A FreeCAD RPC helper module provides screenshot and dimension query functions. Pytest tests assert geometry dimensions against specs.py.

**Tech Stack:** Python 3.10, Claude Code hooks (JSON stdin), xmlrpc.client (FreeCAD RPC on port 9875), pytest, FreeCAD 1.0 GUI

---

## File Structure

| File | Responsibility |
|------|---------------|
| `hooks/cad_post_execute.py` | PostToolUse: error detection + auto-screenshot + dimension print |
| `hooks/cad_pre_execute.py` | PreToolUse: block scaling, oversized code, missing recompute |
| `hooks/cad_pre_commit.py` | PreCommit: require validation screenshots before commit |
| `hooks/freecad_rpc_helper.py` | Shared: FreeCAD RPC connection, screenshot, bounding box queries |
| `.claude/settings.json` | Hook wiring configuration |
| `tests/test_spar_geometry.py` | Dimensional assertions for carbon spar tube |
| `tests/conftest.py` | Pytest fixture for FreeCAD RPC connection |
| `cad-progress.md` | Session state tracking (which components validated) |

---

### Task 1: FreeCAD RPC Helper Module

**Files:**
- Create: `hooks/freecad_rpc_helper.py`
- Create: `hooks/__init__.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_rpc_helper.py
import pytest
from hooks.freecad_rpc_helper import FreecadRPC

def test_rpc_connection():
    """RPC helper connects to FreeCAD on port 9875."""
    rpc = FreecadRPC(port=9875)
    assert rpc.ping() == True

def test_rpc_screenshot(tmp_path):
    """RPC helper takes a screenshot and saves to disk."""
    rpc = FreecadRPC(port=9875)
    path = str(tmp_path / "test_screenshot.png")
    result = rpc.take_screenshot(path, view="isometric")
    assert result == True
    assert (tmp_path / "test_screenshot.png").exists()

def test_rpc_bounding_box():
    """RPC helper queries bounding box of an object."""
    rpc = FreecadRPC(port=9875)
    # Create a test box first
    rpc.execute("import FreeCAD, Part; doc = FreeCAD.newDocument('Test'); b = Part.makeBox(10,20,30); doc.addObject('Part::Feature','TestBox').Shape = b; doc.recompute()")
    bb = rpc.get_bounding_box("TestBox")
    assert abs(bb["X"] - 10.0) < 0.01
    assert abs(bb["Y"] - 20.0) < 0.01
    assert abs(bb["Z"] - 30.0) < 0.01
    # Cleanup
    rpc.execute("FreeCAD.closeDocument('Test')")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python -m pytest tests/test_rpc_helper.py -v`
Expected: FAIL with "No module named 'hooks.freecad_rpc_helper'"

- [ ] **Step 3: Write the implementation**

```python
# hooks/__init__.py
# (empty - makes hooks a package)

# hooks/freecad_rpc_helper.py
"""FreeCAD RPC helper for hooks and tests.

Connects to FreeCAD GUI via XML-RPC on port 9875.
Provides: ping, execute, screenshot, bounding box queries.
"""

import xmlrpc.client
import os
import re
import time


class FreecadRPC:
    """Helper for communicating with FreeCAD via XML-RPC."""

    def __init__(self, host: str = "localhost", port: int = 9875):
        self.url = f"http://{host}:{port}"
        self.server = xmlrpc.client.ServerProxy(self.url, allow_none=True)

    def ping(self) -> bool:
        """Check if FreeCAD is responding."""
        try:
            result = self.server.ping()
            return result in (True, "pong")
        except Exception:
            return False

    def execute(self, code: str) -> str:
        """Execute Python code in FreeCAD. Returns output string."""
        result = self.server.execute_code(code)
        if isinstance(result, dict):
            return result.get("message", str(result))
        return str(result)

    def take_screenshot(
        self, filepath: str, view: str = "isometric", width: int = 1920, height: int = 1080
    ) -> bool:
        """Take a screenshot from FreeCAD and save to filepath."""
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

        view_commands = {
            "isometric": "v.viewIsometric()",
            "front": "v.viewFront()",
            "top": "v.viewTop()",
            "right": "v.viewRight()",
            "left": "v.viewLeft()",
        }
        view_cmd = view_commands.get(view, "v.viewIsometric()")
        filepath_escaped = filepath.replace("\\", "/")

        code = f"""
import FreeCADGui, time, os
os.makedirs(os.path.dirname("{filepath_escaped}") or ".", exist_ok=True)
gd = FreeCADGui.ActiveDocument
if gd:
    v = gd.ActiveView
    {view_cmd}
    v.fitAll()
    time.sleep(0.3)
    v.saveImage("{filepath_escaped}", {width}, {height}, "Current")
    print("SCREENSHOT_OK")
else:
    print("SCREENSHOT_FAIL: No active document")
"""
        output = self.execute(code)
        return "SCREENSHOT_OK" in output

    def get_bounding_box(self, object_name: str) -> dict:
        """Get bounding box of a FreeCAD object. Returns dict with X, Y, Z lengths."""
        code = f"""
import FreeCAD
doc = FreeCAD.ActiveDocument
obj = doc.getObject("{object_name}")
if obj and hasattr(obj, "Shape"):
    bb = obj.Shape.BoundBox
    print(f"BB_X:{{bb.XLength:.6f}}")
    print(f"BB_Y:{{bb.YLength:.6f}}")
    print(f"BB_Z:{{bb.ZLength:.6f}}")
    print(f"BB_VOL:{{obj.Shape.Volume:.6f}}")
else:
    print("BB_ERROR: Object not found or has no Shape")
"""
        output = self.execute(code)
        result = {}
        for line in output.split("\n"):
            if line.startswith("BB_X:"):
                result["X"] = float(line.split(":")[1])
            elif line.startswith("BB_Y:"):
                result["Y"] = float(line.split(":")[1])
            elif line.startswith("BB_Z:"):
                result["Z"] = float(line.split(":")[1])
            elif line.startswith("BB_VOL:"):
                result["VOL"] = float(line.split(":")[1])
        return result

    def get_all_objects(self) -> str:
        """List all objects in active document with bounding boxes."""
        code = """
import FreeCAD
doc = FreeCAD.ActiveDocument
if doc:
    for obj in doc.Objects:
        if hasattr(obj, "Shape") and obj.Shape.Volume > 0:
            bb = obj.Shape.BoundBox
            print(f"OBJ:{obj.Label}|X:{bb.XLength:.2f}|Y:{bb.YLength:.2f}|Z:{bb.ZLength:.2f}|VOL:{obj.Shape.Volume:.1f}")
else:
    print("OBJ_ERROR: No active document")
"""
        return self.execute(code)

    def take_validation_screenshots(self, component_name: str, output_dir: str = "exports/validation") -> list:
        """Take 4 validation screenshots (isometric, front, top, right)."""
        os.makedirs(output_dir, exist_ok=True)
        paths = []
        for view in ["isometric", "front", "top", "right"]:
            path = os.path.join(output_dir, f"{component_name}_{view}.png")
            if self.take_screenshot(path, view=view):
                paths.append(path)
        return paths
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python -m pytest tests/test_rpc_helper.py -v`
Expected: PASS (requires FreeCAD running with RPC on port 9875)

- [ ] **Step 5: Commit**

```bash
git add hooks/__init__.py hooks/freecad_rpc_helper.py tests/test_rpc_helper.py
git commit -m "feat: add FreeCAD RPC helper module with screenshot and bounding box queries"
```

---

### Task 2: PostToolUse Hook (auto-screenshot + error detection)

**Files:**
- Create: `hooks/cad_post_execute.py`

- [ ] **Step 1: Write the hook script**

```python
#!/usr/bin/env python3
"""PostToolUse hook: runs after every mcp__freecad__execute_code call.

Reads JSON from stdin with tool_input and tool_response.
1. Checks output for FreeCAD errors → exit 2 (BLOCK) if found
2. Takes auto-screenshot → saves to exports/validation/
3. Prints all object dimensions to stdout

Exit codes:
  0 = allow (no errors)
  2 = deny (errors detected)
"""

import json
import sys
import os
import re
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ERROR_PATTERNS = [
    r"Failed to",
    r"Invalid",
    r"Error:",
    r"Traceback",
    r"Exception",
    r"Volume:\s*-",        # Negative volume
    r"Volume:\s*0\.0",     # Zero volume
    r"nan",
    r"BoundBox.*inf",
]


def main():
    data = json.load(sys.stdin)

    tool_response = data.get("tool_response", {})
    if isinstance(tool_response, dict):
        output = tool_response.get("message", "") or tool_response.get("content", "")
    else:
        output = str(tool_response)

    # ── 1. Error detection ──
    errors = []
    for pattern in ERROR_PATTERNS:
        matches = re.findall(pattern, output, re.IGNORECASE)
        if matches:
            errors.append(f"Pattern '{pattern}' matched: {matches[:3]}")

    if errors:
        print(f"[CAD HOOK] BLOCKING — FreeCAD errors detected:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        print(f"\nFreeCAD output was:\n{output[:500]}", file=sys.stderr)
        sys.exit(2)  # BLOCK

    # ── 2. Auto-screenshot ──
    try:
        from hooks.freecad_rpc_helper import FreecadRPC
        rpc = FreecadRPC()
        if rpc.ping():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports", "validation")
            screenshot_path = os.path.join(screenshot_dir, f"auto_{timestamp}.png")
            rpc.take_screenshot(screenshot_path)
            print(f"[CAD HOOK] Screenshot: {screenshot_path}", file=sys.stderr)

            # ── 3. Dimension extraction ──
            obj_info = rpc.get_all_objects()
            if obj_info and "OBJ:" in obj_info:
                print(f"[CAD HOOK] Objects in document:", file=sys.stderr)
                for line in obj_info.split("\n"):
                    if line.startswith("OBJ:"):
                        print(f"  {line}", file=sys.stderr)
    except Exception as e:
        # Screenshot failure should NOT block the operation
        print(f"[CAD HOOK] Screenshot/dimension query failed: {e}", file=sys.stderr)

    sys.exit(0)  # ALLOW


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test the hook manually**

```bash
echo '{"tool_input":{"code":"print(1)"},"tool_response":{"message":"Output: 1\n"}}' | python hooks/cad_post_execute.py
echo "Exit code: $?"
# Expected: exit 0 (allow), screenshot taken

echo '{"tool_input":{"code":"x"},"tool_response":{"message":"Failed to create object\n"}}' | python hooks/cad_post_execute.py
echo "Exit code: $?"
# Expected: exit 2 (block), error message on stderr
```

- [ ] **Step 3: Commit**

```bash
git add hooks/cad_post_execute.py
git commit -m "feat: add PostToolUse hook for auto-screenshot and error detection"
```

---

### Task 3: PreToolUse Hook (anti-pattern blocker)

**Files:**
- Create: `hooks/cad_pre_execute.py`

- [ ] **Step 1: Write the hook script**

```python
#!/usr/bin/env python3
"""PreToolUse hook: runs before every mcp__freecad__execute_code call.

Reads JSON from stdin with tool_input.
Blocks known anti-patterns:
1. .scale() operations (destroys dimensions)
2. Code longer than 500 lines (forces incremental building)
3. Code without doc.recompute() (geometry won't update)

Exit codes:
  0 = allow
  2 = deny
"""

import json
import sys
import re


BLOCKED_PATTERNS = [
    (r'\.scale\s*\(', "SCALING IS FORBIDDEN. It destroys dimensions and breaks interoperability. Resize geometry by recreating it with correct parameters."),
    (r'\.Scale\s*=', "SCALING IS FORBIDDEN. Do not set Scale property. Recreate geometry with correct dimensions."),
]


def main():
    data = json.load(sys.stdin)

    tool_input = data.get("tool_input", {})
    code = tool_input.get("code", "")

    # ── 1. Check for blocked patterns ──
    for pattern, message in BLOCKED_PATTERNS:
        if re.search(pattern, code):
            print(f"[CAD HOOK] BLOCKING — {message}", file=sys.stderr)
            sys.exit(2)

    # ── 2. Check code length ──
    line_count = len(code.strip().split("\n"))
    if line_count > 500:
        print(f"[CAD HOOK] BLOCKING — Code is {line_count} lines (max 500).", file=sys.stderr)
        print(f"Break into smaller operations. Build incrementally.", file=sys.stderr)
        sys.exit(2)

    # ── 3. Warn (not block) if no recompute ──
    if "recompute" not in code and line_count > 5:
        print(f"[CAD HOOK] WARNING: No doc.recompute() found. Geometry may not update.", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test the hook manually**

```bash
echo '{"tool_input":{"code":"Part.makeBox(10,20,30)\ndoc.recompute()"}}' | python hooks/cad_pre_execute.py
echo "Exit code: $?"
# Expected: 0 (allow)

echo '{"tool_input":{"code":"obj.Shape = obj.Shape.scale(2.0)"}}' | python hooks/cad_pre_execute.py
echo "Exit code: $?"
# Expected: 2 (block)
```

- [ ] **Step 3: Commit**

```bash
git add hooks/cad_pre_execute.py
git commit -m "feat: add PreToolUse hook blocking scaling and oversized code"
```

---

### Task 4: Wire Hooks into Settings

**Files:**
- Create: `.claude/settings.json`
- Modify: `.claude/settings.local.json`

- [ ] **Step 1: Create project settings.json with hooks**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__freecad__execute_code",
        "hooks": [
          {
            "type": "command",
            "command": "python hooks/cad_post_execute.py"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "mcp__freecad__execute_code",
        "hooks": [
          {
            "type": "command",
            "command": "python hooks/cad_pre_execute.py"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Merge permissions from settings.local.json**

The existing `settings.local.json` has permissions. Keep them there (gitignored). The new `settings.json` has hooks (committed, shared).

- [ ] **Step 3: Commit**

```bash
git add .claude/settings.json
git commit -m "feat: wire PostToolUse and PreToolUse hooks into project settings"
```

---

### Task 5: Spar Tube Test (TDD — RED)

**Files:**
- Create: `tests/conftest.py` (RPC fixture)
- Create: `tests/test_spar_geometry.py`

- [ ] **Step 1: Write the pytest fixture**

```python
# tests/conftest.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def freecad_rpc():
    """Fixture providing FreeCAD RPC connection."""
    from hooks.freecad_rpc_helper import FreecadRPC
    rpc = FreecadRPC(port=9875)
    if not rpc.ping():
        pytest.skip("FreeCAD RPC not available on port 9875")
    return rpc
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_spar_geometry.py
"""Dimensional assertions for the 8mm carbon spar tube.

These tests query FreeCAD via RPC and assert exact dimensions
against specs.py. They MUST be run with FreeCAD GUI active.
"""

from src.core.specs import SAILPLANE


def test_main_spar_exists(freecad_rpc):
    """MainSpar object must exist in FreeCAD document."""
    bb = freecad_rpc.get_bounding_box("MainSpar")
    assert "X" in bb, "MainSpar object not found in FreeCAD document"


def test_main_spar_outer_diameter(freecad_rpc):
    """Main spar OD must be 8.0mm ± 0.01mm."""
    expected_od = SAILPLANE.spar.main_od  # 8.0
    bb = freecad_rpc.get_bounding_box("MainSpar")
    # Cylinder along Y axis: OD = XLength = ZLength
    od = max(bb["X"], bb["Z"])
    assert abs(od - expected_od) < 0.01, f"Spar OD {od:.3f}mm != {expected_od}mm"


def test_main_spar_length(freecad_rpc):
    """Main spar length must be 256mm (one panel span)."""
    expected_length = SAILPLANE.wing.panel_span  # 256.0
    bb = freecad_rpc.get_bounding_box("MainSpar")
    length = bb["Y"]
    assert abs(length - expected_length) < 0.1, f"Spar length {length:.1f}mm != {expected_length}mm"


def test_main_spar_volume_positive(freecad_rpc):
    """Spar volume must be positive (not inverted geometry)."""
    bb = freecad_rpc.get_bounding_box("MainSpar")
    assert bb.get("VOL", 0) > 0, f"Spar volume is {bb.get('VOL', 0)} (must be positive)"


def test_main_spar_is_hollow(freecad_rpc):
    """Spar must be hollow (volume < solid cylinder volume)."""
    import math
    bb = freecad_rpc.get_bounding_box("MainSpar")
    od = max(bb["X"], bb["Z"])
    length = bb["Y"]
    solid_vol = math.pi * (od / 2) ** 2 * length
    actual_vol = bb.get("VOL", 0)
    # Hollow tube volume should be ~44% of solid (1mm wall on 8mm tube)
    assert actual_vol < solid_vol * 0.8, f"Spar appears solid (vol={actual_vol:.0f} vs solid={solid_vol:.0f})"
    assert actual_vol > solid_vol * 0.2, f"Spar volume too small ({actual_vol:.0f}mm³)"
```

- [ ] **Step 3: Run tests — verify RED**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python -m pytest tests/test_spar_geometry.py -v`
Expected: FAIL (MainSpar object doesn't exist — no geometry created yet)

- [ ] **Step 4: Commit the failing tests**

```bash
git add tests/conftest.py tests/test_spar_geometry.py
git commit -m "test: add failing spar geometry tests (TDD RED phase)"
```

---

### Task 6: Build Spar in FreeCAD (TDD — GREEN)

**Files:**
- Create: `src/freecad_scripts/spar.py`

- [ ] **Step 1: Write the spar creation script**

```python
# src/freecad_scripts/spar.py
"""Create the 8mm carbon spar tube in FreeCAD via RPC."""

from src.core.specs import SAILPLANE


def generate_spar_code(length_mm: float = 256.0) -> str:
    """Generate FreeCAD Python code to create the main carbon spar.

    Args:
        length_mm: Spar section length (default: one panel span)
    """
    spar = SAILPLANE.spar
    return f"""
import FreeCAD
import Part
import FreeCADGui

doc = FreeCAD.ActiveDocument
if doc is None:
    doc = FreeCAD.newDocument("AeroForge")

# Main carbon spar tube: {spar.main_od}mm OD, {spar.main_id}mm ID, {length_mm}mm long
outer = Part.makeCylinder({spar.main_od / 2}, {length_mm}, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0))
inner = Part.makeCylinder({spar.main_id / 2}, {length_mm + 2}, FreeCAD.Vector(0, -1, 0), FreeCAD.Vector(0, 1, 0))
spar_shape = outer.cut(inner)

obj = doc.addObject("Part::Feature", "MainSpar")
obj.Shape = spar_shape
obj.Label = "MainSpar (8mm carbon tube)"
obj.ViewObject.ShapeColor = (0.12, 0.12, 0.12)

doc.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()

bb = spar_shape.BoundBox
print(f"MainSpar created: {{bb.XLength:.2f}}x{{bb.YLength:.2f}}x{{bb.ZLength:.2f}}mm")
print(f"Volume: {{spar_shape.Volume:.1f}}mm³")
"""
```

- [ ] **Step 2: Execute in FreeCAD via RPC**

```bash
cd D:/Repos/aeroforge && PYTHONPATH=. python -c "
from hooks.freecad_rpc_helper import FreecadRPC
from src.freecad_scripts.spar import generate_spar_code

rpc = FreecadRPC()
code = generate_spar_code()
result = rpc.execute(code)
print(result)
"
```

Expected: "MainSpar created: 8.00x256.00x8.00mm"

- [ ] **Step 3: Run tests — verify GREEN**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python -m pytest tests/test_spar_geometry.py -v`
Expected: ALL PASS

- [ ] **Step 4: Take validation screenshots**

```bash
cd D:/Repos/aeroforge && PYTHONPATH=. python -c "
from hooks.freecad_rpc_helper import FreecadRPC
rpc = FreecadRPC()
paths = rpc.take_validation_screenshots('MainSpar')
for p in paths:
    print(f'Screenshot: {p}')
"
```

- [ ] **Step 5: Commit**

```bash
git add src/freecad_scripts/spar.py
git commit -m "feat: create carbon spar tube in FreeCAD — all dimension tests GREEN"
```

---

### Task 7: PreCommit Hook

**Files:**
- Create: `hooks/cad_pre_commit.py`

- [ ] **Step 1: Write the hook**

```python
#!/usr/bin/env python3
"""PreCommit hook: blocks commits without validation artifacts.

Checks:
1. No .FCBak or temp_* files staged
2. If geometry files are staged, validation screenshots must exist (< 10 min old)
"""

import subprocess
import sys
import os
import time


def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def main():
    staged = get_staged_files()

    # ── 1. Block forbidden files ──
    for f in staged:
        if f.endswith(".FCBak"):
            print(f"[PRE-COMMIT] BLOCKED: {f} — FreeCAD backup files cannot be committed", file=sys.stderr)
            sys.exit(1)
        if os.path.basename(f).startswith("temp_"):
            print(f"[PRE-COMMIT] BLOCKED: {f} — Temporary files cannot be committed", file=sys.stderr)
            sys.exit(1)

    # ── 2. Check for validation artifacts when geometry is staged ──
    geometry_extensions = (".step", ".stl", ".FCStd", ".3mf")
    geometry_staged = any(f.endswith(ext) for f in staged for ext in geometry_extensions)

    if geometry_staged:
        validation_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports", "validation")
        if not os.path.isdir(validation_dir):
            print("[PRE-COMMIT] BLOCKED: No validation directory. Run visual validation first.", file=sys.stderr)
            sys.exit(1)

        # Check for recent screenshots (< 10 minutes old)
        now = time.time()
        recent_screenshots = []
        for f in os.listdir(validation_dir):
            if f.endswith(".png"):
                fpath = os.path.join(validation_dir, f)
                age_minutes = (now - os.path.getmtime(fpath)) / 60
                if age_minutes < 10:
                    recent_screenshots.append(f)

        if not recent_screenshots:
            print("[PRE-COMMIT] BLOCKED: No recent validation screenshots (< 10 min).", file=sys.stderr)
            print("  Take screenshots first: rpc.take_validation_screenshots('ComponentName')", file=sys.stderr)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test manually**

```bash
echo "" | python hooks/cad_pre_commit.py
echo "Exit code: $?"
# Expected: 0 (no geometry staged)
```

- [ ] **Step 3: Commit**

```bash
git add hooks/cad_pre_commit.py
git commit -m "feat: add PreCommit hook requiring validation before geometry commits"
```

---

### Task 8: Session State Tracking

**Files:**
- Create: `cad-progress.md`

- [ ] **Step 1: Create initial progress file**

```markdown
# CAD Progress Tracker

## Component Status

| Component | Testing Gate | Validation Gate | Notes |
|-----------|-------------|-----------------|-------|
| MainSpar (8mm carbon tube) | PENDING | PENDING | First test case |

## Session Log

### 2026-03-28 — Enforcement Harness Setup
- Created hook infrastructure (PostToolUse, PreToolUse, PreCommit)
- Created FreeCAD RPC helper module
- Created spar geometry tests (TDD)
- Next: Execute spar test case end-to-end
```

- [ ] **Step 2: Commit**

```bash
git add cad-progress.md
git commit -m "docs: add CAD progress tracker for session state"
```

---

### Task 9: Update Settings and Documentation

**Files:**
- Modify: `.claude/settings.json` — add PreCommit hook
- Modify: `docs/spec_registry.md` — add new files
- Modify: `CLAUDE.md` — add hooks section

- [ ] **Step 1: Add PreCommit hook to settings**

Add to `.claude/settings.json`:
```json
"PreCommit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python hooks/cad_pre_commit.py"
      }
    ]
  }
]
```

- [ ] **Step 2: Update spec registry with new files**

Add to `docs/spec_registry.md`:
```markdown
### Enforcement Hooks
- `hooks/cad_post_execute.py` — PostToolUse: auto-screenshot + error detection
- `hooks/cad_pre_execute.py` — PreToolUse: block scaling, oversized code
- `hooks/cad_pre_commit.py` — PreCommit: require validation screenshots
- `hooks/freecad_rpc_helper.py` — FreeCAD RPC connection helper
- `.claude/settings.json` — Hook wiring configuration
- `cad-progress.md` — Session state tracking
```

- [ ] **Step 3: Add enforcement section to CLAUDE.md**

Add after the "Validation Artifacts" section:
```markdown
## MANDATORY: Enforcement Hooks (Deterministic, Cannot Skip)

Three hooks enforce quality automatically:

1. **PostToolUse** (`hooks/cad_post_execute.py`): After every FreeCAD execute_code:
   - Checks output for errors → BLOCKS if found
   - Takes auto-screenshot → saves to exports/validation/
   - Prints all object dimensions

2. **PreToolUse** (`hooks/cad_pre_execute.py`): Before every FreeCAD execute_code:
   - BLOCKS .scale() operations (destroys dimensions)
   - BLOCKS code > 500 lines (forces incremental building)

3. **PreCommit** (`hooks/cad_pre_commit.py`): Before every git commit:
   - BLOCKS .FCBak and temp_* files
   - BLOCKS geometry commits without recent validation screenshots

These hooks are DETERMINISTIC — they run automatically and cannot be overridden.
The CLAUDE.md rules are ADVISORY — they guide behavior but can be missed.
```

- [ ] **Step 4: Commit**

```bash
git add .claude/settings.json docs/spec_registry.md CLAUDE.md
git commit -m "docs: update CLAUDE.md, spec registry, and settings with enforcement hooks"
```

---

### Task 10: End-to-End Validation

- [ ] **Step 1: Run all existing tests**

```bash
cd D:/Repos/aeroforge && PYTHONPATH=. python -m pytest tests/ -v --tb=short
```

Expected: All original 91 tests pass + new spar tests pass (if FreeCAD running)

- [ ] **Step 2: Test the full hook pipeline**

1. Execute spar code via FreeCAD MCP → PostToolUse hook fires → screenshot taken
2. Try executing scaling code → PreToolUse hook blocks it
3. Try committing without screenshots → PreCommit hook blocks it
4. Take validation screenshots → commit succeeds

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: enforcement harness complete — hooks, tests, visual validation"
git push
```
