## Structural Review: Iva Aeroforge Aircraft Assembly (R1)

**Author:** Aircraft-Level Structural Review
**Date:** 2026-04-02
**Reviewing:** `Aero Proposal: Iva Aeroforge Aircraft Assembly (R1)`
**Status:** Accept baseline layout with required mass/accounting corrections before final aircraft consensus

### 1. Mass Analysis

- Current whole-aircraft baseline from repo context: `886-906 g`
- Spec target band: `750-800 g`
- Practical ceiling from current project direction: `~850 g`
- Verdict: pass as interim integration baseline, not pass as final frozen aircraft target

Why:
- The aircraft is structurally plausible at `886-906 g`
- But that baseline is too heavy to treat as the final aircraft consensus for an F5J-focused layout
- The main issue is not gross structural infeasibility, but unresolved top-level mass closure

Primary mass concerns:
- The wing consensus implies a heavier systems/control architecture than the older aircraft specs budget
- There is a repo-level conflict between earlier servo-count assumptions and the current wing assembly concept
- Electronics/propulsion mass remains broad enough that CG and AUW are still too uncertain at aircraft level

### 2. Printability And Integration

- Current fuselage sectioning concept remains printable
- Current wing/fuselage/tail stationing does not create an obvious printability reason to move the geometry
- Complex aerodynamic OML is acceptable structurally if:
  - shell thickness does not collapse below manufacturing minimums
  - local saddle and spar-tunnel structure are reinforced where loads enter
  - section splits stay driven by print bed, access, and load transfer

Verdict:
- `Wing LE station X=260 mm`: accept
- `H-stab pivot station X=911 mm`: accept
- `Integrated fuselage concept`: accept
- `Complex fuselage shaping`: accept with structural constraints, not a reason to simplify the aircraft

### 3. Load Path Review

Current load path is directionally sound:

- Wing bending loads enter through the wing saddle and spar tunnel
- Fuselage carries those loads through the `4 x 2 mm` CF longeron system already defined in fuselage consensus
- Tail loads are modest relative to wing-root loads and remain compatible with the current aft-body concept
- H-stab station at `X=911 mm` is structurally acceptable if local bearing and fin-root reinforcement are preserved

Structural judgment:
- There is no aircraft-level reason in R1 to move the wing or tail stations
- The existing fuselage structural concept can support the current baseline aircraft
- The real remaining risk is local detail definition, not global layout

### 4. What Can Be Frozen Now

Freeze now:
- aircraft datum at nose tip / fuselage centerplane
- wing LE station at `X=260 mm`
- H-stab pivot station at `X=911 mm`
- current H-stab assembly as the top-level empennage baseline
- current wing and fuselage as the aircraft integration baseline

### 5. What Must Stay Provisional

Keep provisional:
- whole-aircraft mass budget
- final control-system architecture
- final propulsion mass assumption
- final CG closure
- wing chord-law optimization
- fuselage OML refinement near nose, saddle, and boom
- final incidence/decalage setup

### 6. What Must Be Modified Before Valid Final Consensus

Required before final aircraft consensus:
- reconcile the top-level mass budget with the current wing/fuselage/H-stab decisions
- resolve the servo/control architecture conflict at aircraft level
- add an aircraft-level CG and equipment placement table
- add explicit wing-root structural definition:
  - saddle walls
  - spar tunnel reinforcement
  - anti-crush / bolt-load strategy
- confirm exact mass trims that do not require a new aircraft layout

### 7. Direct Answers To Aero R1 Questions

1. Must layout force reduction below `850 g` now?
- No for R1 baseline integration
- Yes for final aircraft signoff if F5J performance remains the project goal

2. Can current longeron/saddle/spar-tunnel system carry the loads?
- Yes, provisionally
- Needs local root-detail definition, not a station move

3. Any structural reason to move wing LE from `X=260 mm`?
- No

4. Must fuselage OML become simpler?
- No
- Structural review does not require simplification; complexity is acceptable if printable and locally reinforced

5. Can H-stab remain at `X=911 mm`?
- Yes

6. Best structural mass-trim opportunities without new aircraft geometry?
- control-system architecture rationalization
- electronics/propulsion mass closure
- wing local hardware/detail simplification
- avoiding unnecessary reinforcement at aircraft-wrapper level

### 8. Requested Modifications For Aero Round 2

Please address these in Aero Round 2:

- confirm whether the aircraft is truly staying with the current full wing-control architecture, and update the aircraft-level mass consequences explicitly
- accept that `X=260 mm` wing LE and `X=911 mm` tail station are structurally acceptable baselines
- keep fuselage OML refinement open, but do not assume structural simplification is required
- prioritize mass recovery through system architecture and allocation before reopening global aircraft geometry
- state whether any aero benefit from changing the whole-aircraft layout is large enough to justify restarting the current wing/fuselage baseline

### 9. Structural Verdict

R1 Verdict: accept baseline aircraft layout with required mass-closure follow-up.

- Global layout: accept
- Stationing: accept
- Structural concept: accept
- Final aircraft consensus today: not yet
- Reason not yet: unresolved top-level mass/accounting and integration-detail closure, not a failed aircraft layout

### 10. Inference Notes

Directly supported by repo docs:
- wing LE `X=260 mm`
- H-stab pivot `X=911 mm`
- fuselage `4 x 2 mm` longeron concept
- existing wing/fuselage/H-stab consensus states
- current mass baseline near `886-906 g`

Inference from assembly-level integration reasoning:
- current stationing does not need to move for structural reasons
- mass closure is the main blocker to final aircraft consensus
- complex fuselage OML remains structurally acceptable if print constraints are respected
