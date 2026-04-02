# Component: Folding Prop 11x6

## Description

Aeronaut CAM Carbon 11x6 folding propeller for F5J electric sailplane. Two carbon fiber blades with computer-optimized airfoil sections, mounted on a yoke-type aluminum hub with 4mm shaft adapter. Blades fold flat against the fuselage when the motor stops (requires ESC brake function).

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf folding propeller |
| Manufacturer | Aeronaut (Germany) |
| Model | CAM Carbon 11x6 |
| Mass | 14 g (both blades + hub hardware) |
| Diameter | 279mm (11 inches) |
| Pitch | 152mm (6 inches) |
| Blade length | 139.7mm (from hub center) |
| Blade count | 2 |
| Blade material | Carbon fiber (CAM-optimized) |
| Blade max width | ~22mm |
| Blade tip width | ~8mm |
| Hub type | Standard yoke, aluminum |
| Hub dimensions | 22 x 8 x 12 mm |
| Yoke spacing | 8mm |
| Shaft adapter | 4mm (fits Sunnysky X2216) |
| Rotation | CW (viewed from front) |
| Twist | 27 deg (root) to 11 deg (tip) |

## Coordinate System

- Origin = center of hub (blade pivot point)
- Z = motor axis, +Z toward pilot
- X = blade span axis when deployed
- Y = perpendicular to blade span

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| hub_center | (0, 0, 0) | Hub center / pivot point |
| hub_rear | (0, 0, -6) | Rear face (mounts against spinner) |
| blade_tip_a | (139.7, 0, 0) | Blade A tip |
| blade_tip_b | (-139.7, 0, 0) | Blade B tip |

## Assembly Notes

- Propeller mounts on motor shaft via M5 collet prop adapter
- Spinner covers the hub from the front
- Blades fold backward (toward tail) when motor stops
- ESC brake function MUST be enabled for proper folding
- Blade rotation: clockwise viewed from front
- Static thrust with Sunnysky X2216 880KV on 3S: ~1000g

## Performance (with Sunnysky X2216 880KV on 3S)

| Parameter | Value |
|-----------|-------|
| Static thrust | ~1000g |
| Current draw | ~16A |
| Power | ~178W |
| Thrust/weight ratio | 1.25:1 (at 800g AUW) |
| Recommended KV range | 810-1050 |

## Procurement

- Source: 3DJake.com (EU), Amazon.de
- Price: ~$15-18 USD / ~15 EUR (blades only)
- Lead time: 3-5 days (3DJake EU warehouse)
- Spare blades recommended: 2-3 sets
