"""
Generate 4-view renders for off-shelf electronic hardware components.
Uses trimesh for rendering since these are simple solid bodies.

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/render_hardware_electronics.py
"""

import sys
import os
from pathlib import Path
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

try:
    import trimesh
    from trimesh import Scene
    HAS_TRIMESH = True
except ImportError:
    HAS_TRIMESH = False

try:
    from build123d import *
    HAS_BUILD123D = True
except ImportError:
    HAS_BUILD123D = False


def _step_to_mesh(step_path: str) -> "trimesh.Trimesh":
    """Load a STEP file and convert to trimesh via Build123d."""
    shape = import_step(step_path)

    # Try multiple tolerance levels
    for tol, ang_tol in [(0.01, 0.1), (0.05, 0.5), (0.1, 1.0)]:
        try:
            vertices, triangles = shape.tessellate(tolerance=tol, angular_tolerance=ang_tol)
            verts = np.array([[v.X, v.Y, v.Z] for v in vertices])
            faces = np.array(triangles)
            mesh = trimesh.Trimesh(vertices=verts, faces=faces)
            if len(mesh.faces) > 0:
                return mesh
        except (AttributeError, Exception):
            continue

    # Fallback: export to STL temporarily and load
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as f:
        tmp_stl = f.name
    try:
        export_stl(shape, tmp_stl, tolerance=0.05, angular_tolerance=0.5)
        mesh = trimesh.load(tmp_stl)
        return mesh
    finally:
        os.unlink(tmp_stl)


def _render_4_views(mesh: "trimesh.Trimesh", output_dir: Path, name: str,
                    color=(100, 100, 100, 255)):
    """Render isometric, front, top, right views of a mesh."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set mesh color
    mesh.visual.face_colors = color

    views = {
        "isometric": {"angles": (math.radians(35), math.radians(45))},
        "front": {"angles": (0, 0)},
        "top": {"angles": (math.radians(90), 0)},
        "right": {"angles": (0, math.radians(90))},
    }

    for view_name, params in views.items():
        scene = Scene([mesh])
        out_path = output_dir / f"{name}_{view_name}.png"

        try:
            # Use scene.save_image if available (requires pyglet/pyrender)
            png_data = scene.save_image(resolution=(800, 600))
            if png_data:
                with open(str(out_path), 'wb') as f:
                    f.write(png_data)
                print(f"  {view_name}: {out_path}")
            else:
                print(f"  {view_name}: SKIPPED (no renderer available)")
        except Exception as e:
            print(f"  {view_name}: SKIPPED ({e})")


def _render_matplotlib_views(mesh: "trimesh.Trimesh", output_dir: Path,
                              name: str, color='steelblue'):
    """Render 4 views using matplotlib as fallback."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    output_dir.mkdir(parents=True, exist_ok=True)

    vertices = mesh.vertices
    faces = mesh.faces

    views = {
        "isometric": (35, 45),
        "front": (0, 0),
        "top": (90, 0),
        "right": (0, 90),
    }

    for view_name, (elev, azim) in views.items():
        fig = plt.figure(figsize=(8, 6), dpi=150)
        ax = fig.add_subplot(111, projection='3d')

        # Create polygon collection
        poly3d = [[vertices[j] for j in face] for face in faces]
        collection = Poly3DCollection(poly3d, alpha=0.85, linewidth=0.1,
                                       edgecolors='#333333', facecolors=color)
        ax.add_collection3d(collection)

        # Set axis limits
        bounds = mesh.bounds
        center = (bounds[0] + bounds[1]) / 2
        extent = max(bounds[1] - bounds[0]) * 0.6

        ax.set_xlim(center[0] - extent, center[0] + extent)
        ax.set_ylim(center[1] - extent, center[1] + extent)
        ax.set_zlim(center[2] - extent, center[2] + extent)

        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title(f"{name} - {view_name}")

        # Clean up
        ax.set_box_aspect([1, 1, 1])

        out_path = output_dir / f"{name}_{view_name}.png"
        fig.savefig(str(out_path), dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        print(f"  {view_name}: {out_path}")


def render_component(step_path: str, render_dir: str, name: str, color: str):
    """Render a single component from STEP file."""
    print(f"\nRendering {name}...")

    mesh = _step_to_mesh(step_path)
    output_dir = Path(render_dir)

    _render_matplotlib_views(mesh, output_dir, name, color=color)


def main():
    print("Generating hardware electronics renders...")

    components = [
        {
            "step": "cad/components/hardware/Flysky_FS_iA6B_Receiver/Flysky_FS_iA6B_Receiver.step",
            "renders": "cad/components/hardware/Flysky_FS_iA6B_Receiver/renders",
            "name": "Flysky_FS_iA6B_Receiver",
            "color": "#1a1a1a",  # Black
        },
        {
            "step": "cad/components/hardware/LiPo_3S_1300mAh/LiPo_3S_1300mAh.step",
            "renders": "cad/components/hardware/LiPo_3S_1300mAh/renders",
            "name": "LiPo_3S_1300mAh",
            "color": "#2c3e6b",  # Dark blue
        },
        {
            "step": "cad/components/hardware/XT60_Connector/XT60_Connector.step",
            "renders": "cad/components/hardware/XT60_Connector/renders",
            "name": "XT60_Connector",
            "color": "#e6c619",  # Yellow
        },
    ]

    for comp in components:
        if not Path(comp["step"]).exists():
            print(f"  SKIP {comp['name']}: STEP not found at {comp['step']}")
            continue
        render_component(comp["step"], comp["renders"], comp["name"], comp["color"])

    print("\nAll renders generated.")


if __name__ == "__main__":
    main()
