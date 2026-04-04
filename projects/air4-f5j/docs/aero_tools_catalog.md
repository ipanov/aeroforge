# Aerodynamic Design Tools Catalog for AeroForge

Comprehensive catalog of Python-callable aerodynamic, optimization, structural, and
manufacturing tools for AI-driven RC sailplane design.

Last updated: 2026-03-28

---

## 1. AIRFOIL ANALYSIS TOOLS (2D)

### 1.1 AeroSandbox (RECOMMENDED - Primary Tool)

| Field | Value |
|-------|-------|
| PyPI | `aerosandbox` |
| Install | `pip install aerosandbox` |
| GitHub | https://github.com/peterdsharpe/AeroSandbox |
| Stars | ~920+ |
| Maintained | Yes, actively (2025-2026) |
| Python-callable | Yes, pure Python |
| License | MIT |

**What it does:** All-in-one aircraft design optimization framework with automatic
differentiation. Combines 2D airfoil analysis, 3D VLM aerodynamics, structural models,
propulsion, trajectory, and stability into a single differentiable optimization framework.

**Key capabilities:**
- 2D airfoil Cl, Cd, Cm via NeuralFoil (ML-based, trained on millions of XFoil runs)
- 3D aerodynamics via built-in VLM and 3D panel methods
- Lift, drag, moment coefficients, pressure distributions
- Stability derivatives (longitudinal and lateral)
- Wing optimization (planform, twist, airfoil shape)
- Trajectory optimization
- Propulsion and weight models
- Full aircraft performance analysis
- Automatic differentiation for gradient-based optimization
- ~5ms per airfoil evaluation, no convergence failures
- Works across 360-degree angle of attack range, any Reynolds number
- Control surface deflection modeling
- Compressible flow (transonic) modeling

**AeroForge relevance:** Ideal for optimizing our AG24-to-AG03 blended wing. Can
simultaneously optimize twist distribution, planform, and airfoil blending for minimum
drag at our target Reynolds numbers (~100k-200k). Differentiable, so optimization of
10,000+ design variables runs in seconds.

```python
import aerosandbox as asb
import aerosandbox.numpy as np

# Define airfoil and get polars
af = asb.Airfoil("ag24")
aero = af.get_aero_from_neuralfoil(
    alpha=5,      # degrees
    Re=150000,    # Reynolds number
    mach=0.05     # low-speed
)
print(f"Cl={aero['CL']:.4f}, Cd={aero['CD']:.5f}, Cm={aero['CM']:.4f}")

# Define a full airplane and analyze
airplane = asb.Airplane(
    name="AeroForge Sailplane",
    wings=[
        asb.Wing(
            name="Main Wing",
            symmetric=True,
            xsecs=[
                asb.WingXSec(xyz_le=[0, 0, 0], chord=0.210, airfoil=asb.Airfoil("ag24")),
                asb.WingXSec(xyz_le=[0.02, 1.28, 0], chord=0.115, airfoil=asb.Airfoil("ag03")),
            ]
        )
    ]
)
op_point = asb.OperatingPoint(velocity=12, alpha=3)
vlm = asb.VortexLatticeMethod(airplane=airplane, op_point=op_point)
aero_result = vlm.run()
```

---

### 1.2 NeuralFoil

| Field | Value |
|-------|-------|
| PyPI | `neuralfoil` |
| Install | `pip install neuralfoil` |
| GitHub | https://github.com/peterdsharpe/NeuralFoil |
| Maintained | Yes, actively |
| Python-callable | Yes, pure Python+NumPy |
| License | MIT |

**What it does:** Physics-informed neural network for airfoil aerodynamics analysis.
Standalone version of the engine inside AeroSandbox. Trained on tens of millions of
XFoil runs.

**Key capabilities:**
- Cl, Cd, Cm predictions for any airfoil shape
- ~5ms evaluation time (vs ~1s for XFoil)
- No convergence failures (unlike XFoil)
- Vectorized batch evaluation
- C-infinity continuous (smooth gradients for optimization)
- Valid across wide Re and alpha range

**AeroForge relevance:** Use standalone when only 2D analysis is needed. Already
bundled inside AeroSandbox.

---

### 1.3 XFoil (Python Wrappers)

Multiple Python wrappers exist for Mark Drela's XFoil:

#### 1.3a xfoil (DARcorporation) - RECOMMENDED wrapper

| Field | Value |
|-------|-------|
| PyPI | `xfoil` |
| Install | `pip install xfoil` |
| GitHub | https://github.com/DARcorporation/xfoil-python |
| Maintained | Moderate (compiled Fortran, stable) |
| Python-callable | Yes, compiled Fortran module |

**What it does:** Direct Python binding to XFoil Fortran code. No subprocess or file I/O.

```python
from xfoil import XFoil
xf = XFoil()
xf.airfoil = xf.load('ag24.dat')  # or define coordinates
xf.Re = 150000
xf.max_iter = 100
cl, cd, cm, cp = xf.a(5.0)  # analyze at alpha=5 deg
# Or sweep: cl, cd, cm, cp = xf.aseq(-5, 15, 0.5)
```

#### 1.3b python-xfoil

| Field | Value |
|-------|-------|
| PyPI | `python-xfoil` |
| Install | `pip install python-xfoil` |
| GitHub | https://github.com/cc-aero/python-xfoil |
| Python-callable | Yes, subprocess wrapper |

**What it does:** Subprocess-based wrapper with concurrent analysis support.

#### 1.3c AeroPy

| Field | Value |
|-------|-------|
| PyPI | Not on PyPI (install from GitHub) |
| Install | `pip install git+https://github.com/leal26/AeroPy.git` |
| GitHub | https://github.com/leal26/AeroPy |
| Maintained | Low (legacy) |

**What it does:** Simple 4-line XFoil interface. Good for quick scripting.

**XFoil capabilities (all wrappers):**
- Viscous/inviscid airfoil analysis
- Cl, Cd, Cm vs alpha polars
- Pressure distribution (Cp)
- Boundary layer parameters
- Transition prediction
- Limited to subsonic, 2D, single-element airfoils

**AeroForge relevance:** XFoil is the gold standard for low-Re airfoil analysis.
Use for validating NeuralFoil results and generating training data. AG24/AG03 are
low-Re airfoils where XFoil excels.

---

### 1.4 XFLR5 (with Python Interface)

| Field | Value |
|-------|-------|
| PyPI | Not on PyPI |
| Install | `pip install git+https://github.com/nikhil-sethi/xflrpy.git` |
| GitHub | https://github.com/nikhil-sethi/xflrpy |
| Maintained | Active development (v0.7.0) |
| Python-callable | Yes, via xflrpy |
| Platform | Linux only (WSL on Windows) |

**What it does:** xflrpy wraps XFLR5 (which itself wraps XFoil + VLM/3D panel methods)
with a Python API. XFLR5 is the de-facto standard for RC model design.

**Key capabilities:**
- 2D airfoil analysis (XFoil engine)
- 3D wing analysis (VLM, lifting line, 3D panels)
- Stability analysis
- Polar generation and management
- Project file management

**AeroForge relevance:** XFLR5 is what most RC designers use. The Python wrapper
allows automation, but Linux-only limitation means WSL is required on our Windows setup.
AeroSandbox is more practical for our workflow.

---

## 2. 3D AERODYNAMIC ANALYSIS TOOLS

### 2.1 AVL (Athena Vortex Lattice) + AVLWrapper

| Field | Value |
|-------|-------|
| PyPI | `avlwrapper` |
| Install | `pip install avlwrapper` (also need AVL binary) |
| GitHub (wrapper) | https://github.com/jbussemaker/AVLWrapper |
| AVL source | https://web.mit.edu/drela/Public/web/avl/ |
| Maintained | Yes (wrapper v0.4.0) |
| Python-callable | Yes, via wrapper |

**What it does:** AVL by Mark Drela is the industry-standard vortex lattice code for
aircraft analysis. AVLWrapper provides a clean Python interface.

**Key capabilities:**
- 3D vortex lattice method
- Lift, drag (induced), moment coefficients
- **Stability derivatives** (all 6 DOF) - AVL's primary strength
- Control surface effectiveness
- Trim analysis
- Neutral point / static margin calculation
- Multiple lifting surfaces (wing + tail)

**Does NOT compute:** Profile drag, pressure distributions (inviscid method)

**AeroForge relevance:** Essential for tail sizing, CG placement, and stability analysis.
AVL can compute our sailplane's static margin, elevator authority, and rudder effectiveness.
Pair with XFoil/NeuralFoil profile drag for total drag prediction.

```python
from avlwrapper import Case, Session, Parameter
# Define geometry, create session, run trim analysis
session = Session(geometry=my_avl_geometry)
result = session.run_case(my_case)
print(result['Cmtot'], result['CLtot'], result['CDind'])
# Access stability derivatives: CLa, Cma, Cnb, Clb, etc.
```

---

### 2.2 OpenVSP + Python API

| Field | Value |
|-------|-------|
| PyPI | Not on PyPI (bundled with OpenVSP install) |
| Install | Download from https://openvsp.org/ ; Python API via SWIG |
| GitHub | https://github.com/OpenVSP/OpenVSP |
| Maintained | Yes, actively (NASA-backed) |
| Python-callable | Yes, via openvsp Python module |
| License | NOSA 1.3 |

**What it does:** NASA's parametric aircraft geometry tool. Defines aircraft by
engineering parameters (span, chord, sweep, etc.) and includes VSPAero for aerodynamic
analysis.

**Key capabilities:**
- Parametric aircraft geometry definition
- VSPAero: VLM and panel method solver
- Lift, drag, moment coefficients
- Stability derivatives
- Parasite drag buildup
- Wetted area computation
- STEP/STL/IGES export
- Mesh generation for external CFD
- MCP server available for AI integration

**AeroForge relevance:** Overkill for our RC sailplane but useful for full-aircraft
wetted area and parasite drag estimation. The MCP server integration is interesting
for AI workflows.

---

### 2.3 PyTornado

| Field | Value |
|-------|-------|
| PyPI | `pytornado` |
| Install | `pip install pytornado` |
| GitHub | https://github.com/airinnova/pytornado |
| Maintained | Moderate |
| Python-callable | Yes |

**What it does:** Pure Python VLM implementation with CPACS file support.

**Key capabilities:**
- 3D vortex lattice method
- Aerodynamic coefficients (CL, CD_induced, Cm)
- Spanwise load distributions
- CPACS input/output (industry standard XML format)
- CLI and Python API

---

### 2.4 PyVLM Implementations

Multiple lightweight VLM codes in Python:

| Package | PyPI | GitHub | Notes |
|---------|------|--------|-------|
| pyvlm (Xero64) | `pyvlm` | https://github.com/Xero64/pyvlm | Terminal + Python API |
| PyVLM (aqreed) | `pyvlm` v0.1.1 | https://github.com/aqreed/PyVLM | Educational |
| pyVLM (ggruszczynski) | N/A | https://github.com/ggruszczynski/pyVLM | 3D implementation |

**AeroForge relevance:** Educational value only. Use AeroSandbox VLM or AVL instead --
they are more mature and validated.

---

## 3. OPTIMIZATION FRAMEWORKS

### 3.1 AeroSandbox (Optimization Engine)

Already covered in Section 1.1. AeroSandbox IS primarily an optimization tool that
happens to include aerodynamics models.

**Optimization capabilities:**
- Automatic differentiation (reverse mode)
- Gradient-based optimization (IPOPT, SNOPT backends)
- Handles 10,000+ design variables
- Constrained optimization (equality and inequality)
- Multi-objective via weighted sums
- Design space exploration
- NumPy-compatible syntax

---

### 3.2 OpenMDAO

| Field | Value |
|-------|-------|
| PyPI | `openmdao` |
| Install | `pip install openmdao` |
| GitHub | https://github.com/OpenMDAO/OpenMDAO |
| Maintained | Yes, actively (NASA-backed) |
| Python-callable | Yes |
| License | Apache 2.0 |
| Requires | Python 3.10+ |

**What it does:** NASA's open-source multidisciplinary design, analysis, and optimization
(MDAO) framework. General-purpose -- not aero-specific.

**Key capabilities:**
- Component-based architecture (like our DAG system)
- Automatic derivative computation (analytic + finite difference)
- Parallel execution (MPI)
- Multiple optimizer interfaces (scipy, pyOptSparse, SNOPT)
- Coupled multidisciplinary analysis
- Design of experiments
- Surrogate modeling

**AeroForge relevance:** More infrastructure than we need. AeroSandbox provides the
same optimization capability with built-in aero models. OpenMDAO shines when coupling
many different physics codes (thermal + structural + aero + propulsion), which is
beyond our scope.

---

### 3.3 OpenAeroStruct (RECOMMENDED for wing optimization)

| Field | Value |
|-------|-------|
| PyPI | `openaerostruct` |
| Install | `pip install openaerostruct` |
| GitHub | https://github.com/mdolab/OpenAeroStruct |
| Maintained | Yes, actively (v2.12.0) |
| Python-callable | Yes |
| License | Apache 2.0 |
| Requires | OpenMDAO |

**What it does:** Coupled aerostructural optimization using VLM + beam FEM. Built
on OpenMDAO. Specifically designed for wing design.

**Key capabilities:**
- Coupled VLM aerodynamics + 1D beam structural model
- Simultaneous aero + structural optimization
- Wingbox structural model
- Adjoint-based gradient computation
- Planform optimization (span, chord, sweep, twist)
- Skin thickness optimization
- Spar sizing
- Multi-point optimization (multiple flight conditions)
- Fuel burn minimization
- Structural weight minimization

**AeroForge relevance:** Directly applicable to our wing panel design. Can optimize
twist distribution and structural sizing simultaneously. The beam model can represent
our carbon tube spar. However, it assumes metal wingbox construction -- our 3D-printed
lattice structure would need custom structural modeling.

```python
import openaerostruct.api as oas
# Define wing mesh, structural properties, flight conditions
# Run aerostructural optimization
# Get optimized twist, thickness, chord distributions
```

---

## 4. AIRFOIL DATABASES

### 4.1 UIUC Airfoil Coordinates Database

| Field | Value |
|-------|-------|
| URL | https://m-selig.ae.illinois.edu/ads/coord_database.html |
| Format | .dat text files (Selig or Lednicer format) |
| Count | ~1,650 airfoils |
| Python access | Direct HTTP download + parsing |

**Programmatic access:**
```python
import urllib.request
import numpy as np

def load_uiuc_airfoil(name):
    """Download airfoil coordinates from UIUC database."""
    url = f"https://m-selig.ae.illinois.edu/ads/coord/{name}.dat"
    data = urllib.request.urlopen(url).read().decode()
    lines = data.strip().split('\n')
    coords = []
    for line in lines[1:]:  # skip header
        parts = line.split()
        if len(parts) == 2:
            coords.append([float(parts[0]), float(parts[1])])
    return np.array(coords)

ag24 = load_uiuc_airfoil("ag24")
```

**AeroForge relevance:** Source of AG24 and AG03 coordinate data. Already used in
our project.

### 4.2 AeroSandbox Built-in Database

AeroSandbox includes a built-in airfoil coordinate database accessible via:
```python
import aerosandbox as asb
af = asb.Airfoil("ag24")  # Loads from built-in database
coords = af.coordinates    # numpy array of [x, y] points
```

Contains most UIUC airfoils plus additional ones. No network access needed.

### 4.3 airfoiltools.com

| Field | Value |
|-------|-------|
| URL | http://airfoiltools.com |
| Python access | Web scraping (no official API) |
| Data | Coordinates + precomputed XFoil polars |

Useful for quick polar lookups but not suitable for automated workflows.

---

## 5. STRUCTURAL ANALYSIS TOOLS

### 5.1 FreeCAD FEM (Already in our stack)

| Field | Value |
|-------|-------|
| Solver | CalculiX (bundled with FreeCAD) |
| Install | Already installed at C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0 |
| Python-callable | Yes, via FreeCAD Python + our MCP server |

**Key capabilities:**
- Full 3D FEM (shell, solid, beam elements)
- Static linear analysis
- Modal analysis (natural frequencies)
- Buckling analysis
- Thermal analysis
- Mesh generation (Gmsh or Netgen)

**AeroForge relevance:** Primary structural tool. Ideal for analyzing 3D-printed
lattice ribs and thin-wall skins under flight loads.

### 5.2 PyNite

| Field | Value |
|-------|-------|
| PyPI | `PyNiteFEA` |
| Install | `pip install PyNiteFEA` |
| GitHub | https://github.com/JWock82/Pynite |
| Maintained | Yes, actively |
| Python-callable | Yes |

**What it does:** 3D structural FEM library for frame-type structures in pure Python.

**Key capabilities:**
- 3D frame analysis (beams, columns)
- P-delta analysis
- Modal analysis
- Plate/shell elements (rectangular)
- Load combinations
- Reaction forces, shear/moment diagrams

**AeroForge relevance:** Could model our spar (carbon tube + spruce strip) as a beam
structure to quickly estimate deflections and stresses without full FreeCAD FEM. Good
for preliminary sizing.

### 5.3 SU2 (Advanced CFD + Structural)

| Field | Value |
|-------|-------|
| Install | Build from source or conda |
| GitHub | https://github.com/su2code/SU2 |
| Maintained | Yes, actively |
| Python-callable | Yes, via Python wrapper |
| License | LGPL 2.1 |

**What it does:** Full RANS CFD + structural + fluid-structure interaction.

**Key capabilities:**
- Reynolds-Averaged Navier-Stokes (RANS) solver
- Euler solver
- Adjoint-based shape optimization
- Fluid-structure interaction (FSI)
- Mesh deformation
- Multi-zone analysis

**AeroForge relevance:** Way overkill for RC sailplane design. The setup complexity
and computation time are not justified at our scale. XFoil + VLM covers our needs.

### 5.4 FEniCS

| Field | Value |
|-------|-------|
| PyPI | `fenics-dolfinx` |
| Install | `pip install fenics-dolfinx` (or conda) |
| Maintained | Yes, actively |

**What it does:** General PDE solver using FEM. Research-grade.

**AeroForge relevance:** Too general-purpose. FreeCAD FEM is more practical for us.

---

## 6. SLICER INTEGRATION

### 6.1 OrcaSlicer CLI (RECOMMENDED)

| Field | Value |
|-------|-------|
| Install | Download from https://github.com/OrcaSlicer/OrcaSlicer/releases |
| Python-callable | Yes, via subprocess |
| Input formats | STL, 3MF, OBJ |
| Output | G-code |

**CLI usage:**
```bash
orca-slicer --slice --load config.ini model.3mf -o output.gcode
```

**Python integration:**
```python
import subprocess
result = subprocess.run([
    "orca-slicer",
    "--slice",
    "--load", "wing_panel_config.ini",
    "wing_panel_01.3mf",
    "-o", "wing_panel_01.gcode"
], capture_output=True, text=True)
```

**Key capabilities:**
- Headless slicing from command line
- Profile loading from .ini or .3MF files
- Parameter override via CLI flags
- Bambu Lab printer profiles built-in
- Tree supports, adaptive layer height
- Multi-material support

**Known limitations:**
- --assemble flag issues with 3MF files
- Some CLI segfault fixes in recent versions
- No REST API (CLI only)

### 6.2 PrusaSlicer CLI

| Field | Value |
|-------|-------|
| Install | Download from https://github.com/prusa3d/PrusaSlicer |
| Python-callable | Yes, via subprocess |
| Binary | `prusa-slicer-console.exe` (Windows) |

**CLI usage:**
```bash
prusa-slicer-console.exe -g --load config.ini model.stl
```

**Python helpers:**
- AutoSlicer: https://github.com/vinjarv/autoslicer
- PrusaSlicer CLI Helper: https://github.com/theskyishard/prusaslicer-command-line-helper

**AeroForge relevance:** OrcaSlicer is preferred since it has better Bambu Lab
integration and is based on PrusaSlicer anyway.

---

## 7. CAPABILITY MATRIX

### What each tool can compute:

| Tool | Cl | Cd | Cm | Cp dist | Stab. derivs | 3D wing | Optimization | Profile drag | Induced drag |
|------|----|----|----|---------|----|---------|------|---------|------|
| AeroSandbox | Yes | Yes | Yes | Yes | Yes | Yes (VLM) | Yes (AD) | Yes (NeuralFoil) | Yes |
| NeuralFoil | Yes | Yes | Yes | Partial | No | No (2D only) | Compatible | Yes | N/A |
| XFoil | Yes | Yes | Yes | Yes | No | No (2D only) | No | Yes | N/A |
| AVL | Yes | Induced only | Yes | No | **Yes (best)** | Yes (VLM) | No | No | Yes |
| OpenVSP | Yes | Yes | Yes | Yes | Yes | Yes (panels) | No | Yes (buildup) | Yes |
| XFLR5/xflrpy | Yes | Yes | Yes | Yes | Yes | Yes (VLM+panels) | No | Yes (via XFoil) | Yes |
| OpenAeroStruct | Yes | Induced only | Yes | No | No | Yes (VLM+beam) | **Yes (coupled)** | No | Yes |
| PyTornado | Yes | Induced only | Yes | No | Partial | Yes (VLM) | No | No | Yes |
| FreeCAD FEM | N/A | N/A | N/A | N/A | N/A | N/A | No | N/A | N/A |
| PyNite | N/A | N/A | N/A | N/A | N/A | N/A | No | N/A | N/A |
| SU2 | Yes | Yes | Yes | Yes | Yes | Yes (RANS) | Yes (adjoint) | Yes | Yes |

---

## 8. RECOMMENDED TOOLCHAIN FOR AEROFORGE

Based on this research, the recommended tool stack for AeroForge is:

### Tier 1: Essential (install now)

| Tool | Purpose | Install |
|------|---------|---------|
| **AeroSandbox** | All-in-one aero + optimization | `pip install aerosandbox` |
| **xfoil** | Reference 2D polars, validation | `pip install xfoil` |
| **avlwrapper** + AVL | Stability derivatives, tail sizing | `pip install avlwrapper` + AVL binary |
| **FreeCAD FEM** | Structural analysis of printed parts | Already installed |
| **OrcaSlicer CLI** | Automated slicing pipeline | Already installed |

### Tier 2: Useful (install when needed)

| Tool | Purpose | Install |
|------|---------|---------|
| **OpenAeroStruct** | Coupled wing aero-structural optimization | `pip install openaerostruct` |
| **PyNite** | Quick spar deflection estimates | `pip install PyNiteFEA` |

### Tier 3: Reference only (don't install unless needed)

| Tool | Purpose | Why not primary |
|------|---------|-----------------|
| OpenVSP | Full aircraft geometry | Overkill, we have Build123d |
| OpenMDAO | MDO framework | AeroSandbox handles this |
| SU2 | High-fidelity CFD | Overkill for RC scale |
| XFLR5/xflrpy | Traditional RC design | Linux only, AeroSandbox is better |
| FEniCS | General PDE/FEM | FreeCAD FEM is simpler |

### Typical AeroForge workflow:

```
1. Airfoil selection    -> AeroSandbox (NeuralFoil) sweep AG-series at Re=100k-200k
2. Airfoil validation   -> XFoil polars to validate NeuralFoil predictions
3. Wing optimization    -> AeroSandbox VLM (planform, twist, blending)
4. Stability analysis   -> AVL (static margin, trim, control derivatives)
5. Structural sizing    -> PyNite (spar quick-check) + FreeCAD FEM (detailed)
6. Print preparation    -> Build123d export STL/3MF -> OrcaSlicer CLI
```

---

## Sources

- [AeroSandbox GitHub](https://github.com/peterdsharpe/AeroSandbox)
- [AeroSandbox PyPI](https://pypi.org/project/AeroSandbox/)
- [NeuralFoil GitHub](https://github.com/peterdsharpe/NeuralFoil)
- [NeuralFoil Paper (arXiv)](https://arxiv.org/html/2503.16323v1)
- [xfoil-python GitHub](https://github.com/DARcorporation/xfoil-python)
- [xfoil PyPI](https://pypi.org/project/xfoil/)
- [python-xfoil GitHub](https://github.com/cc-aero/python-xfoil)
- [AeroPy GitHub](https://github.com/leal26/AeroPy)
- [AVLWrapper GitHub](https://github.com/jbussemaker/AVLWrapper)
- [AVLWrapper PyPI](https://pypi.org/project/avlwrapper/)
- [AVL (MIT)](https://web.mit.edu/drela/Public/web/avl/)
- [OpenVSP GitHub](https://github.com/OpenVSP/OpenVSP)
- [OpenVSP Python API Docs](https://openvsp.org/pyapi_docs/latest/)
- [xflrpy GitHub](https://github.com/nikhil-sethi/xflrpy)
- [PyTornado GitHub](https://github.com/airinnova/pytornado)
- [PyTornado PyPI](https://pypi.org/project/pytornado/)
- [OpenMDAO GitHub](https://github.com/OpenMDAO/OpenMDAO)
- [OpenMDAO PyPI](https://pypi.org/project/openmdao/)
- [OpenAeroStruct GitHub](https://github.com/mdolab/OpenAeroStruct)
- [OpenAeroStruct PyPI](https://pypi.org/project/openaerostruct/)
- [UIUC Airfoil Database](https://m-selig.ae.illinois.edu/ads/coord_database.html)
- [PyNite GitHub](https://github.com/JWock82/Pynite)
- [PyNite PyPI](https://pypi.org/project/PyNiteFEA/)
- [SU2 GitHub](https://github.com/su2code/SU2)
- [OrcaSlicer CLI Discussion](https://github.com/OrcaSlicer/OrcaSlicer/discussions/8593)
- [PrusaSlicer CLI Wiki](https://github.com/prusa3d/PrusaSlicer/wiki/Command-Line-Interface)
- [PanelAero (DLR)](https://github.com/DLR-AE/PanelAero)
