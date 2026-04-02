# Component: Rudder

## Description

Rudder shell — the movable control surface forming the aft portion of the VStab
(vertical stabilizer). The rudder chord varies from 38% of VStab chord at the root
(68.4mm including bull-nose) to 35% at the tip (32.3mm). The hinge line runs from
62% chord at root to 65% chord at tip. A convex bull-nose extends 2.5mm forward of
the hinge line at root, tapering to zero at Z=155mm, providing aerodynamic sealing
when nested into the concave saddle on the VStab trailing edge. A 0.6mm wire bore
carries the concealed piano-wire hinge (0.5mm ASTM A228 spring steel), and a 1.6mm
pushrod hole at Z=9mm accepts the Z-bend control linkage.

The rudder is functionally identical in concept to the Elevator — a bull-nose control
surface that forms the trailing portion of a symmetric (HT-series) airfoil — but
oriented vertically on the VStab instead of horizontally on the HStab.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Custom printed component |
| Material | LW-PLA |
| Shell mass | 5.15 g (analytical, 0.40mm wall) |
| Total mass (with ribs, wire, sleeves, seal) | 5.96 g |
| Root chord (hinge to TE) | 66.3 mm (38% of 180mm VStab) |
| Tip chord (hinge to TE) | 32.3 mm (35% of 95mm VStab) |
| Height (span) | 165 mm |
| Hinge line position | 62% chord (root) to 65% chord (tip) |
| Bull-nose overhang | 2.5 mm at root, tapering to 0 at Z=155mm |
| Wall thickness | 0.40 mm (vase mode) |
| Bull-nose wall | 0.55 mm (reinforced) |
| Hinge wire bore | 0.6 mm diameter |
| Pushrod hole | 1.6 mm diameter at Z=9mm |
| Root airfoil | HT-14 (aft 38% of profile) |
| Tip airfoil | HT-12 (aft 35% of profile) |
| Planform area | ~81.3 cm^2 |
| Deflection range | +/-30 deg |

## Bounding Box

| Axis | Min | Max | Extent |
|------|-----|-----|--------|
| X (chord) | -2.5 mm | 66.3 mm | 68.8 mm |
| Y (height) | 0.0 mm | 165.0 mm | 165.0 mm |
| Z (thickness) | -3.6 mm | 3.6 mm | 7.2 mm |

## Print Settings

| Parameter | Value |
|-----------|-------|
| Material | LW-PLA |
| Nozzle temp | 230 C |
| Mode | Vase mode (spiral), 0.40 mm wall |
| Bull-nose zone | 0.55 mm reinforced wall |
| Orientation | Hinge face down on build plate |
| Supports | None (vase mode) |
| Est. print time | ~60 min |

## Internal Structure

| Element | Position | Mass (g) |
|---------|----------|----------|
| Internal ribs (3x) | Z=41, 83, 124 mm | 0.11 |
| PETG sleeves (5x, rudder side) | 20mm intervals, interleaved | 0.02 |
| Hinge wire (shared) | 0.5mm spring steel, 170mm | 0.26 |
| Gap seal | 0.05mm Mylar + 3M 468MP, 170x12mm | 0.18 |
| Z-bend clevis | At pushrod attachment | 0.15 |

## Assembly Notes

- The bull-nose interlocks with the hinge saddle on the VStab fixed fin, with
  alternating PETG sleeves on the 0.5mm music wire providing bearing surfaces.
- 10 total PETG sleeves: 5 in fixed fin, 5 in rudder, at 20mm intervals.
- Wire enters from fin tip (Z=165), passes through all sleeves, bent 90 deg
  at both ends for retention.
- The rudder starts at the hinge face; cross-sections of this component show
  only the rudder shell, not the VStab airfoil forward of the hinge.
- Pushrod connects at Z=9mm through the 1.6mm hole via Z-bend from Bowden
  tube (1.0mm wire in 2.0mm OD PTFE) routed from rudder servo at fuselage X=350.
- Deflection range: +/-30 degrees, limited by bull-nose/saddle clearance.
- Trailing edge is sharp and unsupported; handle with care during assembly.
- No rudder-elevator interference at any combined deflection (perpendicular axes).

## Design Source

Specifications from Fuselage Assembly DESIGN_CONSENSUS v2 (rudder integration round).
See: `cad/assemblies/fuselage/Fuselage_Assembly/DESIGN_CONSENSUS.md`
