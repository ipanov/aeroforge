# Iva_Aeroforge Agent Context Package

## Purpose

This file is the aircraft-level context bundle for the mandatory aero/structural
feedback loop. It exists so the aerodynamic and structural agents operate from
the same top-down brief before a valid `DESIGN_CONSENSUS.md` is written.

## Aircraft Identity

- Project: `Iva_Aeroforge`
- Role: top-level F5J electric thermal glider assembly
- User naming: `Iva` is the aircraft name
- Assembly scope: whole aircraft first, then wings, fuselage, and lower-level
  component refinement

## User Direction

- The top-level assembly is the glider itself, not just a wrapper.
- The workflow must start from the whole plane, then propagate downward.
- Existing wing and fuselage work should be reused where justified, not
  destroyed.
- The H-stab assembly is the current quality bar and is treated as done for
  now, though later integration adjustments are allowed.
- The concept image provided in the session is a general visual reference only:
  slender integrated electric fuselage, long high-aspect-ratio wing,
  conventional H-stab, elegant glider proportions.
- Design philosophy: complexity is acceptable when it buys performance or
  integration quality. Do not accept oversimplified first-order geometry without
  review.

## Required Process Rule

Per `docs/superpowers/specs/2026-03-28-aero-structural-agent-team-design.md`,
the top-level aircraft assembly must go through a sequential aero/structural
feedback loop before its `DESIGN_CONSENSUS.md` is considered valid.

Round pattern:
1. Aero Proposal R1
2. Structural Review R1
3. Aero Response / Proposal R2
4. Structural Review R2
5. If still unresolved, continue to R3 max

For the active Iva loop, the repo has intentionally continued into R4 because
aircraft-level span, tail-mount geometry, and fuselage philosophy are still
being refined before 3D approval.

## Current Top-Level Inputs

- `cad/assemblies/Iva_Aeroforge/ASSEMBLY_INFO.md`
- `cad/assemblies/Iva_Aeroforge/DESIGN_CONSENSUS.md`
- `cad/assemblies/Iva_Aeroforge/AERO_PROPOSAL_IVA_R4.md`
- `cad/assemblies/Iva_Aeroforge/STRUCTURAL_REVIEW_IVA_R4.md`
  - R4 keeps span, H-stab mount geometry, and fuselage philosophy actively open.

## Current Subassembly Inputs

- `cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md`
- `cad/assemblies/wing/Wing_Assembly/AERO_RESPONSE_WING_R2.md`
- `cad/assemblies/fuselage/Fuselage_Assembly/DESIGN_CONSENSUS.md`
- `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md`

## Higher-Level Audit Inputs

- `docs/specifications.md`
- `docs/top_down_redesign_audit_2026-04-02.md`
- `docs/f5j_benchmark_lookup_2026-04-02.md`
  - Use this as the minimum external benchmark pack before proposing whole-aircraft geometry changes.
  - Treat it as a source-backed lookup rack, not as a copy target.
- `docs/automatic_glider_workflow.md`
  - This is the standing process rule for top-down and bottom-up iteration.
- `cad/assemblies/Iva_Aeroforge/TOP_LEVEL_RESEARCH_BRIEF_R4.md`
  - This captures the next open aircraft-level decisions before 3D modeling.

## Aircraft-Level Facts Already in Repo

- Wingspan: `2560 mm`
- Wing area: `41.6 dm^2`
- Wing root chord: `210 mm`
- Wing tip chord: `115 mm`
- Fuselage length: `1046 mm`
- Wing LE station: `260 mm` from nose
- H-stab pivot station: `911 mm` from nose
- Wing baseline:
  - AG24 root to AG03 tip
  - 4.0 deg washout, non-linear
  - 7.0 deg EDA polyhedral
  - 430 g total wing mass target
- Fuselage baseline:
  - integrated body, 5 print sections
  - 4 x 2 mm carbon longerons
  - 91 g fuselage subtotal
- H-stab baseline:
  - conventional fixed stab + elevator
  - 430 mm span
  - 29.33 g assembly mass

## Aircraft-Level Tensions To Resolve

1. The top-down audit says the current wing chord law may still be too
   first-order and should be compared against more curved / optimized options.
2. The fuselage section schedule exists, but the aircraft-level outer mold line
   may still be under-optimized.
3. The current aircraft mass baseline is about `886-906 g`, above the nominal
   `700-850 g` target band and near or above the desired ceiling.
4. The top-level datum, incidence, decalage, and integration assumptions need a
   real aircraft-level review instead of a wrapper-only acceptance.

## What The Agents Must Decide

- Which aircraft-level parameters are frozen now
- Which are provisionally accepted pending downstream refinement
- Which must be reopened in later loops
- Whether the current wing and fuselage layouts are acceptable aircraft-level
  baselines or need top-down changes
- What structural concerns the aerodynamic layout creates
- Whether the top-level concept image supports or contradicts the current repo
  geometry direction

## Deliverables Expected In This Folder

- `AERO_PROPOSAL_IVA_R1.md`
- `STRUCTURAL_REVIEW_IVA_R1.md`
- `AERO_RESPONSE_IVA_R2.md`
- `STRUCTURAL_REVIEW_IVA_R2.md`
- Updated `DESIGN_CONSENSUS.md`
