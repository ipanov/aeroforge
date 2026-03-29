# Assembly: HStab_Assembly

## Type
Assembly (all-moving horizontal stabilizer)

## Description
Complete all-moving horizontal stabilizer for the AeroForge sailplane. The entire
surface pivots as a unit — no separate elevator. Two printed halves joined by a
3mm carbon fiber pivot rod, with 2mm rear spar rods for torsional stiffness.

Span-varying airfoil blend from HT-14 (root) to HT-13 (tip) provides optimized
aerodynamic performance at every station — a 3D printing differentiator impossible
with conventional construction.

## Design Consensus
`DESIGN_CONSENSUS.md` (v2, 2026-03-29) — 3 rounds, both agents signed off.

## Specifications

| Parameter | Value |
|-----------|-------|
| Configuration | All-moving (entire surface pivots) |
| Total span | 430mm (215mm per half) |
| Root chord | 115mm |
| Tip chord | 75mm → 60mm at swept tip |
| Root airfoil | HT-14 (7.5% t/c) |
| Tip airfoil | HT-13 (6.5% t/c) |
| Airfoil blend | Linear, 7 stations per half |
| Area | ~408 cm² (4.08 dm²) |
| Aspect ratio | 4.53 |
| Taper ratio | 0.652 |
| Vh | 0.382 |
| S_h/S_w | 9.8% |
| Pivot axis | 3mm CF rod at 25% MAC |
| Rear spar | 2mm CF rod at 65% chord |
| Deflection | -20° (down) to +12° (up) |
| Mass target | 25g nominal (22–28g range) |

## Bill of Materials

| # | Component | Type | Material | Mass (g) | Qty |
|---|-----------|------|----------|----------|-----|
| 1 | HStab_Left | Custom (printed) | LW-PLA | 10–12 | 1 |
| 2 | HStab_Right | Custom (printed) | LW-PLA | 10–12 | 1 |
| 3 | HStab_Joiner_Rod | Off-shelf | 3mm CF rod | 1.4 | 1 |
| 4 | Rear_Spar_Left | Off-shelf | 2mm CF rod | 0.5 | 1 |
| 5 | Rear_Spar_Right | Off-shelf | 2mm CF rod | 0.5 | 1 |
| 6 | Control_Horn | Custom/wire | PETG or 0.8mm music wire | 0.5 | 1 |
| | **Total** | | | **23–27** | |

## Assembly Sequence

1. Insert 2mm rear spar rods into left and right halves (CA glue into channels)
2. Slide 3mm pivot rod through both halves (root-to-root)
3. Attach control horn at 80% chord on bottom surface
4. Slide assembly into tail mount bearings (PETG socket with brass tube inserts)
5. Retain with E-clips or CA'd collars at bearing points
6. Connect 0.8mm music wire pushrod to control horn ball-link

## Pivot Bearing Detail

- PETG tail mount socket with brass tube inserts (4mm OD / 3mm ID, 8mm long)
- Two bearing points spaced 25–30mm
- 3mm CF rod slides through brass tubes
- Low friction, no play

## Print Strategy

- Each half printed flat on Bambu bed (215mm x 115mm footprint, 8.6mm Z height)
- Vase mode with diagonal rib grid (Tom Stanton method)
- LW-PLA at 230°C, target density 0.5–0.65 g/cm³
- 0.45mm single wall
- TE bonded with thin CA after printing
- Tip closed with PLA cap or folded wall

## Performance

| Station | Re | CL at 2° | L/D at 4° | Mission L/D |
|---------|-----|----------|-----------|-------------|
| Root (HT-14) | 61,300 | 0.253 | 21.1 | 16.3 |
| Mid (blend) | 50,700 | ~0.245 | ~20.0 | ~15.5 |
| Tip (HT-13) | 40,000 | 0.220 | 17.0 | 12.8 |

## Servo & Linkage

- 9g servo, fuselage-mounted (NOT at pivot — CG penalty unacceptable)
- 0.8mm music wire pushrod, ~250mm, ball-link at horn end
- Horn: PETG, bolted through rear spar at 80% chord

## Drawings
- Assembly: `HStab_Assembly_drawing.dxf` (3-view with all components)
- Component drawings in respective component folders

## What Makes This Special

1. **Span-varying airfoil blend** — every rib station unique, optimized for local Re
2. **Optimized tip closure** — swept LE controls vortex formation
3. **All-moving simplicity** — one piece per half, no hinge gap drag
4. **Vase-mode construction** — lightest possible continuous shell
