---
name: earnings-quality-analysis
description: Assess whether reported earnings are cash-backed, repeatable, and supported by defensible accounting using accruals, working capital, recognition, one-offs, footnotes, controls, and alternative explanations. Use when the user asks accounting-quality or earnings-durability questions after statements are normalized. Do not use for earnings beat/miss, guidance, valuation, catalysts, fraud accusations, or trading decisions.
---

# Earnings Quality Analysis

Version: 0.2.0

## Objective

Test the durability and accounting support of earnings with evidence-backed diagnostics while remaining skeptical without making unsupported misconduct claims.

## Responsibility Boundary

Own cash conversion, accruals, working-capital bridges, recognition policy, one-offs, non-GAAP reconciliation, capitalization, reserves, impairments, obligations, related parties, auditors, controls, restatements, alternatives, and quality risk paths. Exclude statement normalization, beat/miss, valuation, and fraud probability.

## Positive Triggers

- “Assess why profit rose while operating cash flow fell and receivables expanded.”
- “Review recurring earnings, accounting policies, one-offs, footnotes, auditors, and controls.”

## Near-Miss Negative Triggers

- “Did this quarter beat consensus and how did management change guidance?”
- “Normalize the three statements and calculate basic financial ratios.”

## Inputs

Require validated multi-period statement artifacts, source IDs, comparable periods, audit state, and available filing/policy/footnote evidence. Accept non-GAAP reconciliation, working-capital detail, controls, auditor, and acquisition data.

### Missing-Data Behavior

Complete supported diagnostics and record absent footnotes, policies, working-capital detail, or controls as unknowns that lower evidence confidence. Suppress ratios with invalid denominators. Never fill gaps, assign neutral scores, or call a flag proof of manipulation.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/financial-data-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Validate normalized statements, comparable periods, source IDs, audit state, and evidence coverage.
2. Analyze OCF-to-earnings, guarded accruals, defined FCF conversion, and the working-capital bridge.
3. Test revenue-recognition policy against contract balances, receivables, returns, allowances, and concentration.
4. Separate recurring operations from asset sales, fair-value, tax, restructuring, acquisition, and other one-offs.
5. Reconcile management-defined adjustments, including stock compensation where material.
6. Review capitalization, reserves, impairments, goodwill/intangibles, leases, pensions, contingencies, and related parties.
7. Review auditor opinions/changes, restatements, controls, critical estimates, and policy changes.
8. Pair every concern with evidence, plausible alternatives, follow-up needs, confidence, and causal risk path.
9. Preserve missing domains as unknowns and emit no composite fraud or quality score.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` envelope with facts, assumptions, estimates, unknowns, findings, risks, warnings, and source IDs. Use [the earnings-quality method contract](references/method-contract.md).

## Source Requirements

Facts cite normalized statements or filing sources with explicit source quality; prefer audited filings, notes, and controls evidence over commentary. Evaluate freshness against the research as-of date and the latest applicable filing period, retaining stale evidence as a warning. Calculations include formulas, periods, input IDs, denominator and annualization policies. Concerns cite evidence and distinguish management explanations from corroborated facts.

## Risk and Non-Advice Boundaries

A red flag is not proof of manipulation; state alternative explanations and uncertainty. No brokerage connection, order placement, real-money action, fraud probability, buy/sell direction, or return promise is permitted.

## Non-Applicable Cases

Do not run on mixed-period or unvalidated statement inputs. Do not replace earnings-event analysis or claim quality when every relevant accounting source is absent.

## Composition

Consume `financial-statement-analysis`. Emit supported positives, concerns, alternatives, unknowns, and risk paths to thesis, bear case, source verification, and report; keep event surprise authoritative in `earnings-analysis`.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test rising profit/falling cash, seasonal inventory, negative earnings, acquisitions, non-GAAP adjustments, one-offs, missing footnotes, and alternative explanations.
