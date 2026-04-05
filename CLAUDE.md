# AeroForge — AI-Autonomous Aircraft Design Framework

> Generic framework for designing heavier-than-air aircraft. Any type:
> sailplane, drone, aerobatic, interceptor, paper airplane.
> The active project determines all specifics.

## MANDATORY: Automation Rule

**The user NEVER types commands or runs scripts manually.** Claude does everything.
The user only reviews results and gives design direction in natural language.

When running Python scripts: `cd D:/Repos/aeroforge && PYTHONPATH=. python <script>`

## Entry Points

- **`/aeroforge`** — Drive the active project's workflow
- **`/aeroforge-init`** — Initialize a new project

These are Claude Code skills. The LLM reads workflow state, decides what to do,
spawns agents, and updates state. See `.claude/commands/` for details.

## Hierarchical Workflow

### Project Phases (top level)

```
REQUIREMENTS → RESEARCH → DESIGN → IMPLEMENTATION → VALIDATION → RELEASE
```

### Per-Node Design Cycle (each component/assembly)

```
AERO_PROPOSAL → STRUCTURAL_REVIEW → AERO_RESPONSE → CONSENSUS → DRAWING_2D → MODEL_3D → OUTPUT
```

- **Top-down design**: Start at aircraft level, drill down to components
- **All 2D drawings approved** before ANY 3D modeling starts
- **Bottom-up implementation**: Build 3D from leaves up (components first, assemblies last)
- **OUTPUT** format determined by manufacturing provider (3MF, laser files, fold diagram, etc.)
- **VALIDATION** runs CFD + FEA on the assembled top object only
- **Validation cascade**: If changes needed, LLM decides which nodes to redesign

### Node Types

| Type | Design Cycle | Examples |
|------|-------------|----------|
| **component** | Full 7-step | Wing panel, elevator, fuselage nose |
| **assembly** | Full 7-step | Wing assembly, H-stab, the whole aircraft |
| **off_shelf** | None | Servo, battery, carbon rod, screw |

### Iteration Rules

- Up to 3 agent rounds per node before user decides
- Agents: aerodynamicist proposes, structural engineer reviews
- DESIGN_CONSENSUS.md required before any drawing
- If requirements change at the top → entire tree invalidates

## Multi-Project Structure

```
aeroforge/
├── src/                        # Framework code (shared)
├── config/                     # System-level providers
│   └── system_providers.yaml   # CFD, FEA, airfoil providers
├── projects/
│   └── {project-slug}/         # Each project is self-contained
│       ├── aeroforge.yaml      # Project config + project providers
│       ├── workflow_state.json  # Workflow state
│       ├── cad/                # Components + assemblies
│       │   ├── components/     # Individual pieces (incl. off-shelf)
│       │   └── assemblies/     # Multi-piece assemblies
│       ├── docs/               # Project-specific docs, RAG data
│       └── exports/            # Validation artifacts
├── docs/framework/             # Generic framework documentation
├── hooks/                      # Deterministic enforcement hooks
├── tests/                      # Framework tests
└── .claude/
    ├── agents/                 # Generic agent definitions
    ├── commands/               # /aeroforge, /aeroforge-init skills
    └── active_project          # Points to current project slug
```

## CAD Folder Organization

- **Every single piece = Component** (even a screw gets its own folder)
- **Anything with >1 piece = Assembly**
- **Top-level aircraft = just another assembly** (no special level)
- **Off-shelf components** go in `cad/components/hardware/` with spec.yaml

### Component Folder

```
ComponentName/
├── AERO_PROPOSAL_R1.md          # Versioned design documents
├── STRUCTURAL_REVIEW_R1.md      # R = round (monotonic, never resets)
├── AERO_RESPONSE_R1.md
├── DESIGN_CONSENSUS_R1.md       # Agent agreement
├── ComponentName_drawing.dxf    # 2D drawing (FIRST)
├── ComponentName_drawing.png    # PNG render
├── ComponentName.step           # 3D model (AFTER drawing approval)
├── renders/                     # 4 views (isometric, front, top, right)
└── COMPONENT_INFO.md
```

### Deliverable Naming Convention

Design documents are versioned: `{STEP}_R{round}.md`

- **R** = round number (monotonically increasing, never resets)
- Increments on: user rejection, agent negotiation restart, or validation cascade
- Every component/assembly tracks its own round counter independently

Use `sm.deliverable_name(node_name, step)` to generate the correct filename.

```
AERO_PROPOSAL_R1.md       — first proposal
STRUCTURAL_REVIEW_R1.md   — first review
AERO_PROPOSAL_R2.md       — second round (user rejected / cascade)
DESIGN_CONSENSUS_R2.md    — consensus after second round
AERO_PROPOSAL_R3.md       — third round (another cascade)
```

### Drawing-First Rule (MANDATORY)

2D drawing MUST be created and approved BEFORE any 3D modeling.
The drawing is constructed from the design consensus specifications,
NOT projected from a 3D model (the 3D model doesn't exist yet).

## Provider System

### System-level (shared, hardware-dependent)

| Provider | Purpose | Config |
|----------|---------|--------|
| CFD | Wind tunnel simulation | `config/system_providers.yaml` |
| FEA | Structural analysis | `config/system_providers.yaml` |
| Airfoil | 2D polar analysis | `config/system_providers.yaml` |

### Project-level (per-project, manufacturing-dependent)

| Provider | Purpose | Config |
|----------|---------|--------|
| Manufacturing | FDM, manual, CNC, laser | `projects/{slug}/aeroforge.yaml` |
| Slicer | OrcaSlicer, PrusaSlicer | `projects/{slug}/aeroforge.yaml` |

Auto-detected during init. The LLM suggests based on hardware scan.

## Agents

All agents are **generic** — they read project config at runtime.

| Agent | Role | Reads From |
|-------|------|-----------|
| Aerodynamicist | Airfoil, planform, performance | Project aeroforge.yaml |
| Structural Engineer | Mass, strength, manufacturability | Project aeroforge.yaml |
| Wind-Tunnel Engineer | SU2 CFD analysis | system_providers.yaml |
| Structures Analyst | FreeCAD FEA analysis | system_providers.yaml |

Aircraft type, materials, tooling are NOT hardcoded in agent definitions.

## Enforcement Hooks (Deterministic)

Hooks run automatically and cannot be overridden:

| Hook | Trigger | Action |
|------|---------|--------|
| `workflow_step_guard.py` | Write/Edit | Blocks work outside active step |
| `aero_consensus_check.py` | Write (drawings) | Blocks without DESIGN_CONSENSUS.md |
| `cad_structure_validate.py` | git commit | Blocks naming/structure violations |
| `cad_pre_commit.py` | git commit | Blocks unvalidated geometry |
| `complexity_check.py` | Write | Warns against unjustified simplification |
| `assembly_validate.py` | PostToolUse | Blocks assembly collisions |

## Visual Validation (MANDATORY)

After creating/modifying any visual artifact:
1. View the full image
2. Zoom into critical areas (tips, edges, transitions)
3. Fix any issues BEFORE proceeding
4. Report what was validated

## Engineering Drawing Rules

Drawings must comply with ASME Y14.3 / ISO orthographic conventions:
- Orthographic views must be true projections
- Primary views aligned by projection
- Same scale across views on one sheet
- Long-span parts arranged horizontally on landscape sheets
- Dimensions follow geometry orientation

## Complexity Philosophy

**"Why make it simple when it can be complex — for the same price?"**

- NEVER simplify for manufacturing convenience
- The aerodynamicist decides optimal shapes — never hardcode
- Compare at least 3 design options with quantified data
- Manufacturing does not penalize geometric complexity

## Specification Consistency

When ANY design parameter changes:
1. Update project specifications FIRST
2. Update ALL references (use spec_registry.md if it exists)
3. Recalculate dependent values
4. Mark affected models for regeneration

## Architecture

- **Build123d** (Python, headless) — ALL 3D modeling
- **OCP Viewer** (VS Code) — 3D visualization and screenshots
- **ezdxf** — 2D engineering drawings (constructed from specs)
- **NetworkX** — Component dependency graph
- **Pydantic** — Specification validation
- **Provider system** — Swappable analysis and manufacturing backends
- **SU2 + Gmsh** — CFD meshing and solving (Euler/RANS)
- **ParaView** — 3D Cp/Cf heatmap rendering (matplotlib fallback)
- **n8n** — Visual dashboard workflow + event webhooks (mandatory)

### CFD Validation Pipeline (`src/analysis/`)

| Module | Responsibility |
|--------|---------------|
| `cfd_results.py` | Parse SU2 output, stability derivatives, drag breakdown, Aero Test Report |
| `cfd_monitor.py` | Real-time SU2 progress polling, ETA, divergence detection |
| `cfd_visualization.py` | ParaView 3D heatmaps (Cp/Cf), matplotlib fallback |
| `cfd_feedback.py` | Structured pass/fail for orchestrator — no hierarchy knowledge |

### n8n Visual Dashboard (`src/orchestrator/`)

| Module | Responsibility |
|--------|---------------|
| `n8n_workflow_builder.py` | Generate sticky-note canvas from workflow state |
| `n8n_client.py` | REST API client, visual sync, event webhooks |

### BOM and Procurement (`src/core/`)

BOM data is **per-project** (`projects/{slug}/aeroforge.bom.yaml`).
Framework code is generic and shared.

## Coding Conventions

- Python 3.10+, type hints, docstrings
- All dimensions in mm, weights in grams
- Tests required for framework code
- CI must pass before push to master
