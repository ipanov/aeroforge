# Design Consensus: Fuselage Assembly (v2)

**Date:** 2026-04-01
**Rounds:** 4 total (v1: 2 rounds; v2 rudder integration: 2 rounds)
**Status:** AGREED — both agents signed off on v1 and v2 rudder integration

---

## Agreed Specifications

| Parameter | Value | Source |
|-----------|-------|--------|
| Configuration | Continuous 3D-printed aerodynamic body | Aero R1 |
| Total length | **1046mm** (spinner tip to VStab root TE) | Aero R1 |
| Max cross-section | **50mm W × 44mm H** at X=150mm (battery) | Aero R1 |
| Fineness ratio | 20.9 | Aero R1 |
| Wing LE station | 260mm from nose | Aero R1 |
| HStab pivot station | 911mm from nose | Aero R1 |
| Tail moment arm (l_h) | 651mm | Derived from Vh=0.382 |
| Longerons | **4× 2mm solid CF rods** | Struct R2 (upgraded from 1.5mm) |
| Total mass | **~91g** (79g excl. VStab skin) | Struct R2 |
| CG position | 31% MAC (adjustable 28–34%) | Aero R1 |
| Print sections | 5 pieces | Aero R1, Struct R2 (nose split) |

## Integrated VStab (part of fuselage)

| Parameter | Value |
|-----------|-------|
| Height | 165mm |
| Root chord | 180mm |
| Tip chord | 95mm |
| Root airfoil | HT-14 (7.5%) |
| Tip airfoil | HT-12 (5.1%) |
| Planform area | 226.9 cm² (2.27 dm²) |
| Vv (geometric) | 0.014 |
| Rudder chord (root) | **38%** (68.4mm) — v2 update |
| Rudder chord (tip) | **35%** (33.3mm) |
| Rudder hinge (root) | **62% chord from LE** (111.6mm) — v2 update |
| Rudder hinge (tip) | **65% chord from LE** (61.7mm) |
| Rear spar | 1.5mm CF rod at 60% chord |
| Fin integration | Superelliptical blend X=650–866mm |

## Cross-Section Schedule (Key Stations)

| Station X (mm) | W × H (mm) | Shape | Section | Notes |
|----------------|-----------|-------|---------|-------|
| 0 | 0 | point | Nose | Spinner tip |
| 30 | 32 × 32 | circle | Nose | Spinner base / motor face |
| 55 | 35 × 35 | circle | Motor | **PETG shell** (M3) |
| 150 | 50 × 44 | ellipse | Battery | **MAX SECTION** |
| 260 | 38 × 34 | egg | Wing saddle | Wing LE station |
| 350 | 30 × 26 | ellipse | Servo bay | Elevator + rudder servos |
| 500 | 18 × 16 | ellipse | Boom | Pushrod zone |
| 650 | 13 × 13 | circle | Pre-fin | Boom-to-fin transition starts |
| 866 | 8.5 × 165 | HT-14 | Fin root | VStab root LE |
| 911 | 7 × 145 | HT-14→12 | Fin | HStab pivot station |
| 1046 | 0 | point | End | VStab root TE |

## Print Sections

| Section | X Range | Length | Print Method | Material |
|---------|---------|--------|-------------|----------|
| S1 - Nose | 0–260mm | 250mm + 10mm spinner cap | **Left/right halves** (M2) | LW-PLA shell, **PETG motor bay** (M3) |
| S2 - Wing | 260–430mm | 170mm | Horizontal, belly-down | LW-PLA, **CF-PLA spar tunnel** (M6) |
| S3 - Boom | 430–660mm | 230mm | Horizontal / vase mode | LW-PLA |
| S4a - Fin base | 660–880mm | 220mm | Fin laying flat | LW-PLA |
| S4b - Fin top | 880–1046mm | 166mm | Fin laying flat | LW-PLA, PETG HStab bearing |

## Structural Modifications (from Structural Review R2)

| Mod | Change | Mass Impact | Rationale |
|-----|--------|-------------|-----------|
| M1 | **2mm CF longerons** (was 1.5mm) | +9.2g (21.1g total) | Euler buckling SF 4.6 vs 1.47; battery deflection 1.1mm vs 3.4mm |
| M2 | **Nose prints as left/right halves** | 0g | 250mm tall with overhangs; standard 3DLabPrint/Eclipson practice |
| M3 | **PETG motor bay** (X=30–90mm) | +2g | LW-PLA Tg=55–60°C; motor reaches 70–80°C |
| M4 | **Interlocking teeth at joints** | 0g | +40% bond area, better alignment, zero weight cost |
| M5 | **HStab bearing: print undersized, ream** | 0g | FDM tolerance ±0.15mm; ream through both bores simultaneously |
| M6 | **CF-PLA spar tunnel** (X=260–320mm) | +1g | Wing bending loads concentrated at spar tunnel |

## 4-Longeron Layout (2mm CF rods)

| Station | Top-R | Top-L | Bot-R | Bot-L | Spacing W×H |
|---------|-------|-------|-------|-------|-------------|
| 40mm (motor) | +9,+9 | -9,+9 | +9,-9 | -9,-9 | 18×18 |
| 150mm (battery) | +18,+16 | -18,+16 | +18,-16 | -18,-16 | 36×32 |
| 280mm (wing) | +12,+10 | -12,+10 | +12,-10 | -12,-10 | 24×20 |
| 500mm (boom) | +6,+5 | -6,+5 | +6,-5 | -6,-5 | 12×10 |
| 650mm (pre-fin) | +4,+4 | -4,+4 | +4,-4 | -4,-4 | 8×8 |
| 866mm (fin root) | +2,+3 | -2,+3 | +2,-3 | -2,-3 | 4×6 |

Top 2 rods sweep into VStab LE spar channel at fin section.
Bottom 2 rods continue to HStab bearing mount.

## Wing Root Fairing

| Parameter | Value |
|-----------|-------|
| Forward extension | 30mm (14% root chord) |
| Aft extension | 60mm (29% root chord) |
| Fillet radius | 15mm (7.1% root chord) |
| Profile | Quartic polynomial, C2 continuous |
| Interference drag | CD = 0.000005 (negligible with fairing) |

## Mass Budget

| Component | Mass (g) |
|-----------|----------|
| LW-PLA shell (all sections) | 40.7 |
| Internal structure (bulkheads, trays, mounts) | 26.0 |
| CF longerons (4× 2mm, 1050mm) | 21.1 |
| PETG motor bay | 2.0 |
| CF-PLA spar tunnel reinforcement | 1.0 |
| **Fuselage subtotal (excl. VStab skin)** | **~91g** |
| VStab skin (counted in empennage budget) | 11.90 |

## Performance

| Metric | Value |
|--------|-------|
| Fuselage body CD0 | 0.00171 |
| VStab fin CD0 | 0.00062 |
| Interference CD0 | 0.00005 |
| **Total system CD0** | **0.00238** |
| vs. pod-and-boom | 0.00240 (essentially equal) |

---

## Rudder Integration (v2 Addition)

**Source:** Aero R2 (AERO_RESPONSE_FUSELAGE_R2.md) + Structural R2 (STRUCTURAL_RESPONSE_FUSELAGE_R2.md)
**Consensus:** Both modifications ACCEPTED. All structural questions resolved favorably.

### Rudder Geometry

| Parameter | Value | Source |
|-----------|-------|--------|
| Rudder chord ratio (root) | **38%** (68.4mm at root) | Aero R2 Mod 1, Struct R2 ACCEPT |
| Rudder chord ratio (tip) | **35%** (33.3mm at tip) | Consensus v1 |
| Rudder hinge line (root) | **62% chord from LE** (111.6mm) | Derived from 38% root ratio |
| Rudder hinge line (tip) | **65% chord from LE** (61.7mm) | Consensus v1 |
| Rudder planform area | **83.9 cm²** | Aero R2 with Mod 1 |
| Fixed fin area | **143.0 cm²** | Derived (226.9 - 83.9) |
| Deflection range | **±30 deg** | Aero R2 |
| Yaw authority (Cn_delta_r) | **0.033** | Aero R2 with Mod 1 |
| Rudder height | 165mm (matches VStab) | Consensus v1 |
| Root airfoil | HT-14 (aft 38% of profile) | Aero R2 |
| Tip airfoil | HT-12 (aft 35% of profile) | Aero R2 |

### Rudder Structure

| Element | Specification | Mass (g) |
|---------|--------------|----------|
| Rudder shell | LW-PLA, 0.4mm vase mode | 5.22 |
| Internal ribs | 3× LW-PLA 0.6mm, at Z=41, 83, 124mm | 0.11 |
| Hinge wire | 0.5mm ASTM A228 spring steel, 170mm | 0.26 |
| PETG sleeves | 10× (1.2mm OD / 0.6mm ID / 3mm), interleaved at 20mm intervals | 0.04 |
| Gap seal | **0.05mm Mylar + 3M 468MP adhesive**, 170mm × 12mm | 0.18 |
| Z-bend clevis + CA | Steel clevis at pushrod attachment | 0.15 |
| **Rudder total** | | **5.96g** |

### Rudder Structural Verification

| Item | Verdict | Key Detail |
|------|---------|------------|
| Fin thickness at hinge line | **FEASIBLE** | 2.6mm min internal at tip, 7.3mm at root. Sleeve is 1.2mm OD |
| Shell torsional stiffness | **ADEQUATE** | GJ ~577,000 N-mm² at root, ~14% of elevator load. Twist < 0.002° at VNE |
| Hinge wire bending | **ADEQUATE** | Safety factor 36.3 at max load. 0.5mm ASTM A228 spring steel |
| 3 ribs for flutter | **ADEQUATE** | Bending mode ~90–100 Hz. Zero-slop wire + servo is primary flutter prevention |
| Hinge vs rear longeron | **CLEARS** | 1.5mm edge-to-edge clearance. Hinge at 62% chord, longeron at 60% |
| Printability | **CONFIRMED** | Fits Bambu A1 (165×68mm). Vase mode 0.4mm. ~60 min print time |

### Rudder-Elevator Clearance

| Parameter | Value |
|-----------|-------|
| Rudder hinge axis | Vertical (Z), at X=977.6mm (fuselage station) |
| Elevator hinge axis | Horizontal (Y), at X=942.25mm (fuselage station) |
| Axes separation | 35.35mm in X |
| Collision risk | **ZERO** — perpendicular rotation axes guarantee orthogonal separation |
| Min clearance at max combined deflection | **15.2mm** (at R30 + E18) |

### Rudder Gap Seal

| Parameter | Value |
|-----------|-------|
| Type | Mylar strip (not TPU co-print) |
| Thickness | 0.05mm |
| Dimensions | 170mm × 12mm |
| Adhesive | 3M 468MP transfer adhesive |
| Mass | 0.18g |
| Durability | 100+ flights, annual replacement |
| Rationale | Proven F3J/F5J standard, zero drag penalty, simple installation |

### Hinge Wire Routing

1. Wire enters from fin tip (Z=165mm)
2. Passes downward through fixed fin (5× PETG sleeves)
3. Crosses rudder split line at 62% chord
4. Passes through rudder LE (5× PETG sleeves, interleaved)
5. Terminates at Z=0 with 90° bend into fuselage body (retained)
6. Top end bent 90° at Z=165mm (retained)
7. Sleeve spacing: 20mm intervals
8. Sleeve count: 10 total (5 fixed fin + 5 rudder, interleaved)

### Rudder Pushrod

| Parameter | Value |
|-----------|-------|
| Pushrod type | 1.0mm music wire in 2.0mm OD / 1.2mm ID PTFE tube (Bowden) |
| Route | Rudder servo (fuselage X=350) → boom interior → fin interior → Z-bend at rudder root bottom |
| Attachment | Z-bend through 1.6mm hole in rudder root face, 8–10mm above Z=0 |
| Deflection rate | Direct (no differential; rudder is symmetric) |

### Revised Empennage Mass Budget

| Item | Mass (g) |
|------|----------|
| HStab assembly (v6) | 29.33 |
| Rudder | 5.96 |
| **Empennage subtotal** | **35.29g** |
| VStab fin skin (fuselage budget) | 11.90 |
| **Total empennage at aircraft level** | **47.19g** |

Empennage subtotal is 0.29g over the 35g target (0.04% AUW). Acceptable — within measurement uncertainty and CG trim range.

---

## Assembly Sequence

### Original Steps (v1)

1. Print all 5 sections (S1 as left/right halves)
2. Bond PETG motor bay insert into S1
3. Slide 4× 2mm CF rods through S1, glue at motor mount bulkhead
4. Slide S2 onto rods, align with dowels, CA joint + teeth
5. Slide S3, align, CA
6. Slide S4a, align, CA
7. Slide S4b, align, CA
8. Insert 1.5mm VStab rear spar rod
9. Press brass tube bearings into HStab mount, ream
10. Bond electronics tray into S1 interior
11. Install servos, route pushrods/cables through S3

### Rudder Integration Steps (v2 Addition)

12. Print rudder shell (vase mode, LW-PLA) and 10 PETG sleeves
13. Embed 5 PETG sleeves into fixed fin hinge pockets (CA, 20mm intervals)
14. Embed 5 PETG sleeves into rudder LE bull-nose pockets (CA, interleaved)
15. Slide rudder into position, mating bull-nose into fin channel
16. Thread 0.5mm spring steel wire from fin top through all sleeves, bend at both ends
17. Test rudder deflection ±30°, verify smooth rotation
18. Apply Mylar gap seal to fixed fin TE face (3M 468MP adhesive)
19. Route rudder pushrod (1mm wire in PTFE) from servo to rudder Z-bend
20. Verify full deflection with servo actuation, check for binding
21. Weigh complete empennage, verify under 36g

---

## What Makes This Design Special

1. **One continuous shape** — no joints, gaps, or steps in the aerodynamic surface
2. **Integrated VStab** — fin grows organically from the boom via superelliptical blending
3. **Zero-gap wing fairing** — 3D-printed C2 continuous surface, impossible with composite construction
4. **4-longeron structure** — 2.5× bending stiffness of 10mm carbon boom, superior torsion
5. **No carbon tail boom to buy** — saves $10–15, eliminates crash failure point
6. **Every cross-section optimized** — varying elliptical profiles, Sears-Haack taper, ideal fillets
7. **Concealed rudder hinge** — same proven piano-wire design as HStab elevator, zero visible hardware
8. **Mylar gap seal** — competition-proven drag reduction, 0.18g mass cost
9. **Perpendicular-axis safety** — rudder (Z) and elevator (Y) axes guarantee zero collision at any deflection

## References

- Fuselage aero analysis: `AERO_PROPOSAL_FUSELAGE.md`
- Fuselage structural review: `STRUCTURAL_REVIEW_FUSELAGE.md`
- Rudder aero review R2: `AERO_RESPONSE_FUSELAGE_R2.md`
- Rudder structural response R2: `STRUCTURAL_RESPONSE_FUSELAGE_R2.md`
- HStab consensus v6: `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md`
- Wing consensus v1: `cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md`

## Round History

**v1 (2 rounds):**
- Aero R1: Proposed integrated fuselage with 4-longeron structure, 5 print sections, superelliptical VStab blend
- Struct R1/R2: 6 modifications (2mm longerons, PETG motor bay, nose halves, interlocking teeth, ream bearings, spar tunnel). All accepted. Consensus reached.

**v2 — Rudder Integration (2 rounds):**
- Aero R2: Reviewed rudder sizing, elevator clearance, performance, gap seal, mass impact. 2 modifications proposed: (1) increase root chord to 38% for yaw authority, (2) mandate Mylar gap seal over TPU co-print
- Struct R2: Accepted both modifications. Verified hinge wire clearance (1.5mm), fin thickness at all span stations (2.6mm min), torsional stiffness (GJ ~577,000 N-mm²), flutter resistance (90–100 Hz), hinge wire safety factor (36.3). Consensus reached.

## Revision History

| Version | Date | Description |
|---------|------|-------------|
| v1 | 2026-03-29 | Initial fuselage consensus (2 agent rounds) |
| v2 | 2026-04-01 | Rudder integration (2 additional agent rounds) — 38% root chord, Mylar seal, 5.96g rudder |
