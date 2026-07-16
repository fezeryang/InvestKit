---
name: business-model-analysis
description: Analyze who pays, what value is delivered, how revenue becomes cash, and which unit economics, dependencies, strengths, and fragilities define a business. Use when the user asks about business-model, revenue-mechanics, customer, pricing, recurrence, concentration, or order-to-cash questions. Do not use for pure statement ratios, peer multiples, final moat verdicts, or valuation.
---

# Business Model Analysis

Version: 0.2.0

## Objective

Explain the company’s economic engine using model-appropriate evidence without forcing every company into one familiar archetype.

## Responsibility Boundary

Own payer/user roles, value proposition, pricing, channel, revenue model, economic states, mix, recurrence, concentration, unit economics, capital intensity, durability mechanisms, and fragilities. Exclude general company history, accounting normalization, full peer analysis, valuation, and thesis verdicts.

## Positive Triggers

- “Analyze this hybrid product-and-subscription business model and its unit economics.”
- “Trace orders through delivery, revenue recognition, billing, working capital, and cash.”

## Near-Miss Negative Triggers

- “Calculate three-statement margins, leverage, and liquidity ratios.”
- “Select comparable companies and calculate peer trading multiples.”

## Inputs

Require resolved identity, company fact-base version, reporting dimensions, covered periods, units, currency, and source IDs. Accept optional segment/customer data, contract terms, cohort data, backlog, capacity, and cost evidence.

### Missing-Data Behavior

Skip only the affected diagnostic—such as retention, LTV, or backlog conversion—when its inputs are absent. Preserve other model analysis and record the missing field and blocked conclusion; never impute an industry average.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`
- `specs/financial-data-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Validate the company fact base, periods, dimensions, definitions, and provenance.
2. Classify product, service, subscription, transaction, advertising, licensing, project/order, spread, or hybrid components.
3. Map payer versus user, value proposition, pricing basis, contract duration, channel, and value-chain role.
4. Trace demand/contract, backlog, delivery, recognition, billing, working capital, and collection as distinct states.
5. Normalize product, segment, geography, customer, and channel dimensions separately.
6. Apply only model-relevant metrics such as recurrence, cohorts, take rate, utilization, or backlog conversion.
7. Separate price, volume, mix, FX, acquisitions, pull-forward, and reclassification effects when evidenced.
8. Emit strengths, fragile dependencies, falsification indicators, alternative explanations, and unknowns.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` envelope with facts, assumptions, estimates, unknowns, findings, risks, warnings, and source IDs. Use [the business-model method contract](references/method-contract.md).

## Source Requirements

Facts need persisted source IDs and compatible periods/definitions. Record source quality, prefer issuer filings or independently corroborated operating evidence, and label management-only claims. Evaluate freshness against the research as-of date and the reporting cadence of each driver; stale evidence remains explicit. Every calculated metric records formula, inputs, units, period, and applicability. A concentration number is a fact; “high” requires sourced context.

## Risk and Non-Advice Boundaries

Do not turn an attractive model archetype into an investment conclusion. No brokerage connection, order placement, real-money action, deterministic moat claim, or return promise is permitted.

## Non-Applicable Cases

Do not use without a resolved company fact base, for a pure statement-normalization request, or when no business-model evidence exists.

## Composition

Consume `company-deep-research` and selected normalized facts. Emit revenue drivers, model-specific metrics, fragilities, and unknowns to financial, valuation, thesis, bear-case, and catalyst capabilities while leaving accounting definitions authoritative upstream.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test a hybrid company, payer/user distinction, missing cohort data, changed segment definitions, acquisition effects, order-state integrity, and source-linked formulas.
