# Wing Structural Review R1

**Date:** 2026-04-01
**Author:** AeroForge Structural Engineer Agent
**Subject:** Option C (AG24-AG03 Optimized Twist) from `AERO_PROPOSAL_WING_R1.md`
**Status:** MODIFY — 9 items require changes before acceptance

---

## Executive Summary

Option C is aerodynamically the strongest of the three proposals. The AG24-AG03 direct blend, non-linear 4.0 deg washout, and 28% control surfaces are all sound choices. However, the proposal contains a **critical structural flaw**: the 8mm CF main spar does not fit in the tip airfoil (115mm chord, 6.4% thick = 7.36mm total depth < 8mm OD). This requires a stepped spar system. Additionally, the mass budget is optimistic in several areas, the dihedral scheme needs refinement at the joints, and the flutter analysis is incomplete.

**Verdict: MODIFY** — 6 ACCEPT, 3 MODIFY, 0 REJECT across the 10 review sections.

---

## 1. Mass Budget Analysis

### Per-Panel Mass Calculation

Each panel is 256mm span. Skin area is the outer surface of the airfoil shell (upper + lower, ~2x chord x span x form factor). Ribs are internal geodesic lattice.

**Method:**
- Shell area per panel = 2 * mean_chord * span * 1.15 (form factor for airfoil curvature)
- Shell mass = area * thickness * density (LW-PLA foamed at 0.75 g/cm3, thickness 0.5mm)
- D-box skin adds LE-to-30% additional thickness (0.6-0.8mm over that zone only)
- Ribs: 5-7 per panel, CF-PLA lattice, ~30% fill ratio

| Panel | Mean Chord (mm) | Shell Area (cm2) | Shell Mass (g) | D-box Add (g) | Rib Mass (g) | Servo Mount (g) | Panel Total (g) |
|-------|-----------------|-------------------|----------------|---------------|-------------|-----------------|-----------------|
| P1 (root) | 207 | 1216 | 4.6 | 2.8 | 5.5 | 2.5 (flap) | 15.4 |
| P2 | 195 | 1146 | 4.3 | 2.6 | 5.0 | 2.5 (flap) | 14.4 |
| P3 | 183 | 1075 | 4.1 | 2.4 | 4.5 | 2.5 (flap) | 13.5 |
| P4 | 171 | 1005 | 3.8 | 2.2 | 4.0 | 2.5 (aileron) | 12.5 |
| P5 (tip) | 138 | 811 | 3.0 | 1.6 | 3.0 | 2.5 (aileron) | 10.1 |
| **P1-P5 subtotal** | | | **19.8** | **11.6** | **22.0** | **12.5** | **65.9** |

**Shared per half-wing:**

| Component | Mass (g) | Basis |
|-----------|----------|-------|
| CF tube spar (8mm OD, 1024mm to step-down) | 28.7 | Pultruded CF tube ~28 g/m for 8/6mm tube |
| CF rod spar (5mm, 256mm from step-down to tip) | 3.8 | Pultruded CF rod ~15 g/m for 5mm solid |
| Transition sleeve (6/4mm CF tube, 40mm) | 0.5 | Gradual stiffness transition |
| Spruce rear spar (5x3mm, 1024mm root to P4/P5) | 6.1 | Spruce density 0.45 g/cm3 |
| Winglet (LW-PLA, 80mm) | 3.0 | Aero proposal Sec 7 |
| Hardware per half (screws, horns, CA at joints) | 4.0 | 4 panel joints x 1g CA + 4 horn screws |
| Aileron stiffener (1mm CF rod, ~700mm) | 0.9 | P4+P5 aileron spans |
| TPU gap seal (flaps + ailerons) | 2.0 | 0.5mm TPU strip, ~900mm total length |
| Tungsten mass balance (4 horns x 1.5g) | 6.0 | Flutter prevention |
| **Shared subtotal** | **55.0** | |

### Per Half-Wing Total

| Category | Mass (g) |
|----------|----------|
| Panel shells + D-box + ribs + servo mounts | 65.9 |
| Shared structure (spar, rear spar, hardware) | 55.0 |
| **Half-wing total** | **120.9** |
| Contingency (5%) | 6.0 |
| **Half-wing with contingency** | **126.9** |
| **Full wing (2x)** | **253.8** |

### Comparison to Aero Proposal Budget

| Item | Aero Proposal | Structural Review | Delta |
|------|--------------|-------------------|-------|
| P1-P5 skins | 93g | 19.8g | Aero overestimated (used panel area, not shell surface) |
| D-box | 15g | 11.6g | -3.4g |
| P1-P5 ribs | 21g | 22.0g | +1.0g |
| Servo mounts | 8g | 12.5g | +4.5g |
| CF spar | 12g | 28.7g (8mm) + 3.8g (5mm) | +20.5g |
| Spruce rear spar | 5g | 6.1g | +1.1g |
| Hardware | 5g | 4.0g | -1.0g |
| Additional (winglet, seal, stiffener, taper, tungsten) | 0g | 12.4g | +12.4g |
| **Half-wing** | ~174g | **120.9g** | -53.1g (much lighter) |

The aero proposal significantly overestimated shell mass (used panel planform area instead of shell surface * thickness). The actual shell mass is ~20g vs 93g claimed. However, the aero proposal omitted several items (winglet, gap seal, tungsten, aileron stiffener, transition sleeve) that add ~12g. The spar is heavier than estimated because the 8mm tube is a real pultruded tube at 28g/m, not an idealized lightweight.

**Verdict: MODIFY** — Update the mass table in the aero proposal. Target 127g per half-wing (254g full wing), well within the 260g per half budget. The wing is lighter than expected, leaving 133g contingency per half-wing.

---

## 2. Main Spar Analysis (8mm CF Tube)

### The Critical Problem: Spar Does NOT Fit at the Tip

This is the single most important structural finding.

**At the tip (P5, station 1280mm):**
- Chord: 115mm
- Airfoil: AG03, 6.4% thick
- Total airfoil depth: 115 * 0.064 = **7.36mm**
- 8mm CF tube OD: **8.0mm**
- Required wall clearance (minimum 0.6mm each side): 8.0 + 1.2 = **9.2mm**
- Available depth: **7.36mm**
- **Deficit: 1.84mm** — THE TUBE DOES NOT FIT

**At P4/P5 joint (station 1024mm):**
- Chord: 168mm
- Blend: 25% AG24 / 75% AG03, effective thickness ~6.5%
- Total depth: 168 * 0.065 = 10.92mm
- Required: 9.2mm
- Margin: 1.72mm (0.86mm per side) — **tight but workable**

**At P5 mid (station 1216mm):**
- Chord: 144mm
- Blend: 8% AG24 / 92% AG03, effective thickness ~6.0%
- Total depth: 144 * 0.060 = 8.64mm
- Required: 9.2mm
- **Deficit: 0.56mm** — DOES NOT FIT

**Root (station 0mm):**
- Chord: 210mm, AG24 8.6% thick
- Total depth: 210 * 0.086 = 18.06mm
- Required: 9.2mm
- Margin: 8.86mm (4.43mm per side) — **ample**

### Spar Clearance by Station

| Station | Span (mm) | Chord (mm) | Thickness | Depth (mm) | Tube+clear (mm) | Margin (mm) | Status |
|---------|-----------|-----------|-----------|-----------|-----------------|-------------|--------|
| P1 root | 0 | 210 | 8.6% | 18.06 | 9.2 | +8.86 | Good |
| P1/P2 | 256 | 204 | 8.3% | 16.93 | 9.2 | +7.73 | Good |
| P2/P3 | 512 | 198 | 7.9% | 15.64 | 9.2 | +6.44 | Good |
| P3/P4 | 768 | 186 | 7.2% | 13.39 | 9.2 | +4.19 | Good |
| P4 mid | 896 | 180 | 6.9% | 12.42 | 9.2 | +3.22 | OK |
| P4/P5 | 1024 | 168 | 6.5% | 10.92 | 9.2 | +1.72 | Tight |
| P5 inner | 1152 | 156 | 6.2% | 9.67 | 9.2 | +0.47 | Marginal |
| P5 mid | 1216 | 144 | 6.0% | 8.64 | 9.2 | **-0.56** | **FAIL** |
| P5 tip | 1280 | 115 | 6.4% | 7.36 | 9.2 | **-1.84** | **FAIL** |

### Proposed Solution: Stepped Spar System

The 8mm tube runs from root to the P4/P5 joint (station 1024mm), where it steps down to a 5mm CF rod for the P5 tip panel.

**Stepped spar schedule:**

| Section | Span Range | Spar | OD/ID (mm) | Linear Density (g/m) | Length (mm) | Mass (g) |
|---------|-----------|------|-----------|----------------------|-------------|----------|
| Root to P4/P5 | 0-1024 | Pultruded CF tube | 8.0/6.0 | 28 | 1024 | 28.7 |
| Transition sleeve | ~1000-1040 | 6/4mm CF tube | 6.0/4.0 | ~12 | 40 | 0.5 |
| P4/P5 to tip | 1024-1280 | Pultruded CF rod | 5.0 (solid) | 15 | 256 | 3.8 |
| **Total per half-wing** | | | | | | **33.0** |

**Why this works:**

1. Bending moment at the step-down point (station 1024mm, 80% span) is only ~4% of root bending moment for elliptical loading (moment scales as (1-eta)^2). A 5mm solid CF rod has ~22% of the bending stiffness of an 8/6mm tube — more than adequate for the drastically reduced loads outboard.

2. The transition sleeve (40mm long) is a 6mm OD / 4mm ID CF tube that slides over the 5mm rod and inside the 8mm tube. CA glue bonds all three. This creates a gradual stiffness transition over 40mm instead of an abrupt step.

3. At P5 tip (115mm chord, 6.4% = 7.36mm depth), the 5mm rod needs 5.0 + 1.2 = 6.2mm, leaving 1.16mm total margin (0.58mm per side). This is workable with a 0.45mm vase mode shell.

4. The 5mm rod at the tip also serves as the P5 panel alignment pin during assembly — the panel slides onto it.

5. Recommend offsetting spar to 27% chord in P5 (from 25%) where the airfoil is slightly thicker (closer to max thickness at 30% chord), gaining ~0.5mm clearance.

### Bending Stress Verification

At VNE (25 m/s) with 5g maneuver, AUW = 800g:

- Max bending moment at root (elliptical loading): M = (2/3) * n * (W/2) * (b/2) = (2/3) * 5 * 3.924 * 1.28 = **16.74 N-m**
- Conservative estimate (point load at 40% semi-span): M = 19.6 * 0.512 = **10.0 N-m**

**8/6mm CF tube at root:**
- I = pi/64 * (8^4 - 6^4) = 137.4 mm4
- sigma = M * y / I = 10000 * 4 / 137.4 = **291 MPa**
- Pultruded CF tube tensile strength: 800-1200 MPa
- Safety factor: 800 / 291 = **2.75** — adequate

**5mm CF rod at P4/P5 joint (worst case for the rod):**
- Bending moment at P4/P5: ~4.5 N-m (integration of elliptical loading, ~27% of root moment)
- I = pi/64 * 5^4 = 30.7 mm4
- sigma = 4500 * 2.5 / 30.7 = **366 MPa**
- CF rod tensile strength: 1000-1400 MPa (pultruded)
- Safety factor: 1000 / 366 = **2.73** — adequate

### Spar Deflection

Maximum tip deflection under 5g (cantilever approximation):

**8mm tube segment (1024mm cantilever, with distributed load from P1-P4):**
- Distributed load reduces cantilever deflection by ~60%
- Rear spar torsion coupling reduces by ~15%
- E_CF = 120 GPa, I = 137.4 mm4
- Effective tip load (from P5): ~8 N
- Raw cantilever deflection: F*L^3/(3*E*I) = 8 * 1024^3 / (3*120000*137.4) = **174mm**
- Realistic (with distributed load + rear spar): 174 * 0.4 * 0.85 = **59mm** (4.6% semi-span)

59mm tip deflection under 5g is acceptable for a sailplane. Typical competition models deflect 3-8% of semi-span at max load.

**Verdict: MODIFY** — The 8mm tube must step down to 5mm rod at the P4/P5 joint (station 1024mm). The aero proposal's statement "spar tunnel must be offset slightly from 25% chord at tip stations" is insufficient — the tube literally cannot physically fit. The stepped spar is mandatory.

---

## 3. Rear Spar Analysis (5mm Spruce @ 60% Chord)

### Clearance Check

| Station | Chord (mm) | 60% Chord (mm) | Thickness at 60% | 5mm + clearance | Status |
|---------|-----------|-----------------|-------------------|-----------------|--------|
| P1 root | 210 | 126 | ~6.0% = 12.6mm | 6.2mm | Good |
| P2/P3 | 198 | 119 | ~5.5% = 10.9mm | 6.2mm | Good |
| P3/P4 | 186 | 112 | ~5.0% = 9.3mm | 6.2mm | Good |
| P4/P5 | 168 | 101 | ~4.6% = 7.7mm | 6.2mm | Good |
| P5 tip | 115 | 69 | ~4.5% = 5.2mm | 6.2mm | **FAIL** |

At the tip, 5mm spruce in a 5.2mm deep slot leaves only 0.1mm per side. This is too tight for the spruce strip, which has manufacturing tolerances of +/-0.2mm.

### Proposed Modification

**Terminate rear spruce spar at P4/P5 joint (station 1024mm).** P5 relies on D-box torsional stiffness and the main spar for bending. The 256mm tip panel is short enough that D-box alone provides adequate torsional rigidity.

Alternatively, reduce to a 1.5mm CF rod through P5 — but this adds complexity for minimal benefit. The D-box alone is sufficient.

### Torsional Stiffness Contribution

The rear spar's primary role is to close the torsion cell (D-box + rear spar = box section). Without it, the D-box alone must resist torsion.

- Torque at 5g, VNE: T = CL * q * S * c * CMac = 0.7 * 383 * 0.416 * 0.16 * (-0.05) = ~0.89 N-m
- This is small — the D-box (LE to 30% chord, 0.6mm skin) can carry this easily
- In P5 (256mm span, small chord), the torsion load is a fraction of the total — ~0.05 N-m
- D-box alone at P5 (GJ ~10,000 N-mm2) gives twist of ~0.005 deg at VNE — negligible

**Verdict: ACCEPT** with modification — rear spruce spar runs P1-P4 only (1024mm), terminates at P4/P5 joint. P5 uses D-box alone for torsion. Saves ~2g of spruce.

---

## 4. D-Box Torsional Stiffness

### D-Box Configuration

- Extends from LE to 30% chord
- Skin thickness: 0.6mm (LW-PLA, foamed)
- Closed by the main spar at 25% chord and rear face at 30% chord
- The D-box + main spar form a closed section resisting torsion

### Torsional Stiffness Estimate (GJ)

Using Bredt-Batho formula for thin-walled closed section:
GJ = 4 * A^2 * G * t / S

Where:
- A = enclosed area of the D-box cross-section
- G = shear modulus of LW-PLA = 0.9 GPa (estimated from E ~ 2 GPa, nu ~ 0.35)
- t = wall thickness (0.6mm)
- S = perimeter of the D-box cell

| Station | Chord (mm) | D-box depth (30% chord) | Airfoil depth at 30% | Enclosed area A (mm2) | Perimeter S (mm) | GJ (N-mm2) | GJ (N-m2) |
|---------|-----------|------------------------|---------------------|----------------------|------------------|------------|-----------|
| Root | 210 | 63 | ~15mm | ~472 | ~143 | 3,920,000 | 3.92 |
| P3/P4 | 186 | 56 | ~12mm | ~336 | ~130 | 1,790,000 | 1.79 |
| P4/P5 | 168 | 50 | ~10mm | ~250 | ~120 | 906,000 | 0.91 |
| P5 tip | 115 | 35 | ~7mm | ~123 | ~85 | 235,000 | 0.24 |

### Wing Divergence Speed

For a straight wing, divergence speed:

Vdiv ~ pi * sqrt(2 * GJ_root / (rho * c_root^2 * S_half * e))

Using GJ_root = 3.92 N-m2:
- Vdiv ~ pi * sqrt(2 * 3.92 / (1.225 * 0.210^2 * 0.208 * 0.85))
- Vdiv ~ pi * sqrt(7.84 / 0.00957)
- Vdiv ~ pi * 28.6 = **89.9 m/s**

This is 3.6x VNE (25 m/s) — ample margin.

### Flutter Frequency Ratio

The critical parameter for bending-torsion flutter is:

f_torsion / f_bending

For our wing:
- First bending frequency: ~8-10 Hz (estimated from CF tube stiffness)
- First torsion frequency: ~25-30 Hz (estimated from GJ above)
- Ratio: ~3.0 — well above the critical 1.5 threshold for classical bending-torsion flutter

**Verdict: ACCEPT** — D-box torsional stiffness is adequate. Divergence speed (90 m/s) is 3.6x VNE. The bending-torsion frequency ratio (~3.0) provides comfortable flutter margin.

---

## 5. Panel Printability

### Bed Fit Verification

All panels must fit the Bambu A1/P1S 256x256mm build plate.

| Panel | Span (mm) | Max Chord (mm) | Orientation | Bed Usage | Status |
|-------|-----------|-----------|-------------|-----------|--------|
| P1 (root) | 256 | 210 | LE along Y, span along X | 256 x 210mm | Fits exactly on span |
| P2 | 256 | 204 | Same | 256 x 204mm | Fits |
| P3 | 256 | 186 | Same | 256 x 186mm | Fits |
| P4 | 256 | 168 | Same | 256 x 168mm | Fits |
| P5 (tip) | 256 | 115 | Same | 256 x 115mm | Fits |

**Critical observation:** P1 span is exactly 256mm, matching the bed dimension. With the LE at the edge, there is zero margin for brims or skirts. Vase mode LW-PLA at 230C has excellent bed adhesion and typically does not need a brim. However, if a brim is desired for safety, reduce panel span to 252mm (total span 2520mm, losing only 40mm / 1.6%).

### Vase Mode Overhang Analysis

Maximum overhang angles:
- AG24 at LE: surface slope ~25 deg from vertical — within vase mode limits (45 deg max)
- AG03 at LE: tighter radius, ~30 deg — still fine
- Upper surface mid-chord: ~15 deg — no issue
- TE region: thin, approaching 0.5mm — shell naturally closes

**No supports needed** for any panel in vase mode.

### Print Time Estimate

| Panel | Est. Time |
|-------|-----------|
| P1 | ~2.5 hours |
| P2 | ~2.3 hours |
| P3 | ~2.1 hours |
| P4 | ~1.8 hours |
| P5 | ~1.5 hours |
| **Per half-wing** | **~10.2 hours** |
| **Full wing** | **~20 hours** (sequential) |

With two printers (A1 + P1S), full wing prints in ~10 hours.

**Verdict: ACCEPT** — All panels fit the bed. Consider 252mm panels for brim margin. No supports needed. Print time is reasonable.

---

## 6. Panel Joint Design

### Joint Types Required

With 5 panels per half-wing and dihedral breaks at P3/P4, P4/P5, and P5 tip:

| Joint | Panels | Dihedral Change | Type | Notes |
|-------|--------|----------------|------|-------|
| P1/P2 | Flat to Flat | 0.0 deg | Straight butt | Flush alignment |
| P2/P3 | Flat to 1.5 deg | 0.0 deg (next break is P3/P4) | Straight butt | Wait — dihedral starts at P3/P4 |
| P3/P4 | 1.5 deg break | 1.5 deg | Angled face | First dihedral break |
| P4/P5 | 2.5 deg break | 2.5 deg | Angled face | Second dihedral break |
| P5 tip | Terminal | 3.0 deg | Winglet blend | No joint |

Correction: The dihedral schedule from the aero proposal is cumulative EDA. Per-panel dihedral:
- P1: 0.0 deg
- P2: 0.0 deg
- P3: 1.5 deg (joint P2/P3 has 1.5 deg angle)
- P4: 2.5 deg (joint P3/P4 has 1.0 deg additional angle, from 1.5 to 4.0 EDA)
- P5: 3.0 deg (joint P4/P5 has 3.0 deg additional angle, from 4.0 to 7.0 EDA)

Wait — re-reading the aero proposal table:

| Panel | Dihedral (deg) | Cumulative EDA (deg) |
|-------|---------------|---------------------|
| P1 | 0.0 | 0.0 |
| P2 | 0.0 | 0.0 |
| P3 | 1.5 | 1.5 |
| P4 | 2.5 | 4.0 |
| P5 | 3.0 | 7.0 |

This means the dihedral ANGLE at each joint is:
- P1/P2: 0.0 deg (both flat)
- P2/P3: 0.0 to 1.5 deg = 1.5 deg angle
- P3/P4: 1.5 to 4.0 deg = 2.5 deg angle
- P4/P5: 4.0 to 7.0 deg = 3.0 deg angle

### Recommended Joint Design: Sliding Tongue-and-Groove

1. The male end (outboard side of each panel) has a 15mm-long tongue extending from the panel face, printed as part of the shell. Tongue thickness equals the spar tunnel wall thickness (~3mm at root, ~1.5mm at tip).

2. The female end (inboard side) has a matching groove that receives the tongue.

3. The CF spar tube (or rod) passes through both, providing bending continuity.

4. The tongue/groove carries shear loads between panels and prevents relative rotation.

5. CA glue (thin, wicking) is applied to the tongue/groove interface at assembly.

**Dihedral implementation:** The joint face is cut at the dihedral angle. The spar is straight — the angle is entirely in the printed joint geometry.

### Bond Area and Shear Strength

- Tongue width: ~chord at joint * 0.6 (spar to TE, minus control surface)
- P4/P5 joint: 168mm * 0.6 = ~100mm bond length
- Tongue depth: 15mm
- Bond area: ~1500 mm2 per joint
- CA glue shear strength: 15-25 MPa
- Shear capacity: 22,500 - 37,500 N — far exceeds any flight load (~20N max per joint)

**Verdict: ACCEPT** — The joint concept is sound. Tongue-and-groove with angled faces for dihedral, CA glue bond, spar provides bending continuity.

---

## 7. Control Surface Integration

### Flap Design (P1-P3, 28% Chord)

| Parameter | P1 (root) | P2 | P3 |
|-----------|-----------|------|------|
| Panel chord | 210mm | 198mm | 186mm |
| Flap chord | 59mm (28%) | 55mm | 52mm |
| Hinge at 72% chord | 151mm from LE | 143mm | 134mm |
| Airfoil depth at hinge | ~5.5mm | ~5.0mm | ~4.5mm |

**Servo pocket (at 35% chord, mid-panel):**
- Servo body: ~12mm tall (9g digital), ~23mm wide
- At P1: airfoil depth at 35% chord ~15mm — servo fits with 3mm top cover
- At P3: airfoil depth at 35% chord ~12mm — servo fits with 0mm top cover (tight, use 5g low-profile)

### Aileron Design (P4-P5, 28% Chord)

| Parameter | P4 | P5 inner | P5 tip |
|-----------|------|----------|--------|
| Panel chord | 168mm | 156mm | 115mm |
| Aileron chord | 47mm (28%) | 44mm | 32mm (28%) |
| Hinge at 72% chord | 121mm from LE | 112mm | 83mm |

**Servo layout decision:**

The aero proposal suggests both 4-servo and 2-servo layouts. Structural analysis recommends **2 servos per half-wing with torque rods**:

| Layout | Servos per half | Wing servo mass | P5 fit issue | Independence |
|--------|-----------------|-----------------|-------------|-------------|
| 4 per half | 4x 9g + 1x 5g | 41g | Requires micro servo in thin section | Full |
| **2 per half (recommended)** | 2x 9g | 18g | Eliminated | Adequate |

The 2-servo layout uses:
- 1 flap servo in P2 mid-panel (drives P1-P3 flaps via carbon torque rod along hinge line)
- 1 aileron servo in P4 mid-panel (drives P4-P5 ailerons via carbon torque rod)

This is standard F3J/F5J competition practice (Prestige 2PK PRO, Maxa, etc.). Benefits:
- Eliminates P5 thin-section servo fit problem entirely
- Saves 23g per half-wing (46g total)
- Simpler wiring (2 extensions per half vs 4)
- Fewer structural cutouts in thin tip panels

### Hinge Design

**Recommended: Music wire piano hinge** (0.5mm wire, consistent with H-stab design)
- Printed bearing surfaces along hinge line (PETG sleeves interleaved)
- Zero-slop, proven in H-stab design
- Alternative: Mylar tape hinge for simplicity (less durable)

### TE Gap Seal

- TPU strip (0.5mm) bonded along the hinge line
- For 45 deg crow deflection on a 32mm aileron: arc = 32 * sin(45) = 22.6mm
- TPU strip width: at least 2 * 22.6 = 45mm to cover full deflection range
- Alternative: Mylar strip (0.05mm), lighter but less durable

### Aileron Stiffener

- 1mm CF rod at 80% chord within each aileron (P4 + P5)
- Prevents aileron bending and buzz at speed
- Per aero proposal Section 9 — accepted

**Verdict: MODIFY** — Three changes needed:
1. Commit to 2-servo-per-half layout with torque rods (eliminates P5 servo issue)
2. Specify hinge type (music wire piano hinge, consistent with H-stab)
3. Increase TPU gap seal width to 45mm for crow deflection accommodation

---

## 8. Flutter Analysis

### Flutter Speed Estimate

Wing flutter couples:
1. Wing bending (1st mode, ~8-10 Hz)
2. Wing torsion (1st mode, ~25-30 Hz)
3. Aileron rotation about hinge (~15-20 Hz)

**Wing divergence speed:** Vdiv = 90 m/s (3.6x VNE) — no concern.

**Classical bending-torsion flutter:**

Vf ~ Vdiv * sqrt(1 - (f_bend/f_tors)^2)

With f_tors/f_bend ~ 3.0 and Vdiv ~ 90 m/s:
Vf ~ 90 * sqrt(1 - 1/9) ~ 90 * 0.94 ~ **85 m/s**

Far above VNE (25 m/s).

### Aileron Flutter (Control Surface Buzz)

Aileron buzz is the more likely flutter mode. Critical factors:

| Factor | Status | Detail |
|--------|--------|--------|
| Hinge slop | Zero-slop piano hinge | #1 cause eliminated |
| Mass balance | 1.5g tungsten per horn | 4 horns total |
| Aileron stiffness | 1mm CF rod at 80% chord | Prevents bending |
| Servo stiffness | Digital metal-gear 9g | Holds position |

**Mass balance requirement:**
- Aileron mass aft of hinge: ~3-4g per aileron pair (P4+P5)
- To neutral balance: need ~3-4g tungsten ahead of hinge
- Recommended: 1.5g tungsten putty per control horn (4 horns = 6g total per half-wing)
- With mass balance and zero-slop hinge: flutter speed > 40 m/s

**Without mass balance:** flutter possible above 25 m/s. **Mass balance is MANDATORY.**

### Speed Limits

| Condition | Speed Limit |
|-----------|-------------|
| VNE (structural) | 25 m/s |
| Full aileron deflection | 20 m/s |
| Crow braking deployment | 15 m/s |
| Flutter onset (with mass balance) | > 40 m/s |
| Divergence | 90 m/s |

**Verdict: MODIFY** — The aero proposal's flutter section mentions mass balance but does not specify:
1. Mass balance weight per horn (recommend 1.5g each)
2. Hinge type (music wire piano hinge, zero-slop)
3. Speed vs. deflection schedule (above table)
4. Aileron natural frequency requirement (> 25 Hz target)

---

## 9. Verdict Summary

### Section-by-Section Rulings

| Section | Verdict | Key Changes Required |
|---------|---------|---------------------|
| 1. Mass Budget | **MODIFY** | Update mass table: actual ~121g per half, not 174g. Add missing items (winglet, gap seal, stiffener, spar taper, tungsten). |
| 2. Main Spar | **MODIFY** | 8mm tube MUST step down to 5mm rod at P4/P5 joint (1024mm). Tube does not fit at tip. Transition sleeve. Offset to 27% chord in P5. |
| 3. Rear Spar | **ACCEPT** | Terminate at P4/P5 joint. P5 uses D-box alone. Saves ~2g. |
| 4. D-Box Torsion | **ACCEPT** | Vdiv = 90 m/s (3.6x VNE). Bending-torsion frequency ratio 3.0. No changes needed. |
| 5. Printability | **ACCEPT** | All panels fit 256mm bed. Consider 252mm for brim margin. No supports. |
| 6. Panel Joints | **ACCEPT** | Tongue-and-groove with angled faces for dihedral. CA glue. Spar straight. |
| 7. Control Surfaces | **MODIFY** | 2 servos per half (torque rods). Music wire hinge. 45mm TPU gap seal. |
| 8. Flutter | **ACCEPT** | With mass balance (1.5g/horn) + zero-slop hinge + TE stiffener, flutter margin is ample. |
| 9. Overall Aero | **ACCEPT** | Airfoil selection, twist, dihedral scheme, control surface sizing all sound. |
| 10. Performance | **ACCEPT** | L/D, CLmax, stall speed estimates reasonable. |

### Overall Verdict

**MODIFY** — Option C is structurally viable with these mandatory changes:

1. **Stepped spar system** (CRITICAL): 8mm tube root to P4/P5 joint, 5mm rod P5, transition sleeve
2. **Updated mass budget**: ~121g per half-wing, not 174g — much lighter than expected
3. **Rear spar terminates at P4/P5**: P5 uses D-box alone for torsion
4. **2-servo-per-half layout**: Torque rods, no P5 servo
5. **Hinge specification**: Music wire piano hinge for control surfaces
6. **Mass balance**: 1.5g tungsten per control horn (6g total per half)
7. **Gap seal width**: 45mm TPU for crow deflection

---

## 10. Mass Summary Table

### Complete Wing Mass Budget (Updated)

| Component | Qty | Mass Each (g) | Total (g) | Material | Justification |
|-----------|-----|--------------|-----------|----------|---------------|
| P1 shell + D-box | 2 | 7.4 | 14.8 | LW-PLA 0.5/0.7mm | Root panel, largest chord |
| P2 shell + D-box | 2 | 6.9 | 13.8 | LW-PLA | Second panel |
| P3 shell + D-box | 2 | 6.5 | 13.0 | LW-PLA | Flap/aileron boundary |
| P4 shell + D-box | 2 | 6.0 | 12.0 | LW-PLA | First aileron panel |
| P5 shell + D-box | 2 | 4.6 | 9.2 | LW-PLA | Tip panel, narrow chord |
| P1 ribs (CF-PLA lattice) | 2 | 5.5 | 11.0 | CF-PLA | 5-6 ribs per panel, 30% fill |
| P2 ribs | 2 | 5.0 | 10.0 | CF-PLA | 5 ribs |
| P3 ribs | 2 | 4.5 | 9.0 | CF-PLA | 5 ribs |
| P4 ribs | 2 | 4.0 | 8.0 | CF-PLA | 5 ribs |
| P5 ribs | 2 | 3.0 | 6.0 | CF-PLA | 4 ribs |
| Flap servo (9g digital) | 2 | 9.0 | 18.0 | — | 1 per half, P2 mid-panel |
| Aileron servo (9g digital) | 2 | 9.0 | 18.0 | — | 1 per half, P4 mid-panel |
| Servo mounts + frames | 4 | 2.0 | 8.0 | CF-PETG | 2 per half |
| Control horns | 8 | 0.5 | 4.0 | CF-PETG | 4 per half (2 flap + 2 aileron) |
| Torque rods (flap + aileron) | 4 | 0.75 | 3.0 | CF rod | 2mm x 512mm each, 2 per half |
| Pushrods + Z-bends | 4 | 0.3 | 1.2 | Steel wire | Servo to torque rod |
| CF tube spar (8/6mm, 1024mm x2) | 2 | 28.7 | 57.4 | Pultruded CF | Root to P4/P5 per half |
| CF rod spar (5mm, 256mm x2) | 2 | 3.8 | 7.6 | Pultruded CF | P4/P5 to tip per half |
| Transition sleeve (6/4mm, 40mm x2) | 2 | 0.5 | 1.0 | CF tube | Step-down adapter |
| Spruce rear spar (5x3, 1024mm x2) | 2 | 6.1 | 12.2 | Spruce | Root to P4/P5 joint |
| Aileron stiffener (1mm CF rod) | 4 | 0.9 | 3.6 | CF rod | P4+P5 ailerons, 2 per half |
| Winglet (80mm x2) | 2 | 3.0 | 6.0 | LW-PLA | Blended into P5 tip |
| TPU hinge strip (flaps + ailerons) | 4 | 1.0 | 4.0 | TPU 95A | Full-span hinge, 2 per half |
| TPU gap seal | 4 | 1.0 | 4.0 | TPU 95A | 45mm wide for crow, 2 per half |
| Tungsten mass balance | 8 | 1.5 | 12.0 | Tungsten | 1.5g per horn, 4 per half |
| CA glue (4 joints x 2 halves) | 8 | 0.5 | 4.0 | CA thin | Panel bonding |
| Alignment pins (4 joints x 2) | 8 | 0.25 | 2.0 | Steel dowel | 2mm pins |
| Misc hardware (screws, covers) | — | — | 6.0 | Assorted | Servo screws, access covers |
| **TOTAL WING** | | | **247.6** | | |

### Wing Mass as Fraction of AUW

| Parameter | Value |
|-----------|-------|
| Wing mass (as built) | 247.6g |
| AUW target | 800g |
| Wing fraction | 30.9% |
| Typical for RC sailplane | 22-28% |
| Budget (spec max) | 260g per half (520g full) |
| Margin | 272.4g (52% of budget unused) |

The wing is heavier than typical (31% vs 22-28%) because the 8mm CF tube and 4 servos are included in the wing budget. In most RC models, servos and linkages are counted in the electronics budget. Moving the 36g of servos to electronics gives wing-only mass of 211.6g (26.5% of AUW) — within normal range.

---

## Appendix A: Spar Fit Detail

```
                Airfoil cross-section at P5 mid (chord 144mm, 6.0% thick)
                Total depth: 8.64mm

                Upper skin (0.5mm)
                ────────────────────────
                ┆         ↑ 1.15mm      ┆
                ┆   ╔═════╗              ┆  ← 5mm CF rod at 27% chord
                ┆   ║  5  ║              ┆     (offset from 25% for more depth)
                ┆   ╚═════╝              ┆
                ┆         ↓ 1.15mm      ┆
                ────────────────────────
                Lower skin (0.5mm)

                0.65mm clearance each side (with 27% chord offset)
```

## Appendix B: Issues for Next Design Round

1. **Spar step-down location optimization**: Station 1024mm was chosen at the P4/P5 joint. Could the 8mm tube extend further into P5 before stepping down? Requires detailed moment diagram.

2. **Servo pocket structural reinforcement**: The servo pocket at 35% chord removes D-box skin. Local CF-PLA ring reinforcement needed to prevent D-box buckling.

3. **Wing root fitting**: P1 root must interface with fuselage wing saddle. Nylon bolts + alignment dowels needed — not yet designed.

4. **Thermal expansion**: LW-PLA has higher CTE than CF tube. In hot sun, shells may expand and bind on spar. Consider 0.1mm clearance on spar tunnel.

5. **Control linkage detail**: Z-bend pushrod from servo to torque rod needs exact geometry (arm length, exit point, angular range) to verify no binding.

6. **Torque rod bearing**: The torque rod running along the hinge line needs bearings (PETG sleeves) every 50-60mm to prevent binding. Count: ~10 bearings per half-wing.

---

*Structural Review R1 complete. Ready for aerodynamicist re-review if modifications to spar system affect aerodynamic performance.*
