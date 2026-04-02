# Structural Review: Iva_Aeroforge Aircraft Layout (R3)

**Date:** 2026-04-02  
**Role:** Aircraft-level structural refinement memo  
**Scope:** Whole-glider load path and packaging policy, not local part FEA closure

---

## 1. Position

The R3 parent drawing direction is structurally correct for aircraft-level control. The sheet now shows the load-bearing architecture and installation logic clearly enough to continue top-down refinement without reopening the whole-aircraft layout.

---

## 2. What Improved In R3

- `scripts/draw_iva_assembly.py` now freezes the aircraft datum and key stations directly on the aircraft sheet.
- `scripts/draw_top_level_assemblies.py` now promotes structural layout cues into the parent drawings:
  - spar / hinge / root-interface information on the wing sheet
  - battery / ESC / receiver / servo envelopes on the fuselage sheet
  - spar tunnel, wing saddle, and Bowden-routing visibility in parent documentation
- `cad/assemblies/Iva_Aeroforge/ASSEMBLY_INFO.md` already defines the aircraft as a real root assembly, which is the correct structural workflow.

Relevant repo files:
- `scripts/draw_iva_assembly.py`
- `scripts/draw_top_level_assemblies.py`
- `cad/assemblies/Iva_Aeroforge/ASSEMBLY_INFO.md`
- `cad/assemblies/Iva_Aeroforge/DESIGN_CONSENSUS.md`

---

## 3. Freeze Now

- Aircraft datum and identity
- Wing LE station = `X=260 mm`
- H-stab pivot station = `X=911 mm`
- Reuse of current wing, fuselage, and H-stab baseline assemblies
- 4-longeron fuselage concept as the aircraft-level load path baseline
- Wing loads entering through the wing saddle / spar tunnel region
- Decision not to restart whole-aircraft geometry in this loop

---

## 4. Still Open

- Whole-aircraft mass recovery
- Final aircraft-level CG and equipment table
- Wing-root local closure:
  - saddle wall thickness
  - spar tunnel reinforcement
  - anti-crush / bolt-load strategy
- Final propulsion / equipment closure
- Final control-system and trim signoff

These are release-level blockers, not aircraft-layout blockers.

---

## 5. Off-The-Shelf Component Rule

Represent off-the-shelf components as **engineering envelopes with placement datums**, not as aircraft-owned detailed drawings.

Use envelopes for:
- battery
- ESC
- receiver
- servos
- motor
- spinner
- propeller
- wiring / connector clearance

The parent sheets must show:
- containment
- cooling / routing implications
- collision / interference boundaries
- mass and CG relevance

The parent sheets must not pretend to own vendor-internal geometry.

---

## 6. Verdict

**APPROVE** the current R3 structural direction.

The aircraft-level layout is stable enough to continue downward refinement.  
The next meaningful structural gains will come from:
1. mass closure
2. wing-root local engineering
3. equipment and wiring definition
