# AeroForge - AI-Enabled RC Sailplane Design System

## Project Mission

Design a **groundbreaking 3D-printed RC sailplane** that rivals commercial kits (F5J, Insight, Bowser) in performance while being:
- **Cheaper** - leverage 3D printing with consumer printers (Bambu A1/P1S)
- **Faster to manufacture** - parametric design optimized for printability
- **AI-designed** - cutting-edge Text2Cut/Sketch2Cut workflow

## Core Architecture

### Dependency Graph System
- **Parametric components** with automatic update propagation
- **CRUD operations** on component hierarchy
- **Validation hooks** at every deterministic step
- **Topological sort** for update ordering

### Component Model
```
Component (base class)
├── OffShelfComponent  (servos, motors, screws - from datasheets)
├── CustomComponent    (designed parts - from Text2Cut)
└── Assembly           (components + sub-assemblies + constraints)
```

When a component changes → all dependents update automatically.

## Tech Stack

### Core CAD
- **Build123d** - Python-native parametric CAD (VS Code native)
- **FreeCAD 1.0+** - FEM analysis, visualization, technical drawings

### Analysis
- **OpenFOAM** - CFD for aerodynamics
- **FreeCAD FEM** - Structural analysis (CalculiX)
- **xfoil** - 2D airfoil analysis

### Manufacturing
- **Target printers**: Bambu A1, Bambu P1S
- **Materials**: PLA, LW-PLA (lightweight), TPU (flexible parts)
- **Export**: STL, 3MF for slicing

### Radio/Components
- **Transmitter**: Turnigy 9X
- **Servos**: Micro digital servos (9g class)
- **Flight modes**: Launch, Cruise, Speed, Thermal, Landing (crow)

## Project Structure

```
clearskies/
├── src/
│   ├── cad/                    # Build123d parametric models
│   │   ├── airfoils/           # Airfoil generators (NACA, AG series)
│   │   ├── wing/               # Wing sections, spars, skins
│   │   ├── fuselage/           # Pod, boom, nose
│   │   ├── tail/               # V-tail, T-tail, conventional
│   │   └── components/         # Servo mounts, control horns, etc.
│   ├── cfd/                    # OpenFOAM cases
│   ├── fem/                    # Structural analysis
│   └── text2cut/               # AI workflow pipeline
├── components/                 # Off-the-shelf component specs
│   ├── servos/                 # Dimensions, weights, torque
│   ├── motors/                 # Motors, props
│   └── electronics/            # ESC, receiver, battery
├── docs/                       # Design documentation
├── exports/                    # STL, STEP, 3MF files for printing
└── tests/                      # Validation tests
```

## Design Constraints

### Target Specifications (Initial)
- **Wingspan**: 1.5m - 2m (modular for printing)
- **Weight**: < 800g (goal: 500-600g with LW-PLA)
- **Wing loading**: 20-30 g/dm²
- **Airfoil**: RG-15 or AG series (thermal efficiency)
- **Control surfaces**: Full-house (ailerons, flaps, elevator, rudder)
- **Flight modes**: Launch, Cruise, Speed, Thermal, Crow landing

### Component Inventory (User's Equipment)
- Turnigy 9X transmitter
- Micro servos (9g class)
- Various motors and ESCs (to be catalogued)

## AI Workflow Philosophy

This project explores **Text2Cut** - using natural language descriptions to generate parametric 3D models:

1. **Describe** → Natural language design intent
2. **Generate** → Build123d Python code with constraints
3. **Validate** → CFD/FEM analysis automatically
4. **Iterate** → AI suggests improvements
5. **Export** → Print-ready meshes

## Coding Conventions

- Python 3.11+
- Type hints required
- Docstrings for all modules/classes
- Parametric values as constants at module top
- All dimensions in mm, weights in grams

## Git Workflow

- `main` - stable, tested designs
- `develop` - work in progress
- Feature branches for major changes
- GitHub Issues for task tracking
