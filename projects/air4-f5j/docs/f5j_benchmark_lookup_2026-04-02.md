# F5J Benchmark Lookup Pack

Purpose: give AeroForge a grounded external benchmark set before aero and structural rounds change whole-aircraft geometry.

Status: strategic reference only. We are not copying any single aircraft. We are extracting repeated patterns, then deciding where 3D printing can outperform conventional composite practice.

## Rules / Competition Context

- FAI Sporting Code Volume F5 confirms that `F5J` is the active class for electric powered thermal duration gliders.
  Source: https://www.fai.org/sites/default/files/sc4_vol_f5_electric_24_v2.pdf
- FAI confirms the `2025 F5J World Championships` were held in Cordoba, Argentina from `2-8 March 2025`.
  Source: https://www.fai.org/news/argentina-welcomes-2025-fai-f5j-world-championships-electric-powered-thermal-duration-gliders
- FAI confirms the `2025 senior world champion` was `Joe Wurts` and the `junior world champion` was `John Bradley`.
  Source: https://www.fai.org/sites/default/files/fai_press_release_f5j-worlds-winners_11mar2025.pdf

## Benchmark Aircraft

### NAN Xplorer 2 F5J

- Source: https://nanmodels.com/models/xplorer-2-f5j/
- Key signals:
  - explicitly positioned as a high-performance competition F5J aircraft
  - NAN states later upgrades included a `new slimmer fuselage` to reduce drag
  - same tail and wing design lineage as a successful soaring platform, with F5J-specific weight and fuselage refinement
- AeroForge takeaway:
  - fuselage drag reduction is a first-class design driver, not a cosmetic afterthought
  - parent-sheet fuselage OML should stay refined and slender

### NAN Explorer Q

- Source: https://nanmodels.com/models/explorer-q/
- Key signals:
  - modular family with multiple span options
  - emphasizes transport / packaging flexibility without giving up high-end soaring identity
- AeroForge takeaway:
  - modularity is normal in top-tier gliders
  - our parent geometry should preserve clean interfaces for future variants instead of hard-coding a dead-end layout

### Samba Prestige 3PK F5J

- Source: https://f3j.com/pages/prestige-3pk-f5j
- Supporting setup source: https://f3j.com/pages/prestige-3pk-settings
- Key signals:
  - current production / competition presence
  - multiple layup stiffness bands for different conditions
  - X-tail and V-tail options exist in the same family
  - positioned as versatile across low starts and stronger air
- AeroForge takeaway:
  - structural tuning by condition is part of elite F5J practice
  - we should separate baseline geometry from later stiffness / layup variants

### RCRCM Eagle F5J

- Source: https://www.rcrcm.com/products/eagle-f5j
- Key signals:
  - explicit `full-house` configuration: ailerons, flaps, rudder, elevator
  - published span / length / area / CG / channel expectations
  - packaged as a competition-format F5J glider rather than a simple sport ship
- AeroForge takeaway:
  - our drawings must keep reading as a full-house glider
  - exaggerated two-channel-style front-view dihedral cues are the wrong visual language

## Repeated External Patterns

Patterns that repeat across current official sources:

- long, slender fuselage pods with low frontal area
- full-house control architecture
- clean, refined tail geometry rather than blunt triangular fins
- modular / configurable product families
- different stiffness or weight variants for conditions
- strong emphasis on drag reduction and finish quality

## Packaging Benchmark

- Samba's `Prestige 2PK Instructions` give a directly useful packaging reference for an F5J-class fuselage:
  - the nose-cone back part can be shortened to adjust CG
  - the receiver is installed in a slot under the wing
  - the forward fuselage volume is reserved for motor / regulator / battery packaging
  Source: https://old.f3j.com/prestige2pk/prestigeinstructions_txt_only.pdf
- AeroForge takeaway:
  - stop crowding the receiver into the ESC bay
  - show the LiPo as a forward-pod sliding mass, not as a spinner-tip mass
  - keep the receiver and fuselage servos in the center-wing / post-wing zone where wiring and antenna routing are cleaner

## Working Rules For AeroForge

Before any new aero or structural proposal changes whole-aircraft geometry, require:

1. one competition / rules source
2. two to five benchmark aircraft sources
3. one short note explaining why the proposed change is not just a copy

## Immediate Design Implications For Iva

- keep the aircraft sheet geometry-first
- keep the glider visually in the elite F5J family: slender pod, refined fin, full-house wing language
- use a homologous superelliptic family across wing, fin, and H-stab
- avoid cartoon triangle fins and blunt placeholder tips
- keep off-the-shelf hardware primarily on subsystem sheets, not as clutter on the aircraft parent sheet

## Open Questions For Later Rounds

- which competitor families are closest to our intended performance envelope versus only our intended look
- where 3D-printed structure can beat molded practice on packaging or internal integration
- whether our final wingtip, fin-height, and fuselage-blend choices should bias toward low-drag purity or broader condition tolerance
