# AeroForge Workflow

> Compatibility note: the canonical framework workflow document now lives at
> [`docs/framework/workflow.md`](framework/workflow.md).
>
> This page remains as a stable entry point and summary for existing links.

## Purpose

This document summarizes the initialization boundary, workflow boundary, and
domain model boundary for AeroForge.

For the maintained framework version, use the canonical page in
`docs/framework/workflow.md`.

## Boundary Rule

### LLM / User Decisions

These are upstream decisions. They are not hardcoded by the workflow engine:

- what the aircraft or aerodynamic body is
- whether the request is for a full aircraft, an assembly, or a component
- tooling
- manufacturing technique
- material strategy
- production strategy
- output artifact strategy
- which deliverables matter for each node after drill-down

The user can provide these directly.
If the user does not provide enough, the LLM guides the user through a wizard,
proposes options, explains pros and cons, and records the selected outcome.

### Deterministic Engine Responsibilities

Once those decisions are captured, deterministic code is responsible for:

- persisting the project profile
- building the workflow profile
- enforcing step order
- enforcing dependency order
- exposing the active step
- blocking artifact work under the wrong active step
- generating dashboard and monitor outputs
- broadcasting status to `n8n`
- recording step deliverables
- synchronizing the living BOM after deliverable or procurement changes
- running final validation on the assembled top object

## Initialization Flow

### Step 1: User Design Brief

The user states the intent:

- "design a racing sailplane"
- "design a paraglider wing"
- "design a paper airplane"
- "design a full-size wing"
- "design a drone interceptor"

### Step 2: Guided Wizard

The wizard captures or helps decide:

- aircraft type or body type
- project scope
- top object
- location context for procurement and local quoting
- tooling
- manufacturing technique
- material strategy
- production strategy
- output artifact strategy

If the user already specifies a preference, the wizard accepts it and presents
tradeoffs.

If the user does not specify enough, the LLM proposes viable options.

### Step 3: Persist Decisions

The selected outcome is written to [`aeroforge.yaml`](/d:/Repos/aeroforge/aeroforge.yaml).

That file becomes the deterministic contract for execution.

## Core Domain Model

### Project

The top-level container for:

- user brief
- chosen domain strategy
- workflow profile
- current round
- current top object

### Tooling

Tooling describes the physical or industrial path available for production.

Examples:

- in-house FDM printer
- laser cutter
- CNC workflow
- outsourced factory
- hand-crafted fabrication

### Manufacturing Technique

Manufacturing technique describes how the design is intended to be produced.

Examples:

- thin-wall shell printing
- laser-cut rib and spar build
- stitched fabric panels
- molded composite layup
- folded paper construction

### Material Strategy

Material strategy records the intended material family or families.

Examples:

- paper
- LW-PLA / PLA / TPU
- balsa / plywood / carbon
- fabric / reinforcements
- composite laminates

### Production Strategy

Production strategy describes who or what produces the design output.

Examples:

- in-house build
- hybrid in-house plus procured parts
- outsourced factory production

### Deliverable

A deliverable is the artifact expected from a step or node.

Examples:

- DXF drawing
- PNG drawing
- STEP model
- STL mesh
- 3MF mesh
- fold instructions
- crease pattern
- stitching plan
- cut pattern
- mold tooling data
- validation report
- BOM update
- procurement shortlist

### Component

Every lowest single part is a component.

Two main classes matter:

- custom component
- off-the-shelf component

### Assembly

An assembly is any object made of components and/or lower-level assemblies.

The top assembly follows the same rules as all other assemblies. It only differs
in that no higher assembly exists above it.

## Top-Down and Drill-Down

The standing design method is:

1. define the main requirement
2. define the top object
3. create the project profile
4. create or refine parent geometry
5. run top-level iterative rounds
6. drill down into assemblies
7. drill down into components
8. rebuild dependent outputs
9. run full top-object validation

If final validation moves the design materially, the process can return to a
higher level and open another round.

## Bottom-Up Refresh

After drill-down work, updates move upward again:

1. component updates
2. assembly refresh
3. top-object refresh
4. validation rerun

The dependency graph is still useful, but strict staged execution reduces drift
and makes the dependency logic easier to reason about.

## Validation Rule

Final synthetic wind tunnel and structural strength calculations are run on the
assembled top object, not on isolated parts.

Local part checks can still exist for fit, geometry, or manufacturability, but
the true aerodynamic and structural convergence loop is a full-object activity.

## Step Sequence

Every tracked node follows the same deterministic stage order:

`REQUIREMENTS -> RESEARCH -> AERO_PROPOSAL -> STRUCTURAL_REVIEW -> AERO_RESPONSE -> CONSENSUS -> DRAWING_2D -> MODEL_3D -> MESH -> VALIDATION -> RELEASE`

The dashboard and workflow monitor always show which step is active.

For Mermaid workflow charts and the maintained explanation, use:

- [Framework workflow and iteration model](framework/workflow.md)
- [Monitoring, hooks, and n8n](framework/monitoring-hooks-and-n8n.md)

## Deliverables by Node

Deliverables are not universal. They can differ after drill-down.

Examples:

- printed custom part:
  - `DRAWING_2D`: DXF + PNG
  - `MODEL_3D`: STEP
  - `MESH`: STL + 3MF
- paper aircraft:
  - fold instructions
  - crease pattern
  - three-view or sheet layout
- paraglider-style wing:
  - panel patterns
  - stitching plans
  - reinforcement schedule
- molded part:
  - mold tooling data
  - drawings
  - inspection references

## Living BOM and Procurement

The bill of materials is a living project artifact.

It must update when:

- a custom part geometry changes
- a deliverable is regenerated
- a manufacturing technique changes
- a material strategy changes
- an off-the-shelf component specification changes
- a procurement shortlist or quote changes

Once the user or LLM has supplied location, provider preferences, component
classification, and production strategy, the synchronization itself is
deterministic:

- off-the-shelf components refresh procurement candidates
- quoted or outsourced parts refresh quote placeholders
- custom printed parts refresh estimated cost from filament and machine time
- the markdown BOM and machine-readable BOM state are updated together

## Best-Practice Summary

The intended architecture is:

- domain-driven at the profile and workflow level
- strict and explicit at the state-machine level
- extensible through data files instead of code branching for every case
- object-oriented at the component/assembly/domain boundary
- conservative about where deterministic code is allowed to decide things
