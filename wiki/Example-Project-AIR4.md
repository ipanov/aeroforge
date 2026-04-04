# Example Project: AIR4

AIR4 is the first example project built with the AeroForge framework -- an electric F5J thermal sailplane (the "Iva Aeroforge").

---

## Project Location

```
projects/air4-f5j/
├── aeroforge.yaml          # Project config + providers
├── cad/
│   ├── components/         # Individual pieces
│   │   ├── empennage/      # H-stab, elevator, etc.
│   │   ├── wing/           # Wing panels
│   │   ├── fuselage/       # Pod, boom
│   │   └── hardware/       # Servos, battery, rods
│   └── assemblies/         # Multi-piece assemblies
│       ├── empennage/      # H-stab assembly
│       ├── wing/           # Wing assembly
│       └── Iva_Aeroforge/  # Top-level aircraft
├── docs/                   # Project-specific docs
│   └── specifications.md   # Locked-in specs
└── exports/                # Generated artifacts
```

---

## Quick Reference

| Parameter | Value |
|-----------|-------|
| Wingspan | 2.56m |
| Panels | 10 (5 per half, 256mm each -- exact bed fit) |
| Root chord | 210mm |
| Tip chord | 115mm |
| Airfoil | AG24 (root) to AG03 (tip), blended continuously |
| Main spar | 8mm carbon tube (off-shelf) |
| Rear spar | 5mm spruce strip |
| Target AUW | 750-850g |
| Battery | 3S 1300mAh 75C racing LiPo (~155g pack, ~165g w/XT60) |
| Receiver | Turnigy 9X V2 8ch (18g) |
| Controls | Full-house + crow braking, 6 servos |
| Printer | Bambu A1 / P1S (256x256x256mm bed) |

---

## What AIR4 Demonstrates

AIR4 exercises every part of the AeroForge framework:

| Capability | How AIR4 uses it |
|-----------|-----------------|
| Multi-level node tree | Aircraft > Wing/Empennage/Fuselage assemblies > individual panels/components |
| Agent design cycle | Aerodynamicist and structural engineer iterate on every aerodynamic surface |
| Drawing-first workflow | All components have 2D DXF drawings approved before 3D modeling |
| Provider system | FDM manufacturing, OrcaSlicer, SU2 CUDA CFD, FreeCAD FEA |
| Assembly validation | Collision and containment checks on all assemblies |
| Symmetric components | Wing panels mirrored at assembly time, not duplicated |
| Living BOM | Tracks all printed parts, off-shelf hardware, and costs |
| RAG knowledge base | Populated with F5J competition sailplane data |

---

## Design Philosophy Applied

AIR4 embodies the core AeroForge principle: "Why make it simple when it can be complex -- for the same price?"

- **Blended airfoils** at every rib station (AG24 to AG03 continuous blend)
- **Geodetic lattice ribs** -- internal structure that would be impossible to manufacture traditionally
- **Topology-optimized mounts** for servos and hardware
- **Integrated gap seals** on control surfaces
- **Zero exposed hardware** on aerodynamic surfaces

The goal: beat EUR 2000 carbon F5J models with a EUR 60 printed sailplane by exploiting the zero marginal cost of geometric complexity in FDM printing.

---

## Note

AIR4 is project-specific material. It should not be read as the generic framework definition. The framework is aircraft-type agnostic -- AIR4 is one instantiation of it.
