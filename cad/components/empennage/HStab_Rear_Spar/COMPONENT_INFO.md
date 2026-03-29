# Component: HStab_Rear_Spar

## Description
The anti-rotation rear spar for the fixed horizontal stabilizer halves. A solid pultruded carbon fiber rod that threads through both HStab_Left and HStab_Right shells at 60% chord. Together with the main spar it forms a two-point constraint that prevents the stab from rotating about the main spar axis under elevator aerodynamic loads.

## Specifications
| Parameter       | Value                             | Source              |
|-----------------|-----------------------------------|---------------------|
| Material        | Pultruded Carbon Fiber Solid Rod  | specifications.md   |
| Diameter        | 1.5 mm                            | drawing             |
| Length          | 440 mm                            | drawing             |
| Weight          | 1.20 g                            | calculated          |
| Chord position  | 60% chord                         | design consensus    |

## Manufacturing
- Print orientation: N/A — off-shelf component
- Material: Pultruded carbon fiber solid rod (not printed)
- Special notes: Standard 1.5mm CF rod. Cut to 440mm with a rotary tool. Spans across both stab halves plus the VStab core.

## Connections
- Connects to: HStab_Left shell spar channel, HStab_Right shell spar channel
- Connection method: Slide-through (light press fit into printed PETG channels, CA-tipped at ends)

## Drawing Approval
- Date: 2026-03-29
- Approved by: AI review (off-shelf hardware, dimensions from assembly consensus)
- Drawing file: HStab_Rear_Spar_drawing.dxf
