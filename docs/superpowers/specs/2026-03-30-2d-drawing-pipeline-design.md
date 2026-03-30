# Design Spec: 2D Drawing Pipeline (Build123d Projection + MCP Validation)

**Date:** 2026-03-30
**Status:** DRAFT — awaiting user review
**Problem:** Every 2D drawing attempt produces wrong orientation, overlapping labels, inconsistent scales, and unprofessional output. The root cause is hand-computing coordinates in Python scripts with no layout engine, no projection system, and no validation.

---

## Architecture

```
DESIGN_CONSENSUS.md
        │
        ▼
┌─────────────────────┐
│  Stage 1: 3D Sketch │  Build123d Python script
│  (lightweight shell) │  ~50 lines, runs in seconds
│  Planform outline    │  NOT the production model
│  + spar lines        │  Just enough geometry for projection
│  + airfoil sections  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Stage 2: Project   │  Build123d project_to_viewport()
│  Top view   (0,0,1) │  Hidden line removal automatic
│  Front view (0,-1,0)│  Orientation MATHEMATICALLY CORRECT
│  Side view  (1,0,0) │  Cannot be wrong
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Stage 3: Export DXF │  Build123d ExportDXF
│  Visible edges layer │  Clean geometry, correct scale
│  Hidden edges layer  │  One DXF per view, or combined
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Stage 4: Annotate  │  stgen-dxf-viewer MCP
│  via MCP             │
│  • Dimensions        │  Transaction-based editing
│  • Labels            │  Quality score after each step
│  • Title block       │  Invariant rules prevent overlap
│  • Section cuts      │  Visual verification via capture
│  • Parts list        │  Must score >80 to proceed
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Stage 5: Validate  │  stgen-dxf-viewer MCP
│  • run_drawing_checks│  Score 0-100
│  • check_geometry    │  Catches gaps, near-ortho lines
│  • check_dimensions  │  Dim text matches actual geometry
│  • capture_dxf_view  │  PNG for user review
│  • diff_against_spec │  Verify against consensus
└────────┬────────────┘
         │
         ▼
    User reviews PNG
    Approves or requests changes
```

---

## Stage 1: 3D Sketch Builder

**Purpose:** Create just enough 3D geometry to generate correct 2D projections. This is NOT the production model — it's a throwaway wireframe/shell.

**What gets modeled:**
- Planform outline (superellipse boundary as a Face or thin Shell)
- Spar centerlines as Wire objects at their fixed X positions
- Root airfoil cross-section (for front view)
- Hinge line
- Tip closure

**What does NOT get modeled:**
- Internal structure details (tunnels, wall thickness)
- Hinge knuckles, control horns
- Elevator deflection geometry

These details are added as annotations in Stage 4.

**Script pattern:**
```python
# scripts/sketch_hstab.py
from build123d import *

# Parameters from DESIGN_CONSENSUS.md
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
# ... etc

# Build planform as a thin shell
with BuildPart() as stab:
    # Root airfoil section
    with BuildSketch(Plane.XZ) as root:
        # HT-13 profile points
        ...
    # Tip airfoil section
    with BuildSketch(Plane.XZ.offset(HALF_SPAN)) as tip:
        # HT-12 profile points (scaled)
        ...
    loft()

# Project to standard views
top_vis, top_hid = stab.part.project_to_viewport((0, 0, 100))
front_vis, front_hid = stab.part.project_to_viewport((0, -100, 0))
side_vis, side_hid = stab.part.project_to_viewport((100, 0, 0))

# Export DXF with layers
exporter = ExportDXF(unit=Unit.MM)
exporter.add_layer("VISIBLE", line_weight=0.5)
exporter.add_layer("HIDDEN", line_type=LineType.ISO_DASH, line_weight=0.25)
# Add shapes per view (offset on sheet for layout)
exporter.add_shape(top_vis, layer="VISIBLE")
exporter.add_shape(top_hid, layer="HIDDEN")
exporter.write("cad/.../drawing_raw.dxf")
```

**Coordinate convention for projections:**
- TOP view (planform): looking down Z axis → X = chordwise (LE forward), Y = spanwise
- FRONT view: looking along Y axis → X = chordwise, Z = thickness
- RIGHT view: looking along X axis → Y = spanwise, Z = thickness

The projection math handles this automatically. We just set the viewport direction.

---

## Stage 2: View Layout on Sheet

**Sheet sizes:** A3 landscape (420×297mm) for assemblies, A4 landscape (297×210mm) for components.

**Third-angle projection arrangement:**
```
┌──────────────────────────────────────────────┐
│                                              │
│    ┌─────────────────┐                       │
│    │   TOP VIEW       │   ┌──────┐           │
│    │   (planform)     │   │RIGHT │           │
│    │                  │   │VIEW  │           │
│    │                  │   │      │           │
│    └─────────────────┘   └──────┘           │
│    ┌─────────────────┐                       │
│    │   FRONT VIEW     │   ┌──────────┐       │
│    │   (root section) │   │ DETAIL   │       │
│    └─────────────────┘   │ (hinge)  │       │
│                           └──────────┘       │
│    ┌────────────────────────────────────┐     │
│    │         TITLE BLOCK (ISO 7200)     │     │
│    └────────────────────────────────────┘     │
└──────────────────────────────────────────────┘
```

**Layout rules:**
- All views at SAME scale (or clearly labeled different scale for details)
- Minimum 15mm gap between views
- Front view directly below top view (third-angle projection alignment)
- Right view directly right of front view
- Detail views in remaining space with scale callout
- Title block bottom-right per ISO 7200

**Scale selection:** Automatic — compute bounding box of all views, find largest scale that fits sheet with margins.

---

## Stage 3: DXF Layer Standard

| Layer | Color | Weight | Content |
|-------|-------|--------|---------|
| VISIBLE | 7 (white) | 0.50mm | Visible outlines |
| HIDDEN | 8 (gray) | 0.25mm | Hidden edges (ISO dash) |
| CENTER | 5 (blue) | 0.18mm | Centerlines (dash-dot) |
| DIM | 1 (red) | 0.18mm | Dimensions |
| TEXT | 7 (white) | 0.18mm | Labels and notes |
| SECTION | 4 (cyan) | 0.35mm | Section cut indicators |
| HATCH | 252 (lt gray) | 0.13mm | Section hatching |
| BORDER | 7 (white) | 0.70mm | Sheet border |
| TITLEBLOCK | 7 (white) | 0.35mm | Title block |
| SPAR | 3 (green) | 0.35mm | Spar positions (annotation) |

---

## Stage 4: MCP Annotation Workflow

After exporting raw geometry from Build123d, use stgen-dxf-viewer MCP for annotation:

**Mandatory startup sequence:**
1. `get_dxf_summary()` — understand current state
2. `write_drawing_spec()` — define sheet, scale, layer rules
3. `set_invariant_rules()` — spacing, alignment, layer compliance
4. `register_grid_anchors()` — 5mm grid for anchor placement
5. `update_work_plan()` — define annotation steps

**Annotation steps (each in a transaction):**
1. Title block (border, company info, drawing number, scale, date)
2. View labels ("VIEW 1: TOP", "VIEW 2: FRONT", etc.)
3. Dimensions — one view at a time, using `create_dimension`
4. Labels — spar names, material callouts, using `create_leader`
5. Section cut indicators (A-A, B-B lines)
6. Parts list / notes block
7. Orientation arrows (FWD, INBD)

**After each transaction:**
- `end_transaction()`
- `run_drawing_checks()` — must score >80
- `capture_dxf_view()` — visual check
- If score <80: `rollback_transaction()`, fix, retry

---

## Stage 5: Validation Rules

**Invariant rules set at drawing start:**

```json
[
  {"type": "spacing", "rule": "min_gap_between_views", "value": 15, "unit": "mm"},
  {"type": "spacing", "rule": "min_text_spacing", "value": 2, "unit": "mm"},
  {"type": "layer_assignment", "rule": "dimensions_on_DIM_layer"},
  {"type": "layer_assignment", "rule": "text_on_TEXT_layer"},
  {"type": "dimension_consistency", "rule": "dim_text_matches_geometry"},
  {"type": "alignment", "rule": "front_view_below_top_view"},
  {"type": "alignment", "rule": "right_view_right_of_front_view"},
  {"type": "custom", "rule": "no_text_overlapping_geometry"},
  {"type": "custom", "rule": "all_views_same_scale_unless_detail"}
]
```

**Quality gates:**
- Drawing checks score must be >80 before user review
- Geometry quality check must pass (no tiny gaps, no near-orthogonal lines)
- Dimension consistency must pass (all dimension text matches actual measurement)
- Visual capture must show no obvious overlap or misalignment

---

## Workflow Integration with CAD Framework

The pipeline fits into the existing CAD_FRAMEWORK.md workflow:

```
1. Research (reference images, datasheets)
2. Aero+Structural agent team → DESIGN_CONSENSUS.md
3. ★ NEW: 3D sketch (Build123d, throwaway)
4. ★ NEW: Auto-project 2D views
5. ★ NEW: Annotate via MCP with validation
6. 2D Drawing review (user approves PNG)
7. Production 3D model (Build123d, full detail)
8. Assembly validation
9. Renders
10. Documentation
11. Commit
```

Step 3-5 replace the old "hand-draw DXF in Python" step. The 3D sketch in step 3 is NOT the production model from step 7 — it's a lightweight wireframe that exists only to generate correct projections.

---

## File Organization

```
scripts/
├── sketch_hstab_assembly.py    # Stage 1: 3D sketch for H-Stab assembly
├── sketch_hstab_left.py        # Stage 1: 3D sketch for HStab_Left component
└── project_to_drawing.py       # Stage 2-3: Reusable projection + DXF export utility

src/cad/drawing/
├── __init__.py
├── projector.py                # project_to_viewport wrapper with standard views
├── layout.py                   # Sheet layout calculator (view positions, scale)
└── exporter.py                 # ExportDXF wrapper with standard layers
```

**`projector.py`** provides:
- `project_standard_views(part)` → dict of {view_name: (visible_edges, hidden_edges)}
- Standard viewport directions for top/front/right/iso
- Bounding box calculation for each view

**`layout.py`** provides:
- `calculate_layout(views, sheet_size)` → dict of {view_name: (x_offset, y_offset, scale)}
- Auto-scale to fit sheet with margins
- Third-angle projection alignment
- Minimum gap enforcement

**`exporter.py`** provides:
- `export_drawing(views, layout, output_path)` → DXF file with standard layers
- Standard layer creation
- View geometry placed at computed positions

---

## What This Solves

| Previous Problem | How Pipeline Fixes It |
|---|---|
| LE/TE orientation wrong | `project_to_viewport()` is mathematically correct — cannot be wrong |
| Overlapping labels | MCP invariant rules enforce minimum spacing |
| Inconsistent view scales | `layout.py` computes unified scale for all views |
| Views not aligned | Third-angle projection layout with alignment rules |
| Tips not rounded | 3D sketch uses actual airfoil geometry — projection preserves curves |
| No validation | Quality score >80 gate, geometry checks, visual capture |
| Labels on top of geometry | MCP `spacing` invariant prevents text-geometry overlap |
| Unprofessional output | ISO layer standards, proper line weights, title block |

---

## Scope and Boundaries

**In scope:**
- Projection engine (Build123d → DXF)
- Layout calculator (auto-fit views on sheet)
- MCP annotation workflow
- Validation rules and quality gates
- Reusable for ALL components and assemblies

**Out of scope (for now):**
- FreeCAD TechDraw integration (deferred to post-3D-model phase)
- GD&T symbols
- Automatic BOM generation
- Print-ready PDF export (SVG/DXF are sufficient for now)

---

## Success Criteria

1. H-Stab assembly drawing with correct orientation in all views
2. No overlapping text or dimensions
3. All views at consistent scale with proper third-angle alignment
4. Quality score >80 from stgen-dxf-viewer checks
5. User approves the drawing on first or second review
6. Pipeline is reusable for HStab_Left, Elevator_Left, and all future components
