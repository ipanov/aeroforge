# Component: Elevator_Right

## Description

Right elevator half with a concealed bull-nose hinge, a mirror of Elevator_Left across the Y=0 centerline. Identical hinge geometry, bull-nose taper, wall thicknesses, and pushrod hole as the left half. Each elevator half is actuated independently for differential deflection capability.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Custom printed component |
| Material | LW-PLA |
| Mass | 5.05 g |
| Root chord | ~51.5 mm (45% of stab chord) |
| Hinge line position | X=60.0 mm |
| Bull-nose overhang | 2.5 mm at root, tapering to 0 at y=206 mm |
| Wall thickness | 0.40 mm (vase mode) |
| Bull-nose wall | 0.55 mm (reinforced) |
| Hinge wire bore | 0.6 mm diameter |
| Pushrod hole | 1.6 mm diameter at X=70 mm |
| Mirror | Y=0 mirror of Elevator_Left |

## Print Settings

| Parameter | Value |
|-----------|-------|
| Material | LW-PLA |
| Nozzle temp | 230 C |
| Mode | Vase mode (spiral), 0.40 mm wall |
| Bull-nose zone | 0.55 mm reinforced wall |
| Orientation | Bull-nose face down on build plate |
| Supports | None (vase mode) |

## Assembly Notes

- Mirror image of Elevator_Left. Generate STL by mirroring across Y=0 or running the parametric script with `mirror=True`.
- Mates with HStab_Right via the concealed hinge system (alternating PETG sleeves on music wire).
- Independent servo actuation allows differential elevator for roll/pitch mixing if desired.
- Pushrod connects at X=70mm through the 1.6mm hole to its own dedicated micro servo.
