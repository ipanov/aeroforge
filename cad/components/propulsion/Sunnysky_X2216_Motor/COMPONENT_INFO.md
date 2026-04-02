# Component: Sunnysky X2216 880KV Motor

## Description

Sunnysky X2216 880KV brushless outrunner motor for electric sailplane propulsion. Lightweight aluminum construction with 4mm steel shaft. Suitable for 2-3S LiPo operation on sailplanes in the 700-1000g AUW range.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf brushless outrunner |
| Manufacturer | Sunnysky |
| Model | X2216 880KV |
| Mass | 56 g |
| KV rating | 880 RPM/V |
| Max current | 18 A |
| Max power | 250 W |
| Input voltage | 2-3S LiPo (7.4-11.1V) |
| Stator diameter | 28.0 mm |
| Bell (can) diameter | 27.5 mm |
| Bell height | 26.0 mm |
| Shaft diameter | 4.0 mm |
| Shaft protrusion | 14.0 mm |
| Overall length (with shaft) | ~42.5 mm |
| Mounting | 4x M3 on 19mm bolt circle (cross pattern) |
| X-mount plate | 25 x 25 x 2 mm |
| Prop adapter | M5 collet type |

## Coordinate System

- Origin = center of mounting face (back plate rear)
- Z = motor axis, +Z toward propeller
- X-mount plate at Z < 0 (rear)
- Shaft tip at Z = +42.5mm

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| mount_face | (0, 0, -2) | Firewall attachment |
| shaft_tip | (0, 0, 42.5) | Propeller mounting |
| shaft_prop | (0, 0, 30.5) | Prop adapter position |
| mount_fr | (9.5, 0, -1) | Front-right M3 hole |
| mount_fl | (-9.5, 0, -1) | Front-left M3 hole |
| mount_br | (0, 9.5, -1) | Back-right M3 hole |
| mount_bl | (0, -9.5, -1) | Back-left M3 hole |

## Assembly Notes

- Motor mounts to the fuselage nose firewall via the X-mount plate
- 4x M3 bolts through the cross-pattern mounting holes
- Propeller attaches to the 4mm shaft via an M5 collet adapter
- 3 motor wires connect to ESC (any order, swap 2 to reverse rotation)
- Ensure adequate cooling airflow around the bell

## Procurement

- Source: AliExpress / HobbyKing / Banggood
- Price: ~$12-15 USD
- Lead time: 2-4 weeks (AliExpress)
