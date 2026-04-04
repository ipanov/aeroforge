# Assembly: Iva_Aeroforge

## Description
Top-level aircraft assembly for the Iva F5J glider. This is the root
integration artifact above wing, fuselage, and empennage subassemblies.

This assembly is not a wrapper. It is the controlling parent object for:
- aircraft datum
- wing stationing
- tail stationing
- whole-aircraft packaging
- top-down layout decisions

## Bill of Materials
| # | Component | Qty | Source |
|---|-----------|-----|--------|
| 1 | Wing_Assembly | 1 | `cad/assemblies/wing/Wing_Assembly/` |
| 2 | Fuselage_Assembly | 1 | `cad/assemblies/fuselage/Fuselage_Assembly/` |
| 3 | HStab_Assembly | 1 | `cad/assemblies/empennage/HStab_Assembly/` |
| 4 | Battery + XT60 | 1 | envelope only in parent drawings |
| 5 | Receiver | 1 | envelope only in parent drawings |
| 6 | Servos / propulsion / wiring | 1 set | envelope only in parent drawings |

## Assembly Constraints
| Constraint | Component A | Component B | Type |
|-----------|------------|------------|------|
| 1 | Wing_Assembly | Fuselage_Assembly | mate / datum alignment |
| 2 | Fuselage_Assembly | HStab_Assembly | coaxial / tail-axis placement |
| 3 | Battery + XT60 | Fuselage_Assembly | containment |
| 4 | Receiver | Fuselage_Assembly | containment |

## Assembly Order
1. Set aircraft datum at nose tip.
2. Position fuselage centerline and wing saddle at X=260 mm.
3. Attach wing assembly to the wing saddle and spar tunnel datum.
4. Attach HStab assembly at the fuselage tail datum.
5. Place battery, receiver, ESC, and wiring inside fuselage bays.
6. Run collision and containment validation before any mesh or render export.

## Specifications
| Parameter | Value |
|-----------|-------|
| Wingspan | 2560 mm |
| Fuselage length | 1046 mm |
| Wing LE station | 260 mm from nose |
| HStab pivot station | 911 mm from nose |
| Integration status | Wing and fuselage remain WIP; HStab is mostly complete |
| CG window | 30-35% MAC target |
| Parent-drawing policy | Off-the-shelf components shown as envelopes only |

## Drawing Approval
- Date: 2026-04-02
- Approved by: workspace integration review
- Drawing file: `Iva_Aeroforge_drawing.dxf`

## Parent-Drawing Scope

The aircraft parent drawing owns:
- aircraft geometry
- interfaces between subassemblies
- packaging zones
- containment and routing references

The aircraft parent drawing does not own:
- vendor-part internal geometry for battery, motor, ESC, receiver, servos, spinner, or propeller
