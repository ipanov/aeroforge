# AeroForge

**AI-Enabled 3D-Printed RC Sailplane Design System**

## What Is This?

AeroForge uses AI-driven **Text2CAD** workflow to design a high-performance RC sailplane from natural language descriptions. Every component -- from wing spars down to individual screws -- is a parametric 3D model with automatic dependency propagation.

The goal: design a 3D-printable sailplane that beats commercial kits (F5J, Insight, Bowser) in cost and manufacturing speed.

## Architecture

```
Text2CAD (natural language)
    │
    ▼
Build123d (Python parametric CAD, headless)
    │
    ├── Component DAG (NetworkX dependency graph)
    ├── Validation hooks (every change validated)
    ├── STEP/STL/3MF export
    │
    ▼
FreeCAD 1.0+ (headless analysis only)
    ├── FEM - structural (CalculiX)
    ├── CFD - aerodynamics (OpenFOAM)
    └── Mass/CG/inertia properties
```

## Quick Start

```bash
git clone https://github.com/ipanov/aeroforge.git
cd aeroforge

# Install dependencies
pip install -r requirements.txt

# Verify Build123d
python -c "import build123d; print(build123d.__version__)"

# Run tests
pytest
```

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| CAD Engine | Build123d 0.10+ | Parametric 3D modeling (Python) |
| Dependency Graph | NetworkX | Component change propagation |
| Validation | Pydantic | Spec validation with hooks |
| Structural Analysis | FreeCAD FEM + CalculiX | Stress, torsion, buckling |
| Aero Analysis | OpenFOAM / xfoil | CFD, airfoil polars |
| 3D Printing | Bambu A1 / P1S | STL/3MF export |
| AI Workflow | Text2CAD | Natural language to CAD |

## Target Specifications

- **Wingspan**: 1.5m - 2m (modular panels for print bed)
- **Weight**: < 800g (goal: 500-600g with LW-PLA)
- **Controls**: Full-house (ailerons, flaps, elevator, rudder)
- **Flight modes**: Launch, Cruise, Speed, Thermal, Crow landing
- **Radio**: Turnigy 9X compatible

## Project Status

Early development -- building the parametric component framework and dependency graph system.

## License

MIT License
