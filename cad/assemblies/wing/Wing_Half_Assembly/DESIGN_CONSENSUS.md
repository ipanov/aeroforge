# Design Consensus: Wing Half Assembly (derived baseline)

**Date:** 2026-04-02  
**Status:** BASELINE FOR TOP-DOWN REWORK

This assembly is the canonical half-wing parent for the current glider baseline.
It is derived from [Wing_Assembly](D:/Repos/aeroforge/cad/assemblies/wing/Wing_Assembly/DESIGN_CONSENSUS.md)
and exists so the workflow can proceed correctly:

1. Whole wing consensus
2. Wing half assembly drawing
3. Panel/component derivation
4. Bottom-up 3D reassembly and validation

## Role

- This folder defines the **single canonical half-wing assembly**.
- Left and right aircraft wings are mirrored uses of this same assembly.
- Panel drawings and panel solids must derive from this assembly-level geometry, not bypass it.

## Current Baseline

- Semi-span: 1280 mm
- Panels: 5 at 256 mm each
- Root chord: 210 mm
- Tip chord: 115 mm
- Airfoil family: AG24 to AG03 continuous blend
- Washout: 4.0 deg total, non-linear
- Polyhedral: 0 / 0 / 1.5 / 2.5 / 7.0 deg cumulative scheme
- Control layout: flaps in P1-P3, ailerons in P4-P5

## Next Design Loop

This baseline is intentionally a parent artifact, not a final optimization result.
The next aero/structural loop must revisit:

- Planform family comparison beyond the current first-order trapezoidal schedule
- Quarter-chord law and sweep strategy
- Tip-shape family and winglet integration
- Assembly-first internal structure strategy so the wing reaches HStab-level shell/mesh quality
