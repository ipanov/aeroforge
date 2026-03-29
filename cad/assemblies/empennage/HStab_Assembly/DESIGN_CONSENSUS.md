# Design Consensus: H-Stab Assembly (v2)

**Date:** 2026-03-29
**Rounds:** 3 (R1: initial → R2: structural constraints → R3: airfoil blending + tip optimization)
**Status:** AGREED — both agents signed off on v2

---

## Agreed Specifications

| Parameter | Value | Source |
|-----------|-------|--------|
| Configuration | All-moving (entire surface pivots) | Aero R1, Struct R1 approved |
| Root airfoil | **HT-14 (7.5%)** | Structural need for spar clearance |
| Tip airfoil | **HT-13 (6.5%)** | Aero R3 — equal L/D, 13% less material |
| Blend | **Linear HT-14 → HT-13, root to tip** | Every rib unique — 3D printing differentiator |
| Span | **430mm** (215mm per half) | Struct R1 |
| Root chord | **115mm** | Re 61,300 at 8 m/s |
| Tip chord | **75mm** (tapers to 60mm in last 15mm) | Aero R3 — swept tip closure |
| Taper ratio | 0.652 (main section) | Derived |
| Area | ~408 cm² (4.08 dm²) | Derived |
| AR | 4.53 | Derived |
| Vh | 0.382 | Acceptable for all-moving |
| S_h/S_w | 9.8% | Within F5J range (8.9-11.6%) |
| Planform | **Trapezoidal** | Aero R3 justified: elliptical gives only 0.22% drag improvement |
| Tip shape | **Squared-off with LE sweep (last 15mm)** | Aero R3 — fixes vortex location, reduces mass |
| Sweep | 0° main section, ~45° LE in last 15mm tip | Aero R3 |
| Mass target | **22-28g (25g nominal)** | Struct R1 |
| Pivot axis | 3mm CF rod at 25% MAC | Aero R1, Struct approved |
| Rear spar | 2mm CF rod at 65% chord | Struct R1 |
| Deflection | -20° to +12° | Aero R1 |
| TE truncation | 97% chord (~0.8mm flat TE) | Struct R2 |
| Wall thickness | 0.45mm (vase mode, LW-PLA) | Struct R1 |

## Airfoil Blending Schedule

| Span station (eta) | Airfoil | t/c | Thickness (mm) | Chord (mm) |
|---------------------|---------|-----|----------------|------------|
| 0.00 (root) | HT-14 | 7.5% | 8.6 | 115 |
| 0.25 | Blend | 7.25% | 7.8 | 105 |
| 0.50 | Blend | 7.0% | 6.9 | 95 |
| 0.75 | Blend | 6.75% | 5.9 | 85 |
| 0.93 (before tip) | HT-13 | 6.5% | 4.9 | 75 |
| 1.00 (tip) | HT-13 thinned | ~5% | 3.0 | 60 |

Implementation: linearly interpolate HT-14 and HT-13 coordinate arrays as function of span fraction. Every rib station gets a unique blended profile. Trivial in code, free in 3D printing.

## Tip Geometry Detail

```
Plan view (right half, last 15mm of span):

    ----TE (straight)---+  75mm chord at eta=0.93
        \               |
         \-LE (swept)---+  60mm chord at eta=1.00
                        |
    <--15mm-->
```

- LE sweeps back ~45° in the last 15mm
- TE remains straight
- Chord tapers from 75mm to 60mm
- Thickness tapers to ~5% at tip (3mm absolute)
- **Pivot rod terminates BEFORE the swept section** (at eta=0.93, 200mm from root)

## Components

| Component | Type | Material | Est. Mass |
|-----------|------|----------|-----------|
| HStab_Left | Custom, printed | LW-PLA, blended airfoil | 10-12g |
| HStab_Right | Custom, printed (mirror) | LW-PLA, blended airfoil | 10-12g |
| HStab_Joiner_Rod | Off-shelf | 3mm CF rod, ~430mm | 1.4g |
| Rear_Spar_Left | Off-shelf | 2mm CF rod, ~200mm | 0.5g |
| Rear_Spar_Right | Off-shelf | 2mm CF rod, ~200mm | 0.5g |
| Control_Horn | Custom or wire | PETG or 0.8mm music wire | 0.5g |
| **Total** | | | **23-27g (25g target)** |

## Pivot Bearing Detail

- PETG tail mount socket with brass tube inserts (4mm OD / 3mm ID, 8mm long)
- Two bearing points spaced 25-30mm
- 3mm CF rod slides through brass tubes
- Retained by E-clips or CA'd collars

## Servo & Linkage

- 9g servo, fuselage-mounted (NOT at pivot — CG penalty unacceptable)
- 0.8mm music wire pushrod, ~250mm, ball-link at horn end
- Horn: PETG, bolted through rear spar at 80% chord

## Print Strategy

- Each half flat on Bambu bed (215mm x 115mm, 8.6mm Z)
- Vase mode with diagonal rib grid (Tom Stanton method)
- LW-PLA at 230°C, target density 0.5-0.65 g/cm³
- 0.45mm single wall
- TE bonded with thin CA, tip closed with PLA cap

## Performance (HT-14 root / HT-13 tip blend)

| Station | Re | CL at 2° | L/D at 4° | Mission-weighted L/D |
|---------|-----|----------|-----------|---------------------|
| Root (HT-14) | 61,300 | 0.253 | 21.1 | 16.3 |
| Mid (blend) | 50,700 | ~0.245 | ~20.0 | ~15.5 |
| Tip (HT-13) | 40,000 | 0.220 | 17.0 | 12.8 |

## Trade-offs Made

| What Aero Wanted | What Structural Constrained | Compromise |
|-----------------|---------------------------|------------|
| 15-18g mass | Min achievable: 22-25g | 25g target |
| HT-13 everywhere (best aero) | Need 7.5% at root for spar | HT-14 root → HT-13 tip blend |
| 460mm span | Mass + bed fit | 430mm, chords increased |
| No rear spar | TE would flutter | 2mm CF at 65% (+1g) |
| Simple tip radius | Aero R3: vortex not controlled | Squared-off with LE sweep |
| Uniform airfoil | 3D printing differentiator | Span-varying blend |

## Round History

**Round 1:** Aero: HT-13, 460mm, 110/70, 15-18g. Struct: MODIFY — mass impossible, thickness marginal.
**Round 2:** Aero: HT-14, 430mm, 115/75, 22-28g, +rear spar. Struct: ACCEPT.
**Round 3 (user feedback):** Why no airfoil blending? Why simple tips? Aero: added HT-14→HT-13 blend, optimized tip with LE sweep, justified trapezoid planform with 0.22% induced drag math. Struct: ACCEPT all changes.

## What Makes This Design Special (3D Printing Differentiator)

1. **Span-varying airfoil blend** — every rib station has a unique profile optimized for local Re. Impossible with conventional construction, trivial with 3D printing.
2. **Optimized tip closure** — swept LE tip shape that controls vortex formation. Free geometry with a printer.
3. **All-moving simplicity** — one piece per half, no hinge gap drag, maximum control authority.
4. **Vase-mode construction** — single continuous print path, lightest possible shell.
