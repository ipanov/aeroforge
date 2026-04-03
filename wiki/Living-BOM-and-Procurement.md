# Living BOM and Procurement

Canonical source:
[docs/framework/bom-and-procurement.md](https://github.com/ipanov/aeroforge/blob/master/docs/framework/bom-and-procurement.md)

The BOM is a living artifact. It updates when geometry, materials,
manufacturing assumptions, or off-the-shelf specifications change.

```mermaid
flowchart LR
    A[Deliverable or spec change] --> B{Custom or off-the-shelf?}
    B -- Custom --> C[Refresh manufacturing cost]
    B -- Off-the-shelf --> D[Refresh supplier shortlist]
    C --> E[Update BOM]
    D --> E
```
