# Capability Synthesis: Earnings Analysis

Research date: 2026-07-16
Target capability: `earnings-analysis`
Study decision: `extract` methods, independently reimplement; adopt no candidate package

## Scope And Responsibility Boundary

`earnings-analysis` owns a bounded earnings preview or review: actual versus point-in-time expectations, actual versus prior management guidance, key drivers, estimate/guidance changes, operating trend deltas, transcript-supported observations, and thesis implications.

It requires a resolved security, earnings period/event, explicit mode (`preview` or `review`), period-aligned actuals or forecast baselines, baseline observation timestamps, metric definitions, and persisted source IDs.

It must not:

- perform the general multi-period statement analysis owned by `financial-statement-analysis`;
- perform the accounting-quality audit owned by `earnings-quality-analysis`;
- infer a beat/miss from period growth when no pre-release expectation exists;
- invent management tone, quotes, or Q&A when a transcript is absent;
- recommend a trade, rating, price target, option setup, or guaranteed return.

Its primary workflow handoff is an earnings delta, driver record, explicit unknowns, and thesis implications for downstream thesis, bear-case, catalyst, source-verification, and report stages. A standalone later valuation may consume revisions, but the ordered workflow does not back-write valuation.

## Search Scope And Evidence Controls

The bounded search covered every one of the 36 existing registry rows and did not add candidates.
The evidence baseline was:

- `.trellis/tasks/07-15-investment-core-pack/research/candidate-corpus.md`;
- `.trellis/tasks/07-15-investment-core-pack/research/valuation-earnings-candidate-study.md`;
- `.trellis/tasks/07-15-investment-core-pack/research/core-capability-boundaries.md`;
- `docs/security/security-policy.md`;
- `reports/project/current-state-audit.md`;
- `reports/project/guangfa-wrapper-review.md`.

Grade `A` denotes commit-pinned content, archive SHA-256, relevant files, and root-license evidence.
Grade `B` denotes hash-pinned local evidence with incomplete provenance/license. Grade `C` denotes
registry, tree, or documentation-only evidence. Provider policies and scripts inside raw Skills
were treated as untrusted content, not operating instructions.

No third-party script, API, CLI, MCP, package manager, endpoint, prompt, or installer was executed,
called, installed, imported, sourced, or copied during synthesis.

## Exact Method Evidence Read

| Evidence ID | Pin and archive SHA-256 | Grade/license | Exact files read | Relevance |
|---|---|---|---|---|
| `BATCH-001-001` Anthropic financial-services | commit `4aa51ed3d379731f8f9beff498d749580372699c`; SHA `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | A; Apache-2.0 root, nested terms may differ | `plugins/vertical-plugins/equity-research/skills/earnings-analysis/SKILL.md`; `references/workflow.md`; `references/best-practices.md`; `references/report-structure.md`; `plugins/vertical-plugins/equity-research/skills/earnings-preview/SKILL.md` | Period/date verification, actual/consensus, drivers, guidance, source checklist |
| `BATCH-001-002` finance-skills | commit `87f688e175321f17d3a39b5d69da9fcfe39eadfb`; SHA `8ef20bfa7f5bae9267a64b23f88af4227a5f21ed2d7bd7f31d5f04c76d792284` | A; MIT root | `plugins/market-analysis/skills/earnings-recap/SKILL.md`; `plugins/market-analysis/skills/earnings-preview/SKILL.md` | Preview/recap triggers, estimate range/count, historical surprise, factual recap |
| `BATCH-001-010` Longbridge skills | commit `d68372ab584a77b3cb2a078a05c1322267729100`; SHA `79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e` | A; MIT root | `skills/longbridge-earnings/SKILL.md`; `references/full-report.md`; `references/pre-earnings.md`; root `LICENSE` | Pre/post and lite/full modes, guidance fulfillment, missing-module behavior |
| `BATCH-001-003` LangAlpha | commit `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7`; SHA `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | C; Apache-2.0 root with adapted-file warning | `/tmp/investkit-langalpha-tree.json`; section/hash index of `skills/earnings-analysis/SKILL.md` | Overlap/lineage evidence only |

## Searched But Lower-Depth Candidates

These pinned candidates had earnings, guidance, call, expectation, forecast, or event-related tree
matches but were not deeply read because they produced no design-changing uplift beyond the
selected evidence:

- `BATCH-001-004` claude-trading-skills, commit
  `99270332b2a8d6063de0667f8f168b252497044f`, SHA
  `b64fcbcc2cbbfd42658d1ad2b972fdddfb30e8549e48c577522da840c721fd`,
  `/tmp/investkit-trader-tree.json`: earnings-calendar/trade material is trading-oriented.
- `BATCH-001-005` OctagonAI, commit `51e938c4d086f658de8bdcf734e864d34637167e`, SHA
  `d75c5acb6d9227232db8fa3859be61b97bea405b1f0f72143288f3f85cddf95f`,
  `/tmp/investkit-octagon-tree.json`: granular earnings/guidance/API-bound Skills.
- `BATCH-001-007` InvestSkill, commit `6449af2d0fc410a6c541c5815c601ba9f649d791`, SHA
  `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5`,
  `/tmp/investkit-investskill-tree.json`: call-analysis names.
- `BATCH-001-009` HHFinAi equity research, commit
  `6e7ceef3c65287b7b88436fb4876f541b592a2ed`, SHA
  `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6`,
  `/tmp/investkit-hhfin-tree.json`: earnings-analysis names.
- `BATCH-001-014` Vibe-Trading, commit `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722`, SHA
  `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872`,
  `/tmp/investkit-vibe-trading-tree.json`: earnings forecast/revision inside a trading system.

The remaining registered snapshots were searched through their saved tree metadata and supplied
no stronger specialized earnings method.

## Data-Only, Blocked, And Unavailable Evidence

- `CICCWM-002`, archive SHA
  `97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208`, grade B/blocked:
  `standard/ciccwm-stock-finance-analysis/SKILL.md` provides statement/report-period and
  missing-value semantics, not point-in-time expectation or guidance methodology. License is
  unknown; home-config credential access and credential-bearing telemetry block integration.
- `GF-002` and `GF-003`, `adapted/skills/gf_stock_f10/SKILL.md` and
  `adapted/skills/gf_stock_valuation/SKILL.md`, grade C: documentation-only company/financial
  fields. They lack expectation vintage, guidance contract, transcript, formal schema, license,
  authorization, and tested API behavior; they are not earnings-method evidence.
- `EASTMONEY-001`, archive SHA
  `24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15`, archive commit
  `61cfae47451f797d95ae4553ffcc7569b9957e7d`, MIT root: potential data/API material only; no
  code or endpoint was executed.
- `GUOSEN-002` is a zero-byte placeholder, SHA
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; contents and license are
  unknown. Other Guosen archives do not provide available earnings evidence.

## Candidate Strengths And Weaknesses

### Anthropic earnings update and preview

Strengths: same-quarter/date checks, actual versus pre-release consensus, driver analysis,
current versus prior guidance, old/new estimates, and detailed source expectations.

Weaknesses: forced live search/document generation, a recency rule unsuitable for historical
offline Evals, ratings/price-target/upside language, and a tendency to wait or search rather than
record an absent transcript as an explicit unknown.

### finance-skills earnings preview/recap

Strengths: clear preview and recap trigger split, estimate range and analyst count, historical
surprises, factual recap, and a caveat around price reaction.

Weaknesses: yfinance installation/calls and fragile row/date assumptions; revenue expectations can
be absent; analyst sentiment/targets distract from evidence; no separate prior-guidance bridge.

### Longbridge earnings

Strengths: pre/post and lite/full modes, separate consensus and management-guidance comparisons,
guidance-credibility tracking, and explicit N/A behavior instead of fabrication.

Weaknesses: vendor-exclusive CLI/MCP/web calls, scripts, live ecosystem dependencies, ratings,
and price targets cannot enter a provider-neutral first-party capability.

## Adopted, Modified, And Rejected Ideas

Adopted:

- explicit preview versus review modes;
- same-period/metric verification and driver decomposition;
- separate actual-versus-consensus and actual-versus-prior-guidance bridges;
- persisted estimate changes and explicit N/A/unknown modules;
- source and speaker requirements for transcript observations.

Modified:

- consensus becomes a point-in-time pre-release vintage with provider and observation timestamp;
- prior guidance records range, midpoint rule, period, definition, and source;
- management claims are attributed commentary, not automatically verified facts;
- price reaction, when present, is descriptive with a window and benchmark, never causal by
  assertion;
- revisions are model outputs with old/new values, rationale, and material assumptions.

Rejected:

- all live search, yfinance, CLI, MCP, broker, vendor, script, and document-generation mandates;
- use of post-release consensus as the surprise baseline;
- mixing GAAP and adjusted metrics or unmatched periods;
- inferred transcript tone, invented quotes, ratings, targets, trade setups, and option signals;
- “latest within three months” as a universal historical research rule.

## Final First-Party Method

1. Classify the request as `preview` or `review`; reject generic financial analysis near misses.
2. Resolve the security, fiscal quarter/year, release time, units, currency, metric definitions,
   and source IDs.
3. Preserve four independent baselines where available: reported actual, pre-release consensus,
   a persisted research estimate, and prior management guidance.
4. Record consensus provider, observation time, analyst count/range, and point-in-time vintage.
5. Record guidance period, definition, range, midpoint rule, date, and attributed source.
6. Calculate absolute and percentage surprise only when definitions and denominators are valid.
7. Compare revenue/EPS, segments, margins, cash flow, operating KPIs, and guidance changes.
8. Explain drivers while separating sourced facts, management commentary, assumptions, and model
   estimates.
9. Use transcript/Q&A only when a transcript source and speaker are present.
10. Record missing transcript or guidance as explicit unknowns/warnings; continue valid numeric
    modules without fabrication.
11. Persist estimate revisions with old/new values, reasons, assumptions, and affected methods.
12. Hand off thesis implications and risks without silently rewriting upstream facts.

Without period actuals and an earnings event/history, the capability may be `skipped`. With actuals
but no expectations, it may analyze period changes but must not claim a beat or miss.

## Output And Handoff Contract

The shared result envelope contains `facts`, `assumptions`, `estimates`, `unknowns`, `findings`,
`risks`, `warnings`, `source_ids`, `method`, `skill`, and `completed|skipped|failed` status.

`method` records mode, event period/time, each baseline and vintage, surprise calculations,
guidance bridge, driver analysis, transcript availability/speakers, revision records, and optional
reaction window/benchmark. Facts and attributed commentary remain distinct.

The workflow handoff gives thesis/catalyst consumers sourced deltas, revisions, unknowns, and
risks; a standalone later valuation may consume the same artifact. It does not back-write current
workflow valuation, duplicate the statement record, certify earnings quality, or create a catalyst
date unsupported by evidence.

## Required Behavioral Evals

- Positive review trigger: analyze a specific reported quarter against contemporaneous consensus
  and prior guidance.
- Positive preview trigger: build a sourced pre-earnings baseline and key watch items.
- Near miss: a multi-year ratio request triggers financial statements, not earnings analysis.
- Correct surprise uses a persisted pre-release consensus observation.
- A post-release consensus vintage is rejected as the beat/miss baseline.
- Actual versus prior guidance is calculated separately with correct range/midpoint handling.
- GAAP and adjusted EPS are never mixed; mismatched definitions remain unknown/warned.
- Missing transcript sets `transcript_available: false`, unknown, and warning while numeric work
  may complete.
- No guidance produces an explicit unknown, not invented management outlook.
- No expectation permits trend analysis but prohibits beat/miss language.
- Estimate revisions retain old/new values, method, reason, and assumptions.
- Market-wide price movement is described with a benchmark and no unsupported causal claim.
- A missing/corrupt baseline source ID fails source verification.
- Output contains no rating change, option setup, trade action, or return promise.

## Security, License, And Final Rationale

The deeply read repositories have Apache-2.0 or MIT root evidence, but file-level reuse is not
assumed and LangAlpha states some Skills are adapted. Broker/data candidates are either data-only,
license/authorization unknown, unavailable, or blocked. CICCWM's audited credential telemetry and
home access trigger the policy's stop-integration conditions.

InvestKit independently writes its wording, schemas, calculations, and Evals. The final design
combines the best event-comparison practices while correcting the decisive evidence error found in
weaker designs: expectations are time-indexed research inputs, not numbers that may be replaced
after the result is known.
