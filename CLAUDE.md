# AeroForge - AI-Enabled RC Sailplane Design System

## MANDATORY: Automation Rule

**The user NEVER types commands or runs scripts manually.** Claude does everything:
- Run all Python scripts, tests, builds, exports
- Execute all git operations
- Run all tools and viewers
- The user only reviews results and gives design direction

When running Python scripts from this project, always use: `cd D:/Repos/aeroforge && PYTHONPATH=. python <script>`

## MANDATORY: CAD Folder Organization (Clear Skies Style)

**Full rules in `cad/CAD_FRAMEWORK.md` (the authoritative reference).**

Key rules:
- **Every single piece = Component** (TPU strip, carbon rod, screw -- each gets its own folder)
- **Anything with >1 piece = Assembly**
- **2D technical drawing MUST be created and approved BEFORE any 3D modeling**
- **No special "master" level** -- top-level airplane is just another assembly
- **Hard enforcement via hooks** -- `hooks/cad_structure_validate.py` BLOCKS commits that violate structure

### Folder Structure (abbreviated)

```
cad/
├── components/{category}/{ComponentName}/
│   ├── ComponentName_drawing.dxf     # FIRST (2D drawing)
│   ├── ComponentName_drawing.png     # PNG render of drawing
│   ├── ComponentName.FCStd           # 3D model (AFTER drawing approval)
│   ├── renders/                      # 4 views (isometric, front, top, right)
│   └── COMPONENT_INFO.md
└── assemblies/{category}/{AssemblyName}/
    ├── AssemblyName_drawing.dxf
    ├── AssemblyName_drawing.png
    ├── AssemblyName.FCStd
    ├── renders/
    └── ASSEMBLY_INFO.md
```

### Workflow Order (Drawing-First, MANDATORY)

1. **Research** -- reference images, datasheets, sub-parts identification
2. **2D Drawing** -- create DXF + PNG, review and approve
3. **3D Model** -- only after drawing approval, dimensions match drawing exactly
4. **Assembly Validation** (assemblies only) -- collision detection, containment checks, spar routing verification using `src/cad/validation/assembly_check.py`. MUST PASS before proceeding.
5. **Renders** -- 4 standard views saved to renders/ folder
6. **Documentation** -- COMPONENT_INFO.md or ASSEMBLY_INFO.md
7. **Validation** -- dimensional tests + visual comparison, both gates pass
8. **Commit** -- only after all above steps complete

### Error Handling
- If a geometry check fails: fix the geometry, not the check
- If visual comparison shows misalignment: trace back to which joint/constraint is wrong
- Document any non-obvious design decisions in COMPONENT_INFO.md
- If unsure about real-world geometry: search for more reference images, don't guess

### Validation Artifacts
- Renders are saved to `cad/{components|assemblies}/{category}/{Name}/renders/`
- Additional validation screenshots to `exports/validation/`
- **Keep final validation artifacts** (they serve as visual documentation)
- **Delete intermediate/failed artifacts** once the component passes validation
- The `.gitignore` excludes temporary validation PNGs from git

## MANDATORY: Visual Validation After Every Change

**Every time a 2D drawing, 3D model, render, or any visual artifact is created or modified,
Claude MUST perform visual validation before proceeding. No exceptions.**

### The Protocol (cannot be skipped)

1. **Generate the artifact** (DXF+PNG, STEP, screenshot, etc.)
2. **View the FULL image** (Read the PNG) — check overall layout, proportions, orientation
3. **Zoom into critical areas** — render cropped/zoomed views of:
   - Tips, edges, corners (anywhere geometry converges)
   - Small features (bore holes, pockets, fillets)
   - Transitions between curves (look for slope discontinuities / kinks)
   - Label placement and readability
4. **Reason like an expert mechanical engineer** — ask:
   - Does this look like a professional engineering drawing?
   - Would a machinist / 3D printer understand this unambiguously?
   - Are there visible discontinuities, kinks, or artifacts?
   - Do the proportions match what the design consensus specifies?
5. **If ANY issue is found**: fix it BEFORE showing to the user or proceeding
6. **Report what was validated**: brief note on what was checked and any fixes applied

### Zoomed Validation Method (for 2D DXF drawings)

```python
# After generating a drawing, render zoomed views of critical areas:
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt

doc = ezdxf.readfile('path/to/drawing.dxf')
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(doc.modelspace())
ax.set_xlim(x_min, x_max)  # zoom to area of interest
ax.set_ylim(y_min, y_max)
ax.set_aspect('equal')
fig.savefig('exports/validation/detail_zoom.png', dpi=300, facecolor='white')
```

### Why This Exists

Incident: AI approved drawings with visible tip discontinuities across 6+ iterations
because validation was done only at full-sheet scale where 4mm features are invisible.
The aero and structural review agents also missed it. Zoomed validation would have
caught the slope discontinuity on iteration 1.

**Rule: If you can't see it clearly at full scale, ZOOM IN. Always zoom into tips,
transitions, and small features.**

## MANDATORY: Enforcement Hooks (Deterministic, Cannot Skip)

Four hooks enforce quality automatically:

1. **PostToolUse** (`hooks/cad_post_execute.py`): After every FreeCAD execute_code:
   - Checks output for errors → BLOCKS if found (exit 2)
   - Takes auto-screenshot → saves to exports/validation/
   - Prints all object dimensions

2. **PreToolUse** (`hooks/cad_pre_execute.py`): Before every FreeCAD execute_code:
   - BLOCKS .scale() operations (destroys dimensions)
   - BLOCKS code > 500 lines (forces incremental building)

3. **PreCommit** (`hooks/cad_pre_commit.py`): Before every git commit:
   - BLOCKS .FCBak and temp_* files
   - BLOCKS geometry commits without recent validation screenshots

4. **PreCommit** (`hooks/cad_structure_validate.py`): Before every git commit touching cad/:
   - BLOCKS .FCStd without corresponding .dxf (drawing-first rule)
   - BLOCKS .FCStd commit without 4 render views
   - BLOCKS renders commit without COMPONENT_INFO.md or ASSEMBLY_INFO.md
   - BLOCKS files with wrong naming conventions
   - Run standalone with `--all` flag to validate entire cad/ tree

These hooks are DETERMINISTIC — they run automatically and cannot be overridden.
CLAUDE.md rules are ADVISORY — they guide behavior but can be missed.

### Dual Quality Gates

Every component must pass BOTH gates independently:
- **Testing gate:** Dimensional assertions via pytest + FreeCAD RPC (deterministic)
- **Validation gate:** Visual comparison of screenshots to reference (semantic)

## MANDATORY: Assembly Validation (Collision & Containment)

**Every assembly MUST pass collision and containment checks before renders or commit.**

This was added after Incident 004 where spar rods protruded through H-Stab skin
and no one noticed because validation was skipped.

### Rules
1. **Collision check**: No two components in an assembly may intersect (boolean AND volume = 0)
2. **Containment check**: Internal components (spars, rods) must be FULLY inside their shells
3. **Spar routing check**: Every spar/rod must stay inside the airfoil envelope at EVERY span station
4. **Visual inspection**: After generating renders, ACTUALLY LOOK at them for errors (protruding parts, gaps, holes)
5. **Assembly-level agent review**: When assembling aerodynamic components, invoke the aero+structural agent team to review the ASSEMBLY, not just individual components

### Enforcement
- `src/cad/validation/assembly_check.py` provides `validate_assembly()`, `check_collision()`, `check_containment()`, `check_spar_routing()`
- Hook (`hooks/assembly_validate.py`) runs after any assembly 3D model is created — BLOCKS if collisions or protrusions detected
- These checks are run BEFORE renders, BEFORE commit

### Spar Routing Rule
Spars and rods are NOT straight cylinders placed in space. They must:
- Follow the actual taper/twist of the airfoil surface
- Be routed along the chord fraction at every span station (e.g., 25% chord line, 65% chord line)
- The chord fraction line CURVES as the planform tapers — the spar follows this curve
- Validate clearance at every 10mm span station

## MANDATORY: Complexity Philosophy (NEVER Simplify)

**"Why make it simple when it can be complex — for the same price?"**

The 3D printer has ZERO marginal cost for complexity. This means:

### Rules
1. **NEVER dismiss a performance improvement** because the shape is "too complex." The printer doesn't care about geometric complexity.
2. **The aerodynamicist decides the optimal shape** — NEVER prescribe or hardcode specific planforms, profiles, or geometries. The agent uses the latest aerodynamic science to determine the answer.
3. **Every surface must be the aerodynamic optimum** — the agent compares multiple options with quantified data and selects the best one. No shortcuts, no preconceptions.
4. **If in doubt, do MORE research** — spend more tokens, run more simulations, study more references. Never guess. Never settle.
5. **These rules apply to ANY aircraft type** — sailplane, aerobatic, drone, interceptor. The process is generic; the science determines the specific shapes.

### What This Means in Practice
- The aerodynamicist agent analyzes multiple design options and picks the best based on data
- Aero proposals MUST include comparison of at least 3 options with quantified performance
- The main thread NEVER overrides the agent's shape selection with a hardcoded alternative
- If the structural engineer requires changes, the aerodynamicist re-optimizes within the constraints
- Every junction, fillet, blend, and transition is optimized — not approximated

### Enforcement
- Hook (`hooks/complexity_check.py`) scans DESIGN_CONSENSUS.md — WARNS if it finds language suggesting simplification without quantified justification (e.g., "for simplicity" without a mass/strength tradeoff number)
- Aero proposals MUST include a comparison table with at least 3 design options

## MANDATORY: Aero-Structural Agent Team

**Every aerodynamic component/assembly MUST be designed by the two-agent team before any drawing is created.**

This applies to components in: `empennage/`, `wing/`, `fuselage/` (aerodynamic surfaces only).
Does NOT apply to: `hardware/`, `propulsion/` (unless designing a fairing).

### The Agents
- **Aerodynamicist** (`.claude/agents/aerodynamicist.md`): Proposes airfoil, planform, dimensions with NeuralFoil polar data
- **Structural Engineer** (`.claude/agents/structural-engineer.md`): Reviews for mass, printability, structural integrity

### The Protocol
1. Main thread spawns aerodynamicist → produces **Aero Proposal** (MUST compare at least 3 design options)
2. Main thread spawns structural engineer with the proposal → produces **Structural Review**
3. If modifications needed: aerodynamicist gets another pass (max 3 rounds)
4. When both agree: `DESIGN_CONSENSUS.md` written to the component/assembly folder
5. **Only then** can a 2D drawing be created

### Assembly-Level Agent Review
When assembling multiple aerodynamic components into an assembly:
- The agent team MUST review the assembly integration (not just individual components)
- Check for: interference drag at junctions, spar routing through assemblies, control surface clearances
- The aerodynamicist reviews the assembly aerodynamics
- The structural engineer reviews fit, clearance, collision, and load paths

### Enforcement
- `DESIGN_CONSENSUS.md` must exist in the folder before any `_drawing.dxf` file is created
- Hook (`hooks/aero_consensus_check.py`) checks this automatically and BLOCKS if missing
- Hook (`hooks/complexity_check.py`) WARNS if consensus contains unjustified simplification
- Hook (`hooks/assembly_validate.py`) reminds to run collision/containment checks on assemblies

## MANDATORY: Specification Consistency Rule

**When ANY design parameter changes, you MUST update ALL references immediately.**

This is the #1 project rule. Never leave outdated information anywhere. Never require
the user to remind you. This is automatic and deterministic.

Workflow:
1. Update `docs/specifications.md` FIRST (single source of truth)
2. Consult `docs/spec_registry.md` to find ALL other references
3. Update every listed file (docs, code, tests, component specs)
4. Recalculate dependent values (weight budget, wing loading, Reynolds, CG)
5. Mark affected 3D models as needing regeneration
6. Report transparently: list every file and value that changed

If you create a new file that references any design parameter, add it to
`docs/spec_registry.md` so future changes propagate to it.

## Project Mission

Design a **groundbreaking 3D-printed RC sailplane** using AI-driven complexity
to exceed commercial kits in aerodynamic performance at a fraction of the cost.

**Motto: "Why make it simple when it can be complex - for the same price?"**

The 3D printer has zero marginal cost for complexity. A topology-optimized lattice
rib costs the same as a flat plate. We exploit this to produce aerodynamic surfaces
that commercial kits cannot economically manufacture.

See `docs/philosophy.md` for the full design philosophy.
See `docs/specifications.md` for locked-in dimensions and weight budget.

## Architecture

### Two-Engine System
- **Build123d** (Python, headless) - ALL 3D modeling, parametric design, assemblies
- **FreeCAD 1.0+** (headless via FreeCADCmd) - FEM analysis (CalculiX), CFD (OpenFOAM)
- Both share the OpenCascade (OCCT) kernel. STEP files interchange losslessly.
- FreeCAD path: C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0

### Dependency Graph System
- **NetworkX DAG** for component dependency tracking
- **Pydantic models** for validated component specifications
- **Topological sort** for update ordering
- **CRUD operations** on component hierarchy
- **Validation hooks** at every deterministic step
- When a component changes -> all dependents update automatically

### Component vs Assembly Model

**Component** = ONE single physical piece. Never contains other pieces.
```
Component
├── OffShelfComponent  (servos, motors, screws - fixed dims from datasheets)
└── CustomComponent    (designed parts - parametric, from Text2CAD)
```

**Assembly** = TWO or more Components (or sub-Assemblies) joined together.
```
Assembly = Component + Component [+ Component...] + constraints
```

These are SEPARATE concepts with IDENTICAL folder structure (see CAD_FRAMEWORK.md).
Every item (component or assembly) has: mass, CG, inertia tensor, local coordinate system, bounding box.
Even the smallest screw is a component.

## Sailplane Quick Reference

| Parameter | Value |
|-----------|-------|
| Wingspan | 2.56m |
| Panels | 10 (5 per half, 256mm each - exact bed fit) |
| Root chord | 210mm |
| Tip chord | 115mm |
| Airfoil | AG24 (root) → AG03 (tip), blended continuously |
| Main spar | 8mm carbon tube (off-shelf) |
| Rear spar | 5mm spruce strip |
| Target AUW | 750-850g |
| Battery | 3S 1300mAh 75C racing LiPo (~155g pack, ~165g w/XT60, FIXED) |
| Receiver | Turnigy 9X V2 8ch (18g, FIXED) |
| Controls | Full-house + crow braking, 6 servos |
| Printer | Bambu A1 / P1S (256x256x256mm bed) |

## Key Design Principles

1. **Maximize printed complexity** - blended airfoils at every rib, geodetic lattice,
   topology-optimized mounts, integrated gap seals
2. **Minimize hand labor** - carbon tube slides through holes, spruce glues into slots,
   no cutting carbon cloth or cap strips
3. **AI optimizes everything** - airfoils, twist, planform, control sizing, Tx programming
4. **Every detail matters** - squeeze 2% from every surface. Printer doesn't charge extra.
5. **Cheap materials** - complex geometry is free, keep material cost under $60

## Tech Stack

### Core CAD
- **Build123d 0.10+** - Python parametric CAD (headless)
- **NetworkX** - DAG management
- **Pydantic** - Spec validation

### Analysis
- **FreeCAD FEM** - Structural (CalculiX)
- **CfdOF/OpenFOAM** - CFD aerodynamics
- **xfoil** - 2D airfoil polars

### Manufacturing
- **OrcaSlicer** CLI for headless slicing
- **3MF** preferred export format
- See `docs/slicer_pipeline.md`

### MCP Servers
- **context7** - Library docs
- **freecad-mcp** (neka-nat) - FreeCAD RPC
- **ocp-viewer-mcp** (dmilad) - Visual feedback

## Project Structure

```
aeroforge/
├── cad/                        # CAD folder (Clear Skies organization)
│   ├── CAD_FRAMEWORK.md        # Folder structure rules (authoritative)
│   ├── components/             # Individual pieces (one folder per piece)
│   │   ├── empennage/          # Category: tail surfaces
│   │   ├── wing/               # Category: wing parts
│   │   ├── fuselage/           # Category: fuselage parts
│   │   ├── hardware/           # Category: off-shelf parts
│   │   └── propulsion/         # Category: motor/prop/ESC
│   └── assemblies/             # Multi-piece assemblies
│       ├── empennage/
│       ├── wing/
│       └── AeroForge_Sailplane/  # Top-level (just another assembly)
├── src/
│   ├── core/                   # Component framework & DAG
│   │   ├── component.py        # Base Component, OffShelf, Custom classes
│   │   ├── assembly.py         # Assembly with constraints
│   │   ├── dag.py              # Dependency graph (NetworkX)
│   │   └── validation.py       # Validation hooks
│   ├── cad/                    # Build123d parametric models
│   │   ├── airfoils/           # Airfoil generators (AG, NACA)
│   │   ├── wing/               # Wing panels, ribs, skins
│   │   ├── fuselage/           # Pod, boom
│   │   ├── tail/               # H-stab, V-stab
│   │   └── hardware/           # Mounts, horns, hinges
│   ├── analysis/               # FreeCAD headless wrappers
│   └── text2cad/               # AI workflow pipeline
├── hooks/                      # Enforcement hooks (deterministic)
│   ├── cad_post_execute.py     # PostToolUse: error detection + screenshots
│   ├── cad_pre_execute.py      # PreToolUse: anti-pattern blocker
│   ├── cad_pre_commit.py       # PreCommit: validation gate
│   └── cad_structure_validate.py # PreCommit: folder structure enforcement
├── components/                 # Off-the-shelf specs (YAML)
├── docs/                       # Design documentation
│   ├── philosophy.md           # Design philosophy & competitive advantage
│   ├── specifications.md       # Locked-in specs, weight budget, dimensions
│   └── slicer_pipeline.md      # Print pipeline (OrcaSlicer, Bambu LAN)
├── exports/                    # STL, STEP, 3MF for printing
└── tests/                      # Validation tests
```

## Coding Conventions

- Python 3.10+
- Type hints required
- Docstrings for all modules/classes
- All dimensions in mm, weights in grams
- Pydantic models for all component specs
- NetworkX for all dependency relationships

## Git Workflow

- `main` - stable, tested designs
- Feature branches for changes
- PR reviews via pr-review-toolkit plugin
