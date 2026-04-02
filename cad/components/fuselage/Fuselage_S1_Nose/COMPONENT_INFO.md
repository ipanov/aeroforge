# Component: Fuselage_S1_Nose

## Description

The nose section (S1) of the AeroForge integrated fuselage, spanning X=0 to X=260mm.
This is the forward-most structural section, housing the motor, ESC, battery, and receiver.
It transitions from a 32mm circular spinner base through the maximum cross-section (50x44mm
at the battery bay) to a 38x34mm egg-shaped joint face at the wing leading edge station.

The section prints as **left and right halves** (split along the vertical centerline plane)
to eliminate overhang issues. Halves are bonded with thin CA along the vertical seam.

## Specifications

| Parameter | Value | Source |
|-----------|-------|--------|
| Overall length | 260mm (X=0 to X=260) | DESIGN_CONSENSUS v2 |
| Max width | 50mm at X=150 | Cross-section schedule |
| Max height | 44mm at X=150 | Cross-section schedule |
| Nose diameter | 32mm at X=30 (spinner base) | Cross-section schedule |
| Joint face | 38mm W x 34mm H at X=260 | Cross-section schedule |
| Shell wall (LW-PLA) | 0.6mm (X=90-260) | Structural review M3 |
| Shell wall (PETG) | 0.6mm (X=30-90) | Structural review M3 |
| Shell mass | ~12g (LW-PLA + PETG zones) | Shell mass calc |
| Internal structure mass | ~13g (motor mount, tray, bulkheads) | Structural review |
| Total mass (excl. longerons) | ~25g | Estimated |
| Longeron channels | 4x 2.5mm ID sleeves for 2mm CF rods | Structural review M1 |

## Internal Layout

| Zone (X range) | Function | Internal WxH | Contents |
|----------------|----------|-------------|----------|
| 0-10mm | Spinner tip | -- | Separate ogive nose cone insert |
| 10-30mm | Spinner cone | -- | Ogive profile, 32mm dia at base |
| 30-70mm | Motor bay | 29x29mm | CF-PETG motor mount ring, 28mm motor bore |
| 70-90mm | ESC bay | 34x31mm | 45x25x12mm ESC, PETG shell |
| 90-120mm | Battery fwd | 40x35mm | CG adjustment range start |
| 120-180mm | Battery main | 44x38mm | 78x38x28mm LiPo, MAX section at X=150 |
| 180-210mm | Receiver bay | 42x36mm | 52x35x15mm Turnigy 9X V2 receiver |
| 210-250mm | Transition | 34x29mm | Wiring routing, taper to joint |
| 250-260mm | Joint face | 32x28mm | Interlocking teeth + 2x alignment dowels |

## Key Features

### Motor Mount (M3, M5)
- CF-PETG motor mount ring: 35mm OD, 28mm bore, 30mm long
- 4x M3 holes on 16mm PCD for motor attachment
- PETG shell from X=30-90mm for thermal protection (motor can reach 80C)

### Battery Tray (CG Adjustment)
- M3 nylon threaded rod allows +/-25mm fore-aft battery position
- Forward limit (X=120mm): CG at ~28% MAC (safe for first flights)
- Aft limit (X=170mm): CG at ~34% MAC (efficient cruise)

### Access Hatch
- Location: LEFT side, X=80 to X=210mm
- Opening: 130mm x 25mm
- Retention: 3x neodymium magnets (3mm x 1mm disc)
- Access to: ESC, battery, receiver, CG adjustment

### Longeron Layout (4x 2mm CF rods)
| Station | Top-R | Top-L | Bot-R | Bot-L | Spacing WxH |
|---------|-------|-------|-------|-------|-------------|
| X=40 | +9,+9 | -9,+9 | +9,-9 | -9,-9 | 18x18mm |
| X=150 | +18,+16 | -18,+16 | +18,-16 | -18,-16 | 36x32mm |
| X=260 | +12,+10 | -12,+10 | +12,-10 | -12,-10 | 24x20mm |

### Joint Face (X=260)
- Interlocking teeth: 1.5mm depth, 3mm pitch (M4)
- 2x 2mm steel alignment dowels
- 4x longeron sleeves (15mm depth into section)
- Mates with S2 Wing Section

## Manufacturing

- **Print method**: Left/right halves, flat on bed (M2)
- **Material**: LW-PLA 0.6mm shell (X=90-260), PETG 0.6mm shell (X=30-90)
- **Motor mount**: CF-PETG, printed separately, bonded into shell
- **Temperature**: LW-PLA at 230C, PETG at 240C
- **Bed size**: Each half ~260mm L x 25mm W x 44mm H -- fits Bambu A1/P1S
- **Post-processing**: Bond halves with thin CA, sand seam line

## Connections

- **Forward**: Spinner nose cone insert (press-fit + CA)
- **Aft**: S2 Wing Section at X=260 (longeron slip joint + interlocking teeth + CA)
- **Motor**: CF-PETG ring, bonded into shell at X=30-70
- **Longerons**: 4x 2mm CF rods pass through, glued at motor mount bulkhead

## Drawing Approval

- Date: 2026-04-02
- Status: FOR APPROVAL
- Drawing file: Fuselage_S1_Nose_drawing.dxf
- Revision: v1
