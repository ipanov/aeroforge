## Wing Research Brief: Iva_Aeroforge R2

### Scope
This is the next wing-loop brief for the full `Iva_Aeroforge` aircraft, not a panel-only review. The wing decision must stay coupled to aircraft datum, CG, tail station, and fuselage packaging.

### Current aircraft context
- Datum: nose tip / fuselage centerline reference used by the aircraft-level assembly.
- Wing LE station: `X = 260 mm`
- H-stab station: `X = 911 mm`
- CG target: `31-33% MAC`
- Incidence / decalage: provisional aircraft-level wing incidence `0.0 deg`; tail setting remains inherited from the H-stab consensus until aircraft trim is closed.

### Core finding
The current wing loop should not treat the old trapezoidal area estimate as final. The present superelliptic chord law likely increases effective wing area enough to matter for:
- wing loading
- Reynolds distribution
- span efficiency assumptions
- mass budget and bending moment
- aircraft-level CG and trim margins

If that is true, the wing planform is not just a refinement of the old trapezoid; it is a different loading and mass problem.

### Working candidate now

The active candidate to carry into the next 2D pass is:
- **span:** `2816 mm`
- **half-span:** `1408 mm`
- **panelization:** five `256 mm` sections plus one short `128 mm` tip section per half-wing
- **root chord:** `170 mm`
- **tip chord:** `85 mm`
- **planform family:** superelliptic, tightened versus the older broader wing
- **estimated area:** `~43.7 dm^2`
- **estimated aspect ratio:** `~18.2`
- **estimated MAC:** `~157 mm`

This is the current best compromise between:
- less stubby overall proportion
- controlled wing area
- plausible printed structural depth
- acceptable aspect ratio for the class intent

### 2560 vs 2816 vs 3072 span
| Option | What it means | Pros | Risks | Recommendation |
|---|---|---|---|---|
| `2560 mm` | Baseline current architecture | Lowest integration risk, matches current subassemblies, easiest to validate against existing wing consensus | May leave performance on the table versus current F5J benchmark direction | Keep as reference baseline |
| `2816 mm` | Moderate stretch using a shorter added section per half-wing | Better proportion, likely better induced-drag efficiency than `2560 mm`, smaller structural jump than `3072 mm` | Still requires taper and area re-closure; still adds bending and mass | Preferred next candidate |
| `3072 mm` | Full extra `256 mm` segment per half-wing | Maximum span efficiency potential in the current printer logic | Biggest bending, joint, and mass penalty; most likely to overshoot area if taper stays loose | Keep only as an upper-bound comparison |

### Superelliptic taper implications
The superelliptic chord law is the main risk item here.

If the wing keeps the same root/tip endpoints and only changes from a trapezoid to a superelliptic taper, the effective mean chord can rise above the old estimate. That means:
- the old `41.6 dm²` figure is likely optimistic
- loading may be lower than expected only if mass stays fixed, but
- structural mass and wetted area can rise enough to erase the benefit
- both `2816 mm` and `3072 mm` amplify the same issue if taper is not tightened

Practical conclusion:
- do **not** lock the span first and the taper later
- do **not** lock the chord law until the integrated area and MAC are recomputed from the actual profile
- if the superelliptic law materially increases area, the current wing needs a second pass on taper and tip shape before it can be considered final

### Airfoil research set for the next loop
Use an explicit comparison set instead of treating airfoil review as open-ended.

Recommended research set:
- **Root candidate:** `AG35`
- **Mid-span candidate:** `AG36 / AG37`
- **Outer-panel candidate:** `AG38`
- **Tip comparison:** `AG38` vs `AG03`

Why this set:
- the local research already flags the `AG35-38` family as more appropriate through the full Reynolds band of a lighter, slimmer wing
- the current root no longer needs to stay as thick as the older `AG24`-driven baseline
- `AG38` is attractive at the outer wing and tip because the tighter taper pushes the local Reynolds number down again
- `AG03` remains a useful tip comparison, but no longer needs to be treated as the default winner

Required comparison:
- current direct `AG24 -> AG03` blend
- revised `AG35 -> AG36/37 -> AG38` family
- hybrid `AG35 -> AG37 -> AG38 -> AG03` family
- reject any revised family that improves polars only by forcing unacceptable structural thickness penalties in the printed wing

### Tip concept options
Compare these three tip families under the same aircraft-level assumptions:

1. **Current blended winglet / tip extension**
- Best if the goal is to preserve the existing visual language and keep some induced-drag benefit.
- Risk: extra tip mass and more bending moment, which is expensive at 3D-print scale.

2. **Clean tapered tip, no winglet**
- Lowest mass, simplest structure, easiest to print and validate.
- Likely the best baseline if `3072 mm` is selected and the span increase is used to buy efficiency instead of tip complexity.

3. **Mild polyhedral / load-relief tip**
- Can help span efficiency and handling without the full winglet penalty.
- Risk: if overdone, it becomes a geometry complication without a clear aero payoff at this Reynolds number.

Working position:
- for `2560 mm`, a light blended tip concept may be acceptable
- for `2816 mm`, the safer candidate is a cleaner, lower-mass tip unless the winglet gives a clear quantified benefit
- for `3072 mm`, the tip should stay as simple and light as possible

### Wing loading risk
Because the aircraft-level baseline already sits near the upper mass band, any area increase from the superelliptic law must be treated as a real loading change.

Implication:
- if area grows and mass does not drop, wing loading may remain acceptable but induced drag and bending mass may worsen
- if area grows and mass also grows, the aircraft moves away from the intended F5J efficiency target
- the wing loop should therefore measure actual integrated area before making any final span decision

### Next comparisons to run
1. **Integrate actual wing area and MAC**
- Compare `2560 mm`, `2816 mm`, and `3072 mm`
- Use the current superelliptic chord law, then compare against the old trapezoidal baseline
- Output: area delta, MAC delta, aspect ratio, and wing loading at the current AUW band

2. **Sweep taper law against span**
- Keep span fixed, then compare:
  - current superelliptic taper
  - a tighter outer taper
  - a simpler linear/trapezoidal fallback
- Goal: identify whether the extra area is coming from a beneficial spanload shape or just geometric overgrowth

3. **Tip concept A/B/C**
- Compare:
  - blended winglet
  - clean tapered tip
  - mild polyhedral tip
- Hold span and root/tip stations constant during the comparison

4. **Aircraft trim re-check after area changes**
- Recompute CG sensitivity, wing loading, and incidence/decalage assumptions after the final wing area is known
- Confirm the wing LE at `260 mm` and H-stab station at `911 mm` still give a workable trim envelope

5. **Mass-growth sensitivity**
- Quantify how much extra structural mass the `2816 mm` and `3072 mm` spans require relative to `2560 mm`
- Reject any span/tip option that improves span efficiency on paper but pushes AUW and bending mass out of the current budget

- 6. **Airfoil-family comparison**
- Compare:
  - direct `AG24 -> AG03`
  - staged `AG35 -> AG36/37 -> AG38`
  - hybrid `AG35 -> AG37 -> AG38 -> AG03`
- Hold the same span and taper law while checking:
  - Reynolds suitability
  - section thickness for printed structure
  - flap / aileron practicality

### Draft decision direction
- Keep `2560 mm` as the validated baseline
- Treat `2816 mm` / `170 -> 85 mm` as the preferred candidate only if the airfoil family and tip structure close cleanly
- Keep `3072 mm` only as an upper-bound comparison case
- Reopen the wing chord law before freezing final span
- Use `AG35 -> AG36/37 -> AG38`, with `AG03` as the tip comparison rather than the assumed default
- Do not assume the trapezoidal area estimate is still valid
