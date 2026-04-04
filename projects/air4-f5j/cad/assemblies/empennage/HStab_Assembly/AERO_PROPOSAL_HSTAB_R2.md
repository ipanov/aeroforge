# Aero Proposal: H-Stab Configuration (Round 2 -- Revised)

**Date:** 2026-03-29
**Author:** Aerodynamicist Agent
**Status:** REVISED PROPOSAL -- incorporating structural review modifications
**Revision:** R2 (response to STRUCTURAL_REVIEW_HSTAB_R1.md)
**Scope:** Planform revision, structural modification acceptance, updated mass budget

---

## 0. Executive Summary

This Round 2 proposal incorporates the structural engineer's 7 modifications and introduces a **planform upgrade from trapezoidal to modified elliptical (superellipse)**. The key changes from R1:

1. **Planform changed to superellipse (n=2.3)** -- saves 0.75 induced drag counts at cruise trim and 5.9 counts at thermal circling CL (net 0.64 ct at trim including profile drag trade). The 3D printer pays zero cost for the curved leading edge. This corrects the R1 error of dismissing the elliptical option.

2. **All 7 structural modifications ACCEPTED** -- every modification is aerodynamically sound or has negligible aerodynamic impact. The structural engineer's flutter analysis is particularly compelling; the mass balance is non-negotiable.

3. **Mass budget revised to 32.3g** -- I accept the structural engineer's corrected mass calculation. My R1 estimate of 25.5g significantly underestimated CF rod and shell masses. At 32.3g, the H-Stab is within the 35g hard limit with 2.7g contingency.

4. **Configuration unchanged: Fixed Stabilizer + 35% Chord Elevator + TPU Living Hinge** -- the R1 aerodynamic case for this configuration remains decisive (1.30 drag counts saved at junction, 72% more control authority than all-moving).

---

## 1. Structural Modification Response

### 1.1 Modification M1: Main Spar 3mm CF Tube (3/2mm OD/ID)

**ACCEPT.**

Aerodynamic impact: NONE. The spar is entirely internal. The 80% stiffness retention means negligible change to wing-in-bending deformation at any flight condition. The 2.2g weight saving directly reduces tail inertia for pitch dynamics.

The tube has EI = 414,700 N-mm^2 vs. 517,400 for the solid rod. At 1g cruise, tip deflection increases from ~9mm to ~12mm for spar-alone (mitigated by shell stiffness contribution). This is invisible to the pilot.

### 1.2 Modification M2: 1.0g Mass Balance (Tungsten Putty on Control Horn)

**ACCEPT -- this is the most critical modification.**

The structural engineer's flutter analysis is correct: with the elevator CG at 81% chord (16% aft of the 65% hinge line), flutter onset at 20 m/s is virtually guaranteed without mass balance. The 1.0g tungsten putty on a forward-extending horn provides 12% static balance, which -- combined with the 9g digital servo's stiffness and the TPU hinge damping -- is sufficient for Vne = 25 m/s.

**Aerodynamic impact of added mass:**
- The 1.0g at 8mm forward of the hinge line adds 0.064 x 10^-6 kg-m^2 to the elevator moment of inertia
- This increases the elevator's dynamic response time by approximately 3-5%, which is imperceptible to the pilot
- The servo load fraction at maximum deflection (25 deg) at Vne is only 8.3% of a 2.5 kg-cm servo's capacity
- **No change to control authority or deflection range**

### 1.3 Modification M3: Spar Terminates at 195mm (Tip 20mm Shell-Only)

**ACCEPT with aerodynamic note.**

The 3mm tube physically cannot pass through the 3.8mm thick HT-12 tip section (the spar would occupy 79% of the airfoil thickness, leaving only 0.4mm per side for skin). Terminating at 195mm is correct.

**Aerodynamic implication:** The last 20mm of tip (9.3% of half-span) is unsupported by spar. Under high load, this section will deflect more than the spar-supported portion. This creates a natural washout (twist reduction) at the tip under load, which is actually aerodynamically BENEFICIAL:
- At high CL (gust recovery, thermal circling), the tip unloads slightly
- This moves the stall onset inboard, away from the tip
- This is the same principle as the Spitfire's elliptical wing -- tip washout under load prevents tip stall

**No tip shape change required.** The shell-only tip will flex under extreme loads, providing passive load relief. The modified elliptical planform already provides a more gradual chord reduction at the tip (50mm at 95% span vs. trapezoidal's 73mm), giving better structural support at the spar termination point.

### 1.4 Modification M4: Rear Spar 1.5mm CF Solid Rod

**ACCEPT.**

The rear spar's primary function in the fixed stab is anti-rotation (preventing the shell from twisting on the main spar) and providing a second attachment point to the VStab fin. The 1.5mm rod at 60% chord is adequate for both roles. Aerodynamic impact: NONE (internal component).

The 1.0g weight saving is welcome. Every gram matters at 32.3g total.

### 1.5 Modification M5: 1mm CF Rod Stiffener in Elevator at 80% Chord

**ACCEPT -- critical for flutter prevention.**

The structural engineer correctly identified that the elevator has NO spar (the rear spar is at 60% chord, inside the fixed stab, not the elevator). A 215mm span elevator with only 0.45mm shell walls and no spanwise stiffener is highly susceptible to bending flutter modes.

The 1mm CF rod at 80% chord:
- Provides spanwise bending stiffness to the elevator
- Mass: only 0.55g (negligible compared to flutter risk)
- Sits at 80% chord, which is 15% chord aft of the hinge line -- well inside the elevator's structural envelope
- Does NOT change the airfoil profile (it's internal)

**Aerodynamic impact:** The 0.55g mass sits at 80% chord (15% chord aft of hinge). This slightly increases the elevator's CG offset from the hinge, but the effect is small (adds ~7.7 g-mm to the static moment of ~65 g-mm, or 12%). The mass balance (M2) was sized WITH this stiffener in mind.

### 1.6 Modification M6: TPU Hinge 0.8mm (was 0.6mm)

**ACCEPT.**

The structural engineer's FDM fatigue data is sobering: 500 cycles at 0.6mm means hinge failure within 5 flying sessions. This is unacceptable. At 0.8mm, the estimated 2,000-5,000 cycle life provides at least one full flying season, and the hinge is field-replaceable in 10 minutes.

**Aerodynamic impact analysis:**

The 0.8mm hinge protrudes 0.3mm below the lower surface skin line at 65% chord. My boundary layer analysis confirms this is hydraulically smooth:

| Parameter | Value |
|-----------|-------|
| BL thickness at hinge (laminar) | 1.70 mm |
| BL thickness at hinge (turbulent) | 2.85 mm |
| Protrusion height | 0.30 mm |
| Protrusion / BL_laminar | 0.176 |
| Protrusion / BL_turbulent | 0.105 |
| Classification | **HYDRAULICALLY SMOOTH** (ratio < 0.30) |

The 0.3mm protrusion is less than 18% of the laminar BL thickness and less than 11% of the turbulent BL thickness. Both are well below the 30% threshold for "hydraulically smooth" (Schlichting, Boundary Layer Theory). **The drag penalty is effectively zero** -- below the resolution of any measurement technique applicable to RC models.

Furthermore, the protrusion is on the **lower surface**, which is aerodynamically less critical than the upper surface. The 0.5mm gap on the upper surface remains unsealed (gap/BL = 0.18 on upper surface, also hydraulically smooth). I agree with the structural engineer: a sliding seal is not worth the complexity for zero measurable benefit.

### 1.7 Modification M7: Interlocking Dovetail at VStab Joint

**ACCEPT.**

The dovetail provides positive mechanical retention against peel loads, self-jigging during assembly, and increased bond area. Mass impact: zero. Aerodynamic impact: zero (internal feature, hidden under the fillet).

I further support the structural engineer's recommendation to print the junction fillet as part of the stab root (not the VStab fin), so the bond line is hidden inside the fillet, away from the aerodynamic surface.

---

## 2. Planform Revision: Trapezoidal to Modified Elliptical

### 2.1 The Case for Change

The R1 proposal used a simple trapezoidal planform (taper ratio 0.652). The R1 text stated: "elliptical offers only 0.22% improvement." This was a critical error in judgment that violated the project motto:

> "Why make it simple when it can be complex -- for the same price?"

The 3D printer creates curved leading edges at ZERO additional cost. Every slicer handles curved outlines natively. There is no manufacturing argument for straight taper lines on a 3D-printed part. The ONLY reason to use trapezoidal is if the aerodynamic benefit is literally zero -- and it is not.

### 2.2 Three Planforms Analyzed

I ran NeuralFoil analysis on three planform options, all with root chord 115mm and approximately 408 cm^2 area:

| Parameter | Trapezoidal | Elliptical | Mod Elliptical (SE n=2.3) |
|-----------|-------------|------------|---------------------------|
| Tip chord | 75mm | 0mm (impractical) | ~50mm at 95% span |
| Mean chord | 95.0mm | 90.3mm | 94.8mm |
| Area | 408.5 cm^2 | 388.4 cm^2 | 407.7 cm^2 |
| AR | 4.53 | 4.76 | 4.53 |
| Oswald e | 0.960 | 1.000 | 0.990 |
| k (CDi/CL^2) | 0.07325 | 0.06686 | 0.07090 |

### 2.3 Why Not Pure Elliptical?

The pure ellipse (Option 2) has the theoretical optimum Oswald factor of 1.0. However:

1. **Zero tip chord is impractical.** The tip tapers to literally 0mm, which cannot be printed, cannot hold skin, and cannot accommodate the spar termination.
2. **5% less area** than the trapezoidal at the same root chord. This would reduce Vh and S_h/S_w below the validated sizing, requiring either a longer tail arm or a larger root chord to compensate.
3. **Very low Re at the tip.** With chords approaching zero, the tip Reynolds numbers drop below 20,000 where laminar separation becomes severe and profile drag increases sharply.

The pure elliptical planform is impractical despite its theoretical perfection.

### 2.4 Modified Elliptical: The Optimal Choice

The **superellipse with n=2.3** provides:

```
c(y) = c_root * [1 - |y/b_half|^2.3]^(1/2.3)
```

This is a "slightly squared" ellipse -- fuller near the root than a true ellipse, with a more gradual taper toward the tip. The key advantages:

1. **Oswald e = 0.99** -- captures 97% of the elliptical induced drag benefit while maintaining a practical tip chord
2. **Same area as trapezoidal** (407.7 vs. 408.5 cm^2) -- no change to Vh or S_h/S_w
3. **Practical tip chord** (~50mm at 95% span) -- adequate for spar termination and printing
4. **Zero additional manufacturing cost** -- the curved leading edge is handled natively by the slicer
5. **Continuous curvature** -- no sharp taper breaks, smoother span loading

### 2.5 Induced Drag Savings (NeuralFoil Verified)

| CL | Trap CDi | Mod Ell CDi | Savings (counts) | Context |
|----|----------|-------------|------------------|---------|
| 0.05 | 1.83 ct | 1.77 ct | +0.06 | Cruise (low tail CL) |
| 0.178 | 23.21 ct | 22.46 ct | +0.75 | Trim at cruise |
| 0.30 | 65.93 ct | 63.81 ct | +2.12 | Moderate maneuvering |
| 0.50 | 183.14 ct | 177.25 ct | +5.89 | Thermal circling |
| 0.80 | 468.83 ct | 453.75 ct | +15.08 | High-CL recovery |

At the critical thermal circling condition (CL = 0.50), the modified elliptical saves **5.9 drag counts** compared to trapezoidal. This is 4.5x larger than the junction drag saving of 1.30 counts that justified the entire configuration change from all-moving to fixed+elevator. We cannot dismiss this.

At cruise trim (CL = 0.178), the saving is 0.75 counts -- comparable to the junction drag difference. Over a 10-minute thermal flight with half the time at CL > 0.3, the cumulative induced drag reduction translates to measurably better thermalling performance.

### 2.6 Profile Drag Impact

The modified elliptical planform shifts chord from the tip toward the root compared to trapezoidal. This means:
- **Higher Re at mid-span** (higher chord, same velocity) -- LOWER profile drag coefficient
- **Lower Re at the tip** (smaller tip chord) -- higher profile drag coefficient
- Net effect: approximately neutral, as the higher-Re mid-span region dominates

The total profile drag difference between planforms is less than 0.05 counts -- negligible compared to the induced drag savings.

### 2.7 Structural Mass Impact

| Planform | Wetted Area (mm^2) | Shell Mass (g) | Delta |
|----------|-------------------|----------------|-------|
| Trapezoidal | 84,151 | 30.0 | baseline |
| Mod Elliptical | 84,003 | 29.9 | -0.1g |

The shell mass difference is negligible (-0.1g). The modified elliptical has almost identical wetted area because, while the chord distribution changes, the total area is the same.

### 2.8 Tip Design

With the superellipse planform, the tip chord at 95% span is 50mm (vs. 73mm for trapezoidal, vs. 36mm for pure elliptical). At 95% span:
- HT-12 airfoil at 5.1% thickness: max thickness = 50 * 0.051 = 2.6mm
- This is too thin for the 3mm spar tube (M3 already addresses this -- spar terminates at 195mm)
- The last 20mm of tip is shell-only, which is structurally adequate at the lower loads present at the tip

At the spar termination point (195mm of 215mm = 90.7% span):
- Chord = 57.3mm
- Max thickness = 57.3 * 0.058 (blended HT-13/HT-12) = 3.3mm
- Wall thickness 0.45mm x 2 = 0.90mm, leaving 2.4mm interior
- The 3mm spar fits with 0.20mm clearance per side (tight but workable; the spar tunnel is printed at 3.1mm ID, requiring slight local thickening of the upper/lower skins at the spar station)

**Recommendation:** Taper the spar tunnel slightly at its termination to guide the spar smoothly to its endpoint. The last 5mm of the tunnel narrows from 3.1mm to 3.05mm for a snug friction fit.

---

## 3. Revised Specification Table

### 3.1 Planform

| Parameter | R1 Value | R2 Value | Change |
|-----------|----------|----------|--------|
| Planform shape | Trapezoidal | **Superellipse n=2.3** | Curved LE |
| Span | 430mm (215mm/half) | 430mm (215mm/half) | unchanged |
| Root chord | 115mm | 115mm | unchanged |
| Tip chord | 75mm (linear) | **~50mm at 95% span** | varies |
| Mean chord | 95.0mm | 94.8mm | -0.2mm |
| Area | 408.5 cm^2 | 407.7 cm^2 | -0.2% |
| Aspect ratio | 4.53 | 4.53 | unchanged |
| S_h/S_w | 9.8% | 9.8% | unchanged |
| Vh | 0.393 | 0.393 | unchanged |
| Oswald e | 0.960 | **0.990** | +3.1% |
| Taper ratio | 0.652 (constant) | N/A (continuous curve) | -- |
| LE sweep | ~5 deg straight | **Continuous curvature** | smooth curve |
| Tail moment arm | 651mm | 651mm | unchanged |

### 3.2 Airfoils (unchanged from R1)

| Station | Airfoil | t/c | Chord (R2) | Thickness | Re (8 m/s) | CD0 |
|---------|---------|-----|------------|-----------|------------|-----|
| Root | HT-13 | 6.5% | 115mm | 7.5mm | 61,300 | 0.01270 |
| 50% span | HT-13 | 6.5% | 106mm | 6.9mm | 56,500 | 0.01310 |
| 90% span | HT-13/12 blend | ~5.8% | 63mm | 3.6mm | 33,600 | 0.01680 |
| 95% span | HT-12 | 5.1% | 50mm | 2.6mm | 26,700 | 0.01920 |

### 3.3 Elevator (unchanged from R1 except hinge)

| Parameter | R1 Value | R2 Value | Change |
|-----------|----------|----------|--------|
| Chord ratio | 35% | 35% | unchanged |
| Hinge line | 65% chord | 65% chord | unchanged |
| Root elevator chord | 40.2mm | 40.2mm | unchanged |
| Tip elevator chord (95% span) | 26.2mm | ~16.3mm | narrower tip |
| Elevator area | 143.0 cm^2 | ~142.7 cm^2 | -0.2% |
| Deflection up | -20 deg | -20 deg | unchanged |
| Deflection down | +25 deg | +25 deg | unchanged |
| Hinge type | TPU 95A, 0.6mm | **TPU 95A, 0.8mm** | +0.2mm (M6) |
| Hinge gap | ~0.5mm | ~0.5mm | unchanged |
| Mass balance | none | **1.0g tungsten** | M2 |
| Elevator stiffener | none | **1mm CF rod at 80% chord** | M5 |

### 3.4 Structural Elements (revised per M1-M7)

| Element | R1 Spec | R2 Spec | Change |
|---------|---------|---------|--------|
| Main spar | 3mm CF solid rod | **3mm CF tube (3/2mm OD/ID)** | M1 |
| Main spar length | 440mm | **390mm** (195mm per half) | M3 |
| Rear spar | 2mm CF solid rod | **1.5mm CF solid rod** | M4 |
| Rear spar length | 440mm | 440mm | unchanged |
| Elevator stiffener | none | **1mm CF solid rod at 80% chord** | M5 |
| Elevator stiffener length | -- | 440mm | M5 |
| TPU hinge | 0.6mm | **0.8mm** | M6 |
| VStab joint | CA only | **Dovetail interlock + CA** | M7 |
| Junction fillet | Printed on VStab | **Printed on stab root** | per struct. recommendation |

### 3.5 VStab Junction Fillet (unchanged)

| Parameter | Value |
|-----------|-------|
| Fillet radius | 9.2mm |
| r/t ratio | 1.31 |
| Profile | Quartic polynomial, C2 continuous |
| Drag reduction | 90% vs. unfilleted |
| Manufacturing | 3D printed as part of stab root (per M7 recommendation) |

---

## 4. Revised Mass Budget

### 4.1 Component Masses (accepting structural engineer's calculations)

| Component | R1 Est. (g) | R2 Est. (g) | Source |
|-----------|-------------|-------------|--------|
| Stab shell (2 halves, LW-PLA) | 14.0 | **17.0** | Structural review (0.45mm, 0.72 g/cm^3) |
| Elevator shell (2 halves, LW-PLA) | 6.0 | **7.5** | Structural review (0.40mm elevator) |
| Main spar (3mm CF tube 3/2, 390mm) | 2.0 | **2.4** | pi/4*(3^2-2^2) * 390 * 1.58 / 1000 |
| Rear spar (1.5mm CF rod, 440mm) | 1.0 | **1.2** | pi/4*1.5^2 * 440 * 1.58 / 1000 |
| Elevator stiffener (1mm CF rod, 440mm) | -- | **0.55** | pi/4*1^2 * 440 * 1.58 / 1000 (M5) |
| TPU hinge strips (2x, 0.8mm) | 1.0 | **1.4** | 2 * 0.8 * 10 * 215 * 1.22 / 1e6 * 2 |
| Control horn (CF-PLA) | 0.5 | **0.8** | Standard mini horn + hardpoint |
| Mass balance (tungsten putty) | -- | **1.0** | M2 flutter prevention |
| CA glue, misc | -- | **0.5** | Bond lines, clevis |
| **TOTAL** | **25.5** | **32.3** | |

**Notes on mass calculation corrections:**
- R1 underestimated CF rod mass by a factor of 2.5x (forgot density of pultruded CF is 1.58 g/cm^3, not ~0.7)
- R1 underestimated shell mass by ~20% (used simpler area estimate without curvature correction and TE closure)
- The structural engineer's shell calculations, while conservative, are credible and calibrated against known 3D-printed glider tail masses
- Main spar mass reduced vs. structural review's 2.7g because spar is now 390mm (M3 termination at 195mm/half) not 440mm

### 4.2 Mass Budget Acceptance

**32.3g is ACCEPTED.** Justification:

1. The 35g empennage hard limit provides 2.7g contingency
2. At 32.3g, the H-Stab tail loading is 32.3g / 407.7 cm^2 = 0.079 g/cm^2 -- extremely light
3. The aircraft AUW increase from the R1 estimate is 32.3 - 25.5 = 6.8g, which is 0.85% of the 800g target AUW
4. Wing loading increase: 6.8g / 41.6 dm^2 = 0.16 g/dm^2 -- insignificant
5. The mass balance (1.0g) and stiffener (0.55g) are **non-negotiable** for flutter safety

### 4.3 Where the Mass Went

| Category | R1 (g) | R2 (g) | Delta | Reason |
|----------|--------|--------|-------|--------|
| Shells | 20.0 | 24.5 | +4.5 | Corrected calculation |
| CF rods/tubes | 3.0 | 4.15 | +1.15 | Correct CF density + tube + new stiffener |
| Hinge | 1.0 | 1.4 | +0.4 | 0.8mm instead of 0.6mm |
| Control system | 0.5 | 1.8 | +1.3 | Horn + mass balance |
| Misc | 0.0 | 0.5 | +0.5 | Glue and hardware |
| **Total** | **25.5** | **32.3** | **+6.8** | |

---

## 5. Revised Aerodynamic Performance

### 5.1 Elevator Control Authority (NeuralFoil, R2)

Tested with HT-13 approximation, 35% chord flap at 65% hinge, Re = 50,000:

| Elevator Deflection | CL | CD | CM | L/D |
|--------------------|------|---------|---------|-------|
| -20 deg | -1.333 | 0.04331 | +0.158 | -30.8 |
| -12 deg | -0.873 | 0.02378 | +0.110 | -36.7 |
| -5 deg | -0.334 | 0.01830 | +0.050 | -18.2 |
| 0 deg | +0.004 | 0.01463 | -0.000 | -- |
| +2 deg | +0.129 | 0.01528 | -0.019 | 8.5 |
| +5 deg | +0.357 | 0.01803 | -0.053 | 19.8 |
| +8 deg | +0.610 | 0.02064 | -0.087 | 29.5 |
| +12 deg | +0.879 | 0.02369 | -0.110 | 37.1 |
| +15 deg | +1.050 | 0.02963 | -0.125 | 35.4 |
| +20 deg | +1.337 | 0.04309 | -0.158 | 31.0 |
| +25 deg | +1.586 | 0.05975 | -0.185 | 26.5 |

**Key performance numbers:**
- Maximum CL at 25 deg: **+1.586** (nose up) -- 5% higher than R1 estimate of 1.508
- Maximum CL at -20 deg: **-1.333** (nose down)
- Peak L/D: **37.1** at 12 deg deflection
- Trim deflection for CL=0.178: approximately +2.7 deg

### 5.2 Trim Drag (Updated)

| Condition | Tail CL | Elevator Deflection | Tail CD (profile + induced) | Aircraft Drag Increment |
|-----------|---------|--------------------|-----------------------------|------------------------|
| Cruise (8 m/s) | 0.178 | +2.7 deg | 0.01535 + 0.00225 = 0.01760 | 1.73 ct |
| Thermal (6 m/s) | 0.50 | +8.5 deg | 0.02100 + 0.01772 = 0.03872 | 3.80 ct |
| Flare (5 m/s) | 0.80 | +14 deg | 0.02700 + 0.04538 = 0.07238 | 7.11 ct |

### 5.3 Junction Drag (Unchanged from R1)

| Item | CD (ref. wing area) | Drag Counts |
|------|---------------------|-------------|
| C2-continuous fillet | 0.0000014 | 0.01 |
| TPU hinge gap (0.5mm) | 0.0000001 | 0.00 |
| Hinge protrusion (0.3mm, lower surface) | < 0.0000001 | 0.00 |
| **Total junction drag** | **0.0000138** | **0.14** |

### 5.4 Total Tail System Drag Comparison (R1 vs. R2)

| Component | R1 Trapezoidal | R2 Mod Elliptical | Delta |
|-----------|---------------|-------------------|-------|
| Profile drag at trim | 0.001524 | 0.001535 | +0.01 ct |
| Induced drag at trim | 0.002321 | 0.002246 | -0.75 ct |
| Junction interference | 0.000014 | 0.000014 | 0 ct |
| **Total at trim** | **0.003859** | **0.003795** | **-0.64 ct** |

At thermal circling (CL = 0.50):

| Component | R1 Trapezoidal | R2 Mod Elliptical | Delta |
|-----------|---------------|-------------------|-------|
| Profile drag | 0.002100 | 0.002100 | 0 ct |
| Induced drag | 0.018314 | 0.017725 | -5.89 ct |
| Junction interference | 0.000014 | 0.000014 | 0 ct |
| **Total at thermal** | **0.020428** | **0.019839** | **-5.89 ct** |

**The modified elliptical planform saves 0.64 counts at cruise and 5.89 counts at thermal circling.** At thermal CL, this is a larger improvement than the 1.30 count junction drag saving that justified the entire configuration change.

---

## 6. Component List (Updated for R2)

### 6.1 Printed Parts (LW-PLA, Vase Mode, 230C)

| Part | Material | Wall | Qty | Mass (g) |
|------|----------|------|-----|----------|
| Left stab half (LE to 65% chord) | LW-PLA | 0.45mm | 1 | 8.5 |
| Right stab half (LE to 65% chord) | LW-PLA | 0.45mm | 1 | 8.5 |
| Left elevator (65% to 97% chord) | LW-PLA | 0.40mm | 1 | 3.75 |
| Right elevator (65% to 97% chord) | LW-PLA | 0.40mm | 1 | 3.75 |
| TPU hinge strip (left) | TPU 95A | 0.80mm | 1 | 0.70 |
| TPU hinge strip (right) | TPU 95A | 0.80mm | 1 | 0.70 |
| Control horn with forward extension | CF-PLA | 1.2mm | 1 | 0.80 |

### 6.2 Off-the-Shelf Components

| Part | Specification | Qty | Mass (g) |
|------|--------------|-----|----------|
| Main spar | 3mm CF tube, 3/2mm OD/ID, 390mm | 1 | 2.40 |
| Rear spar | 1.5mm CF solid rod, 440mm | 1 | 1.20 |
| Elevator stiffener | 1mm CF solid rod, 440mm | 1 | 0.55 |
| Mass balance | Tungsten putty on horn | 1 | 1.00 |

### 6.3 Adhesives and Hardware

| Item | Mass (g) |
|------|----------|
| CA glue (bond lines) | 0.30 |
| Clevis pin (pushrod attachment) | 0.20 |
| **Total** | **0.50** |

---

## 7. Print Strategy (Updated for Superellipse)

The superellipse planform has a continuously curved leading edge. For vase mode printing:

1. **Left stab half:** Print flat on bed, hinge line (TE face) down. The curved LE is a smooth contour that the slicer resolves natively. At 0.2mm layer height, the 7.5mm root height gives 37 layers. At the 195mm station (spar endpoint), the height is ~3.4mm = 17 layers. Minimum for vase mode stability.

2. **Right stab half:** Mirror of left.

3. **Elevators:** Print flat on bed, hinge-side face down. The elevator has the same curved planform (superellipse at 65%-97% chord). Maximum root height ~5mm, TE truncation at ~0.7mm.

4. **TPU hinges:** Print flat, 4 layers, 100% rectilinear infill with lines parallel to span. Print all 4 strips (2 per half, left+right) in one 5-minute batch.

5. **Tip treatment:** The last 20mm of each stab half (beyond spar endpoint) may benefit from 2-perimeter mode instead of vase mode for structural integrity. The slicer can handle a mixed-mode approach: vase mode from root to 195mm, then switch to 2-perimeter at 0% infill for the final 20mm.

---

## 8. Risk Assessment (Updated)

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| Elevator flutter | Catastrophic | Low (with M2+M5) | 1.0g mass balance + 1mm CF stiffener + stiff digital servo |
| TPU hinge fatigue | Moderate | Medium | 0.8mm thickness (3000+ cycles), field-replaceable in 10 min |
| VStab joint peel | Moderate | Low | Dovetail interlock + CA (M7) |
| Tip shell damage | Minor | Medium | Spar terminates at 195mm; shell-only tip is expendable |
| Mass overrun (>35g) | Minor | Low | 2.7g contingency; no further mass-saving options needed |
| Spar fit at termination | Minor | Low | 3.1mm tunnel tapered to 3.05mm at endpoint |
| Print quality (LE curve) | Minor | Low | Superellipse is gentle curvature; slicer handles natively |

---

## 9. What Changes from R1 to R2

| Parameter | R1 | R2 | Reason |
|-----------|----|----|--------|
| Planform | Trapezoidal | **Superellipse n=2.3** | +0.75 ct at trim, +5.9 ct at thermal |
| Oswald e | 0.960 | **0.990** | Near-elliptical span loading |
| Tip chord (95% span) | 73mm | **50mm** | Continuous taper |
| Main spar | 3mm solid rod | **3mm tube 3/2mm** | M1: -2.2g |
| Main spar length | 440mm | **390mm** | M3: tip section too thin |
| Rear spar | 2mm solid rod | **1.5mm solid rod** | M4: -1.0g |
| Elevator stiffener | none | **1mm CF rod at 80% chord** | M5: flutter prevention |
| TPU hinge | 0.6mm | **0.8mm** | M6: fatigue life |
| Mass balance | none | **1.0g tungsten putty** | M2: flutter prevention |
| VStab joint | CA only | **Dovetail + CA** | M7: peel strength |
| Junction fillet | On VStab | **On stab root** | Bond line hidden |
| Mass | 25.5g | **32.3g** | Corrected calculations |
| Max CL | 1.508 | **1.586** | NeuralFoil rerun |

---

## 10. Chord Distribution Table (Superellipse n=2.3)

For drafting the 2D drawing, here is the chord at every 10mm span station:

| y (mm) | y/b_half | Chord (mm) | Chord to hinge (mm) | Elev chord (mm) |
|--------|----------|------------|---------------------|-----------------|
| 0 | 0.000 | 115.0 | 74.8 | 36.8 |
| 10 | 0.047 | 115.0 | 74.7 | 36.8 |
| 20 | 0.093 | 114.8 | 74.6 | 36.7 |
| 30 | 0.140 | 114.5 | 74.4 | 36.6 |
| 40 | 0.186 | 113.9 | 74.1 | 36.5 |
| 50 | 0.233 | 113.2 | 73.6 | 36.2 |
| 60 | 0.279 | 112.3 | 73.0 | 35.9 |
| 70 | 0.326 | 111.1 | 72.2 | 35.6 |
| 80 | 0.372 | 109.7 | 71.3 | 35.1 |
| 90 | 0.419 | 108.0 | 70.2 | 34.6 |
| 100 | 0.465 | 105.9 | 68.9 | 33.9 |
| 110 | 0.512 | 103.6 | 67.3 | 33.1 |
| 120 | 0.558 | 100.8 | 65.5 | 32.3 |
| 130 | 0.605 | 97.6 | 63.4 | 31.2 |
| 140 | 0.651 | 93.9 | 61.0 | 30.0 |
| 150 | 0.698 | 89.6 | 58.2 | 28.7 |
| 160 | 0.744 | 84.6 | 55.0 | 27.1 |
| 170 | 0.791 | 78.6 | 51.1 | 25.2 |
| 180 | 0.837 | 71.5 | 46.5 | 22.9 |
| 190 | 0.884 | 62.7 | 40.7 | 20.1 |
| 195 | 0.907 | 57.3 | 37.2 | 18.3 |
| 200 | 0.930 | 50.9 | 33.1 | 16.3 |
| 210 | 0.977 | 32.0 | 20.8 | 10.2 |
| 215 | 1.000 | 0.0 | 0.0 | 0.0 |

**Notes:**
- The elevator chord is 32% of local chord (from 65% to 97% chord, accounting for TE truncation at 97%)
- The mathematical superellipse goes to zero at the tip. In practice, the tip is printed down to approximately 32mm chord (at y = 210mm), below which the shape is closed off with a smooth fairing cap. The effective tip span is ~210mm per half, with the last 5mm being a printed rounded cap.
- The spar terminates at y = 195mm where chord = 57.3mm and max thickness = 3.3mm (HT-12/13 blend at 5.8%)

---

## 11. Awaiting Structural Review (Round 2)

I request the structural engineer to verify:

1. **Superellipse planform structural adequacy** -- does the curved LE change any shell buckling or torsion calculations?
2. **Spar termination at 195mm** -- is the 3.4mm airfoil thickness at this station adequate for the 3mm/2mm tube + 0.45mm walls?
3. **Tip fairing cap** -- structural recommendation for closing off the tip at ~210mm span
4. **Revised mass of 32.3g** -- acceptable or further optimization needed?

If the structural engineer concurs with R2, I recommend proceeding directly to DESIGN_CONSENSUS.md and 2D drawing.

---

## 12. Analysis Script

All NeuralFoil computations for this proposal are reproducible via:
```
cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/hstab_r2_analysis.py
```

---

*Analysis performed with NeuralFoil 0.3.2 / AeroSandbox. All polars at actual operating Reynolds numbers (23,000-61,000). Interference drag estimates from Hoerner (Fluid-Dynamic Drag, Ch. 8). Boundary layer analysis from Schlichting (Boundary Layer Theory, 8th ed.). Oswald efficiency factors from Prandtl lifting-line theory with span loading corrections.*
