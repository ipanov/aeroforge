# Design Consensus: H-Stab Assembly (v3.1)

**Date:** 2026-03-30 (v3), 2026-03-29 mechanical detail (v3.1)
**Rounds:** 2 (R1: configuration decision + sizing → R2: planform upgrade + structural integration) + Round 3 mechanical detail
**Status:** AGREED — both agents signed off, user approved concept; mechanical integration details added in v3.1

---

## Agreed Specifications

| Parameter | Value | Source |
|-----------|-------|--------|
| Configuration | **Fixed stabilizer + 35% chord elevator** | Aero R1, Struct R1 approved |
| Planform | **Superellipse n=2.3** | Aero R2 — 0.75 ct savings at cruise, 5.9 ct at thermal |
| Root airfoil | **HT-13 (6.5%)** | Aero R1 — lowest CD0 at Re>50k |
| Tip airfoil | **HT-12 (5.1%)** | Aero R1 — lowest CD0 at Re=40k |
| Blend | **Linear HT-13 → HT-12, root to tip** | Every rib unique — 3D printing differentiator |
| Span | **430mm** (215mm per half) | Validated sizing from v1 |
| Root chord | **115mm** | Re 61,300 at 8 m/s |
| Tip chord (95% span) | **~50mm** | Superellipse taper |
| Mean chord | **94.8mm** | Derived |
| Area | **407.7 cm² (4.08 dm²)** | Derived |
| AR | **4.53** | Derived |
| Oswald e | **0.990** | Near-elliptical span loading |
| Vh | **0.393** | Acceptable for fixed+elevator |
| S_h/S_w | **9.8%** | Within F5J range (8.9-11.6%) |
| Tail moment arm | **651mm** | From fuselage consensus |
| LE sweep | **Continuous curvature** (superellipse) | No straight taper lines |
| Mass target | **34.2g (35g hard limit)** | Struct R2 verified, v3.1 updated |

## Elevator Specifications

| Parameter | Value |
|-----------|-------|
| Chord ratio | 35% of local chord |
| Hinge line | 65% chord from LE |
| Root elevator chord | 40.2mm |
| Tip elevator chord (95% span) | ~16.3mm |
| Elevator area | ~142.7 cm² |
| Deflection up (nose down) | -20 deg |
| Deflection down (nose up) | +25 deg |
| Max CL at 25 deg | +1.586 |
| Max CL at -20 deg | -1.333 |
| Peak L/D | 37.1 at 12 deg deflection |

## Hinge: Music Wire Pin (Infinite Life)

| Parameter | Value |
|-----------|-------|
| Type | Continuous music wire pin through interleaved PETG knuckle strips |
| Wire | 0.5mm spring steel (ASTM A228), 440mm |
| Wire mass | 0.68g |
| Fatigue life | **Infinite** (stress <1% of endurance limit) |
| Knuckle strips | PETG, solid, 215mm x 2mm x 1.2mm per half |
| Knuckle OD/ID | 1.2mm / 0.6mm |
| Knuckle spacing | 8mm center-to-center, alternating stab/elevator |
| Upper surface gap | 0.3mm (buried in BL, drag negligible) |
| Lower surface knuckles | 1.2mm protrusion (42% of turbulent BL, <0.05 ct drag) |
| Maintenance | **None, ever** |
| Proven by | 3DLabPrint, Kraga Kodo, Painless360 |

## Airfoil Blending Schedule

| Span station (eta) | Airfoil | t/c | Thickness (mm) | Chord (mm) |
|---------------------|---------|-----|----------------|------------|
| 0.00 (root) | HT-13 | 6.5% | 7.5 | 115.0 |
| 0.25 | Blend | 6.2% | 6.8 | 110.8 |
| 0.50 | Blend | 5.9% | 6.2 | 105.9 |
| 0.75 | Blend | 5.5% | 4.7 | 86.2 |
| 0.90 (spar end) | Blend | 5.3% | 3.3 | 62.7 |
| 0.95 | HT-12 | 5.1% | 2.6 | 50.0 |
| 1.00 (tip cap) | HT-12 | -- | 0 (closed) | 0 |

## Superellipse Chord Distribution

c(y) = 115 * [1 - |y/215|^2.3]^(1/2.3)

Key stations (per half, from root):

| y (mm) | Chord (mm) | Stab chord (65%) | Elevator chord (32%) |
|--------|------------|-------------------|----------------------|
| 0 | 115.0 | 74.8 | 36.8 |
| 50 | 113.2 | 73.6 | 36.2 |
| 100 | 105.9 | 68.9 | 33.9 |
| 150 | 89.6 | 58.2 | 28.7 |
| 195 | 57.3 | 37.2 | 18.3 |
| 210 | 32.0 | 20.8 | 10.2 |

## Structural Elements

| Element | Specification | Mass (g) |
|---------|--------------|----------|
| Main spar | 3mm CF tube (3/2mm OD/ID), 390mm | 2.40 |
| Rear spar | 1.5mm CF solid rod at 60% chord, 440mm | 1.20 |
| Elevator stiffener | 1mm CF solid rod at 80% chord, 340mm | 0.44 |
| Hinge wire | 0.5mm music wire, 440mm | 0.68 |
| PETG hinge strips | 4x (2 stab, 2 elevator), solid with knuckles | 2.00 |
| VStab junction fillet | 9.2mm radius, quartic polynomial, C2 continuous | (in fuselage budget) |
| VStab joint | Interlocking dovetail + CA | 0g |
| Mass balance | 1.0g tungsten putty on control horn forward extension | 1.00 |
| TE truncation | 97% chord (~0.7mm flat TE) | -- |

### Spar Notes
- Main spar terminates at 195mm of 215mm half-span (tip 20mm shell-only)
- Spar tunnel drifts from 25% chord at root to 30% chord at termination (gradual, 0.15 deg)
- Tunnel tapers from 3.1mm to 3.05mm ID at endpoint for friction fit
- Shell-only tip provides beneficial passive load relief (tip washout under gust)

## Components

| Component | Type | Material | Mass (g) |
|-----------|------|----------|----------|
| HStab_Left | Custom, printed | LW-PLA 0.45mm vase mode | 8.50 |
| HStab_Right | Custom, printed (mirror) | LW-PLA 0.45mm vase mode | 8.50 |
| Elevator_Left | Custom, printed | LW-PLA 0.40mm vase mode | 3.75 |
| Elevator_Right | Custom, printed (mirror) | LW-PLA 0.40mm vase mode | 3.75 |
| HStab_Hinge_Strip_Left | Custom, printed | PETG solid with knuckles | 0.50 |
| HStab_Hinge_Strip_Right | Custom, printed | PETG solid with knuckles | 0.50 |
| Elevator_Hinge_Strip_Left | Custom, printed | PETG solid with knuckles | 0.50 |
| Elevator_Hinge_Strip_Right | Custom, printed | PETG solid with knuckles | 0.50 |
| Control_Horn | Custom, printed | CF-PLA solid, with forward extension | 0.80 |
| HStab_Main_Spar | Off-shelf | 3mm CF tube 3/2mm, 390mm | 2.40 |
| HStab_Rear_Spar | Off-shelf | 1.5mm CF rod, 440mm | 1.20 |
| Elevator_Stiffener | Off-shelf | 1mm CF rod, 340mm | 0.44 |
| Hinge_Wire | Off-shelf | 0.5mm music wire, 440mm | 0.68 |
| Mass_Balance | Off-shelf | Tungsten putty | 1.00 |
| Elevator_Bridge_Joiner | Custom, printed | CF-PLA solid U-channel | 0.60 |
| **TOTAL** | | | **33.62g** |
| CA glue + Z-bend clevis | | | 0.55 |
| **GRAND TOTAL** | | | **34.17g** |

## VStab Junction Fillet

| Parameter | Value |
|-----------|-------|
| Fillet radius | 9.2mm |
| r/t ratio | 1.31 (>1.0 = ideal) |
| Profile | Quartic polynomial, C2 continuous |
| Drag reduction | 90% vs unfilleted junction |
| Construction | Printed as part of stab root (bond line hidden inside fillet) |
| Junction interlock | Dovetail tongue on VStab fin, slot in stab root |

## Performance

### Configuration Comparison (Why Fixed+Elevator Wins)

| Metric | All-Moving | Fixed+Elevator | Delta |
|--------|-----------|----------------|-------|
| Junction drag | 1.43 counts | 0.14 counts | **-1.30 ct** |
| Max CL authority | 0.88 | 1.59 | **+72%** |
| Drag at 8/10 operating points | Higher | **Lower** | Fixed wins |
| Total tail drag at trim | 0.001599 | 0.001510 | **-0.89 ct** |

### Planform Comparison (Why Superellipse Wins)

| Metric | Trapezoidal | Superellipse n=2.3 | Delta |
|--------|------------|---------------------|-------|
| Oswald e | 0.960 | 0.990 | +3.1% |
| Induced drag at trim | 23.21 ct | 22.46 ct | **-0.75 ct** |
| Induced drag at thermal | 183.14 ct | 177.25 ct | **-5.89 ct** |
| Shell mass | 30.0g | 29.9g | -0.1g |
| Print cost | Same | Same | Zero cost for curved LE |

### Tail System Performance

| Condition | Tail CL | Elevator Deflection | Total Tail CD |
|-----------|---------|--------------------|----|
| Cruise (8 m/s) | 0.178 | +2.7 deg | 0.003795 |
| Thermal (6 m/s) | 0.50 | +8.5 deg | 0.019839 |
| Flare (5 m/s) | 0.80 | +14 deg | 0.072380 |

## Print Strategy

| Part | Orientation | Mode | Material | Temp |
|------|-----------|------|----------|------|
| Stab halves | Flat, hinge face down | Vase mode (tip: 2-perimeter) | LW-PLA | 230°C |
| Elevator halves | Flat, hinge face down | Vase mode | LW-PLA | 230°C |
| Hinge strips | Flat, knuckles up | 100% solid | PETG | 240°C |
| Control horn | Flat | Solid, 1.2mm | CF-PLA | 220°C |
| Bridge joiner | Flat | Solid, 1.2mm | CF-PLA | 220°C |

## Assembly Sequence

1. Print all parts (4 LW-PLA shells, 4 PETG hinge strips, 1 control horn, 1 bridge joiner)
2. Bond hinge strips to stab TE faces and elevator LE faces (CA, lower surface)
3. Interleave knuckles: mate left stab + left elevator, right stab + right elevator
4. Thread 0.5mm music wire from left tip through all left knuckles, through VStab fin hole, through all right knuckles to right tip
5. Bend hinge wire 90° at each tip, tuck into tip fairing pockets
6. Test deflection range (-20° to +25°), verify smooth operation and bevel clearance
7. Install elevator bridge joiner: slide into left elevator root pocket (CA), then right elevator root pocket (CA)
8. Verify synchronization: deflect one half, confirm the other follows within 1°
9. Install rear spar (1.5mm rod through stab at 60% chord)
10. Install elevator stiffener (1mm rod through elevator at 80% chord, 340mm)
11. Thread main spar (3mm tube) through left stab → VStab fin → right stab
12. Bond stab roots to VStab fin (dovetail interlock + CA)
13. Bond control horn to left elevator (through slot in lower skin, CF pin + CA)
14. Pack tungsten putty into mass balance pocket, seal with cap
15. Route pushrod: thread 1mm wire through PTFE tube, connect Z-bend to control horn
16. Connect pushrod Z-bend to servo arm at X=350mm
17. Verify full deflection range with servo actuation, check for binding

## Elevator Bevel Angle (v3.1)

The stab TE face and elevator LE face are beveled asymmetrically to clear the full deflection range:

| Surface | Stab TE bevel | Elevator LE bevel | Total gap angle | Clears deflection |
|---------|--------------|-------------------|-----------------|-------------------|
| Upper | 11° aft-chamfer | 11° forward-chamfer | 22° | -20° + 2° margin |
| Lower | 14° aft-chamfer | 13° forward-chamfer | 27° | +25° + 2° margin |

The bevel starts at the hinge wire axis and opens toward each respective surface. The 0.3mm gap between the beveled faces is sufficient for friction-free rotation with manufacturing tolerance absorption.

## Rudder-Elevator Clearance (v3.1)

| Parameter | Value |
|-----------|-------|
| Elevator root gap (at hinge line) | 8.0mm (VStab fin 7mm + 0.5mm clearance each side) |
| Elevator root gap (at TE) | 10.2mm (adds rudder sweep clearance) |
| Rudder max lateral excursion at elevator TE overlap | ±4.6mm from VStab centerline |
| Hinge wire routing | Through 0.6mm hole in VStab fin at X=957mm (forward of rudder hinge at X=983) |
| PETG sleeve in fin hole | 1.2mm OD / 0.6mm ID, CA-bonded into fin |

The elevator hinge line (X=957mm) is 26mm FORWARD of the rudder hinge (X=983mm), so the hinge wire passes through solid VStab fin structure with no rudder interaction.

## Control Horn (v3.1)

| Parameter | Value |
|-----------|-------|
| Type | Custom 3D printed |
| Material | CF-PLA solid (1.2mm walls, 100% infill) |
| Location | Left elevator half, 15mm inboard from root |
| Horn height below elevator | 15mm |
| Horn width | 8mm (base), 5mm (tip) — tapered |
| Pushrod holes | 3 holes at 11, 13, 15mm below surface (1.6mm dia) |
| Connection type | Z-bend clevis (1.0mm wire through 1.6mm hole) |
| Mass balance arm | 12mm forward of hinge axis, 6x4x3mm putty pocket |
| Mounting | Through slot in elevator lower skin + CF pin + CA |
| Horn protrudes into | Root gap zone (between elevator root and VStab fin), no stab cutout needed |

## Elevator Bridge Joiner (v3.1)

Both elevator halves are synchronized by a rigid printed bridge that straddles the VStab fin:

| Parameter | Value |
|-----------|-------|
| Material | CF-PLA solid |
| Shape | U-shaped channel straddling VStab fin |
| Dimensions | 25mm span × 5mm H × 12mm W (1.2mm walls) |
| Bond length into each elevator | 12.5mm |
| Mass | 0.60g |
| Position | At elevator hinge line (X=957), below hinge axis |
| Combined torsional stiffness (bridge + wire) | 310.8 N-mm/rad |
| Max differential at Vne | 3.7° (acceptable) |
| Max differential at cruise | 0.4° (excellent synchronization) |

The 0.5mm hinge wire alone is insufficient to synchronize the halves (18.8° twist at Vne). The bridge joiner is essential.

## Pushrod Routing (v3.1)

| Parameter | Value |
|-----------|-------|
| Pushrod type | 1.0mm music wire in 2.0mm OD / 1.2mm ID PTFE tube |
| System | Bowden-style (rigid wire in low-friction tube) |
| Route | Servo (X=350) → boom interior → fin interior → exit VStab fin at X=957 → control horn |
| Exit slot | 1.5mm × 3mm oval in VStab fin left surface, PETG grommet |
| Wire length | ~650mm |
| System mass | ~5.5g (in fuselage wiring budget) |
| Servo | 9g class at X=350mm, Z-bend connection at servo arm |

## Elevator Tip Closure (v3.1)

| Parameter | Value |
|-----------|-------|
| Tip closure profile | Parabolic cap, integral part of elevator shell |
| Closure zone | y = 205mm to y = 213mm |
| Wall thickness in closure | 0.55mm (thicker than 0.40mm main shell) |
| Last hinge knuckle | y = 200mm |
| Wire extends to | y = 213mm, 90° bend, tucked into tip pocket |
| Stiffener rod terminates | y = 170mm (airfoil too thin beyond for 1mm rod) |
| Tip beyond y=200mm | Elastic flex zone, follows elevator deflection via shell compliance |

Full details in `ELEVATOR_MECHANICAL_DETAIL.md`.

## Trade-offs Made

| What Aero Wanted | What Structural Constrained | Resolution |
|-----------------|---------------------------|------------|
| All-moving tail (simpler) | Junction gap drag unacceptable | Fixed stab + elevator (1.30 ct saved) |
| 3mm solid CF rod spar | Overkill weight | 3mm CF tube 3/2mm (80% stiffness, 55% weight) |
| Full-span spar | Tip too thin for 3mm tube | Spar ends at 195mm, tip shell-only |
| 2mm rear spar | Oversized for fixed stab | 1.5mm rod (adequate, -1.0g) |
| TPU living hinge | Fails in 1-3 flights | Music wire pin hinge (infinite life) |
| No mass balance | Flutter certain at Vne | 1.0g tungsten on horn (non-negotiable) |
| No elevator stiffener | Elevator bending flutter | 1mm CF rod at 80% chord (+0.55g) |

## What Makes This Design Special (3D Printing Differentiator)

1. **C2-continuous VStab junction fillet** — impossible in balsa/composite construction, trivial in 3D printing. Eliminates 90% of junction interference drag.
2. **Superellipse planform** — curved leading edge at zero manufacturing cost. Oswald e = 0.99, saving 5.9 drag counts in thermals.
3. **Span-varying airfoil blend** — every rib station has a unique HT-13/HT-12 profile optimized for local Re. Impossible conventionally.
4. **Integrated with continuous fuselage** — the stab bonds directly to the VStab fin with a dovetail interlock, becoming part of the one-body airframe.
5. **Music wire pin hinge** — infinite-life hinge with 0.3mm upper-surface gap, proving that fixed+elevator can be aerodynamically cleaner than all-moving when 3D printing enables perfect fillets.

## Round History

**Round 1:** Aero: Fixed stab + 35% elevator + TPU hinge, trapezoidal planform, HT-13/HT-12, 25.5g. Struct: MODIFY — 7 changes (tube spar, mass balance, spar termination, smaller rear spar, elevator stiffener, thicker TPU hinge, dovetail joint). Mass corrected to 32g.
**Round 2:** Aero: Accepted all 7 mods, upgraded planform to superellipse n=2.3, mass 32.3g. Struct: ACCEPT all except hinge — TPU rejected (fails in 1 flight), replaced with music wire pin hinge (infinite life). Mass 33.7g. User approved concept.
**Round 3 (v3.1):** Mechanical integration detail: elevator bevel angles (asymmetric 22°/27°), rudder-elevator clearance (10.2mm root gap), control horn (CF-PLA, Z-bend, 15mm height, on left elevator), elevator bridge joiner (CF-PLA U-channel, 0.6g), pushrod routing (1mm wire in PTFE tube, X=350 to X=957), elevator tip closure (parabolic cap, knuckles end at y=200mm). Stiffener shortened to 340mm. Mass updated to 34.17g (within 35g limit).

## References

- Full aero analysis: `AERO_PROPOSAL_HSTAB_R1.md` (configuration decision), `AERO_PROPOSAL_HSTAB_R2.md` (planform + revisions)
- Structural reviews: `STRUCTURAL_REVIEW_HSTAB_R1.md`, `STRUCTURAL_REVIEW_HSTAB_R2.md`
- Mechanical integration: `ELEVATOR_MECHANICAL_DETAIL.md`
- NeuralFoil analysis script: `scripts/hstab_r2_analysis.py`
