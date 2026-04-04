# Design Consensus: Iva Aeroforge Aircraft Assembly (v3 with R4 active review)

**Date:** 2026-04-02
**Rounds:** 8 documents across 4 aircraft-level review rounds
**Status:** AGREED AS TOP-LEVEL LAYOUT CONSENSUS, WITH R4 ACTIVE ON SPAN / TAIL / FUSELAGE REFINEMENT

This document is backed by an actual aircraft-level aero/structural feedback loop:
- `AERO_PROPOSAL_IVA_R1.md`
- `STRUCTURAL_REVIEW_IVA_R1.md`
- `AERO_RESPONSE_IVA_R2.md`
- `STRUCTURAL_REVIEW_IVA_R2.md`
- `AERO_PROPOSAL_IVA_R3.md`
- `STRUCTURAL_REVIEW_IVA_R3.md`
- `AERO_PROPOSAL_IVA_R4.md`
- `STRUCTURAL_REVIEW_IVA_R4.md`

External benchmark input for subsequent rounds:
- `docs/f5j_benchmark_lookup_2026-04-02.md`

This remains a valid top-level layout consensus for the full aircraft. It is not yet a final release freeze for the aircraft configuration, and R4 explicitly keeps span, tail mount geometry, and fuselage refinement open.

---

## 1. Agreed Top-Level Layout

| Item | Decision | Status |
|------|----------|--------|
| Aircraft identity | `Iva Aeroforge` / `Iva_Aeroforge` | Frozen |
| Aircraft datum | Nose tip = `X=0`, fuselage centerplane = `Y=0` | Frozen |
| Wing LE station | `X=260 mm` from nose | Frozen |
| H-stab pivot station | `X=911 mm` from nose | Frozen |
| Tail moment arm | `~651 mm` | Accepted baseline |
| Wing assembly reuse | Reuse current `Wing_Assembly` consensus as aircraft baseline | Accepted baseline |
| Fuselage assembly reuse | Reuse current `Fuselage_Assembly` consensus as aircraft baseline | Accepted baseline |
| H-stab assembly reuse | Reuse current `HStab_Assembly` consensus as aircraft baseline | Accepted baseline |
| Global layout restart | Do not restart the whole-aircraft geometry in this loop | Rejected |

---

## 2. Aircraft-Level Aero Consensus

The aero rounds converged on the following:
- The current full-aircraft layout is aerodynamically valid as the top-level baseline.
- The uploaded concept image supports the same aircraft reading already emerging from the repo:
  - slender integrated electric F5J fuselage
  - long high-aspect wing
  - conventional H-stab
  - refined, non-simplified glider character
- The wing and fuselage should be preserved as the current aircraft baseline rather than discarded.
- The aerodynamicist explicitly rejected treating the aircraft assembly as a pure wrapper.
- The aerodynamicist also explicitly rejected restarting the whole aircraft now, because the expected gain is too small relative to the disruption.

### Aero items accepted now

| Item | Decision |
|------|----------|
| Integrated fuselage concept | Accept |
| Current wing placement | Accept |
| Current tail placement | Accept |
| Current H-stab as aircraft reference tail | Accept |
| No fuselage simplification mandate | Accept |

### Aero items still provisional

| Item | Why still open |
|------|----------------|
| Wing chord-law optimization | Current chord law is credible but not yet proven globally optimal |
| Wing sweep / tip refinement | Still open for later top-down refinement |
| Local fuselage OML refinement | Nose, wing saddle, and boom transition can still improve |
| Final incidence / decalage signoff | Needs integrated trim closure |

---

## 3. Aircraft-Level Structural Consensus

The structural rounds converged on the following:
- There is no aircraft-level structural reason to move the wing LE from `X=260 mm`.
- There is no aircraft-level structural reason to move the H-stab pivot from `X=911 mm`.
- The current `4 x 2 mm` CF longeron fuselage concept, wing saddle, and spar tunnel are acceptable as the top-level structural baseline.
- Complex fuselage shaping is allowed; structural review does not require the aircraft to become simpler.
- Remaining structural work is local detail closure and mass closure, not global layout restart.

### Structural items accepted now

| Item | Decision |
|------|----------|
| Wing LE station | Accept |
| H-stab pivot station | Accept |
| Integrated fuselage concept | Accept |
| Complex OML with local reinforcement | Accept |
| Reuse of current wing/fuselage/H-stab as aircraft baseline | Accept |

### Structural items still provisional

| Item | Why still open |
|------|----------------|
| Whole-aircraft mass closure | Current baseline is still heavy for final signoff |
| Aircraft-level equipment table | Needed for exact AUW and CG closure |
| Wing-root local detail definition | Saddle walls, spar tunnel reinforcement, anti-crush / bolt-load strategy |
| Final propulsion/electronics definition | Needed before final release freeze |

---

## 4. Mass And Performance Position

| Subsystem | Baseline mass |
|-----------|---------------|
| Wing assembly | `430 g` |
| Fuselage assembly | `~91 g` |
| H-stab / empennage baseline | `~35 g` at assembly-level tail budget |
| Electronics and power system | `~330-350 g` |
| Whole-aircraft baseline | `886-906 g` |

Mass interpretation from the aero + structural loop:
- `886-906 g` is acceptable as an interim integration baseline.
- `886-906 g` is not yet acceptable as a final released F5J-focused aircraft target.
- The main remaining performance limiter is mass and systems definition, not a failed aircraft layout.

Aircraft-level aerodynamic interpretation:
- wing loading remains plausible for flight at this mass
- weak-lift and minimum-sink performance are penalized versus the preferred target
- the biggest near-term gain now comes from mass recovery and equipment closure, not from restarting the layout

---

## 5. Control Architecture Position

The aircraft-level loop agreed on a conditional position:
- keep the current full-house wing-control architecture as the aerodynamic baseline for now
- do not freeze it as the final released aircraft control/BOM architecture until mass closure is complete
- if mass closure fails, revisit control/equipment architecture before reopening global aircraft geometry

This keeps the current wing work usable while acknowledging that servo count, servo class, wiring, and propulsion definition materially affect AUW and CG.

---

## 6. What Is Closed Vs Open

### Closed for top-level layout purposes

- aircraft identity
- aircraft datum
- wing placement
- tail placement
- integrated glider configuration
- reuse of current wing, fuselage, and H-stab baselines
- decision not to restart aircraft geometry from scratch in this loop

### Open for release-level closure

- final AUW closure
- aircraft-level equipment placement table
- aircraft-level CG table
- exact propulsion package
- final control-system signoff
- local fuselage OML refinement
- final incidence / decalage / trim signoff

Nothing above blocks top-level layout consensus. These items block only a final released aircraft configuration freeze.

---

## 7. Round History

| Round | File | Outcome |
|-------|------|---------|
| Aero R1 | `AERO_PROPOSAL_IVA_R1.md` | Accepted current aircraft as baseline, but kept wing chord law and fuselage OML provisional |
| Struct R1 | `STRUCTURAL_REVIEW_IVA_R1.md` | Accepted geometry/stationing; flagged mass closure and equipment/CG definition as remaining blockers |
| Aero R2 | `AERO_RESPONSE_IVA_R2.md` | Accepted structural position and rejected restarting the whole-aircraft geometry |
| Struct R2 | `STRUCTURAL_REVIEW_IVA_R2.md` | Confirmed top-level layout consensus is now valid, with explicit release-level conditions |

---

## 8. Final Verdict

- APPROVE: `Iva_Aeroforge` as a valid top-level aircraft layout consensus
- APPROVE: reuse of current wing, fuselage, and H-stab baselines at aircraft level
- APPROVE: frozen aircraft stations at `X=260 mm` wing LE and `X=911 mm` H-stab pivot
- KEEP OPEN: mass closure, equipment placement, CG closure, propulsion definition, and final trim signoff
- REJECT: restarting the whole-aircraft geometry in this loop

Next work should refine the aircraft from this agreed top-level baseline downward, while preserving the current subassembly work and only reopening the parts that materially improve mass, CG, or local aerodynamic quality.

---

## 9. R3 Parent-Drawing Refinement

Round 3 did not reopen the aircraft layout. It refined how the aircraft is represented and controlled at the 2D parent-sheet level.

### R3 outcomes

- The aircraft sheet is now treated as a real top-level parent drawing rather than a wrapper.
- The wing sheet now carries real parent-level interface information:
  - spar lines
  - hinge lines
  - servo envelopes
  - center-gap / root detail
- The fuselage sheet now carries real packaging and structural-installation information:
  - battery, ESC, receiver, and servo envelopes
  - spar tunnel
  - Bowden routing
  - integrated fin expression
- The aircraft sheet now visibly preserves:
  - datum
  - wing station
  - tail station
  - H-stab placement
  - off-the-shelf installation envelopes

### R3 freeze statement

R3 explicitly confirms:
- keep the aircraft stations frozen
- keep the wing, fuselage, and H-stab baselines
- continue refinement only inside the frozen aircraft architecture

---

## 10. Parent-Drawing Ownership Rule

The aircraft-level and parent-level assembly drawings must show off-the-shelf parts as **engineering envelopes only**.

---

## 11. R4 Active Direction

Round 4 does not invalidate the aircraft-level consensus.  
It reopens three specific aircraft-level variables before final 2D approval:

1. span / aspect ratio direction
2. H-stab position on the fin
3. fuselage fullness and blending philosophy

### R4 points of agreement

- keep the aircraft datum and major stationing logic
- keep the current aircraft architecture
- keep the wing, fuselage, and H-stab baselines reusable
- do not restart the whole aircraft
- continue using the benchmark lookup pack and workflow rules as mandatory context

### R4 tension that is still open

| Item | Aero position | Structural position |
|------|---------------|--------------------|
| Span | Prefer `2816 mm` candidate | Keep `2560 mm` as structural baseline until the stretch proves itself |
| H-stab mount | Move higher and slightly aft | Accept only if fin-root load path closes in the same loop |
| Fuller printed fuselage | Accept as the right aerodynamic philosophy | Accept only with strict mass discipline |

### R4 practical interpretation

- `2816 mm` is the preferred **candidate** direction for the next design loop.
- `2560 mm` remains the accepted **fallback / structural baseline** until the stretch variant is closed.
- `3072 mm` remains only as an exploratory upper-bound case.
- The H-stab should no longer be treated as a low-mounted tail.
- The fuselage should become cleaner and better blended, but not bloated.

### Active drawing-closure candidate

The current approval-target 2D drawing set is now using one tighter R4 candidate instead of leaving the tail trade unresolved:

- wing span `2816 mm`
- fuselage length `1088 mm`
- H-stab c/4 station `~X=946 mm`
- H-stab planform `446 mm` span, `118 mm` root chord, area `~4.21 dm^2`
- tail-volume target `~0.42`

This is still an active candidate pending 2D approval. It is the working closure point for the current drawing pass, not a claim that the older baseline tables were invalid.

### R4 implication for next work

The next drawing and research passes must decide:
- whether the stretch survives mass and stiffness closure
- the exact higher / aft H-stab geometry
- the final parent-level fuselage OML philosophy

Until then, the aircraft consensus remains valid, but not final.

### Show in parent drawings

- space claim
- mounting / containment zone
- connector or wire exit direction
- cooling implication
- CG and mass implication
- collision boundaries

### Do not create as owned engineering drawings at this stage

- battery
- motor
- ESC
- receiver
- servos
- spinner
- propeller

The parent drawings own the airframe geometry and interfaces, not the vendor part internals.

---

## 11. Updated Round History

| Round | File | Outcome |
|-------|------|---------|
| Aero R1 | `AERO_PROPOSAL_IVA_R1.md` | Accepted current aircraft as baseline, but kept wing chord law and fuselage OML provisional |
| Struct R1 | `STRUCTURAL_REVIEW_IVA_R1.md` | Accepted geometry/stationing; flagged mass closure and equipment/CG definition as remaining blockers |
| Aero R2 | `AERO_RESPONSE_IVA_R2.md` | Accepted structural position and rejected restarting the whole-aircraft geometry |
| Struct R2 | `STRUCTURAL_REVIEW_IVA_R2.md` | Confirmed top-level layout consensus is now valid, with explicit release-level conditions |
| Aero R3 | `AERO_PROPOSAL_IVA_R3.md` | Approved refined parent-drawing direction; froze aircraft layout and envelope policy |
| Struct R3 | `STRUCTURAL_REVIEW_IVA_R3.md` | Approved parent-level load-path / packaging representation; kept local closure items open |
