"""
Render Wing Panel P1 — 4 standard views using OCP Viewer.
Isometric, front, top, right.

Usage: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/render_wing_panel_p1.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from build123d import import_step
from ocp_vscode import show, save_screenshot, set_port, Camera

VIEWS = {
    "isometric": Camera.ISO,
    "front": Camera.FRONT,
    "top": Camera.TOP,
    "right": Camera.RIGHT,
}

BASE = "D:/Repos/aeroforge"
STEP_PATH = os.path.join(BASE, "cad/components/wing/Wing_Panel_P1/Wing_Panel_P1.step")
RENDER_DIR = os.path.join(BASE, "cad/components/wing/Wing_Panel_P1/renders")


def main():
    set_port(3939)
    os.makedirs(RENDER_DIR, exist_ok=True)

    print(f"Loading STEP: {STEP_PATH}")
    panel = import_step(STEP_PATH)
    print(f"  Loaded. Bounding box: {panel.bounding_box()}")

    for vname, cam in VIEWS.items():
        show(panel, names=["Wing_Panel_P1"], colors=["lightblue"],
             alphas=[0.4], reset_camera=cam)
        time.sleep(2.5)
        fname = f"Wing_Panel_P1_{vname}.png"
        path = os.path.join(RENDER_DIR, fname)
        save_screenshot(path)
        print(f"  Saved {path}")
        time.sleep(0.5)

    print("\nAll 4 renders saved.")


if __name__ == "__main__":
    main()
