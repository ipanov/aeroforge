# Aero Proposal: H-Stab Assembly Round 3 (Refinements)

**Date:** 2026-03-29
**Author:** Aerodynamicist Agent
**Status:** PROPOSAL -- awaiting structural review
**Basis:** DESIGN_CONSENSUS.md v4, HStab_Assembly_drawing.png (current planform)

---

## 1. MAIN SPAR REPOSITIONING (Critical Fix)

### 1.1 Problem Statement

Examining the current drawing (`HStab_Assembly_drawing.png`), the main spar is shown as the leftmost green vertical line at X=28.75mm (25% root chord). The LE sweeps rightward as the planform tapers outboard, and the spar -- being a straight rod at fixed X -- drifts toward the LE in local chord fraction terms. The drawing clearly shows the spar very close to the LE at mid-to-outboard stations.

**Quantitative analysis of the current X=28.75mm position:**

| y (mm) | Chord | LE_x | Spar local % | Airfoil depth at spar | Status |
|--------|-------|------|-------------|----------------------|--------|
| 0 | 115.0 | 0.00 | 25.0% | 7.30mm | OK |
| 100 | 105.9 | 4.08 | 23.3% | 6.80mm | OK |
| 150 | 89.6 | 11.44 | 19.3% | 5.82mm | OK |
| 180 | 71.5 | 19.56 | 12.8% | 4.50mm | OK |
| 185 | 67.4 | 21.44 | 10.9% | 3.57mm | Marginal |
| 190 | 62.7 | 23.55 | 8.3% | 3.59mm | TIGHT (< 3.9mm needed) |
| 195 | 57.3 | 25.98 | 4.8% | 2.75mm | FAIL |
| 200 | 50.9 | 28.86 | -- | -- | EXITS AIRFOIL |

**Problems with X=28.75mm:**
1. The spar exits the airfoil at y=200mm (93% span). The consensus claims termination at y=195mm, but even there the spar is at only 4.8% chord -- essentially pressed against the LE skin with no structural depth.
2. The 3mm tube requires ~4.1mm external airfoil depth (3mm OD + 2x0.45mm shell + 0.1mm clearance). The spar physically fits only to y=185mm (86% span). Beyond that, the airfoil is too thin to accommodate the tube.
3. From y=150 to y=185, the spar is at 10-19% chord, well forward of the max thickness point. The tube sits in a thin, rapidly curving LE region where it is structurally inefficient and creates printing difficulties (tight curvature around a tube near the LE radius).

### 1.2 Airfoil Thickness Analysis

The HT-13 airfoil has **maximum thickness at 19% chord** (t/c = 6.50%). This is a forward max-thickness design typical of Drela's HT series (laminar flow tailplane airfoils).

Thickness at key chord fractions (HT-13):

| x/c | t/c | Depth at root (115mm) |
|-----|-----|----------------------|
| 15% | 6.42% | 7.38mm |
| 19% (max) | 6.50% | 7.48mm |
| 25% | 6.35% | 7.30mm |
| 30% | 6.07% | 6.98mm |
| 35% | 5.71% | 6.57mm |
| 40% | 5.31% | 6.10mm |

The spar does NOT need to be at the max thickness point. The 3mm tube only needs 4.1mm of depth. Even at 40% chord, the root provides 6.10mm -- ample margin. The critical constraint is **how far outboard the spar stays above 4.1mm depth**, not how much depth it has at the root.

### 1.3 Spar Position Options (3 Compared)

I evaluated spar X positions from 20mm to 50mm in 0.1mm increments. The key metric is **max span where depth exceeds 4.1mm** (the minimum for the 3mm tube to fit inside the shell with clearance).

| Spar X (mm) | Root chord % | Root depth | Exits airfoil at y | Tube fits to y (>4.1mm) | Unsupported tip |
|-------------|-------------|-----------|--------------------|-----------------------|----------------|
| **28.75 (current)** | 25.0% | 7.30mm | 200mm (93%) | **185mm (86%)** | 30mm |
| **35.0 (Option A)** | 30.4% | 6.95mm | 208mm (97%) | **189.5mm (88%)** | 25.5mm |
| **40.0 (Option B)** | 34.8% | 6.59mm | 212mm (99%) | **187mm (87%)** | 28mm |

**Option A (X=35.0mm, 30.4% root chord) is optimal.** Here is why:

1. **Maximizes structural span:** The tube fits (>4.1mm depth) to y=189.5mm, the best of any position tested. This is because at ~30% root chord, the spar balances two competing effects:
   - Moving aft delays the LE sweeping past the spar (extends exit point)
   - Moving aft reduces local thickness (HT-13 max thickness at 19%)
   - The sweet spot where these balance is 30-31% root chord.

2. **Adequate root depth:** 6.95mm at root for a 3mm tube gives 3.85mm clearance above and below -- more than sufficient.

3. **Reasonable chord fraction drift:** At y=190mm, the spar is at 18.3% chord (near max thickness of the local airfoil blend). Compare to the current 8.3% at the same station. The spar remains in structurally useful territory nearly 10mm further outboard.

4. **Practical termination:** The spar can terminate at y=190mm (where depth drops to ~4.1mm) instead of y=185mm. The unsupported tip shell is 25mm instead of 30mm.

### 1.4 Recommendation

**Move main spar from X=28.75mm to X=35.0mm (30.4% root chord).**

Updated spar table at key stations:

| y (mm) | Chord | LE_x | Spar local % | Airfoil depth | Status |
|--------|-------|------|-------------|---------------|--------|
| 0 | 115.0 | 0.00 | 30.4% | 6.95mm | OK (+2.85mm margin) |
| 50 | 113.2 | 0.79 | 30.2% | 6.86mm | OK |
| 100 | 105.9 | 4.08 | 29.2% | 6.49mm | OK |
| 150 | 89.6 | 11.44 | 26.3% | 5.64mm | OK |
| 180 | 71.5 | 19.56 | 21.6% | 4.62mm | OK |
| 185 | 67.4 | 21.44 | 20.1% | 4.31mm | OK |
| 190 | 62.7 | 23.55 | 18.3% | 4.07mm | Marginal (terminate here) |
| 195 | 57.3 | 25.98 | 15.7% | 3.69mm | Below min |
| 200 | 50.9 | 28.86 | 12.1% | 3.17mm | Below min |
| 208 | 42.0 | 32.68 | -- | -- | Exits airfoil |

**Changes required:**
- Spar X: 28.75 --> 35.0mm
- Spar termination: y=195mm --> y=190mm per half (the tube physically fits to ~189.5mm, round to 190mm)
- Spar length: 390mm --> 380mm (2x190mm)
- Spar mass: 2.40g --> 2.34g (negligible change)
- VStab fin bore for spar: moves from X=28.75 to X=35.0 from HStab root LE (fuselage X=917.25 instead of X=911.0)

**Impact on planform alignment:** The 45%-chord line remains at X=51.75mm. The spar moves from 25% to 30.4% of root chord. The hinge wire stays at X=74.75mm (65% root chord). The gap between spar and hinge increases from 46.0mm to 39.75mm -- this is the elevator chord region and poses no structural issue.

### 1.5 Alternative: Angled Spar

An angled spar (following the 30% chord line, curving aft with the planform taper) would stay at max structural efficiency across the full span. However:
- A carbon tube cannot be bent to follow a gentle curve
- A straight tube in a tilted bore would create manufacturing complexity
- The fixed-X straight rod is far simpler, proven in every 3DLabPrint design
- The 4.5mm improvement in fit span (185mm to 189.5mm) from the X repositioning achieves most of the benefit

**Verdict: Straight rod at X=35.0mm. Do not pursue angled spar.**

---

## 2. COUNTER-FLUTTER TIP HORN GEOMETRY

### 2.1 Current Design

The tip horn is an integral part of each elevator tip (y=195-210mm). It extends 15mm forward of the hinge line at X=74.75mm into the stab zone, with 0.5g tungsten putty in each side for partial mass balance (13.3% of elevator mass).

### 2.2 Should the Horn Extend Forward of the Hinge Line?

**Yes -- this is correct and should be retained.** The forward extension serves three purposes:

1. **Mass balance leverage.** The tungsten pocket is located 8mm forward of the hinge line (at X=74.75-8=66.75mm in local coords). Mass forward of the hinge creates a nose-heavy moment about the hinge axis that counters flutter tendency. The 0.5g at 8mm arm creates 4.0 g-mm of anti-flutter moment per side.

2. **Aerodynamic horn balance.** A horn balance is a portion of the control surface at the tip that extends forward of the hinge line, outboard of the fixed surface. This reduces the aerodynamic hinge moment (stick force) and reduces floating tendency. Per full-scale aircraft design practice (Raymer, Roskam), a horn balance of 10-20% of the control surface area reduces hinge moments by 30-50%. Our forward extension of 15mm x ~15mm span = ~225mm^2 is approximately 6% of elevator area -- modest but beneficial.

3. **Tip closure.** The stab shell ends open at the tip. The horn wraps around from the elevator side to form the aerodynamic tip closure, eliminating an open-ended airfoil (which would produce strong tip vortex drag).

### 2.3 Horn Geometry Refinement

The current specification (15mm forward extension) is adequate for the mass balance function. However, I recommend two refinements:

**A. Horn plan-view profile:** The horn leading edge (the forward edge of the extension) should follow a smooth parabolic curve from the hinge line at y=195mm to the tip closure at y=210mm. Currently unspecified -- should be:

```
Horn LE x-position (local coords):
  y=195mm: x = 74.75mm (at hinge line -- horn starts)
  y=200mm: x = 66.75mm (8mm forward -- tungsten pocket center)
  y=205mm: x = 59.75mm (15mm forward -- max extension)
  y=210mm: x = LE(y=210) = ~37.4mm (merges with stab LE at tip closure)
```

This creates a smooth, streamlined horn shape that does NOT have any sharp corners or abrupt transitions.

**B. Horn lower surface:** The horn extends below the hinge line's lower surface. The lower surface of the horn should be faired smoothly into the elevator lower surface to avoid a step. The current 1.2mm knuckle protrusion from the hinge strips ends at y=200mm (last knuckle), so the horn zone beyond y=200mm is clean.

### 2.4 Mass Balance Adequacy

Full-scale aircraft require 100% static balance (CG at or forward of hinge line). RC sailplanes at V_ne < 20 m/s operate well below the flutter boundary. Industry practice (Model Aviation, EAA guidelines) confirms that partial mass balance of 10-15% combined with zero-slop hinge is adequate. Our 13.3% partial balance with the music wire pin hinge (zero free play) is appropriate.

**No change to mass balance amount (1.0g total, 0.5g per side).**

---

## 3. TIP SHAPE

### 3.1 Current Design

The tips are currently defined by the superellipse planform formula closing to zero chord at y=215mm. The consensus describes a "parabolic tip cap" at y=210-215mm, but the drawing shows the planform simply converging to a point -- effectively a sharp tip with rapid taper.

### 3.2 Analysis of Tip Shape Options

For a low-AR tail surface (AR=4.53), the tip shape has a small but measurable effect on induced drag. Three options compared:

| Option | Description | Oswald e impact | Wetted area | Manufacturing |
|--------|------------|-----------------|-------------|---------------|
| **A. Superellipse natural** | Planform formula runs to y=215, chord->0 | Baseline | Baseline | Easiest (no modification) |
| **B. Rounded cap (semicircular)** | At y=207mm, cut and add semicircular cap, R=chord(207)/2 | +0.002 | +1.2% | Moderate |
| **C. Elliptical tip cap** | At y=205mm, replace tip with half-ellipse 10mm span x chord(205)/2 | +0.003 | +0.8% | Moderate |

### 3.3 Recommendation: Modified Superellipse with Rounded Closure

The superellipse n=2.3 already produces a tip shape intermediate between pointed and rounded. The chord at y=210mm is 32mm, which is not actually pointed -- it is a reasonable tip chord.

**However, the tip needs to close smoothly.** The superellipse formula gives chord=0 at y=215mm, creating an infinitely thin knife edge -- which is unprintable and aerodynamically undesirable (sharp trailing vortex sheet).

**Recommended modification:**

1. **Truncate the planform at y=210mm** (chord = 32mm). This is already done implicitly because the horn/closure zone handles y=210-215mm.

2. **Close the tip with a semi-elliptical cap** from y=210 to y=214mm (4mm span). The cap has:
   - y=210: full 32mm chord (continuous with planform)
   - y=214: chord = 0 (closed)
   - Profile: semi-ellipse in plan view

3. **The cap is part of the elevator tip horn** (since the horn closes the tip). It deflects with the elevator. At these tiny chords (32mm tapering to 0), the aerodynamic effect is negligible.

4. **Wall thickness in cap zone: 0.55mm** (matching horn specification). Two-perimeter printing for strength.

This gives a smooth, printable tip closure with no knife edge, minimal induced drag penalty, and clean vortex formation.

**No change to the overall span (430mm). The aerodynamic span remains effectively 420mm (210mm per half to the start of the tip cap). The 4mm cap is a fairing, not a lifting surface.**

---

## 4. H-STAB vs RUDDER OVERLAP

### 4.1 Geometry

From the Fuselage consensus (cross-section schedule):
- VStab root: LE at fuselage X=866mm, TE at X=1046mm, chord=180mm
- VStab tip (at HStab height): chord=95mm
- VStab quarter-chord is constant at X=911mm (matches HStab pivot station)

Assuming quarter-chord alignment (standard for tail surfaces, and confirmed by the cross-section table showing X=911 as both the VStab fin station and HStab pivot):

| Surface | LE (fus. X) | Hinge (fus. X) | TE (fus. X) |
|---------|-------------|----------------|-------------|
| **VStab tip** | 887.25mm | 949.00mm | 982.25mm |
| **HStab root** | 882.25mm | 957.00mm | 997.25mm |

### 4.2 Overlap Analysis

**There is a 25.25mm overlap zone** between the elevator and rudder in the X (chordwise) direction, from X=957mm to X=982mm. In this zone, both the elevator (fixed stab aft of its hinge) and the rudder (VStab aft of its hinge) are movable control surfaces.

However, the surfaces are **perpendicular**: the rudder swings left/right (about a vertical hinge), the elevator swings up/down (about a horizontal hinge). They occupy different planes.

**Physical clearance check at the junction:**

The VStab fin at the HStab station is 7mm thick (HT-14/HT-12 blend). The elevator root face is 0.5mm from the fin surface. When the rudder deflects, the rudder TE swings laterally:

| Rudder deflection | TE lateral swing | TE forward shift |
|-------------------|-----------------|-----------------|
| 15 deg | 8.6mm | 1.1mm |
| 20 deg | 11.4mm | 2.0mm |
| 25 deg | 14.1mm | 3.1mm |
| 30 deg | 16.6mm | 4.5mm |

The rudder TE at max deflection (25 deg typical for RC sailplanes) swings 14.1mm laterally. The elevator root face is 4.0mm from the fuselage centerline (half of 8mm gap = 0.5mm clearance + 3.5mm half-fin). At the X-overlap zone, the rudder TE is at 14.1mm from centerline while the elevator face is at 4.0mm -- so the rudder TE swings OUTBOARD of the elevator root face.

**But the rudder also has height.** At the junction, the rudder extends both above and below the HStab plane. The rudder TE at the HStab plane height would sweep past the elevator root. The 0.5mm gap between elevator root and fin surface provides NO clearance for a rudder surface that swings through.

### 4.3 Finding

**The rudder surface WILL interfere with the elevator at the junction** if the rudder extends up to the HStab plane height. This is a real geometric conflict.

**Resolution options:**

| Option | Description | Impact |
|--------|------------|--------|
| **A. Rudder cutout** | Cut a notch in the rudder at the HStab station height, clearing the elevator root + deflection arc. Standard practice on T-tails. | Rudder loses ~10mm height, 6% area loss. Acceptable. |
| **B. HStab position shift** | Move HStab aft so its hinge line clears the rudder TE at max deflection. Would need ~25mm aft shift. | Increases tail moment arm by 25mm (good for stability), but moves CG forward. Requires full spec update. |
| **C. Angled elevator root cut** | Bevel the elevator root faces at ~30 deg to clear the rudder swing arc. | Increases root gap, adds drag. Not recommended. |

### 4.4 Recommendation

**Option A (rudder cutout) is the standard solution.** Every T-tail and cruciform tail configuration has this feature. The rudder has a rectangular notch at the HStab crossing height.

Notch dimensions (preliminary):
- Height: HStab airfoil thickness at root (7.5mm = 6.5% of 115mm) + elevator deflection arc (40.2mm elevator chord x sin(25 deg) = 17.0mm up, sin(20 deg) = 13.7mm down) + 2mm clearance each side
- Total notch height: ~40mm (20mm above HStab plane, 20mm below)
- Width: Full rudder chord (33.25mm at VStab tip)

This is a standard cutout and does not affect rudder authority significantly. The rudder area loss is ~33mm x 40mm = 1320mm^2 out of total rudder area ~2450mm^2 (rudder is 35% of 226.9cm^2 VStab area = ~79.4cm^2 = 7940mm^2) -- about 17% loss at the tip station, but the rudder is most effective at the root (higher chord, higher dynamic pressure). Net rudder authority loss is estimated at 8-10%.

**Detailed rudder cutout geometry will be finalized during integration phase**, when the VStab 3D model is built and exact clearances can be verified with collision detection.

**This confirms the consensus v4 decision to defer rudder clearance to integration was correct**, but the analysis shows that a cutout WILL be needed -- it should not be a surprise during integration.

---

## 5. SUMMARY OF PROPOSED CHANGES

| Item | Current | Proposed | Rationale |
|------|---------|----------|-----------|
| **Main spar X** | 28.75mm (25% root chord) | **35.0mm (30.4% root chord)** | Tube fits to y=189.5mm vs 185mm; spar stays inside airfoil to y=208mm vs 200mm |
| **Spar termination** | y=195mm per half | **y=190mm per half** | Realistic fit boundary; current y=195 has only 2.75mm depth (tube needs 4.1mm) |
| **Spar length** | 390mm | **380mm** | 2x190mm |
| **Spar mass** | 2.40g | **2.34g** | Negligible |
| **Tip closure** | Parabolic, y=210-215mm | **Semi-elliptical cap, y=210-214mm** | Cleaner closure, printable, avoids knife edge |
| **Horn forward extension** | 15mm (retained) | **15mm (no change)** | Correct for mass balance + horn balance + tip closure |
| **Horn LE profile** | Unspecified | **Parabolic curve from hinge line to tip** | Smooth, streamlined, no sharp transitions |
| **Rudder clearance** | Deferred | **Rudder cutout required (~40mm tall notch)** | Physical interference confirmed at junction |
| **VStab fin spar bore** | At X=28.75 from HStab LE | **At X=35.0 from HStab LE** | Moves with spar |

### Mass Impact

| Component | Current (g) | Proposed (g) | Delta |
|-----------|------------|-------------|-------|
| Main spar | 2.40 | 2.34 | -0.06 |
| All other | 31.36 | 31.36 | 0 |
| **Total** | **33.76** | **33.70** | **-0.06** |

No meaningful mass change. All changes are geometric repositioning.

### Updated Rod Position Table (with X=35.0mm spar)

| y (mm) | Chord | LE_x | Spar X=35.0 | Rear X=69.0 | Hinge X=74.75 | Stiff X=92.0 | TE_x |
|--------|-------|------|-------------|-------------|---------------|-------------|------|
| 0 | 115.0 | 0.00 | 35.0 (30.4%) | 69.0 (60.0%) | 74.8 (65.0%) | 92.0 (80.0%) | 115.00 |
| 50 | 113.2 | 0.79 | 34.2 (30.2%) | 68.2 (60.3%) | 74.0 (65.3%) | 91.2 (80.6%) | 114.03 |
| 100 | 105.9 | 4.08 | 30.9 (29.2%) | 64.9 (61.3%) | 70.7 (66.8%) | 87.9 (83.1%) | 110.02 |
| 150 | 89.6 | 11.44 | 23.6 (26.3%) | 57.6 (64.2%) | 63.3 (70.7%) | 80.6 (89.9%) | 101.02 |
| 190 | 62.7 | 23.55 | 11.4 (18.3%) | 45.4 (72.5%) | 51.2 (81.7%) | exits | 86.21 |
| 195 | 57.3 | 25.98 | 9.0 (15.7%) | 43.0 (75.1%) | 48.8 (85.2%) | exits | 83.24 |
| 200 | 50.9 | 28.86 | 6.1 (12.1%) | 40.1 (78.9%) | 45.9 (90.2%) | exits | 79.73 |
| 205 | 42.9 | 32.43 | 2.6 (6.0%) | 36.6 (85.3%) | 42.3 (98.6%) | exits | 75.37 |
| 208 | 37.5 | 34.89 | exits | 34.1 (90.9%) | exits | exits | 72.37 |

---

## 6. ITEMS NOT CHANGED

The following are confirmed as correct and do not need modification:

- **Planform**: Superellipse n=2.3 (no change)
- **Span**: 430mm (no change)
- **Root/tip chord**: 115mm / ~50mm (no change)
- **Airfoil blend**: HT-13 root to HT-12 tip (no change)
- **Hinge wire**: X=74.75mm, 0.5mm music wire (no change)
- **Rear spar**: X=69.0mm, 1.5mm CF rod (no change)
- **Elevator stiffener**: X=92.0mm, 1mm CF rod (no change)
- **Elevator chord ratio**: 35% at root (no change)
- **Mass balance**: 1.0g tungsten in tip horns (no change)
- **Wall thickness**: 0.45mm stab / 0.40mm elevator (no change)

---

## References

- HT-13 airfoil data: `docs/rag/airfoil_database/ht13.dat` (max thickness at 19% chord, t/c=6.50%)
- Fuselage consensus: `cad/assemblies/fuselage/Fuselage_Assembly/DESIGN_CONSENSUS.md` (VStab geometry)
- Current planform drawing: `HStab_Assembly_drawing.png`
- Control surface balance: [AvWeb - Control Surface Design](http://avweb.com/flight-safety/control-surface-design-keeping-them-balanced/)
- EAA mass balance: [EAA - Control Surface Balancing](https://www.eaa.org/eaa/aircraft-building/builderresources/while-youre-building/building-articles/control-systems/control-surface-balancing-in-homebuilts)
- Flutter prevention: [Motion RC - Flutter, Balance, and VNE](https://www.motionrc.com/blogs/motion-rc-blog/control-surface-flutter-balance-and-vne)
- Drela HT airfoil series: [Charles River RC - Drela Airfoil Shop](https://charlesriverrc.org/articles/on-line-plans/mark-drela-designs/drela-airfoil-shop/)
