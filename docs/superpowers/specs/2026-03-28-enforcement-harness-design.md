# Enforcement Harness for CAD Validation

**Date:** 2026-03-28
**Status:** Approved (PARTIALLY SUPERSEDED by `cad/CAD_FRAMEWORK.md` for folder structure and workflow order)
**Problem:** AI writes policies but never enforces them. Claims completion without verification. Produces garbage geometry without visual validation.

> **NOTE (2026-03-28):** The CAD folder organization and drawing-first workflow rules
> are now defined in `cad/CAD_FRAMEWORK.md` and enforced by `hooks/cad_structure_validate.py`.
> The three-layer enforcement hooks described below remain active and unchanged.
> Render screenshots now go to `cad/{components|assemblies}/{category}/{Name}/renders/`
> in addition to the auto-screenshots in `exports/validation/`.

## Core Principle

Every enforcement mechanism must BLOCK, not warn. If it can be ignored, it will be.

## Three-Layer Enforcement

### Layer 1: PostToolUse BLOCKING Hook

**File:** `hooks/cad_post_execute.py`
**Trigger:** After every `mcp__freecad__execute_code` call
**Actions:**
1. Parse tool output for errors ("Failed to", "Invalid", "Error", negative volume, NaN)
2. If errors found: print to stderr, exit code 2 (BLOCK)
3. Send RPC to FreeCAD: take isometric screenshot, save to `exports/validation/auto_{timestamp}.png`
4. Query all object bounding boxes, print dimensions to stdout
5. Exit 0 (allow) only if no errors detected

**Why it blocks:** The AI cannot proceed to the next operation if FreeCAD reported any error. Forces immediate diagnosis and fix.

### Layer 2: PreCommit BLOCKING Hook

**File:** `hooks/cad_pre_commit.py`
**Trigger:** Before every git commit
**Checks:**
1. No `.FCBak` or `temp_*` files staged
2. If any `.step`, `.FCStd`, or geometry Python file is staged:
   - A validation screenshot must exist in `exports/validation/` from the last 10 minutes
   - A `_comparison.md` file must exist with "PASS" verdict
3. Block commit (exit 1) if checks fail

**Why it blocks:** Cannot commit geometry that hasn't been visually validated.

### Layer 3: PreToolUse BLOCKING Hook

**File:** `hooks/cad_pre_execute.py`
**Trigger:** Before any `mcp__freecad__execute_code` call
**Checks:**
1. Block code containing `.scale(` — scaling destroys dimensions (ClearSkies rule)
2. Block code longer than 500 lines — forces incremental building
3. Block code without `doc.recompute()` — geometry must be recomputed after changes

**Why it blocks:** Prevents known anti-patterns before they execute.

## Settings Configuration

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
    ],
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
  }
}
```

## Dimensional Assertion Tests (pytest)

### Structure
- `tests/test_freecad_geometry.py` — Bounding box and volume assertions
- `tests/test_geometry_visual.py` — Screenshot capture + reference path logging
- `tests/test_assembly_fit.py` — Collision and clearance checks

### Pattern for Every Component

```python
def test_component_dimensions():
    """Query FreeCAD via RPC, assert against specs.py."""
    server = xmlrpc.client.ServerProxy("http://localhost:9875")
    result = server.execute_code("""
        obj = FreeCAD.ActiveDocument.getObject("ComponentName")
        bb = obj.Shape.BoundBox
        print(f"X:{bb.XLength:.3f}")
        print(f"Y:{bb.YLength:.3f}")
        print(f"Z:{bb.ZLength:.3f}")
        print(f"VOL:{obj.Shape.Volume:.3f}")
    """)
    # Parse dimensions from output
    # Assert against specs.py values with tolerance
    assert abs(x - EXPECTED_X) < TOLERANCE
```

### Test-Driven CAD
1. Write test FIRST (assert expected dimensions)
2. Run test — FAILS (no geometry) = RED
3. Build geometry in FreeCAD
4. Run test — PASSES = GREEN
5. Visual validation
6. Commit

## Visual Validation Loop

### Mandatory Steps (Cannot Skip)

1. **Before building:** Store reference image at `components/{name}/reference.png`
   - Source: datasheet, photo, existing STEP render, or online image
   - If no reference exists, document why and what dimensions to check instead

2. **After building:** Take 4 screenshots via FreeCAD RPC
   ```python
   views = ["isometric", "front", "top", "right"]
   for view_name in views:
       view.viewXxx()
       view.fitAll()
       view.saveImage(f"exports/validation/{name}_{view_name}.png", 1920, 1080, "Current")
   ```

3. **Compare:** AI reads both reference and screenshots using vision capability
   - Check: proportions, features, orientation, relative positions, missing details
   - List every discrepancy found

4. **Log:** Write to `exports/validation/{name}_comparison.md`
   ```markdown
   ## Visual Comparison: {ComponentName}
   Reference: components/{name}/reference.png
   Screenshots: exports/validation/{name}_*.png

   ### Discrepancies
   - [list each issue]

   ### Verdict: PASS / FAIL
   ```

5. **Iterate or commit:** FAIL → fix → re-screenshot → re-compare. PASS → commit allowed.

## Test Case: Carbon Spar Tube

The simplest real component to validate the harness end-to-end.

### Spec (from specs.py)
- OD: 8.0mm
- ID: 6.0mm
- Wall: 1.0mm
- Material: Pultruded carbon fiber
- Length: cut to fit (256mm per panel section)

### Test File
```python
# tests/test_spar_geometry.py

def test_main_spar_outer_diameter():
    """Main spar OD must be 8.0mm ± 0.01mm."""
    bb = query_freecad_bounding_box("MainSpar")
    # Cylinder along Y: OD = max(XLength, ZLength)
    od = max(bb['X'], bb['Z'])
    assert abs(od - 8.0) < 0.01, f"Spar OD {od}mm != 8.0mm"

def test_main_spar_inner_diameter():
    """Main spar ID must be 6.0mm ± 0.01mm."""
    # Query inner hole diameter
    id = query_freecad_inner_diameter("MainSpar")
    assert abs(id - 6.0) < 0.01, f"Spar ID {id}mm != 6.0mm"

def test_main_spar_wall_thickness():
    """Wall thickness must be 1.0mm ± 0.01mm."""
    od = query_outer_diameter("MainSpar")
    id = query_inner_diameter("MainSpar")
    wall = (od - id) / 2
    assert abs(wall - 1.0) < 0.01, f"Wall {wall}mm != 1.0mm"
```

### Execution Sequence
1. Write test → run → RED (no geometry)
2. Build spar in FreeCAD via MCP
3. PostToolUse hook fires → auto-screenshot + dimension print
4. Run test → GREEN
5. Visual validation (it's a cylinder — verify it's round, not square)
6. Write comparison.md with PASS
7. Commit → PreCommit hook checks screenshot + comparison → allowed

## What This Prevents

| Past Failure | How Harness Prevents It |
|---|---|
| Hollow shell wing with no ribs | PostToolUse would show empty interior in auto-screenshot |
| Spar tubes hanging below wing | Dimension extraction would show wrong Z position |
| Claiming "done" without looking | PreCommit blocks without recent screenshot + comparison |
| Traditional ribs instead of geodesic | Visual comparison to reference would catch wrong pattern |
| Negative volume from offset() | PostToolUse blocks on negative volume detection |
| OCP screenshot hanging forever | Using FreeCAD saveImage() instead — proven working |

## Dual Quality Gates (from Sagar Mandal's Agentic Engineering)

Testing and validation are SEPARATE processes. Both must pass independently.

**Testing gate (deterministic):** "Does it work?"
- Python script ran without errors
- FreeCAD geometry compiles (no Invalid objects)
- Bounding box dimensions match specs.py within tolerance
- Volume is positive and reasonable

**Validation gate (visual/semantic):** "Is it right?"
- Screenshot looks like the real component
- Proportions match reference image
- All features present (holes, fillets, connectors)
- Orientation correct
- Assembly fit verified

A component can pass testing (correct dimensions) but fail validation (looks nothing like the real thing). Our battery incident is exactly this — dimensions were roughly right but the result looked nothing like a Tattu 1300mAh.

## Session State Tracking (from Anthropic Harness Article)

**File:** `cad-progress.md` (persistent across sessions)

Tracks:
- Which components have been built
- Which have passed testing gate
- Which have passed validation gate
- Which need rework and why
- Current assembly state

Updated automatically by PostToolUse hooks. Read at session start to understand current state.

## Advisory vs Deterministic Split

**CLAUDE.md (advisory ~80% compliance):**
- Design philosophy ("why make it simple when complex?")
- Research-first protocol
- Material selection guidelines
- Aerodynamic design principles

**Hooks (deterministic 100% compliance):**
- Auto-screenshot after every FreeCAD operation
- Block commits without validation
- Block scaling operations
- Block oversized code blocks
- Error detection in FreeCAD output

This split follows the principle: if it must happen every time without exception, make it a hook.

## Implementation Priority

1. **hooks/cad_post_execute.py** — Auto-screenshot + error detection + dimension extraction
2. **hooks/cad_pre_execute.py** — Anti-pattern blocker (no scaling, size limits)
3. **tests/test_spar_geometry.py** — First test case (carbon spar tube)
4. **hooks/cad_pre_commit.py** — Commit gate (validation required)
5. **cad-progress.md** — Session state tracking
6. **Visual validation scripts** — Screenshot → compare → log loop

## Sources

- Anthropic: "Effective Harnesses for Long-Running Agents" (https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- Sagar Mandal: "Agentic Engineering Part 9: Product Guardrails" (https://www.sagarmandal.com/2026/03/15/agentic-engineering-part-9-product-guardrails/)
- disler: "Claude Code Hooks Mastery" (https://github.com/disler/claude-code-hooks-mastery)
- ClearSkies project: hooks/freecad_enforcer.py, check_execute_output.py, auto_validate_cad.py
- Claude Code hooks documentation (https://code.claude.com/docs/en/hooks)
