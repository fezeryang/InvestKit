---
name: earnings-analysis
description: Analyze an earnings preview or reported period against point-in-time expectations, prior guidance, operating drivers, estimate changes, and transcript evidence. Use when the user asks for an earnings preview, earnings review, beat/miss, guidance, surprise, call, or post-results analysis. Do not use for general multi-year statements, accounting-quality audits, catalyst scanning, or trade setups.
---

# Earnings Analysis

Version: 0.2.0

## Objective

Compare an earnings event with the baselines that existed before it, keeping actuals, expectations, guidance, commentary, and unknowns distinct.

## Responsibility Boundary

Own preview/review mode, actual-versus-consensus, actual-versus-prior-guidance, operating drivers, guidance changes, estimate revisions, transcript-backed observations, and thesis implications. Exclude statement normalization, accounting-quality judgment, generic news, valuation, and trading action.

## Positive Triggers

- “Review this reported quarter against pre-release consensus and prior guidance.”
- “Build a pre-earnings baseline with expectations, guidance, and watch items.”

## Near-Miss Negative Triggers

- “Analyze multi-year financial statement ratios and cash-flow trends.”
- “Assess whether reported earnings are cash-backed and free of one-off distortions.”

## Inputs

Require resolved security, event period/time, `preview` or `review` mode, metric definitions, currency/units, source IDs, and relevant baselines. Accept actuals, pre-release consensus vintage, persisted research estimate, prior management guidance, transcript, operating KPIs, and benchmarked price reaction.

### Missing-Data Behavior

With actuals but no expectation, analyze changes without saying beat or miss. Missing transcript sets availability false and creates an unknown/warning; never infer tone or quotes. No period actuals or event/history permits `skipped` with missing inputs.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`
- `specs/financial-data-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Classify preview or review mode and reject generic-statement near misses.
2. Resolve security, fiscal period, release time, units, currency, definitions, and sources.
3. Preserve separate actual, pre-release consensus, persisted estimate, and prior-guidance baselines.
4. Validate consensus provider, observation time, analyst count/range, and pre-release vintage.
5. Validate guidance period, range, midpoint rule, definition, date, and attributed source.
6. Calculate absolute/percentage surprise only for aligned definitions and valid denominators.
7. Analyze revenue/EPS, segments, margins, cash flow, KPIs, and guidance changes.
8. Separate sourced facts, management commentary, assumptions, and estimates when explaining drivers.
9. Use transcript or Q&A observations only with a transcript source and identified speaker.
10. Persist estimate revisions with old/new values, method, reason, and assumptions.
11. Describe price reaction only with a defined window and benchmark, without asserting causality.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` envelope with facts, assumptions, estimates, unknowns, findings, risks, warnings, and source IDs. Follow [the earnings-event method contract](references/method-contract.md).

## Source Requirements

Actuals cite issuer/filing records; consensus includes its provider and pre-release observation time; guidance is attributed and dated; transcript observations cite document and speaker. Record source quality for each baseline and evaluate freshness against the event time and research as-of date. Never use stale or post-release consensus as the surprise baseline.

## Risk and Non-Advice Boundaries

Separate GAAP and adjusted metrics and disclose missing baselines. No brokerage connection, order placement, real-money action, rating change, option setup, target-price promotion, causal price claim, or return promise is permitted.

## Non-Applicable Cases

Do not use for long-run statement trends without an event, accounting quality absent an event comparison, or generic news/catalyst collection.

## Composition

Consume financial/business baselines and earnings records. Emit sourced deltas, guidance/expectation bridges, revisions, unknowns, and thesis implications to downstream thesis, bear case, catalyst, verification, and report without rewriting statements. A standalone later valuation may consume earnings revisions, but the ordered workflow never back-writes its already completed valuation artifact.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test pre-release vintage, prior-guidance midpoint, GAAP/adjusted separation, missing transcript/guidance, no expectation, preview/review routing, and benchmarked non-causal reaction.
