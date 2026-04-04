# Vase-Mode Slot Technique - Technical Analysis

Based on study of Vase-Wing (OpenSCAD) and industry references.

## How It Works

### The Core Principle
The wing is NOT a shell with separate internal ribs. It's a **single solid** with thin slots cut through it. These slots create walls that the slicer traces in vase mode.

### Construction in Vase-Wing (OpenSCAD)

**Step 1: Create the outer wing solid**
- Hull pairs of adjacent airfoil cross-sections along the span
- Each section is scaled to the local chord length
- Washout (twist) applied at each section
- Result: a solid wing-shaped body

**Step 2: Create the internal grid structure**
Two grid modes available:

**Mode 1 (Diamond grid):**
- A 3D grid of thin cubes (width = `slice_gap_width` = 0.01mm)
- Rotated 45 degrees to form diamond/diagonal pattern
- Grid spacing controlled by `grid_size_factor`
- The grid extends through the entire wing volume
- `StructureGrid()` creates cubes at regular intervals, rotated 45°
- Each cube is hollow: outer shell is `slice_gap_width/2` thick, interior is subtracted

**Mode 2 (Spar + cross-ribs):**
- Vertical spar walls running spanwise (parallel to spar direction)
- Cross-ribs at an angle (55 degrees from vertical in the code)
- Number of spars and ribs is configurable
- Spar walls are `slice_gap_width` (0.01mm) thick — essentially zero-thickness cuts

**Step 3: Boolean intersection**
- The grid is **intersected** with the wing solid using `difference()`
- Grid elements outside the airfoil shape are removed
- What remains: grid walls that exactly follow the internal contour of the airfoil

**Step 4: Subtract features**
- Spar hole: cylindrical void for carbon tube
- Rib voids: holes through the ribs for weight reduction
- Servo void: rectangular cutout for servo placement
- Aileron: control surface separation cut

### Key Parameters

| Parameter | Typical Value | Purpose |
|-----------|---------------|---------|
| `slice_gap_width` | 0.01mm | Gap in outer skin where grid intersects (slicer recognizes as path) |
| `slice_ext_width` | 0.6mm | Extrusion width (determines wall thickness) |
| `grid_size_factor` | 2 | Grid cell size = chord / factor / sqrt(2) |
| `spar_num` | 3 | Number of spanwise spar walls |
| `rib_num` | 6 | Number of angled cross-rib walls |
| `spar_offset` | 15mm | Offset from LE/TE for first/last spar |
| `rib_offset` | 1mm | Offset from root/tip for first/last rib |

### Why 0.01mm Gap Width?
The `slice_gap_width` is the critical dimension. It must be:
- Small enough that the slicer treats it as a **path to trace** (not a gap to skip)
- Large enough that the slicer **recognizes** the feature (>0 after floating-point)
- In practice: 0.01mm works with PrusaSlicer, Cura, OrcaSlicer, BambuStudio

When the slicer encounters these micro-gaps in the solid, it creates a continuous tool path that:
1. Traces the outer skin
2. Dips inward through the gap
3. Traces the internal wall
4. Returns to the outer skin through another gap
5. Continues the skin path

This is why it works in vase mode (spiralize outer contour) — the nozzle never lifts or retracts.

## Adaptation for FreeCAD/AeroForge

### What Changes
1. **Airfoil profiles** come from Build123d (exact AG NURBS), not OpenSCAD polygons
2. **Lofting** uses FreeCAD `Part.makeLoft()` instead of OpenSCAD `hull()`
3. **Grid creation** uses FreeCAD `Part.makeBox()` with rotation/translation
4. **Boolean operations** use FreeCAD `shape.common()` (intersection) and `shape.cut()` (difference)

### FreeCAD Implementation Plan

```python
# Pseudocode for FreeCAD Python implementation

# 1. Create wing solid
wing_wires = [make_airfoil_wire(span_frac) for span_frac in stations]
wing_solid = Part.makeLoft(wing_wires, solid=True)

# 2. Create grid structure
grid_elements = []
for i in range(n_spars):
    # Spanwise spar wall (thin box running full span)
    spar_wall = Part.makeBox(gap_width, chord*2, panel_span)
    spar_wall.translate(spar_position)
    grid_elements.append(spar_wall)

for j in range(n_ribs):
    # Angled cross-rib (rotated ~55 degrees)
    rib_wall = Part.makeBox(chord*2, chord*2, gap_width)
    rib_wall.rotate(center, axis, 55)
    rib_wall.translate(rib_position)
    grid_elements.append(rib_wall)

# 3. Fuse grid elements
grid = grid_elements[0]
for g in grid_elements[1:]:
    grid = grid.fuse(g)

# 4. Intersect grid with wing (trim to airfoil shape)
internal_structure = grid.common(wing_solid)

# 5. Combine wing + internal structure
final = wing_solid.fuse(internal_structure)

# 6. Subtract spar hole
spar_cylinder = Part.makeCylinder(spar_radius, panel_span, ...)
final = final.cut(spar_cylinder)
```

### Grid Mode Recommendation for AeroForge

**Use Mode 2 (Spar + cross-ribs)** because:
1. Gives explicit control over spar wall positions
2. Cross-ribs at 55° provide diagonal bracing
3. Number of ribs/spars is configurable per panel
4. Simpler Boolean operations than diamond grid
5. Better matches the structural load paths in a glider wing

### Wall Thickness Considerations

The 0.01mm gap width is the CAD geometry dimension. The actual wall thickness is determined by:
- Nozzle diameter (0.4mm standard)
- Extrusion width (0.6mm for LW-PLA with flow multiplier 0.45)
- Layer height (0.2mm typical)

The slicer interprets the 0.01mm gap as "trace a wall here" and creates a 0.6mm wide extrusion path.
