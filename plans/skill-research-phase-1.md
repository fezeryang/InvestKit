# Skill Research Phase 1 Plan

Status: proposed; no third-party execution or acquisition authorized by this plan

Role: supporting third-party asset research track. This is not the InvestKit product roadmap and does not block the first-party Harness vertical slice. Product milestones are defined in `plans/product-development-roadmap.md`.

## Objective

Turn the 36-source intake into a scoped, traceable, static-review batch without treating every asset as a Skill and without promoting any candidate before human approval.

## Entry Conditions

The minimum governance record now controls entry:

1. Batch 001 is limited to fundamentals, financial statements, basic valuation, and source verification.
2. Only candidates routed `include_in_batch_001` may proceed to later static research.
3. CICCWM and Guosen candidates remain blocked under their recorded security or acquisition conditions.
4. Guangfa authorization and license evidence remain required before any wrapper can move beyond draft.
5. `skills/` is the authoritative first-party Skill source; the project owner is the only candidate-promotion and first-party-release approver. End users install released capabilities through explicit InvestKit CLI actions.
6. This research track must not block the first-party product milestones in `plans/product-development-roadmap.md`.

## Work Sequence

### 1. Candidate cleanup and scope lock

- Freeze the 36-row registry snapshot and define source-status vocabulary.
- Move ETF, news, fund, technical/trading, and general-agent entries to later batches if the narrow Batch 001 scope is selected.
- Keep processing decision separate from intake/review status.
- Preserve excluded candidates as traceable records; do not delete them merely for being out of batch scope.

### 2. Intake registration and provenance

- Complete one acquisition record per in-scope source: URL, redirect-resolved URL, pinned commit/version, local filename, bytes, SHA-256, acquisition time with timezone, operator/tool, HTTP result, license evidence, and failure reason.
- Treat zero-byte files as failed placeholders.
- Require human provenance for manually supplied Guosen assets.
- Never lower TLS security or accept an invalid certificate to make acquisition succeed.

### 3. Static package analysis

- List archive entries without installing or importing code.
- Inspect `SKILL.md`, manifests, scripts, dependencies, network endpoints, filesystem access, shell/subprocess use, telemetry, credential flow, and prompt instructions.
- For authoritative broker or financial-institution assets, statically document authentication, signing, endpoints, parameters, response fields, pagination, limits, retries, errors, market-code conversion, and data-cleaning logic without executing the original scripts.
- Stop automatic integration on policy triggers while still completing an evidence-backed report where safe.
- Classify target form using the full taxonomy: Agent Skill, MCP/tool, data provider, quant module, agent, workflow, template, reference, or reject.

### 4. Single-asset reviewed records and reports

- Produce one schema-valid JSON record and one human-readable report per candidate.
- Mark every unknown field and explain why it is unknown.
- Assign exactly one processing decision only after evidence review.
- Record supported markets, method assumptions, data limitations, financial risks, and non-advice boundaries.

### 5. Capability matrix and duplicate analysis

- Compare capabilities, inputs, outputs, dependencies, permissions, provider endpoints, data rights, and method assumptions.
- Distinguish duplicate capability from different data-provider coverage.
- Prefer extraction/reference when an asset is useful knowledge but unsuitable as an installable Skill.
- Distinguish methodology reference, API-integration candidacy, controlled code-reuse candidacy, and blocked execution without replacing the existing review, disposition, and approval dimensions.

### 6. Adaptation and test recommendations

- Specify the smallest safe target form and the behavior to remove or isolate.
- Require formal input/output schemas, deterministic offline fixtures, error cases, secret-redaction tests, network-denial tests, and financial-method checks.
- For data providers, document timeout/rate-limit/caching/provenance behavior.
- Route any approved financial API through an InvestKit-owned Provider Adapter and unified data model; first-party Skills must not bind directly to vendor credentials, URLs, or response formats.
- For backtests or simulations, require bias, cost, calendar, and assumption tests.

### 7. Human approval and promotion

- Present the record, report, security findings, license evidence, duplicate analysis, and test results to the named approver.
- Record approval/rejection separately from the processing decision.
- Promote only through the future formal directory/mechanism; never install directly from `third_party/raw/` or from an instruction snapshot.

## Proposed Rebuildable Acquisition Manifest

This is a design proposal, not authorization to download anything. A future machine-readable manifest could contain:

```yaml
source_id: EASTMONEY-001
requested_url: https://github.com/meission/eastmoney
resolved_artifact_url: unknown
version_or_commit: 61cfae47451f797d95ae4553ffcc7569b9957e7d
expected_filename: EASTMONEY-001-eastmoney.zip
sha256: 24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15
bytes: 30649
license_status: identified
license: MIT
network_policy: human_approved_only
tls_policy: verify_certificate_and_hostname
```

A future acquisition helper, if approved, should be opt-in and inert by default. It should accept only allowlisted HTTPS URLs, require normal TLS verification, refuse redirects outside the allowlist, cap bytes/time, write to a quarantine temp path, compute SHA-256, compare expected metadata, atomically move a verified artifact into the raw batch directory, and emit a redacted receipt. It must never execute, unpack, install, source, import, or pipe downloaded content to a shell. Manual acquisitions should use the same receipt format with operator and chain-of-custody fields.

## Batch Completion Gate

Phase 1 is complete only when every in-scope candidate has traceable source evidence, honest license status, a schema-valid record, a single processing decision, a single-asset report, duplicate and security analysis, adaptation/test recommendations, and human sign-off where promotion is proposed. Unknowns are acceptable only when explicit and justified.
