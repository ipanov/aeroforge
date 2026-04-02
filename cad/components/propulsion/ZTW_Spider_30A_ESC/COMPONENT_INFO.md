# Component: ZTW Spider 30A ESC

## Description

ZTW Spider 30A electronic speed controller with integrated 5A switching BEC. Compact heat-shrink wrapped PCB design suitable for sailplane and sport electric applications. Provides reliable motor control and regulated 5V power for servos and receiver.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf ESC with switching BEC |
| Manufacturer | ZTW |
| Model | Spider 30A |
| Mass | 16 g (with wires) |
| Current rating | 30 A continuous |
| Burst current | 40 A (10s) |
| BEC output | 5V / 5A switching |
| Input voltage | 2-4S LiPo (7.4-14.8V) |
| Body length | 45.0 mm |
| Body width | 24.0 mm |
| Body height | 11.0 mm |
| Motor wires | 3x 200mm (silicone) |
| Battery wires | 150mm with XT60 connector |
| Signal wire | 200mm with JR/Futaba connector |
| Programming | Yes (via transmitter stick) |

## Coordinate System

- Origin = center of PCB body
- X = length axis (motor wires exit +X, battery/signal exit -X)
- Y = width axis
- Z = thickness axis

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| battery_wire | (-22.5, 0, 0) | Battery XT60 connection |
| signal_wire | (-22.5, 8, 0) | Receiver signal input |
| motor_wire_a | (22.5, -5, 0) | Motor phase A |
| motor_wire_b | (22.5, 0, 0) | Motor phase B |
| motor_wire_c | (22.5, 5, 0) | Motor phase C |
| mount_top | (0, 0, 5.5) | Top face (tape/strap mount) |
| mount_bottom | (0, 0, -5.5) | Bottom face mount |

## Assembly Notes

- ESC mounts inside the fuselage pod via double-sided tape or Velcro strap
- Position near the CG to minimize wiring length
- Battery XT60 connects to battery lead
- Motor wires connect to Sunnysky X2216 (any order; swap 2 to reverse)
- Signal wire connects to receiver throttle channel
- BEC powers all servos and receiver (no separate BEC needed)
- Ensure heat dissipation: do not fully enclose in foam

## Procurement

- Source: AliExpress / HobbyKing / Banggood
- Price: ~$8-12 USD
- Lead time: 2-4 weeks (AliExpress)
