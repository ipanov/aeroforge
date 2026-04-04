# Aero Proposal: Iva_Aeroforge Aircraft Layout (R4)

**Date:** 2026-04-02  
**Role:** Aircraft-level aerodynamic proposal  
**Scope:** Whole-aircraft span direction, tail placement philosophy, and fuselage aerodynamic direction before final 2D approval

---

## 1. Position

The aircraft architecture remains valid and should not be restarted.  
However, the next aircraft-level aerodynamic gains will not come from minor drafting cleanup. They depend on reopening three whole-aircraft questions:

1. span / aspect ratio direction  
2. H-stab position on the fin  
3. fuselage drag philosophy for a 3D-printed airframe

---

## 2. Recommendation Summary

- **Span:** recommend `2816 mm` as the preferred aircraft baseline candidate, with `2560 mm` retained as the fallback / reference variant and `3072 mm` kept only as an upper-bound comparison
- **H-stab placement:** move the H-stab **higher on the fin and slightly aft**, but do not turn the aircraft into a T-tail
- **Fuselage philosophy:** keep a **slender printed pod**, but do **not** optimize only for minimum frontal area; accept slightly more fullness where it buys better area progression, cooling volume, and cleaner wing-root / fin-body blending

---

## 3. Why This Direction Is Correct

### 3.1 Span

Current benchmark direction from official and manufacturer sources:
- top F5J aircraft cluster near the `4 m` class limit
- long span and high aspect ratio remain central to the class
- our current `2.56 m` aircraft is practical and compact, but clearly below the raw-performance envelope of current F5J practice

Source-backed context:
- `F5J` remains an active FAI class under the current sporting code  
  Source: https://www.fai.org/sites/default/files/sc4_vol_f5_electric_24_v2.pdf
- the benchmark pack already records the current elite-family pattern of long-span, refined F5J aircraft  
  Source: [f5j_benchmark_lookup_2026-04-02.md](/d:/Repos/aeroforge/docs/f5j_benchmark_lookup_2026-04-02.md)

Aircraft-level interpretation:
- `2816 mm` is a better next candidate than an immediate jump to `3072 mm`
- it moves Iva away from the visually stubby `2560 mm` baseline without taking the full structural and mass penalty of the largest stretch
- it still moves the aircraft toward a more credible F5J family reading without forcing a full architectural restart
- the active wing candidate for this next pass is:
  - span `2816 mm`
  - root chord `170 mm`
  - tip chord `85 mm`
  - tighter superelliptic taper
  - estimated area `~43.7 dm^2`
  - estimated aspect ratio `~18.2`

### 3.2 H-stab Position

The current low-mounted tail logic is not the right long-term answer for a precision-landing electric glider.

Reasons:
- low tail placement is vulnerable during landing
- a low mount produces an awkward visual and aerodynamic junction
- a slightly higher, slightly aft mount on the fin is more credible for clearance, durability, and tail-flow cleanliness

This does **not** mean a high T-tail.  
It means a more disciplined fin-top / fin-mid mount integrated into the fin fillet region.

### 3.3 Fuselage Philosophy

Do not chase the absolute smallest frontal area as if the aircraft were a molded carbon tube.

For this 3D-printed aircraft, the fuselage should prioritize:
- low drag in thermalling / minimum-sink conditions
- smooth spinner-to-pod transition
- clean wing-root and fin-body blending
- enough internal volume for battery, cooling, and CG management
- structural shell depth where the printed body needs it

That makes a disciplined teardrop / egg-like pod the right aerodynamic direction, even if it is slightly fuller than the thinnest composite-style tube.

---

## 4. Important Local Finding

The current shared superelliptic wing family materially changes the implied wing area relative to the older trapezoidal approximation in the specification files.

Repo-derived sizing check:
- the older broader `210 / 115 mm` superelliptic family grows area too much for a stretched wing
- the current tighter candidate `170 / 85 mm` at `2816 mm` closes back toward the intended wing area while improving proportion and aspect ratio

Interpretation:
- wing span and wing taper cannot be frozen independently
- the wing loop must reopen:
  - tip chord
  - outer-panel taper acceleration
  - wingtip treatment
  - span variant

This is an inference from the current repo geometry and is not yet a released aircraft value.

---

## 5. Freeze Now

- aircraft datum and centerplane
- current aircraft-level architecture as the governing parent object
- reuse of current wing, fuselage, and H-stab baselines
- the rule that off-the-shelf parts stay envelope-only at parent-sheet level
- the rule that the next meaningful aircraft decisions are:
  - span
  - tail mount
  - fuselage OML philosophy

---

## 6. Keep Open

- final span choice: `2560 mm` fallback vs `2816 mm` preferred candidate, with `3072 mm` only as an exploratory upper bound
- exact wing taper law
- exact wingtip concept
- final H-stab vertical offset and aft shift
- final rudder / elevator interference clearance geometry
- local fuselage OML at:
  - nose
  - wing saddle
  - boom taper
  - fin-body transition
- final incidence / decalage / trim signoff

---

## 7. Verdict

**APPROVE** the current aircraft architecture.  
**DO NOT RESTART** the aircraft from scratch.  
**REOPEN** the aircraft-level geometry only where it materially improves performance:

1. prefer `2816 mm` as the next candidate span  
2. move the H-stab higher and slightly aft on the fin  
3. keep a slender but not ultra-minimized printed fuselage  
4. reopen the wing taper / tip law together with the span decision
