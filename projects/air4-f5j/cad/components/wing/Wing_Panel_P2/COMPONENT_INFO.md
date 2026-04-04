# Wing_Panel_P2 -- Component Information

## Overview

Second panel of the right half-wing (Panel 2 of 5). Span station
256-512mm from wing root. The left wing uses a mirrored copy
of this component; no separate left-side component folder exists.

## Specifications

| Parameter | Value |
|-----------|-------|
| **Span station** | 256 - 512mm (from wing root) |
| **Span** | 256mm (exact Bambu bed fit) |
| **Root chord** | 204mm (at P1/P2 joint) |
| **Outboard chord** | 198mm (at P2/P3 joint) |
| **Root airfoil** | 90% AG24 / 10% AG03 blend |
| **Outboard airfoil** | 80% AG24 / 20% AG03 blend |
| **Twist** | -0.1 deg (root) to -0.4 deg (outboard) |
| **Dihedral** | 0.0 deg (inboard face) / 0.0 deg (outboard face) |

## Structural Features

| Feature | Specification |
|---------|---------------|
| **Main spar** | 8mm CF tube at 25% chord |
| **Rear spar** | 5x3mm spruce strip at 60% chord |
| **D-box** | LE to 30% chord, 0.70mm wall thickness |
| **Shell wall** | 0.50mm vase mode (0.70mm in D-box zone) |
| **Ribs** | 5-6 ribs at ~32mm spacing, CF-PLA lattice |
| **Joint (inboard)** | Female groove 3.2mm. 0.0 deg dihedral |
| **Joint (outboard)** | Male tongue 3.0mm, 2mm deep. 0.0 deg dihedral |
| **Spar tunnel** | 8.3mm bore (8.0mm + 0.15mm clearance/side) |

## Control Surface

| Feature | Specification |
|---------|---------------|
| **Type** | Flap |
| **Chord fraction** | 28% of local chord |
| **Hinge position** | 72% chord |
| **Flap chord** | 57mm (root) to 55mm (outboard) |
| **Hinge type** | TPU living hinge, 0.6mm, full span |
| **Gap seal** | 0.5mm TPU overlap on upper surface |

## Servo

No dedicated servo in P2. The flap is driven from the adjacent
panel servo via torque rod linkage.

## Mass Estimate

| Component | Mass (g) |
|-----------|----------|
| Shell + D-box | 7.2 |
| Ribs (CF-PLA) | 5.3 |
| Servo mount | 0.0 |
| **Panel total** | **12.5** |

(Spar, rear spar, servo, and joint hardware counted separately in wing budget.)

## Manufacturing

| Parameter | Value |
|-----------|-------|
| **Material** | LW-PLA (foamed at 230C) |
| **Print mode** | Vase mode 0.50mm (0.70mm in D-box zone) |
| **Orientation** | LE down (LE at build plate edge) |
| **Bed usage** | 256mm x 204mm (fits 256x256 bed) |
| **Print time** | ~2.5 hours |
| **Supports** | None required |

## Notes

1. This component represents the RIGHT half panel only. Left = mirror at assembly time.
2. The airfoil blend is continuous -- every rib station has a unique blended AG24/AG03 profile.
3. The main spar is a STRAIGHT datum line. The LE and TE curves follow the planform
   around the spar position.
4. Twist distribution follows twist(eta) = -4.0 * eta^2.5 (non-linear washout).
5. Dihedral is built into the joint face geometry, NOT bent into the spar.

## References

- Design consensus: `cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md`
- Airfoil data: `src/cad/airfoils/ag24.dat`, `src/cad/airfoils/ag03.dat`
- Panel builder: `src/cad/wing/panel.py`
- Drawing: `Wing_Panel_P2_drawing.dxf` / `.png`

## Status

| Phase | Status |
|-------|--------|
| Design consensus | COMPLETE (Wing Assembly DESIGN_CONSENSUS.md) |
| 2D Drawing | COMPLETE (v1, FOR APPROVAL) |
| 3D Model | NOT STARTED |
| Mesh + 3MF | NOT STARTED |
| Renders | NOT STARTED |
| Validation | PENDING (drawing review) |
