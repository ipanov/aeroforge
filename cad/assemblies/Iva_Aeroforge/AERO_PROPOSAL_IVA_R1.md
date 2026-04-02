## Aero Proposal: Iva Aeroforge Aircraft Assembly (R1)

**Author:** Aircraft-Level Aerodynamic Review
**Date:** 2026-04-02
**Status:** Round 1 proposal for handoff to Structural Review

### 1. Operating Conditions

- Mission: F5J electric thermal glider, integrated printed fuselage, high-AR wing, conventional H-stab
- Design cruise speed: `8 m/s`
- Thermal speed band: `6.5-7.5 m/s`
- Fast penetration band: `10-13 m/s`
- Current wing area: `41.6 dm^2`
- Current AUW baseline from repo: `886-906 g`
- Wing loading at that mass: `21.3-21.8 g/dm^2`
- Root Reynolds number at `8 m/s`, `210 mm` chord: about `112,000`
- Mid-span Reynolds number at `8 m/s`, `~162-180 mm` chord: about `87,000-96,000`
- Tip Reynolds number at `8 m/s`, `115 mm` chord: about `61,000`

### 2. Aircraft-Level Layout

- Aircraft datum: freeze nose tip as `X=0`, fuselage centerplane as `Y=0`
- Wing LE station: freeze provisionally at `X=260 mm`
- H-stab pivot station: freeze provisionally at `X=911 mm`
- Tail moment arm from current repo geometry: about `651 mm`
- CG target for aircraft integration: `31-33% MAC`
- Acceptable trim envelope for early CAD: `30-35% MAC`

### 3. Whole-Aircraft Aero Reading

The current repo already points toward a coherent F5J aircraft:
- long, efficient `2.56 m` wing
- slender integrated fuselage rather than crude pod-and-boom
- conventional H-stab with good aerodynamic maturity
- moderate wing loading even at the present overweight baseline

The uploaded concept image reinforces this reading rather than changing it:
- slim nose and long tapering body
- wing visually dominant, fuselage subordinate
- conventional tail, not T-tail or V-tail
- integrated electric glider character, not simplified club trainer geometry

This is an inference from the image and current assembly docs, not a directly dimensioned drawing source.

### 4. Wing Position on R1

Recommendation: provisionally accept, not fully freeze.

Keep for aircraft R1:
- current span `2560 mm`
- current area `41.6 dm^2`
- current AG24 to AG03 family choice
- current non-linear `4.0 deg` washout
- current `7.0 deg` EDA/polyhedral baseline

Do not declare fully optimized yet:
- current chord law remains a credible baseline, but the top-down audit is right that it has not yet beaten curved alternatives quantitatively
- current sweep distribution is effectively unresolved at aircraft level
- tip concept may later evolve once winglet and whole-aircraft interference are reviewed together

Aircraft-level aero judgment:
- the current wing is good enough to anchor the aircraft layout
- the current wing is not yet proven to be the final top-down optimum

### 5. Fuselage Position on R1

Recommendation: provisionally accept, not fully freeze.

Keep for aircraft R1:
- integrated continuous fuselage concept
- current length `1046 mm`
- current max section around battery packaging
- current wing saddle / spar tunnel location
- current tail stationing

Do not fully freeze yet:
- outer mold line between nose, wing saddle, and boom is still under-optimized
- wing-root fairing and local area progression may still improve
- spinner-to-body transition and saddle-body continuity deserve a later aircraft-level refinement pass

Aircraft-level aero judgment:
- the fuselage concept is directionally correct
- the exact OML is still provisional

### 6. Incidence, Decalage, and Trim

For aircraft integration CAD, adopt this provisional setup:
- wing incidence relative to fuselage datum: `0.0 deg`
- H-stab reference setting: `0.0 deg` relative to aircraft datum for first assembly pass
- expected trim to be achieved through final decalage and CG tuning, not by moving major stations

This is an integration inference, not a locked result already proven by repo analysis.

### 7. Performance Implications of Current Mass

At `886-906 g`, the aircraft is still flyable and still within a plausible F5J-like loading band, but it gives away thermal margin:
- higher sink than a cleaner `750-820 g` solution
- weaker climb in soft lift
- less forgiving float and circle radius
- more pressure on the wing and fuselage to be genuinely low-drag

So the current aircraft layout is aerodynamically viable, but the mass baseline reduces how much benefit the refined wing and fuselage can realize.

### 8. Option Review

#### Option A: Treat current top-level assembly as a pure wrapper
- Reject
- This violates the top-down intent and leaves wing/fuselage assumptions unchallenged

#### Option B: Accept current wing + fuselage + H-stab as the aircraft baseline, but mark wing chord law and fuselage OML as provisional
- Selected for R1
- This preserves progress, creates a usable whole-aircraft source of truth, and still leaves room for real optimization

#### Option C: Reopen the entire aircraft geometry immediately before structural review
- Not recommended in R1
- Too disruptive before structural feasibility and mass reality are checked at whole-aircraft level

### 9. R1 Aero Conclusion

Aircraft-level recommendation: accept as baseline with provisional flags.

Freeze now:
- top-level aircraft identity and datum
- wing LE station at `260 mm`
- H-stab pivot station at `911 mm`
- current H-stab assembly as the reference empennage solution
- current wing and fuselage as aircraft-baseline geometry for integration

Keep provisional and explicitly reopen later:
- wing chord-law optimization
- wing sweep / tip refinement
- fuselage outer mold line around nose, saddle, and boom
- final incidence / decalage trim setup
- mass-driven drag optimization loop

### 10. Questions for Structural Round 1

1. Is the current aircraft mass baseline `886-906 g` acceptable as an interim structural target, or must the top-level layout immediately force reduction below `850 g`?
2. Can the current fuselage longeron, wing saddle, and spar tunnel system carry the wing loads at this aircraft mass without adding enough reinforcement to erase the aerodynamic benefit?
3. Does the current wing-root / fuselage integration create any structural or printability reason to move the wing LE station away from `X=260 mm`?
4. Is there any structural reason the fuselage OML must become simpler, or can aerodynamic refinement around the saddle and nose remain geometrically complex?
5. Does the current tail mounting and fuselage aft-body structure support keeping the H-stab station at `X=911 mm` with only local reinforcement?
6. Which top-level mass items are the most realistic structural trim opportunities without forcing a new aircraft geometry?

### 11. Explicit Inference Notes

Directly supported by repo docs:
- `2560 mm` span
- `41.6 dm^2` wing area
- `210/115 mm` wing chords
- `1046 mm` fuselage length
- `X=260 mm` wing LE station
- `X=911 mm` H-stab pivot station
- current wing, fuselage, and H-stab consensus states
- current mass baseline around `886-906 g`

Inference from current assembly state and concept image:
- use of `0.0 deg` / `0.0 deg` provisional incidence and tail setting for first aircraft CAD pass
- need to keep wing chord law and fuselage OML provisional rather than frozen
- interpretation that the concept image supports a slender integrated F5J form rather than a simpler fallback layout
