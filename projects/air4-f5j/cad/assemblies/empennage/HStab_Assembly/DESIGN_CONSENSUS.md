# Design Consensus: H-Stab Assembly (v6)

**Date:** 2026-03-31 (v6), 2026-03-30 (v5), 2026-03-29 (v3.1/v3.2)
**Rounds:** 4 (R1: configuration + sizing, R2: planform + structural, R3: spar repositioning + horn + tip, R4: concealed hinge + single spar + forward hinge)
**Status:** AGREED — v6 incorporates R4 concealed saddle hinge, single spar, forward hinge line, elimination of rear spar/stiffener/horn/tungsten

---

## Agreed Specifications

| Parameter | Value | Source |
|-----------|-------|--------|
| Configuration | **Fixed stabilizer + 45% chord elevator** | R4 — hinge moved forward to X=60mm |
| Planform | **Superellipse n=2.3** | Aero R2 — 0.75 ct savings at cruise, 5.9 ct at thermal |
| Planform alignment | **45%-chord line is straight** (optimal for spar) | v3.2 correction |
| Root airfoil | **HT-13 (6.5%)** | Aero R1 — lowest CD0 at Re>50k |
| Tip airfoil | **HT-12 (5.1%)** | Aero R1 — lowest CD0 at Re=40k |
| Blend | **Linear HT-13 to HT-12, root to tip** | Every rib unique — 3D printing differentiator |
| Span | **430mm** (215mm per half) | Validated sizing from v1 |
| Root chord | **115mm** | Re 61,300 at 8 m/s |
| Tip chord (95% span) | **~50mm** | Superellipse taper |
| Mean chord | **94.8mm** | Derived |
| Area | **394.8 cm2 (3.95 dm2)** | Derived (numerical integration) |
| AR | **4.53** | Derived |
| Oswald e | **0.990** | Near-elliptical span loading |
| Vh | **0.393** | Acceptable for fixed+elevator |
| S_h/S_w | **9.8%** | Within F5J range (8.9-11.6%) |
| Tail moment arm | **651mm** | From fuselage consensus |
| LE sweep | **Continuous curvature** (superellipse) | No straight taper lines |
| Mass target | **29.3g (35g hard limit)** | v6 — 4.3g saved vs v5 |

## Planform Alignment and Coordinate System

The superellipse planform is aligned on the **45%-chord line**, which remains at a constant X position across all span stations.

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
x_TE(y) = 51.75 + 0.55 * c(y) * 0.97                Trailing edge position (97% truncation)
```

At the root (y=0): LE=0.00, TE=111.55. At y=100: LE=4.08, TE=106.80. At y=200: LE=28.86, TE=78.20.

## Elevator Specifications (v6 — MAJOR CHANGE from v5)

| Parameter | Value |
|-----------|-------|
| Chord ratio | **~45% of local chord at root** (was 35% in v5) |
| Hinge line | **Fixed at X=60.0mm from root LE** (was 74.75mm in v5) |
| Root elevator chord | **51.5mm** (was 36.8mm) |
| Elevator at y=200mm | **18.2mm (36% local chord)** |
| Elevator chord reaches zero | **y≈212mm** (was y≈204mm in v5) |
| Elevator area | **176.6 cm2** (was 114.7 cm2, +54%) |
| Authority integral | **14,987** (was 10,556, +42%) |
| Deflection up (nose down) | **-18 deg** (reduced from -20°) |
| Deflection down (nose up) | **+18 deg** (reduced from +25°) |
| Cruise deflection | 1.9 deg |
| Thermal deflection | 5.4 deg |
| Flare deflection | 8.7 deg |

**Why the hinge moved forward:** Removing the rear spar (which was at X=69.0) eliminated the constraint that kept the hinge at X=74.75. Moving to X=60.0 increases elevator area by 54% and authority by 42%, while the reduced deflection angles (±18° vs -20/+25°) simplify the concealed hinge mechanism. The 25.5mm gap between spar (X=34.5) and hinge (X=60.0) provides adequate D-box torsional stiffness.

## Concealed Saddle Hinge (v6 — NEW)

The v6 hinge is a fully concealed mechanism with zero visible gap, replacing the v5 music-wire-pin + external PETG knuckle strips.

### Mechanism

| Parameter | Value |
|-----------|-------|
| Type | Concealed saddle: convex bull-nose in concave channel |
| Wire | 0.5mm spring steel (ASTM A228), 424mm |
| Wire mass | 0.65g |
| Hinge axis | **Inside the stab body**, not at the surface |
| External surface | **Completely flush — zero gap** |
| Saddle in stab | Concave channel at TE inner surface, variable depth |
| Bull-nose on elevator | Convex protrusion at LE, extends 2-3mm forward of wire |
| Bearing surfaces | PETG sleeves (1.2mm OD, 0.6mm ID, 3mm long), interleaved |
| Gap seal | **TBD** — options: co-printed TPU lip, bonded Mylar, bonded tape |
| Saddle viable span | Root to y=206mm (airfoil thick enough at X=60) |
| Beyond y=206mm | Wire-only through bore, gap seal still covers |

### Saddle Geometry Schedule

The saddle tapers with the airfoil. At X=60.0mm the airfoil is 25-57% thicker than at the v5 hinge position (X=74.75), providing excellent saddle depth.

| Span zone | Airfoil thickness at hinge | Bull-nose radius | Saddle type |
|-----------|---------------------------|-----------------|-------------|
| y=0 to 50 | 6.4-6.0mm | 2.2mm | Full saddle |
| y=50 to 100 | 6.0-5.3mm | 1.8-1.7mm | Full saddle |
| y=100 to 150 | 5.3-4.1mm | 1.7-1.2mm | Tapered saddle |
| y=150 to 200 | 4.1-2.0mm | 1.2-0.5mm | Minimal saddle |
| y=200 to 206 | 2.0-1.5mm | 0.5-0mm | Fading |
| y=206 to 212 | <1.5mm | 0 | Wire-only |

### Hinge Bearing Details

PETG sleeves alternate between stab-fixed and elevator-fixed (interleaved), spaced at 15-20mm intervals. The wire passes through all sleeves freely. Stab-fixed sleeves are the bearing surfaces; elevator-fixed sleeves prevent spanwise wire migration.

| Parameter | Value |
|-----------|-------|
| Sleeve dimensions | 1.2mm OD, 0.6mm ID, 3mm long |
| Sleeve material | PETG solid |
| Count | ~24 per half-span (48 total) |
| Total sleeve mass | 0.10g |
| Interleaving | Alternating stab/elevator, same as v5 knuckle principle |
| Installation | Embedded in printed pockets during post-print assembly |

### Gap Seal (TBD — to be resolved during integration)

The external aerodynamic surface must be completely flush with zero visible gap at all deflection angles. Options under investigation:

1. **Co-printed TPU lip** — integral with shell, requires multi-material investigation on Bambu P1S + AMS
2. **Bonded Mylar strip** (0.05mm) — competition standard, lightest (0.18g), annual replacement
3. **Bonded elastic tape** — Blenderm or similar, lightest consumable option
4. **Printed LW-PLA lip** — REJECTED by structural review (foamed LW-PLA cracks at 0.25mm after 10-50 flights)

Decision deferred to integration phase after multi-material printing feasibility is tested.

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

## Comprehensive Chord and Position Table (v6)

**Spar: X=34.5mm | Hinge: X=60.0mm | No rear spar | No stiffener**

All positions in mm from root LE. The main spar is the ONLY carbon rod. The hinge line is the concealed saddle.

| y (mm) | Chord | LE_x | Spar X=34.5 | Hinge X=60.0 | TE_x | Elev chord |
|--------|-------|------|-------------|---------------|------|------------|
| 0 | 115.0 | 0.00 | 34.5 (30%) | 60.0 (52%) | 111.6 | 51.5 (45%) |
| 50 | 113.2 | 0.79 | 33.7 (30%) | 59.2 (52%) | 110.6 | 50.6 (45%) |
| 100 | 105.9 | 4.08 | 30.4 (29%) | 55.9 (53%) | 106.8 | 46.8 (44%) |
| 150 | 89.6 | 11.44 | 23.0 (26%) | 48.6 (54%) | 98.3 | 38.3 (43%) |
| 189 | 63.7 | 23.19 | **tube end** | 36.8 (58%) | 84.9 | 24.9 (39%) |
| 200 | 50.9 | 28.86 | 5.6 (11%) | 31.1 (61%) | 78.2 | 18.2 (36%) |
| 206 | 44.1 | 31.87 | exits | 28.1 (64%) | 74.6 | 14.6 (33%) |
| 210 | 32.0 | 37.36 | exits | 22.6 (71%) | 68.4 | 8.4 (26%) |
| 212 | ~14.6 | -- | exits | exits (~97%) | -- | ~0 |
| 214 | 0 | -- | -- | -- | -- | -- |

**Key insight (v6):** The elevator chord fraction only drops from 45% at root to 26% at y=210. Compare v5 where it dropped from 32% to 0% at y=204. The forward hinge keeps the elevator effective across the full span.

## Structural Elements (v6)

| Element | Specification | Fixed X (mm) | Terminates at | Mass (g) |
|---------|--------------|-------------|---------------|----------|
| Main spar | 3mm CF tube (3/2mm OD/ID), 378mm | 34.50 | y=189mm per half | 2.38 |
| Hinge wire | 0.5mm music wire, 424mm | 60.00 | y=212mm per half | 0.65 |
| PETG sleeves | 48x, 1.2mm OD / 0.6mm ID / 3mm long | (on hinge line) | -- | 0.10 |
| VStab junction fillet | 9.2mm radius, quartic polynomial, C2 continuous | -- | -- | (in fuselage budget) |
| VStab joint | Interlocking dovetail + CA | -- | -- | 0g |
| TE truncation | 97% chord (~0.7mm flat TE) | -- | -- | -- |

### What was REMOVED in v6

| Removed item | v5 mass | Reason |
|-------------|---------|--------|
| Rear spar (1.5mm CF rod, 420mm) | 1.15g | Concealed hinge provides TE stiffness; D-box torsion adequate |
| Elevator stiffener left (1mm CF, 150mm) | 0.19g | Shell EI adequate (35 Hz bending mode, 0.63mm gust deflection) |
| Elevator stiffener right (1mm CF, 150mm) | 0.19g | Same |
| Tip horn (integral elevator structure) | ~0.30g | Not needed — both stab and elevator self-close at tip |
| Tungsten putty (2x 0.5g) | 1.00g | Zero-slop wire + servo provides flutter prevention |
| 4x PETG hinge strips | 2.00g | Replaced by concealed saddle + embedded PETG sleeves |
| **Total removed** | **4.83g** | |

### Spar Geometry Notes

The main spar passes through the VStab fin at the HStab root station. The fin is 7mm thick at this point.

| Rod | Hole in fin | Fit type |
|-----|-----------|----------|
| Main spar (3mm tube) | 3.1mm bore, PETG sleeve | Friction fit, tapers to 3.05mm at endpoint |
| Hinge wire (0.5mm) | 0.6mm bore, PETG sleeve 1.2mm OD | Free rotation |

## Tip Closure (v6 — SIMPLIFIED)

With the hinge at X=60, both the stab shell and elevator taper naturally to zero at the tip. **No horn or wrap-around closure is needed.**

- **Stab shell** (LE to hinge): covers chord from LE to X=60. At y=210, this is 22.6mm chord. The stab closes its own tip with a C1-continuous cap at y=210-214mm.
- **Elevator** (hinge to TE): covers chord from X=60 to TE. At y=210, this is 8.4mm chord. The elevator tapers to zero at y=212mm with its own tip closure.
- Both halves self-close. No forward-wrapping horn, no complex tip geometry.

## Structural Analysis Summary (v6)

### Torsional Stiffness

| Station | V6 D-box GJ (N-mm²) | V5 two-spar GJ | V6/V5 ratio |
|---------|---------------------|-----------------|-------------|
| Root | 601,037 | 1,463,160 | 41% |
| y=100 | 359,765 | 947,876 | 38% |
| y=150 | 163,876 | 531,375 | 31% |

V6 has 31-41% of V5 torsional stiffness. But twist at Vne (20 m/s) is only **0.01 degrees** — negligible. The single-spar D-box is structurally adequate because H-stab torsional loads are small.

### Elevator Bending (no stiffener)

- First bending mode: **35 Hz** (well above any structural concern)
- Tip deflection under 2g gust: **0.63mm** (0.30% of span)
- Optional: printed ribs every 40mm (0.12g total) as insurance

### Flutter

- Zero-slop music wire eliminates the #1 RC flutter cause (hinge play)
- Servo is the primary anti-flutter mechanism (standard RC practice)
- Digital metal-gear servo mandatory (e.g., KST X06, 3.5g)
- Flutter speed with servo powered: >100 m/s (no risk)

## Components (v6)

| Component | Type | Material | Mass (g) |
|-----------|------|----------|----------|
| HStab_Left | Custom, printed | LW-PLA 0.45mm vase mode (0.6mm saddle zone) | 6.89 |
| HStab_Right | Custom, printed (mirror) | LW-PLA 0.45mm vase mode (0.6mm saddle zone) | 6.89 |
| Elevator_Left | Custom, printed | LW-PLA 0.40mm vase mode (0.55mm bull-nose) | 5.05 |
| Elevator_Right | Custom, printed (mirror) | LW-PLA 0.40mm vase mode (0.55mm bull-nose) | 5.05 |
| HStab_Main_Spar | Off-shelf | 3mm CF tube 3/2mm, 378mm | 2.38 |
| Hinge_Wire | Off-shelf | 0.5mm music wire, 424mm | 0.65 |
| PETG_Sleeves | Custom, printed | PETG solid, 48x (1.2/0.6/3mm) | 0.10 |
| Gap_Seal | TBD | TBD (Mylar/tape/co-print) | ~0.18 |
| Elevator_Bridge_Joiner | Custom, printed | CF-PLA solid U-channel | 0.60 |
| CA glue + Z-bend clevis | -- | -- | 0.55 |
| **TOTAL** | | | **29.33g** |

## Pushrod Routing (v6)

| Parameter | Value |
|-----------|-------|
| Pushrod type | 1.0mm music wire in 2.0mm OD / 1.2mm ID PTFE tube (Bowden) |
| Attachment point | **Elevator root face** (direct, shortest path) |
| Route | Servo (fuselage X=350) → fuselage boom → VStab fin interior → exits fin at H-Stab root → Z-bend clevis at elevator root face |
| Connection | Z-bend through 1.6mm hole in elevator root face, 8-10mm below hinge line |
| Alternate holes | 6mm and 12mm below hinge (for rate adjustment) |

**v6 change:** Pushrod attaches at elevator ROOT (not tip horn as in v5). This is shorter, stiffer, and eliminates the long internal pushrod run through the elevator span.

## Performance (v6)

### Elevator Performance Comparison

| Parameter | V5 | V6 | Delta |
|-----------|-----|------|-------|
| Elevator area | 114.7 cm² | **176.6 cm²** | +54% |
| Authority integral | 10,556 | **14,987** | +42% |
| Root elevator chord | 36.8mm (32%) | **51.5mm (45%)** | +40% |
| Root tau (flap effectiveness) | 0.910 | 0.842 | -7.5% |
| Cruise deflection | 1.8° | 1.9° | +0.1° |
| Thermal deflection | 5.0° | 5.4° | +0.4° |
| Flare deflection | 8.0° | 8.7° | +0.7° |
| Max deflection available | -20/+25° | **±18°** | Reduced (adequate) |
| Hinge gap drag | 3-6 counts | **0.4-0.8 counts** | -3 to -5 counts saved |
| Mass | 33.65g | **29.33g** | -4.32g (12.8%) |

### Why V6 is Superior

1. **42% more pitch authority** — better landing precision, stronger flare capability
2. **3-5 drag counts saved** — concealed hinge eliminates gap drag and knuckle protrusions
3. **4.3g lighter** — eliminating 5 component types (rear spar, stiffeners, horn, tungsten, knuckle strips)
4. **Simpler tip** — both stab and elevator self-close, no horn geometry
5. **Zero visible hardware** — completely flush aerodynamic surface
6. **Competition advantage** — no carbon F5J kit offers a fully concealed zero-gap hinge

## Print Strategy

| Part | Orientation | Mode | Material | Temp | Notes |
|------|-----------|------|----------|------|-------|
| Stab halves | Flat, saddle face down | Vase mode 0.45mm (0.6mm saddle zone) | LW-PLA | 230°C (210°C saddle) | Dense saddle bearing surface |
| Elevator halves | Flat, bull-nose face down | Vase mode 0.40mm (0.55mm bull-nose) | LW-PLA | 230°C | |
| PETG sleeves | Flat | 100% solid | PETG | 240°C | Print 48+ on one plate |
| Bridge joiner | Flat | Solid, 1.2mm | CF-PLA | 220°C | |

## Assembly Sequence

1. Print all parts: 2 stab shells (with saddle), 2 elevator shells (with bull-nose), 48 PETG sleeves, 1 bridge joiner
2. Embed PETG sleeves into stab saddle pockets and elevator bull-nose pockets (CA)
3. Mate elevator bull-nose into stab saddle channel (slide in from root face)
4. Thread 0.5mm music wire from one tip through all interleaved sleeves, through VStab fin bore, out other tip
5. Bend wire 90° at each tip (y=212mm), tuck flush
6. Test deflection range ±18°, verify smooth operation
7. Install elevator bridge joiner into left/right elevator root pockets (CA)
8. Verify synchronization: deflect one half, confirm other follows within 1°
9. Thread main spar (3mm CF tube, 378mm) through left stab at X=34.5, through VStab fin bore, through right stab
10. Bond stab roots to VStab fin (dovetail interlock + CA)
11. Apply gap seal (method TBD: Mylar/tape/co-print)
12. Route pushrod: thread 1mm wire through PTFE tube in fuselage, through VStab fin exit, Z-bend at elevator root face
13. Verify full deflection range with servo actuation, check for binding
14. Weigh complete assembly, verify under 35g

## Round History

**Round 1:** Aero: Fixed stab + 35% elevator + TPU hinge, trapezoidal planform, HT-13/HT-12, 25.5g. Struct: MODIFY — 7 changes.
**Round 2:** Aero: Superellipse n=2.3, mass 32.3g. Struct: ACCEPT except hinge — music wire pin replaces TPU.
**Round 3 (v3-v5):** Mechanical integration, spar repositioning, tip horn, tungsten balance, mass 33.65g.
**Round 4 (v6):** User-directed radical redesign:
- Concealed saddle hinge (user whiteboard sketch, 2026-03-31)
- Single spar (remove rear spar + stiffener)
- Hinge forward to X=60mm (maximize elevator area)
- No horn, no tungsten (flutter via zero-slop wire + servo)
- Gap seal TBD (co-print / Mylar / tape)
- Aero: +54% elevator area, +42% authority, -3 to -5 drag counts
- Struct: 29.33g (-4.32g), D-box twist 0.01°, elevator 35 Hz bending mode
- Both agents: ACCEPT

## References

- Aero analysis R1-R2: `AERO_PROPOSAL_HSTAB_R1.md`, `AERO_PROPOSAL_HSTAB_R2.md`
- Structural reviews R1-R3: `STRUCTURAL_REVIEW_HSTAB_R1.md` through `R3.md`
- R4 aero analysis script: `scripts/hstab_r4_analysis.py`
- R4 concealed hinge research: Agent research report (2026-03-31)
- R4 F5J elevator sizing research: Agent research report (2026-03-31)
- Geometry module: `scripts/hstab_geometry.py`
- Spec validator: `src/cad/drawing/spec_validator.py`
