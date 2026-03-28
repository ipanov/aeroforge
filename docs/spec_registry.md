# Specification Registry (Single Source of Truth Map)

## Purpose

This file maps every design parameter to every location it appears in the project.
When a parameter changes, EVERY listed location must be updated.

**docs/specifications.md is the SINGLE SOURCE OF TRUTH.** All other files reference
or derive from it. If there's ever a conflict, specifications.md wins.

## Parameter Map

### Wingspan
- `docs/specifications.md` — primary definition
- `CLAUDE.md` — quick reference table
- `README.md` — current specifications table
- `docs/slicer_pipeline.md` — panel sizing table
- `src/core/specs.py` — `WingSpec.wingspan`
- `src/cad/wing/` — any wing generator code using span constants
- `tests/test_wing.py` — test fixtures using span values
- `tests/test_spec_consistency.py` — consistency checks

### Chord (root/tip)
- `docs/specifications.md` — primary definition
- `CLAUDE.md` — quick reference table
- `src/cad/wing/` — WingSectionSpec defaults
- `src/cad/airfoils/` — if chord-dependent scaling exists
- `tests/test_wing.py` — test fixtures

### Airfoil Selection
- `docs/specifications.md` — airfoil table with stations
- `docs/aerodynamics_research.md` — AG series analysis, Re-based recommendations (Section 2)
- `CLAUDE.md` — quick reference
- `src/cad/airfoils/__init__.py` — AIRFOIL_DATABASE, generator functions
- `tests/test_airfoils.py` — test data

### Panel Count / Layout
- `docs/specifications.md` — panel layout diagram
- `docs/slicer_pipeline.md` — panel sizing table
- `CLAUDE.md` — quick reference
- `src/cad/wing/` — panel generation code

### Spar Specifications
- `docs/specifications.md` — spar table
- `CLAUDE.md` — quick reference
- `src/cad/wing/` — spar hole dimensions in rib generator
- `components/` — off-shelf spar specs if defined

### Motor / Propeller / Spinner
- `docs/specifications.md` — weight budget (motor 50-60g, prop+spinner 15-20g)
- `docs/motor_propeller_research.md` — full motor/prop/spinner research and recommendations
- `CLAUDE.md` — quick reference (motor TBD)
- `src/cad/hardware/` — motor mount dimensions depend on motor OD (28mm)

### Weight Budget
- `docs/specifications.md` — full weight budget tables
- `docs/motor_propeller_research.md` — power system weight breakdown
- `CLAUDE.md` — target AUW
- `components/servos/servo_database.py` — servo weights
- `src/core/validation.py` — mass validation thresholds

### Battery / Receiver (Fixed Constraints)
- `docs/specifications.md` — weight and dimensions
- `components/` — if component spec files exist

### Material Properties
- `docs/specifications.md` — material table
- `docs/aerodynamics_research.md` — LW-PLA foaming parameters, wall thicknesses (Section 10)
- `src/core/component.py` — MATERIAL_DENSITY dict, Material enum
- `src/core/validation.py` — if material-specific validation exists

### Flight Modes / Control
- `docs/specifications.md` — flight mode table, channel assignments
- `docs/aerodynamics_research.md` — flap configurations and deflection angles (Section 6)
- `src/text2cad/` — if flight mode definitions exist in code

### Print Bed Size
- `docs/specifications.md` — manufacturing section
- `docs/slicer_pipeline.md` — bed dimensions
- `src/core/validation.py` — BAMBU_BED_SIZE constant

### Fuselage Dimensions
- `docs/specifications.md` — fuselage section
- `src/cad/fuselage/__init__.py` — FuselagePodSpec defaults

### Empennage Dimensions
- `docs/specifications.md` — empennage section
- `docs/aerodynamics_research.md` — tail volume coefficients, tail config comparison (Section 9)
- `src/cad/tail/__init__.py` — TailSectionSpec defaults

### Performance Targets
- `docs/specifications.md` — performance table
- No code references yet

### Bill of Materials
- `src/core/bom.py` — BOM data model and generator
- `docs/bom.md` — auto-generated BOM markdown (to be created)
- `docs/specifications.md` — weight budget tables must match BOM totals
- `CLAUDE.md` — target AUW must match BOM total mass
- `README.md` — cost estimate must match BOM total cost

### Consumables & Assembly Materials
- `docs/bom.md` — CA glue, epoxy, Velcro, zip ties, covering film
- Not in specs.py (not parametric), but tracked in BOM

### Enforcement Hooks
- `hooks/cad_post_execute.py` — PostToolUse: auto-screenshot + error detection
- `hooks/cad_pre_execute.py` — PreToolUse: block scaling, oversized code
- `hooks/cad_pre_commit.py` — PreCommit: require validation screenshots
- `hooks/freecad_rpc_helper.py` — FreeCAD RPC connection helper
- `.claude/settings.json` — Hook wiring configuration
- `cad-progress.md` — Session state tracking
- `tests/test_spar_geometry.py` — Spar dimensional assertions

## How to Use This Registry

When changing ANY parameter:

1. Update `docs/specifications.md` FIRST (single source of truth)
2. Look up the parameter in this registry
3. Update EVERY listed file
4. If a file doesn't exist yet, skip it
5. If you find a reference NOT listed here, add it to this registry
6. Run tests to catch any value mismatches
7. Report all changes transparently to the user

## Keeping This Registry Current

When creating new files that reference design parameters:
- Add an entry to this registry mapping parameter → new file
- This applies to code, tests, docs, and component specs
