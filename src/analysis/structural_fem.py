"""Structural FEM analysis using FreeCAD headless (CalculiX).

Generates a simplified wing spar beam model and runs static analysis
to verify deflection and stress under flight loads.

Requires FreeCAD 1.0+ with FEM workbench and CalculiX solver.
FreeCADCmd path: C:/Users/ilija/AppData/Local/Programs/FreeCAD 1.0/bin/FreeCADCmd.exe

Usage:
    from src.analysis.structural_fem import run_spar_analysis

    results = run_spar_analysis(load_factor=3.0)

All dimensions in mm, weights in grams, forces in N.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import json
from pathlib import Path

from src.core.specs import SAILPLANE

FREECAD_CMD = r"C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0\bin\FreeCADCmd.exe"


def _generate_fem_script(
    output_dir: str,
    load_factor: float = 3.0,
    auw_grams: float = 800.0,
) -> str:
    """Generate a FreeCAD Python script for spar FEM analysis.

    Models the main carbon spar as a cantilever beam with distributed lift load.
    The load is semi-elliptical (approximating actual lift distribution).

    Args:
        output_dir: Directory for result files
        load_factor: Load factor for analysis (e.g. 3.0 for 3g pull-up)
        auw_grams: All-up weight in grams

    Returns:
        Python script as string
    """
    wing = SAILPLANE.wing
    spar = SAILPLANE.spar

    half_span_mm = wing.half_span
    spar_od = spar.main_od
    spar_id = spar.main_id
    half_weight_n = (auw_grams / 1000.0) * 9.81 / 2  # half-wing lift in N
    total_load_n = half_weight_n * load_factor

    script = f'''import sys
import os
import json

output_dir = r"{output_dir}"

import FreeCAD
import Part
import ObjectsFem

doc = FreeCAD.newDocument("SparAnalysis")

half_span = {half_span_mm}
spar_od = {spar_od}
spar_id = {spar_id}
total_load_N = {total_load_n}

# Geometry: hollow carbon tube
outer = doc.addObject("Part::Cylinder", "SparOuter")
outer.Radius = spar_od / 2
outer.Height = half_span

inner = doc.addObject("Part::Cylinder", "SparInner")
inner.Radius = spar_id / 2
inner.Height = half_span

spar_shape = doc.addObject("Part::Cut", "CarbonSpar")
spar_shape.Base = outer
spar_shape.Tool = inner
doc.recompute()

# Find root (z=0) and tip (z=half_span) annular faces
root_face = None
tip_face = None
for i, face in enumerate(spar_shape.Shape.Faces):
    com = face.CenterOfMass
    if abs(com.z) < 1.0 and face.Area < 100:
        root_face = f"Face{{i+1}}"
    if abs(com.z - half_span) < 1.0 and face.Area < 100:
        tip_face = f"Face{{i+1}}"

# FEM Analysis
analysis = ObjectsFem.makeAnalysis(doc, "Analysis")

solver = ObjectsFem.makeSolverCalculiXCcxTools(doc, "CalculiX")
solver.GeometricalNonlinearity = "linear"
analysis.addObject(solver)

material = ObjectsFem.makeMaterialSolid(doc, "CarbonFiber")
mat = material.Material
mat["Name"] = "Carbon Fiber Pultruded"
mat["YoungsModulus"] = "135000 MPa"
mat["PoissonRatio"] = "0.3"
mat["Density"] = "1600 kg/m^3"
material.Material = mat
analysis.addObject(material)

# Mesh via GMSH - 1st order to avoid negative jacobians on thin walls
mesh_obj = ObjectsFem.makeMeshGmsh(doc, "FEMMesh")
mesh_obj.Shape = spar_shape
mesh_obj.CharacteristicLengthMax = 15.0
mesh_obj.CharacteristicLengthMin = 0.5
mesh_obj.ElementOrder = "1st"
analysis.addObject(mesh_obj)
doc.recompute()

from femmesh.gmshtools import GmshTools
gmsh = GmshTools(mesh_obj)
error = gmsh.create_mesh()
doc.recompute()

node_count = mesh_obj.FemMesh.NodeCount if hasattr(mesh_obj.FemMesh, 'NodeCount') else 0
vol_count = mesh_obj.FemMesh.VolumeCount if hasattr(mesh_obj.FemMesh, 'VolumeCount') else 0

if vol_count == 0:
    result = {{"error": "Mesh generation failed - no volume elements"}}
    with open(os.path.join(output_dir, "fem_results.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(1)

# Fixed constraint at root
fixed = ObjectsFem.makeConstraintFixed(doc, "FixedRoot")
fixed.References = [(spar_shape, root_face)]
analysis.addObject(fixed)

# Force direction line (Y axis = lift direction, perpendicular to spar)
dir_line = doc.addObject("Part::Line", "ForceDir")
dir_line.X1 = 0
dir_line.Y1 = 0
dir_line.Z1 = 0
dir_line.X2 = 0
dir_line.Y2 = 10
dir_line.Z2 = 0
doc.recompute()

force = ObjectsFem.makeConstraintForce(doc, "LiftForce")
force.References = [(spar_shape, tip_face)]
force.Force = total_load_N * 1000  # FreeCAD FEM expects mN
force.Direction = (dir_line, ["Edge1"])
force.Reversed = False
analysis.addObject(force)
doc.recompute()

# Run CalculiX
from femtools import ccxtools
fea = ccxtools.FemToolsCcx(analysis, solver)
fea.setup_working_dir(output_dir)
fea.purge_results()
fea.reset_all()
fea.update_objects()

prereq = fea.check_prerequisites()
if prereq:
    result = {{"error": f"Prerequisites failed: {{prereq}}"}}
    with open(os.path.join(output_dir, "fem_results.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(1)

fea.run()
fea.load_results()

# Extract results
results_obj = None
for obj in analysis.Group:
    if obj.isDerivedFrom("Fem::FemResultObject"):
        results_obj = obj
        break

if results_obj:
    # Get displacement and stress - handle FreeCAD 1.0 attribute names
    disp_lengths = None
    stress_values = None

    if hasattr(results_obj, "DisplacementLengths"):
        disp_lengths = list(results_obj.DisplacementLengths)
    elif hasattr(results_obj, "Displacement"):
        disp = results_obj.Displacement
        disp_lengths = [(d[0]**2 + d[1]**2 + d[2]**2)**0.5 for d in disp]

    if hasattr(results_obj, "StressValues"):
        stress_values = list(results_obj.StressValues)
    elif hasattr(results_obj, "vonMises"):
        stress_values = list(results_obj.vonMises)
    elif hasattr(results_obj, "NodeStressVectors"):
        svs = results_obj.NodeStressVectors
        stress_values = []
        for sv in svs:
            s11, s22, s33, s12, s23, s13 = sv[0], sv[1], sv[2], sv[3], sv[4], sv[5]
            vm = ((s11-s22)**2 + (s22-s33)**2 + (s33-s11)**2 + 6*(s12**2+s23**2+s13**2))**0.5 / 2**0.5
            stress_values.append(vm)

    if disp_lengths and stress_values:
        max_disp = max(disp_lengths)
        max_stress = max(stress_values)
        sf = 1500.0 / max_stress if max_stress > 0 else float("inf")
        defl_ratio = max_disp / half_span

        result = {{
            "analysis": "Carbon Spar Static FEM",
            "load_factor": {load_factor},
            "auw_grams": {auw_grams},
            "half_span_mm": half_span,
            "spar_od_mm": spar_od,
            "spar_id_mm": spar_id,
            "total_load_N": total_load_N,
            "max_displacement_mm": round(max_disp, 3),
            "deflection_span_pct": round(defl_ratio * 100, 2),
            "max_von_mises_MPa": round(max_stress, 2),
            "safety_factor": round(sf, 2),
            "mesh_nodes": node_count,
            "mesh_elements": vol_count,
            "pass": sf > 1.5,
        }}
    else:
        result = {{"error": "Could not extract displacement/stress from results"}}
else:
    result = {{"error": "No FEM result object found"}}

with open(os.path.join(output_dir, "fem_results.json"), "w") as f:
    json.dump(result, f, indent=2)

doc.saveAs(os.path.join(output_dir, "spar_analysis.FCStd"))
sys.exit(0)
'''

    return script


def run_spar_analysis(
    load_factor: float = 3.0,
    auw_grams: float = 800.0,
    output_dir: str | None = None,
) -> dict:
    """Run FEM analysis on the main carbon spar.

    Models as a cantilever beam with tip load (conservative).

    Args:
        load_factor: Load factor (1.0 = straight flight, 3.0 = typical maneuver)
        auw_grams: All-up weight
        output_dir: Optional output directory (uses temp if None)

    Returns:
        dict with FEM results
    """
    if not Path(FREECAD_CMD).exists():
        return {"error": f"FreeCADCmd not found at {FREECAD_CMD}"}

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="aeroforge_fem_")
    else:
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)

    script = _generate_fem_script(output_dir, load_factor, auw_grams)
    script_path = os.path.join(output_dir, "fem_script.py")

    with open(script_path, "w") as f:
        f.write(script)

    # Run FreeCADCmd with script file (FreeCAD 1.0 executes .py files passed as args)
    try:
        result = subprocess.run(
            [FREECAD_CMD, script_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=output_dir,
        )
    except subprocess.TimeoutExpired:
        return {"error": "FEM analysis timed out after 5 minutes"}
    except FileNotFoundError:
        return {"error": f"FreeCADCmd not found: {FREECAD_CMD}"}

    # Read results
    results_file = os.path.join(output_dir, "fem_results.json")
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            return json.load(f)

    return {
        "error": "FEM analysis produced no results",
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
        "returncode": result.returncode,
    }


def analytical_spar_check(
    load_factor: float = 3.0,
    auw_grams: float = 800.0,
) -> dict:
    """Quick analytical beam calculation (no FreeCAD required).

    Uses Euler-Bernoulli beam theory for a hollow carbon tube cantilever.
    This gives a fast sanity check before running full FEM.

    Args:
        load_factor: Load factor
        auw_grams: All-up weight

    Returns:
        dict with analytical results
    """
    import math

    wing = SAILPLANE.wing
    spar = SAILPLANE.spar

    L = wing.half_span / 1000  # m (half span)
    R_o = spar.main_od / 2 / 1000  # m (outer radius)
    R_i = spar.main_id / 2 / 1000  # m (inner radius)

    # Material properties - pultruded carbon tube
    E = 135e9  # Pa (135 GPa)
    sigma_ult = 1500e6  # Pa (1500 MPa)

    # Second moment of area for hollow circular section
    I = math.pi / 4 * (R_o**4 - R_i**4)

    # Section modulus
    Z = I / R_o

    # Load: half-wing lift at given load factor
    W = (auw_grams / 1000) * 9.81  # Total weight in N
    P = W / 2 * load_factor  # Half-wing load in N

    # Case 1: Point load at tip (most conservative)
    delta_tip_point = P * L**3 / (3 * E * I)
    sigma_max_point = P * L / Z

    # Case 2: Uniformly distributed load (less conservative)
    w = P / L  # N/m distributed load
    delta_tip_dist = w * L**4 / (8 * E * I)
    sigma_max_dist = w * L**2 / (2 * Z)

    # Case 3: Elliptical distribution (most realistic for wing)
    # For elliptical loading, max deflection ~ 0.318 * P*L^3/(EI)
    delta_tip_ellip = 0.318 * P * L**3 / (E * I)
    # Max bending moment at root for elliptical = 4P/(3*pi) * L
    M_root_ellip = 4 * P / (3 * math.pi) * L
    sigma_max_ellip = M_root_ellip / Z

    sf_point = sigma_ult / sigma_max_point
    sf_dist = sigma_ult / sigma_max_dist
    sf_ellip = sigma_ult / sigma_max_ellip

    return {
        "analysis": "Analytical Beam (Euler-Bernoulli)",
        "load_factor": load_factor,
        "auw_grams": auw_grams,
        "half_span_m": round(L, 4),
        "spar_od_mm": spar.main_od,
        "spar_id_mm": spar.main_id,
        "I_mm4": round(I * 1e12, 2),
        "Z_mm3": round(Z * 1e9, 2),
        "total_half_load_N": round(P, 2),
        "point_load": {
            "tip_deflection_mm": round(delta_tip_point * 1000, 2),
            "deflection_span_pct": round(delta_tip_point / L * 100, 2),
            "max_stress_MPa": round(sigma_max_point / 1e6, 1),
            "safety_factor": round(sf_point, 2),
        },
        "distributed_load": {
            "tip_deflection_mm": round(delta_tip_dist * 1000, 2),
            "deflection_span_pct": round(delta_tip_dist / L * 100, 2),
            "max_stress_MPa": round(sigma_max_dist / 1e6, 1),
            "safety_factor": round(sf_dist, 2),
        },
        "elliptical_load": {
            "tip_deflection_mm": round(delta_tip_ellip * 1000, 2),
            "deflection_span_pct": round(delta_tip_ellip / L * 100, 2),
            "max_stress_MPa": round(sigma_max_ellip / 1e6, 1),
            "safety_factor": round(sf_ellip, 2),
        },
        "pass": sf_ellip > 1.5,
        "notes": "Elliptical distribution is most realistic for a sailplane wing.",
    }
