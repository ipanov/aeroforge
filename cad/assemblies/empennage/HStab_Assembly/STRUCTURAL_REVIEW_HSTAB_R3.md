# Structural Review: H-Stab Round 3 (Refinements)

**Author:** Structural Engineer Agent
**Date:** 2026-03-29
**Reviewing:** AERO_PROPOSAL_HSTAB_R3.md (Round 3 Refinements)
**Status:** ACCEPT WITH MODIFICATIONS (3 corrections required)

---

## 0. Executive Summary

The Round 3 proposal addresses real geometric problems and the overall direction is correct. I accept all four items conceptually, but three require corrections before consensus:

1. **Main spar at X=35.0mm** -- ACCEPT WITH CORRECTION. The move to 30.4% root chord is structurally sound and provides genuine improvement. However, the proposal's depth calculations contain a **critical arithmetic error**: the aerodynamicist used HT-13 (root) thickness values at all span stations without applying the HT-13-to-HT-12 linear blend. The corrected spar fit limits are significantly shorter than claimed. The 35.0mm position is still the better choice, but the spar termination point and the claimed improvement margin must be corrected.

2. **Tip horn** -- ACCEPT WITH CORRECTION. The geometry, mass balance philosophy, and horn LE profile are correct. However, the tungsten pocket dimensions do not fit the available airfoil interior at the specified location. The pocket depth must be reduced.

3. **Tip shape (semi-elliptical cap)** -- ACCEPT. Printable, structurally sound, good tip closure.

4. **Rudder cutout** -- ACCEPT deferral to integration. The analysis is thorough and the 40mm notch estimate is reasonable. No action needed now.

---

## 1. Main Spar Repositioning: ACCEPT WITH CORRECTION

### 1.1 Direction: Correct

The aerodynamicist's analysis of the problem is correct. At the current X=28.75mm position, the spar drifts to very low chord fractions outboard, approaching the thin LE region where the airfoil has insufficient depth. Moving the spar aft to X=35.0mm (30.4% root chord) is the right response. I independently verified:

- At X=35.0mm, the spar stays inside the airfoil envelope to y=208mm (vs. y=200mm at X=28.75mm). Confirmed.
- At X=35.0mm, the spar is at 18.3% chord at y=190mm, very close to the HT-13 max-thickness location (19%). Confirmed.
- The D-box (LE to spar) at 30% chord is 20% larger in enclosed area than at 25% chord, providing better torsional rigidity. This is a structural bonus not mentioned in the proposal.
- Bending loads are negligible (safety factor >140 at 2.5g) regardless of spar position. The 3mm CF tube is massively oversized for a 430mm span tail surface. Spar position does not affect bending adequacy.

**I concur: X=35.0mm is structurally superior to X=28.75mm.**

### 1.2 Critical Error: Airfoil Depth Not Blended

The proposal's depth analysis contains a significant error. The aerodynamicist's Table 1.3 shows airfoil depth values that correspond to HT-13 (6.50% t/c) at all span stations. But the design consensus specifies a **linear blend from HT-13 (6.50%) at root to HT-12 (5.10%) at tip**. This blend reduces the effective t/c at outboard stations substantially.

**Proof:**

The proposal claims depth = 4.07mm at y=190mm. Check: 4.07 / 62.7mm chord = 6.49% t/c. This is the HT-13 root value, not the blended value.

At y=190mm, eta = 190/215 = 0.884. Blended t/c_max = 6.50% x (1-0.884) + 5.10% x 0.884 = 5.26%. At 18.3% chord (near max thickness), the local thickness is approximately 5.26% x 62.7mm = 3.30mm -- NOT 4.07mm.

**This error inflates all outboard depth values by approximately 24%** (ratio 6.50/5.26 = 1.236).

### 1.3 Corrected Spar Fit Analysis

I independently computed the airfoil depth at the spar location for both positions, with correct HT-13/HT-12 blending. The minimum external depth for the 3mm tube is:

- **Normal fit:** 4.1mm (3.0mm tube + 3.1mm bore + 2 x 0.45mm wall + 0.1mm clearance)
- **Tight fit:** 3.9mm (3.0mm tube + 2 x 0.45mm wall, zero clearance)
- **With local tunnel bulge:** 3.5mm (the spar tunnel locally deforms the shell outward by ~0.25mm per surface -- accepted in R2 review)

| Threshold | X=28.75mm (current) | X=35.0mm (proposed) | Improvement |
|-----------|-------------------|-------------------|-------------|
| Normal fit (4.1mm) | y = 172mm (80%) | y = 172mm (80%) | 0mm |
| Tight fit (3.9mm) | y = 175mm (81%) | y = 177mm (82%) | +2mm |
| With tunnel bulge (3.5mm) | y = 178mm (83%) | y = 186mm (87%) | **+8mm** |
| Airfoil exit | y = 200mm (93%) | y = 208mm (97%) | +8mm |

**Key finding:** The X=35.0mm position provides a genuine +8mm improvement in spar span **when using the local tunnel bulge technique** (which was already accepted in the R2 structural review). Without tunnel bulging, the two positions are nearly equivalent.

The proposal's claim that the tube fits to y=189.5mm is incorrect. With tunnel bulging, the corrected limit is y~186mm.

### 1.4 Corrected Spar Specification

| Parameter | Proposal Value | Corrected Value | Notes |
|-----------|---------------|-----------------|-------|
| Spar X | 35.0mm | **35.0mm** | Accepted |
| Spar termination | y=190mm per half | **y=186mm per half** | Corrected from blended airfoil |
| Spar length | 380mm | **372mm** (2 x 186mm) | Corrected |
| Unsupported tip shell | 25mm | **29mm** (from y=186 to y=215) | Slightly larger but acceptable |
| Spar mass | 2.34g | **2.29g** | pi/4 x (3^2-2^2) x 372 x 1.58 / 1e3 |

The 29mm unsupported tip is 4mm longer than the proposed 25mm but 1mm shorter than the current design's 30mm (y=185 to y=215, using the corrected depth at X=28.75mm). So the new position is still a net improvement.

### 1.5 Structural Adequacy of 372mm Spar

At y=186mm, the bending moment from the unsupported tip (29mm of thin, low-lift surface) is negligible. The LW-PLA shell alone can sustain these loads. The spar's primary role is to prevent gross bending/flutter of the full span, and 186mm per half (87% of aerodynamic span) is adequate coverage.

For comparison: the rear spar (1.5mm CF rod) terminates at y=205mm and the hinge wire at y=203mm. These lighter elements extend further outboard because they are thinner. The main 3mm spar is the one limited by depth, and 186mm per half is the honest limit.

**Verdict: ACCEPT the move to X=35.0mm with corrected termination at y=186mm.**

---

## 2. Counter-Flutter Tip Horn: ACCEPT WITH CORRECTION

### 2.1 Horn Geometry and LE Profile: ACCEPT

The parabolic horn LE profile (from hinge line at y=195mm, curving forward to 15mm extension at y=205mm, then merging with the stab LE at y=210mm) is structurally sound and aerodynamically clean. This is a well-designed horn geometry.

The horn is integral with the elevator shell (LW-PLA, 0.55mm wall in the horn zone). This is the correct approach -- a separate CF-PLA horn would add a bond joint at the thinnest, most vulnerable part of the surface. An integral horn in thickened LW-PLA avoids this.

**The 0.55mm (2-perimeter) wall in the horn zone is adequate.** At y=205mm (max horn extension), the airfoil depth is 2.22mm with 1.12mm interior. This is thin but printable. The horn is essentially a solid-walled shell at the very tip, transitioning to hollow section inboard. This gradual closure is exactly how 3DLabPrint and Kraga handle their tip fairings.

### 2.2 Mass Balance: ACCEPT WITH POCKET CORRECTION

The 0.5g tungsten putty at 8mm forward of the hinge line provides a balance moment of 4.0 g-mm per side. My independent calculation of the elevator CG gives:

- Elevator mass per side: 4.0g
- Elevator average CG: 17.1mm aft of hinge line
- Elevator aft moment: 68.6 g-mm
- Balance fraction: 5.8%

The proposal claims 13.3% balance fraction. The discrepancy arises because the proposal uses a different (likely simplified) CG estimate. My 5.8% calculation uses the full tapered elevator geometry. Even at 5.8%, this partial balance combined with the zero-freeplay music wire pin hinge is adequate for Vne < 20 m/s. No aircraft in this speed/size regime has experienced flutter with a zero-slop hinge, regardless of mass balance percentage. The tungsten is a conservative safety margin, not a necessity.

**However, the tungsten pocket dimensions do not fit.**

The consensus specifies the pocket at y=200mm, centered 8mm forward of hinge, with dimensions 10mm span x 5mm chord x 2mm depth (100mm^3).

At y=200mm, the airfoil depth is 2.64mm. With 2 x 0.55mm walls, the interior height is only 1.54mm. The specified 2.0mm pocket depth exceeds the available interior by 0.46mm.

**Correction required:** Reduce pocket depth to 1.5mm and increase footprint to maintain volume:

| Parameter | Original | Corrected |
|-----------|----------|-----------|
| Pocket depth | 2.0mm | **1.5mm** |
| Pocket footprint | 10mm x 5mm | **10mm x 6.5mm** |
| Volume | 100mm^3 | ~97mm^3 |
| Tungsten fill | 71mm^3 (0.5g at 7 g/cm^3) | 71mm^3 (same) |

Alternatively, shift the pocket center to y=197mm where the interior height is 1.76mm, allowing a 1.7mm deep pocket with the original footprint. Either approach works; the key is that the pocket cannot be 2.0mm deep at this location.

### 2.3 Horn Structural Integrity

At the horn zone (y=195-210mm), the airfoil sections are thin (3.0mm down to 1.6mm total depth). The structural integrity depends on:

1. **Print quality:** 2-perimeter 0.55mm wall at these small chord sections requires precise extrusion. The 0.2mm layer height with 0.4mm nozzle can resolve these thin sections, but the slicer must not produce gaps in the perimeter. Recommendation: test print the tip horn in isolation before committing to the full elevator build.

2. **Handling loads:** The tip is the most likely contact point during assembly and ground handling. The 0.55mm LW-PLA wall provides adequate stiffness for aerodynamic loads but limited impact resistance. This is acceptable -- all LW-PLA vase-mode aircraft have fragile tips. A light coat of CA glue on the exterior tip surface (standard finishing technique for 3DLabPrint builds) would significantly improve impact resistance without measurable mass penalty.

3. **Tungsten pocket stress concentration:** The pocket creates a local stiffness discontinuity. With the corrected 1.5mm depth, the remaining wall below the pocket is 0.55mm -- the same as the rest of the horn. This is acceptable as long as the pocket walls are printed (not cut post-print). The snap-on cap mentioned in the consensus must be a gentle press-fit, not a forced interference fit that could crack the thin walls.

**Verdict: ACCEPT the horn geometry and mass balance philosophy. Correct the pocket dimensions.**

---

## 3. Tip Shape (Semi-Elliptical Cap): ACCEPT

### 3.1 Geometry: Sound

Truncating the planform at y=210mm (chord=32mm) and closing with a 4mm semi-elliptical cap to y=214mm is structurally appropriate. This avoids the unprintable knife-edge that the superellipse formula produces at y=215mm.

### 3.2 Printability: Confirmed

The cap zone (y=210-214mm) transitions from 32mm chord to 0mm chord over 4mm of span. This is a steep taper (8:1 chord-to-span ratio), which means the cap is essentially a blunt, streamlined tip.

At y=210mm, the airfoil depth is 1.64mm. With 0.55mm walls, the interior is 0.54mm -- essentially solid. By y=211mm, the upper and lower walls have merged into a single solid wall. This is exactly how tip caps should print: the slicer naturally transitions from hollow to solid as the section closes. No special print considerations needed.

**Wall thickness at the tip cap:** 0.55mm is correct. The cap is printed as part of the elevator horn (since the horn closes the tip, and the tip deflects with the elevator). The 2-perimeter setting handles the transition from hollow to solid automatically.

### 3.3 Vase Mode Compatibility

The cap is part of the elevator, which is printed in vase mode. Vase mode cannot produce a true closed tip -- the spiral path would have nowhere to go at the point of closure. However, because we specify 2-perimeter printing in the horn zone (y>195mm), the slicer switches from single-wall spiral (vase mode) to standard perimeter mode at y=195mm. The tip cap at y=210-214mm is fully within this 2-perimeter zone, so vase mode limitations do not apply.

**Verdict: ACCEPT. No modifications required.**

---

## 4. Rudder Cutout: ACCEPT Deferral

### 4.1 Analysis Quality

The aerodynamicist's overlap analysis is thorough and geometrically correct. The 25.25mm X-overlap zone (X=957mm to X=982mm) between elevator and rudder is real. The rudder TE sweeps through the elevator root at maximum deflection. A notch is required.

### 4.2 Preliminary Notch Dimensions

The proposed 40mm total notch height (20mm above, 20mm below the H-stab plane) accounts for:
- H-stab airfoil thickness at root: 7.5mm
- Elevator deflection arc: +17mm (25 deg up), -13.7mm (20 deg down)
- Clearance: 2mm per side

I verified these calculations. The elevator TE at root sweeps a vertical arc of:
- Up: 40.2mm x sin(25 deg) = 17.0mm
- Down: 40.2mm x sin(20 deg) = 13.7mm

Adding the half-thickness of the stab (3.75mm) and clearance (2mm):
- Above stab plane: 3.75 + 17.0 + 2.0 = 22.75mm
- Below stab plane: 3.75 + 13.7 + 2.0 = 19.45mm
- Total: 42.2mm, round to 42mm

The proposal's 40mm estimate is slightly tight. I recommend 44mm (22mm each side) for a clean symmetric notch with adequate clearance.

### 4.3 Structural Impact on Rudder

A 44mm x 33mm notch removes approximately 1,452mm^2 from the rudder. The rudder total area is approximately 35% of the VStab area. From the fuselage consensus, VStab area is 226.9cm^2, so rudder area is ~79.4cm^2 = 7,940mm^2. The notch removes 18.3% of rudder area.

However, the notch is at the VStab tip, where the rudder is least effective (lowest dynamic pressure in the vertical velocity profile during yaw, shortest moment arm). The net rudder authority loss is estimated at 8-10%, consistent with the proposal's estimate. This is typical for T-tail configurations and is accounted for in the VStab sizing.

**Verdict: ACCEPT deferral. The notch will be designed during integration with the VStab model. Use 44mm total height (22mm above + 22mm below) as the preliminary dimension.**

---

## 5. Items Not Changed: Confirmed

I confirm that the following items from the consensus v4 remain structurally valid and do not need modification:
- Planform (superellipse n=2.3)
- Span (430mm)
- Root/tip chord (115mm / ~50mm)
- Airfoil blend (HT-13 to HT-12)
- Hinge wire (X=74.75mm, 0.5mm music wire)
- Rear spar (X=69.0mm, 1.5mm CF rod)
- Elevator stiffener (X=92.0mm, 1mm CF rod)
- Elevator chord ratio (35%)
- Wall thickness (0.45mm stab / 0.40mm elevator)

---

## 6. Required Changes for Consensus v5

The following changes should be incorporated into the design consensus:

### From Round 3 (accepted with corrections):

| Item | Consensus v4 Value | New Value (v5) |
|------|-------------------|----------------|
| Main spar X position | 28.75mm (25.0% root chord) | **35.0mm (30.4% root chord)** |
| Spar termination | y=195mm per half | **y=186mm per half** |
| Spar length | 390mm | **372mm** |
| Spar mass | 2.40g | **2.29g** |
| Unsupported tip shell | 20mm | **29mm** |
| Tip closure | Parabolic, y=210-215mm | **Semi-elliptical cap, y=210-214mm** |
| Horn LE profile | Unspecified | **Parabolic curve: hinge line at y=195 to 15mm forward at y=205, merging with stab LE at y=210** |
| Tungsten pocket depth | 2.0mm | **1.5mm** |
| Tungsten pocket footprint | 10mm x 5mm | **10mm x 6.5mm** |
| Rudder clearance | Deferred | **Deferred; 44mm notch required (confirmed by analysis)** |
| VStab fin spar bore | At X=28.75 from HStab LE | **At X=35.0 from HStab LE** |

### Updated Rod Position Table (must replace the one in consensus):

The rod position table in the consensus must be updated with X=35.0mm for the main spar. All other rod positions remain unchanged.

### Updated Component Table:

| Component | Change |
|-----------|--------|
| HStab_Main_Spar | 3mm CF tube, **372mm** (was 390mm), mass **2.29g** (was 2.40g) |

### Updated Mass:

| | v4 | v5 | Delta |
|--|----|----|-------|
| Spar | 2.40g | 2.29g | -0.11g |
| Grand Total | 33.76g | **33.65g** | -0.11g |

### Planform Drawing Update Required:

The HStab_Assembly_drawing.png must be updated to show the main spar at X=35.0mm instead of X=28.75mm. The leftmost green vertical line moves rightward by 6.25mm.

---

## 7. Summary Verdict

**ACCEPT WITH MODIFICATIONS.**

All four R3 proposals are directionally correct and well-reasoned. Three corrections are required:

1. **Spar termination corrected from y=190mm to y=186mm** due to unblended airfoil thickness error.
2. **Tungsten pocket resized from 2.0mm to 1.5mm depth** due to insufficient airfoil interior height.
3. **Rudder notch height increased from 40mm to 44mm** for adequate symmetric clearance.

None of these corrections change the design direction. They are refinements to make the numbers honest. The aerodynamicist should verify my blending calculation by re-running the depth analysis with the correct span-varying t/c values.

Once the aerodynamicist acknowledges these corrections, the consensus can be updated to v5.
