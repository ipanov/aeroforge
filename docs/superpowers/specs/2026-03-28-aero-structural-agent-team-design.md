# Aero-Structural Agent Team Design

**Date:** 2026-03-28
**Status:** Approved
**Context:** Repeated failures designing aerodynamic components (H-stab) because no engineering validation was applied. Shapes were drawn from formulas without checking physical feasibility, structural constraints, or real-world reference.

## Problem

A single designer (the main Claude thread) cannot simultaneously optimize for aerodynamic performance AND structural/manufacturing constraints. Every attempt produced designs that were either aerodynamically unjustified (rectangular planforms, wrong airfoils) or structurally impossible (hinges that can't physically rotate, internal structures that don't fit).

## Solution

A mandatory two-agent team that negotiates every aerodynamic component design before any drawing is created.

## Architecture

### Approach: Sequential Feedback Loop (Approach C)

Two custom agents defined in `.claude/agents/`, orchestrated by the main thread. No separate orchestrator agent.

### Agent 1: Aerodynamicist

**File:** `.claude/agents/aerodynamicist.md`

**Role:** MSc Aerospace Engineering, specializing in low-Reynolds-number RC model design. Thinks like Mark Drela.

**Responsibilities:**
- Airfoil selection with NeuralFoil/AeroSandbox polar analysis
- Planform optimization (span, chord, taper, sweep, tip shape)
- Reynolds number analysis at each span station
- Tail volume coefficient sizing
- Control surface sizing and deflection ranges
- Drag estimation and L/D prediction
- Reference to competition sailplane data (docs/rag/)

**Tools:** `Bash` (AeroSandbox/NeuralFoil), `Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`

**Output:** Aero Proposal document with specific numbers, justifications, and polar data.

### Agent 2: Structural Engineer

**File:** `.claude/agents/structural-engineer.md`

**Role:** MSc Mechanical Engineering, specializing in 3D-printed aircraft structures and additive manufacturing.

**Responsibilities:**
- Mass budget feasibility (can this be printed at target weight?)
- Wall thickness vs strength analysis
- Spar sizing (diameter, material, position)
- Print orientation and bed fit
- Attachment point design (pivot bushings, joiner rod, control horns)
- Flutter/divergence assessment
- Material selection (LW-PLA, PLA, PETG, TPU per sub-part)
- Infill strategy (Gyroid %, vase mode feasibility)

**Tools:** `Bash` (structural calculations), `Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`

**Output:** Structural Review document with feasibility assessment, weight estimate, and proposed modifications.

## Feedback Loop Protocol

### Round 1
1. Main thread spawns **aerodynamicist** with design brief (component type, constraints from specs, reference data paths)
2. Aerodynamicist produces **Aero Proposal** (airfoil, planform, dimensions, performance predictions)
3. Main thread spawns **structural engineer** with the Aero Proposal as input
4. Structural engineer produces **Structural Review** (feasibility, weight, modifications needed)

### Round 2 (if modifications needed)
5. Main thread spawns **aerodynamicist** with Structural Review
6. Aerodynamicist produces **Revised Proposal** (adjusted or justified pushback)
7. Main thread spawns **structural engineer** with Revised Proposal
8. Structural engineer produces **Final Review** (accept or remaining conflicts)

### Round 3 (max, if still not converged)
9. Same pattern. If no convergence after 3 rounds, main thread presents both positions to the user for a tiebreaker decision.

### Convergence
Both agents agree on the final specifications. The main thread writes a `DESIGN_CONSENSUS.md` file to the component/assembly folder.

## Design Consensus Document

Written to the component or assembly folder after agents converge. Required before any drawing can be created.

```
DESIGN_CONSENSUS.md
- Aero Requirements: airfoil, planform shape, Re at each station, performance targets
- Structural Requirements: mass budget, wall thickness, spar specs, print strategy
- Trade-offs: what aero wanted vs what structural constrained, and the compromise
- Agreed Specifications: final dimensions, materials, weights (both agents signed off)
- Round History: number of rounds, what changed each round
```

## Enforcement

### When triggered
Any design work on a component or assembly in these categories:
- `cad/components/empennage/` (H-stab, V-stab, elevator, rudder)
- `cad/components/wing/` (panels, ribs, skins, spars)
- `cad/components/fuselage/` (pod shell, fairings)
- `cad/assemblies/empennage/`
- `cad/assemblies/wing/`

### Not triggered
- `cad/components/hardware/` (screws, rods, off-shelf parts)
- `cad/components/propulsion/` (motor, ESC, prop — unless designing a fairing)
- Electronics, wiring, servo brackets

### CLAUDE.md rule (advisory)
Mandatory text in CLAUDE.md stating that aerodynamic components MUST go through the aero+structural feedback loop before any 2D drawing is created.

### Hook (enforcement)
A PreToolUse hook that checks when a drawing file (`*_drawing.dxf` or `*_drawing.py`) is being created in an aerodynamic component folder. If no `DESIGN_CONSENSUS.md` exists in that folder, the hook warns that the aero+structural review hasn't been completed.

## Integration with Existing Workflow

The agent team inserts between step 1 (folder creation) and step 2 (2D drawing) of the existing CAD workflow:

1. Create folder structure
2. **NEW: Run aero+structural feedback loop → DESIGN_CONSENSUS.md**
3. Create 2D technical drawing (from consensus, not from guesswork)
4. User approves drawing
5. Build 3D model
6. Take 4 renders
7. Write COMPONENT_INFO.md / ASSEMBLY_INFO.md

## Files to Create/Modify

| File | Action |
|------|--------|
| `.claude/agents/aerodynamicist.md` | Create — agent definition |
| `.claude/agents/structural-engineer.md` | Create — agent definition |
| `CLAUDE.md` | Update — add mandatory aero+structural rule |
| `.claude/settings.json` | Update — add consensus-check hook |
| `cad/CAD_FRAMEWORK.md` | Update — add DESIGN_CONSENSUS.md as required file |

## Success Criteria

- Both agents produce substantive, numbered engineering analysis (not vague prose)
- Structural agent catches infeasible designs (too thin, too heavy, can't print)
- Aerodynamicist agent justifies every choice with Re numbers and polar data
- The consensus document contains enough detail to create a correct 2D drawing
- The H-stab redesign produces a result the user approves on the first or second attempt
