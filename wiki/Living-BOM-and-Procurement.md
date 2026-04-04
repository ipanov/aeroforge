# Living BOM and Procurement

The Bill of Materials (BOM) is a **living artifact** -- it updates automatically whenever geometry, materials, manufacturing assumptions, or off-the-shelf specifications change. The `deliverable_bom_sync` hook keeps it in sync.

---

## BOM Update Flow

```mermaid
flowchart TD
    subgraph Triggers["What triggers a BOM update"]
        T1["📐 Deliverable created\nSTEP, 3MF, DXF"]
        T2["📦 Off-shelf spec changed\nmass, supplier, cost"]
        T3["🔧 Manufacturing change\nmaterial, technique"]
    end

    subgraph Sync["deliverable_bom_sync hook"]
        S1["Detect event type"]
        S2{"Custom or\noff-shelf?"}
        S3["Refresh manufacturing\ncost estimate"]
        S4["Refresh supplier\nshortlist"]
        S5["Update BOM entry"]
    end

    subgraph BOM["Living BOM"]
        B1["Component list\nwith mass, cost, source"]
        B2["Total mass budget"]
        B3["Total cost estimate"]
        B4["Procurement checklist"]
    end

    T1 & T2 & T3 --> S1
    S1 --> S2
    S2 -->|"Custom"| S3
    S2 -->|"Off-shelf"| S4
    S3 --> S5
    S4 --> S5
    S5 --> B1

    style Triggers fill:#1d3557,color:#fff
    style Sync fill:#264653,color:#fff
    style BOM fill:#2d6a4f,color:#fff
    style S2 fill:#6a4c93,color:#fff
    style S3 fill:#457b9d,color:#fff
    style S4 fill:#457b9d,color:#fff
    style S5 fill:#2a9d8f,color:#fff
```

---

## BOM Entry Structure

Each BOM line item includes:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Component name | "Wing_Panel_P1" |
| `type` | `custom` or `off_shelf` | `custom` |
| `mass_g` | Mass in grams | 28.5 |
| `material` | Material specification | "LW-PLA" |
| `quantity` | How many needed | 2 (left + right) |
| `source` | Where to get it | "3D printed" or "supplier" |
| `cost_estimate` | Estimated cost | 2.50 EUR |
| `supplier` | Supplier name (off-shelf) | "HobbyKing" |
| `link` | Purchase link (off-shelf) | URL |
| `lead_time` | Shipping estimate | "2-3 weeks" |

---

## Procurement Strategy

The procurement hierarchy:

1. **Local suppliers** (Bulgaria) -- fastest delivery, highest priority
2. **Temu** -- good prices, reasonable shipping
3. **AliExpress** -- last resort (3-month customs delays possible)

For custom printed parts, the BOM tracks filament usage and print time estimates from the slicer provider.

---

## Automatic Sync

The `deliverable_bom_sync` PostToolUse hook fires on every deliverable creation or modification. It:

1. Detects which component/assembly was updated
2. Reads the component's mass, material, and manufacturing info
3. Updates or creates the BOM entry
4. Recalculates totals (mass budget, cost estimate)

This is fully automatic -- no manual BOM maintenance needed.
