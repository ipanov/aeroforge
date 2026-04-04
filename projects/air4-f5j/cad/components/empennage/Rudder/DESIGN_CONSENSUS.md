# Design Consensus: Rudder

**Date:** 2026-04-02
**Status:** AGREED (inherited from Fuselage Assembly v2 consensus)

## Source

All rudder specifications are defined in the Fuselage Assembly consensus v2:
`cad/assemblies/fuselage/Fuselage_Assembly/DESIGN_CONSENSUS.md`

The rudder was designed through a 2-round aero-structural agent review as part of
the fuselage/VStab integration. Both agents signed off.

## Key Specifications (from Fuselage Consensus v2)

| Parameter | Value |
|-----------|-------|
| Rudder chord ratio (root) | 38% of VStab root chord (68.4mm) |
| Rudder chord ratio (tip) | 35% of VStab tip chord (33.3mm) |
| Rudder height | 165mm (full VStab span) |
| Rudder hinge line (root) | 62% chord from VStab LE (111.6mm) |
| Rudder hinge line (tip) | 65% chord from VStab LE (61.7mm) |
| Rudder planform area | 83.9 cm^2 |
| Root airfoil | HT-14 (aft 38% of profile) |
| Tip airfoil | HT-12 (aft 35% of profile) |
| Deflection range | +/-30 deg |
| Yaw authority (Cn_delta_r) | 0.033 |
| Target mass | 5.96g |

## Structural Elements

| Element | Specification | Mass (g) |
|---------|--------------|----------|
| Shell | LW-PLA, 0.4mm vase mode | 5.22 |
| Internal ribs | 3x LW-PLA 0.6mm, at Z=41, 83, 124mm | 0.11 |
| Hinge wire | 0.5mm ASTM A228 spring steel, 170mm | 0.26 |
| PETG sleeves (rudder side) | 5x (1.2mm OD / 0.6mm ID / 3mm long) | 0.02 |
| Gap seal | 0.05mm Mylar + 3M 468MP, 170mm x 12mm | 0.18 |
| Z-bend clevis | Steel clevis at pushrod attachment | 0.15 |
| **Total** | | **5.96g** |

## VStab Geometry Context

| Parameter | Value |
|-----------|-------|
| VStab height | 165mm |
| VStab root chord | 180mm |
| VStab tip chord | 95mm |
| VStab LE | Straight (zero sweep), X=866mm fuselage station |
| Root airfoil | HT-14 (7.5% t/c) |
| Tip airfoil | HT-12 (5.1% t/c) |
| Taper ratio | 0.528 |

## Hinge Design

Concealed piano-wire hinge, identical concept to HStab elevator:
- 0.5mm ASTM A228 spring steel wire, 170mm long
- 10 PETG sleeves total (5 in fixed fin, 5 in rudder, interleaved at 20mm intervals)
- Wire enters from fin tip, exits at base with 90-deg bends at both ends
- Bull-nose on rudder LE mates with concave saddle in VStab TE

## Pushrod Attachment

- 1.6mm hole in rudder root face, 8-10mm above Z=0
- Z-bend through hole, connected to 1.0mm music wire in PTFE Bowden tube
- Route: Rudder servo (X=350 fuselage) through boom/fin interior to rudder root
