# Wing_Panel_P4 -- Component Information

## Overview

Fourth panel of the right half-wing (Panel 4 of 5). Span station
768-1024mm from wing root. The left wing uses a mirrored copy
of this component; no separate left-side component folder exists.

## Specifications

| Parameter | Value |
|-----------|-------|
| **Span station** | 768 - 1024mm (from wing root) |
| **Span** | 256mm (exact Bambu bed fit) |
| **Root chord** | 186mm (at P3/P4 joint) |
| **Outboard chord** | 168mm (at P4/P5 joint) |
| **Root airfoil** | 55% AG24 / 45% AG03 blend |
| **Outboard airfoil** | 25% AG24 / 75% AG03 blend |
| **Twist** | -1.1 deg (root) to -2.3 deg (outboard) |
| **Dihedral** | 1.5 deg (inboard face) / 2.5 deg (outboard face) |

## Structural Features

| Feature | Specification |
|---------|---------------|
| **Main spar** | 8mm CF tube at 25% chord |
| **Rear spar** | 5x3mm spruce strip at 60% chord |
| **D-box** | LE to 30% chord, 0.70mm wall thickness |
| **Shell wall** | 0.50mm vase mode (0.70mm in D-box zone) |
| **Ribs** | 5-6 ribs at ~32mm spacing, CF-PLA lattice |
| **Joint (inboard)** | Female groove 3.2mm. 1.5 deg dihedral |
| **Joint (outboard)** | Male tongue 3.0mm, 2mm deep. 2.5 deg dihedral |
| **Spar tunnel** | 8.3mm bore (8.0mm + 0.15mm clearance/side) |

## Control Surface

| Feature | Specification |
|---------|---------------|
| **Type** | Aileron |
| **Chord fraction** | 28% of local chord |
| **Hinge position** | 72% chord |
| **Aileron chord** | 52mm (root) to 47mm (outboard) |
| **Hinge type** | TPU living hinge, 0.6mm, full span |
| **Gap seal** | 0.5mm TPU overlap on upper surface |

## Servo

| Feature | Specification |
|---------|---------------|
| **Type** | 9g digital metal gear |
| **Position** | Mid-panel (y=896mm), 35% chord |
| **Drives** | P4 aileron via direct pushrod |
| **Pocket** | 23mm x 11mm cutout in shell, CF-PETG mount frame |

## Mass Estimate

| Component | Mass (g) |
|-----------|----------|
| Shell + D-box | 6.3 |
| Ribs (CF-PLA) | 4.7 |
| Servo mount | 2.5 |
| **Panel total** | **13.5** |

(Spar, rear spar, servo, and joint hardware counted separately in wing budget.)

## Manufacturing

| Parameter | Value |
|-----------|-------|
| **Material** | LW-PLA (foamed at 230C) |
| **Print mode** | Vase mode 0.50mm (0.70mm in D-box zone) |
| **Orientation** | LE down (LE at build plate edge) |
| **Bed usage** | 256mm x 186mm (fits 256x256 bed) |
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
- Drawing: `Wing_Panel_P4_drawing.dxf` / `.png`

## Status

| Phase | Status |
|-------|--------|
| Design consensus | COMPLETE (Wing Assembly DESIGN_CONSENSUS.md) |
| 2D Drawing | COMPLETE (v1, FOR APPROVAL) |
| 3D Model | NOT STARTED |
| Mesh + 3MF | NOT STARTED |
| Renders | NOT STARTED |
| Validation | PENDING (drawing review) |
