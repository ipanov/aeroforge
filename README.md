# AeroForge

**AI-guided heavier-than-air vehicle design system with tracked iterative workflows.**

AeroForge is not tied to one aircraft class or one fabrication path. The system
starts from a design brief, captures project decisions such as aircraft type,
tooling, manufacturing technique, material strategy, and output artifacts, then
executes a strict staged workflow with visible progress.

The current example project is `AIR4`, the `Iva_Aeroforge` thermal electric
sailplane. The framework is intended to remain broader than that one vehicle.

## What AeroForge Does

- Accepts a user design brief for a heavier-than-air flying object
- Guides initialization through a wizard that records:
  - aircraft type decided by user/LLM
  - tooling
  - manufacturing technique
  - material strategy
  - production strategy
  - expected output artifacts
- Builds a project-specific workflow profile from those decisions
- Tracks every sub-assembly through a strict step sequence
- Exposes the currently running step in:
  - persisted workflow state
  - HTML dashboard
  - local monitor server
  - optional `n8n` workflow runtime
- Runs final synthetic wind-tunnel and strength validation on the assembled top object

## Core Rule

Non-deterministic decisions belong upstream:

- aircraft type
- tooling
- manufacturing technique
- material strategy
- production strategy
- output package

Those are not hardcoded by the deterministic engine. They are chosen by the
user and/or an LLM reasoning step, written into [`aeroforge.yaml`](/d:/Repos/aeroforge/aeroforge.yaml),
and then enforced by code.

Deterministic code is responsible for:

- workflow sequencing
- dependency ordering
- artifact-to-step enforcement
- state persistence
- dashboard generation
- monitor serving
- status broadcasting to `n8n`
- BOM and procurement synchronization after deliverable changes

## Workflow

The standing workflow is top-down first, then bottom-up:

1. Capture the main requirement for the aircraft or aerodynamic body.
2. Decide the project profile through the initialization wizard.
3. Build the top object and parent geometry first.
4. Drill down into assemblies and components only after parent approval.
5. Rebuild dependent outputs in a disciplined sequence.
6. Run final CFD / synthetic wind tunnel / structural validation on the full assembled object.
7. If convergence fails, open another top-level round and propagate the affected updates downward again.

Every tracked node follows the same strict staged sequence:

`REQUIREMENTS -> RESEARCH -> AERO_PROPOSAL -> STRUCTURAL_REVIEW -> AERO_RESPONSE -> CONSENSUS -> DRAWING_2D -> MODEL_3D -> MESH -> VALIDATION -> RELEASE`

## Current Monitoring Stack

The workflow stack now includes:

- `.claude/workflow_state.json` as the source of execution truth
- `exports/workflow_dashboard.html` as the graphical status board
- `python -m src.orchestrator.cli serve` as a local monitor server
- optional `n8n` integration for the graphical workflow runtime
- a workflow guard hook that blocks drawing/model/mesh edits when the wrong step is active

The dashboard highlights the active step and shows the dependency graph and
project initialization choices.

The same monitoring layer now treats the BOM as a live artifact, not a static
report.

## Project Profile

The tracked project profile lives in [`aeroforge.yaml`](/d:/Repos/aeroforge/aeroforge.yaml).

That file is now the place where AeroForge records:

- the current project family and round
- the top object
- the aircraft type chosen upstream
- the location context used for procurement and local quoting
- tooling and available production resources
- manufacturing and material strategy
- production mode, including outsourced/factory production
- provider preferences for procurement agents
- output artifacts, such as print files, technical drawings, stitching plans, or tooling data
- the workflow profile and sub-assembly dependency structure

## Initialization Wizard

Use the initializer to guide project setup:

```bash
python -m src.orchestrator.cli init --name "AIR4" --prompt "Thermal electric sailplane"
```

The wizard shows data-driven options for:

- procurement location and provider preferences
- tooling
- manufacturing technique
- material strategy
- production mode
- output artifacts

It does not auto-decide them in code. It records the chosen decisions.

## Living BOM

The BOM is synchronized as the project changes:

- off-the-shelf updates refresh provider candidates and quote paths
- custom-part deliverables refresh estimated manufacturing cost
- markdown and machine-readable BOM views are kept together

## Starting the Workflow

Preferred path:

```bash
python -m src.orchestrator.cli start-profile --profile aeroforge.yaml --name "Iva Aeroforge F5J"
```

Useful commands:

```bash
python -m src.orchestrator.cli status
python -m src.orchestrator.cli step --sub wing --step REQUIREMENTS --action start --agent aerodynamicist
python -m src.orchestrator.cli dashboard
python -m src.orchestrator.cli rename-round --sub wing --label R5
python -m src.orchestrator.cli start-iteration --sub wing --label R5
python -m src.orchestrator.cli serve --launch-n8n
```

## Launching n8n and the Monitor

This repo now includes a small Node runtime wrapper for `n8n`.

```bash
npm install
python -m src.orchestrator.cli serve --launch-n8n
```

Or on PowerShell:

```powershell
.\scripts\launch_workflow_stack.ps1 -InstallNodeDeps
```

The local monitor server serves:

- `/dashboard`
- `/api/state`
- `/api/status`
- `/api/settings`

## Design Concepts

### Component

Every lowest single part is a component.

Two important categories exist:

- custom component
- off-the-shelf component

Off-the-shelf components are still modeled as components, even when the vendor
item contains more than one physical internal part. They are treated as one
procured object in the digital assembly.

### Assembly

An assembly is any object made by combining components and/or lower-level
assemblies. The top assembly follows the same rules as every other assembly.
The only difference is that nothing sits above it.

### Tooling

Tooling is a project decision captured at initialization. It is not hardcoded
into the framework. A project can target:

- in-house fabrication
- hybrid in-house plus procured subsystems
- outsourced or factory production

### Manufacturing Technique

Manufacturing technique describes how the output is meant to be produced. That
can mean printing, laser-cut rib construction, folded sheet work, molded
composites, stitched fabric plans, or factory-ready tooling data.

### Output Artifact

The design output is not always a print file. Depending on the project, it may
be:

- 3D models
- technical drawings
- print files
- molds
- cut patterns
- stitching plans
- factory data packages

## Current Example

The current `AIR4` profile is a thermal electric sailplane with:

- hybrid in-house + procured production
- FDM-based custom geometry for selected parts
- procured propulsion and electronics
- final full-assembly validation at the aircraft level

The current next round is `R5`.

## Status

The orchestrator, dashboard, profile-driven initialization, and hook-based
workflow enforcement are being put in place so the aircraft development process
stays visible, accountable, and extensible.
