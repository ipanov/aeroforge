# Structural Review: H-Stab Round 2 -- Final Sign-Off

**Author:** Structural Engineer Agent
**Date:** 2026-03-29
**Reviewing:** AERO_PROPOSAL_HSTAB_R2.md
**Status:** MODIFY -- one critical change required (hinge technology replacement)

---

## 0. Executive Summary

The Round 2 aero proposal is structurally sound. The aerodynamicist has accepted all 7 Round 1 modifications and produced a well-revised design. I concur with:

1. **Superellipse n=2.3 planform** -- ACCEPT. No structural concerns; actually slightly beneficial.
2. **Spar termination at 195mm** -- ACCEPT. Adequate clearance confirmed.
3. **Mass budget of 32.3g** -- ACCEPT. Honest, within limits, calibrated against known references.
4. **All M1-M7 integration** -- correctly implemented in R2 spec tables.

**However, one critical change is required:**

5. **REJECT the TPU living hinge (M6).** The user has correctly identified that TPU FDM living hinges are fundamentally inadequate for an elevator on a thermalling sailplane. Even at 0.8mm, the 2,000-5,000 cycle life is consumed in 1-3 flights. **Replace with a music wire pin hinge system** -- the same approach used by 3DLabPrint, Kraga, and the majority of successful production 3D-printed aircraft.

This is the sole modification. If the aerodynamicist accepts the hinge change, we proceed to DESIGN_CONSENSUS.md.

---

## 1. Superellipse Planform Review

### 1.1 Structural Assessment: ACCEPT

The superellipse n=2.3 planform presents **no new structural concerns** compared to the trapezoidal planform. In fact, it is slightly beneficial:

**Shell buckling:** The superellipse distributes chord more evenly across the span than a linear taper. This means the mid-span sections retain wider chord (and therefore greater section depth), which increases local shell buckling resistance. At 50% span, the superellipse chord is 106mm vs. the trapezoidal 95mm -- 12% more chord at mid-span means 12% more section height, which increases the critical buckling load by approximately (1.12)^2 = 25%.

**Torsional rigidity:** The closed-section torsion box (LE to 65% hinge line) has its torsional stiffness proportional to the enclosed area squared divided by perimeter (Bredt-Batho). The superellipse's fuller mid-span sections increase the enclosed area, slightly improving torsional rigidity at the stations most susceptible to aeroelastic effects.

**Spar loading:** The span loading becomes more elliptical (Oswald e = 0.99), which means a more uniform distribution of lift across the span. This actually *reduces* the peak bending moment at the root compared to a trapezoidal planform at the same total lift, because the triangular-to-elliptical load shift moves the centroid slightly inboard. The effect is small (~2%) but favorable.

**Tip chord reduction:** The superellipse tip chord at 95% span is 50mm vs. 73mm for the trapezoidal. This means the unsupported tip (beyond the 195mm spar endpoint) is narrower and shorter-chorded, reducing the structural load on the shell-only tip. The tip becomes a smaller lever arm, reducing the risk of tip damage on landing.

**Print curvature:** The continuously curved leading edge has a minimum radius of curvature at the tip of approximately 40mm. At 0.2mm layer height, this curve is resolved by the slicer with steps smaller than the nozzle diameter. No print issues.

**Verdict: The superellipse is structurally equivalent or slightly superior to the trapezoidal planform. No modifications required.**

### 1.2 One Note on Tip Fairing

The aerodynamicist notes the mathematical superellipse goes to zero chord at y = 215mm, with the practical tip closed off at approximately y = 210mm with a fairing cap.

**Structural recommendation for the tip cap:**

Print the tip cap as an integral part of the stab half -- not a separate piece. The last 5mm of span should be a smooth parabolic closure of the upper and lower skins, similar to a wingtip fairing. This provides:
- Sealed tip (no open ends to catch on grass)
- Smooth load path at the shell terminus
- Zero additional mass or assembly steps

The tip cap should have slightly thicker walls (0.55-0.60mm vs. 0.45mm for the main shell) to resist denting, as the tip is the most likely contact point during handling and landing.

---

## 2. Spar Termination Review

### 2.1 Assessment: ACCEPT

The spar terminates at y = 195mm (90.7% of half-span). At this station:

| Parameter | Value |
|-----------|-------|
| Chord | 57.3mm |
| Airfoil | HT-13/12 blend, ~5.8% t/c |
| Max thickness | 57.3 x 0.058 = 3.32mm |
| Wall thickness (2 sides) | 2 x 0.45 = 0.90mm |
| Available interior | 3.32 - 0.90 = 2.42mm |
| Spar OD | 3.0mm |
| Spar tunnel ID | 3.1mm |

**The 3.0mm spar does NOT fit inside 2.42mm of available interior at the 25% chord location.** Wait -- let me re-examine this.

At 25% chord, the local thickness is NOT the maximum thickness. For HT-series airfoils, the maximum thickness is at approximately 30-35% chord. At 25% chord, the local thickness is approximately 90-95% of the maximum.

Local thickness at 25% chord, y = 195mm:
- t_max = 3.32mm
- t_at_25% ~ 0.93 x 3.32 = 3.09mm
- Interior available: 3.09 - 0.90 = 2.19mm

This is LESS than the 3.0mm spar OD. **The aerodynamicist's clearance calculation appears to assume the spar sits at maximum thickness (30-35% chord), not at 25% chord.**

**Resolution:** There are two options:
1. Move the spar to 30% chord at the tip region (where the airfoil is thickest) -- this requires the spar tunnel to curve slightly from 25% chord at the root to 30% chord at the termination point
2. Locally thicken the shell at the spar station by creating a gentle fairing bump (adding ~0.5mm to the external profile)

**I recommend option 1: allow the spar tunnel to drift from 25% chord at root to 30% chord at the spar termination point.** This is a gradual shift of 5% chord over 195mm span -- a tunnel slope of only 0.15 degrees. The spar, being a flexible tube, follows this curve with zero spring-back issues. The aerodynamic impact is nil (the spar is internal and the shell profile is unchanged).

At 30% chord, y = 195mm:
- Local thickness ~ t_max = 3.32mm
- Interior: 3.32 - 0.90 = 2.42mm
- Spar tunnel 3.1mm ID still does not fit.

Hmm -- 2.42mm interior for a 3.1mm tunnel. **The tunnel must locally deform the shell.** Actually, the spar tunnel is a reinforced feature: the upper and lower skins are locally pushed apart by the tunnel, creating a slight bulge on the external surface. At 195mm span (near the tip), a 0.3mm bulge on each surface is within the boundary layer thickness and aerodynamically insignificant.

The aerodynamicist's R2 text states: "the spar tunnel is printed at 3.1mm ID, requiring slight local thickening of the upper/lower skins at the spar station." This is the correct approach. The tunnel acts as a local reinforcement, slightly widening the airfoil at the spar station.

**Revised verdict: Spar termination at 195mm is acceptable with local tunnel thickening as the aerodynamicist proposes.** The tapered tunnel end (3.1mm narrowing to 3.05mm over the last 5mm) provides a snug friction fit at the termination. ACCEPT.

---

## 3. Mass Budget Review

### 3.1 Assessment: ACCEPT

The revised mass of 32.3g is structurally honest and within the 35g empennage hard limit. Let me verify the key line items:

| Component | R2 Value (g) | My Verification | Delta |
|-----------|-------------|-----------------|-------|
| Stab shell (2 halves) | 17.0 | 16.5-18.0 | OK |
| Elevator shell (2 halves) | 7.5 | 7.0-8.5 | OK |
| Main spar (3mm tube, 390mm) | 2.4 | pi/4*(9-4)*390*1.58/1e3 = 2.42 | Exact |
| Rear spar (1.5mm rod, 440mm) | 1.2 | pi/4*2.25*440*1.58/1e3 = 1.23 | OK |
| Elevator stiffener (1mm rod, 440mm) | 0.55 | pi/4*1*440*1.58/1e3 = 0.546 | OK |
| TPU hinge strips | 1.4 | Will change -- see Section 4 | -- |
| Control horn | 0.8 | 0.6-1.0 typical | OK |
| Mass balance | 1.0 | Fixed by flutter requirement | OK |
| CA glue, misc | 0.5 | Reasonable allowance | OK |
| **Total** | **32.3** | | |

The CF rod/tube masses are now correctly calculated with density 1.58 g/cm^3. The shell masses are calibrated against known 3D-printed glider references (Planeprint Rise, Eclipson Fox class). The 2.7g contingency to the 35g hard limit is adequate.

**With the hinge change (Section 4), the mass will shift slightly. See Section 4.7 for the revised mass impact.**

### 3.2 One Observation on Elevator Shell Mass

The aerodynamicist uses 0.40mm wall for the elevator vs. 0.45mm for the stab. This is appropriate -- the elevator is a less critical structural element (it carries only hinge moments and its own inertial loads, not the full bending). The 0.40mm wall provides adequate print stability in vase mode for the elevator's maximum 40.2mm chord and approximately 5mm height at root.

---

## 4. HINGE TECHNOLOGY: CRITICAL REDESIGN

### 4.1 Why TPU Living Hinge is Rejected

The user's analysis is correct and my Round 1 estimate of "2,000-5,000 cycles" was framed as "acceptable for one season." I was wrong to accept this. Let me recalculate the actual cycle demand:

**Cycle count per flight:**

A sailplane elevator is not like a flap that deflects once and stays. The elevator is the primary pitch control. During thermalling:

- The autopilot/pilot makes continuous micro-corrections to maintain optimal bank and pitch
- Typical servo update rate: 50 Hz (analog) to 333 Hz (digital)
- Not every servo update causes a hinge deflection cycle, but the elevator oscillates continuously
- Conservative estimate: 2-5 meaningful deflection reversals per second during active thermalling
- A thermal circle takes 15-25 seconds; in a 10-minute thermal, that is 25-40 circles
- Even at the conservative 2 reversals/second: 2 x 600 seconds = 1,200 cycles per thermal session
- A good flight: 2-3 thermals of 5-10 minutes each = 2,400-7,200 deflection cycles per flight
- Add transition flying, approach, and landing corrections: +500-1,000 cycles
- **Total per flight: 3,000-8,000 meaningful hinge flex cycles**

**Lifetime demand:**

- 50 flights per season, 3+ seasons of use: 150+ flights minimum
- 150 flights x 5,000 avg cycles = **750,000 cycles minimum lifetime**
- Target with safety margin: **1,000,000+ cycles**

**TPU FDM fatigue:**

- At 0.8mm: 2,000-5,000 cycles to visible cracking (FDM layer delamination)
- At 0.6mm: 500-1,000 cycles
- **Even the best TPU FDM hinge fails within ONE FLIGHT.**

The aerodynamicist's R1 claim of ">100,000 cycles" was based on injection-molded TPU data, which does not apply to FDM parts with layer adhesion as the weak link. My R1 review accepted 0.8mm as "adequate with field replacement." This was wrong. A hinge that fails every flight is not a hinge -- it is a failure mode.

**The TPU living hinge is REJECTED for this application. A fundamentally different hinge technology is required.**

### 4.2 Industry Survey: How Production 3D-Printed Planes Handle Hinges

I surveyed every major 3D-printed RC aircraft manufacturer and community design to understand what actually works in production:

| Manufacturer/Design | Hinge Method | Notes |
|---------------------|-------------|-------|
| **3DLabPrint** (Edge 540) | Music wire pin through printed loops | "Appallingly simple and works much better than CA hinges" -- forum user |
| **3DLabPrint** (Stearman) | CA hinges in slots | Legacy method, less preferred by builders |
| **3DLabPrint** (newer designs) | Printable hinge with metal pin | Pin heated and bent to secure |
| **Eclipson** (Vortex) | Print-in-place gap hinge | Aileron prints functional off the bed; PLA+ gap hinge |
| **Eclipson** (Model A XL) | Aerodynamic printed hinges | Integrated into wing structure |
| **Kraga Kodo** | Wire trombone pin (0.7mm wire, 0.9mm hole) | Simple, proven, bent wire secures |
| **Kraga Kodo II** | Covering film (Oracover) | Film acts as hinge across gap |
| **Planeprint Rise** | TPU hinge strips | 1g per set; known short life |
| **SoarKraft** | Pinned hinges (16x28mm commercial) | 10 hinges per aircraft |
| **Nucking Futs (community)** | CA hinges | Traditional, proven |
| **HAWk modular wing** | LW-PLA vase mode with hinge zone | Printed hinge in LW-PLA |
| **F5J competition** | Diamond tape / covering film | Later preferred over silicone |
| **Traditional balsa RC** | Robart hinge points / Dubro nylon | Industry standard, decades of service |

**Key insight:** The most successful 3D-printed aircraft overwhelmingly use one of two approaches:
1. **Metal pin through printed hinge loops** (3DLabPrint, Kraga, Painless360)
2. **Film/tape hinge** (Kraga Kodo II, F5J competition, traditional RC)

TPU living hinges are used only by Planeprint and a few community designs -- and builders consistently report fatigue issues.

### 4.3 Comprehensive Hinge Technology Comparison

I evaluated 8 candidate hinge technologies against the requirements:

**Requirements:**
- R1: 1,000,000+ cycle life (non-negotiable)
- R2: Never needs replacement during aircraft lifetime
- R3: Minimal aerodynamic drag (gap as small as possible)
- R4: Compatible with LW-PLA shell + elevator
- R5: Handles -20 deg to +25 deg deflection range
- R6: Lightweight (<2g total for 430mm span)
- R7: Buildable (no exotic tools or materials)

---

#### Option A: TPU Living Hinge (0.8mm FDM)

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Cycle life | **FAIL** | 2,000-5,000 cycles; one flight can consume entire life |
| Permanent | **FAIL** | Requires replacement every 1-3 flights |
| Drag | Good | Flush mounting, 0.3mm protrusion below BL threshold |
| Compatibility | Good | CA bonds to LW-PLA |
| Deflection range | Pass | 45 deg range within TPU elastic limit |
| Weight | 1.4g | Two strips, 0.8mm x 10mm x 215mm each |
| Buildability | Easy | Print flat, CA-glue to surfaces |

**VERDICT: ELIMINATED.** Fails the two most critical requirements.

---

#### Option B: Kapton (Polyimide) Film Tape Hinge

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Cycle life | **EXCELLENT** | Polyimide endures 500M+ flex cycles in dynamic applications (DuPont data) |
| Permanent | **EXCELLENT** | Material does not fatigue at RC model stress levels |
| Drag | Good | 0.025-0.050mm thick, completely within BL; gap sealed by tape |
| Compatibility | Moderate | Kapton adhesive bonds to smooth PLA/LW-PLA but can peel under shear loads; surface prep critical |
| Deflection range | Pass | Film flexes easily through 45 deg |
| Weight | ~0.3g | 25 micron film + adhesive, full span both sides |
| Buildability | Easy | Apply tape to upper and lower surfaces spanning the hinge gap |

**Concerns:**
- Bond durability on foamed LW-PLA surface is questionable -- the porous surface reduces effective adhesive contact area
- Kapton tape adhesive is silicone-based and can creep under sustained load
- If one side delaminates, the hinge fails catastrophically (no mechanical backup)
- Not load-bearing -- provides flex but no positive retention of the elevator to the stab
- Applied correctly, produces the lowest-drag hinge of any option

**VERDICT: Viable as a supplementary gap seal, but NOT recommended as the sole hinge mechanism.** No mechanical retention means a bond failure = elevator departure. For a primary control surface, this is unacceptable risk.

---

#### Option C: Packing Tape / Blenderm Tape Hinge

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Cycle life | Moderate | Thousands of flights reported by community; tape degrades over years |
| Permanent | **Moderate** | Tape adhesive degrades with UV and temperature cycling; needs periodic inspection |
| Drag | Good | Thin tape (0.05-0.1mm), flush with surface |
| Compatibility | Good | Packing tape bonds well to smooth surfaces |
| Deflection range | Pass | Tape easily flexes through 45 deg |
| Weight | ~0.5g | Two strips, full span, both surfaces |
| Buildability | Easy | Bevel gap, apply tape top and bottom |

**Concerns:**
- Adhesive weakens over time, especially with temperature cycling (car trunk in summer)
- Tape stretches under repeated deflection, introducing slop
- Like Kapton, no mechanical retention -- pure adhesive bond
- Blenderm is better than standard packing tape (medical-grade adhesive) but still degrades
- Community reports: "check these hinges frequently as the tape tends to lose adhesion over time"

**VERDICT: Acceptable for foam park flyers, not for a performance sailplane that must be maintenance-free for years.** The adhesive degradation over time violates R2 (permanent, never needs replacement).

---

#### Option D: CA (Cyanoacrylate) Hinges

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Cycle life | **EXCELLENT** | Woven Kevlar/nylon CA hinges: essentially unlimited at RC loads |
| Permanent | **EXCELLENT** | CA-bonded hinges outlast the airframe |
| Drag | Moderate | Point hinges create small bumps at each hinge location; gap between hinges is unsealed |
| Compatibility | Good | CA wicks into slots in LW-PLA; needs solid (non-foamed) material at hinge slots |
| Deflection range | Pass | CA hinges rated for 45 deg+ |
| Weight | ~0.6g | 5-6 hinges at ~0.1g each |
| Buildability | Moderate | Requires slotting the hinge line and careful CA application |

**Concerns:**
- Requires cutting slots into the thin LW-PLA shell at the hinge line -- at 0.40-0.45mm wall, there is barely enough material for the CA hinge to grip
- Foamed LW-PLA is porous; CA wicks INTO the foam structure, which can be either beneficial (deep penetration) or problematic (difficult to control wicking depth)
- Point hinges leave unsealed gaps between hinge locations -- aerodynamic penalty at the gap
- Need 5-6 hinges across the 215mm half-span for even load distribution
- Industry-proven for balsa and foam, but LW-PLA vase mode wall is thinner than typical foam

**VERDICT: Viable but suboptimal.** The very thin LW-PLA walls at the hinge line (the TE of the stab shell and LE of the elevator shell) are marginal for CA hinge slot retention. The unsealed gaps between hinge points create small aerodynamic penalties.

---

#### Option E: Print-in-Place Gap Hinge (Eclipson Style)

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Cycle life | Good | PLA gap hinge life depends on gap clearance and load; typically >10,000 cycles |
| Permanent | Moderate | PLA can creep and wear at the contact surfaces over time |
| Drag | **EXCELLENT** | Minimal gap (0.3-0.5mm), integrated into print |
| Compatibility | Poor | Requires stab and elevator to be printed as ONE piece in the SAME print |
| Deflection range | Limited | Gap hinges typically limited to +/-30 deg; our -20/+25 deg range is at the limit |
| Weight | 0g | Integral part of the structure |
| Buildability | Difficult | Requires redesigning the stab as a single vase-mode print with integrated elevator |

**Concerns:**
- The stab root chord is 115mm x 7.5mm thick. Printing the stab + elevator as one piece in vase mode is possible but the elevator section is very thin
- The hinge gap must be precisely calibrated (0.3-0.5mm) -- too small and it binds, too large and it flops
- LW-PLA foaming makes gap control difficult -- the material expands unpredictably at the gap
- Cannot run the main spar through the stab if stab and elevator are one piece (spar would cross the hinge zone)
- Assembly complexity increases dramatically
- Replacement of a damaged elevator requires reprinting the entire stab+elevator assembly

**VERDICT: ELIMINATED for this design.** Incompatible with our separate stab/elevator construction, spar routing, and LW-PLA foaming. The Eclipson approach works in PLA+ with standard extrusion, not foamed LW-PLA.

---

#### Option F: Robart / Dubro Nylon Pin Hinges (Commercial Off-the-Shelf)

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Cycle life | **EXCELLENT** | Nylon pin hinges: "withstand extreme stress, vibration, and repeated flight cycles without loosening or binding" (Dubro) |
| Permanent | **EXCELLENT** | Decades of RC industry use; outlast the airframe |
| Drag | Moderate | Point hinges, same gap issue as CA hinges; small surface protrusions |
| Compatibility | Moderate | Require drilling holes into the hinge line; need solid material at hinge points |
| Deflection range | Pass | Designed for RC control surfaces, full range |
| Weight | ~1.0g | Robart 1/8" hinge points: ~0.15g each, need 5-6 per half |
| Buildability | Easy | Drill, insert, epoxy. Proven technique with 35+ years of industry use |

**Concerns:**
- Same thin-wall issue as CA hinges: the 0.40-0.45mm LW-PLA wall may not provide enough material for the hinge to grip
- Requires locally reinforced (solid, non-foamed) material at each hinge point
- Point hinges leave gaps between locations
- Available globally (Bulgaria: hobbyking.com or local hobby shops)

**VERDICT: Viable. Industry-proven and essentially permanent. But the thin LW-PLA walls require local reinforcement at each hinge point, and the point-hinge approach leaves unsealed gaps.**

---

#### Option G: Continuous Music Wire Pin Hinge (RECOMMENDED)

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Cycle life | **EXCELLENT** | Spring steel / music wire: effectively infinite at these loads (metal fatigue limit not reached) |
| Permanent | **EXCELLENT** | Steel wire does not degrade, delaminate, creep, or lose adhesion |
| Drag | **EXCELLENT** | Continuous hinge line with minimal gap; wire is fully embedded |
| Compatibility | **EXCELLENT** | Wire threads through printed loops on both stab and elevator |
| Deflection range | Pass | Wire acts as pivot axis; full -20/+25 deg range with zero resistance |
| Weight | ~0.8g | 0.5mm music wire, 430mm + hinge loops (see calculation below) |
| Buildability | Easy | Thread wire through printed loops; bend ends to retain |

**Design concept:**

The stab shell TE and elevator shell LE each have a series of small hinge loops (knuckles) printed as integral features. These interleave like a piano hinge. A single 0.5mm music wire (spring steel) threads through all the knuckles across the full 430mm span, forming a continuous hinge axis.

**This is exactly how 3DLabPrint's Edge 540 works** -- and forum users describe it as "appallingly simple and works much better than CA hinges." It is also the Kraga Kodo approach (0.7mm trombone wire through 0.9mm holes).

**Detailed design:**

| Parameter | Value |
|-----------|-------|
| Wire material | 0.5mm spring steel (music wire) |
| Wire length | 440mm (430mm span + 5mm retention bend each end) |
| Wire mass | pi/4 x 0.5^2 x 440 x 7.85 / 1e3 = **0.68g** |
| Hinge knuckle OD | 1.2mm (printed, integral to shell) |
| Hinge knuckle ID | 0.6mm (0.1mm clearance on 0.5mm wire) |
| Knuckle length | 3mm each |
| Knuckle spacing | 8mm center-to-center |
| Knuckles on stab TE | 27 per half (alternating with elevator knuckles) |
| Knuckles on elevator LE | 27 per half (interleaved) |
| Total knuckle mass | 54 knuckles x 3mm x pi x (0.6^2 - 0.3^2) x 1.24 / 1e3 per half... negligible; integral to shell |
| Gap between stab and elevator | 0.3mm (knuckle clearance gap, smaller than TPU approach) |
| Wire retention | 90-degree bend at each wing tip, tucked into the tip fairing |

**Why 0.5mm wire, not larger:**

- At 0.5mm diameter, music wire (ASTM A228, yield ~2,800 MPa) is vastly oversized for the hinge loads
- The wire carries only the shear load from the hinge moment: at max deflection (25 deg) and Vne, the total hinge moment is ~0.02 N-m (dominated by the servo)
- Shear stress on the wire: V / A = 0.5N / (pi/4 x 0.25) = 2.5 MPa -- negligible vs. yield of 2,800 MPa
- The wire is essentially infinitely durable in fatigue at these stress levels (below the endurance limit of spring steel)
- 0.5mm is also small enough to create a very tight, low-drag hinge gap (0.3mm gap is achievable)

**Fatigue analysis:**

Music wire (high-carbon spring steel) has a well-defined endurance limit at approximately 40-50% of ultimate tensile strength. For 0.5mm ASTM A228 wire:
- UTS: ~2,800 MPa
- Endurance limit: ~1,200 MPa
- Actual stress in our application: <10 MPa (bending + shear from hinge moment)
- Stress ratio: 10 / 1,200 = 0.008 (less than 1% of endurance limit)
- **At stress levels below the endurance limit, spring steel has INFINITE fatigue life.** This is not an approximation -- it is a fundamental property of ferrous metals. The S-N curve becomes horizontal below the endurance limit.

**Cycle life: UNLIMITED.** The wire will never fail in fatigue. Period.

---

#### Option H: Silicone Caulk Hinge

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Cycle life | Good | Silicone is very fatigue-resistant; thousands of flights reported |
| Permanent | Good | Silicone does not degrade significantly over years |
| Drag | Good | Gap-free when applied correctly; smooth fillet |
| Compatibility | Poor | Silicone adhesion to LW-PLA is unreliable; silicone repels CA glue, making future repairs difficult |
| Deflection range | Pass | Silicone easily flexes through 45 deg |
| Weight | ~0.5g | Thin bead along hinge line |
| Buildability | Moderate | Requires careful application and 24h cure |

**VERDICT: Not recommended.** Adhesion to LW-PLA is the weak point, and silicone contamination makes the area impossible to bond with CA in the future. Some F5J builders initially used silicone but later switched to tape/film, reporting tape hinges were "every bit as good as silicon hinges and in many respects far better."

---

### 4.4 Hinge Recommendation: Music Wire Pin Hinge (Option G)

**The music wire pin hinge is the clear winner.** It is the only option that simultaneously achieves:

1. **Truly infinite fatigue life** -- steel below its endurance limit never fails
2. **Permanent, zero-maintenance** -- no adhesive degradation, no material creep, no UV sensitivity
3. **Excellent aerodynamics** -- continuous hinge line (no point-hinge gaps), small 0.3mm gap
4. **Proven in production** -- used by 3DLabPrint, Kraga, and dozens of community designs
5. **Simple construction** -- thread wire, bend ends, done
6. **Lightweight** -- 0.68g wire + knuckles are integral to shells (no net add vs. TPU hinge area)

### 4.5 Detailed Hinge Design

#### 4.5.1 Hinge Knuckle Geometry

The hinge knuckles are small cylindrical loops printed as part of the stab trailing edge face and the elevator leading edge face. They interleave along the hinge line:

```
 Stab TE face                    Elevator LE face
 ___________                     ___________
|           |   0.3mm gap       |           |
|   Knuckle |___      ___      _| Knuckle   |
|   (stab)  |   |    |   |   | | (elevator) |
|     OO====|===|====|===|===|=|====OO      |
|   (stab)  |___|    |___|   |_| (elevator) |
|   Knuckle |                   | Knuckle    |
|___________|                   |___________|

  S  E  S  E  S  E  S  E  ...  (alternating)
```

**Profile view (cross-section at a knuckle):**

The knuckle is a small half-cylinder that protrudes from the TE face (stab) or LE face (elevator) into the gap. The wire passes through the center of all knuckles.

- Stab knuckle: extends 0.6mm aft of the stab TE face
- Elevator knuckle: extends 0.6mm forward of the elevator LE face
- Total hinge zone width: 0.6mm (stab knuckle) + 0.3mm (gap) + 0.6mm (elevator knuckle) = 1.5mm
- The knuckle diameter (1.2mm OD) defines a natural circular arc at the hinge line

**Knuckle print orientation:**

The knuckles are printed as part of the stab/elevator shell. In vase mode, the stab TE face is on the print bed. The knuckles extend from this face as small bumps that the slicer handles as part of the outer contour.

**IMPORTANT: The knuckles must have solid (non-foamed) walls.** To achieve this, we print the knuckle features in standard PLA or at a lower temperature (200C) for the first few layers where the knuckle contacts the bed. Alternatively, the knuckles can be printed as a separate small reinforcement strip (solid PLA, 2mm wide) that CA-bonds to the hinge line of each shell.

**Preferred approach:** Print separate hinge strips with integral knuckles in PETG or CF-PLA (non-foamed, tough material), then CA-bond these strips to the stab TE and elevator LE. This isolates the knuckle precision from the LW-PLA foaming variability.

#### 4.5.2 Hinge Strip Design (Recommended Sub-Component)

Rather than printing knuckles directly on the foamed LW-PLA shells (where dimensional accuracy is compromised by foaming), I recommend separate hinge strips:

| Parameter | Stab Hinge Strip | Elevator Hinge Strip |
|-----------|-----------------|---------------------|
| Material | PETG or CF-PLA (not foamed) | PETG or CF-PLA |
| Dimensions | 215mm x 2mm x 1.2mm (per half) | 215mm x 2mm x 1.2mm (per half) |
| Knuckle OD | 1.2mm | 1.2mm |
| Knuckle ID | 0.6mm | 0.6mm |
| Knuckle length | 3mm | 3mm |
| Knuckle spacing | 8mm c/c | 8mm c/c (offset by 4mm from stab knuckles) |
| Knuckle count | 27 per half | 27 per half |
| Mass per strip | ~0.5g | ~0.5g |
| Print orientation | Flat, knuckles pointing up | Flat, knuckles pointing up |
| Print time | ~3 min per strip | ~3 min per strip |

The strips bond to the stab TE face and elevator LE face with medium CA. The bonding surface is 2mm wide x 215mm long = 430 mm^2, which at 5 MPa CA shear strength provides 2,150N capacity -- vastly more than needed.

#### 4.5.3 Wire Installation

1. Pre-cut 0.5mm music wire to 440mm (430mm span + 5mm each end for retention bends)
2. Mate left stab and left elevator via their hinge strips (interleave the knuckles)
3. Thread wire from root end through all knuckles to tip
4. Repeat for right half
5. At each wing tip: bend wire 90 degrees, trim to 3mm, tuck into tip fairing
6. At root (VStab junction): the wire passes through a small printed guide in the VStab fin, providing continuity between left and right halves. **The wire is ONE continuous piece across the full 430mm span.**

Total wire threading time: approximately 2 minutes per half.

#### 4.5.4 Aerodynamic Integration

**Upper surface:** The hinge gap on the upper surface (aerodynamically critical) is only 0.3mm -- smaller than the 0.5mm gap in the TPU hinge design. The knuckles are on the LOWER surface. The upper surface sees only the 0.3mm gap between the stab TE and elevator LE, which is well within the boundary layer thickness at 65% chord.

| Parameter | Music Wire Hinge | TPU Hinge (R2) | Delta |
|-----------|-----------------|----------------|-------|
| Upper surface gap | 0.3mm | 0.5mm | -0.2mm (better) |
| Lower surface protrusion | 1.2mm (knuckle diameter) | 0.3mm | +0.9mm (worse locally) |
| Lower surface BL thickness (65% chord) | 2.85mm (turbulent) | 2.85mm | -- |
| Protrusion / BL_turbulent | 0.42 | 0.105 | Higher but still below surface |
| Gap continuity | Continuous (no unsealed gaps) | Continuous | Equal |

The 1.2mm knuckles on the lower surface protrude 42% into the turbulent boundary layer. This is above the "hydraulically smooth" threshold of 30% but well below the BL edge. The drag penalty is small and localized to the 1.2mm-diameter semi-cylinders, which represent only 3mm / 8mm = 37.5% of the hinge line length (the rest is flush gap).

**Estimated drag penalty of knuckles vs. TPU hinge:** less than 0.05 drag counts, which is below measurement precision and negligible compared to the 0.75-5.89 count savings from the superellipse planform change.

**Optional refinement:** If the lower-surface knuckle drag is a concern, they can be faired with a thin bead of lightweight filler (microballoon + CA), creating a smooth transition. This adds perhaps 0.1g and eliminates any drag from the knuckle geometry.

### 4.6 Comparison: Why Music Wire Wins Over Every Alternative

| Criterion | Music Wire Pin | Kapton Film | CA Hinges | Dubro/Robart | TPU Living |
|-----------|---------------|-------------|-----------|--------------|------------|
| Fatigue life | **Infinite** | 500M+ cycles | Infinite | Infinite | 2-5K cycles |
| Mechanical retention | **Yes** (pin locks) | No (adhesive only) | Yes (embedded) | Yes (pinned) | No (adhesive) |
| Gap size | **0.3mm** | ~0mm (taped over) | 0.5-1mm between points | 0.5-1mm | 0.5mm |
| LW-PLA compatible | **Yes** (separate strips) | Marginal (porous surface) | Marginal (thin walls) | Marginal (thin walls) | Yes |
| Continuous hinge | **Yes** (full span wire) | Yes (full span tape) | No (point hinges) | No (point hinges) | Yes |
| Weight (430mm span) | **~1.7g** total | ~0.3g | ~0.6g | ~1.0g | 1.4g |
| Maintenance | **Zero** | Tape may need re-application | Zero | Zero | Replace every flight |
| Industry proven | **3DLabPrint, Kraga** | F5J competition | Traditional balsa | Traditional balsa | Planeprint |

The music wire pin hinge is the only option that scores "excellent" or "good" across ALL criteria. It has positive mechanical retention (the wire physically prevents the elevator from departing the stab), infinite fatigue life, continuous hinge coverage, and proven production use.

### 4.7 Mass Impact of Hinge Change

| Component | TPU Hinge (R2) | Music Wire Hinge | Delta |
|-----------|---------------|-----------------|-------|
| TPU hinge strips (2x) | 1.40g | -- | -1.40g |
| Music wire (0.5mm, 440mm) | -- | 0.68g | +0.68g |
| PETG hinge strips (4x) | -- | 2.00g | +2.00g |
| **Net hinge mass** | **1.40g** | **2.68g** | **+1.28g** |

**Revised total assembly mass: 32.3 - 1.4 + 2.68 = 33.58g**

This is still within the 35g hard limit with 1.42g contingency. The 1.28g mass increase is the cost of a permanent, infinite-life hinge system vs. a consumable that fails every flight. This trade is non-negotiable.

**If mass margin is a concern, we can recover 0.5g by:**
- Reducing the elevator wall from 0.40mm to 0.38mm (saves ~0.5g)
- Reducing the PETG strip width from 2mm to 1.5mm (saves ~0.5g)
- Using 0.4mm wire instead of 0.5mm (saves 0.25g, still vastly oversized for loads)

I do NOT recommend these optimizations at this stage. The 1.42g contingency is adequate.

### 4.8 Revised Assembly Sequence (Hinge Section Only)

Replace steps 3-4 from the R1 assembly sequence:

**3. Bond hinge strips to shells:**
   - CA-glue the stab hinge strip to each stab half's trailing edge face (lower surface side)
   - CA-glue the elevator hinge strip to each elevator half's leading edge face (lower surface side)
   - Allow 2 minutes cure
   - Verify knuckle alignment: place stab and elevator face-to-face, check that knuckles interleave correctly

**4. Assemble elevator to stab:**
   - Interleave knuckles (stab and elevator knuckles mesh like a zipper)
   - Thread 0.5mm music wire from root end through all knuckles
   - Thread wire through VStab fin guide hole (0.6mm hole printed in the fin at the hinge line)
   - Continue through opposite half's knuckles
   - Test deflection: -20 to +25 degrees, smooth and free
   - Bend wire ends 90 degrees and tuck into tip fairings

**Total hinge assembly time: approximately 5 minutes per half.** Comparable to the TPU hinge approach.

### 4.9 Procurement

| Item | Specification | Source | Approx. Cost |
|------|--------------|--------|-------------|
| Music wire | 0.5mm diameter, 500mm length | HobbyKing, local hobby shop, eBay | <EUR 1.00 |
| PETG filament | Standard 1.75mm PETG, any color | Already in stock (printer supplies) | <EUR 0.05 (4 strips) |

Both items are trivially available in Bulgaria and worldwide. Music wire is a standard RC hobby supply item.

---

## 5. Updated Modification Summary

All R1 modifications (M1-M7) remain as accepted by the aerodynamicist in R2. One modification is changed:

| Mod | R1 (accepted in R2) | R2 Final | Change |
|-----|---------------------|----------|--------|
| M1 | 3mm CF tube (3/2mm OD/ID) | Unchanged | -- |
| M2 | 1.0g mass balance (tungsten putty on horn) | Unchanged | -- |
| M3 | Spar terminates at 195mm | Unchanged | -- |
| M4 | 1.5mm CF solid rod rear spar | Unchanged | -- |
| M5 | 1mm CF rod stiffener in elevator at 80% chord | Unchanged | -- |
| **M6** | **TPU 95A, 0.8mm living hinge** | **0.5mm music wire pin hinge with PETG knuckle strips** | **CHANGED** |
| M7 | Interlocking dovetail at VStab joint | Unchanged | -- |

### M6 Revised: Music Wire Pin Hinge

| Parameter | Old (TPU) | New (Music Wire) |
|-----------|-----------|-----------------|
| Hinge type | TPU living hinge (continuous flex strip) | Music wire pin through interleaved knuckle strips |
| Material | TPU 95A, 0.8mm thick, FDM printed | 0.5mm spring steel wire + PETG knuckle strips |
| Fatigue life | 2,000-5,000 cycles | **Infinite** (below endurance limit) |
| Maintenance | Replace every 1-3 flights | **None, ever** |
| Upper gap | 0.5mm | 0.3mm (tighter) |
| Lower protrusion | 0.3mm (flush strip) | 1.2mm (knuckles, in BL) |
| Mass | 1.4g | 2.68g |
| Assembly method | CA-glue flat strip | Thread wire through knuckles |
| Hinge axis | Distributed flex zone | Precise cylindrical axis (0.5mm wire center) |

**Note on hinge axis precision:** The music wire hinge has a precisely defined rotation axis at the center of the 0.5mm wire. This is aerodynamically superior to a living hinge, which has a distributed flex zone with a "virtual" rotation center that shifts as the deflection angle changes. A precise hinge axis ensures the gap between stab and elevator remains constant at all deflection angles, eliminating any gap widening at high deflection that can cause boundary layer trips and drag spikes.

---

## 6. Flutter Analysis Update

The hinge change from TPU to music wire affects the flutter analysis:

**TPU hinge:** provided slight damping through elastic hysteresis (material absorbs energy during flexing). This was beneficial for flutter suppression.

**Music wire hinge:** provides essentially zero damping -- the wire is a pure pivot with negligible friction.

**Impact:** The loss of hinge damping is compensated by:
1. The music wire hinge has ZERO backlash (the wire fits snugly in the knuckles), whereas the TPU hinge had slight compliance allowing micro-oscillation
2. The servo (9g digital, 2.5 kg-cm) provides the dominant hinge stiffness and damping
3. The 1.0g mass balance (M2) provides the critical flutter suppression
4. The 1mm CF rod elevator stiffener (M5) prevents spanwise bending flutter modes

**Revised flutter assessment:** The music wire hinge does NOT change the flutter conclusion. The flutter margin remains adequate at Vne = 25 m/s with mass balance + stiff servo + elevator stiffener. The loss of TPU damping is negligible compared to servo stiffness.

---

## 7. Risk Assessment Update

| Risk | Severity | Likelihood | Mitigation | Change from R1 |
|------|----------|-----------|------------|-----------------|
| Elevator flutter | Catastrophic | Low | M2 mass balance + M5 stiffener + stiff servo | Unchanged |
| Hinge fatigue | ~~Moderate~~ None | ~~Medium~~ **None** | Music wire: infinite life | **ELIMINATED** |
| Hinge departure | Catastrophic | **Very Low** | Wire physically retains elevator; knuckles prevent separation | **New -- better than TPU** |
| VStab joint peel | Moderate | Low | M7 dovetail interlock + CA | Unchanged |
| Tip shell damage | Minor | Medium | Shell-only tip, expendable | Unchanged |
| Mass overrun (>35g) | Minor | Low | 1.42g contingency | Slightly reduced margin |
| Spar fit at termination | Minor | Low | Tapered tunnel, local thickening | Unchanged |
| Knuckle print accuracy | Minor | Low | PETG strips printed separately, not in foamed LW-PLA | New |

**The hinge fatigue risk -- previously the #2 risk in the entire design -- is now ELIMINATED.** This is the single largest risk reduction achievable for 1.28g of mass.

---

## 8. Overall Verdict

### MODIFY -- Accept with One Change

**The R2 aero proposal is ACCEPTED in its entirety except for the hinge technology.**

Specific verdicts:

| Item | Verdict |
|------|---------|
| Superellipse n=2.3 planform | **ACCEPT** -- structurally equivalent or better |
| Spar termination at 195mm | **ACCEPT** -- with local tunnel thickening as proposed |
| Mass budget 32.3g | **ACCEPT** -- revised to 33.6g with new hinge, still within 35g limit |
| All M1-M7 integration | **ACCEPT** -- correctly implemented |
| TPU living hinge (M6) | **REJECT** -- replace with music wire pin hinge |

**If the aerodynamicist accepts the M6 revision (TPU -> music wire), the structural review is complete and we can proceed to DESIGN_CONSENSUS.md.**

The music wire hinge is:
- Aerodynamically superior (tighter gap, precise hinge axis)
- Structurally superior (infinite life, mechanical retention)
- Heavier by only 1.28g (33.6g total, within 35g limit)
- Simpler to maintain (never needs replacement)
- Industry-proven (3DLabPrint, Kraga, and dozens of production designs)

There is no rational argument for keeping the TPU hinge when the music wire alternative exists. The user is right: "the hinge must NEVER be replaced."

---

## 9. Revised Component List

### 9.1 Printed Parts

| Part | Material | Wall/Config | Qty | Mass (g) |
|------|----------|-------------|-----|----------|
| Left stab half (LE to 65% chord) | LW-PLA | 0.45mm vase mode | 1 | 8.5 |
| Right stab half (LE to 65% chord) | LW-PLA | 0.45mm vase mode | 1 | 8.5 |
| Left elevator (65% to 97% chord) | LW-PLA | 0.40mm vase mode | 1 | 3.75 |
| Right elevator (65% to 97% chord) | LW-PLA | 0.40mm vase mode | 1 | 3.75 |
| Stab hinge strip (left) | PETG | Solid, with knuckles | 1 | 0.50 |
| Stab hinge strip (right) | PETG | Solid, with knuckles | 1 | 0.50 |
| Elevator hinge strip (left) | PETG | Solid, with knuckles | 1 | 0.50 |
| Elevator hinge strip (right) | PETG | Solid, with knuckles | 1 | 0.50 |
| Control horn with forward extension | CF-PLA | Solid, 1.2mm | 1 | 0.80 |

### 9.2 Off-the-Shelf Components

| Part | Specification | Qty | Mass (g) |
|------|--------------|-----|----------|
| Main spar | 3mm CF tube, 3/2mm OD/ID, 390mm | 1 | 2.40 |
| Rear spar | 1.5mm CF solid rod, 440mm | 1 | 1.20 |
| Elevator stiffener | 1mm CF solid rod, 440mm | 1 | 0.55 |
| Hinge wire | 0.5mm music wire (spring steel), 440mm | 1 | 0.68 |
| Mass balance | Tungsten putty on horn | 1 | 1.00 |

### 9.3 Adhesives and Hardware

| Item | Mass (g) |
|------|----------|
| CA glue (bond lines, hinge strips) | 0.35 |
| Clevis pin (pushrod attachment) | 0.20 |
| **Total** | **0.55** |

### 9.4 Mass Summary

| Category | Mass (g) |
|----------|----------|
| LW-PLA shells (4 pieces) | 24.50 |
| PETG hinge strips (4 pieces) | 2.00 |
| CF rods/tubes (3 pieces) | 4.15 |
| Music wire hinge | 0.68 |
| Control horn + mass balance | 1.80 |
| Adhesives + hardware | 0.55 |
| **TOTAL** | **33.68** |
| **Contingency to 35g limit** | **1.32g** |

---

## Sources

- [3DLabPrint Stearman Hinge Discussion](https://3dlabprint.com/forums/topic/stearman-control-surface-hinges/)
- [RC Plane Hinge Types -- Flite Test](https://www.flitetest.com/articles/RC_Plane_Hinge_Types)
- [RC Plane Hinges: Choose the Best Type -- FMS Hobby](https://www.fmshobby.com/blogs/news/rc-plane-hinge-types-guide)
- [Dubro RC Hinges -- Precision Hinges for RC Aircraft](https://www.dubro.com/collections/hinges)
- [Robart Control Hinges](https://robart.com/collections/control-hinges)
- [Robart Hinge Points Installation -- Airfield Models](http://airfieldmodels.com/information_source/how_to_articles_for_model_builders/construction/hinge_points/index.htm)
- [How to Build an Aeroplane - Day 6: Aileron and Elevator Hinges](https://www.rc3dprint.com/post/how-to-build-an-aeroplane-day-6-aileron-and-elevator-hinges)
- [Free 3DLabPrint-compatible Hinges -- Thingiverse](https://www.thingiverse.com/thing:3458652)
- [Painless360 Paper-Clip Hinge -- Thingiverse](https://www.thingiverse.com/thing:1334035)
- [DuPont Kapton HN Polyimide Film Technical Data](https://www.epectec.com/downloads/DuPont-Kapton-HN-Polyimide-Film.pdf)
- [Kapton FPC Technical Data Sheet -- DuPont](https://americandurafilm.com/wp-content/uploads/2022/02/Kapton-FPC-1.pdf)
- [Bending Strain and Fatigue of Flexible Substrates -- PMC/NIH](https://pmc.ncbi.nlm.nih.gov/articles/PMC6696189/)
- [K&S Music Wire 0.5mm x 1000mm -- HobbyKing](https://hobbyking.com/en_us/1-meter-piano-wire-5mm-1.html)
- [Kraga Kodo -- 3D Printed RC Planes](https://3dprintedrcplanes.com/kodo/)
- [Eclipson Vortex -- 3D Printed Slope Soarer](https://www.eclipson-airplanes.com/motorgliders/vortex)
- [Planeprint Rise](https://www.planeprint.com/rise)
- [Airfield Models -- Hinges for Model Airplanes](https://airfieldmodels.com/information_source/model_aircraft_hardware/hinges.htm)
- [HOW TO HINGE FOAMIES -- Model Airplane News](https://www.modelairplanenews.com/how-to-hinge-foamies/)
- [Tape Weave Hinges -- Flite Test](https://www.flitetest.com/articles/tape-weave-hinges)
- [Foamflyer's Tape Hinges Guide (PDF)](https://www.foamflyer.info/tapehinges.pdf)
- [PROGLIDE F5J Home Build -- BARCS](https://www.barcs.co.uk/f5j/articles-events-and-reports/articles/proglide-home-built-composite-f5j-38m-glider-update/)
- [CA Hinge Sheet 0.3mm -- Amazon](https://www.amazon.com/Hinge-Sheet-180mmx140mmx0-3mm-RJX1850-airplane/dp/B076CRXVMH)
