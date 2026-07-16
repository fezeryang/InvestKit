---
name: valuation-analysis
description: Build source-linked intrinsic and scenario valuation using guarded DCF, historical context, sensitivity analysis, and an EV-to-equity bridge. Use when the user asks for DCF, intrinsic value, historical valuation, scenario, sensitivity, or valuation reconciliation analysis. Do not use to select peers, fetch live data, fill missing forecasts with defaults, or issue a buy/sell recommendation.
---

# Valuation Analysis

Version: 0.2.0

## Objective

Produce an assumption-explicit valuation range whose model, inputs, scenarios, invalid cells, and limitations remain auditable.

## Responsibility Boundary

Own scenario DCF, supported historical-valuation context, sensitivity, terminal-value checks, EV-to-equity bridge, and method reconciliation. Exclude peer selection/statistics, live retrieval, thesis verdicts, and trading instructions.

## Positive Triggers

- “Build a sourced base, bull, and bear DCF with WACC/growth sensitivity.”
- “Reconcile intrinsic value, historical multiples, and an available comps result.”

## Near-Miss Negative Triggers

- “Choose defensible comparable companies and calculate peer trading multiples.”
- “Summarize the company’s business model and customer economics.”

## Inputs

Require resolved identity, normalized financial history, forecast drivers, valuation date, currency/units, capital structure, diluted shares, and source IDs. Accept historical multiple series and a completed comps artifact when available.

### Missing-Data Behavior

Skip the affected method when forecast drivers, capital structure, positive shares, or valid terminal assumptions are absent. Preserve partial methods and explicit unknowns. Never use generic defaults, silently cap terminal growth, or turn missing values into zero.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/financial-data-policy.md`
- `specs/valuation-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Validate identity, periods, currencies, units, actual/estimate labels, date, and source IDs.
2. Register forecast assumptions with rationale, materiality, and evidence dependencies.
3. Forecast revenue, operating margin, tax, D&A, CapEx, and change in net working capital.
4. Calculate UFCF as NOPAT plus D&A minus CapEx minus change in NWC.
5. Calculate WACC from market equity and gross interest-bearing debt or a documented target structure.
6. Require positive diluted shares and `WACC > terminal growth` for every scenario and grid cell.
7. Calculate perpetuity terminal value; use exit multiple only as a separately disclosed cross-check.
8. Bridge enterprise to equity value through cash, debt, minority interest, preferred stock, and non-operating assets.
9. Run internally consistent bear/base/bull driver sets and an odd sensitivity grid centered exactly on base.
10. Add historical context only from comparable point-in-time definitions.
11. Reconcile available methods while preserving disagreement and limitations.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` envelope with distinct facts, assumptions, estimates, unknowns, findings, risks, warnings, and source IDs. Follow [the valuation method contract](references/method-contract.md).

## Source Requirements

Every input resolves to a fact or assumption ID with period, currency, unit, source, and source-quality rationale. Evaluate freshness against the valuation date; market values and capital structure require point-in-time alignment, while stale drivers remain labeled or block the affected method. Historical multiples require point-in-time numerator/price definitions and restatement handling. Model outputs identify their method and material inputs.

## Risk and Non-Advice Boundaries

Show sensitivity, terminal-value share, and disagreement; do not disguise uncertainty as precision. No brokerage connection, order placement, real-money action, deterministic target, rating, or guaranteed return is permitted.

## Non-Applicable Cases

Do not value an unresolved security, run DCF without essential drivers/capital structure, or provide per-share output without positive diluted shares. Banks and other special sectors require an applicable method.

## Composition

Consume business drivers and normalized financial facts. A completed `comps-analysis` result may be consumed in a standalone reconciliation or from a prior task; in `company-deep-dive`, valuation runs before the current comps and earnings stages, whose later reconciliation belongs to thesis and report. Emit scenario ranges, sensitivities, assumptions, and limitations without rewriting upstream facts.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test center-cell equality, `WACC <= g`, negative net debt, missing shares, cyclical normalization, historical-definition mismatch, and visible DCF/comps disagreement.
