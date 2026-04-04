# Aero Proposal: Iva_Aeroforge Aircraft Layout (R3)

**Date:** 2026-04-02  
**Role:** Aircraft-level aerodynamic refinement memo  
**Scope:** Whole-glider parent layout only, not part-level CFD release

---

## 1. Position

The aircraft-level parent drawings are now materially closer to the intended F5J glider than the earlier wrapper-style sheet. The top-down layout is valid and should stay frozen at aircraft level while local refinements continue downward into wing, fuselage, and empennage detail.

---

## 2. What Improved In R3

- `scripts/draw_iva_assembly.py` now treats the aircraft as a true parent sheet, not as a placeholder wrapper.
- `scripts/draw_top_level_assemblies.py` now carries:
  - integrated fuselage + fin expression in side view
  - real hardware installation envelopes in fuselage parent drawings
  - root-interface, spar, hinge, and servo information in wing parent drawings
  - aircraft-level layout tied to the frozen aircraft stations
- The aircraft now reads closer to the uploaded concept image:
  - slender electric fuselage
  - long high-aspect wing
  - conventional H-stab
  - integrated vertical-tail body

Relevant repo files:
- `scripts/draw_iva_assembly.py`
- `scripts/draw_top_level_assemblies.py`
- `cad/assemblies/Iva_Aeroforge/DESIGN_CONSENSUS.md`

---

## 3. Freeze Now

- Aircraft identity: `Iva_Aeroforge` / `Iva`
- Aircraft datum: nose tip = `X=0`, centerplane = `Y=0`
- Wing LE station = `X=260 mm`
- H-stab pivot station = `X=911 mm`
- Integrated fuselage concept
- Conventional H-stab baseline
- Reuse of the current wing, fuselage, and H-stab baselines
- Decision not to restart the whole-aircraft geometry

---

## 4. Keep Open

- Whole-aircraft mass closure
- Aircraft-level CG closure
- Final propulsion package and cooling layout
- Final wing incidence / decalage / trim signoff
- Local fuselage OML refinement around:
  - nose
  - wing saddle
  - boom-to-fin transition
- Vertical-tail / rudder detail closure downstream
- Later chord-law refinement inside the frozen aircraft stationing

---

## 5. Parent-Drawing Policy

Aircraft parent drawings should own:
- airframe geometry
- interfaces
- packaging zones
- aerodynamic integration references

Aircraft parent drawings should not own:
- detailed vendor-part geometry for battery, motor, ESC, receiver, servos, spinner, or propeller

Those items should appear as **installation envelopes only**, with enough information for:
- space claim
- connector / wire direction
- cooling path
- interference / collision reasoning
- CG and mass accounting

---

## 6. Verdict

**APPROVE** the current R3 parent-drawing direction as the correct aircraft-level aerodynamic control sheet.

**DO NOT REOPEN** aircraft stationing.

**CONTINUE** with:
1. fuselage OML refinement
2. wing root / center-gap refinement
3. mass and CG closure
4. later synthetic analysis once the 3D aircraft baseline is mature
