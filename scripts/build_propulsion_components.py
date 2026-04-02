"""
Build all artifacts for propulsion off-shelf components:
  1. 2D technical drawings (DXF + PNG)
  2. 4-view renders from STEP
  3. COMPONENT_INFO.md

Components:
  - Sunnysky X2216 880KV Brushless Motor
  - ZTW Spider 30A ESC

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_propulsion_components.py
"""
import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ezdxf
from src.core.dxf_utils import setup_drawing, save_dxf_and_png

BASE = "D:/Repos/aeroforge"


# ═══════════════════════════════════════════════════════════════
# DRAWING 1: Sunnysky X2216 880KV Motor
# ═══════════════════════════════════════════════════════════════

def draw_motor():
    """Create 2D technical drawing for Sunnysky X2216 880KV motor."""
    print("\n=== Drawing: Sunnysky X2216 880KV Motor ===")

    doc = setup_drawing(
        title="Sunnysky X2216 880KV Motor",
        drawing_number="PROP-001",
        subtitle="Brushless outrunner motor | 56g | 4mm shaft | 19mm bolt circle",
        material="Off-shelf (aluminum can, steel shaft)",
        scale="2:1",
        mass="56g",
        status="APPROVED",
        sheet_size="A3",
        orientation_labels={},  # No FWD/INBD for non-aero components
    )
    msp = doc.modelspace()

    # Motor parameters
    bell_od = 27.5
    bell_r = bell_od / 2
    bell_h = 26.0
    back_plate_od = 28.0
    back_plate_r = back_plate_od / 2
    back_plate_t = 2.5
    shaft_d = 4.0
    shaft_r = shaft_d / 2
    shaft_protrusion = 14.0
    xmount_size = 25.0
    xmount_t = 2.0
    bolt_circle = 19.0
    bolt_r = bolt_circle / 2
    hole_d = 3.0

    total_h = xmount_t + back_plate_t + bell_h + shaft_protrusion

    # ── SIDE VIEW (left side of sheet) ──
    # Origin for side view
    sx, sy = 60, 160
    label_attr = {"layer": "TEXT"}
    outline_attr = {"layer": "OUTLINE"}
    center_attr = {"layer": "CENTERLINE", "linetype": "CENTER"}
    dim_style = "AEROFORGE"

    msp.add_text("SIDE VIEW", height=3.5, dxfattribs=label_attr).set_placement(
        (sx - 10, sy + total_h / 2 + 15))

    # X-mount plate (bottom)
    xm_left = sx - xmount_size / 2
    xm_right = sx + xmount_size / 2
    xm_bot = sy
    xm_top = sy + xmount_t
    msp.add_line((xm_left, xm_bot), (xm_right, xm_bot), dxfattribs=outline_attr)
    msp.add_line((xm_right, xm_bot), (xm_right, xm_top), dxfattribs=outline_attr)
    msp.add_line((xm_right, xm_top), (xm_left, xm_top), dxfattribs=outline_attr)
    msp.add_line((xm_left, xm_top), (xm_left, xm_bot), dxfattribs=outline_attr)

    # Back plate
    bp_left = sx - back_plate_r
    bp_right = sx + back_plate_r
    bp_bot = xm_top
    bp_top = bp_bot + back_plate_t
    msp.add_line((bp_left, bp_bot), (bp_right, bp_bot), dxfattribs=outline_attr)
    msp.add_line((bp_right, bp_bot), (bp_right, bp_top), dxfattribs=outline_attr)
    msp.add_line((bp_right, bp_top), (bp_left, bp_top), dxfattribs=outline_attr)
    msp.add_line((bp_left, bp_top), (bp_left, bp_bot), dxfattribs=outline_attr)

    # Bell (can)
    bell_left = sx - bell_r
    bell_right = sx + bell_r
    bell_bot = bp_top
    bell_top = bell_bot + bell_h
    msp.add_line((bell_left, bell_bot), (bell_right, bell_bot), dxfattribs=outline_attr)
    msp.add_line((bell_right, bell_bot), (bell_right, bell_top), dxfattribs=outline_attr)
    msp.add_line((bell_right, bell_top), (bell_left, bell_top), dxfattribs=outline_attr)
    msp.add_line((bell_left, bell_top), (bell_left, bell_bot), dxfattribs=outline_attr)

    # Shaft
    shaft_left = sx - shaft_r
    shaft_right = sx + shaft_r
    shaft_bot = bell_top
    shaft_top = shaft_bot + shaft_protrusion
    msp.add_line((shaft_left, shaft_bot), (shaft_right, shaft_bot), dxfattribs=outline_attr)
    msp.add_line((shaft_right, shaft_bot), (shaft_right, shaft_top), dxfattribs=outline_attr)
    msp.add_line((shaft_right, shaft_top), (shaft_left, shaft_top), dxfattribs=outline_attr)
    msp.add_line((shaft_left, shaft_top), (shaft_left, shaft_bot), dxfattribs=outline_attr)

    # Centerline (motor axis)
    msp.add_line((sx, sy - 5), (sx, shaft_top + 8), dxfattribs=center_attr)

    # ── Dimensions (side view) ──
    # Total height
    dim = msp.add_linear_dim(
        base=(sx + back_plate_r + 18, sy),
        p1=(sx, sy), p2=(sx, shaft_top),
        angle=90, dimstyle=dim_style)
    dim.render()

    # Bell height
    dim = msp.add_linear_dim(
        base=(sx + bell_r + 8, bell_bot),
        p1=(sx, bell_bot), p2=(sx, bell_top),
        angle=90, dimstyle=dim_style)
    dim.render()

    # Bell diameter
    dim = msp.add_linear_dim(
        base=(sx, bell_top + 5),
        p1=(bell_left, bell_top), p2=(bell_right, bell_top),
        dimstyle=dim_style)
    dim.render()

    # Shaft protrusion
    dim = msp.add_linear_dim(
        base=(sx - bell_r - 8, shaft_bot),
        p1=(sx, shaft_bot), p2=(sx, shaft_top),
        angle=90, dimstyle=dim_style)
    dim.render()

    # Shaft diameter
    dim = msp.add_linear_dim(
        base=(sx, shaft_top + 12),
        p1=(shaft_left, shaft_top), p2=(shaft_right, shaft_top),
        dimstyle=dim_style)
    dim.render()

    # ── FRONT VIEW (right side - looking at mounting face) ──
    fx, fy = 200, 160
    msp.add_text("FRONT VIEW (mount face)", height=3.5, dxfattribs=label_attr).set_placement(
        (fx - 25, fy + back_plate_r + 15))

    # Back plate circle
    msp.add_circle((fx, fy), back_plate_r, dxfattribs=outline_attr)

    # X-mount square outline
    xm_half = xmount_size / 2
    msp.add_line((fx - xm_half, fy - xm_half), (fx + xm_half, fy - xm_half), dxfattribs=outline_attr)
    msp.add_line((fx + xm_half, fy - xm_half), (fx + xm_half, fy + xm_half), dxfattribs=outline_attr)
    msp.add_line((fx + xm_half, fy + xm_half), (fx - xm_half, fy + xm_half), dxfattribs=outline_attr)
    msp.add_line((fx - xm_half, fy + xm_half), (fx - xm_half, fy - xm_half), dxfattribs=outline_attr)

    # Shaft center bore
    msp.add_circle((fx, fy), shaft_r + 0.5, dxfattribs=outline_attr)

    # M3 mounting holes on bolt circle (cross pattern)
    for angle in [0, 90, 180, 270]:
        hx = fx + bolt_r * math.cos(math.radians(angle))
        hy = fy + bolt_r * math.sin(math.radians(angle))
        msp.add_circle((hx, hy), hole_d / 2, dxfattribs=outline_attr)

    # Bolt circle (dashed)
    msp.add_circle((fx, fy), bolt_r, dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"})

    # Centerlines
    msp.add_line((fx - back_plate_r - 3, fy), (fx + back_plate_r + 3, fy), dxfattribs=center_attr)
    msp.add_line((fx, fy - back_plate_r - 3), (fx, fy + back_plate_r + 3), dxfattribs=center_attr)

    # Dimensions: bolt circle
    dim = msp.add_linear_dim(
        base=(fx, fy - back_plate_r - 10),
        p1=(fx - bolt_r, fy), p2=(fx + bolt_r, fy),
        dimstyle=dim_style)
    dim.render()

    # ── TOP VIEW (below side view) ──
    tx, ty = 60, 80
    msp.add_text("TOP VIEW", height=3.5, dxfattribs=label_attr).set_placement(
        (tx - 10, ty + bell_r + 8))

    # Bell circle (top of motor)
    msp.add_circle((tx, ty), bell_r, dxfattribs=outline_attr)
    # Shaft circle
    msp.add_circle((tx, ty), shaft_r, dxfattribs=outline_attr)
    # Centerlines
    msp.add_line((tx - bell_r - 3, ty), (tx + bell_r + 3, ty), dxfattribs=center_attr)
    msp.add_line((tx, ty - bell_r - 3), (tx, ty + bell_r + 3), dxfattribs=center_attr)

    # ── NOTES ──
    notes_x, notes_y = 140, 70
    notes = [
        "NOTES:",
        "1. Off-shelf component - Sunnysky X2216 880KV",
        "2. Weight: 56g (with cables)",
        "3. Shaft: 4.0mm diameter, steel",
        "4. Mounting: 4x M3 on 19mm bolt circle",
        "5. KV: 880 RPM/V | Max current: 18A",
        "6. Max power: 250W",
        "7. 3 motor wires (banana connectors)",
    ]
    for i, note in enumerate(notes):
        h = 2.5 if i == 0 else 2.0
        msp.add_text(note, height=h, dxfattribs=label_attr).set_placement(
            (notes_x, notes_y - i * 4))

    out_path = os.path.join(
        BASE, "cad/components/propulsion/Sunnysky_X2216_Motor/Sunnysky_X2216_Motor_drawing.dxf"
    )
    save_dxf_and_png(doc, out_path)
    print(f"  Motor drawing: {out_path}")
    return out_path


# ═══════════════════════════════════════════════════════════════
# DRAWING 2: ZTW Spider 30A ESC
# ═══════════════════════════════════════════════════════════════

def draw_esc():
    """Create 2D technical drawing for ZTW Spider 30A ESC."""
    print("\n=== Drawing: ZTW Spider 30A ESC ===")

    doc = setup_drawing(
        title="ZTW Spider 30A ESC",
        drawing_number="PROP-002",
        subtitle="30A ESC with 5A switching BEC | 16g | Heat-shrink wrapped PCB",
        material="Off-shelf (PCB + heat shrink)",
        scale="2:1",
        mass="16g",
        status="APPROVED",
        sheet_size="A3",
        orientation_labels={},
    )
    msp = doc.modelspace()

    # ESC parameters
    pcb_l = 45.0
    pcb_w = 24.0
    pcb_h = 11.0
    wire_stub = 12.0

    outline_attr = {"layer": "OUTLINE"}
    center_attr = {"layer": "CENTERLINE", "linetype": "CENTER"}
    label_attr = {"layer": "TEXT"}
    dim_style = "AEROFORGE"

    # ── TOP VIEW (plan view, XY plane) ──
    sx, sy = 80, 200
    msp.add_text("TOP VIEW", height=3.5, dxfattribs=label_attr).set_placement(
        (sx - 10, sy + pcb_w / 2 + 12))

    # ESC body rectangle
    hl, hw = pcb_l / 2, pcb_w / 2
    msp.add_line((sx - hl, sy - hw), (sx + hl, sy - hw), dxfattribs=outline_attr)
    msp.add_line((sx + hl, sy - hw), (sx + hl, sy + hw), dxfattribs=outline_attr)
    msp.add_line((sx + hl, sy + hw), (sx - hl, sy + hw), dxfattribs=outline_attr)
    msp.add_line((sx - hl, sy + hw), (sx - hl, sy - hw), dxfattribs=outline_attr)

    # Motor wire stubs (+X end, 3 wires)
    for i in range(3):
        wy = sy + (i - 1) * 5.0
        msp.add_line((sx + hl, wy), (sx + hl + wire_stub, wy), dxfattribs={"layer": "SPAR"})

    # Battery wires (-X end, 2 thick)
    for dy in [3.0, -3.0]:
        msp.add_line((sx - hl, sy + dy), (sx - hl - wire_stub, sy + dy),
                     dxfattribs={"layer": "DIMENSION"})  # red

    # Signal wire (-X end)
    msp.add_line((sx - hl, sy + 8), (sx - hl - wire_stub, sy + 8),
                 dxfattribs={"layer": "ORIENTATION"})

    # Wire labels
    msp.add_text("Motor (3x)", height=1.8, dxfattribs=label_attr).set_placement(
        (sx + hl + wire_stub + 2, sy - 1))
    msp.add_text("Batt (+/-)", height=1.8, dxfattribs=label_attr).set_placement(
        (sx - hl - wire_stub - 20, sy - 1))
    msp.add_text("BEC/Sig", height=1.8, dxfattribs=label_attr).set_placement(
        (sx - hl - wire_stub - 18, sy + 7))

    # Centerlines
    msp.add_line((sx - hl - wire_stub - 5, sy), (sx + hl + wire_stub + 5, sy),
                 dxfattribs=center_attr)
    msp.add_line((sx, sy - hw - 3), (sx, sy + hw + 3), dxfattribs=center_attr)

    # Dimensions
    dim = msp.add_linear_dim(
        base=(sx, sy - hw - 10),
        p1=(sx - hl, sy), p2=(sx + hl, sy),
        dimstyle=dim_style)
    dim.render()

    dim = msp.add_linear_dim(
        base=(sx + hl + 20, sy),
        p1=(sx, sy - hw), p2=(sx, sy + hw),
        angle=90, dimstyle=dim_style)
    dim.render()

    # ── SIDE VIEW (XZ plane, below top view) ──
    ex, ey = 80, 130
    msp.add_text("SIDE VIEW", height=3.5, dxfattribs=label_attr).set_placement(
        (ex - 10, ey + pcb_h / 2 + 10))

    hh = pcb_h / 2
    # Body rectangle (side)
    msp.add_line((ex - hl, ey - hh), (ex + hl, ey - hh), dxfattribs=outline_attr)
    msp.add_line((ex + hl, ey - hh), (ex + hl, ey + hh), dxfattribs=outline_attr)
    msp.add_line((ex + hl, ey + hh), (ex - hl, ey + hh), dxfattribs=outline_attr)
    msp.add_line((ex - hl, ey + hh), (ex - hl, ey - hh), dxfattribs=outline_attr)

    # Centerline
    msp.add_line((ex - hl - 5, ey), (ex + hl + 5, ey), dxfattribs=center_attr)

    # Height dimension
    dim = msp.add_linear_dim(
        base=(ex - hl - 10, ey),
        p1=(ex, ey - hh), p2=(ex, ey + hh),
        angle=90, dimstyle=dim_style)
    dim.render()

    # ── END VIEW (looking from motor end) ──
    endx, endy = 240, 200
    msp.add_text("END VIEW", height=3.5, dxfattribs=label_attr).set_placement(
        (endx - 10, endy + hw + 10))

    # Rectangle
    msp.add_line((endx - hw, endy - hh), (endx + hw, endy - hh), dxfattribs=outline_attr)
    msp.add_line((endx + hw, endy - hh), (endx + hw, endy + hh), dxfattribs=outline_attr)
    msp.add_line((endx + hw, endy + hh), (endx - hw, endy + hh), dxfattribs=outline_attr)
    msp.add_line((endx - hw, endy + hh), (endx - hw, endy - hh), dxfattribs=outline_attr)

    # Centerlines
    msp.add_line((endx - hw - 3, endy), (endx + hw + 3, endy), dxfattribs=center_attr)
    msp.add_line((endx, endy - hh - 3), (endx, endy + hh + 3), dxfattribs=center_attr)

    # ── NOTES ──
    notes_x, notes_y = 200, 130
    notes = [
        "NOTES:",
        "1. Off-shelf component - ZTW Spider 30A",
        "2. Weight: 16g (with wires)",
        "3. Current rating: 30A continuous",
        "4. BEC: 5V / 5A switching",
        "5. Input: 2-4S LiPo (7.4-14.8V)",
        "6. Motor wires: 3x 200mm",
        "7. Battery wires: 150mm (XT60)",
        "8. Signal: 200mm (JR/Futaba)",
        "9. Body: heat-shrink wrapped PCB",
    ]
    for i, note in enumerate(notes):
        h = 2.5 if i == 0 else 2.0
        msp.add_text(note, height=h, dxfattribs=label_attr).set_placement(
            (notes_x, notes_y - i * 4))

    out_path = os.path.join(
        BASE, "cad/components/propulsion/ZTW_Spider_30A_ESC/ZTW_Spider_30A_ESC_drawing.dxf"
    )
    save_dxf_and_png(doc, out_path)
    print(f"  ESC drawing: {out_path}")
    return out_path


# ═══════════════════════════════════════════════════════════════
# RENDERS (4-view from STEP)
# ═══════════════════════════════════════════════════════════════

def render_component(step_path, render_dir, name):
    """Generate 4 standard views from a STEP file using OCP Viewer."""
    import time
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


# ═══════════════════════════════════════════════════════════════
# COMPONENT_INFO.md
# ═══════════════════════════════════════════════════════════════

def write_motor_info():
    """Write COMPONENT_INFO.md for Sunnysky X2216 motor."""
    path = os.path.join(
        BASE, "cad/components/propulsion/Sunnysky_X2216_Motor/COMPONENT_INFO.md"
    )
    content = """# Component: Sunnysky X2216 880KV Motor

## Description

Sunnysky X2216 880KV brushless outrunner motor for electric sailplane propulsion. Lightweight aluminum construction with 4mm steel shaft. Suitable for 2-3S LiPo operation on sailplanes in the 700-1000g AUW range.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf brushless outrunner |
| Manufacturer | Sunnysky |
| Model | X2216 880KV |
| Mass | 56 g |
| KV rating | 880 RPM/V |
| Max current | 18 A |
| Max power | 250 W |
| Input voltage | 2-3S LiPo (7.4-11.1V) |
| Stator diameter | 28.0 mm |
| Bell (can) diameter | 27.5 mm |
| Bell height | 26.0 mm |
| Shaft diameter | 4.0 mm |
| Shaft protrusion | 14.0 mm |
| Overall length (with shaft) | ~42.5 mm |
| Mounting | 4x M3 on 19mm bolt circle (cross pattern) |
| X-mount plate | 25 x 25 x 2 mm |
| Prop adapter | M5 collet type |

## Coordinate System

- Origin = center of mounting face (back plate rear)
- Z = motor axis, +Z toward propeller
- X-mount plate at Z < 0 (rear)
- Shaft tip at Z = +42.5mm

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| mount_face | (0, 0, -2) | Firewall attachment |
| shaft_tip | (0, 0, 42.5) | Propeller mounting |
| shaft_prop | (0, 0, 30.5) | Prop adapter position |
| mount_fr | (9.5, 0, -1) | Front-right M3 hole |
| mount_fl | (-9.5, 0, -1) | Front-left M3 hole |
| mount_br | (0, 9.5, -1) | Back-right M3 hole |
| mount_bl | (0, -9.5, -1) | Back-left M3 hole |

## Assembly Notes

- Motor mounts to the fuselage nose firewall via the X-mount plate
- 4x M3 bolts through the cross-pattern mounting holes
- Propeller attaches to the 4mm shaft via an M5 collet adapter
- 3 motor wires connect to ESC (any order, swap 2 to reverse rotation)
- Ensure adequate cooling airflow around the bell

## Procurement

- Source: AliExpress / HobbyKing / Banggood
- Price: ~$12-15 USD
- Lead time: 2-4 weeks (AliExpress)
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Motor COMPONENT_INFO: {path}")


def write_esc_info():
    """Write COMPONENT_INFO.md for ZTW Spider 30A ESC."""
    path = os.path.join(
        BASE, "cad/components/propulsion/ZTW_Spider_30A_ESC/COMPONENT_INFO.md"
    )
    content = """# Component: ZTW Spider 30A ESC

## Description

ZTW Spider 30A electronic speed controller with integrated 5A switching BEC. Compact heat-shrink wrapped PCB design suitable for sailplane and sport electric applications. Provides reliable motor control and regulated 5V power for servos and receiver.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf ESC with switching BEC |
| Manufacturer | ZTW |
| Model | Spider 30A |
| Mass | 16 g (with wires) |
| Current rating | 30 A continuous |
| Burst current | 40 A (10s) |
| BEC output | 5V / 5A switching |
| Input voltage | 2-4S LiPo (7.4-14.8V) |
| Body length | 45.0 mm |
| Body width | 24.0 mm |
| Body height | 11.0 mm |
| Motor wires | 3x 200mm (silicone) |
| Battery wires | 150mm with XT60 connector |
| Signal wire | 200mm with JR/Futaba connector |
| Programming | Yes (via transmitter stick) |

## Coordinate System

- Origin = center of PCB body
- X = length axis (motor wires exit +X, battery/signal exit -X)
- Y = width axis
- Z = thickness axis

## Joints

| Joint | Location | Purpose |
|-------|----------|---------|
| battery_wire | (-22.5, 0, 0) | Battery XT60 connection |
| signal_wire | (-22.5, 8, 0) | Receiver signal input |
| motor_wire_a | (22.5, -5, 0) | Motor phase A |
| motor_wire_b | (22.5, 0, 0) | Motor phase B |
| motor_wire_c | (22.5, 5, 0) | Motor phase C |
| mount_top | (0, 0, 5.5) | Top face (tape/strap mount) |
| mount_bottom | (0, 0, -5.5) | Bottom face mount |

## Assembly Notes

- ESC mounts inside the fuselage pod via double-sided tape or Velcro strap
- Position near the CG to minimize wiring length
- Battery XT60 connects to battery lead
- Motor wires connect to Sunnysky X2216 (any order; swap 2 to reverse)
- Signal wire connects to receiver throttle channel
- BEC powers all servos and receiver (no separate BEC needed)
- Ensure heat dissipation: do not fully enclose in foam

## Procurement

- Source: AliExpress / HobbyKing / Banggood
- Price: ~$8-12 USD
- Lead time: 2-4 weeks (AliExpress)
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ESC COMPONENT_INFO: {path}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("Building propulsion component artifacts")
    print("=" * 60)

    # 1. Technical drawings (DXF + PNG)
    draw_motor()
    draw_esc()

    # 2. COMPONENT_INFO.md
    write_motor_info()
    write_esc_info()

    # 3. Renders (4-view from STEP)
    motor_step = os.path.join(
        BASE, "cad/components/propulsion/Sunnysky_X2216_Motor/Sunnysky_X2216_Motor.step"
    )
    esc_step = os.path.join(
        BASE, "cad/components/propulsion/ZTW_Spider_30A_ESC/ZTW_Spider_30A_ESC.step"
    )

    if os.path.exists(motor_step):
        render_component(
            motor_step,
            os.path.join(BASE, "cad/components/propulsion/Sunnysky_X2216_Motor/renders"),
            "Sunnysky X2216 880KV Motor",
        )
    else:
        print(f"  WARNING: Motor STEP not found at {motor_step}")
        print("  Run model.py first to generate STEP.")

    if os.path.exists(esc_step):
        render_component(
            esc_step,
            os.path.join(BASE, "cad/components/propulsion/ZTW_Spider_30A_ESC/renders"),
            "ZTW Spider 30A ESC",
        )
    else:
        print(f"  WARNING: ESC STEP not found at {esc_step}")
        print("  Run model.py first to generate STEP.")

    print("\n" + "=" * 60)
    print("Done! All propulsion component artifacts generated.")
    print("=" * 60)
