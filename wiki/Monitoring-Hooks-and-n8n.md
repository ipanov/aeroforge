# Monitoring, Hooks, and n8n

Canonical source:
[docs/framework/monitoring-hooks-and-n8n.md](https://github.com/ipanov/aeroforge/blob/master/docs/framework/monitoring-hooks-and-n8n.md)

```mermaid
flowchart LR
    A[Workflow engine] --> B[workflow_state.json]
    B --> C[Dashboard]
    B --> D[Monitor server]
    B --> E[Guard hooks]
    D --> F[n8n visibility layer]
```

`n8n` is always started alongside the workflow monitor server. The persisted
workflow state remains the authoritative source of truth. If n8n becomes
unreachable, the engine continues without it.
