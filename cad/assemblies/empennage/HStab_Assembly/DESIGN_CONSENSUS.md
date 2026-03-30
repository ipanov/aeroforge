# Design Consensus: H-Stab Assembly (v4)

**Date:** 2026-03-30 (v3), 2026-03-29 (v3.1/v3.2), 2026-03-29 cleanup (v4)
**Rounds:** 2 (R1: configuration + sizing, R2: planform + structural) + R3 (mechanical detail, corrections, cleanup)
**Status:** AGREED — v4 consolidates corrections and defers integration details

---

## Agreed Specifications

| Parameter | Value | Source |
|-----------|-------|--------|
| Configuration | **Fixed stabilizer + 35% chord elevator** | Aero R1, Struct R1 approved |
| Planform | **Superellipse n=2.3** | Aero R2 — 0.75 ct savings at cruise, 5.9 ct at thermal |
| Planform alignment | **45%-chord line is straight** (optimal for spar + hinge) | v3.2 correction |
| Root airfoil | **HT-13 (6.5%)** | Aero R1 — lowest CD0 at Re>50k |
| Tip airfoil | **HT-12 (5.1%)** | Aero R1 — lowest CD0 at Re=40k |
| Blend | **Linear HT-13 to HT-12, root to tip** | Every rib unique — 3D printing differentiator |
| Span | **430mm** (215mm per half) | Validated sizing from v1 |
| Root chord | **115mm** | Re 61,300 at 8 m/s |
| Tip chord (95% span) | **~50mm** | Superellipse taper |
| Mean chord | **94.8mm** | Derived |
| Area | **407.7 cm2 (4.08 dm2)** | Derived |
| AR | **4.53** | Derived |
| Oswald e | **0.990** | Near-elliptical span loading |
| Vh | **0.393** | Acceptable for fixed+elevator |
| S_h/S_w | **9.8%** | Within F5J range (8.9-11.6%) |
| Tail moment arm | **651mm** | From fuselage consensus |
| LE sweep | **Continuous curvature** (superellipse) | No straight taper lines |
| Mass target | **33.8g (35g hard limit)** | v4 |

## Planform Alignment and Coordinate System

The superellipse planform is aligned on the **45%-chord line**, which remains at a constant X position across all span stations. This alignment was chosen because it minimizes chord-fraction drift for both the main spar (at 25% root chord) and the hinge wire (at 65% root chord), keeping both inside the airfoil profile to nearly full span.

**Coordinate system (local H-Stab):**
- **X axis**: chordwise, positive aft. X=0 at root LE.
- **Y axis**: spanwise, positive to the left. Y=0 at root (VStab fin centerline).
- **Z axis**: vertical, positive up.

**Fuselage station mapping:**
- H-Stab root LE = fuselage X=882.25mm (HStab c/4 at fuselage X=911mm)
- H-Stab root TE = fuselage X=997.25mm

**Planform formulas (local coords):**

```
c(y) = 115 * [1 - |y/215|^2.3]^(1/2.3)            Superellipse chord
x_LE(y) = 51.75 - 0.45 * c(y)                       Leading edge position
x_TE(y) = 51.75 + 0.55 * c(y)                       Trailing edge position
```

At the root (y=0): LE=0.00, TE=115.00. At y=100: LE=4.08, TE=110.02. At y=200: LE=28.86, TE=79.73.

## Elevator Specifications

| Parameter | Value |
|-----------|-------|
| Chord ratio | ~35% of local chord at root, varies with span (see table) |
| Hinge line | Fixed at X=74.75mm from root LE (perpendicular to fuselage CL) |
| Root elevator chord | 40.2mm |
| Tip elevator chord (y=200mm) | 5.0mm |
| Elevator chord reaches zero | y~204mm (geometric limit of hinge wire) |
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
| Knuckle strips | PETG, solid, 200mm x 2mm x 1.2mm per half |
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

## Comprehensive Chord and Rod Position Table

All four rods (main spar, rear spar, hinge wire, stiffener) are **ONE continuous straight piece each**, running perpendicular to the fuselage centerline (spanwise). Each rod is at a **fixed X position** (constant distance from root LE). The chord fraction each rod occupies **varies with span** as a geometric consequence of the tapered planform.

| y (mm) | Chord | LE_x | Spar X=28.75 | Rear X=69.0 | Hinge X=74.75 | Stiff X=92.0 | TE_x |
|--------|-------|------|-------------|-------------|---------------|-------------|------|
| 0 | 115.0 | 0.00 | 28.8 (25.0%) | 69.0 (60.0%) | 74.8 (65.0%) | 92.0 (80.0%) | 115.00 |
| 50 | 113.2 | 0.79 | 28.0 (24.7%) | 68.2 (60.3%) | 74.0 (65.3%) | 91.2 (80.6%) | 114.03 |
| 100 | 105.9 | 4.08 | 24.7 (23.3%) | 64.9 (61.3%) | 70.7 (66.8%) | 87.9 (83.1%) | 110.02 |
| 150 | 89.6 | 11.44 | 17.3 (19.3%) | 57.6 (64.2%) | 63.3 (70.7%) | 80.6 (89.9%) | 101.02 |
| 190 | 62.7 | 23.55 | 5.2 (8.3%) | 45.4 (72.5%) | 51.2 (81.7%) | exits | 86.21 |
| 195 | 57.3 | 25.98 | 2.8 (4.8%) | 43.0 (75.1%) | 48.8 (85.2%) | exits | 83.24 |
| 200 | 50.9 | 28.86 | exits | 40.1 (78.9%) | 45.9 (90.2%) | exits | 79.73 |
| 205 | 42.9 | 32.43 | exits | 36.6 (85.3%) | 42.3 (98.6%) | exits | 75.37 |
| 210 | 32.0 | 37.36 | exits | 31.6 (98.8%) | exits | exits | 69.34 |

**Key insight:** The v3.1 statement "spar tunnel drifts from 25% chord at root to 30% chord at termination" was misleading. The spar does NOT drift or angle — it is perfectly straight and perpendicular to the fuselage. The chord fraction changes because the **planform tapers around the spar**, not because the spar moves. At the root, the spar is at 25.0% chord; at y=195mm (termination), the LE has swept aft enough that the spar is at only 4.8% chord — very close to the leading edge.

## Structural Elements

| Element | Specification | Fixed X (mm) | Terminates at | Mass (g) |
|---------|--------------|-------------|---------------|----------|
| Main spar | 3mm CF tube (3/2mm OD/ID), 390mm | 28.75 | y=195mm per half (tip 20mm shell-only) | 2.40 |
| Rear spar | 1.5mm CF rod, 420mm | 69.00 | y=205mm per half (airfoil too thin beyond) | 1.15 |
| Hinge wire | 0.5mm music wire, 440mm | 74.75 | y=203mm per half (90-deg bend into tip pocket) | 0.68 |
| Elevator stiffener | 1mm CF rod, 300mm | 92.00 | y=150mm per half (airfoil too thin beyond) | 0.38 |
| PETG hinge strips | 4x, solid with knuckles | (on hinge line) | y=200mm (last knuckle) | 2.00 |
| VStab junction fillet | 9.2mm radius, quartic polynomial, C2 continuous | -- | -- | (in fuselage budget) |
| VStab joint | Interlocking dovetail + CA | -- | -- | 0g |
| Mass balance | 1.0g tungsten putty in tip horn pockets (0.5g per side) | -- | y=195-205mm | 1.00 |
| TE truncation | 97% chord (~0.7mm flat TE) | -- | -- | -- |

### Spar Geometry Notes

All four rods pass through the VStab fin at the HStab root station. The fin is 7mm thick at this point (HT-14/HT-12 blend at VStab tip). Each rod passes through a precisely drilled/printed hole in the fin:

| Rod | Hole in fin | Fit type |
|-----|-----------|----------|
| Main spar (3mm tube) | 3.1mm bore, PETG sleeve | Friction fit, tapers to 3.05mm at endpoint |
| Rear spar (1.5mm rod) | 1.6mm bore | Friction fit + CA |
| Hinge wire (0.5mm) | 0.6mm bore, PETG sleeve 1.2mm OD | Free rotation |
| Stiffener (1mm rod) | Does NOT pass through fin — starts at y=150mm each side | N/A |

**Important:** The stiffener does NOT pass through the VStab fin. It consists of TWO separate 150mm rods, one in each elevator half. This is because at y=0 (the root), the stiffener is at X=92mm from root LE = 80% chord = deep in the elevator zone. It cannot reach the fin (which is at y=0) because the elevator root face is ~4mm from the fin surface (see root gap below). Each stiffener rod is inserted from the root face of each elevator half and glued with CA.

### Rod Chord-Fraction Behavior

Because all rods are straight and the planform tapers, each rod experiences a characteristic drift in chord fraction:

- **Main spar (X=28.75):** Starts at 25.0% chord, drifts FORWARD toward LE as the LE sweeps aft. At termination (y=195), it is at 4.8% chord — barely inside the LE. This is acceptable because the spar provides bending stiffness regardless of chord position.
- **Rear spar (X=69.0):** Starts at 60.0%, drifts AFT toward TE. At y=205mm it is at 85.3% chord. Still safely inside the airfoil.
- **Hinge wire (X=74.75):** Starts at 65.0% chord (the designed hinge fraction), drifts AFT. At y=200mm it is at 90.2% chord, and at y~206mm it would exit the TE. The last hinge knuckle is at y=200mm; beyond that, the wire bends 90 degrees into a tip pocket.
- **Stiffener (X=92.0):** Starts at 80.0% chord, drifts AFT rapidly. The airfoil becomes too thin for a 1mm rod past y~160mm, so the stiffener terminates at y=150mm (89.9% chord at that station).

## Counter-Flutter Tip Horn

**The control horn is NOT a separate component.** It is an **integral part of the elevator tip**, printed as one piece with the elevator shell. Each elevator half has its own tip horn.

### Why the Tip (Not the Root)

The counter-flutter mass balance horn is placed at the **tip of the elevator**, not the root. This is the correct placement because:

1. **Tip closure function:** The stab shell (LE to hinge line) does NOT close the tip. The stab shell ends open at the tip. The **elevator** must close the tip of the entire H-stab. The tip horn is the forward extension that wraps around from the hinge line to form this closure.
2. **Maximum flutter prevention leverage:** The tip is the farthest point from the elevator spanwise CG (at y~85mm). Mass at the tip creates the largest moment about the torsional axis, providing the most effective flutter damping per gram.
3. **Aerodynamic tip fairing:** The horn smoothly closes the H-stab planform at the tip, eliminating tip vortex shedding from an open end.
4. **Pushrod attachment:** The pushrod runs along the elevator span from root to tip; the horn at the tip provides the actuation point.

### Horn Geometry

| Parameter | Value |
|-----------|-------|
| Type | Integral part of elevator shell (NOT a separate component) |
| Material | Same as elevator: LW-PLA vase mode (thickened to 0.55mm in horn zone) |
| Spanwise extent | y=195mm to y=210mm (last 15mm of H-stab span) |
| Forward extension | 15mm ahead of hinge line (X=74.75) into the stab zone |
| Aft extent | Follows the elevator TE taper to tip closure |
| Profile | Blended airfoil section transitioning to a streamlined tip cap |
| Tip closure | At y=210mm, the horn wraps fully around from LE to TE (chord=32mm) |

### Horn Plan-View Shape

At the tip, the stab shell chord (from LE to hinge) grows relative to the elevator chord (from hinge to TE), until at y~204mm the elevator chord reaches zero. Beyond y=204mm, the horn IS the entire remaining airfoil cross-section plus a forward extension.

```
               Stab LE
              /
y=195mm   ---/----------+------- Hinge line (X=74.75)
             |  STAB    |  ELEV (8.5mm chord)
y=200mm   ---/-------+--+------
             |  STAB  |horn extends fwd
y=205mm   ---/-----+--+--------
             | horn IS the tip
y=210mm   ---+---+-----------    Tip closure (chord=32mm, all horn)
              \ /
               V  (tip point at y=215mm)
```

The horn forward extension creates a pocket that is in the zone that would otherwise be "stab" — this is the mass balance cavity.

### Tungsten Putty Pocket

| Parameter | Value |
|-----------|-------|
| Location | Inside each tip horn, forward of hinge line |
| Pocket dimensions | 10mm span x 5mm chord x 2mm depth |
| Pocket volume | 100 mm3 per side |
| Tungsten mass | 0.50g per side (1.00g total) |
| Pocket center | y=200mm, 8mm forward of hinge line |
| Balance moment | 4.0 g-mm per side (8.0 g-mm total, both halves) |
| Sealing | Printed cap snaps over pocket after filling |

**Mass balance philosophy:** Full static balance of the elevator (CG at hinge line) would require ~6g of tungsten — impractical. For RC sailplanes at Vne < 20 m/s, **partial mass balance** (10-15% of control surface mass) is standard industry practice. Our 1.0g tungsten (13.3% of 7.5g elevator mass) combined with the **zero-slop music wire pin hinge** provides adequate flutter prevention within the flight envelope. Sources: Model Aviation, EAA, Hobby Squawk forums — all confirm partial balance is sufficient for sub-20 m/s RC aircraft when hinge slop is eliminated.

### Pushrod Attachment at Horn

| Parameter | Value |
|-----------|-------|
| Connection type | Z-bend clevis (1.0mm wire through 1.6mm hole) |
| Hole location | Horn lower surface, 12mm forward of hinge line, y=200mm |
| Alternate holes | 10mm and 14mm forward (for rate adjustment) |
| Wire exit | Through 2mm slot in horn lower surface |

## Elevator Tip Closure

The tip of the entire H-stab is closed by the **elevator**, not the stab shell. This is a fundamental geometric consequence of the fixed-X hinge line.

### How the Tip Closes

At the outboard tip, the hinge wire (at fixed X=74.75) occupies an increasing fraction of the local chord as the chord shrinks. At y~204mm, the hinge wire chord fraction reaches 100% — the entire remaining chord is "stab" (forward of hinge) and the elevator chord reaches zero.

The elevator tip closure works as follows:
1. **y=190 to 200mm:** Normal elevator with shrinking chord (11.5mm down to 5.0mm). Hinge knuckles present (last knuckle at y=200mm).
2. **y=200 to 204mm:** Elevator chord tapers to zero. The horn forward extension begins, wrapping around the hinge line from the elevator side into the stab zone.
3. **y=204 to 210mm:** The horn IS the tip. It spans from LE to TE, providing the full airfoil closure.
4. **y=210 to 215mm (tip cap):** Parabolic tip cap closing the airfoil to zero chord.

| Parameter | Value |
|-----------|-------|
| Tip closure zone | y=200mm to y=215mm |
| Wall thickness in closure | 0.55mm (thicker than 0.40mm main shell) |
| Last hinge knuckle | y=200mm |
| Hinge wire terminates | y=203mm, 90-deg bend tucked into tip pocket |
| Stiffener rod terminates | y=150mm (airfoil too thin beyond for 1mm rod) |
| Tip beyond y=200mm | Horn/closure zone, attached to elevator, deflects with elevator |

The stab shell ends at y~204mm with an open face at the hinge line. The elevator (with its horn) wraps around this open face to form the aerodynamic tip closure. When the elevator deflects, the entire tip (y=200-215mm) deflects with it, since the tip is part of the elevator. This is acceptable because the tip chord is very small at these stations and the aerodynamic effect is negligible.

## Elevator Root Gap and Rudder Clearance

| Parameter | Value |
|-----------|-------|
| Elevator root gap (total) | 8.0mm (VStab fin 7mm + 0.5mm clearance each side) |
| Gap shape | Parallel — no angled cut needed |
| Hinge wire routing | Through 0.6mm bore in VStab fin at X=74.75 from H-Stab root LE |
| PETG sleeve in fin hole | 1.2mm OD / 0.6mm ID, CA-bonded into fin |
| Bevel angles | Asymmetric: ~22 deg upper, ~27 deg lower (to clear -20/+25 deg deflection) |

**Rudder clearance: DEFERRED to integration phase.** The H-Stab position at fuselage X=911mm (c/4) may interact with the VStab rudder swing arc. Initial estimate suggests the elevator TE is forward of the rudder hinge at the H-Stab level, so no overlap is expected, but the exact clearance will be verified when the full tail assembly is integrated. No angled root cuts are planned unless integration testing shows interference.

## Elevator Bridge Joiner (TBD — detail in integration phase)

Both elevator halves need synchronization. The hinge wire alone provides insufficient torsional coupling. A rigid printed bridge (CF-PLA U-channel, ~0.6g) straddling the VStab fin is planned. Exact dimensions, stiffness analysis, and force path will be finalized during integration when the VStab fin geometry is confirmed.

## Pushrod Routing (brief — detail in integration phase)

| Parameter | Value |
|-----------|-------|
| Pushrod type | 1.0mm music wire in 2.0mm OD / 1.2mm ID PTFE tube (Bowden) |
| Route | Servo (fuselage X=350) -> fuselage boom -> VStab fin interior -> exits fin at H-Stab root -> inside left elevator -> tip horn |
| Tip connection | Z-bend clevis at tip horn, 12mm forward of hinge line |
| Total wire length | ~820mm |
| System mass | ~6.5g (in fuselage wiring budget, not in H-Stab mass) |

Detailed routing (guide clip spacing, exit slot geometry, root gap crossing) will be finalized during fuselage/tail integration.

## VStab Junction Fillet

| Parameter | Value |
|-----------|-------|
| Fillet radius | 9.2mm |
| r/t ratio | 1.31 (>1.0 = ideal) |
| Profile | Quartic polynomial, C2 continuous |
| Drag reduction | 90% vs unfilleted junction |
| Construction | Printed as part of stab root (bond line hidden inside fillet) |
| Junction interlock | Dovetail tongue on VStab fin, slot in stab root |

## Components (v4)

| Component | Type | Material | Mass (g) |
|-----------|------|----------|----------|
| HStab_Left | Custom, printed | LW-PLA 0.45mm vase mode | 8.50 |
| HStab_Right | Custom, printed (mirror) | LW-PLA 0.45mm vase mode | 8.50 |
| Elevator_Left (with integral tip horn) | Custom, printed | LW-PLA 0.40mm vase mode (0.55mm in horn zone) | 4.00 |
| Elevator_Right (with integral tip horn, mirror) | Custom, printed | LW-PLA 0.40mm vase mode (0.55mm in horn zone) | 4.00 |
| HStab_Hinge_Strip_Left | Custom, printed | PETG solid with knuckles | 0.50 |
| HStab_Hinge_Strip_Right | Custom, printed | PETG solid with knuckles | 0.50 |
| Elevator_Hinge_Strip_Left | Custom, printed | PETG solid with knuckles | 0.50 |
| Elevator_Hinge_Strip_Right | Custom, printed | PETG solid with knuckles | 0.50 |
| HStab_Main_Spar | Off-shelf | 3mm CF tube 3/2mm, 390mm | 2.40 |
| HStab_Rear_Spar | Off-shelf | 1.5mm CF rod, 420mm | 1.15 |
| Elevator_Stiffener_Left | Off-shelf | 1mm CF rod, 150mm | 0.19 |
| Elevator_Stiffener_Right | Off-shelf | 1mm CF rod, 150mm | 0.19 |
| Hinge_Wire | Off-shelf | 0.5mm music wire, 440mm | 0.68 |
| Mass_Balance | Off-shelf | Tungsten putty, 0.5g per tip horn | 1.00 |
| Elevator_Bridge_Joiner (TBD) | Custom, printed | CF-PLA solid U-channel | 0.60 |
| **TOTAL** | | | **33.21g** |
| CA glue + Z-bend clevis | | | 0.55 |
| **GRAND TOTAL** | | | **33.76g** |

Note: Control_Horn is NOT a separate component -- the horn is integral to each Elevator shell (tip horn). The Elevator_Bridge_Joiner is retained as TBD pending integration-phase verification of the VStab fin geometry.

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
| Stab halves | Flat, hinge face down | Vase mode (tip: 2-perimeter) | LW-PLA | 230 C |
| Elevator halves (with tip horn) | Flat, hinge face down | Vase mode (horn: 2-perimeter 0.55mm) | LW-PLA | 230 C |
| Hinge strips | Flat, knuckles up | 100% solid | PETG | 240 C |
| Bridge joiner | Flat | Solid, 1.2mm | CF-PLA | 220 C |

## Assembly Sequence

1. Print all parts: 2 stab shells, 2 elevator shells (each with integral tip horn), 4 PETG hinge strips, 1 bridge joiner
2. Bond hinge strips to stab TE faces and elevator LE faces (CA, lower surface)
3. Interleave knuckles: mate left stab + left elevator, right stab + right elevator
4. Thread 0.5mm music wire from left tip through all left knuckles, through VStab fin bore, through all right knuckles to right tip
5. Bend hinge wire 90 deg at each tip (y=203mm), tuck into tip horn pockets
6. Test deflection range (-20 deg to +25 deg), verify smooth operation and bevel clearance
7. Install elevator bridge joiner: slide into left elevator root pocket (CA), then right elevator root pocket (CA)
8. Verify synchronization: deflect one half, confirm the other follows within 1 deg
9. Install rear spar (1.5mm CF rod, 420mm): thread through left stab at X=69mm, through VStab fin bore, through right stab
10. Insert elevator stiffener rods: push 1mm CF rod into left elevator from root face (150mm deep, CA), repeat for right
11. Thread main spar (3mm CF tube, 390mm): through left stab at X=28.75mm, through VStab fin bore, through right stab
12. Bond stab roots to VStab fin (dovetail interlock + CA)
13. Pack tungsten putty into left tip horn pocket (0.5g), snap cap shut. Repeat for right.
14. Route pushrod: thread 1mm wire through PTFE tube in fuselage, through VStab fin exit slot, through left elevator root face, along elevator span with guide clips, Z-bend through tip horn hole
15. Connect pushrod PTFE tube to servo arm at fuselage X=350mm
16. Verify full deflection range with servo actuation, check for binding

## Trade-offs Made

| What Aero Wanted | What Structural Constrained | Resolution |
|-----------------|---------------------------|------------|
| All-moving tail (simpler) | Junction gap drag unacceptable | Fixed stab + elevator (1.30 ct saved) |
| 3mm solid CF rod spar | Overkill weight | 3mm CF tube 3/2mm (80% stiffness, 55% weight) |
| Full-span spar | Tip too thin for 3mm tube | Spar ends at 195mm, tip shell-only |
| 2mm rear spar | Oversized for fixed stab | 1.5mm rod (adequate, -1.0g) |
| TPU living hinge | Fails in 1-3 flights | Music wire pin hinge (infinite life) |
| No mass balance | Flutter risk at Vne | 1.0g tungsten in tip horns (partial balance, 13.3%) |
| No elevator stiffener | Elevator bending flutter | 1mm CF rod at 80% chord (+0.38g) |
| Separate control horn at root | Adds 0.8g, wrong placement | Integral elevator tip horn (saves weight, provides tip closure + flutter prevention) |
| Full static balance | Would need 6g tungsten | Partial balance (1g) + zero-slop hinge = adequate for Vne<20 m/s |

## What Makes This Design Special (3D Printing Differentiator)

1. **C2-continuous VStab junction fillet** — impossible in balsa/composite construction, trivial in 3D printing. Eliminates 90% of junction interference drag.
2. **Superellipse planform** — curved leading edge at zero manufacturing cost. Oswald e = 0.99, saving 5.9 drag counts in thermals.
3. **Span-varying airfoil blend** — every rib station has a unique HT-13/HT-12 profile optimized for local Re. Impossible conventionally.
4. **Integrated tip horn/closure** — the elevator tip wraps forward past the hinge to form the tip fairing, mass balance cavity, and pushrod attachment. One printed piece does three jobs.
5. **Music wire pin hinge** — infinite-life hinge with 0.3mm upper-surface gap, proving that fixed+elevator can be aerodynamically cleaner than all-moving when 3D printing enables perfect fillets.
6. **Internal pushrod routing** — pushrod runs inside the elevator shell from root to tip horn, invisible externally. No external horn or linkage protrusion.

## Round History

**Round 1:** Aero: Fixed stab + 35% elevator + TPU hinge, trapezoidal planform, HT-13/HT-12, 25.5g. Struct: MODIFY — 7 changes (tube spar, mass balance, spar termination, smaller rear spar, elevator stiffener, thicker TPU hinge, dovetail joint). Mass corrected to 32g.
**Round 2:** Aero: Accepted all 7 mods, upgraded planform to superellipse n=2.3, mass 32.3g. Struct: ACCEPT all except hinge — TPU rejected (fails in 1 flight), replaced with music wire pin hinge (infinite life). Mass 33.7g. User approved concept.
**Round 3 (v3.1):** Mechanical integration detail: elevator bevel angles (asymmetric 22/27 deg), rudder-elevator clearance, control horn (CF-PLA, Z-bend, 15mm height, on left elevator root), elevator bridge joiner (CF-PLA U-channel, 0.6g), pushrod routing (1mm wire in PTFE tube, X=350 to X=957), elevator tip closure (parabolic cap, knuckles end at y=200mm). Stiffener shortened to 340mm. Mass 34.17g.
**Round 3 (v3.2):** Critical corrections: spar geometry (all rods straight/perpendicular at fixed X), control horn moved to tip (integral to elevator), rudder clearance corrected, stiffener split to 2x150mm, pushrod rerouted to tip horn, mass 33.76g.
**Round 3 (v4):** Cleanup pass. Removed detailed mechanical sections (bevel angles, rudder clearance analysis, bridge joiner spec, pushrod routing detail) -- these will be refined during integration. Marked bridge joiner as TBD. Deferred rudder clearance verification to integration phase. No mass or geometry changes from v3.2.

## References

- Full aero analysis: `AERO_PROPOSAL_HSTAB_R1.md` (configuration decision), `AERO_PROPOSAL_HSTAB_R2.md` (planform + revisions)
- Structural reviews: `STRUCTURAL_REVIEW_HSTAB_R1.md`, `STRUCTURAL_REVIEW_HSTAB_R2.md`
- NeuralFoil analysis script: `scripts/hstab_r2_analysis.py`
- Mass balance research: Model Aviation "Deadly Flutter" article, EAA mass balance guide, Hobby Squawk forums
