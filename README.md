# AeroForge

**AI-Enabled 3D-Printed RC Sailplane Design System**

> *"Why make it simple when it can be complex - for the same price?"*

---

## What Is This?

AeroForge is an AI-driven parametric design system for RC sailplanes. It exploits
the fact that **3D printers have zero marginal cost for complexity** - a topology-optimized
lattice rib costs the same filament as a flat plate, but performs dramatically better.

The system takes natural language design intent (**Text2CAD**) and produces
fully parametric, constraint-based 3D models ready for printing on consumer
printers (Bambu A1/P1S).

## The Goal

Design a 3D-printed RC sailplane that **exceeds commercial kits** (Insight F5J,
Introduction, Bowser) in aerodynamic performance - at a fraction of the cost.

Commercial kits are locked into 10-15 year old designs constrained by manufacturing:
2-3 airfoil stations, simple planforms, uniform internal structure. AeroForge has
**no such constraints** - every rib can be a unique airfoil, every surface can be
optimally shaped, every internal structure can be topology-optimized.

## Current Specifications

| Parameter | Value |
|-----------|-------|
| Wingspan | 2.56m |
| Wing panels | 10 (5 per half, 256mm each - exact bed fit) |
| Root chord | 210mm |
| Tip chord | 115mm |
| Airfoil | AG24 (root) → AG09 (mid) → AG03 (tip), blended continuously |
| Main spar | 8mm pultruded carbon tube |
| Rear spar | 5x3mm spruce strip |
| Controls | Full-house (ailerons, flaps, elevator, rudder) + crow braking |
| Target AUW | 700-850g |
| Target cost | Under $150 total (filament + carbon + electronics) |

## Architecture

```
Text2CAD (natural language design)
    │
    ▼
Build123d (Python parametric CAD, headless)
    │
    ├── Dependency DAG (NetworkX) ── auto-propagates changes
    ├── Pydantic validation ── enforces constraints
    ├── Consistency tests ── spec vs docs vs code
    │
    ├── STEP export ──► FreeCAD (headless FEM/CFD analysis)
    └── 3MF export ──► OrcaSlicer CLI ──► Bambu printer
```

### Key Innovation: Specification Consistency System

Every design parameter has a **single source of truth** in Python (`src/core/specs.py`).
24 automated tests verify that documentation, code, and specs stay in sync.
When a parameter changes, the dependency graph propagates updates to all affected
components automatically.

See [docs/consistency_system.md](docs/consistency_system.md) for the full system
architecture with Mermaid diagrams.

## Project Structure

```
aeroforge/
├── src/
│   ├── core/               # Component framework, DAG, specs, validation
│   ├── cad/                # Build123d parametric models
│   │   ├── airfoils/       # AG/NACA airfoil generators
│   │   ├── wing/           # Wing panels, ribs, skins
│   │   ├── fuselage/       # Pod, boom
│   │   └── tail/           # Empennage
│   ├── analysis/           # FreeCAD headless wrappers (FEM, CFD)
│   └── text2cad/           # AI workflow pipeline
├── components/             # Off-the-shelf component specs
├── docs/
│   ├── philosophy.md       # Design philosophy
│   ├── specifications.md   # Complete spec reference
│   ├── consistency_system.md # How spec sync works (with diagrams)
│   ├── spec_registry.md    # Parameter → file map
│   └── slicer_pipeline.md  # 3D print automation
├── exports/                # STL, STEP, 3MF output
└── tests/                  # 72 tests (framework + consistency)
```

## Installation and Setup (Step by Step)

This project uses **AI coding agents** that design, model, and validate 3D-printed aircraft components automatically. You interact by giving design direction; the agent does all the CAD work.

### Prerequisites

| Software | Version | What It Does |
|----------|---------|-------------|
| [Python](https://www.python.org/downloads/) | 3.10+ | Runs all CAD scripts and parametric models |
| [Git](https://git-scm.com/downloads) | 2.30+ | Version control |
| [VS Code](https://code.visualstudio.com/) | Latest | Code editor + 3D viewer |
| [Node.js](https://nodejs.org/) | 18+ | Required by Claude Code CLI |

### Step 1: Clone and Install Python Dependencies

```bash
git clone https://github.com/ipanov/aeroforge.git
cd aeroforge
pip install -r requirements.txt

# Verify installation
python -c "from src.core.specs import SAILPLANE; print(SAILPLANE.summary())"
pytest  # Run all tests
```

### Step 2: Install VS Code Extensions

Open VS Code, go to Extensions (Ctrl+Shift+X), and install:

1. **OCP CAD Viewer** (`bernhard-42.ocp-cad-viewer`) -- 3D model viewer for Build123d
2. **Python** (`ms-python.python`) -- Python language support
3. **Claude Code** (`anthropic.claude-code`) -- AI coding agent (if using Anthropic)

### Step 3: Install Claude Code CLI

```bash
# Install globally
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

### Step 4: Configure Your AI Provider

Claude Code works with **Anthropic** by default. You can also use alternative providers for cost savings. Configure by setting environment variables or editing your Claude Code settings.

#### Option A: Anthropic (Default)

```bash
# Set your API key (or export in your shell profile)
claude config set --global apiKey sk-ant-your-key-here
```

#### Option B: xAI (Grok Models)

To use xAI's Grok models as your provider, set these environment variables before launching Claude Code:

```bash
# Windows (PowerShell)
$env:ANTHROPIC_BASE_URL = "https://api.x.ai"
$env:ANTHROPIC_API_KEY = "xai-your-key-here"

# Linux/Mac
export ANTHROPIC_BASE_URL="https://api.x.ai"
export ANTHROPIC_API_KEY="xai-your-key-here"
```

Or add to your global Claude Code settings (`~/.claude/settings.json`):
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.x.ai",
    "ANTHROPIC_API_KEY": "xai-your-key-here"
  }
}
```

#### Option C: Groq (Llama 3.1 405B)

```bash
# Windows (PowerShell)
$env:ANTHROPIC_BASE_URL = "https://api.groq.com/openai"
$env:ANTHROPIC_API_KEY = "gsk_your-groq-key-here"

# Linux/Mac
export ANTHROPIC_BASE_URL="https://api.groq.com/openai"
export ANTHROPIC_API_KEY="gsk_your-groq-key-here"
```

**Where to get API keys:**
- Anthropic: https://console.anthropic.com/settings/keys
- xAI: https://console.x.ai/
- Groq: https://console.groq.com/keys

### Step 5: Open the Project

```bash
cd aeroforge
claude   # Launch the AI agent in this directory
```

The agent reads `CLAUDE.md` for project rules and `cad/CAD_FRAMEWORK.md` for folder structure. It designs, models, validates, and commits everything automatically. You give design direction; it does the work.

### Step 6: Key Scripts

| Script | What It Does |
|--------|-------------|
| `scripts/rebuild_all_meshes.py` | Regenerates all print meshes (STEP -> STL -> ribs -> 3MF) |
| `scripts/render_all_mesh.py` | Generates 4-view renders for all components + assemblies |
| `scripts/build_hstab_left_v7.py` | Builds the H-Stab STEP model from parametric definition |

Run any script: `cd aeroforge && PYTHONPATH=. python scripts/<script>.py`

### Switching Providers Mid-Session

If you run out of tokens on one provider, switch by updating your environment:

```bash
# Switch to xAI
$env:ANTHROPIC_BASE_URL = "https://api.x.ai"
$env:ANTHROPIC_API_KEY = "xai-your-key"
claude  # Restart Claude Code
```

The agent state is preserved in the git history and CLAUDE.md -- a new session picks up exactly where the last one left off.

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| CAD Engine | [Build123d](https://github.com/gumyr/build123d) | Parametric 3D modeling |
| Dependency Graph | [NetworkX](https://networkx.org/) | Change propagation |
| Validation | [Pydantic](https://docs.pydantic.dev/) | Spec validation |
| FEM Analysis | FreeCAD + CalculiX | Structural analysis |
| CFD Analysis | OpenFOAM | Aerodynamics |
| Airfoil Analysis | xfoil | 2D polars |
| Slicer | OrcaSlicer (CLI) | Automated slicing |
| Target Printer | Bambu A1 / P1S | 256x256x256mm bed |

## Design Philosophy

A 3D printer doesn't care about complexity. This project exploits that:

- **Every rib is unique** - continuously blended airfoil profiles (not 2-3 stations like commercial kits)
- **Topology-optimized structure** - geodetic lattice, variable density, computed lightening patterns
- **AI-optimized everything** - airfoils, twist, planform, control sizing, transmitter programming
- **Cheap materials, complex geometry** - filament + carbon tubes + spruce. Under $60 in materials.

See [docs/philosophy.md](docs/philosophy.md) for the full rationale.

## Status

Early development - core framework built, specifications locked, building components.

## License

All rights reserved. License terms will be determined before public release.
The Text2CAD workflow and parametric design system may be subject to
specific licensing restrictions for commercial use.
