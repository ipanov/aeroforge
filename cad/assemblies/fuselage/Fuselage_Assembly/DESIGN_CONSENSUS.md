# Design Consensus: Fuselage Assembly (v1)

**Date:** 2026-03-29
**Rounds:** 2 (R1: aero proposal → R2: structural review + modifications)
**Status:** AGREED — both agents signed off on v1

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
| Rudder chord | 35% (63mm root, 33mm tip) |
| Rudder hinge | 65% chord from LE |
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
| VStab skin (counted in empennage budget) | ~12g |

## Performance

| Metric | Value |
|--------|-------|
| Fuselage body CD0 | 0.00171 |
| VStab fin CD0 | 0.00062 |
| Interference CD0 | 0.00005 |
| **Total system CD0** | **0.00238** |
| vs. pod-and-boom | 0.00240 (essentially equal) |

## Assembly Sequence

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

## What Makes This Design Special

1. **One continuous shape** — no joints, gaps, or steps in the aerodynamic surface
2. **Integrated VStab** — fin grows organically from the boom via superelliptical blending
3. **Zero-gap wing fairing** — 3D-printed C2 continuous surface, impossible with composite construction
4. **4-longeron structure** — 2.5× bending stiffness of 10mm carbon boom, superior torsion
5. **No carbon tail boom to buy** — saves $10-15, eliminates crash failure point
6. **Every cross-section optimized** — varying elliptical profiles, Sears-Haack taper, ideal fillets

## References

- Full aero analysis: `AERO_PROPOSAL_FUSELAGE.md`
- Structural review: `STRUCTURAL_REVIEW_FUSELAGE.md`
