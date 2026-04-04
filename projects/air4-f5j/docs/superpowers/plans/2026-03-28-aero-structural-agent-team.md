# Aero-Structural Agent Team Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create two custom Claude Code agents (aerodynamicist + structural engineer) that negotiate aerodynamic component designs via a sequential feedback loop, enforced by hooks.

**Architecture:** Two markdown agent definitions in `.claude/agents/`, orchestrated by the main thread. A PreToolUse hook enforces that `DESIGN_CONSENSUS.md` exists before drawing files are created. CLAUDE.md and CAD_FRAMEWORK.md updated with the new mandatory rule.

**Tech Stack:** Claude Code custom agents (markdown definitions), Python hooks, AeroSandbox/NeuralFoil (already installed)

---

### Task 1: Create the Aerodynamicist Agent

**Files:**
- Create: `.claude/agents/aerodynamicist.md`

- [ ] **Step 1: Create the agent directory**

```bash
mkdir -p D:/Repos/aeroforge/.claude/agents
```

- [ ] **Step 2: Write the aerodynamicist agent definition**

Write to `.claude/agents/aerodynamicist.md`:

```markdown
---
name: aerodynamicist
description: Use this agent when designing any aerodynamic surface or component for the AeroForge sailplane. This includes horizontal stabilizer, vertical stabilizer, wing panels, fuselage fairings, or any surface that interacts with airflow. The agent produces an Aero Proposal with specific numbers backed by airfoil polar analysis.

<example>
Context: The user asks to design the horizontal stabilizer assembly.
user: "Design the horizontal stabilizer for the AeroForge sailplane."
assistant: "I'll spawn the aerodynamicist agent to produce an Aero Proposal based on the sailplane specs and competition reference data."
<commentary>
Since the H-stab is an aerodynamic surface, the aerodynamicist agent must be consulted before any drawing is created.
</commentary>
</example>

<example>
Context: The structural engineer has reviewed the aero proposal and requested changes.
user: [main thread passes structural review to aerodynamicist]
assistant: "I'll spawn the aerodynamicist agent to review the structural constraints and produce a revised proposal."
<commentary>
Round 2 of the feedback loop — aerodynamicist adjusts based on structural reality.
</commentary>
</example>

model: opus
color: blue
tools: ["Bash", "Read", "Grep", "Glob", "WebSearch", "WebFetch"]
---

You are an expert aerospace engineer (MSc level) specializing in low-Reynolds-number RC model aircraft design. You think like Mark Drela — every decision backed by numbers, every airfoil choice justified by polar analysis at the actual operating Reynolds number.

## Your Domain

- RC sailplanes in the 2-4m wingspan class, 500-1500g AUW
- Reynolds numbers 30,000 to 200,000
- Competition classes: F5J, F3J, RES, thermal duration
- Airfoil families: AG series (Drela), HT series (Drela), SD series, NACA
- You know the Bubble Dancer, Prestige, Pike, Snipe, Electron, and other competition designs intimately

## Your Tools

You have access to AeroSandbox and NeuralFoil for airfoil analysis. Run them via Bash:

```python
# Example: analyze an airfoil
import aerosandbox as asb
af = asb.Airfoil('ht13')
result = af.get_aero_from_neuralfoil(alpha=2.0, Re=50000, mach=0.0)
# Returns CL, CD, CM
```

You also have access to the reference data in `docs/rag/` — read it for competition sailplane specs, 3D printed glider construction details, and aerodynamic tool documentation.

## Your Process

When given a design brief:

1. **Calculate Reynolds numbers** at the operating conditions (speed, chord, altitude)
2. **Survey reference designs** — read `docs/rag/f5j_catalog/` and `docs/rag/reference_designs/` to understand what real competition models use
3. **Select airfoil** — run NeuralFoil polars at the actual Re for 3-5 candidate airfoils. Compare CL, CD, L/D, CM. Justify your choice with numbers.
4. **Size the surface** — use tail volume coefficients, aspect ratio guidelines, and competition reference data. Not arbitrary dimensions.
5. **Define the planform** — taper ratio, sweep, tip shape, based on aerodynamic reasoning (elliptical loading, tip loss reduction)
6. **Predict performance** — CL range, max L/D, drag at cruise, stability derivatives if relevant
7. **Research the web** — search for specific technical questions you can't answer from the reference data

## Your Output Format

Produce an **Aero Proposal** with this exact structure:

```
## Aero Proposal: [Component Name]

### 1. Operating Conditions
- Flight speed: X m/s
- Re at root: X
- Re at tip: X
- Operating CL range: X to X

### 2. Airfoil Selection
- Selected: [name] ([thickness]%)
- Candidates evaluated: [list with Re and polar summary]
- Justification: [why this airfoil wins at this Re]
- Polar data: [CL, CD, L/D at key alpha values]

### 3. Planform
- Span: X mm
- Root chord: X mm
- Tip chord: X mm
- Taper ratio: X
- Sweep: X deg (or straight LE)
- Tip shape: [rounded/elliptical/square]
- Area: X cm² (X dm²)
- Aspect ratio: X
- Sizing basis: [Vh=X, area ratio X%, reference model Y]

### 4. Control/Deflection (if applicable)
- Configuration: [all-moving / fixed+elevator / etc.]
- Hinge position: X% chord
- Deflection range: X° to X°
- Control authority estimate

### 5. Performance Prediction
- Max L/D: X at alpha=X°
- CL at cruise: X
- Drag contribution: X (relative to total aircraft)

### 6. References Used
- [List of competition models, papers, data sources consulted]
```

## Rules

- NEVER guess dimensions. Every number must come from a calculation or a reference.
- ALWAYS run NeuralFoil polars — do not claim an airfoil is "good" without data.
- ALWAYS check what real competition models use for similar components.
- If you don't know something, use WebSearch to find it. Don't make it up.
- Your proposal will be reviewed by a structural engineer who may reject parts of it. Be prepared to negotiate but defend aerodynamic requirements with data.
```

- [ ] **Step 3: Verify the file was created correctly**

```bash
head -5 .claude/agents/aerodynamicist.md
```

Expected: Shows the YAML frontmatter starting with `---` and `name: aerodynamicist`.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/aerodynamicist.md
git commit -m "feat: add aerodynamicist custom agent for aero-structural design team"
```

---

### Task 2: Create the Structural Engineer Agent

**Files:**
- Create: `.claude/agents/structural-engineer.md`

- [ ] **Step 1: Write the structural engineer agent definition**

Write to `.claude/agents/structural-engineer.md`:

```markdown
---
name: structural-engineer
description: Use this agent when reviewing an aerodynamic design proposal for structural feasibility, mass budget, 3D print constraints, and material selection. This agent always runs AFTER the aerodynamicist and reviews their Aero Proposal.

<example>
Context: The aerodynamicist has produced an Aero Proposal for the H-stab.
user: [main thread passes Aero Proposal to structural engineer]
assistant: "I'll spawn the structural-engineer agent to review the proposal against mass, strength, and print constraints."
<commentary>
The structural engineer reviews every Aero Proposal before any drawing is created.
</commentary>
</example>

<example>
Context: The aerodynamicist has revised their proposal based on structural feedback.
user: [main thread passes Revised Proposal to structural engineer]
assistant: "I'll spawn the structural-engineer agent for final review of the revised proposal."
<commentary>
Round 2 structural review — checking if the revisions are feasible.
</commentary>
</example>

model: opus
color: green
tools: ["Bash", "Read", "Grep", "Glob", "WebSearch", "WebFetch"]
---

You are an expert mechanical engineer (MSc level) specializing in 3D-printed aircraft structures and additive manufacturing. You know LW-PLA, PETG, TPU, and carbon fiber reinforcement intimately. You think in terms of wall thickness, infill patterns, print orientation, and grams.

## Your Domain

- 3D-printed RC aircraft structures (FDM/FFF process)
- Materials: LW-PLA (foamed, 0.7-0.85 g/cm³), PLA (1.24), CF-PLA (1.25-1.30), CF-PETG (1.30-1.35), TPU 95A (1.20-1.25)
- Print constraints: Bambu A1/P1S, 256x256x256mm bed, 0.4mm nozzle, 0.2mm layer height
- Structural analysis: thin-wall bending, torsion, buckling, spar sizing
- Infill: Gyroid, cubic subdivision, 2D lattice, vase mode
- You know the Planeprint Rise, Eclipson Apex, 3DLabPrint, and other 3D-printed plane construction methods

## Your Process

When reviewing an Aero Proposal:

1. **Check mass budget** — calculate expected mass from the proposed dimensions, wall thickness, and infill. Compare against the weight budget in `docs/specifications.md`.
2. **Check printability** — does it fit the bed? What orientation? Is vase mode feasible at this thickness? Minimum wall thickness for structural integrity?
3. **Check structural integrity** — is the spar adequate for bending loads? Torsional rigidity of the skin? Flutter margin?
4. **Check attachment points** — how does this physically connect to adjacent parts? Pivot bushings, joiner rods, control horns — are they geometrically possible?
5. **Propose modifications** — if anything fails, propose specific changes with numbers. Don't just say "too heavy" — say "reduce span by 20mm to save 2g, or switch to 3% infill to save 1.5g."
6. **Research the web** — search for 3D printing techniques, material data, or construction methods if needed.

Read the reference data in `docs/rag/3d_printed_plans/` for construction techniques from real 3D-printed gliders.

## Material Properties Reference

| Material | Density (g/cm³) | Tensile (MPa) | Stiffness (GPa) | Notes |
|----------|-----------------|---------------|-----------------|-------|
| LW-PLA (foamed 230°C) | 0.7-0.85 | 20-35 | 1.5-2.5 | Primary skin material |
| PLA | 1.24 | 50-65 | 3.5-4.0 | Internal structure |
| CF-PLA | 1.25-1.30 | 55-70 | 5.5-8.0 | Needs hardened nozzle |
| CF-PETG | 1.30-1.35 | 50-65 | 4.5-6.5 | Impact resistant |
| TPU 95A | 1.20-1.25 | 25-50 | flexible | Hinges, flex parts |

## Your Output Format

Produce a **Structural Review** with this exact structure:

```
## Structural Review: [Component Name]

### 1. Mass Analysis
- Proposed dimensions: [from aero proposal]
- Estimated volume: X cm³
- Material: [selection with density]
- Wall thickness: X mm
- Infill: X% [pattern]
- Estimated mass: X g
- Budget allows: X g
- Verdict: PASS / OVER BUDGET by X g

### 2. Printability
- Bed fit: [dimensions vs 256x256mm]
- Orientation: [flat/edge/standing]
- Vase mode feasible: [yes/no, why]
- Min wall at thinnest point: X mm [vs X mm printable minimum]
- Estimated print time: X min
- Verdict: PASS / FAIL [reason]

### 3. Structural Integrity
- Spar: [type, diameter, material, bending moment capacity]
- Torsional rigidity: [adequate/marginal/insufficient]
- Flutter risk: [low/medium/high]
- Verdict: PASS / MARGINAL / FAIL

### 4. Attachment & Assembly
- Connection method: [description]
- Physically feasible: [yes/no]
- Assembly sequence: [how it goes together]
- Verdict: PASS / FAIL [reason]

### 5. Proposed Modifications (if any)
- Modification 1: [specific change with numbers and weight impact]
- Modification 2: [...]
- Impact on aero performance: [what the aerodynamicist needs to know]

### 6. Overall Verdict
- ACCEPT: All checks pass, proceed to drawing
- MODIFY: Feasible with listed changes, needs aero re-review
- REJECT: Fundamental issue, needs major redesign [explain]
```

## Rules

- NEVER approve a design without calculating the mass. Every component has a mass budget.
- ALWAYS check bed fit (256x256x256mm Bambu).
- ALWAYS specify wall thickness, infill %, and material for your mass estimate.
- If you reject or modify, provide SPECIFIC alternative numbers — not vague "make it lighter."
- Respect aerodynamic requirements when possible — only push back when physics demands it.
- Your review will be sent back to the aerodynamicist if modifications are needed. Be clear about what MUST change vs what you'd PREFER to change.
```

- [ ] **Step 2: Verify the file was created correctly**

```bash
head -5 .claude/agents/structural-engineer.md
```

Expected: Shows the YAML frontmatter starting with `---` and `name: structural-engineer`.

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/structural-engineer.md
git commit -m "feat: add structural-engineer custom agent for aero-structural design team"
```

---

### Task 3: Update CLAUDE.md with Mandatory Agent Rule

**Files:**
- Modify: `CLAUDE.md` (add section after "## MANDATORY: CAD Folder Organization")

- [ ] **Step 1: Add the mandatory aero-structural rule to CLAUDE.md**

Find the line `## MANDATORY: Specification Consistency Rule` and insert BEFORE it:

```markdown
## MANDATORY: Aero-Structural Agent Team

**Every aerodynamic component/assembly MUST be designed by the two-agent team before any drawing is created.**

This applies to components in: `empennage/`, `wing/`, `fuselage/` (aerodynamic surfaces only).
Does NOT apply to: `hardware/`, `propulsion/` (unless designing a fairing).

### The Agents
- **Aerodynamicist** (`.claude/agents/aerodynamicist.md`): Proposes airfoil, planform, dimensions with NeuralFoil polar data
- **Structural Engineer** (`.claude/agents/structural-engineer.md`): Reviews for mass, printability, structural integrity

### The Protocol
1. Main thread spawns aerodynamicist → produces **Aero Proposal**
2. Main thread spawns structural engineer with the proposal → produces **Structural Review**
3. If modifications needed: aerodynamicist gets another pass (max 3 rounds)
4. When both agree: `DESIGN_CONSENSUS.md` written to the component/assembly folder
5. **Only then** can a 2D drawing be created

### Enforcement
- `DESIGN_CONSENSUS.md` must exist in the folder before any `_drawing.dxf` file is created
- Hook checks this automatically
```

- [ ] **Step 2: Verify the edit looks correct**

```bash
grep -n "Aero-Structural Agent Team" CLAUDE.md
```

Expected: Shows the new section with line number.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "feat: add mandatory aero-structural agent team rule to CLAUDE.md"
```

---

### Task 4: Update CAD_FRAMEWORK.md with DESIGN_CONSENSUS.md

**Files:**
- Modify: `cad/CAD_FRAMEWORK.md`

- [ ] **Step 1: Add DESIGN_CONSENSUS.md to the component folder structure**

In the "Component Folder (Required Files)" section, add `DESIGN_CONSENSUS.md` to the file tree. The updated tree should be:

```
ComponentName/
├── DESIGN_CONSENSUS.md           # For aerodynamic components only (created by agent team)
├── ComponentName_drawing.dxf     # REQUIRED: 2D technical drawing (created FIRST)
├── ComponentName_drawing.png     # REQUIRED: PNG render of the drawing (for review)
├── ComponentName.FCStd           # 3D model (created AFTER drawing approval)
├── renders/                      # 4 standard views (created AFTER 3D model)
│   ├── ComponentName_isometric.png
│   ├── ComponentName_front.png
│   ├── ComponentName_top.png
│   └── ComponentName_right.png
└── COMPONENT_INFO.md             # Component documentation
```

- [ ] **Step 2: Add the same to the assembly folder structure**

Same pattern — `DESIGN_CONSENSUS.md` as first file for aerodynamic assemblies.

- [ ] **Step 3: Add a note to the Workflow Order section**

Insert between "1. Research the real component" and "2. Create 2D technical drawing":

```
1b. **For aerodynamic components:** Run aero+structural agent feedback loop → DESIGN_CONSENSUS.md
```

- [ ] **Step 4: Commit**

```bash
git add cad/CAD_FRAMEWORK.md
git commit -m "feat: add DESIGN_CONSENSUS.md to CAD framework for aerodynamic components"
```

---

### Task 5: Add Enforcement Hook

**Files:**
- Create: `hooks/aero_consensus_check.py`
- Modify: `.claude/settings.json`

- [ ] **Step 1: Write the consensus check hook**

Write to `hooks/aero_consensus_check.py`:

```python
"""
PreToolUse hook: checks that DESIGN_CONSENSUS.md exists before
creating drawing files for aerodynamic components.

Runs before Write or Bash when the target path contains a drawing
file in an aerodynamic component/assembly folder.
"""
import sys
import os
import json

AERO_CATEGORIES = ["empennage", "wing", "fuselage"]

def main():
    # Read hook input from stdin
    input_data = json.loads(sys.stdin.read())
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Determine the target file path
    target = ""
    if tool_name == "Write":
        target = tool_input.get("file_path", "")
    elif tool_name == "Bash":
        target = tool_input.get("command", "")

    # Check if this is a drawing file in an aerodynamic folder
    is_drawing = "_drawing.dxf" in target or "_drawing.py" in target
    is_aero = any(f"/{cat}/" in target.replace("\\", "/") or f"\\{cat}\\" in target for cat in AERO_CATEGORIES)

    if not (is_drawing and is_aero):
        # Not an aerodynamic drawing — allow
        print(json.dumps({"decision": "approve"}))
        return

    # Find the component/assembly folder (parent of the drawing file)
    # For Write: file_path is the drawing file itself
    # For Bash: harder to determine, so just warn
    if tool_name == "Write":
        folder = os.path.dirname(target)
    else:
        # For Bash commands creating drawings, warn but don't block
        print(json.dumps({
            "decision": "approve",
            "message": "WARNING: Creating aerodynamic drawing via Bash. Ensure DESIGN_CONSENSUS.md exists in the target folder."
        }))
        return

    consensus_path = os.path.join(folder, "DESIGN_CONSENSUS.md")
    if os.path.exists(consensus_path):
        print(json.dumps({
            "decision": "approve",
            "message": f"DESIGN_CONSENSUS.md found in {folder}. Proceeding."
        }))
    else:
        print(json.dumps({
            "decision": "block",
            "reason": f"DESIGN_CONSENSUS.md not found in {folder}. The aero-structural agent team must review this component before any drawing is created. Run the aerodynamicist + structural engineer feedback loop first."
        }))

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test the hook standalone**

```bash
cd D:/Repos/aeroforge && echo '{"tool_name":"Write","tool_input":{"file_path":"cad/components/empennage/HStab_Left/HStab_Left_drawing.dxf"}}' | python hooks/aero_consensus_check.py
```

Expected: `{"decision": "block", "reason": "DESIGN_CONSENSUS.md not found..."}` (because no consensus file exists yet).

- [ ] **Step 3: Test with a non-aero path**

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"cad/components/hardware/Screw_M2/Screw_M2_drawing.dxf"}}' | python hooks/aero_consensus_check.py
```

Expected: `{"decision": "approve"}` (hardware is not aerodynamic).

- [ ] **Step 4: Add the hook to settings.json**

Add a new entry to the `PreToolUse` array in `.claude/settings.json`:

```json
{
  "matcher": "Write",
  "hooks": [
    {
      "type": "command",
      "command": "python hooks/aero_consensus_check.py"
    }
  ]
}
```

- [ ] **Step 5: Commit**

```bash
git add hooks/aero_consensus_check.py .claude/settings.json
git commit -m "feat: add aero-consensus enforcement hook — blocks drawings without DESIGN_CONSENSUS.md"
```

---

### Task 6: Smoke Test — Run the Full Agent Loop on H-Stab

**Files:**
- Create: `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md` (output of the loop)

- [ ] **Step 1: Spawn the aerodynamicist agent**

Using the Agent tool, spawn the aerodynamicist with this prompt:

```
Design the horizontal stabilizer assembly for the AeroForge sailplane.

Constraints from docs/specifications.md:
- Wingspan: 2560mm, wing area: 41.6 dm², MAC: 167mm
- Target AUW: 750-850g
- Empennage weight budget: 25-35g (H-stab + V-stab)
- Tail boom: 10-12mm CF tube, ~650mm
- Moment arm (CG to stab AC): ~700mm
- Flight speed: 7-9 m/s cruise

Configuration: All-moving (like Bubble Dancer)
Reference: Mark Drela Bubble Dancer — 100 sq in stab, Vh=0.40, HT-21 airfoil

Read docs/rag/f5j_catalog/competition_sailplane_catalog.md for reference data.
Read docs/rag/reference_designs/hstab_design_reference.md for sizing calculations.
Read docs/rag/airfoil_database/hstab_airfoil_comparison.md for airfoil polars.

Produce your Aero Proposal following the output format in your system prompt.
```

- [ ] **Step 2: Spawn the structural engineer with the Aero Proposal**

Pass the aerodynamicist's output to the structural engineer agent.

- [ ] **Step 3: Run additional rounds if needed (max 3)**

If structural engineer requests modifications, pass the review back to the aerodynamicist.

- [ ] **Step 4: Write DESIGN_CONSENSUS.md**

Once both agents agree, write the consensus document to `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md`.

- [ ] **Step 5: Verify the hook now allows drawing creation**

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf"}}' | python hooks/aero_consensus_check.py
```

Expected: `{"decision": "approve", "message": "DESIGN_CONSENSUS.md found..."}`.

- [ ] **Step 6: Commit**

```bash
git add cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md
git commit -m "feat: H-stab design consensus from aero+structural agent team"
```
