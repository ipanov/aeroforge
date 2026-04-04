"""
Generate 4 Standard Renders for HStab Components
=================================================
Imports STEP files into FreeCAD and captures isometric, front, top, right views.
Run when FreeCAD MCP server is available.

Usage: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/render_hstab.py
"""

import os
import sys
import xmlrpc.client

# FreeCAD RPC connection
FREECAD_RPC = "http://localhost:12345"

COMPONENTS = {
    "HStab_Left": {
        "step": "cad/components/empennage/HStab_Left/HStab_Left.step",
        "render_dir": "cad/components/empennage/HStab_Left/renders",
    },
    "HStab_Right": {
        "step": "cad/components/empennage/HStab_Right/HStab_Right.step",
        "render_dir": "cad/components/empennage/HStab_Right/renders",
    },
}

VIEWS = ["Isometric", "Front", "Top", "Right"]


def render_component(name, step_path, render_dir):
    """Import STEP and capture 4 standard views."""
    print(f"\nRendering {name}...")
    os.makedirs(render_dir, exist_ok=True)

    # This script is meant to be adapted for FreeCAD MCP or FreeCAD CLI
    # For now, it documents the render commands needed
    print(f"  STEP: {step_path}")
    print(f"  Output: {render_dir}/")
    for view in VIEWS:
        out_path = os.path.join(render_dir, f"{name}_{view.lower()}.png")
        print(f"  View: {view} -> {out_path}")


def main():
    for name, paths in COMPONENTS.items():
        if not os.path.exists(paths["step"]):
            print(f"SKIP {name}: STEP file not found ({paths['step']})")
            continue
        render_component(name, paths["step"], paths["render_dir"])

    print("\n--- MANUAL STEPS ---")
    print("When FreeCAD MCP is available, use these commands:")
    print("  1. mcp__freecad__execute_code to import each STEP")
    print("  2. mcp__freecad__get_view for each of the 4 standard views")
    print("  3. Save screenshots to renders/ folders")


if __name__ == "__main__":
    main()
