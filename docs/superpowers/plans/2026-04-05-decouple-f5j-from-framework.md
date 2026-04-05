# Decouple F5J Sailplane Code From Generic Framework

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Move all F5J sailplane-specific code out of src/ into projects/air4-f5j/, leaving src/ as a clean generic aircraft design framework.

**Architecture:** Surgical extraction -- move F5J-specific files and class instances into the project directory. Generic base classes and parametric builders stay in src/. Mixed files get their SAILPLANE defaults removed (parameters become required). The F5J project keeps working via local imports.

**Tech Stack:** Python, Build123d, pytest

---

### Task 1: Move specs.py to F5J project

The SAILPLANE singleton is the root of all hardcoding. Move it to the project.

**Files:**
- Move: src/core/specs.py -> projects/air4-f5j/specs.py
- Modify: src/core/__init__.py (remove SAILPLANE export)

- [ ] Step 1: Copy specs.py to project
- [ ] Step 2: Remove SAILPLANE from core __init__.py (delete the import line)
- [ ] Step 3: Delete src/core/specs.py
- [ ] Step 4: Run tests (test_core.py, test_bom.py, test_bom_sync.py) -- these dont use SAILPLANE
- [ ] Step 5: Commit

### Task 2: Move F5J hardware models to project

battery.py, receiver.py, and the F5J-specific servo classes all import SAILPLANE.

**Files:**
- Move: src/cad/hardware/battery.py -> projects/air4-f5j/hardware/battery.py
- Move: src/cad/hardware/receiver.py -> projects/air4-f5j/hardware/receiver.py
- Modify: src/cad/hardware/servo.py (keep generic MicroServo, extract F5J classes)
- Create: projects/air4-f5j/hardware/servos.py (JX_PDI_1109MG, JX_PDI_933MG, FlyskyIA6B)
- Create: projects/air4-f5j/hardware/__init__.py

- [ ] Step 1: Create projects/air4-f5j/hardware/
- [ ] Step 2: Move battery.py and receiver.py, update SAILPLANE import to project-local
- [ ] Step 3: Extract JX/Flysky classes from servo.py into projects/air4-f5j/hardware/servos.py
- [ ] Step 4: Clean servo.py -- keep only generic MicroServo base, remove SAILPLANE import
- [ ] Step 5: Run tests
- [ ] Step 6: Commit

### Task 3: Move F5J wing panel builder to project

wing_panel_p1.py is 100% F5J-specific.

**Files:**
- Move: src/cad/wing/wing_panel_p1.py -> projects/air4-f5j/cad/wing_panel_p1.py
- Modify: src/cad/wing/panel.py (remove SAILPLANE default, make wing/spar required params)

- [ ] Step 1: Move wing_panel_p1.py to projects/air4-f5j/cad/
- [ ] Step 2: In panel.py, replace SAILPLANE defaults with ValueError if specs missing
- [ ] Step 3: Remove SAILPLANE import from panel.py
- [ ] Step 4: Run tests
- [ ] Step 5: Commit

### Task 4: Move F5J analysis code to project

structural_fem.py is F5J-specific. airfoil_polars.py is mixed.

**Files:**
- Move: src/analysis/structural_fem.py -> projects/air4-f5j/analysis/structural_fem.py
- Extract: analyze_wing_stations() + print_wing_analysis() -> projects/air4-f5j/analysis/wing_polars.py
- Clean: src/analysis/airfoil_polars.py (remove F5J function, keep generic ones)

- [ ] Step 1: Create projects/air4-f5j/analysis/
- [ ] Step 2: Move structural_fem.py, update SAILPLANE imports
- [ ] Step 3: Extract analyze_wing_stations into project wing_polars.py
- [ ] Step 4: Clean airfoil_polars.py -- remove SAILPLANE import, keep generic functions
- [ ] Step 5: Run tests
- [ ] Step 6: Commit

### Task 5: Update F5J project scripts to use local imports

All scripts in projects/air4-f5j/scripts/ that import from src.core.specs need updating.

- [ ] Step 1: grep -rl "from src.core.specs" projects/air4-f5j/scripts/
- [ ] Step 2: Update each to import from project-local specs
- [ ] Step 3: Update hardware imports similarly
- [ ] Step 4: Commit

### Task 6: Verify zero SAILPLANE references remain in src/

- [ ] Step 1: grep -r "SAILPLANE" src/ --include="*.py" -- expect zero
- [ ] Step 2: grep -ri "f5j|jx.pdi|flysky|turnigy|tattu|1109mg|933mg" src/ --include="*.py" -- expect zero
- [ ] Step 3: Full test suite passes
- [ ] Step 4: Lint passes
- [ ] Step 5: Commit any cleanup

### Task 7: Push and verify CI

- [ ] Step 1: git push (pre-push hook runs tests)
- [ ] Step 2: Verify CI passes: gh run list --limit 1

---

## What moves where

| From (src/) | To (projects/air4-f5j/) | Type |
|---|---|---|
| src/core/specs.py | specs.py | Full move |
| src/cad/hardware/battery.py | hardware/battery.py | Full move |
| src/cad/hardware/receiver.py | hardware/receiver.py | Full move |
| src/cad/hardware/servo.py (JX/Flysky) | hardware/servos.py | Extract |
| src/cad/wing/wing_panel_p1.py | cad/wing_panel_p1.py | Full move |
| src/analysis/structural_fem.py | analysis/structural_fem.py | Full move |
| src/analysis/airfoil_polars.py (wing fn) | analysis/wing_polars.py | Extract |

## What stays in src/ (generic framework)

| File | Purpose |
|---|---|
| src/core/component.py | Generic component/assembly framework |
| src/core/assembly.py | Generic assembly hierarchy |
| src/core/validation.py | Generic validation hooks |
| src/core/bom.py, bom_sync.py | Generic BOM system |
| src/cad/airfoils/ | Generic airfoil library (NACA gen, .dat loader, blending) |
| src/cad/wing/__init__.py | Generic WingSection parametric class |
| src/cad/wing/panel.py | Generic wing panel builder (specs required, no defaults) |
| src/cad/hardware/servo.py | Generic MicroServo base class only |
| src/cad/drawing/ | Generic drawing modules |
| src/analysis/airfoil_polars.py | Generic airfoil analysis (no wing-specific fns) |
| src/orchestrator/ | Generic workflow engine |
| src/providers/ | Generic provider system |
