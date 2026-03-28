# Tooling Analysis & Pipeline Assessment

## Current Stack Assessment

### Build123d (Python, OCCT kernel) - KEEP as primary CAD
**Strengths:**
- Mathematically exact NURBS geometry (not polygon approximation)
- Airfoil splines are TRUE curves (confirmed: AG profiles render perfectly)
- Parametric: every dimension from specs.py, full DAG propagation
- Python scripting = AI can generate/modify geometry programmatically
- STEP export is lossless (OCCT → OCCT)
- Shell, loft, Boolean operations work on exact geometry

**Weaknesses:**
- Complex Boolean operations on spline surfaces are slow (~80s per panel)
- No built-in FEM/CFD
- No assembly constraint solver (joints are positional, not physics)
- Visualization depends on OCP viewer (MCP integration fragile)

**Verdict: KEEP. The airfoil precision is irreplaceable. Build all parametric geometry here.**

### FreeCAD 1.0 (installed, headless via FreeCADCmd.exe)
**Use for:**
- FEM analysis (CalculiX solver, built-in)
- CFD analysis (CfdOF + OpenFOAM integration)
- Mesh generation (Gmsh or Netgen, built-in)
- Assembly visualization (if OCP viewer fails)
- STEP import from Build123d is lossless (same OCCT kernel)

**Path:** `C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0\bin\FreeCADCmd.exe`

**Workflow:** Build123d → STEP → FreeCAD import → Mesh → FEM/CFD

**Note on polygon display:** FreeCAD's 3D viewport shows tessellated (polygon) approximation for display only. The underlying BREP geometry is exact NURBS - same as Build123d. The "rough circles" are just display tessellation, not the actual geometry.

### Slicer (NOT INSTALLED - NEEDS ACTION)
**Need either:**
- **OrcaSlicer** (recommended, open-source, Bambu compatible, has CLI)
- **BambuStudio** (official Bambu software, more limited CLI)

**Purpose:**
- Generate actual 3D print mesh (G-code paths)
- Validate printability (overhangs, supports, print time)
- Export mesh for analysis (STL → FreeCAD FEM)

**Action: Install OrcaSlicer**

### OCP Viewer (MCP server, port 3939)
**Status:** Port 3939 is OPEN. Viewer is running.
**Issue:** The `capture_ocp_screenshot` MCP tool fails/hangs sometimes.
**Workaround:** Use `show()` to display in viewer, skip screenshot capture if it hangs.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│  1. PARAMETRIC DESIGN (Build123d + Python)               │
│     specs.py → airfoils → wing panels → fuselage → tail │
│     Output: STEP files (exact NURBS geometry)            │
│     Validation: geometric checks, mass estimates         │
├─────────────────────────────────────────────────────────┤
│  2. STRUCTURAL ANALYSIS (FreeCAD + CalculiX)             │
│     Import STEP → Mesh (Gmsh) → FEM → stress/deflection │
│     Loads: flight loads, landing loads, spar bending     │
│     Output: stress maps, safety factors                  │
├─────────────────────────────────────────────────────────┤
│  3. AERODYNAMIC ANALYSIS (xfoil + optional OpenFOAM)     │
│     2D: xfoil polars at each span station (Re-specific)  │
│     3D: optional full-wing CFD in OpenFOAM via FreeCAD   │
│     Output: Cl/Cd polars, drag breakdown, L/D            │
├─────────────────────────────────────────────────────────┤
│  4. PRINT PREPARATION (OrcaSlicer)                       │
│     STEP/STL → slice → validate printability             │
│     Layer texture analysis for aerodynamic effects       │
│     Output: G-code, print time, filament usage           │
├─────────────────────────────────────────────────────────┤
│  5. PRINT-QUALITY ANALYSIS (FreeCAD FEM on mesh)         │
│     Sliced mesh → FEM with actual print geometry         │
│     Accounts for infill, layer adhesion, wall thickness  │
│     Output: as-printed structural analysis               │
└─────────────────────────────────────────────────────────┘
```

## Quality Gates (Must-Pass Checkpoints)

### Gate 1: Geometry Validation (after Build123d)
- [ ] All airfoil profiles verified against UIUC data (max 0.1% deviation)
- [ ] Panel dimensions fit 256x256mm print bed
- [ ] Spar tunnel diameter correct (8.1-8.2mm ID for 8.0mm tube)
- [ ] Rear spar slot dimensions correct (5.2x3.2mm for 5x3mm strip)
- [ ] Control surface hinge line at correct chord fraction
- [ ] Minimum wall thickness ≥ 0.5mm everywhere
- [ ] No self-intersecting geometry
- [ ] Mass estimate within weight budget

### Gate 2: Printability Validation (after slicing)
- [ ] No unsupported overhangs > 45°
- [ ] Bridge spans < 10mm (or support planned)
- [ ] Print orientation optimized (flat bottom on bed)
- [ ] Estimated print time reasonable
- [ ] Filament usage within budget

### Gate 3: Structural Validation (FEM)
- [ ] Spar bending stress < 50% of carbon tube yield
- [ ] Wing skin stress < 50% of LW-PLA tensile strength
- [ ] Rib stress < material limit
- [ ] Deflection at tip < 5% of half-span under 3g load
- [ ] No flutter predicted at Vne

### Gate 4: Aerodynamic Validation (xfoil/CFD)
- [ ] Cl_max > 1.2 at thermal speed
- [ ] L/D > 15:1 at cruise
- [ ] No premature stall at any span station
- [ ] Drag breakdown matches targets

### Gate 5: Assembly Validation
- [ ] All panels slide onto spar without interference
- [ ] Wing joiner fits both sections
- [ ] CG achievable within target range
- [ ] All servo linkages have clearance
- [ ] Boom-to-pod joint secure

## Incident Prevention Rules

1. **Never show geometry without internal structure** - if ribs aren't built, say so
2. **Never retry a failing tool more than twice** - diagnose the failure
3. **Always source physical components before modeling** around them
4. **Always verify STEP export** - re-import and check bounding box
5. **Always estimate mass** - compare to weight budget immediately
6. **Every component must pass Gate 1** before moving to next component
7. **Screenshot failures** - use `show()` only, don't block on screenshot capture

## Wing Panel Build Strategy (Corrected)

### Previous (WRONG) approach:
1. Loft solid → shell → subtract spar hole → pray
Result: Hollow skin, no structure, spar punches through top

### Corrected approach - Built-Up Structure:
1. **Create rib profiles** at each station (airfoil wire → face → extrude to rib thickness)
2. **Cut lightening holes** in ribs (elliptical, between spars)
3. **Cut spar holes** in ribs (circular for main, rectangular for rear)
4. **Loft outer skin** between rib outer edges (thin shell, NOT hollowed solid)
5. **Loft D-box skin** from LE to 30% chord (separate shell, bonds to ribs)
6. **Add spar reinforcement rings** around spar tunnel at each rib
7. **Add trailing edge strip** connecting ribs at TE
8. **Result:** A printable wing panel with visible internal structure

Each sub-step is a separate Part that gets combined (union) at the end.
