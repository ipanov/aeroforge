# H-Stab Design Reference — Data from Real F5J Models

## Hard Numbers from Competition Sailplanes

### H-stab Area Ratios (stab area / wing area)
| Model | Ratio | Source |
|-------|-------|--------|
| Prestige 2PK | 9.2% | Manufacturer |
| Pike Perfection (X-tail) | 10.3% | Manufacturer |
| Pike Perfection (V-tail) | 9.9% | Manufacturer |
| Xplorer 3 | 10.8-11.6% | Manufacturer |
| Edge F5J | ~10.9% | Manufacturer |
| El Nino F5J | 8.9% | Manufacturer |
| Eternity F5J | 10.1% | Manufacturer |
| **Median** | **~10%** | |

### For AeroForge (wing area = 41.6 dm²)
- Target: 10% of wing area = **4.16 dm²** (416 cm²)
- Range: 8.9-11.6% = 3.7 to 4.8 dm²

### Tail Volume Coefficients
- Prestige 2PK PRO: Vh = 0.45
- Typical F5J: Vh = 0.40-0.50
- General sailplane: Vh = 0.35-0.55

### Bubble Dancer (our primary reference, Mark Drela)
- All-moving tail
- Area: 100 sq in = 6.45 dm² (9.8% of 1014 sq in wing)
- Vh = 0.40
- HT-21 airfoil (5.1% thick)
- Joiner: 3/8" (9.5mm) CF rod
- Weight: 21g (for a 3m, 888g sailplane)
- Deflection: -20° to +12°

### Tail Configuration Trends
Most modern F5J models use X-tail or V-tail. The Bubble Dancer uses conventional all-moving.
For 3D printing, all-moving conventional is simplest (one-piece per half, pivot rod).

## AeroForge H-Stab Target (derived from data)

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Area | 4.16 dm² (416 cm²) | 10% of 41.6 dm² wing |
| Vh | ~0.42-0.45 | Competition range |
| Airfoil | HT-13 (6.5%) | Best balance of response + printability at Re 37k-59k |
| Configuration | All-moving | Simplest for 3D printing, proven (Bubble Dancer) |

### Planform sizing (area = 416 cm², tapered)
Using taper ratio 0.64 (from Bubble Dancer scaling):
- Span = 460mm, Root = 110mm, Tip = 70mm → Area = (110+70)/2 × 460 = 414 cm² ✓

But the actual planform should have **rounded/elliptical tips** (not square cut), which reduces effective area by ~5-8%. So either:
- Option A: Keep 460mm span, increase root to 115mm → ~430 cm² after tip rounding
- Option B: Increase span to 480mm, keep 110/70mm → ~435 cm² after tip rounding

### Weight Target
Bubble Dancer stab weighs 21g at 3m span. Scaling by area ratio:
- BD stab: 6.45 dm² → 21g → 3.26 g/dm²
- AeroForge: 4.16 dm² × 3.26 = **13.6g** target
- 3D printed in LW-PLA will likely be heavier: **15-20g** realistic target
