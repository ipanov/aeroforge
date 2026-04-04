# Component: LiPo 3S 1300mAh 75C Racing

## Description

3S 1300mAh 75C racing LiPo battery pack. This is a fixed off-the-shelf component from the owner's inventory. The model provides the outer envelope dimensions needed for fuselage battery bay sizing, CG calculation, and weight budget. Typical brands: Tattu, GNB, CNHL, Turnigy Graphene. The pack has XT60 connectors soldered on the power leads.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf battery pack |
| Chemistry | LiPo (Lithium Polymer) |
| Configuration | 3S (11.1V nominal, 12.6V full) |
| Capacity | 1300 mAh |
| C-rating | 75C continuous |
| Mass (pack only) | 155 g |
| Mass (with XT60 + leads) | 165 g |
| Length | 78.0 mm |
| Width | 38.0 mm |
| Height | 28.0 mm |
| Connector | XT60 male (soldered) |
| Wire gauge | 12 AWG silicone (~100 mm leads) |
| Balance plug | JST-XH 4-pin |

## Coordinate System

| Axis | Direction |
|------|-----------|
| Origin | Center of battery body |
| X | Length (78 mm) |
| Y | Width (38 mm) |
| Z | Height (28 mm) |
| +X | Wire exit end |
| +Z | Label face (top) |

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| wire_exit_pos | (39, 2.5, 9) | Positive power lead exit |
| wire_exit_neg | (39, -2.5, 9) | Negative power lead exit |
| balance_exit | (34, 19, -9) | Balance lead exit |
| bottom | (0, 0, -14) | Battery tray mounting |
| top | (0, 0, 14) | Top face reference |

## Assembly Notes

- Battery slides into the fuselage pod battery bay from below or from the side (removable hatch)
- Bay dimensions should be 80 x 40 x 30 mm minimum (2mm clearance each axis)
- CG position is critical: battery placement is the primary CG adjustment mechanism
- Fore-aft sliding in the bay allows +/- 10mm CG adjustment
- XT60 connector adds ~16mm to the +X end; total assembly length ~100mm with leads
- Secure with hook-and-loop strap to prevent shift during flight

## Weight Budget Impact

| Item | Mass |
|------|------|
| Battery pack | 155 g |
| XT60 + leads | 10 g |
| **Total** | **165 g** |

This is the single heaviest component (19-22% of AUW) and the primary CG ballast.

## Source Files

| File | Description |
|------|-------------|
| LiPo_3S_1300mAh_drawing.dxf | 2D technical drawing (3-view, 2:1 scale) |
| LiPo_3S_1300mAh_drawing.png | PNG render of drawing |
| LiPo_3S_1300mAh.step | 3D STEP model |
| renders/ | 4 standard views (isometric, front, top, right) |
