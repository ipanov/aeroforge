# Reference and Research Index

This page indexes the reference and research materials available in the repository.

---

## Repository Archive

The `docs/reference/` directory contains:

| Category | Description |
|----------|-------------|
| **Catalogs** | Component catalogs (servos, motors, batteries, hardware) |
| **Competition benchmarks** | Specs and performance data from competitive aircraft |
| **Tooling studies** | Analysis of manufacturing techniques and their tradeoffs |
| **Historical research** | Design notes, iteration history, decision logs |
| **Vendor references** | Off-the-shelf component datasheets and supplier information |

---

## RAG Knowledge Base

The [RAG Knowledge Base](RAG-Knowledge-Base) provides fast semantic search over pre-fetched competitive intelligence. Agents query it during design decisions.

---

## External Tools Documentation

| Tool | Purpose | Documentation |
|------|---------|---------------|
| Build123d | Parametric 3D CAD (headless Python) | [build123d docs](https://build123d.readthedocs.io/) |
| SU2 | CFD solver (Euler, RANS) | [su2code.github.io](https://su2code.github.io/) |
| FreeCAD | FEM analysis (CalculiX) | [freecad.org](https://www.freecad.org/) |
| Gmsh | Mesh generation | [gmsh.info](https://gmsh.info/) |
| OrcaSlicer | FDM slicer | [github.com/SoftFever/OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) |
| NeuralFoil | Neural network airfoil polars | [github.com/peterdsharpe/NeuralFoil](https://github.com/peterdsharpe/NeuralFoil) |
| ChromaDB | Vector database for RAG | [docs.trychroma.com](https://docs.trychroma.com/) |

---

## Specifications

The single source of truth for design parameters is `docs/specifications.md` in each project. All references to design parameters are tracked in `docs/spec_registry.md` for automatic propagation when values change.
