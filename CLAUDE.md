# AeroForge - AI-Enabled RC Sailplane Design System

## Project Mission

Design a **groundbreaking 3D-printed RC sailplane** using AI-driven complexity
to exceed commercial kits in aerodynamic performance at a fraction of the cost.

**Motto: "Why make it simple when it can be complex - for the same price?"**

The 3D printer has zero marginal cost for complexity. A topology-optimized lattice
rib costs the same as a flat plate. We exploit this to produce aerodynamic surfaces
that commercial kits cannot economically manufacture.

See `docs/philosophy.md` for the full design philosophy.
See `docs/specifications.md` for locked-in dimensions and weight budget.

## Architecture

### Two-Engine System
- **Build123d** (Python, headless) - ALL 3D modeling, parametric design, assemblies
- **FreeCAD 1.0+** (headless via FreeCADCmd) - FEM analysis (CalculiX), CFD (OpenFOAM)
- Both share the OpenCascade (OCCT) kernel. STEP files interchange losslessly.
- FreeCAD path: C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0

### Dependency Graph System
- **NetworkX DAG** for component dependency tracking
- **Pydantic models** for validated component specifications
- **Topological sort** for update ordering
- **CRUD operations** on component hierarchy
- **Validation hooks** at every deterministic step
- When a component changes -> all dependents update automatically

### Component Model
```
Component (base class)
├── OffShelfComponent  (servos, motors, screws - fixed dims from datasheets)
├── CustomComponent    (designed parts - parametric, from Text2CAD)
└── Assembly           (components + sub-assemblies + constraints)
```

Every component has: mass, CG, inertia tensor, local coordinate system, bounding box.
Even the smallest screw is a component.

## Sailplane Quick Reference

| Parameter | Value |
|-----------|-------|
| Wingspan | 2.1m |
| Panels | 6 (3 per half, ~350mm each) |
| Root chord | 200mm |
| Tip chord | 110mm |
| Airfoil | AG24 (root) → AG03 (tip), blended continuously |
| Main spar | 10mm carbon tube (off-shelf) |
| Rear spar | 5mm spruce strip |
| Target AUW | 700-850g |
| Battery | 3S 1300mAh racing LiPo (~115g, FIXED) |
| Receiver | Turnigy 9X V2 8ch (18g, FIXED) |
| Controls | Full-house + crow braking, 6 servos |
| Printer | Bambu A1 / P1S (256x256x256mm bed) |

## Key Design Principles

1. **Maximize printed complexity** - blended airfoils at every rib, geodetic lattice,
   topology-optimized mounts, integrated gap seals
2. **Minimize hand labor** - carbon tube slides through holes, spruce glues into slots,
   no cutting carbon cloth or cap strips
3. **AI optimizes everything** - airfoils, twist, planform, control sizing, Tx programming
4. **Every detail matters** - squeeze 2% from every surface. Printer doesn't charge extra.
5. **Cheap materials** - complex geometry is free, keep material cost under $60

## Tech Stack

### Core CAD
- **Build123d 0.10+** - Python parametric CAD (headless)
- **NetworkX** - DAG management
- **Pydantic** - Spec validation

### Analysis
- **FreeCAD FEM** - Structural (CalculiX)
- **CfdOF/OpenFOAM** - CFD aerodynamics
- **xfoil** - 2D airfoil polars

### Manufacturing
- **OrcaSlicer** CLI for headless slicing
- **3MF** preferred export format
- See `docs/slicer_pipeline.md`

### MCP Servers
- **context7** - Library docs
- **freecad-mcp** (neka-nat) - FreeCAD RPC
- **ocp-viewer-mcp** (dmilad) - Visual feedback

## Project Structure

```
aeroforge/
├── src/
│   ├── core/                   # Component framework & DAG
│   │   ├── component.py        # Base Component, OffShelf, Custom classes
│   │   ├── assembly.py         # Assembly with constraints
│   │   ├── dag.py              # Dependency graph (NetworkX)
│   │   └── validation.py       # Validation hooks
│   ├── cad/                    # Build123d parametric models
│   │   ├── airfoils/           # Airfoil generators (AG, NACA)
│   │   ├── wing/               # Wing panels, ribs, skins
│   │   ├── fuselage/           # Pod, boom
│   │   ├── tail/               # H-stab, V-stab
│   │   └── hardware/           # Mounts, horns, hinges
│   ├── analysis/               # FreeCAD headless wrappers
│   └── text2cad/               # AI workflow pipeline
├── components/                 # Off-the-shelf specs
├── docs/                       # Design documentation
│   ├── philosophy.md           # Design philosophy & competitive advantage
│   ├── specifications.md       # Locked-in specs, weight budget, dimensions
│   └── slicer_pipeline.md      # Print pipeline (OrcaSlicer, Bambu LAN)
├── exports/                    # STL, STEP, 3MF for printing
└── tests/                      # Validation tests
```

## Coding Conventions

- Python 3.10+
- Type hints required
- Docstrings for all modules/classes
- All dimensions in mm, weights in grams
- Pydantic models for all component specs
- NetworkX for all dependency relationships

## Git Workflow

- `main` - stable, tested designs
- Feature branches for changes
- PR reviews via pr-review-toolkit plugin
