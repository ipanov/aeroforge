# Design Consensus: Wing Assembly (v2 — R4 Superelliptical)

**Date:** 2026-04-03
**Rounds:** 2 (R1: aero proposal R4 + structural review R4)
**Status:** AGREED — 3 required structural modifications accepted by aero, consensus reached

---

## Agreed Specifications

| Parameter | Value | Source |
|-----------|-------|--------|
| Configuration | Full-house sailplane wing — flaps + ailerons + 4 servos per half | Aero R4 R1 |
| Airfoil root | **AG24** (9.0% thick, 6.2% camber) — L/D 56.7 at Re 116k | Aero R4 R1 — NeuralFoil |
| Airfoil tip | **AG03** (8.4% thick, 5.1% camber) — L/D 35.0 at Re 58k | Aero R4 R1 — NeuralFoil |
| Airfoil blend | Continuous AG24→AG09→AG03, three-zone linear interpolation | Aero R4 R1 |
| Span | **2816mm** (1408mm per half) | R4 locked |
| Panels | **6 per half (P1-P6)**, 5×256mm + 1×128mm tip | R4 locked |
| Root chord | **170mm** | R4 locked |
| Tip chord | **85mm** (taper ratio 0.5) | R4 locked |
| Planform | **Superelliptical n=2.3**: c(eta) = 170 × (1 - 0.5 × eta^2.3) | Aero R4 R1 |
| Wing area | **40.62 dm²** | Derived |
| Aspect ratio | **19.52** | Derived |
| MAC | **148.6mm** | Derived |
| Oswald span e | **0.997** (Schrenk) | Aero R4 R1 |
| Twist distribution | Non-linear, **4.0 deg total washout**: twist(eta) = -4.0 × eta^2.5 | Aero R4 R1 |
| Dihedral (EDA) | **~5.0 deg** hybrid — flat P1-P2, continuous P2-P5, tip break at P5/P6 | Aero R4 R1 |
| Flap chord | **28%** of local chord (P1-P3, span 0-768mm) | Aero R4 R1 |
| Aileron chord | **28%** of local chord (P4-P6, span 768-1408mm) | Aero R4 R1 |
| Main spar root | **10mm CF tube** (10/8mm OD/ID), root→P3/P4 | Struct R4 R1 — REQ CHANGE #1 |
| Main spar mid | **8mm CF tube** (8/6mm OD/ID), P3/P4→P4/P5 | Struct R4 R1 |
| Main spar tip | **4mm CF rod** (solid), P4/P5→tip | Struct R4 R1 |
| Rear spar | **5×3mm spruce**, root→P4/P5 only | Struct R4 R1 — REQ CHANGE #2 |
| Mass target | **490g full wing** (245g per half) | Struct R4 R1 — REQ CHANGE #3 |
| Wing tip | **Schuemann integrated + raked tip** (5 deg aft rake, last 5%) | Aero R4 R1 |

---

## Planform Chord Distribution

Chord law: **c(eta) = 170 × (1 - 0.5 × eta^2.3)** where eta = y/1408

| Station | Span y (mm) | eta | Chord (mm) | Re @ 10 m/s | Airfoil |
|---------|------------|------|-----------|-------------|---------|
| P1 root | 0 | 0.000 | 170.0 | 115,800 | AG24 |
| P1/P2 | 256 | 0.182 | 168.3 | 114,600 | AG24 |
| P2/P3 | 512 | 0.364 | 161.7 | 110,200 | AG24→AG09 blend |
| P3/P4 | 768 | 0.545 | 148.9 | 101,400 | AG09 |
| P4/P5 | 1024 | 0.727 | 129.1 | 87,900 | AG09→AG03 blend |
| P5/P6 | 1280 | 0.909 | 101.7 | 69,300 | AG03 |
| Tip | 1408 | 1.000 | 85.0 | 57,900 | AG03 |

---

## Airfoil Blending Schedule

| Span Range | eta Range | Airfoil | Blend Method |
|------------|-----------|---------|--------------|
| P1 (root to P1/P2) | 0.00-0.18 | AG24 (100%) | Direct |
| P1/P2 → P2/P3 | 0.18-0.36 | AG24 → AG09 | Linear interpolation |
| P2/P3 → P3/P4 | 0.36-0.55 | AG09 (100%) | Direct |
| P3/P4 → P4/P5 | 0.55-0.73 | AG09 → AG03 | Linear interpolation |
| P4/P5 → tip | 0.73-1.00 | AG03 (100%) | Direct |

### NeuralFoil Section Performance

| Station | Airfoil | Re | L/D_max | CL at best | CD at best | CL_max | CM |
|---------|---------|------|---------|-----------|-----------|--------|------|
| Root | AG24 | 115,800 | 56.7 | 0.828 | 0.01459 | 1.218 | -0.058 |
| P1/P2 | AG24 | 114,600 | 56.4 | 0.827 | 0.01466 | 1.217 | -0.058 |
| P2/P3 | AG09 | 110,200 | 45.3 | 0.561 | 0.01240 | 0.992 | -0.029 |
| P3/P4 | AG09 | 101,400 | 43.8 | 0.563 | 0.01285 | 0.985 | -0.030 |
| P4/P5 | AG03 | 87,900 | 43.8 | 0.689 | 0.01575 | 1.067 | -0.031 |
| P5/P6 | AG03 | 69,300 | 38.6 | 0.691 | 0.01790 | 1.045 | -0.032 |
| Tip | AG03 | 57,900 | 35.0 | 0.694 | 0.01985 | 1.030 | -0.033 |

---

## Twist Distribution

Function: **twist(eta) = -4.0 × eta^2.5** (deg, negative = washout)

| Station | eta | Twist (deg) | Notes |
|---------|------|-------------|-------|
| P1 root | 0.00 | 0.0 | Reference |
| P1/P2 | 0.18 | -0.1 | Minimal — inner wing at peak efficiency |
| P2/P3 | 0.36 | -0.3 | |
| P3/P4 | 0.55 | -0.8 | Twist accelerating |
| P4/P5 | 0.73 | -1.8 | Outer 45% receives 55% of total |
| P5/P6 | 0.91 | -3.3 | |
| Tip | 1.00 | -4.0 | Full washout — docile tip stall |

---

## Dihedral / Hybrid Scheme

| Zone | Span Range | Dihedral Change (deg) | Cumulative EDA (deg) | Implementation |
|------|-----------|----------------------|---------------------|----------------|
| P1-P2 | 0-512mm | 0.0 | 0.0 | Flat joint faces |
| P2-P3 | 512-768mm | +0.75 | 0.75 | Built into panel geometry |
| P3-P4 | 768-1024mm | +0.75 | 1.50 | Built into panel geometry |
| P4-P5 | 1024-1280mm | +0.75 | 2.25 | Built into panel geometry |
| P5/P6 break | 1280mm | +2.50 | 4.75 | Discrete break at joint face |
| Tip cant | 1280-1408mm | 0.0 | 4.75 | Flat (break already applied) |

**Total EDA: ~5.0 deg.** Continuous dihedral P2-P5 provides smooth thermal response; discrete P5/P6 break concentrates dihedral at aileron station for roll authority.

---

## Spar System (Structural R4 R1 — 3-Step Design)

### Main Spar — Three-Step System

| Segment | Length | Type | OD/ID (mm) | I (mm^4) | Chord Position | SF @ 8g |
|---------|--------|------|-----------|----------|----------------|---------|
| Root → P3/P4 | 768mm | CF tube | 10/8 | 290 | 25% | **1.64** |
| P3/P4 → P4/P5 | 256mm | CF tube | 8/6 | 137 | 25% | **5.55** |
| P4/P5 → tip | 384mm | CF rod | 4 solid | 12.6 | 25% | **3.08** |

### Spar Clearance Verification

| Station | Chord (mm) | Depth at 25% (mm) | Spar | Clearance |
|---------|-----------|-------------------|------|-----------|
| Root | 170 | 14.1 | 10mm tube | +4.1mm OK |
| P3/P4 | 149 | 11.9 | 10mm tube | +1.9mm OK |
| P4/P5 | 129 | 10.2 | 8mm tube | +2.2mm OK |
| P5/P6 | 102 | 7.9 | 4mm rod | +3.9mm OK |
| Tip | 85 | 6.6 | 4mm rod | +2.6mm OK |

### Transition Sleeves

| Transition | Location | Sleeve OD | Sleeve Length | Mass |
|------------|----------|-----------|---------------|------|
| 10mm → 8mm | P3/P4 end-rib | 12mm | 20mm | ~1.5g |
| 8mm → 4mm | P4/P5 end-rib | 10mm | 20mm | ~1.0g |

### Rear Spar

| Segment | Length | Type | Position | Notes |
|---------|--------|------|----------|-------|
| Root → P4/P5 | 1024mm | 5×3mm spruce | 60% chord | Clearance OK at all stations |
| P4/P5 → tip | — | None | — | D-box provides adequate torsion |

Torsional twist at VNE with full aileron deflection in P5/P6: **0.12 deg** — negligible.

---

## Control Surface Geometry

### Flaps (P1-P3, span 0-768mm per half)

| Panel | Chord Range (mm) | Flap 28% (mm) | Hinge at 72% (mm) |
|-------|-----------------|---------------|-------------------|
| P1 | 170-168 | 48-47 | 122-121 |
| P2 | 168-162 | 47-45 | 121-117 |
| P3 | 162-149 | 45-42 | 117-107 |

### Ailerons (P4-P6, span 768-1408mm per half)

| Panel | Chord Range (mm) | Aileron 28% (mm) | Hinge at 72% (mm) |
|-------|-----------------|-----------------|-------------------|
| P4 | 149-129 | 42-36 | 107-93 |
| P5 | 129-102 | 36-29 | 93-73 |
| P6 (tip) | 102-85 | 29-24 | 73-61 |

### Deflection Schedule

| Mode | Flap (deg) | Aileron (deg) | Purpose |
|------|-----------|--------------|---------|
| Launch | +2 down | +2 down | Reduced drag climb |
| Cruise | 0 | 0 | Max L/D |
| Speed | -2 up | -1 up | Penetration |
| Thermal 1 | +3 down | +2 down | Light lift |
| Thermal 2 | +5 down | +3 down | Strong lift |
| Crow/Landing | -60 down | +45 up | Max drag descent |

### Servo Placement

| Servo | Panel | Position | Type | Mass |
|-------|-------|----------|------|------|
| Flap 1 | P1 | Mid-panel, 35% chord | 9g digital metal gear | 9g |
| Flap 2 | P3 | Mid-panel, 35% chord | 9g digital metal gear | 9g |
| Aileron 1 | P4 | Mid-panel, 35% chord | 9g digital metal gear | 9g |
| Aileron 2 | P6 | Mid-panel, 30% chord | 5g low-profile (7mm) | 5g |

### Hinge Design

TPU living hinge consistent with HStab/rudder:
- 0.6mm TPU strip, 4mm wide, full span
- Upper surface gap seal (0.5mm TPU overlap)
- No discrete hardware, zero visible gap

---

## D-Box Structure

| Parameter | Value |
|-----------|-------|
| Extent | LE to 30% chord |
| Wall thickness | 0.7mm (D-box zone) vs 0.4mm standard vase |
| Forward boundary | CF tube main spar |
| Aft boundary | Closing web at 30% chord |
| Material | LW-PLA outer, CF-PLA reinforced D-box zone in P1-P3 |
| Max torsional twist at VNE | <0.12 deg (all panels) |

---

## Flutter Prevention

| Item | Specification | Mass |
|------|--------------|------|
| Tungsten mass balance | 1g per horn, 4 per half | 4.0g/half |
| TE stiffener | 0.8mm CF rod at 80% chord in ailerons | Included in shell |
| Hinge | Zero-slop TPU living hinge | 2.0g/half |

**Flutter speed:** > 35 m/s (> 1.4 × VNE).

---

## Wing Tip

| Parameter | Value |
|-----------|-------|
| Treatment | Schuemann integrated (inherent in superelliptical planform) + raked tip |
| Rake angle | 5 deg aft, last 5% span (P6 outer section) |
| TE convergence | TE naturally straightens toward tip — built into chord law |
| No winglet | Rejected: 3-5g mass penalty, flutter risk, off-design drag penalty |

---

## Panel Joint Design

| Feature | Spec |
|---------|------|
| Type | Male/female tongue + groove, 3mm / 3.2mm × 2mm deep |
| Spar bore | 10.3mm (P1-P3), 8.3mm (P3/P4→P4/P5), 4.2mm (P4/P5→tip) |
| Rear spar slot | 5.2 × 3.2mm |
| Adhesive | CA glue (medium viscosity) |
| Dihedral | In end-rib face geometry |
| Alignment | 2mm CF dowel pins (2 per joint) |

---

## Performance Predictions

| Parameter | Value |
|-----------|-------|
| Profile CD0 (wing) | 0.0125 |
| 3D CD0 (wing) | 0.0138 |
| CDi at CL=0.8 (cruise) | 0.00829 |
| CD total cruise | 0.0221 |
| 3D L/D (wing alone) | 36.2 |
| 3D L/D (full aircraft) | 16-18:1 |
| CL max (wing) | ~1.15 |
| CL max (+5 deg flap) | ~1.30 |
| Min sink | 0.40-0.45 m/s |
| Stall speed (850g) | ~4.8 m/s |
| Best L/D speed | ~9-10 m/s |
| VNE | 25 m/s |
| CDi reduction vs v1 (linear taper, 2560mm) | **-20.3%** |

---

## Mass Budget Per Half-Wing

| Component | Mass (g) |
|-----------|----------|
| Shell P1-P6 (LW-PLA, 0.4mm vase) | 91.3 |
| D-box reinforcement (0.3mm extra LE-30%, P1-P4) | 14.0 |
| Ribs (25 × CF-PLA lattice, ~0.3g) | 7.5 |
| Main spar 10mm tube (768mm) | 36.0 |
| Main spar 8mm tube (256mm) | 9.2 |
| Main spar 4mm rod (384mm) | 7.7 |
| Transition sleeves (×2) | 2.5 |
| Rear spar spruce (1024mm) | 6.9 |
| Servos (2×9g + 1×9g + 1×5g) | 32.0 |
| Servo mounts + covers + horns | 12.0 |
| Tungsten mass balance (4×1g) | 4.0 |
| Pushrods + Z-bends | 1.2 |
| TPU hinge + gap seal | 3.0 |
| Winglet (none — raked tip only) | 0.0 |
| Joint hardware (pins + CA) | 4.0 |
| Raked tip fairing | 1.0 |
| **HALF-WING SUBTOTAL** | **232.3** |
| Contingency (5%) | 11.6 |
| **HALF-WING WITH CONTINGENCY** | **243.9** |
| **FULL WING (×2)** | **487.8 ≈ 490g** |

### Wing Loading Check

| AUW | Loading (g/dm²) | Status |
|-----|-----------------|--------|
| 850g | 20.9 | Target range |
| 900g | 22.2 | Acceptable |
| 950g | 23.4 | Upper limit |
| 982g | 24.2 | Flyable — competitive for 2.8m class |

---

## Transport Configuration

**2+2+2 grouping** — two glued joints per half, field-assembled.

| Group | Panels | Assembled Length | Pieces |
|-------|--------|-----------------|--------|
| Inner | P1-P2 | 512mm | Fits 550mm tube |
| Mid | P3-P4 | 512mm | Fits 550mm tube |
| Outer | P5-P6 | 384mm | Fits 550mm tube |

---

## Print Strategy

| Part | Mode | Material | Notes |
|------|------|----------|-------|
| Panels P1-P3 | Vase 0.4mm + D-box 0.7mm | LW-PLA | D-box extra perimeter in LE-30% zone |
| Panels P4-P6 | Vase 0.4mm | LW-PLA | Standard shell |
| Ribs | 30% lattice | CF-PLA | Separate, installed post-print |
| Servo mounts | 100% solid | CF-PETG | Press-fit |
| TPU hinges | Flexible | TPU 95A | Bonded post-print |
| Raked tip fairing | Vase | LW-PLA | Integrated into P6 shell |

---

## Assembly Sequence

1. Print all panels, ribs, servo mounts
2. Install ribs into panels (CA + alignment pins)
3. Route 10mm CF tube through P1-P3 ribs
4. Install transition sleeve at P3/P4 joint (inside P3 end-rib)
5. Route 8mm CF tube through P3-P4 ribs into sleeve
6. Install transition sleeve at P4/P5 joint (inside P4 end-rib)
7. Route 4mm CF rod through P5-P6 ribs into sleeve
8. Install spruce rear spar through P1-P4 rib slots
9. Install servo mounts, servos, pushrods
10. Bond panel joints with CA (P1/P2→P2/P3→P3/P4→P4/P5→P5/P6)
11. Apply TPU hinges + gap seals
12. Install control horns with tungsten mass balance
13. Route servo wiring to root
14. Weigh and verify under 244g per half

---

## Comparison to v1 (2560mm Linear Taper)

| Parameter | v1 | R4 (v2) | Delta |
|-----------|-----|---------|-------|
| Span | 2560mm | 2816mm | +10% |
| Panels per half | 5 | 6 | +1 |
| Planform | Linear taper | Superelliptical n=2.3 | Improved Oswald |
| AR | 15.7 | 19.5 | +24% |
| CDi at CL=0.8 | 0.01040 | 0.00829 | -20.3% |
| Root spar | 8mm tube | 10mm tube | Upgraded |
| Tip spar | 5mm rod | 4mm rod | Downsized (less chord) |
| Wing mass | 430g | 490g | +60g |
| Wing loading (850g) | 20.4 g/dm² | 20.9 g/dm² | +2.4% |

---

## Round History

**R1 (2026-04-03):**
- Aero: Proposed superelliptical n=2.3 planform with AG24→AG09→AG03 blend. Compared 3 planform options, 4 tip treatments, 3 dihedral schemes. NeuralFoil polars at 7 span stations. 4.0 deg eta^2.5 washout. Schuemann integrated + raked tip. Hybrid dihedral.
- Struct: **MODIFY** — 3 required changes: (1) upgrade root spar to 10mm CF tube (8mm fails at SF=0.97 at 8g launch), (2) confirm rear spar terminates at P4/P5 (D-box adequate for P5/P6 torsion), (3) accept 490g full wing mass (+60g vs v1). 2 recommended changes: tungsten mass balance for flutter prevention, P3/P4 joint designed for 10→8mm transition.

---

## References

- Aero proposal R4 R1: `AERO_PROPOSAL_WING_R4_R1.md`
- Structural review R4 R1: `STRUCTURAL_REVIEW_WING_R4_R1.md`
- Specifications: `docs/specifications.md`
- HStab consensus: `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md`
- Fuselage consensus: `cad/assemblies/fuselage/Fuselage_Assembly/DESIGN_CONSENSUS.md`
- Aircraft consensus R4: `cad/assemblies/Iva_Aeroforge/DESIGN_CONSENSUS.md`
