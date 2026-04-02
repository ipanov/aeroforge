"""Build servo component artifacts: DXF drawings, PNGs, STEP files, renders, COMPONENT_INFO.

Generates all required files for:
  - JX_PDI_1109MG_Servo (aileron/elevator/rudder)
  - JX_PDI_933MG_Servo (flap)

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_servos.py
"""

from pathlib import Path
import sys

# ── Build123d imports ──────────────────────────────────────────────
from build123d import *
from build123d.exporters import Drawing

# ── DXF drawing imports ───────────────────────────────────────────
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Project imports ───────────────────────────────────────────────
from src.cad.hardware.servo import JX_PDI_1109MG, JX_PDI_933MG

# ── Paths ─────────────────────────────────────────────────────────
ROOT = Path("D:/Repos/aeroforge")
COMP_DIR = ROOT / "cad" / "components" / "hardware"
VALIDATION_DIR = ROOT / "exports" / "validation"
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)


# ── Servo specs ───────────────────────────────────────────────────
SERVO_SPECS = {
    "JX_PDI_1109MG_Servo": {
        "class": JX_PDI_1109MG,
        "model": "JX PDI-1109MG",
        "weight": 10,
        "torque": "2.5 kg-cm @ 6V",
        "length": 23.2,
        "width": 12.5,
        "height": 25.4,
        "ear_to_ear": 32.5,
        "spline": "21T standard micro",
        "wire": "~150mm, 3-pin JR connector",
        "voltage": "4.8-6.0V",
        "speed": "0.10 sec/60 deg @ 6V",
        "usage": "Ailerons (x2), elevator (x1), rudder (x1) = 4 total",
        "color": "Dark blue/black case, metal gear visible on top",
        "mount_holes": "M2 x2, ear-to-ear 32.5mm",
    },
    "JX_PDI_933MG_Servo": {
        "class": JX_PDI_933MG,
        "model": "JX PDI-933MG",
        "weight": 13,
        "torque": "3.5 kg-cm @ 6V",
        "length": 23.0,
        "width": 12.2,
        "height": 29.0,
        "ear_to_ear": 32.0,
        "spline": "21T standard micro",
        "wire": "~150mm, 3-pin JR connector",
        "voltage": "4.8-6.0V",
        "speed": "0.11 sec/60 deg @ 6V",
        "usage": "Flaps (x2) - needs higher torque for crow braking",
        "color": "Dark blue/black case",
        "mount_holes": "M2 x2, ear-to-ear 32.0mm",
    },
}


def create_dxf_drawing(servo_part, spec: dict, output_dxf: Path, output_png: Path):
    """Create a 3-view technical drawing in DXF with dimensions, then render PNG."""

    L = spec["length"]
    W = spec["width"]
    H = spec["height"]
    ear = spec["ear_to_ear"]
    model_name = spec["model"]

    doc = ezdxf.new("R2013")
    doc.header["$INSUNITS"] = 4  # mm
    msp = doc.modelspace()

    # Layers
    doc.layers.add("OUTLINE", color=7)        # White/black
    doc.layers.add("HIDDEN", color=8, linetype="DASHED")
    doc.layers.add("DIMENSION", color=3)      # Green
    doc.layers.add("CENTER", color=1, linetype="CENTER")
    doc.layers.add("TEXT", color=7)
    doc.layers.add("TITLE", color=5)          # Blue

    # Add linetypes
    if "DASHED" not in doc.linetypes:
        doc.linetypes.add("DASHED", pattern=[0.5, -0.25])
    if "CENTER" not in doc.linetypes:
        doc.linetypes.add("CENTER", pattern=[1.0, -0.25, 0.25, -0.25])

    # ── Layout constants ──
    gap = 20.0  # gap between views
    scale = 3.0  # scale up for readability

    sL = L * scale
    sW = W * scale
    sH = H * scale
    sEar = ear * scale
    tab_ext = (ear - L) / 2 * scale
    tab_thick = 1.5 * scale
    tab_z = H * 0.6 * scale  # 60% from bottom in front view
    shaft_d = 4.8 * scale
    shaft_h = 3.5 * scale
    gear_d = 10.0 * scale
    gear_h = 1.0 * scale
    hole_d = 2.0 * scale

    # ── FRONT VIEW (X=length, Y=height) — bottom-left ──
    fx, fy = 10.0, 10.0

    # Main body
    msp.add_lwpolyline(
        [(fx, fy), (fx + sL, fy), (fx + sL, fy + sH), (fx, fy + sH), (fx, fy)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Mounting tabs
    tab_y = fy + tab_z - tab_thick / 2
    tab_left_x = fx - tab_ext
    tab_right_x = fx + sL + tab_ext
    msp.add_lwpolyline(
        [(tab_left_x, tab_y), (tab_right_x, tab_y),
         (tab_right_x, tab_y + tab_thick),
         (tab_left_x, tab_y + tab_thick), (tab_left_x, tab_y)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Mounting holes in front view (shown as vertical lines / circles)
    for hx in [tab_left_x + tab_ext / 2, tab_right_x - tab_ext / 2]:
        msp.add_circle((hx, tab_y + tab_thick / 2), hole_d / 2,
                       dxfattribs={"layer": "HIDDEN"})

    # Gear cover on top (rectangle in front view)
    gear_cx = fx + sL * 0.58  # slightly offset
    msp.add_lwpolyline(
        [(gear_cx - gear_d / 2, fy + sH), (gear_cx + gear_d / 2, fy + sH),
         (gear_cx + gear_d / 2, fy + sH + gear_h),
         (gear_cx - gear_d / 2, fy + sH + gear_h)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Output shaft on top
    msp.add_lwpolyline(
        [(gear_cx - shaft_d / 2, fy + sH + gear_h),
         (gear_cx + shaft_d / 2, fy + sH + gear_h),
         (gear_cx + shaft_d / 2, fy + sH + gear_h + shaft_h),
         (gear_cx - shaft_d / 2, fy + sH + gear_h + shaft_h)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Dimensions - front view (manual annotation lines + text)
    dim_offset = 8.0

    # Height dimension (right side) - vertical
    dx_r = fx + sL + tab_ext + dim_offset
    msp.add_line((fx + sL, fy), (dx_r + 2, fy), dxfattribs={"layer": "DIMENSION"})
    msp.add_line((fx + sL, fy + sH), (dx_r + 2, fy + sH), dxfattribs={"layer": "DIMENSION"})
    msp.add_line((dx_r, fy), (dx_r, fy + sH), dxfattribs={"layer": "DIMENSION"})
    msp.add_text(f"{H}", height=2.5,
                 dxfattribs={"layer": "DIMENSION", "insert": (dx_r + 1, fy + sH / 2 - 1)})

    # Length dimension (bottom) - horizontal
    dy_b = fy - dim_offset
    msp.add_line((fx, fy), (fx, dy_b - 2), dxfattribs={"layer": "DIMENSION"})
    msp.add_line((fx + sL, fy), (fx + sL, dy_b - 2), dxfattribs={"layer": "DIMENSION"})
    msp.add_line((fx, dy_b), (fx + sL, dy_b), dxfattribs={"layer": "DIMENSION"})
    msp.add_text(f"{L}", height=2.5,
                 dxfattribs={"layer": "DIMENSION", "insert": (fx + sL / 2 - 3, dy_b - 5)})

    # Ear-to-ear dimension (below tabs)
    dy_e = tab_y - dim_offset - 5
    msp.add_line((tab_left_x, tab_y), (tab_left_x, dy_e - 2), dxfattribs={"layer": "DIMENSION"})
    msp.add_line((tab_right_x, tab_y), (tab_right_x, dy_e - 2), dxfattribs={"layer": "DIMENSION"})
    msp.add_line((tab_left_x, dy_e), (tab_right_x, dy_e), dxfattribs={"layer": "DIMENSION"})
    msp.add_text(f"{ear}", height=2.5,
                 dxfattribs={"layer": "DIMENSION", "insert": ((tab_left_x + tab_right_x) / 2 - 4, dy_e - 5)})

    # Front view label
    msp.add_text("FRONT", height=3.0,
                 dxfattribs={"layer": "TEXT", "insert": (fx + sL / 2 - 6, fy - dim_offset - 10)})

    # ── RIGHT VIEW (X=width, Y=height) — right of front ──
    rx = fx + sEar + gap + dim_offset + 15
    ry = fy

    # Main body
    msp.add_lwpolyline(
        [(rx, ry), (rx + sW, ry), (rx + sW, ry + sH), (rx, ry + sH), (rx, ry)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Mounting tab (seen from side)
    msp.add_lwpolyline(
        [(rx, tab_y), (rx + sW, tab_y),
         (rx + sW, tab_y + tab_thick),
         (rx, tab_y + tab_thick)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Gear cover (circle in right view = rectangle showing width)
    msp.add_lwpolyline(
        [(rx, fy + sH), (rx + sW, fy + sH),
         (rx + sW, fy + sH + gear_h),
         (rx, fy + sH + gear_h)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Shaft (circle in right view = rectangle)
    shaft_cx_r = rx + sW / 2
    msp.add_lwpolyline(
        [(shaft_cx_r - shaft_d / 2, fy + sH + gear_h),
         (shaft_cx_r + shaft_d / 2, fy + sH + gear_h),
         (shaft_cx_r + shaft_d / 2, fy + sH + gear_h + shaft_h),
         (shaft_cx_r - shaft_d / 2, fy + sH + gear_h + shaft_h)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Width dimension (manual)
    dy_w = ry - dim_offset
    msp.add_line((rx, ry), (rx, dy_w - 2), dxfattribs={"layer": "DIMENSION"})
    msp.add_line((rx + sW, ry), (rx + sW, dy_w - 2), dxfattribs={"layer": "DIMENSION"})
    msp.add_line((rx, dy_w), (rx + sW, dy_w), dxfattribs={"layer": "DIMENSION"})
    msp.add_text(f"{W}", height=2.5,
                 dxfattribs={"layer": "DIMENSION", "insert": (rx + sW / 2 - 3, dy_w - 5)})

    # Right view label
    msp.add_text("RIGHT", height=3.0,
                 dxfattribs={"layer": "TEXT", "insert": (rx + sW / 2 - 7, ry - dim_offset - 10)})

    # ── TOP VIEW (X=length, Y=width) — above front ──
    tx = fx
    ty = fy + sH + gear_h + shaft_h + gap + 15

    # Main body
    msp.add_lwpolyline(
        [(tx, ty), (tx + sL, ty), (tx + sL, ty + sW), (tx, ty + sW), (tx, ty)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Mounting tabs
    tab_left_tx = tx - tab_ext
    tab_right_tx = tx + sL + tab_ext
    tab_ty = ty  # full width of servo
    msp.add_lwpolyline(
        [(tab_left_tx, tab_ty), (tab_right_tx, tab_ty),
         (tab_right_tx, tab_ty + sW),
         (tab_left_tx, tab_ty + sW), (tab_left_tx, tab_ty)],
        close=True, dxfattribs={"layer": "OUTLINE"}
    )

    # Mounting holes (circles in top view)
    for hx in [tab_left_tx + tab_ext / 2, tab_right_tx - tab_ext / 2]:
        msp.add_circle((hx, ty + sW / 2), hole_d / 2,
                       dxfattribs={"layer": "OUTLINE"})

    # Gear cover circle
    gear_cx_t = tx + sL * 0.58
    msp.add_circle((gear_cx_t, ty + sW / 2), gear_d / 2,
                   dxfattribs={"layer": "OUTLINE"})

    # Output shaft circle (smaller, concentric)
    msp.add_circle((gear_cx_t, ty + sW / 2), shaft_d / 2,
                   dxfattribs={"layer": "OUTLINE"})

    # Center lines through shaft
    cl_ext = 3.0
    msp.add_line((gear_cx_t - gear_d / 2 - cl_ext, ty + sW / 2),
                 (gear_cx_t + gear_d / 2 + cl_ext, ty + sW / 2),
                 dxfattribs={"layer": "CENTER"})
    msp.add_line((gear_cx_t, ty + sW / 2 - gear_d / 2 - cl_ext),
                 (gear_cx_t, ty + sW / 2 + gear_d / 2 + cl_ext),
                 dxfattribs={"layer": "CENTER"})

    # Top view label
    msp.add_text("TOP", height=3.0,
                 dxfattribs={"layer": "TEXT", "insert": (tx + sL / 2 - 4, ty + sW + 5)})

    # ── Title Block ──
    title_x = rx + sW + 10
    title_y = ry
    msp.add_text(model_name, height=4.0,
                 dxfattribs={"layer": "TITLE", "insert": (title_x, title_y + 40)})
    msp.add_text(f"Weight: {spec['weight']}g", height=2.5,
                 dxfattribs={"layer": "TEXT", "insert": (title_x, title_y + 33)})
    msp.add_text(f"Torque: {spec['torque']}", height=2.5,
                 dxfattribs={"layer": "TEXT", "insert": (title_x, title_y + 27)})
    msp.add_text(f"Dims: {L} x {W} x {H} mm", height=2.5,
                 dxfattribs={"layer": "TEXT", "insert": (title_x, title_y + 21)})
    msp.add_text(f"Ear-to-ear: {ear} mm", height=2.5,
                 dxfattribs={"layer": "TEXT", "insert": (title_x, title_y + 15)})
    msp.add_text(f"Spline: {spec['spline']}", height=2.5,
                 dxfattribs={"layer": "TEXT", "insert": (title_x, title_y + 9)})
    msp.add_text(f"Usage: {spec['usage']}", height=2.0,
                 dxfattribs={"layer": "TEXT", "insert": (title_x, title_y + 3)})
    msp.add_text("Off-shelf component", height=2.0,
                 dxfattribs={"layer": "TEXT", "insert": (title_x, title_y - 3)})
    msp.add_text("AeroForge Sailplane Project", height=2.0,
                 dxfattribs={"layer": "TEXT", "insert": (title_x, title_y - 9)})
    msp.add_text("Scale 3:1", height=2.0,
                 dxfattribs={"layer": "TEXT", "insert": (title_x, title_y - 15)})

    doc.saveas(str(output_dxf))
    print(f"  DXF saved: {output_dxf}")

    # Render PNG
    fig, ax = plt.subplots(figsize=(16, 10), dpi=200)
    ax.set_facecolor("white")
    ctx = RenderContext(doc)
    Frontend(ctx, MatplotlibBackend(ax)).draw_layout(msp)
    ax.set_aspect("equal")
    ax.margins(0.05)
    fig.savefig(str(output_png), dpi=200, facecolor="white",
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print(f"  PNG saved: {output_png}")


def export_step(servo_part, output_path: Path):
    """Export servo STEP file."""
    export_step_fn = export_step_orig
    servo_part.export_step(str(output_path))
    print(f"  STEP saved: {output_path}")


# Use the actual build123d export
from build123d import export_step as export_step_orig


def render_4_views(servo_part, renders_dir: Path, name: str):
    """Generate 4 standard view renders (isometric, front, top, right) using matplotlib."""
    from build123d.exporters import Drawing

    views = {
        "front":     {"look_from": (0, -1, 0),   "look_up": (0, 0, 1)},
        "top":       {"look_from": (0, 0, 1),    "look_up": (0, 1, 0)},
        "right":     {"look_from": (1, 0, 0),    "look_up": (0, 0, 1)},
        "isometric": {"look_from": (1, -1, 0.8), "look_up": (0, 0, 1)},
    }

    for view_name, params in views.items():
        drawing = Drawing(
            servo_part,
            look_from=params["look_from"],
            look_up=params["look_up"],
            with_hidden=True,
        )

        fig, ax = plt.subplots(figsize=(8, 6), dpi=200)
        ax.set_facecolor("white")
        ax.set_aspect("equal")

        # Draw visible edges
        for edge in drawing.visible_lines.edges():
            pts = [tuple(v)[:2] for v in edge.vertices()]
            if len(pts) >= 2:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                ax.plot(xs, ys, "k-", linewidth=1.0)

        # Draw hidden edges
        for edge in drawing.hidden_lines.edges():
            pts = [tuple(v)[:2] for v in edge.vertices()]
            if len(pts) >= 2:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                ax.plot(xs, ys, "gray", linewidth=0.4, linestyle="--")

        ax.set_title(f"{name} - {view_name}", fontsize=10)
        ax.margins(0.1)
        ax.axis("off")

        out_path = renders_dir / f"{name}_{view_name}.png"
        fig.savefig(str(out_path), dpi=200, facecolor="white",
                    bbox_inches="tight", pad_inches=0.2)
        plt.close(fig)

    print(f"  4 renders saved to: {renders_dir}")


def write_component_info(spec: dict, comp_dir: Path, name: str):
    """Write COMPONENT_INFO.md for a servo."""
    info = f"""# Component: {name}

## Description

{spec['model']} digital micro servo with metal gears. Off-the-shelf component
used in the AeroForge sailplane for control surface actuation. Features a compact
form factor with mounting ears for M2 screws and a 21-tooth output spline.

## Specifications

| Parameter | Value |
|-----------|-------|
| Type | Off-shelf component |
| Model | {spec['model']} |
| Mass | {spec['weight']} g |
| Torque | {spec['torque']} |
| Voltage | {spec['voltage']} |
| Speed | {spec['speed']} |
| Dimensions (L x W x H) | {spec['length']} x {spec['width']} x {spec['height']} mm |
| Ear-to-ear | {spec['ear_to_ear']} mm |
| Output spline | {spec['spline']} |
| Wire | {spec['wire']} |
| Mounting holes | {spec['mount_holes']} |
| Color | {spec['color']} |

## Usage in Sailplane

{spec['usage']}

## Assembly Notes

- Servo mounts into a printed pocket matching the body dimensions ({spec['length']} x {spec['width']} mm).
- Mounting ears rest on the pocket ledge; secured with M2 x 6mm screws.
- Output shaft protrudes through the skin; control horn attaches to the 21T spline.
- Wire routes through internal channels to the receiver bay.
- Pocket depth = body height below ears ({spec['height'] * 0.6:.1f} mm from bottom to ear centerline).
"""
    info_path = comp_dir / "COMPONENT_INFO.md"
    info_path.write_text(info, encoding="utf-8")
    print(f"  COMPONENT_INFO.md saved: {info_path}")


def build_servo(folder_name: str, spec: dict):
    """Build all artifacts for one servo component."""
    print(f"\n{'='*60}")
    print(f"Building: {folder_name}")
    print(f"{'='*60}")

    comp_dir = COMP_DIR / folder_name
    comp_dir.mkdir(parents=True, exist_ok=True)
    renders_dir = comp_dir / "renders"
    renders_dir.mkdir(exist_ok=True)

    # 1. Create servo instance
    servo = spec["class"]()
    bb = servo.bounding_box()
    print(f"  Bounding box: {bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f} mm")
    print(f"  Joints: {list(servo.joints.keys())}")

    # 2. DXF drawing + PNG
    dxf_path = comp_dir / f"{folder_name}_drawing.dxf"
    png_path = comp_dir / f"{folder_name}_drawing.png"
    create_dxf_drawing(servo, spec, dxf_path, png_path)

    # 3. STEP export
    step_path = comp_dir / f"{folder_name}.step"
    export_step_orig(servo, str(step_path))
    print(f"  STEP saved: {step_path}")

    # 4. 4-view renders
    render_4_views(servo, renders_dir, folder_name)

    # 5. COMPONENT_INFO.md
    write_component_info(spec, comp_dir, folder_name)

    # 6. Validation PNG
    val_path = VALIDATION_DIR / f"{folder_name}_validation.svg"
    # Create a simple validation composite
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=150)
    fig.suptitle(f"{spec['model']} - Validation", fontsize=14, fontweight="bold")

    # Left: drawing PNG
    if png_path.exists():
        img = plt.imread(str(png_path))
        axes[0].imshow(img)
        axes[0].set_title("Technical Drawing")
        axes[0].axis("off")

    # Right: isometric render
    iso_path = renders_dir / f"{folder_name}_isometric.png"
    if iso_path.exists():
        img = plt.imread(str(iso_path))
        axes[1].imshow(img)
        axes[1].set_title("Isometric View")
        axes[1].axis("off")

    fig.tight_layout()
    val_png = VALIDATION_DIR / f"{folder_name}_validation.png"
    fig.savefig(str(val_png), dpi=150, facecolor="white")
    plt.close(fig)
    print(f"  Validation image: {val_png}")

    return servo


if __name__ == "__main__":
    print("AeroForge - Servo Component Builder")
    print("=" * 60)

    for folder_name, spec in SERVO_SPECS.items():
        build_servo(folder_name, spec)

    # Clean up PTK servo folder if it exists and is empty or outdated
    ptk_dir = COMP_DIR / "PTK_7308MG_D_Servo"
    if ptk_dir.exists():
        contents = list(ptk_dir.iterdir())
        if not contents:
            print(f"\nNote: {ptk_dir} exists but is empty (outdated servo selection).")
            print("  Consider removing it: the project uses JX servos instead.")
        else:
            print(f"\nNote: {ptk_dir} has {len(contents)} files. Review if needed.")

    print("\n" + "=" * 60)
    print("All servo components built successfully!")
    print("=" * 60)
