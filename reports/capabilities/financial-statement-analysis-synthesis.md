# Financial Statement Analysis Capability Synthesis

Research date: 2026-07-16

Task: InvestKit v0.2 — Investment Core Pack

Decision: independently implement a normalization-led first-party Skill; no candidate is approved for installation or thin adaptation.

## Outcome

The strongest method is not a larger ratio checklist. It is a guarded process that first establishes period, unit, currency, accounting basis, consolidation scope, audit state, and line-item definitions, then maps all three statements and calculates only comparable, sourced values.

InvestSkill contributes filing and footnote coverage, Vibe-Trading contributes three-statement linkages and return decomposition, China-stock contributes filing provenance and risk paths, and Longbridge contributes explicit period taxonomy and graceful partial-statement behavior.

Universal “healthy” ranges, silent imputation, fraud probabilities, and trading conclusions are rejected.

## Responsibility Boundary

This capability owns:

- source-preserving normalization of income statement, balance sheet, and cash-flow statement data;
- fiscal period, annual/interim/cumulative status, currency, scale, accounting standard, audit state, and consolidation basis;
- mapping original line items to a versioned canonical taxonomy;
- like-for-like multi-period trends, growth, margins, liquidity, leverage, returns, working capital, and cash-flow components;
- guarded formulas, denominator checks, statement linkages, restatement bridges, and data-quality warnings;
- normalized facts and transparent estimates for downstream consumers.

It must not own:

- business-model or moat conclusions;
- a fraud probability, accounting-quality score, or manipulation verdict;
- earnings surprise versus consensus, price reaction, guidance, or catalysts;
- final valuation, thesis, report assembly, or investment action.

Its upstream requirement is identifiable statement evidence with source and period metadata.

Its primary handoff is normalized statements plus derived metrics whose formulas and inputs are explicit.

## Search Method And Evidence Honesty

Exactly the existing 36 registry rows were searched; no collection was expanded.

The 14 registered GitHub snapshots were tree-searched, and selected files below were read statically as method evidence.

Grade A means commit/hash-pinned content and identifiable root-license evidence, not permission to copy any nested file.

Grade B means hash-pinned local evidence with incomplete license/provenance.

Grade C means registry metadata or draft-only evidence.

Unavailable and API-only candidates are reported separately from analysis methods.

## Exact Design-Changing Evidence

| Candidate | Commit and snapshot | Files actually read | Exact method contribution |
|---|---|---|---|
| BATCH-001-007 InvestSkill | commit 6449af2d0fc410a6c541c5815c601ba9f649d791; SHA-256 758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5; MIT root; grade A | plugins/us-stock-analysis/skills/financial-report-analyst/SKILL.md, with plugins/us-stock-analysis/skills/10k-digest/SKILL.md as filing support | filing orientation, auditor/restatement checks, MD&A drivers, GAAP/non-GAAP reconciliation, debt maturities, three statements, footnotes, and comparable periods |
| BATCH-001-014 Vibe-Trading | commit 531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722; SHA-256 8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872; MIT root; grade A | agent/src/skills/financial-statement/SKILL.md | clear three-statement map, linkage questions, DuPont decomposition, and accounting-framework/seasonality/consolidation caveats |
| BATCH-001-008 China-stock | commit d49f1f360deac57821d5d6b3aff664dff232acc6; SHA-256 4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2; MIT root; grade A | skills/financial-health/SKILL.md | audited-status labeling, facts versus judgments, filing-linked ratios, cash conversion, debt, impairment, and stress transmission |
| BATCH-001-010 Longbridge | commit d68372ab584a77b3cb2a078a05c1322267729100; SHA-256 79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e; MIT root; grade A | skills/longbridge-fundamentals/SKILL.md, skills/longbridge-fundamentals/references/financial-report.md, skills/longbridge-fundamentals/references/financial-statement.md | annual/semiannual/quarterly/cumulative selection, all-three reconciliation requirement, partial-statement behavior, and average-assets accrual denominator |

## Strengths, Weaknesses, And Disposition

| Candidate | Strengths | Weaknesses and risks | InvestKit disposition |
|---|---|---|---|
| InvestSkill | Broad filing workflow; links statements, MD&A, non-GAAP, debt, footnotes, auditors, and prior periods | Requires live price even when irrelevant; allows warned training-data estimates; arbitrary thresholds/scores; ends in technical and trading signals | Adopt filing coverage and comparison sequence; reject price gate, imputation, scores, and signals |
| Vibe-Trading | Explains statement relationships; includes DuPont and important comparability caveats | Uses sector-blind “healthy” ranges, simplistic reconciliation tolerances, unsupported fraud probabilities, and buy/avoid language | Adopt linkage questions and named decompositions with guards; reject thresholds, probabilities, and actions |
| China-stock | Preserves period/audit provenance; distinguishes fact from judgment; links cash, leverage, impairment, and risk paths | Combines normalization with earnings quality; A-share overlays; formula details are not fully contained in the reviewed Skill | Adopt provenance and stress-path questions; hand accounting-quality judgments to the next Skill |
| Longbridge | Best period taxonomy; transparent degradation when one statement is absent; uses average assets for accruals | Requires vendor CLI/login/update/network; retained-earnings equality ignores dividends, OCI, FX, and restatements | Adopt period/missing-statement rules; reject provider coupling and oversimplified equality |

## Supporting And Non-Leading Evidence

BATCH-001-011 Anthropic financial-model cookbook was read at repository commit 67ce644d33e5933f0bcc0b6eb4113df41bbf3a8f, snapshot SHA-256 0a63b2cc4d1271dc59106cbfceff27ea244e0fb43868d72e00e8e307c80a4c37, file skills/custom_skills/analyzing-financial-statements/SKILL.md, MIT root evidence.

It is a thin ratio-oriented reference, not a complete statement-analysis design.

Its suggestion to use industry averages for missing values is rejected because it would silently turn missing facts into estimates.

BATCH-001-009 HHFin, commit 6e7ceef3c65287b7b88436fb4876f541b592a2ed and snapshot SHA-256 e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6, was read only through lines 1–360 of earnings-analysis/SKILL.md.

It helps define the boundary: actual-versus-expectation and price response belong to earnings-analysis, not this capability.

## Data/API-Only And Unavailable Evidence

CICCWM-002, archive SHA-256 97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208, was statically read through SKILL.md and scripts/finance_query.py.

It demonstrates income, balance, cash-flow, indicator, report-period, empty-string, and uncertain-field semantics, but not a professional analysis method.

Its license is unknown; the script reads a home-directory credential and sends credential-bearing telemetry, so execution/integration is blocked.

EASTMONEY-001, archive commit 61cfae47451f797d95ae4553ffcc7569b9957e7d and SHA-256 24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15, exposes raw/standardized tables, indicator labels, and query provenance.

Its MIT root evidence does not make its network/dependency code Runtime-ready; it writes to a fixed external path and was not reused.

GF-003, adapted/skills/gf_stock_valuation/SKILL.md, SHA-256 49421c138609516b44aa6680808143f786ade30eda532e21dc6ebbdb791a5588, identifies profitability, leverage, cash-flow, growth, year, and report-type fields.

GF-003 remains grade C because license, authorization, API terms, definitions, units, restatement policy, schema, and fixture behavior are unknown.

GUOSEN-002 is a zero-byte placeholder with SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

No method judgment is possible for Guosen; TLS was not weakened to acquire it.

No Provider is necessary for the offline acceptance path.

## Adopted, Modified, And Rejected Ideas

Adopted:

- filing and source provenance before calculation;
- explicit annual, semiannual, quarterly, and cumulative period types;
- all-three-statement mapping when available and transparent partial analysis otherwise;
- original line-item retention beside a canonical taxonomy;
- audit/restatement/consolidation and accounting-standard warnings;
- statement linkages, debt maturity, working capital, returns, and cash-flow analysis.

Modified:

- every formula becomes a model output with formula ID, input references, units, period, and denominator rule;
- reconciliation is a bridge with dividends, OCI, FX, acquisitions, disposals, and restatements, not a naive equality;
- financial and non-financial sectors use applicability rules rather than one ratio list;
- ratios with negative, near-zero, or mismatched denominators are warned or skipped;
- missing statements preserve valid partial work while disabling dependent checks.

Rejected:

- universal “healthy” bands or sector-blind cutoffs presented as facts;
- training-data estimates, industry-average imputation, and silent zeros;
- red-flag counts presented as fraud probability;
- provider-specific execution, network, login, or automatic update instructions;
- live-price requirements for statement normalization;
- buy/hold/sell, technical-signal, position, or return language.

## Final InvestKit Method

1. Validate entity, fiscal period, covered dates, currency, scale, accounting standard, annual/interim/cumulative type, audit state, and consolidation basis.
2. Register each source and preserve its reported labels and values before mapping.
3. Map original line items to a versioned canonical taxonomy with mapping confidence and warnings.
4. Detect restatements, fiscal-year changes, acquisitions/disposals, discontinued operations, and consolidation changes.
5. Compare only like-for-like periods; reject mixed annual, cumulative, and standalone-quarter arithmetic.
6. Analyze revenue/cost/margin drivers and their period changes.
7. Analyze asset composition, working capital, liquidity, debt maturity, leverage, and equity bridges.
8. Analyze operating, investing, and financing cash flows plus cash/earnings reconciliation.
9. Calculate growth, margins, returns, turnover, leverage, liquidity, and cash measures only when inputs and denominator rules pass.
10. Emit normalized facts, guarded estimates, anomalies, missing fields, warnings, and source IDs without judging manipulation or investment action.

## Output Contract And Handoff Rationale

The capability envelope separates facts, assumptions, estimates, unknowns, findings, risks, warnings, source_ids, method, status, and Skill version.

Normalized facts retain original label, canonical label, value, currency/unit, period, source ID, and mapping status.

Estimates retain formula, input fact IDs, denominator policy, period alignment, and applicability.

Unknowns state whether a field is absent, not disclosed, ambiguous, not comparable, or blocked by a missing statement.

Earnings-quality-analysis consumes only validated normalized line items and guarded metrics.

Business-model-analysis may use reported segment facts but cannot override statement definitions.

Valuation-analysis receives historical baselines and cash/debt/share inputs without an implied valuation conclusion.

Source-verification can trace every derived metric back to the precise statement facts.

## Security, License, And Honest Unknowns

Root MIT evidence permits further legal review, not wholesale copying.

Nested-file license and attribution requirements remain subject to separate approval.

CICCWM's license is unknown and its credential/telemetry behavior triggers the stop-integration policy.

Eastmoney's API and fixed-path code is not part of the first-party implementation.

Guangfa authorization, license, terms, field definitions, and redistribution rights are unknown.

Guosen is unavailable; absence is not approval or rejection.

Any future Provider must serve an explicit missing-data need and preserve field definitions and provenance.

## Non-Execution And No-Copy Attestation

All candidate review used static text and existing audit evidence.

No third-party script, Skill, installer, CLI, MCP, endpoint, dependency, or financial API was executed, imported, sourced, installed, or called.

No credential or user-home file was read, no package was installed, and no TLS control was weakened.

No raw asset was copied into first-party source, Runtime code, or host targets.

The final design paraphrases multiple methods and adds InvestKit-owned guards, schemas, handoffs, and Evals; no prompt, formula implementation, code, or output template was copied wholesale.

## Required Evals

1. Positive: three annual periods with all statements and a documented restatement.
2. Near miss: “Was this earnings beat high quality?” routes event comparison to earnings-analysis and accounting quality downstream.
3. Missing cash flow: complete valid income/balance analysis but skip cash reconciliation and dependent metrics.
4. Mixed periods: reject annual-to-nine-month growth arithmetic.
5. Currency/unit mismatch: prevent calculation until normalized or explicitly bridged.
6. Negative denominator: do not emit a normal cash-conversion or return percentage.
7. Near-zero denominator: warn and skip unstable ratios.
8. Financial-company fixture: do not apply industrial-company working-capital metrics blindly.
9. Restatement: retain original and restated values and use the comparable series.
10. Retained-earnings bridge: include distributions and other equity movements.
11. Empty string: preserve missingness rather than coerce it to zero.
12. Mapping ambiguity: expose low-confidence canonical mapping as a warning.
13. Formula traceability: every estimate resolves to persisted fact IDs.
14. Multi-Skill handoff: earnings quality refuses mixed-period or unvalidated inputs.
15. Safety: no result includes fraud certainty, buy/sell direction, or guaranteed return.

## Final Rationale

Professional statement analysis begins with definitions and comparability, not with ratio volume.

The normalization-led boundary gives downstream Skills reliable facts while preserving uncertainty and prevents accounting observations from becoming unsupported quality or trading judgments.
