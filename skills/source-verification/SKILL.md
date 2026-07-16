---
name: source-verification
description: Verify persisted claim-to-source links, provenance, dates, freshness, quality, definitions, units, conflicts, accessibility, checksums, and demo status across capability results. Use when the user asks for source verification, citation audit, evidence-quality review, provenance checking, or the mandatory pre-report evidence gate. Do not use to perform new company analysis, resolve uncertainty by invention, rewrite a thesis, or assemble the final report.
---

# Source Verification

Version: 0.2.0

## Objective

Determine whether every material claim and model input is traceable, correctly typed, sufficiently fresh, and honestly qualified before report assembly.

## Responsibility Boundary

Own source identity and quality, claim coverage, freshness, period/unit/scope checks, accessibility, checksums, conflicts, and unresolved-evidence status. Do not fetch undeclared data, generate new factual claims, silently repair upstream artifacts, choose an investment conclusion, or write the report.

## Positive Triggers

- “Verify every fact and estimate against the persisted source register before reporting.”
- “Run a citation audit for provenance, freshness, quality, conflicts, and unresolved claims.”

## Near-Miss Negative Triggers

- “Rewrite the investment conclusion into a polished report.”
- “Analyze the company’s business model and unit economics.”

## Inputs

Require the complete source register, capability envelopes, task as-of date, claim IDs, source IDs, artifact checksums, and applicable freshness policy. Accept provider/fixture metadata, audit/accounting scope, license/use warnings, and accessibility state.

### Missing-Data Behavior

Classify absent or unresolvable evidence as `unsupported`, missing material metadata as `partially_supported`, and stale/conflicting/low-quality evidence separately. Do not invent a citation or convert an unsupported fact into an assumption. This mandatory stage fails when a completed task relies materially on unresolved factual claims.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`
- `specs/financial-data-policy.md`
- `specs/risk-policy.md`
- `specs/report-policy.md`

## Analytical Procedure

1. Validate task scope, as-of date, artifact checksums, and source-register schema.
2. Inventory every fact, assumption, estimate, unknown, finding, risk, and warning by capability origin.
3. Resolve every factual claim to one or more persisted source IDs; never require fabricated citations for assumptions.
4. Validate source title, issuer, type, locator, dates, provider/fixture identity, demo flag, and fingerprint.
5. Preserve market, currency, period, unit, accounting scope, and audit/review status where applicable.
6. Apply field- and capability-specific freshness windows with any explicit rationale override.
7. Evaluate first-party/secondary status, quality tier/rationale, accessibility, and known use constraints independently of epistemic type.
8. Classify each material claim as `verified`, `partially_supported`, `unsupported`, `stale`, `conflicted`, `low_quality`, or `not_applicable`.
9. Preserve all authoritative conflicts and warnings; never average or majority-vote them away.
10. Produce the verification gate, coverage metrics, unresolved claims, and eligible next-source paths without altering upstream content.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` envelope with distinct `facts`, `assumptions`, `estimates`, `unknowns`, `findings`, `risks`, `warnings`, and `source_ids`. Put claim verification records, source audit records, coverage, conflicts, freshness decisions, and gate status in `method` per [the source-verification method contract](references/method-contract.md).

## Source Requirements

Each source record includes stable ID, title, issuer/publisher, type, locator or fixture path, publication/effective date, retrieval time or fixture version, as-of date, source-quality rationale, accessibility, checksum, provider without credentials, warnings, and demo state. Apply the applicable freshness policy independently from quality and preserve the decision. Financial sources also retain market, currency, period, unit, accounting scope, and audit/review status.

## Risk and Non-Advice Boundaries

Verification establishes traceability, not truth certainty or investment suitability. No brokerage connection, order placement, real-money action, credential request, buy/sell conclusion, source execution, or return promise is permitted.

## Non-Applicable Cases

Do not use as a substitute for missing upstream research or to adjudicate a conclusion. A claim can be `not_applicable` only when the policy genuinely does not require evidence, not because verification is inconvenient.

## Composition

Consume capability results and `sources.json` from stages 1–11. Emit an immutable verification ledger and gate to `investment-report`, resume validation, and `doctor`; downstream stages may disclose gaps but may not silently fix them.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test missing source IDs, stale high-quality versus fresh low-quality evidence, authoritative conflicts, assumptions without fake citations, malformed fingerprints, demo/provenance retention, and a material unsupported-claim gate failure.
