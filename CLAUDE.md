# AeroForge - AI-Enabled RC Sailplane Design System

## Project Mission

Design a **groundbreaking 3D-printed RC sailplane** that rivals commercial kits (F5J, Insight, Bowser) in performance while being:
- **Cheaper** - leverage 3D printing with consumer printers (Bambu A1/P1S)
- **Faster to manufacture** - parametric design optimized for printability
- **AI-designed** - Text2CAD workflow: natural language to parametric 3D model

## Architecture

### Two-Engine System
- **Build123d** (Python, headless) - ALL 3D modeling, parametric design, assemblies
- **FreeCAD 1.0+** (headless via FreeCADCmd) - FEM analysis (CalculiX), CFD (OpenFOAM), visualization
- Both share the OpenCascade (OCCT) kernel. STEP files are the lossless interchange format.

### Dependency Graph System
- **NetworkX DAG** for component dependency tracking
- **Pydantic models** for validated component specifications
- **Topological sort** for update ordering
- **CRUD operations** on component hierarchy
- **Validation hooks** at every deterministic step
- When a component changes -> all dependents update automatically

### Component Model
```
Component (base class - Pydantic model)
├── OffShelfComponent  (servos, motors, screws - from datasheets, fixed dims)
├── CustomComponent    (designed parts - parametric, from Text2CAD)
└── Assembly           (components + sub-assemblies + constraints)
```

Every component has: mass, center of gravity, inertia tensor, local coordinate system, bounding box.
Even the smallest screw is a component.

### Design Philosophy
- **Top-down design** (concept first) but **bottom-up construction** (build small parts first)
- Assembly hierarchy: components -> sub-assemblies -> assemblies -> top assembly
- Same workflow for all assembly levels

## Tech Stack

### Core CAD
- **Build123d 0.10+** - Python-native parametric CAD (headless, VS Code with OCP Viewer)
- **NetworkX** - Dependency graph (DAG) management
- **Pydantic** - Component spec validation

### Analysis (via FreeCAD 1.0.2 headless)
- **FreeCAD FEM** - Structural analysis (CalculiX solver)
- **CfdOF/OpenFOAM** - CFD for aerodynamics
- **xfoil** - 2D airfoil analysis (quick iteration)
- FreeCAD path: C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0

### Manufacturing
- **Target printers**: Bambu A1, Bambu P1S
- **Materials**: PLA, LW-PLA (lightweight), TPU (flexible parts)
- **Export**: STL, 3MF for slicing

### MCP Servers
- **context7** - Library documentation (Build123d, FreeCAD API)
- **freecad-mcp** (neka-nat) - FreeCAD RPC for headless FEM/CFD [to install]
- **ocp-viewer-mcp** (dmilad) - Visual feedback from Build123d [to install]

### Radio/Components
- **Transmitter**: Turnigy 9X
- **Servos**: Micro digital servos (9g class)
- **Flight modes**: Launch, Cruise, Speed, Thermal, Landing (crow)
- **Controls**: Full-house (ailerons, flaps, elevator, rudder)

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
│   │   ├── airfoils/           # Airfoil generators (NACA, AG series)
│   │   ├── wing/               # Wing sections, spars, skins
│   │   ├── fuselage/           # Pod, boom, nose
│   │   ├── tail/               # V-tail, T-tail, conventional
│   │   └── hardware/           # Servo mounts, control horns, hinges
│   ├── analysis/               # FreeCAD headless wrappers
│   │   ├── fem.py              # FEM setup & results
│   │   ├── cfd.py              # CFD setup & results
│   │   └── xfoil.py            # 2D airfoil analysis
│   └── text2cad/               # AI workflow pipeline
├── components/                 # Off-the-shelf component specs (YAML)
│   ├── servos/
│   ├── motors/
│   ├── electronics/
│   └── hardware/               # Screws, rods, bearings
├── docs/                       # Design documentation
├── exports/                    # STL, STEP, 3MF files for printing
└── tests/                      # Validation tests
```

## Design Constraints

### Target Specifications
- **Wingspan**: 1.5m - 2m (modular for printing)
- **Weight**: < 800g (goal: 500-600g with LW-PLA)
- **Wing loading**: 20-30 g/dm²
- **Airfoil**: RG-15 or AG series (thermal efficiency)
- **Control surfaces**: Full-house (ailerons, flaps, elevator, rudder)
- **Flight modes**: Launch, Cruise, Speed, Thermal, Crow landing

## Coding Conventions

- Python 3.10+
- Type hints required
- Docstrings for all modules/classes
- Parametric values as constants at module top
- All dimensions in mm, weights in grams
- Pydantic models for all component specs
- NetworkX for all dependency relationships

## Git Workflow

- `main` - stable, tested designs
- Feature branches for changes
- GitHub Issues for task tracking
- PR reviews via pr-review-toolkit plugin
