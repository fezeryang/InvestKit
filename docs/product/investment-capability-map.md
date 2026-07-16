# InvestKit Investment Capability Map

Status date: 2026-07-16

This map describes behavior present in the current repository and the planned capability sequence. It is not a release-readiness, whole-suite test, live-data, or production-readiness claim.

## Status Definitions

| Status | Meaning |
|---|---|
| `implemented` | A governed first-party Skill and/or local Runtime method performs this bounded behavior and persists its result. |
| `experimental` | A partial form exists inside another capability or only on the fictional offline path; it is not yet a complete standalone capability. |
| `planned` | The capability is named in a future pack but has no complete current implementation. |
| `deferred` | Work is intentionally postponed until earlier capability contracts establish a concrete need. |

The v0.2 offline fixture is fictional and marked `is_demo: true`. No status implies live market coverage, investment advice, brokerage access, or a promise of returns.

## Fundamental Research

| Capability | Status | Current boundary |
|---|---|---|
| Company Deep Research | `implemented` | `company-deep-research` creates a sourced company fact base with gaps and conflicts. |
| Business Model | `implemented` | `business-model-analysis` maps customers, value, revenue mechanics, economics, dependencies, moat evidence, and fragility. |
| Competitive Advantage | `experimental` | Competitive context and defensibility are bounded sections of company/business-model analysis, not a standalone moat capability. |
| Management | `experimental` | The offline dossier records management evidence and unknowns; it does not provide a full management-quality program. |
| Capital Allocation | `experimental` | The company dossier records capital-allocation history/context; deeper policy and track-record analysis belongs in the Advanced Research Pack. |

## Financial Analysis

| Capability | Status | Current boundary |
|---|---|---|
| Financial Statements | `implemented` | `financial-statement-analysis` normalizes multi-period statements and calculates guarded trends and ratios. |
| Earnings Quality | `implemented` | `earnings-quality-analysis` covers accruals, cash conversion, working capital, one-offs, and explicit missing-data warnings. |
| Cash Flow | `experimental` | Cash-flow trends and conversion are analyzed inside the two financial Skills, not as a standalone cash-flow capability. |
| Balance Sheet | `experimental` | Liquidity, leverage, and balance-sheet observations exist inside statement analysis. |
| Financial Health | `experimental` | A bounded offline health view exists; there is no universal score or complete standalone health product. |

## Valuation

| Capability | Status | Current boundary |
|---|---|---|
| DCF | `implemented` | `valuation-analysis` provides guarded bear/base/bull DCF, terminal checks, and an EV-to-equity bridge. |
| Comps | `implemented` | `comps-analysis` records peer inclusion/exclusion, valid metric samples, medians, and implied ranges. |
| Historical Valuation | `planned` | The current offline path records a definition-aligned historical series as unavailable rather than fabricating one. |
| Scenario Analysis | `implemented` | Named bear/base/bull driver sets remain separate and auditable. |
| Sensitivity Analysis | `implemented` | An odd WACC/terminal-growth grid is centered on the base case and invalid cells are guarded. |

## Earnings & Events

| Capability | Status | Current boundary |
|---|---|---|
| Earnings Preview | `planned` | The Skill contract routes preview requests, but the current deterministic demo exercises a historical review path. |
| Earnings Review | `implemented` | `earnings-analysis` compares actuals with dated expectations and prior guidance. |
| Earnings Call | `planned` | The current fixture has no transcript; the Runtime preserves that as an unknown and does not invent call commentary. |
| Guidance | `implemented` | Prior/current guidance remains separately attributed and defined. |
| Expectations | `implemented` | Pre-release expectations remain distinct from actuals, guidance, and model estimates. |
| Catalysts | `implemented` | `catalyst-analysis` persists dated/windowed events, uncertainty, dependencies, materiality, and downside paths. |

## Investment Thesis

| Capability | Status | Current boundary |
|---|---|---|
| Bull Case | `implemented` | The thesis result retains an evidence-linked bull case. |
| Base Case | `implemented` | The thesis result retains a bounded base case and conclusion status. |
| Bear Case | `implemented` | `bear-case-analysis` produces an independent counter-thesis rather than a rewritten bull case. |
| Thesis | `implemented` | `investment-thesis` produces pillars, evidence, assumptions, unknowns, KPIs, and falsifiers. |
| Thesis Tracking | `experimental` | KPIs and review conditions exist, but a complete longitudinal thesis-update lifecycle is not implemented. |
| Red Team | `implemented` | The 13-stage Workflow makes an independent red-team pass mandatory before reporting. |

## Industry

| Capability | Status | Current boundary |
|---|---|---|
| Industry Research | `planned` | Dedicated industry work belongs in the Advanced Research Pack. |
| Competitor Analysis | `experimental` | Company context and comps provide bounded competitor evidence, not full industry coverage. |
| Supply Chain | `planned` | Dependencies may be recorded, but no dedicated supply-chain method is implemented. |
| Thematic Research | `planned` | Scheduled for the Advanced Research Pack. |

## Quant

| Capability | Status | Current boundary |
|---|---|---|
| Factor Research | `planned` | Scheduled for the Quant Pack. |
| Strategy Design | `planned` | Scheduled for the Quant Pack and remains research-only. |
| Backtesting | `planned` | No backtest engine is present in v0.2. |
| Validation | `planned` | Quant-specific leakage, cost, bias, and reproducibility validation belongs with the Quant Pack. |

## Portfolio & Risk

| Capability | Status | Current boundary |
|---|---|---|
| Portfolio Review | `planned` | Scheduled for the Portfolio & Risk Pack. |
| Risk Analysis | `experimental` | Company-level risks and an independent bear case exist; portfolio-level risk analysis does not. |
| Correlation | `planned` | Scheduled for the Portfolio & Risk Pack. |
| Position Sizing | `planned` | Any future method is research-only and cannot authorize trading. |
| Stress Testing | `planned` | Portfolio-level scenario and stress testing is not part of v0.2. |

## Research Output

| Capability | Status | Current boundary |
|---|---|---|
| Initiating Coverage | `planned` | The current report is a bounded offline research artifact, not a full institutional initiating-coverage product. |
| Earnings Report | `planned` | Earnings results feed the general report; a dedicated earnings-report format is not implemented. |
| IC Memo | `experimental` | `investment-report` can assemble the required evidence layers, but no distinct IC-memo format exists. |
| Research Report | `implemented` | `investment-report` assembles validated structured results without introducing new material. |
| Source Verification | `implemented` | `source-verification` is a mandatory claim/source gate before report assembly. |

## Harness And Data Support

| Capability | Status | Current boundary |
|---|---|---|
| Codex Adapter | `implemented` | The current Runtime has one host adapter. |
| Durable Task/Resume | `implemented` | Capability artifacts, normalized indexes, reports, and append-only run events are persisted. |
| Offline Demo Provider | `implemented` | Fictional, provenance-bearing fixture operations support the bounded demo only. |
| Additional Platform Adapters | `deferred` | Claude, Cursor, and other adapters follow stabilized capability and lifecycle contracts. |
| Credentialed Real-Data Providers | `deferred` | Provider expansion follows the Advanced Research, Quant, and Portfolio & Risk packs and must serve a named capability gap. |

Brokerage connectivity, order placement, transaction signing, funds transfer, and trade execution are outside the product scope rather than deferred capabilities.
