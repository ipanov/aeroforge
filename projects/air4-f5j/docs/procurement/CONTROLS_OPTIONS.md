# Controls Procurement Options - Receiver, Servos, Connectors

**Date:** 2026-04-01
**Status:** Research complete, awaiting selection

## Aircraft Requirements

| Parameter | Value |
|-----------|-------|
| AUW target | 750-850g |
| Battery | 3S LiPo (BEC provides 5V to Rx + servos) |
| Transmitter | Turnigy 9X V2 (stock Flysky AFHDS module) |
| Channels needed | 6 minimum (aileron R, aileron L, elevator, rudder, throttle, flap mix) |
| Wing servos | 4 (2x flap + 2x aileron), mounted inside thin wing panels |
| Tail servos | 2 (elevator + rudder), mounted in fuselage servo bay |
| Wing airfoil thickness | 6.4-8.6% = 7-18mm internal height |

---

## 1. Receiver Options

### Protocol Compatibility

| Protocol | Turnigy 9X Stock Module | With Module Upgrade |
|----------|------------------------|---------------------|
| **AFHDS** (original) | Direct compatible | N/A |
| **AFHDS 2A** | NOT compatible | Requires iRangeX module or Flysky FS-i6X module swap |
| **AFHDS 3** | NOT compatible | Requires full module replacement |

The stock Turnigy 9X V2 uses the original **AFHDS** protocol. To use the much lighter AFHDS 2A receivers, a module swap is required. The JR-style module bay makes this straightforward.

### Module Upgrade Path

| Module | Protocols | Price | Source |
|--------|-----------|-------|--------|
| **iRangeX iRX6** | AFHDS 2A, FrSky, DSM2, Futaba, +more | ~$5.50 | [Banggood](https://www.banggood.com/search/irangex-irx6.html) |
| **Flysky FS-i6X module** | AFHDS 2A only | ~$15 | Banggood/AliExpress |

The iRangeX iRX6 multi-protocol module ($5.50 on Banggood) is a no-brainer upgrade. It unlocks AFHDS 2A receivers (which are smaller, lighter, and have better range with diversity antennas) plus FrSky, Spektrum, and Futaba protocols. It plugs directly into the JR module bay on the back of the Turnigy 9X.

### Tier 1: Budget (under $8)

#### Option A: Flysky FS-R6B (AFHDS, stock-compatible)

| Field | Value |
|-------|-------|
| **Name** | Flysky FS-R6B |
| **Protocol** | AFHDS (original) |
| **Channels** | 6 |
| **Weight** | ~10g |
| **Dimensions** | 47 x 22 x 12 mm |
| **Price** | ~$7-11 (~EUR 6-10) |
| **Compatible with Turnigy 9X?** | YES (stock module) |
| **Source** | [Banggood](https://www.banggood.com/search/flysky-fs-r6b.html), AliExpress |
| **Notes** | Direct bind to stock 9X. No module swap needed. 6ch sufficient for full-house. Heavier than AFHDS 2A options. |

**Verdict:** Best budget option if keeping stock module. Saves 8g vs stock Rx. Only 6ch but sufficient for this sailplane.

#### Option B: Flysky FS-iA6 (AFHDS 2A, requires module)

| Field | Value |
|-------|-------|
| **Name** | Flysky FS-iA6 |
| **Protocol** | AFHDS 2A |
| **Channels** | 6 |
| **Weight** | ~8g |
| **Dimensions** | 40 x 22 x 10 mm |
| **Price** | ~$4.80 (~EUR 4.50) |
| **Compatible with Turnigy 9X?** | YES with iRangeX module (+$5.50) |
| **Source** | [Banggood](https://www.banggood.com/search/flysky-fs-ia6.html), AliExpress |
| **Notes** | Lighter than FS-R6B. Requires module swap. Single antenna. No telemetry. |

### Tier 2: Mainstream ($8-20)

#### Option A: Flysky FS-iA6B (AFHDS 2A, requires module) -- RECOMMENDED

| Field | Value |
|-------|-------|
| **Name** | Flysky FS-iA6B |
| **Protocol** | AFHDS 2A |
| **Channels** | 6 (PWM) / 10 (i-BUS) |
| **Weight** | ~7.7g (with case), ~5.8g (without case) |
| **Dimensions** | 40 x 22 x 10 mm |
| **Price** | ~$7.00 (~EUR 6.50) |
| **Compatible with Turnigy 9X?** | YES with iRangeX module (+$5.50) |
| **Source** | [Banggood](https://www.banggood.com/search/flysky-fs-ia6b.html) (5900+ reviews, $6.99) |
| **Notes** | **Best value.** Dual antenna diversity for superior range. i-BUS output. PPM output. Telemetry support. Remove case to save 2g. Proven reliability with 5000+ reviews. |

#### Option B: Flysky FS-A8S (AFHDS 2A, requires module) -- LIGHTWEIGHT

| Field | Value |
|-------|-------|
| **Name** | Flysky FS-A8S |
| **Protocol** | AFHDS 2A |
| **Channels** | 8 (i-BUS) / 4 (PWM) |
| **Weight** | ~3.8g |
| **Dimensions** | 22.0 x 13.6 x 7.8 mm |
| **Price** | ~$10-15 (~EUR 9-14) |
| **Compatible with Turnigy 9X?** | YES with iRangeX module (+$5.50) |
| **Source** | Banggood, AliExpress |
| **Notes** | **Lightest option at 3.8g.** Ultra-compact. Dual antenna diversity. i-BUS gives 8 channels on single wire. Only 4 PWM channels - need i-BUS decoder or flight controller for 6+ servos. Popular in F3J/F5J competition sailplanes. |

**WARNING:** The FS-A8S only has 4 PWM outputs. To drive 6 servos, you need an i-BUS to PWM decoder (~$3-5) or use PPM + decoder. This adds complexity and weight. For 6 direct PWM servo connections, the FS-iA6B is the better choice.

### Tier 3: Premium ($20-40)

#### Flysky FS-TR8B (AFHDS 3, requires full module)

| Field | Value |
|-------|-------|
| **Name** | Flysky FS-TR8B |
| **Protocol** | AFHDS 3 |
| **Channels** | 8 |
| **Weight** | ~5g |
| **Dimensions** | ~25 x 18 x 8 mm |
| **Price** | ~$25 (~EUR 23) |
| **Compatible with Turnigy 9X?** | Requires AFHDS 3 module (expensive) |
| **Source** | Banggood |
| **Notes** | Latest generation protocol. Overkill for this application. Module cost prohibitive. |

### Receiver Comparison Table

| Receiver | Protocol | Weight | Channels (PWM) | Price (EUR) | Module Swap? | Total Cost |
|----------|----------|--------|----------------|-------------|-------------|------------|
| **Stock Turnigy 9X V2** | AFHDS | 18g | 8 | EUR 0 (owned) | No | EUR 0 |
| **FS-R6B** | AFHDS | 10g | 6 | EUR 8 | No | EUR 8 |
| **FS-iA6** + iRX6 | AFHDS 2A | 8g + 5.5 | 6 | EUR 4.5 + 5 | Yes | EUR 9.5 |
| **FS-iA6B** + iRX6 | AFHDS 2A | 5.8g* + 5.5 | 6 | EUR 6.5 + 5 | Yes | EUR 11.5 |
| **FS-A8S** + iRX6 | AFHDS 2A | 3.8g + 5.5 | 4 | EUR 12 + 5 | Yes | EUR 17 |

\* Without case. With case: 7.7g.

**Weight savings vs stock:** FS-iA6B saves 12.2g (10.4g with case). FS-A8S saves 14.2g but needs decoder.

---

## 2. Servo Options

### Wing Servo Requirements

The wing panels have airfoils 6.4-8.6% thick. At the servo locations:
- **Root panel (P1, flap):** 210mm chord, AG24, ~9% thick = ~19mm. Internal height ~14-16mm after walls.
- **Outboard panel (P3/P4, aileron):** ~162mm chord, AG09, ~9.2% thick = ~15mm. Internal height ~10-12mm after walls.

Servo must fit in ~12mm height minimum. Slim 8mm-wide servos are ideal for minimal airfoil disruption.

### Wing Servos

#### Tier 1: Budget ($3-5)

**JX PDI-1109MG**

| Field | Value |
|-------|-------|
| **Price** | ~$4 (~EUR 3.70) each on AliExpress |
| **Weight** | 10.0g |
| **Dimensions** | 23.2 x 12.0 x 25.5 mm |
| **Torque** | 2.2 kg-cm @ 4.8V / 2.5 kg-cm @ 6.0V |
| **Speed** | 0.12 s/60deg @ 4.8V / 0.10 s/60deg @ 6.0V |
| **Gear** | Metal |
| **Wire** | 180mm, JR connector |
| **Fit** | 12mm wide, 25.5mm tall - fits in root panels but TIGHT in tip panels |
| **Notes** | Good torque for the price. Standard 12mm width is not ideal for thin wings. Best for flap servos in root panels. |

#### Tier 2: Mainstream ($8-15) -- RECOMMENDED

**JX PDI-HV0903MG** (8mm slim wing servo)

| Field | Value |
|-------|-------|
| **Price** | ~$8-10 (~EUR 7-9) each on AliExpress |
| **Weight** | 9.0g |
| **Dimensions** | 23.5 x 8.1 x 24.3 mm |
| **Torque** | 1.5 kg-cm @ 4.8V / 2.0 kg-cm @ 6.0V |
| **Speed** | 0.12 s/60deg @ 4.8V / 0.09 s/60deg @ 6.0V |
| **Gear** | Metal |
| **Wire** | 150mm, JR connector |
| **Fit** | **8.1mm wide** - slim profile ideal for wing mounting. 24.3mm tall fits all panels. |
| **Notes** | Perfect wing servo. Slim 8mm profile minimizes airfoil disruption. Metal gear for reliability. Good torque at 6V from BEC. |

**PTK 7308MG-D** (8mm slim, lower profile)

| Field | Value |
|-------|-------|
| **Price** | ~$8-12 (~EUR 7-11) each on AliExpress |
| **Weight** | 8.0g |
| **Dimensions** | 23.5 x 8.0 x 16.8 mm |
| **Torque** | 1.8 kg-cm @ 4.8V / 2.5 kg-cm @ 6.0V |
| **Speed** | 0.14 s/60deg @ 4.8V / 0.083 s/60deg @ 6.0V |
| **Gear** | Metal |
| **Wire** | 150mm, JR connector |
| **Fit** | **8.0mm wide x 16.8mm tall** - excellent low profile for thin wings. |
| **Notes** | Lower profile (16.8mm vs 24.3mm) is great for thin tip panels. Higher torque than HV0903MG at 6V. Slightly slower at 4.8V but excellent at 6V. **Best slim wing servo for the price.** |

#### Tier 3: Premium ($20-30)

**KST X08 V6.0** (competition-grade slim wing servo)

| Field | Value |
|-------|-------|
| **Price** | ~$25-30 (~EUR 23-28) each |
| **Weight** | 8.0g |
| **Dimensions** | 23.5 x 8.0 x 16.8 mm |
| **Torque** | 1.4 kg-cm @ 4.2V / 2.2 kg-cm @ 6.0V / 2.8 kg-cm @ 8.4V |
| **Speed** | 0.18 s/60deg @ 4.2V / 0.15 s/60deg @ 6.0V / 0.09 s/60deg @ 8.4V |
| **Gear** | Metal |
| **Wire** | 150mm, JR connector |
| **Fit** | 8.0mm wide x 16.8mm tall - same form factor as PTK 7308MG-D |
| **Notes** | Competition-grade servo used in F3K/F5J. Brushless motor core. Very consistent centering. HV capable (8.4V). Available from soaring-specialty shops like Soaring USA, Aloft Hobbies, Kennedy Composites. Higher price justified only for competition use. |

### Wing Servo Comparison

| Servo | Width | Height | Weight | Torque @6V | Speed @6V | Price (EUR) |
|-------|-------|--------|--------|------------|-----------|-------------|
| JX PDI-1109MG | 12mm | 25.5mm | 10g | 2.5 kg-cm | 0.10s | ~3.70 |
| **JX PDI-HV0903MG** | 8.1mm | 24.3mm | 9g | 2.0 kg-cm | 0.09s | ~7-9 |
| **PTK 7308MG-D** | 8.0mm | 16.8mm | 8g | 2.5 kg-cm | 0.083s | ~7-11 |
| KST X08 V6 | 8.0mm | 16.8mm | 8g | 2.2 kg-cm | 0.15s | ~23-28 |

### Tail Servos

Tail servos mount in the fuselage servo bay at X=350mm. Size constraints are relaxed compared to wing servos.

#### Tier 1: Budget ($3-5)

**Emax ES08MA II**

| Field | Value |
|-------|-------|
| **Price** | ~$4-5 (~EUR 3.70-4.60) each on AliExpress |
| **Weight** | 12.0g |
| **Dimensions** | 23.0 x 11.5 x 24.0 mm |
| **Torque** | 1.6 kg-cm @ 4.8V / 2.0 kg-cm @ 6.0V |
| **Speed** | 0.12 s/60deg @ 4.8V / 0.10 s/60deg @ 6.0V |
| **Gear** | Metal |
| **Wire** | 250mm, JR connector |
| **Notes** | Good budget tail servo. Metal gear. 250mm wire length good for fuselage routing. |

**JX PDI-1109MG** (same as wing budget option)

| Field | Value |
|-------|-------|
| **Price** | ~$4 (~EUR 3.70) each |
| **Weight** | 10.0g |
| **Dimensions** | 23.2 x 12.0 x 25.5 mm |
| **Torque** | 2.2 kg-cm @ 4.8V / 2.5 kg-cm @ 6.0V |
| **Speed** | 0.12 s/60deg @ 4.8V / 0.10 s/60deg @ 6.0V |
| **Gear** | Metal |
| **Wire** | 180mm, JR connector |
| **Notes** | Higher torque than ES08MA II. Lighter. Better value for tail use. |

#### Tier 2: Mainstream ($5-10)

**JX PDI-933MG** (higher torque)

| Field | Value |
|-------|-------|
| **Price** | ~$6-8 (~EUR 5.50-7.40) each |
| **Weight** | 13.0g |
| **Dimensions** | 23.0 x 12.0 x 25.5 mm |
| **Torque** | 2.8 kg-cm @ 4.8V / 3.5 kg-cm @ 6.0V |
| **Speed** | 0.12 s/60deg @ 4.8V / 0.10 s/60deg @ 6.0V |
| **Gear** | Metal |
| **Wire** | 180mm, JR connector |
| **Notes** | Highest torque option. Good for elevator pushrod with friction. Slightly heavier. |

#### Tier 3: Premium ($20-30)

**KST X06** (ultra-light micro digital)

| Field | Value |
|-------|-------|
| **Price** | ~$25 (~EUR 23) each |
| **Weight** | 3.5g |
| **Dimensions** | 17.4 x 8.2 x 9.5 mm |
| **Torque** | 0.9 kg-cm @ 4.8V / 1.2 kg-cm @ 6.0V |
| **Speed** | 0.10 s/60deg @ 4.8V |
| **Gear** | Plastic (Delrin) |
| **Wire** | ~100mm |
| **Notes** | Ultra-light. Too weak for elevator pushrod through boom. Better suited for V-tail or direct-link applications. Plastic gear not ideal for pushrod friction. **NOT recommended for this application.** |

### Tail Servo Comparison

| Servo | Weight | Torque @6V | Speed @6V | Price (EUR) |
|-------|--------|------------|-----------|-------------|
| Emax ES08MA II | 12g | 2.0 kg-cm | 0.10s | ~4.60 |
| **JX PDI-1109MG** | 10g | 2.5 kg-cm | 0.10s | ~3.70 |
| JX PDI-933MG | 13g | 3.5 kg-cm | 0.10s | ~6.50 |

---

## 3. Connectors and Wiring

### Wing-to-Fuselage Connector

Two approaches for the 4 wing servos crossing the wing-fuselage junction:

#### Option A: Multiplex MPX 6-pin Flange Connector
- **Standard in European sailplane kits** (Multiplex, Roedesign, S2G)
- Carries 2 servo signals + common VCC + common GND per connector
- Need 2 connectors (one per wing half) = 8 pins total for 4 servos
- **Pros:** Robust, self-aligning, proven in competition sailplanes
- **Cons:** Requires special crimp tool, harder to source, ~EUR 8-12 per pair
- **Source:** [Hyperflight.co.uk](https://www.hyperflight.co.uk), [SoaringUSA](https://soaringusa.com), AliExpress search "MPX wing connector"

#### Option B: Individual JR Servo Extensions -- RECOMMENDED
- Standard 3-pin servo connectors for each servo
- 4 connectors per wing half (2 signal + 2 returns), or use Y-harness for paired servos
- **Pros:** Universal, no special tools, cheap (~EUR 0.50 each)
- **Cons:** More wires to manage, can be fiddly
- **Source:** AliExpress, any RC shop

#### Option C: Multi-pin DIN Connector (6-pin or 8-pin)
- Single round connector per wing half carrying all 4 servo channels
- **Pros:** Clean installation, quick connect/disconnect
- **Cons:** Need to solder/assemble, non-standard
- **Source:** AliExpress search "aviation connector 6 pin"

### Servo Extension Lengths

| Position | Extension Length | Notes |
|----------|-----------------|-------|
| Flap servo (P1 root panel) | 200-250mm | Servo at ~200mm from root, needs to reach fuselage Rx |
| Aileron servo (P3/P4) | 350-450mm | Servo at ~700mm from root, needs extension |
| Elevator servo (fuselage) | None (direct) | Servo bay near Rx, ~50mm jumper |
| Rudder servo (fuselage) | None (direct) | Same bay as elevator, ~50mm jumper |

**Wing servo wire routing:** Servo wire runs inside wing panel, exits at root rib, passes through wing saddle into fuselage receiver.

**Needed parts:**
- 4x servo extension 250mm (~EUR 1 each on AliExpress)
- 4x servo extension 450mm (~EUR 1.50 each on AliExpress)
- OR: solder custom-length extensions to avoid excess wire weight

### Pushrod Hardware

| Item | Qty | Price | Source |
|------|-----|-------|--------|
| 0.8mm music wire (for Z-bends) | 1m | ~EUR 2 | Local hardware / AliExpress |
| 1.5mm carbon rod (elevator pushrod, 400mm through boom) | 2x | ~EUR 2 | AliExpress |
| Kevlar thread (rudder pull-pull, 2x 600mm) | 1m | ~EUR 3 | Soaring shops, AliExpress |
| Micro clevises (2mm) | 8x | ~EUR 0.50 each | AliExpress |
| Control horns (nylon, mini) | 6x | ~EUR 0.30 each | AliExpress |
| Heat shrink tubing (1.5mm, for pushrod guides) | 0.5m | ~EUR 1 | AliExpress |

---

## 4. BEC Current Calculation

### Servo Current Draw Estimates

| Servo Type | Idle (mA) | Normal Flight (mA) | Stall (mA) |
|------------|-----------|-------------------|------------|
| PDI-1109MG (analog) | 5-10 | 150-300 | 500-800 |
| PDI-HV0903MG (analog) | 5-10 | 100-250 | 400-700 |
| PTK 7308MG-D (digital) | 10-20 | 150-350 | 600-900 |

### Worst-Case Calculation (all PTK 7308MG-D digital servos)

| Component | Current |
|-----------|---------|
| 4x wing servos @ 350mA average (flap+aileron thermal circling) | 1,400 mA |
| 1x elevator servo @ 250mA | 250 mA |
| 1x rudder servo @ 200mA | 200 mA |
| Receiver | 50 mA |
| **Total average** | **~1,900 mA** |
| **Peak (crow braking, all surfaces loaded)** | **~4,000-5,000 mA** |

### ESC BEC Requirements

| BEC Type | Rating | Suitable? |
|----------|--------|-----------|
| Linear BEC (cheap ESC) | 1.5-2.0A @ 3S | **NO** - will overheat |
| Switching BEC (SBEC) | 3.0-4.0A continuous | **MARGINAL** - OK for cruise, may brown out during crow |
| SBEC 5A+ | 5.0A continuous, 7A peak | **YES** - safe margin |
| External UBEC 5A | 5.0A continuous | **YES** - best option with 6 digital servos |

**Recommendation:** Select an ESC with a **switching BEC rated at 5A+ continuous**. Many 30A+ ESCs in the recommended motor section include 4A SBEC which is adequate for analog servos but marginal for digital. If using PTK 7308MG-D (digital), prefer a 5A+ SBEC or add an external UBEC.

---

## 5. Bulgarian/EU Source Research

### Bulgarian RC Shops

| Shop | Website | Notes |
|------|---------|-------|
| Hobbyzone.bg | hobbyzone.bg | General hobby, may stock Flysky |
| Modelist.bg | modelist.bg | Modeling supplies |
| RC Market BG | Various listings | Check local classifieds (alo.bg, olx.bg) |

**Reality check:** Bulgarian RC shops typically have limited stock of Flysky receivers and specialty servos. AliExpress/Banggood are the primary practical sources. Delivery from AliExpress to Bulgaria: 2-4 weeks standard, 7-10 days with premium shipping.

### EU-based Alternatives (faster shipping)

| Shop | Website | Shipping to BG |
|------|---------|---------------|
| Banggood | banggood.com | 1-2 weeks priority |
| 3DJake | 3djake.com | 3-5 days (EU warehouse) |
| HobbyKing EU warehouse | hobbyking.com | 5-7 days |
| Hyperflight (UK) | hyperflight.co.uk | Sailplane specialty, 5-7 days post-Brexit |

### Sourcing Priority (per CLAUDE.md rules)

1. **Bulgaria first** -- check hobbyzone.bg and local shops
2. **Banggood** -- fastest international option, good Flysky stock
3. **AliExpress** -- cheapest servos, 2-4 week delivery
4. **EU specialty shops** (Hyperflight, SoaringUSA) -- for premium KST servos

---

## 6. Recommended Selection

### Option A: Best Value (recommended for first build)

| Position | Component | Weight | Price (EUR) | Source |
|----------|-----------|--------|-------------|--------|
| **Module upgrade** | iRangeX iRX6 multi-protocol | ~15g (in Tx) | EUR 5.00 | Banggood |
| **Receiver** | Flysky FS-iA6B (case removed) | 5.8g | EUR 6.50 | Banggood |
| **Wing servo x4** | PTK 7308MG-D (8mm slim, digital) | 8.0g ea = 32g | EUR 8.00 ea = EUR 32 | AliExpress |
| **Tail servo x2** | JX PDI-1109MG (metal gear) | 10.0g ea = 20g | EUR 3.70 ea = EUR 7.40 | AliExpress |
| **Extensions + connectors** | Servo extensions + clevises + wire | ~8g | EUR 12 | AliExpress |
| | | **Total: 65.8g** | **Total: EUR 63** | |

**Weight savings vs current spec:** Current electronics budget assumes 54g for 6x 9g servos + 18g Rx = 72g. This selection: 32g wing + 20g tail + 5.8g Rx = 57.8g. **Saves 14.2g** (7.8g from Rx, 6g from lighter wing servos).

### Option B: Budget (minimum cost)

| Position | Component | Weight | Price (EUR) | Source |
|----------|-----------|--------|-------------|--------|
| **Receiver** | Flysky FS-R6B (AFHDS, no module swap) | 10g | EUR 8.00 | Banggood |
| **Wing servo x4** | JX PDI-1109MG | 10g ea = 40g | EUR 3.70 ea = EUR 14.80 | AliExpress |
| **Tail servo x2** | JX PDI-1109MG | 10g ea = 20g | EUR 3.70 ea = EUR 7.40 | AliExpress |
| **Extensions + connectors** | Basic servo extensions + hardware | ~8g | EUR 8 | AliExpress |
| | | **Total: 78g** | **Total: EUR 38** | |

**Notes:** No module swap needed. 12mm-wide servos are tight in thin wing panels. Heavier but cheapest. Still saves 8g on receiver vs stock.

### Option C: Competition (maximum performance)

| Position | Component | Weight | Price (EUR) | Source |
|----------|-----------|--------|-------------|--------|
| **Module upgrade** | iRangeX iRX6 | ~15g (in Tx) | EUR 5.00 | Banggood |
| **Receiver** | Flysky FS-A8S (ultra-light) + i-BUS decoder | 3.8g + 3g = 6.8g | EUR 12 + 4 = EUR 16 | Banggood |
| **Wing servo x4** | KST X08 V6 (competition) | 8.0g ea = 32g | EUR 25 ea = EUR 100 | Soaring shops |
| **Tail servo x2** | JX PDI-1109MG | 10g ea = 20g | EUR 3.70 ea = EUR 7.40 | AliExpress |
| **Extensions + connectors** | Premium extensions + hardware | ~6g | EUR 15 | AliExpress |
| | | **Total: 64.8g** | **Total: EUR 143** | |

**Notes:** Lightest receiver option. Competition-grade wing servos. Marginal tail servos (could upgrade to KST DS125MG for another EUR 30). High cost but best performance.

---

## 7. Summary Weight Impact

| Config | Rx | 4x Wing | 2x Tail | Electronics Total | Savings vs Stock |
|--------|----|---------|---------|-------------------|-----------------|
| **Stock** (current spec) | 18g | 36g (4x9g) | 18g (2x9g) | 72g | -- |
| **Option A** (recommended) | 5.8g | 32g (4x8g) | 20g (2x10g) | 57.8g | **-14.2g** |
| **Option B** (budget) | 10g | 40g (4x10g) | 20g (2x10g) | 70g | **-2g** |
| **Option C** (competition) | 6.8g | 32g (4x8g) | 20g (2x10g) | 58.8g | **-13.2g** |

The recommended Option A saves 14g at reasonable cost (EUR 63 total for all controls electronics including module upgrade).

---

## 8. Action Items

1. **Confirm module upgrade preference** -- iRangeX iRX6 ($5.50) unlocks AFHDS 2A receivers. Worth it for the weight savings alone.
2. **Verify PTK 7308MG-D availability** -- search AliExpress for "PTK 7308MG" or "7308MG digital servo 8mm"
3. **Order iRangeX module first** -- test binding with any AFHDS 2A receiver before committing to full servo order
4. **Wing servo mounting design** -- the 8mm slim servos need a pocket in the wing rib. Design the mounting cutout based on 23.5 x 8.0 x 16.8mm (PTK 7308MG-D dimensions)
5. **Update specifications.md** -- once selections are confirmed, update electronics budget section
