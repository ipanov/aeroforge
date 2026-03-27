# AeroForge

**AI-Enabled 3D-Printed RC Sailplane Design System**

## Overview

AeroForge is an ambitious project to design high-performance RC sailplanes using:
- **Parametric CAD** via Python (Build123d)
- **Dependency graph** for automatic update propagation
- **CFD/FEM analysis** for aerodynamic and structural optimization
- **AI-driven Text2Cut/Sketch2Cut workflow** for rapid design iteration

## Goals

1. Design a 3D-printable RC sailplane rivaling commercial kits
2. Develop a reusable Text2Cut pipeline for future aircraft designs
3. Document everything for the community (public repo)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/ipanov/aeroforge.git
cd aeroforge

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Tech Stack

| Component | Tool |
|-----------|------|
| Parametric CAD | Build123d |
| FEM Analysis | FreeCAD + CalculiX |
| CFD | OpenFOAM |
| Target Printer | Bambu A1 / P1S |

## Project Status

🚧 **Early Development** - Project structure and toolchain setup

## License

MIT License - Open source for the RC community
