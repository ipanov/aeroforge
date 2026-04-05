---
trigger: /aeroforge
description: AeroForge aircraft design workflow. Activates for any aircraft design task — initializing projects, running design iterations, spawning aerodynamicist/structural agents, managing workflow steps, reviewing deliverables.
model: opus
tools: ["Bash", "Read", "Write", "Edit", "Grep", "Glob", "Agent", "WebSearch", "WebFetch"]
---

You are operating the AeroForge autonomous aircraft design system.

## Architecture

AeroForge uses a **hierarchical node tree** where each component and assembly
has its own design cycle. The workflow has two phases:

1. **Top-down design phase** — from the aircraft level, drill down through
   assemblies to components. Each node gets its own aero/structural cycle.
2. **Bottom-up implementation phase** — build 3D models from leaves up,
   assemble into parent assemblies.

### Node Types

| Type | Design Cycle | Examples |
|------|-------------|----------|
| **component** | Full cycle | Wing panel, elevator, fuselage nose |
| **assembly** | Full cycle | Wing assembly, H-stab assembly, the whole aircraft |
| **off_shelf** | None | Servo, battery, carbon rod, screw |

### Per-Node Design Cycle (7 steps)

```
AERO_PROPOSAL → STRUCTURAL_REVIEW → AERO_RESPONSE → CONSENSUS → DRAWING_2D → MODEL_3D → OUTPUT
```

- **OUTPUT** (not "mesh") — format determined by manufacturing provider
- Up to 3 agent rounds per node before user decides
- DRAWING_2D must be approved by user before MODEL_3D starts

### Project Phases (top level only)

```
REQUIREMENTS → RESEARCH → DESIGN → IMPLEMENTATION → VALIDATION → RELEASE
```

- **DESIGN gate**: ALL nodes must have approved 2D drawings before IMPLEMENTATION starts
- **IMPLEMENTATION order**: Leaves first (components), then assemblies, bottom-up
- **VALIDATION**: CFD + FEA on assembled top object only
- **VALIDATION cascade**: If changes needed, LLM decides which nodes to re-run

## Step 1: Read Current State

ALWAYS start by reading the workflow state:

```python
import sys; sys.path.insert(0, "D:/Repos/aeroforge")
from src.orchestrator.workflow_engine import WorkflowEngine
engine = WorkflowEngine()
state = engine.load_project()
print(engine.get_workflow_summary())
```

## Step 2: Determine Next Action

```python
action = engine.get_next_recommended_action()
print(action)
```

## Step 3: Execute

### Design steps — spawn agents:
```python
engine.start_step("wing", "AERO_PROPOSAL", agent="aerodynamicist")
# ... spawn aerodynamicist agent ...
engine.complete_step("wing", "AERO_PROPOSAL", output_files=["..."])
```

### User rejects deliverable:
```python
engine.reject_step("wing", "DRAWING_2D", reason="planform too rectangular",
                   rework_notes="make it elliptical")
```

### User gives feedback:
```python
engine.record_user_feedback("wing", "AERO_PROPOSAL", "higher aspect ratio")
```

### Approve drawing (gate for implementation):
```python
from src.orchestrator.state_manager import StateManager
sm = StateManager()
sm.approve_drawing("wing")

# Check if all drawings approved:
print(sm.check_design_phase_complete())
```

### Get implementation order (leaves first):
```python
order = sm.get_implementation_order()
# Returns: ["Wing_Panel_P1", "Wing_Panel_P2", ..., "Wing_Assembly", ..., "Iva_Aeroforge"]
```

### After validation, cascade changes:
```python
sm.invalidate_node("HStab_Assembly")  # Reset just this node
sm.invalidate_subtree("empennage")     # Reset node + all descendants
```

## Agent Configuration

Agents (aerodynamicist, structural-engineer) are parameterized per project.
Read the project's `aeroforge.yaml` for:
- Aircraft type and mission
- Manufacturing technique and tooling
- Materials
- Provider selections

The agent prompts in `.claude/agents/` provide the base role. The LLM
customizes behavior based on the project context — materials, tooling,
constraints are NOT hardcoded in the agent definitions.

## Providers

System-level (shared): `config/system_providers.yaml`
```python
print(engine.get_provider_status())
```

Project-level (per-project): `projects/{slug}/aeroforge.yaml`

## n8n Visual Dashboard

The n8n visual workflow is automatically synced on every state change.
It shows:
- **Project phases** as a row of colored sticky notes (green=done, yellow=active, gray=pending)
- **Active step banner** — prominently shows what node/step/agent is running right now
- **Component hierarchy** — grid of sticky notes (rows=components, columns=design steps)
- **Per-cell status** — color-coded with rejection counts, agent info
- **Validation section** — CFD and FEA cards with pass/fail
- **Convergence criteria** — checklist of met/unmet targets

When the component hierarchy is modified (nodes added/removed during RESEARCH),
the visual workflow is automatically rebuilt. The user sees this in the n8n editor
at **http://localhost:5678**.

**n8n is MANDATORY.** If `engine.load_project()` fails due to n8n unavailability,
STOP and report the error. Never silently proceed without n8n.

## Rules

1. **Read state before acting** — always check workflow_state.json
2. **Aircraft types are free-form** — decided by LLM, not an enum
3. **Spawn agents for design decisions** — don't make aero/structural choices yourself
4. **Update workflow state** — start_step before, complete_step after
5. **Hooks enforce quality** — if blocked, fix the issue
6. **Query RAG before design decisions**
7. **Errors: recover, don't crash** — retry with different approach
8. **n8n is mandatory** — hard stop if unavailable, never skip visual sync
