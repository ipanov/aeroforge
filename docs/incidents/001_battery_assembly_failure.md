# Incident Report #001: Battery Assembly Geometry Failures

**Date**: 2026-03-28
**Component**: Battery Assembly (src/cad/hardware/battery.py)
**Severity**: High - fundamental workflow failure

## What Happened

The first Build123d component (3S 1300mAh LiPo battery with XT60 connector) was built
with multiple geometry errors. The assembly was generated without any visual validation
or reference image comparison.

## Identified Failures

### 1. XT60 Connector Orientation Wrong
- **Problem**: XT60 connector is oriented with pins pointing UP (Z-axis). In reality,
  XT60 pins point FORWARD (away from battery, along X-axis) inline with the power leads.
- **Root cause**: No reference image was consulted. The connector was placed as a
  standalone box without considering how it physically connects to the leads.
- **Impact**: Connector appears perpendicular to the wires - physically impossible.

### 2. XT60 Position Disconnected from Leads
- **Problem**: XT60 is at X=-135 to -119, but power leads end at X=-119. The connector
  body floats at the end of the leads but the pins point upward instead of mating with
  the wire ends.
- **Root cause**: Manual offset positioning (`Location((-80-8, 0, 0))`) without
  constraint-based alignment. No "attach pin to wire end" constraint.

### 3. Power Leads Exit Wrong Location
- **Problem**: Leads exit from the center of the battery face (Z=0). In reality, power
  leads exit from the TOP of one end of the battery, with some slack/loop.
- **Root cause**: Hardcoded origin points without referencing actual battery anatomy.

### 4. Balance Lead Position/Direction Wrong
- **Problem**: Balance lead exits from the top-rear of the battery and curves upward/backward.
  In reality, the balance lead (thin multi-wire ribbon) typically exits from the SAME END
  as the power leads, often right next to them, or from the side of the battery.
- **Root cause**: Guessed the exit point without looking at reference photos.

### 5. Balance Lead is Oversimplified
- **Problem**: Modeled as a single 4mm cylinder. Real balance leads are 4 or 5 thin wires
  (22AWG) in a flat ribbon cable, terminating in a white JST-XH connector.
- **Root cause**: Approximation without research.

### 6. Battery Shape Too Simple
- **Problem**: The battery is just a rounded box. Real LiPo packs have visible cell
  structure under the heat-shrink, with a label/sticker on one face, and the heat-shrink
  wraps tighter at the edges creating a distinctive shape.
- **Acceptable for now**: For CG/bay sizing, a simplified box is adequate. But for a
  project that claims "complexity is free," this is below standard.

### 7. No Solder Cups on XT60
- **Problem**: The XT60 model shows pins sticking out but no solder cups on the back
  where the wires attach. Real XT60 connectors have tubular solder cups that the wire
  insulation slides into.
- **Root cause**: Incomplete modeling of the connector.

## Root Cause Analysis

### Primary Root Cause: No Visual Validation in Workflow

The component was generated entirely from dimension tables and code, with **zero visual
reference**. At no point did the workflow:

1. Look at a reference photo of the actual component
2. Capture a screenshot of the generated geometry
3. Compare the generated geometry against the reference
4. Validate spatial relationships between sub-parts

### Secondary Root Cause: Manual Positioning Instead of Constraints

All sub-parts were positioned using hardcoded `Location()` offsets:
```python
xt60.moved(Location((-SPEC.length / 2 - 80 - 8, 0, 0)))  # Guessed offset
```

This is exactly the anti-pattern our Assembly system was designed to prevent. The battery
assembly should use:
- Joint definitions (wire end connects to connector solder cup)
- Constraint-based positioning (connector axis aligned with wire axis)
- Reference geometry (exit point on battery body)

### Tertiary Root Cause: No Reference Image Research

For off-the-shelf components, there are thousands of photos available online. The workflow
should have:
1. Searched for "3S 1300mAh LiPo battery" images
2. Identified key features: wire exit point, connector orientation, balance lead routing
3. Used these as design constraints BEFORE writing any geometry code

## Corrective Actions

### Immediate Fixes
1. Research reference images for every off-the-shelf component before modeling
2. Fix battery model with correct wire exit points, connector orientation, balance routing
3. Add visual validation step to the workflow

### Workflow Changes Required

#### MANDATORY: Visual Validation Protocol
Add to CLAUDE.md:

For EVERY Build123d component or assembly:
1. **Before coding**: Search for reference images of the real component
2. **After generating**: Capture OCP viewer screenshot
3. **Compare**: Check generated geometry against reference
4. **Validate positions**: Log bounding boxes and verify spatial relationships
5. **Fix before committing**: Never commit unvalidated geometry

#### MANDATORY: Use Assembly Constraints
Stop using manual `Location()` offsets for multi-part assemblies.
Use the Assembly system with proper joint definitions:
- `RigidJoint` for fixed connections (connector to wire end)
- Alignment constraints (axes must be parallel/coincident)
- Reference points on parent geometry (wire exit face on battery)

#### Add Visual Validation Tests
Create automated tests that:
- Check sub-part bounding boxes don't overlap incorrectly
- Verify connector axes are aligned with their mating geometry
- Ensure wire start points match parent exit points
- Compare key dimensions against datasheet values

## Lessons Learned

1. **Dimensional accuracy != geometric accuracy.** The battery box was the right SIZE
   but everything was in the wrong PLACE and ORIENTATION.
2. **Off-the-shelf components need reference photos, not just datasheets.** Datasheets
   give dimensions but not spatial relationships.
3. **Manual positioning is fragile.** This is exactly why we built the constraint-based
   Assembly system - and then didn't use it.
4. **Visual validation is non-negotiable.** The system claimed "every detail matters"
   but didn't look at what it produced.
