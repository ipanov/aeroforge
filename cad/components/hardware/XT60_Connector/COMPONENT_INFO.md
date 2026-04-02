# Component: XT60 Male Connector

## Description

Amass XT60 male connector (battery side). This is the standard power connector for the 3S LiPo battery, soldered onto the battery's 12AWG power leads. The model is imported from a KiCad/Amass reference STEP file for accurate geometry. The XT60 features a keyed shape (chamfered corner) to prevent reverse polarity connection, and two 3.5mm gold-plated bullet pins.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf connector |
| Model | Amass XT60 Male |
| Mass | ~5 g (pair) |
| Length (depth) | 16.0 mm |
| Width | 8.0 mm |
| Height | 15.8 mm |
| Pin type | 3.5 mm gold-plated bullet |
| Pin spacing | 7.2 mm center-to-center |
| Current rating | 60A continuous |
| Body material | Nylon (PA) |
| Body color | Yellow (standard) |

## Coordinate System

| Axis | Direction |
|------|-----------|
| Origin | Center of mating face |
| X | Longitudinal (pin direction) |
| +X | Toward rear (solder cups / wire attachment) |
| -X | Toward front (pins protrude) |

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| mating_face | (0, 0, 0) | Mating with female XT60 |
| solder_positive | (depth, +3.6, 0) | Red wire connection |
| solder_negative | (depth, -3.6, 0) | Black wire connection |
| rear_face | (depth, 0, 0) | General rear attachment |

## Assembly Notes

- The XT60 is pre-soldered to the battery pack's power leads
- In the fuselage, the female XT60 is mounted on a bracket or wired to the ESC
- The keyed shape prevents reverse polarity -- the chamfered corner only fits one way
- The connector extends ~16mm beyond the battery pack body
- For fuselage routing, allow a minimum 10mm radius bend in the 12AWG leads
- The mating force is ~3-5 N; the fuselage mount must resist this pull-out force

## Source Files

| File | Description |
|------|-------------|
| XT60_Connector_drawing.dxf | 2D technical drawing (3-view, 5:1 scale) |
| XT60_Connector_drawing.png | PNG render of drawing |
| XT60_Connector.step | 3D STEP model (from KiCad reference) |
| renders/ | 4 standard views (isometric, front, top, right) |
