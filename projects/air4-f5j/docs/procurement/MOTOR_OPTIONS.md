# Motor, ESC & Prop Options — AeroForge F5J Sailplane
> Procurement research document for propulsion system selection
> Date: 2026-04-01
> Status: DRAFT — Manual verification needed before ordering
> Researcher: AeroForge Procurement Team
> Branch: feat/hstab-complete-vstab-design
> Spec Source: docs/specifications.md
> URL: (this document)
> https://github.com/anthropics/aeroforge/blob/feat/hstab-complete-vstab-design/docs/procurement/MOTOR_OPTIONS.md
> Related: docs/procurement/BATTERY_OPTIONS.md, docs/procurement/ELECTRONICS_OPTIONS.md
> Last updated: 2026-04-01

---

## Overview

This document covers propulsion system procurement for the AeroForge 2.56m F5J-class 3D-printed RC sailplane.
The propulsion system provides climb power only -- F5J rules limit motor run time, and the aircraft
spends 95%+ of flight time gliding with motor off and prop folded.

### Aircraft Constraints
- **AUW target**: 750-800g (competition), up to 900g (ballast)
- **Battery**: 3S LiPo (11.1V nominal, 12.6V charged)
- **Climb power target**: 150-200W
- **Climb duration**: 10-15 seconds per launch (F5J rules: motor timer)
- **Target altitude**: 80-120m in 10s motor run
- **Climb current**: 14-18A at 11.1V (~155-200W)
- **Gliding current**: ~0A (motor off, prop folded)
- **Motor weight budget**: 50-70g
- **ESC weight budget**: 15-25g
- **Prop+spinner weight budget**: 10-20g
- **Total propulsion budget**: 75-115g (motor + ESC + prop + spinner)

---

## 1. Motor Options

### Motor Sizing Analysis
For a 750-850g F5J sailplane:
- **Power loading**: ~200W/kg target = 150-170W at AUW
- **At 3S (11.1V)**: 150W / 11.1V = ~13.5A continuous, ~18A peak
- **KV range**: 900-1400KV (depends on prop size chosen)
- **Stator size**: 2204-2822 range (22mm stator, 04-22mm magnet length)
- **Weight range**: 35-70g (lighter is better for CG)

### 1A. Budget Tier ($10-20) -- AliExpress/Generic

| Motor | KV | Weight | Cells | Max Power | Shaft | Price | Source |
|-------|----|--------|-------|-----------|-------|-------|--------|
| **Surpass Hobby 2204** | 1400KV | ~28g | 2-3S | ~150W | 3mm | $8-12 | AliExpress |
| **Surpass Hobby 2206** | 1300KV | ~32g | 2-3S | ~180W | 3mm | $10-14 | AliExpress |
| **Surpass Hobby 2212** | 1000KV | ~48g | 2-3S | ~250W | 4mm | $12-16 | AliExpress |
| **BGNing 2212** | 1400KV | ~45g | 2-3S | ~220W | 4mm | $10-14 | Amazon |
| **Racerstar 2206** | 1250KV | ~30g | 2-3S | ~170W | 3mm | $8-10 | AliExpress |

**Notes**:
- Surpass Hobby 2204/2206 are FPV racing motors adapted for sailplane use
- The 2204 at 1400KV is the lightest option (28g) but marginal on power for F5J climb
- Surpass Hobby 2212 at 1000KV provides ample power with 10-11" folding prop
- BGNing 2212 at 1400KV is too fast for large props -- use only with 8-9" prop
- **Best budget choice**: Surpass Hobby 2206 1300KV (~32g, $12) -- good power-to-weight

### 1B. Mainstream Tier ($20-40) -- RECOMMENDED

| Motor | KV | Weight | Cells | Max Power | Shaft | Price | Source |
|-------|----|--------|-------|-----------|-------|-------|--------|
| **Surpass Hobby 2216** | 880KV | ~56g | 2-4S | ~300W | 4mm | $18-22 | Amazon/AliExpress |
| **D3536** | 1000-1450KV | ~65g | 2-4S | ~350W | 4mm | $15-20 | Amazon |
| **D2830** | 850-1300KV | ~52g | 2-4S | ~280W | 4mm | $15-18 | Amazon |
| **D3542** | 1000-1450KV | ~75g | 2-4S | ~400W | 5mm | $18-22 | Amazon |
| **Cobra C2217/14** | ~1050KV | ~52g | 3S | ~250W | 4mm | $25-30 | Innov8tive |
| **ReadytoSky LE2204** | 1800KV | ~28g | 2-3S | ~150W | 3mm | $15-18 | Amazon |

**Notes**:
- **Surpass Hobby 2216 880KV** -- excellent sailplane motor at 56g
  - At 3S with 11x6 folding prop: ~16A, ~178W -- ideal for F5J climb
  - Weight at 56g is reasonable for this power class
  - [Amazon listing](https://www.amazon.com/s?k=Surpass+Hobby+2216+brushless+motor)
- **D2830 1000KV** -- popular budget fixed-wing motor, 52g
  - At 3S with 10x7 folding prop: ~14A, ~155W -- meets minimum F5J requirements
  - Good power-to-weight ratio
  - [Amazon listing](https://www.amazon.com/s?k=D2830+brushless+outrunner+motor)
- **D3536 1000KV** -- larger motor, 65g, overkill for this application
  - At 3S with 11x7 prop: ~18A, ~200W -- good power but heavier than needed
  - Better suited for 1.5-2kg aircraft
- **Cobra C2217/14** -- quality US-brand motor at 52g
  - Excellent efficiency, smooth running
  - [Innov8tive Designs](https://www.innov8tivedesigns.com)
- **ReadytoSky LE2204 1800KV** -- very light (28g) but high KV
  - Needs small prop (7-8"), may not produce enough thrust for steep climb
  - Better for F3K/DLG class (1.5m sailplanes, 300-500g)

### 1C. Premium Tier ($40-80) -- Competition Grade

| Motor | KV | Weight | Cells | Max Power | Shaft | Price | Source |
|-------|----|--------|-------|-----------|-------|-------|--------|
| **E-flite Power 60** | 400-470KV | ~115g | 3-6S | ~600W | 5mm | $60-70 | Amazon |
| **E-flite Power 160** | 245KV | ~90g | 3-4S | ~160W | 4mm | $50-60 | Amazon |
| **Spektrum Avian 4250** | 800KV | ~85g | 3-4S | ~350W | 5mm | $55-60 | Amazon |
| **Spektrum Avian 4260** | 480-800KV | ~95g | 3-6S | ~500W | 5mm | $55-60 | Amazon |
| **Scorpion SII-2208-14** | ~1050KV | ~37g | 3S | ~200W | 3mm | $35-40 | Innov8tive |
| **Scorpion SII-2215-14** | ~960KV | ~55g | 3S | ~280W | 4mm | $40-50 | Innov8tive |

**Notes**:
- **E-flite and Spektrum motors are overkill for this application**
  - E-flite Power 60 at 115g is too heavy, designed for 1.5-3kg pattern models
  - Spektrum Avian 4250/4260 at 85-95g is also oversized
  - These motors shine on 4-6S, not optimal on 3S
- **Scorpion SII-2208-14** at 37g -- excellent lightweight competition motor
  - Perfect for 3S F5J sailplane at 750-850g
  - ~1050KV ideal for 10-11" folding prop
  - Premium quality, excellent efficiency
- **Scorpion SII-2215-14** at 55g -- slightly heavier, more power reserve
  - Better for windy conditions or heavier ballast configuration

---

## 2. ESC Options

### ESC Requirements
- **Cells**: 3S LiPo
- **Current rating**: 20A continuous minimum, 30A preferred
- **BEC**: 3A-5A linear or switching (powers Rx + 6 servos)
- **Weight**: 10-20g (lighter is better)
- **Features**: Brake enabled (folding prop), programmable timing

### ESC Comparison

| ESC | Rating | BEC | Weight | Brake | Price | Source |
|-----|--------|-----|--------|-------|-------|--------|
| **ZTW Spider 30A** | 30A | 3A/5V linear | 16g | Yes | $18-22 | AliExpress |
| **ZTW Spider 20A** | 20A | 2A/5V linear | 12g | Yes | $14-18 | AliExpress |
| **HobbyKing BlueSeries 30A** | 30A | 3A/5V linear | 18g | Yes (fw) | $12-15 | HobbyKing |
| **DYS SN30A** | 30A | -- | 10g | Yes (fw) | $12-15 | AliExpress |
| **T-Motor ESC 30A** | 30A | 5A/5V switching | 15g | Yes | $35-40 | GetFPV |
| **BLHeli_S 30A** | 30A | -- | 8g | Yes | $10-14 | AliExpress |
| **KISS ESC 30A** | 30A | 5A/5V switching | 12g | Yes | $40-50 | GetFPV |

**Notes**:
- **ZTW Spider 30A** -- proven sailplane ESC, optical coupling, built-in brake
  - Spider series is specifically designed for glider use
  - 3A BEC sufficient for 6 analog servos
  - [AliExpress](https://www.aliexpress.com/search?SearchText=ZTW+spider+30A+ESC)
- **ZTW Spider 20A** -- lighter option, adequate BEC for analog servos only
  - If using digital servos (PTK 7308MG-D), the 2A BEC may be marginal
  - 20A sufficient for F5J climb with efficient motor
- **HobbyKing BlueSeries 30A** -- budget option, requires BLHeli firmware flash for brake
  - Best value if comfortable with firmware flashing
  - Reliable and widely used
- **DYS SN30A** -- lightweight with BLHeli_S, excellent for sailplanes
  - Requires BLHeli Suite to configure brake and timing
  - Very light at 10g

### BEC Current Analysis
With recommended PTK 7308MG-D digital servos (4 wing + 2 tail):
- **4x wing servos average**: ~350mA each = 1,400mA
- **2x tail servos average**: ~200mA each = 400mA
- **Receiver**: ~50mA
- **Total average**: ~1,850mA (~1.9A)
- **Peak (crow braking)**: ~4-5A

**Conclusion**: 3A linear BEC is adequate for normal flight. During crow braking (all surfaces deflected), a 3A BEC may brown out. **5A switching BEC recommended** if using digital servos. 2A BEC is marginal -- avoid with digital servos.

---

## 3. Folding Propeller + Spinner Options

### Prop Requirements
- **Type**: Folding (CAM or Aeronaut style)
- **Size**: 9-12" diameter, 5-7" pitch (depends on motor KV)
- **Shaft**: 3mm or 4mm (must match motor)
- **Spinner**: 28-30mm diameter (aerodynamic)
- **Weight target**: 10-20g (prop + spinner + hub)
- **Folding blades**: Low-drag profile when folded

### Prop + Spinner Comparison

| Product | Size | Shaft | Weight | Price | Source |
|---------|------|-------|--------|-------|--------|
| **Aeronaut CAM Carbon 10x6** | 10x6 | 3/4mm | ~12g | $15-20 | Amazon/3DJake |
| **Aeronaut CAM Carbon 11x6** | 11x6 | 3/4mm | ~14g | $15-20 | Amazon/3DJake |
| **Aeronaut CAM Carbon 10x8** | 10x8 | 3/4mm | ~12g | $15-20 | Amazon/3DJake |
| **Graupner CAM Folding 10x6** | 10x6 | 3mm | ~14g | $18-22 | Amazon |
| **Graupner CAM Folding 11x6** | 11x6 | 3mm | ~16g | $18-22 | Amazon |
| **Generic folding prop 10x6** | 10x6 | 3/4mm | ~10g | $3-5 | AliExpress |
| **Generic folding prop 11x7** | 11x7 | 3/4mm | ~12g | $3-5 | AliExpress |

**Spinner Options**:
| Product | Diameter | Shaft | Weight | Price | Source |
|---------|----------|-------|--------|-------|--------|
| **Aeronaut Spinner 30mm** | 30mm | 3/4mm | ~5g | $8-12 | 3DJake |
| **Graupner Spinner 28mm** | 28mm | 3mm | ~4g | $8-10 | Amazon |
| **Generic aluminum spinner** | 30mm | 3/4mm | ~8g | $3-5 | AliExpress |

### Motor KV vs Prop Selection Guide

| Motor KV | Prop Size | Est. Thrust (3S) | Est. Current | Notes |
|----------|-----------|-------------------|---------------|-------|
| 880KV | 11x6 CAM | ~900g | ~16A | Good climb angle, quiet |
| 1000KV | 10x6 CAM | ~850g | ~14A | Ideal balance |
| 1050KV | 10x6 CAM | ~900g | ~15A | Ideal for Cobra/Scorpion |
| 1300KV | 9x5 CAM | ~750g | ~13A | Light motor, adequate thrust |
| 1400KV | 8x5 CAM | ~650g | ~12A | Marginal for 850g AUW |

**Recommended combinations**:
1. **Surpass 2216 880KV + Aeronaut 11x6** (~178W, ~16A) -- best climb performance
2. **Cobra 2217/14 1050KV + Aeronaut 10x6** (~167W, ~15A) -- best quality
3. **Surpass 2206 1300KV + Aeronaut 9x5** (~144W, ~13A) -- lightest setup

---

## 4. Recommended Combinations

### Option A: Best Value (recommended for first build)
| Component | Item | Weight | Price |
|-----------|------|--------|-------|
| Motor | Surpass Hobby 2216 880KV | 56g | $18-22 |
| ESC | ZTW Spider 30A | 16g | $18-22 |
| Prop | Aeronaut CAM Carbon 11x6 + 30mm spinner | 19g | $20-25 |
| **Total** | | **91g** | **$56-69** |

- **Power**: ~178W at 3S, plenty for F5J climb
- **Climb rate**: Estimated 60-70 degree climb angle at 800g AUW
- **Weight**: 91g for propulsion is reasonable (within spec budget)

### Option B: Budget (minimum cost)
| Component | Item | Weight | Price |
|-----------|------|--------|-------|
| Motor | Surpass Hobby 2206 1300KV | 32g | $10-14 |
| ESC | BLHeli_S 30A | 8g | $10-14 |
| Prop | Generic folding prop 9x5 + spinner | 13g | $5-8 |
| **Total** | | **53g** | **$25-36** |

- **Power**: ~144W at 3S, adequate for F5J climb
- **Lightest option** at 53g total -- saves 38g vs Option A
- **Risk**: Generic props less efficient, BLHeli_S requires firmware configuration

### Option C: Competition (maximum performance)
| Component | Item | Weight | Price |
|-----------|------|--------|-------|
| Motor | Scorpion SII-2215-14 960KV | 55g | $40-50 |
| ESC | T-Motor ESC 30A (switching BEC) | 15g | $35-40 |
| Prop | Aeronaut CAM Carbon 10x7 + spinner | 16g | $23-28 |
| **Total** | | **86g** | **$98-118** |

- **Power**: ~200W at 3S, best climb performance
- **Premium quality** throughout, proven in competition
- **Switching BEC** handles digital servos during crow braking

---

## 5. Bulgarian/EU Source Research

### Priority Order (per CLAUDE.md rules)
1. **Bulgaria first** -- hobbyzone.bg, modelist.bg, local shops
2. **3DJake.com** -- ships to Balkans, carries Aeronaut props
3. **Amazon.de** -- Amazon Germany, ships to Bulgaria
4. **HobbyKing EU warehouse** -- 5-7 days to Bulgaria
5. **AliExpress** -- cheapest but 3+ week shipping

### EU Specialty Sources
| Shop | Carries | Shipping to BG |
|------|---------|---------------|
| [3DJake.com](https://www.3djake.com) | Aeronaut props/spinners, Scorpion motors | 3-5 days |
| [Innov8tive Designs](https://www.innov8tivedesigns.com) | Cobra motors, Scorpion | 7-10 days (US) |
| [Hyperflight UK](https://www.hyperflight.co.uk) | Sailplane motors, folding props | 5-7 days |
| [SoaringUSA](https://www.soaringusa.com) | Competition sailplane gear | 7-14 days (US) |

---

## 6. Thrust Analysis

### Estimated Climb Performance at 800g AUW

| Setup | Motor (g) | Prop | Power (W) | Thrust (g) | Thrust/Weight | Climb Angle |
|-------|-----------|------|-----------|------------|---------------|-------------|
| **Option A** | 2216 880KV (56g) | 11x6 | 178 | 900 | 1.13:1 | ~62 deg |
| **Option B** | 2206 1300KV (32g) | 9x5 | 144 | 750 | 0.94:1 | ~48 deg |
| **Option C** | 2215 960KV (55g) | 10x7 | 200 | 950 | 1.19:1 | ~65 deg |
| Alt: 2212 1000KV (48g) | 10x6 | 155 | 850 | 1.06:1 | ~55 deg |

**Minimum for competitive F5J**: Thrust/weight > 1.0:1 (45 degree climb).
**Recommended**: Thrust/weight > 1.1:1 (60+ degree climb) for 80-100m altitude in 10s.

### Altitude Estimates (10s motor run)
- Option A (178W): ~85-95m altitude -- competitive
- Option B (144W): ~65-75m altitude -- marginal
- Option C (200W): ~90-100m altitude -- excellent

---

## 7. Summary Weight Impact

| Config | Motor | ESC | Prop+Spinner | Total | Notes |
|--------|-------|-----|-------------|-------|-------|
| **Stock spec** | TBD | 15-20g | 15-20g | 80-100g | Current spec budget |
| **Option A** | 56g | 16g | 19g | 91g | Within budget |
| **Option B** | 32g | 8g | 13g | 53g | **38g under budget** |
| **Option C** | 55g | 15g | 16g | 86g | Within budget |

---

## 8. Action Items

1. **Verify Surpass Hobby 2216 availability** on AliExpress/Amazon
2. **Order Aeronaut CAM Carbon prop early** -- specialty item, may take longer to ship
3. **Match shaft size** -- motor shaft (3mm or 4mm) must match prop hub adapter
4. **Configure ESC brake** -- folding prop requires ESC brake function enabled
5. **Test CG with chosen motor** -- 50-70g motor at nose affects CG significantly
6. **Consider 2S battery option** -- if motor allows, 2S saves ~80g battery weight (1300mAh 2S ~80g vs 3S 165g)
   - But: owner already has 3S batteries. Stay with 3S for now.
7. **Update specifications.md** once motor selection is confirmed

---

## Notes
- All prices in USD. Verify current pricing before ordering.
- Weight estimates are approximate; actual weight varies by manufacturer batch.
- Thrust estimates are based on similar motor/prop combinations, not measured data.
- For F5J competition, the motor is used for <15 seconds per flight -- efficiency matters less than thrust-to-weight ratio.
- **The prop folds during glide** -- drag from folded prop is critical. Aeronaut CAM Carbon blades have excellent folded profile.
- **Buy spare prop blades** -- they break on landing. 2-3 sets recommended.
- ESC brake setting is **mandatory** for folding prop -- without brake, prop windmills during glide, creating massive drag.

---

## Appendix A: Amazon Products Found (April 2026)

| Product | Price | Rating | Notes |
|---------|-------|--------|-------|
| Surpass Hobby 2204 1400KV | ~$12 | 4.4 (238 reviews) | Light (28g), high KV |
| Surpass Hobby 2216 880KV | ~$20 | 4.2+ | Best budget sailplane motor |
| D3536 1000KV Outrunner | ~$16 | 4.6 (36 reviews) | Good power, 65g |
| D2830 1000KV Outrunner | ~$15 | -- | 52g, good power-to-weight |
| D3542 1250KV Outrunner | ~$18 | -- | 75g, overkill |
| E-flite Power 60 470KV | ~$70 | 4.3 (64 reviews) | Premium, heavy (115g) |
| E-flite Power 160 245KV | ~$55 | 4.2 (21 reviews) | Premium, 90g |
| Spektrum Avian 4260 | ~$55 | 5.0 (3 reviews) | Premium, 95g |
| ReadytoSky LE2204 1800KV | ~$16 | 4.1 (68 reviews) | Light (28g), high KV |
| BGNing 2212 1400KV + 30A ESC | ~$30 | 4.3 (105 reviews) | Motor+ESC combo |
| FPVKing 2212 2200KV + 30A ESC kit | ~$30 | 4.1 (206 reviews) | Kit, too high KV |

---

## Revision History
| Date | Author | Description |
|------|--------|-------------|
| 2026-04-01 | AeroForge Team | Initial procurement research |
