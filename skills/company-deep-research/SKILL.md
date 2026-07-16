---
name: company-deep-research
description: Build a source-led company dossier covering identity, history, segments, management, capital allocation, competition, disclosures, and research gaps. Use when initiating or refreshing deep fundamental company research. Do not use for a standalone DCF, detailed unit economics, statement normalization, thesis verdict, or final report assembly.
---

# Company Deep Research

Version: 0.2.0

## Objective

Create a traceable company fact base broad enough for downstream analysis without collapsing facts, management claims, interpretations, or unknowns.

## Responsibility Boundary

Own company context, products, segments, customers, geographies, management, governance, capital allocation, competition, regulation, material disclosures, contradictions, and research gaps. Exclude detailed business economics, ratios, valuation, thesis, and report writing.

## Positive Triggers

- “Build a deep company dossier from these filings and profile records.”
- “Refresh the company fact base, management record, competitive context, and open questions.”

## Near-Miss Negative Triggers

- “Calculate this company’s intrinsic value with a DCF.”
- “Analyze customer economics and the order-to-cash model in detail.”

## Inputs

Require a resolved security, research question, as-of date, bounded source register, profile/filing records, and source IDs. Accept optional prior-period dossier and management or governance evidence.

### Missing-Data Behavior

Complete bounded sections when evidence exists and record absent governance, customer, segment, or competitive evidence as unknowns with downstream impact. Use `skipped` only when identity or all company evidence is absent; never substitute model memory.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Validate identity, scope, date, market, and source bounds.
2. Inventory sources by issuer, type, period, publication/fixture date, quality, and freshness.
3. Extract sourced facts on history, products, segments, customers/channels, geography, and value chain.
4. Extract attributed management, governance, ownership, and capital-allocation records.
5. Map competitors, regulation, dependencies, disclosures, and material risks without issuing a verdict.
6. Compare only like-for-like periods and retain definition or restatement changes.
7. Preserve conflicts, rank findings by materiality, and name the evidence needed to close each gap.
8. Revalidate dependent findings after any material fact correction.

## Output Contract

Return the shared envelope with `completed`, `skipped`, or `failed` status and distinct `facts`, `assumptions`, `estimates`, `unknowns`, `findings`, `risks`, `warnings`, and `source_ids`. Follow [the dossier method contract](references/method-contract.md).

## Source Requirements

Every factual claim needs a persisted source ID, period, and as-of context. Record source quality; prefer current issuer, regulatory, and audited evidence for material claims, and keep issuer or management statements explicitly attributed unless corroborated. Evaluate freshness against the research as-of date and the fact's change cadence. Retain stale, low-quality, and conflicting evidence rather than choosing silently.

## Risk and Non-Advice Boundaries

Use materiality and conditional language. No brokerage connection, order placement, real-money action, rating, target price, or return promise is permitted.

## Non-Applicable Cases

Do not use for unresolved identity, a purely macro question, technical chart analysis, or a request whose sole output is valuation or a transaction.

## Composition

Consume `security-identification`. Emit the company fact base and source manifest to `business-model-analysis`, `financial-statement-analysis`, `investment-thesis`, `bear-case-analysis`, and `source-verification` without pre-judging their conclusions.

## Evals

Use [trigger Evals](references/trigger-evals.json) and verify management attribution, conflict preservation, changed segment definitions, missing governance evidence, revision propagation, and source-linked facts.
