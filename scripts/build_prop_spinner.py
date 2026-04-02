"""
Build all artifacts for propulsion off-shelf components:
  - Folding_Prop_11x6 (Aeronaut CAM Carbon 11x6 folding propeller)
  - Spinner_30mm (30mm aluminum cone spinner)

Generates:
  1. 2D technical drawings (DXF + PNG)
  2. COMPONENT_INFO.md
  3. 4-view renders from STEP

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_prop_spinner.py
"""
import os
import sys
import math
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ezdxf
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

BASE = "D:/Repos/aeroforge"


# ===================================================================
# DRAWING 1: Folding Prop 11x6
# ===================================================================

def draw_prop():
    """Create 2D technical drawing for Aeronaut CAM Carbon 11x6 folding prop."""
    print("\n=== Drawing: Folding Prop 11x6 ===")

    doc = setup_drawing(
        title="Folding Prop 11x6",
        drawing_number="PROP-003",
        subtitle="Aeronaut CAM Carbon 11x6 | 14g | 2 blades | 4mm shaft adapter",
        material="Off-shelf (carbon fiber blades, aluminum hub)",
        scale="1:1",
        mass="14g",
        status="APPROVED",
        sheet_size="A3",
        orientation_labels={},
    )
    msp = doc.modelspace()

    # Prop parameters
    blade_length = 139.7  # mm from hub center
    hub_w = 22.0
    hub_h = 8.0
    hub_l = 12.0
    shaft_d = 4.0
    blade_root_w = 18.0
    blade_max_w = 22.0
    blade_tip_w = 8.0
    total_span = blade_length * 2  # ~279mm

    outline_attr = {"layer": "OUTLINE"}
    center_attr = {"layer": "CENTERLINE", "linetype": "CENTER"}
    label_attr = {"layer": "TEXT"}
    dim_style = "AEROFORGE"

    # ── PLANFORM VIEW (deployed, top-down, main view) ──
    px, py = 200, 200
    msp.add_text("PLANFORM VIEW (deployed)", height=3.5,
                 dxfattribs=label_attr).set_placement((px - 60, py + 25))

    # Hub rectangle
    hl, hh = hub_w / 2, hub_h / 2
    msp.add_line((px - hl, py - hh), (px + hl, py - hh), dxfattribs=outline_attr)
    msp.add_line((px + hl, py - hh), (px + hl, py + hh), dxfattribs=outline_attr)
    msp.add_line((px + hl, py + hh), (px - hl, py + hh), dxfattribs=outline_attr)
    msp.add_line((px - hl, py + hh), (px - hl, py - hh), dxfattribs=outline_attr)

    # Shaft hole
    msp.add_circle((px, py), shaft_d / 2, dxfattribs=outline_attr)

    # Blade A (right side, +X) - tapered planform outline
    # Leading edge (wider side)
    blade_pts_le = [
        (px + hl, py + blade_root_w * 0.3),
        (px + hl + (blade_length - hl) * 0.3, py + blade_max_w * 0.3),
        (px + hl + (blade_length - hl) * 0.6, py + blade_max_w * 0.20),
        (px + hl + (blade_length - hl) * 0.85, py + blade_tip_w * 0.15),
        (px + blade_length, py),
    ]
    # Trailing edge
    blade_pts_te = [
        (px + hl, py - blade_root_w * 0.7),
        (px + hl + (blade_length - hl) * 0.3, py - blade_max_w * 0.7),
        (px + hl + (blade_length - hl) * 0.6, py - blade_max_w * 0.55),
        (px + hl + (blade_length - hl) * 0.85, py - blade_tip_w * 0.4),
        (px + blade_length, py),
    ]

    # Draw blade A outline (LE)
    for i in range(len(blade_pts_le) - 1):
        msp.add_line(blade_pts_le[i], blade_pts_le[i + 1], dxfattribs=outline_attr)
    # Draw blade A outline (TE)
    for i in range(len(blade_pts_te) - 1):
        msp.add_line(blade_pts_te[i], blade_pts_te[i + 1], dxfattribs=outline_attr)
    # Connect root
    msp.add_line(blade_pts_le[0], blade_pts_te[0], dxfattribs=outline_attr)

    # Blade B (left side, -X) - mirror
    for pts_list in [blade_pts_le, blade_pts_te]:
        mirrored = [(2 * px - p[0], p[1]) for p in pts_list]
        for i in range(len(mirrored) - 1):
            msp.add_line(mirrored[i], mirrored[i + 1], dxfattribs=outline_attr)
    # Connect root
    msp.add_line(
        (2 * px - blade_pts_le[0][0], blade_pts_le[0][1]),
        (2 * px - blade_pts_te[0][0], blade_pts_te[0][1]),
        dxfattribs=outline_attr,
    )

    # Centerline (span axis)
    msp.add_line((px - blade_length - 10, py), (px + blade_length + 10, py),
                 dxfattribs=center_attr)
    # Centerline (rotation axis)
    msp.add_line((px, py - 20), (px, py + 20), dxfattribs=center_attr)

    # Dimensions
    # Total diameter/span
    dim = msp.add_linear_dim(
        base=(px, py - blade_max_w * 0.7 - 15),
        p1=(px - blade_length, py), p2=(px + blade_length, py),
        dimstyle=dim_style)
    dim.render()

    # Blade length (one side)
    dim = msp.add_linear_dim(
        base=(px + blade_length / 2, py + blade_max_w * 0.3 + 12),
        p1=(px, py), p2=(px + blade_length, py),
        dimstyle=dim_style)
    dim.render()

    # Hub width
    dim = msp.add_linear_dim(
        base=(px, py + hh + 5),
        p1=(px - hl, py), p2=(px + hl, py),
        dimstyle=dim_style)
    dim.render()

    # ── SIDE VIEW (blade cross section / edge view) ──
    sx, sy = 80, 100
    msp.add_text("SIDE VIEW (edge)", height=3.5,
                 dxfattribs=label_attr).set_placement((sx - 15, sy + 15))

    # Hub side view
    hub_half_l = hub_l / 2
    msp.add_line((sx - hl, sy - hub_half_l), (sx + hl, sy - hub_half_l),
                 dxfattribs=outline_attr)
    msp.add_line((sx + hl, sy - hub_half_l), (sx + hl, sy + hub_half_l),
                 dxfattribs=outline_attr)
    msp.add_line((sx + hl, sy + hub_half_l), (sx - hl, sy + hub_half_l),
                 dxfattribs=outline_attr)
    msp.add_line((sx - hl, sy + hub_half_l), (sx - hl, sy - hub_half_l),
                 dxfattribs=outline_attr)

    # Blade edge (thin, with twist shown as tapering thickness)
    # Root thickness ~3mm, tip ~0.8mm
    root_t = 3.0
    tip_t = 0.8
    blade_end_x = sx + blade_length

    msp.add_line((sx + hl, sy + root_t / 2), (blade_end_x, sy + tip_t / 2),
                 dxfattribs=outline_attr)
    msp.add_line((sx + hl, sy - root_t / 2), (blade_end_x, sy - tip_t / 2),
                 dxfattribs=outline_attr)
    msp.add_line((blade_end_x, sy + tip_t / 2), (blade_end_x, sy - tip_t / 2),
                 dxfattribs=outline_attr)

    # Mirror for blade B
    msp.add_line((sx - hl, sy + root_t / 2), (sx - blade_length + hl, sy + tip_t / 2),
                 dxfattribs=outline_attr)
    msp.add_line((sx - hl, sy - root_t / 2), (sx - blade_length + hl, sy - tip_t / 2),
                 dxfattribs=outline_attr)
    msp.add_line((sx - blade_length + hl, sy + tip_t / 2),
                 (sx - blade_length + hl, sy - tip_t / 2),
                 dxfattribs=outline_attr)

    # Centerline
    msp.add_line((sx - blade_length - 5, sy), (blade_end_x + 5, sy),
                 dxfattribs=center_attr)

    # Hub height dimension
    dim = msp.add_linear_dim(
        base=(sx + hl + 8, sy),
        p1=(sx, sy - hub_half_l), p2=(sx, sy + hub_half_l),
        angle=90, dimstyle=dim_style)
    dim.render()

    # ── FOLDED VIEW (blades folded back) ──
    fx, fy = 280, 100
    msp.add_text("FOLDED VIEW (stowed)", height=3.5,
                 dxfattribs=label_attr).set_placement((fx - 15, fy + 25))

    # Hub (end view)
    msp.add_line((fx - hh, fy - hub_half_l), (fx + hh, fy - hub_half_l),
                 dxfattribs=outline_attr)
    msp.add_line((fx + hh, fy - hub_half_l), (fx + hh, fy + hub_half_l),
                 dxfattribs=outline_attr)
    msp.add_line((fx + hh, fy + hub_half_l), (fx - hh, fy + hub_half_l),
                 dxfattribs=outline_attr)
    msp.add_line((fx - hh, fy + hub_half_l), (fx - hh, fy - hub_half_l),
                 dxfattribs=outline_attr)

    # Blades folded along fuselage (both going same direction, -Z)
    fold_end = fy - blade_length + hl
    blade_folded_w = blade_max_w * 0.3  # visible width when folded
    for dx in [-2, 2]:
        msp.add_line((fx + dx - blade_folded_w / 2, fy - hub_half_l),
                     (fx + dx - 1, fold_end),
                     dxfattribs=outline_attr)
        msp.add_line((fx + dx + blade_folded_w / 2, fy - hub_half_l),
                     (fx + dx + 1, fold_end),
                     dxfattribs=outline_attr)
        msp.add_line((fx + dx - 1, fold_end), (fx + dx + 1, fold_end),
                     dxfattribs=outline_attr)

    # Folded length dimension
    dim = msp.add_linear_dim(
        base=(fx + hh + 12, fy),
        p1=(fx, fy + hub_half_l), p2=(fx, fold_end),
        angle=90, dimstyle=dim_style)
    dim.render()

    # ── NOTES ──
    notes_x, notes_y = 30, 55
    notes = [
        "NOTES:",
        "1. Off-shelf: Aeronaut CAM Carbon 11x6 folding prop",
        "2. Weight: 14g (both blades + hub hardware)",
        f"3. Diameter: {total_span:.0f}mm (11 inches)",
        "4. Pitch: 152mm (6 inches)",
        "5. Hub: standard yoke type, 8mm yoke spacing",
        "6. Shaft adapter: 4mm (for Sunnysky X2216)",
        "7. Blade material: Carbon fiber, CAM-optimized airfoil",
        "8. Blades fold flat against fuselage when motor stops",
        "9. Requires ESC brake function for folding",
    ]
    for i, note in enumerate(notes):
        h = 2.5 if i == 0 else 2.0
        msp.add_text(note, height=h, dxfattribs=label_attr).set_placement(
            (notes_x, notes_y - i * 4))

    out_path = os.path.join(
        BASE, "cad/components/propulsion/Folding_Prop_11x6/Folding_Prop_11x6_drawing.dxf"
    )
    save_dxf_and_png(doc, out_path)
    print(f"  Prop drawing: {out_path}")
    return out_path


# ===================================================================
# DRAWING 2: Spinner 30mm
# ===================================================================

def draw_spinner():
    """Create 2D technical drawing for 30mm aluminum spinner."""
    print("\n=== Drawing: Spinner 30mm ===")

    doc = setup_drawing(
        title="Spinner 30mm",
        drawing_number="PROP-004",
        subtitle="Aluminum cone spinner | 5g | 2 blade slots | 4mm shaft bore",
        material="Off-shelf (aluminum, polished)",
        scale="2:1",
        mass="5g",
        status="APPROVED",
        sheet_size="A3",
        orientation_labels={},
    )
    msp = doc.modelspace()

    # Spinner parameters
    diameter = 30.0
    radius = diameter / 2
    length = 28.0
    wall_t = 1.2
    shaft_d = 4.0
    set_screw_d = 3.0
    set_screw_z = 8.0
    slot_l = 18.0
    slot_w = 3.5
    slot_z_start = 3.0
    recess_d = 22.0
    recess_depth = 5.0

    outline_attr = {"layer": "OUTLINE"}
    center_attr = {"layer": "CENTERLINE", "linetype": "CENTER"}
    hidden_attr = {"layer": "HIDDEN", "linetype": "DASHED"}
    label_attr = {"layer": "TEXT"}
    dim_style = "AEROFORGE"

    # ── SIDE VIEW (cross-section through blade slots) ──
    sx, sy = 100, 180

    msp.add_text("SIDE VIEW (section through blade slots)", height=3.5,
                 dxfattribs=label_attr).set_placement((sx - 30, sy + radius + 20))

    # Outer cone profile (left side = LE of spinner)
    # Parabolic cone shape
    n_pts = 20
    cone_pts_top = []
    cone_pts_bot = []
    for i in range(n_pts + 1):
        z = length * i / n_pts
        if z < 2.0:
            r = radius
        else:
            # Parabolic taper
            t = (z - 2.0) / (length - 2.0)
            r = radius * (1.0 - t ** 0.7)
        cone_pts_top.append((sx + z, sy + r))
        cone_pts_bot.append((sx + z, sy - r))

    # Draw outer profile
    for i in range(len(cone_pts_top) - 1):
        msp.add_line(cone_pts_top[i], cone_pts_top[i + 1], dxfattribs=outline_attr)
        msp.add_line(cone_pts_bot[i], cone_pts_bot[i + 1], dxfattribs=outline_attr)

    # Rear face
    msp.add_line(cone_pts_top[0], cone_pts_bot[0], dxfattribs=outline_attr)

    # Inner wall (dashed, showing hollow interior)
    inner_pts_top = []
    inner_pts_bot = []
    for i in range(n_pts + 1):
        z = length * i / n_pts
        if z < wall_t:
            continue
        if z > length - wall_t:
            break
        if z < 2.0:
            r = radius - wall_t
        else:
            t = (z - 2.0) / (length - 2.0)
            r = (radius - wall_t) * (1.0 - t ** 0.7)
        if r < shaft_d / 2 + 0.5:
            break
        inner_pts_top.append((sx + z, sy + r))
        inner_pts_bot.append((sx + z, sy - r))

    for i in range(len(inner_pts_top) - 1):
        msp.add_line(inner_pts_top[i], inner_pts_top[i + 1], dxfattribs=hidden_attr)
        msp.add_line(inner_pts_bot[i], inner_pts_bot[i + 1], dxfattribs=hidden_attr)

    # Shaft bore (hidden)
    msp.add_line((sx, sy + shaft_d / 2), (sx + length * 0.8, sy + shaft_d / 2),
                 dxfattribs=hidden_attr)
    msp.add_line((sx, sy - shaft_d / 2), (sx + length * 0.8, sy - shaft_d / 2),
                 dxfattribs=hidden_attr)

    # Rear recess (hidden)
    msp.add_line((sx, sy + recess_d / 2), (sx + recess_depth, sy + recess_d / 2),
                 dxfattribs=hidden_attr)
    msp.add_line((sx, sy - recess_d / 2), (sx + recess_depth, sy - recess_d / 2),
                 dxfattribs=hidden_attr)
    msp.add_line((sx + recess_depth, sy + recess_d / 2),
                 (sx + recess_depth, sy - recess_d / 2),
                 dxfattribs=hidden_attr)

    # Blade slot (shown as gap in section)
    slot_z_mid = slot_z_start + slot_l / 2
    msp.add_line((sx + slot_z_start, sy + radius - 0.5),
                 (sx + slot_z_start, sy + radius + 2),
                 dxfattribs={"layer": "SECTION"})
    msp.add_line((sx + slot_z_start + slot_l, sy + radius - 0.5),
                 (sx + slot_z_start + slot_l, sy + radius + 2),
                 dxfattribs={"layer": "SECTION"})
    msp.add_text(f"SLOT {slot_l}x{slot_w}", height=1.8,
                 dxfattribs=label_attr).set_placement(
        (sx + slot_z_mid - 8, sy + radius + 3))

    # Set screw location
    ss_x = sx + set_screw_z
    msp.add_circle((ss_x, sy + radius), set_screw_d / 2,
                   dxfattribs={"layer": "SECTION"})
    msp.add_text(f"M{set_screw_d:.0f} set screw", height=1.8,
                 dxfattribs=label_attr).set_placement((ss_x + 3, sy + radius + 2))

    # Centerline
    msp.add_line((sx - 5, sy), (sx + length + 10, sy), dxfattribs=center_attr)

    # Dimensions
    # Diameter
    dim = msp.add_linear_dim(
        base=(sx - 8, sy),
        p1=(sx, sy - radius), p2=(sx, sy + radius),
        angle=90, dimstyle=dim_style)
    dim.render()

    # Length
    dim = msp.add_linear_dim(
        base=(sx + length / 2, sy - radius - 12),
        p1=(sx, sy), p2=(sx + length, sy),
        dimstyle=dim_style)
    dim.render()

    # Shaft bore diameter
    dim = msp.add_linear_dim(
        base=(sx + length * 0.5, sy + shaft_d / 2 + 5),
        p1=(sx + length * 0.5, sy - shaft_d / 2),
        p2=(sx + length * 0.5, sy + shaft_d / 2),
        angle=90, dimstyle=dim_style)
    dim.render()

    # ── REAR VIEW (looking from motor side) ──
    rx, ry = 300, 180
    msp.add_text("REAR VIEW", height=3.5, dxfattribs=label_attr).set_placement(
        (rx - 15, ry + radius + 12))

    # Outer circle
    msp.add_circle((rx, ry), radius, dxfattribs=outline_attr)

    # Shaft hole
    msp.add_circle((rx, ry), shaft_d / 2, dxfattribs=outline_attr)

    # Rear recess circle
    msp.add_circle((rx, ry), recess_d / 2, dxfattribs=hidden_attr)

    # Blade slots (2, diametrically opposite)
    for angle in [0, 180]:
        rad = math.radians(angle)
        cx = rx + (radius - wall_t / 2) * math.cos(rad)
        cy = ry + (radius - wall_t / 2) * math.sin(rad)
        # Draw slot as a small rectangle
        hw = slot_w / 2
        ht = wall_t * 1.5
        msp.add_line((cx - hw, cy - ht), (cx + hw, cy - ht), dxfattribs=outline_attr)
        msp.add_line((cx + hw, cy - ht), (cx + hw, cy + ht), dxfattribs=outline_attr)
        msp.add_line((cx + hw, cy + ht), (cx - hw, cy + ht), dxfattribs=outline_attr)
        msp.add_line((cx - hw, cy + ht), (cx - hw, cy - ht), dxfattribs=outline_attr)

    # Set screw (at 90 deg from blade slots)
    ss_cx = rx
    ss_cy = ry + radius
    msp.add_circle((ss_cx, ss_cy), set_screw_d / 2, dxfattribs=outline_attr)

    # Centerlines
    msp.add_line((rx - radius - 3, ry), (rx + radius + 3, ry), dxfattribs=center_attr)
    msp.add_line((rx, ry - radius - 3), (rx, ry + radius + 3), dxfattribs=center_attr)

    # ── NOTES ──
    notes_x, notes_y = 30, 120
    notes = [
        "NOTES:",
        "1. Off-shelf: Aeronaut-compatible aluminum spinner",
        "2. Weight: 5g",
        f"3. Diameter: {diameter:.0f}mm",
        f"4. Length: {length:.0f}mm",
        f"5. Shaft bore: {shaft_d:.0f}mm (matches Sunnysky X2216)",
        f"6. Set screw: M{set_screw_d:.0f}",
        "7. 2 blade slots, diametrically opposite",
        "8. Material: aluminum (silver finish)",
        "9. Mounts on motor shaft in front of prop hub",
    ]
    for i, note in enumerate(notes):
        h = 2.5 if i == 0 else 2.0
        msp.add_text(note, height=h, dxfattribs=label_attr).set_placement(
            (notes_x, notes_y - i * 4))

    out_path = os.path.join(
        BASE, "cad/components/propulsion/Spinner_30mm/Spinner_30mm_drawing.dxf"
    )
    save_dxf_and_png(doc, out_path)
    print(f"  Spinner drawing: {out_path}")
    return out_path


# ===================================================================
# COMPONENT_INFO.md
# ===================================================================

def write_prop_info():
    """Write COMPONENT_INFO.md for Folding Prop 11x6."""
    path = os.path.join(
        BASE, "cad/components/propulsion/Folding_Prop_11x6/COMPONENT_INFO.md"
    )
    content = """# Component: Folding Prop 11x6

## Description

Aeronaut CAM Carbon 11x6 folding propeller for F5J electric sailplane. Two carbon fiber blades with computer-optimized airfoil sections, mounted on a yoke-type aluminum hub with 4mm shaft adapter. Blades fold flat against the fuselage when the motor stops (requires ESC brake function).

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf folding propeller |
| Manufacturer | Aeronaut (Germany) |
| Model | CAM Carbon 11x6 |
| Mass | 14 g (both blades + hub hardware) |
| Diameter | 279mm (11 inches) |
| Pitch | 152mm (6 inches) |
| Blade length | 139.7mm (from hub center) |
| Blade count | 2 |
| Blade material | Carbon fiber (CAM-optimized) |
| Blade max width | ~22mm |
| Blade tip width | ~8mm |
| Hub type | Standard yoke, aluminum |
| Hub dimensions | 22 x 8 x 12 mm |
| Yoke spacing | 8mm |
| Shaft adapter | 4mm (fits Sunnysky X2216) |
| Rotation | CW (viewed from front) |
| Twist | 27 deg (root) to 11 deg (tip) |

## Coordinate System

- Origin = center of hub (blade pivot point)
- Z = motor axis, +Z toward pilot
- X = blade span axis when deployed
- Y = perpendicular to blade span

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| hub_center | (0, 0, 0) | Hub center / pivot point |
| hub_rear | (0, 0, -6) | Rear face (mounts against spinner) |
| blade_tip_a | (139.7, 0, 0) | Blade A tip |
| blade_tip_b | (-139.7, 0, 0) | Blade B tip |

## Assembly Notes

- Propeller mounts on motor shaft via M5 collet prop adapter
- Spinner covers the hub from the front
- Blades fold backward (toward tail) when motor stops
- ESC brake function MUST be enabled for proper folding
- Blade rotation: clockwise viewed from front
- Static thrust with Sunnysky X2216 880KV on 3S: ~1000g

## Performance (with Sunnysky X2216 880KV on 3S)

| Parameter | Value |
|-----------|-------|
| Static thrust | ~1000g |
| Current draw | ~16A |
| Power | ~178W |
| Thrust/weight ratio | 1.25:1 (at 800g AUW) |
| Recommended KV range | 810-1050 |

## Procurement

- Source: 3DJake.com (EU), Amazon.de
- Price: ~$15-18 USD / ~15 EUR (blades only)
- Lead time: 3-5 days (3DJake EU warehouse)
- Spare blades recommended: 2-3 sets
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Prop COMPONENT_INFO: {path}")


def write_spinner_info():
    """Write COMPONENT_INFO.md for Spinner 30mm."""
    path = os.path.join(
        BASE, "cad/components/propulsion/Spinner_30mm/COMPONENT_INFO.md"
    )
    content = """# Component: Spinner 30mm

## Description

30mm aluminum cone spinner compatible with Aeronaut folding propeller hubs. Streamlined cone shape reduces aerodynamic drag at the nose and covers the prop hub mechanism. Features two diametrically opposite blade slots, a 4mm central shaft bore, and an M3 set screw for shaft retention.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf aluminum spinner |
| Manufacturer | Aeronaut-compatible (generic) |
| Mass | 5 g |
| Diameter | 30.0 mm |
| Length | 28.0 mm |
| Wall thickness | 1.2 mm |
| Material | Aluminum (polished silver) |
| Shaft bore | 4.0 mm |
| Set screw | M3 (radial) |
| Blade slots | 2x 18.0 x 3.5 mm |
| Rear recess | 22mm dia x 5mm deep |

## Coordinate System

- Origin = center of rear face (mounts against motor/prop hub)
- Z = motor axis, +Z toward nose (forward)
- Spinner tip at Z = +28mm

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| rear_face | (0, 0, 0) | Mounts against prop hub |
| tip | (0, 0, 28) | Front tip of cone |
| shaft_center | (0, 0, 0) | Center of shaft bore |
| blade_slot_a | (12, 0, 12) | Center of blade slot A |
| blade_slot_b | (-12, 0, 12) | Center of blade slot B |

## Assembly Notes

- Spinner slides onto motor shaft from the front
- M3 set screw locks spinner to shaft (tighten gently)
- Blade slots align with folding prop blade root positions
- Rear recess clears the prop hub/yoke mechanism
- Spinner tip should align approximately with fuselage nose contour
- Gap between spinner rear face and motor bell: ~2mm

## Procurement

- Source: 3DJake.com (with Aeronaut prop), AliExpress
- Price: ~$8-12 USD / ~9 EUR (Aeronaut), ~$3-5 (generic aluminum)
- Lead time: 3-5 days (3DJake), 2-4 weeks (AliExpress)
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Spinner COMPONENT_INFO: {path}")


# ===================================================================
# RENDERS (4-view from STEP)
# ===================================================================

def render_component(step_path, render_dir, name):
    """Generate 4 standard views from a STEP file using OCP Viewer."""
    from build123d import import_step
    from ocp_vscode import show, save_screenshot, Camera

    VIEWS = {
        "isometric": Camera.ISO,
        "front": Camera.FRONT,
        "top": Camera.TOP,
        "right": Camera.RIGHT,
    }

    print(f"\n=== Renders: {name} ===")
    os.makedirs(render_dir, exist_ok=True)

    part = import_step(step_path)
    for vname, cam in VIEWS.items():
        show(part, names=[name], reset_camera=cam)
        time.sleep(2.0)
        path = os.path.join(render_dir, f"{vname}.png")
        save_screenshot(path)
        print(f"  Saved {path}")
        time.sleep(0.5)


# ===================================================================
# MAIN
# ===================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Building prop + spinner component artifacts")
    print("=" * 60)

    # 1. Technical drawings (DXF + PNG)
    draw_prop()
    draw_spinner()

    # 2. COMPONENT_INFO.md
    write_prop_info()
    write_spinner_info()

    # 3. Renders (4-view from STEP)
    prop_step = os.path.join(
        BASE, "cad/components/propulsion/Folding_Prop_11x6/Folding_Prop_11x6.step"
    )
    spinner_step = os.path.join(
        BASE, "cad/components/propulsion/Spinner_30mm/Spinner_30mm.step"
    )

    if os.path.exists(prop_step):
        render_component(
            prop_step,
            os.path.join(BASE, "cad/components/propulsion/Folding_Prop_11x6/renders"),
            "Folding Prop 11x6",
        )
    else:
        print(f"  WARNING: Prop STEP not found at {prop_step}")
        print("  Run model.py first to generate STEP.")

    if os.path.exists(spinner_step):
        render_component(
            spinner_step,
            os.path.join(BASE, "cad/components/propulsion/Spinner_30mm/renders"),
            "Spinner 30mm",
        )
    else:
        print(f"  WARNING: Spinner STEP not found at {spinner_step}")
        print("  Run model.py first to generate STEP.")

    print("\n" + "=" * 60)
    print("Done! All prop + spinner artifacts generated.")
    print("=" * 60)
