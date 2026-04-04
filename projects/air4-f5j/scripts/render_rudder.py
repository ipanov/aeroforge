"""
Rudder Renders — 4 standard views from mesh (trimesh + matplotlib).
====================================================================
Generates isometric, front, top, and right views.
Uses the STL mesh directly (no OCP Viewer dependency).

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/render_rudder.py
"""
import os
import sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

COMPONENT = "Rudder"
STL_PATH = f"cad/components/empennage/{COMPONENT}/{COMPONENT}.stl"
RENDER_DIR = f"cad/components/empennage/{COMPONENT}/renders"


def render_view(mesh, view_name, elev, azim, out_path):
    """Render a single view of the mesh."""
    fig = plt.figure(figsize=(10, 8), dpi=150)
    ax = fig.add_subplot(111, projection='3d')

    # Get mesh faces as polygons
    vertices = mesh.vertices
    faces = mesh.faces

    # Subsample faces for performance if too many
    max_faces = 8000
    if len(faces) > max_faces:
        idx = np.random.choice(len(faces), max_faces, replace=False)
        faces_sub = faces[idx]
    else:
        faces_sub = faces

    polygons = vertices[faces_sub]
    collection = Poly3DCollection(
        polygons, alpha=0.6, facecolor='#8B5CF6',
        edgecolor='#4C1D95', linewidth=0.1
    )
    ax.add_collection3d(collection)

    # Set axis limits
    bbox = mesh.bounding_box.bounds
    center = (bbox[0] + bbox[1]) / 2
    extent = np.max(bbox[1] - bbox[0]) * 0.6

    ax.set_xlim(center[0] - extent, center[0] + extent)
    ax.set_ylim(center[1] - extent, center[1] + extent)
    ax.set_zlim(center[2] - extent, center[2] + extent)

    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel('X (chord)')
    ax.set_ylabel('Y (height)')
    ax.set_zlabel('Z (thickness)')
    ax.set_title(f"{COMPONENT} — {view_name}", fontsize=14)

    # Equal aspect ratio
    ax.set_box_aspect([1, 1, 1])

    fig.savefig(out_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  {view_name}: {out_path}")


def main():
    print(f"Rendering {COMPONENT} 4-view set...")
    os.makedirs(RENDER_DIR, exist_ok=True)

    mesh = trimesh.load(STL_PATH)
    print(f"  Loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    print(f"  Bounds: {mesh.bounds}")

    views = [
        ("isometric", 25, -45),
        ("front", 0, 0),
        ("top", 90, 0),
        ("right", 0, 90),
    ]

    for name, elev, azim in views:
        out_path = os.path.join(RENDER_DIR, f"{name}.png")
        render_view(mesh, name, elev, azim, out_path)

    print(f"\nAll 4 renders saved to {RENDER_DIR}/")


if __name__ == "__main__":
    main()
