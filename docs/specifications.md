# AeroForge Sailplane Specifications

## Authority Note

This document is a framework-level baseline, not the final authority for an
active aircraft under refinement.

For the current glider program, the authoritative values are the active
assembly-level `DESIGN_CONSENSUS.md` files:
- `cad/assemblies/Iva_Aeroforge/DESIGN_CONSENSUS.md`
- `cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md`
- `cad/assemblies/fuselage/Fuselage_Assembly/DESIGN_CONSENSUS.md`
- `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md`

When this file disagrees with an active assembly consensus, the assembly
consensus wins.

## Parent-Drawing Policy

Whole-aircraft and parent-level assembly drawings must include off-the-shelf
components as **engineering envelopes only** for:
- packaging
- CG accounting
- cooling / routing
- interference checks

The project does **not** create owned manufacturing drawings for vendor parts
such as batteries, motors, ESCs, receivers, servos, spinners, or propellers at
this stage.

## Baseline Dimensions

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Wingspan** | 2560mm (2.56m) | 5 panels per half-wing, 256mm each |
| **Root chord** | 210mm | At fuselage centerline |
| **Tip chord** | 115mm | Taper ratio ~0.55 |
| **Wing area** | ~41.6 dm² | Trapezoidal approximation |
| **Aspect ratio** | ~15.8 | High AR for thermal efficiency |
| **Sweep** | TBD (AI-optimized) | Slight sweep likely for CG |
| **Dihedral** | TBD (AI-optimized) | Continuous polyhedral possible |
| **Twist (washout)** | TBD (AI-optimized) | Continuously varying, not linear |

## Wing Panel Layout

10 panels total, 5 per half-wing, each 256mm span (exact Bambu bed fit).

```
Tip ◄── P5 ──┬── P4 ──┬── P3 ──┬── P2 ──┬── P1 ──► Root
     256mm   │ 256mm  │ 256mm  │ 256mm  │ 256mm
     Aileron │Aileron │ Flap   │ Flap   │ Flap
     AG03    │AG-blend│AG-blend│AG-blend│ AG24
             │        │        │        │
            joint    joint    joint    joint    fuselage
```

Each panel slides onto the carbon spar tube. Panels are unique - different airfoil
profile at every rib station, different chord (taper), different twist angle.

## Airfoils

| Station | Airfoil | Chord | Thickness | Reynolds (8 m/s) |
|---------|---------|-------|-----------|------------------|
| Root (0%) | AG24 | 210mm | ~9.0% (19mm) | ~112,000 |
| 25% span | AG24→AG09 blend | 186mm | ~9.1% | ~99,000 |
| 50% span | AG09 | 162mm | ~9.2% | ~87,000 |
| 75% span | AG09→AG03 blend | 139mm | ~8.8% | ~74,000 |
| Tip (100%) | AG03 | 115mm | ~8.4% | ~61,000 |

Blending is continuous - every rib has a unique, interpolated airfoil profile.
This is a key advantage over commercial kits limited to 2-3 stations.

Final airfoil selection subject to xfoil/CFD analysis at actual Reynolds numbers.

## Structure

### Spars
| Spar | Material | Size | Source | Role |
|------|----------|------|--------|------|
| **Main spar** | Pultruded carbon tube | 8mm OD (off-shelf) | HobbyKing/AliExpress | Primary bending |
| **Rear spar** | Spruce strip | ~5x3mm | Local (Macedonia) | Torsion + TE support |

No hand-cut carbon. Carbon tube slides through printed holes. Spruce glues into slots.

### Printed Structure
| Part | Material | Wall Thickness | Print Mode | Printer |
|------|----------|---------------|------------|---------|
| Wing skins | LW-PLA | 0.5-0.6mm | Vase/2-perimeter, 230°C | A1 or P1S |
| D-box (LE to 30% chord) | LW-PLA | 0.6-0.8mm | Structural shell for torsion | A1 or P1S |
| Ribs/formers | **CF-PLA** | 1.0-1.2mm | Lattice/lightened, 30% infill | A1/P1S + hardened nozzle |
| Servo mounts | **CF-PETG** | 1.6-2.0mm | Impact-resistant | P1S preferred |
| Motor mount | **CF-PETG** | 2.0-3.0mm | High stress, vibration | P1S preferred |
| Fuselage shell | LW-PLA | 0.6mm | Lightweight outer | A1 or P1S |
| Fuselage bulkheads | CF-PLA or PETG | 1.2-1.6mm | Internal structure | A1 or P1S |
| Tail surfaces | LW-PLA | 0.5-0.6mm | Lightweight | A1 or P1S |
| Hinges | **TPU 95A** | 0.6-0.8mm | Flexible living hinge | A1 or P1S |

### Material Properties
| Material | Density (g/cm³) | Tensile (MPa) | Stiffness (GPa) | Cost (€/kg) | Nozzle |
|----------|----------------|---------------|-----------------|-------------|--------|
| LW-PLA (foamed 230°C) | 0.7-0.85 | 20-35 | 1.5-2.5 | 30-45 | Brass OK |
| PLA | 1.24 | 50-65 | 3.5-4.0 | 15-25 | Brass OK |
| CF-PLA | 1.25-1.30 | 55-70 | 5.5-8.0 | 30-50 | **Hardened steel** |
| CF-PETG | 1.30-1.35 | 50-65 | 4.5-6.5 | 35-55 | **Hardened steel** |
| PETG | 1.27 | 45-55 | 2.0-2.5 | 18-28 | Brass OK |
| TPU 95A | 1.20-1.25 | 25-50 | flexible | 25-40 | Brass OK |

**Nozzle note**: Buy one hardened steel 0.4mm nozzle per printer (~€10-15). CF filaments destroy brass nozzles.

**LW-PLA brands** (in order of quality): ColorFabb LW-PLA > Polymaker PolyLite LW-PLA > eSUN eLW-PLA.
Available via 3DJake.com (ships to Balkans), Bambu Lab Store, Amazon.de.

### Key Structural Notes
- Every rib is unique (different airfoil, different chord, different lightening pattern)
- Internal structure can be geodetic lattice, topology-optimized - complexity is free
- D-box (leading edge shell from LE to ~30% chord) is the primary torsion structure
- Carbon tube main spar carries all bending loads
- Panel joints: panels slide onto spar, secured with printed locking features + CA glue

## Weight Budget

### Fixed Components (Owner's Inventory)
| Component | Weight | Dimensions | Notes |
|-----------|--------|------------|-------|
| **Battery (3S 1300mAh 75C racing LiPo)** | ~155g (165g w/ XT60) | ~78x38x28mm | Fixed constraint, two available |
| **Receiver (Turnigy 9X V2 8ch)** | 18g | 52x35x15mm | Fixed constraint, large |

### Electronics Budget
| Component | Weight (g) | Notes |
|-----------|-----------|-------|
| Battery (3S 1300mAh 75C + XT60) | 165 | Fixed (155g pack + 10g connector) |
| Receiver (Turnigy 9X V2) | 18 | Fixed |
| Servos (6x 9g class) | 54 | Ailerons x2, flaps x2, elevator, rudder |
| Motor (TBD - ideal KV) | 50-60 | Will order optimal motor last |
| ESC (20-30A) | 15-20 | |
| Folding prop + spinner | 15-20 | |
| Wiring, connectors, extensions | 20-25 | Includes wing connectors |
| **Electronics total** | **~330-350** | |

### Airframe Budget
| Component | Weight (g) | Notes |
|-----------|-----------|-------|
| Wing structure (6 panels, LW-PLA) | 200-260 | Skins + ribs + D-box |
| Wing spars (carbon tube + spruce) | 25-35 | Main + rear, full span |
| Fuselage pod (printed) | 50-70 | Two halves + internal structure |
| Tail boom (carbon tube) | 20-25 | 10-12mm OD, ~650mm |
| Empennage (H-stab + V-stab) | 25-35 | Printed, lightweight |
| Hardware (screws, hinges, horns) | 20-30 | M2/M3, music wire, clevises |
| **Airframe total** | **~340-455** | |

### Total
| | Min | Target | Max |
|--|-----|--------|-----|
| **AUW** | 700g | 750-800g | 900g |
| **Wing loading** | 17 g/dm² | 18-19 g/dm² | 22 g/dm² |

Wing loading of 18-19 g/dm² is competitive with commercial F5J kits (~18-25 g/dm²).
The larger wingspan (2.56m) properly accommodates the heavy racing battery.
Higher Reynolds numbers (112,000 at root) let AG airfoils perform near their optimum.

## Control System

### Turnigy 9X (9 channels, 8 proportional + 1 switch)
| Channel | Function | Servo Location |
|---------|----------|----------------|
| CH1 | Right Aileron | Right wing, outboard panel |
| CH2 | Elevator | Fuselage pod |
| CH3 | Throttle/Motor | ESC |
| CH4 | Rudder | Fuselage pod |
| CH5 | Right Flap | Right wing, root panel |
| CH6 | Left Flap | Left wing, root panel |
| CH7 | Left Aileron | Left wing, outboard panel |
| CH8 | Flight Mode (3-pos switch) | Virtual |

### Flight Modes
| Mode | Ailerons | Flaps | Elevator Trim | Use |
|------|----------|-------|---------------|-----|
| **Launch** | Reflex (+2°) | Reflex (+2°) | Slight down | Motor climb, max speed |
| **Cruise** | Neutral | Neutral | Neutral | Normal flying |
| **Speed** | Slight reflex | Reflex (+1°) | Slight down | Wind penetration |
| **Thermal** | Down (-2°) | Camber (-5°) | Compensate up | Circling in lift, min sink |
| **Landing (Crow)** | UP (+45°) | DOWN (-60°) | Compensate down | Steep drag descent |

Crow braking: ailerons up as spoilers + flaps down for drag. Mixed on proportional
slider/knob for variable deployment. AI-assisted programming of Turnigy 9X curves.

### Control Surface Actuation
| Surface | Actuation | Linkage |
|---------|-----------|---------|
| Ailerons | Wing-mounted 9g servos | Short pushrod, Z-bend |
| Flaps | Wing-mounted 9g servos | Short pushrod, Z-bend |
| Elevator | Pod-mounted 9g servo | Carbon rod pushrod through boom |
| Rudder | Pod-mounted 9g servo | Pull-pull Kevlar cable through boom |

## Fuselage (TBD — pending aero/structural consensus)

- **Configuration**: Continuous 3D-printed aerodynamic body (NOT pod-and-boom)
- **Outer shell**: One continuous optimized shape from spinner to VStab fin tip
- **Structure**: Multiple printed sections on 4 carbon rods + CA (like wing panels)
- **Internal pod**: Electronics mounting tray inside the shell (for maintainability)
- **No carbon tail boom**: The tail is printed fuselage sections, not a separate tube
- **VStab fin**: Integrated into fuselage — only the Rudder is a separate component
- **Layout** (nose to tail): Spinner → Motor mount → ESC → Battery bay (adjustable for CG) →
  Receiver → Wing saddle/spar tunnel → Servo bay → Taper → VStab fin
- **Wing fairing**: Blends into fuselage, must consider AG24 root airfoil (210mm chord)
- **Wing attachment**: Wing saddle with spar pass-through, nylon bolts + alignment dowels
- **CG target**: 30-35% of mean aerodynamic chord
- **Print sections**: Each fits Bambu 256mm bed, slide onto 4 CF rod longerons

## Empennage

- **Configuration**: Conventional (horizontal + vertical stabilizer)

### Horizontal Stabilizer (Design Consensus v3, 2026-03-30)
- **Type**: Fixed stabilizer + 35% chord elevator
- **Planform**: Superellipse n=2.3 (Oswald e=0.990)
- **Span**: 430mm (215mm per half)
- **Root chord**: 115mm (Re 61,300 at 8 m/s)
- **Tip chord**: ~50mm at 95% span (superellipse taper)
- **Mean chord**: 94.8mm
- **Area**: ~408 cm² (4.08 dm²)
- **Aspect ratio**: 4.53
- **Airfoil**: HT-13 (6.5%) root → HT-12 (5.1%) tip, linear blend
- **Vh**: 0.393
- **S_h/S_w**: 9.8% (within F5J range 8.9–11.6%)
- **Elevator**: 35% chord, hinge at 65% chord, -20° to +25° deflection
- **Hinge**: 0.5mm music wire pin through PETG knuckle strips (infinite fatigue life)
- **Main spar**: 3mm CF tube (3/2mm OD/ID), 390mm, terminates at 195mm/half
- **Rear spar**: 1.5mm CF rod at 60% chord
- **Elevator stiffener**: 1mm CF rod at 80% chord
- **VStab junction**: C2-continuous fillet (r=9.2mm) + dovetail interlock
- **TE truncation**: 97% chord (~0.7mm flat TE)
- **Wall thickness**: 0.45mm stab / 0.40mm elevator (vase mode, LW-PLA)
- **Mass balance**: 1.0g tungsten putty on control horn (flutter prevention)
- **Mass target**: 33.7g nominal (35g hard limit)
- **Print strategy**: Vase mode, LW-PLA at 230°C; PETG hinge strips printed separately

### Vertical Stabilizer (Integrated into Fuselage)
- **Height**: 165mm
- **Root chord**: 180mm, Tip chord: 95mm
- **Root airfoil**: HT-14 (7.5%), Tip: HT-12 (5.1%)
- **Rudder**: 35% chord ratio, hinge at 65% chord
- **Rear spar**: 1.5mm CF rod at 60% chord
- **Integration**: Superelliptical blend X=650–866mm (part of fuselage)

### Tail Mount
- **HStab mount**: Stab roots bond to VStab fin via dovetail interlock + CA
- **Main spar**: Continuous 3mm CF tube passes through VStab fin hole

## Manufacturing

### Printer
- **Bambu A1** or **Bambu P1S** (friends' printers)
- Build volume: 256 x 256 x 256 mm
- Each wing panel (~350mm span) fits comfortably on bed

### Materials Cost Estimate
| Item | Cost |
|------|------|
| LW-PLA filament (~500g) | $15-25 |
| PLA filament (~200g) | $5-8 |
| Carbon tube (main spar, boom) | $10-15 |
| Spruce strips (rear spar) | $2-5 |
| Hardware (screws, wire, hinges) | $5-10 |
| **Materials total** | **~$35-60** |

### Slicer Pipeline
```
Build123d → export 3MF → OrcaSlicer CLI → .gcode.3mf → Bambu printer
```

## Performance Targets

| Parameter | Target | Comparable Kit |
|-----------|--------|----------------|
| Glide ratio (L/D) | 15-20:1 | Insight F5J: ~18:1 |
| Min sink rate | < 0.5 m/s | Competition: 0.3-0.4 m/s |
| Cruise speed | 7-9 m/s | |
| Stall speed | < 4 m/s | |
| Launch altitude (10s motor) | 80-120m | F5J competition standard |
