"""Master orchestration script for building the complete glider in FreeCAD.

This script generates the FreeCAD Python code for the entire glider,
organized into phases that can be executed sequentially via the MCP
execute_code tool.

Usage (via FreeCAD MCP):
    Phase 1: Right wing (5 panels, vase-mode construction)
    Phase 2: Fuselage pod + boom
    Phase 3: Empennage (H-stab + V-stab)
    Phase 4: Assembly positioning + CG calculation
    Phase 5: STL export for slicer validation

Each phase is a self-contained FreeCAD Python script that can be
executed independently. Phases build on each other (Phase 2 assumes
Phase 1 objects exist in the document).
"""

from __future__ import annotations

from src.freecad_scripts.vase_mode_wing import (
    generate_vase_mode_panel_code,
    generate_all_vase_panels_code,
)
from src.freecad_scripts.fuselage import (
    generate_fuselage_pod_code,
    generate_boom_code,
)
from src.freecad_scripts.empennage import generate_empennage_code
from src.core.specs import SAILPLANE


def get_phase_1_code() -> str:
    """Phase 1: Build right half-wing (5 vase-mode panels)."""
    return generate_all_vase_panels_code()


def get_phase_2_code() -> str:
    """Phase 2: Build fuselage pod and tail boom."""
    return generate_fuselage_pod_code() + "\n\n" + generate_boom_code()


def get_phase_3_code() -> str:
    """Phase 3: Build empennage (H-stab + V-stab)."""
    return generate_empennage_code()


def get_phase_4_code() -> str:
    """Phase 4: Position all components and calculate CG."""
    wing = SAILPLANE.wing

    return f"""
import FreeCAD
import FreeCADGui

doc = FreeCAD.ActiveDocument

# ════════════════════════════════════════════════════════════
# PHASE 4: ASSEMBLY + CG CALCULATION
# ════════════════════════════════════════════════════════════

print("Calculating mass budget and CG...")
print("=" * 50)

# Component mass estimates (from geometry volumes + material density)
components = []

# Wing panels (from Phase 1)
for obj in doc.Objects:
    if obj.Label.startswith("Wing Panel"):
        mass = obj.Shape.Volume / 1000 * 0.54  # LW-PLA foamed
        components.append((obj.Label, mass, 160))  # CG at wing LE + 40mm

# Fuselage (from Phase 2)
for obj in doc.Objects:
    if "Fuselage" in obj.Label:
        mass = obj.Shape.Volume / 1000 * 0.80  # LW-PLA (pod is thicker, less foaming)
        components.append((obj.Label, mass, 125))

# Tail boom
for obj in doc.Objects:
    if "Boom" in obj.Label:
        mass = obj.Shape.Volume / 1000 * 1.60  # Carbon
        components.append((obj.Label, mass, 575))

# Empennage (from Phase 3)
for obj in doc.Objects:
    if "Stab" in obj.Label:
        mass = obj.Shape.Volume / 1000 * 0.54
        components.append((obj.Label, mass, 920))

# Fixed components (not modeled but accounted for)
fixed = [
    ("Battery 3S 1300mAh + XT60", 165.0, 115),
    ("Receiver Turnigy 9X V2", 18.0, 155),
    ("Servos 6x (mix 10g/13g)", 66.0, 165),
    ("Motor (est.)", 55.0, 15),
    ("ESC 20-30A", 17.0, 45),
    ("Prop + spinner", 17.0, 5),
    ("Wiring + connectors", 22.0, 120),
    ("Hardware (screws, hinges)", 25.0, 160),
    ("Wing spars (carbon, both halves)", 30.0, 160),
    ("Mirror wing (left half)", 0, 160),  # Mass added below
]
components.extend(fixed)

# Calculate mirror wing mass (same as right half)
right_wing_mass = sum(m for name, m, _ in components if "Wing Panel" in name)
components.append(("Left wing (mirror)", right_wing_mass, 160))

# CG calculation
total_mass = sum(m for _, m, _ in components)
total_moment = sum(m * x for _, m, x in components)
cg_x = total_moment / total_mass if total_mass > 0 else 0

print(f"COMPONENT MASS BREAKDOWN:")
print(f"-" * 50)
for name, mass, cg in components:
    if mass > 0:
        print(f"  {{name:35s}} {{mass:6.1f}}g  (CG@{{cg}}mm)")

print(f"")
print(f"  {{'TOTAL AUW':35s}} {{total_mass:6.1f}}g")
print(f"")

# CG analysis
wing_le_x = 120  # mm from nose
mac = {wing.mean_chord:.1f}
cg_from_le = cg_x - wing_le_x
cg_pct = cg_from_le / mac * 100
wing_loading = total_mass / {wing.wing_area_dm2:.1f}

print(f"CG ANALYSIS:")
print(f"  CG from nose: {{cg_x:.1f}}mm")
print(f"  CG from wing LE: {{cg_from_le:.1f}}mm")
print(f"  CG as % MAC: {{cg_pct:.1f}}% (target: 30-35%)")
print(f"  Wing loading: {{wing_loading:.1f}} g/dm² (target: 18-19)")
print(f"")

# Status
if 700 <= total_mass <= 900:
    print(f"  ✓ AUW {{total_mass:.0f}}g is within target (700-900g)")
else:
    print(f"  ⚠ AUW {{total_mass:.0f}}g is outside target (700-900g)")

if 28 <= cg_pct <= 38:
    print(f"  ✓ CG {{cg_pct:.1f}}% MAC is in acceptable range")
else:
    print(f"  ⚠ CG {{cg_pct:.1f}}% MAC needs adjustment")

if 16 <= wing_loading <= 22:
    print(f"  ✓ Wing loading {{wing_loading:.1f}} g/dm² is good")
else:
    print(f"  ⚠ Wing loading {{wing_loading:.1f}} g/dm² outside target")

doc.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()
"""


def get_phase_5_code() -> str:
    """Phase 5: Export STL files for slicer validation."""
    return """
import FreeCAD
import Part
import Mesh
import os

doc = FreeCAD.ActiveDocument
export_dir = "D:/Repos/aeroforge/exports/stl"
os.makedirs(export_dir, exist_ok=True)

print("Exporting STL files for slicer validation...")
print("=" * 50)

for obj in doc.Objects:
    if hasattr(obj, "Shape") and obj.Shape.Volume > 0:
        name = obj.Label.replace(" ", "_").replace("(", "").replace(")", "")
        stl_path = os.path.join(export_dir, f"{name}.stl")

        # Export with 0.1mm tessellation tolerance
        mesh = Mesh.Mesh()
        shape = obj.Shape.copy()
        mesh.addFacets(shape.tessellate(0.1))
        mesh.write(stl_path)

        size_mb = os.path.getsize(stl_path) / 1024 / 1024
        print(f"  {obj.Label}: {stl_path} ({size_mb:.1f} MB)")

print(f"")
print(f"STL export complete. Open in OrcaSlicer for print validation:")
print(f"  1. Open OrcaSlicer")
print(f"  2. Import STL files from {export_dir}")
print(f"  3. Set printer: Bambu A1 or P1S")
print(f"  4. Set filament: LW-PLA")
print(f"  5. Enable: Spiral vase mode (spiralize outer contour)")
print(f"  6. Set flow: 0.45, temp: 230°C, retraction: 0mm")
print(f"  7. Preview and check print path traces internal ribs")
"""


def print_build_plan():
    """Print the build execution plan."""
    print("=" * 60)
    print("IVA AEROFORGE GLIDER BUILD PLAN")
    print("=" * 60)
    print()
    print("Phase 1: Right Half-Wing (5 vase-mode panels)")
    print("  - 5 panels with AG24→AG09→AG03 blended airfoils")
    print("  - Vase-mode slot construction (spar walls + cross-ribs)")
    print("  - Carbon spar tunnel at 28% chord")
    print()
    print("Phase 2: Fuselage Pod + Tail Boom")
    print("  - Elliptical pod (46×50mm, fineness ratio 5.4)")
    print("  - 12mm carbon tail boom (650mm)")
    print()
    print("Phase 3: Empennage")
    print("  - H-Stab: 450mm span, 95mm chord, NACA 0009")
    print("  - V-Stab: 140mm height, 110→60mm taper, NACA 0009")
    print()
    print("Phase 4: Assembly + CG Calculation")
    print("  - Position all components")
    print("  - Calculate mass budget and CG location")
    print("  - Verify against targets")
    print()
    print("Phase 5: STL Export")
    print("  - Export all panels for OrcaSlicer validation")
    print("  - Verify vase-mode printability")
    print()
    print("Execute via FreeCAD MCP:")
    print("  mcp__freecad__execute_code(code=get_phase_N_code())")
    print("=" * 60)


if __name__ == "__main__":
    print_build_plan()

    # Syntax-check all phases
    for i, (name, fn) in enumerate([
        ("Phase 1: Wing", get_phase_1_code),
        ("Phase 2: Fuselage", get_phase_2_code),
        ("Phase 3: Empennage", get_phase_3_code),
        ("Phase 4: Assembly", get_phase_4_code),
        ("Phase 5: Export", get_phase_5_code),
    ], 1):
        code = fn()
        try:
            compile(code, f'<phase_{i}>', 'exec')
            print(f"  {name}: {len(code)} chars - OK")
        except SyntaxError as e:
            print(f"  {name}: SYNTAX ERROR line {e.lineno}: {e.msg}")
