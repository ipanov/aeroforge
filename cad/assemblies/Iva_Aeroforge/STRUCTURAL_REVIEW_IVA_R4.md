# Structural Review: Iva_Aeroforge Aircraft Layout (R4)

**Date:** 2026-04-02  
**Role:** Aircraft-level structural review  
**Scope:** Whole-aircraft structural response to span stretch, higher tail mount, and fuller printed fuselage philosophy

---

## 1. Position

The aircraft-level architecture remains structurally valid.  
The open question is not whether the whole aircraft must be restarted.  
The open question is which of the proposed aerodynamic improvements survive the mass, stiffness, and landing-robustness constraints of the printed airframe.

---

## 2. Structural Reading Of The R4 Questions

### 2.1 Span Stretch Beyond `2560 mm`

The stretch is structurally plausible, but it is **not** a trivial panel addition.

Reasons:
- the existing wing structural baseline was tuned around the `2560 mm` aircraft
- even a moderate stretch raises bending and tip-deflection demands
- the current wing mass budget is already aggressive relative to the aircraft-level weight target

Therefore:
- `2816 mm` is the most credible next structural candidate
- `3072 mm` should remain only an exploratory upper bound
- the active wing candidate should be understood as a tighter tapered wing, not the older broader `210 / 115 mm` superelliptic shape simply stretched outward
- no stretch should **not** be frozen until the wing structure proves:
  - acceptable bending stiffness
  - acceptable torsional stiffness
  - acceptable joint / segment continuity
  - AUW still below `1 kg`

### 2.2 Higher / Aft H-stab Mount

Moving the H-stab upward and slightly aft is structurally reasonable and likely better for landing robustness.

But it changes the local load path:
- more bending demand in the fin root
- more torsional demand in the upper fuselage / fin junction
- more importance on the local H-stab saddle and anti-rotation strategy

This move is acceptable only if:
- the fin becomes a real structural element, not a fairing
- the fin root closes into the fuselage shell and longerons cleanly
- local reinforcement is designed in the same loop

### 2.3 Fuller Printed Fuselage

A slightly fuller fuselage is structurally acceptable and likely preferable to an ultra-thin printed tube.

Benefits:
- more shell depth
- better packaging for battery, cooling, and routing
- better structural continuity in the wing saddle / spar tunnel region
- more realistic printed load paths

Risk:
- mass creep if the extra volume is not disciplined

So the correct structural interpretation is:
- fuller where it improves stiffness or packaging
- tapered aggressively where it does not
- no cosmetic bulk with no structural job

---

## 3. Freeze Now

- aircraft datum and coordinate references
- current aircraft stationing as the governing baseline
- reuse of current wing, fuselage, and H-stab baselines
- the `4 x 2 mm` longeron concept as the aircraft-level fuselage load-path baseline
- off-the-shelf components as envelope-only items at parent-drawing level

---

## 4. Keep Open

- final span choice
- final wing structural mass budget under the stretch option
- final H-stab mount height / aft shift
- local fin-root and tail-junction reinforcement
- final fuselage fullness limits
- whole-aircraft AUW closure
- aircraft-level CG closure

---

## 5. Risks

- primary risk: the stretch pushes AUW above `1 kg`
- secondary risk: the higher tail mount overloads the fin-root junction
- tertiary risk: fuller fuselage sections become dead mass instead of useful structure

---

## 6. Verdict

**KEEP `2560 mm` AS THE STRUCTURAL BASELINE UNTIL PROVEN OTHERWISE.**  
**ALLOW `2816 mm` TO CONTINUE AS THE PREFERRED AERODYNAMIC CANDIDATE UNDER STRUCTURAL REVIEW.**  
**KEEP `3072 mm` ONLY AS AN EXPLORATORY UPPER-BOUND CASE.**  
**ALLOW THE HIGHER / AFT H-STAB MOUNT ONLY IF THE FIN-ROOT LOAD PATH CLOSES IN THE SAME LOOP.**  
**ALLOW THE FULLER PRINTED FUSELAGE ONLY WITH STRICT MASS DISCIPLINE.**

The aircraft-level geometry itself is sound.  
The next structural work is closure, not restart.
