# H-Stab Airfoil Comparison at Re=50,000

Analysis performed with AeroSandbox 4.2.9 + NeuralFoil.

## Summary

| Airfoil | t/c | Best L/D | CL at 2° | CD at 2° | Notes |
|---------|-----|----------|----------|----------|-------|
| NACA 0009 | 9.0% | 24.9 | 0.113 | 0.0186 | **DEADBAND** — weak response at low alpha |
| HT-08 | 5.0% | 20.3 | 0.210 | 0.0140 | Linear, thin, Drela for small tails |
| HT-13 | 6.5% | 19.4 | 0.239 | 0.0149 | **Linear, printable thickness**, intermediate |
| HT-14 | 7.5% | 19.3 | 0.255 | 0.0158 | Linear, thickest, for heavy gliders |
| HT-21 | 5.1% | 19.0 | 0.227 | 0.0147 | Bubble Dancer choice, all-moving design |

## Key Finding

NACA 0009 has the highest L/D but **generates only 0.113 CL at 2° alpha** — less than half of HT-13's 0.239 CL. This is the "deadband" problem Drela designed the HT series to solve.

For our all-moving stab, **HT-13 is the best choice**:
- 2x the CL response of NACA 0009 at small deflections
- 6.5% thick = 7.15mm at 110mm root chord — printable in LW-PLA
- Good L/D of 19.4
- Linear CL through zero — no deadband

## Recommendation

**HT-13** for AeroForge H-stab. At 110mm root chord, Re≈58,000. At 70mm tip, Re≈37,000.
