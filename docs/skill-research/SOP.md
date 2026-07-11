# Third-Party Skill Processing SOP

## Default Mode

InvestKit uses static analysis by default. Raw files must not be modified directly. Draft and adaptation work belongs in `adapted/`, but presence there does not mean approval or installation. Third-party code must not be executed unless a human explicitly approves a controlled review step.

Each batch should normally process 10 to 20 related assets. Failures, missing files, unknown licenses, and incomplete information must still be recorded.

## Fixed Workflow

1. Receive source.
2. Verify source.
3. Save original asset.
4. Identify asset type.
5. Check `SKILL.md` and directory structure.
6. Analyze functions, inputs, and outputs.
7. Analyze scripts and dependencies.
8. Check license.
9. Perform static security review.
10. Analyze financial methods.
11. Check duplicate relationship with existing assets.
12. Determine InvestKit target form.
13. Give processing decision.
14. Generate adaptation recommendations.
15. Generate test recommendations.
16. Output single-asset report.
17. Update batch summary.

## Source Intake

Register candidate sources in `registry/inbox/sources.csv`. Store local archives or source snapshots under the relevant batch directory inside `third_party/raw/`, such as `third_party/raw/batch-001/`. Do not overwrite raw files during review.

## Output Locations

- Structured reviewed records: batch directories inside `registry/reviewed/`, such as `registry/reviewed/batch-001/`.
- Single-asset reports: batch directories inside `reports/skills/`, such as `reports/skills/batch-001/`.
- Batch summaries and matrices: `reports/batches/`.
- Draft and adaptation workspace: `adapted/` (not an approval or installation boundary).

## Required Decision Values

Every candidate must receive one decision:

- `adopt`
- `adapt`
- `extract`
- `reference`
- `duplicate`
- `unsafe`
- `reject`
- `unknown`

## Decision And Review Status Are Separate

The processing `decision` and the operational review `status` are independent dimensions:

- `decision` answers what InvestKit should ultimately do with a candidate and must use exactly one value from the required decision list above.
- `status` answers where the candidate currently is in intake or review, for example `new`, `needs_manual_acquisition`, or `draft`.
- A `draft` status is not an `adapt` decision. An `adapt` decision is not approval.
- No candidate is approved merely because files exist under `adapted/skills/`.

`adapted/skills/` is currently a draft workspace. Nothing in `adapted/` may be described as production-ready or formally installed; the release and approval boundary is defined below.

## Minimum Release Boundary

The project owner is the only approver. `skills/` is the governed first-party release-source directory. `.agents/skills/`, `.claude/skills/`, `.cursor/`, and comparable harness paths are installation targets. Moving a Skill from release source to an installation target requires a later explicit owner-authorized action naming both paths.

Never auto-install from `third_party/raw/` or `adapted/skills/`. Candidate route, review status, disposition, approval status, and acquisition evidence follow `docs/governance/minimum-governance.md`.
