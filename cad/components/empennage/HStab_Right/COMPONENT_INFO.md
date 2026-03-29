# Component: HStab_Right

## Type
Custom (3D printed)

## Description
Right half of the all-moving horizontal stabilizer. Mirror of HStab_Left across
the Y=0 plane. Identical airfoil blend, spar channels, and internal structure.

## Design Consensus
See `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md` (v2, 2026-03-29)

## Specifications

| Parameter | Value |
|-----------|-------|
| Half-span | 215mm (main section 200mm + 15mm swept tip) |
| Root chord | 115mm |
| Tip chord | 75mm → 60mm at swept tip |
| Root airfoil | HT-14 (7.5% t/c) |
| Tip airfoil | HT-13 (6.5% t/c) |
| Airfoil blend | Linear, 7 stations (eta 0.0–1.0) |
| Pivot rod channel | 3mm bore at 25% chord |
| Rear spar channel | 2mm bore at 65% chord |
| TE truncation | 97% chord (~0.8mm flat TE) |
| Mass | 10–12g |
| Mirror of | HStab_Left |

## Material & Print Settings

| Parameter | Value |
|-----------|-------|
| Material | LW-PLA (foamed, 230°C) |
| Wall thickness | 0.45mm |
| Print mode | Vase mode with diagonal rib grid |
| Orientation | Flat on bed (215mm x 115mm, 8.6mm Z) |
| Target density | 0.5–0.65 g/cm³ |

## Build Script
`scripts/build_hstab_right.py` (Build123d, mirrors HStab_Left, exports STEP + STL)

## Drawing
`HStab_Right_drawing.dxf` — 3-view technical drawing (mirror of Left)

## Dependencies
- HStab_Left build script: `scripts/build_hstab_left.py`
- HT-14 airfoil data: `docs/rag/airfoil_database/ht14.dat`
- HT-13 airfoil data: `docs/rag/airfoil_database/ht13.dat`

## Assembly
Part of `HStab_Assembly` (right half of all-moving horizontal stabilizer)
