## Summary

- what changed
- why it changed
- which workflow or project requirement it addresses

## Verification

- [ ] `python -m pytest tests/test_bom.py tests/test_bom_sync.py tests/test_orchestrator_workflow.py -q`
- [ ] workflow/dashboard behavior checked when relevant
- [ ] BOM/procurement synchronization checked when relevant

## Review Notes

- active branch and merge target confirmed
- user/LLM decisions remain profile-driven, not hardcoded in deterministic logic
- deliverable-triggered hooks and guardrails updated when workflow behavior changed
