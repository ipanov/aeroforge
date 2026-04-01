# AeroForge F5J Sailplane - Bill of Materials

> Consolidated procurement document with final selections, prices, weights, and ordering links
> Date: 2026-04-01
> Status: DRAFT -- Subject to component availability verification before ordering
> Sources: MOTOR_OPTIONS.md, BATTERY_OPTIONS.md, CONTROLS_OPTIONS.md
> Branch: feat/hstab-complete-vstab-design

---

## Quick Summary

| Category | Option A (Recommended) | Option B (Budget) | Option C (Competition) |
|----------|----------------------|-------------------|----------------------|
| **Total electronics cost** | $173-205 | $101-122 | $271-310 |
| **Total electronics weight** | 194.8g | 161g | 186.8g |
| **Est. AUW** | ~805g | ~771g | ~797g |
| **Wing loading** | 19.4 g/dm2 | 18.5 g/dm2 | 19.2 g/dm2 |

All three options meet F5J competition requirements (AUW < 850g, wing loading < 22 g/dm2).

---

## 1. Propulsion System

### Recommended: Option A -- Best Value

| # | Component | Selection | Qty | Unit Weight | Total Weight | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-------------|-----------|------------|--------|
| P1 | Motor | Surpass Hobby 2216 880KV | 1 | 56g | 56g | $18-22 | $18-22 | [Amazon](https://www.amazon.com/s?k=Surpass+Hobby+2216+brushless+motor) / AliExpress |
| P2 | ESC | ZTW Spider 30A (3A BEC, brake) | 1 | 16g | 16g | $18-22 | $18-22 | [AliExpress](https://www.aliexpress.com/search?SearchText=ZTW+spider+30A+ESC) |
| P3 | Folding prop | Aeronaut CAM Carbon 11x6 | 1 | ~14g | 14g | $15-20 | $15-20 | [3DJake](https://www.3djake.com) / Amazon |
| P4 | Spinner | Aeronaut 30mm (3/4mm shaft) | 1 | ~5g | 5g | $8-12 | $8-12 | [3DJake](https://www.3djake.com) |
| | | | | | **91g** | | **$59-76** | |

**Performance:** ~178W at 3S, ~900g thrust, thrust/weight 1.13:1, ~62 deg climb angle, ~85-95m altitude in 10s.

### Alternative: Option B -- Budget (lightest)

| # | Component | Selection | Qty | Unit Weight | Total Weight | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-------------|-----------|------------|--------|
| P1 | Motor | Surpass Hobby 2206 1300KV | 1 | 32g | 32g | $10-14 | $10-14 | AliExpress |
| P2 | ESC | BLHeli_S 30A | 1 | 8g | 8g | $10-14 | $10-14 | AliExpress |
| P3 | Folding prop | Generic 9x5 + spinner | 1 | ~13g | 13g | $5-8 | $5-8 | AliExpress |
| | | | | | **53g** | | **$25-36** | |

**Performance:** ~144W, ~750g thrust, thrust/weight 0.94:1, ~48 deg climb angle, ~65-75m altitude in 10s. Marginal for F5J competition.

### Alternative: Option C -- Competition

| # | Component | Selection | Qty | Unit Weight | Total Weight | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-------------|-----------|------------|--------|
| P1 | Motor | Scorpion SII-2215-14 960KV | 1 | 55g | 55g | $40-50 | $40-50 | [Innov8tive](https://www.innov8tivedesigns.com) |
| P2 | ESC | T-Motor ESC 30A (5A switching BEC) | 1 | 15g | 15g | $35-40 | $35-40 | [GetFPV](https://www.getfpv.com) |
| P3 | Folding prop | Aeronaut CAM Carbon 10x7 + spinner | 1 | ~16g | 16g | $20-28 | $20-28 | [3DJake](https://www.3djake.com) |
| | | | | | **86g** | | **$95-118** | |

**Performance:** ~200W, ~950g thrust, thrust/weight 1.19:1, ~65 deg climb angle, ~90-100m altitude in 10s. Best climb performance.

---

## 2. Battery System

### Flight Battery (Standard)

| # | Component | Selection | Qty | Unit Weight | Total Weight | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-------------|-----------|------------|--------|
| B1 | Flight battery | OVONIC 3S 850mAh 80C XT30 | 2 | ~64g | 128g | $18.22 | $36.44 | [Amazon](https://www.amazon.com/s?k=OVONIC+3S+850mAh+XT30) |
| B2 | XT30 pigtail adapter | 20AWG, XT30 female to XT60 male | 2 | ~5g | 10g | $5-8 | $10-16 | Amazon / AliExpress |

**Subtotal:** 138g, $46.44-52.44

### Ballast Battery (Owner's Inventory -- NO PURCHASE NEEDED)

| # | Component | Selection | Qty | Unit Weight | Notes |
|---|-----------|-----------|-----|-------------|-------|
| B3 | Ballast battery | Owner's 3S 1300mAh 75C XT60 | 2 | ~165g each | Already owned. Use 1 for ballast, 1 as spare. Monitor health. |

### Charging

| # | Component | Selection | Qty | Unit Weight | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-----------|------------|--------|
| B4 | Balance charger | ISDT Q6 Plus | 1 | ~120g | $45-55 | $45-55 | Amazon |
| B5 | LiPo safe bag | Fireproof storage | 3 | -- | $6 | $18 | Amazon |

**Charging subtotal:** $63-73

### Alternative: Ultra-Light (Calm Air Competition)

| # | Component | Selection | Qty | Unit Weight | Unit Price | Source |
|---|-----------|-----------|-----|-------------|-----------|--------|
| B6 | Ultra-light battery | OVONIC 3S 650mAh 80C XT30 | 1 | ~54g | $12.99 | [Amazon](https://www.amazon.com/s?k=OVONIC+3S+650mAh+XT30) |

---

## 3. Controls Electronics

### Recommended: Option A -- Best Value

| # | Component | Selection | Qty | Unit Weight | Total Weight | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-------------|-----------|------------|--------|
| C1 | Tx module upgrade | iRangeX iRX6 multi-protocol | 1 | ~15g (in Tx) | -- | ~$5.50 | $5.50 | [Banggood](https://www.banggood.com/search/irangex-irx6.html) |
| C2 | Receiver | Flysky FS-iA6B (case removed) | 1 | 5.8g | 5.8g | ~$7.00 | $7.00 | [Banggood](https://www.banggood.com/search/flysky+fs-ia6b.html) |
| C3 | Wing servos | PTK 7308MG-D (8mm slim, digital) | 4 | 8.0g | 32g | ~$8-10 | $32-40 | AliExpress |
| C4 | Tail servos | JX PDI-1109MG (metal gear) | 2 | 10.0g | 20g | ~$4 | $8 | AliExpress |

**Controls subtotal:** 57.8g, $52.50-60.50

### Alternative: Option B -- Budget (No Module Swap)

| # | Component | Selection | Qty | Unit Weight | Total Weight | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-------------|-----------|------------|--------|
| C5 | Receiver | Flysky FS-R6B (AFHDS, stock-compatible) | 1 | 10g | 10g | ~$8 | $8 | [Banggood](https://www.banggood.com/search/flysky-fs-r6b.html) |
| C6 | Wing servos | JX PDI-1109MG | 4 | 10g | 40g | ~$4 | $16 | AliExpress |
| C7 | Tail servos | JX PDI-1109MG | 2 | 10g | 20g | ~$4 | $8 | AliExpress |

**Controls subtotal:** 70g, $32 (no module upgrade needed, but heavier and 12mm-wide servos are tight in thin wing panels)

---

## 4. Wiring, Connectors, and Hardware

| # | Component | Selection | Qty | Weight Est. | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-----------|------------|--------|
| W1 | Servo extensions 250mm | 3-pin JR, 250mm | 4 | ~2g ea | ~$1 | $4 | AliExpress |
| W2 | Servo extensions 450mm | 3-pin JR, 450mm | 4 | ~3g ea | ~$1.50 | $6 | AliExpress |
| W3 | Music wire 0.8mm | For Z-bends, 1m length | 1 | ~10g | ~$2 | $2 | Local hardware / AliExpress |
| W4 | Carbon rod 1.5mm | Elevator pushrod through boom, 400mm | 2 | ~2g ea | ~$1 | $2 | AliExpress |
| W5 | Kevlar thread | Rudder pull-pull, 1m | 1 | ~1g | ~$3 | $3 | AliExpress / soaring shops |
| W6 | Micro clevises 2mm | For pushrod connections | 8 | ~0.3g ea | ~$0.50 | $4 | AliExpress |
| W7 | Control horns (mini nylon) | For all control surfaces | 6 | ~0.5g ea | ~$0.30 | $2 | AliExpress |
| W8 | Heat shrink tubing 1.5mm | Pushrod guides | 0.5m | ~1g | ~$1 | $1 | AliExpress |
| W9 | PTFE tube 2.0mm OD / 1.2mm ID | Bowden pushrod guide | 0.5m | ~2g | ~$2 | $2 | AliExpress |
| W10 | Servo screws M2x6 | Mounting screws | 10 | ~0.3g ea | ~$0.10 | $1 | AliExpress |
| W11 | Nylon bolts M3x20 | Wing attachment | 4 | ~0.5g ea | ~$0.20 | $1 | AliExpress |
| W12 | CA glue (thin) | Structural bonding | 1 | -- | $5 | $5 | Local / Amazon |
| W13 | CA glue (medium/thick) | Gap filling | 1 | -- | $5 | $5 | Local / Amazon |
| W14 | CA accelerator | Quick set | 1 | -- | $4 | $4 | Local / Amazon |

**Wiring + hardware subtotal:** ~33g, $42

---

## 5. Structural Materials (Airframe)

### Carbon Fiber and Wood

| # | Component | Selection | Qty | Weight Est. | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-----------|------------|--------|
| S1 | Carbon tube 8mm OD x 7mm ID | Main wing spar, ~2600mm | 1 | ~85g | $8-12 | $8-12 | AliExpress / [HobbyKing](https://hobbyking.com) |
| S2 | Carbon tube 3mm OD x 2mm ID | H-Stab spar, 378mm | 1 | ~2.4g | $2-3 | $2-3 | AliExpress |
| S3 | Carbon rod 1.5mm | H-Stab rear spar (removed in v6 -- not needed) | 0 | -- | -- | -- | -- |
| S4 | Music wire 0.5mm | H-Stab hinge wire, 424mm | 1 | ~0.65g | ~$1 | $1 | AliExpress / local |
| S5 | Carbon tube 10-12mm OD | Tail boom (if pod-and-boom config) | 1 | ~20-25g | $5-8 | $5-8 | AliExpress / HobbyKing |
| S6 | Spruce strip 5x3mm | Rear wing spar, ~2600mm | 1 | ~18g | ~$2 | $2 | Local (Macedonia/Bulgaria) |
| S7 | Carbon rod 4mm | Fuselage longerons (4x), ~1200mm | 4 | ~8g ea | ~$2 | $8 | AliExpress |
| S8 | CF rod 1mm | Aileron stiffener (optional) | 2 | ~1g ea | ~$1 | $2 | AliExpress |

**Structural subtotal:** ~138g, $28-36

### 3D Printing Filament

| # | Component | Selection | Qty | Weight Needed | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|-------------|-----------|------------|--------|
| F1 | LW-PLA (white) | Wing skins, fuselage, empennage | 500g | ~500g | $30-45/kg | $15-23 | [3DJake](https://www.3djake.com) / Amazon.de |
| F2 | CF-PLA (black) | Ribs, bulkheads, internal structure | 200g | ~200g | $30-50/kg | $6-10 | Amazon / AliExpress |
| F3 | CF-PETG (black) | Servo mounts, motor mount, high-stress | 100g | ~100g | $35-55/kg | $4-6 | Amazon / AliExpress |
| F4 | PETG (solid) | Hinge sleeves, misc parts | 50g | ~50g | $18-28/kg | $1-2 | Amazon / AliExpress |
| F5 | Hardened steel nozzle 0.4mm | Required for CF filaments | 1 | -- | $10-15 | $10-15 | Amazon / Bambu |
| F6 | TPU 95A (optional) | Hinge seals, bumper pads | 50g | ~50g | $25-40/kg | $1-2 | Amazon / AliExpress |

**Filament subtotal:** ~900g total filament, $37-58

---

## 6. H-Stab Specific Components (from Design Consensus v6)

| # | Component | Selection | Qty | Weight | Unit Price | Total Price | Source |
|---|-----------|-----------|-----|--------|-----------|------------|--------|
| H1 | H-Stab_Left shell | LW-PLA vase mode 0.45mm | 1 | 6.89g | (filament) | -- | Printed |
| H2 | H-Stab_Right shell | LW-PLA vase mode 0.45mm (mirror) | 1 | 6.89g | (filament) | -- | Printed |
| H3 | Elevator_Left shell | LW-PLA vase mode 0.40mm | 1 | 5.05g | (filament) | -- | Printed |
| H4 | Elevator_Right shell | LW-PLA vase mode 0.40mm (mirror) | 1 | 5.05g | (filament) | -- | Printed |
| H5 | Main spar | 3mm CF tube, 378mm | 1 | 2.38g | (in S2) | -- | -- |
| H6 | Hinge wire | 0.5mm music wire, 424mm | 1 | 0.65g | (in S4) | -- | -- |
| H7 | PETG sleeves | 48x, 1.2/0.6/3mm | 48 | 0.10g | (filament) | -- | Printed |
| H8 | Elevator bridge joiner | CF-PLA U-channel | 1 | 0.60g | (filament) | -- | Printed |
| H9 | Gap seal | Mylar/tape (TBD) | 1 | ~0.18g | ~$1 | $1 | Mylar tape |
| | | | | **29.33g** | | | |

---

## 7. Grand Total -- Option A (Recommended Build)

### Weight Summary

| Category | Weight (g) | % of AUW |
|----------|-----------|----------|
| **Propulsion** (motor + ESC + prop + spinner) | 91 | 11.3% |
| **Flight battery** (OVONIC 3S 850mAh XT30) | 64 | 7.9% |
| **Controls electronics** (Rx + servos + module) | 57.8 | 7.2% |
| **Wiring + hardware** | 33 | 4.1% |
| **Wing structure** (printed + spar + ribs) | ~348 | 43.2% |
| **Fuselage** (printed + longerons) | ~100 | 12.4% |
| **Empennage** (H-Stab + V-Stab + rudder) | ~45 | 5.6% |
| **Tail boom** (if carbon tube) | ~22 | 2.7% |
| **Misc** (glue, tape, sealant) | ~10 | 1.2% |
| **Estimated AUW** | **~770g** | 100% |
| **Wing loading** | **18.5 g/dm2** | -- |

*With 1300mAh ballast battery (+101g): AUW ~871g, wing loading 20.9 g/dm2*

### Cost Summary

| Category | Cost (USD) |
|----------|-----------|
| **Propulsion** (motor + ESC + prop + spinner) | $59-76 |
| **Battery system** (2x flight + charger + accessories) | $109-125 |
| **Controls** (module + Rx + 6 servos) | $53-61 |
| **Wiring + hardware** | $42 |
| **Structural materials** (carbon, wood, rods) | $28-36 |
| **Filament** (LW-PLA, CF-PLA, CF-PETG, nozzle) | $37-58 |
| | |
| **Total investment** | **$328-398** |

### What You Already Own (No Purchase Needed)

| Item | Notes |
|------|-------|
| Turnigy 9X V2 transmitter | Stock AFHDS module; upgrade to iRangeX iRX6 ($5.50) recommended |
| 2x 3S 1300mAh 75C LiPo packs | XT60, ~165g each. Use for ballast/windy conditions |
| Bambu A1 / P1S printer access | Friends' printers, no purchase needed |

---

## 8. Cost Comparison by Build Option

| Category | Option A (Recommended) | Option B (Budget) | Option C (Competition) |
|----------|----------------------|-------------------|----------------------|
| Propulsion | $59-76 | $25-36 | $95-118 |
| Battery system | $109-125 | $109-125 | $109-125 |
| Controls | $53-61 | $32 | $143 |
| Wiring + hardware | $42 | $35 | $42 |
| Structural materials | $28-36 | $28-36 | $28-36 |
| Filament | $37-58 | $37-58 | $37-58 |
| **Total** | **$328-398** | **$266-322** | **$454-522** |
| **Electronics AUW** | ~194.8g | ~161g | ~186.8g |
| **Est. total AUW** | ~770g | ~736g | ~762g |

---

## 9. Ordering Priority

### Phase 1: Order Immediately (Long Lead Time)
These items have limited availability or long shipping times. Order first.

| Priority | Item | Source | Lead Time | Reason |
|----------|------|--------|-----------|--------|
| 1 | Aeronaut CAM Carbon prop (11x6 or 10x7) | 3DJake / Amazon | 5-14 days | Specialty item, limited stock |
| 2 | Aeronaut 30mm spinner | 3DJake | 5-14 days | Match with prop order |
| 3 | iRangeX iRX6 module | Banggood | 2-4 weeks | Must test binding before servo order |
| 4 | PTK 7308MG-D servos (4x) | AliExpress | 2-4 weeks | Specialty 8mm slim servos |
| 5 | Flysky FS-iA6B receiver | Banggood | 2-3 weeks | Match with module |

### Phase 2: Order with Standard Shipping
| Priority | Item | Source | Lead Time | Reason |
|----------|------|--------|-----------|--------|
| 6 | OVONIC 3S 850mAh 80C XT30 (2x) | Amazon | 3-7 days | Standard Amazon delivery |
| 7 | Surpass Hobby 2216 880KV motor | Amazon / AliExpress | 3-14 days | Verify shaft = 4mm for prop adapter |
| 8 | ZTW Spider 30A ESC | AliExpress | 2-4 weeks | Sailplane-specific ESC |
| 9 | Carbon tube 8mm OD (2600mm) | AliExpress | 3-4 weeks | Main spar -- verify ID clearance |
| 10 | Carbon tube 3mm OD x 2mm ID | AliExpress | 3-4 weeks | H-Stab spar |

### Phase 3: Order from Local/EU Sources
| Priority | Item | Source | Lead Time | Reason |
|----------|------|--------|-----------|--------|
| 11 | LW-PLA filament (1 roll) | 3DJake / Amazon.de | 3-5 days | EU warehouse, fast to Bulgaria |
| 12 | CF-PLA filament | Amazon.de / AliExpress | 5-14 days | |
| 13 | CF-PETG filament | Amazon.de / AliExpress | 5-14 days | |
| 14 | Hardened steel nozzle 0.4mm | Amazon | 3-7 days | Required before printing CF filament |
| 15 | ISDT Q6 Plus charger | Amazon | 3-7 days | |

### Phase 4: Hardware and Misc (Local + AliExpress)
| Priority | Item | Source | Lead Time | Reason |
|----------|------|--------|-----------|--------|
| 16 | JX PDI-1109MG servos (2x tail) | AliExpress | 2-4 weeks | |
| 17 | Servo extensions (4x 250mm, 4x 450mm) | AliExpress | 2-4 weeks | |
| 18 | Clevises, horns, wire, PTFE tube | AliExpress | 2-4 weeks | Order in one batch |
| 19 | Spruce strip 5x3mm | Local (Bulgaria/Macedonia) | Same day | Wood supplier |
| 20 | CA glue (thin + medium) | Local / Amazon | 1-7 days | |

---

## 10. Critical Compatibility Checks

Before ordering, verify these compatibility items:

| Check | Item | Verify |
|-------|------|--------|
| **Shaft size** | Motor shaft vs prop hub adapter | Surpass 2216 has 4mm shaft. Aeronaut spinner must include 4mm adapter. |
| **ESC protocol** | ZTW Spider brake compatibility | Configure brake ON for folding prop via programming card. |
| **Connector chain** | Battery XT30 -> pigtail XT60 -> ESC XT60 | ESC must have XT60 input, pigtail bridges XT30 battery to XT60 ESC. |
| **BEC current** | ZTW Spider 30A has 3A linear BEC | Adequate for analog servos. If using PTK 7308MG-D digital, consider ESC with 5A switching BEC (T-Motor or add external UBEC). |
| **Tx module fit** | iRangeX iRX6 fits Turnigy 9X JR bay | Direct plug-in, confirmed compatible. |
| **Servo dimensions** | PTK 7308MG-D: 23.5 x 8.0 x 16.8mm | Must fit in wing panel at 35% chord position. Verify airfoil internal height > 17mm. |
| **Battery bay** | OVONIC 850mAh: ~68x32x22mm | Must fit in 82x42x32mm battery bay with padding. |

---

## 11. Spare Parts Recommendation

| Item | Qty | Cost | Reason |
|------|-----|------|--------|
| Spare prop blades (Aeronaut 11x6) | 2 sets | $30-40 | Props break on landing |
| Spare servo (PTK 7308MG-D) | 1 | $8-10 | Wing servo replacement |
| Spare servo (JX PDI-1109MG) | 1 | $4 | Tail servo replacement |
| Spare flight battery | (already 2x) | -- | Second OVONIC 850mAh is the spare |
| Spare motor mount screws M3 | 5 | $1 | Vibration loosens screws |
| Spare XT30 connectors + 20AWG wire | 5 pair | $5 | For repairs and adapters |

**Spare parts budget:** ~$48-60

---

## 12. Bulgarian/EU Sourcing Summary

Per CLAUDE.md rules: Bulgaria first, then EU, AliExpress last.

| Source | Use For | Shipping to BG | Notes |
|--------|---------|---------------|-------|
| **Local shops** (hobbyzone.bg, modelkom.bg) | Check first for servos, wire, glue | Same day | Limited RC sailplane stock |
| **3DJake.com** | Aeronaut props, LW-PLA filament, PETG | 3-5 days | EU warehouse, free ship > EUR 29 |
| **Amazon.de** | OVONIC batteries, nozzle, charger | 3-7 days | Prime shipping to BG |
| **Amazon.com** | Motors, ESCs (wider selection) | 7-14 days | Some items ship to BG |
| **Banggood** | Flysky receivers, iRangeX module | 1-2 weeks priority | Good Flysky stock |
| **AliExpress** | Servos, carbon tube, clevises, hardware | 2-4 weeks standard | Cheapest but slowest |
| **HobbyKing EU** | Carbon tube, general hardware | 5-7 days | EU warehouse |
| **Innov8tive Designs** | Scorpion motors (Option C only) | 7-10 days (US) | Premium, only if Option C selected |
| **Hyperflight UK** | Competition sailplane parts, KST servos | 5-7 days | Post-Brexit may have customs |

---

## Revision History

| Date | Author | Description |
|------|--------|-------------|
| 2026-04-01 | AeroForge Procurement Team | Initial BOM compiled from MOTOR_OPTIONS.md, BATTERY_OPTIONS.md, CONTROLS_OPTIONS.md |
