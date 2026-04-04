# H-Stab Redesign Spec: Fixed Stabilizer + Elevator

**Date:** 2026-03-30
**Status:** Approved — ready for implementation planning

## Summary

Complete redesign of the horizontal stabilizer, replacing the failed all-moving (v2) design with a fixed stabilizer + 35% chord elevator. The design exploits 3D printing's zero-cost complexity to create a perfectly blended VStab junction fillet and superelliptical planform.

## Design Decision: Why Fixed+Elevator Over All-Moving

The all-moving tail was rejected because the integrated VStab (part of the continuous fuselage) creates an unavoidable 3mm rotational gap at the junction — wider than the boundary layer — producing 1.30 drag counts of interference. A fixed stab allows a C2-continuous 3D-printed fillet that reduces this to 0.14 counts.

Additionally, the elevator wins at 8/10 operating points in total drag comparison and provides 72% more pitch authority (CL=1.59 vs 0.88). Every modern F5J competition sailplane uses fixed+elevator; all-moving is only found in RES balsa designs where hand-built fillets are impractical.

## Key Specifications

- **Planform**: Superellipse n=2.3 (Oswald e=0.990)
- **Span**: 430mm, Root: 115mm, Tip ~50mm at 95% span
- **Airfoil**: HT-13 (6.5%) root → HT-12 (5.1%) tip blend
- **Elevator**: 35% chord, hinge at 65%, -20° to +25°
- **Hinge**: 0.5mm music wire pin through PETG knuckle strips (infinite life)
- **Main spar**: 3mm CF tube (3/2mm), 390mm, ends at 195mm/half
- **Mass**: 33.7g (35g hard limit)
- **Junction**: 9.2mm radius C2 fillet + dovetail interlock

## Components (14 total)

4 LW-PLA shells (2 stab halves, 2 elevator halves), 4 PETG hinge strips, 1 control horn (CF-PLA), 3 CF rods/tubes, 1 music wire, 1 tungsten mass balance.

## Supporting Analysis

- `cad/assemblies/empennage/HStab_Assembly/AERO_PROPOSAL_HSTAB_R1.md` — Configuration decision (497 lines)
- `cad/assemblies/empennage/HStab_Assembly/STRUCTURAL_REVIEW_HSTAB_R1.md` — First structural review (905 lines)
- `cad/assemblies/empennage/HStab_Assembly/AERO_PROPOSAL_HSTAB_R2.md` — Revised proposal with superellipse (539 lines)
- `cad/assemblies/empennage/HStab_Assembly/STRUCTURAL_REVIEW_HSTAB_R2.md` — Final review + hinge solution (745 lines)
- `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md` — Agreed design

## Implementation Notes

- Drawing-first workflow: 2D DXF technical drawing must be created and approved before any 3D modeling
- Assembly validation: collision/containment checks required before renders
- The VStab junction fillet is printed as part of the stab root, not the VStab fin
- Stab halves bond to VStab fin via dovetail interlock (same approach as fuselage section joints)
