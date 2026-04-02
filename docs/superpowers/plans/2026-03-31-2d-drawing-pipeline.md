# 2D Drawing Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Build123d projection + DXF export pipeline and prove it with the H-Stab Assembly drawing.

**Architecture:** A Python script builds a lightweight 3D sketch of the H-Stab assembly from consensus parameters, then `project_to_viewport()` generates mathematically correct top/front/side views, and `ExportDXF` writes a clean DXF with standard layers. The stgen-dxf-viewer MCP adds dimensions, labels, and title block with quality validation.

**Tech Stack:** Build123d (3D sketch + projection + export), ezdxf (DXF post-processing backup), stgen-dxf-viewer MCP (annotation + validation)

---

### Task 1: Projection Utility — `src/cad/drawing/projector.py`

**Files:**
- Create: `src/cad/drawing/__init__.py`
- Create: `src/cad/drawing/projector.py`
- Test: `tests/cad/drawing/test_projector.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/cad/drawing/test_projector.py
"""Tests for the 2D projection utility."""
import pytest
from build123d import Box


def test_project_standard_views_returns_three_views():
    from src.cad.drawing.projector import project_standard_views

    box = Box(100, 50, 10)
    views = project_standard_views(box)

    assert "top" in views
    assert "front" in views
    assert "right" in views
    for name in ["top", "front", "right"]:
        assert "visible" in views[name]
        assert "hidden" in views[name]
        assert len(views[name]["visible"]) > 0


def test_compute_2d_bounds_of_box():
    from src.cad.drawing.projector import project_standard_views, compute_2d_bounds

    box = Box(100, 50, 10)
    views = project_standard_views(box)
    xmin, ymin, xmax, ymax = compute_2d_bounds(
        views["top"]["visible"] + views["top"]["hidden"]
    )
    # Top view of 100x50x10 box → projected width ~100, height ~50
    assert abs((xmax - xmin) - 100) < 1.0
    assert abs((ymax - ymin) - 50) < 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. pytest tests/cad/drawing/test_projector.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Create the module**

```python
# src/cad/drawing/__init__.py
"""AeroForge 2D drawing pipeline — Build123d projection + DXF export."""
```

```python
# src/cad/drawing/projector.py
"""Project 3D Build123d parts to standard 2D views.

Uses project_to_viewport() for mathematically correct orthographic
projections with automatic hidden-line removal.

Standard views (third-angle projection):
  TOP:   looking down -Z  → viewport_origin=(0, 0, 100)
  FRONT: looking along +Y → viewport_origin=(0, -100, 0)
  RIGHT: looking along -X → viewport_origin=(100, 0, 0)
"""

from build123d import Shape, Compound


# Standard viewport directions for third-angle projection
VIEWPORTS = {
    "top": (0, 0, 100),
    "front": (0, -100, 0),
    "right": (100, 0, 0),
}


def project_standard_views(
    part: Shape,
) -> dict[str, dict[str, list]]:
    """Project a 3D part to top, front, and right views.

    Returns dict: {view_name: {"visible": [Edge...], "hidden": [Edge...]}}
    """
    views = {}
    for name, vp in VIEWPORTS.items():
        visible, hidden = part.project_to_viewport(vp)
        views[name] = {"visible": list(visible), "hidden": list(hidden)}
    return views


def compute_2d_bounds(edges: list) -> tuple[float, float, float, float]:
    """Compute 2D bounding box (xmin, ymin, xmax, ymax) of projected edges."""
    if not edges:
        return (0.0, 0.0, 0.0, 0.0)
    c = Compound(edges)
    bb = c.bounding_box()
    return (bb.min.X, bb.min.Y, bb.max.X, bb.max.Y)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. pytest tests/cad/drawing/test_projector.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/cad/drawing/__init__.py src/cad/drawing/projector.py tests/cad/drawing/test_projector.py
git commit -m "feat: add Build123d projection utility for 2D drawing pipeline"
```

---

### Task 2: Layout Calculator — `src/cad/drawing/layout.py`

**Files:**
- Create: `src/cad/drawing/layout.py`
- Test: `tests/cad/drawing/test_layout.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/cad/drawing/test_layout.py
"""Tests for the sheet layout calculator."""
import pytest


def test_layout_fits_on_a3_sheet():
    from src.cad.drawing.layout import calculate_layout

    # Simulate view bounding boxes (model-space mm)
    view_bounds = {
        "top": (0, 0, 115, 430),      # planform: 115mm chord x 430mm span
        "front": (0, -4, 115, 4),      # root section: 115mm x 8mm
        "right": (0, -4, 430, 4),      # side view: 430mm x 8mm
    }

    layout = calculate_layout(view_bounds, sheet_size="A3")

    assert layout["scale"] > 0
    assert layout["scale"] <= 1.0  # never scale up

    # All view origins must be inside the sheet (with margins)
    sw, sh = 420, 297
    for view_name in ["top", "front", "right"]:
        ox, oy = layout[view_name]
        assert ox >= 15, f"{view_name} left edge outside margin"
        assert oy >= 15, f"{view_name} bottom edge outside margin"


def test_top_view_is_above_front_view():
    from src.cad.drawing.layout import calculate_layout

    view_bounds = {
        "top": (0, 0, 100, 200),
        "front": (0, -5, 100, 5),
        "right": (0, -5, 200, 5),
    }

    layout = calculate_layout(view_bounds, sheet_size="A3")

    # Third-angle: top view Y > front view Y
    assert layout["top"][1] > layout["front"][1]
    # Right view X > front view X
    assert layout["right"][0] > layout["front"][0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. pytest tests/cad/drawing/test_layout.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Write the layout calculator**

```python
# src/cad/drawing/layout.py
"""Calculate view positions on a standard engineering drawing sheet.

Third-angle projection (ISO standard):
  - FRONT view: bottom-left
  - TOP view: directly above front view
  - RIGHT view: directly right of front view

Auto-scales all views with a single scale factor to fit the sheet.
"""

SHEETS = {
    "A4": (297, 210),
    "A3": (420, 297),
    "A2": (594, 420),
}


def calculate_layout(
    view_bounds: dict[str, tuple[float, float, float, float]],
    sheet_size: str = "A3",
    margin: float = 20.0,
    gap: float = 15.0,
    title_block_h: float = 42.0,
) -> dict:
    """Calculate view positions on sheet using third-angle projection.

    Args:
        view_bounds: {view_name: (xmin, ymin, xmax, ymax)} in model mm
        sheet_size: "A3" or "A4"
        margin: border margin in mm
        gap: minimum gap between views in mm
        title_block_h: title block height at bottom-right

    Returns:
        dict with "scale" and per-view (x_offset, y_offset) for bottom-left corner.
    """
    sw, sh = SHEETS[sheet_size]

    # Available drawing area
    avail_w = sw - 2 * margin
    avail_h = sh - 2 * margin - title_block_h

    # View dimensions in model space
    def dim(bb):
        return bb[2] - bb[0], bb[3] - bb[1]

    top_w, top_h = dim(view_bounds["top"])
    front_w, front_h = dim(view_bounds["front"])
    right_w, right_h = dim(view_bounds["right"])

    # Space needed (third-angle layout)
    col1_w = max(top_w, front_w)
    needed_w = col1_w + gap + right_w
    needed_h = top_h + gap + max(front_h, right_h)

    # Scale to fit (never scale up beyond 1:1)
    scale = min(avail_w / needed_w, avail_h / needed_h, 1.0)

    # Scaled dimensions
    s_col1_w = col1_w * scale
    s_front_h = front_h * scale
    s_top_h = top_h * scale

    # Position front view: bottom-left of available area
    front_x = margin
    front_y = margin + title_block_h

    # Top view: directly above front, left-aligned
    top_x = margin
    top_y = front_y + s_front_h + gap

    # Right view: right of front, bottom-aligned
    right_x = margin + s_col1_w + gap
    right_y = front_y

    return {
        "scale": scale,
        "sheet": (sw, sh),
        "top": (top_x, top_y),
        "front": (front_x, front_y),
        "right": (right_x, right_y),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. pytest tests/cad/drawing/test_layout.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/cad/drawing/layout.py tests/cad/drawing/test_layout.py
git commit -m "feat: add sheet layout calculator for third-angle projection"
```

---

### Task 3: DXF Exporter — `src/cad/drawing/exporter.py`

**Files:**
- Create: `src/cad/drawing/exporter.py`
- Test: `tests/cad/drawing/test_exporter.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/cad/drawing/test_exporter.py
"""Tests for the DXF drawing exporter."""
import os
import pytest
from build123d import Box


def test_export_produces_dxf_file(tmp_path):
    from src.cad.drawing.projector import project_standard_views, compute_2d_bounds
    from src.cad.drawing.layout import calculate_layout
    from src.cad.drawing.exporter import export_drawing

    box = Box(100, 50, 10)
    views = project_standard_views(box)

    view_bounds = {}
    for name in ["top", "front", "right"]:
        all_edges = views[name]["visible"] + views[name]["hidden"]
        view_bounds[name] = compute_2d_bounds(all_edges)

    layout = calculate_layout(view_bounds, sheet_size="A3")

    out_path = str(tmp_path / "test_drawing.dxf")
    export_drawing(views, layout, out_path)

    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 100  # not empty
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. pytest tests/cad/drawing/test_exporter.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Write the exporter**

```python
# src/cad/drawing/exporter.py
"""Export projected views to DXF with standard engineering drawing layers.

Takes projected views + layout and writes a single DXF file with
all views positioned on the sheet using the computed scale and offsets.
"""

from build123d import Compound, Location, ExportDXF, LineType, Unit


def export_drawing(
    views: dict[str, dict[str, list]],
    layout: dict,
    output_path: str,
) -> str:
    """Export projected views to a DXF file.

    Args:
        views: {view_name: {"visible": [Edge], "hidden": [Edge]}}
        layout: from calculate_layout() — scale + per-view offsets
        output_path: path to write the DXF file

    Returns:
        The output path.
    """
    scale = layout["scale"]

    exporter = ExportDXF(unit=Unit.MM)
    exporter.add_layer("VISIBLE", line_weight=0.5)
    exporter.add_layer(
        "HIDDEN",
        line_color=(150, 150, 150),
        line_type=LineType.ISO_DASH,
        line_weight=0.25,
    )

    for view_name in ["top", "front", "right"]:
        if view_name not in views or view_name not in layout:
            continue

        ox, oy = layout[view_name]
        vis = views[view_name]["visible"]
        hid = views[view_name]["hidden"]

        vis_moved = _scale_and_translate(vis, scale, ox, oy)
        hid_moved = _scale_and_translate(hid, scale, ox, oy)

        if vis_moved:
            exporter.add_shape(vis_moved, layer="VISIBLE")
        if hid_moved:
            exporter.add_shape(hid_moved, layer="HIDDEN")

    exporter.write(output_path)
    return output_path


def _scale_and_translate(
    edges: list, scale: float, ox: float, oy: float
) -> list:
    """Scale edges by factor, then translate to (ox, oy) on sheet."""
    if not edges:
        return []
    c = Compound(edges)
    # Scale about origin
    scaled = c.scale(scale)
    # Get current bounds to compute translation
    bb = scaled.bounding_box()
    # Translate so bounding box min lands at (ox, oy)
    dx = ox - bb.min.X
    dy = oy - bb.min.Y
    moved = scaled.moved(Location((dx, dy, 0)))
    return list(moved.edges())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. pytest tests/cad/drawing/test_exporter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/cad/drawing/exporter.py tests/cad/drawing/test_exporter.py
git commit -m "feat: add DXF exporter with standard layers and auto-layout"
```

---

### Task 4: H-Stab Assembly 3D Sketch + Drawing Generation

**Files:**
- Create: `scripts/sketch_hstab_assembly.py`

This is the assembly-level 3D sketch. It creates OUTLINE-level geometry for ALL components: both stab halves, both elevator halves, all four rods, and the VStab fin gap. Then projects to top/front/right views and exports DXF.

- [ ] **Step 1: Write the sketch script**

```python
# scripts/sketch_hstab_assembly.py
"""
H-Stab Assembly: 3D sketch → 2D projected drawing.

Builds lightweight 3D outlines of ALL assembly components from
DESIGN_CONSENSUS.md v5 parameters, then projects to standard
orthographic views (top, front, right) via Build123d.

Components shown as outlines:
  - HStab_Left + HStab_Right (stab shells, LE to hinge)
  - Elevator_Left + Elevator_Right (hinge to TE)
  - Main spar (3mm CF tube at X=35mm)
  - Rear spar (1.5mm CF rod at X=69mm)
  - Hinge wire (0.5mm at X=74.75mm)
  - Stiffeners (1mm CF rod at X=92mm, split)
  - VStab fin (7mm thick at center)
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from build123d import (
    BuildPart, BuildSketch, Plane, Location,
    Spline, Line, Polygon, loft, Cylinder, Box, Compound,
    Axis, mirror, Vector,
)
from src.cad.drawing.projector import project_standard_views, compute_2d_bounds
from src.cad.drawing.layout import calculate_layout
from src.cad.drawing.exporter import export_drawing

# ═══════════════════════════════════════════════════════════════
# PARAMETERS FROM DESIGN_CONSENSUS.md v5
# ═══════════════════════════════════════════════════════════════
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
N = 2.3                    # superellipse exponent
ALIGN_X = 0.45 * ROOT_CHORD  # 51.75mm — constant X of 45% chord

HINGE_X = 74.75            # mm from root LE
TE_TRUNC = 0.97            # 97% chord truncation

MAIN_SPAR_X = 35.0
MAIN_SPAR_OD = 3.0
MAIN_SPAR_TERM = 186.0     # per half

REAR_SPAR_X = 69.0
REAR_SPAR_DIA = 1.5
REAR_SPAR_TERM = 210.0

HINGE_WIRE_X = 74.75
HINGE_WIRE_DIA = 0.5
HINGE_WIRE_TERM = 203.0

STIFFENER_X = 92.0
STIFFENER_DIA = 1.0
STIFFENER_TERM = 150.0

VSTAB_FIN_THICK = 7.0
ROOT_GAP = 8.0             # total gap at root (fin + clearance)

TC_ROOT = 0.065             # HT-13
TC_TIP = 0.051              # HT-12


# ═══════════════════════════════════════════════════════════════
# GEOMETRY HELPERS
# ═══════════════════════════════════════════════════════════════

def chord_at(y):
    eta = abs(y) / HALF_SPAN
    if eta >= 1.0:
        return 0.0
    return ROOT_CHORD * (1.0 - eta**N) ** (1.0 / N)


def le_at(y):
    return ALIGN_X - 0.45 * chord_at(y)


def tc_at(y):
    eta = min(abs(y) / HALF_SPAN, 1.0)
    return TC_ROOT * (1.0 - eta) + TC_TIP * eta


def airfoil_yt(xc_frac, tc, chord):
    """NACA 4-digit half-thickness at chord fraction."""
    if xc_frac <= 0 or xc_frac > 1.0 or chord <= 0:
        return 0.0
    yt = 5.0 * tc * (
        0.2969 * xc_frac**0.5
        - 0.1260 * xc_frac
        - 0.3516 * xc_frac**2
        + 0.2843 * xc_frac**3
        - 0.1015 * xc_frac**4
    ) * chord
    return max(yt, 0.0)


def airfoil_section_pts(y, x_start, x_end, n_pts=20):
    """Generate 2D points (x, z) for an airfoil section at span y.
    x_start and x_end are absolute X positions (not fractions).
    Returns closed polygon points: upper surface LE→TE, lower TE→LE.
    """
    c = chord_at(y)
    tc = tc_at(y)
    le_x = le_at(y)

    if c <= 0:
        return []

    pts_upper = []
    pts_lower = []

    for i in range(n_pts + 1):
        x = x_start + (x_end - x_start) * i / n_pts
        xc_frac = (x - le_x) / c  # chord fraction
        xc_frac = max(0.001, min(xc_frac, 0.999))
        yt = airfoil_yt(xc_frac, tc, c)
        pts_upper.append((x, yt))
        pts_lower.append((x, -yt))

    pts_lower.reverse()
    # Close: upper LE→TE, lower TE→LE
    return pts_upper + pts_lower[1:-1]  # avoid duplicate endpoints


# ═══════════════════════════════════════════════════════════════
# BUILD 3D SKETCH
# ═══════════════════════════════════════════════════════════════

def build_shell_half(y_start, y_end, x_start_fn, x_end_fn, n_stations=5):
    """Loft an airfoil shell between span stations.
    x_start_fn(y) and x_end_fn(y) return chordwise start/end at station y.
    """
    station_ys = [
        y_start + (y_end - y_start) * i / (n_stations - 1)
        for i in range(n_stations)
    ]

    with BuildPart() as part:
        for y in station_ys:
            x_s = x_start_fn(y)
            x_e = x_end_fn(y)
            if x_e - x_s < 1.0:
                continue  # skip degenerate sections
            pts = airfoil_section_pts(y, x_s, x_e)
            if len(pts) < 4:
                continue
            with BuildSketch(Plane.XZ.offset(y)):
                Polygon(pts, align=None)
        loft()

    return part.part


def build_assembly():
    """Build the complete H-Stab assembly as lightweight 3D outlines."""
    parts = []

    # ── Stab shells (LE to hinge line) ──
    # Stab left: y = ROOT_GAP/2 (4mm) to HALF_SPAN
    def stab_le(y): return le_at(y)
    def stab_te(y): return min(HINGE_X, le_at(y) + chord_at(y))  # hinge or TE, whichever is less

    stab_left = build_shell_half(ROOT_GAP / 2, HALF_SPAN * 0.95, stab_le, stab_te)
    if stab_left:
        parts.append(stab_left)
        # Mirror for right half (mirror across XZ plane, y → -y)
        stab_right = stab_left.mirror(Plane.XZ)
        parts.append(stab_right)

    # ── Elevator shells (hinge+gap to TE) ──
    HINGE_GAP = 0.3
    def elev_le(y): return HINGE_X + HINGE_GAP
    def elev_te(y):
        c = chord_at(y)
        return le_at(y) + TE_TRUNC * c

    elev_left = build_shell_half(ROOT_GAP / 2, HALF_SPAN * 0.93, elev_le, elev_te)
    if elev_left:
        parts.append(elev_left)
        elev_right = elev_left.mirror(Plane.XZ)
        parts.append(elev_right)

    # ── Spars (cylinders at constant X positions) ──
    # Main spar: 3mm tube, ±186mm
    with BuildPart() as spar:
        Cylinder(
            MAIN_SPAR_OD / 2, MAIN_SPAR_TERM * 2,
            align=None,
        )
    spar_part = spar.part.moved(
        Location((MAIN_SPAR_X, -MAIN_SPAR_TERM, 0))
    )
    # Rotate so cylinder axis is along Y
    spar_part = spar.part.rotate(Axis.X, 90).moved(
        Location((MAIN_SPAR_X, 0, 0))
    )
    parts.append(spar_part)

    # Rear spar: 1.5mm rod, ±210mm
    rear = Cylinder(REAR_SPAR_DIA / 2, REAR_SPAR_TERM * 2).rotate(Axis.X, 90).moved(
        Location((REAR_SPAR_X, 0, 0))
    )
    parts.append(rear)

    # Hinge wire: 0.5mm, ±203mm
    hinge = Cylinder(HINGE_WIRE_DIA / 2, HINGE_WIRE_TERM * 2).rotate(Axis.X, 90).moved(
        Location((HINGE_WIRE_X, 0, 0))
    )
    parts.append(hinge)

    # Stiffeners: 1mm, y=4..150 each side (NOT through fin)
    for sign in [1, -1]:
        stiff = Cylinder(STIFFENER_DIA / 2, STIFFENER_TERM - ROOT_GAP / 2).rotate(
            Axis.X, 90
        ).moved(
            Location((STIFFENER_X, sign * (ROOT_GAP / 2 + (STIFFENER_TERM - ROOT_GAP / 2) / 2), 0))
        )
        parts.append(stiff)

    # ── VStab fin (thin rectangle at root) ──
    fin = Box(50, VSTAB_FIN_THICK, 8).moved(
        Location((HINGE_X - 25, 0, 0))
    )
    parts.append(fin)

    # Combine all components
    assembly = Compound(parts)
    return assembly


# ═══════════════════════════════════════════════════════════════
# MAIN: BUILD → PROJECT → LAYOUT → EXPORT
# ═══════════════════════════════════════════════════════════════

def main():
    print("Stage 1: Building 3D sketch of H-Stab assembly...")
    assembly = build_assembly()
    print(f"  Assembly: {len(assembly.solids())} solids")

    print("Stage 2: Projecting to standard views...")
    views = project_standard_views(assembly)
    for name, v in views.items():
        print(f"  {name}: {len(v['visible'])} visible, {len(v['hidden'])} hidden edges")

    print("Stage 3: Calculating layout for A3 sheet...")
    view_bounds = {}
    for name in ["top", "front", "right"]:
        all_edges = views[name]["visible"] + views[name]["hidden"]
        view_bounds[name] = compute_2d_bounds(all_edges)
        bb = view_bounds[name]
        print(f"  {name} bounds: {bb[2]-bb[0]:.1f} x {bb[3]-bb[1]:.1f} mm")

    layout = calculate_layout(view_bounds, sheet_size="A3")
    print(f"  Scale: 1:{1/layout['scale']:.1f}")

    print("Stage 4: Exporting DXF...")
    out_path = "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf"
    export_drawing(views, layout, out_path)
    print(f"  DXF: {out_path}")

    # Also export PNG via ezdxf for quick preview
    try:
        import ezdxf
        from ezdxf.addons.drawing.matplotlib import qsave
        doc = ezdxf.readfile(out_path)
        png_path = out_path.replace(".dxf", ".png")
        qsave(doc.modelspace(), png_path, dpi=200, bg="#FFFFFF")
        print(f"  PNG: {png_path}")
    except Exception as e:
        print(f"  PNG export failed: {e}")

    print("\nDone. Open DXF in stgen-dxf-viewer for annotation (Stage 5).")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/sketch_hstab_assembly.py`

Expected output: DXF file created with projected views. Check that:
- Top view shows superellipse planform outline with spar lines
- Front view shows root airfoil shape with rod circles
- Right view shows span with thickness envelope

- [ ] **Step 3: View the PNG output and verify orientation**

Read the generated PNG file and verify:
- Top view: LE at one side, TE at the other, span visible
- Front view: airfoil shape visible
- Right view: span length visible
- No overlap between views

- [ ] **Step 4: Debug and fix any issues**

Common issues to check:
- If loft fails: reduce number of stations or simplify sections
- If views overlap: adjust gap parameter in calculate_layout
- If cylinder rotation is wrong: test Axis.X vs Axis.Z rotation
- If scale is too small: check bounding box calculations

- [ ] **Step 5: Commit working script**

```bash
git add scripts/sketch_hstab_assembly.py
git commit -m "feat: H-Stab assembly 3D sketch + projected 2D drawing"
```

---

### Task 5: MCP Annotation Workflow (Interactive)

**Files:** None (this is an interactive MCP workflow, documented here for reproducibility)

After the DXF is generated with correct geometry, use stgen-dxf-viewer MCP to add annotations. This task documents the exact MCP calls to make.

- [ ] **Step 1: Open the DXF in stgen-dxf-viewer and initialize**

```
1. Open cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf in VS Code
2. Call: get_dxf_summary()
3. Call: write_drawing_spec({
     drawingType: "assembly",
     scale: "<from layout>",
     unit: "mm",
     layerRules: {
       VISIBLE: "geometry outlines",
       HIDDEN: "hidden edges",
       DIM: "dimensions",
       TEXT: "labels and notes",
       BORDER: "sheet border",
       TITLEBLOCK: "title block"
     }
   })
4. Call: set_invariant_rules([
     {type: "spacing", rule: "min_text_spacing", value: 3},
     {type: "layer_assignment", rule: "dimensions_on_DIM_layer"},
     {type: "dimension_consistency", rule: "dim_text_matches_geometry"}
   ])
5. Call: update_work_plan({steps: [
     "Add sheet border and title block",
     "Add view labels",
     "Add dimensions to top view",
     "Add dimensions to front view",
     "Add component labels",
     "Add parts list",
     "Final quality check"
   ]})
```

- [ ] **Step 2: Add title block (in transaction)**

```
1. begin_transaction("title_block")
2. Create border rectangle for the sheet size
3. Create title block lines and text:
   - Drawing title: "AEROFORGE — HStab Assembly [AF-EMP-ASM-001]"
   - Subtitle: "Horizontal Stabilizer Assembly"
   - Material: "LW-PLA + CF tube/rod + Music wire"
   - Scale, date, mass, revision, status
4. end_transaction()
5. run_drawing_checks() — verify score >80
6. capture_dxf_view() — visual check
```

- [ ] **Step 3: Add dimensions and labels (in transactions)**

One transaction per view:
- Top view: span (430mm), root chord (115mm), spar position (35mm), hinge position (74.75mm)
- Front view: max thickness, chord, spar positions
- Labels: "TOP VIEW", "FRONT VIEW", "RIGHT VIEW", "FWD" arrow

- [ ] **Step 4: Final validation**

```
1. run_drawing_checks() — must score >80
2. check_geometry_quality() — no tiny gaps
3. check_dimension_consistency() — dim text matches geometry
4. capture_dxf_view() — final PNG for user review
```

- [ ] **Step 5: Commit annotated drawing**

```bash
git add cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf
git add cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.png
git commit -m "feat: H-Stab assembly drawing via Build123d projection pipeline"
```

---

### Task 6: Validate Pipeline is Reusable

**Files:**
- Test: `tests/cad/drawing/test_pipeline_integration.py`

- [ ] **Step 1: Write integration test**

```python
# tests/cad/drawing/test_pipeline_integration.py
"""Integration test: full pipeline from 3D shape to DXF."""
import os
import pytest
from build123d import Box


def test_full_pipeline_box(tmp_path):
    from src.cad.drawing.projector import project_standard_views, compute_2d_bounds
    from src.cad.drawing.layout import calculate_layout
    from src.cad.drawing.exporter import export_drawing

    # Simple box as stand-in for any component
    part = Box(100, 50, 10)

    # Project
    views = project_standard_views(part)
    assert len(views) == 3

    # Layout
    bounds = {}
    for name in ["top", "front", "right"]:
        bounds[name] = compute_2d_bounds(
            views[name]["visible"] + views[name]["hidden"]
        )
    layout = calculate_layout(bounds)
    assert layout["scale"] > 0

    # Export
    out = str(tmp_path / "test.dxf")
    export_drawing(views, layout, out)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 100

    # Verify DXF is readable
    import ezdxf
    doc = ezdxf.readfile(out)
    msp = doc.modelspace()
    entities = list(msp)
    assert len(entities) > 0  # has geometry
```

- [ ] **Step 2: Run integration test**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. pytest tests/cad/drawing/test_pipeline_integration.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/cad/drawing/test_pipeline_integration.py
git commit -m "test: add pipeline integration test for 2D drawing generation"
```
