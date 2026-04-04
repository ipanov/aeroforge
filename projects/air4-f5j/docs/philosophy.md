# AeroForge Design Philosophy

> Classification note: this document reflects the philosophy of the current
> AIR4 sailplane example and its manufacturing assumptions.
>
> It is preserved as example-project context, not as universal framework
> policy.

## The Core Idea

**"Why make it simple when it can be complex - for the same price?"**

A 3D printer doesn't care if it prints a flat rectangle or a topology-optimized lattice.
The filament cost is the same. The print time is similar. But the aerodynamic performance
is vastly different.

This is the fundamental competitive advantage of AeroForge over commercial RC sailplane kits.

## The Problem with Commercial Kits

Commercial F5J and competition sailplanes (Insight, Introduction, F3J models) are built
from carbon fiber layups in precision molds. This gives excellent strength-to-weight ratio,
but it constrains the design:

- **2-3 airfoil stations maximum** - because each station needs a different mold plug
- **Simple planforms** - straight taper or at most two taper breaks, because complex
  shapes require complex molds
- **Uniform internal structure** - because laying carbon cloth over complex internal
  geometry is impractical
- **Fixed geometry** - once the mold is cut, the design is frozen

These kits cost $300-600+ and represent 10-15 year old aerodynamic designs locked
into manufacturing constraints.

## The AeroForge Advantage

A 3D printer has **zero marginal cost for complexity**:

- **Every rib can be a unique airfoil** - continuously blended from root to tip across
  10, 20, or 50 stations. Not just AG24 at root and AG03 at tip, but a smooth
  mathematical transition at every single rib position.

- **Optimal planform** - elliptical, Horten-style, or any shape the aerodynamic
  analysis says is ideal. Not constrained to what a human can cut from a template.

- **Continuously varying twist** - not "2 degrees washout at the tip" but an
  optimally computed twist distribution at every station to minimize induced drag
  across all flight regimes.

- **Complex internal structure** - geodetic lattice, topology-optimized lightening
  patterns, variable-density infill. Each rib can have a unique internal structure
  optimized for the local loads at that span station.

- **Perfect gap seals** - control surface gaps shaped to minimize leakage drag,
  printed as integral features of the structure.

- **Continuous dihedral/polyhedral** - not a single angle break but a smooth curve
  if that's what the stability analysis recommends.

## What We Sacrifice

3D-printed thermoplastic (LW-PLA) has 10-20x worse specific strength than carbon fiber.
We cannot match a competition sailplane in:

- Absolute structural weight (our airframe will be heavier per unit span)
- Maximum wingspan (we top out around 2-2.5m vs 3-4m for carbon F3J)
- Torsional stiffness at the extremes
- Surface finish (printed surfaces have layer lines vs polished mold surfaces)

## How We Compensate

Every gram of structural disadvantage must be recovered through aerodynamic superiority:

1. **Latest airfoil research** - not RG-15 from 1988, but the latest AG series and
   potentially custom-optimized profiles for our exact Reynolds number range
2. **Perfect twist distribution** - computed, not approximated
3. **Blended airfoils** - smooth transitions that commercial kits can't economically produce
4. **Optimized control surface sizing** - AI-computed deflections for each flight mode
5. **Ideal planform** - whatever shape maximizes L/D, not what's easy to build
6. **Advanced mixing** - 5+ flight modes with optimized camber, reflex, and crow settings
   programmed into the Turnigy 9X (AI-assisted programming of the notoriously
   difficult Chinese radio interface)
7. **Topology-optimized structure** - minimum weight for required strength at each location

## The Price-Performance Target

The goal is the **best possible price-performance ratio**:

- **Material cost**: ~$10-20 in filament + $10-15 in carbon tubes/spruce + $5 in hardware
- **Electronics**: ~$80-120 (servos, motor, ESC, receiver, battery - mostly already owned)
- **Total**: ~$100-150 vs $300-600 for a commercial kit
- **Performance**: Must EXCEED classic designs like Insight and Introduction in
  glide ratio, handling, and controllability - despite the structural weight penalty

## Design Principles

1. **Maximize printed complexity** - if the printer can do it, do it. Complex lattice ribs,
   blended airfoils, integrated gap seals, topology-optimized mounts.
2. **Minimize hand labor with exotic materials** - no cutting carbon cap strips, no hand-
   laminating fiberglass. Use off-the-shelf carbon tubes (slide through holes) and spruce
   strips (glue into slots). Assembly should be: print, slide spars in, glue, fly.
3. **AI optimizes everything** - airfoil selection, twist, planform, control surface sizing,
   transmitter programming, CG placement, flight mode settings.
4. **Every detail matters** - squeeze 2% performance from every surface, every gap, every
   transition. The printer doesn't charge extra for perfection.
5. **Cost discipline** - complex geometry is free, but material cost and off-the-shelf parts
   must stay cheap. No exotic components.
