# Design Consensus: Wing Assembly (v1)

**Date:** 2026-04-01
**Rounds:** 2 (R1: aero proposal + structural review; R2: aero accepts all structural modifications)
**Status:** AGREED — Option C accepted with structural modifications, aero R2 confirmed zero aerodynamic penalty

---

## Agreed Specifications

| Parameter | Value | Source |
|-----------|-------|--------|
| Configuration | **Full-house sailplane wing** — flaps + ailerons + 4 servos per half | Aero R1 |
| Airfoil root | **AG24 (8.6% thick, 6.2% camber)** | Aero R1 — NeuralFoil L/D 55.5 at Re 112k |
| Airfoil tip | **AG03 (6.4% thick, 5.1% camber)** | Aero R1 — best low-Re performance, docile stall |
| Airfoil blend | **Continuous AG24→AG03**, direct linear blend root to tip | Aero R1 |
| Span | **2560mm** (1280mm per half) | Locked spec |
| Panels | **5 per half (P1-P5), 256mm each** | Locked spec |
| Root chord | **210mm** | Locked spec |
| Tip chord | **115mm** | Locked spec |
| Taper ratio | **0.548** | Derived |
| Wing area | **41.6 dm²** (trapezoidal) | Derived |
| Aspect ratio | **15.7** | Derived |
| Twist distribution | **Non-linear, 4.0 deg total washout** — twist(η) = -4.0 × η^2.5 | Aero R1 |
| Dihedral (EDA) | **7.0 deg** — progressive polyhedral at panel joints | Aero R1 |
| Flap chord | **28%** of local chord (P1-P3, span 0-40%) | Aero R1 |
| Aileron chord | **28%** of local chord (P4-P5, span 40-100%) | Aero R1 |
| Main spar (P1-P4) | **8mm CF tube** at 25% chord, 1024mm per half | Struct R1 |
| Main spar (P5) | **5mm CF rod** at 27% chord, 256mm per half | Struct R1 — R2 aero confirmed zero penalty |
| Rear spar | **5×3mm spruce**, P1-P4 only, terminates at P4/P5 | Struct R1 |
| Mass target | **215g per half (430g full wing)** | Struct R1 |

---

## Airfoil Blending Schedule

| Station | Span (mm) | Span Fraction | AG24 % | AG03 % | Effective Thickness | Chord (mm) | Re @ 8 m/s |
|---------|-----------|--------------|--------|--------|-------------------|-----------|------------|
| P1 root | 0 | 0.00 | 100% | 0% | 8.6% | 210 | 112,000 |
| P1/P2 | 256 | 0.10 | 90% | 10% | 8.3% | 204 | 109,000 |
| P2/P3 | 512 | 0.20 | 80% | 20% | 7.9% | 198 | 106,000 |
| P3 mid | 640 | 0.30 | 70% | 30% | 7.6% | 192 | 103,000 |
| P3/P4 | 768 | 0.40 | 55% | 45% | 7.2% | 186 | 99,000 |
| P4 mid | 896 | 0.50 | 40% | 60% | 6.9% | 180 | 96,000 |
| P4/P5 | 1024 | 0.60 | 25% | 75% | 6.5% | 168 | 90,000 |
| P5 inner | 1152 | 0.70 | 15% | 85% | 6.2% | 156 | 83,000 |
| P5 mid | 1216 | 0.80 | 8% | 92% | 6.0% | 144 | 77,000 |
| P5 tip | 1280 | 1.00 | 0% | 100% | 6.4% | 115 | 61,000 |

---

## Twist Distribution

Twist function: **twist(η) = -4.0 × η^2.5** (where η = span fraction 0→1)

| Station | Span Fraction | Twist (deg) | Notes |
|---------|--------------|-------------|-------|
| P1 root | 0.00 | 0.0 | Reference |
| P1/P2 | 0.10 | -0.1 | |
| P2/P3 | 0.20 | -0.3 | |
| P3 mid | 0.30 | -0.5 | |
| P3/P4 | 0.40 | -0.8 | |
| P4 mid | 0.50 | -1.2 | Twist accelerating |
| P4/P5 | 0.60 | -1.8 | |
| P5 inner | 0.70 | -2.5 | Outer 40% gets 70% of total |
| P5 mid | 0.80 | -3.2 | |
| P5 tip | 1.00 | -4.0 | Total 4.0 deg washout |

---

## Dihedral / Polyhedral Scheme

| Joint | Dihedral Change (deg) | Cumulative EDA (deg) | Implementation |
|-------|----------------------|---------------------|----------------|
| P1/P2 | 0.0 | 0.0 | Flat joint face |
| P2/P3 | 0.0 | 0.0 | Flat joint face |
| P3/P4 | 1.5 | 1.5 | Angled end rib |
| P4/P5 | 2.5 | 4.0 | Angled end rib |
| P5 tip | 3.0 | 7.0 | Winglet cant |

**Total EDA: 7.0 deg.** Dihedral built into joint faces, NOT bent into spar.

---

## Spar System (Structural R1 + Aero R2 Confirmed)

### Main Spar — Stepped System

| Segment | Length | Type | OD | Chord Position | Wall Clearance |
|---------|--------|------|----| ------------ | -------------- |
| Root → P4/P5 | 1024mm | CF tube | 8/6mm | 25% | ≥ 2.2mm OK |
| P4/P5 joint | 30mm | Transition sleeve | 10mm OD | — | Inside P4 end-rib |
| P4/P5 → tip | 256mm | CF rod | 5mm solid | **27%** | ≥ 0.9mm at tip |

**Aero R2 confirmed:** Spar step has 0.0% L/D impact — fully internal, external profile unchanged. Sleeve positioned inside P4 end-rib avoids any skin bulge.

**Spar offset in P5 (25% → 27%):** Moves closer to max thickness (30% chord), gaining ~0.5mm clearance. Zero aero penalty — external geometry unchanged. Actually improves D-box enclosed area.

### Rear Spar

| Segment | Length | Type | Position | Notes |
|---------|--------|------|----------|-------|
| Root → P4/P5 | 1024mm | 5×3mm spruce | 60% chord | Clearance ≥ 0.5mm at P4/P5 |
| P4/P5 → tip | — | **None** | — | D-box provides torsion alone |

**Aero R2 confirmed:** P5 torsional twist at VNE with full aileron deflection = only 0.52 deg — negligible. D-box alone adequate for 256mm tip panel.

### Spar Fit Verification

| Station | Chord | Depth (mm) | Spar | Clearance |
|---------|-------|-----------|------|-----------|
| P1 root | 210 | ~15.0 | 8mm tube | 3.5mm |
| P3/P4 | 186 | ~12.4 | 8mm tube | 2.2mm |
| P4/P5 | 168 | ~9.3 | 8mm tube | 0.65mm |
| P5 inner | 156 | ~8.2 | 5mm rod | 1.6mm |
| P5 tip | 115 | ~6.3 | 5mm rod | 0.65mm (marginal at 27%) |

---

## Control Surface Geometry

### Flaps (P1-P3, span 0-512mm per half)

| Parameter | P1 | P2 | P3 |
|-----------|-----|-----|-----|
| Panel chord (mm) | 210-204 | 204-192 | 192-180 |
| Flap chord 28% (mm) | 59-57 | 57-54 | 54-50 |
| Hinge at 72% chord | 151-147mm | 147-138mm | 138-130mm |

### Ailerons (P4-P5, span 512-1280mm per half)

| Parameter | P4 | P5 inner | P5 tip |
|-----------|-----|----------|--------|
| Panel chord (mm) | 180-168 | 168-144 | 144-115 |
| Aileron chord 28% (mm) | 50-47 | 47-40 | 40-32 |
| Hinge at 72% chord | 130-121mm | 121-104mm | 104-83mm |

### Deflection Schedule

| Mode | Flap (deg) | Aileron (deg) | Purpose |
|------|-----------|--------------|---------|
| Launch | +2 down | +2 down | Reduced drag climb |
| Cruise | 0 | 0 | Normal flight |
| Speed | -2 up | -1 up | Penetration |
| Thermal 1 | +3 down | +2 down | Light lift |
| Thermal 2 | +5 down | +3 down | Strong lift |
| Crow/Landing | -60 down | +45 up | Max drag descent |

### Hinge Design

TPU living hinge — consistent with HStab:
- 0.6mm TPU strip, 4mm wide, full span
- Upper surface gap seal (0.5mm TPU overlap)
- No discrete hardware, zero visible gap

### Servo Placement

| Servo | Panel | Position | Type |
|-------|-------|----------|------|
| Flap 1 | P1 | Mid-panel, 35% chord | 9g digital metal gear |
| Flap 2 | P3 | Mid-panel, 35% chord | 9g digital metal gear |
| Aileron 1 | P4 | Mid-panel, 35% chord | 9g digital metal gear |
| Aileron 2 | P5 | Mid-panel, 30% chord (thickest) | **5g low-profile** (7mm height) |

**P5 servo:** KST X08 or PTK 7308MG-D equivalent, 7mm height. External fairing blister +0.5mm may be needed.

---

## D-Box Structure

| Parameter | Value |
|-----------|-------|
| Extent | LE to 30% chord |
| Wall thickness | 0.7mm (D-box zone) vs 0.55mm standard vase |
| Forward boundary | CF tube main spar |
| Aft boundary | Closing web at 30% chord |
| GJ (root) | 3.92 N·m² |
| GJ (P4/P5) | 0.88 N·m² |

---

## Flutter Prevention (REQUIRED)

| Item | Specification | Mass |
|------|--------------|------|
| Tungsten mass balance | 1g per horn, 4 per half | 4.0g/half |
| TE stiffener | 1mm CF rod at 80% chord in ailerons | Included |
| Hinge | Zero-slop TPU living hinge | 2.0g/half |

**Flutter speed:** > 35 m/s (> 1.4 × VNE). **Divergence speed:** ~90 m/s (3.6 × VNE).

---

## Winglet (Preliminary)

| Parameter | Value |
|-----------|-------|
| Height | 80mm (~6% semi-span) |
| Root chord | 55mm |
| Tip chord | 25mm |
| Cant | 75 deg from horizontal |
| Toe | 2 deg toe-out |
| Airfoil | NACA 0006 |
| LE sweep | 30 deg |
| Mass | ~3g |

---

## Panel Joint Design

| Feature | Spec |
|---------|------|
| Type | Male/female tongue+groove |
| Tongue | 3mm, groove 3.2mm, 2mm deep |
| Spar hole | 8.3mm (P1-P4), 5.2mm (P5) |
| Adhesive | CA glue |
| Dihedral | In end-rib face geometry |
| Alignment | 2mm dowel pins |

---

## Performance Predictions

| Parameter | Value |
|-----------|-------|
| Profile L/D (root, Re 112k) | 55.5 |
| Profile L/D (tip, Re 61k) | 35.9 |
| 3D wing L/D (realistic) | 16-18:1 |
| CLmax (wing) | ~1.15 |
| CLmax (+5 deg flap) | ~1.3 |
| Min sink | 0.40-0.45 m/s |
| Stall speed (800g) | ~4.9 m/s |
| Best L/D speed | ~9-10 m/s |
| VNE | 25 m/s |
| Combined L/D impact of all structural mods | < 0.1% |

---

## Mass Budget Per Half-Wing

| Component | Mass (g) |
|-----------|---------|
| P1-P5 shells (LW-PLA vase) | 86 |
| D-box reinforcement | 15.6 |
| Ribs (CF-PLA lattice, 25x) | 5.3 |
| Flap servos x2 (9g) | 18 |
| Aileron servo P4 (9g) | 9 |
| Aileron servo P5 (5g) | 5 |
| Servo mounts + covers + horns | 12.0 |
| Tungsten mass balance (4x 1g) | 4.0 |
| Pushrods + Z-bends | 1.2 |
| TPU hinge + gap seal | 3.0 |
| Main spar 8mm tube (1024mm) | 28.6 |
| Main spar 5mm rod (256mm) | 3.8 |
| Transition sleeve | 2.0 |
| Rear spar spruce (1024mm) | 6.1 |
| Winglet | 3.0 |
| Joint hardware (pins + CA) | 4.0 |
| **HALF-WING TOTAL** | **204.8** |
| **Contingency (5%)** | **10.2** |
| **HALF-WING WITH CONTINGENCY** | **215.0** |
| **FULL WING (×2)** | **430.0** |

### Wing Loading Check

| AUW | Loading | Status |
|-----|---------|--------|
| 750g | 18.0 g/dm² | At target |
| 800g | 19.2 g/dm² | Acceptable |
| 850g | 20.4 g/dm² | Upper limit |

---

## Print Strategy

| Part | Mode | Material | Notes |
|------|------|----------|-------|
| Panels P1-P5 | Vase 0.50-0.55mm | LW-PLA | D-box gets extra perimeters |
| Ribs | 30% lattice | CF-PLA | Separate, installed post-print |
| Winglet | Vase mode | LW-PLA | Integrated into P5 tip |
| Servo mounts | 100% solid | CF-PETG | Press-fit |
| TPU hinges | Flexible | TPU 95A | Bonded post-print |

Print time: ~10h per half (sequential), ~5h with two printers.

---

## Assembly Sequence

1. Print all panels, ribs, servo mounts, winglet
2. Install ribs into panels (CA + alignment pins)
3. Route 8mm CF tube through P1-P4 ribs
4. Install transition sleeve at P4/P5 joint (inside P4 end-rib)
5. Route 5mm CF rod through P5 ribs into sleeve
6. Install spruce rear spar through P1-P4 rib slots
7. Install servo mounts, servos, pushrods
8. Bond panel joints with CA (P1/P2 → P2/P3 → P3/P4 → P4/P5)
9. Install winglet
10. Apply TPU hinges + gap seals
11. Install control horns with tungsten mass balance
12. Route servo wiring to root
13. Weigh and verify under 260g per half

---

## Round History

**Round 1:**
- Aero: Option C proposed (AG24-AG03 optimized twist, 3 options compared). L/D 55.5 root, 35.9 tip, non-linear 4° washout, 7° EDA, 28% controls.
- Struct: **MODIFY** — 4 required changes: (1) stepped spar at P4/P5 (8mm tube doesn't fit in thin tip), (2) rear spar terminates at P4/P5, (3) P5 servo downgraded to 5g low-profile, (4) mass balance locked as structural requirement.

**Round 2:**
- Aero: **ACCEPT ALL** — Quantitative analysis confirms < 0.1% total L/D impact from all modifications. Spar step is fully internal (0% aero penalty). Spar offset at 27% actually improves D-box area. Rear spar termination causes only 0.52° twist at VNE. Consensus reached.

---

## References

- Aero proposal R1: `AERO_PROPOSAL_WING_R1.md`
- Aero response R2: `AERO_RESPONSE_WING_R2.md`
- Structural review R1: `STRUCTURAL_REVIEW_WING_R1.md`
- Specifications: `docs/specifications.md`
- HStab consensus: `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md`
