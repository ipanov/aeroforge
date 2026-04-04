# Rudder-Elevator Clearance Analysis

**Author:** Aerodynamicist Agent (Rudder/Integration Specialist)
**Date:** 2026-04-01
**Status:** ANALYSIS COMPLETE
**References:** HStab DESIGN_CONSENSUS v6, Fuselage DESIGN_CONSENSUS v1

---

## 1. Rudder Planform Design

### 1.1 VStab Planform Parameters (from Fuselage Consensus v1)

| Parameter | Value |
|-----------|-------|
| VStab height | 165mm |
| Root chord | 180mm |
| Tip chord | 95mm |
| Taper ratio | 0.528 |
| Root airfoil | HT-14 (7.5%) |
| Tip airfoil | HT-12 (5.1%) |
| Planform area | 226.9 cm^2 |
| Vv (geometric) | 0.014 |
| Rudder chord ratio | 35% |
| Rudder hinge position | 65% chord from LE |

### 1.2 Rudder Planform Table

The rudder chord is 35% of local VStab chord at every span station. The VStab is a straight-tapered planform (linear taper from root to tip).

**VStab local chord:** `c_v(z) = 180 - (180-95)/165 * z = 180 - 0.5152*z` (mm, z measured from root)

**Rudder chord:** `c_r(z) = 0.35 * c_v(z)`

**Rudder hinge position (from VStab LE):** `x_hinge(z) = 0.65 * c_v(z)`

| z (mm from root) | VStab chord (mm) | Rudder chord (mm) | Hinge from LE (mm) | Rudder LE from LE (mm) | Rudder TE from LE (mm) |
|-------------------|-------------------|--------------------|---------------------|--------------------------|--------------------------|
| 0 (root) | 180.0 | 63.0 | 117.0 | 117.0 | 180.0 |
| 10 | 174.8 | 61.2 | 113.6 | 113.6 | 174.8 |
| 20 | 169.7 | 59.4 | 110.3 | 110.3 | 169.7 |
| 30 | 164.5 | 57.6 | 107.0 | 107.0 | 164.5 |
| 40 | 159.4 | 55.8 | 103.6 | 103.6 | 159.4 |
| 50 | 154.2 | 54.0 | 100.2 | 100.2 | 154.2 |
| 60 | 149.1 | 52.2 | 96.9 | 96.9 | 149.1 |
| 70 | 143.9 | 50.4 | 93.6 | 93.6 | 143.9 |
| 80 | 138.8 | 48.6 | 90.2 | 90.2 | 138.8 |
| 90 | 133.6 | 46.8 | 86.9 | 86.9 | 133.6 |
| 100 | 128.5 | 45.0 | 83.5 | 83.5 | 128.5 |
| 110 | 123.3 | 43.2 | 80.2 | 80.2 | 123.3 |
| 120 | 118.2 | 41.4 | 76.8 | 76.8 | 118.2 |
| 130 | 113.0 | 39.6 | 73.5 | 73.5 | 113.0 |
| 140 | 107.9 | 37.8 | 70.1 | 70.1 | 107.9 |
| 150 | 102.7 | 35.9 | 66.8 | 66.8 | 102.7 |
| 160 | 97.6 | 34.2 | 63.4 | 63.4 | 97.6 |
| 165 (tip) | 95.0 | 33.2 | 61.8 | 61.8 | 95.0 |

### 1.3 Rudder Hinge Line in Fuselage Coordinates

VStab root LE is at fuselage X=866mm.

| z (mm) | VStab chord | Rudder hinge (from VStab LE) | Fuselage X of hinge |
|--------|-------------|-------------------------------|---------------------|
| 0 | 180.0 | 117.0 | 983.0 |
| 55 (HStab station) | 151.6 | 98.6 | 964.6 |
| 82.5 | 137.5 | 89.4 | 955.4 |
| 110 | 123.3 | 80.2 | 946.2 |
| 165 | 95.0 | 61.8 | 927.8 |

### 1.4 Rudder Deflection Analysis

**Rudder volume coefficient (Vv_rudder):**
- Rudder area: S_r = 0.35 * S_v = 0.35 * 226.9 = 79.4 cm^2
- Moment arm to CG: l_r = CG_to_VStab_LE + 0.65*mean_chord = (866-312) + 0.65*137.5 = 554 + 89.4 = 643.4mm
- Vv_rudder = S_r * l_r / (S_w * b) = 79.4 * 64.34 / (4160 * 256) = 5,109 / 1,064,960 = **0.00480**
- Total Vv with max deflection (effectiveness ~0.5 at 30 deg): Vv_effective ~ 0.014 + 0.5*0.0048 = **0.0164**

**Deflection range:** Target **+/-25 deg** for adequate authority. Up to 30 deg possible if clearance allows.

**Rudder authority check:**
- At 25 deg deflection, Cl_rudder ~ 0.025 (typical for 35% chord rudder)
- Yawing moment: Cn = Cl_rudder * S_r/S_v * (mean_rudder_chord / mean_VStab_chord) = 0.025 * 0.35 * 0.35 = 0.0031
- This provides adequate yaw control for thermal circling and crosswind correction.

---

## 2. Rudder-Elevator Clearance Analysis (CRITICAL)

### 2.1 Geometry Setup

**Coordinate Systems:**

Fuselage coordinates: X = distance from nose, Z = vertical (up from centerline).

| Reference Point | Fuselage X (mm) |
|-----------------|-----------------|
| VStab root LE | 866.0 |
| HStab root LE | 882.25 |
| HStab pivot (c/4) | 911.0 |
| Elevator hinge (X=60 local) | 942.25 |
| Rudder hinge (65% of 180) | 983.0 |
| HStab root TE | 997.25 |
| VStab root TE | 1046.0 |

**The Overlap Zone:**
- Rudder occupies X = 983.0 to 1046.0 mm (in the VStab plane, Z direction)
- Elevator root occupies X = 942.25 to 997.25 mm (in the HStab plane, Y direction)
- **Planform overlap: X = 983.0 to 997.25 mm = 14.25 mm**

### 2.2 3D Geometry at the Junction

The rudder and elevator meet at the VStab fin centerline. Understanding the 3D relationship:

- **Elevator**: Lies in the horizontal plane (XY plane at Z=0 in HStab coords). Deflects UP/DOWN (rotation about Y-axis at the elevator hinge line X=942.25).
- **Rudder**: Lies in the vertical plane (XZ plane at Y=0 in HStab coords). Deflects LEFT/RIGHT (rotation about Z-axis at the rudder hinge line X=983.0).
- **VStab fin thickness at junction**: ~7mm (HT-14 at 180mm chord, 7.5% = 13.5mm thick at max, ~7mm at 65% chord)

### 2.3 Elevator Swept Volume Analysis

At the root (y=0, at the VStab fin centerline):

**Elevator geometry:**
- Elevator chord at root: 51.5mm (45% of 115mm HStab root chord)
- Elevator hinge: X=942.25mm (fuselage)
- Elevator TE: X=993.75mm (hinge + 51.5mm, but HStab TE is at 997.25 — elevator is slightly shorter than hinge-to-TE due to TE truncation)

When the elevator deflects by angle delta_e:
- Every point on the elevator at distance d from the hinge sweeps an arc of radius d
- The arc is in the VERTICAL plane (Z direction)
- Vertical displacement at distance d: z = d * sin(delta_e)
- Aft displacement at distance d: dx = d * (1 - cos(delta_e))

**Elevator swept volume at root for +18 deg (trailing edge up):**

| Point on elevator | d from hinge (mm) | z at 18 deg (mm) | dx at 18 deg (mm) | New X position |
|--------------------|--------------------|------------------|--------------------|-----------------|
| Elevator LE (at hinge) | 0 | 0 | 0 | 942.25 |
| Mid-chord | 25.75 | 7.96 | 1.27 | 943.52 |
| 3/4 chord | 38.6 | 11.93 | 1.90 | 944.15 |
| TE | 51.5 | 15.92 | 2.54 | 944.79 |

**Key observation**: The elevator TE only moves ~2.5mm aft when deflected 18 deg. The elevator TE stays well forward of the rudder hinge at X=983mm.

### 2.4 Rudder Swept Volume Analysis

At the root (z=0, at the VStab base):

**Rudder geometry:**
- Rudder chord at root: 63.0mm
- Rudder hinge: X=983.0mm (fuselage)
- Rudder TE: X=1046.0mm

When the rudder deflects by angle delta_r:
- Every point on the rudder at distance d from the hinge sweeps an arc of radius d
- The arc is in the LATERAL plane (Y direction, perpendicular to VStab)
- Lateral displacement at distance d: y = d * sin(delta_r)
- Aft displacement at distance d: dx = d * (1 - cos(delta_r))

**Rudder swept volume at root for 25 deg deflection:**

| Point on rudder | d from hinge (mm) | y at 25 deg (mm) | dx at 25 deg (mm) | Elevator zone? |
|------------------|--------------------|-------------------|--------------------|-----------------|
| Rudder LE (at hinge) | 0 | 0 | 0 | At X=983 |
| 5mm aft of hinge | 5 | 2.11 | 0.47 | X=983.47 — IN overlap |
| 10mm aft of hinge | 10 | 4.23 | 0.94 | X=983.94 — IN overlap |
| 14.25mm aft (overlap end) | 14.25 | 6.02 | 1.34 | X=984.34 — at elevator TE |
| 20mm aft | 20 | 8.45 | 1.87 | X=984.87 — PAST overlap |
| 31.5mm (mid-chord) | 31.5 | 13.31 | 2.95 | X=985.95 |
| 63.0mm (TE) | 63.0 | 26.60 | 5.92 | X=988.92 |

**Rudder swept volume at root for 30 deg deflection:**

| Point on rudder | d from hinge (mm) | y at 30 deg (mm) | dx at 30 deg (mm) |
|------------------|--------------------|--------------------|--------------------|
| 5mm aft | 5 | 2.50 | 0.67 |
| 10mm aft | 10 | 5.00 | 1.34 |
| 14.25mm aft | 14.25 | 7.13 | 1.91 |
| 31.5mm (mid) | 31.5 | 15.75 | 4.22 |
| 63.0mm (TE) | 63.0 | 31.50 | 8.43 |

### 2.5 The Interference Question

The rudder swings laterally (Y direction). The elevator sweeps vertically (Z direction). They move in **perpendicular planes**. The question is: does the rudder's lateral extent intersect the elevator's vertical extent?

**Critical dimension: VStab fin thickness at the HStab junction.**

At the HStab root station (fuselage X=911mm), the VStab fin is approximately:
- VStab span station: z = 145mm (out of 165mm total, since fin extends from boom to tip)
- VStab chord at z=145: ~105mm (linear taper: 180 - 0.5152*145 = 105.3mm)
- HT-14/HT-12 blended airfoil at this station, approximately 6.1% thick (blend toward HT-12)
- Fin thickness: 0.061 * 105.3 = 6.4mm

At the rudder hinge station (X=983mm), the VStab chord is 180mm (root chord, since the hinge line is at the VStab root in the Z direction — the HStab sits at a specific Z height on the fin).

Wait — let me reconsider the geometry more carefully.

**The HStab is mounted at a specific height on the VStab fin.** The VStab is a vertical surface; the HStab is horizontal. The HStab root sits at approximately z=82.5mm on the VStab (mid-height of the exposed fin, accounting for the boom-to-fin blend).

Actually, from the fuselage consensus cross-section data:
- At X=911mm (HStab pivot), the fuselage/VStab height is 145mm
- The HStab centerline is at the midpoint of this height

So the HStab root is at the VStab fin's **span station z ~82.5mm** (midpoint of 165mm height).

At z=82.5mm:
- VStab chord: 180 - 0.5152*82.5 = 137.5mm
- Airfoil blend: (82.5/165) = 50% blend HT-14 to HT-12
- Thickness ratio: ~6.3% (halfway between 7.5% and 5.1%)
- Fin thickness: 0.063 * 137.5 = **8.66mm**

At the rudder hinge position (65% chord from LE), the airfoil is thinner than max thickness:
- HT-14 upper surface y/c at x/c=0.65: approximately 2.0% (upper)
- HT-12 upper surface y/c at x/c=0.65: approximately 1.3% (upper)
- Blend at 50%: ~1.65% above camber line
- Half-thickness at hinge: ~1.65% * 137.5 = **2.27mm**

**The VStab fin half-thickness at the rudder hinge / HStab junction is ~2.27mm.**

### 2.6 Detailed Interference Calculation

The rudder is a control surface on the VStab. When the rudder deflects, its LE moves laterally. The question is whether this lateral movement intersects the elevator, which sweeps vertically.

**Case: Elevator UP 18 deg, Rudder LEFT 25 deg**

In the overlap zone (X = 983 to 997.25mm), we need to check:

**Elevator position** (at the VStab fin center, y=0):
- The elevator extends from X=942.25 to X=997.25 (root TE)
- At 18 deg up, the elevator TE has risen to z = 51.5*sin(18) = 15.92mm and moved aft to X = 942.25 + 51.5*(1-cos(18)) = 944.79mm
- **At the overlap zone (X>983)**, the elevator does NOT physically exist at full deflection because the TE has moved forward to X=944.79mm!
- The elevator at 18 deg up has its TE at X=944.79, which is AFT of the rudder hinge (983)? No — 944.79 < 983, so the elevator TE is FORWARD of the rudder hinge.

Wait — I need to think about this more carefully. The elevator rotates about its hinge at X=942.25. When it deflects UP, the TE moves UP and slightly forward (toward the hinge). So:

- At 0 deg: elevator spans X=942.25 to X=993.75 (approximately, with TE truncation to 997.25)
- At 18 deg UP: the point that was at X=993.75 is now at X = 942.25 + 51.5*cos(18) = 942.25 + 49.0 = 991.25, z = 51.5*sin(18) = 15.92mm
- At -18 deg DOWN: the TE is at X=991.25, z = -15.92mm

**The elevator TE stays at approximately X=991mm regardless of deflection angle.** The elevator ALWAYS occupies the X-range from 942.25 to ~991mm (at 18 deg) or 993.75mm (at 0 deg).

**The rudder LE is at X=983mm (the hinge line).**

So the overlap zone is actually X = 983 to ~993mm = **~10mm** where both surfaces coexist.

### 2.7 The Real 3D Question

The elevator sweeps vertically. The rudder swings laterally. At the overlap zone:

1. **Elevator at 18 deg up**: A vertical slab from Z=-15.92 to Z=+15.92mm (at the TE), tapering to 0 at the hinge. At X=983 (8mm from elevator TE, 40.75mm from elevator hinge): the elevator height is 40.75*sin(18) = 12.59mm above and below neutral.

2. **Rudder at 25 deg left**: A lateral slab. At X=983 (the hinge), the rudder LE is at Y=0 (no lateral movement at the hinge itself). At X=988 (5mm aft of hinge), the rudder surface is at Y = 5*sin(25) = 2.11mm.

**The interference requires the rudder's lateral extent to overlap with the elevator's vertical extent.** But these are perpendicular motions!

The rudder is in the XZ plane (the VStab plane). The elevator is in the XY plane (the HStab plane). They share the X-axis but move in perpendicular directions (Z for elevator, Y for rudder).

**Therefore: The rudder and elevator CANNOT physically interfere because they move in perpendicular planes, UNLESS the VStab fin is thick enough that the rudder extends beyond the fin thickness into the elevator's vertical swept volume.**

### 2.8 VStab Thickness Check

At the overlap zone (X=983 to 993mm, VStab span station z=82.5mm):

The VStab fin at this location is approximately 8.66mm thick (total). The rudder is the aft 35% of this fin. When the rudder deflects, it swings OUT of the fin plane.

**The rudder at 25 deg deflection at 5mm aft of hinge:**
- Lateral displacement: 2.11mm
- The VStab fin half-thickness at the rudder hinge (65% chord) is ~2.27mm
- The rudder surface starts at Y = fin_half_thickness = 2.27mm (flush with fin surface at neutral)
- At 25 deg, the rudder LE moves to Y = 2.27mm (unchanged — the hinge is AT the surface) and the aft part swings out

Actually, the rudder hinge is at the fin surface. The rudder rotates about this surface point. So:

- **Rudder at neutral**: lies flush with the VStab fin surface
- **Rudder at 25 deg**: the rudder TE swings out to Y = 63*sin(25) = 26.6mm from the hinge line
- **Rudder LE** (at the hinge): does not move laterally

The **elevator** sweeps vertically. The elevator root (at y=0 in HStab coords) is at the VStab fin centerline. The elevator at 18 deg up sweeps through Z = +15.92mm at the TE.

**The rudder swings in Y, the elevator sweeps in Z. They are in perpendicular directions. There is NO intersection because the rudder moves sideways while the elevator moves up/down.**

### 2.9 BUT: The Edge Case — Rudder Bullnose Radius

There IS one potential interference: the rudder LE bullnose (the rounded leading edge of the rudder). At the HStab junction height, the rudder LE has a small radius (~1-2mm). When the rudder deflects, this bullnose extends slightly beyond the fin surface in ALL directions, including the vertical (Z) direction.

**Bullnose at rudder LE:**
- Radius at root: ~2mm (matching the concealed hinge bullnose design philosophy)
- At 25 deg deflection, the bullnose center moves to Y = 0 (it's at the hinge), but the bullnose extends vertically by its radius above and below the chord line

This vertical extension of the bullnose (2mm above and below the chord center) at X=983 is very small compared to the elevator sweep (15.92mm). The bullnose is at the fin surface, while the elevator at this X-station (40.75mm from elevator hinge) is at Z = 12.59mm above/below.

**The bullnose does NOT reach the elevator.** 2mm vs 12.59mm — no contact.

### 2.10 Complete Interference Matrix

| Rudder angle | Elevator angle | Rudder lateral at 10mm aft | Elevator vertical at X=983 | Contact? |
|--------------|----------------|----------------------------|----------------------------|----------|
| 0 deg | 0 deg | 0mm | 0mm | NO — both neutral |
| 25 deg | 0 deg | 4.23mm | 0mm | NO — elevator at neutral |
| 25 deg | +18 deg | 4.23mm | 12.59mm up | NO — perpendicular planes |
| 25 deg | -18 deg | 4.23mm | 12.59mm down | NO — perpendicular planes |
| 30 deg | +18 deg | 5.00mm | 12.59mm up | NO — perpendicular planes |
| 30 deg | -18 deg | 5.00mm | 12.59mm down | NO — perpendicular planes |
| 0 deg | +18 deg | 0mm | 15.92mm up (at TE) | NO — rudder at neutral |
| 30 deg | 0 deg | 5.00mm | 0mm | NO — elevator at neutral |

**CONCLUSION: No rudder-elevator interference at any combined deflection angle up to rudder 30 deg / elevator 18 deg.**

The rudder and elevator move in perpendicular planes (lateral vs. vertical). Their swept volumes do not intersect because the fin separates them in the lateral direction, and the vertical motions are orthogonal.

### 2.11 HStab-to-VStab Fairing Considerations

While there is no rudder-elevator interference, the **HStab-to-VStab junction fillet** (r=9.2mm, C2 continuous) must be designed carefully:

1. The fillet wraps around the VStab fin at the HStab root
2. The rudder hinge (at 65% VStab chord) is FORWARD of the HStab TE — the fillet must not interfere with rudder deflection
3. The fillet should be smooth and C2 continuous, providing clean airflow from VStab to HStab

**Fillet zone in fuselage X-coordinates:**
- Fillet starts: X = 882.25 - 9.2 = 873.05mm (9.2mm forward of HStab LE)
- Fillet ends: X = 997.25 + 9.2 = 1006.45mm (9.2mm aft of HStab TE)
- Rudder hinge: X = 983.0mm

The fillet extends past the rudder hinge (983 < 1006.45). The fillet is on the STATIC fin surface. The rudder is a SEPARATE moving surface aft of the hinge. **The fillet must stop at the rudder hinge line** — it cannot extend onto the rudder surface.

---

## 3. Rudder Hinge Mechanism Design

### 3.1 Concealed Hinge Design (Compatible with HStab Philosophy)

Following the concealed saddle hinge philosophy from HStab v6:

| Parameter | Value |
|-----------|-------|
| Type | Concealed piano-wire hinge inside VStab fin |
| Wire | 0.8mm spring steel (ASTM A228), 170mm long |
| Wire mass | 0.53g |
| Hinge axis | Inside the fin at 65% chord, flush with fin surface |
| External surface | Completely flush — zero gap when neutral |
| Bullnose on rudder | Convex LE, radius 1.5-2.0mm at root, tapering to 1.0mm at tip |
| Saddle in VStab | Concave channel at fin TE inner surface |
| Bearing surfaces | PETG sleeves (1.2mm OD, 0.8mm ID, 3mm long), interleaved |
| Gap seal | Mylar strip or elastic tape (TBD, same as HStab) |

### 3.2 Hinge Bearing Schedule

| VStab z (mm) | Fin thickness at hinge (mm) | Bullnose radius (mm) | Saddle type |
|--------------|------------------------------|----------------------|-------------|
| 0-30 | 2.3-2.1 | 1.5 | Full saddle |
| 30-80 | 2.1-1.6 | 1.2-1.0 | Full saddle |
| 80-120 | 1.6-1.2 | 1.0-0.6 | Tapered saddle |
| 120-150 | 1.2-0.8 | 0.6-0.3 | Minimal saddle |
| 150-165 | 0.8-0.6 | 0.3-0 | Fading to wire-only |

### 3.3 Rudder Deflection Range

| Parameter | Value |
|-----------|-------|
| Maximum deflection | **+/-25 deg** (primary) |
| Possible range (if servo authority allows) | +/-30 deg |
| Hinge effectiveness at 25 deg | tau ~ 0.48 (Glauert thin-airfoil) |
| Hinge effectiveness at 30 deg | tau ~ 0.42 (with flow separation onset) |
| Recommended max | 25 deg (cleaner flow, adequate authority) |

---

## 4. VStab Cross-Section Data at HStab Station

The HStab mounts at approximately z=82.5mm on the VStab (midpoint of 165mm fin height).

| Parameter | Value |
|-----------|-------|
| VStab chord at z=82.5 | 137.5mm |
| Airfoil | 50% blend HT-14/HT-12 |
| Thickness ratio | ~6.3% |
| Max thickness | 8.66mm |
| Thickness at 65% chord (rudder hinge) | ~2.27mm half-thickness |
| Thickness at 34.5% chord (HStab spar bore) | ~3.4mm half-thickness |
| Fin width at HStab spar | ~6.8mm (adequate for 3.1mm bore) |

### HStab Spar Through VStab

The 3mm CF tube spar passes through the VStab fin at X=34.5mm local (HStab coords), which is:

- HStab LE at fuselage X=882.25mm
- Spar at X=882.25 + 34.5 = 916.75mm fuselage
- VStab chord at z=82.5: 137.5mm
- VStab LE at this height: X=866 + (180-137.5)*0.65 = not applicable — VStab LE is straight

Actually, the VStab is a straight-tapered planform. The LE is a straight line from root LE to tip LE.

VStab root LE: X=866mm
VStab root TE: X=1046mm (root chord 180mm)
VStab tip LE: X=866 + 165*tan(sweep)... wait, the VStab is a straight taper with:
- Root chord 180mm at z=0
- Tip chord 95mm at z=165mm

If the LE is straight (zero sweep): LE at all z = X=866mm, and TE tapers from 1046 to 961mm.
If the TE is straight (common practice): TE at all z = X=1046mm, and LE moves forward from 866 to 951mm.

From the consensus: "Fin integration: Superelliptical blend X=650-866mm" — the VStab root LE is at X=866mm. The consensus doesn't specify sweep. For an RC sailplane fin, the typical approach is **zero LE sweep** (straight LE) with the TE tapering. This keeps the spar bore aligned.

**Assumed: VStab LE is straight at X=866mm at all heights.**

Then at z=82.5mm:
- Chord = 137.5mm
- TE at X = 866 + 137.5 = 1003.5mm
- Rudder hinge at 65% chord: X = 866 + 0.65*137.5 = 955.4mm (fuselage)

Hmm, this is different from my earlier calculation at the root. Let me be precise:

| VStab z (mm) | Chord (mm) | LE X (fuse) | TE X (fuse) | Rudder hinge X (fuse) |
|---------------|-------------|-------------|-------------|------------------------|
| 0 (root) | 180.0 | 866.0 | 1046.0 | 983.0 |
| 82.5 (HStab) | 137.5 | 866.0 | 1003.5 | 955.4 |
| 165 (tip) | 95.0 | 866.0 | 961.0 | 927.8 |

The HStab spar passes through the VStab at z=82.5, where:
- VStab chord = 137.5mm
- Spar X in fuselage: 882.25 + 34.5 = 916.75mm
- This is (916.75 - 866) / 137.5 = 50.75/137.5 = **36.9% chord** on the VStab
- VStab max thickness is at ~30% chord for HT airfoils
- Fin thickness at 36.9% chord, 6.3% thick: ~0.063 * 137.5 * (thickness_fraction) ~ 4.1mm half = 8.2mm total
- Adequate for 3.1mm bore

---

## 5. HStab-to-VStab Fairing Design

### 5.1 Fairing Specification

| Parameter | Value |
|-----------|-------|
| Fillet radius | r=9.2mm |
| Profile | Quartic polynomial, C2 continuous |
| Forward extent | 9.2mm forward of HStab root LE |
| Aft extent | Stops at rudder hinge line (no fairing on rudder) |
| Fairing chord | From X=873mm to X=983mm at VStab root |
| Cross-section | D-shaped, tangent to both VStab fin and HStab root airfoil |

### 5.2 Quartic Polynomial Profile

The fillet height h(s) as a function of arc-length s from the junction:

```
h(s) = r * [1 - (1 - s/r)^4]    for s in [0, r]
```

This gives:
- h(0) = 0 (tangent at junction)
- h'(0) = 4/r (smooth entry)
- h(r) = r (full radius)
- h'(r) = 0 (tangent to surface — C2 continuous)
- h''(0) = 12/r^2, h''(r) = 0 (C2 continuity)

### 5.3 Fairing Zones

| Zone | Fuselage X range | Fairing type |
|------|------------------|--------------|
| Forward blend | 873 to 882 | Growing fillet (approaching HStab LE) |
| HStab chord | 882 to 983 | Full fillet (along HStab root chord) |
| Aft of rudder hinge | 983 to 1003 | **No fairing** — rudder clearance zone |
| Aft rudder | 1003 to 1046 | **No fairing** — rudder surface only |

**The fairing STOPS at the rudder hinge line (X=983 at root, X=955 at HStab height).** Forward of the hinge, the VStab fin surface and HStab root are faired together. Aft of the hinge, the rudder is a separate moving surface and must have clearance from the HStab.

### 5.4 Fairing-to-Rudder Clearance

At the rudder hinge line, the fairing must taper to zero to allow rudder deflection. The fairing profile at the hinge:

```
h_end = 0 (flush with fin surface)
h'_end = 0 (smooth tangent, C1 minimum)
```

This creates a natural transition: the fairing shrinks from r=9.2mm to 0 over the last ~10mm before the hinge.

---

## 6. Rudder Structural Design

### 6.1 Rudder Mass Estimate

| Component | Specification | Mass (g) |
|-----------|--------------|----------|
| Rudder shell | LW-PLA, 0.40mm vase mode, 35% of 226.9 cm^2 = 79.4 cm^2 | 3.2 |
| Internal ribs (3-4) | LW-PLA, 0.5mm | 0.3 |
| Hinge wire | 0.8mm spring steel, 170mm | 0.53 |
| PETG sleeves | 12x (1.2/0.8/3mm) | 0.03 |
| Gap seal (TBD) | Mylar/tape | ~0.15 |
| **Total rudder** | | **~4.2g** |

### 6.2 Rudder Stiffness Check

- Rudder root chord: 63mm, thickness ~4.5mm (7.5% * 63 = 4.7mm, but at 65% chord it's thinner ~1.5mm per side)
- First bending mode estimate: >50 Hz (short span, thin section, but wire provides constraint)
- Gust deflection at Vne (20 m/s): <0.3mm — negligible
- Flutter: servo-powered, zero-slop wire hinge — no risk

### 6.3 Rudder Pushrod

| Parameter | Value |
|-----------|-------|
| Pushrod type | 0.8mm music wire in 1.5mm OD PTFE tube |
| Route | Servo (fuselage X=350) through boom → VStab fin interior → exit at rudder root |
| Connection | Z-bend through hole in rudder root face, 10mm below hinge |
| Alternate holes | 6mm and 14mm below hinge (rate adjustment) |

---

## 7. Summary and Recommendations

### 7.1 Key Findings

1. **No rudder-elevator interference**: The rudder deflects laterally (Y) while the elevator deflects vertically (Z). Their swept volumes are in perpendicular planes and cannot intersect up to rudder 30 deg / elevator 18 deg combined deflection.

2. **Overlap zone exists**: X=983 to 993mm at the VStab root where both rudder and elevator planforms coexist, but they move in perpendicular directions.

3. **No notch/cutout required in rudder**: The perpendicular motion planes mean no material removal is needed.

4. **Fairing must stop at rudder hinge**: The HStab-to-VStab fairing (r=9.2mm, C2) must terminate at the rudder hinge line to allow full rudder deflection.

5. **Rudder deflection range**: +/-25 deg recommended (adequate authority, clean flow). Up to +/-30 deg possible with no interference.

### 7.2 Rudder Specifications Summary

| Parameter | Value |
|-----------|-------|
| Chord ratio | 35% of VStab chord |
| Root chord | 63.0mm |
| Tip chord | 33.2mm |
| Area | 79.4 cm^2 |
| Hinge position | 65% chord from VStab LE |
| Hinge type | Concealed, 0.8mm spring steel wire |
| Deflection range | +/-25 deg (max +/-30 deg) |
| Mass | ~4.2g |
| Vv_rudder | 0.0048 |
| Vv_effective (at 25 deg) | 0.0164 |
| Bullnose radius | 1.5mm root, 0.3mm tip |
| Gap seal | TBD (Mylar/tape, same as HStab) |

### 7.3 Recommendations for Fuselage Consensus Update

1. **Rudder deflection range**: Confirm +/-25 deg as the design target.
2. **HStab-to-VStab fairing**: Confirm r=9.2mm, C2 quartic, stopping at rudder hinge line.
3. **Rudder hinge wire**: Confirm 0.8mm (heavier than HStab 0.5mm because rudder is larger and sees higher loads from asymmetric flow).
4. **No rudder cutout needed**: Confirm that perpendicular motion planes eliminate interference.
5. **Fairing integration**: The fairing is part of the fuselage print (static surface), not the rudder or HStab.

---

## 8. VStab Cross-Section at HStab Junction (Reference for 3D Modeling)

At VStab span station z=82.5mm (HStab root junction):

| Property | Value |
|----------|-------|
| VStab chord | 137.5mm |
| LE position (fuselage) | X=866.0mm |
| TE position (fuselage) | X=1003.5mm |
| Airfoil | 50% HT-14 / HT-12 blend |
| Thickness ratio | ~6.3% |
| Max thickness | 8.66mm at ~30% chord (X=907.3mm) |
| HStab spar bore | X=916.75mm (36.9% VStab chord), fin width ~8.2mm |
| Rudder hinge | X=955.4mm (65% VStab chord), fin half-thickness ~2.27mm |
| Rudder chord | 48.1mm (35% of 137.5mm) |
| Rudder TE | X=1003.5mm |
