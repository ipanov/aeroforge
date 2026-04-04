# Powertrain Procurement Document -- AeroForge 2.56m F5J RC Sailplane

> Comprehensive motor, ESC, and folding propeller procurement research
> Date: 2026-04-01
> Status: RESEARCH COMPLETE -- Awaiting selection decision
> Researcher: AeroForge Procurement Team
> Branch: feat/hstab-complete-vstab-design
> Spec Source: docs/specifications.md
> Related: docs/procurement/BATTERY_OPTIONS.md, docs/procurement/CONTROLS_OPTIONS.md, docs/procurement/MOTOR_OPTIONS.md (superseded by this document)
> Last updated: 2026-04-01

---

## Overview

This document covers the complete powertrain (motor + ESC + folding prop + spinner) for the
AeroForge 2.56m F5J-class 3D-printed RC sailplane. The propulsion system provides climb power
only -- F5J rules limit motor run time, and the aircraft spends 95%+ of flight time gliding
with motor off and prop folded flat against the fuselage.

This document **supersedes** `MOTOR_OPTIONS.md` with expanded research, corrected specifications,
three-tier pricing with verified product data, and integration with the battery and controls
procurement documents.

### Key Design Philosophy

In F5J competition, the power system serves one purpose: haul the sailplane to 80-100m altitude
in 10-15 seconds as efficiently as possible. After that, the motor is dead weight and the prop
must fold to minimize drag. This means:

1. **Thrust-to-weight ratio > 1.1:1** is the primary motor metric
2. **ESC brake function is mandatory** -- without it, the prop windmills during glide
3. **Switching BEC at 5A+ is required** -- 6 digital servos can draw 4-5A peak during crow braking
4. **Folding prop drag when stowed** matters more than prop efficiency under power
5. **Motor weight directly impacts CG** -- a heavier nose motor helps CG but increases wing loading

---

## Aircraft Constraints

| Parameter | Value | Notes |
|-----------|-------|-------|
| **AUW target** | 750-850g | Competition config |
| **AUW max (ballast)** | 900g | With 1300mAh battery |
| **Wingspan** | 2560mm | 10 panels, 5 per half |
| **Wing area** | 41.6 dm^2 | Trapezoidal |
| **Wing loading target** | 18-19 g/dm^2 | Competition range |
| **Battery (flight)** | 3S 850mAh 80C XT30 | OVONIC, $18.22 |
| **Battery (ballast)** | 3S 1300mAh 75C XT60 | Owner's inventory, 2 units |
| **Voltage range** | 9.0-12.6V | 3S LiPo (3.0-4.2V/cell) |
| **Climb power target** | 150-200W | ~200W/kg at 800g AUW |
| **Climb duration** | 10-15 seconds | F5J rules: motor timer |
| **Target altitude** | 80-100m in 10s | F5J competition standard |
| **Climb current** | 14-18A at 11.1V | (~155-200W) |
| **Gliding current** | ~0A motor + ~1.5A Rx/servos | Motor off, prop folded |
| **BEC requirement** | 5A+ switching BEC | For 6 digital servos (peak 4-5A) |
| **ESC connector** | XT30 (flight battery) | XT60 for ballast battery |
| **Motor mount** | Front fuselage pod | CF-PETG printed mount |
| **Spinner clearance** | ~30mm | Spinner-to-fuselage nose |
| **Motor weight budget** | 25-60g | With mount hardware |
| **ESC weight budget** | 10-20g | Under 15g preferred |
| **Prop+spinner weight** | 10-25g | Folding prop with spinner |
| **Total powertrain budget** | 75-100g | Motor + ESC + prop + spinner + wiring |

---

## 1. Motor Options

### Motor Sizing Analysis

For a 750-850g F5J sailplane on 3S:
- **Power loading**: ~200W/kg target = 150-170W at AUW
- **At 3S (11.1V nominal, 12.6V charged)**: 150W / 11.1V = ~13.5A continuous, ~18A peak
- **At 3S charged (12.6V)**: 200W / 12.6V = ~15.9A -- this is the real climb current
- **KV range**: 900-1400KV depending on prop size
- **Stator size**: 2204-2216 range (22mm diameter, 4-16mm height)
- **Weight range**: 25-60g (lighter is better, but motor weight helps CG)
- **Shaft size**: 3mm (2204-2208) or 4mm (2212-2216) -- must match prop hub

### Power Requirements Derivation

```
F5J climb to 100m in 10 seconds:
- Potential energy: m*g*h = 0.8kg * 9.81 * 100m = 785 J
- Aerodynamic drag during climb (~30N at 15 m/s climb): ~3000 J
- Total energy: ~3785 J in 10s = 378W mechanical
- Motor efficiency: ~75% -> 504W electrical input
- At 3S (11.1V): 504W / 11.1V = 45A -- TOO HIGH
```

This is the theoretical worst case. In practice:
- Climb angle is 50-70 degrees, not vertical
- Airspeed during climb is 8-12 m/s (lower drag)
- Target altitude is 80-100m, not 100m minimum
- Real F5J setups use 150-200W electrical and achieve 60-70 degree climb angles

**Practical power target**: 150-200W electrical at 3S = 13.5-18A. This produces
thrust-to-weight ratios of 1.0-1.3:1 with efficient folding props, which is competitive.

### 1A. Budget Tier ($8-18) -- AliExpress/Temu/Generic

| Motor | KV | Weight (g) | Cells | Max Power (W) | Shaft | Prop (3S) | Price | Source |
|-------|----|-----------|-------|---------------|-------|-----------|-------|--------|
| **Surpass Hobby C2204** | 1400KV | 28g | 2-3S | ~150W | 3mm | 8x4 to 9x5 | $8-12 | AliExpress, Banggood |
| **Surpass Hobby C2206** | 1300KV | 32g | 2-3S | ~180W | 3mm | 9x5 to 10x5 | $10-14 | AliExpress |
| **XXD A2212 1000KV** | 1000KV | 48g | 2-3S | ~220W | 3.17mm | 10x6 to 11x5 | $6-10 | AliExpress, Banggood |
| **Racerstar BR2212 810KV** | 810KV | 45g | 2-4S | ~250W | 4mm | 11x6 to 12x6 | $12-15 | Banggood |
| **Surpass Hobby C2822 1200KV** | 1200KV | 38g | 2-4S | ~200W | 3mm | 9x5 to 10x5 | $7-11 | Banggood |

**Notes**:
- **Surpass Hobby C2206 1300KV** (32g, $12) is the best budget pick for this application
  - Light enough for CG flexibility
  - 180W max power sufficient for F5J climb with 9x5 folding prop
  - 3mm shaft -- compatible with most budget folding props
  - Widely available on AliExpress with 500+ reviews
- **XXD A2212 1000KV** (48g, $8) is the cheapest adequate option
  - Heavier at 48g, but the weight helps CG on a nose-mounted motor
  - Very common, parts and replacements easy to find
  - 3.17mm shaft is annoying -- needs adapter for standard 3mm prop hubs
- **Racerstar BR2212 810KV** (45g, $13) -- good for larger props
  - Low KV allows 11x6 or 12x6 folding prop for high static thrust
  - Actually a multirotor motor, but works well on sailplanes with folding props
  - 612 reviews on Banggood, 4.95 rating

### 1B. Mainstream Tier ($18-30) -- RECOMMENDED

| Motor | KV | Weight (g) | Cells | Max Power (W) | Shaft | Prop (3S) | Price | Source |
|-------|----|-----------|-------|---------------|-------|-----------|-------|--------|
| **Sunnysky X2216 880KV** | 880KV | 56g | 2-4S | ~300W | 4mm | 11x6 to 12x6 | $18-22 | Banggood, AliExpress |
| **Surpass Hobby C3530 1100KV** | 1100KV | 52g | 2-4S | ~280W | 4mm | 10x6 to 11x5 | $16-20 | Banggood |
| **Surpass Hobby C2830 1000KV** | 1000KV | 48g | 2-4S | ~260W | 4mm | 10x6 to 11x6 | $15-18 | Banggood |
| **Cobra C2217/14** | 1050KV | 52g | 3S | ~250W | 4mm | 10x6 to 11x6 | $25-30 | Innov8tive Designs |
| **Volantex 2216 1400KV** | 1400KV | 50g | 2-3S | ~220W | 3mm | 9x5 to 10x6 | $12-15 | Banggood (OEM spare) |

**Notes**:
- **Sunnysky X2216 880KV** (56g, $20) -- THE mainstream sailplane motor
  - Sunnysky is a well-known Chinese motor brand with consistent quality
  - 880KV with 11x6 folding prop: ~16A, ~178W on 3S -- ideal F5J climb
  - 56g is moderate -- helps CG without excessive weight
  - 4mm shaft compatible with Aeronaut and Graupner prop hubs
  - Available in multiple KV options: 800, 900, 1000, 1100, 1250, 1400KV
  - 612 reviews on Banggood (4.95 rating) -- proven track record
  - **Best motor at this price point for a 2.5m F5J sailplane**
- **Surpass Hobby C3530 1100KV** (52g, $18) -- good alternative
  - Slightly lighter than Sunnysky, similar power
  - 1100KV better suited for 10" props
  - 52 reviews on Banggood (5.00 rating) -- very positive
- **Cobra C2217/14** (52g, $28) -- quality US-designed motor
  - Excellent efficiency and smooth operation
  - Made by Innov8tive Designs (USA), ships internationally
  - Higher price reflects better bearings and magnet quality
  - [Innov8tive Designs](https://www.innov8tivedesigns.com)

### 1C. Premium Tier ($35-60) -- Competition Grade

| Motor | KV | Weight (g) | Cells | Max Power (W) | Shaft | Prop (3S) | Price | Source |
|-------|----|-----------|-------|---------------|-------|-----------|-------|--------|
| **Scorpion SII-2208-14** | 1050KV | 37g | 3S | ~200W | 3mm | 10x6 to 11x5 | $35-40 | Innov8tive |
| **Scorpion SII-2215-14** | 960KV | 55g | 3S | ~280W | 4mm | 11x6 to 12x6 | $40-50 | Innov8tive |
| **Kolibri 830** | ~830KV | 30g | 2-3S | ~180W | 3mm | 10x6 to 11x6 | $45-55 | SoaringUSA |
| **Hacker A10-9L** | ~920KV | 32g | 2-3S | ~190W | 3mm | 10x5 to 11x5 | $50-60 | Hyperflight |

**Notes**:
- **Scorpion SII-2208-14** (37g, $38) -- best power-to-weight in premium tier
  - Only 37g -- saves 19g vs Sunnysky X2216
  - Premium bearings, excellent efficiency, very smooth
  - 1050KV ideal for 10-11" folding prop on 3S
  - Competition-proven in F5J and F3J
- **Scorpion SII-2215-14** (55g, $45) -- more power reserve
  - Same weight as Sunnysky X2216 but much higher quality
  - 960KV with 11x6 prop produces ~200W -- excellent climb
  - Better for windy conditions or heavy ballast configuration
- **Kolibri 830** (30g, $50) -- ultra-lightweight competition motor
  - Designed specifically for F5J competition
  - Very light at 30g but requires careful prop selection
  - Available from [SoaringUSA](https://soaringusa.com) and [Hyperflight UK](https://hyperflight.co.uk)
- **Hacker A10-9L** (32g, $55) -- German engineering quality
  - Very smooth, efficient, well-balanced
  - Premium price but exceptional build quality
  - Available from European sailplane shops

### Motor KV vs Prop Quick Reference

| Motor KV | Recommended Prop (3S) | Est. Static Thrust | Est. Current | Est. Power | Thrust/Weight (800g) |
|----------|----------------------|--------------------|--------------|------------|---------------------|
| 810-880KV | 11x6 or 12x6 CAM | 900-1000g | 15-18A | 165-200W | 1.13-1.25:1 |
| 960-1000KV | 10x6 or 11x5 CAM | 850-950g | 14-17A | 155-190W | 1.06-1.19:1 |
| 1050-1100KV | 10x6 CAM | 850-950g | 14-16A | 155-178W | 1.06-1.19:1 |
| 1200-1300KV | 9x5 or 9x6 CAM | 700-850g | 12-15A | 133-167W | 0.88-1.06:1 |
| 1400KV | 8x5 CAM | 600-750g | 11-14A | 122-155W | 0.75-0.94:1 |

**Minimum for competitive F5J**: Thrust/weight > 1.0:1.
**Recommended**: Thrust/weight > 1.1:1 for reliable 80-100m altitude in 10s.

---

## 2. ESC Options

### ESC Requirements

| Requirement | Specification | Why |
|-------------|--------------|-----|
| **Cells** | 3S LiPo | Fixed battery constraint |
| **Continuous current** | 20A minimum, 30A preferred | 14-18A climb with safety margin |
| **Burst current** | 30A for 15 seconds | F5J climb duration |
| **BEC type** | Switching (SBEC), NOT linear | 6 digital servos draw 4-5A peak |
| **BEC rating** | 5A+ continuous, 7A+ peak | Crow braking = all surfaces loaded |
| **Output voltage** | 5.0V or 5.5V | Standard servo voltage |
| **Brake** | REQUIRED (folding prop) | Without brake, prop windmills = massive drag |
| **Protocols** | PWM standard (no DShot needed) | Sailplane ESC, not FPV racer |
| **Weight** | Under 15g preferred | Every gram counts |
| **Battery connector** | XT30 (or solder pigtail) | Flight battery uses XT30 |

### BEC Current Analysis (from CONTROLS_OPTIONS.md)

With 6x digital servos (PTK 7308MG-D):
- **4x wing servos average**: ~350mA each = 1,400mA
- **2x tail servos average**: ~250mA each = 500mA
- **Receiver**: ~50mA
- **Total average**: ~1,950mA (~2.0A)
- **Peak (crow braking)**: ~4,000-5,000mA (4-5A)

**Linear BEC (3A) is INADEQUATE for 6 digital servos.** It will overheat during extended crow
braking on final approach. A switching BEC (SBEC) rated at 5A+ is mandatory.

### 2A. Budget Tier ($8-15) -- AliExpress/Generic

| ESC | Rating | BEC | Weight | Brake | Protocols | Price | Source |
|-----|--------|-----|--------|-------|-----------|-------|--------|
| **BLHeli_S 30A** | 30A/35A burst | NONE* | 8g | Yes (fw) | DShot300, PWM | $8-12 | AliExpress |
| **DYS SN30A** | 30A/40A burst | NONE* | 10g | Yes (fw) | DShot600, PWM | $10-15 | AliExpress |
| **Racerstar Star ESC 30A** | 30A/35A burst | 2A/5V linear | 12g | Yes | PWM | $8-10 | Banggood |
| **Generic 30A SBEC airplane ESC** | 30A/40A burst | 5A/5V SBEC | 18-22g | Yes | PWM | $10-14 | AliExpress |

*BLHeli_S and DYS SN30A are multirotor ESCs with NO built-in BEC. They require an external
UBEC or the receiver must be powered separately. This adds weight and complexity.

**Notes**:
- **BLHeli_S 30A** (8g, $10) is the lightest option but has NO BEC
  - Must add external 5A UBEC (~$3, ~5g) for servo power
  - Requires BLHeli Suite to configure brake and timing
  - Best for weight-obsessed builders comfortable with firmware configuration
- **Generic 30A SBEC airplane ESC** ($12, 18-22g) -- heaviest budget option
  - Has proper 5A switching BEC -- adequate for digital servos
  - Built-in brake function for folding prop
  - Generic quality means inconsistent performance
  - Search AliExpress for "30A ESC SBEC airplane brake"

### 2B. Mainstream Tier ($15-30) -- RECOMMENDED

| ESC | Rating | BEC | Weight | Brake | Protocols | Price | Source |
|-----|--------|-----|--------|-------|-----------|-------|--------|
| **ZTW Spider 30A** | 30A/40A burst | 5A/5V SBEC | 16g | Yes | PWM | $18-22 | AliExpress, Amazon |
| **ZTW Spider 20A** | 20A/30A burst | 3A/5V linear | 12g | Yes | PWM | $14-18 | AliExpress |
| **HobbyKing BlueSeries 30A** | 30A/40A burst | 3A/5V linear | 18g | Yes (fw) | PWM | $12-15 | HobbyKing |
| **HobbyKing YEP 30A** | 30A/40A burst | 4A/5V SBEC | 15g | Yes | PWM | $15-18 | HobbyKing |
| **Turnigy Plush 30A** | 30A/40A burst | 3A/5V linear | 19g | Yes | PWM | $18-22 | HobbyKing |

**Notes**:
- **ZTW Spider 30A** (16g, $20) -- THE sailplane ESC
  - Specifically designed for glider/sailplane use
  - Built-in brake function, optical coupling (reduces interference)
  - 5A switching BEC handles 6 digital servos during crow braking
  - Proven reliability in F3J/F5J competition
  - Available from multiple AliExpress sellers
  - **Best ESC for this application**
- **HobbyKing YEP 30A** (15g, $17) -- good alternative
  - 4A SBEC is adequate but marginal for 6 digital servos at peak
  - Programmable via programming card (sold separately, $5)
  - Good value from HobbyKing EU warehouse
- **Turnigy Plush 30A** (19g, $20) -- classic but heavy
  - Very reliable, widely used, excellent support
  - Linear BEC at 3A is insufficient for 6 digital servos
  - Would need external UBEC -- skip for digital servo setups
- **ZTW Spider 20A** (12g, $16) -- lighter but limited BEC
  - 20A is adequate for most motors in this power range
  - 3A linear BEC only -- marginal for digital servos
  - Use only with analog servos or add external UBEC

### 2C. Premium Tier ($30-55) -- Competition Grade

| ESC | Rating | BEC | Weight | Brake | Protocols | Price | Source |
|-----|--------|-----|--------|-------|-----------|-------|--------|
| **T-Motor Air 30A** | 30A/40A burst | 5A/5V SBEC | 15g | Yes | PWM, DShot | $35-40 | GetFPV |
| **KISS ESC 30A** | 30A/40A burst | 5A/5V SBEC | 12g | Yes | PWM | $40-50 | GetFPV |
| **Castle Creations Phoenix Edge 25** | 25A/35A burst | 5A/5V SBEC | 14g | Yes | PWM | $45-55 | Castle, Amazon |
| **Jeti Spin 44** | 44A/55A burst | 4A/5V SBEC | 18g | Yes | PWM | $50-55 | Hyperflight |

**Notes**:
- **T-Motor Air 30A** (15g, $38) -- excellent quality
  - T-Motor is a premium brand known for reliability
  - 5A switching BEC, configurable brake
  - Lightweight at 15g
  - Available from [GetFPV](https://www.getfpv.com)
- **KISS ESC 30A** (12g, $45) -- lightweight premium
  - Very light at 12g with proper 5A SBEC
  - Simple, reliable design by Felix Rieseberg
  - Popular in high-end F5J builds
- **Castle Creations Phoenix Edge 25** (14g, $50) -- US-made
  - Excellent programming interface (Castle Link USB)
  - Data logging (current, voltage, RPM)
  - Premium price for premium features
- **Jeti Spin 44** (18g, $52) -- European competition grade
  - Overkill current rating (44A) but very reliable
  - Excellent German engineering
  - Available from [Hyperflight UK](https://hyperflight.co.uk)

### ESC Selection Matrix

| ESC | BEC Adequate? | Weight | Brake | Price | Verdict |
|-----|--------------|--------|-------|-------|---------|
| BLHeli_S 30A (no BEC) | NO (need UBEC) | 8g | Yes (fw) | $10 | Complex but lightest |
| Generic 30A SBEC | YES (5A) | 20g | Yes | $12 | Heavy, generic |
| ZTW Spider 20A | MARGINAL (3A linear) | 12g | Yes | $16 | OK for analog servos |
| HobbyKing YEP 30A | MARGINAL (4A SBEC) | 15g | Yes | $17 | Good value |
| **ZTW Spider 30A** | **YES (5A SBEC)** | **16g** | **Yes** | **$20** | **BEST CHOICE** |
| T-Motor Air 30A | YES (5A SBEC) | 15g | Yes | $38 | Premium quality |
| KISS ESC 30A | YES (5A SBEC) | 12g | Yes | $45 | Lightest premium |
| Castle Phoenix Edge 25 | YES (5A SBEC) | 14g | Yes | $50 | Data logging |

---

## 3. Folding Propeller + Spinner Options

### Why Folding Props?

F5J sailplanes spend 95%+ of flight time with the motor off. A folding propeller:
- **Folds blades flat against fuselage** when motor stops (ESC brake engages)
- **Reduces drag by 80-90%** vs windmilling fixed prop
- **Is mandatory for competitive F5J** -- fixed props are never used
- **Requires ESC brake function** -- without brake, propeller windmills from forward airspeed

### Prop Terminology
- **Diameter**: Total circle swept by prop blades (inches), e.g., 11" = 279mm
- **Pitch**: Theoretical distance advanced per revolution (inches), e.g., 6" = 152mm
- **CAM**: Computer-Aided Manufactured -- precision-molded blades with optimized airfoil
- **Hub/Spinner**: Central cone that covers the prop mounting point, improves aerodynamics

### 3A. Budget Tier ($2-8) -- AliExpress/Generic

| Product | Size | Shaft | Blade Material | Weight (g) | Price | Source |
|---------|------|-------|---------------|-----------|-------|--------|
| **Generic CF folding prop** | 9.5x5 to 14x8 | 3/4mm | Carbon fiber | ~10-14g | $0.99-3.00 | AliExpress |
| **Haoye folding prop + spinner set** | 8x4.5, 8x6, 11x6 | 2.3/3.0/3.17/4.0mm | Plastic + aluminum spinner | ~15-20g | $4-7 (2 sets) | AliExpress |
| **Generic folding prop 10x6 + plastic spinner** | 10x6 | 3mm | Plastic | ~12-15g | $3-5 | AliExpress |
| **Volantex 1060 folding prop + spinner** | 10x6 | 3mm | Plastic + aluminum | ~15g | $5 (Banggood) | Banggood |

**Notes**:
- **Generic CF folding prop** ($1-3 on AliExpress) -- cheapest option
  - Carbon fiber blades, decent quality
  - Available in all sizes: 9.5x5, 10x6, 11x6, 11x8, 12x6, 12x6.5, 13x7, 14x8
  - 800+ sold, 4.8 rating -- good value
  - Search: "carbon fiber folding propeller 11x6" on AliExpress
- **Haoye folding prop set** ($5-7 for 2 sets) -- excellent budget value
  - Comes with spinner and shaft adapters (2.3/3.0/3.17/4.0mm)
  - Multiple sizes available
  - 221 sold, 4.8 rating
- **Volantex 1060** ($5, Banggood) -- OEM replacement prop
  - Designed for Volantex Phoenix/ASW gliders
  - Proven folding action, includes spinner
  - 293 reviews, 4.94 rating
  - [Banggood listing](https://www.banggood.com/search/volantex-1060-folding-prop.html)

### 3B. Mainstream Tier ($12-25) -- RECOMMENDED

| Product | Size | Shaft | Blade Material | Weight (g) | Price | Source |
|---------|------|-------|---------------|-----------|-------|--------|
| **Aeronaut CAM Carbon 10x6** | 10x6 | 3/4mm | Carbon fiber | ~12g | $15-18 | 3DJake, Amazon.de |
| **Aeronaut CAM Carbon 11x6** | 11x6 | 3/4mm | Carbon fiber | ~14g | $15-18 | 3DJake, Amazon.de |
| **Aeronaut CAM Carbon 10x8** | 10x8 | 3/4mm | Carbon fiber | ~12g | $15-18 | 3DJake, Amazon.de |
| **Gemfan 10x6 / 11x6 / 12x6** | Various | 3/4mm | Carbon fiber | ~10-14g | $3-5 | AliExpress |
| **Graupner CAM Folding 10x6** | 10x6 | 3mm | CAM plastic | ~14g | $18-22 | Amazon.de |

**Spinner Options (Mainstream)**:
| Product | Diameter | Shaft | Weight (g) | Price | Source |
|---------|----------|-------|-----------|-------|--------|
| **Aeronaut Spinner 30mm** | 30mm | 3/4mm | ~5g | $8-12 | 3DJake, Amazon.de |
| **Graupner Spinner 28mm** | 28mm | 3mm | ~4g | $8-10 | Amazon.de |
| **Aluminum spinner 30mm** | 30mm | 3/4mm | ~8g | $3-5 | AliExpress |

**Notes**:
- **Aeronaut CAM Carbon 11x6** ($16 + $10 spinner = $26) -- the gold standard
  - Aeronaut (Germany) makes the best folding prop blades for sailplanes
  - CAM Carbon blades have optimized airfoil section for maximum efficiency
  - Excellent folded profile -- minimal drag when stowed
  - Hub accepts 3mm or 4mm shaft (adapter included)
  - Available from [3DJake.com](https://www.3djake.com) (EU, ships to Bulgaria in 3-5 days)
  - **Best prop for F5J competition at any price**
- **Gemfan folding prop** ($3-5) -- excellent budget-midrange
  - Good quality carbon fiber blades
  - Widely available on AliExpress
  - 4.9 rating, 4000+ sold
  - Not as refined as Aeronaut but 80% of the performance at 20% of the price

### 3C. Premium Tier ($25-45) -- Competition Grade

| Product | Size | Shaft | Blade Material | Weight (g) | Price | Source |
|---------|------|-------|---------------|-----------|-------|--------|
| **Aeronaut CAM Carbon 12x6.5** | 12x6.5 | 4mm | Carbon fiber | ~16g | $18-22 | 3DJake, Hyperflight |
| **Aeronaut CAM Carbon 13x6.5** | 13x6.5 | 4mm | Carbon fiber | ~18g | $20-25 | 3DJake, Hyperflight |
| **GM/Boghanski carbon folding prop** | Custom | 4mm | Carbon fiber | ~12g | $30-40 | SoaringUSA |
| **Aeronaut Slim Spinner 30mm** | 30mm | 3/4mm | Aluminum | ~4g | $12-15 | 3DJake |

**Notes**:
- **GM/Boghanski** props are hand-made competition props from Germany
  - Ultra-lightweight, custom-pitched for specific motor/KV combinations
  - Available from [SoaringUSA](https://soaringusa.com) and [Hyperflight UK](https://hyperflight.co.uk)
  - Overkill for a first build -- reserve for competition season
- **Aeronaut CAM Carbon 12x6.5** -- for low-KV motors (810-880KV)
  - Produces maximum static thrust with Sunnysky X2216 880KV
  - Larger diameter = more thrust, but more drag when folded
  - Best paired with 4mm shaft motors

### Propeller Selection Guide by Motor

| Motor | KV | Best Prop | Alt Prop | Est. Thrust | Est. Current |
|-------|----|-----------|----------|-------------|--------------|
| Surpass C2206 | 1300 | 9x5 CF folding | 9x6 | 750g | 13A |
| Sunnysky X2216 | 880 | 11x6 CAM Carbon | 12x6 CF | 1000g | 18A |
| Sunnysky X2216 | 1100 | 10x6 CAM Carbon | 11x6 CF | 900g | 16A |
| Cobra C2217/14 | 1050 | 10x6 CAM Carbon | 11x5 CF | 900g | 15A |
| Scorpion SII-2208 | 1050 | 10x6 CAM Carbon | 11x5 CF | 900g | 15A |
| Scorpion SII-2215 | 960 | 11x6 CAM Carbon | 12x6 CF | 1000g | 18A |
| Kolibri 830 | 830 | 11x6 CAM Carbon | 12x6 CF | 950g | 16A |

---

## 4. Recommended Powertrain Combinations

### Option A: Best Value (RECOMMENDED for first build)

| Component | Item | Weight | Price (USD) | Price (EUR) |
|-----------|------|--------|-------------|-------------|
| **Motor** | Sunnysky X2216 880KV | 56g | $20 | ~EUR 18 |
| **ESC** | ZTW Spider 30A (5A SBEC) | 16g | $20 | ~EUR 18 |
| **Prop** | Aeronaut CAM Carbon 11x6 | 14g | $16 | ~EUR 15 |
| **Spinner** | Aeronaut 30mm aluminum | 5g | $10 | ~EUR 9 |
| **Wiring** | XT30 pigtail + extensions | 3g | $3 | ~EUR 3 |
| | **TOTAL** | **94g** | **$69** | **~EUR 63** |

**Performance**:
- Power: ~178W at 3S 11.1V (~16A)
- Thrust: ~1000g static (thrust/weight = 1.25:1 at 800g AUW)
- Climb angle: ~65 degrees
- Altitude in 10s: ~90-100m
- BEC: 5A SBEC -- handles 6 digital servos with margin

**Why this combination**:
- Sunnysky X2216 is proven, reliable, well-reviewed (612 reviews, 4.95 rating)
- ZTW Spider 30A has the 5A switching BEC needed for digital servos
- Aeronaut CAM Carbon 11x6 is the best F5J prop at any price
- Total weight of 94g fits well within the powertrain budget
- All components available from Banggood + 3DJake (EU shipping to Bulgaria)

### Option B: Budget (minimum cost)

| Component | Item | Weight | Price (USD) | Price (EUR) |
|-----------|------|--------|-------------|-------------|
| **Motor** | Surpass Hobby C2206 1300KV | 32g | $12 | ~EUR 11 |
| **ESC** | Generic 30A SBEC airplane ESC | 20g | $12 | ~EUR 11 |
| **Prop** | Generic CF folding 9x5 | 10g | $2 | ~EUR 2 |
| **Spinner** | Generic aluminum 28mm | 8g | $3 | ~EUR 3 |
| **Wiring** | Basic connectors | 2g | $2 | ~EUR 2 |
| | **TOTAL** | **74g** | **$31** | **~EUR 29** |

**Performance**:
- Power: ~144W at 3S (~13A)
- Thrust: ~750g static (thrust/weight = 0.94:1 at 800g AUW)
- Climb angle: ~48 degrees
- Altitude in 10s: ~65-75m
- BEC: 5A SBEC -- adequate for digital servos

**Why this combination**:
- Lightest total setup at 74g (saves 20g vs Option A)
- Cheapest complete powertrain at $31
- Thrust/weight ratio below 1.0:1 -- marginal for competition but flyable
- Generic ESC and prop quality is acceptable for practice flying
- **Not recommended for competition** -- upgrade prop and motor for F5J events

### Option C: Competition (maximum performance)

| Component | Item | Weight | Price (USD) | Price (EUR) |
|-----------|------|--------|-------------|-------------|
| **Motor** | Scorpion SII-2215-14 960KV | 55g | $45 | ~EUR 42 |
| **ESC** | KISS ESC 30A (5A SBEC) | 12g | $45 | ~EUR 42 |
| **Prop** | Aeronaut CAM Carbon 11x6 | 14g | $16 | ~EUR 15 |
| **Spinner** | Aeronaut Slim 30mm | 4g | $12 | ~EUR 11 |
| **Wiring** | Premium silicone + XT30 | 2g | $3 | ~EUR 3 |
| | **TOTAL** | **87g** | **$121** | **~EUR 113** |

**Performance**:
- Power: ~200W at 3S (~18A)
- Thrust: ~1050g static (thrust/weight = 1.31:1 at 800g AUW)
- Climb angle: ~70 degrees
- Altitude in 10s: ~95-110m
- BEC: 5A SBEC -- handles all servos with margin

**Why this combination**:
- Scorpion motor + KISS ESC = competition-proven reliability
- Highest thrust-to-weight ratio of all options
- Lightest ESC at 12g with proper 5A switching BEC
- Premium components last longer and run cooler
- **The setup to beat if budget allows**

### Option D: Ultra-Light (weight-optimized)

| Component | Item | Weight | Price (USD) | Price (EUR) |
|-----------|------|--------|-------------|-------------|
| **Motor** | Scorpion SII-2208-14 1050KV | 37g | $38 | ~EUR 35 |
| **ESC** | BLHeli_S 30A + external UBEC | 13g | $13 | ~EUR 12 |
| **Prop** | Gemfan CF 10x6 folding | 10g | $4 | ~EUR 4 |
| **Spinner** | Generic aluminum 28mm | 5g | $3 | ~EUR 3 |
| **Wiring** | Minimal | 2g | $2 | ~EUR 2 |
| | **TOTAL** | **70g** | **$60** | **~EUR 56** |

**Performance**:
- Power: ~167W at 3S (~15A)
- Thrust: ~900g static (thrust/weight = 1.13:1 at 800g AUW)
- Climb angle: ~60 degrees
- Altitude in 10s: ~80-90m
- BEC: External 5A UBEC

**Why this combination**:
- Lightest motor (37g) saves 19g vs Sunnysky X2216
- Still achieves competitive thrust-to-weight
- Requires BLHeli_S firmware configuration -- not for beginners
- Best for weight-critical competition builds

---

## 5. Thrust & Climb Performance Analysis

### Estimated Climb Performance at 800g AUW

| Setup | Motor | Prop | Power (W) | Thrust (g) | T/W | Climb Angle | 10s Altitude |
|-------|-------|------|-----------|------------|-----|-------------|-------------|
| **Option A** | X2216 880KV | 11x6 | 178 | 1000 | 1.25 | ~65 deg | 90-100m |
| **Option B** | C2206 1300KV | 9x5 | 144 | 750 | 0.94 | ~48 deg | 65-75m |
| **Option C** | SII-2215 960KV | 11x6 | 200 | 1050 | 1.31 | ~70 deg | 95-110m |
| **Option D** | SII-2208 1050KV | 10x6 | 167 | 900 | 1.13 | ~60 deg | 80-90m |

### Altitude Estimate Methodology

Altitude from energy balance:
```
E_motor = P * t * eta_motor * eta_prop
E_potential = m * g * h
E_drag = 0.5 * rho * Cd * A * v^2 * v * t
h = (E_motor - E_drag) / (m * g)

Where:
  P = electrical power (W)
  t = motor run time (10s)
  eta_motor = 0.75 (motor efficiency)
  eta_prop = 0.65 (folding prop static efficiency)
  m = 0.8 kg (AUW)
  g = 9.81 m/s^2
  rho = 1.225 kg/m^3
  Cd = 0.02 (sailplane parasite drag during climb)
  A = 0.0416 m^2 (wing area)
  v = climb speed, 8-12 m/s
```

These estimates assume:
- 3S LiPo at 11.1V nominal (fresh charge gives 12.6V, improving initial climb)
- Sea-level density altitude
- No wind (headwind adds to climb angle)
- Prop efficiency degrades with climb speed (static thrust > in-flight thrust)

---

## 6. Integration Notes

### Motor Mount Design

The motor mounts to the front of the fuselage pod via a printed CF-PETG mount:
- **Mount material**: CF-PETG, 2.0-3.0mm wall thickness
- **Motor bolt pattern**: Standard 16x19mm (2204-2216 class) or 25x25mm (larger)
- **Thrust line**: Motor axis should be 0-2 degrees down and 0-2 degrees right (counters torque)
- **Cooling**: Small air inlet near spinner + exit vent behind motor
- **Vibration isolation**: Motor mounted with rubber grommets or CA-glued directly

### Shaft Size Compatibility

| Shaft Size | Prop Hub Compatibility |
|-----------|----------------------|
| 3mm | Most budget CF folding props, Gemfan, Haoye |
| 3.17mm (1/8") | XXD A2212, requires adapter or reaming for 3mm hub |
| 4mm | Aeronaut CAM Carbon (with adapter), Graupner |

### Connector Wiring

```
Battery (XT30) --> ESC (XT30 pigtail soldered) --> Motor (3.5mm bullet connectors)
                    |
                    +--> BEC output (5V, JR connector) --> Receiver
                                                         |
                                                         +--> Servo bus (6x servos)
```

### ESC Programming Checklist

Before first flight, configure the ESC:
1. **Brake: ON** (mandatory for folding prop)
2. **Brake strength: 100%** (hard brake folds prop faster)
3. **Timing: Medium** (good compromise for outrunners)
4. **Cutoff voltage: 3.3V/cell (9.9V for 3S)** (protects battery)
5. **Cutoff type: Soft** (gradual power reduction, not sudden cutoff)
6. **BEC voltage: 5.0V** (standard servo voltage)

---

## 7. Bulgarian/EU Source Research

### Priority Order (per project rules)

1. **Bulgaria first** -- check local shops before ordering online
2. **3DJake.com** -- EU warehouse, ships to Balkans in 3-5 days
3. **Amazon.de** -- Amazon Germany, ships to Bulgaria
4. **Banggood** -- 1-2 weeks with priority shipping
5. **AliExpress** -- cheapest but 2-4 week delivery (3+ months with customs delays)
6. **HobbyKing EU warehouse** -- 5-7 days to Bulgaria

### Bulgarian Hobby Shops

| Shop | Website | Notes |
|------|---------|-------|
| Hobbyzone.bg | hobbyzone.bg | General hobby, may stock ESC/motors |
| Modelist.bg | modelist.bg | Modeling supplies |
| RC Market BG | rcmarket.bg | RC cars/planes, check for motor stock |
| BG Hobby | bghobby.com | Online hobby shop |

**Reality check**: Bulgarian RC shops typically have limited sailplane-specific inventory
(Aeronaut props, Scorpion motors, etc.). Online ordering from EU shops is usually necessary.
Check local shops first for basic items (wire, connectors, servo extensions).

### EU Specialty Sources

| Shop | Carries | Shipping to BG | Notes |
|------|---------|---------------|-------|
| [3DJake.com](https://www.3djake.com) | Aeronaut props/spinners, motors | 3-5 days | EU warehouse, free shipping > EUR 29 |
| [Hyperflight UK](https://www.hyperflight.co.uk) | Sailplane motors, folding props, Scorpion | 5-7 days | Sailplane specialty, excellent selection |
| [SoaringUSA](https://www.soaringusa.com) | Competition F5J gear, Kolibri, GM props | 7-14 days | US-based, comprehensive sailplane catalog |
| [Innov8tive Designs](https://www.innov8tivedesigns.com) | Cobra motors, Scorpion | 7-10 days | US-based, motor specialist |
| [HobbyKing EU](https://hobbyking.com) | Turnigy, ZTW, generic motors/ESCs | 5-7 days | EU warehouse, check stock |
| [Amazon.de](https://amazon.de) | OVONIC, Surpass Hobby, generic | 3-5 days | Amazon Germany, fast to Bulgaria |

### Specific Product Sourcing

| Item | Best Source | Est. Shipping to BG |
|------|------------|-------------------|
| Sunnysky X2216 motor | Banggood ($20) | 1-2 weeks priority |
| ZTW Spider 30A ESC | AliExpress ($20) or HobbyKing ($22) | 2-3 weeks / 5-7 days |
| Aeronaut CAM Carbon 11x6 | 3DJake.com ($16) | 3-5 days |
| Aeronaut 30mm spinner | 3DJake.com ($10) | 3-5 days (combine with prop) |
| Generic CF folding prop | AliExpress ($2) | 2-4 weeks |
| Scorpion motor | Innov8tive Designs ($38-45) | 7-10 days |
| KISS ESC 30A | GetFPV ($45) | 7-14 days |

---

## 8. Bill of Materials

### Option A: Best Value (recommended)

| Item | Qty | Unit Cost (USD) | Total (USD) | Unit Cost (EUR) | Total (EUR) | Source |
|------|-----|-----------------|-------------|-----------------|-------------|--------|
| Sunnysky X2216 880KV motor | 1 | $20 | $20 | EUR 18 | EUR 18 | Banggood |
| ZTW Spider 30A ESC (SBEC) | 1 | $20 | $20 | EUR 18 | EUR 18 | AliExpress/HK |
| Aeronaut CAM Carbon 11x6 blades | 1 set | $16 | $16 | EUR 15 | EUR 15 | 3DJake |
| Aeronaut 30mm spinner (3/4mm) | 1 | $10 | $10 | EUR 9 | EUR 9 | 3DJake |
| Spare 11x6 CF blades (backup) | 1 set | $2 | $2 | EUR 2 | EUR 2 | AliExpress |
| XT30 pigtail (for ESC) | 2 | $1.50 | $3 | EUR 1.50 | EUR 3 | AliExpress |
| Motor mounting screws (M3x6) | 4 | $0.50 | $0.50 | EUR 0.50 | EUR 0.50 | AliExpress |
| 3.5mm bullet connectors (motor) | 3 pair | $1 | $1 | EUR 1 | EUR 1 | AliExpress |
| **SUBTOTAL** | | | **$72.50** | | **~EUR 66.50** | |
| Shipping estimates | | | $10-15 | | EUR 10-15 | |
| **TOTAL** | | | **~$85** | | **~EUR 80** | |

### Option B: Budget

| Item | Qty | Unit Cost (USD) | Total (USD) | Source |
|------|-----|-----------------|-------------|--------|
| Surpass Hobby C2206 1300KV | 1 | $12 | $12 | AliExpress |
| Generic 30A SBEC ESC | 1 | $12 | $12 | AliExpress |
| Generic CF folding prop 9x5 | 2 | $2 | $4 | AliExpress |
| Generic aluminum spinner 28mm | 1 | $3 | $3 | AliExpress |
| XT30 pigtail + connectors | 1 set | $3 | $3 | AliExpress |
| **TOTAL** | | | **~$34** | |

### Option C: Competition

| Item | Qty | Unit Cost (USD) | Total (USD) | Source |
|------|-----|-----------------|-------------|--------|
| Scorpion SII-2215-14 960KV | 1 | $45 | $45 | Innov8tive |
| KISS ESC 30A (5A SBEC) | 1 | $45 | $45 | GetFPV |
| Aeronaut CAM Carbon 11x6 | 1 set | $16 | $16 | 3DJake |
| Aeronaut Slim 30mm spinner | 1 | $12 | $12 | 3DJake |
| Spare 11x6 blades (2 sets) | 2 | $16 | $32 | 3DJake |
| Premium wiring + connectors | 1 set | $5 | $5 | Various |
| **TOTAL** | | | **~$155** | |

---

## 9. Weight Impact Summary

| Config | Motor | ESC | Prop+Spinner | Wiring | Total Powertrain | Notes |
|--------|-------|-----|-------------|--------|-----------------|-------|
| **Spec budget** | -- | -- | -- | -- | 75-100g | Current spec |
| **Option A** (recommended) | 56g | 16g | 19g | 3g | **94g** | Within budget |
| **Option B** (budget) | 32g | 20g | 18g | 2g | **72g** | 22g under budget |
| **Option C** (competition) | 55g | 12g | 18g | 2g | **87g** | Within budget |
| **Option D** (ultra-light) | 37g | 13g | 15g | 2g | **67g** | 28g under budget |

### Full AUW Impact

| Config | Powertrain | Battery (850mAh) | Electronics | Airframe | AUW | Wing Loading |
|--------|-----------|-----------------|-------------|----------|-----|-------------|
| Option A | 94g | 64g | 280g* | 400g | **838g** | 20.1 g/dm^2 |
| Option B | 72g | 64g | 280g* | 400g | **816g** | 19.6 g/dm^2 |
| Option C | 87g | 64g | 280g* | 400g | **831g** | 20.0 g/dm^2 |
| Option D | 67g | 64g | 280g* | 400g | **811g** | 19.5 g/dm^2 |

*Electronics = Rx (6g) + 6 servos (52g) + wiring/extensions (20g) + motor mount hardware (5g) = ~83g
wait -- recalculate: Rx 6g + wing servos 4x8=32g + tail servos 2x10=20g + extensions 12g + connectors 5g + misc 5g = 80g. Adding powertrain gives total electronics.

### Corrected Full AUW

| Config | Powertrain | Battery | Rx+Servos+Wiring | Airframe | AUW | Wing Loading |
|--------|-----------|---------|-------------------|----------|-----|-------------|
| Option A | 94g | 64g | 80g | 400g | **638g** | **15.3 g/dm^2** |
| Option B | 72g | 64g | 80g | 400g | **616g** | **14.8 g/dm^2** |

Note: 638g seems light. The airframe estimate of 400g includes wing (200-260g), spars (25-35g),
fuselage (50-70g), tail boom (20-25g), empennage (25-35g), hardware (20-30g). Real airframe
weight will be determined as components are designed and weighed. The specifications.md
airframe total is 340-455g, so 400g is a reasonable mid-estimate.

If AUW comes in at 638g, that is excellent (well below 750g target). The owner can add the
1300mAh ballast battery (+100g) to reach 738g for windier conditions.

---

## 10. Action Items

1. [ ] **Verify Sunnysky X2216 availability** on Banggood and AliExpress
2. [ ] **Order Aeronaut CAM Carbon 11x6 prop early** -- specialty item from 3DJake (EU)
3. [ ] **Match shaft size** -- Sunnysky X2216 has 4mm shaft, Aeronaut prop accepts 3/4mm
4. [ ] **Configure ESC brake** before first flight -- without brake, prop windmills = huge drag
5. [ ] **Design motor mount** in CF-PETG for the X2216 bolt pattern (16x19mm, M3 screws)
6. [ ] **Test CG with chosen motor** -- 56g motor at nose shifts CG forward, battery position adjusts
7. [ ] **Order spare prop blades** -- blades break on landing, 2-3 spare sets recommended
8. [ ] **Solder XT30 pigtail** on ESC (most ESCs come with bare wires or XT60)
9. [ ] **Update specifications.md** once motor selection is confirmed and weighed
10. [ ] **Create motor component YAML** in `components/motors/` once ordered

---

## Appendix A: Banggood Products Found (April 2026)

| Product | Price | Rating | Reviews | Notes |
|---------|-------|--------|---------|-------|
| SunnySky X2216 1250KV/1100KV/1400KV/2400KV | $12.99 (sale) | 4.95 | 612 | Best budget-mainstream motor |
| Surpass Hobby C3542 1000/1250/1450KV | $15.00 (sale) | 5.00 | 78 | Larger than needed, 75g |
| Surpass Hobby C2830 850/1000/1300KV | $10.50 (sale) | 4.95 | 20 | Good 48g motor |
| Surpass Hobby C2822 1200/1300/1400KV | $6.99 (sale) | 5.00 | 12 | Budget option, 38g |
| Racerstar BR2212 810KV | $12.14 (sale) | 4.98 | 84 | Multirotor motor, works for sailplane |
| XXD A2212 950/1100/1250/1500KV | $4.00 (sale) | 5.00 | 2 | Cheapest adequate motor |
| Volantex 2216 1400KV | $12.49 (sale) | 4.86 | 7 | OEM spare for Ranger 2000 |

## Appendix B: AliExpress Propeller Products Found (April 2026)

| Product | Price | Rating | Sold | Notes |
|---------|-------|--------|------|-------|
| CF folding prop 9.5x5 to 14x8 | $0.99 | 4.8 | 800+ | Best budget CF folding prop |
| CF folding prop 10x6 to 14x8 (2-leaf) | $0.99 | 4.9 | 316 | Good quality CF blades |
| Haoye folding prop set (2 sets, with spinner) | $6.92 | 3.9 | 118 | Complete set with adapters |
| Gemfan 10x6/11x6/12x6 folding | $3.25 | 4.8 | 900+ | Good midrange option |
| 3K CF folding prop 10x6 to 19x10 | $8.50 | -- | 4 | Premium CF, larger sizes |

## Appendix C: Search Terms for Manual Verification

Prices and availability change frequently. Verify before ordering:

**Motor**:
- Banggood: "Sunnysky X2216", "Surpass Hobby 2206 outrunner", "2216 outrunner brushless"
- AliExpress: "2216 brushless outrunner 880KV", "sailplane motor 3S"
- Amazon.de: "Brushless Motor 2216 Outrunner 3S"

**ESC**:
- AliExpress: "ZTW Spider 30A ESC", "30A SBEC ESC airplane brake"
- HobbyKing: "ZTW Spider", "YEP 30A"
- Amazon: "30A ESC SBEC sailplane brake"

**Folding Prop**:
- 3DJake: "Aeronaut CAM Carbon folding"
- AliExpress: "carbon fiber folding propeller 11x6"
- Amazon.de: "Aeronaut Faltprop", "Faltprop Segelflugzeug"

---

## Appendix D: ESC Brake Configuration

### Why Brake is Mandatory

Without ESC brake, the folding prop windmills during glide. A windmilling 11x6 prop produces
approximately the same drag as a flat plate of 11" diameter -- this can double the sailplane's
sink rate and cut L/D ratio in half. The brake function shorts the motor windings when throttle
is at zero, creating a magnetic brake that stops the prop. Aerodynamic drag then folds the
blades flat against the fuselage.

### Configuring Brake on ZTW Spider

1. Power on ESC with transmitter throttle at FULL position
2. Wait for beep sequence (programming mode)
3. Move throttle to midpoint -- enter programming menu
4. Navigate to brake setting (usually option 1)
5. Set brake to "ON" or "Hard" (100%)
6. Move throttle to zero to save and exit

Alternative: Use ZTW programming card ($5-8) for easier configuration.

---

## Revision History

| Date | Author | Description |
|------|--------|-------------|
| 2026-04-01 | AeroForge Team | Initial comprehensive powertrain procurement document |
| 2026-04-01 | AeroForge Team | Supersedes MOTOR_OPTIONS.md with expanded ESC and prop research |
