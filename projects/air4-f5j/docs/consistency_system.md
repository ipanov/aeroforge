# Specification Consistency System

## How It Works

AeroForge uses a three-layer system to ensure design parameters never go out of sync
across documentation, code, and 3D models.

### Architecture Overview

```mermaid
flowchart TD
    USER[User says: 'Change wingtip chord to 120mm'] --> SPEC

    SPEC[/"src/core/specs.py<br/>SAILPLANE object<br/>(Single Source of Truth)"/]

    SPEC --> CODE["All Python Code<br/>imports SAILPLANE<br/>(auto-updated)"]
    SPEC --> TESTS["pytest test_spec_consistency.py<br/>(catches doc drift)"]
    SPEC --> DOCS["Update docs manually<br/>guided by spec_registry.md"]

    TESTS -->|PASS| COMMIT[git commit + push]
    TESTS -->|FAIL| FIX["Fix inconsistent files<br/>(test tells you which)"]
    FIX --> TESTS

    CODE --> DAG["DAG rebuilds dependent<br/>components automatically"]
    DAG --> EXPORT["Updated STL/STEP/3MF"]

    style SPEC fill:#ff6,stroke:#333,stroke-width:3px
    style TESTS fill:#6f6,stroke:#333,stroke-width:2px
    style FIX fill:#f66,stroke:#333,stroke-width:2px
```

### The Three Layers

```mermaid
graph LR
    subgraph "Layer 1: Executable Spec"
        A["src/core/specs.py<br/>SAILPLANE = SailplaneSpec()"]
    end

    subgraph "Layer 2: Consistency Tests"
        B["test_spec_consistency.py<br/>24 tests: spec vs docs vs code"]
    end

    subgraph "Layer 3: Registry"
        C["docs/spec_registry.md<br/>Parameter → file map"]
    end

    A -->|"values compared by"| B
    C -->|"guides manual updates"| A
    B -->|"catches missed updates"| C
```

## Layer 1: Executable Single Source of Truth

**File: `src/core/specs.py`**

All design parameters live in one Python object:

```python
from src.core.specs import SAILPLANE

# Access any parameter
wingspan = SAILPLANE.wing.wingspan           # 2100.0 mm
root_chord = SAILPLANE.wing.root_chord       # 200.0 mm
battery_weight = SAILPLANE.battery.weight    # 115.0 g

# Computed properties update automatically
wing_area = SAILPLANE.wing.wing_area_dm2     # computed from span + chord
wing_loading = SAILPLANE.wing_loading_at_auw # computed from area + weight
reynolds = SAILPLANE.wing.reynolds_at(0.5)   # computed from chord + velocity
```

### Spec Hierarchy

```mermaid
classDiagram
    class SailplaneSpec {
        +name: str
        +wing: WingSpec
        +spar: SparSpec
        +fuselage: FuselageSpec
        +empennage: EmpennageSpec
        +battery: BatterySpec
        +receiver: ReceiverSpec
        +controls: ControlSpec
        +printing: PrintSpec
        +electronics_weight: float
        +wing_loading_at_auw: dict
        +summary(): str
    }

    class WingSpec {
        +wingspan: 2100mm
        +root_chord: 200mm
        +tip_chord: 110mm
        +panels_per_half: 3
        +airfoil_root: AG24
        +airfoil_tip: AG03
        +main_spar_od: 8mm
        +half_span: float
        +taper_ratio: float
        +wing_area_dm2: float
        +aspect_ratio: float
        +panel_span: float
        +chord_at(fraction): float
        +reynolds_at(fraction): float
    }

    class SparSpec {
        +main_od: 8mm
        +main_id: 6mm
        +rear_width: 5mm
        +rear_height: 3mm
        +boom_od: 12mm
        +boom_length: 650mm
    }

    class BatterySpec {
        +cells: 3
        +capacity_mah: 1300
        +weight: 115g
        +dimensions: 72x35x23mm
        FIXED - owner inventory
    }

    class ReceiverSpec {
        +channels: 8
        +weight: 18g
        +dimensions: 52x35x15mm
        FIXED - owner inventory
    }

    class ControlSpec {
        +servo_count: 6
        +servo_weight: 9g
        +flight_modes: list
    }

    SailplaneSpec --> WingSpec
    SailplaneSpec --> SparSpec
    SailplaneSpec --> BatterySpec
    SailplaneSpec --> ReceiverSpec
    SailplaneSpec --> ControlSpec
    SailplaneSpec --> FuselageSpec
    SailplaneSpec --> EmpennageSpec
    SailplaneSpec --> PrintSpec
```

### Why Python, Not Markdown?

| Approach | Markdown spec file | Python spec object |
|----------|-------------------|-------------------|
| Can code import values from it? | No - must duplicate | **Yes - `from specs import SAILPLANE`** |
| Computed properties auto-update? | No - manual recalc | **Yes - `wing_area` recomputes** |
| Type-checked? | No | **Yes - Pydantic validates** |
| Testable? | Barely | **Yes - full pytest** |
| Human-readable? | Yes | **Yes - `SAILPLANE.summary()`** |

## Layer 2: Consistency Tests

**File: `tests/test_spec_consistency.py`**

24 automated tests in 4 categories:

### Test Categories

```mermaid
graph TD
    subgraph "TestSpecVsDocumentation (10 tests)"
        D1[wingspan in specifications.md]
        D2[root chord in specifications.md]
        D3[tip chord in specifications.md]
        D4[panel count in specifications.md]
        D5[airfoils in specifications.md]
        D6[battery weight in specifications.md]
        D7[receiver weight in specifications.md]
        D8[spar size in specifications.md]
        D9[servo count in specifications.md]
        D10[wingspan in specifications.md]
    end

    subgraph "TestSpecVsCLAUDEmd (6 tests)"
        C1[root chord]
        C2[tip chord]
        C3[airfoil root]
        C4[airfoil tip]
        C5[battery capacity]
        C6[panel count]
    end

    subgraph "TestSpecVsCode (2 tests)"
        K1[print bed size matches validation.py]
        K2[panel fits on print bed]
    end

    subgraph "TestSpecInternalConsistency (6 tests)"
        I1[taper ratio reasonable]
        I2[aspect ratio reasonable]
        I3[spar fits in airfoil]
        I4[electronics weight budget]
        I5[wing loading reasonable]
        I6[Reynolds number adequate]
    end
```

### What Happens When Tests Fail

Example: Someone changes `SAILPLANE.wing.wingspan = 2200` but forgets to update CLAUDE.md:

```
FAILED test_wingspan_in_claude_md
  AssertionError: CLAUDE.md doesn't contain wingspan 2200mm
```

The test tells you EXACTLY which file is wrong and what value is missing.

### Real Example: Spar Size Catch

When we first set the main spar to 10mm OD, this test caught it:

```
FAILED test_spar_fits_in_airfoil
  AssertionError: Spar 10.0mm doesn't fit in 9.2mm airfoil height at tip
```

The AG03 airfoil at 110mm tip chord is only 9.2mm thick. A 10mm tube physically
cannot fit inside it. The test caught this BEFORE any 3D model was generated.
We corrected to 8mm.

## Layer 3: Spec Registry

**File: `docs/spec_registry.md`**

A human-readable map of where each parameter appears. Used as a checklist
when updating, but NOT the primary guardrail (tests are).

```
Wingspan → specs.py, CLAUDE.md, specifications.md, slicer_pipeline.md, wing code, tests
Chord → specs.py, CLAUDE.md, specifications.md, wing code, tests
Airfoil → specs.py, CLAUDE.md, specifications.md, airfoil code, tests
...
```

## Change Workflow

### When User Changes a Parameter

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant SpecsPy as specs.py
    participant Tests as pytest
    participant Docs as Documentation
    participant Code as CAD Code
    participant DAG as Component DAG

    User->>Claude: "Change tip chord to 120mm"

    Claude->>SpecsPy: Update SAILPLANE.wing.tip_chord = 120
    Note over SpecsPy: Computed properties auto-update:<br/>taper_ratio, wing_area, aspect_ratio,<br/>reynolds numbers, wing_loading

    Claude->>Tests: Run test_spec_consistency.py
    Tests-->>Claude: FAIL: specifications.md says 110mm
    Tests-->>Claude: FAIL: CLAUDE.md says 110mm

    Claude->>Docs: Update specifications.md: 110→120
    Claude->>Docs: Update CLAUDE.md: 110→120

    Claude->>Tests: Re-run tests
    Tests-->>Claude: PASS (24/24)

    Claude->>Code: Rebuild wing rib generators
    Code->>DAG: Mark dependents dirty
    DAG->>DAG: Topological rebuild cascade

    Claude->>User: "Updated tip chord 110→120mm.<br/>Files changed: specs.py, CLAUDE.md, specifications.md<br/>Wing area: 32.5→33.6 dm²<br/>Wing loading at 750g: 23.1→22.3 g/dm²<br/>Spar still fits: 10.1mm internal height at tip<br/>All 24 consistency tests pass."
```

### Full Update Cascade

```mermaid
flowchart LR
    CHANGE["Parameter Change"] --> SPEC["specs.py<br/>(update value)"]
    SPEC --> COMPUTED["Recompute:<br/>wing area<br/>wing loading<br/>Reynolds<br/>aspect ratio"]
    SPEC --> DOCS["Update docs:<br/>specifications.md<br/>CLAUDE.md<br/>slicer_pipeline.md"]
    SPEC --> CODE["Code auto-gets<br/>new value via import"]
    CODE --> DAG["DAG marks<br/>dependents dirty"]
    DAG --> REBUILD["Rebuild affected<br/>3D components"]
    REBUILD --> EXPORT["Re-export<br/>STL/STEP/3MF"]
    DOCS --> TESTS["Run consistency<br/>tests"]
    TESTS -->|all pass| COMMIT["Commit + Push"]
```

## Running the Tests

```bash
# Run only consistency tests (fast, < 1 second)
pytest tests/test_spec_consistency.py -v

# Run all tests including core framework
pytest tests/ -v

# Print current spec summary
python -c "from src.core.specs import SAILPLANE; print(SAILPLANE.summary())"
```

## Adding New Parameters

When adding a new design parameter:

1. Add the field to the appropriate spec class in `specs.py`
2. Add a consistency test in `test_spec_consistency.py`
3. Add the parameter to the docs where relevant
4. Add an entry to `spec_registry.md`
5. Run all tests to confirm

## Adding New Files That Reference Parameters

When creating a new file that uses any design parameter:

1. Import from `specs.py`: `from src.core.specs import SAILPLANE`
2. Use `SAILPLANE.wing.wingspan` (not hardcoded `2100`)
3. Add the file to `spec_registry.md` under each parameter it uses
4. Add a consistency test if the file contains hardcoded reference values
