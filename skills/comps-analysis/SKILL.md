---
name: comps-analysis
description: Select and document defensible comparable companies, align metrics and periods, exclude invalid observations, calculate peer distributions, and derive relative-value ranges. Use when the user asks for comparable-company, peer-set, trading-multiple, or relative-valuation analysis. Do not use for standalone DCF, generic industry essays, borrowed sector medians, or investment recommendations.
---

# Comparable Companies Analysis

Version: 0.2.0

## Objective

Produce an auditable peer-relative valuation that makes comparability decisions, invalid denominators, sample size, and uncertainty visible.

## Responsibility Boundary

Own considered-peer selection/exclusion, operating comparability, metric/period alignment, valid multiple distributions, implied ranges, and the relative-value EV-to-equity bridge. Exclude intrinsic DCF, industry narrative, fixed premiums, and thesis conclusions.

## Positive Triggers

- “Choose defensible peers and calculate comparable-company trading multiples.”
- “Build a peer ledger, valid multiple distributions, and a relative implied-value range.”

## Near-Miss Negative Triggers

- “Calculate an intrinsic DCF with terminal-growth sensitivity.”
- “Research the industry structure and supply chain without relative valuation.”

## Inputs

Require resolved target, target financial facts, considered peer records, metric definitions, fiscal periods/vintages, market-data dates, currencies/conversion metadata, capital structure, and source IDs.

### Missing-Data Behavior

Exclude invalid observations per peer and metric while retaining other valid metrics. Use `skipped` only when no defensible peer set or comparable definition exists. Missing/zero/negative denominators never become zero-valued multiples or a borrowed sector median.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/financial-data-policy.md`
- `specs/valuation-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Validate target facts, units, periods, currencies, dates, and source IDs.
2. Build a considered-peer ledger before calculating multiples.
3. Compare business model, mix, geography, scale, growth, margins, leverage, fiscal calendar, and accounting policy.
4. Record each peer as included or excluded with a durable reason.
5. Define and align every LTM, NTM, or annual metric and estimate vintage.
6. Match enterprise multiples to enterprise metrics and equity multiples to equity metrics.
7. Exclude zero, negative, missing, or definitionally incompatible denominators per observation.
8. Preserve conversion source/date and market-data as-of time.
9. Calculate sample size, median, quartiles, range, and disclosed outlier treatment from valid observations only.
10. Apply evidence-selected distributions to the target and complete the EV-to-equity bridge.
11. Report implied ranges, peer sensitivity, comparability risks, and unknowns without calling the median fair value.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` envelope with facts, assumptions, estimates, unknowns, findings, risks, warnings, and source IDs. Follow [the comps method contract](references/method-contract.md).

## Source Requirements

Every target/peer fact, market value, conversion, and metric has a source ID, source-quality rationale, and as-of/period definition. Prefer authoritative filings and consistently defined market data; evaluate freshness against one disclosed comparison date and reject or label stale/mixed-vintage observations. Peer decisions and outlier rules are method judgments with rationale, not facts.

## Risk and Non-Advice Boundaries

Expose weak samples and peer sensitivity; do not apply automatic premiums or conceal missingness. No brokerage connection, order placement, real-money action, rating, price promise, or guaranteed return is permitted.

## Non-Applicable Cases

Do not run when the subject is unique and no peer is defensible, definitions cannot be aligned, or the request is solely intrinsic valuation.

## Composition

Consume company/business/financial facts and peer records. Emit a peer ledger, distributions, exclusions, bridge, and implied ranges to downstream thesis, bear case, verification, and report without duplicating upstream facts. A standalone later valuation may consume this result, but the ordered workflow never back-writes its already completed valuation artifact.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test negative EBITDA, missing EPS, a conglomerate exclusion, fiscal-year mismatch, currency conversion, weak sample size, and safe valuation handoff.
