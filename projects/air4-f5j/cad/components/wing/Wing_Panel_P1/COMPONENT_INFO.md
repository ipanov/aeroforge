# Wing_Panel_P1 — Component Information

## Overview

Root panel of the right half-wing (Panel 1 of 5). This is the innermost panel
that attaches to the fuselage wing saddle. The left wing uses a mirrored copy
of this component; no separate left-side component folder exists.

## Specifications

| Parameter | Value |
|-----------|-------|
| **Span station** | 0 - 256mm (from wing root) |
| **Span** | 256mm (exact Bambu bed fit) |
| **Root chord** | 210mm (at fuselage) |
| **Outboard chord** | 204mm (at P1/P2 joint) |
| **Root airfoil** | AG24 (100%) |
| **Outboard airfoil** | 90% AG24 / 10% AG03 blend |
| **Twist** | 0.0 deg (root) to -0.07 deg (outboard) -- negligible |
| **Dihedral** | 0.0 deg (flat, no polyhedral break in P1) |

## Structural Features

| Feature | Specification |
|---------|---------------|
| **Main spar** | 8mm CF tube at 25% chord (straight through panel) |
| **Rear spar** | 5x3mm spruce strip at 60% chord |
| **D-box** | LE to 30% chord, 0.70mm wall thickness |
| **Shell wall** | 0.50mm vase mode (0.70mm in D-box zone) |
| **Ribs** | 5-6 ribs at 32mm spacing, CF-PLA lattice |
| **Joint (outboard)** | Male tongue 3.0mm, 2mm deep. Flat face (0 deg dihedral) |
| **Joint (root)** | Interfaces with fuselage wing saddle |
| **Spar tunnel** | 8.3mm bore (0.15mm clearance per side) |

## Control Surface

| Feature | Specification |
|---------|---------------|
| **Type** | Flap |
| **Chord fraction** | 28% of local chord |
| **Hinge position** | 72% chord |
| **Flap chord** | 59mm (root) to 54mm (outboard) |
| **Hinge type** | TPU living hinge, 0.6mm, full span |
| **Gap seal** | 0.5mm TPU overlap on upper surface |

## Servo

| Feature | Specification |
|---------|---------------|
| **Type** | 9g digital metal gear |
| **Position** | Mid-panel (y=128mm), 35% chord |
| **Drives** | P1 flap via direct pushrod (or P1-P3 flaps via torque rod) |
| **Pocket** | 23mm x 11mm cutout in shell, CF-PETG mount frame |

## Mass Estimate

| Component | Mass (g) |
|-----------|----------|
| Shell + D-box | 7.4 |
| Ribs (CF-PLA) | 5.5 |
| Servo mount | 2.5 |
| **Panel total** | **15.4** |

(Spar, rear spar, servo, and joint hardware counted separately in wing budget.)

## Manufacturing

| Parameter | Value |
|-----------|-------|
| **Material** | LW-PLA (foamed at 230C) |
| **Print mode** | Vase mode 0.50mm (0.70mm in D-box zone) |
| **Orientation** | LE down (LE at build plate edge) |
| **Bed usage** | 256mm x 210mm (fits 256x256 bed exactly on span) |
| **Print time** | ~2.5 hours |
| **Supports** | None required |

## Notes

1. This component represents the RIGHT half panel only. Left = mirror at assembly time.
2. The airfoil blend is continuous -- not a simple two-section panel. Every rib station
   has a unique blended AG24/AG03 profile.
3. The main spar is a STRAIGHT datum line. The LE and TE curves follow the planform
   around the spar position.
4. Twist in P1 is negligible (0.07 deg total). For practical purposes, P1 is untwisted.
5. Root face must match fuselage wing saddle geometry (designed separately).

## References

- Design consensus: `cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md`
- Airfoil data: `src/cad/airfoils/ag24.dat`, `src/cad/airfoils/ag03.dat`
- Panel builder: `src/cad/wing/panel.py`
- Drawing: `Wing_Panel_P1_drawing.dxf` / `.png`

## Status

| Phase | Status |
|-------|--------|
| Design consensus | COMPLETE (Wing Assembly DESIGN_CONSENSUS.md) |
| 2D Drawing | COMPLETE (v1, FOR APPROVAL) |
| 3D Model | COMPLETE (Build123d loft, 9 ribs, D-box, spars) |
| Mesh + 3MF | NOT STARTED |
| Renders | COMPLETE (4 standard views) |
| Validation | VISUAL PASS (isometric, front, top, right checked) |
