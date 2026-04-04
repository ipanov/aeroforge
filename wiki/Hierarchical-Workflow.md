# Hierarchical Workflow

AeroForge uses a **hierarchical node tree** where each component and assembly has its own design cycle. The workflow operates at two levels: top-level project phases and per-node design steps.

---

## Project Phases

Six sequential phases govern the overall project lifecycle:

```mermaid
flowchart LR
    R["📋 REQUIREMENTS"] --> RE["🔍 RESEARCH"]
    RE --> D["✏️ DESIGN"]
    D --> I["🔧 IMPLEMENTATION"]
    I --> V["✅ VALIDATION"]
    V --> RL["📦 RELEASE"]

    style R fill:#2d6a4f,color:#fff
    style RE fill:#1b4332,color:#fff
    style D fill:#1d3557,color:#fff
    style I fill:#264653,color:#fff
    style V fill:#6a4c93,color:#fff
    style RL fill:#9d4edd,color:#fff
```

| Phase | What happens | Gate to next |
|-------|-------------|--------------|
| **REQUIREMENTS** | Capture mission brief, constraints, performance targets | User confirms brief |
| **RESEARCH** | RAG population, web search, competitive analysis, reference study | Sufficient domain knowledge gathered |
| **DESIGN** | Top-down drill: aero/structural agent cycles for every node | All nodes have approved 2D drawings |
| **IMPLEMENTATION** | Bottom-up build: 3D models from leaves to root | All nodes have OUTPUT deliverables |
| **VALIDATION** | CFD (SU2) + FEA (CalculiX) on assembled aircraft | All convergence criteria pass |
| **RELEASE** | Package deliverables, BOM, documentation | User signs off |

### Critical Gate: DESIGN to IMPLEMENTATION

**Every node in the tree must have an approved 2D drawing before IMPLEMENTATION begins.** This is the drawing-first gate. The engine checks this with `StateManager.check_design_phase_complete()`.

---

## Per-Node Design Cycle

Every component and assembly follows the same 7-step cycle:

```mermaid
flowchart LR
    AP["🔵 AERO_PROPOSAL\nAerodynamicist"] --> SR["🟠 STRUCTURAL_REVIEW\nStructural Engineer"]
    SR --> AR["🔵 AERO_RESPONSE\nAerodynamicist"]
    AR --> CO["📝 CONSENSUS\nDESIGN_CONSENSUS.md"]
    CO --> D2["📐 DRAWING_2D\nDXF + PNG"]
    D2 --> M3["🔧 MODEL_3D\nBuild123d STEP"]
    M3 --> OU["📦 OUTPUT\nFormat per provider"]

    style AP fill:#4a90d9,color:#fff
    style SR fill:#e76f51,color:#fff
    style AR fill:#4a90d9,color:#fff
    style CO fill:#2d6a4f,color:#fff
    style D2 fill:#1d3557,color:#fff
    style M3 fill:#264653,color:#fff
    style OU fill:#6a4c93,color:#fff
```

| Step | Agent / Actor | Output | Notes |
|------|--------------|--------|-------|
| **AERO_PROPOSAL** | Aerodynamicist | Aero Proposal document | Must compare at least 3 design options |
| **STRUCTURAL_REVIEW** | Structural Engineer | Structural Review document | Mass, strength, manufacturability check |
| **AERO_RESPONSE** | Aerodynamicist | Revised proposal (if needed) | Addresses structural concerns |
| **CONSENSUS** | Both agents agree | `DESIGN_CONSENSUS.md` | Written to the node's folder |
| **DRAWING_2D** | LLM + ezdxf | DXF + PNG | User must approve before MODEL_3D |
| **MODEL_3D** | LLM + Build123d | STEP file | Dimensions must match drawing exactly |
| **OUTPUT** | Manufacturing provider | 3MF, STL, or other | Format determined by provider config |

### OUTPUT, Not MESH

The final step is called **OUTPUT** because the deliverable format depends on the manufacturing provider. For FDM 3D printing, OUTPUT is `STEP -> STL -> geodesic ribs -> 3MF`. For manual construction, OUTPUT might be laser-cut DXF templates. For CNC, it might be G-code. The provider decides.

---

## Top-Down Design, Bottom-Up Implementation

```mermaid
flowchart TB
    subgraph Design["✏️ DESIGN Phase: Top-Down"]
        direction TB
        AC["✈️ Aircraft"] --> W["Wing Assembly"]
        AC --> E["Empennage Assembly"]
        AC --> F["Fuselage Assembly"]
        W --> WP1["Wing Panel P1"]
        W --> WP2["Wing Panel P2"]
        E --> HS["H-Stab Assembly"]
        E --> EL["Elevator"]
    end

    subgraph Impl["🔧 IMPLEMENTATION Phase: Bottom-Up"]
        direction BT
        WP1b["Wing Panel P1"] --> Wb["Wing Assembly"]
        WP2b["Wing Panel P2"] --> Wb
        HSb["H-Stab Assembly"] --> Eb["Empennage Assembly"]
        ELb["Elevator"] --> Eb
        Wb --> ACb["✈️ Aircraft"]
        Eb --> ACb
        Fb["Fuselage Assembly"] --> ACb
    end

    Design --> Impl

    style Design fill:#1d3557,color:#fff
    style Impl fill:#2d6a4f,color:#fff
    style AC fill:#4a90d9,color:#fff
    style W fill:#457b9d,color:#fff
    style E fill:#457b9d,color:#fff
    style F fill:#457b9d,color:#fff
    style WP1 fill:#2a9d8f,color:#fff
    style WP2 fill:#2a9d8f,color:#fff
    style HS fill:#2a9d8f,color:#fff
    style EL fill:#2a9d8f,color:#fff
    style ACb fill:#4a90d9,color:#fff
    style Wb fill:#457b9d,color:#fff
    style Eb fill:#457b9d,color:#fff
    style Fb fill:#457b9d,color:#fff
    style WP1b fill:#2a9d8f,color:#fff
    style WP2b fill:#2a9d8f,color:#fff
    style HSb fill:#2a9d8f,color:#fff
    style ELb fill:#2a9d8f,color:#fff
```

- **Design phase:** Start at the aircraft level, drill down through assemblies to leaf components. Each node runs its 7-step design cycle. The aerodynamicist and structural engineer work at the appropriate level of abstraction.
- **Implementation phase:** Build 3D models from leaves first (components), then assemble into parent assemblies, bottom-up. `StateManager.get_implementation_order()` returns the correct build sequence.

---

## Drawing Approval Gate

The DRAWING_2D step has a **mandatory user approval gate**:

```mermaid
flowchart TD
    CO["✅ CONSENSUS achieved"] --> D2["📐 Create 2D Drawing\nDXF + PNG"]
    D2 --> VIS["🔍 Visual Validation\nFull view + zoomed details"]
    VIS --> SHOW["👤 Show to User"]
    SHOW --> Q{"User approves?"}
    Q -->|"✅ Yes"| M3["🔧 Proceed to MODEL_3D"]
    Q -->|"❌ No"| FB["📝 User gives feedback"]
    FB --> BACK["🔄 Back to AERO_PROPOSAL\nor fix drawing"]
    BACK --> D2

    style CO fill:#2d6a4f,color:#fff
    style D2 fill:#1d3557,color:#fff
    style VIS fill:#264653,color:#fff
    style SHOW fill:#6a4c93,color:#fff
    style Q fill:#9d4edd,color:#fff
    style M3 fill:#2d6a4f,color:#fff
    style FB fill:#e76f51,color:#fff
    style BACK fill:#e76f51,color:#fff
```

No 3D modeling begins until the user approves the 2D drawing. This prevents expensive geometry rework.

---

## Validation Cascade

After IMPLEMENTATION, the VALIDATION phase runs CFD and FEA on the assembled aircraft. If issues are found, the LLM decides which nodes need redesign:

```mermaid
flowchart TD
    V["✅ VALIDATION\nCFD + FEA"] --> R{"Results pass\nall criteria?"}
    R -->|"✅ All pass"| REL["📦 RELEASE"]
    R -->|"❌ Issues found"| AN["🤖 LLM analyzes results"]
    AN --> SEL["Select nodes to redesign"]
    SEL --> INV["Invalidate selected nodes"]
    INV --> D["🔄 Back to DESIGN\nfor affected nodes only"]
    D --> I["🔧 Re-implement\naffected subtree"]
    I --> V

    style V fill:#6a4c93,color:#fff
    style R fill:#9d4edd,color:#fff
    style REL fill:#2d6a4f,color:#fff
    style AN fill:#1d3557,color:#fff
    style SEL fill:#264653,color:#fff
    style INV fill:#e76f51,color:#fff
    style D fill:#1d3557,color:#fff
    style I fill:#264653,color:#fff
```

### Convergence Criteria

The iteration loop terminates when ALL criteria are satisfied:

| Criterion | Target | Verified by |
|-----------|--------|-------------|
| L/D at design CL | Type-specific (e.g., >= 15:1 for sailplane) | SU2 CFD |
| Interference drag | < 5% of total CD | SU2 CFD |
| Static margin | 5-15% MAC | SU2 CFD + calculations |
| Control authority | Surfaces achieve required moments | SU2 CFD |
| Structural safety factor | >= 1.5 all components | FreeCAD FEA |
| Flutter margin | >= 1.2 x VNE | FreeCAD modal + SU2 aero |
| All-up weight | Within target range | Mass tracking |
| Assembly collisions | Zero intersections | Collision check |

---

## Iteration Rules

1. **Max 3 agent rounds per node.** If the aerodynamicist and structural engineer cannot agree in 3 rounds, the user decides.
2. **User can reject any deliverable.** Rejection sends the node back with feedback. The LLM decides how far back to go (to AERO_PROPOSAL for fundamental changes, or just fix the drawing).
3. **Invalidation is surgical.** `StateManager.invalidate_node()` resets one node. `StateManager.invalidate_subtree()` resets a node and all descendants. The LLM chooses the minimal scope.
4. **Step status tracking.** Each step has a status: `pending`, `running`, `done`, `failed`, `skipped`. The engine prevents skipping steps or working out of order.

---

## Node Types and Design Cycle Applicability

| Node Type | Design Cycle | Description |
|-----------|-------------|-------------|
| **component** | Full 7-step cycle | A single physical piece (wing panel, elevator, fuselage section) |
| **assembly** | Full 7-step cycle | Two or more components joined (wing assembly, H-stab, the whole aircraft) |
| **off_shelf** | None (skipped) | Servo, battery, carbon rod, screw -- dimensions from datasheets |

Off-shelf nodes have no design cycle. Their specs are captured from datasheets and they participate in assemblies as fixed-dimension items.
