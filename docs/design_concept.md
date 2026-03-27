# AeroForge Design Concept

## Design Decision: 1.5m Wingspan, Hybrid Construction

### Why 1.5m?

The optimal wingspan for a 3D-printed RC sailplane is determined by the intersection of:
- **Material limits**: PLA/LW-PLA has ~10-20x worse specific strength than carbon composite
- **Weight budget**: 500-600g AUW target with ~300-400g airframe budget
- **Print bed**: Bambu A1/P1S bed is 256x256x256mm, constraining panel size
- **Thermal performance**: Need wing loading 17-25 g/dm² for real thermalling

### Size Analysis

| Wingspan | Construction | AUW (g) | Wing Loading (g/dm²) | Verdict |
|----------|-------------|---------|---------------------|---------|
| 1.0m | Fully printed | 380-450 | 22-28 | Too small for thermals |
| 1.2m | Fully printed LW-PLA | 430-510 | 20-25 | Maximum for all-printed |
| **1.5m** | **LW-PLA shell + carbon spar** | **500-600** | **17-22** | **Sweet spot** |
| 1.8m | Printed ribs + carbon + film | 470-580 | 13-16 | Stretch goal |
| 2.0m+ | Hybrid only | 520-650+ | 12-15 | Ambitious, diminishing returns |

### Construction: Printed Shell + Carbon Tube Spar

- **Main spar**: 12mm OD pultruded carbon tube carry-through
- **Wing skins**: 0.5-0.6mm LW-PLA walls (spiral vase or double perimeter)
- **Ribs/formers**: 0.8mm PLA (higher strength at stress points)
- **Servo mounts, wing joiner, motor mount**: Standard PLA or PETG (need strength)
- **Panel count**: 3 per half-wing (~250mm each, fits print bed)

### Weight Budget

| Component | Weight (g) |
|-----------|-----------|
| Servos (6x 9g) | 54 |
| Motor + prop | 50 |
| ESC | 10 |
| Receiver | 10 |
| Battery (3S 500mAh) | 45 |
| Wiring/connectors | 20 |
| **Electronics total** | **~189** |
| Wing (LW-PLA + carbon) | 160-200 |
| Fuselage pod | 50-70 |
| Tail boom (carbon) | 15-20 |
| Empennage | 30-40 |
| **Airframe total** | **~280-330** |
| **AUW** | **~470-520** |

### Material Properties

| Material | Density (g/cm³) | Tensile (MPa) | Use |
|----------|----------------|---------------|-----|
| PLA | 1.24 | 50-65 | Structural nodes, mounts |
| LW-PLA (50% foam) | 0.55-0.65 | 20-35 | Wing skins, fairings |
| PETG | 1.27 | 50-75 | Impact-prone parts |
| Carbon tube | 1.55 | 600-1500 | Main spar, tail boom |

### Top-Level Assembly Hierarchy

```
Sailplane (top assembly)
├── Wing Assembly
│   ├── Center Panel Assembly
│   │   ├── Ribs (5x CustomComponent, LW-PLA)
│   │   ├── Main Spar Section (OffShelf, carbon tube 12mm)
│   │   ├── Rear Spar Section (OffShelf, carbon rod 4mm)
│   │   ├── Leading Edge Skin (CustomComponent, LW-PLA)
│   │   ├── Top Skin (CustomComponent, LW-PLA)
│   │   ├── Bottom Skin (CustomComponent, LW-PLA)
│   │   ├── Flap Hinge Assembly
│   │   │   ├── Hinge Pin (OffShelf, steel 1.5mm)
│   │   │   ├── Hinge Brackets x2 (CustomComponent, PLA)
│   │   │   └── Flap Surface (CustomComponent, LW-PLA)
│   │   ├── Aileron Hinge Assembly (same pattern)
│   │   ├── Servo Mount - Flap (CustomComponent, PLA)
│   │   ├── Servo Mount - Aileron (CustomComponent, PLA)
│   │   ├── Servo - Flap (OffShelf, 9g)
│   │   ├── Servo - Aileron (OffShelf, 9g)
│   │   ├── Control Horn - Flap (OffShelf/Custom)
│   │   ├── Control Horn - Aileron (OffShelf/Custom)
│   │   ├── Pushrod - Flap (OffShelf, steel wire)
│   │   └── Pushrod - Aileron (OffShelf, steel wire)
│   ├── Left Tip Panel Assembly (similar structure, no flap)
│   ├── Right Tip Panel Assembly (mirror)
│   └── Wing Joiner (CustomComponent, PLA/PETG)
│
├── Fuselage Assembly
│   ├── Pod Assembly
│   │   ├── Nose Cone (CustomComponent, PLA)
│   │   ├── Motor Mount (CustomComponent, PLA/PETG)
│   │   ├── Motor (OffShelf)
│   │   ├── Prop + Spinner (OffShelf)
│   │   ├── ESC (OffShelf)
│   │   ├── Battery Tray (CustomComponent, PLA)
│   │   ├── Battery (OffShelf)
│   │   ├── Receiver (OffShelf)
│   │   ├── Wing Saddle (CustomComponent, PLA)
│   │   ├── Wing Hold-Down (CustomComponent, screws)
│   │   └── Pod Shell (CustomComponent, LW-PLA)
│   └── Tail Boom (OffShelf, carbon tube 10-12mm)
│
└── Empennage Assembly
    ├── Horizontal Stabilizer
    │   ├── H-Stab Structure (CustomComponent, LW-PLA)
    │   ├── Elevator (CustomComponent, LW-PLA)
    │   ├── Elevator Hinge (OffShelf, pin)
    │   ├── Elevator Servo (OffShelf, 9g)
    │   └── Elevator Pushrod (OffShelf)
    ├── Vertical Stabilizer
    │   ├── V-Stab Structure (CustomComponent, LW-PLA)
    │   ├── Rudder (CustomComponent, LW-PLA)
    │   ├── Rudder Hinge (OffShelf, pin)
    │   ├── Rudder Servo (OffShelf, 9g)
    │   └── Rudder Pushrod (OffShelf)
    └── Boom Mount (CustomComponent, PLA)

Hardware (throughout):
├── M2 Screws (various lengths)
├── M2 Nuts
├── M3 Screws (wing hold-down)
├── CA Hinges
├── Clevis connectors
└── Heat-shrink / zip ties
```

### Flight Modes (Turnigy 9X - 9 channels)

| Mode | Ailerons | Flaps | Elevator | Rudder | Notes |
|------|----------|-------|----------|--------|-------|
| Launch | Reflex (+2°) | Reflex (+2°) | Slight down | Free | Max speed climb |
| Cruise | Neutral | Neutral | Neutral | Free | Normal flying |
| Speed | Slight reflex | Neutral | Neutral | Free | Penetration |
| Thermal | Slight down (-2°) | Camber (-5°) | Compensate | Free | Min sink |
| Landing (Crow) | Up (+45°) | Down (-60°) | Compensate | Free | Drag braking |

### Airfoil Selection

Primary candidates:
- **AG09**: Excellent thermal performance, 9.2% thick, proven in competition sailplanes
- **RG-15**: All-round performer, 8.9% thick, proven in F3B/F3J
- **AG35**: Better for heavier models, 9.5% thick

For 1.5m span with 180mm chord, 9-10% thickness = 16-18mm internal height.
12mm spar fits comfortably with clearance for skin thickness.

### Next Steps (Bottom-Up Build Order)

1. Off-the-shelf component models (servos, motor, battery - from datasheets)
2. Airfoil generator (import real coordinate data, not NACA approximations)
3. Wing rib generator (parametric, with spar holes and lightening cutouts)
4. Wing panel assembly (ribs + spar + skin)
5. Fuselage pod (motor bay, battery bay, wing saddle)
6. Empennage (H-stab, V-stab, control surfaces)
7. Full assembly with CG calculation
8. FEM analysis (wing root bending, spar stress)
9. CFD analysis (lift/drag at cruise speed)
10. Print optimization (orientation, support, panel splitting)
