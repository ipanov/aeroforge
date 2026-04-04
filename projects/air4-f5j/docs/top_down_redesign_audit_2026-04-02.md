# Top-Down Redesign Audit

Date: 2026-04-02
Checkpoint commit: `9c45e52` (`Checkpoint current CAD progress before top-down redesign`)

## Why this exists

The repository has enough geometry and consensus work to move forward, but the current wing and fuselage path has drifted away from the stated workflow in [CLAUDE.md](D:/Repos/aeroforge/CLAUDE.md) and the complexity philosophy in [README.md](D:/Repos/aeroforge/README.md). This note defines the gaps and the next review loop.

## What is already strong

### H-stab quality bar is materially higher than wing/fuselage

- The empennage path shows the intended quality level: multi-round aero/structural negotiation, explicit geometry schedules, hidden-hinge reasoning, mass budget, and mesh-visible internal structure. See [DESIGN_CONSENSUS.md](D:/Repos/aeroforge/cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md) and [ASSEMBLY_INFO.md](D:/Repos/aeroforge/cad/assemblies/empennage/HStab_Assembly/ASSEMBLY_INFO.md).
- The rendered assembly visibly exposes internal lattice structure, which matches the mesh-first philosophy and the "complexity is free" rule. See [isometric.png](D:/Repos/aeroforge/cad/assemblies/empennage/HStab_Assembly/renders/isometric.png).

### Wing and fuselage consensus are not empty

- The wing consensus already includes twist, polyhedral, spar step, control schedule, and mass budget. See [DESIGN_CONSENSUS.md](D:/Repos/aeroforge/cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md).
- The fuselage consensus already defines cross-section schedule, longeron layout, print sectioning, and integrated fin logic. See [DESIGN_CONSENSUS.md](D:/Repos/aeroforge/cad/assemblies/fuselage/Fuselage_Assembly/DESIGN_CONSENSUS.md).

## Where the current design is still too simplified

### 1. Wing planform is still a first-order answer, not the "leave no performance on the table" answer

- The accepted wing uses a simple trapezoidal root-to-tip chord definition with fixed root and tip chords and no documented higher-order optimization of planform curvature. This is explicit in [README.md](D:/Repos/aeroforge/README.md) and [docs/specifications.md](D:/Repos/aeroforge/docs/specifications.md), which still describe wing area as a trapezoidal approximation.
- The current consensus locks `210mm -> 115mm` chord with a direct blend and then adds twist and polyhedral on top. That is a reasonable first pass, but it is not evidence that quartic/superelliptic/elliptical-with-constraints alternatives were eliminated quantitatively. See [DESIGN_CONSENSUS.md](D:/Repos/aeroforge/cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md).
- The current panel realization is visibly a structural envelope model, not yet a mesh-driven printed wing with the same level of internal complexity as the H-stab. See [Wing_Panel_P1_isometric.png](D:/Repos/aeroforge/cad/components/wing/Wing_Panel_P1/renders/Wing_Panel_P1_isometric.png).
- P1 is modeled as a loft plus ribs and spars, but the path stops before mesh/3MF and before a full assembly-level validation loop. [COMPONENT_INFO.md](D:/Repos/aeroforge/cad/components/wing/Wing_Panel_P1/COMPONENT_INFO.md) explicitly says `Mesh + 3MF | NOT STARTED`.

### 2. Fuselage cross-sections are specified, but the external body is still under-optimized

- The fuselage consensus has a good station table, but it is still mostly a schedule of sections and packaging constraints rather than a demonstrated multi-objective aerodynamic body optimization. See [DESIGN_CONSENSUS.md](D:/Repos/aeroforge/cad/assemblies/fuselage/Fuselage_Assembly/DESIGN_CONSENSUS.md).
- [COMPONENT_INFO.md](D:/Repos/aeroforge/cad/components/fuselage/Fuselage_S1_Nose/COMPONENT_INFO.md) shows S1 as a packaging-driven section with practical internal zones, which is necessary, but this is not yet proof that the assembled full body has optimal curvature continuity, cross-sectional area ruling, spinner transition quality, or local interference minimization with the wing root.
- The current repo has section drawings and an S1 model, but not a validated full fuselage three-view that drives all downstream section geometry.

### 3. Off-the-shelf components are still mostly envelope models

- The receiver, battery, ESC, spinner, motor, propeller, and servos are generally dimensionally plausible but simplified for packaging. Examples:
  - [src/cad/hardware/servo.py](D:/Repos/aeroforge/src/cad/hardware/servo.py): box body + tabs + shaft boss, no horn geometry, no wire routing, no case undercuts, no spline detail.
  - [src/cad/hardware/battery.py](D:/Repos/aeroforge/src/cad/hardware/battery.py): filleted block with joints, not a detailed cell-pack-and-lead geometry.
  - [cad/components/propulsion/Folding_Prop_11x6/model.py](D:/Repos/aeroforge/cad/components/propulsion/Folding_Prop_11x6/model.py): explicitly described as a simplified envelope model.
  - [cad/components/propulsion/ZTW_Spider_30A_ESC/model.py](D:/Repos/aeroforge/cad/components/propulsion/ZTW_Spider_30A_ESC/model.py): explicitly a rectangular body with wire stubs.
- That level is sufficient for early packaging, but not sufficient if downstream inertia, local interference, cooling, and serviceability are meant to be credible.

## Where the process order drifted from top-down

### 1. The workflow says assembly drawing first, but the wing path is proceeding panel-first

- The mandatory workflow in [CLAUDE.md](D:/Repos/aeroforge/CLAUDE.md) requires research -> drawing -> model -> mesh -> assembly validation, and the user intent here is explicitly top-down.
- The wing repo state is currently the opposite in practice:
  - assembly consensus exists in [cad/assemblies/wing/Wing_Assembly](D:/Repos/aeroforge/cad/assemblies/wing/Wing_Assembly)
  - panel drawings and at least one panel model exist in [cad/components/wing](D:/Repos/aeroforge/cad/components/wing)
  - there is no completed wing assembly drawing + integrated model + validated render set
- That means the component breakdown is advancing before the top-level wing assembly has become the hard geometric source of truth.

### 2. The fuselage is section-first instead of aircraft-assembly-first

- The user goal is a full aircraft assembly, and the correct top-down starting point for that is the fuselage assembly three-view plus aircraft datum/coordinate system.
- The repo currently has a fuselage assembly consensus, then section drawings such as [Fuselage_S1_Nose_drawing.dxf](D:/Repos/aeroforge/cad/components/fuselage/Fuselage_S1_Nose/Fuselage_S1_Nose_drawing.dxf), but not a committed assembly-level fuselage drawing that all sections inherit from.
- That creates risk that S1, S2, S3, and fin sections converge locally but do not produce the best full-body outer mold line when assembled.

### 3. The dependency graph idea is not yet the operational driver

- The architecture promises dependency propagation from [README.md](D:/Repos/aeroforge/README.md), but the actual CAD path is still largely script-per-part and file-per-part.
- That is acceptable for the first buildout, but the next loop should formalize which aircraft-level parameters propagate into:
  - wing planform and joint geometry
  - fuselage wing saddle and spar tunnel geometry
  - tail moment arm and empennage placement
  - hardware bay positions and CG trim range

## Immediate conclusions

### Keep

- The H-stab review style and mesh-visible structural standard.
- The fuselage packaging rigor.
- The wing control/spar/twist mass-accounting rigor.

### Reject or reopen

- Any assumption that a trapezoidal wing with fixed root/tip chord is already "optimized enough."
- Any assumption that section-level fuselage work can continue before the full fuselage three-view and aircraft datum are locked.
- Any assumption that simplified off-the-shelf envelopes are good enough for final mass property and local-flow work.

## Next questions for the aerodynamicist

1. Wing planform:
   - What spanwise chord law beats the current trapezoid once structure and print sectioning are included: superellipse, quartic, piecewise Bezier, or constrained elliptical loading?
   - What is the best sweep distribution once CG, spinner clearance, and root interference are included?
   - Is 7 deg EDA still optimal after re-optimizing planform curvature and winglet geometry together?
   - Should the winglet remain a discrete appendage, or should the P5 tip become a continuous spiroid-like or curved tip concept within printability limits?

2. Wing section law:
   - Is direct AG24 -> AG03 blending still best, or should there be a non-linear airfoil schedule with a different mid-span family and local reflex/camber distribution?
   - Is the current twist law `-4.0 * eta^2.5` still best once the final planform changes, or should washout and control chord vary together?

3. Fuselage body:
   - Given the battery, receiver, motor, and wing root geometry, what is the best full-body outer mold line, not just the best section schedule?
   - Should the body use a stricter area-rule style progression around the wing saddle to reduce interference drag?
   - Is the current wing-fairing extension and fillet strategy actually optimal once the real wing root shape is updated?

4. Aircraft integration:
   - Where should the aircraft datum and reference frames be defined so all component placement, CG, and CFD exports become deterministic?

## Next questions for the structural engineer

1. Wing structure:
   - If the aerodynamicist proposes a curved/non-trapezoidal chord law, how should rib spacing, spar routing, and control-surface segmentation adapt without compromising printability?
   - Should the wing move from the current built-up rib/web concept to a mesh-derived shell closer to the H-stab lattice standard?
   - Where do the servo volumes, wire runs, ballast, and joiner sleeves force local thickening or reinforcement?

2. Fuselage structure:
   - Can the longeron layout remain four straight 2mm rods, or should the rod paths curve with the optimized body and wing saddle loads?
   - Are the current section breaks the best for stiffness, access, and print quality, or should they move to align with load path changes and hardware zones?
   - What local reinforcement is required around wing mount loads, spar tunnel loads, and nose-motor torque reaction once the final hardware geometry is no longer simplified?

3. Off-the-shelf integration:
   - Which components need exact external geometry versus just exact mass + CG + connector/wire envelope?
   - For the components that remain approximate, what error bounds are acceptable for mass properties and packaging clearance?

## Ordered next implementation steps

1. Create the fuselage assembly three-view drawing first.
   - Side, top, and front views.
   - Include aircraft datum, wing LE/MAC references, spinner interface, wing saddle, H-stab and rudder axes, and section break stations.

2. Re-open the wing assembly consensus before building more panel geometry.
   - Demand a quantified comparison among at least three chord-law / sweep / tip-shape families.
   - Treat the current trapezoidal solution as baseline A, not the final answer.

3. Upgrade off-the-shelf component fidelity selectively.
   - Keep exact mass and envelope for all.
   - Add true geometry where it matters for cooling, collisions, wiring, inertia, or aerodynamic exposure.

4. Only then derive component drawings bottom-up from the top-level assembly drawings.

5. After the first integrated aircraft assembly exists, run:
   - collision and containment validation
   - aircraft-level mass and CG aggregation
   - CFD / synthetic wind tunnel setup export
   - redesign loop on only the parts that move the result

## External geometry sourcing notes

- XT60 already has a stronger source path than the other off-the-shelf parts because it is imported from a reference STEP model in [xt60.py](D:/Repos/aeroforge/src/cad/hardware/xt60.py).
- The other off-the-shelf components should be split into:
  - exact-CAD candidates: motor, spinner, connector, receiver case
  - exact-envelope-plus-mass candidates: ESC, battery
  - exact-kinematic-envelope candidates: servos, folding prop

