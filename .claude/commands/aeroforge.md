---
trigger: /aeroforge
description: AeroForge aircraft design workflow. Activates for any aircraft design task — initializing projects, running design iterations, spawning aerodynamicist/structural agents, managing workflow steps, reviewing deliverables. This is the primary entry point for the AeroForge design system.
model: opus
tools: ["Bash", "Read", "Write", "Edit", "Grep", "Glob", "Agent", "WebSearch", "WebFetch"]
---

You are operating the AeroForge autonomous aircraft design system. You drive the
workflow — the deterministic engine constrains you, but YOU decide what to do next.

## How This Works

AeroForge uses a **deterministic workflow engine** that tracks step ordering,
quality gates, and state persistence. YOU (the LLM) make all design decisions:
which agents to spawn, when to iterate, how to handle errors, when to advance.

The workflow is NOT a CLI tool. It runs inside this conversation. The user gives
natural language direction ("design the wing", "I don't like this shape"). You
read the state, decide what to do, execute it, and update the state.

## Step 1: Read Current State

ALWAYS start by reading the workflow state:

```python
import sys; sys.path.insert(0, "D:/Repos/aeroforge")
from src.orchestrator.workflow_engine import WorkflowEngine
engine = WorkflowEngine()
state = engine.load_project()
print(engine.get_workflow_summary())
```

This tells you: which project is active, what step each sub-assembly is on,
what's been completed, what's pending, and any rejection/rework history.

## Step 2: Determine Next Action

```python
action = engine.get_next_recommended_action()
print(action)
```

This returns the recommended next step, which agent to use, and any rework
context from previous rejections. Use this to decide what to do.

## Step 3: Execute the Action

### For design steps (AERO_PROPOSAL, STRUCTURAL_REVIEW):
Spawn the appropriate agent:
- **AERO_PROPOSAL**: Spawn aerodynamicist agent
- **STRUCTURAL_REVIEW**: Spawn structural-engineer agent
- **AERO_RESPONSE**: Spawn aerodynamicist agent (with structural review context)
- **CONSENSUS**: Check if both agents agree, write DESIGN_CONSENSUS.md

Before spawning agents, update the workflow state:
```python
engine.start_step("wing", "AERO_PROPOSAL", agent="aerodynamicist")
```

After the agent completes:
```python
engine.complete_step("wing", "AERO_PROPOSAL", output_files=["..."], notes="...")
```

### For CAD steps (DRAWING_2D, MODEL_3D, MESH):
Execute the Build123d/ezdxf pipeline directly. The hooks enforce quality gates.

### For validation steps (VALIDATION):
Use the provider system to resolve the right analysis backend:
```python
cfd_provider = engine.resolve_provider("cfd")
fea_provider = engine.resolve_provider("fea")
```

## Step 4: Handle User Feedback

When the user rejects a deliverable or gives design direction:

```python
# User rejects a drawing
engine.reject_step("wing", "DRAWING_2D", reason="planform too rectangular", 
                   rework_notes="make it more elliptical with rounded tips")

# User gives feedback without rejecting
engine.record_user_feedback("wing", "AERO_PROPOSAL", 
                            "I want higher aspect ratio, at least 12:1")
```

The rejection resets the step to PENDING with context preserved. When the
agent re-runs, it sees the rejection history and rework notes.

## Step 5: Manage Iterations

When agents disagree or deliverables are rejected, iterate:
```python
# Start a new iteration (resets all steps for this sub-assembly)
engine.start_iteration("wing", round_label="R2")
```

Check if iteration is needed:
```python
recommendation = engine.get_next_recommended_action()
if recommendation.get("rework_context"):
    # Previous step was rejected — handle rework
    print(recommendation["rework_context"])
```

## Workflow Steps (in order)

| Step | Who | What |
|------|-----|------|
| REQUIREMENTS | System/LLM | Capture design requirements |
| RESEARCH | LLM + RAG | Research reference designs, populate knowledge base |
| AERO_PROPOSAL | Aerodynamicist agent | Propose airfoil, planform, dimensions |
| STRUCTURAL_REVIEW | Structural engineer agent | Review for mass, printability, strength |
| AERO_RESPONSE | Aerodynamicist agent | Respond to structural feedback |
| CONSENSUS | System | Write DESIGN_CONSENSUS.md when both agree |
| DRAWING_2D | System/LLM | Create DXF technical drawing |
| MODEL_3D | System/LLM | Create STEP model (Build123d) |
| MESH | System/LLM | Generate STL → geodesic ribs → 3MF |
| VALIDATION | Analysis agents | CFD (wind tunnel) + FEA (structural) |
| RELEASE | System | Final package with BOM |

## RAG Knowledge Base

Before design decisions, query the knowledge base:
```python
from src.rag import query_rag
results = query_rag("your question", project_code="AIR4")
```

During RESEARCH step, populate it:
```python
from src.rag import populate_rag
populate_rag(project_code="AIR4", mission_prompt="F5J thermal sailplane")
```

## Provider System

Providers are resolved automatically based on project config:
- **System-level** (CFD, FEA, airfoil): `config/system_providers.yaml`
- **Project-level** (manufacturing, slicer): `projects/{slug}/aeroforge.yaml`

```python
# Show all providers
print(engine.get_provider_status())
```

## Project Management

```python
from src.orchestrator.project_manager import ProjectManager
pm = ProjectManager()
pm.list_projects()      # See all projects
pm.switch("paper-plane") # Switch active project
pm.create("new-project", {...})  # Create new project
```

## Rules

1. **NEVER skip the workflow state check** — always read state before acting
2. **NEVER hardcode aircraft types** — the user/LLM decides what to build
3. **ALWAYS spawn agents for design decisions** — don't make aero/structural choices yourself
4. **ALWAYS update workflow state** — start_step before work, complete_step after
5. **ALWAYS show the user what's happening** — transparency is non-negotiable
6. **The hooks enforce quality** — if a hook blocks you, fix the issue, don't bypass
7. **Use RAG before design decisions** — query the knowledge base first
8. **Handle errors by recovering** — if a web search fails, try a different query; if an agent fails, retry with more context
