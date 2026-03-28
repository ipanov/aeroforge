"""FreeCAD Python code generators for AeroForge.

These modules generate Python code strings that execute inside FreeCAD
via the MCP execute_code tool. They do NOT run inside FreeCAD directly.

Modules:
- airfoil_to_freecad: Wing panel geometry (airfoil profiles → lofted surfaces)
- fuselage: Pod-and-boom fuselage with elliptical cross-section
- empennage: Horizontal and vertical stabilizers
- assembly: Full glider assembly with CG calculation
"""
