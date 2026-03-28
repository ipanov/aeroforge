# Off-The-Shelf Components - Procurement Plan

## Primary Source: Der Himmlische Höllein (Germany)
Website: hoelleinshop.com | Ships EU | RC model building specialist

### Carbon Fiber Rods (fuselage stringers)
| Product | Item # | Dimensions | Price | Qty Needed |
|---------|--------|-----------|-------|------------|
| CF rod 1.0x1000mm | HOEKS10010 | 1.0mm dia x 1000mm | ~€2.00 | 4 (stringers) |
| CF rod 1.5x1000mm | HOEKS10015 | 1.5mm dia x 1000mm | ~€2.20 | 2 (backup) |
| CF rod 2.0x1000mm | HOEKS10020 | 2.0mm dia x 1000mm | €2.35 | 2 (control linkage) |
| CF rectangular 3.0x0.5x1000mm | HOEKV03005 | 3.0x0.5mm x 1000mm | TBD | Optional |

### Carbon Fiber Tubes
| Product | Dimensions | Price | Use |
|---------|-----------|-------|-----|
| CF tube 8.0/6.0x1000mm | 8mm OD, 6mm ID, 1mm wall | TBD (check Höllein or Lindinger) | Main wing spar |
| CF tube 10.0/8.0x1000mm | 10mm OD, 8mm ID, 1mm wall | TBD | Tail boom |
| CF tube 12.0/10.0x1000mm | 12mm OD, 10mm ID | TBD | Tail boom (alternative) |

**CRITICAL: Maximum tube length available matters!**
- Höllein: Likely 1000mm max
- Lindinger.at: R&G brand up to 2000mm
- Easy Composites EU (NL): Up to 2000mm

### Pine/Spruce Strips (rear spar)
| Product | Dimensions | Price | Qty |
|---------|-----------|-------|-----|
| Pine strip 5x5x1000mm | 5x5mm x 1000mm | ~€0.95 | 4 |
| Pine strip 5x3x1000mm | 5x3mm x 1000mm | ~€0.85 | 4 (if available) |

## Wing Spar Strategy

### Problem: Half-span = 1280mm, but tubes max ~1000mm
**Options:**
1. **Two-piece spar with sleeve joint:** Two 1000mm tubes, joined with a 6mm OD insert tube (200mm overlap). Joint at panel 2-3 boundary (512mm from root). Adds ~5g, but proven technique.
2. **Single 1500mm tube:** Source from Lindinger.at or Easy Composites EU. Cut to 1280mm. Cleaner but harder to source.
3. **Two-section wing:** Break wing at panel 3 (768mm from root). Each section has its own 800mm spar. Join sections with external joiner tube. Better for transport.

**Recommended: Option 3 (two-section wing)**
- Inner section: Panels 1-3 (768mm span, ~800mm spar)
- Outer section: Panels 4-5 (512mm span, ~550mm spar)
- Joiner: 6mm OD tube, 200mm long, slides into both sections
- Benefits: Fits in car easily, 1m tubes from any source work, proven in competition

### Wing Section Breakdown
```
Root ─── P1 ─── P2 ─── P3 ═══ P4 ─── P5 ─── Tip
         256     256     256 ║  256     256
    ────── Inner section ──── ║ ── Outer section ──
         768mm spar           ║    512mm spar
                              ║
                         Wing joiner
                     (6mm tube, 200mm)
```

## Fixed Inventory (Already Owned)
| Component | Weight | Notes |
|-----------|--------|-------|
| Battery 3S 1300mAh 75C | 165g (w/ XT60) | 2 units available |
| Turnigy 9X V2 receiver | 18g | 8 channels |

## To Order - Priority List
| Priority | Item | Source | Est. Cost |
|----------|------|--------|-----------|
| 1 | CF tube 8/6x1000mm (x2) | Höllein or Lindinger | ~€8-12 |
| 2 | CF tube 10/8x1000mm (x1) | Höllein or Lindinger | ~€6-8 |
| 3 | CF rod 1.0x1000mm (x4) | Höllein | ~€8 |
| 4 | Pine strip 5x5x1000mm (x4) | Höllein | ~€4 |
| 5 | CF joiner tube 6/4x200mm | Höllein | ~€2 |
| 6 | Servos JX PDI-1109MG (x4) | Temu/AliExpress | ~€24 |
| 7 | Servo JX PDI-933MG (x2) | Temu/AliExpress | ~€14 |
| 8 | Motor (TBD spec) | Temu/AliExpress | ~€15-25 |
| 9 | ESC 20-30A | Temu/AliExpress | ~€8-12 |
| 10 | Folding prop + spinner | Temu/AliExpress | ~€8-12 |
| **Total** | | | **~€95-120** |

## Shipping Strategy
- **Höllein (Germany):** Items 1-5. Single order ~€25-30 + shipping. Fast EU delivery.
- **Temu:** Items 6-10. Single order ~€70-85. 7-14 day delivery.
- **AliExpress:** Backup for anything not on Temu. 3-6 week delivery.
- **Bulgaria:** Check local hobby shops for CF tubes/rods if faster than Germany.
