# Aerodynamics & 3D Printing Research for AeroForge

**Date:** 2026-03-28
**Purpose:** Comprehensive aerodynamics research for AeroForge 2.56m 3D-printed F5J-style sailplane
**Scope:** Airfoils, structures, boundary layer, twist, tails, flaps, winglets, Reynolds effects

---

## 1. Blended/Morphing Airfoil Technology

### Continuous Spanwise Airfoil Variation

3D printing's killer advantage over traditional construction: **arbitrary airfoil variation at every station along the span without any manufacturing penalty.** Unlike hand-sheeted balsa or composite-molded wings (which are limited to 2-3 airfoil templates with linear interpolation between them), a 3D-printed wing can have a computationally optimized, unique airfoil at every single rib station.

**Key research findings:**

- Utah State University demonstrated 3D-printed wings with morphing trailing-edge technology, using two approaches:
  - **ARCS** (Airfoil Recambering Compliant System) -- continuous trailing-edge morphing
  - **KINCS** (Kinetic Internal Nexus Compliant System) -- discontinuous trailing-edge morphing
- Both systems were fully 3D-printed and showed "low cost, minimal man-hours required for manufacturing, and speed at which design iterations can be explored."

**What this means for AeroForge:**

Top F5J competition gliders (Prestige 2PK PRO, Plus X, Neutrino) already use 5-9 different airfoils blended along the span. Our 3D-printed approach can go further:
- Optimize airfoil shape at **every 10mm of span** (25+ unique stations vs. 5-9)
- Vary not just thickness and camber, but also:
  - Leading edge radius (tuned to local Reynolds number)
  - Trailing edge angle
  - Maximum thickness position
  - Reflex amount
- Each station optimized via XFOIL at its actual local Reynolds number and angle of attack

**Implementation approach:**
1. Define airfoil at root (AG24-family) and tip (AG03-family)
2. Use XFOIL to analyze performance at each span station's actual Re
3. Optimize intermediate profiles beyond simple linear interpolation
4. Each printed rib is a unique, optimized airfoil cross-section

### Morphing Control Surfaces

Research from Utah State and others shows that 3D-printed compliant mechanisms can create seamless, gapless control surfaces. For AeroForge, this is relevant for:
- **TPU living hinges** -- already in our design (gap-free flex hinges)
- **Compliant trailing edges** -- could eliminate discrete flap gaps entirely
- **Passive aeroelastic tailoring** -- wing that washes out under load

**Sources:**
- [3D-Printed Wings with Morphing Trailing-Edge Technology (Utah State)](https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=1023&context=mae_stures)
- [3D-Printed Morphing Wings for Controlling Yaw (Utah State)](https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=9317&context=etd)
- [Design, Analysis and 3D Printing of a Morphing Wing Prototype](https://www.researchgate.net/publication/375617073)
- [A Guide To 3D Printing Model Aircraft Wings (Hackaday)](https://hackaday.com/2022/08/26/a-guide-to-3d-printing-model-aircraft-wings/)

---

## 2. AG Series Airfoils (Mark Drela)

### Complete AG Family Overview

The AG series airfoils were designed by Prof. Mark Drela (MIT) specifically for RC sailplanes at very low Reynolds numbers. They feature small separation bubbles for good minimum sink and docile stall characteristics.

#### AG Airfoil Categories and Applications

| Series | Application | Design Features | Typical Use |
|--------|------------|-----------------|-------------|
| AG03-AG11 | Small wood HLGs, solid-balsa | Flat aft bottom (AG03), thin | Tip sections, small gliders |
| AG04, AG08-AG10 | Composite HLGs (Apogee) | Launch/run emphasis | DLG root-to-tip progression |
| AG12-AG14 | Composite HLGs (XP3) | Float/run balance | Mid-performance DLGs |
| AG16-AG19 | 2M poly gliders (Photon, Allegro) | Float emphasis | Light thermal gliders |
| AG24-AG27 | 2-3M poly gliders (Bubble Dancer) | Heavier glider optimization | **Our root airfoil family** |
| AG31-AG33 | Small aileron gliders (Wind Dancer) | Built-up wood construction | Small sport gliders |
| AG35-AG38 | Thinner, lower Re optimization | Significantly better at low Re | **Best for smaller/lighter gliders** |
| AG40d-AG43d | 3M composite aileron (Aegea 3m) | Camber-changing flap design | Large aileron gliders |
| AG44ct-AG47ct | 2M composite aileron (Aegea 2m) | Flap-optimized contours | **Relevant for our size class** |
| AG45c-AG47c | 1.5M aileron HLGs (SuperGee) | Ultralight, low Re | DLG competition |
| AG455ct | 1.5M HLGs (SuperGee II, XP3, TabooXL) | Midway AG45c/AG46c | Latest DLG designs |

#### Key Design Philosophy

- **AG4x series** are "significantly thinner and have less camber than the SD7037" and are "geared for lower Reynolds numbers"
- **AG35-AG38** are "thinner, and perform noticeably better at lower Reynolds numbers" -- "especially attractive for smaller gliders"
- **AG4x flap versions** (ct, c suffixes) have "contours designed for both high- and low-camber flap positions"
- The suffix meanings: `d` = DLG version, `ct` = camber+thickness optimized, `c` = camber optimized

#### AG24 Specifications (Our Root Airfoil)
- **Max thickness:** ~10% of chord
- **Application:** Bubble Dancer DLG root section, 2-3M poly gliders
- **Design Re range:** ~80,000-150,000
- **Characteristics:** Good thermalling performance, moderate camber, docile stall
- **XFOIL polars available** at Re 100,000 and Re 1,000,000

#### AG03 Specifications (Our Tip Airfoil)
- **Feature:** Flat aft bottom
- **Application:** Small HLGs, tip sections
- **Design Re range:** ~40,000-80,000
- **Characteristics:** Very low drag at low Re, thin, designed for low-speed float

#### Reynolds Number Recommendations for F5J Class

For our 2.56m wingspan at typical F5J speeds:

| Station | Chord | Re (thermal 8m/s) | Re (cruise 11m/s) | Recommended AG Family |
|---------|-------|-------------------|--------------------|-----------------------|
| Root | 210mm | ~118,000 | ~162,000 | AG24 or AG25 |
| 25% span | 186mm | ~104,000 | ~143,000 | AG24/AG09 blend |
| 50% span | 162mm | ~91,000 | ~125,000 | AG09 or AG35 |
| 75% span | 139mm | ~78,000 | ~107,000 | AG35/AG03 blend |
| Tip | 115mm | ~64,000 | ~88,000 | AG03 or AG38 |

**Revised recommendation:** Consider the AG35-38 series for mid-span stations instead of AG09. The AG35-38 are specifically optimized for the Re 60,000-100,000 range that our mid-to-outer panels operate in. The AG44ct-AG47ct series is also worth evaluating since they're designed for 2M aileron gliders with camber-changing flaps -- exactly our configuration.

#### What Top Competition Uses

From the F5J competition research (see `f5j_competition_research.md`):
- Top F5J gliders use **5.0-7.8% thick** airfoils (thinner than AG24's ~10%)
- Competition airfoils: JW series, NAN-F3J, HN507M1, DI 8120-820, Dirk Pflug series
- **Our AG24 at 10% may be too thick for the root** by competition standards
- Consider: AG35-family (~7-8% thick) might be better even at root for our wing loading

**Sources:**
- [Drela Airfoil Shop (Charles River RC)](https://charlesriverrc.org/articles/on-line-plans/mark-drela-designs/drela-airfoil-shop/)
- [Mark Drela's AG and HT Airfoils](https://charlesriverrc.org/articles/drela-airfoilshop/markdrela-ag-ht-airfoils.htm/)
- [AG24 on Airfoil Tools](http://airfoiltools.com/airfoil/details?airfoil=ag24-il)
- [AG03 on Airfoil Tools](http://airfoiltools.com/airfoil/details?airfoil=ag03-il)
- [AG35 on Airfoil Tools](http://airfoiltools.com/airfoil/details?airfoil=ag35-il)
- [UIUC Airfoil Data Site](https://m-selig.ae.illinois.edu/ads/coord_database.html)
- [Summary of Low-Speed Airfoil Data Vol. 5](https://m-selig.ae.illinois.edu/uiuc_lsat/Low-Speed-Airfoil-Data-V5.pdf)

---

## 3. Turbulator Strips and 3D-Printed Surface Features

### The Low-Re Boundary Layer Problem

At Re 50,000-200,000 (our entire operating range), the laminar boundary layer is the dominant aerodynamic challenge:

1. Laminar flow separates from the airfoil surface due to adverse pressure gradient
2. A **laminar separation bubble (LSB)** forms
3. Flow transitions to turbulent within the bubble
4. Turbulent flow may (or may not) reattach

The separation bubble **significantly increases drag and reduces lift.** At Re < 100,000, the bubble can extend to the trailing edge and cause complete stall.

### Turbulators / Trip Strips

Small aircraft operating at Re 60,000-500,000 often install **turbulators** (trip strips) near the leading edge to force early transition:
- Forces laminar-to-turbulent transition before the natural separation point
- Prevents formation of large separation bubbles
- Trades slightly higher skin friction for much lower form drag
- **Net effect: lower total drag and higher maximum lift**

**Typical placement:** 5-15% chord from the leading edge on the upper surface.

### 3D Printing as Inherent Turbulator

This is a key insight for AeroForge:

**Research finding:** "3D printed lifting surfaces exhibit a riblet-like effect distinct from random roughness, with printing layer height being a crucial parameter that determines riblet size."

This means:
- FDM layer lines naturally create spanwise "riblets" on the wing surface
- At the right scale, these can **beneficially trip the boundary layer**
- Higher-precision printers produce more uniform riblet-like patterns
- The effect is distinct from random roughness -- it's semi-organized

**Design implications:**
1. **Print orientation matters:** Chordwise printing creates spanwise riblets (beneficial for tripping)
2. **Layer height selection:** 0.15-0.20mm layers may provide the optimal "trip" effect for our Re range
3. **Don't over-sand:** Light sanding for fit is fine, but aggressive surface smoothing may remove beneficial roughness on the upper surface aft of the spar
4. **Controlled roughness zones:** We can intentionally print at different orientations or layer heights in the trip zone (5-15% chord upper surface) vs. the rest of the airfoil

### Riblets for Drag Reduction

Properly sized riblets (streamwise grooves) can reduce turbulent skin friction by 5-10%:
- Optimal riblet height: ~15 wall units (depends on local Re)
- For our Re range, this translates to roughly 0.1-0.3mm height
- **FDM layer lines at 0.15-0.20mm are in the right range** for riblet effect on the aft portion of the airfoil
- The herringbone riblet pattern generates streamwise vortices that can control separation

### Vortex Generators (VGs)

Micro vortex generators (0.5-1.5mm height for our scale) can:
- Energize the boundary layer before separation
- Be 3D-printed as integral features of the wing skin
- Placed at 15-30% chord on the upper surface
- Most effective at higher angles of attack (thermal turning)

**Practical recommendation for AeroForge:**
- Use FDM layer lines as passive boundary layer trip on upper surface
- Consider printed micro-VGs at ~20% chord on outer panels (Re < 80,000)
- Keep lower surface smooth (laminar flow is beneficial there)
- Test with and without sanding in XFOIL to quantify the effect

**Sources:**
- [Riblets and Scales on 3D-Printed Wind Turbine Blades (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S0167610525001849)
- [Boundary Layer, Vortex Generator & Turbulator Experiments](https://www.juliantrubin.com/encyclopedia/aviation/boundary_layer.html)
- [Low Reynolds Number Airfoil Characteristics (Cadence)](https://resources.system-analysis.cadence.com/blog/msa2022-low-reynolds-number-airfoil-characteristics)
- [Low Reynolds Number Airfoil Design (Selig, UIUC)](https://m-selig.ae.illinois.edu/pubs/Selig-2003-VKI-LRN-Airfoil-Design-Lecture-Series.pdf)
- [Conformal Vortex Generators](https://colleenduffley.wixsite.com/edge-aerodynamix/single-post/2016/04/17/Taming-Turbulence-With-Tape-Conformal-Vortex-Generators)

---

## 4. Winglet Design for RC Gliders

### Winglet Types Compared

| Type | Mechanism | Pros | Cons | Best For |
|------|-----------|------|------|----------|
| **Simple endplate** | Blocks spanwise flow at tip | Easy to make | High profile drag, flow separation | Not recommended |
| **Whitcomb winglet** | Airfoil-section vertical extension | Effective drag reduction | Junction drag if not blended | Larger models |
| **Blended winglet** | Smooth transition wing-to-winglet | Low junction drag, 3-5% drag reduction | Complex geometry | **Our best option** |
| **Tip extension** | Simply extend the span | Most efficient drag reduction | Increases bending moment | If span allows |
| **Winglet fence** | Both upper and lower winglets | Good at low Re | More wetted area | Low-speed applications |

### Key Design Parameters

From Prof. Mark Maughmer's research (Penn State, leading winglet designer for sailplanes):

- **"Each glider must have winglets specifically designed for it"** -- no universal winglet works
- **Blend the winglet into the wing** -- avoid sharp junction angles
- **Winglet airfoil:** Should be different from the wing airfoil, optimized for the local flow conditions (sideslip angle, lower Re due to smaller chord)
- **Height:** Typically 5-10% of semi-span (for our design: ~65-130mm)
- **Cant angle:** 70-80 degrees from horizontal (near-vertical)
- **Toe angle:** 1-3 degrees toe-out (to account for induced angle)
- **Sweep:** 20-35 degrees leading edge sweep

### Low Reynolds Number Considerations

At model scale, winglets face an additional challenge:
- Winglet chord is typically 40-60% of tip chord
- For our 115mm tip chord, winglet chord would be ~50-70mm
- At 8 m/s: Re on winglet = ~28,000-39,000
- This is **extremely low Re** -- laminar separation is severe
- Winglet airfoil must be thin (4-6%) and possibly have a trip strip

**Practical recommendation for AeroForge:**
- A **blended winglet** of ~80-100mm height with ~60mm root chord tapering to ~30mm tip chord
- Thin symmetric or slightly cambered airfoil (NACA 0006 or similar)
- 3D-printed as integral part of the tip panel
- Include a printed turbulator strip at 10% chord on the outer surface
- The blending radius is free with 3D printing (no manufacturing cost for the compound curve)

**Alternative: Polyhedral tips** (like the Joy F5J uses) may be more effective than winglets at this scale. They increase effective dihedral while slightly increasing projected span.

**Sources:**
- [Design of Winglets for Low-Speed Aircraft (Maughmer)](http://www.mandhsoaring.com/why%20winglets/wl-it.pdf)
- [About Winglets (Maughmer)](http://mandhsoaring.com/Why%20Winglets/WL-Soaring.pdf)
- [Numerical Study of Winglet at Low Reynolds Numbers](https://www.researchgate.net/publication/267497254)
- [The Science Behind an Efficient Winglet Design (Flite Test)](https://www.flitetest.com/articles/the-science-behind-an-efficient-winglet-design)
- [Design Process: End Plates and Winglets (Kitplanes)](https://www.kitplanes.com/design-process-end-plates-and-winglets/)

---

## 5. Geodesic/Lattice Internal Wing Structures

### Historical Context

Geodesic construction (Vickers Wellington bomber, Barnes Wallis) uses intersecting diagonal members arranged along geodesic paths on the surface. Advantages:
- **Lightweight** with excellent load distribution
- **Damage tolerant** -- local failure doesn't propagate
- **Ideal for 3D printing** -- complexity is free

### Research: Lattice-Infilled Wing Structures (2024)

A peer-reviewed study compared five lattice unit cell types for additive-manufactured wing structures:

| Lattice Type | Unit Cell Size | Weight Reduction vs. Conventional | Max Deflection | Max Stress |
|-------------|---------------|----------------------------------|----------------|------------|
| **Kelvin** | 5x5x5mm | **9.5%** | 1.40mm | 128 MPa |
| FCC | 5x5x5mm | ~7% | 1.50mm | 134.8 MPa |
| Fluorite | 6x6x6mm | ~7% | 1.50mm | ~130 MPa |
| BCC | 4x4x4mm | 5.8% | 1.42mm | ~132 MPa |
| Octet | 6x6x6mm | 4.6% | varies | ~132 MPa |
| Conventional (rib-spar) | -- | baseline | 1.60mm | ~134 MPa |

**Key finding:** The Kelvin lattice was identified as "the best choice for current applications, with comparatively minimal wing-tip deflection, weight, and stress."

**Critical insight:** "Stress is uniformly distributed in the infilled lattice compared to the base-wing model, where the stress peak occurred in the spar end area."

### Advantages for 3D-Printed Wings

1. **Uniform stress distribution** -- no stress concentrations at rib-spar junctions
2. **Weight savings of 5-10%** vs. conventional rib-spar (at equal strength)
3. **Damage tolerance** -- geodesic paths redistribute load around damage
4. **Torsional stiffness** -- diagonal members resist twisting better than perpendicular ribs
5. **Print-friendly** -- lattice patterns are naturally self-supporting at many angles

### Practical Implementation for AeroForge

**D-box region (LE to 30% chord):**
- Use a **closed-shell D-box** for primary torsion (this is standard practice)
- Internal structure: **geodesic lattice** connecting the outer skin to the spar tube
- Cell size: 5-8mm (scaled from Kelvin study to our dimensions)

**Aft wing (30% to trailing edge):**
- Traditional rib-like formers at rib stations (needed for airfoil shape accuracy)
- **Geodesic web connecting ribs** instead of solid shear webs
- Lightening holes in ribs follow topology-optimization patterns

**Material consideration:**
- The cited study used AlSi10Mg aluminum -- our PLA/CF-PLA will have different failure modes
- PLA is more brittle than aluminum; lattice members must be thicker (minimum 1.0mm wall)
- CF-PLA improves stiffness significantly (5.5-8.0 GPa vs. 3.5-4.0 for plain PLA)
- Consider **gyroid infill** in Bambu slicer as a practical approximation of Kelvin lattice

**Sources:**
- [Non-Conventional Wing Structure Design with Lattice Infilled (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11012710/)
- [Development of Geodesic Composite Aircraft Structures (ICAS 2012)](https://www.icas.org/icas_archive/ICAS2012/PAPERS/319.PDF)
- [3D Printing of Topologically Optimized Wing Spar (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1359836823006698)
- [Finite Element Analysis of 3D Printed Aircraft Wing (Portland State)](https://pdxscholar.library.pdx.edu/cgi/viewcontent.cgi?article=1717&context=honorstheses)

---

## 6. Flap Configurations for F5J

### Universal F5J Control Architecture

Every competitive F5J glider uses a **4-servo wing minimum** (2 aileron servos + 2 flap servos). Top models use 6-servo wings for independent flaperon control.

### Flight Modes and Deflection Angles

| Mode | Flaps | Ailerons | Elevator Trim | Purpose |
|------|-------|----------|---------------|---------|
| **Launch** | 0 to +3 deg down | 0 | Slight down | Motor climb |
| **Cruise/Normal** | 0 | 0 | Neutral | Searching for lift |
| **Thermal 1 (light)** | +3 to +5 deg down | +2 to +3 deg down | Slight down compensation | Weak lift |
| **Thermal 2 (strong)** | +5 to +10 deg down | +3 to +5 deg down | More down compensation | Strong thermal |
| **Reflex/Speed** | -2 to -5 deg up | -1 to -3 deg up | Slight up compensation | Wind penetration |
| **Crow braking** | +30 to +60 deg down | -15 to -30 deg up | Down compensation (3-point curve) | Landing approach |

### Detailed Configuration Notes

**Full-span flaperons (4-flap system):**
- Flaps and ailerons are mixed so that both surfaces contribute to roll AND camber change
- Flap deflection in roll mode should be **~2/3 of aileron deflection** to reduce adverse yaw
- "Snap flaps": Mix elevator-to-flaps so flaps deploy slightly down with up-elevator (tighter thermal turns)

**Crow braking specifics:**
- Both flaps go down (+30 to +60 deg) while both ailerons go up (-15 to -30 deg)
- Creates massive drag from flaps + reduced lift from up-ailerons
- **Must mix down-elevator compensation** -- use a 3-point compensation curve:
  - 0-45 deg flap: increasing nose-up moment (compensate with increasing down-elevator)
  - Beyond 45 deg: braking effect increases but pitch moment decreases
- Result: "a fast-flying glider can be slowed right down and brought in with very little forward airspeed"

**Camber changing (thermal flap):**
- All surfaces drop uniformly by same amount
- Increases wing camber without creating differential effects
- Effective range: +1 to +10 degrees
- More camber = more lift at lower speed, but only works in rising air
- **Rule of thumb:** "Equal camber on flaps and aileron surfaces, and more camber the better the air"

**Reflex (speed mode):**
- All surfaces raise uniformly by same amount (-1 to -5 degrees)
- Reduces camber, makes wing more "slippery"
- Reduces lift coefficient and induced drag
- Used for upwind penetration and racing between thermals

### Flap Chord

- Competition standard: **25-30% of local wing chord** (Prestige 2PK: 28%)
- Our 210mm root chord: flap chord ~53-63mm
- Our 115mm tip chord: flap chord ~29-35mm

### Servo Recommendations

For our 2.56m design with 6 servos:
- **Wing servos (x4):** Micro digital servos, 2-3kg-cm torque
- **Elevator (x1):** Micro servo in tailboom or tail
- **Rudder (x1):** Micro servo in tailboom or tail

**Sources:**
- [RC Glider Wing Setups](https://www.rc-airplane-world.com/rc-glider-wing-setups.html)
- [NAN Explorer F5J Settings (Aaro Malila)](https://www.rcgroups.com/forums/showatt.php?attachmentid=19203445)
- [ArmSoar Initial Glider Setup](https://www.armsoar.com/pages/initial-glider-setup)
- [Glider Guider's Guide To FrOS](https://www.rcgroups.com/forums/showatt.php?attachmentid=12338413)

---

## 7. Boundary Layer Control -- Passive Methods

### Gap Seals

**Problem:** At the hinge line between wing and control surface, high-pressure air from the lower surface leaks upward through the gap, causing:
- Loss of lift at the hinge line
- Increased drag (mixing losses)
- Reduced control effectiveness
- Early flow tripping in high-speed flight

**Solution: Integrated TPU gap seals**

Our design already uses TPU 95A living hinges. These inherently provide gap sealing. Key details:
- The "top cavity of the hinge line can trip airflow early in launch and high-speed flight"
- For solid-core wings: "the cavity might benefit in slower flight" (acts as passive boundary layer trip)
- For hollow-wing designs (like ours): seal is essential to prevent internal-to-external airflow

**3D printing advantage:** Gap seals can be printed as integral features of the wing panel, with the TPU hinge providing both structural flexibility AND aerodynamic sealing. No aftermarket tape or Mylar strips needed.

### Riblets (Streamwise Grooves)

As discussed in Section 3:
- FDM layer lines create semi-organized riblet-like patterns
- Optimal riblet height for our Re range: ~0.1-0.3mm
- Can reduce turbulent skin friction by 5-10%
- Most beneficial on the aft portion of the airfoil (where flow is turbulent)

### Micro Vortex Generators

Printed as integral features of the wing skin:
- Height: 0.5-1.5mm (sized to local boundary layer thickness)
- Spacing: 5-10 times their height apart
- Position: 15-30% chord on upper surface
- Orientation: 15-20 degrees to freestream
- Most effective on outer panels where Re is lowest

### Surface Texture Zones

A novel approach enabled by 3D printing -- **deliberate surface texture variation across the chord:**

| Chord Position | Surface Treatment | Reason |
|---------------|-------------------|--------|
| 0-5% (leading edge) | Smooth (sanded) | Prevent premature transition |
| 5-15% (upper, trip zone) | As-printed (layer lines) | Natural turbulator effect |
| 15-80% (upper surface) | Light sanding or as-printed | Riblet-like drag reduction |
| 0-100% (lower surface) | Smooth (sanded) | Maintain laminar flow |
| 80-100% (trailing edge) | Smooth, thin | Minimize TE drag |

**Sources:**
- [Applying Gap Seal on a DLG (ArmSoar)](https://www.armsoar.com/blogs/news/applying-gap-seal)
- [Sealing the Aileron Hinge Line (AMA Flight School)](https://www.amaflightschool.org/diy/sealing-aileron-hinge-line)
- [TPU Hinge for RC Plane (MakerWorld)](https://makerworld.com/en/models/937950-tpu-hinge-for-rc-plane)

---

## 8. Twist Distribution Optimization

### Elliptical vs. Bell-Shaped Loading

#### Elliptical Loading (Classical, Prandtl 1920)
- Produces **minimum induced drag for a given span and lift**
- Requires elliptical planform OR appropriate twist distribution
- Constant downwash across the span
- Used by virtually all conventional aircraft

#### Bell-Shaped Loading (Prandtl 1933, Rediscovered by NASA/Al Bowers)
- Produces **minimum induced drag for a given structural weight (root bending moment)**
- Allows 22% more span at the same structural weight as elliptical
- **11% more aerodynamically efficient** at equal structural weight
- Non-constant downwash: strong downwash at root, transitioning to **upwash near tips**
- The upwash at tips produces **proverse yaw** (coordinated turns without rudder)

### Washout Requirements

**For elliptical loading on a tapered wing:**
- Typical washout: 2-4 degrees from root to tip
- Linear distribution is a reasonable approximation
- Additional twist for stall safety: 1-2 degrees extra at tip

**For bell-shaped loading:**
- **Much more aggressive washout required:** ~12 degrees total
- Non-linear distribution: most twist concentrated in outer 30% of span
- The twist "is not a scalar quantity, it is a vector" -- both direction and magnitude vary

### Proverse Yaw Mechanism (Bell Loading)

The bell-shaped distribution creates:
- Strong downwash at root -> induced drag concentrated inboard
- Upwash at tips -> **induced thrust** at wingtips
- When one wing rises (roll), the rising wing creates more induced thrust than the dropping wing
- This produces **yaw in the direction of the turn** (proverse yaw)
- Eliminates adverse yaw that normally requires rudder coordination

**NASA validation:** The Prandtl-D program (RC flying wings) experimentally confirmed proverse yaw with bell-shaped loading. The aircraft could make coordinated turns with ailerons alone, no rudder needed.

### Recommendation for AeroForge

**Do NOT use bell-shaped loading** for our conventional-tail sailplane:
- Bell loading requires ~12 degrees washout, which severely reduces maximum Cl
- The proverse yaw benefit is most relevant for flying wings (no vertical tail)
- Our design has a rudder for yaw coordination
- The 22% span extension benefit assumes a structural-weight-limited design; our 3D-printed wing is not weight-optimized to the same degree as a composite spar

**Instead, use an optimized non-linear washout:**
- Target: approximately elliptical loading in thermal flight
- Root to tip washout: 3-5 degrees total
- Non-linear: more twist in outer 40% of span
- Calculate using lifting-line theory (XFLR5) at the design Cl
- The exact distribution should vary with flight condition (more washout benefits thermal turning, less washout benefits speed)

**Aeroelastic twist:** At our wing loading, the carbon tube main spar is stiff enough that aeroelastic twist is minimal. However, 3D-printed skin panels may flex slightly under load, adding passive washout. This should be analyzed in FreeCAD FEM.

**Sources:**
- [NASA TP-2016-219072: On Wings of the Minimum Induced Drag (Bowers)](https://ntrs.nasa.gov/api/citations/20160003578/downloads/20160003578.pdf)
- [Experimental Flight Validation of Prandtl 1933 Bell Spanload (NASA)](https://ntrs.nasa.gov/api/citations/20210014683/downloads/H3284FINAL.pdf)
- [Prandtl-D (Wikipedia)](https://en.wikipedia.org/wiki/Prandtl-D)
- [Twist Distributions for Swept Wings (RC Soaring Digest)](https://medium.com/rc-soaring-digest/twist-distributions-for-swept-wings-5b9f6ec2bb1)
- [Al Bowers and the Bell-Shaped Curve (Sustainable Skies)](https://sustainableskies.org/al-bowers-bell-shaped-curve/)
- [Aerodynamic Design and Strength Analysis -- Bell-Shaped Lift Distribution (MDPI)](https://www.mdpi.com/2226-4310/9/1/13)

---

## 9. Tail Volume Coefficients

### Standard Formulas

**Horizontal tail volume coefficient:**
VH = (SH x LH) / (SW x MAC)

Where:
- SH = horizontal tail area
- LH = distance from tail aerodynamic center to aircraft CG
- SW = wing area
- MAC = mean aerodynamic chord

**Vertical tail volume coefficient:**
VV = (SV x LV) / (SW x b)

Where:
- SV = vertical tail area
- LV = distance from vertical tail AC to aircraft CG
- b = wingspan

### Typical Values for RC Sailplanes

| Aircraft Type | VH | VV |
|--------------|-----|------|
| General aviation | 0.50-1.00 | 0.03-0.08 |
| RC sailplane (typical) | 0.30-0.50 | 0.02-0.04 |
| F5J competition | 0.40-0.50 | 0.02-0.03 |
| Prestige 2PK PRO (reference) | **0.45** | **0.025** |
| DLG gliders | 0.35-0.45 | 0.02-0.03 |

**Stability margin:** CG should be 5-25% of MAC ahead of neutral point:
- 5% = responsive, agile (competition setup)
- 10-15% = moderate stability (good for thermal flying)
- 25% = very stable, sluggish (beginner setup)

**Simplified CG formula:** CG position = (10 + 40 x VH) as % of MAC from leading edge

### Tail Configuration Comparison for F5J

| Config | Advantages | Disadvantages | F5J Usage |
|--------|-----------|---------------|-----------|
| **Conventional (+ tail)** | Simple, proven, independent control, lightest | More drag (2 surfaces in flow), TE wake interaction | Declining |
| **T-tail** | H-stab above wing wake (cleaner flow), smaller H-stab needed | Heavier (V-stab supports H-stab), deep stall risk | Rare in F5J |
| **V-tail** | Lighter (2 surfaces vs. 3), less drag, compact | Control mixing needed, reduced rudder authority, requires more deflection | **Popular** |
| **X-tail** | Good rudder authority, easy alignment, redundancy | Slightly more drag than V-tail, slightly heavier | **Most popular** |

**Competition trend:** X-tail and V-tail dominate modern F5J. Conventional is declining. T-tail is rare.

### Sizing for AeroForge

Using Prestige 2PK PRO values as reference (VH = 0.45, VV = 0.025):

Our parameters:
- SW = 41.6 dm^2 = 4,160 cm^2
- MAC = ~170mm (approximate for our taper ratio)
- b = 2,560mm
- Boom length (estimated LH = LV): ~700mm from CG to tail AC

**Required horizontal tail area:**
SH = VH x SW x MAC / LH = 0.45 x 4160 x 170 / 700 = **455 cm^2 = 4.55 dm^2**

**Required vertical tail area:**
SV = VV x SW x b / LV = 0.025 x 4160 x 2560 / 700 = **381 cm^2 = 3.81 dm^2**

These are reasonable starting values. Final sizing requires XFLR5 stability analysis.

**Sources:**
- [Tail Volume Coefficient (RCU Forums)](https://www.rcuniverse.com/forum/aerodynamics-76/1659429-tail-volume-coefficient.html)
- [How Big The Tail (EAA)](https://www.eaa62.org/technotes/tail.htm)
- [Empennage Sizing with Tail Volume (HAW Hamburg)](https://www.fzt.haw-hamburg.de/pers/Scholz/Aero/AERO_PUB_INCAS_TailVolume_Vol13No3_2021.pdf)
- [Aircraft Horizontal and Vertical Tail Design (AeroToolbox)](https://aerotoolbox.com/design-aircraft-tail/)
- [Prestige 2PK PRO Specifications (Samba)](https://f3j.com/pages/prestige-pk2-pro)

---

## 10. 3D-Printed Structural Innovations

### Optimal Wall Thickness for Wing Skins

| Material | Application | Wall Thickness | Notes |
|----------|------------|---------------|-------|
| LW-PLA (foamed, 230C) | Wing skin (non-structural) | 0.5-0.6mm | Vase mode or 2-perimeter |
| LW-PLA (foamed, 230C) | D-box shell (structural) | 0.6-0.8mm | Primary torsion structure |
| CF-PLA | Ribs/formers | 1.0-1.2mm | 30% gyroid infill |
| CF-PETG | Servo mounts | 1.6-2.0mm | Impact resistant |
| CF-PETG | Motor mount | 2.0-3.0mm | High stress |

### LW-PLA Printing Parameters

| Parameter | Non-foamed | Foamed (optimal) | Max foam |
|-----------|-----------|-------------------|----------|
| Temperature | 190-210C | **230C** | 270C |
| Density (g/cm^3) | 1.24 | **0.70-0.85** | 0.54 |
| Flow rate | 100% | **45-65%** | 35% |
| Volume expansion | 1.0x | **1.5-1.8x** | 2.2x |
| Weight reduction | 0% | **35-45%** | 65% |

**Key insight:** "One roll of LW-PLA can be used as 2.2 rolls of ordinary PLA" at maximum foaming.

**Bambu printer settings** (A1/P1S):
- **Temperature:** 230C for optimal foam (balance of weight and strength)
- **Speed:** Moderate (50-80mm/s) -- speed affects foaming uniformity
- **Fan:** Moderate (40-60%) -- needed to solidify foamed structure
- **Retraction:** Minimize -- LW-PLA oozes badly during retraction (design for continuous extrusion)

**Weight comparison** (fully instrumented wing):
- PLA wing: 600g
- LW-PLA wing: **372g** (38% lighter)

### Infill Patterns for Maximum Strength-to-Weight

| Pattern | Strength | Weight | Stiffness | Print Time | Best For |
|---------|----------|--------|-----------|------------|----------|
| Gyroid | Excellent | Low | Isotropic | Moderate | **General use, ribs** |
| Honeycomb | Good | Low | Anisotropic | Fast | Flat panels |
| Cubic | Good | Low | Isotropic | Moderate | Bulkheads |
| Lines/Grid | Poor | Low | Very anisotropic | Fast | Non-structural |
| Kelvin lattice | **Best** | **Lowest** | Good | Slow | Topology-optimized parts |

**PhysicsX study finding:** "22% infill with three perimeter wall lines, striking the ideal balance between structural integrity and weight" -- for their 1m wingspan glider in TPU.

**Recommendation for AeroForge:**
- Wing skin: **0% infill, 1-2 perimeters** (vase mode or equivalent)
- D-box: **0% infill, 2 perimeters** at 0.6-0.8mm each
- Ribs: **20-30% gyroid infill** with topology-optimized lightening holes
- Servo mounts: **30-40% gyroid infill** with 3+ perimeters
- Motor mount: **40-50% gyroid infill** with 4+ perimeters

### Spar Integration with Printed Structure

**Carbon tube main spar (8mm OD):**
- Print spar tunnels as part of each rib
- Tunnel ID: 8.1-8.2mm (0.1-0.2mm clearance for slide-on fit)
- Reinforce tunnel walls to 1.5-2.0mm minimum
- Add printed locking features (collet clips, pins, or wedge slots)
- Carbon tube carries ALL bending loads; printed structure transfers loads to spar

**Spruce rear spar (5x3mm):**
- Print rectangular slots in each rib
- Slot dimensions: 5.1x3.1mm (snug fit for glue-in)
- Spruce glued in with CA or epoxy
- Carries torsion + trailing edge loads

**Carbon tube spar design rules:**
- Spar must pass through all 5 panels per half-wing continuously
- Panel joints: spar provides alignment and structural continuity
- Each panel is self-supporting on the spar even before panel-to-panel bonding
- Panel joint reinforcement: printed female/male interlocking features + CA glue

### D-Box Construction

The D-box (leading edge to ~30% chord) is the primary torsion structure:

**Print approach:**
1. D-box is a closed shell, printed as part of the wing panel
2. Outer skin: 0.6-0.8mm LW-PLA
3. Inner shear web at ~30% chord: 0.6mm connecting upper and lower skins
4. Carbon spar tunnel at ~25-30% chord (inside the D-box)
5. Interior: hollow or with minimal geodesic webbing

**Critical dimensions:**
- D-box depth (chordwise): ~30% of chord = 63mm at root, 35mm at tip
- D-box must maintain airfoil contour accuracy to +/-0.2mm
- Trailing edge of D-box is the hinge line for ailerons/flaps
- Print orientation: chord-aligned layers give spanwise riblet texture

### Vase Mode vs. Multi-Perimeter Printing

**Vase mode (spiral/continuous):**
- Single wall, no retractions, no ooze
- Perfect for LW-PLA (which oozes terribly)
- Internal ribs must be designed into the single continuous path
- Diagonal grid ribs "split into four quadrants" so the slicer treats entire print as one continuous perimeter

**Multi-perimeter (2-3 walls):**
- Stronger but heavier
- More retractions = more ooze points with LW-PLA
- Better for structural components (D-box, spar area)

**Hybrid approach (recommended):**
- Wing aft section (flaps/ailerons): vase mode, single wall
- D-box: 2 perimeters for torsion strength
- Rib stations: increase wall count locally (possible with Bambu's adaptive walls)

**Sources:**
- [PhysicsX AI-Designed 3D-Printed Glider](https://www.physicsx.ai/newsroom/from-code-to-sky-the-journey-of-our-ai-designed-3d-printed-glider)
- [A Guide To 3D Printing Model Aircraft Wings (Hackaday)](https://hackaday.com/2022/08/26/a-guide-to-3d-printing-model-aircraft-wings/)
- [LW-PLA Version D Wing (Printables)](https://www.printables.com/model/392053-lw-pla-rc-plane-version-d-wing)
- [LW-PLA Pusher Prop Plane (Printables)](https://www.printables.com/model/282480-lw-plapla-rc-plane-pusher-propeller-pprop)
- [Planeprint RISE](https://www.planeprint.com/rise)
- [3D Printing A Fully Functional RC Aircraft (Model Aviation)](https://www.modelaviation.com/3d-printing-rcaircraft)
- [ColorFabb LW-PLA for RC Planes](https://colorfabb.com/blog/post/lightweight-3d-printing-filaments-for-rc-planes)
- [SainSmart LW-PLA Specifications](https://www.sainsmart.com/products/lightweight-pla)

---

## 11. Reynolds Number Effects at Model Scale

### The Critical Re Ranges

| Re Range | Boundary Layer Behavior | Performance Impact |
|----------|------------------------|--------------------|
| **Re < 30,000** | Laminar separation, no reattachment | Very high drag, poor lift, stall-prone |
| **Re 30,000-50,000** | Large separation bubble, may not reattach | High drag, reduced Cl_max, unstable |
| **Re 50,000-80,000** | Separation bubble reattaches near TE | Moderate drag penalty, sensitive to conditions |
| **Re 80,000-150,000** | Small separation bubble, clean reattachment | **Acceptable performance**, airfoil-dependent |
| **Re 150,000-300,000** | Transition zone, bubble shrinks rapidly | Good performance, approaching "adult" behavior |
| **Re > 300,000** | Natural transition, minimal bubble | Near full-scale performance |

### What Changes Between Re 50k and Re 200k

This is the exact range our wing spans from tip to root:

**At Re 50,000 (our tip, thermalling):**
- Laminar separation bubble extends over 20-40% of upper surface
- Maximum Cl is significantly reduced (Cl_max ~0.8-1.0 vs. 1.2-1.5 at higher Re)
- Drag polar has a pronounced "bubble drag" hump
- Thin airfoils outperform thick ones (cambered plates may even beat thick airfoils)
- **Critical:** Surface roughness (dust, bugs, rain) can either help (trip the bubble) or hurt (premature transition)

**At Re 100,000 (our mid-span, thermalling):**
- Separation bubble is smaller, typically 10-20% of chord
- Cl_max recovers to ~1.0-1.2
- Airfoil selection matters significantly -- AG series designed for this range
- Turbulator strips become effective and beneficial
- Reasonable performance achievable with careful design

**At Re 200,000 (our root, cruise):**
- Small separation bubble or natural transition
- Near "normal" aerodynamic behavior
- Cl_max ~1.2-1.4 (airfoil-dependent)
- Most RC airfoils work reasonably well
- Surface finish becomes more important (smooth = less drag)

### Implications for Spanwise Airfoil Selection

The dramatic change in flow physics from root to tip means:
1. **Root airfoil (Re ~120-170k):** Can use moderate thickness (8-10%), conventional design
2. **Mid-span (Re ~80-120k):** Needs thinner, more carefully designed airfoil (AG35 family)
3. **Tip (Re ~55-85k):** Must use very thin, low-Re-optimized airfoil (AG03, AG38)
4. **The transition is NOT linear** -- performance degrades rapidly below Re ~80,000

This is why top F5J competition gliders taper their airfoil thickness from 7-8% at root to 5-6% at tip. Our current AG24 (10%) to AG03 (~7%) progression may need to be reconsidered -- even the root may benefit from a thinner profile at our wing loading.

**Key design rule:** At Re < 80,000, reduce airfoil thickness. The penalty for "too thick" is much worse than the penalty for "too thin" at low Reynolds numbers.

**Sources:**
- [Low Reynolds Number Airfoil Characteristics (Cadence)](https://resources.system-analysis.cadence.com/blog/msa2022-low-reynolds-number-airfoil-characteristics)
- [Basic Understanding of Airfoil Characteristics at Low Re (AIAA)](https://arc.aiaa.org/doi/10.2514/1.C034415)
- [Low Reynolds Number Airfoil Design Lecture Notes (Selig)](https://m-selig.ae.illinois.edu/pubs/Selig-2003-VKI-LRN-Airfoil-Design-Lecture-Series.pdf)
- [NACA0012 at Re 50,000-140,000 (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S0142727X24003801)

---

## 12. Recent Competition Trends (2024-2025)

### 2025 FAI F5J World Championships (Cordoba, Argentina)

**Results:**
- **Senior World Champion:** Joe Wurts (New Zealand) -- 4th world title
  - Aircraft: Vladimir's Model Plus X
  - Flying weight: 1,380g with 493g ballast per wing
  - Converted to DualSky direct-drive motors
  - Key strategy: launching at lowest altitude that scored
- **Junior World Champion:** John Bradley (USA)
  - Aircraft: Samba Prestige 2PK PRO
- **Team World Champions:** Czech Republic
  - All flew Prestige 2PK and 2PK PRO exclusively

**60 senior + 12 junior competitors from 18 nations, 11 rounds completed.**

### 2024 FAI F5J European Championships (Deva, Romania)

- **Team Champions:** France (both junior and senior)

### Key Competition Design Trends

1. **Wingspan convergence at 3.9-4.0m** for top competition
2. **Ultra-thin airfoils** (5-7.8% thickness) designed for Re 80,000-200,000
3. **Multiple airfoils along span** (5-9 different profiles blended)
4. **Solid core (Rohacell) construction** dominates for geometric accuracy and low weight
5. **X-tail or V-tail** (conventional declining)
6. **Ballast systems** essential for wind adaptation (up to 1,400g added)
7. **4-6 servo wing** with full camber change capability
8. **Direct-drive motors** gaining popularity (eliminating gearbox failure mode)
9. **Flying weight** of top models: 1,000-1,400g RTF (3.9m span)
10. **Wing loading** in calm: 12-16 g/dm^2; ballasted for wind: up to 30 g/dm^2

### What Top Pilots Do Differently

**It's pilot, not plane:**
- Joe Wurts: "The current popular choices are all great sailplanes"
- Thermal reading ability before launch is the #1 differentiator
- Low-altitude save technique (gentle inputs, flat circles)
- Risk management in launch altitude vs. thermal probability
- Composure across 10+ competition rounds
- Ballast strategy adapted to conditions round-by-round

### Relevance to AeroForge

Our 2.56m / 750-850g design cannot compete with 4m composite competition gliders on raw performance. But 3D printing offers:
- **Rapid iteration** (test 10 wing variants in a week)
- **Unique airfoil at every rib** (vs. 5-9 stations in composite)
- **Integrated features** (gap seals, turbulators, winglets) at zero cost
- **Topology-optimized structure** (geodesic lattice, no extra tooling cost)
- **Accessible to anyone** with a $300 3D printer (vs. $2,000-4,000 competition molded gliders)

**Sources:**
- [2025 F5J World Championships Results (FAI)](https://www.fai.org/news/results-2025-fai-f5j-world-champions-electric-powered-thermal-duration-gliders)
- [Joe Wurts 2025 F5J Worlds (Model Aviation)](https://www.modelaviation.com/article/joe-wurts-2025-f5j-world-championships)
- [Samba at 2025 Worlds (f3j.com)](https://f3j.com/blogs/news/world-championship-f5j-2025-argentina-1)
- [2024 F5J European Championships (FAI)](https://www.fai.org/news/team-france-triumphs-2024-fai-f5j-european-championships-electric-powered-thermal-duration)
- [Prestige 2PK PRO (Samba)](https://f3j.com/pages/prestige-pk2-pro)
- [Prestige 2PK (Samba)](https://f3j.com/pages/prestige-2pk)

---

## 13. Design Action Items for AeroForge

Based on this research, the following actions should be evaluated:

### High Priority
1. **Re-evaluate root airfoil:** AG24 at 10% may be too thick. Consider AG35 (~7-8%) or the AG44ct-AG47ct series designed for 2M aileron gliders with flaps. Run XFOIL comparison at Re 100,000-170,000.
2. **Re-evaluate tip airfoil:** AG03 at ~7% may still be slightly thick for Re 55,000-85,000. Consider AG38 or even thinner. Run XFOIL at Re 55,000-85,000.
3. **Implement non-linear washout:** 3-5 degrees total, concentrated in outer 40% of span. Calculate with XFLR5 lifting-line analysis.
4. **Size tail surfaces:** Use VH=0.45, VV=0.025 as starting point. Verify with XFLR5 stability analysis.
5. **Choose tail configuration:** V-tail or X-tail (both lighter and lower drag than conventional).

### Medium Priority
6. **Flap configuration detailed design:** 28% chord flaps, 4-servo minimum, define all flight modes and deflection angles per Section 6.
7. **D-box detailed design:** 0.6-0.8mm LW-PLA shell, closed D-box to 30% chord, with carbon spar integration.
8. **Winglet design:** Blended, ~80-100mm height, thin airfoil, integral with tip panel.
9. **Surface finish strategy:** Define sand/no-sand zones per Section 7 table.

### Lower Priority (But Valuable)
10. **Geodesic lattice internal structure:** Implement Kelvin-type lattice in D-box interior if FEM analysis confirms benefit.
11. **Printed micro-VGs:** Test on outer panels at 20% chord for Re < 80,000 stations.
12. **LW-PLA print optimization:** Determine exact foaming parameters for Bambu A1/P1S at 230C, 45-55% flow rate.

---

## 14. Key Numerical Reference Table

Quick-reference numbers for the design:

| Parameter | Value | Source |
|-----------|-------|--------|
| Root Re (thermal, 8m/s) | ~118,000 | Calculated |
| Tip Re (thermal, 8m/s) | ~64,000 | Calculated |
| Root Re (cruise, 11m/s) | ~162,000 | Calculated |
| Tip Re (cruise, 11m/s) | ~88,000 | Calculated |
| Optimal root airfoil thickness | 7-8% | Competition analysis |
| Optimal tip airfoil thickness | 5-6% | Competition analysis |
| VH (horizontal tail volume) | 0.45 | Prestige 2PK PRO |
| VV (vertical tail volume) | 0.025 | Prestige 2PK PRO |
| Flap chord | 28% of local chord | Competition standard |
| Washout (total) | 3-5 deg | Calculated |
| Wing loading target | 18-22 g/dm^2 | Our constraint |
| Competition wing loading | 12-16 g/dm^2 | Top F5J data |
| LW-PLA density (230C) | 0.70-0.85 g/cm^3 | Manufacturer data |
| LW-PLA skin thickness | 0.5-0.6mm | Community practice |
| D-box shell thickness | 0.6-0.8mm | Engineering estimate |
| Kelvin lattice weight saving | 9.5% vs. rib-spar | PMC study |
| Winglet height | 80-100mm | Calculated (~5-8% semi-span) |
| Winglet cant angle | 70-80 deg | Maughmer recommendation |
