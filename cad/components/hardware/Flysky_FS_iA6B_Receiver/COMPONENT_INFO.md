# Component: Flysky FS-iA6B Receiver

## Description

Flysky FS-iA6B 6-channel receiver, compatible with the Turnigy 9X V2 transmitter via AFHDS 2A protocol. This is a fixed off-the-shelf component from the owner's inventory. The model provides a dimensionally accurate body envelope for fuselage bay sizing, CG calculation, and assembly clearance checks. Features include a single wire antenna (165mm), 6 servo output pin headers (3-pin), and a bind button on top.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf electronic component |
| Model | Flysky FS-iA6B |
| Protocol | AFHDS 2A |
| Channels | 6 |
| Mass | 18 g |
| Length | 47.2 mm (body only) |
| Width | 26.2 mm |
| Height | 15.0 mm |
| Antenna | Single wire, 165 mm |
| Voltage | 4.0-6.5 V DC |
| Connector | Standard 3-pin servo headers (S/+/GND) |

## Coordinate System

| Axis | Direction |
|------|-----------|
| Origin | Center of receiver body |
| X | Length (47.2 mm) |
| Y | Width (26.2 mm) |
| Z | Height (15.0 mm) |
| +X | Antenna exit end |
| -Y | Servo pin header side |
| +Z | Top (bind button) |

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| bottom | (0, 0, -7.5) | Mounting in receiver bay |
| top | (0, 0, 7.5) | Top face reference |
| antenna | (23.6, 0, 4.5) | Antenna wire exit point |
| pins | (0, -13.1, 0) | Servo header center |

## Assembly Notes

- Receiver sits in a padded bay inside the fuselage pod, secured with foam or hook-and-loop
- Antenna wire exits through a PTFE tube in the fuselage boom (avoids carbon shielding)
- Servo wires route from pin headers through internal fuselage channels
- Keep minimum 30mm clearance from motor/ESC to avoid RF interference
- Bind button must remain accessible (removable hatch or slot in fuselage)

## Source Files

| File | Description |
|------|-------------|
| Flysky_FS_iA6B_Receiver_drawing.dxf | 2D technical drawing (3-view, 2:1 scale) |
| Flysky_FS_iA6B_Receiver_drawing.png | PNG render of drawing |
| Flysky_FS_iA6B_Receiver.step | 3D STEP model |
| renders/ | 4 standard views (isometric, front, top, right) |
