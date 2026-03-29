# AeroForge Sailplane Specifications

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

## Fuselage

- **Configuration**: Pod-and-boom (not monocoque)
- **Pod**: Printed in 2 halves (left/right), LW-PLA shell + PLA internal structure
- **Boom**: Off-the-shelf carbon tube, 10-12mm OD, ~650mm
- **Layout** (nose to tail): Motor mount → ESC → Battery bay (adjustable for CG) →
  Receiver → Wing saddle/spar tunnel → Servo bay → Boom socket
- **Wing attachment**: Wing saddle with spar pass-through, nylon bolts + alignment dowels
- **CG target**: 30-35% of mean aerodynamic chord

## Empennage

- **Configuration**: Conventional (horizontal + vertical stabilizer)

### Horizontal Stabilizer (Design Consensus v2, 2026-03-29)
- **Type**: All-moving (entire surface pivots, no separate elevator)
- **Span**: 430mm (215mm per half)
- **Root chord**: 115mm (Re 61,300 at 8 m/s)
- **Tip chord**: 75mm → tapers to 60mm in last 15mm (swept LE tip)
- **Taper ratio**: 0.652 (main section)
- **Area**: ~408 cm² (4.08 dm²)
- **Aspect ratio**: 4.53
- **Airfoil**: HT-14 (7.5%) root → HT-13 (6.5%) tip, linear blend
- **Vh**: 0.382 (acceptable for all-moving)
- **S_h/S_w**: 9.8% (within F5J range 8.9–11.6%)
- **Pivot axis**: 3mm CF rod at 25% MAC
- **Rear spar**: 2mm CF rod at 65% chord
- **Deflection**: -20° to +12°
- **TE truncation**: 97% chord (~0.8mm flat TE)
- **Wall thickness**: 0.45mm (vase mode, LW-PLA)
- **Mass target**: 25g nominal (22–28g range, full assembly)
- **Print strategy**: Vase mode with diagonal rib grid, LW-PLA at 230°C

### Vertical Stabilizer (TBD — pending aero/structural consensus)
- **V-stab**: ~120mm height, tapered chord (preliminary)
- **Rudder**: 30-35% chord ratio (preliminary)

### Tail Mount
- **Tail mount**: PETG socket bonded to boom end, brass tube inserts (4mm OD / 3mm ID)

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
