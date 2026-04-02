# Structural Review: Fuselage OML

**Author:** Structural Engineer Agent
**Date:** 2026-03-29
**Reviewing:** AERO_PROPOSAL_FUSELAGE.md v1
**Status:** MODIFY (conditionally acceptable with 6 required changes)

---

## 1. Mass Analysis

### 1.1 Longeron Mass (4x 1.5mm solid CF rods)

The aerodynamicist's calculation is correct:
- Cross-section area per rod: pi/4 * 1.5^2 = 1.767 mm^2
- Length per rod: 1050mm
- Volume: 1.767 * 1050 = 1855 mm^3 = 1.855 cm^3
- Density (pultruded CF): 1.6 g/cm^3
- Mass per rod: 1.855 * 1.6 = **2.97g**
- Total 4 rods: **11.9g**

**Verdict: 11.9g for longerons is correct.** However, see Section 3 for why 1.5mm is insufficient.

### 1.2 Shell Mass (station-by-station calculation)

Using LW-PLA at 0.6mm wall, foamed density 0.75 g/cm^3 (mid-range of 0.7-0.85).

Shell mass per station segment = perimeter * wall_thickness * segment_length * density.

Ellipse perimeter approximation: P = pi * [3(a+b) - sqrt((3a+b)(a+3b))] (Ramanujan), where a = W/2, b = H/2.

| Segment (X mm) | Length (mm) | Avg W (mm) | Avg H (mm) | Avg Perimeter (mm) | Shell vol (mm^3) | Shell mass (g) |
|-----------------|-------------|------------|------------|---------------------|-------------------|----------------|
| 0-30 (nose ogive) | 30 | 16 | 16 | ~40 (avg, conical) | 40 * 0.6 * 30 = 720 | 0.54 |
| 30-70 (motor) | 40 | 34 | 34 | 107 | 107 * 0.6 * 40 = 2568 | 1.93 |
| 70-150 (ESC+batt fwd) | 80 | 43 | 39 | 129 | 129 * 0.6 * 80 = 6192 | 4.64 |
| 150-230 (batt+Rx) | 80 | 48 | 41 | 140 | 140 * 0.6 * 80 = 6720 | 5.04 |
| 230-350 (wing saddle+servo) | 120 | 35 | 30 | 103 | 103 * 0.6 * 120 = 7416 | 5.56 |
| 350-430 (post-wing) | 80 | 26 | 22 | 76 | 76 * 0.6 * 80 = 3648 | 2.74 |
| 430-650 (boom) | 220 | 17 | 15 | 50 | 50 * 0.6 * 220 = 6600 | 4.95 |
| 650-866 (fin blend body) | 216 | 11 | ~30 (avg w/ fin) | ~65 (est) | 65 * 0.6 * 216 = 8424 | 6.32 |
| 866-1046 (fin upper) | 180 | 6 | ~120 (avg) | ~140 (airfoil perim, est) | 140 * 0.5 * 180 = 12600 | 9.45 |

**Note on fin section (866-1046):** The VStab skin is essentially a 180mm chord airfoil, 165mm high. At 0.5mm wall (vase mode for tail surfaces per spec), the perimeter of the HT-14 at 180mm chord is approximately 2 * 180 = 360mm at root. Mean perimeter across the fin height (root to tip) is roughly (360+190)/2 = 275mm. This is a triangular planform, so I need to integrate properly.

**Revised fin skin mass:**
- VStab planform area: 226.9 cm^2 = 22,690 mm^2
- Both surfaces: 2 * 22,690 = 45,380 mm^2
- Wall thickness: 0.5mm (matching HStab spec for tail surfaces)
- Volume: 45,380 * 0.5 = 22,690 mm^3
- Add ~15% for internal ribs/structure: 26,094 mm^3
- Mass: 26.1 cm^3 * 0.75 = **19.6g** (for the entire VStab skin including the fin-body blend zone)

Wait -- this double-counts the body shell in the fin zone. Let me separate properly:

**Fin blend body (650-866, just the body tube portion):**
- Average body perimeter: ~35mm (shrinking tube)
- Volume: 35 * 0.6 * 216 = 4536 mm^3
- Mass: 4.5 * 0.75 = **3.4g**

**VStab fin skin (exposed fin above body, stations 700-1046):**
- Exposed fin height grows from 0mm at X=650 to 165mm at X=866, then tapers to 0mm at tip
- Exposed planform area (one side): approximately 226.9 cm^2 minus the blended body portion
- The VStab area of 226.9 cm^2 is the TOTAL fin planform. Approximately 70% is above the body.
- Exposed area: ~159 cm^2 per side, both sides: 318 cm^2 = 31,800 mm^2
- Wall: 0.5mm, density 0.75: 31,800 * 0.5 * 0.75 / 1000 = **11.9g**

**Revised shell mass table:**

| Section | Mass (g) |
|---------|----------|
| Nose ogive (0-30) | 0.5 |
| Motor section (30-70) | 1.9 |
| Electronics bay (70-230) | 9.7 |
| Wing saddle + servo (230-430) | 8.3 |
| Boom taper (430-650) | 5.0 |
| Fin blend body (650-866) | 3.4 |
| VStab fin skin (exposed) | 11.9 |
| **Shell subtotal** | **40.7g** |

### 1.3 Internal Structure

| Item | Material | Mass (g) | Notes |
|------|----------|----------|-------|
| Motor mount ring (CF-PETG) | CF-PETG, 2mm wall | 3.0 | 35mm dia, 30mm long, density 1.3 |
| Battery tray + CG rail | PLA or CF-PLA | 4.0 | 78mm long, 40mm wide, M3 rod |
| Bulkheads (4x at joints) | CF-PLA, 1.2mm | 3.0 | Elliptical frames with lightening holes |
| Servo mounts (2x in fuse) | CF-PETG, 1.6mm | 4.0 | 2x servo trays, reinforced |
| Wing saddle structure | CF-PLA, 1.5mm | 3.5 | Spar tunnel, dowel sockets, bolt plate |
| HStab bearing mount | PETG block + 2x brass tubes | 3.5 | Solid PETG, 30x15x15mm + brass |
| Hatch (magnets + cover) | LW-PLA + 3x magnets | 1.5 | 130x25mm cover, 3x 3mm magnets |
| Alignment dowels (steel) at joints | Steel 2mm | 1.5 | 4 joints x 2 dowels x ~0.4g |
| Longeron sleeves (printed channels) | LW-PLA | 2.0 | Integrated into shell at joints |
| **Internal structure subtotal** | | **26.0g** |

### 1.4 Total Mass Budget

| Item | Mass (g) |
|------|----------|
| LW-PLA shell (all sections) | 40.7 |
| Internal structure | 26.0 |
| Longerons (4x 1.5mm CF) | 11.9 |
| **Total** | **78.6g** |

**Verdict: The 75g target is UNDERESTIMATED by approximately 4-5g.** A realistic target is **78-85g**. This matters because the specifications.md weight budget allocates:
- Fuselage pod (printed): 50-70g
- Tail boom (carbon tube): 20-25g
- Combined: 70-95g

Since we are replacing both pod AND boom with the integrated fuselage, the combined budget of 70-95g applies. Our 78-85g estimate falls within this range, so **mass is acceptable** but has no margin. The VStab skin (11.9g) is the main driver -- this is essentially the VStab component mass that in the original budget was part of the 25-35g empennage line item.

**If we subtract the VStab mass (which belongs in the empennage budget):**
- Fuselage structure alone: 78.6 - 11.9 = **66.7g**
- This replaces the 50-70g fuselage pod + 20-25g tail boom = 70-95g budget
- We are 3-28g under budget. **Mass is fine.**

### 1.5 Impact of Upgrading to 2mm Longerons (Recommended)

- 2mm rod: area = pi/4 * 4 = 3.14 mm^2, volume per rod = 3.30 cm^3, mass = 5.28g
- Total 4 rods: **21.1g** (vs 11.9g for 1.5mm)
- Mass increase: **+9.2g**
- New fuselage total: 87.8g (or 75.9g excluding VStab skin)
- Still within the combined pod+boom budget of 70-95g: **marginally acceptable**

---

## 2. Printability Analysis

### 2.1 Section S1 -- Nose (0-260mm)

| Check | Result |
|-------|--------|
| Length | 260mm > 256mm bed height -- **FAILS** |
| Proposed fix (separate nose cone) | Reduces to 250mm -- **PASSES** |
| Print orientation | Vertical (nose up) -- good for circular cross-sections |
| Overhang | Spinner ogive has shallow angles, but elliptical widening at 70-150mm creates overhangs on the flat sides -- **needs supports or split** |
| Material | LW-PLA shell at 230C -- OK. CF-PETG motor mount printed separately |

**Issue:** Printing a 250mm tall elliptical body nose-up means the elliptical transition zone (70-230mm) will have severe overhangs on the sides where the width grows. The widest point (50mm at X=150) transitions from circular (32mm at X=70).

**Recommendation:** Print S1 in two halves (left-right split along the vertical plane). Each half is flat on the bed: 260mm long x 25mm wide x 44mm tall. Fits bed easily. Halves bonded with thin CA along the vertical seam. This is standard for fuselage pods (Eclipson, 3DLabPrint all do this). It eliminates overhangs entirely and gives excellent surface finish on the aerodynamic surfaces.

### 2.2 Section S2 -- Wing (260-430mm, 170mm)

| Check | Result |
|-------|--------|
| Length | 170mm -- **PASSES** (well within 256mm) |
| Width | 38mm -- **PASSES** |
| Height | 34mm -- **PASSES** |
| Orientation | Belly-down, horizontal -- good |
| Overhangs | Egg-shaped cross-section: top overhang moderate, printable at 45 degrees |
| Wing saddle cutout | Top opening eliminates top overhang issue |

**Verdict: PASSES.** This is the simplest section to print. The wing saddle opening on top means no bridging issues.

### 2.3 Section S3 -- Boom (430-660mm, 230mm)

| Check | Result |
|-------|--------|
| Length | 230mm -- **PASSES** |
| Max cross-section | 22x19mm -- **PASSES** (tiny) |
| Orientation | Horizontal along Y axis |
| Vase mode potential | Nearly circular, excellent candidate for vase mode |
| Wall integrity | At 0.6mm wall on a ~18mm dia tube, this is structurally fine |

**Verdict: PASSES.** Could even be vase-mode printed for minimum weight. However, longeron channels and pushrod channels require multi-perimeter printing, not pure vase mode.

### 2.4 Section S4a -- Fin Base (660-880mm, 220mm)

| Check | Result |
|-------|--------|
| Length | 220mm -- **PASSES** |
| Height | Fin grows from 0 to ~140mm -- **PASSES** bed but orientation is critical |
| Orientation | Fin laying flat (fin horizontal, fuselage body vertical) |
| Overhangs | The body-to-fin transition creates complex 3D overhangs |

**Issue:** The superelliptical blend from a 13mm circle to an airfoil shape means the geometry is genuinely 3D. Printing with the fin flat means the fuselage body tube is vertical at one end -- this 13mm tube printed vertically is fine. But the morphing zone will have overhangs where the fin grows from the body.

**Recommendation:** Print S4a with the fin lying flat on the bed (fin chord along X, fin span along Y). The fuselage body portion sticks up vertically and is small enough (13mm dia shrinking to 8.5mm) that it can be supported or printed with minimal support. The fin skin surfaces are against the bed or near-vertical -- good surface quality.

### 2.5 Section S4b -- Fin Top (880-1046mm, 166mm)

| Check | Result |
|-------|--------|
| Length | 166mm -- **PASSES** |
| Fin height at start | ~140mm, tapering to 0 |
| Max chord | ~170mm at X=880 |
| Orientation | Fin flat on bed, TE down or leading edge down |

**Verdict: PASSES.** This is essentially a tapered airfoil surface (like HStab), printable flat on the bed in vase mode. The HStab bearing mount (PETG block) should be printed separately and bonded in.

### 2.6 Printability Summary

| Section | Fits Bed | Orientation | Issues | Verdict |
|---------|----------|-------------|--------|---------|
| S1 Nose | YES (with separate nose cone) | **Left-right halves** (revised) | Overhang if printed whole | MODIFY |
| S2 Wing | YES | Belly-down | None | PASS |
| S3 Boom | YES | Horizontal | None | PASS |
| S4a Fin base | YES | Fin flat | Complex transition geometry | PASS with care |
| S4b Fin top | YES | Fin flat | None | PASS |

---

## 3. Structural Integrity

### 3.1 Longeron Analysis: 1.5mm vs 2mm CF Rods

**Open Question 1: Is 1.5mm adequate for a nose-first 10g hard landing?**

Scenario: 720g aircraft, nose-first deceleration at 10g:
- Impact force: F = m * a = 0.720 * 10 * 9.81 = **70.6 N**
- This force is distributed across the 4 longerons in bending.
- Critical section: just aft of the motor mount (X=70mm), where the fuselage transitions from rigid motor mount to shell structure.
- Bending moment at wing saddle (X=260mm) from nose impact: M = 70.6 * (260-70) / 1000 = **13.4 N*m**

**Longeron stress at X=260mm (wing saddle, longeron spacing 24x20mm):**
- I_total = 4 * (pi/64 * 1.5^4 + 1.767 * 10^2) = 4 * (0.249 + 176.7) = **708 mm^4**
  (using bottom longerons at 10mm from neutral axis)
- Stress in extreme fiber (longeron): sigma = M * y / I = 13,400 * 10 / 708 = **189 MPa**
- Pultruded CF rod tensile strength: ~1500 MPa
- Safety factor: 1500 / 189 = **7.9** -- adequate

**BUT: Euler buckling of 1.5mm rod between support points.**

The longerons are supported by printed sleeves at each joint and by intermediate bulkheads. Between supports, the rod is free to buckle. Worst case unsupported span in the electronics bay: approximately 80mm (between bulkheads).

- Euler critical load (pinned-pinned): P_cr = pi^2 * E * I / L^2
- E = 135 GPa, I = pi/64 * 1.5^4 = 0.249 mm^4, L = 80mm
- P_cr = pi^2 * 135,000 * 0.249 / 80^2 = 9.87 * 33,615 / 6400 = **51.8 N**
- Load per rod in compression (nose impact, 2 rods in compression): 70.6 / 2 = **35.3 N**
- Safety factor against buckling: 51.8 / 35.3 = **1.47** -- MARGINAL

A safety factor of 1.47 against Euler buckling is too low for a crash load case with uncertainty. The real failure mode in a nose-first crash is compression buckling of the bottom longerons.

**With 2mm rods:**
- I = pi/64 * 2^4 = 0.785 mm^4
- P_cr = pi^2 * 135,000 * 0.785 / 80^2 = **163.4 N**
- Safety factor: 163.4 / 35.3 = **4.6** -- GOOD

**RECOMMENDATION: Use 2mm solid CF rods for longerons.** The mass penalty is 9.2g but the buckling safety factor improves from 1.47 to 4.6. This is a 3x improvement for a 1.2% AUW increase. Non-negotiable for flight safety.

### 3.2 Battery Span Loading (Open Question 7)

Battery mass: 165g = 1.62N, sitting on the bottom 2 longerons over ~78mm length.
Unsupported span of bottom longerons between motor mount bulkhead (X=70) and wing saddle bulkhead (X=260): **190mm**.

Battery load as point load at center of bay (X=150mm):
- Reaction at each support: R = 1.62/2 = 0.81N (per longeron, 2 bottom rods carry the load)
- Max bending moment at battery CG: M = 0.81 * 80 = 64.8 N*mm per rod

For 2mm rod:
- Stress: sigma = M * y / I = 64.8 * 1 / 0.785 = **82.6 MPa** (well below 1500 MPa)
- Deflection: delta = F*L^3 / (48*E*I) = 0.81 * 190^3 / (48 * 135,000 * 0.785) = 0.81 * 6,859,000 / 5,086,800 = **1.09mm**

1mm deflection under battery weight is acceptable. The battery tray (printed PLA rail) distributes the load and adds stiffness. **No concern here with 2mm rods.**

For 1.5mm rods, deflection would be 1.09 * (0.785/0.249) = **3.4mm** -- visible sag. Another reason to use 2mm.

### 3.3 Joint Design (Open Question 2)

The proposed 4-longeron slip joint with CA and alignment dowels is structurally sound for normal flight loads. However:

**Concern 1: Shear at joints during landing.**
- Belly landing at 3g: F_shear = 0.720 * 3 * 9.81 = **21.2N** laterally
- Each joint has 4 longerons + 2 dowels = 6 shear members
- Shear per member: 21.2 / 6 = 3.5N -- negligible

**Concern 2: Torsion resistance.**
- CA bond on butt joint has zero torsion resistance until cured.
- The 4 longerons at their spacing provide excellent torsion resistance (I_polar = 2 * I_xx + 2 * I_yy from parallel axis theorem).
- 2x 2mm dowels at ~15mm spacing provide additional torsion lock.

**Concern 3: Pull-apart (tension along fuselage axis).**
- Only relevant in a crash scenario where the nose section is stopped and the aft section continues.
- CA butt joint: shear strength ~10 MPa on the joint face area
- Joint face at X=260 (worst case): approximately elliptical, 38x34mm, perimeter interface ~2mm wide
- Bond area: ~2 * pi * 18 * 0.6 = ~68 mm^2 (just the shell wall-to-wall contact)
- Pull-apart strength: 68 * 10 = **680N** = 680 / (0.720 * 9.81) = **96g deceleration**
- Plus the 4 longerons are CA'd in their sleeves: 4 * pi * 2 * 15 * 10 = **3770N additional**
- Total pull-apart: >4000N -- **no concern**

**Recommendation: Add printed interlocking teeth at joint faces.** Simple triangular teeth (1.5mm depth, 3mm pitch) around the joint circumference. These provide:
1. Precise axial alignment (no sliding during assembly)
2. Increased bonding surface area (+40%)
3. Mechanical interlock against shear
4. Zero weight penalty (geometry, not material)

This is a free 3D-printing advantage -- complexity costs nothing.

### 3.4 Torsional Stiffness (Flutter Check)

The fuselage must resist torsion from rudder deflection and asymmetric gusts.

**4-longeron torsional stiffness (boom section, 2mm rods at 12x10mm spacing):**
- Enclosed area of longeron rectangle: A = 12 * 10 = 120 mm^2
- Torsion constant (Bredt-Batho, thin-walled with discrete longerons): GJ_eff = 4 * G * A_rod * A^2 / (sum of L_i)
- This is complex; simpler: the 0.6mm LW-PLA shell acts as the torsion-carrying skin.
- Shell torsion: GJ_shell = 4 * A_enclosed^2 * G * t / perimeter
- At boom section (18mm dia): A_enclosed = pi/4 * 18^2 = 254 mm^2
- G_lwpla = E / (2*(1+v)) = 2000 / (2*1.35) = 741 MPa
- GJ = 4 * 254^2 * 741 * 0.6 / (pi*18) = 4 * 64,516 * 444.6 / 56.5 = **2.03 * 10^6 N*mm^2**

For a 650mm boom length, torsional deflection under 0.1 N*m rudder hinge moment:
- theta = T * L / GJ = 100 * 650 / 2.03e6 = **0.032 rad = 1.8 degrees**

This is acceptable. The shell provides adequate torsional stiffness. The longerons add to this. **No flutter concern at V < 15 m/s.**

### 3.5 Wing Attachment (Open Question 8)

The proposal specifies: wing saddle, 8mm spar tunnel, 2x 3mm dowel pins, 1x M3 nylon bolt from bottom.

**Analysis:**
- Wing bending load at root: L = m*g = 0.720 * 9.81 = 7.1N (1g flight)
- At 3g pullout: 21.2N, distributed across 1280mm half-span
- Root bending moment: M = 21.2 * 640 / 2 = **6784 N*mm** (triangular lift distribution)
- The 8mm carbon spar carries this bending. The spar tunnel in the fuselage transfers the load.

**Spar tunnel design requirement:**
- 8mm spar passes through the fuselage from left wing to right wing (continuous tube).
- The tunnel must be reinforced: CF-PLA or double-wall LW-PLA around the 8.1mm bore.
- Vertical load from wing weight/lift is carried by the saddle bearing surfaces (top of fuselage contacts bottom of wing root).
- The M3 nylon bolt prevents the wing from lifting off in negative-g maneuvers or inverted flight.

**Concern:** A single M3 nylon bolt is marginal for anti-lift retention. Nylon M3 tensile strength ~30-40 MPa, root area ~5.0 mm^2. Ultimate load: 150-200N. At 5g: retention force = 0.260 * 5 * 9.81 = ~12.7N per wing half. Safety factor: 150/12.7 = **11.8** -- actually fine.

**Additional concern:** Wing torsion must be reacted. The 2x 3mm dowels provide anti-rotation. Verify dowel spacing is at least 30mm for adequate moment arm.

**Recommendation: ACCEPTABLE** as proposed. Ensure dowel spacing >= 30mm and spar tunnel wall thickness >= 1.5mm (CF-PLA recommended for the spar tunnel zone).

---

## 4. Thermal and Material Concerns

### 4.1 Motor Thermal Isolation (Open Question 3)

The Hacker A20-22L can reach 80C on the can during extended full-power climbs (10-second F5J motor runs).

**LW-PLA glass transition: 55-60C.** At 80C, LW-PLA will soften and deform under load.

The motor mount ring is already specified as CF-PETG (HDT ~80-90C under load), which is correct. But the proposal has LW-PLA shell immediately adjacent to the motor mount.

**Thermal analysis:**
- Motor run duration: 10 seconds (F5J standard)
- Motor can temperature after 10s run: approximately 50-60C (not the steady-state 80C)
- Temperature at shell wall (6mm from motor can, separated by air gap): approximately 40-45C
- LW-PLA is safe up to 55C.

**For extended motor runs (thermal soaring, not F5J):**
- 30-second run: motor can at 70-80C
- Shell temperature: 50-60C -- **approaching LW-PLA limit**

**Recommendation:** Use standard PETG (not LW-PLA) for the motor section shell (X=30 to X=90mm). This is only 60mm of shell. PETG density 1.27 g/cm^3 vs LW-PLA 0.75 g/cm^3 -- mass increase: (1.27-0.75) * 0.6 * 107 * 60 / 1000 = **2.0g**. Acceptable weight penalty for thermal safety. The PETG section bonds to the LW-PLA aft section with CA at the X=90mm joint.

Alternatively, add a thin (0.3mm) PTFE or aluminum foil heat shield between motor mount and LW-PLA shell. But the PETG shell section is simpler and more reliable.

### 4.2 VStab Root Thickness (Open Question 4)

HT-14 at 180mm root chord: max thickness = 7.5% * 180 = **13.5mm** at ~28% chord (50.4mm from LE).

Contents that must fit at root section:
- 2x 1.5mm CF longeron channels (top pair, transitioning into fin LE): need 2.5mm dia sleeves each = 5mm total
- 1x 1.5mm CF rear spar at 60% chord: needs 2.5mm dia sleeve
- Skin: 2x 0.5mm = 1.0mm

**At LE spar location (28% chord, where thickness is 13.5mm):**
- Available internal height: 13.5 - 2*0.5 (skin) = 12.5mm
- 2 longeron channels (vertically stacked or side-by-side): 2 * 2.5 = 5.0mm
- Remaining: 7.5mm for air gap and structure -- adequate

**At rear spar location (60% chord):**
- HT-14 thickness at 60% chord: approximately 5.5% * 180 = ~9.9mm (reading off typical HT-14 coordinates, thickness decreases aft of max)
- Actually, more precisely: HT-14 at 60% chord has approximately 5.0% local thickness = 9.0mm
- Internal: 9.0 - 1.0 (skin) = 8.0mm
- Rear spar channel: 2.5mm
- Remaining: 5.5mm -- adequate

**Verdict: 13.5mm root thickness is SUFFICIENT** for all internal structure. The critical point is where the 2 upper longerons transition from horizontal (in the body) to vertical (in the fin LE). This transition must occur over at least 50mm of span to avoid sharp bends in the CF rods. Since the fin blend zone is 216mm long (X=650 to X=866), there is ample length for this transition.

**However:** With 2mm longerons (recommended), the sleeves need 3.0mm diameter. Two channels = 6.0mm. Still fits in the 12.5mm available space. **No issue.**

### 4.3 HStab Bearing Alignment (Open Question 6)

PETG block with 2x brass tubes (4mm OD / 3mm ID), 28mm spacing.

**Achievable tolerance on a Bambu P1S:**
- Hole position accuracy: +/-0.15mm (typical FDM)
- Hole diameter accuracy: +/-0.1mm
- After pressing in brass tubes: alignment depends on bore fit

**The problem:** Two 3mm bores, 28mm apart, must be coaxial within ~0.1mm to allow the 3mm CF pivot rod to slide freely. FDM printing with +/-0.15mm position error means the two holes could be offset by up to 0.3mm -- the rod will bind.

**Recommendation: Post-print reaming is REQUIRED.**
1. Print the PETG block with 2.8mm pilot holes (undersized)
2. Press brass tubes in with cyanoacrylate
3. Ream both bores simultaneously with a 3.1mm reamer passed through both tubes
4. This ensures coaxiality to within ~0.05mm

Alternatively, print the PETG block as one piece with a single long bore (28mm deep, 3.1mm ID) instead of two separate tubes. A single bore is inherently coaxial. Then press brass tube liners in from each end.

**Verdict: Achievable with post-processing.** Budget 1 extra minute of hand work. Not a design blocker.

---

## 5. Responses to Open Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | 1.5mm vs 2mm longerons | **Use 2mm.** Buckling SF improves from 1.47 to 4.6. Mass penalty 9.2g is acceptable. |
| 2 | Slip joints vs interlocking | **Add interlocking teeth** to joint faces. Free complexity, better alignment, +40% bond area. |
| 3 | Motor thermal | **Use PETG shell** for X=30-90mm (motor section only). +2g, prevents softening. |
| 4 | VStab root thickness | **13.5mm is sufficient.** Even with 2mm longerons, all channels fit. |
| 5 | S4 print orientation | **Fin flat on bed.** S4a: fin horizontal, body tube vertical (small, supportable). S4b: standard flat airfoil print. |
| 6 | HStab bearing tolerance | **Post-print reaming required.** Print 2.8mm pilot holes, press brass tubes, ream to 3.1mm through both simultaneously. |
| 7 | Battery on longerons | **No concern with 2mm rods.** 1.1mm deflection. With 1.5mm: 3.4mm sag -- unacceptable. Another reason for 2mm. |

**Additional question 8 (wing saddle):**
- 8mm spar passes through fuselage continuously (left wing to right wing)
- Saddle + spar tunnel + 2 dowels + 1 M3 bolt is structurally adequate
- Spar tunnel should be CF-PLA reinforced (1.5mm wall minimum)
- Dowel spacing >= 30mm for torsion resistance

---

## 6. Proposed Modifications (with mass impact)

| # | Modification | Reason | Mass Impact |
|---|-------------|--------|-------------|
| **M1** | Longerons: 2mm solid CF rods (not 1.5mm) | Buckling SF 1.47 -> 4.6, battery sag 3.4mm -> 1.1mm | **+9.2g** |
| **M2** | S1 nose: Print as left-right halves | Eliminates overhang problem, better surface finish | +0g (same material) |
| **M3** | Motor section shell: PETG (X=30-90mm) | Thermal protection from 80C motor | **+2.0g** |
| **M4** | Joint faces: Add interlocking teeth | Better alignment, stronger bond, free complexity | +0g |
| **M5** | HStab bearing: Single long bore + brass liners | Simpler, inherently coaxial | +0g |
| **M6** | Spar tunnel: CF-PLA reinforcement (1.5mm wall) | Wing bending load transfer | **+1.0g** |
| **Net mass change** | | | **+12.2g** |

**Revised fuselage mass: 78.6 + 12.2 = ~91g** (including VStab skin)
- Excluding VStab skin (empennage budget): **~79g** for fuselage structure
- Combined pod+boom budget in specs: 70-95g
- **Within budget at 79g** (though near the upper end)

---

## 7. Overall Verdict

### MODIFY

The aerodynamic proposal is thorough, well-researched, and fundamentally sound. The integrated fuselage concept is a genuine improvement over pod-and-boom for this aircraft. The cross-section schedule, taper profile, and fin integration strategy are all aerodynamically correct.

**Six required modifications** (M1-M6 above) address structural safety concerns, primarily:
1. **2mm longerons** (M1) -- non-negotiable for crash safety (buckling SF 1.47 is too low)
2. **Split nose print** (M2) -- manufacturing necessity for FDM
3. **PETG motor bay** (M3) -- thermal safety for extended motor runs
4. Interlocking joint teeth (M4), single-bore bearing (M5), and CF-PLA spar tunnel (M6) are quality improvements

**None of the modifications change the OML or aerodynamic performance.** All changes are internal structure and manufacturing method. The aero proposal's drag analysis, CG calculation, and performance comparisons remain valid.

**Risk items to monitor during detailed design:**
- VStab Vv = 0.014 is low. If flight testing shows insufficient yaw damping, the VStab height may need to increase from 165mm to 190mm. This would add ~3g to fin mass but improve Vv to ~0.017. Design the fin section split (S4a/S4b boundary) to accommodate this growth.
- The 5-section fuselage has 4 joints. Each joint is a potential crack initiation site. Inspect joints after every 20 flights.
- The longeron-to-fin-LE transition (where upper rods sweep upward) is a stress concentration. Ensure the transition radius in the printed sleeves is at least 10mm.

**Summary:** Accept the aerodynamic design. Implement the 6 structural modifications. Proceed to DESIGN_CONSENSUS.md when the aerodynamicist acknowledges the changes.
