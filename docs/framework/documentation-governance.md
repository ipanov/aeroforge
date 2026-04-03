# Documentation Governance

## Source of Truth

`docs/` is the canonical source of truth for documentation in this repository.

The GitHub wiki is a curated published view of selected pages, not an
independent knowledge base. The repo-managed wiki publishing source lives under
`wiki/`.

## Classification Rule

Use these categories when adding or editing docs:

- `Framework docs`
  - generic behavior
  - orchestration
  - initialization
  - workflow
  - monitoring
  - BOM and procurement
- `Example project docs`
  - AIR4 or other concrete project instances
  - project-specific assumptions and accepted geometry
- `Reference and research docs`
  - catalogs
  - benchmarks
  - regulations
  - historical investigations
  - vendor notes

## Maintenance Workflow

Update framework docs when:

- deterministic workflow behavior changes
- the initialization boundary changes
- monitoring or hook behavior changes
- BOM/procurement synchronization rules change

Update example docs when:

- a specific project consensus changes
- the current example program changes round or scope

Update the wiki when:

- canonical framework docs change materially
- example-project onboarding needs to reflect a new baseline

Use `scripts/publish_wiki.ps1` to copy the repo-managed wiki pages into a local
clone of the GitHub wiki repository before publishing.

## Obsolescence Rule

If framework-facing docs start reading like a single-aircraft project brief,
move that content into example or reference material and replace it with generic
platform wording.
