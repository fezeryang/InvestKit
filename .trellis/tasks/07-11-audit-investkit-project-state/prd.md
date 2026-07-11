# Audit InvestKit project state

## Goal

Reconcile the repository's documented Batch 001 state with the assets already present, record a reproducible static audit, and define the remaining conditions for starting governed candidate review.

## Scope

- Static inspection and documentation changes only.
- Preserve every file under `third_party/raw/` as untrusted evidence; do not execute or install it.
- Keep the paused `07-11-install-financial-skills` task `in_progress` while moving this session to an independent audit task.
- Correct source and wrapper review statuses without approving any candidate.
- Expand the Batch 001 intake manifest with provenance, integrity, acquisition, license, and risk evidence.
- Clarify the difference between processing decisions and review/workspace status.
- Produce current-state, repository-inventory, context-gap, and Phase 1 planning artifacts.

## Required corrections

- Remove the example row from `registry/inbox/sources.csv`.
- Change GF-001 through GF-008 from `adapted` to `draft`.
- Change GUOSEN-001 through GUOSEN-006 to `needs_manual_acquisition`.
- Change Batch 001 from `waiting_for_sources` to a state meaning sources exist but review has not begun, consistently across README, task description, and batch summary.
- Treat the two zero-byte Guosen files as failed placeholders, never as valid ZIP archives.
- Keep all eight Guangfa wrappers as drafts and record their governance, implementation, schema, naming, and test gaps.

## Deliverables

- `third_party/raw/batch-001/manifest.md`
- `reports/project/current-state-audit.md`
- `reports/project/repository-inventory.md`
- `reports/project/context-gap-analysis.md`
- `plans/skill-research-phase-1.md`
- Corrected Batch 001 status documents, source registry, and SOP.

## Acceptance

- No third-party code, installer, or network service is executed.
- CSV structure, IDs, statuses, and example-row removal are verified with Python's standard library.
- The JSON Schema validates against Draft 2020-12 using the already-installed `jsonschema` package.
- Markdown local references resolve.
- Non-empty ZIP integrity, size, and SHA-256 values are verified without extraction into the workspace.
- Raw ZIPs and Trellis runtime state remain ignored and untracked.
- Secret-pattern, trading-boundary, approval-state, and automatic-execution scans are documented without exposing secret values.
- Final diff contains only deliberate audit corrections and artifacts; unrelated existing files remain uncommitted unless the user later approves a commit plan.
