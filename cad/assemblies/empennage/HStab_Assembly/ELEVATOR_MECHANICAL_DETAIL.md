# Elevator Mechanical Integration Detail Specification

**Date:** 2026-03-29
**Author:** Mechanical Integration Engineer
**Status:** SPECIFICATION -- ready for drawing-first workflow
**Depends on:** DESIGN_CONSENSUS.md v3, Fuselage DESIGN_CONSENSUS.md v1

---

## Reference Data (from existing consensuses)

| Parameter | Value | Source |
|-----------|-------|--------|
| HStab root chord | 115mm | HStab consensus v3 |
| Elevator chord ratio | 35% of local chord | HStab consensus v3 |
| Elevator root chord | 40.2mm (35% of 115) | HStab consensus v3 |
| Hinge line position | 65% chord from LE = 74.75mm | HStab consensus v3 |
| TE truncation | 97% chord (= 111.55mm from LE) | HStab consensus v3 |
| Elevator deflection | -20 deg (nose down) / +25 deg (nose up) | HStab consensus v3 |
| Hinge wire | 0.5mm music wire, continuous 440mm | HStab consensus v3 |
| Knuckle OD/ID | 1.2mm / 0.6mm | HStab consensus v3 |
| Gap at hinge | 0.3mm | HStab consensus v3 |
| VStab root chord | 180mm (LE at X=866, TE at X=1046) | Fuselage consensus v1 |
| VStab tip chord | 95mm | Fuselage consensus v1 |
| VStab height | 165mm | Fuselage consensus v1 |
| VStab fin thickness at HStab station (X=911) | 7mm | Fuselage cross-section schedule |
| VStab rudder chord ratio | 35% | Fuselage consensus v1 |
| VStab rudder hinge | 65% chord from LE | Fuselage consensus v1 |
| Rudder deflection | +/-25 deg | Specifications.md |
| HStab attaches at VStab root (bottom) | Dovetail interlock + CA | Both consensuses |

---

## 1. Elevator Bevel / Cut Angle at Hinge Line

### 1.1 Problem Statement

The elevator rotates about the hinge wire axis (at 65% chord). The elevator LE face and stab TE face are in close proximity (0.3mm gap from the knuckle interleaving). When the elevator deflects:

- **Nose up (+25 deg):** Elevator TE rises, elevator LE dips below the hinge line. The BOTTOM of the elevator LE face swings FORWARD and DOWN, potentially colliding with the BOTTOM of the stab TE face.
- **Nose down (-20 deg):** Elevator TE drops, elevator LE rises above the hinge line. The TOP of the elevator LE face swings FORWARD and UP, potentially colliding with the TOP of the stab TE face.

### 1.2 Geometry Analysis

At the root section (worst case, thickest airfoil):

- HT-13 airfoil, 6.5% t/c, chord 115mm
- Airfoil thickness at 65% chord: approximately 3.8% of chord = 4.37mm
- Upper surface ordinate at 65% chord: approximately +2.1mm from chord line
- Lower surface ordinate at 65% chord: approximately -2.27mm from chord line
- Total local thickness at hinge: ~4.37mm

The stab shell TE face and elevator LE face are vertical cuts at the 65% chord station. The music wire hinge axis is at the midpoint of this thickness, approximately on the chord line.

**Critical clearance calculation:**

When the elevator deflects by angle theta, the corner of the elevator LE face (at distance r from the hinge axis) sweeps through an arc. The maximum corner distance from the hinge axis is half the local airfoil thickness at the hinge line:

```
r_upper = +2.1mm (distance from hinge axis to upper surface at hinge)
r_lower = -2.27mm (distance from hinge axis to lower surface at hinge)
```

**At +25 deg (nose up):**

The lower-surface corner of the elevator LE face swings forward. Its forward excursion into the stab TE face zone:

```
Forward excursion (lower corner) = r_lower * sin(25 deg) = 2.27 * 0.4226 = 0.96mm
Downward drop = r_lower * (1 - cos(25 deg)) = 2.27 * 0.0937 = 0.21mm
```

The upper-surface corner moves backward:
```
Backward excursion (upper corner) = r_upper * sin(25 deg) = 2.1 * 0.4226 = 0.89mm
```

**At -20 deg (nose down):**

The upper-surface corner of the elevator LE face swings forward:

```
Forward excursion (upper corner) = r_upper * sin(20 deg) = 2.1 * 0.3420 = 0.72mm
Upward rise = r_upper * (1 - cos(20 deg)) = 2.1 * 0.0603 = 0.13mm
```

### 1.3 Required Bevel Angles

To prevent collision, both the stab TE face and elevator LE face must be beveled. The bevel removes material from the faces so the rotating elevator clears the stationary stab.

**Worst case is +25 deg (nose up)** because the lower corner has a larger moment arm (2.27mm vs 2.1mm) and the deflection is larger.

**Required total bevel angle = max deflection angle + clearance margin.**

For the lower surface (critical at nose-up deflection):
```
Required bevel from horizontal = 25 deg + 2 deg margin = 27 deg
```

For the upper surface (critical at nose-down deflection):
```
Required bevel from horizontal = 20 deg + 2 deg margin = 22 deg
```

**Bevel specification (asymmetric):**

| Surface | Stab TE face bevel | Elevator LE face bevel | Total gap angle |
|---------|-------------------|----------------------|-----------------|
| Upper surface | 11 deg aft-chamfer | 11 deg forward-chamfer | 22 deg |
| Lower surface | 14 deg aft-chamfer | 13 deg forward-chamfer | 27 deg |

The bevel is split roughly equally between the stab and elevator faces. The lower-surface bevel is steeper because the nose-up deflection (+25 deg) is greater than nose-down (-20 deg).

### 1.4 Cross-Section Diagrams

**NOTE:** In these diagrams, the hinge wire axis is marked with `O`. The stab is to the LEFT, elevator to the RIGHT. Upper surface is UP. The gap between stab TE and elevator LE is exaggerated for clarity.

```
NEUTRAL (0 deg):
                    upper surface
    ________________/    0.3mm gap    \__________________
   |    STAB       / ___________gap___ \    ELEVATOR     |
   |              / /                 \ \                 |
   |    stab TE  | |        O <--wire  | |  elev LE      |
   |    face     | |                   | |  face          |
   |    (beveled)\ \                   / /  (beveled)     |
   |              \ \___________gap___/ /                  |
   |_______________\                   /__________________|
                    \  lower surface  /

   The bevel creates a V-shaped gap that opens downward (wider bevel below)
   and a narrower V-shaped gap upward.
```

```
NOSE UP (+25 deg) -- elevator TE rises, LE dips:
                    upper surface
    ________________/                  __________________
   |    STAB       /   gap widens  ----    ELEVATOR      |
   |              /   here       /        (rotated 25    |
   |    stab TE  |              /          deg CW)       |
   |    face     |     O-------/                         |
   |    (beveled) \          /   <-- bevel provides      |
   |               \       /       clearance here        |
   |________________\    /________________________________|
                     \  /  lower surface -- GAP NARROWS
                      \/   but bevel prevents collision

   Lower bevel (27 deg total) > deflection (25 deg): CLEARS with 2 deg margin
```

```
NOSE DOWN (-20 deg) -- elevator TE drops, LE rises:
                      /\   upper surface -- GAP NARROWS
                     /  \  but bevel prevents collision
    ________________/    \_______________________________
   |    STAB       /       \    ELEVATOR                 |
   |              /   O-----\   (rotated 20 deg CCW)     |
   |    stab TE  |           \                            |
   |    face     |            \                           |
   |    (beveled) \   gap      \                          |
   |               \ widens     ----                      |
   |________________\ here        ________________________|
                     \           /  lower surface

   Upper bevel (22 deg total) > deflection (20 deg): CLEARS with 2 deg margin
```

### 1.5 Gap Sufficiency

The 0.3mm gap (set by the knuckle interleaving) is sufficient. At the neutral position, the 0.3mm gap provides:
- Manufacturing tolerance absorption: +/-0.1mm FDM accuracy
- Thermal expansion room: LW-PLA expands ~0.07mm/K, delta-T of 30K = 0.002mm per mm -- negligible
- Friction-free rotation: 0.3mm >> surface roughness of printed faces (~0.05mm)

**However:** The bevels reduce the effective face contact area. At the upper surface, the 22 deg total bevel means the stab TE and elevator LE faces are NOT parallel -- they form a V-opening. This is desirable: it means the gap widens away from the hinge axis, preventing binding.

### 1.6 Bevel Implementation

The bevel is printed into the stab and elevator shells during manufacturing:
- Stab shell: The TE face (at 65% chord) is printed with an 11 deg chamfer on upper surface and 14 deg chamfer on lower surface
- Elevator shell: The LE face is printed with an 11 deg chamfer on upper surface and 13 deg chamfer on lower surface
- The chamfer starts at the hinge axis (wire center) and opens toward the respective surface

**In the CAD model:** The hinge line cut is not a vertical plane but two angled planes meeting at the wire axis. This is straightforward in Build123d using chamfer or angled section cuts.

---

## 2. Rudder-Elevator Clearance at Root

### 2.1 VStab Geometry at HStab Station

The HStab root attaches at the bottom of the VStab fin. The VStab root chord is 180mm (LE at X=866, TE at X=1046). At this bottom station:

| Parameter | Value |
|-----------|-------|
| VStab chord at root | 180mm |
| VStab root LE (X coordinate) | 866mm |
| VStab root TE (X coordinate) | 1046mm |
| Rudder hinge position | 65% chord = 117mm from LE = X=983mm |
| Rudder root chord | 35% of 180 = 63mm |
| VStab root thickness | HT-14 at 180mm chord: 7.5% = 13.5mm max (at ~28% chord) |
| VStab thickness at 65% chord (rudder hinge) | ~5.0% of 180mm = ~9.0mm |
| VStab thickness at HStab station (X=911) | ~7mm (from cross-section schedule, blended) |

### 2.2 Rudder TE Swing Arc

The rudder pivots about the hinge line at 65% VStab chord (X=983mm). The rudder TE at root is at X=1046mm, so the rudder chord below the hinge is 1046 - 983 = 63mm.

When the rudder deflects +/-25 deg, the rudder TE sweeps laterally:

```
Lateral excursion of rudder TE = rudder_chord * sin(25 deg) = 63 * 0.4226 = 26.6mm
```

The rudder TE moves 26.6mm to the LEFT or RIGHT of the VStab centerline at full deflection.

**But this is at the rudder TE (X=1046), not at the HStab station (X=911).** The HStab root sits at the VStab root, at X=911. At X=911, the rudder has not yet started -- the rudder hinge is at X=983, which is 72mm AFT of the HStab station.

### 2.3 Critical Interference Zone

The elevator hinge line is at 65% of the HStab chord = 74.75mm aft of the HStab LE. The HStab LE at root is approximately at X=911 - (some offset based on HStab incidence setting and mounting). For this analysis, we define the HStab position as centered at X=911 with the 25% chord point at X=911 (the aerodynamic center):

```
HStab LE at root: X = 911 - 0.25*115 = 882.25mm
HStab TE at root (97% chord): X = 882.25 + 0.97*115 = 882.25 + 111.55 = 993.8mm
Elevator hinge at root: X = 882.25 + 0.65*115 = 882.25 + 74.75 = 957mm
Elevator TE at root: X = 993.8mm
```

Now compare with the rudder:
```
Rudder hinge: X = 983mm
Rudder TE: X = 1046mm
```

The elevator extends from X=957 to X=994. The rudder starts at X=983. **There IS overlap: the aft 11mm of the elevator (from X=983 to X=994) coexists with the forward 11mm of the rudder (from X=983 to X=994) in the X-direction.**

However, the elevator is a HORIZONTAL surface and the rudder is a VERTICAL surface. They exist in perpendicular planes. The question is whether the rudder, when deflected, swings into the space occupied by the elevator root.

### 2.4 Rudder Lateral Excursion at the Elevator Zone

At X=994mm (the elevator TE), the rudder has a chordwise distance from its hinge of:
```
rudder_local = 994 - 983 = 11mm from hinge
```

Lateral excursion at this point:
```
lateral = 11 * sin(25 deg) = 11 * 0.4226 = 4.6mm to each side
```

The elevator root is at the VStab centerline. The VStab fin at the HStab station is 7mm thick (3.5mm each side of centerline). The elevator root edge must sit outside the rudder sweep zone.

**Required clearance at elevator root:**

The elevator root needs to clear:
1. The VStab fin half-thickness: 3.5mm (static clearance for the fixed fin)
2. The rudder sweep at the overlap zone: 4.6mm (dynamic clearance for rudder at +/-25 deg)
3. Assembly tolerance: 0.5mm

**Minimum gap from VStab centerline to elevator root edge: 4.6 + 0.5 = 5.1mm each side.**

Since the VStab fin is 7mm wide (3.5mm each side), and the rudder at maximum sweep at X=994 extends 4.6mm each side from the VStab centerline, the elevator root must be at least 5.1mm from the VStab centerline.

**This means each elevator half root face is offset 5.1mm from the VStab centerline, leaving a 10.2mm total gap between the two elevator halves.** The VStab fin (7mm) sits in this gap with 1.6mm clearance on each side at the aft end, growing as we move forward along the elevator (because the rudder sweep decreases toward the hinge).

### 2.5 Gap Between Elevator Halves

| Parameter | Value |
|-----------|-------|
| Total gap between elevator halves (at TE) | 10.2mm |
| VStab fin width | 7.0mm |
| Rudder max sweep at elevator TE station | +/-4.6mm from centerline |
| Clearance (each side, at TE) | 0.5mm |
| Gap between elevator halves (at hinge line) | 8.0mm (fin 7mm + 0.5mm each side) |

Note: At the elevator hinge line (X=957), the rudder has not yet started (rudder hinge is at X=983). At the hinge line, the only constraint is clearing the VStab fin itself, so the gap is 7mm + 1mm tolerance = 8mm.

The elevator root gap varies from 8mm (at hinge line) to 10.2mm (at TE), tapering linearly as the rudder sweep increases toward the aft end.

### 2.6 Hinge Wire Routing Through VStab

The continuous 0.5mm music wire must pass from the left elevator half to the right elevator half, crossing the VStab fin. Three options were evaluated:

**Option A: Wire passes through the VStab fin** (SELECTED)
- A 0.6mm hole is drilled/printed through the VStab fin at the hinge axis height
- The hole is at X=957mm (the elevator hinge line), at the chord line elevation
- The fin is 7mm wide at this point; the hole passes through 7mm of PETG/LW-PLA
- The wire simply threads through: left elevator knuckles -> fin hole -> right elevator knuckles
- The hole is lined with a printed PETG sleeve (1.2mm OD / 0.6mm ID) bonded into the fin for smooth rotation and wear resistance
- **Advantage:** Simplest, strongest, most reliable. The wire is fully supported across the gap.
- **Disadvantage:** Requires a hole through the VStab fin, slightly weakens it at one point. However, a 0.6mm hole in a 7mm wide fin removes only 0.54% of the cross-sectional area -- negligible.

**Option B: Wire passes through the rudder**
- REJECTED: The rudder moves +/-25 deg. If the wire passes through the rudder, it would constrain the rudder or the wire would need a flexible section. Mechanically incompatible.

**Option C: Wire passes through a gap above/below the rudder**
- The rudder hinge is at 65% of VStab chord (X=983). The elevator hinge is at X=957. These are different X positions, so the elevator hinge wire does NOT intersect the rudder hinge line.
- The wire passes through the fin at X=957, which is FORWARD of the rudder hinge (X=983). At this X position, the VStab is solid fin structure (not rudder). So Option A naturally avoids the rudder.

**CONCLUSION: Option A is correct. The elevator hinge wire passes through a hole in the solid portion of the VStab fin, well forward of the rudder hinge. No interaction with the rudder.**

### 2.7 Cross-Section at VStab (Plan View, Looking Down)

```
        FORWARD (LE) ←────────────────────────────→ AFT (TE)

X=882   X=911   X=957        X=983        X=994   X=1046
  |       |       |             |            |        |
  |  HStab LE  HStab 25%  Elev hinge    Rudder     Elev TE   VStab TE
  |       |    chord       line          hinge      (97%)
  |       |       |             |            |        |
  |       |       |<-- STAB -->|<--ELEVATOR->|        |

                  |<--- 7mm VStab fin --->|
                  |  (solid fin here)     |
                  |                       |<-rudder starts
                  |                       |
                                          |<-- 4.6mm lateral
                                               sweep each side

LEFT    ====[LEFT ELEVATOR]=====         =======[LEFT STAB]========
SIDE          |  5.1mm gap  |
              |  ___________| VStab fin (3.5mm)
CENTER  ------|-/           \-|----------------------------------------
              |  ___________| VStab fin (3.5mm)
RIGHT         |  5.1mm gap  |
SIDE    ====[RIGHT ELEVATOR]====         =======[RIGHT STAB]=======
```

---

## 3. Control Horn Specification

### 3.1 Research Summary

Commercial RC sailplane elevator horns (Dubro Micro, Sullivan, etc.) are typically:
- Nylon molded, 15-25mm height
- 1.0-1.5g each
- Designed for balsa structures with screw or CA mounting
- Available but overbuilt for a 3D-printed empennage

For a lightweight 3D-printed sailplane where every gram counts, a **custom 3D-printed control horn** is optimal. This is consistent with 3DLabPrint, Planeprint, and Eclipson designs, which all use printed horns integrated into the control surface.

### 3.2 Horn Design

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Type | Custom 3D printed | Matches mass target, integrates with printed elevator |
| Material | CF-PLA solid (1.2mm walls, 100% infill) | Stiff, strong, prints on hardened nozzle |
| Total mass (horn + mount tab) | 0.80g | Per DESIGN_CONSENSUS budget |
| Horn height (below elevator surface) | 15mm | Provides adequate lever arm for pushrod |
| Horn width | 8mm | Sufficient for pushrod hole and mass balance pocket |
| Horn thickness | 1.2mm (walls) with internal web | Solid CF-PLA |
| Forward extension (mass balance arm) | 12mm forward of hinge axis | For 1.0g tungsten putty pocket |
| Pushrod attachment hole | 1.6mm diameter | For M1.5 ball link or 1.5mm Z-bend |
| Pushrod hole position | 13mm below elevator lower surface | Lever arm for servo geometry |
| Number of pushrod holes | 3 (at 11mm, 13mm, 15mm below surface) | Adjustment range for throw |
| Horn profile | Tapered: 8mm wide at base, 5mm at tip | Streamlined, reduces drag |
| Horn location | LEFT elevator half, 15mm from root | Close to VStab for short pushrod exit |

### 3.3 Mounting to Elevator

The horn mounts to the elevator via a **printed pocket with through-bolt:**

1. The elevator shell has a 9mm x 3mm rectangular slot cut in the lower surface, 15mm from the root edge
2. The horn has a flat mounting tab (9mm x 6mm x 1.2mm) that sits on the INSIDE of the elevator lower skin
3. The horn blade passes through the slot and extends 15mm below
4. A 1mm CF pin (or M1.2 nylon bolt) passes horizontally through the elevator skin + horn tab, locking the horn in place
5. Medium CA is applied around the mounting tab for permanent bond

**Why the horn protrudes BELOW the elevator:** The pushrod comes from below (from the fuselage/VStab interior), so the horn must extend downward. The stab shell sits below the elevator at the hinge line, but the horn is positioned 15mm inboard from the elevator root, in the gap between the elevator root and the VStab fin. The horn blade passes through the gap, not through the stab shell.

### 3.4 Horn Clearance with Stab

```
SIDE VIEW (looking from left, at 15mm inboard from elevator root):

        STAB upper surface
       ________________________
      /                        \
     /     STAB SHELL           \
    |   (ends at hinge line)     |
    |         |    |             |
    \         |    |   ELEVATOR  /
     \_______/|    |____________/
              |    |
    0.3mm gap |    |  elevator lower surface
              |    |
              | horn blade (1.2mm thick)
              |    |
              |    | 15mm
              |    |
              |    O  <-- pushrod attachment hole (13mm below surface)
              |    |
              |    |
              |___/  tapered tip (5mm wide)

The horn blade is in the ROOT GAP ZONE -- between the elevator root and VStab fin.
The stab shell does NOT exist at this location (the stab also has a root gap).
Therefore NO CUTOUT in the stab is needed.
```

### 3.5 Mass Balance Pocket

| Parameter | Value |
|-----------|-------|
| Pocket location | Forward extension of horn, 12mm forward of hinge axis |
| Pocket dimensions | 6mm x 4mm x 3mm cavity |
| Pocket volume | 72 mm^3 |
| Tungsten putty mass | 1.0g (density ~11 g/cm^3, volume needed: ~91 mm^3) |
| Actual implementation | Putty packed into pocket + wrapped around forward arm |
| Pocket sealed with | Thin CA-tacked LW-PLA cap (0.1g) |

The mass balance arm extends FORWARD of the hinge axis and UP (along the lower surface of the elevator), counterbalancing the elevator mass aft of the hinge. This placement, forward of the hinge, is aerodynamically inside the stab-elevator gap zone and does not protrude into the airstream.

### 3.6 Pushrod Connection at Horn

| Parameter | Value |
|-----------|-------|
| Connection type | M1.5 ball link (snap-on) |
| Ball link mass | ~0.3g (included in "CA glue + clevis" budget) |
| Ball stud | M1.5 threaded into horn (printed M1.5 pocket, CA-locked) |
| Ball link socket | Snaps onto stud, retained by spring clip |
| Alternative | 1.5mm Z-bend clevis through 1.6mm hole (simpler, lighter) |

**Recommended: Z-bend clevis.** The Z-bend is lighter (no ball link mass), simpler (just bend the pushrod wire), and proven in thousands of RC models. The 1.6mm hole in the horn accepts the 1.5mm wire with 0.1mm clearance for free rotation.

---

## 4. Elevator Joiner / Synchronizer

### 4.1 Problem Statement

The two elevator halves are separated by the VStab fin (8-10.2mm gap). Both halves MUST deflect together as one surface. Three synchronization mechanisms exist:

1. The continuous hinge wire (already specified)
2. A separate joiner element
3. Printing both halves as one piece with a bridge

### 4.2 Hinge Wire Torsional Stiffness Analysis

The 0.5mm music wire passes through both elevator halves and through the VStab fin hole. Can it alone synchronize the two halves?

**Torsional stiffness of 0.5mm wire over the 8mm gap:**

```
GJ/L = G * (pi * d^4 / 32) / L
G (spring steel) = 79,300 MPa
d = 0.5mm
L = 8mm (gap through VStab fin)

GJ/L = 79,300 * (pi * 0.5^4 / 32) / 8
     = 79,300 * 0.006136 / 8
     = 60.8 N-mm/rad
     = 1.06 N-mm/deg
```

At the maximum hinge moment (~0.02 N-m = 20 N-mm at Vne), the angular twist over the 8mm gap would be:

```
theta = M / (GJ/L) = 20 / 60.8 = 0.33 rad = 18.8 deg
```

**This is UNACCEPTABLE.** An 18.8 degree twist means the two elevator halves could be nearly 19 degrees apart. The wire alone is far too compliant to synchronize the halves.

### 4.3 Solution: Printed Bridge Joiner (SELECTED)

**Both elevator halves are printed as separate pieces (for bed fit and to allow threading the hinge wire). A rigid bridge joiner connects them across the VStab gap.**

| Parameter | Value |
|-----------|-------|
| Type | 3D printed rigid bridge |
| Material | CF-PLA solid |
| Shape | U-shaped channel that straddles the VStab fin |
| Length (spanwise) | 25mm (12.5mm into each elevator half) |
| Height | 5mm (fits inside elevator profile, below hinge axis) |
| Width | 12mm (straddles 7mm fin + 2.5mm clearance each side) |
| Wall thickness | 1.2mm |
| Mass | ~0.6g |
| Attachment | CA-bonded into printed pockets inside each elevator half |

### 4.4 Bridge Joiner Geometry

```
FRONT VIEW (looking aft along the HStab):

         Left Elevator                  Right Elevator
    ________________________       ________________________
   |                        |     |                        |
   |   ____________________/|     |\____________________   |
   |  |  Bridge pocket     ||     ||     Bridge pocket  |  |
   |  |  (printed recess)  ||     ||  (printed recess)  |  |
   |  |                    ||     ||                     |  |
   |  |  ╔════════════════╗|     |╔════════════════╗    |  |
   |  |  ║  BRIDGE JOINER ║|     |║  BRIDGE JOINER ║    |  |
   |  |  ║  (CF-PLA)      ║| FIN |║  (CF-PLA)      ║    |  |
   |  |  ║   ┌────────────╫┤─┬─┬─├╫────────────┐   ║    |  |
   |  |  ║   │            ║│ │F│ │║            │   ║    |  |
   |  |  ║   │  12.5mm    ║│ │I│ │║  12.5mm   │   ║    |  |
   |  |  ║   │  bond zone ║│ │N│ │║  bond zone │   ║    |  |
   |  |  ║   └────────────╫┤─┴─┴─├╫────────────┘   ║    |  |
   |  |  ╚════════════════╝|     |╚════════════════╝    |  |
   |  |____________________||     ||_____________________|  |
   |________________________|     |________________________|

             12.5mm  2.5 7mm 2.5  12.5mm
             bond    clr fin  clr  bond

   The U-channel straddles the fin, does not touch it.
   Rudder clearance: The joiner is FORWARD of the rudder hinge (X=983),
   at the elevator hinge line (X=957). No interaction with rudder.
```

### 4.5 Torsional Stiffness of Bridge Joiner

The CF-PLA bridge (E = 6 GPa, 1.2mm walls, 5mm x 12mm cross-section, 12mm unsupported span across the fin gap):

```
I_bridge ~ (12 * 5^3 - 9.6 * 2.6^3) / 12 = (1500 - 168.7) / 12 = 110.9 mm^4
GJ ~ E * I / (1+nu) for a channel section: approximately 3000 N-mm^2

Stiffness: GJ/L = 3000 / 12 = 250 N-mm/rad = 4.36 N-mm/deg
```

At max hinge moment (20 N-mm):
```
theta = 20 / 250 = 0.08 rad = 4.6 deg
```

Still significant. **We need the bridge PLUS the wire acting together:**

Combined stiffness: 60.8 + 250 = 310.8 N-mm/rad
```
theta = 20 / 310.8 = 0.064 rad = 3.7 deg
```

This is at Vne under maximum aerodynamic load. At normal cruise, the hinge moment is ~2 N-mm:
```
theta_cruise = 2 / 310.8 = 0.006 rad = 0.37 deg
```

**At cruise, the two halves are synchronized within 0.4 degrees. At Vne/max load, 3.7 degrees of differential is acceptable (both halves are still deflecting in the same direction; this is a small compliance).**

### 4.6 Assembly Sequence for Joiner

1. Print left and right elevator halves, each with a 12.5mm x 5mm x 1.2mm deep pocket on the root end interior (lower surface)
2. Print the bridge joiner separately in CF-PLA
3. Thread hinge wire through left stab knuckles, left elevator knuckles, through VStab fin hole, right elevator knuckles, right stab knuckles
4. Slide bridge joiner into left elevator pocket, apply medium CA
5. Slide right elevator onto the bridge joiner protruding tab, apply medium CA
6. Verify both halves deflect together: apply finger pressure to one side, check the other follows

### 4.7 Why Not Print as One Piece?

Printing both elevator halves as one piece with an integral bridge was considered and REJECTED for these reasons:
1. The combined span (430mm + bridge) exceeds the 256mm print bed
2. Threading the hinge wire requires the elevator halves to be separate pieces that interleave with the stab knuckles
3. The bridge would need to flex around the VStab fin during assembly, which conflicts with rigidity requirements
4. Separate printing allows each half to be vase-mode printed flat, which is optimal for thin LW-PLA shells

---

## 5. Pushrod Routing

### 5.1 System Overview

The elevator servo is at X=350mm in the fuselage servo bay. The control horn is on the left elevator half, 15mm inboard from the root, at approximately X=957mm (hinge line). Total straight-line distance: 607mm.

### 5.2 Pushrod Specification

| Parameter | Value |
|-----------|-------|
| Material | 1.0mm spring steel wire (music wire) |
| Outer guide tube | 2.0mm OD / 1.2mm ID PTFE (Teflon) tube |
| System type | Pushrod in tube (Bowden-style, rigid wire) |
| Total wire length | ~650mm (includes bends and connection geometry) |
| Wire mass | pi/4 * 1.0^2 * 650 * 7.85 / 1e6 = 4.0g |
| PTFE tube mass | ~1.5g |
| Total pushrod system mass | ~5.5g (included in "wiring/pushrods" budget) |

**Why 1.0mm wire, not carbon rod:** A 1.0mm music wire pushrod in a PTFE tube is the standard for RC sailplane elevator actuation. It is flexible enough to route through curves but has zero backlash in compression (unlike pull-pull cables). Carbon rod pushrods are stiffer but cannot negotiate the curves required to exit through the VStab fin. 1.0mm wire in a 1.2mm ID tube has approximately 0.1mm radial clearance -- very low friction when lubricated with silicone.

### 5.3 Route Description

```
SIDE VIEW (fuselage profile, looking from left):

X=350     X=430      X=660     X=866    X=911   X=957
  |         |          |         |        |       |
  S --------|----------|---------|--------|---H---+
  e  servo  | boom     | fin     | fin    | stab  |  horn
  r  bay    | section  | blend   |        |       |
  v         |          |         |        |       |
  o         |          |         |        |       |

Route:
1. Servo arm (X=350) -> Z-bend on servo arm output
2. Straight through boom section (X=350 to X=660) in PTFE guide tube
3. Continue through fin base (X=660 to X=866) -- tube bonded to fin interior wall
4. Curve gently upward from boom centerline to HStab hinge height
5. Exit through hole in VStab fin at X=957, at the hinge axis height
6. Connect to control horn Z-bend, 15mm to the LEFT of the VStab centerline
```

### 5.4 Pushrod Exit Point

The pushrod exits the VStab fin through a **1.5mm x 3mm oval slot** at:
- X position: 957mm (at the elevator hinge line, well forward of the rudder hinge at X=983)
- Y position: Centerline, on the LEFT side of the fin
- Z position: At the HStab chord line height (hinge axis level), approximately 5mm below the HStab lower surface

The oval slot allows the pushrod to move fore/aft as the servo sweeps. At +/-25 deg elevator deflection with a 13mm horn arm:
```
Pushrod travel = 13 * sin(25 deg) = 5.5mm forward/aft
Servo arm travel = similar (matched geometry)
```

The 3mm slot height accommodates the 1.0mm wire with vertical clearance for assembly.

### 5.5 Exit Slot Detail

```
DETAIL: Pushrod exit through VStab fin (view looking LEFT at fin surface):

                VStab fin left surface
                ________________________
               |                        |
               |   ┌──────┐             |
               |   │ 3mm  │  <-- oval slot, 1.5mm wide x 3mm tall
               |   │      │             |
               |   └──────┘             |
               |     ^                  |
               |     |                  |
               |   pushrod (1mm wire)   |
               |   exits here           |
               |________________________|

The slot is lined with a PETG grommet (printed separately, CA-bonded into fin)
to prevent the wire from wearing through the LW-PLA fin skin.
```

### 5.6 Internal Routing Details

Inside the boom section (X=430 to X=660):
- The PTFE tube is bonded to the boom interior wall with small CA tacks every 50mm
- The tube runs along the lower-left quadrant of the boom cross-section
- At X=500, the boom is 18x16mm; the tube (2mm OD) easily fits alongside the rudder pull-pull cables (which run along the lower-right quadrant)

Inside the fin section (X=660 to X=957):
- The tube curves gently upward from the boom centerline (at ~0mm Z) to the HStab hinge height (at approximately +3mm Z relative to the VStab root chord line)
- The curve radius is approximately 300mm -- extremely gentle, zero friction issues
- The tube exits through the PETG grommet at the fin surface

### 5.7 Servo Connection

| Parameter | Value |
|-----------|-------|
| Servo type | 9g class (Emax ES9051 or equivalent) |
| Servo arm length | 12-14mm (adjust to match horn geometry) |
| Servo arm connection | Z-bend in pushrod wire through servo arm hole |
| Servo position | X=350mm, centered in fuselage, on bottom tray |
| Servo output shaft | Right side (toward VStab) |
| Pushrod routing | Left side of fuselage/boom interior |

---

## 6. Elevator Tip Closure

### 6.1 Geometry

The superellipse planform c(y) = 115 * [1 - |y/215|^2.3]^(1/2.3) defines the chord at every span station. The elevator is the aft 35% of the local chord (from 65% to 97% chord) PLUS the tip closure.

At the extreme tip (y > ~205mm), the chord becomes very small:

| y (mm) | Chord (mm) | Stab (65%) | Elevator (32%) | Airfoil thickness (mm) |
|--------|------------|------------|----------------|----------------------|
| 205 | 40.6 | 26.4 | 13.0 | 2.3 |
| 208 | 32.0 | 20.8 | 10.2 | 1.8 |
| 210 | 24.8 | 16.1 | 7.9 | 1.4 |
| 212 | 17.0 | 11.1 | 5.4 | 0.96 |
| 213 | 12.2 | 7.9 | 3.9 | 0.69 |
| 214 | 6.6 | 4.3 | 2.1 | 0.37 |
| 215 | 0 | 0 | 0 | 0 |

The stab shell ends at the hinge line (65% chord). Everything aft of that -- including the tip closure -- is part of the elevator.

### 6.2 Tip Closure Design

The elevator tip closes with a **parabolic cap** that smoothly merges the upper and lower surfaces:

```
PLAN VIEW (elevator tip, looking down):

    y=205      y=210       y=215
      |          |           |
      |   ELEV   |  tip cap  | closed
      |   shell  |  zone     |
      |__________|___________|
     /                        \
    |  elevator body           \
    |  (normal thickness)       \  <-- parabolic closure
    |                            |      walls thicken to 0.55mm
    |  hinge line                |      then merge to solid tip
    |  (LE of elevator)         /
    |                          /
    |_________________________/
```

| Parameter | Value |
|-----------|-------|
| Tip closure start | y = 205mm (where chord = 40.6mm, elevator chord = 13mm) |
| Tip closure end | y = 213mm (practical tip, where thickness < 1mm) |
| Closure profile | Parabolic blend of upper and lower surfaces |
| Wall thickness in closure zone | 0.55mm (thicker than main 0.40mm, per structural review tip cap recommendation) |
| Tip cap construction | Integral part of elevator shell -- NOT a separate piece |
| Tip shape | Smooth parabolic, sealed, rounded for handling |

### 6.3 Hinge at the Extreme Tip

At y > 205mm, the elevator becomes very narrow (< 13mm chord, < 2.3mm thick). The hinge must still work here.

**Design decision:** The hinge knuckle strip ENDS at y = 200mm (slightly before the tip closure zone begins). The last knuckle is at y = 200mm. Beyond that, the elevator tip is held by:

1. The continuous music wire, which continues past the last knuckle to y = 213mm where it bends 90 degrees and tucks into the tip fairing
2. The inherent stiffness of the elevator shell connection to the stab shell at the tip cap

At the tip, the elevator and stab merge into a single closed surface. The "hinge" at the extreme tip is really a thin wall flex zone -- the elevator tip cannot deflect independently because it is so narrow that the entire tip flexes as one piece with the main elevator.

**The tip last 10-12mm (y=203 to y=215) is effectively a flexible fairing that follows the elevator deflection through elastic deformation, not through a discrete hinge.** This is exactly how 3DLabPrint and Planeprint handle their control surface tips.

### 6.4 Wire Retention at Tip

| Parameter | Value |
|-----------|-------|
| Last knuckle position | y = 200mm |
| Wire extends beyond last knuckle | To y = 213mm |
| Wire end treatment | 90-degree bend, 3mm leg, tucked into tip fairing pocket |
| Tip fairing pocket | 3mm deep x 1.5mm wide printed slot in the elevator tip interior |
| Wire is NOT glued at tip | The bend mechanically retains it; allows disassembly if needed |

### 6.5 Elevator Stiffener in Tip Region

The 1mm CF elevator stiffener rod (at 80% chord) terminates where the airfoil thickness can no longer accommodate it:

```
At 80% chord, local thickness ~ 2.5% of chord
At y=200mm (chord 45.5mm): thickness at 80% = 0.025 * 45.5 = 1.14mm
Internal space = 1.14 - 2*0.40 = 0.34mm -- CANNOT FIT 1.0mm rod
```

The stiffener terminates at approximately y = 170mm where the chord is 73.7mm and the internal space at 80% chord is:
```
thickness at 80% = 0.025 * 73.7 = 1.84mm
internal = 1.84 - 0.80 = 1.04mm -- just fits 1.0mm rod
```

| Parameter | Value |
|-----------|-------|
| Elevator stiffener termination | y = 170mm per half (340mm total rod length) |
| Beyond y = 170mm | Elevator shell only, no stiffener rod |
| Tip flexibility | INTENTIONAL -- thin tip flexes under load, providing passive load relief |

---

## 7. Updated Mass Budget

The bridge joiner adds a new component:

| Component | Mass (g) | Change from v3 |
|-----------|----------|-----------------|
| Bridge Joiner (CF-PLA) | 0.60 | NEW |
| Elevator stiffener | 0.44 | Was 0.55g (shorter: 340mm not 440mm) |
| Pushrod system (wire + tube) | 5.50 | Counted in fuselage/wiring budget |

Net change to HStab assembly mass: +0.60 - 0.11 = +0.49g

**Revised HStab assembly mass: 33.68 + 0.49 = 34.17g** (within 35g hard limit, 0.83g contingency)

Note: The pushrod system (5.5g) is in the fuselage wiring budget, not the HStab budget.

---

## 8. Updated Component List

| Component | Type | Material | Mass (g) |
|-----------|------|----------|----------|
| HStab_Left | Custom, printed | LW-PLA 0.45mm vase mode | 8.50 |
| HStab_Right | Custom, printed (mirror) | LW-PLA 0.45mm vase mode | 8.50 |
| Elevator_Left | Custom, printed | LW-PLA 0.40mm vase mode | 3.75 |
| Elevator_Right | Custom, printed (mirror) | LW-PLA 0.40mm vase mode | 3.75 |
| HStab_Hinge_Strip_Left | Custom, printed | PETG solid with knuckles | 0.50 |
| HStab_Hinge_Strip_Right | Custom, printed | PETG solid with knuckles | 0.50 |
| Elevator_Hinge_Strip_Left | Custom, printed | PETG solid with knuckles | 0.50 |
| Elevator_Hinge_Strip_Right | Custom, printed | PETG solid with knuckles | 0.50 |
| Control_Horn | Custom, printed | CF-PLA solid, with mass balance arm | 0.80 |
| Elevator_Bridge_Joiner | Custom, printed | CF-PLA solid U-channel | 0.60 |
| HStab_Main_Spar | Off-shelf | 3mm CF tube 3/2mm, 390mm | 2.40 |
| HStab_Rear_Spar | Off-shelf | 1.5mm CF rod, 440mm | 1.20 |
| Elevator_Stiffener | Off-shelf | 1mm CF rod, 340mm | 0.44 |
| Hinge_Wire | Off-shelf | 0.5mm music wire, 440mm | 0.68 |
| Mass_Balance | Off-shelf | Tungsten putty | 1.00 |
| **TOTAL** | | | **33.62g** |
| CA glue + Z-bend clevis | | | 0.55 |
| **GRAND TOTAL** | | | **34.17g** |

---

## 9. Revised Assembly Sequence

1. Print all parts: 4 LW-PLA shells, 4 PETG hinge strips, 1 control horn, 1 bridge joiner
2. Bond hinge strips to stab TE faces and elevator LE faces (CA, lower surface)
3. Interleave knuckles: mate left stab + left elevator, right stab + right elevator
4. Thread 0.5mm music wire from left tip through all left knuckles, through VStab fin hole, through all right knuckles to right tip
5. Bend wire 90 deg at each tip, tuck into tip fairing pockets
6. Test deflection range (-20 deg to +25 deg), verify smooth operation and bevel clearance
7. Install elevator bridge joiner: slide into left elevator root pocket (CA), then right elevator root pocket (CA)
8. Verify synchronization: deflect one half, confirm the other follows within 1 deg
9. Install rear spar (1.5mm rod through stab at 60% chord)
10. Install elevator stiffener (1mm rod through elevator at 80% chord, 340mm length)
11. Thread main spar (3mm tube) through left stab, VStab fin, right stab
12. Bond stab roots to VStab fin (dovetail interlock + CA)
13. Bond control horn to left elevator (through slot in lower skin, pin + CA)
14. Pack tungsten putty into mass balance pocket, seal with cap
15. Route pushrod: thread 1mm wire through PTFE tube (pre-installed in boom/fin), connect Z-bend to control horn hole
16. Connect pushrod Z-bend to servo arm at X=350mm
17. Verify full deflection range with servo actuation, check for binding

---

## 10. Open Questions for Future Resolution

1. **Elevator servo throw geometry:** The exact servo arm length and pushrod hole position need to be calculated together to achieve the required +25/-20 deg range with the specific servo chosen. This is a servo-specific calculation done during electronics integration.

2. **Pushrod guide tube attachment inside fin:** The exact bonding points of the PTFE tube inside the VStab fin need to be determined during the fin section detailed design. The tube must not interfere with the VStab rear spar or rudder mechanism.

3. **Rudder pushrod/cable routing:** The rudder uses pull-pull Kevlar cables (per specifications.md). These cables route through the same boom and fin sections as the elevator pushrod. A cross-section layout at key stations (X=500, X=660, X=866) should be drawn to confirm no interference between elevator pushrod, rudder cables, and structural elements.

4. **Bridge joiner thermal cycling:** The CF-PLA bridge joiner operates in an open environment. CF-PLA has Tg ~60 deg C, which is adequate. Verify that summer car trunk temperatures (up to 70 deg C in Bulgaria) do not soften the bridge. Consider CF-PETG (Tg 80 deg C) if this is a concern.
