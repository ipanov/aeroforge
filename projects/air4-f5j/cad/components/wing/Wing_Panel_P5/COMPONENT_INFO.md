# Wing_Panel_P5 -- Component Information

## Overview

Tip panel of the right half-wing (Panel 5 of 5). Span station
1024-1280mm from wing root. The left wing uses a mirrored copy
of this component; no separate left-side component folder exists.

## Specifications

| Parameter | Value |
|-----------|-------|
| **Span station** | 1024 - 1280mm (from wing root) |
| **Span** | 256mm (exact Bambu bed fit) |
| **Root chord** | 168mm (at P4/P5 joint) |
| **Outboard chord** | 115mm (at wing tip) |
| **Root airfoil** | 25% AG24 / 75% AG03 blend |
| **Outboard airfoil** | 0% AG24 / 100% AG03 blend |
| **Twist** | -2.3 deg (root) to -4.0 deg (outboard) |
| **Dihedral** | 2.5 deg (inboard face) / 3.0 deg (outboard face) |

## Structural Features

| Feature | Specification |
|---------|---------------|
| **Main spar** | 5mm CF rod at 27% chord |
| **Rear spar** | None (D-box provides torsion) |
| **D-box** | LE to 30% chord, 0.70mm wall thickness |
| **Shell wall** | 0.50mm vase mode (0.70mm in D-box zone) |
| **Ribs** | 5-6 ribs at ~32mm spacing, CF-PLA lattice |
| **Joint (inboard)** | Female groove 3.2mm. 2.5 deg dihedral |
| **Joint (outboard)** | Tip closure (integrated). Winglet attach point.. 3.0 deg dihedral |
| **Spar tunnel** | 5.3mm bore (5.0mm rod + 0.15mm clearance/side) |

## Control Surface

| Feature | Specification |
|---------|---------------|
| **Type** | Aileron |
| **Chord fraction** | 28% of local chord |
| **Hinge position** | 72% chord |
| **Aileron chord** | 47mm (root) to 32mm (outboard) |
| **Hinge type** | TPU living hinge, 0.6mm, full span |
| **Gap seal** | 0.5mm TPU overlap on upper surface |

## Servo

| Feature | Specification |
|---------|---------------|
| **Type** | 5g low-profile digital (7mm height) |
| **Position** | Mid-panel (y=1152mm), 30% chord |
| **Drives** | P5 aileron via direct pushrod |
| **Pocket** | 20mm x 10mm cutout in shell |

## Mass Estimate

| Component | Mass (g) |
|-----------|----------|
| Shell + D-box | 5.1 |
| Ribs (CF-PLA) | 3.8 |
| Servo mount | 2.5 |
| **Panel total** | **11.3** |

(Spar, rear spar, servo, and joint hardware counted separately in wing budget.)

## Manufacturing

| Parameter | Value |
|-----------|-------|
| **Material** | LW-PLA (foamed at 230C) |
| **Print mode** | Vase mode 0.50mm (0.70mm in D-box zone) |
| **Orientation** | LE down (LE at build plate edge) |
| **Bed usage** | 256mm x 168mm (fits 256x256 bed) |
| **Print time** | ~2.5 hours |
| **Supports** | None required |

## Notes

1. This component represents the RIGHT half panel only. Left = mirror at assembly time.
2. The airfoil blend is continuous -- every rib station has a unique blended AG24/AG03 profile.
3. The main spar is a STRAIGHT datum line. The LE and TE curves follow the planform
   around the spar position.
4. Twist distribution follows twist(eta) = -4.0 * eta^2.5 (non-linear washout).
5. Dihedral is built into the joint face geometry, NOT bent into the spar.
6. Winglet attaches at tip face (80mm height, NACA 0006, 75 deg cant).

## References

- Design consensus: `cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md`
- Airfoil data: `src/cad/airfoils/ag24.dat`, `src/cad/airfoils/ag03.dat`
- Panel builder: `src/cad/wing/panel.py`
- Drawing: `Wing_Panel_P5_drawing.dxf` / `.png`

## Status

| Phase | Status |
|-------|--------|
| Design consensus | COMPLETE (Wing Assembly DESIGN_CONSENSUS.md) |
| 2D Drawing | COMPLETE (v1, FOR APPROVAL) |
| 3D Model | NOT STARTED |
| Mesh + 3MF | NOT STARTED |
| Renders | NOT STARTED |
| Validation | PENDING (drawing review) |
