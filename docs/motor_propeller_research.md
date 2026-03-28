# Motor & Folding Propeller Research for AeroForge F5J Sailplane

## Requirements Summary

| Parameter | Value |
|-----------|-------|
| Wingspan | 2560mm |
| Target AUW | 750-850g |
| Battery | 3S 1300mAh 75C (11.1V nominal) |
| Motor run | 30 seconds max (F5J altitude penalty rules) |
| Target altitude | 80-120m in ~10 seconds |
| Pod nose diameter | ~32mm spinner |
| Motor shaft clearance | Must fit 28-32mm pod bore |

---

## 1. KV Rating Analysis for 3S 2.5m F5J

For a 2.5m F5J glider on 3S (11.1V nominal, ~12.6V full charge):

- **Optimal KV range: 900-1100 KV**
- Lower KV (~900) = more torque, swings larger props (11x6, 11x7), lower current draw, gentler climb
- Higher KV (~1100) = faster RPM, works with smaller props (10x6), higher current, more aggressive climb
- For our 750-850g AUW with 1300mAh 75C pack (max 97.5A burst, but we want ~15-20A sustained), **~1000 KV is the sweet spot**

**Key principle**: At 1000 KV on 3S (11.1V), the motor spins ~11,100 RPM unloaded. With a folding prop load, expect 7000-8500 RPM under load, which matches the efficient operating range for 10-11" props.

---

## 2. Motor Candidates (Ranked by Suitability)

### TIER 1: Competition-Grade (Best Performance)

#### Hacker A20-22L EVO kv924 -- RECOMMENDED
| Spec | Value |
|------|-------|
| KV | 924 RPM/V |
| Weight | 55g |
| Diameter | 28mm |
| Length | 34mm (body) |
| Shaft | 3mm |
| Max power | 200W (15 sec bursts) |
| Idle current (8.4V) | 0.75A |
| Internal resistance | 0.109 Ohm |
| Max LiPo | 3S |
| ESC recommendation | 20-30A |
| Mounting | Front or back mount, cross-mount |
| Recommended props | APC SF 10x4.7 (17A/187W), ACC 11x6 (15A/165W) on 3S |
| Price | ~EUR 65-75 (EVO), ~EUR 75 (Competition variant) |
| Suitability | "Gliders up to 900g" -- perfect for our 750-850g |

**Why this motor**: The gold standard for sub-900g F5J gliders. Used by Vladimirs Models Introduction F5J (2.9m) as the primary recommendation paired with CamCarbon 11x6 prop. The 924 KV on 3S gives ~10,250 RPM unloaded, loads to ~7500 RPM with 11x6 prop. Very efficient, well-proven in competition.

#### Hacker A20-20L EVO kv1022 -- ALTERNATIVE
| Spec | Value |
|------|-------|
| KV | 1022 RPM/V |
| Weight | 55g |
| Diameter | 28mm |
| Length | 34mm (body) |
| Shaft | 3mm |
| Max power | 200W (15 sec bursts) |
| Idle current (8.4V) | 0.85A |
| Internal resistance | 0.089 Ohm |
| Max LiPo | 3S |
| Recommended props | APC SF 10x4.7 (19A/209W), ACC 10x6 (16A/176W) on 3S |
| Price | ~EUR 65-75 |
| Suitability | Slightly higher KV, more aggressive climb, smaller prop |

**Why consider**: Higher KV gives more aggressive climb with smaller 10x6 prop. Lower resistance (0.089 vs 0.109) means slightly more efficient. Choose this if you want a quicker 10-second burst to altitude with a smaller prop diameter.

### TIER 2: Excellent Value (Competition-Capable)

#### Scorpion SII-2208-1100KV (V2)
| Spec | Value |
|------|-------|
| KV | 1100 RPM/V |
| Weight | 45g |
| Diameter | 27.9mm (outside) |
| Length | 26mm (body), 45mm (overall shaft) |
| Shaft | 2.98mm (~3mm) |
| Max continuous current | 12A |
| Max continuous power | 133W |
| Internal resistance | 0.17 Ohm |
| Max LiPo | 3S |
| Stator | 22x8mm (12-arm, 14-pole) |
| Mounting | 22mm cross-mount, M5x0.8 adapter thread |
| Price | ~USD 60 / EUR 45 |

**Why consider**: Lightest option at 45g -- saves 10g vs Hacker. Excellent quality (0.2mm laminations). But lower continuous power (133W vs 200W) means it works harder during climb. The 8mm stator thickness (vs 12mm on the 2212) limits sustained power. Best for lighter builds targeting 750g.

#### Scorpion SII-2212-960KV (V2)
| Spec | Value |
|------|-------|
| KV | 960 RPM/V |
| Weight | 58g |
| Diameter | 27.9mm (outside) |
| Length | 30mm (body), 49mm (overall shaft) |
| Shaft | 2.98mm (~3mm) |
| Max continuous current | 13A |
| Max continuous power | 192W |
| Internal resistance | 0.139 Ohm |
| Max LiPo | 4S |
| Stator | 22x12mm (12-arm, 14-pole) |
| Mounting | Cross-mount, M5x0.8 adapter thread |
| Price | ~USD 65-70 |

**Why consider**: Longer stator (12mm) = more copper = more sustained power (192W). Closer to the Hacker in power. The 960 KV is perfect for 11x6 or 11x7 props on 3S. 4S capable gives future upgrade path. 13g heavier than the 2208 but more robust.

### TIER 3: Budget Options

#### Turnigy D2830-11 1000KV
| Spec | Value |
|------|-------|
| KV | 1000 RPM/V |
| Weight | 54g |
| Diameter | 28mm (can), 32mm (with mount) |
| Length | 28mm (body), 48mm (overall with shaft) |
| Shaft | 3mm (15.8mm front shaft) |
| Max power | 210W |
| Max current | 21A |
| Max LiPo | 3S |
| Recommended props | 9x6 to 10x4.7 |
| Thrust | 500-900g |
| Price | ~USD 8-12 (HobbyKing) |

**Why consider**: Incredibly cheap. Will get you flying for testing. Known to work on 500-800g models. Quality is inconsistent -- bearings may fail, magnets may loosen. NOT for competition, but excellent for prototyping.

#### AXi 2212/26 V2 Long (920 KV)
| Spec | Value |
|------|-------|
| KV | 920 RPM/V |
| Weight | 59g (with cables) |
| Diameter | 27.7mm |
| Length | 39.4mm |
| Shaft | 3.17mm |
| Max LiPo | 3S |
| Recommended props | 7-11" range |
| Price | ~USD 70-85 |

**Why consider**: Czech-made (Model Motors), legendary quality. 3.17mm shaft is slightly non-standard (most spinners need 3mm). The 39.4mm body length is longer than competitors -- check pod clearance.

---

## 3. Folding Propeller Recommendations

### Prop Size Selection

For our setup (3S, ~1000 KV motor, 750-850g AUW):

| Prop Size | Best With | Climb Character | Current Draw (3S) | Notes |
|-----------|-----------|-----------------|-------------------|-------|
| **10x6** | 1000-1100 KV | Moderate, efficient | ~15-17A | Conservative, good for 800g+ |
| **11x6** | 900-1000 KV | Strong, balanced | ~15-18A | **Best all-round for our build** |
| **11x7** | 900 KV | Aggressive climb | ~18-22A | Maximum altitude gain |
| **10x8** | 1000-1100 KV | Fast pitch, low diameter | ~16-19A | Alternative to 11x6 |

### Aeronaut CAM Carbon Z Folding Blades -- RECOMMENDED

The industry standard for F5J competition. CAD-designed, carbon fiber reinforced nylon.

| Feature | Specification |
|---------|--------------|
| Material | Carbon fiber + nylon composite |
| Blade root width | 8mm |
| Fixing hole | 3mm |
| Max RPM (11x6) | ~13,000 |
| Compatible spinners | All 8mm-root spinners (GM, CN, Aeronaut, Graupner, RFM, Vitaprop) |
| Sizes for our build | **11x6** (primary), 10x6 (backup), 11x7 (aggressive) |
| Price | ~EUR 15-20 per pair of blades |

Available sizes relevant to us: 10x6, 10x7, 10x8, 11x4, 11x5, **11x6**, 11x7, 11x8.

**Note**: The specified prop size assumes a 42mm center piece (yoke). Smaller or larger yokes change the effective diameter and pitch slightly.

### APC Slow Fly Folding Props -- BUDGET ALTERNATIVE

APC offers folding props but they are less common in F5J competition. The APC SF 10x4.7 is specifically listed in Hacker motor datasheets. Cheaper (~USD 8-12) but heavier and less refined than Aeronaut CAM.

---

## 4. Spinner Selection

### GM F5J Carbon Spinner 30mm -- RECOMMENDED

| Feature | Specification |
|---------|--------------|
| Diameter | 30mm |
| Weight | ~13g |
| Material | Carbon fiber cone, 7075 aluminum CNC yoke |
| Shaft sizes available | 3mm, 3.17mm, 4mm, 5mm, 6mm |
| Blade root compatibility | 8mm (fits Aeronaut CAM, GM, CN, Vitaprop, etc.) |
| Mounting | Split collet (no shaft flats needed) or direct collet |
| Assembly | Carbon cone + alloy yoke + 2 steel hinge pins + hex retaining screw |
| Price | ~EUR 40-50 |

**For our build**: GM F5J 30/3mm (for Hacker/Scorpion 3mm shaft) or 30/3.17mm (for AXi).

### Aeronaut Turbo Spinner 30mm -- ALTERNATIVE

Available in 30mm diameter for 6mm shafts (too large for our motors). Not suitable unless using an adapter.

### GM F5J 32mm Spinner

Available for 5mm shafts. Only useful if we pick a motor with a larger shaft. The Joy F5J 2.5m recommends a 32mm spinner -- our pod nose is spec'd at ~32mm, so either 30mm or 32mm works depending on pod design.

---

## 5. Complete Power System Recommendations

### PRIMARY RECOMMENDATION: Hacker + Aeronaut + GM

| Component | Model | Weight | Price (approx) |
|-----------|-------|--------|----------------|
| Motor | Hacker A20-22L EVO kv924 | 55g | EUR 70 |
| Prop blades | Aeronaut CAM Carbon Z 11x6 | ~8g (pair) | EUR 18 |
| Spinner | GM F5J Carbon 30/3mm | ~13g | EUR 45 |
| ESC | 20-30A BLHeli (any quality brand) | ~15g | EUR 15-25 |
| **Total power system** | | **~91g** | **~EUR 150** |

**Expected performance on 3S 1300mAh 75C:**
- Static thrust: ~600-700g (near 1:1 thrust/weight at 800g AUW)
- Climb current: ~15-17A
- Power: ~165-187W
- RPM under load: ~7500
- Climb rate: ~8-10 m/s
- Time to 100m: ~10-12 seconds
- Motor run capacity: 1300mAh at 17A = ~4.5 minutes total (but we only need 30 sec)

### BUDGET RECOMMENDATION: Scorpion + Aeronaut + GM

| Component | Model | Weight | Price (approx) |
|-----------|-------|--------|----------------|
| Motor | Scorpion SII-2208-1100KV | 45g | EUR 45 |
| Prop blades | Aeronaut CAM Carbon Z 10x6 | ~7g (pair) | EUR 16 |
| Spinner | GM F5J Carbon 30/3mm | ~13g | EUR 45 |
| ESC | 20A BLHeli | ~12g | EUR 12 |
| **Total power system** | | **~77g** | **~EUR 118** |

### PROTOTYPE/TEST RECOMMENDATION: Turnigy + APC

| Component | Model | Weight | Price (approx) |
|-----------|-------|--------|----------------|
| Motor | Turnigy D2830-11 1000KV | 54g | EUR 10 |
| Prop blades | APC SF 10x4.7 folding | ~10g | EUR 10 |
| Spinner | Generic 30mm plastic | ~8g | EUR 5 |
| ESC | 20A generic | ~15g | EUR 8 |
| **Total power system** | | **~87g** | **~EUR 33** |

---

## 6. Reference: What Commercial 2.5m F5J Gliders Use

| Glider | Wingspan | AUW | Motor | Prop | Battery |
|--------|----------|-----|-------|------|---------|
| Joy F5J (HQ Composites) | 2.5m | 650g (light) | 2830 ~1000KV | 10x6 folding | 3S 800mAh |
| Geronimo 2 F5J | 2.5m | ~700g | Dualsky XM2208ECO 1800KV | Aeronaut 9.5x5 - 10x6 | **2S** 900mAh |
| Introduction F5J | 2.9m | 920-1000g | Hacker A20-22L EVO | CamCarbon 11x6 | 3S 1300mAh |
| GT2400 F5J (RedWingRC) | 2.4m | ~800g | Scorpion class | 10x6 | 3S 800-1300mAh |

**Key insight**: The Geronimo 2 uses a 1800KV motor on **2S** with a smaller prop -- this is the "high KV / low voltage" approach. Our 3S 1300mAh pack dictates the "low KV / higher voltage" approach, which is actually better: lower current for the same power means less resistive losses and less stress on ESC/wiring.

---

## 7. 3D Model Availability

### Motors
- **GrabCAD "2208" tag**: Multiple outrunner motor models available (generic 2208 size)
  - URL: https://grabcad.com/library/tag/2208
  - A2212 1000KV model available: https://grabcad.com/library/a2212-1000kv-brushless-outrunner-motor-1
  - Generic outrunner models can be adapted to exact dimensions
- **No official STEP files** from Hacker, Scorpion, or AXi manufacturers

### Folding Propellers
- **GrabCAD "Folding Prop 30mm Spinner"**: Complete folding prop + spinner assembly
  - URL: https://grabcad.com/library/folding-prop-30mm-spinner-1
  - Designed for Aeronaut CAM blades (8mm root, 3mm fixing hole)
- **GrabCAD folding propeller mechanism**: https://grabcad.com/library/folding-propeller-mechanism-1
- **GrabCAD folding prop 9x6**: https://grabcad.com/library/folding-propeller-9x6-1
- **STLFinder**: Multiple Aeronaut-compatible folding prop models
  - https://www.stlfinder.com/3dmodels/aeronaut-folding-propellers/

### Recommended Approach for CAD
Since no official STEP files exist for the specific motors, we should model the motor parametrically in Build123d using the exact dimensions from this research. The motor is a simple cylinder (can) + shaft + cross-mount -- straightforward to model accurately.

---

## 8. Final Recommendation

**For AeroForge, order the Hacker A20-22L EVO kv924.**

Rationale:
1. **Perfect match**: Rated for "gliders up to 900g" -- our 750-850g sits squarely in range
2. **Proven combo**: A20-22L + 11x6 CamCarbon is THE standard F5J setup for 2.5-3m gliders
3. **28mm diameter**: Fits our ~32mm pod nose with room for the motor mount
4. **55g weight**: Within our 50-60g motor budget in specifications.md
5. **3mm shaft**: Compatible with GM F5J 30/3mm spinner (our 30-32mm nose diameter)
6. **200W burst power**: More than enough for 10-second climb to 100m
7. **Available in Europe**: Hacker is German, ships within EU, no customs for Bulgaria

**Prop**: Aeronaut CAM Carbon Z 11x6 (primary), keep 10x6 as backup set
**Spinner**: GM F5J Carbon 30/3mm
**ESC**: Any quality 20-30A BLHeli_S ESC with 3-5A BEC

---

## Sources

- [Scorpion SII-2208-1100KV](https://www.scorpionsystem.com/catalog/aeroplane/motors_1/s-22_v2/SII-2208-1100KV/)
- [Scorpion SII-2208-1280KV](https://www.scorpionsystem.com/catalog/aeroplane/motors_1/s-22_v2/SII-2208-1280KV/)
- [Scorpion SII-2212-960KV](https://www.scorpionsystem.com/catalog/aeroplane/motors_1/s-22_v2/SII-2212-960KV/)
- [Hacker A20-22L EVO kv924 (DE shop)](https://www.hacker-motor-shop.com/outrunner-electric-motor-a20-22-l-evo-kv924.htm)
- [Hacker A20-20L EVO kv1022 (DE shop)](https://www.hacker-motor-shop.com/outrunner-electric-motor-a20-20l-evo-kv1022.htm)
- [Hacker A20-22L EVO (USA shop)](https://hackermotors.us/product/a20-22-l-evo-kv924/)
- [Joy F5J 2.5m (FlightPoint)](https://flightpoint.co/product/joy-f5j-glider/)
- [Introduction F5J 2.9m (HyperFlight)](https://www.hyperflight.co.uk/products.asp?code=INTRODUCTION-F5J)
- [Geronimo 2 F5J 2.5m (HyperFlight)](https://www.hyperflight.co.uk/products.asp?code=GERONIMO)
- [Aeronaut CAM Carbon Z props (ElectricWingman)](https://www.electricwingman.com/aeronaut-folding-propeller-blades)
- [Aeronaut CAM 11x6 (SoaringUSA)](https://www.soaringusa.com/Aeronaut-CAM-Folding-Propeller-Blades.html)
- [GM F5J Spinner 30mm (SoaringUSA)](https://www.soaringusa.com/GM-30-4mm.html)
- [GM F5J Spinner 30mm (HyperFlight)](https://www.hyperflight.co.uk/products.asp?code=GM-F5J-30)
- [AXi 2212 series (ElectricWingman)](https://www.electricwingman.com/brushless-motors/axi-2212-gold-line.aspx)
- [Turnigy D2830-11 (HobbyKing)](https://hobbyking.com/en_us/turnigy-2830-brushless-motor-1000kv.html)
- [ALES/F5J Motor Selection Chart (iCare)](https://icare-icarus.3dcartstores.com/ALES-F5J-Glider-motor-selection-chart_c_138.html)
- [GrabCAD 2208 motors](https://grabcad.com/library/tag/2208)
- [GrabCAD folding prop 30mm spinner](https://grabcad.com/library/folding-prop-30mm-spinner-1)
