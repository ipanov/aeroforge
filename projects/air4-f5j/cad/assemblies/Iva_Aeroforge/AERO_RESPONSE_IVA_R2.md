## Aero Response: Iva Aeroforge Aircraft Assembly (R2)

**Author:** Aircraft-Level Aerodynamic Response
**Date:** 2026-04-02
**Responding To:** Structural Review of `Iva_Aeroforge` R1
**Status:** Round 2 response; aircraft baseline converges with provisional mass-closure items still open

### 1. Explicit Accept / Modify Decisions

| Item | Aero R2 Decision | Notes |
|------|------------------|-------|
| `X=260 mm` wing LE station | **ACCEPT** | Freeze as aircraft baseline |
| `X=911 mm` H-stab pivot station | **ACCEPT** | Freeze as aircraft baseline |
| Integrated fuselage concept | **ACCEPT** | No aerodynamic need to simplify OML |
| Fuselage OML refinement remains open | **ACCEPT** | Keep refinement open, but as a local optimization task |
| Prioritize mass recovery through architecture/allocation before reopening global geometry | **ACCEPT** | This is the correct next step |
| Restart current whole-aircraft layout now | **REJECT** | Expected aero gain is too small to justify discarding current wing/fuselage baseline |
| Current full wing-control architecture must be explicitly confirmed | **MODIFY / CLARIFY** | Keep current full-house baseline for now, but treat servo/control architecture as a mass-sensitive aircraft integration item, not frozen geometry |

### 2. Top-Level Mass / Performance Interpretation

The structural review is correct that the aircraft-level blocker is no longer primary geometry. It is now mass closure and systems definition.

Current aircraft baseline:
- AUW: about `886-906 g`
- Wing area: `41.6 dm^2`
- Wing loading: about `21.3-21.8 g/dm^2`

Aerodynamic interpretation:
- This is still a viable F5J-class aircraft loading
- It is no longer a light-air dominant loading
- The aircraft should still cruise, penetrate, and thermal adequately
- The penalty is mainly in weak-lift climb, minimum sink, and launch-to-search efficiency

Main aero conclusion:
- The current aircraft layout is aerodynamically valid, but the mass state is suppressing the value of the already-good wing and fuselage work.

### 3. Wing-Control Architecture Position

R2 decision: keep the current full wing-control architecture baseline at aircraft level unless and until the equipment table proves it cannot close mass.

Reasoning:
- full-house wing control is fully compatible with the aircraft mission
- it preserves landing authority, camber scheduling, and thermal/speed mode flexibility
- at aircraft level, changing the control architecture now is a systems/mass trade, not a reason to reopen wing placement or tail placement

However, the mass consequence must be stated explicitly:
- if the aircraft keeps the current full wing-control architecture, the mass budget stays under pressure and must be recovered elsewhere in equipment selection, servo count/spec, wiring, propulsion, and local structural allocation
- if later mass closure fails, the first reconsideration should be control/equipment architecture, not global aircraft geometry

### 4. Does the Current Layout Converge as Aircraft Baseline?

Yes.

The aircraft baseline now converges at the layout level because both aero and structural agree on:
- aircraft datum concept
- wing placement
- tail placement
- integrated fuselage concept
- reuse of current wing, fuselage, and H-stab baselines
- keeping local refinement open without resetting the whole aircraft

What does not yet converge is the final released aircraft configuration package, because these are still open:
- mass closure
- equipment allocation
- propulsion selection
- aircraft-level CG/equipment table
- final servo/control architecture signoff if weight remains too high

### 5. What Remains Provisional

The following stay provisional after R2:

1. Aircraft-level mass closure
- current `886-906 g` baseline is not yet signed off as final

2. Servo/control architecture as a finalized aircraft BOM decision
- full-house remains the aerodynamic baseline
- final signoff depends on system mass closure

3. Propulsion and electronics definition
- motor, ESC, prop/spinner, wiring, connector routing, and exact servo mix still need an aircraft-level table

4. Aircraft-level CG/equipment allocation
- battery, receiver, servos, propulsion, and wiring positions need to be tabulated against the `31-33% MAC` target

5. Local fuselage OML refinement
- keep open around nose, wing saddle, and boom transition
- this is refinement, not a restart trigger

6. Final incidence / decalage signoff
- the global stations are converged
- final trim numbers still need integration confirmation

### 6. Should Whole-Aircraft Geometry Be Reopened?

No, not at this stage.

Aerodynamic judgment:
- reopening the whole-aircraft layout now would likely yield only modest improvement relative to the disruption cost
- the largest current performance penalty is from mass and systems allocation, not from a fundamentally wrong planform/station layout
- any near-term aero gains from restarting wing/fuselage baseline geometry are unlikely to beat the practical gains available from mass recovery and equipment definition

Optimization order:
1. close aircraft systems mass and CG
2. confirm control architecture against that mass table
3. refine local OML only where it is low-risk and additive
4. reopen global geometry only if the mass/system solution still fails mission targets

### 7. What Should Go Into Final Consensus After R2

The final consensus should now include:

- Aircraft baseline accepted:
  - nose-tip datum
  - `X=260 mm` wing LE station
  - `X=911 mm` H-stab pivot station
  - integrated fuselage concept
  - current wing/fuselage/H-stab baselines reused at aircraft level

- Aircraft-level aero conclusion:
  - current layout is valid and converged as the top-level baseline
  - fuselage OML refinement remains open locally
  - no simplification mandate

- Aircraft-level mass conclusion:
  - current mass is above preferred target and is the main unresolved performance limiter
  - mass recovery should happen through system architecture/allocation first

- Control architecture conclusion:
  - full-house wing control remains the aero baseline
  - final release signoff depends on aircraft-level mass table and equipment allocation

- Remaining required artifacts:
  - aircraft-level equipment table
  - aircraft-level CG table
  - propulsion definition
  - final mass closure statement
  - final trim/incidence/decalage note

### 8. R2 Final Verdict

- Accept: current aircraft layout as the top-level baseline
- Accept: `X=260` and `X=911` as frozen structural/aerodynamic baselines
- Accept: integrated fuselage concept with refinement still open
- Modify: final consensus must remain conditional on mass/equipment/CG closure
- Reject: restarting whole-aircraft geometry at this point

Net result:
- the aircraft baseline converges in R2, with remaining work moved to aircraft systems definition and mass closure rather than global layout redesign

### 9. Explicit Inference Notes

Directly supported by the provided structural review summary:
- structural acceptance of current baseline layout
- structural acceptance of `X=260 mm` and `X=911 mm`
- acceptance of integrated fuselage concept
- open issues being mass closure, servo/control architecture conflict, propulsion/equipment uncertainty, and missing aircraft-level CG/equipment table

Inference in this R2 response:
- that full-house control should remain the default aero baseline unless mass closure proves otherwise
- that local OML refinement is lower-value than system mass recovery at this stage
- that restarting whole-aircraft geometry would not produce enough aerodynamic gain to justify discarding the present baseline
