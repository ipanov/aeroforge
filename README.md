# AeroForge

**AI-Enabled 3D-Printed RC Sailplane Design System**

> *"Why make it simple when it can be complex - for the same price?"*

---

## What Is This?

AeroForge is an AI-driven parametric design system for RC sailplanes. It exploits
the fact that **3D printers have zero marginal cost for complexity** - a topology-optimized
lattice rib costs the same filament as a flat plate, but performs dramatically better.

The system takes natural language design intent (**Text2CAD**) and produces
fully parametric, constraint-based 3D models ready for printing on consumer
printers (Bambu A1/P1S).

## The Goal

Design a 3D-printed RC sailplane that **exceeds commercial kits** (Insight F5J,
Introduction, Bowser) in aerodynamic performance - at a fraction of the cost.

Commercial kits are locked into 10-15 year old designs constrained by manufacturing:
2-3 airfoil stations, simple planforms, uniform internal structure. AeroForge has
**no such constraints** - every rib can be a unique airfoil, every surface can be
optimally shaped, every internal structure can be topology-optimized.

## Current Specifications

| Parameter | Value |
|-----------|-------|
| Wingspan | 2.56m |
| Wing panels | 10 (5 per half, 256mm each - exact bed fit) |
| Root chord | 210mm |
| Tip chord | 115mm |
| Airfoil | AG24 (root) → AG09 (mid) → AG03 (tip), blended continuously |
| Main spar | 8mm pultruded carbon tube |
| Rear spar | 5x3mm spruce strip |
| Controls | Full-house (ailerons, flaps, elevator, rudder) + crow braking |
| Target AUW | 700-850g |
| Target cost | Under $150 total (filament + carbon + electronics) |

## Architecture

```
Text2CAD (natural language design)
    │
    ▼
Build123d (Python parametric CAD, headless)
    │
    ├── Dependency DAG (NetworkX) ── auto-propagates changes
    ├── Pydantic validation ── enforces constraints
    ├── Consistency tests ── spec vs docs vs code
    │
    ├── STEP export ──► FreeCAD (headless FEM/CFD analysis)
    └── 3MF export ──► OrcaSlicer CLI ──► Bambu printer
```

### Key Innovation: Specification Consistency System

Every design parameter has a **single source of truth** in Python (`src/core/specs.py`).
24 automated tests verify that documentation, code, and specs stay in sync.
When a parameter changes, the dependency graph propagates updates to all affected
components automatically.

See [docs/consistency_system.md](docs/consistency_system.md) for the full system
architecture with Mermaid diagrams.

## Project Structure

```
aeroforge/
├── src/
│   ├── core/               # Component framework, DAG, specs, validation
│   ├── cad/                # Build123d parametric models
│   │   ├── airfoils/       # AG/NACA airfoil generators
│   │   ├── wing/           # Wing panels, ribs, skins
│   │   ├── fuselage/       # Pod, boom
│   │   └── tail/           # Empennage
│   ├── analysis/           # FreeCAD headless wrappers (FEM, CFD)
│   └── text2cad/           # AI workflow pipeline
├── components/             # Off-the-shelf component specs
├── docs/
│   ├── philosophy.md       # Design philosophy
│   ├── specifications.md   # Complete spec reference
│   ├── consistency_system.md # How spec sync works (with diagrams)
│   ├── spec_registry.md    # Parameter → file map
│   └── slicer_pipeline.md  # 3D print automation
├── exports/                # STL, STEP, 3MF output
└── tests/                  # 72 tests (framework + consistency)
```

## Quick Start

```bash
git clone https://github.com/ipanov/aeroforge.git
cd aeroforge

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from src.core.specs import SAILPLANE; print(SAILPLANE.summary())"

# Run all tests
pytest
```

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| CAD Engine | [Build123d](https://github.com/gumyr/build123d) | Parametric 3D modeling |
| Dependency Graph | [NetworkX](https://networkx.org/) | Change propagation |
| Validation | [Pydantic](https://docs.pydantic.dev/) | Spec validation |
| FEM Analysis | FreeCAD + CalculiX | Structural analysis |
| CFD Analysis | OpenFOAM | Aerodynamics |
| Airfoil Analysis | xfoil | 2D polars |
| Slicer | OrcaSlicer (CLI) | Automated slicing |
| Target Printer | Bambu A1 / P1S | 256x256x256mm bed |

## Design Philosophy

A 3D printer doesn't care about complexity. This project exploits that:

- **Every rib is unique** - continuously blended airfoil profiles (not 2-3 stations like commercial kits)
- **Topology-optimized structure** - geodetic lattice, variable density, computed lightening patterns
- **AI-optimized everything** - airfoils, twist, planform, control sizing, transmitter programming
- **Cheap materials, complex geometry** - filament + carbon tubes + spruce. Under $60 in materials.

See [docs/philosophy.md](docs/philosophy.md) for the full rationale.

## Status

Early development - core framework built, specifications locked, building components.

## License

All rights reserved. License terms will be determined before public release.
The Text2CAD workflow and parametric design system may be subject to
specific licensing restrictions for commercial use.
