# InvestKit Investment Capability Map

Status date: 2026-07-17

This map describes bounded behavior present in the current repository and the planned sequence. It is not a release-readiness, live-data, investment-advice, or production-readiness claim.

## Status definitions

| Status | Meaning |
|---|---|
| `implemented` | A governed first-party Skill and/or local Runtime method performs this bounded behavior, persists its result, and can consume the relevant normalized imported record when supplied. |
| `experimental` | A partial form exists inside another capability or only for a narrow evidence shape; it is not yet a complete standalone capability. |
| `planned` | The capability is named for a future milestone but has no complete current implementation. |
| `deferred` | Work is intentionally postponed until earlier contracts or release gates establish a concrete need. |

The Runtime has two distinct offline modes. `demo` uses a fictional fixture marked `is_demo: true`. `imported` uses a user-supplied, validated local bundle marked `is_demo: false`; InvestKit does not fetch or independently guarantee it. No status implies current market coverage, sufficient inputs for a particular issuer, investment suitability, brokerage access, or a promise of returns.

## Fundamental research

| Capability | Status | Current boundary |
|---|---|---|
| Company Deep Research | `implemented` | `company-deep-research` creates a sourced company fact base from the profile record, including explicit gaps and conflicts. |
| Business Model | `implemented` | `business-model-analysis` uses supplied customers, value, revenue mechanics, economics, dependencies, and risks; missing concepts remain unknown. |
| Competitive Advantage | `experimental` | Competitive context and defensibility are bounded sections, not a standalone moat study. The Microsoft bundle supplies a risk topic but no supported competitive-position conclusion. |
| Management | `experimental` | Supplied management evidence can be retained, but there is no full management-quality program. An empty management record produces an unknown rather than a finding. |
| Capital Allocation | `experimental` | Supplied history/context can be retained; policy, governance, and longitudinal track-record analysis belong in a later pack. |

## Financial analysis

| Capability | Status | Current boundary |
|---|---|---|
| Financial Statements | `implemented` | `financial-statement-analysis` normalizes supplied multi-period statements and calculates guarded trends and ratios with source attribution. |
| Earnings Quality | `implemented` | `earnings-quality-analysis` covers accruals, cash conversion, working capital, one-offs, and explicit missing-data warnings. |
| Cash Flow | `experimental` | Cash-flow trends and conversion are analyzed inside the two financial Skills, not as a standalone cash-flow capability. |
| Balance Sheet | `experimental` | Liquidity, leverage, and balance-sheet observations exist inside statement analysis. |
| Financial Health | `experimental` | A bounded evidence-led view exists; there is no universal score or complete standalone health product. |

## Valuation

| Capability | Status | Current boundary |
|---|---|---|
| DCF | `implemented` | `valuation-analysis` can run guarded bear/base/bull DCF, terminal checks, and an EV-to-equity bridge when forecasts and assumptions are supplied. It skips for the Microsoft acceptance bundle because they are absent. |
| Comps | `implemented` | `comps-analysis` records supplied peer inclusion/exclusion, aligned metric samples, medians, and implied ranges. It skips when no governed peer set is supplied. |
| Historical Valuation | `experimental` | Guangfa target-only acquisition preserves provider-defined PE/PB historical percentiles as supporting context; lookback, scale, and a full aligned valuation series remain unavailable. |
| Scenario Analysis | `implemented` | Named bear/base/bull driver sets remain separate and auditable when the required valuation inputs exist. |
| Sensitivity Analysis | `implemented` | An odd WACC/terminal-growth grid is centered on the base case and guards invalid cells when axes are supplied. |
| Consensus Forecasts | `experimental` | The normalized contract and analysis now preserve point-in-time contributor estimates, counts, dispersion, and revisions separately from guidance and InvestKit forecasts; licensed live acquisition and longitudinal revision history remain pending. |
| Earnings Forecast Model | `experimental` | The valuation path now retains a driver-model method, vintage, periods, and DCF cash-flow series, but automated driver construction and estimate-versus-actual tracking remain pending. |
| Target Value Range | `experimental` | DCF emits an auditable bear/base/bull per-share range labeled as non-guaranteed; reverse DCF, historical bands, and cross-method reconciliation remain pending. |

## Earnings and events

| Capability | Status | Current boundary |
|---|---|---|
| Earnings Preview | `planned` | The Skill contract routes preview requests, but the deterministic workflow exercises historical evidence rather than a complete preview product. |
| Earnings Review | `implemented` | `earnings-analysis` retains supplied actuals and compares them with dated expectations/guidance only when those records exist. |
| Earnings Call | `planned` | No transcript acquisition or standalone call-analysis path exists. `transcript_available: false` means not supplied in the bundle, not nonexistent elsewhere. |
| Guidance | `implemented` | Supplied prior/current guidance remains separately attributed and defined; absent guidance remains unknown. |
| Expectations | `implemented` | Supplied point-in-time expectations remain distinct from actuals, guidance, and model estimates; an empty expectation object is not a consensus estimate. |
| Catalysts | `implemented` | `catalyst-analysis` persists supplied dated/windowed events, uncertainty, dependencies, materiality, and downside paths. It skips when no supported event is supplied. |

## Investment thesis

| Capability | Status | Current boundary |
|---|---|---|
| Bull Case | `implemented` | The thesis result retains an evidence-linked bull case bounded by supplied inputs. |
| Base Case | `implemented` | The thesis result retains a bounded base case and conclusion status without converting gaps into neutral evidence. |
| Bear Case | `implemented` | `bear-case-analysis` produces an independent counter-thesis from the frozen evidence set. |
| Thesis | `implemented` | `investment-thesis` produces evidence-led pillars, assumptions, unknowns, KPIs, and falsifiers without issuer-specific demo defaults. |
| Thesis Tracking | `experimental` | KPIs and review conditions exist, but a longitudinal thesis-update lifecycle and new-data ingestion path are not implemented. |
| Red Team | `implemented` | The 13-stage Workflow requires an independent red-team pass before reporting. |

## Industry

| Capability | Status | Current boundary |
|---|---|---|
| Industry Research | `planned` | Dedicated industry work belongs in the Advanced Research Pack. |
| Competitor Analysis | `experimental` | Company context and supplied comps provide bounded evidence, not full industry coverage. |
| Supply Chain | `planned` | Dependencies may be recorded, but no dedicated supply-chain method is implemented. |
| Thematic Research | `planned` | Scheduled for the Advanced Research Pack. |
| Industry Comparison | `experimental` | Target-only Guangfa acquisition now reports PE/PB against provider industry averages without requiring a user-selected peer; complete constituent membership/sample size and broader growth/profitability benchmarks remain pending. A supplied governed benchmark still requires sample, vintage, aligned definitions, target-minus-median, and percentile. |
| Industry Rotation | `planned` | Full-market relative strength, breadth, flows, valuation, and earnings-revision evidence is not yet normalized. |
| Macro/Market Regime | `planned` | No governed macro-cycle, liquidity, risk-appetite, or market-state classifier is currently implemented. |

## Quant

| Capability | Status | Current boundary |
|---|---|---|
| Factor Research | `planned` | Scheduled for the Quant Pack. |
| Strategy Design | `planned` | Scheduled for the Quant Pack and remains research-only. |
| Backtesting | `planned` | No backtest engine is present in v0.3. |
| Validation | `planned` | Quant-specific leakage, cost, bias, and reproducibility validation belongs with the Quant Pack. |
| Technical Indicators | `planned` | Indicator definitions, adjustment rules, calendars, warm-up periods, and signal timing require a governed time-series contract. |
| Quant Screening | `planned` | Cross-sectional factor scoring and selection require point-in-time universes and reproducible eligibility rules. |
| Realistic Backtest | `planned` | Must model transaction costs, slippage, corporate actions, suspensions, price limits, delistings, capacity, look-ahead, and survivorship bias before any performance claim. |

## Portfolio and risk

| Capability | Status | Current boundary |
|---|---|---|
| Portfolio Review | `planned` | Scheduled for the Portfolio & Risk Pack. |
| Risk Analysis | `experimental` | Company-level sourced risks and an independent bear case exist; portfolio-level risk does not. |
| Correlation | `planned` | Scheduled for the Portfolio & Risk Pack. |
| Position Sizing | `planned` | Any future framework remains research-only and cannot authorize trading. |
| Stress Testing | `planned` | Portfolio-level scenario and stress testing is not part of v0.3. |
| Asset Allocation | `planned` | Multi-asset expected-return, covariance, constraint, rebalance, and uncertainty contracts are not implemented. |
| Risk Budgeting | `planned` | Research-only marginal risk, factor risk, drawdown, liquidity, and concentration budgets are not implemented. |

## Market and asset coverage

| Capability | Status | Current boundary |
|---|---|---|
| A-share Research | `experimental` | A live, opt-in multi-provider path has been acceptance-tested for one Shanghai-listed issuer; this is not full-market or institution-grade coverage. |
| Hong Kong / US Equities | `planned` | Venue-specific identifiers, currencies, calendars, disclosures, corporate actions, entitlements, and data providers are not implemented. |
| Bonds | `planned` | Instrument terms, curves, spread, duration, convexity, credit, and liquidity contracts are not implemented. |
| Futures / Options | `planned` | Contract rolls, multipliers, margin, settlement, volatility surfaces, Greeks, and expiry semantics are not implemented. |
| FX | `planned` | Pair conventions, sessions, forwards, carry, fixing, and cross-currency risk are not implemented. |
| Intraday Monitoring / Alerts | `planned` | No continuously running scheduler, freshness SLA, alert delivery, provider failover, or institution-grade observability is present. |

## Research output

| Capability | Status | Current boundary |
|---|---|---|
| Initiating Coverage | `planned` | The current report is a bounded research artifact, not an institutional initiating-coverage product. |
| Earnings Report | `planned` | Earnings results feed the general report; a dedicated earnings-report format is not implemented. |
| IC Memo | `experimental` | `investment-report` can assemble required evidence layers, but no distinct IC-memo format exists. |
| Research Report | `implemented` | `investment-report` assembles validated structured results and imported provenance without introducing unsupported material. |
| Source Verification | `implemented` | `source-verification` is a mandatory multi-source claim/source gate before report assembly; unresolved gaps remain visible. |

## Harness and data support

| Capability | Status | Current boundary |
|---|---|---|
| Codex Adapter | `implemented` | The current Runtime has one host adapter. |
| Durable Task/Resume | `implemented` | Both modes persist capability artifacts, indexes, reports, and run events; imported resume reconstructs from the immutable task snapshot. |
| Offline Demo Provider | `implemented` | Fictional, provenance-bearing fixture operations support deterministic evaluation and compatibility. |
| Research Bundle Contract | `implemented` | A closed Draft 2020-12 schema and annotated template define one provider-neutral, project-local issuer bundle. |
| Local File Provider | `implemented` | A bounded, read-only, no-network Provider validates and serves the nine operations with operation-specific source IDs. |
| Imported-Task Doctor | `implemented` | Read-only checks cover bundle hash/schema, source joins, persisted records, disclosures, freshness, and unsafe/corrupt artifacts. |
| Pinned Real-Issuer Acceptance | `implemented` | Microsoft FY2025 exercises historical filing evidence and intentional missing-data behavior; it is not a current investment dataset. |
| Approved Live Acquisition | `experimental` | Opt-in SSE, Guangfa, and clean-room CICCWM adapters emit the normalized bundle for a bounded A-share workflow; coverage and reliability remain narrower than a released data platform. |
| Automatic Filing Acquisition | `planned` | Original filing retrieval/parsing remains an optional evidence-escalation producer, not a universal product-readiness gate. |
| Additional Platform Adapters | `deferred` | Claude, Cursor, and other adapters follow stabilized capability, migration, and release contracts. |
| Credentialed Providers | `experimental` | Approved Guangfa and clean-room CICCWM adapters are opt-in and credential-gated; production entitlement, coverage, fallback, and service-level qualification remain pending. |

Brokerage connectivity, order placement, transaction signing, funds transfer, and trade execution are outside the product scope rather than deferred capabilities.

Full annual-report text extraction is also not a universal readiness gate. Original disclosures are retained as an optional, high-value verification layer for footnotes, accounting policies, unusual items, related-party matters, source conflicts, and material claims; ordinary analysis should prefer normalized point-in-time evidence.
