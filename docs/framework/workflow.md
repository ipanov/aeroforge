# Workflow and Iteration Model

The standing AeroForge method is:

1. capture the main requirement
2. initialize the project profile
3. define the top object and parent geometry
4. iterate top-down before drilling into child nodes
5. refresh bottom-up after local changes
6. validate the assembled top object
7. open another round if convergence fails

## Stage Sequence

```mermaid
flowchart LR
    A[REQUIREMENTS] --> B[RESEARCH]
    B --> C[AERO_PROPOSAL]
    C --> D[STRUCTURAL_REVIEW]
    D --> E[AERO_RESPONSE]
    E --> F[CONSENSUS]
    F --> G[DRAWING_2D]
    G --> H[MODEL_3D]
    H --> I[MESH]
    I --> J[VALIDATION]
    J --> K[RELEASE]
```

Every tracked node follows this deterministic stage order. The active stage is
surfaced through the monitor stack and enforced through hooks.

## Top-Down, Drill-Down, Bottom-Up

```mermaid
flowchart TD
    A[Main requirement] --> B[Top object]
    B --> C[Top-level rounds]
    C --> D[Assembly drill-down]
    D --> E[Component drill-down]
    E --> F[Deliverables refreshed]
    F --> G[Assembly refresh]
    G --> H[Top-object refresh]
    H --> I[Full validation]
    I --> J{Converged?}
    J -- No --> C
    J -- Yes --> K[Release package]
```

## Validation Rule

Final aerodynamic and structural convergence is a **full-object activity**.

Local component checks still matter for:

- fit
- manufacturability
- packaging
- mass contribution
- interface integrity

But synthetic wind-tunnel and structural convergence belong to the assembled
top object, not isolated parts.

## Internal Non-Aerodynamic Components

Some components affect:

- mass
- inertia
- center of gravity
- packaging
- stiffness
- routing

without materially affecting the external aerodynamic shape. Those components
can skip aerodynamic treatment while still participating in structural,
packaging, and BOM/procurement flows.
