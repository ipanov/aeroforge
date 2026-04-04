# AIR4 Example Project

`AIR4` is the current example program used to exercise the AeroForge framework.
It is an electric thermal sailplane project with tracked rounds, assembly
consensus files, monitored workflow state, and living BOM/procurement behavior.

## Why It Exists

AIR4 demonstrates:

- top-down aircraft definition before component drill-down
- tracked iteration rounds
- assembly-level consensus ownership
- deliverable discipline
- full-object validation intent
- BOM and procurement synchronization

## Example-Project Material

- `cad/assemblies/Iva_Aeroforge/`
- `cad/assemblies/wing/Wing_Assembly/`
- `cad/assemblies/fuselage/Fuselage_Assembly/`
- `cad/assemblies/empennage/HStab_Assembly/`
- [Project BOM artifact](../BOM.md)
- [Automatic glider workflow](../automatic_glider_workflow.md)

## Interpretation Rule

If AIR4-specific documents disagree with framework docs about concrete project
values, the AIR4 consensus files win for AIR4 itself. Framework docs remain the
generic platform definition.
