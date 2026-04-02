# CAD Framework: Clear Skies-Style Folder Organization

**Status:** MANDATORY -- enforced by hooks (hard failure)
**Supersedes:** Any conflicting rules in other docs regarding component folder structure

## Core Principles

1. **Every single piece = Component** (TPU strip, carbon rod, screw, printed shell -- each gets its own folder)
2. **Anything with >1 piece = Assembly** (an H-stab with a hinge and elevator is an assembly of 3+ components)
3. **Components and assemblies have IDENTICAL folder structure**
4. **2D technical drawing MUST be created and approved BEFORE any 3D modeling**
5. **No special "master" level** -- the top-level airplane is just another assembly
6. **Hard enforcement via hooks** -- workflow fails if structure is violated

## Folder Structure

### Top-Level Layout

```
cad/
├── CAD_FRAMEWORK.md          # This file (rules reference)
├── components/               # All individual pieces
│   ├── empennage/            # Category grouping
│   │   ├── HStab_Left/       # One component
│   │   ├── Elevator_Left/    # Another component
│   │   └── TPU_Hinge_HStab/  # Even a hinge strip is a component
│   ├── wing/
│   │   ├── Panel_1_Root/
│   │   └── Spar_Main_8mm/
│   ├── fuselage/
│   │   ├── Pod_Left_Half/
│   │   └── Motor_Mount/
│   └── hardware/
│       ├── Servo_JX_933MG/
│       └── Screw_M2x8/
└── assemblies/
    ├── empennage/
    │   ├── HStab_Assembly/
    │   └── Empennage_Assembly/
    ├── wing/
    │   └── Wing_Left_Assembly/
    └── Iva_Aeroforge/        # Top-level assembly (just another assembly)
```

### Component Folder (Required Files)

Every component folder MUST contain these files in this order of creation:

```
ComponentName/
├── DESIGN_CONSENSUS.md           # For aerodynamic components: aero+structural agent agreement
├── ComponentName_drawing.dxf     # REQUIRED: 2D technical drawing (created FIRST)
├── ComponentName_drawing.png     # REQUIRED: PNG render of the drawing (for review)
├── ComponentName.FCStd           # 3D model (created AFTER drawing approval)
├── renders/                      # 4 standard views (created AFTER 3D model)
│   ├── ComponentName_isometric.png
│   ├── ComponentName_front.png
│   ├── ComponentName_top.png
│   └── ComponentName_right.png
└── COMPONENT_INFO.md             # Component documentation
```

### Assembly Folder (Required Files)

Every assembly folder MUST contain these files:

```
AssemblyName/
├── AssemblyName_drawing.dxf      # REQUIRED: 2D assembly drawing (created FIRST)
├── AssemblyName_drawing.png      # REQUIRED: PNG render of the drawing (for review)
├── AssemblyName.FCStd            # 3D assembly model (created AFTER drawing approval)
├── renders/                      # 4 standard views
│   ├── AssemblyName_isometric.png
│   ├── AssemblyName_front.png
│   ├── AssemblyName_top.png
│   └── AssemblyName_right.png
└── ASSEMBLY_INFO.md              # Assembly documentation (BOM, constraints, notes)
```

## Naming Conventions

### Folder Names
- **PascalCase** with underscores separating logical parts: `HStab_Left`, `Panel_1_Root`
- Category folders are **lowercase**: `empennage/`, `wing/`, `fuselage/`, `hardware/`
- No spaces, no special characters

### File Names
- Drawing: `{FolderName}_drawing.dxf` and `{FolderName}_drawing.png`
- Model: `{FolderName}.FCStd`
- Renders: `{FolderName}_{view}.png` where view is `isometric`, `front`, `top`, `right`
- Info: `COMPONENT_INFO.md` or `ASSEMBLY_INFO.md` (always uppercase)

### What Constitutes a Component vs Assembly

| Type | Definition | Examples |
|------|-----------|----------|
| **Component** | A single manufactured or purchased piece | Printed HStab shell, carbon rod, screw, TPU hinge strip, servo |
| **Assembly** | Two or more components joined together | HStab + hinge + elevator, wing panel + spar + ribs |

**Rule of thumb:** If you can pick it up as one piece without it falling apart, it is a component. If it requires joining (glue, screws, snap-fit), the joined result is an assembly.

**Off-the-shelf items** (servos, screws, carbon tubes) are still components. They get a folder with a drawing (can be simplified or from datasheet) and COMPONENT_INFO.md with supplier/specs.

## Workflow Order (MANDATORY)

### Phase 1: Drawing (2D)
1. Research the real component (reference photos, datasheets)
1b. **For aerodynamic components:** Run aero+structural agent feedback loop → DESIGN_CONSENSUS.md
2. Create 2D technical drawing as DXF with key dimensions, tolerances, materials
3. Export PNG render of the drawing
4. Save both to the component/assembly folder
5. **STOP: Drawing must be reviewed and approved before proceeding**

### Drawing Composition Rules (MANDATORY)

These are not optional style preferences. They are part of the acceptance criteria for any drawing.

1. **Use true orthographic projection layout.**
2. **Top, front, and side views must be aligned by projection.**
3. **Views of the same object on one sheet must share the same scale unless a detail view is explicitly labeled with a different scale.**
4. **Long-span parts on landscape sheets must normally be drawn horizontally.**
5. **Wing assembly sheets must show:**
   - top view with span horizontal
   - front view with the same span scale as the top view
   - side/profile or section/profile view clearly labeled
6. **Do not rotate a wing planform vertically on a landscape sheet just to make it fit.**
7. **Dimension placement must support manufacturing clarity and must not break the projection logic of the sheet.**
8. **A drawing can be geometrically correct and still be rejected for bad sheet composition.**

### Drawing Approval Gate

A drawing is **not approved** unless it passes both:

1. **Geometry gate** — the shape/dimensions match the consensus/spec
2. **Composition gate** — the orthographic sheet layout is professional and readable

Examples of composition-gate failure:

- top and front views using different apparent span scales
- wing drawn vertically on a landscape sheet without justification
- views dropped arbitrarily on the page instead of aligned by projection
- oversized empty fields with undersized primary views
- side/profile details shown without clear scale labeling

### Phase 2: 3D Model
6. Only after drawing approval: create 3D model in FreeCAD
7. Model dimensions MUST match the drawing exactly
8. Save as `.FCStd` in the component/assembly folder

### Phase 3: Renders
9. Take 4 standard view screenshots (isometric, front, top, right)
10. Save to `renders/` subfolder
11. Compare renders against the 2D drawing -- proportions must match

### Phase 4: Documentation
12. Write `COMPONENT_INFO.md` or `ASSEMBLY_INFO.md`
13. Include: description, dimensions, material, weight, notes

### Phase 5: Validation
14. Run dimensional tests (pytest assertions against specs)
15. Visual comparison of renders to reference
16. Both gates must pass before commit

## COMPONENT_INFO.md Template

```markdown
# Component: {Name}

## Description
{What this component is and its role in the sailplane}

## Specifications
| Parameter | Value | Source |
|-----------|-------|--------|
| Material  | {e.g., LW-PLA} | specifications.md |
| Length    | {mm} | drawing |
| Width     | {mm} | drawing |
| Height    | {mm} | drawing |
| Weight    | {g} | calculated/measured |

## Manufacturing
- Print orientation: {e.g., flat on bed, TE down}
- Material: {filament type}
- Wall thickness: {mm}
- Special notes: {e.g., vase mode, supports needed}

## Connections
- Connects to: {list of mating components/assemblies}
- Connection method: {glue, snap-fit, screw, slide-on}

## Drawing Approval
- Date: {YYYY-MM-DD}
- Approved by: {user/AI review}
- Drawing file: {filename}_drawing.dxf
```

## ASSEMBLY_INFO.md Template

```markdown
# Assembly: {Name}

## Description
{What this assembly is and its role in the sailplane}

## Bill of Materials
| # | Component | Qty | Source |
|---|-----------|-----|--------|
| 1 | {component name} | 1 | cad/components/{path} |
| 2 | {component name} | 1 | cad/components/{path} |

## Assembly Constraints
| Constraint | Component A | Component B | Type |
|-----------|------------|------------|------|
| 1 | {name} | {name} | {mate/align/insert} |

## Assembly Order
1. {First step}
2. {Second step}

## Specifications
| Parameter | Value |
|-----------|-------|
| Total weight | {g} |
| Envelope (LxWxH) | {mm x mm x mm} |

## Drawing Approval
- Date: {YYYY-MM-DD}
- Approved by: {user/AI review}
- Drawing file: {filename}_drawing.dxf
```

## Validation Hook

The enforcement hook `hooks/cad_structure_validate.py` checks:

1. Component folder has all required files (drawing, model, renders, docs)
2. Assembly folder has all required files
3. Naming conventions are followed
4. No `.FCStd` exists without a corresponding approved drawing (`.dxf`)
5. Renders folder has all 4 required views
6. `COMPONENT_INFO.md` or `ASSEMBLY_INFO.md` exists

The hook is called before commits that touch files in `cad/`. It BLOCKS (hard failure) if the structure is violated.

## Workflow States

A component/assembly progresses through these states:

| State | Required Files | Can Commit? |
|-------|---------------|-------------|
| **DRAWING** | `_drawing.dxf` + `_drawing.png` | Yes (drawing only) |
| **MODELED** | Drawing + `.FCStd` | No (needs renders) |
| **RENDERED** | Drawing + model + 4 renders | No (needs docs) |
| **COMPLETE** | All files present | Yes |

Partial states are allowed for in-progress work, but the hook enforces:
- No `.FCStd` without a `.dxf` (drawing-first rule)
- No commit of `.FCStd` without renders
- No commit of renders without info doc

## Migration Notes

Existing components created before this framework must be migrated:
- Add missing drawings (can be created retroactively from existing 3D models)
- Add missing COMPONENT_INFO.md / ASSEMBLY_INFO.md
- Ensure renders/ folder has all 4 views
- Ensure naming conventions match

## Category Index

Standard categories for organizing components and assemblies:

| Category | Contains |
|----------|---------|
| `empennage/` | H-stab, V-stab, elevators, rudder, tail mount, hinges |
| `wing/` | Wing panels, spars, ribs, ailerons, flaps, joiners |
| `fuselage/` | Pod halves, bulkheads, motor mount, servo mount, boom socket |
| `hardware/` | Servos, screws, carbon tubes, connectors, receivers, batteries |
| `propulsion/` | Motor, ESC, propeller, spinner, motor mount |
