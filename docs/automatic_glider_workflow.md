# Automatic Glider Workflow

This document is now a project-specific derivative of the generic framework
workflow described in `docs/workflow.md`.

Date: 2026-04-02

Purpose: define the standing AeroForge workflow so aircraft development does not drift into ad hoc part-by-part work.

This workflow applies to `Iva_Aeroforge` now and to future aircraft created with the framework.

## Core Principle

The process is iterative, top-down first, then bottom-up from approved parent geometry.

We do not start final component modeling from isolated part ideas.
We first establish the whole aircraft.
Then we refine the major assemblies.
Then we derive the lower-level parts.
Then we return upward with analysis results and repeat.

## Governing Philosophy

- complexity is allowed when it buys aerodynamic, structural, packaging, or manufacturing advantage
- 3D printing is not a reason to simplify the aircraft into crude geometry
- the aircraft should be both aerodynamically credible and visually coherent
- benchmark research is mandatory before major geometry changes
- whole-aircraft geometry owns the major stations and proportions
- subassemblies inherit from the aircraft, not the other way around

## Mandatory Loop Order

### Phase 1: Top-Level Aircraft Definition

1. collect requirements, constraints, and benchmark references
2. define whole-aircraft datum, span target, fuselage length, wing station, tail station, and control architecture
3. produce aircraft parent drawings
4. run sequential aero and structural review rounds on the whole aircraft
5. freeze only the stations and relationships that survive those rounds

Outputs:
- aircraft `ASSEMBLY_INFO.md`
- aircraft parent 2D drawing
- aircraft aero and structural round files
- aircraft `DESIGN_CONSENSUS.md`

### Phase 2: Major Assembly Refinement

Once the aircraft-level geometry is credible, drill down into:
- wing assembly
- fuselage assembly
- empennage assemblies

For each major assembly:
1. inherit aircraft stations and interfaces
2. refine the local 2D parent drawing
3. run aero and structural rounds for that assembly
4. update the assembly consensus
5. only then derive components

Outputs:
- assembly parent drawings
- assembly research rounds
- assembly consensus files

### Phase 3: Bottom-Up Component Derivation

Only after aircraft and major-assembly drawings are approved:
1. derive sections, panels, fairings, ribs, and hardware interfaces
2. model 3D geometry
3. export meshes and printable data
4. validate assembly fit, mass, CG, routing, and collisions

## Analysis Sequence

The framework should run analysis in this order:

1. benchmark lookup and requirements review
2. airfoil and section-law investigation
3. whole-aircraft aerodynamic investigation
4. whole-aircraft structural quick sizing
5. wing aerodynamic refinement
6. wing structural refinement
7. fuselage aerodynamic refinement
8. fuselage structural refinement
9. empennage aerodynamic refinement
10. empennage structural refinement
11. stability, controllability, and CG closure
12. 3D model generation
13. CFD / synthetic wind tunnel / FEM / torsion / flutter loops
14. redesign of only the parameters that move the result materially

## Benchmark Rule

Before any major geometry proposal is accepted, the proposing agent must use:

1. one rules or class source
2. two to five benchmark aircraft sources
3. one explicit note explaining why the proposal is not just a copy

High-impact decisions that require lookup:
- span changes
- aspect ratio changes
- tail configuration changes
- H-stab and fin placement changes
- wingtip concept changes
- fuselage OML changes
- airfoil family changes
- control-surface architecture changes
- structural concepts that materially affect stiffness or mass

Minor drafting cleanup does not require browsing.

## Off-The-Shelf Component Rule

Off-the-shelf components are included in parent drawings as engineering envelopes for:
- packaging
- CG accounting
- routing
- cooling
- collision checks

The project does not own manufacturing drawings for vendor parts at this stage.

## Approval Gates

### Gate A: Aircraft 2D Approval

Before 3D modeling starts:
- aircraft parent drawing must be approved
- major geometry relationships must be accepted
- open strategic questions must be reduced to manageable local refinements

### Gate B: Assembly 2D Approval

Before detailed component modeling starts:
- wing parent drawing approved
- fuselage parent drawing approved
- empennage parent drawing approved

### Gate C: 3D / Analysis Approval

Before CFD / FEM / virtual wind tunnel loops:
- integrated 3D assembly exists
- mass and CG table exists
- exported geometry is watertight enough for the selected solver

## Design Intent For Iva

For the current aircraft:
- the H-stab quality bar is the current geometric benchmark
- the whole aircraft remains the controlling parent object
- wing and fuselage are still under refinement
- the process remains top-down first, bottom-up second
- once the 2D aircraft, wing, fuselage, and tail drawings are approved, 3D modeling begins

## Standing Reminder

When in doubt:
- go up one level in the hierarchy
- verify against benchmark sources
- update the parent geometry first
- then propagate the change downward
