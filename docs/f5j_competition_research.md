# F5J Competition Glider Research

**Date:** 2026-03-28
**Purpose:** Inform AeroForge 2.56m 3D-printed sailplane design with competitive F5J data

---

## 1. F5J Rules Summary (FAI Sporting Code Section 4, Volume F5)

### Scoring Formula
An F5J task score has three components:
1. **Flight Duration:** 1 point per second of flight
2. **Landing Bonus:** Up to 50 points (5 points per meter from spot, <=1m = 50pts, <=2m = 45pts, etc., >10m = 0pts)
3. **Height Penalty:** Subtracted from total

### Motor Rules
- **Maximum motor run time:** 30 seconds
- No penalty for motor run time itself -- penalty is based on altitude achieved

### Altitude Penalty (Critical Design Driver)
- **0.5 points per meter** for start heights up to 200m
- **3.0 points per meter** for start heights above 200m
- Measured from hand release through 10 seconds after motor shutdown
- **Key insight:** Launching lower saves far more points than nailing a landing

### Working Time
- Qualifying rounds: **10 minutes**
- Fly-off rounds: **15 minutes**
- Overflying past working time = lose all landing points
- Overflying by >1 minute = zero flight score

### What This Means for Design
- **Low wing loading is king** -- must thermal efficiently from low altitude
- **Minimum sink rate** matters more than max L/D at speed
- **Agility at low speed** is critical for working weak, narrow thermals near the ground
- **Light weight** directly translates to lower launch altitude needed
- The plane must handle a **wide speed range** (floating in weak lift to penetrating in wind)

---

## 2. What Separates Winners from Mid-Pack

### 2025 F5J World Champion: Joe Wurts (New Zealand) -- 4th world title
- Flew **Vladimir's Model Plus X** throughout
- "The current popular choices (and many less-popular choices) are all great sailplanes"
- "Fly the airplane you brought and you will be successful"
- Converted to **DualSky direct-drive** motors (avoiding gearbox failures)
- In fly-off: plane weighed **1,380g** with **493g ballast per wing** = 2,365g loaded

### 2025 Junior World Champion: John Bradley (USA)
- Flew **Samba Prestige 2PK PRO**

### 2025 Team World Champions: Czech Republic
- All three flew **Prestige 2PK and 2PK PRO exclusively**

### Key Differentiators (Pilot > Plane)
1. **Thermal reading ability** -- detecting lift from ground-level cues before launch
2. **Low-altitude save technique** -- gentle inputs, flat circles, no over-piloting
3. **Risk management** -- choosing launch altitude vs. thermal probability
4. **Strategic assessment** -- reading competitors' behavior, field conditions
5. **Composure under pressure** -- consistency across 10+ rounds
6. **Ballast strategy** -- adapting weight to conditions (calm vs windy)

---

## 3. Top F5J Competition Gliders -- Detailed Specifications

### 3.1 Vladimir's Model Plus X (World Champion's Choice)

| Parameter | Value |
|-----------|-------|
| Wingspan | 3,960mm (156 in) |
| Length | 1,763mm (69.4 in) |
| Wing Area | 77.2 dm^2 (1,196 sq in) |
| Empty Weight (Standard) | 831g (29.3 oz) |
| Empty Weight (Light) | 740g (26.1 oz) |
| Empty Weight (Windy) | 961g (33.9 oz) |
| Flying Weight (Standard) | 1,199g (42.3 oz) |
| Flying Weight (Light) | 1,024g (36.1 oz) |
| Wing Loading (Standard) | 14.0 g/dm^2 |
| Wing Loading (Light) | 12.0 g/dm^2 |
| Wing Loading (Windy) | 16.0 g/dm^2 |
| Airfoil | JW (Joe Wurts design) |
| Controls | 6-servo wing (2A + 2F + R + E) |
| Fuselage | Pod-and-boom, carbon, separates into 2 pieces |
| Nose diameter | 54mm tapering to 38mm |

**Construction highlights:**
- Full Rohacell core wing with integrated carbon shear webs
- Ultra-high module carbon spar
- Spread Tow Carbon (Carboline) skin
- Tail boom: Spread Tow carbon at +/-45 deg with 2 layers UD high-strength carbon
- Tail boom weight: **41g** without pushrods
- Horizontal stabilizer + joiner: **36g**

### 3.2 Samba Prestige 2PK (Team Champions' Choice)

| Parameter | Value |
|-----------|-------|
| Wingspan | 3,900mm |
| Wing Area | 79.3 dm^2 |
| Aspect Ratio | 19.2 |
| Flap Chord | 28% of wing chord |
| RTF Weight (FAI X-tail) | 1,040g |
| RTF Weight (FAI V-tail) | 1,058g |
| RTF Weight (Light) | 1,150-1,250g |
| RTF Weight (Sport) | 1,300-1,350g |
| RTF Weight (Storm/ballasted) | 1,650-1,700g |
| Tail Config | X-tail or V-tail |

**Airfoil system:**
- **7 different airfoils** optimized along the span
- **6 non-symmetrical horizontal stab airfoils**
- **7 vertical tail airfoils** varying 7% to 5.3% thickness

**Construction:**
- Full Rohacell Core (FRC) technology
- Heated aluminum molds
- Carbon fabric servo compartments in wings
- Solidcore technology for stabilizer and elevator

### 3.3 Samba Prestige 2PK PRO (Latest Evolution)

| Parameter | Value |
|-----------|-------|
| Wingspan | 4,000mm (maximum allowed by FAI) |
| Aspect Ratio | >19.2 (increased from 2PK) |
| Tip Airfoil Thickness | 5.8% (0.3% thinner than 2PK) |
| RTF Weight (FAI) | 1,063g |
| RTF Weight (Light) | 1,200-1,300g |
| RTF Weight (Normal) | 1,480-1,580g |
| RTF Weight (Storm) | 1,670-1,780g |
| CG Range | 107-121mm tested with 1,070-2,800g |
| Flap Chord | 28% |
| Vh (horizontal tail volume) | 0.45 |
| Vv (vertical tail volume) | 0.025 |
| EDA (6 deg joiners) | 7.00 deg |
| EDA (8 deg joiners) | 8.49 deg |

**Key innovation:** Fin moved 92mm downstream, stabilizer 65mm downstream vs standard 2PK.
Nonlinear geometric washout twist for improved stall characteristics.

### 3.4 NAN Models Xplorer 3 F5J

| Parameter | 3500mm version | 3800mm version |
|-----------|---------------|---------------|
| Wingspan | 3,500mm | 3,760mm |
| Fuselage Length | 1,550mm | 1,550mm |
| Wing Area | 75.7 dm^2 | 81.3 dm^2 |
| Tail Area | 8.8 dm^2 | 8.8 dm^2 |
| Empty Weight | ~820g | ~880g |
| Airfoil | NAN-F3J | NAN-F3J |
| CG (empty) | 131mm | 131mm |
| CG (ballasted) | 125mm | 125mm |

### 3.5 NAN Models Xplorer 2 F5J

| Parameter | 3500 | 3700 | 3800 | 4000 |
|-----------|------|------|------|------|
| Wingspan (mm) | 3,500 | 3,700 | 3,800 | 4,000 |
| Wing Area (dm^2) | 75.85 | 81.0 | 81.5 | 86.7 |
| Empty Weight (g) | 820 | 880 | 880 | 940 |
| Fuselage Length | 1,550mm | 1,550mm | 1,550mm | 1,550mm |
| Tail Area | 8.8 dm^2 | 8.8 dm^2 | 8.8 dm^2 | 8.8 dm^2 |
| Airfoil | NAN-F3J | NAN-F3J | NAN-F3J | NAN-F3J |

### 3.6 NAN Models Shadow F5J (Out of Production, Reference)

| Parameter | Value |
|-----------|-------|
| Wingspan | 3,654mm |
| Fuselage Length | 1,630mm |
| Wing Area | 73.0 dm^2 |
| Tail Area | 8.8 dm^2 |
| Empty Weight | ~1,200g |
| Airfoil | HN 507M1 (Norbert Habe) |
| CG (empty) | 117mm |
| CG (ballasted) | 113mm |

### 3.7 NAN Models Explorer Q (Latest)

| Parameter | Value |
|-----------|-------|
| Wingspan Options | 3,500 / 3,700 / 3,800 / 4,000mm |
| Wing | 4-piece (2-piece center + 2 tips) |
| Tail Config | X-tail or V-tail |
| Fuselage | 3-piece carbon with pre-installed cables |
| Ballast | Tubes inside wing, easily removable |

### 3.8 Neutrino F5J (jimaero)

| Parameter | Value |
|-----------|-------|
| Wingspan | 3,950mm |
| Wing Area | 79.2 dm^2 |
| Aspect Ratio | 19.9 |
| Wing Loading | 14.5 g/dm^2 |
| Airfoil Series | DI 8120...820 (6.9% root to 5.0% tip) |
| Spinner Diameter | 32mm |
| Flying Weight (Standard) | ~1,350g |
| Flying Weight (Light) | from 1,150g |
| Wing | 4-piece, longest part 1,120mm |
| Construction | Solid core PMI foam (Rohacell) |

### 3.9 Eternity F5J (Infinity Models)

| Parameter | Value |
|-----------|-------|
| Wingspan | 3,970mm |
| Wing Area | 74.42 dm^2 |
| V-tail Area | 7.52 dm^2 |
| Aspect Ratio | **22:1** (highest in class) |
| Root Airfoil Thickness | 7.8% |
| Mid-to-Tip Thickness | 6.9% |
| Airfoil Designer | Dirk Pflug, 5 different airfoils |
| Wing Layout | Triple dihedral |
| Construction | Solid core, CNC aluminum molds (GCM Poland) |
| Wing | 4-piece |
| Fuselage | 2-piece |

### 3.10 Art Hobby Scalar F5J

| Parameter | Value |
|-----------|-------|
| Wingspan | 4,000mm |
| Length | 1,700mm |
| Wing Area | 82.7 dm^2 |
| Flying Weight | ~1,550g |

### 3.11 RCRCM Eagle F5J

| Parameter | Value |
|-----------|-------|
| Wingspan | 3,750mm |
| Wing Area | 81.0 dm^2 |
| Length | 1,580mm |
| Empty Weight | 1,700-1,800g |
| Tail Config | X-tail |
| Construction | Fiberglass+carbon or full carbon versions |

### 3.12 Flyinger Joy F5J (Entry-Level Competitive)

| Parameter | Value |
|-----------|-------|
| Wingspan | 2,500mm |
| AUW (Light) | 615-650g |
| Airfoil | AG series (Drela) |
| Wing | High AR polyhedral |
| Designer | Mykola Horban (MH) |

### 3.13 Introduction F5J (Entry Kit)

| Parameter | Value |
|-----------|-------|
| Wingspan | 2,860mm |
| Airfoil | AG35mod |
| Flying Weight | from 1,100g |
| Construction | Laser-cut wood, CRP spars, GRP leading edges |
| Motor | Hacker A20-22L Evo |

### 3.14 Dream-Flight Libelle DLG (Reference, Not F5J)

| Parameter | Value |
|-----------|-------|
| Wingspan | 1,200mm |
| Wing Area | 21.31 dm^2 |
| Weight | 278-290g |
| Wing Loading | 13-13.6 g/dm^2 |
| Controls | Ailerons, Rudder, Elevator |
| Construction | Precision-moulded EPO foam, carbon tail boom and spars |

---

## 4. Cross-Model Technical Analysis

### 4.1 Wingspan Distribution (Top F5J Gliders)

| Range | Models | Notes |
|-------|--------|-------|
| 2,500mm | Joy F5J | Entry/sub-class |
| 2,860mm | Introduction F5J | Entry kit |
| 3,500-3,760mm | Xplorer 2/3, Eagle | Mid-size competition |
| 3,900-4,000mm | Prestige, Plus X, Neutrino, Eternity, Scalar | **Top competition** |

**Conclusion:** Top F5J competition converges on **3,900-4,000mm** wingspan. The 4m maximum appears to be a practical limit (possibly FAI-related for certain sub-classes), not a rules-mandated limit.

### 4.2 Wing Loading Comparison

| Model | Wing Loading (g/dm^2) | Notes |
|-------|----------------------|-------|
| Plus X Light | 12.0 | Lightest competitive |
| Dream-Flight Libelle | 13.0-13.6 | DLG reference |
| Plus X Standard | 14.0 | World champion setup |
| Neutrino Standard | 14.5 | |
| Plus X Windy | 16.0 | Ballasted |
| General F5J range | 12-30 | Full range |

**Conclusion:** Top competitive F5J wing loading is **12-16 g/dm^2** in calm/light conditions, ballasted up to **20-30 g/dm^2** in wind.

### 4.3 Aspect Ratio Comparison

| Model | Aspect Ratio |
|-------|-------------|
| NAN Shadow | ~18.3 (calculated: 3654^2 / 7300) |
| Prestige 2PK | 19.2 |
| NAN Xplorer 3 (3500) | ~16.2 |
| Neutrino | 19.9 |
| Plus X | ~20.3 (calculated: 3960^2 / 7720) |
| Eternity | **22.0** |
| Optimal theoretical | ~17-20 |

**Conclusion:** Aspect ratios of **17-22** are the competitive range. The theoretical optimum is ~17 for Reynolds number reasons, but many winning designs push to 19-22. The trade-off is roll rate and agility vs. induced drag reduction.

### 4.4 Airfoil Families Used

| Airfoil Family | Designer | Used By | Characteristics |
|---------------|----------|---------|-----------------|
| JW series | Joe Wurts | Plus X | Optimized for ultralight F5J |
| NAN-F3J | NAN proprietary | Xplorer, Explorer | Wide speed range |
| HN 507M1 | Norbert Habe | Shadow | Very wide speed range |
| AG series | Mark Drela | Joy, Introduction | Low Re, small bubbles, docile stall |
| DI 8120-820 | Unknown (DI) | Neutrino | 6.9-5.0% thickness, ultralight F5J |
| Dirk Pflug series | Dirk Pflug | Eternity | 7.8% root to 6.9% tip |
| Samba proprietary | Samba team | Prestige | 7 wing airfoils, 5.8% tip |

**Common characteristics across all top F5J airfoils:**
- **Thin:** 5.0-7.8% thickness (thinner toward tips)
- **Designed for Re 80,000-200,000**
- **Positive flap response** (performance improves with camber change)
- **Docile stall** characteristics for low-altitude saves
- **Multiple airfoils along span** (5-9 different profiles blended)
- AG-series specifically: 100% attached laminar flow at higher speeds

### 4.5 Typical Reynolds Numbers for F5J

Using Re = 70 x V(m/s) x chord(mm):

| Condition | Speed (m/s) | Chord (mm) | Reynolds Number |
|-----------|-------------|------------|-----------------|
| Thermalling (root) | 7-9 | 200 | 98,000-126,000 |
| Thermalling (tip) | 7-9 | 100 | 49,000-63,000 |
| Cruise (root) | 10-12 | 200 | 140,000-168,000 |
| Cruise (tip) | 10-12 | 100 | 70,000-84,000 |
| Penetration (root) | 14-18 | 200 | 196,000-252,000 |

**For our 2.56m design with ~210mm root, ~115mm tip:**
- Thermalling root: Re ~105,000-132,000
- Thermalling tip: Re ~56,000-72,000
- Cruise root: Re ~147,000-176,000

### 4.6 Control Surface Layout

**Universal across all top F5J gliders:**
- **Ailerons + Flaps** (4-servo wing minimum)
- Top models use **6-servo wing** (ailerons + flaperons for full camber control)
- Flap chord typically **25-30%** of wing chord
- Full camber change capability (reflex to full positive camber)
- "Butterfly" / crow braking (flaps down + ailerons up)

### 4.7 Fuselage Design

**All top F5J competition gliders use pod-and-boom:**
- Carbon pod (often 2 or 3 piece for transport)
- Carbon boom (spread tow carbon, typically 40-50g)
- Removable nose cone for motor/battery access
- Nose diameter: 32-54mm (motor spinner area) tapering to ~25-30mm boom

**No molded one-piece fuselages in top F5J competition.**

### 4.8 Tail Configurations

| Config | Models Using It | Advantages |
|--------|----------------|------------|
| X-tail | Prestige, Xplorer, Eagle, Explorer | Better rudder authority, easier alignment |
| V-tail | Prestige (option), Explorer (option) | Lighter, less drag, less damage-prone |
| Conventional | Shadow (cruciform-style) | Simplest, proven |

**Trend:** X-tail is most popular at top level. V-tail is a close second.
Both are offered by most manufacturers as options.

### 4.9 Construction Methods

| Method | Description | Used By |
|--------|-------------|---------|
| Full Rohacell Core (FRC) | PMI foam core with composite skin, heated molds | Prestige, Neutrino, Plus X |
| Hollow molded composite | Traditional fiberglass/carbon shells | RCRCM Eagle, older NAN |
| Laser-cut wood + composite | Wood ribs, composite spar, film covering | Introduction F5J |
| EPO foam + composite | Molded foam with carbon reinforcement | Dream-Flight Libelle |

**FRC (Full Rohacell Core) dominates top competition.** It produces:
- Geometric accuracy (Rohacell postforming)
- Very thin, precise airfoil reproduction
- Light weight
- Good stiffness

---

## 5. Relevance to AeroForge 2.56m Design

### What We Can Learn

1. **Wing loading target:** Our 750-850g AUW with ~40 dm^2 wing area gives ~19-21 g/dm^2.
   Top F5J gliders at 12-16 g/dm^2 are lighter, but they're also 4m span.
   For 2.56m, a wing loading of 18-22 g/dm^2 is reasonable and flyable.

2. **Airfoil selection validated:** AG24 (root) to AG03 (tip) is in the correct family.
   Top F5J gliders use AG-series, JW, HN, and DI airfoils -- all designed for Re 80,000-200,000.
   Our Re range (105,000 root thermal, 56,000 tip thermal) is within the AG design envelope.

3. **Full camber control is mandatory:** Every competitive glider has flaps + ailerons.
   Our full-house + crow braking design matches top competition practice.

4. **Thin airfoils at tips:** Top designs go as thin as 5.0-5.8% at tips.
   AG03 is ~7% thick, which is slightly thicker than the latest competition tips.
   Consider: can 3D printing reproduce 5-6% thick tip airfoils accurately?

5. **Multiple blended airfoils:** Top gliders use 5-9 different airfoils along span.
   Our AG24-to-AG03 blend with airfoil at every rib is consistent with this.
   3D printing's advantage: we can have unique airfoil at EVERY rib station.

6. **Pod-and-boom is universal:** Our carbon tube spar + 3D printed structure
   is conceptually different (distributed structure vs. monocoque pod).
   This is where 3D printing diverges from composite molding.

7. **Aspect ratio context:** Our 2.56m with ~210mm root chord gives AR ~12.
   Competition F5J is AR 17-22. Our lower AR means:
   - Higher induced drag (disadvantage)
   - Better roll rate (advantage for smaller field)
   - Higher Re at tips (less laminar separation issues)

8. **Weight is critical:** The lightest F5J gliders (Plus X Light) achieve 740g empty
   for a 4m span carbon composite airplane. Our 750-850g AUW target for 2.56m
   means we need to be very aggressive on structural weight.

### Where 3D Printing Can Compensate

- **Airfoil accuracy:** Every rib station gets exact computed airfoil (vs. hand-sheeted approximation)
- **Geodetic/lattice structure:** Topology-optimized internal structure at no cost premium
- **Integrated features:** Gap seals, turbulators, winglets designed in, not added on
- **Rapid iteration:** Test 10 wing panel variants in a weekend

### Where 3D Printing Cannot Compete

- **Surface finish:** Rohacell/composite is smoother than FDM/PLA
- **Weight:** Carbon composite will always be lighter per unit strength
- **Stiffness:** Carbon spar >> 3D printed structure (hence our carbon tube main spar)
- **Thin sections:** 5% thick tip airfoils may be impractical in 3D printing

---

## 6. Key Sources

- [NAN Models Xplorer 3 F5J](https://nanmodels.com/models/xplorer-3-f5j/)
- [NAN Models Xplorer 2 F5J](https://nanmodels.com/models/xplorer-2-f5j/)
- [NAN Models Shadow F5J](https://nanmodels.com/models/shadow-f5j/)
- [NAN Models Explorer Q](https://nanmodels.com/models/explorer-q/)
- [Samba Prestige 2PK](https://f3j.com/pages/prestige-2pk)
- [Samba Prestige 2PK PRO](https://f3j.com/pages/prestige-pk2-pro)
- [Vladimir's Model Plus X (Kennedy Composites)](https://www.kennedycomposites.com/plusx.htm)
- [Vladimir's Model Maxa EL Family](http://f3j.in.ua/maxa-el-family.html)
- [Vladimir's Model Plus X](http://f3j.in.ua/plus-x.html)
- [Neutrino F5J (jimaero)](https://www.skyraccoon.com/aircraft/jimaero_Neutrino-F5J_neutrino)
- [Eternity F5J (Infinity)](https://www.air-rc.com/aircraft/Infinity-models_Eternity-F5J_eternity-fr)
- [Art Hobby Scalar F5J](https://www.arthobby.com/index.php?page=item&category=30&sub_category=50&item=642)
- [RCRCM Eagle F5J](https://www.rcrcm.com/products/eagle-f5j)
- [Joy F5J 2.5m](https://flightpoint.co/product/joy-f5j-glider/)
- [Introduction F5J](https://www.hyperflight.co.uk/products.asp?code=INTRODUCTION-F5J)
- [Dream-Flight Libelle DLG](https://dream-flight.com/products/libelle-dlg)
- [F5J Primer (USA)](https://www.f5j-usa.com/f5j-primer/)
- [F5J Rules](https://www.f5j-usa.com/f5j-rules/)
- [2025 F5J World Championships - FAI](https://www.fai.org/news/results-2025-fai-f5j-world-champions-electric-powered-thermal-duration-gliders)
- [Joe Wurts 2025 Worlds - Model Aviation](https://www.modelaviation.com/article/joe-wurts-2025-f5j-world-championships)
- [Samba at 2025 Worlds](https://f3j.com/blogs/news/world-championship-f5j-2025-argentina-1)
- [F5J Glider Comparison (XFLR5)](https://f5jmasters.com/comparison-of-several-glider-features-using-the-software-xflr5-chapter-1/)
- [Adrien Gallet - The Duration Glider and F5J Competition](https://f5j.ch/wp-content/uploads/The-duration-glider-and-the-F5J-Competition-English-version.pdf)
