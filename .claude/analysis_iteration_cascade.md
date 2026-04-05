# AeroForge Workflow Engine: Iteration Tracking & Validation Cascade Analysis

## Executive Summary

The AeroForge workflow engine ALREADY TRACKS iterations and rounds:
- **Iterations**: Fully tracked via node["iteration"] (per-node counter)
- **Agent rounds**: Fully tracked via node["agent_round"] (negotiation rounds within iteration)  
- **Round label**: Stored as node["current_round_label"] ("R1", "R2", etc.)

MISSING FEATURES:
1. **Validation cascade**: No automatic mechanism to reset affected nodes when CFD/FEA fails
2. **Deliverable naming**: Files use only rounds (AERO_PROPOSAL_WING_R1.md) not iteration+rounds (AERO_PROPOSAL_WING_I1_R1.md)

---

## CURRENT STATE: Iteration & Round Tracking

### 1. Per-Node State Structure
File: src/orchestrator/state_manager.py, lines 210-232

Each node stores:
- iteration: int = 1 (design cycle iteration: I1, I2, I3...)
- agent_round: int = 0 (negotiation round within iteration: R1, R2, R3...)
- current_round_label: str = f"R{iteration}" (user-friendly label)

### 2. Per-Step History
File: src/orchestrator/state_manager.py, lines 178-190

Each step stores:
- status: pending/running/done/failed/skipped
- output_files: list of deliverable file paths
- history: list of rejection and feedback entries

### 3. Rejection Flow (reject_step)
File: src/orchestrator/state_manager.py, lines 924-968

When a step is rejected:
1. Appends entry to step.history[] with reason + rework_notes
2. Resets step to PENDING (clears started_at, completed_at, agent)
3. Sets node.current_design_step back to rejected step
4. DOES NOT increment iteration (only step-level rework)

### 4. Iteration Management (start_new_iteration)
File: src/orchestrator/state_manager.py, lines 997-1020

When a new iteration starts:
1. node["iteration"] += 1
2. node["current_round_label"] = round_label or f"R{iteration}"
3. node["agent_round"] = 0 (reset agent rounds)
4. node["design_cycle"] = _new_design_cycle() (all steps back to PENDING)
5. node["current_design_step"] = AERO_PROPOSAL

Called manually via WorkflowEngine.start_iteration() - NOT automatically on validation failure

### 5. Active Runs Track Iteration & Round
File: src/orchestrator/state_manager.py, lines 828-844

When step starts, entry added to state["active_runs"]:
- "node": name
- "step": step_name
- "agent": agent_name
- "iteration": node["iteration"]
- "round_label": node["current_round_label"]
- "started_at": timestamp

So active_runs already track I+R info!

---

## VALIDATION FLOW: Where Cascade Is Missing

File: src/orchestrator/workflow_engine.py, lines 527-651

### Complete CFD (553-570)
Method: complete_cfd(passed: bool, results_files=None, notes="")
- If passed=True: cfd["status"] = DONE
- If passed=False: cfd["status"] = FAILED
- NO cascade logic - doesn't reset affected nodes

### Complete FEA (571-587)
Method: complete_fea(passed: bool, results_files=None, notes="")
- If passed=True: fea["status"] = DONE
- If passed=False: fea["status"] = FAILED
- NO cascade logic - doesn't reset affected nodes

### Check Convergence (589-597)
Method: check_convergence()
- Reads validation["convergence"] dict
- Returns {criteria: {...}, all_met: bool}
- Does NOT identify which nodes caused failure

### LLM Recommendation (625-653)
When CFD and FEA both DONE:
- If all_met=True: return None (success)
- If all_met=False: return {"action": "convergence_not_met", "failed_criteria": [...]}
- LLM must manually identify affected nodes and call start_iteration()

### THE PROBLEM
1. **No affected-node detection** - system can't identify which nodes caused validation failure
2. **No automatic cascade** - complete_cfd/fea(passed=False) just marks FAILED
3. **Manual repair required** - LLM must manually call start_new_iteration() on affected nodes

---

## DELIVERABLE NAMING: Currently Inconsistent

### What Exists
Location: projects/air4-f5j/cad/assemblies/

Examples:
- AERO_PROPOSAL_WING_R1.md (round 1 only)
- AERO_PROPOSAL_WING_R4_R1.md (likely I4_R1)
- STRUCTURAL_REVIEW_WING_R1.md

### What's Needed (Per User Request)
- AERO_PROPOSAL_I1_R1.md (iteration 1, agent round 1)
- AERO_PROPOSAL_I1_R2.md (iteration 1, agent round 2)
- AERO_PROPOSAL_I2_R1.md (iteration 2 after cascade, agent round 1)
- STRUCTURAL_REVIEW_I1_R1.md

### Current Implementation
File: src/orchestrator/state_manager.py, lines 849-873

complete_step() stores output_files as raw list:
- record["output_files"] = output_files (raw paths)
- NO naming convention validation
- NO helper to generate compliant names
- LLM responsible for naming

---

## Invalidation Methods (Exist But Not Auto-Triggered)

### invalidate_node (746-764)
Resets node's design cycle back to AERO_PROPOSAL
- design_cycle = _new_design_cycle() (all steps PENDING)
- current_design_step = AERO_PROPOSAL
- agent_round = 0
- DOES NOT increment iteration

This is for within-iteration repair, not post-validation cascade.

### invalidate_subtree (766-785)
Same as above but for node and all descendants.

---

## Summary: What Works & What's Broken

| Feature | Status | Location | Notes |
|---------|--------|----------|-------|
| Iteration counter | WORKING | node["iteration"] | Line 226, 1001 |
| Agent round counter | WORKING | node["agent_round"] | Line 227, 829, 1003 |
| Round label | WORKING | node["current_round_label"] | Line 1002 |
| Step rejection | WORKING | reject_step() | Line 924-968 |
| Node invalidation | WORKING | invalidate_node() | Line 746-764 |
| Active run tracking | WORKING | active_runs[] | Line 828-844 |
| Validation cascade | MISSING | workflow_engine.py | No auto-invalidation on CFD/FEA fail |
| Deliverable naming | MISSING | state_manager.py | No helper for STEP_I{i}_R{r}.md format |

---

## Key Code Locations

**Iteration tracking**:
- _new_node(): state_manager.py:210-232
- start_new_iteration(): state_manager.py:997-1020
- start_iteration(): workflow_engine.py:261-265

**Round tracking**:
- node["agent_round"] increment: state_manager.py:829
- run_entry creation: state_manager.py:832-844

**Rejection/history**:
- reject_step(): state_manager.py:924-968
- get_step_history(): state_manager.py:992-995

**Validation workflow**:
- complete_cfd(): workflow_engine.py:553-570
- complete_fea(): workflow_engine.py:571-587
- check_convergence(): workflow_engine.py:589-597

**Deliverables storage**:
- complete_step(): state_manager.py:849-873

