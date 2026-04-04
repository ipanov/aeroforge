---
trigger: /aeroforge-init
description: Initialize a new AeroForge project. Creates the project directory, runs hardware detection, sets up providers, and prepares the workflow state. Use this when starting a new aircraft design project.
model: opus
tools: ["Bash", "Read", "Write", "Edit", "Grep", "Glob", "WebSearch", "WebFetch"]
---

You are initializing a new AeroForge project. Guide the user through project
setup by having a conversation — do NOT use CLI commands or interactive prompts.

## Initialization Flow

### 1. Detect Hardware

Run hardware detection to understand what analysis tools are available:

```python
import sys; sys.path.insert(0, "D:/Repos/aeroforge")
from src.providers.hardware import detect_hardware
hw = detect_hardware()
print(hw.summary())
```

Report what was found (GPU, installed software, printers).

### 2. Gather Project Information

Ask the user (or determine from context) the following. Do NOT use hardcoded
aircraft type enums — the type is a free-form string:

- **Project name**: Human-readable name (e.g., "Paper Plane MVP", "F5J Thermal Sailplane")
- **Project slug**: Directory name (e.g., "paper-plane", "air4-f5j")
- **Mission prompt**: What is being designed and why
- **Aircraft type**: Free-form string — "paper airplane", "thermal sailplane", "interceptor drone", etc.
  The ONLY constraint: heavier-than-air, exposed to airflow.
- **Project scope**: "component" (single part) or "assembly" (multiple parts) or "aircraft" (full vehicle)
- **Top object name**: The top-level assembly or component name
- **Manufacturing technique**: What tooling/technique? (FDM 3D printing, manual, CNC, etc.)
- **Materials**: What materials? (LW-PLA, paper, carbon fiber, etc.)

### 3. Create the Project

```python
from src.orchestrator.project_manager import ProjectManager
pm = ProjectManager()

# Create project directory with config
settings = {
    "project": {
        "project_name": "...",
        "design_family": "...",
        "current_round": "R1",
        "next_round": "R2",
        "heavier_than_air": True,
        "project_scope": "...",
        "top_object": "...",
        "aircraft_type": "...",  # FREE-FORM STRING
        "mission_prompt": "...",
        "selected_tooling": "...",
        "manufacturing_strategy": [...],
        "material_strategy": [...],
        "production_strategy": [...],
        "output_artifacts": [...],
    },
    "providers": {
        "manufacturing": {"selected": "..."},  # Project-level
        "slicer": {"selected": "..."},          # Project-level
    },
}
pm.create("project-slug", settings)
pm.switch("project-slug")
```

### 4. Determine Sub-Assemblies

Based on the aircraft type and scope, determine what sub-assemblies exist.
For simple projects (paper plane), there may be just ONE component.
For complex projects (F5J sailplane), there are many sub-assemblies.

You can use reference templates as inspiration:
```python
from src.orchestrator.aircraft_types import REFERENCE_TEMPLATES, list_types
# These are REFERENCE ONLY — modify freely
print(list_types())
```

### 5. Create Workflow Profile

Write the workflow profile section to `aeroforge.yaml`:

```python
# Add workflow profile to the project config
import yaml
config_path = pm.get_settings_path()
with open(config_path) as f:
    config = yaml.safe_load(f)

config["workflow_profile"] = {
    "aircraft_type": "...",
    "project_scope": "...",
    "top_object_name": "...",
    "round_label": "R1",
    "sub_assemblies": [
        {
            "name": "...",
            "level": 1,
            "analysis_scope": "aero_structural",  # or "structural_only", "none"
            "dependencies": [],
            "deliverables": [...],
        }
    ],
    "validation_criteria": {...},
}

with open(config_path, "w") as f:
    yaml.safe_dump(config, f, sort_keys=False)
```

### 6. Initialize Workflow State

```python
from src.orchestrator.workflow_engine import WorkflowEngine
engine = WorkflowEngine()
state = engine.create_project_from_profile_file(
    config_path, config["project"]["project_name"],
    metadata={"project_code": config["project"]["design_family"]},
)
print(engine.get_workflow_summary())
```

### 7. Set Up System Providers

If not already configured, suggest system providers based on hardware:

```python
# Auto-suggest based on detected hardware
suggestions = {}
if hw.cuda_available:
    suggestions["cfd"] = {"selected": "su2_cuda"}
else:
    suggestions["cfd"] = {"selected": "su2_cpu"}

if "freecad" in hw.installed_software:
    suggestions["fea"] = {"selected": "freecad_calculix"}
else:
    suggestions["fea"] = {"selected": "mock"}

suggestions["airfoil"] = {"selected": "neuralfoil"}

pm.save_system_providers(suggestions)
```

### 8. Populate RAG (Optional)

If the project benefits from research data:
```python
from src.rag import populate_rag
populate_rag(
    project_code="...",
    mission_prompt="...",
    web_queries=["relevant search terms"],
)
```

### 9. Show Summary

Display the initialized project status and tell the user they can now
start designing with `/aeroforge` or by just describing what they want.

## Rules

1. **NEVER use hardcoded aircraft type enums** as the primary type
2. **ALWAYS detect hardware** before suggesting providers
3. **ALWAYS let the user confirm** before creating the project
4. **The project directory structure is created automatically** by ProjectManager
5. **System providers are shared** — only configure if not already set up
6. **Project providers are per-project** — always configure manufacturing/slicer
