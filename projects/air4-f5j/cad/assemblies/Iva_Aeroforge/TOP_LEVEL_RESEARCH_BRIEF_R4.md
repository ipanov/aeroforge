# Top-Level Research Brief R4

Date: 2026-04-02
Aircraft: `Iva_Aeroforge`
Purpose: document the next aircraft-level questions before the next aero / structural loop and before final 2D approval.

## Context

The aircraft has a valid top-level consensus, but several whole-aircraft choices are still open enough that they should be decided before 3D modeling:

- span / aspect ratio direction
- wing taper and tip strategy
- vertical tail design
- H-stab placement on the fin
- fuselage drag philosophy for a 3D-printed body
- landing robustness versus minimum drag

## Current Baseline

- wingspan: `2560 mm`
- fuselage length: `1046 mm`
- wing area: `~41.6 dm^2`
- aspect ratio: `~15.8`
- H-stab area: `~4.08 dm^2`
- H-stab volume coefficient already close to acceptable F5J baseline values
- integrated fuselage with printed shell and `4 x 2 mm` longerons

## External Benchmark Direction

Current benchmark pattern from official and manufacturer sources:
- elite F5J competition gliders live near the `4 m` class limit, with high aspect ratio and very refined tail and fuselage proportions
- official FAI F5J rules allow `maximum wingspan 4 m`
- current production competition gliders emphasize slender fuselages, full-house wings, and refined tails rather than crude triangular verticals

For AeroForge this means:
- our current `2.56 m` span is clearly in the compact / practical range, not the raw-performance optimum
- increasing span is a legitimate direction if the printer segmentation, spar strategy, and weight budget survive it

## Span / Aspect Ratio Recommendation

### Recommendation

Do not freeze the current `2560 mm` span as final.
Open a top-level span comparison immediately, but do not force it into an all-or-nothing extra-panel jump.

- Variant A: `2560 mm` baseline
- Variant B: `2816 mm` preferred stretch candidate using a shorter added tip-side section per half-wing
- Variant C: `3072 mm` exploratory full extra-panel case only if the shorter stretch still looks under-spanned after re-closing taper and mass

### Why this is the right next step

- the aircraft does not need to jump directly from `2.56 m` to `3.07 m`
- a shorter stretch around `2.8 m` keeps the airplane from looking stubby without taking the full structural penalty of the largest option
- `2816 mm` preserves the printed-section logic while giving a more credible F5J-like proportion
- `3072 mm` remains useful only as a high-end comparison case

### Active candidate geometry

The active wing candidate for the next parent-drawing pass is:
- span `2816 mm`
- root chord `170 mm`
- tip chord `85 mm`
- tighter superelliptic taper
- five `256 mm` sections plus one short `128 mm` tip section per half-wing

This candidate is preferred because it improves proportion and aspect ratio without letting wing area balloon out of control.

### Constraint

Any stretch variant is only acceptable if:
- AUW remains below `1000 g`
- wing stiffness and torsional integrity remain credible
- the longer span does not force a structurally ugly root section

## Wing Planform Recommendation

### Recommendation

Keep the superelliptic family, but reopen the exact taper law.

### Why

- the H-stab already established a coherent superelliptic visual language
- the current wing taper is cleaner than before, but it still has not earned “final” status
- the exact tip chord, TE behavior, and outer-panel taper acceleration should be decided inside the wing loop, not guessed at the aircraft level

### Required wing-loop comparison

Compare at least:
- baseline current superelliptic wing at `2560 mm`
- preferred stretch candidate at `2816 mm` with tightened taper
- exploratory `3072 mm` case only as an upper bound

## Wingtip Recommendation

Current temporary rounded tips are acceptable only as placeholders.

Required research comparison:
- simple rounded superelliptic tip
- polyhedral outer tip
- blended small winglet / tip fence concept
- pure span extension with no separate winglet

Because this is a 3D-printed aircraft, blended tip geometry is relatively cheap to manufacture and should be studied explicitly.

## Vertical Tail Recommendation

The current vertical tail should be reopened.

Required changes in principle:
- no low-mounted H-stab that is exposed to immediate landing damage
- no triangular placeholder fin
- same superelliptic family language as the H-stab
- enough dorsal / fillet blending into the fuselage to look and behave intentional

## H-Stab Placement Recommendation

### Recommendation

Move the H-stab mounting logic upward on the fin and slightly aft relative to the current low junction concept.

### Reasons

- better landing robustness for F5J precision landing use
- cleaner aerodynamic interaction than a crude low tail intersection
- more realistic clearance for elevator / rudder interaction

### Detailed design consequences

- H-stab should sit on the vertical tail fillet region, not low on the fuselage
- the H-stab should overlap the fin slightly in plan/side logic
- elevator inner corners should be chamfered or relieved so the rudder has free travel
- this requires a deliberate local fin + H-stab blend, not just two surfaces meeting

## Fuselage Philosophy Recommendation

Do not chase the absolute minimum frontal area at all costs.

For a 3D-printed F5J-like aircraft, the fuselage should instead optimize:
- low drag at thermalling and minimum-sink conditions
- enough volume for safe cooling and motor installation
- enough shell curvature and section depth for structural credibility
- enough nose/body volume for battery and CG management without ugly bulges

This means an egg / teardrop pod with disciplined area progression is a valid direction, even if it is slightly fuller than a composite tube fuselage.

The aerodynamic burden then shifts to:
- smooth spinner-to-pod transition
- clean wing-root saddle and fillet
- disciplined boom taper
- elegant fin-body blend

## Required Next Loops

### Aircraft-level next loop

The next aircraft aero / structural loop must decide:
- whether `3072 mm` becomes the new aircraft baseline
- whether the H-stab moves upward and aft on the vertical tail
- what tail-area consequences follow from the fuller printed fuselage philosophy

### Wing-level next loop

The wing loop must decide:
- final span variant
- exact taper law
- tip concept
- structural response to the stretch variant

### Fuselage-level next loop

The fuselage loop must decide:
- final side-view pod fullness
- wing fairing / saddle blend
- fin-body fairing
- tail mount geometry

## Pre-3D Approval Rule

Before 3D modeling:
- aircraft, wing, fuselage, and tail 2D drawings must all be approved
- the span direction must be frozen
- H-stab / fin geometry must be frozen
- fuselage side and top OML must be frozen at the parent-drawing level
