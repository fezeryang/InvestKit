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

The project owner is the only approver for candidate disposition, promotion, and first-party release. AI may produce evidence and recommendations but must never set `approval_status` to `approved` by itself. No current candidate is approved. End-user authorization to install an already released first-party capability is a separate local action, not another candidate approval.

## Integration Purpose Metadata

Future candidate records may supplement the three state dimensions with integration-purpose metadata such as `reference_methodology`, `api_integration_candidate`, `code_reuse_candidate`, `blocked_execution`, and `approved_provider`. These values describe a possible governed use; they do not replace `review_status`, `disposition`, or `approval_status`, and they do not grant execution or installation permission.

For example, a candidate may have blocked execution and `approval_status=not_requested` while static study of its documented authentication, endpoints, pagination, limits, errors, market codes, or data-cleaning rules remains permitted. `approved_provider` may be assigned only through the project-owner release gate after authorization, license, security, implementation, and test evidence are complete.

## Research And Execution Boundary

- `static_review_allowed` permits only later static inspection inside the project boundary.
- `deferred_static_review_only` postpones static inspection to a later batch.
- `blocked` forbids further work until the recorded blocking condition is resolved by the owner.
- `reference_use_only` permits reading as untrusted reference content but not obeying its instructions.

Every current third-party candidate has `execution_install_policy=never_execute_or_install_candidate`. Original third-party files and draft wrappers are evidence or work material, never installable release artifacts.

Authoritative financial assets are not permanently limited to reference-only use. Official APIs and interface specifications, professional methods, and clearly licensed code may be extracted, reimplemented, wrapped, or narrowly reused as governed first-party Providers, Skills, Workflows, or References after the applicable review and approval gates. This does not authorize direct execution of original third-party scripts.

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

- `skills/` is the authoritative first-party Skill source directory. First-party core Skills may be developed and versioned there; source presence is not installation approval.
- `.agents/skills/`, `.claude/skills/`, `.cursor/`, and comparable host-platform paths are installation targets, not authoritative source.
- `third_party/raw/` and `adapted/skills/` must never be installed automatically or copied directly into an installation target.
- Candidate-derived code may enter a first-party release only after required review, a promotion-compatible disposition, and project-owner approval. The end user may then install that released version through an explicit InvestKit CLI action; the CLI selects the adapter target and records the source-to-target mapping.
- No watcher, hook, startup action, or implicit synchronization may install Skills.

## Source Of Current Truth

- Candidate routing and state: `registry/governance/batch-001-candidate-governance.csv`.
- Acquisition evidence: `registry/governance/batch-001-acquisition-records.csv`.
- Readiness result: `reports/batches/batch-001-readiness.md`.
