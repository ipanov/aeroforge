# Monitoring, Hooks, and n8n

The workflow must remain visible and accountable while it runs.

## Monitoring Stack

- `.claude/workflow_state.json` as the state source of truth
- `exports/workflow_dashboard.html` as the visual dashboard
- the local monitor server for status APIs and HTML serving
- workflow guard hooks for stage enforcement
- `n8n` visibility layer for event handling and runtime chart (always started)

## Live Monitoring Story

```mermaid
flowchart LR
    A[Workflow engine] --> B[workflow_state.json]
    B --> C[Dashboard]
    B --> D[Monitor server]
    B --> E[Guard hooks]
    D --> F[API consumers]
    D --> G[n8n visibility layer]
    G --> H[Runtime chart and event flow]
```

## Guardrail Rule

The visible chart is not enough on its own. The system also needs:

- step guards that block the wrong type of work at the wrong stage
- recorded deliverables for each node/stage
- consistent round labels
- deterministic sequencing after upstream decisions are captured

## n8n Position

`n8n` is always started alongside the workflow monitor server. It provides
the runtime visibility chart showing which step is executing at any moment.
If n8n becomes unreachable, the engine continues — the persisted workflow
state remains the authoritative source of truth, not n8n.
