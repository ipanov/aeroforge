# AeroForge Sailplane Specifications

## Baseline Dimensions

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Wingspan** | 2100mm (2.1m) | 3 panels per half-wing |
| **Root chord** | 200mm | At fuselage centerline |
| **Tip chord** | 110mm | Taper ratio ~0.55 |
| **Wing area** | ~32.5 dm² | Trapezoidal approximation |
| **Aspect ratio** | ~13.6 | High AR for thermal efficiency |
| **Sweep** | TBD (AI-optimized) | Slight sweep likely for CG |
| **Dihedral** | TBD (AI-optimized) | Continuous polyhedral possible |
| **Twist (washout)** | TBD (AI-optimized) | Continuously varying, not linear |

## Wing Panel Layout

6 panels total, 3 per half-wing, each ~350mm span.

```
 Tip ◄──── Panel 3 ────┬──── Panel 2 ────┬──── Panel 1 ────► Root
          (~350mm)      │    (~350mm)      │    (~350mm)
          Aileron       │  Aileron/Flap    │    Flap
          AG03-blend    │  AG-blend        │    AG24-blend
                        │                  │
                        joint              joint         fuselage
```

Each panel slides onto the carbon spar tube. Panels are unique - different airfoil
profile at every rib station, different chord (taper), different twist angle.

## Airfoils

| Station | Airfoil | Chord | Thickness | Reynolds (8 m/s) |
|---------|---------|-------|-----------|------------------|
| Root (0%) | AG24 | 200mm | ~9.0% (18mm) | ~107,000 |
| 25% span | AG24→AG09 blend | 177mm | ~9.1% | ~94,000 |
| 50% span | AG09 | 155mm | ~9.2% | ~83,000 |
| 75% span | AG09→AG03 blend | 132mm | ~8.8% | ~71,000 |
| Tip (100%) | AG03 | 110mm | ~8.4% | ~59,000 |

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
| **AUW** | 680g | 750-800g | 900g |
| **Wing loading** | 21 g/dm² | 23-25 g/dm² | 28 g/dm² |

Wing loading of 23-25 g/dm² is adequate for thermal soaring and casual F5J competition.
The heavier racing battery (155g vs typical 45g F5J packs) is the main weight driver.
Consider a lighter 2S 850mAh pack (~52g) as an alternative for pure gliding sessions.

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
- **H-stab**: ~400mm span, ~80mm chord, symmetric airfoil (NACA 0009 or flat)
- **V-stab**: ~120mm height, tapered chord
- **Elevator**: Full-span, 30-35% chord ratio
- **Rudder**: 30-35% chord ratio
- **Tail mount**: Printed socket bonded to boom end

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
