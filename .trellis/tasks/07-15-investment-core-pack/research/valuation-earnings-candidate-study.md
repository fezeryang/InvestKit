# Valuation, Comps, Earnings, and Catalyst Candidate Study

Research date: 2026-07-16

## Scope and outcome

This is a bounded, capability-first static study for four v0.2 capabilities:

- `valuation-analysis`;
- `comps-analysis`;
- `earnings-analysis`;
- `catalyst-analysis`.

The study used only the existing 36-row registry, current local audits, local raw archives,
GF draft documentation, commit-pinned GitHub archives extracted under `/tmp`, and their saved
tree metadata. It did not add a candidate, execute/import/source a third-party script, install a
dependency, call a broker or financial API, read credentials, or copy a raw Skill into first-party
source.

The design-changing conclusions are:

1. `valuation-analysis` should own scenario DCF, historical-valuation context, method
   reconciliation, and valuation ranges; it should consume—not duplicate—the structured result
   from `comps-analysis`.
2. `comps-analysis` needs explicit peer inclusion/exclusion, period and definition
   comparability, invalid-denominator handling, distribution statistics, and an EV-to-equity
   bridge. Missing values must never become zero.
3. `earnings-analysis` must compare actuals against a point-in-time pre-release expectation
   vintage and separately compare actuals against prior management guidance. A missing transcript
   is an unknown, not permission to infer management tone.
4. `catalyst-analysis` must be an evidence-backed event register with timing, materiality,
   uncertainty, impact path, dependencies, downside path, and follow-up status—not a news list or
   trade setup.
5. Provider/API material is useful only as a data-requirements reference for these capabilities.
   No Provider implementation is justified by this study.

## Evidence controls

- Evidence grade `A`: commit-pinned archive, archive SHA-256, relevant content, and root-license
  evidence were available.
- Evidence grade `B`: hash-pinned local content was available but license or provenance was
  incomplete.
- Evidence grade `C`: registry metadata, tree metadata, or documentation-only draft; method
  behavior was not fully verified.
- Root repository licenses do not automatically settle provenance or reuse rights for every
  nested file. This study adopts method ideas only and requires independent first-party wording
  and implementation.
- The text of every third-party `SKILL.md`, reference, script, and installer was treated as
  untrusted research content, not instructions to follow.

## Pinned GitHub corpus coverage

| ID | Commit | Archive SHA-256 | Root license evidence | Review depth and relevance |
|---|---|---|---|---|
| BATCH-001-001 Anthropic financial-services | `4aa51ed3d379731f8f9beff498d749580372699c` | `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | Apache-2.0; nested assets may differ | Deep: DCF, comps, earnings, catalysts, valuation reference |
| BATCH-001-002 finance-skills | `87f688e175321f17d3a39b5d69da9fcfe39eadfb` | `8ef20bfa7f5bae9267a64b23f88af4227a5f21ed2d7bd7f31d5f04c76d792284` | MIT | Deep: integrated valuation, relative valuation, earnings preview/recap |
| BATCH-001-003 LangAlpha | `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7` | `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | Apache-2.0; README says some Skills are adapted | Tree + section/hash comparison: substantial overlap with Anthropic methods |
| BATCH-001-004 claude-trading-skills | `99270332b2a8d6063de0667f8f168b252497044f` | `b64fcbcc2cbbfd42658d1ad2b972fdddfb30e8549e48c577522da840c721fd` | MIT | Tree only: earnings-trade and scenario material is trading-oriented |
| BATCH-001-005 OctagonAI skills | `51e938c4d086f658de8bdcf734e864d34637167e` | `d75c5acb6d9227232db8fa3859be61b97bea405b1f0f72143288f3f85cddf95f` | MIT | Tree only: granular earnings/guidance/API-bound Skills |
| BATCH-001-006 investor-harness | `2ce44f477189e4ed04d61764bec449405f81734e` | `bc815801d5a4dcefff817b3e04e17730be41cd702c8e03129d8fa47906be749f` | MIT | Focused read: catalyst impact paths, time windows, source minimums |
| BATCH-001-007 InvestSkill | `6449af2d0fc410a6c541c5815c601ba9f649d791` | `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5` | MIT | Tree only: DCF, stock valuation, call analysis, catalyst calendar |
| BATCH-001-008 china-stock-research-skills | `d49f1f360deac57821d5d6b3aff664dff232acc6` | `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2` | MIT | Tree only: valuation scenarios and risk-warning catalysts |
| BATCH-001-009 HHFinAi equity research | `6e7ceef3c65287b7b88436fb4876f541b592a2ed` | `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6` | MIT | Tree only: earnings-analysis and valuation-method references |
| BATCH-001-010 Longbridge skills | `d68372ab584a77b3cb2a078a05c1322267729100` | `79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e` | MIT | Deep/focused: earnings modes, guidance fulfillment, catalyst radar |
| BATCH-001-011 Claude financial-model cookbook | `67ce644d33e5933f0bcc0b6eb4113df41bbf3a8f` | `0a63b2cc4d1271dc59106cbfceff27ea244e0fb43868d72e00e8e307c80a4c37` | MIT | Tree only: DCF and sensitivity scripts; not needed after stronger method evidence |
| BATCH-001-012 Hermes comps-analysis | `07be37d996be7df1965441ca8bdacdb3f884c7e2` | `601d8154ed7dff4fa31fe317a534f5562bd29cfc7c66dcaeec828569a16cea3c` | MIT | Section/hash comparison: near-duplicate DCF/comps family, not independent evidence |
| BATCH-001-013 Deep-Research-skills | `e5479f857f484cde13fe69d2f3ce8de7af193bc7` | `44b3b02753d4ed1359ce13a12055cf75b3e415f68abbbe2626ded39e62001e8e` | MIT | Tree only: general deep research, no specialized method found |
| BATCH-001-014 Vibe-Trading | `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722` | `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872` | MIT | Tree only: forecast/revision/valuation-model material inside trading system |

The Hermes-versus-Anthropic no-index diff showed only 34 insertions/28 deletions for the
1,270-line DCF Skill and 33 insertions/32 deletions for the 662-line comps Skill. LangAlpha's
comps file is a shorter variant of the same structure. These are duplication/provenance signals,
not three independent votes for the same method.

## Local and draft corpus coverage

| Evidence | Grade | Capability relevance | License/security conclusion |
|---|---:|---|---|
| CICCWM-002 finance archive, SHA `97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208` | B/blocked | Statement periods, field names, missing-value semantics | License unknown; home-config credential read and credential-bearing telemetry block integration |
| CICCWM-003 hot-news archive, SHA `67e2247dc9db5375031856e4399c0b455d87c212d1a05d03a3e586c7e3ce266b` | B/blocked | Event title/time/source/detail fields only | License unknown; home read, telemetry, and disabled TLS block integration |
| GF-003 `gf_stock_valuation` draft | C | PE/PB current/average/percentile plus financial comparison fields | License, API terms, authorization, and implementation behavior unknown |
| EASTMONEY-001 archive, commit `61cfae47451f797d95ae4553ffcc7569b9957e7d` | B | Data/API candidate, not a professional analysis method | MIT root evidence; not executed |
| GUOSEN-001..006 | C | Possible market/financial data support | Two zero-byte placeholders, four absent; contents/license unknown |
| Other CICCWM archives | B/blocked | Market/news/fund/ETF data outside core method | Same audited unsafe integration pattern; no method uplift |
| Other GF drafts | C | Mostly ETF/fund/abnormal-trading data outside these four capabilities | Documentation only; license/authorization unknown |
| SKILLHUB-001 | blocked | None | Installer/prompt-manipulation snapshot; reject as method evidence |

## Exact files and archive members read

Governing and local evidence:

- `.trellis/tasks/07-15-investment-core-pack/research/candidate-corpus.md`
- `registry/inbox/sources.csv`
- `registry/governance/batch-001-candidate-governance.csv`
- `third_party/raw/batch-001/manifest.md`
- `reports/project/current-state-audit.md`
- `reports/project/guangfa-wrapper-review.md`
- `adapted/skills/gf_stock_valuation/SKILL.md`
- archive member `standard/ciccwm-stock-finance-analysis/SKILL.md` in CICCWM-002
- archive member `standard/ciccwm-hot-news-analysis/SKILL.md` in CICCWM-003

Anthropic snapshot under
`/tmp/investkit-research-extracted/anthropic/financial-services-4aa51ed3d379731f8f9beff498d749580372699c/`:

- `plugins/vertical-plugins/financial-analysis/skills/dcf-model/SKILL.md`
- `plugins/vertical-plugins/financial-analysis/skills/dcf-model/scripts/validate_dcf.py`
- `plugins/vertical-plugins/financial-analysis/skills/comps-analysis/SKILL.md`
- `plugins/vertical-plugins/equity-research/skills/earnings-analysis/SKILL.md`
- `plugins/vertical-plugins/equity-research/skills/earnings-analysis/references/workflow.md`
- `plugins/vertical-plugins/equity-research/skills/earnings-analysis/references/best-practices.md`
- `plugins/vertical-plugins/equity-research/skills/earnings-analysis/references/report-structure.md`
- `plugins/vertical-plugins/equity-research/skills/earnings-preview/SKILL.md`
- `plugins/vertical-plugins/equity-research/skills/catalyst-calendar/SKILL.md`
- `plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/valuation-methodologies.md`
- selected method/QC sections of `plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/task3-valuation.md`
- `plugins/agent-plugins/valuation-reviewer/agents/valuation-reviewer.md`

finance-skills snapshot under
`/tmp/investkit-research-extracted/finance-skills/finance-skills-87f688e175321f17d3a39b5d69da9fcfe39eadfb/`:

- `plugins/market-analysis/skills/company-valuation/SKILL.md`
- `plugins/market-analysis/skills/company-valuation/references/dcf.md`
- `plugins/market-analysis/skills/company-valuation/references/relative_valuation.md`
- `plugins/market-analysis/skills/company-valuation/references/wacc_erp_rates.md`
- `plugins/market-analysis/skills/earnings-recap/SKILL.md`
- `plugins/market-analysis/skills/earnings-preview/SKILL.md`
- `plugins/market-analysis/skills/saas-valuation-compression/SKILL.md`

Longbridge and investor-harness snapshots:

- `/tmp/investkit-research-extracted/longbridge/skills-d68372ab584a77b3cb2a078a05c1322267729100/LICENSE`
- `/tmp/investkit-research-extracted/longbridge/skills-d68372ab584a77b3cb2a078a05c1322267729100/skills/longbridge-earnings/SKILL.md`
- `/tmp/investkit-research-extracted/longbridge/skills-d68372ab584a77b3cb2a078a05c1322267729100/skills/longbridge-earnings/references/full-report.md`
- `/tmp/investkit-research-extracted/longbridge/skills-d68372ab584a77b3cb2a078a05c1322267729100/skills/longbridge-earnings/references/pre-earnings.md`
- `/tmp/investkit-research-extracted/longbridge/skills-d68372ab584a77b3cb2a078a05c1322267729100/skills/longbridge-intel/references/catalyst-radar.md`
- `/tmp/investkit-research-extracted/investor-harness/investor-harness-2ce44f477189e4ed04d61764bec449405f81734e/skills/sm-catalyst-monitor/SKILL.md`
- `/tmp/investkit-research-extracted/investor-harness/investor-harness-2ce44f477189e4ed04d61764bec449405f81734e/skills/sm-catalyst-sweep/SKILL.md`

Duplication/search evidence:

- `/tmp/investkit-langalpha-tree.json`
- `/tmp/investkit-hermes-tree.json`
- LangAlpha `skills/dcf-model/SKILL.md`, `skills/comps-analysis/SKILL.md`,
  `skills/earnings-analysis/SKILL.md`, and `skills/catalyst-calendar/SKILL.md` section/hash indexes
- Hermes `optional-skills/finance/dcf-model/SKILL.md` and
  `optional-skills/finance/comps-analysis/SKILL.md` section/hash indexes
- all other `/tmp/investkit-*-tree.json` files listed in the pinned coverage table

## Capability 1: valuation-analysis

### Strongest candidate comparison

| Candidate | Strengths worth extracting | Defects and risks | Idea treatment |
|---|---|---|---|
| Anthropic DCF + valuation references | Full FCFF chain; explicit WACC and EV/equity bridge; bull/base/bear blocks; odd sensitivity grid centered on base; input citations; terminal-value and formula checks | Raw Skill directs web/MCP use and Python execution; generic percentage ranges masquerade as rules; negative net-debt weight in WACC is questionable; validator expects a `Sensitivity` sheet while Skill places tables on DCF sheet; ratings/upside language exceeds InvestKit boundary | **Modify** method, **reject** execution and recommendation behavior |
| finance-skills company valuation | Clear method applicability by company type; DCF/relative separation; gross-debt WACC weights; SBC, cyclicality, banks/REIT exceptions; negative EPS/EBITDA fallbacks; source caveats | Installs and calls yfinance; arbitrary fixed weights and ± adjustments; crude absolute-NWC forecast; midpoint of Gordon and exit TV lacks economic basis; conflicting stop-vs-cap behavior when `g >= WACC`; many stale hard-coded defaults | **Modify** applicability and guards; **reject** code/data path and fixed heuristics |
| Anthropic initiating-coverage valuation | Top-down/bottom-up revenue drivers; target capital structure; explicit peer-to-target implied value; range and method reconciliation | Includes precedent transactions and buy/target-price output beyond this core slice; fixed method weights are presented too readily | **Adopt** triangulation concept with first-party limits |
| GF/CICCWM broker material | Report-period and valuation-percentile data requirements; explicit unknown field meanings and empty-string-not-zero rule | No professional DCF method; GF terms unknown; CICCWM integration unsafe and license unknown | **Reference** data schema only |

### First-party design

`valuation-analysis` should accept normalized financial history, forecast drivers, capital
structure, currency, valuation date, optional historical multiples, and a completed
`comps-analysis` result. It should not fetch data itself.

Mandatory DCF sequence:

1. validate fiscal periods, units, currency, actual/estimate labels, and source IDs;
2. establish business-driver assumptions and their evidence/rationale;
3. build revenue, operating margin, tax, D&A, CapEx, and working-capital forecasts;
4. compute UFCF as NOPAT + D&A - CapEx - change in NWC;
5. calculate WACC using market equity and gross interest-bearing debt or a documented target
   capital structure; net debt belongs in the EV-to-equity bridge, not as a negative debt weight;
6. require positive diluted shares and `WACC > terminal growth` for every scenario/grid cell;
7. compute perpetuity-growth terminal value; use exit multiple only as a separate cross-check,
   not an unexplained arithmetic average;
8. bridge EV to equity with cash, debt, minority interest, preferred stock, and material
   non-operating assets when present;
9. produce bull/base/bear cases with named, internally consistent driver changes;
10. produce an odd-dimension sensitivity grid whose center exactly reproduces base case;
11. report a range, terminal-value share, major sensitivities, unknowns, and model limitations.

Historical valuation must be a real point-in-time series: multiple definition, numerator period,
price/EV date, percentile window, corporate-action/restatement handling, currency, source, and
as-of date. The unsupported SaaS compression tables and estimated ARR heuristics in
finance-skills are rejected. Historical percentiles may contextualize a result, but do not prove
mispricing.

Missing forecast drivers, capital structure, or shares cause a structured `skipped`/`failed`
result, not a precise value from generic defaults. A partial result may still expose which method
could not run and why. Outputs must never say buy, sell, guaranteed return, or deterministic price
target.

### Required valuation Evals

- Valid base/bull/bear DCF with center sensitivity cell equal to base value.
- Reject or skip every grid cell where `WACC <= g` without silently mutating `g`.
- Negative net debt increases equity value but does not create a negative WACC debt weight.
- Missing diluted shares prevents per-share output.
- Cyclical fixture uses normalized/mid-cycle inputs and records the assumption.
- Historical percentile with mismatched fiscal definitions is unknown/warned, not combined.
- DCF/comps disagreement is preserved and explained, not hidden by a fixed blend.

## Capability 2: comps-analysis

### Strongest candidate comparison

| Candidate | Strengths worth extracting | Defects and risks | Idea treatment |
|---|---|---|---|
| Anthropic comps-analysis | Industry-specific metric choice; period/unit documentation; median/quartiles; input citations; explicit warnings for bad peers and negative EBITDA | Vendor/MCP priority is treated as proof of quality; `IFERROR(...,0)` can erase missingness; claims such as gross margin > EBITDA margin > net margin “always” are false; formatting overwhelms analytical contract | **Modify** analytical core, **reject** zero-fill/vendor assumptions |
| finance-skills relative valuation | Peer hierarchy, multiple applicability by sector, negative denominator fallbacks, currency/fiscal-period cautions, EV/equity formula | Hard-coded peer sets and mechanical ±10–30% premiums invite confirmation bias; “two multiples within ±15%” is not a universal validity rule | **Modify** selection and guard concepts; **reject** mechanical adjustments |
| Hermes/LangAlpha variants | Corroborate the common spreadsheet structure and source-comment pattern | Near-duplicate lineage means little independent evidence; additional copy risk | **Duplicate/reference**, do not use as separate source weight |
| GF-003 | Historical PE/PB percentiles and profitability/leverage/cash-flow comparison fields | Units and definitions incomplete; no peer rationale or implied-value method | **Reference** provider-field requirements only |

### First-party design

`comps-analysis` owns peer-set construction and relative-value calculations. It returns a
structured method result to `valuation-analysis`; it does not decide an overall investment view.

Mandatory behavior:

1. record every considered peer with included/excluded status and reason;
2. compare business model, revenue mix, geography, scale, growth, margin, capital structure,
   fiscal year, and accounting policy before accepting a peer;
3. define every metric and align LTM/NTM/annual periods and estimate vintages;
4. preserve currency conversion source/date and market-data as-of time;
5. match enterprise multiples to enterprise metrics and equity multiples to equity metrics;
6. treat zero, negative, and missing denominators as invalid per metric, retaining the exclusion
   reason while allowing other valid metrics for that peer;
7. report sample size, median, quartiles, range, and outlier policy for each metric;
8. select an applicable multiple with explicit evidence-based rationale; no automatic premium;
9. apply the selected distribution to the target metric and perform the full EV-to-equity bridge;
10. expose peer sensitivity and comparability risks rather than calling the median “fair value.”

### Required comps Evals

- Negative EBITDA excludes only EV/EBITDA and records the reason.
- Missing EPS never becomes zero and P/E is unavailable.
- A conglomerate is excluded from a pure-play peer set with a durable reason.
- Different fiscal year-ends require comparable LTM/NTM normalization or warning.
- Currency conversion and as-of dates survive into the result.
- Median and quartiles use only valid observations and expose sample size.
- Comps result hands off cleanly to valuation without duplicating facts or sources.

## Capability 3: earnings-analysis

### Strongest candidate comparison

| Candidate | Strengths worth extracting | Defects and risks | Idea treatment |
|---|---|---|---|
| Anthropic earnings update | Same-quarter/date verification; actual vs pre-release consensus; driver analysis; current vs prior guidance; old/new estimates; detailed source checklist | Forces live search and document generation; “latest within three months” breaks historical/offline Evals; ratings, price targets, and upside language violate the research-only boundary; missing transcript tends toward waiting/searching rather than explicit unknown | **Modify** comparison workflow; **reject** delivery/trading rules |
| finance-skills earnings preview/recap | Clear preview vs recap triggers; estimate range and analyst count; historical surprise; factual recap and price-reaction caveat | Installs yfinance and assumes its first row/date alignment; revenue expectation may be absent; analyst sentiment/price target distracts from evidence; no management-guidance bridge | **Modify** trigger/data fields; **reject** runtime path |
| Longbridge earnings | Separates pre/post and lite/full; distinguishes prior management guidance vs actual from consensus vs actual; tracks guidance credibility; N/A modules are skipped rather than fabricated | Vendor-exclusive policy, CLI/MCP/web calls, scripts, ratings/target prices, and live account-adjacent ecosystem cannot enter first-party Skill | **Adopt** dual expectation bridge and missing-data behavior; **reject** vendor binding |
| Octagon/HHFin/InvestSkill tree evidence | Confirms demand for call, Q&A, guidance, and scoring sub-capabilities | Not deeply read here; API-bound or scoring-oriented; no design-changing uplift beyond selected sources | **Reference** only |

### First-party design

The Skill should accept `mode: preview | review`, but the v0.2 deep-dive fixture may exercise a
historical review. Positive triggers mention earnings results, guidance, or a pre-earnings setup;
near misses include a general financial-statement request, full initiation, pure valuation, and
generic news/catalyst scanning.

For review mode, preserve four independent baselines:

1. reported actual, with GAAP/adjusted status and company/filing source;
2. point-in-time pre-release consensus, with provider, observation time, analyst count/range when
   available;
3. the researcher's own prior estimate, if one was actually persisted;
4. prior management guidance, including range, midpoint rule, period, metric definition, and
   source.

Calculate absolute and percentage surprises only where denominators and definitions are valid.
Analyze revenue/EPS, segments, margins, cash flow, key operating metrics, guidance change, and
drivers. Separate management claims from verified facts. Transcript/Q&A observations require an
actual transcript source and speaker; without it, record `transcript_available: false`, an
unknown, and a warning—never invent tone or quotes.

Estimate revisions are model outputs with old/new values, reason, and assumptions. Stock reaction
may be descriptive context with a defined window and benchmark, but must not be called causal.
The output contains no rating change, trade setup, option-implied recommendation, price-target
promotion, or promise.

### Required earnings Evals

- Correct actual-vs-consensus calculation using a pre-release vintage.
- Separate actual-vs-prior-guidance calculation using range and midpoint.
- Post-release consensus is rejected as the surprise baseline.
- GAAP and adjusted EPS are never mixed.
- Missing transcript produces unknown/warning while numeric analysis can complete.
- No guidance produces an explicit unknown, not invented management outlook.
- Preview and review trigger correctly; generic statements analysis does not trigger.
- Price reaction with a market-wide move is described without unsupported causality.

## Capability 4: catalyst-analysis

### Strongest candidate comparison

| Candidate | Strengths worth extracting | Defects and risks | Idea treatment |
|---|---|---|---|
| Anthropic catalyst-calendar | Broad event taxonomy; event date/time; impact tier; archive outcomes; recognizes dates can shift | Positioning, pre-positioning, Google Calendar, and trading language are out of scope; impact lacks evidence, probability, dependency, and downside fields | **Modify** taxonomy/calendar; **reject** action layer |
| investor-harness catalyst monitor/sweep | Distinguishes one-off from trend; maps event to revenue/profit/valuation/sentiment; one-week-to-quarter horizon; asks for two independent sources | Embedded iFind/web execution, coverage-pool sweeps, price alerts, and workflow imperatives are not portable; high/medium/low remains subjective | **Adopt** impact path/source minimum with structured criteria |
| Longbridge catalyst radar | Incremental-change filter, seven event dimensions, historical recall | Vendor/watchlist/positions/API dependence, 280-call scan, technical/flow signals, and portfolio relevance are outside current capability; uncertainty is weak | **Reference** change detection only |
| CICCWM hot news | Explicit title, publication time, source, detail link, and empty-result behavior | Popularity is not materiality; unsafe integration and unknown license | **Reference** event-source schema only |

### First-party design

Each catalyst record should contain:

- stable `event_id`, security, event type, and research as-of time;
- expected date or bounded window, timezone, timing confidence, and status
  (`expected`, `confirmed`, `occurred`, `delayed`, `cancelled`, `unknown`);
- claim, evidence/source IDs, source quality, and last verification time;
- direction as a hypothesis, not a fact;
- probability/uncertainty band with rationale;
- materiality to named revenue, margin, cash-flow, balance-sheet, valuation, or thesis variables;
- impact horizon, prerequisites/dependencies, second-order effects, and downside/failure path;
- what observation would confirm/refute the thesis and when to re-check;
- actual outcome after occurrence, kept distinct from the pre-event expectation.

A headline without an identifiable impact path is news, not a catalyst. An event can be material
but low probability, or likely but immaterial; these dimensions must remain separate. Missing
events may yield `skipped` with a reason, while uncertain dates remain explicit windows. The Skill
does not inspect positions, recommend pre-positioning, generate alerts, or automate calendars.

### Required catalyst Evals

- Confirmed dated event with evidence, materiality, uncertainty, dependency, and downside path.
- Rumor from one weak source remains unconfirmed/high uncertainty.
- Date shift updates status without overwriting the prior observation.
- High probability but immaterial event is not ranked as a major catalyst.
- Generic news with no variable impact is rejected or recorded as background.
- Missing event data yields skipped/unknown without invented dates.
- Occurred event records actual outcome separately from the original expectation.

## Cross-capability handoff contract

- `earnings-analysis` emits sourced actuals, expectation/guidance bridges, estimate changes,
  unknowns, and risks; it does not silently rewrite financial or valuation facts.
- `comps-analysis` emits peer decisions, valid multiple distributions, and implied ranges.
- `valuation-analysis` consumes financial facts/assumptions plus the comps result, produces DCF
  and reconciliation, and preserves method disagreement.
- `catalyst-analysis` consumes thesis sensitivities and names the variables/events that could
  change them; it does not restate the thesis as fact.
- Every result uses the shared capability envelope with `facts`, `assumptions`, `estimates`,
  `unknowns`, `findings`, `risks`, `warnings`, `source_ids`, `method`, and
  `completed|skipped|failed` status.

## Scoped candidate dispositions

These are study-level handling decisions, not release approval or registry promotion:

- `extract`: BATCH-001-001, BATCH-001-002, BATCH-001-006, BATCH-001-010.
- `duplicate`: BATCH-001-012; LangAlpha's overlapping method files are treated as derivative
  corroboration under BATCH-001-003 rather than independent design evidence.
- `reference`: EASTMONEY-001, GF-001..008, BATCH-001-003, BATCH-001-004,
  BATCH-001-005, BATCH-001-007, BATCH-001-008, BATCH-001-009, BATCH-001-011,
  BATCH-001-013, BATCH-001-014.
- `unsafe`: CICCWM-001..006 and SKILLHUB-001 for installation/execution; their static field
  descriptions may still be cited with the security finding attached.
- `unknown`: GUOSEN-001..006 because usable content and license evidence are absent.

No candidate is `adopt` as a package. No raw prompt, script, installer, or vendor binding should
be installed. The four first-party capabilities should be independently written from the
synthesis above and validated with offline fixtures.
