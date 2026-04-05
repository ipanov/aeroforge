# AeroForge Overview

AeroForge is a generic design framework for heavier-than-air flying objects.
It combines:

- upstream reasoning for ambiguous project decisions
- deterministic workflow enforcement once those decisions are captured
- visible status tracking across rounds, nodes, and deliverables
- living BOM and procurement synchronization as the design evolves

## Boundary Rule

Upstream reasoning decides project-specific facts such as:

- aircraft or body class
- project scope
- tooling
- manufacturing technique
- material strategy
- production strategy
- output artifacts

Deterministic code is responsible for:

- persisting the profile
- enforcing step order
- enforcing dependencies
- tracking the active step
- surfacing workflow state through the monitor stack
- synchronizing deliverables, BOM state, and procurement state
- running final assembled-object validation

## System View

```mermaid
flowchart LR
    A[User brief] --> B[Wizard]
    B --> C[Project profile]
    C --> D[Workflow engine]
    D --> E[Step guards]
    D --> F[HTML Dashboard]
    D --> G[Monitor server]
    D --> H[n8n visual dashboard]
    D --> I[Deliverables]
    I --> J[Living BOM and procurement]
    D --> K[CFD/FEA validation pipeline]
    K --> L[Aero Test Report + heatmaps]
    L --> M[Feedback to orchestrator]
```

## Design Intent

The framework is meant to cover a range of outcomes, including:

- paper aircraft and fold-based outputs
- RC aircraft with mixed custom and off-the-shelf parts
- outsourced or factory-produced subassemblies
- component-only or assembly-only design requests

The current AIR4 sailplane remains a useful example, but it is not the
framework itself.

## CFD/FEA Validation Pipeline

The VALIDATION phase uses a dedicated analysis pipeline:

```mermaid
flowchart TD
    A[Assembled STEP] --> B[Gmsh mesh generation]
    B --> C[SU2 solver]
    C -->|real-time| D[cfd_monitor.py]
    D --> E[Progress to n8n + dashboard]
    C -->|after run| F[cfd_results.py]
    F --> G[Aero Test Report]
    F --> H[cfd_visualization.py]
    H --> I[3D Cp/Cf heatmaps]
    G --> J[cfd_feedback.py]
    J --> K{Orchestrator: pass?}
    K -->|Yes| L[RELEASE]
    K -->|No| M[Cascade to affected nodes]
```

Key separation of concerns:

- **cfd_results.py**: Parses SU2 output, extracts Cp/Cf, computes stability
  derivatives (CL_alpha, CM_alpha, neutral point), drag breakdown
  (pressure/friction/induced), generates industry-standard Aero Test Report
- **cfd_monitor.py**: Polls SU2 residuals during execution, reports progress
  and ETA, detects divergence early
- **cfd_visualization.py**: ParaView 3D heatmaps for Cp and Cf (4 views each),
  matplotlib fallback when ParaView unavailable
- **cfd_feedback.py**: Structured output the orchestrator consumes to decide
  cascade targets — contains only aerodynamic data, no hierarchy knowledge

## n8n Visual Dashboard

n8n provides two workflows:

1. **AeroForge Dashboard**: Visual sticky-note canvas rebuilt on every state
   change — shows project phases, component hierarchy, active step, validation
2. **AeroForge Events**: Webhook receivers for telemetry events

n8n is mandatory. The engine hard-stops if n8n is unreachable.

## BOM and Procurement

The Bill of Materials and procurement data are per-project:

- `projects/{slug}/aeroforge.bom.yaml` — machine-readable BOM
- `projects/{slug}/docs/BOM.md` — human-readable markdown view

Framework code in `src/core/bom.py`, `bom_sync.py`, `procurement.py` is
generic and shared. Project-specific data (suppliers, costs, quantities)
lives in the project directory.
