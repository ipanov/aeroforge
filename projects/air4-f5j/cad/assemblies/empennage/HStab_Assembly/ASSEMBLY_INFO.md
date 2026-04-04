# Assembly: HStab_Assembly

## Description

Complete horizontal stabilizer assembly comprising all empennage aerodynamic surfaces and structural elements. The assembly uses a symmetric planform with superellipse taper (n=2.3), blended HT-13/HT-12 airfoils, and a fully concealed saddle hinge system. Each printed component is identical on both sides — print one HStab, one Elevator, and one Tip Cap, then mirror for the opposite side.

## Components

| # | Component | Qty | Material | Mass (each) | Role |
|---|-----------|-----|----------|-------------|------|
| 1 | HStab (print 2, mirror one) | 2 | LW-PLA | 6.89 g | Fixed stabilizer half-shell |
| 2 | Elevator (print 2, mirror one) | 2 | LW-PLA | 2.72 g | Movable control surface |
| 3 | HStab_Tip_Cap | 2 | LW-PLA | 0.34 g | Tip closure and fairing |
| 4 | HStab_Main_Spar | 1 | 8mm carbon tube | 4.20 g | Primary structural member |
| 5 | Hinge_Wire | 1 | 0.5mm spring steel | 0.65 g | Concealed piano-wire hinge |
| 6 | PETG_Sleeves | ~48 | PETG | 0.10 g total | Hinge bearing surfaces |

## Mass Budget

| Item | Mass |
|------|------|
| 2x HStab shell | 13.78 g |
| 2x Elevator | 5.44 g |
| 2x Tip Cap | 0.68 g |
| Main spar | 4.20 g |
| Hinge wire | 0.65 g |
| PETG sleeves | 0.10 g |
| Adhesive (est.) | 0.50 g |
| **Total** | **25.35 g** |
| **Target** | **29.3 g** |
| **Margin** | **3.95 g (13.5%)** |

## Specifications

| Parameter | Value |
|-----------|-------|
| Full span | 430 mm (215 mm per half) |
| Root chord | 115 mm |
| Tip chord (95% span) | ~50 mm |
| Mean chord | 94.8 mm |
| Area | 394.8 cm2 |
| Aspect ratio | 4.53 |
| Root airfoil | HT-13 (6.5% t/c) |
| Tip airfoil | HT-12 (5.1% t/c) |
| Planform | Superellipse n=2.3 |
| Elevator chord ratio | ~45% at root |
| Hinge line | X=60.0 mm (concealed saddle) |
| Main spar | X=34.5 mm (single 8mm CF tube) |
| Vh (tail volume) | 0.393 |

## Symmetry

The H-Stab is fully symmetric about Y=0. The airfoil profiles (HT-13, HT-12) are symmetric. All printed components are identical on both halves — the Right side is the Left side mirrored. Only three unique printed parts exist:
- **HStab** (print 2, flip one)
- **Elevator** (print 2, flip one)
- **HStab_Tip_Cap** (print 2, flip one)

## Internal Structure

All printed shells feature internal geodesic lattice ribs at +/-45 degrees, generated during mesh tessellation. The lattice provides:
- Torsional stiffness without solid infill
- Load distribution between spar bore and hinge saddle
- Resistance to panel flutter at high speed

The ribs are thin walls (single-extrusion) spaced at 12mm intervals, following the airfoil inner surface at each span station.

## Assembly Sequence

1. Print 2x HStab, 2x Elevator, 2x Tip Cap (all in LW-PLA vase mode)
2. Thread PETG sleeves onto hinge wire (alternating stab-fixed / elevator-fixed)
3. Insert hinge wire through stab hinge bores
4. Mate elevator bull-nose into stab saddle groove
5. Slide 8mm carbon spar through both stab halves
6. Bond root faces together (CA or epoxy at centerline joint)
7. Press-fit tip caps onto stab tips

## Design Consensus

See `DESIGN_CONSENSUS.md` in this folder for the full aerodynamic and structural rationale (4 rounds of aero/structural agent review).
