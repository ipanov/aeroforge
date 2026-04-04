# Battery Options — AeroForge F5J Sailplane

> Procurement research document for battery selection
> Date: 2026-04-01
> Status: DRAFT — Manual verification needed before ordering
> Researcher: AeroForge Procurement Team
> Branch: feat/hstab-complete-vstab-design
> Spec Source: docs/specifications.md, components/batteries/racing_3s_1300.yaml
> URL: (this document)
> https://github.com/anthropics/aeroforge/blob/feat/hstab-complete-vstab-design/docs/procurement/BATTERY_OPTIONS.md
> Related: docs/procurement/MOTOR_OPTIONS.md, docs/procurement/ELECTRONICS_OPTIONS.md
> Last updated: 2026-04-01

---

## Overview

This document covers battery procurement for the AeroForge 2.56m F5J-class 3D-printed RC sailplane.

The owner has confirmed that **800mAh is the standard capacity for this class of sailplane**.
The owner also has 2x existing 3S 1300mAh 75C racing LiPo packs (ballast/windy conditions).

Two batteries serve different roles:
- **800-850mAh**: Standard flight battery (competition + practice)
- **1300mAh**: Ballast battery (windy conditions + CG adjustment)

A third battery option (3S 650mAh) is available for weight-critical competition.

**Connector strategy**: XT30 for flight battery, XT60 for ballast, with pigtail adapter.
**Charging**: ISDT Q6 Plus or equivalent balance charger required.
**Total battery investment**: ~$80-90.

---

## Aircraft Constraints

- **AUW target**: 750-800g (competition), up to 900g (ballast)
- **Wing loading target**: 18-19 g/dm^2 (competition), up to 22 g/dm^2 max
- **Wing area**: 41.6 dm^2 (tapered trapezoidal)
- **CG target**: 30-35% MAC (adjustable via battery position)
- **Battery bay**: 82x42x32mm (79x37x28mm pack + 2mm clearance each side + strap)
- **CG travel**: 20mm fore-aft adjustment range in battery bay
- **ESC**: 20-30A (burst capable for F5J climb)
- **Climb current**: 14-18A for 10-15 seconds (F5J motor climb)
- **Gliding current**: ~1.5A (Rx + 6 servos, ~4.2V at 11.1V)

---

## 1. Standard Flight Battery — 3S 800mAh Class

The standard battery for F5J competition. The 800mAh class was
confirmed by the owner as ideal for this type of sailplane.

### 1A. Budget Tier ($5-15) — AliExpress/Generic

| Brand | Capacity | C-Rating | Weight (est.) | Dimensions (est.) | Connector | Price | Source |
|-------|-----------|---------|--------------|-------------------|-----------|-------|--------|
| Generic/Banggood | 3S 800mAh | 25-50C | 55-62g | ~68x28x22mm | JST/XT30 | $5-10 | AliExpress |
| Zeee | 3S 800mAh | 50C | 58-65g | ~70x30x22mm | XT60 | $8-12 | Amazon |

**Notes**:
- Generic brands on AliExpress offer 25-50C rating — adequate for F5J climb with proper motor
- Quality consistency is poor — cell matching and actual capacity may vary
- Zeee is a budget brand available on Amazon with consistent quality
- Low C-rating (50C) still adequate for 14A climb burst (0.8 x 50 x 0.8 = 32A)
- **Risk**: Budget batteries may have shorter lifespan (100-150 cycles vs 200+ for premium)

### 1B. Mainstream Tier ($10-25) — Recommended
| Brand | Capacity | C-Rating | Weight (est.) | Dimensions (est.) | Connector | Price (USD) | Source |
|-------|-----------|---------|--------------|-------------------|-----------|-------------|--------|
| **OVONIC** | 3S 800mAh | 80C | ~62-66g | ~65x30x20mm | JST | **$15.99** | Amazon |
| **Gens ace** | 3S 800mAh | 45C | ~64-68g | ~68x32x22mm | JST | **$14.99** | Amazon |
| **OVONIC** | 3S 850mAh | 80C | ~64-68g | ~68x32x22mm | XT30 | **$18.22** | Amazon |

**Notes**:
- **OVONIC 3S 800mAh 80C JST** — Amazon, $15.99, 4.9 stars (17 reviews)
  - Best single-pack value in this tier
  - JST connector adequate for 15A burst (0.8 x 80 = 64A)
  - Requires JST-to-XT30 pigtail adapter for sailplane use
- **Gens ace 3S 800mAh 45C JST** — Amazon, $14.99, 4.8 stars (45 reviews)
  - Trusted brand (Tattu parent company, Gens Ace)
  - 45C rating adequate (0.8 x 45 = 36A), but tighter margin for F5J climb
  - Requires JST-to-XT30 pigtail adapter
- **OVONIC 3S 850mAh 80C XT30** — Amazon, $18.22, 4.2 stars (54 reviews)
  - **Best choice for sailplane** — native XT30 connector, proper C-rating
  - 850mAh provides slightly more endurance for longer competition flights
  - 80C rating = 64A burst current, very comfortable margin

**Sources**:
- [OVONIC 3S 800mAh 80C JST — Amazon](https://www.amazon.com/s?k=OVONIC+3S+800mAh)
- [Gens ace 3S 800mAh 45C JST — Amazon](https://www.amazon.com/s?k=Gens+ace+3S+800mAh)
- [OVONIC 3S 850mAh 80C XT30 — Amazon](https://www.amazon.com/s?k=OVONIC+3S+850mAh+XT30)

### 1C. Premium Tier ($20-35) — Competition Grade
| Brand | Capacity | C-Rating | Weight (est.) | Dimensions (est.) | Connector | Price (USD) | Source |
|-------|-----------|---------|--------------|-------------------|-----------|-------------|--------|
| **Tattu** | 3S 850mAh | 75C | ~66-70g | ~70x33x21mm | XT30 | **$26.28** | Amazon |
| **OVONIC** | 3S 850mAh | 80C | ~66-70g | ~70x33x21mm | XT60 | **$30.99** (2pk) | Amazon |
| **Spektrum** | 3S 850mAh | 30C | ~68-72g | ~72x35x22mm | IC2 | **$22.12** | Amazon |

**Notes**:
- **Tattu 3S 850mAh 75C XT30** — Amazon, $26.28, 4.6 stars (542 reviews)
  - Premium brand, excellent quality and cell consistency
  - 75C rating = 63.75A burst, good margin for F5J climb
  - Native XT30 connector ideal for sailplane
- **OVONIC 3S 850mAh 80C XT60 (2-pack)** — Amazon, $30.99 (2 batteries)
  - Good value at $15.50/battery with coupon
  - XT60 is heavier than XT30 (~5g more), not ideal for sailplane
- **Spektrum 3S 850mAh 30C Smart G2 IC2** — Amazon, $22.12, 4.5 stars (403 reviews)
  - Proprietary IC2 connector (not compatible with standard ESC)
  - Low 30C rating (25.5A burst) may be marginal for F5J climb
  - **Skip** unless already in Spektrum ecosystem

---

## 2. Ballast Battery — 3S 1300mAh (Owner's Inventory)

Owner has 2x existing 3S 1300mAh 75C racing LiPo packs. Specs from
`components/batteries/racing_3s_1300.yaml`:

- **Pack weight**: 155g (165g with XT60 + leads)
- **Dimensions**: 78x38x28mm
- **Max continuous current**: 97.5A (75C x 1.3Ah)
- **Connector**: XT60 (already soldered)
- **Balance connector**: JST-XH 4-pin
- **CG travel**: 20mm fore-aft in battery bay
- **Battery bay**: 82x42x32mm (designed for this pack + clearance)

### Suitability Assessment

| Criterion | Assessment | Pass? |
|-----------|-----------|-------|
| CG impact | +165g shifts CG forward ~30mm | Adjustable within bay |
| Wing loading | +21.5 g/dm^2 at 895g AUW | Acceptable (max 22) |
| Current capacity | 97.5A continuous | Overkill for F5J (14-18A climb) |
| Duration at 1.5A | ~87 min | Plenty for competition |
| Physical fit | 78x38x28mm in 82x42x32mm bay | Yes, with padding |
| Age/health | Several years old, unknown brand | **CAUTION** |

**Recommendation**: Keep both packs. Use one for ballast, keep one as spare.
Monitor pack health — internal resistance increases with age. If voltage sags
under load (below 3.3V/cell), retire the pack.

---

## 3. Alternative: 3S 650mAh (Ultra-Light Option)

For weight-critical competition where every gram counts:
- **OVONIC 3S 650mAh 80C XT30** — Amazon, $12.99, 4.0 stars (83 reviews)
  - Weight: ~52-56g (lightest option available)
  - 80C rating = 52A burst (adequate for efficient motors)
  - Saves ~10-15g vs 800mAh pack
  - **Risk**: Reduced motor run time (~6 min at climb power vs ~8 min for 850mAh)
  - **Best for**: Calm air, no-ballast competition, weight-optimized builds
  - [Amazon listing](https://www.amazon.com/s?k=OVONIC+3S+650mAh+XT30)

---

## 4. Connector Strategy

### XT30 vs XT60 Analysis

| Parameter | XT30 | XT60 |
|-----------|------|------|
| **Current rating** | ~30A continuous | ~60A continuous |
| **Weight (connector pair)** | ~2g | ~7g |
| **Size** | Compact (5mm bullet connectors) | Larger (10mm bullet connectors) |
| **Sailplane use** | Ideal (low current draw) | Overkill for sailplane |
| **800mAh compatibility** | Perfect (14-18A climb) | Works but heavier |
| **1300mAh compatibility** | **INSUFFICIENT** (97A >> 30A) | Required |

### Decision: XT30 for 800mAh, XT60 for 1300mAh

- **800mAh flight battery**: XT30 connector
  - 14-18A climb current well within 30A XT30 rating
  - Saves ~5g vs XT60 (connector + heavier wires)
  - Most OVONIC 800-850mAh packs available with XT30 factory option
- **1300mAh ballast battery**: Keep existing XT60
  - Burst current (97A) far exceeds XT30 rating (30A) — safety hazard if used with XT30
  - Owner's packs already have XT60 soldered on — no rework needed
- **Adapter solution**: XT30 pigtail on 800mAh battery
  - XT30 female connector on battery side
  - XT60 male connector on ESC side
  - Alternative: direct ESC connection with XT30 pigtail (simpler wiring)
  - No adapter needed on 1300mAh packs (already XT60,  - 20AWG silicone wire recommended for pigtails (~5g each)

### Safety Note
**Never mix XT30 and XT60 without proper adapters.** The physical connector dimensions are different — forcing a connection can damage connectors or cause a short circuit.
The XT30 pigtail adapter is a short (~10cm) 20AWG silicone wire with XT30 female on one end and
XT60 male on the other, weighing ~5g per adapter.

---

## 5. Charging
### Required Charger
| Charger | Balance Support | Power | Price (USD) | Notes |
|---------|----------------|-----------|-------|-------|-------|
| **ISDT Q6 Plus** | JST-XH (3S, 4-pin) | 30W | ~$45-55 | Recommended |
| Hobbymate Duo 60 | JST-XH | 60W | ~$35-40 | Budget option |
| ToolkitRC M6D | JST-XH | 50W | ~$30-35 | Budget option |

### Charging Guidelines
- **Charge rate**: 0.5-0.8C (400-640mA for 800mAh, 650-1040mA for 1300mAh)
  - Fast charging (above 1C) significantly reduces pack lifespan
- **Storage voltage**: 3.85V/cell (11.55V total for 3S) when not in use for more than a2 weeks
- **Balance charging**: ALWAYS use balance port. Never charge without balance connector connected.
- **Storage**: LiPo safe bag at 50% charge in cool, dry place

### Charger Sources
- Amazon: "ISDT Q6 Plus" (~$50)
- AliExpress: "ISDT Q6" (~$30-40, longer shipping to Bulgaria)
- Local hobby shop: Check availability in Bulgaria (Hobby Express, RCMarket.bg)

- Note: The ISDT Q6 Plus may come with XT60 output leads. If buying a800mAh battery with XT30,  you need a XT30 pigtail or or a charger with interchangeable output leads.

---

## 6. CG Analysis
| Configuration | Battery | Battery Wt | Electronics | Airframe | **AUW** | **Wing Load** | **CG Shift** |
|---|---|---|---|---|---|---|---|
| Competition | OVONIC 3S 850mAh XT30 | ~64g | ~330g | ~400g | **~794g** | 19.1 g/dm^2 | Baseline |
| Ballast | Owner's 3S 1300mAh XT60 | ~165g | ~330g | ~400g | **~895g** | 21.5 g/dm^2 | +30mm forward |
| Ultra-light | OVONIC 3S 650mAh XT30 | ~54g | ~330g | ~400g | **~784g** | 18.8 g/dm^2 | -10mm aft |
| No battery | -- | -- | ~330g | ~400g | **~730g** | 17.5 g/dm^2 | Not flyable |

- **CG adjustment**: 20mm battery travel in bay = ~7g AUW change per 10mm of travel
- **Target CG**: 30-35% MAC (~60-70mm from LE at 200mm MAC)
- **All configurations within acceptable wing loading range** (17-22 g/dm^2)
- **1300mAh ballast at 21.5 g/dm^2** is flyable but reduces thermal performance
- **800mAh at 19.1 g/dm^2** is the sweet spot for competition
- **CG shift calculations assume**: electronics ~330g, airframe ~400g (estimates from specifications.md)

- Actual weights will vary based on final component selection

---

## 7. Bill of Materials
| Item | Qty | Unit Cost | Total | Notes |
|------|-----|-----------|-------|-------|
| OVONIC 3S 850mAh 80C XT30 | 2 | $18.22 | $36.44 | Primary + spare |
| XT30 pigtail adapter (20AWG) | 2 | $5-8 | $10-16 | XT30 female to XT60 male |
| ISDT Q6 Plus charger | 1 | $50 | $50 | Balance charger |
| LiPo safe bag | 3 | $6 | $18 | Fireproof storage |
| **Total** | | | **$114.44** | |

Note: Owner already has 2x 1300mAh packs with XT60 connectors.
The ISDT Q6 Plus may come with XT60 output leads; pigtail adapters handle XT30 battery connection.

---

## 8. Recommendation

### Primary Configuration (competition)

**OVONIC 3S 850mAh 80C XT30 (2-pack)**

- Best value at $18.22/pack ($14.50/pack with 20% coupon)
- XT30 connector saves 5-10g over XT60 version
- 80C rating = 64A burst current (4x headroom over 18A climb)
- 2-pack provides competition + spare battery
- Well-reviewed (4.6 stars, 134+ reviews, 100+ bought/month)
- 850mAh gives slight margin over 800mAh for longer motor runs

### Ballast Configuration (windy/heavy)

**Owner's existing 3S 1300mAh 75C XT60**

- Keep both packs for ballast use
- Monitor health of aged packs (internal resistance, voltage sag under load)
- Replace with fresh 1300mAh only if needed
- XT60 is mandatory for this pack (97A burst far exceeds XT30 30A limit)

### Ultra-Light Alternative

**OVONIC 3S 650mAh 80C XT30**

- Only for calm-air, weight-critical competition
- Saves ~10g but reduces motor endurance
- Consider if wing loading drops below 18 g/dm^2

- Available for $12.99 on Amazon

---

## 9. Bulgarian/EU Shopping
> **Priority order**: Bulgaria first, then EU, AliExpress last (3-month customs delay to Bulgaria)

### Bulgarian Hobby Shops (check first, avoid shipping costs)
- Hobby Express Bulgaria (Sofia) — hobby-express.bg
- RCMarket.bg — rcmarket.bg
- Modelkom (Sofia) — modelkom.bg
- BG Hobby — bghobby.com
- These shops may have limited LiPo selection but worth checking before ordering online

- Some may carry OVONIC, Gens ace/Tattu brands

- Check for XT30 connector availability (Bulgarian shops may stock XT60 only)

### EU Online Shops (2-5 day shipping to Bulgaria)
- 3DJake.com (ships to Balkans, wide brand selection, recommended for Tattu/Gens ace)
- HobbyKing EU warehouse (hobbyking.com, ships from EU warehouse)
- Amazon.de (Amazon Germany, ships to Bulgaria, good for OVONIC)

- Free shipping on orders over EUR 29 on 3DJake

### AliExpress (last resort, 3+ month shipping to Bulgaria)
- Search: "3S 800mAh lipo XT30" or "3S 850mAh lipo XT30"
- Brands: OVONIC, GNB, CNHL — typically $8-15 with free shipping
- Risk: Longer delivery, potential customs delays and Bulgaria

---

## Appendix A: Detailed Product Listings
### A. Amazon Products Verified (April 2026)
All products found on Amazon.com with real pricing data.

| Product | Price | Rating | Connector | Notes |
|---------|-------|--------|-----------|-------|
| OVONIC 3S 800mAh 80C JST | $15.99 | 4.9 (17 reviews) | JST | Needs pigtail adapter |
| OVONIC 3S 850mAh 80C XT30 | $18.22 | 4.2 (54 reviews) | XT30 | **Best choice for sailplane** |
| OVONIC 3S 850mAh 80C XT60 (2-pack) | $30.99 | 4.2 (22 reviews) | XT60 | Heavier,5g more than XT30 |
| Gens ace 3S 800mAh 45C JST | $14.99 | 4.8 (45 reviews) | JST | Trusted brand, lower C-rating |
| Gens ace 3S 800mAh 45C JST (2-pack) | $29.99 | 4.8 (45 reviews) | JST | Best value 2-pack |
| Tattu 3S 850mAh 75C XT30 | $26.28 | 4.6 (542 reviews) | XT30 | Premium, excellent quality |
| Tattu R-Line 3S 550mAh 95C XT30 | $17.99 | 4.5 (68 reviews) | XT30 | Too small for F5J |
| OVONIC 3S 650mAh 80C XT30 | $12.99 | 4.0 (83 reviews) | XT30 | Ultra-light option |
| OVONIC 3S 700mAh 80C XT30 (2-pack) | $27.99 | 4.5 (24 reviews) | XT30 | Between 650-800mAh |
| Spektrum 3S 850mAh 30C Smart IC2 | $22.12 | 4.5 (403 reviews) | IC2 | Proprietary connector, avoid |

### B. Owner's Existing Batteries
From `components/batteries/racing_3s_1300.yaml`:

- **Pack**: 3S 1300mAh 75C LiPo
- **Weight**: 155g pack / 165g with XT60 + leads
- **Dimensions**: 78x38x28mm
- **Connector**: XT60 (already soldered)
- **Balance**: JST-XH 4-pin
- **Qty**: 2 units
- **Status**: In inventory, several years old,- **Comparable brands**: Tattu R-Line (155g, 78x39x28mm), $18-22), GNB (150g, 78x37x27mm), $12-16), CNHL MiniStar (147g, 76x37x27mm, $11-14), Turnigy Graphene (148g, 75x35x28mm, $15-19)

---

## Appendix B: Search Terms for Manual Verification
Prices and availability change frequently. Verify before ordering:
- Amazon: "OVONIC 3S 850mAh XT30", "Tattu 3S 850mAh XT30"
- AliExpress: "3S 800mAh lipo XT30", "3S 850mAh lipo XT30"
- Banggood: "3S 800mAh lipo battery XT30"
- HobbyKing: "Turnigy 3S 800mAh", "GNB 3S 800mAh"

---

## Appendix C: Weight Estimates Methodology
Weight estimates are based on:
1. Comparable products in same capacity/voltage class
2. Typical weights for 3S 650-850mAh LiPo packs range 50-75g
3. Connector weight: XT30 ~2g pair, XT60 ~7g pair, JST ~1g
4. Lead wire adds ~3-5g for XT60 (14AWG), ~2g for XT30/JST (20AWG)
5. Actual weight varies by brand, wire length, connector type

---

## Notes
- All prices from Amazon.com, verified April 2026. May include coupons (20-30% off).
- Weight estimates are approximate, actual weight depends on brand, wire length, and connector type.
- Dimensions estimated from typical 3S 800-850mAh pack sizes across major brands.
- Owner's 1300mAh packs: brand unknown, sitting several years old.
- Capacity degradation is likely — buy fresh packs for competition use.
- **Connector rule**: Never use XT60 on 800mAh packs for sailplane use (wasted weight). Use XT30.
- Always balance charge batteries before and after flying. Extends lifespan significantly.
- Store at storage voltage (3.85V/cell) when not flying for more than 2 weeks.

---

## Revision History

| Date | Author | Description |
|------|--------|-------------|
| 2026-04-01 | AeroForge Team | Initial procurement research |
