---
name: financial-statement-analysis
description: Normalize and analyze comparable income statements, balance sheets, and cash-flow statements with guarded trends, ratios, linkages, and data-quality warnings. Use when the user asks for multi-period financial-statement, margin, growth, liquidity, leverage, return, working-capital, or cash-flow analysis. Do not use to judge manipulation, announce an earnings beat, perform valuation, or issue an investment action.
---

# Financial Statement Analysis

Version: 0.2.0

## Objective

Produce source-preserving, comparable financial facts and traceable calculations before any accounting-quality or valuation judgment.

## Responsibility Boundary

Own period/unit/currency/accounting normalization, original-to-canonical line mapping, three-statement trends, margins, growth, liquidity, leverage, returns, working capital, cash flows, and reconciliation warnings. Exclude fraud inference, earnings surprise, valuation, thesis, and trade conclusions.

## Positive Triggers

- “Normalize these three annual financial statements and analyze trends and linkages.”
- “Calculate sourced margins, growth, liquidity, leverage, returns, and cash-flow measures.”

## Near-Miss Negative Triggers

- “Assess whether the reported earnings are cash-backed and repeatable.”
- “Compare this quarter’s actual EPS with pre-release consensus and guidance.”

## Inputs

Require resolved entity, source IDs, covered dates, fiscal period type, currency, scale, accounting standard, audit state, consolidation basis, and at least one statement. Accept restatement, acquisition, disposal, discontinued-operation, and mapping metadata.

### Missing-Data Behavior

Complete valid statement modules while marking dependent calculations `skipped`. Missing cash flow disables cash reconciliation; mismatched periods disable growth; negative or near-zero denominators disable unstable ratios. Never coerce blank fields to zero.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/financial-data-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Validate entity, dates, fiscal-period type, currency, scale, accounting standard, audit state, and consolidation basis.
2. Retain reported labels/values and map them to the versioned canonical taxonomy with confidence.
3. Identify restatements, fiscal changes, acquisitions/disposals, discontinued operations, and scope changes.
4. Compare only like-for-like annual, interim, cumulative, or standalone periods.
5. Analyze income-statement revenue, cost, margin, and operating drivers.
6. Analyze asset composition, working capital, liquidity, debt maturity, leverage, and equity bridges.
7. Analyze operating, investing, and financing cash flows.
8. Reconcile cash and earnings; include dividends, OCI, FX, and structural changes in equity bridges.
9. Calculate only metrics with valid inputs and denominators, recording formula and input IDs.
10. Emit normalized facts, estimates, anomalies, unknowns, risks, and warnings without quality or action claims.

## Output Contract

Return the shared envelope with `completed`, `skipped`, or `failed` status and distinct facts, assumptions, estimates, unknowns, findings, risks, warnings, and source IDs. Follow [the statement method contract](references/method-contract.md).

## Source Requirements

Preserve source ID, original label, canonical label, value, currency/unit, period, audit/scope metadata, source quality, and mapping status. Prefer audited or reviewed issuer/regulatory statements. Evaluate freshness against the research as-of date and required reporting period; stale or mixed-vintage inputs remain labeled and are not silently combined. Every estimate names formula, input fact IDs, denominator rule, period alignment, and applicability.

## Risk and Non-Advice Boundaries

Flag comparability and denominator limits; do not infer fraud from anomalies. No brokerage connection, order placement, real-money action, rating, deterministic forecast, or return promise is permitted.

## Non-Applicable Cases

Do not calculate across irreconcilable periods/units or apply industrial-company ratios blindly to financial firms. Use `earnings-quality-analysis` for accounting-quality judgment.

## Composition

Consume company and business-model context without overriding reported accounting dimensions. Emit normalized facts and guarded estimates to earnings quality, valuation, comps, earnings, thesis, bear case, and source verification.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test restatements, mixed periods, missing cash flow, currency/unit mismatch, negative denominators, financial-company applicability, empty fields, and traceable formulas.
