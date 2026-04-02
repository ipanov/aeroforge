# Component: HStab_Tip_Cap

## Description
Replaceable tip cap for the horizontal stabilizer. ONE-PIECE full-airfoil design
(not split at hinge line) covering the outermost 4.4mm of span where the
superellipse planform transitions through the C1-continuous cubic tip closure
to near-zero chord. Bonded with CA glue at a 1mm overlap joint (y=209-210).
Designed to break on impact during handling, protecting the main stab body
from damage. Identical part used on both left and right sides.

## Build Method
NURBS loft of 10 cross-sections:
- Y=209 to Y=212: HT-13/HT-12 blended airfoil sections (60pts/surface Spline)
- Y=212.5 to Y=213.4: Elliptical sections matching local chord and t/c ratio
- C1 continuity maintained at superellipse-to-cubic transition (Y=210)

## Specifications
| Parameter | Value |
|-----------|-------|
| Type | Custom printed (LW-PLA) |
| Span coverage | Y=209.0 to Y=213.4mm (4.4mm) |
| Root chord at joint | 34.6mm (at y=209) |
| Tip chord | ~1.7mm (at y=213.4) |
| Max thickness | 1.75mm (at root) |
| Airfoil | HT-13/HT-12 blend -> ellipse at tip |
| Volume | 106 mm3 |
| Mass (LW-PLA foamed 0.50) | 0.05g |
| Quantity | 2 (one per side, identical) |
| Bond method | CA glue at y=209-210 overlap |
| Alignment | Friction fit at joint face |
| Faces | 3 (upper, lower, root joint) |

## Print Settings
| Setting | Value |
|---------|-------|
| Material | LW-PLA |
| Temperature | 230C |
| Mode | Vase mode 0.45mm |
| Orientation | Flat, joint face down |

## Assembly Notes
- Slide tip cap onto stab end at Y=209 joint face
- Apply thin CA to the 1mm overlap zone (Y=209-210)
- Hold 10 seconds for bond
- If broken: twist off remnants, sand flat, glue replacement
- Keep 2-3 spares in field box
- The tip cap covers the FULL airfoil (stab + elevator chord)
- The elevator tip is NOT separate -- it is part of this tip cap
