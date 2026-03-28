# AeroForge Workflow Redesign Spec

**Date:** 2026-03-28
**Status:** Approved
**Context:** Full project reset after Incidents 001 & 002 (hollow shell wing, traditional balsa-kit ribs instead of 3D-print-optimized geodesic structure, no visual validation)

## Problem Statement

The Text2CAD workflow produced garbage geometry that looked nothing like what was described in console output. Root causes:
1. No visual feedback loop (OCP screenshot MCP tool broken, Claude built blind)
2. Wrong design paradigm (1960s balsa-kit ribs instead of 3D-print geodesic lattice)
3. No enforced quality gates (gates documented but never checked)
4. FreeCAD was headless (no user visibility into analysis)
5. Build123d Boolean operations fragile for complex internal structure

## Solution Architecture

### Three-Tool Pipeline

```
BUILD123d (Python, headless)
  ├─ AG airfoil NURBS profiles (mathematically exact)
  ├─ Chord, twist, washout distributions at every span station
  ├─ Airfoil blending (AG24 → AG09 → AG03, continuous)
  └─ Export: STEP curves, DAT coordinate files
       │
       ▼
FREECAD (GUI via MCP/RPC — user sees everything in real-time)
  ├─ Import airfoil profiles from Build123d
  ├─ Loft wing surface between profiles
  ├─ Generate vase-mode-compatible internal structure (slot technique)
  ├─ Create spar tunnel, control surface hinge lines
  ├─ Create fuselage pod (elliptical cross-section, shoulder-wing)
  ├─ Create empennage (H-stab + V-stab)
  ├─ FEM analysis (CalculiX) — stress, deflection, safety factors
  ├─ Full assembly with CG calculation
  └─ Export: STEP (lossless), STL (for slicer)
       │
       ▼
ORCASLICER (CLI or GUI)
  ├─ Import STL from FreeCAD
  ├─ Vase mode / spiral outer contour slicing
  ├─ LW-PLA settings (230°C, 0.45 flow multiplier, 0 retractions)
  ├─ Validate printability (overhangs, bridges, print time)
  └─ Export: G-code → Bambu A1/P1S printer
```

### FreeCAD MCP Integration (from ClearSkies)

- **Addon:** FreeCADMCP (already installed in FreeCAD 1.0 Mod directory)
- **MCP server:** `uvx --python 3.12 freecad-mcp` (configured in `.mcp.json`)
- **Protocol:** XML-RPC on port 9875
- **Key tools:** `execute_code` (full Python API), `get_view` (screenshots), `create_object`, `edit_object`
- **User experience:** FreeCAD window is open, user sees every operation as it happens
- **Visual validation:** Claude uses `get_view` to capture screenshots after each operation

### Wing Construction: Vase-Mode Slot Technique

Based on research of 3DLabPrint, Eclipson, Planeprint RISE, and open-source projects:

**What it is:**
- The wing is a SINGLE continuous surface (not shell + separate ribs)
- Thin vertical slots cut into the surface create internal rib walls
- When sliced in vase mode (spiralize outer contour), the slicer traces one continuous path
- The nozzle follows: outer skin → down through slot → traces rib wall → back up → continues skin
- Result: internal ribs are integral with the skin, printed in one unbroken extrusion

**Internal structure pattern:**
- Diagonal grid ribs (not perpendicular to spar like traditional balsa)
- 0.6mm single wall (LW-PLA at 230°C, 0.45 flow multiplier)
- Carbon spar tunnel integrated into the geometry
- Zero retractions (critical for LW-PLA — foaming causes ooze/clogs)
- Zero infill (structure comes from designed internal walls)
- All internal corners filleted (4.5mm min radius — 25x stress reduction)

**Print orientation:**
- Flat on bed (trailing edge down)
- Layer lines run spanwise (parallel to spar)
- Each 256mm panel is one print job

**Key reference:** Planeprint RISE (2350mm wingspan, AG44 airfoil, LW-PLA + carbon rods, thermal F5J glider — closest commercial analog to AeroForge)

### Wing Segmentation

Based on carbon spar sourcing (1m tubes max from most suppliers):

```
Root ─── P1 ─── P2 ─── P3 ═══ P4 ─── P5 ─── Tip
         256     256     256 ║  256     256
    ────── Inner section ──── ║ ── Outer section ──
         768mm spar           ║    512mm spar
                              ║
                         Wing joiner
                     (6mm tube, 200mm)
```

- Inner section: Panels 1-3 (768mm span, one 1m spar cut to fit)
- Outer section: Panels 4-5 (512mm span, one 1m spar cut to fit)
- Joiner: 6mm OD tube, 200mm long, slides into both sections

### Fuselage Design

Based on aerodynamic research:
- **Cross-section:** Elliptical, 46mm W × 50mm H (fits battery bay)
- **Fineness ratio:** 5.4 (250mm pod length)
- **Nose:** 2:1 elliptical profile (lowest subsonic drag)
- **Wing position:** Shoulder-wing (competition standard)
- **Fillet radius:** 12-15mm at wing junction (6-7% root chord)
- **Boom transition:** 12° boat-tail half-angle, 100mm taper to 12mm boom
- **Carbon stringers:** 4× 1mm CF rods in printed channels (~2g total)
- **Pod printed in 2 halves** (left/right split), LW-PLA, 0.6mm wall

### Quality Gates (Enforced, Not Optional)

**Gate 1: Geometry (after each FreeCAD operation)**
- [ ] Bounding box matches expected dimensions (±1mm)
- [ ] Volume/mass estimate within weight budget
- [ ] Spar tunnel verified (8.1mm ID, centered in airfoil)
- [ ] No self-intersecting geometry
- [ ] Visual check via `get_view` — Claude MUST look at the screenshot

**Gate 2: Printability (after STL export)**
- [ ] Fits 256×256mm print bed
- [ ] No unsupported overhangs >45°
- [ ] Trailing edge ≥0.3mm thick
- [ ] Vase-mode-compatible (single continuous surface)

**Gate 3: Structural (FEM in FreeCAD)**
- [ ] Spar stress <50% of carbon tube ultimate (1500 MPa)
- [ ] Wing skin stress <50% of LW-PLA tensile (25 MPa)
- [ ] Tip deflection <15% half-span at 3g (with full wing structure)

**Gate 4: Aerodynamic (already completed)**
- [x] L/D >15:1 at cruise — PASS (55.6 at root, 36.1 at tip)
- [x] Cl_max >1.0 at all stations — PASS (1.035 min at tip)
- [x] Root stalls before tip (safe stall) — PASS (washout -3.5°)

### Off-The-Shelf Components

Sourced and documented in `docs/off_shelf_components.md`:
- Main spar: 8mm OD / 6mm ID carbon tube, 1m × 2 (Höllein or Lindinger)
- Tail boom: 10mm OD carbon tube, 1m × 1
- Fuselage stringers: 1mm CF rods × 4 (Höllein HOEKS10010)
- Rear spar: Pine strip 5×5mm (Höllein)
- Wing joiner: 6mm OD carbon tube, 200mm

### Material Settings for LW-PLA Printing

| Parameter | Value |
|-----------|-------|
| Hotend temp | 230-240°C |
| Bed temp | 50-60°C |
| Flow multiplier | 0.40-0.50 |
| Retractions | 0mm (disabled) |
| Infill | 0% |
| Perimeters | 1 (vase mode) |
| Wall thickness | ~0.6mm (foamed) |
| Fan | Off or minimal |
| LW-PLA density | 0.54 g/cm³ (foamed) |
| K-factor (Bambu) | 0 |

### What Gets Preserved from Current Codebase

- ✅ `src/core/specs.py` — single source of truth (all parameters)
- ✅ `src/core/component.py`, `assembly.py`, `dag.py` — component framework
- ✅ `src/cad/airfoils/` — real AG coordinate data + blending + NURBS generation
- ✅ `tests/` — 91 passing tests (airfoils, specs, consistency, components)
- ✅ `src/analysis/` — aerodynamic polars + structural FEM (just completed)
- ✅ `docs/specifications.md` — locked specs
- ✅ `components/` — off-the-shelf YAML specs

### What Gets Replaced

- ❌ `src/cad/wing/panel.py` — complete rewrite using vase-mode slot technique in FreeCAD
- ❌ Direct Build123d geometry for wing/fuselage/tail — moves to FreeCAD via MCP
- ❌ OCP viewer as primary visual feedback — replaced by FreeCAD GUI

### Implementation Sequence

1. Install OrcaSlicer
2. Start FreeCAD with MCP addon (verify connection)
3. Study Vase-Wing OpenSCAD generator code (understand slot technique)
4. Build single wing panel in FreeCAD (root panel, AG24 profile)
5. Verify in FreeCAD GUI + export STL + verify in OrcaSlicer vase mode
6. Iterate until one panel prints correctly
7. Extend to all 5 panels with blended airfoils
8. Build fuselage pod
9. Build empennage
10. Full assembly + CG calculation
11. FEM on complete wing structure
12. Final print preparation
