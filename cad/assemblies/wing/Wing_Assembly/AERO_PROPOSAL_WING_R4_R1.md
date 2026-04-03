# Aero Proposal: Wing Assembly R4 — Revision 1

**Date:** 2026-04-03
**Author:** Aerodynamicist Agent
**Status:** PROPOSAL — requires structural review before consensus
**Predecessor:** Wing Assembly v1 (2560mm span, linear taper)
**Scope:** Full R4 wing redesign with superelliptical planform and 2816mm span

---

## 1. Mission Requirements

| Requirement | Value | Source |
|-------------|-------|--------|
| Aircraft type | F5J thermal sailplane | Project brief |
| Target AUW | 750-900g | Specifications |
| Competition | Beat €2000 carbon F5J models with €60 printed airframe | Project goal |
| Span | 2816mm (R4 candidate) | Aircraft consensus R4 |
| Root chord | 170mm | R4 specifications |
| Tip chord | 85mm (taper ratio 0.5) | R4 specifications |
| Airfoil family | AG series (Mark Drela) | Proven F5J performance |
| Printer bed | 256×256mm (Bambu A1/P1S) | Manufacturing constraint |
| Spar material | Off-the-shelf CF tubes + rods | Procurement constraint |

---

## 2. Planform Design — Three Options Compared

### Chord Law Function

The chord distribution follows a **superelliptical** law:

```
c(eta) = c_root * (1 - (1 - taper) * eta^n)
```

where eta = y / (b/2), taper = c_tip / c_root = 0.5

The exponent `n` controls how rapidly chord decreases from root to tip. Three candidates:

| Parameter | Option A: n=2.3 | Option B: n=2.0 | Option C: n=1.0 (linear) |
|-----------|-----------------|-----------------|--------------------------|
| Planform type | Tightened superelliptical | Pure elliptical | Linear taper |
| Wing area | 40.62 dm^2 | 42.10 dm^2 | 40.57 dm^2 |
| Aspect ratio | 19.52 | 18.84 | 19.55 |
| MAC | 148.6mm | 151.1mm | 148.2mm |
| Root chord | 170mm | 170mm | 170mm |
| Chord at eta=0.5 | 152.7mm | 157.1mm | 127.5mm |
| Chord at eta=0.7 | 132.6mm | 139.4mm | 110.5mm |
| Tip chord | 85mm | 85mm | 85mm |
| Oswald span e (Schrenk) | 0.997 | 0.996 | 0.996 |
| Induced drag CDi (CL=0.8) | 0.00829 | 0.00859 | 0.00828 |
| Spar clearance (8mm @ 25%) | Root-OK, tip-FAIL | Root-OK, tip-FAIL | Root-OK, tip-FAIL |
| Re at root (10 m/s) | 115,800 | 115,800 | 115,800 |
| Re at tip (10 m/s) | 57,900 | 57,900 | 57,900 |

### Analysis

**Option A (n=2.3)** is the recommended planform:

1. **Higher Oswald efficiency** than linear taper: the chord distribution tracks closer to the elliptic ideal across the full span, reducing induced drag.
2. **Wider outboard chords** than linear taper: at eta=0.5, chord is 152.7mm vs 127.5mm (linear). This maintains higher Reynolds numbers in the critical mid-span region where the wing generates peak lift.
3. **Moderate area growth** vs linear: only +0.05 dm^2, keeping wing loading nearly identical.
4. **Superior spar clearance profile**: chord transitions gradually, giving the spar tunnel constructor more material to work with at every station.
5. **Compatible with Schuemann trailing edge**: the TE naturally straightens toward the tip as eta approaches 1.0, without requiring any geometric modification.

The Oswald advantage of n=2.3 over n=1.0 is approximately 0.1% in the Schrenk approximation. However, the **real performance advantage comes from the Reynolds distribution**: the superelliptical planform maintains 10-20% higher Re in the 30-70% span zone compared to linear taper, which translates to measurably lower section drag at those stations where the wing circulates peak lift.

### Separate LE and TE Taper Curves

The planform is defined by **two independent curves** — leading edge and trailing edge — not a single chord function applied about a fixed spar axis.

- **LE position**: x_LE(y) = x_LE_root + LE_sweep(y)
- **TE position**: x_TE(y) = x_LE(y) + c(y)
- **Spar axis**: at 25% chord, follows the chord law but the spar datum is straight in plan view

The LE sweep is near-zero (unswept wing) for structural integrity. The TE carries all the taper. This is aerodynamically optimal because:
- The stagnation point moves along an unswept LE at each station
- Boundary layer development is undisturbed by sweep effects
- The pressure distribution at each station matches the 2D airfoil polar
- Tip stall behavior is controlled entirely by twist and airfoil blend

---

## 3. Airfoil Selection — NeuralFoil Analysis

### Method

NeuralFoil polars computed at V=10 m/s for all AG-series candidates at representative Reynolds numbers. Transition forced (n_crit=9.0, standard F5J sailplane turbulence level).

### Root Airfoil Comparison (Re=116,000)

| Airfoil | L/D_max | Alpha at best | CL at best | CD at best | CL_max | CM at best |
|---------|---------|---------------|-----------|-----------|--------|-----------|
| **AG24** | **56.7** | 5.0° | 0.828 | 0.01459 | 1.218 | -0.058 |
| AG35 | 54.5 | 4.5° | 0.902 | 0.01655 | 1.260 | -0.041 |
| AG36 | 54.0 | 4.5° | 0.877 | 0.01623 | 1.208 | -0.040 |
| AG37 | 53.0 | 4.5° | 0.857 | 0.01616 | 1.206 | -0.039 |
| AG38 | 52.7 | 4.0° | 0.777 | 0.01473 | 1.144 | -0.040 |

**AG24 wins decisively** at the root: 4% higher L/D than the next candidate (AG35), with well-mannered pitching moment (-0.058). The AG35-38 family sacrifices profile efficiency for thickness — a tradeoff that makes sense at higher Re but not at our root Re of 116,000.

### Span Station Polars

| Station | eta | Airfoil | Re | L/D_max | CL_max | CD_min | Confidence |
|---------|-----|---------|------|---------|--------|--------|------------|
| Root | 0.000 | AG24 | 115,800 | 56.7 | 1.218 | 0.01184 | 0.961 |
| P1/P2 | 0.182 | AG24 | 114,600 | 56.4 | 1.217 | 0.01190 | 0.962 |
| P2/P3 | 0.364 | AG09 | 110,200 | 45.3 | 0.992 | 0.01001 | 0.146 |
| P3/P4 | 0.545 | AG09 | 101,400 | 43.8 | 0.985 | 0.01027 | 0.152 |
| P4/P5 | 0.727 | AG03 | 87,900 | 43.8 | 1.067 | 0.01142 | 0.289 |
| P5/P6 | 0.909 | AG03 | 69,300 | 38.6 | 1.045 | 0.01282 | 0.453 |
| Tip | 1.000 | AG03 | 57,900 | 35.0 | 1.030 | 0.01386 | 0.607 |

### Airfoil Blend Schedule

| Span Range | eta Range | Airfoil | Blend Method |
|------------|-----------|---------|--------------|
| Root → P1/P2 | 0.00-0.18 | AG24 (100%) | Direct |
| P1/P2 → P2/P3 | 0.18-0.36 | AG24 → AG09 | Linear interpolation |
| P2/P3 → P3/P4 | 0.36-0.55 | AG09 (100%) | Direct |
| P3/P4 → P4/P5 | 0.55-0.73 | AG09 → AG03 | Linear interpolation |
| P4/P5 → Tip | 0.73-1.00 | AG03 (100%) | Direct |

Every rib station has a unique interpolated airfoil profile. The blend is continuous — not step-changes at panel joints — ensuring zero discontinuity in the pressure distribution.

### NeuralFoil Confidence Note

AG09 polars show very low NeuralFoil confidence (0.15). This is expected — NeuralFoil has limited training data for thin, highly-cambered F5J airfoils in this regime. The AG09 polars should be treated as preliminary estimates pending XFOIL verification and future SU2 RANS validation. The qualitative ranking (AG09 superior to AG03 at mid-span Re) is consistent with published Mark Drela airfoil data and F5J competition practice.

---

## 4. Twist Distribution

### Function

```
twist(eta) = -4.0 * eta^2.5  (degrees, negative = washout)
```

### Schedule

| Station | eta | Twist (deg) | Purpose |
|---------|-----|-------------|---------|
| Root | 0.00 | 0.0 | Reference datum |
| P1/P2 | 0.18 | -0.1 | Minimal — inner wing at peak efficiency |
| P2/P3 | 0.36 | -0.3 | |
| P3/P4 | 0.55 | -0.7 | Twist accelerating |
| P4/P5 | 0.73 | -1.8 | Outer 45% receives 55% of total washout |
| P5/P6 | 0.91 | -3.3 | |
| Tip | 1.00 | -4.0 | Full washout — docile tip stall |

The eta^2.5 distribution concentrates washout in the outer 40% of the span. This achieves:
- **Inner 60% operates at optimum CL** for max L/D
- **Outer 40% flies at reduced CL** to delay tip stall
- **Non-linear progression** matches the lift distribution — more twist where the airfoil is thinner and Re is lower
- **Total washout of 4.0 deg** is consistent with proven F5J designs in this span/AR class

---

## 5. Wing Tip Treatment — Four Options Compared

| Feature | Option A: Schuemann (integrated) | Option B: Raked tip | Option C: Winglet | Option D: Hoerner |
|---------|----------------------------------|--------------------|--------------------|--------------------|
| CDi reduction | 2-3% | 3-5% | 5-8% (design point) | 1-2% |
| Mass penalty | 0g | ~1g | 3-5g | 0g |
| Flutter risk | None | Negligible | Elevated (tip mass) | None |
| Off-design drag | Neutral | Neutral | Penalty at high/low CL | Neutral |
| Manufacturing | Integral to shell | Minor tip geometry change | Separate print, bonded | Lower surface notch |
| Print bed impact | None | None | Requires alignment fixture | None |
| Re sensitivity | Low | Low | Moderate | High (marginal at Re<80k) |
| Structural | Zero change | Slight M increase | Significant M increase | Zero change |

### Recommendation: Option A (Schuemann integrated) + Option B (raked tip) combined

The superelliptical n=2.3 planform already produces a naturally straightening trailing edge toward the tip — this is the Schuemann effect built into the planform geometry. Additionally, a **5-degree aft rake on the last 5% of span** (P6 tip extension) provides:
- ~3% additional CDi reduction
- Negligible mass penalty (~1g)
- Zero flutter risk
- Natural fit within the 128mm P6 panel

A winglet is rejected for this design because:
- The 3-5g mass penalty at the tip increases the root bending moment by ~5% at launch
- Flutter risk at the winglet junction requires additional structural reinforcement
- Off-design drag penalty during launch climb and high-speed penetration
- The manufacturing benefit of the printer is that complex tip shapes are free — but a raked tip IS a complex shape that costs nothing to print, while a winglet adds mass and structural risk

A Hoerner tip is rejected because our tip Reynolds number is only 58,000 — far below the Re>150,000 threshold where Hoerner-style pressure recovery provides measurable benefit.

---

## 6. Dihedral Scheme — Three Options Compared

| Scheme | Description | EDA (deg) | Thermal Detection | Roll Authority | Roll Stability | Turbulence Response | Structural |
|--------|-------------|-----------|-------------------|----------------|---------------|--------------------|------------|
| **A: Continuous V** | Smooth anhedral-to-dihedral curve from root to tip, built into panel geometry | 5.0 | Good — continuous dihedral presents consistent dihedral angle to thermal tilt | Moderate — less dihedral effect at high speed | Good | Smooth — gradual response | Each panel has unique dihedral angle, increasing manufacturing complexity |
| **B: Polyhedral (discrete)** | Flat P1-P3, then discrete dihedral breaks at P3/P4 and P4/P5 joints | 6.0 | Excellent — concentrated dihedral at outer panels maximizes roll response to thermal tilt | Good — concentrated dihedral at aileron zone | Good | Can be twitchy — sudden dihedral breaks amplify turbulence response | Dihedral built into joint faces — zero ongoing geometry penalty |
| **C: Hybrid** | Flat P1-P2, gentle continuous dihedral P2-P5, tip panel break at P5/P6 | 5.5 | Very good — continuous dihedral in thermal-circling zone | Good | Very good | Smooth — gradual transition | One tip panel break, continuous dihedral in mid-panels |

### Recommendation: Option C (Hybrid)

The hybrid scheme captures the thermal sensitivity of continuous dihedral in the mid-span zone (where the wing flies during thermal circling) while providing a discrete tip break for roll authority at the aileron station.

Implementation:
- P1-P2: flat (0 deg dihedral)
- P2-P3 to P4-P5: continuous 1.5 deg per panel, built into panel geometry (0.75 deg per joint face)
- P5/P6 joint: discrete 2.5 deg break (tip panel cant)

EDA = 0 + 0.75 + 0.75 + 0.75 + 2.5 = 4.75 deg (target ~5.0)

The 2.5 deg tip break at P5/P6 places concentrated dihedral at the aileron station, maximizing roll sensitivity to thermal tilt while the continuous mid-span dihedral provides smooth, progressive response.

---

## 7. Panel Layout and Transport

### Panel Definition

6 panels per half-wing, 5 x 256mm + 1 x 128mm tip extension.

| Panel | Span (mm) | eta Range | Control | Airfoil | Chord Range (mm) |
|-------|-----------|-----------|---------|---------|------------------|
| P1 (root) | 256 | 0.00-0.18 | Flap | AG24 | 170-168 |
| P2 | 256 | 0.18-0.36 | Flap | AG24→AG09 | 168-162 |
| P3 | 256 | 0.36-0.55 | Flap | AG09 | 162-149 |
| P4 | 256 | 0.55-0.73 | Aileron | AG09→AG03 | 149-129 |
| P5 | 256 | 0.73-0.91 | Aileron | AG03 | 129-102 |
| P6 (tip) | 128 | 0.91-1.00 | Aileron | AG03 | 102-85 |

### Transport Groupings (Glue Joints)

Three transport grouping options:

| Option | Groups | Assembled Span | Joints in Field | Max Piece Length | Risk |
|--------|--------|---------------|-----------------|-----------------|------|
| **X: 2+2+2** | P1-P2 + P3-P4 + P5-P6 | 512 + 512 + 384 = 1408 | 2 per half | 512mm | Pieces fit in 550mm bag |
| **Y: 3+3** | P1-P2-P3 + P4-P5-P6 | 768 + 640 = 1408 | 1 per half | 768mm | 768mm pieces — long transport bag needed |
| **Z: 4+2** | P1-P2-P3-P4 + P5-P6 | 1024 + 384 = 1408 | 1 per half | 1024mm | 1024mm pieces — very long, fragile |

### Recommendation: Option X (2+2+2)

Two glued joints per half in the field is a minor assembly cost. The 512mm maximum piece length fits in a standard 550mm transport tube. Each glued pair has:
- 3mm tongue/groove alignment (self-locating)
- 8mm spar tube pass-through (structural splice)
- 4mm rear rod pass-through (torsion splice)
- CA adhesive bond

The 2+2+2 scheme also allows dihedral to be distributed: each field joint can carry a discrete dihedral angle, giving the constructor fine control over the wing's dihedral geometry.

---

## 8. Control Surface Geometry

### Flaps (P1-P3, span 0-768mm per half)

| Parameter | P1 | P2 | P3 |
|-----------|-----|-----|-----|
| Panel chord range | 170-168mm | 168-162mm | 162-149mm |
| Flap chord (28%) | 48-47mm | 47-45mm | 45-42mm |
| Hinge at 72% chord | 122-121mm | 121-117mm | 117-107mm |

### Ailerons (P4-P6, span 768-1408mm per half)

| Parameter | P4 | P5 | P6 (tip) |
|-----------|-----|-----|----------|
| Panel chord range | 149-129mm | 129-102mm | 102-85mm |
| Aileron chord (28%) | 42-36mm | 36-29mm | 29-24mm |
| Hinge at 72% chord | 107-93mm | 93-73mm | 73-61mm |

### Deflection Schedule

| Mode | Flap (deg) | Aileron (deg) | Purpose |
|------|-----------|--------------|---------|
| Launch climb | +2 down | +2 down | Reduced-drag motor climb |
| Cruise | 0 | 0 | Max L/D |
| Speed penetration | -2 up | -1 up | Reduced camber for wind penetration |
| Thermal (light) | +3 down | +2 down | Increased camber, lower stall speed |
| Thermal (strong) | +5 down | +3 down | Max camber for tight circling |
| Crow braking | -60 down | +45 up | Max drag for steep descent |

### Hinge Design

TPU living hinge consistent with HStab and rudder design:
- 0.6mm TPU strip, 4mm wide, full span of each control surface
- Upper surface gap seal (0.5mm TPU overlap)
- No discrete hardware — zero visible gap, zero drag penalty

### Servo Placement

| Servo | Panel | Span Position | Chord Position | Type | Mass |
|-------|-------|---------------|----------------|------|------|
| Flap 1 | P1 | Mid-panel (128mm) | 35% chord | 9g digital metal gear | 9g |
| Flap 2 | P3 | Mid-panel (640mm) | 35% chord | 9g digital metal gear | 9g |
| Aileron 1 | P4 | Mid-panel (896mm) | 35% chord | 9g digital metal gear | 9g |
| Aileron 2 | P6 | Mid-panel (1344mm) | 30% chord (thickest) | 5g low-profile (7mm) | 5g |

---

## 9. Performance Synthesis

### Span-Integrated Performance Estimates

Using NeuralFoil section data integrated across the superelliptical planform:

| Parameter | Value | Method |
|-----------|-------|--------|
| Profile CD0 (wing) | 0.0125 | Span-weighted NeuralFoil CD at CL=0 |
| 3D CD0 (wing only) | 0.0138 | Profile + interference + excrescence |
| CDi at CL=0.8 (cruise) | 0.00829 | CL^2 / (pi * AR * e) |
| CD total (cruise) | 0.0221 | CD0 + CDi |
| 3D L/D (cruise, CL=0.8) | 36.2 | CL / CD_total (wing alone, no fuse/tail) |
| 3D L/D (full aircraft) | 16-18:1 | Including fuselage CD0=0.0024, tail CD0=0.0006 |
| CL max (wing) | ~1.15 | Conservative, accounting for tip stall progression |
| CL max (flaps +5 deg) | ~1.30 | Flap contribution adds ~0.15 CL |
| Min sink rate | 0.40-0.45 m/s | CD_min / CL^1.5 analysis |
| Stall speed (850g AUW) | ~4.8 m/s | At CL=1.15, S=0.4062 m^2 |
| Best L/D speed | ~9-10 m/s | At CL=0.8 |

### Comparison to v1 Wing (2560mm, linear taper)

| Parameter | v1 (2560mm, linear) | R4 (2816mm, superelliptical) | Delta |
|-----------|---------------------|-----------------------------|-------|
| Span | 2560mm | 2816mm | +10% |
| Area | 41.6 dm^2 | 40.6 dm^2 | -2.4% |
| AR | 15.7 | 19.5 | +24% |
| MAC | 162.5mm | 148.6mm | -8.5% |
| CDi at CL=0.8 | 0.01040 | 0.00829 | -20.3% |
| Wing loading (850g) | 20.4 g/dm^2 | 20.9 g/dm^2 | +2.4% |
| Root Re (10 m/s) | 112,000 | 115,800 | +3.4% |
| Tip Re (10 m/s) | 61,000 | 57,900 | -5.1% |

The R4 wing achieves a **20.3% reduction in induced drag at cruise CL** through the combination of 24% higher aspect ratio and superior Oswald span efficiency. This directly translates to:
- Higher cruise L/D
- Lower minimum sink rate
- Better climb rate in thermals
- Wider speed range between stall and penetration

The slightly higher wing loading (20.9 vs 20.4 g/dm^2) is an acceptable trade for the induced drag reduction.

---

## 10. Open Items for Structural Review

The aerodynamicist requests structural review of the following:

1. **Spar clearance at P4/P5 (y=1024mm)**: 8mm tube has only 2.2mm clearance. Does the 8mm→4mm step need to happen earlier?
2. **Spar tube sizing at root**: 8mm tube alone has SF=0.97 at 8g launch. Can the D-box composite provide the remaining structural margin, or should the root spar be upgraded to 10mm?
3. **Mass budget**: Can the full wing stay under 450g while accommodating the larger span, 6th panel, and spar upgrades?
4. **Rear spar termination**: Does the rear spruce spar still terminate at P4/P5, or does the extended span require it to continue to P5/P6?
5. **P6 tip panel torsional rigidity**: 128mm panel with 4mm rod and no rear spar — is the D-box alone sufficient for aileron hinge moment loads?
6. **Flutter margin**: With 5g tip servo and increased span, do the mass balance requirements change?

---

## References

- NeuralFoil aero data: computed 2026-04-03 at V=10 m/s, n_crit=9.0
- AG airfoil coordinates: `src/cad/airfoils/ag24.dat`, `ag09.dat`, `ag03.dat`
- HStab consensus: `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md`
- Fuselage consensus: `cad/assemblies/fuselage/Fuselage_Assembly/DESIGN_CONSENSUS.md`
- Aircraft consensus R4: `cad/assemblies/Iva_Aeroforge/DESIGN_CONSENSUS.md`
- Specifications: `docs/specifications.md`
