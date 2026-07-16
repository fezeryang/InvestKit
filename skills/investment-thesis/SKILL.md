---
name: investment-thesis
description: Synthesize validated company, business, financial, valuation, comps, and earnings evidence into a time-bounded, falsifiable investment thesis with bull/base reasoning, measurable pillars, disconfirming evidence, and review conditions. Use when the user asks for an investment thesis, thesis pillars, variant perception, or bull/base/bear synthesis. Do not use for a neutral fact sheet, standalone valuation, independent red-team review, source audit, final report, or buy/sell recommendation.
---

# Investment Thesis

Version: 0.2.0

## Objective

Turn completed upstream research into a falsifiable claim set whose evidence, assumptions, unknowns, and failure conditions can be monitored independently of narrative confidence.

## Responsibility Boundary

Own the bounded thesis statement, bull/base reasoning, preliminary bear seed, pillars, causal mechanisms, variant-perception hypothesis, evidence sufficiency, KPIs, and falsifiers. Do not fetch data, calculate a new valuation, perform the independent bear-case pass, assemble the final report, or decide a trade.

## Positive Triggers

- “Build a falsifiable investment thesis from these completed research artifacts.”
- “Define the bull/base/bear thesis pillars, variant perception, KPIs, and thesis breakers.”

## Near-Miss Negative Triggers

- “Create a neutral company fact sheet from these filings.”
- “Audit every factual claim against the source register.”

## Inputs

Require a resolved security, research as-of date, time horizon, source register, and validated upstream capability envelopes with stable IDs and checksums. Accept optional completed valuation, comps, and earnings results; require their absence or skip reason to remain explicit.

### Missing-Data Behavior

Weaken or block an affected pillar and record the gap as an unknown with decision impact. Use `skipped` only when identity or every usable upstream artifact is absent. Missing valuation or earnings evidence must produce `insufficient_evidence`, not a neutral confidence score or model-memory estimate.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`
- `specs/valuation-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Validate identity, scope, horizon, as-of date, upstream statuses, checksums, and source IDs.
2. Freeze the upstream artifact set; never repair or rewrite an input inside this stage.
3. State one bounded thesis and classify the evidence conclusion as `supported`, `mixed`, `insufficient_evidence`, or `contradicted`.
4. Build bull, base, and preliminary bear reasoning using only upstream fact, estimate, assumption, and unknown IDs.
5. Define three to five pillars with causal mechanism, confirming evidence, disconfirming evidence, assumptions, unknowns, and current status.
6. Record variant perception or expectation gap as sourced evidence or an explicit material assumption.
7. Define observable KPIs and review timing for every material pillar.
8. Define falsifiers with metric or event, threshold or condition, source path, and review window.
9. Reconcile contradictory evidence without averaging it away, then propagate gaps, risks, and warnings.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` envelope with distinct `facts`, `assumptions`, `estimates`, `unknowns`, `findings`, `risks`, `warnings`, and `source_ids`. Put thesis cases, pillars, evidence links, KPIs, falsifiers, conclusion status, horizon, and input checksums in `method` as defined by [the thesis method contract](references/method-contract.md).

## Source Requirements

Every confirming or disconfirming factual statement references persisted fact and source IDs and carries upstream source-quality and freshness decisions. Estimates retain method and material input IDs. An expectation-gap claim is an assumption unless a dated source establishes it. Preserve stale, low-quality, and conflicting evidence visibly; none may silently support a material current pillar.

## Risk and Non-Advice Boundaries

Express uncertainty through evidence sufficiency and observable conditions, not conviction theater. No brokerage connection, order placement, real-money action, BUY/SELL/HOLD label, position size, stop loss, deterministic target, or return promise is permitted.

## Non-Applicable Cases

Do not use for unresolved identity, a neutral dossier, pure valuation math, generic risk extraction, source checking, or report formatting. Do not mark a thesis complete when mandatory upstream evidence is corrupt.

## Composition

Consume immutable outputs from company, business-model, financial, quality, valuation, comps, and earnings analysis. Emit a frozen thesis artifact to `bear-case-analysis`, `catalyst-analysis`, `source-verification`, and `investment-report`; the bear-case stage may challenge but never edit it.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test confirming and disconfirming evidence per pillar, observable falsifiers, missing valuation/earnings evidence, unsourced variant perception, frozen-input checksums, and rejection of advice language.
