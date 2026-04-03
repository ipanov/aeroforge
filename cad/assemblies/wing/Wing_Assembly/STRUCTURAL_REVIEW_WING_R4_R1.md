# Structural Review: Wing Assembly R4 — Revision 1

**Date:** 2026-04-03
**Author:** Structural Engineer Agent
**Status:** REVIEW — response to AERO_PROPOSAL_WING_R4_R1.md
**Action:** MODIFY (3 required changes, 2 recommended changes)

---

## 1. Load Analysis

### Critical Load Cases

| Case | Load Factor | Speed | CL | q (Pa) | Source |
|------|------------|-------|-----|--------|--------|
| **Launch climb** | **8g** | 15 m/s | 1.12 | 137.8 | Electric motor climb at ~60 deg, peak thrust/weight ratio |
| Pullout from dive | 5g | 25 m/s (VNE) | 0.25 | 382.8 | High-speed dive recovery |
| Gust encounter | 3g | 10 m/s (cruise) | 0.95 | 61.3 | Turbulence penetration at thermalling speed |
| Max L/D | 1g | 10 m/s | 0.80 | 61.3 | Steady cruise |
| Landing | 2g | 5 m/s | 1.48 | 15.3 | Hard landing impact |

**Governing case: Launch at 8g** — produces the highest root bending moment.

Note: 8g is a conservative upper bound for an electric F5J launch. Real F5J models with similar power-to-weight ratios experience 3-5g during powered climb. The 8g case represents a peak gust overlay during launch transition. If mass closure requires it, the structural engineer would accept 6g as the design load factor (SF=1.23 at root with 10mm tube, SF=1.97 at 6g — adequate with D-box contribution).

### Bending Moment Distribution (8g Launch)

| Station | y (mm) | M (N*m) | V (N) |
|---------|--------|---------|-------|
| Root | 0 | 21.24 | 33.4 |
| P1/P2 | 256 | 13.61 | 26.2 |
| P2/P3 | 512 | 7.80 | 19.3 |
| P3/P4 | 768 | 3.71 | 12.7 |
| P4/P5 | 1024 | 1.23 | 6.8 |
| P5/P6 | 1280 | 0.12 | 2.0 |
| Tip | 1408 | 0.00 | 0.0 |

---

## 2. Spar Design — REQUIRED CHANGE #1

### Original Aero Proposal (8mm tube continuous)

The aero proposal specifies an 8mm CF tube from root to P4/P5. This is **structurally insufficient**:

| Location | 8mm tube only | Safety Factor | Verdict |
|----------|---------------|---------------|---------|
| Root | 618 MPa | 0.97 | **FAIL** |
| P1/P2 | 396 MPa | 1.52 | Marginal |
| P2/P3 | 227 MPa | 2.64 | OK |
| P3/P4 | 108 MPa | 5.55 | OK |
| P4/P5 | 36 MPa | 16.8 | OK |

CF tube allowable: 600 MPa (conservative, pultruded tube with safety margin for fitting stress concentrations).

### Required: Three-Step Spar System

| Segment | Span Range | Length | Type | I (mm^4) | Z (mm^3) | M (N*m) | sigma (MPa) | SF |
|---------|-----------|--------|------|----------|----------|---------|-------------|-----|
| Root → P3/P4 | 0-768mm | 768mm | 10mm CF tube (10/8mm) | 290 | 58.0 | 21.24 | 366 | **1.64** |
| P3/P4 → P4/P5 | 768-1024mm | 256mm | 8mm CF tube (8/6mm) | 137 | 34.4 | 3.71 | 108 | **5.55** |
| P4/P5 → tip | 1024-1408mm | 384mm | 4mm CF rod (solid) | 12.6 | 6.3 | 1.23 | 195 | **3.08** |

All segments exceed SF=1.5 at the 8g launch case.

### Spar Clearance Verification

| Station | Chord (mm) | Airfoil depth at 25% (mm) | 10mm tube | 8mm tube | 4mm rod |
|---------|-----------|--------------------------|-----------|----------|---------|
| Root | 170 | 14.1 | **+4.1 OK** | — | — |
| P3/P4 | 149 | 11.9 | **+1.9 OK** | — | — |
| P4/P5 | 129 | 10.2 | — | **+2.2 OK** | — |
| P5/P6 | 102 | 7.9 | — | — | **+3.9 OK** |
| Tip | 85 | 6.6 | — | — | **+2.6 OK** |

### Transition Sleeves

Two transition points:

1. **10mm → 8mm at P3/P4** (y=768mm): 20mm long CF sleeve, OD=12mm, bonded with CA. Nestled inside P3 end-rib. Mass: ~1.5g.

2. **8mm → 4mm at P4/P5** (y=1024mm): 20mm long CF sleeve, OD=10mm, bonded with CA. Nestled inside P4 end-rib. Mass: ~1.0g.

The sleeves transfer bending moment through the joint via close-fit bore in the end-ribs. The CF tube butts against the sleeve internally, with 5mm overlap on each side. The sleeve OD fits through the spar holes in the end-ribs.

### Rationale for 10mm Root Spar

The 8mm tube at root has SF=0.97 at 8g — it **barely fails** without D-box contribution. Two paths to adequate strength:

**Path A: 10mm tube alone** — SF=1.64, standalone structural integrity. The D-box is then bonus margin.

**Path B: 8mm tube + reinforced D-box** — CF-PLA shell in root zone (tensile ~60 MPa) + 8mm tube gives composite I_total=3909 mm^4 at root, shell stress=38 MPa (SF=1.58 with CF-PLA).

The structural engineer **recommends Path A (10mm tube)** because:
- Standalone SF=1.64 means the wing survives even if the D-box shell cracks (hard landing, UV degradation, impact)
- 10mm tube fits with 4.1mm clearance at root — no tight-fit risk
- Mass penalty: 10mm tube weighs 36g over 768mm vs 8mm tube at 27.7g over 768mm — only +8.3g per half
- Eliminates reliance on printed shell structural integrity at the highest-stress station

---

## 3. Rear Spar — REQUIRED CHANGE #2

### Aero Proposal: 5×3mm spruce root to P4/P5

The aero proposal does not explicitly specify rear spar extent. The v1 consensus had it terminating at P4/P5 (y=1024mm).

### Structural Assessment

With the extended span (1408mm vs 1280mm half-span), the outer panels (P5 at 256mm, P6 at 128mm) have no rear spar. Torsional analysis:

| Panel | Length | Aileron chord | Hinge moment @ 8g, VNE | Twist angle | Verdict |
|-------|--------|--------------|------------------------|-------------|---------|
| P5 | 256mm | 29-24mm | 0.23 N*m | 0.12 deg | OK |
| P6 | 128mm | 29-24mm | 0.06 N*m | 0.04 deg | OK |

The D-box alone provides adequate torsional rigidity for P5 and P6. The twist angles are negligible.

### Required Change

**Extend rear spruce spar to P4/P5** (unchanged from v1). This is confirmed adequate for the R4 planform.

The rear spar does NOT need to extend into P5/P6 because:
- P5/P6 span is 384mm (same as old P5 alone)
- D-box torsional stiffness GJ ≈ 577,000 N*mm^2 at P5
- Maximum twist at 8g VNE: 0.12 deg — aerodynamically invisible
- The 4mm CF main spar rod provides additional torsional restraint through close-fit rib bores

### Rear Spar Schedule

| Segment | Length | Type | Position | Clearance |
|---------|--------|------|----------|-----------|
| Root → P4/P5 | 1024mm | 5×3mm spruce strip | 60% chord | ≥0.5mm at P4/P5 |

---

## 4. Mass Budget — REQUIRED CHANGE #3

### Detailed Half-Wing Mass Budget

| Component | Mass (g) | Computation |
|-----------|----------|-------------|
| **Shell — all panels** | | |
| P1 shell (LW-PLA, 0.4mm vase, rho=0.55) | 19.5 | perimeter 347mm × 0.4mm × 256mm × 0.55e-3 |
| P2 shell | 19.1 | perimeter 339mm × 256mm |
| P3 shell | 17.9 | perimeter 318mm × 256mm |
| P4 shell | 16.1 | perimeter 285mm × 256mm |
| P5 shell | 13.3 | perimeter 236mm × 256mm |
| P6 shell | 5.4 | perimeter 191mm × 128mm |
| **Shell subtotal** | **91.3** | |
| D-box reinforcement (extra 0.3mm in LE-30% zone, P1-P4) | 14.0 | ~15% of shell mass in D-box zone |
| Ribs (25 × CF-PLA lattice, ~0.3g each) | 7.5 | 25 × 0.3g |
| **Main spar** | | |
| 10mm CF tube (768mm, rho=1.6 g/cm^3) | 36.0 | pi/4 × (10^2-8^2) × 768 × 1.6e-3 |
| 8mm CF tube (256mm) | 9.2 | pi/4 × (8^2-6^2) × 256 × 1.6e-3 |
| 4mm CF rod (384mm) | 7.7 | pi/4 × 4^2 × 384 × 1.6e-3 |
| Transition sleeves (×2) | 2.5 | CF tube offcuts |
| **Spar subtotal** | **55.4** | |
| Rear spar spruce (1024mm, 5×3mm, rho=0.45) | 6.9 | 5 × 3 × 1024 × 0.45e-3 |
| **Servos** | | |
| Flap servo P1 (9g metal gear) | 9.0 | |
| Flap servo P3 (9g metal gear) | 9.0 | |
| Aileron servo P4 (9g metal gear) | 9.0 | |
| Aileron servo P6 (5g low-profile) | 5.0 | KST X08 or PTK 7308MG-D |
| **Servo subtotal** | **32.0** | |
| Servo mounts + covers + horns | 12.0 | CF-PETG printed |
| Pushrods + Z-bends | 1.2 | 0.8mm music wire |
| TPU hinges + gap seal (4 surfaces) | 4.0 | |
| Tungsten mass balance (4 × 1g) | 4.0 | Flutter prevention |
| Joint hardware (dowel pins, CA pads) | 4.0 | 5 joints per half |
| Raked tip fairing | 1.0 | 5 deg aft rake, last 5% span |
| **HALF-WING SUBTOTAL** | **233.3** | |
| Contingency (5%) | 11.7 | |
| **HALF-WING TOTAL** | **245.0** | |
| **FULL WING (×2)** | **490.0** | |

### Mass Comparison to v1

| Item | v1 (2560mm) | R4 (2816mm) | Delta |
|------|-------------|-------------|-------|
| Shell panels | 86g | 91g | +5g (extra 128mm panel) |
| D-box | 15.6g | 14.0g | -1.6g (tighter planform) |
| Ribs | 5.3g | 7.5g | +2.2g (more stations) |
| Main spar | 32.4g | 55.4g | +23.0g (10mm tube upgrade + extra panel) |
| Rear spar | 6.1g | 6.9g | +0.8g |
| Servos | 32g | 32g | 0g |
| Hardware | 25.2g | 26.2g | +1.0g |
| **Per half** | 215.0g | 245.0g | +30.0g |
| **Full wing** | 430.0g | 490.0g | **+60.0g** |

The 60g increase is primarily from the spar upgrade (10mm tube + extra panel span). This is the structural cost of the 10% span increase and higher aspect ratio.

---

## 5. D-Box Torsional Rigidity

| Panel | Chord (mm) | D-box depth (mm) | Wall (mm) | GJ (N*mm^2) | Max twist at VNE |
|-------|-----------|-------------------|-----------|-------------|------------------|
| P1 | 170 | 14.1 | 0.7 | 3,920 | 0.02 deg |
| P2 | 168 | 13.8 | 0.7 | 3,750 | 0.02 deg |
| P3 | 162 | 13.1 | 0.7 | 3,250 | 0.03 deg |
| P4 | 149 | 11.9 | 0.7 | 2,490 | 0.04 deg |
| P5 | 129 | 10.2 | 0.7 | 1,630 | 0.08 deg |
| P6 | 102 | 7.9 | 0.6 | 850 | 0.12 deg |

All twist angles well below 0.5 deg — torsional rigidity is not a concern for any panel.

---

## 6. Flutter Prevention — RECOMMENDED CHANGE #1

| Item | Specification | Mass |
|------|--------------|------|
| Tungsten mass balance | 1g per control horn, 4 per half | 4.0g |
| TE stiffener | 0.8mm CF rod at 80% chord in ailerons | Included in shell |
| Hinge | Zero-slop TPU living hinge | 2.0g |

Flutter speed estimate: **>35 m/s** (> 1.4 × VNE). This exceeds the 1.2×VNE minimum.

The aileron mass balance is placed at the control horn, forward of the hinge line. Each aileron has one horn, one balance mass. The flap horns do not need mass balance because flaps operate at low frequency and are structurally stiffer.

---

## 7. Panel Joint Design — RECOMMENDED CHANGE #2

| Feature | Spec |
|---------|------|
| Type | Male/female tongue + groove |
| Tongue | 3mm, groove 3.2mm, 2mm deep |
| Spar hole | 10.3mm (P1-P3), 8.3mm (P3/P4→P4/P5), 4.2mm (P4/P5→tip) |
| Rear spar slot | 5.2 × 3.2mm |
| Adhesive | CA glue (medium viscosity) |
| Dihedral | In end-rib face geometry |
| Alignment | 2mm CF dowel pins (2 per joint) |

The P3/P4 joint carries the 10mm→8mm spar transition. The end-ribs at P3 must have:
- P3 rib: 10.3mm spar bore + 12mm transition sleeve pocket
- P4 rib: 8.3mm spar bore + 10mm transition sleeve pocket

---

## 8. AUW Impact Assessment

| Subsystem | Mass (g) |
|-----------|----------|
| Wing (full, R4) | 490 |
| Fuselage assembly | 91 |
| Empennage (HStab + Rudder) | 47 |
| Battery (3S 1300mAh 75C + XT60) | 165 |
| Receiver (Turnigy 9X V2) | 18 |
| Motor (Sunnysky X2216 or equivalent) | 55 |
| ESC (20-30A) | 16 |
| Folding prop + spinner | 16 |
| Wing servos (4 × 9g + 2 × 5g) | 46 |
| Fuselage servos (elevator + rudder, 2 × 9g) | 18 |
| Wiring, connectors, extensions | 20 |
| **AUW** | **982g** |

### Assessment

At 982g, the aircraft exceeds the 950g maximum target. This is **32g over budget**. The excess comes from:
- Wing mass increase: +60g vs v1 (due to 10% more span and spar upgrade)
- The spar upgrade (10mm tube) accounts for +23g of this

**Mass recovery options** (in order of preference):

1. **Reduce shell wall thickness to 0.35mm** in P4-P6 (lower-stress outer panels): saves ~8g
2. **Use 5g servos for ALL ailerons** (not just P6): saves ~4g
3. **Reduce root spar design load to 6g** (accept 10mm tube SF=1.23 without D-box, or 1.97 with D-box): allows stepping back to 8mm tube at root, saving ~8g — but this compromises the standalone safety margin
4. **Optimize rib count** (20 instead of 25): saves ~1.5g
5. **Remove one flap servo** (single centralized flap servo with torque rod): saves ~9g but increases mechanical complexity and reduces control authority

If options 1+2+4 are applied: saves ~13.5g, bringing AUW to ~969g — still over budget.

The structural engineer recommends **accepting 950-1000g AUW** for the initial build and targeting mass reduction in the iteration cycle after CFD/FEA validation. The wing loading at 982g is 24.2 g/dm^2 — competitive with F5J models in the 2.8m class.

---

## 9. Structural Verdict

### Summary of Required Changes

| # | Change | Aero Impact | Mass Impact |
|---|--------|-------------|-------------|
| **1** | Upgrade root spar to **10mm CF tube** (root→P3/P4) | Zero — fully internal | +8.3g per half |
| **2** | Confirm rear spruce spar **terminates at P4/P5** | Zero — D-box adequate for torsion in P5/P6 | No change |
| **3** | Accept **490g full wing mass** (+60g vs v1) and manage AUW accordingly | Wing loading increases 2.4% — negligible L/D impact | +60g |

### Summary of Recommended Changes

| # | Change | Rationale |
|---|--------|-----------|
| **1** | Add 4 × 1g tungsten mass balance (one per control horn) | Flutter speed > 1.4 × VNE |
| **2** | P3/P4 joint designed for 10mm→8mm spar transition | Sleeve + pocket geometry |

### Items Accepted Without Modification

- Superelliptical n=2.3 planform — structurally sound
- Airfoil blend schedule — no structural concerns
- Twist distribution — no structural implications
- Panel layout 6× per half — all fit printer bed
- Control surface geometry — hinge moments within limits
- Dihedral scheme (hybrid continuous + tip break) — no structural implications
- Schuemann integrated tip + raked tip — zero structural change

---

## References

- Aero proposal: `AERO_PROPOSAL_WING_R4_R1.md`
- NeuralFoil section data: computed 2026-04-03
- Material properties: LW-PLA 0.55 g/cm^3 (foamed), CF tube 1.6 g/cm^3, spruce 0.45 g/cm^3
- CF tube allowable stress: 600 MPa (conservative, pultruded)
- CF-PLA tensile strength: 55-70 MPa (for D-box reinforcement)
- HStab consensus: `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md`
