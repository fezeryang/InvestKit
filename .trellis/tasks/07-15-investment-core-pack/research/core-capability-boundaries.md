# Core Capability Boundaries

## Responsibility Matrix

| Capability | Owns | Requires | Must not own | Primary handoff |
|---|---|---|---|---|
| `company-deep-research` | company identity/context, segment history, management and capital allocation facts, competitive context, research gaps | security identity, profile, source metadata | detailed ratio calculation, valuation, final thesis | company fact base |
| `business-model-analysis` | customer/value proposition, revenue mechanics, unit economics, pricing, recurrence, moat/fragility | company fact base, segment/customer evidence | statement audit, target value, report assembly | business drivers and vulnerabilities |
| `financial-statement-analysis` | multi-period income/balance/cash-flow trends, margins, growth, liquidity/leverage/returns | normalized statements and definitions | qualitative moat claims, valuation conclusion | financial facts/ratios |
| `earnings-quality-analysis` | accruals, cash conversion, working capital, one-offs, asset/recognition flags | statement result plus necessary line items | general statement recap, earnings-event surprise | quality scorecard and red flags |
| `valuation-analysis` | DCF/scenario/historical valuation where supported, sensitivity, EV-equity bridge | financial/business drivers and valuation inputs | peer selection/statistics, trading instruction | scenario model outputs |
| `comps-analysis` | peer selection/exclusion, operating comparability, multiples, median/range and implied value | peer dataset, target financial facts, metric definitions | standalone intrinsic DCF, industry essay | peer-relative outputs |
| `earnings-analysis` | actual vs expectation/guidance, surprise/drivers, trend changes, transcript unknowns | earnings history, financial/business baselines | accounting-quality audit, catalyst calendar | earnings delta and thesis implications |
| `investment-thesis` | bull/base thesis, pillars, evidence, assumptions, KPIs, falsifiers | all preceding structured results | independent adversarial review, final prose report | falsifiable thesis record |
| `bear-case-analysis` | independent red team, disconfirming evidence, downside mechanisms/scenarios, thesis killers | thesis plus underlying facts/risks | duplicating the base thesis or giving trade instructions | counter-thesis and break conditions |
| `catalyst-analysis` | dated/windows events, mechanism, likelihood/uncertainty, materiality, dependency, positive/downside paths | company/earnings/thesis context and event data | generic news summary, portfolio positioning | monitorable event ledger |
| `source-verification` | source identity/quality/date/freshness, claim coverage, conflicts, unresolved claims | every capability result and source registry | generating new factual claims | verification ledger/gate |
| `investment-report` | balanced assembly from structured artifacts, disclosures, appendices | verified capability results | new research/calculation/facts, advice or promises | `report.md` and report result envelope |

## Composition Invariants

1. Upstream capabilities may expose unknowns; downstream capabilities propagate or explicitly resolve them, never silently drop them.
2. A statement is a fact only when it has at least one persisted source ID. Management commentary is identified as attributed commentary, not independently verified fact.
3. An assumption is never copied into `facts`; an estimate/model output always names its method and material input/assumption IDs.
4. Valuation and comps can be skipped independently. The thesis records the resulting limitation instead of substituting one method without disclosure.
5. Earnings analysis compares actuals to an explicit baseline. If expectations are absent, it may analyze period change but cannot claim a beat/miss.
6. Bear case reads the same evidence but produces an independent adverse causal chain and falsifiers. It cannot merely invert adjectives.
7. Source verification is a gate. A completed report may contain unresolved claims only when clearly labeled unknown/unverified and not relied on for a material conclusion.
8. The report is a view over artifacts. Any value or claim absent from the structured results is a contract violation.

## Skip Rules

| Capability | Valid skip examples | Invalid skip examples |
|---|---|---|
| Valuation | essential forecast/cash/share inputs missing; invalid WACC/terminal relationship cannot be repaired | market price absent when intrinsic DCF inputs are otherwise complete |
| Comps | no defensible peer set or comparable metric definitions | one peer has a missing/negative denominator; exclude that metric/peer instead |
| Earnings | no period actuals and no earnings event/history | transcript absent while actual/expectation/guidance data exist |
| Catalyst | no dated or evidence-backed events in the bounded fixture | event exists but outcome is uncertain; record uncertainty instead |
| Any analytical Skill | subject unresolved or every required input absent | inconvenient adverse evidence or low confidence |

`company-deep-research`, `business-model-analysis`, `financial-statement-analysis`, `earnings-quality-analysis`, `investment-thesis`, `bear-case-analysis`, `source-verification`, and `investment-report` are mandatory for the supplied complete demo fixture. A generic Runtime may skip a method only under the recorded missing/inapplicable rules.

## Trigger Near-Miss Principles

- `company-deep-research` must not trigger for “calculate this company's DCF.”
- `business-model-analysis` must not trigger for a pure three-statement ratio request.
- `financial-statement-analysis` must not claim an earnings beat or miss without expectations.
- `earnings-quality-analysis` must not replace a post-earnings event review.
- `valuation-analysis` must not absorb peer selection when the request is explicitly comps-only.
- `comps-analysis` must not run for a unique company with no defensible peers merely because a market multiple exists.
- `earnings-analysis` must not trigger for long-run accounting quality absent an earnings event/baseline.
- `investment-thesis` must not trigger for a neutral fact sheet or source check.
- `bear-case-analysis` must not trigger for generic risk-list extraction without adversarial causal testing.
- `catalyst-analysis` must not treat every risk as a catalyst without a monitorable event/window.
- `source-verification` must not rewrite the investment conclusion.
- `investment-report` must not perform missing upstream analysis inside the narrative stage.
