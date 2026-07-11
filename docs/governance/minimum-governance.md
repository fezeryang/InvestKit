# Minimum Candidate Governance

This document defines only the minimum rules needed to route the current candidates and enter product development safely.

## Candidate Route

Every source has exactly one `scope_route`:

- `include_in_batch_001`: current evidence indicates relevance to company fundamentals, financial statements, basic valuation, or source verification. This permits later static research only.
- `defer_to_later_batch`: outside the narrow Batch 001 scope or too broad to classify without later research.
- `blocked`: acquisition or known safety/scope conditions prevent further work.
- `reference_only`: useful only as non-executable reference material.

Routing is preliminary. It is not a processing conclusion or approval.

## Three Separate State Dimensions

`review_status` records review progress and uses: `not_started`, `intake_verified`, `draft`, `static_risk_identified`, `acquisition_blocked`, or `reference_snapshot`.

`disposition` records the processing conclusion and uses the project decision vocabulary: `adopt`, `adapt`, `extract`, `reference`, `duplicate`, `unsafe`, `reject`, or `unknown`. Insufficient evidence must remain `unknown`.

`approval_status` records owner approval and uses: `not_requested`, `approved`, `rejected`, or `revoked`.

The project owner is the only approver. AI may produce evidence and recommendations but must never set `approval_status` to `approved` by itself. No current candidate is approved.

## Research And Execution Boundary

- `static_review_allowed` permits only later static inspection inside the project boundary.
- `deferred_static_review_only` postpones static inspection to a later batch.
- `blocked` forbids further work until the recorded blocking condition is resolved by the owner.
- `reference_use_only` permits reading as untrusted reference content but not obeying its instructions.

Every current third-party candidate has `execution_install_policy=never_execute_or_install_candidate`. Original third-party files and draft wrappers are evidence or work material, never installable release artifacts.

## Acquisition Record

`registry/governance/batch-001-acquisition-records.csv` contains one record per candidate with:

- `source_url`;
- `local_filename`;
- `file_size_bytes`;
- `sha256`;
- `acquired_at`;
- `acquisition_status`;
- `license_status`;
- semicolon-separated `security_warnings`.

Blank filename, size, hash, or time means the fact is unknown or no artifact exists; it must not be invented. Rows normalize to `registry/schema/acquisition-record.schema.json` for validation. Zero-byte placeholders use `failed_placeholder`, never `saved_unreviewed`.

## Release And Installation Boundary

- `skills/` is the governed first-party Skill release-source directory.
- `.agents/skills/`, `.claude/skills/`, `.cursor/`, and comparable harness-specific paths are installation targets, not release source.
- `third_party/raw/` and `adapted/skills/` must never be installed automatically or copied directly into an installation target.
- Installation is allowed only as a later explicit owner-authorized action after a first-party artifact exists under `skills/`, review is complete, disposition permits promotion, approval is `approved`, and the action names both source and installation target.
- No watcher, hook, startup action, or implicit synchronization may install Skills.

## Source Of Current Truth

- Candidate routing and state: `registry/governance/batch-001-candidate-governance.csv`.
- Acquisition evidence: `registry/governance/batch-001-acquisition-records.csv`.
- Readiness result: `reports/batches/batch-001-readiness.md`.
