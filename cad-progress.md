# CAD Progress Tracker

## Component Status

| Component | Folder | Drawing | Model | Renders | Docs | Testing Gate | Validation Gate | Notes |
|-----------|--------|---------|-------|---------|------|-------------|-----------------|-------|
| MainSpar (8mm carbon tube) | -- | -- | -- | -- | -- | PASS | PASS | Built in FreeCAD, not yet in cad/ folder structure |
| HStab_Left | cad/components/empennage/HStab_Left | DONE | -- | -- | -- | -- | -- | Drawing created (DXF+PNG) |
| Elevator_Left | cad/components/empennage/Elevator_Left | -- | -- | -- | -- | -- | -- | Empty folder, needs drawing |
| Elevator_Right | cad/components/empennage/Elevator_Right | -- | -- | -- | -- | -- | -- | Empty folder, needs drawing |
| HStab_Right | cad/components/empennage/HStab_Right | -- | -- | -- | -- | -- | -- | Empty folder, needs drawing |
| TailMount_Block | cad/components/empennage/TailMount_Block | -- | -- | -- | -- | -- | -- | Empty folder, needs drawing |
| TPU_Hinge_HStab | cad/components/empennage/TPU_Hinge_HStab | -- | -- | -- | -- | -- | -- | Empty folder, needs drawing |

## Assembly Status

| Assembly | Folder | Drawing | Model | Renders | Docs | Notes |
|----------|--------|---------|-------|---------|------|-------|
| HStab_Assembly | cad/assemblies/empennage/HStab_Assembly | -- | -- | -- | -- | Empty folder |
| Empennage_Assembly | cad/assemblies/empennage/Empennage_Assembly | -- | -- | -- | -- | Empty folder |
| Iva_Aeroforge | cad/assemblies/Iva_Aeroforge | DRAWING | -- | -- | -- | Top-level aircraft wrapper |

## Migration Needed

The following items exist outside the cad/ folder structure and need migration:
- FreeCAD scripts in `scripts/` (build_hstab.py, build_hstab2.py, build_vstab_motor.py, build_fuselage.py, draw_hstab_left.py)
- FreeCAD scripts in `src/freecad_scripts/` (spar.py, empennage.py, fuselage.py, assembly.py, etc.)
- Build123d code in `src/cad/` (hardware/battery.py, hardware/servo.py, hardware/xt60.py, wing/panel.py)
- These scripts contain the parametric logic. They should be kept as generators but their outputs must go into the cad/ folder structure.

## Session Log

### 2026-03-28 — Enforcement Harness
- Created 3-layer hook infrastructure (PostToolUse, PreToolUse, PreCommit)
- FreeCAD RPC helper module with screenshot + bounding box queries
- Carbon spar tube TDD cycle: RED to GREEN with visual validation

### 2026-03-28 — CAD Framework Infrastructure
- Created cad/CAD_FRAMEWORK.md (Clear Skies folder organization rules)
- Created hooks/cad_structure_validate.py (folder structure enforcement hook)
- Updated CLAUDE.md with drawing-first workflow and folder structure rules
- Updated .claude/settings.json to wire the new hook
- Updated spec_registry.md with new files
- Added supersedence notes to workflow-redesign and enforcement-harness specs
- Next: Create drawings for all empty component/assembly folders
