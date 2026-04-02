# AeroForge - Codex Working Memory

This file exists in parallel to `CLAUDE.md` so Codex can preserve project intent
between sessions without relying on short-term memory.

## Project Mission

The mission of AeroForge is larger than one glider:
- build a **generic AI-assisted aircraft framework**
- prove that top-down AI synthesis plus modern tooling can outperform traditional trial-and-error iteration
- use 3D printing freedom to exploit geometric complexity where it buys aerodynamic or structural advantage
- converge through repeated synthetic analysis, packaging review, and engineering refinement

The current aircraft is the F5J glider **Iva** / `Iva_Aeroforge`.

## Non-Negotiable Workflow

1. The **whole aircraft is the top-level assembly**.
2. The top-level aircraft must be designed first.
3. Wing, fuselage, empennage, and lower-level parts refine downward from that parent.
4. 2D parent drawings must exist and be reviewed before 3D ownership expands.
5. The top-level aircraft cannot be treated as a decorative wrapper.

## Design Philosophy

- Complexity is acceptable when it buys measurable performance or integration quality.
- Oversimplified geometry is not a virtue by itself.
- AI should be used to explore:
  - aerodynamic shape
  - structural load paths
  - packaging
  - interference drag reduction
  - control / stability / trim implications
- The target is not “good enough for a hobby project.” The target is to challenge professional benchmark gliders using better iteration speed and broader synthetic exploration.

## Parent-Drawing Rule

Parent drawings must show:
- real airframe geometry
- interfaces
- packaging zones
- routing
- stations
- engineering intent

Off-the-shelf parts must appear as **engineering envelopes only**, not as owned manufacturing drawings:
- battery
- motor
- ESC
- receiver
- servos
- spinner
- propeller

## Current Aircraft Freeze

For `Iva_Aeroforge`, these are frozen unless a later loop produces a real reason to reopen them:
- datum: nose tip = `X=0`
- wing LE = `X=260 mm`
- H-stab pivot = `X=911 mm`
- integrated fuselage concept
- conventional H-stab baseline
- reuse of current wing, fuselage, and H-stab baselines

## Current Open Problems

- whole-aircraft mass closure
- aircraft-level CG closure
- propulsion and cooling definition
- final incidence / decalage / trim signoff
- local fuselage OML refinement
- later synthetic tunnel / strength / flutter / stability workflow

## Analysis Roadmap

Once the 3D whole-aircraft baseline is mature, continue toward:
- synthetic wind-tunnel testing
- structural testing
- torsion testing
- flutter testing
- controllability testing
- stability testing
- interference-drag testing
- packaging and cooling iteration

## Tooling Reality

`SU2` is planned and useful, but current official support does **not** mean full GPU CFD on the RTX 3070. Treat it as a real but limited CFD path, and document the honest constraints.
