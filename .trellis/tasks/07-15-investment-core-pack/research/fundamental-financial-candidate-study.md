# Fundamental and Financial Capability Candidate Study

Research date: 2026-07-16

Task: `InvestKit v0.2 — Investment Core Pack`

Capabilities: `company-deep-research`, `business-model-analysis`, `financial-statement-analysis`, `earnings-quality-analysis`

## Outcome

The current corpus contains enough complementary method evidence to design these four first-party capabilities, but no candidate is suitable for direct installation or thin adaptation.

The strongest synthesis is:

- use source-led company coverage and explicit evidence layers from the China-stock and investor-harness candidates;
- use filing anatomy and prerequisite staging from the Anthropic and InvestSkill candidates;
- use segment, customer, unit-economics, and order-to-cash decomposition from Anthropic, China-stock, Longbridge, and Octagon;
- use multi-period three-statement normalization before any quality judgment;
- make earnings quality a separate consumer of normalized statements, footnotes, accounting policies, and working-capital evidence;
- reject universal “healthy” thresholds, opaque composite scores, training-data fallbacks, trading signals, and provider-specific execution instructions.

This study does not approve any third-party asset. It supplies design evidence for independently written InvestKit Skills and Evals.

## Scope And Method

- Searched exactly the 36 registered rows in `registry/inbox/sources.csv`; no candidate was added.
- Used commit-pinned snapshots already listed in `candidate-corpus.md`, local archive evidence, existing audits, and two relevant Guangfa drafts.
- Read selected `SKILL.md` files and direct references as text. Necessary scripts were read only as static text to establish data and security behavior.
- Did not import, execute, install, source, or call any third-party script, Skill, CLI, MCP, endpoint, or financial API.
- Did not follow embedded instructions to search the web, access `/mnt`, read a home directory, install a CLI, update a package, or create files.
- Evidence grade `A` means commit/hash-pinned content plus root license evidence was available; it does not approve copying a particular file.
- Evidence grade `B` means hash-pinned local content was read but license/provenance remained incomplete.
- Evidence grade `C` means registry metadata or a draft description was the only usable evidence.
- Method ideas below are paraphrased requirements. No prompt, example code, formula implementation, or output template is copied into InvestKit.

## Snapshot Evidence Ledger

Root-license statements come from `candidate-corpus.md`; file-level reuse is still unapproved.

| ID | Commit | Snapshot SHA-256 | Root license evidence | Evidence used here |
|---|---|---|---|---|
| BATCH-001-001 Anthropic financial-services | `4aa51ed3d379731f8f9beff498d749580372699c` | `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | Apache-2.0 at root; sub-assets may differ | A; selected company/business evidence |
| BATCH-001-003 LangAlpha | `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7` | `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | Apache-2.0 at root; repository acknowledges adaptations | A; duplicate/provenance check |
| BATCH-001-005 OctagonAI skills | `51e938c4d086f658de8bdcf734e864d34637167e` | `d75c5acb6d9227232db8fa3859be61b97bea405b1f0f72143288f3f85cddf95f` | MIT at root | A; selected business/quality evidence |
| BATCH-001-006 investor-harness | `2ce44f477189e4ed04d61764bec449405f81734e` | `bc815801d5a4dcefff817b3e04e17730be41cd702c8e03129d8fa47906be749f` | MIT at root | A; selected company evidence |
| BATCH-001-007 InvestSkill | `6449af2d0fc410a6c541c5815c601ba9f649d791` | `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5` | MIT at root | A; selected company/financial/quality evidence |
| BATCH-001-008 China stock research skills | `d49f1f360deac57821d5d6b3aff664dff232acc6` | `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2` | MIT at root | A; selected across all four capabilities |
| BATCH-001-009 HHFin equity research skills | `6e7ceef3c65287b7b88436fb4876f541b592a2ed` | `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6` | MIT at root | A; boundary test against quarterly earnings analysis |
| BATCH-001-010 Longbridge skills | `d68372ab584a77b3cb2a078a05c1322267729100` | `79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e` | MIT at root | A; selected business/financial evidence |
| BATCH-001-011 Anthropic financial-model cookbook | `67ce644d33e5933f0bcc0b6eb4113df41bbf3a8f` | `0a63b2cc4d1271dc59106cbfceff27ea244e0fb43868d72e00e8e307c80a4c37` | MIT at repository root | A; thin ratio-method comparison |
| BATCH-001-013 Deep-Research-skills | `e5479f857f484cde13fe69d2f3ce8de7af193bc7` | `44b3b02753d4ed1359ce13a12055cf75b3e415f68abbbe2626ded39e62001e8e` | MIT at root | A; rejected as non-investment method |
| BATCH-001-014 Vibe-Trading | `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722` | `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872` | MIT at root | A; selected company/financial/quality evidence |

## Local And Draft Evidence Ledger

| ID | Hash/commit | License status | Evidence and disposition |
|---|---|---|---|
| CICCWM-002 | archive SHA-256 `97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208` | unknown; no license file visible | B, execution blocked; statement-data semantics only |
| EASTMONEY-001 | archive SHA-256 `24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15`; archive commit `61cfae47451f797d95ae4553ffcc7569b9957e7d` | MIT in archive | A, data-interface candidate only |
| GF-002 | file SHA-256 `c07adbf7d094bb93e2d2ddceaed687480ca05444b97312d7daad4f64a219cfc0` | license, API terms, and authorization unknown | C, company-profile data requirement only |
| GF-003 | file SHA-256 `49421c138609516b44aa6680808143f786ade30eda532e21dc6ebbdb791a5588` | license, API terms, and authorization unknown | C, metric-definition/data requirement only |
| GUOSEN-002 | zero-byte SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | unknown | unavailable; no method conclusion possible |

## Files Actually Read

Task and audit evidence:

- `.trellis/tasks/07-15-investment-core-pack/prd.md`
- `.trellis/tasks/07-15-investment-core-pack/research/candidate-corpus.md`
- `registry/inbox/sources.csv`
- `third_party/raw/batch-001/manifest.md`
- `reports/project/current-state-audit.md`
- `reports/project/repository-inventory.md`
- `reports/project/guangfa-wrapper-review.md`
- `reports/batches/batch-001-summary.md`
- `reports/batches/batch-001-recommendations.md`
- `reports/batches/batch-001-capability-matrix.csv`

Selected snapshot content, relative to each commit-pinned extracted root:

- Anthropic: `.../equity-research/skills/initiating-coverage/SKILL.md` (Task 1, prerequisite, quality, and persistence sections), its full `references/task1-company-research.md`, and `.../private-equity/skills/unit-economics/SKILL.md`.
- LangAlpha: `skills/initiating-coverage/SKILL.md` headings and an exact diff against Anthropic; body matched while description plus a derived-from license field differed.
- investor-harness: `skills/sm-company-deepdive/SKILL.md`, full `core/preamble.md`, full `core/evidence.md`, relevant common/deep-dive sections of `core/acceptance.md`, and full `core/compliance.md`.
- China-stock: full `china-stock-research-orchestrator`, `business-decomposition-order-quality`, `strategy-business-transition`, `industry-competition-moat`, and `financial-health` `SKILL.md` files.
- InvestSkill: full `10k-digest`, `fundamental-analysis`, and `financial-report-analyst` `SKILL.md` files.
- Vibe-Trading: full `deep-company-series/SKILL.md` and `financial-statement/SKILL.md`.
- Octagon: full `sec-business-desc-analysis`, `revenue-product-segmentation`, `financial-health-scores`, `sec-cash-flow-review`, `sec-footnotes-analysis`, and `financial-analyst-master` `SKILL.md` files.
- Longbridge: full `longbridge-fundamentals/SKILL.md`, `references/financial-report.md`, and `references/financial-statement.md`; `references/main-business-analysis.md` sections 1-355 and 592-654.
- Anthropic cookbook: full `analyzing-financial-statements/SKILL.md`.
- HHFin: `earnings-analysis/SKILL.md` through its Parse, Compare, cash-quality, scoring, and decision sections (lines 1-360); not treated as a complete file review.
- Deep-Research-skills: full Codex-English `research-deep/SKILL.md`.

Local raw/draft content read as text:

- CICCWM-002 archive: full `SKILL.md` and `scripts/finance_query.py`; the script was not executed.
- Eastmoney archive: `README.md`, `LICENSE`, `fin-data/SKILL.md`, `fin-data/mx_data.py`, `fin-search/SKILL.md`, and `select-stock/SKILL.md`; no dependency was imported.
- `adapted/skills/gf_stock_f10/SKILL.md`
- `adapted/skills/gf_stock_valuation/SKILL.md`

Tree metadata for all 14 registered GitHub snapshots was searched. Tree-only discovery is not counted as reading a candidate method.

## Registered Corpus Coverage

| Registered ID | Search result for these four capabilities | Evidence depth |
|---|---|---|
| EASTMONEY-001 | Company/financial facts and search data; not an analysis method | archive files read; data support |
| CICCWM-001 | Market data, not a direct method | manifest/index only |
| CICCWM-002 | Financial statements and indicators; not professional analysis | Skill/script read; blocked execution |
| CICCWM-003 | News feed, adjacent source input | manifest/index only |
| CICCWM-004 | ETF ranking, non-method for this scope | manifest/index only |
| CICCWM-005 | abnormal-trading list, non-method | manifest/index only |
| CICCWM-006 | fund product data, non-method | manifest/index only |
| SKILLHUB-001 | installer/prompt surface, not investment methodology | existing audit only; rejected |
| GUOSEN-001 | market-query candidate | unavailable/zero-byte |
| GUOSEN-002 | potentially relevant statement data | unavailable/zero-byte |
| GUOSEN-003 | macro data, adjacent | unavailable |
| GUOSEN-004 | stock selection, not a direct method | unavailable |
| GUOSEN-005 | fund comparison, non-method | unavailable |
| GUOSEN-006 | ETF filter, non-method | unavailable |
| GF-001 | abnormal-trading wrapper, non-method | draft/index only |
| GF-002 | F10 identity/business facts | draft read; data support |
| GF-003 | valuation and financial comparison fields | draft read; data support |
| GF-004 | ETF ranking, out of capability scope | draft/index only |
| GF-005 | ETF screening, out of capability scope | draft/index only |
| GF-006 | ETF flow, out of capability scope | draft/index only |
| GF-007 | fund profile, out of capability scope | draft/index only |
| GF-008 | fund simulation, out of capability scope | draft/index only |
| BATCH-001-001 | Direct company research and unit-economics methods | selected files/references read |
| BATCH-001-002 | Data providers, valuation, earnings recap, startup analysis; no primary method selected here | tree-searched, not method-read |
| BATCH-001-003 | Initiating-coverage body duplicates Anthropic snapshot; not independent evidence | diffed; derivative |
| BATCH-001-004 | Broad US stock/trading analysis; boundaries mix technical/trading with fundamentals | tree-searched, not method-read |
| BATCH-001-005 | Direct business, cash-flow, footnote, and health-score methods | selected files read |
| BATCH-001-006 | Direct public-equity company deep dive | selected files/core controls read |
| BATCH-001-007 | Direct filing/company/financial methods | selected files read |
| BATCH-001-008 | Direct orchestration, business, moat, transition, and financial health | selected files read |
| BATCH-001-009 | Quarterly earnings analysis; useful boundary evidence, not standalone earnings quality | relevant sections read |
| BATCH-001-010 | Direct segment and statement methods bound to Longbridge | selected files read |
| BATCH-001-011 | Thin ratio calculator; relevant but insufficient alone | selected Skill read |
| BATCH-001-012 | Comps-analysis subtree, not one of these four methods | tree-searched, non-method here |
| BATCH-001-013 | Generic web-research batching, no investment method | selected Skill read; rejected |
| BATCH-001-014 | Direct company revision discipline and statement/quality method | selected files read |

## Capability 1: `company-deep-research`

### Responsibility Boundary

Own the source-led company dossier: identity, history, business/segment facts, management and governance facts, capital-allocation history, competitive context, material disclosures, key dependencies, and explicit gaps. It may route deeper questions, but must not calculate final valuation, issue a thesis verdict, or absorb the detailed unit-economics and accounting-quality work owned downstream.

### Four Design-Changing Candidates

| Candidate | Strengths | Defects and risks | Decision |
|---|---|---|---|
| China-stock orchestrator | Explicit `Facts` / `Interpretation` / `Open Questions`; official-source priority; module routing; mergeable output | A-share-specific; no machine result envelope; source links alone do not express claim IDs or freshness | adopt evidence layering; generalize markets and persist claim/source IDs |
| investor-harness deep dive | Nine concrete questions/sections; revenue/profit drivers, peer differences, near-term verification nodes; evidence labels; non-empty missing-material list | Preamble scans/creates user workspace files and demands external tools; “do not start” on missing data blocks useful partial results; extra frontmatter conflicts with InvestKit contract | adopt questions and evidence classes; replace side effects with Runtime task state and completed/skipped semantics |
| Anthropic initiating coverage Task 1 | Strong filing/IR/source inventory; separates company, management, customers, competition, industry, and risks; staged prerequisites | “No prerequisites” conflicts with evidence needs; word counts drive volume over materiality; no fact/assumption/unknown schema; unsupported institutional-brand quality claims | modify into bounded sections with input gates and materiality, not word quotas |
| Vibe deep-company series | Excellent revision controls: caliber consistency, double-counting scan, source checks, anti-pseudo-precision, cascade repair after a changed fact | Publication series and huge output are wrong trigger; mixes valuation/buy-sell framing; embedded tool calls and fixed example warnings are not portable | adopt revision checklist only; reject series format and decision language |

Supporting evidence: InvestSkill's 10-K digest supplies a useful filing-section inventory and stale-document triggers, but its final bullish/bearish and buy/hold/sell block is prohibited and is not adopted.

### First-Party Design

1. Validate security identity, research question, as-of date, market, and available source set.
2. Build a source manifest with source ID, issuer/authority, document type, period, published/retrieved date, and freshness warning.
3. Extract company facts by topic: identity/history, products, segments, customers/channels, geography, management/governance, capital allocation, competitors/value chain, regulation, and major risks.
4. Create claims only through typed records: fact with source IDs, interpretation with fact dependencies, assumption, or unknown.
5. Identify changes against a prior comparable period without assuming that omitted disclosures mean improvement.
6. Produce materiality-ranked findings, contradictions, and questions that name the source/data needed to resolve them.
7. Hand structured company facts to business-model analysis; hand filing/period metadata to financial analysis.

Missing sources produce a useful bounded result with explicit unknowns or a justified `skipped` status. They never trigger training-data substitution.

### Eval Implications

- Positive: “Build a deep company dossier from these annual-report and profile fixtures.”
- Near miss: “Calculate DCF value” routes to valuation, not company deep research.
- Adversarial: a management claim without independent support remains a sourced management statement, not a fact about market share.
- Missing-data: no management/governance source yields unknown records, not invented biographies.

## Capability 2: `business-model-analysis`

### Responsibility Boundary

Explain who pays, what value is delivered, how revenue and cash are generated, cost/capital intensity, channels, segment mix, unit economics where applicable, value-chain position, concentration, durability, and fragility. It consumes company facts and normalized financial inputs. It does not own broad company history, full peer comps, final moat/industry research, statement normalization, or valuation.

### Four Design-Changing Candidates

| Candidate | Strengths | Defects and risks | Decision |
|---|---|---|---|
| China-stock business/transition/moat set | Separates signed order, backlog, delivered revenue, and collected cash; connects segments/customers/regions to margin, receivables, and cash; falsifiable transition milestones | Strong project/A-share bias; three Skills overlap; no stable cross-market schema | adopt order-to-cash states and transition tests; merge into one business-model contract with conditional overlays |
| Anthropic unit economics | Revenue-model routing; ARR bridge, cohort retention, CAC/payback, concentration, recurring/non-recurring split, margin waterfall; warns NDR can hide churn | SaaS benchmarks are not universal; raw customer data is often unavailable; score lacks provenance and uncertainty handling | adopt conditional metric families; treat benchmarks as sourced context, never universal pass/fail |
| Octagon business description + segmentation | Good Item 1 anatomy, value-chain and revenue-model taxonomy, year-over-year disclosure comparison, peer-claim verification, segment share calculations | Requires Octagon MCP; hard concentration cutoffs and example outputs are provider-shaped; no missing-data contract | adopt anatomy/questions; reimplement from normalized facts and remove MCP dependency/absolute cutoffs |
| Longbridge main-business analysis | Excellent period, unit, split-dimension, continuity, acquisition/disposal, missing-dimension, CR1/CR3/HHI, growth-contribution, and source controls | Mandates vendor CLI, update/install behavior, network search, and Longbridge-only preference; thresholds can misclassify sectors; segment math is not the whole business model | adopt normalization and decomposition; reject vendor routing, auto-update, and universal labels |

### First-Party Design

1. Classify the revenue model: product, service, subscription, transaction/usage, advertising, licensing, project/order, financial spread, or hybrid.
2. Map customer/value proposition, payer/user distinction, channel, pricing basis, contract duration, renewal/retention evidence, and value-chain role.
3. Normalize segment/product/geography/customer dimensions without mixing them; record period, units, consolidation basis, and restatements.
4. Analyze mix, concentration, contribution to growth, gross/contribution margin where available, working-capital needs, capex intensity, and cash conversion.
5. Apply only model-relevant diagnostics: cohorts/ARR for recurring models, take rate for transactions, backlog stages for projects, utilization for capacity models.
6. Distinguish recurring/structural growth from acquisitions, price, FX, pull-forward, one-offs, and accounting reclassification.
7. Output business-model strengths, fragilities, falsification indicators, and missing inputs without assigning a buy/sell conclusion.

Concentration metrics are facts; “high” or “low” is an interpretation requiring sector context. Unknown cohort, customer, or margin data stays unknown and is never filled with an industry average.

### Eval Implications

- Positive: hybrid company fixture requires separate product and recurring-service economics.
- Near miss: “Compare peer valuation multiples” routes to comps.
- Missing data: no customer-level data skips cohort/LTV calculations but preserves segment analysis.
- Integrity: changed segment definitions break trend calculation unless a documented bridge exists.

## Capability 3: `financial-statement-analysis`

### Responsibility Boundary

Normalize and analyze the income statement, balance sheet, and cash-flow statement across comparable periods. Own definitions, periods, units, currency, accounting basis, statement linkage, growth/margin/return/leverage/liquidity/working-capital calculations, and data-quality warnings. Supply normalized facts and estimates to earnings quality and valuation; do not issue an accounting-quality score, fraud probability, or trade signal.

### Four Design-Changing Candidates

| Candidate | Strengths | Defects and risks | Decision |
|---|---|---|---|
| InvestSkill financial-report analyst | Filing orientation, auditor/restatement checks, MD&A driver extraction, GAAP/non-GAAP reconciliation, debt maturities, three statements, footnotes, and prior-period comparison | Demands live price even when irrelevant; permits warned training-data estimates; arbitrary thresholds/scores; ends in technical/trading signals | adopt filing workflow and tables; reject live-price gate, estimates fallback, scoring, and signals |
| Vibe financial-statement | Clear three-statement map, linkage questions, DuPont decomposition, accounting-framework/seasonality/consolidation caveats | Universal “healthy ranges,” simplistic reconciliation tolerances, unsupported fraud-probability table, buy/avoid language | adopt equations as named methods with denominator/period guards; reject thresholds and probability claims |
| China-stock financial health | Ties ratios to filings, records period and audited status, separates fact from judgment, covers cash conversion, debt, impairment, and stress paths | Collapses statement analysis and earnings quality; A-share bias; formula/sector details live outside the reviewed Skill | adopt provenance and stress-path questions; split quality judgment into the next capability |
| Longbridge financial report | Explicit annual/semiannual/quarterly/cumulative period selection; all-three requirement for reconciliation; transparent partial-statement behavior; average-assets accrual denominator | Vendor execution/login/update dependency; retained-earnings linkage is oversimplified without dividends/OCI/FX/restatement bridge | adopt missing-statement degradation and period taxonomy; reject provider coupling and simplistic equality |

The cookbook ratio Skill is too thin to lead the design. Its suggestion to use industry averages for missing values is rejected: imputation would turn missing facts into unstated estimates.

### First-Party Design

1. Validate company, fiscal period, currency, scale, accounting standard, annual/interim/cumulative nature, audit status, and consolidation basis.
2. Preserve original line items and map them into a versioned canonical taxonomy with mapping warnings.
3. Compare like-for-like periods; reject mixed annual/cumulative/quarterly arithmetic and disclose restatements or segment/consolidation changes.
4. Calculate only when all inputs and denominator rules are available; label derived values as estimates/model outputs with formula and inputs.
5. Analyze income drivers/margins, asset quality and working capital, liquidity/debt maturity, cash-flow components, and return decomposition.
6. Reconcile cash and earnings through explicit bridges; retained earnings must account for distributions and other equity movements.
7. Return normalized statement facts, trends, calculations, anomalies, missing fields, and source IDs for downstream consumers.

Financial and non-financial sectors need different applicable metrics. Negative or near-zero denominators, acquisition periods, seasonal quarters, and currency changes must yield warnings or skipped calculations rather than misleading ratios.

### Eval Implications

- Positive: three annual periods with complete statements and a documented restatement.
- Near miss: a request solely to judge earnings manipulation routes to earnings quality after statement normalization.
- Missing data: absent cash flow allows statement analysis but forces reconciliation and cash metrics to `skipped`.
- Calculation safety: a negative net-income denominator must not emit a normal cash-conversion percentage.

## Capability 4: `earnings-quality-analysis`

### Responsibility Boundary

Assess whether reported earnings are cash-backed, repeatable, and supported by defensible accounting. Own accrual/cash conversion, working-capital behavior, revenue recognition, one-offs, non-GAAP reconciliation, capitalization, reserves/impairments, asset quality, auditor/restatement/control evidence, and critical estimates. Do not own beat/miss versus consensus, guidance, stock reaction, catalysts, valuation, or trade action; those belong to `earnings-analysis`, thesis, catalyst, or valuation capabilities.

### Four Design-Changing Candidates

| Candidate | Strengths | Defects and risks | Decision |
|---|---|---|---|
| Vibe financial-statement quality sections | Useful accrual, cash conversion, receivable/inventory, non-recurring, auditor, capitalization, goodwill, and DuPont questions | Fixed cutoffs ignore industry, seasonality, negative earnings, and scale; red-flag count is falsely labeled fraud probability | adopt diagnostic families; reject fixed score and any fraud-probability inference |
| InvestSkill financial-report analyst | Strong revenue-recognition, non-GAAP, working-capital, FCF, SBC, footnote, related-party, estimate, auditor, restatement, and control review | “Cash flow is hardest to manipulate” is overconfident; fixed 5%/30%/80% thresholds and 21-point quality score lack calibration; trading block is prohibited | adopt evidence checklist and multi-period change analysis; use contextual materiality and confidence |
| Octagon cash-flow + footnote analysis | Working-capital components, CCC, cash sources, debt/covenants, revenue policy, estimates, leases, contingencies, pensions, stock comp, policy-change comparison | MCP/provider dependency; FCF and days formulas need explicit definitions, average balances, and period annualization; directional heuristics can fail | adopt categories and source questions; independently implement guarded calculations |
| China-stock financial health | Strong filing linkage, audited-status label, fact/judgment separation, impairment/guarantee/refinancing unknowns, explicit risk-transmission paths | Quality and solvency are combined; A-share-specific overlays; no calibrated confidence model | adopt provenance and open-question design; keep solvency facts as inputs, not a composite quality verdict |

HHFin's quarterly earnings Skill is useful as a boundary test: its Parse/Compare cash-quality questions belong partly here, but consensus comparison, price context, scorer defaults, and position actions belong to `earnings-analysis`. Missing inputs must not silently receive neutral defaults.

### First-Party Design

1. Require normalized multi-period statements plus available filing/accounting-policy/footnote evidence; record gaps and audit status.
2. Analyze operating-cash-flow to earnings, accrual measures, FCF conversion where defined, and the specific working-capital bridge.
3. Test revenue quality through recognition policy, contract assets/liabilities, receivable days, returns/allowances, concentration, and organic versus acquired growth.
4. Separate recurring operating earnings from asset sales, fair-value changes, tax benefits, restructuring, acquisition effects, and management-defined adjustments.
5. Review capitalization/expense choices, reserves, impairment assumptions, goodwill/intangibles, leases, pensions, contingencies, related parties, controls, auditor changes, and restatements.
6. Express every red flag as evidence plus alternative explanations and required follow-up; a flag is not proof of manipulation.
7. Output supported positives, concerns, unknowns, methods/inputs, confidence, and risk paths without a numeric fraud probability or action recommendation.

Thresholds may be used only when the method, sector applicability, period, and source are recorded. The default offline Eval should emphasize directional consistency and evidence sufficiency, not a universal quality score.

### Eval Implications

- Positive: profit rises while OCF falls because receivables and contract assets expand; analysis must trace the bridge.
- Counterexample: negative OCF caused by a documented seasonal inventory build must remain a concern with an alternative explanation, not a fraud claim.
- Missing data: no footnotes yields a partial result with accounting-policy unknowns and lower evidence confidence.
- Boundary: consensus beat and guidance revision are handed to `earnings-analysis`, not used to score accounting quality.

## Cross-Capability Handoffs

| Producer | Required handoff | Consumer guard |
|---|---|---|
| security identification | canonical security/market/entity IDs | all four reject ambiguous identities |
| company deep research | company facts, filing/source manifest, management/capital-allocation facts, open questions | business model does not re-invent source facts |
| business model analysis | revenue-model class, segment/customer/channel/value-chain facts, unit-economics availability, fragilities | financial statements preserve reported accounting dimensions rather than forcing business segments to match |
| financial statement analysis | normalized periods/units/line items, derived metrics with formulas, anomalies, missing fields | earnings quality does not calculate from unvalidated or mixed-period inputs |
| earnings quality analysis | quality positives/concerns, alternative explanations, unknowns, accounting risk paths | thesis consumes evidence without converting flags into certainty |

All four use the Runtime capability envelope with `facts`, `assumptions`, `estimates`, `unknowns`, `findings`, `risks`, `warnings`, `source_ids`, `method`, and `skill`. A factual finding must reference persisted source IDs; an estimate must name its inputs and method.

## Data And Provider Implications

- CICCWM-002 demonstrates useful statement/report-period and raw-field semantics: income, cash flow, balance, indicators, empty string not zero, and uncertain field definitions. Its script reads a home-directory credential and sends credential-bearing telemetry; five sibling packages have worse TLS behavior. Execution remains blocked and license is unknown.
- Eastmoney demonstrates provider normalization needs: security/entity identity, indicator codes and labels, raw versus standardized tables, date granularity, and query provenance. Its script requires network/dependencies and writes to a fixed path outside the project, so it is not reusable Runtime code.
- GF-002 and GF-003 identify useful F10, segment/industry, profitability, leverage, cash-flow, growth, valuation, year, and report-type fields. Authorization, license, units, restatement policy, output schema, and fixture behavior remain unknown.
- These are `api_integration_candidate` inputs only if a named capability later lacks data. No Provider is needed to complete this offline synthesis, and none was called or implemented.

## Rejected Design Patterns

- Direct installation or execution of any raw Skill, script, CLI, MCP, installer, or package.
- Reading credentials from a home directory, credential-bearing telemetry, weak TLS, external fixed output paths, or automatic update/install behavior.
- Provider-exclusive source policy inside an analytical Skill.
- Training-data estimates, silent industry-average imputation, or neutral defaults for missing evidence.
- “Institutional quality” claims justified only by bank-name references, output length, or visual formatting.
- Universal health ranges and sector-blind cutoffs presented as facts.
- Red-flag counts presented as fraud probabilities or deterministic investment conclusions.
- Bullish/bearish scores, buy/hold/sell instructions, position actions, target prices, or return promises.
- Combining source facts, management statements, model outputs, assumptions, and unknowns in one narrative layer.
- Treating LangAlpha's near-identical initiating-coverage body as an independent method vote.

## License And Governance Conclusion

- Apache-2.0 or MIT root evidence supports further review, not automatic reuse of every nested file.
- The LangAlpha initiating-coverage file explicitly declares derivation and differs from Anthropic mainly in frontmatter; it is duplicate provenance, not independent synthesis evidence.
- CICCWM licenses remain unknown and security findings block execution/integration.
- Guangfa authorization, license, API terms, and redistribution rights remain unknown.
- Guosen content is unavailable; no favorable or adverse method judgment is possible.
- InvestKit should record ideas as paraphrased methodology decisions, write its own contracts/tests/fixtures, and require owner approval before any licensed code reuse or Provider promotion.

## Implementation Guidance For The Parent Task

1. Keep four separate Skill responsibilities; do not preserve the v0.1 combined financial-analysis shape.
2. Share one typed evidence/result envelope and one guarded calculation policy.
3. Implement source/period/unit/accounting-basis validation before formulas.
4. Make `company-deep-research` source-led, `business-model-analysis` model-led, `financial-statement-analysis` normalization-led, and `earnings-quality-analysis` evidence-and-accounting-led.
5. Add Eval fixtures for missing sources, changed segment definitions, incomplete statements, negative denominators, restatements, one-offs, and plausible alternative explanations.
6. Preserve partial results and justified skips; never fabricate or overwrite completed artifacts on resume.
7. Keep every broker/API observation subordinate to a concrete data gap and outside the offline acceptance path.

No third-party content was installed, executed, imported, or called during this study.
