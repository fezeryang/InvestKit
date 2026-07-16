---
name: investment-report
description: Assemble validated capability envelopes into a deterministic, source-linked Markdown investment research report that preserves thesis, independent bear case, catalysts, conflicts, assumptions, estimates, unknowns, risks, skipped stages, demo state, and non-advice disclosure. Use when the user asks for the final investment report, research report, initiating-coverage report, or IC memo from completed artifacts. Do not use to conduct missing analysis, fetch data, invent conclusions, or issue a rating or trade recommendation.
---

# Investment Report

Version: 0.2.0

## Objective

Render a balanced, auditable view of frozen research artifacts without introducing any new material claim, number, source, assumption, estimate, risk, or conclusion.

## Responsibility Boundary

Own deterministic Markdown assembly, source footnotes, evidence-layer separation, mandatory disclosures, cross-section consistency, completeness state, and the no-new-material gate. Do not perform research, calculations, source repair, thesis revision, live refresh, or investment advice.

## Positive Triggers

- “Assemble the completed capability artifacts into the final sourced investment report.”
- “Create an IC memo that preserves the thesis, independent bear case, gaps, and source ledger.”

## Near-Miss Negative Triggers

- “Calculate a missing DCF and peer valuation before writing anything.”
- “Verify the unresolved claim-to-source links and freshness policy.”

## Inputs

Require task metadata, validated capability envelopes, exact input checksums, completed `bear-case-analysis` and `source-verification`, `sources.json`, and loaded Skill/spec manifests. Accept valid skipped analytical stages only with their reasons and missing inputs.

### Missing-Data Behavior

Expose every unknown, warning, conflict, and skipped capability. Mark the report `failed_validation` if a mandatory stage or material source gate fails; use `complete_with_gaps` for disclosed permitted gaps. Never fill a missing module with neutral evidence or polished prose.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`
- `specs/financial-data-policy.md`
- `specs/valuation-policy.md`
- `specs/risk-policy.md`
- `specs/report-policy.md`

## Analytical Procedure

1. Validate the exact workflow order, required artifacts, statuses, checksums, and mandatory completed stages.
2. Freeze the allowed union of claim, fact, assumption, estimate, unknown, risk, warning, and source IDs.
3. Determine research subject, as-of date, generation time, demo state, research boundary, and skipped-stage list.
4. Render company, business-model, financial, quality, valuation/comps, and earnings/event sections from structured inputs in deterministic order.
5. Render the thesis, bull/base reasoning, independent counter-thesis, catalysts, positive/negative evidence, and monitoring conditions.
6. Keep facts, assumptions, estimates, unknowns, conflicts, risks, warnings, and skips visibly distinct.
7. Render stable claim/source footnotes and verification states for material facts and tables.
8. Check arithmetic, units, periods, currency, market, accounting scope, peer comparability, scenarios, and duplicate values.
9. Write the executive summary last by selecting already-rendered verified findings only.
10. Compare every emitted ID and numeric value with the frozen input union; fail on new material.
11. Persist Markdown and the report result envelope atomically with `complete`, `complete_with_gaps`, or `failed_validation` state.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` capability envelope and `report.md`. Record input checksums, emitted claim/source IDs, section statuses, validation warnings, and completeness in `method` as defined by [the report assembly contract](references/method-contract.md).

## Source Requirements

Every material factual statement and table row must retain a verified claim/source ID or stable source footnote. Preserve source-quality and freshness decisions, conflicts, dates, definitions, units, and demo markers. The report cannot add a source, refresh data, or cite an inaccessible artifact not present in the verification ledger.

## Risk and Non-Advice Boundaries

Include risks, limitations, demo-data declaration, and research-only/non-advice boundary prominently. No brokerage connection, order placement, real-money action, BUY/SELL/HOLD rating, position size, stop loss, target-return promise, deterministic forecast, browser/CDN, or external report generator is permitted.

## Non-Applicable Cases

Do not use before upstream analysis and verification are complete, to repair missing analysis, or to transform a failed mandatory gate into a polished conclusion. A mandatory bear-case or source-verification failure prevents completion.

## Composition

Consume immutable artifacts from the entire `company-deep-dive` workflow, especially the independent bear case and verification gate. Emit `report.md` and the report envelope to task completion, resume validation, and `doctor`; introduce no new research state.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test exact input-ID union, mandatory stages, skipped capability disclosure, source conflicts, summary-last membership, arithmetic/period/unit consistency, stale checksum rejection, deterministic bytes, and forbidden advice/network language.
