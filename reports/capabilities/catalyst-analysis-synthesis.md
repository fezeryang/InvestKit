# Capability Synthesis: Catalyst Analysis

Research date: 2026-07-16
Target capability: `catalyst-analysis`
Study decision: `extract` methods, independently reimplement; adopt no candidate package

## Scope And Responsibility Boundary

`catalyst-analysis` owns an evidence-backed, monitorable event ledger: event identity, date or window, timing confidence, status, materiality, probability/uncertainty, impact mechanism, dependencies, downside path, validation observations, and post-event outcome.

It requires a resolved security, research as-of time, company/earnings/thesis context, sourced event evidence, and named business, financial, valuation, or thesis variables that an event may change.

It must not:

- turn every headline, risk, or market rumor into a catalyst;
- inspect portfolio positions or propose pre-positioning;
- create alerts, calendar automation, coverage-pool sweeps, or a trading setup;
- present direction or event impact as fact before the event resolves;
- invent dates when evidence provides none.

Its primary handoff is a monitorable event ledger for source verification and investment report, with links back to thesis sensitivities and earnings/valuation variables.

## Search Scope And Evidence Controls

The static search covered all 36 existing registry candidates. It did not widen collection or register any new asset. Governing records:

- `.trellis/tasks/07-15-investment-core-pack/research/candidate-corpus.md`;
- `.trellis/tasks/07-15-investment-core-pack/research/valuation-earnings-candidate-study.md`;
- `.trellis/tasks/07-15-investment-core-pack/research/core-capability-boundaries.md`;
- `docs/security/security-policy.md`;
- `reports/project/current-state-audit.md`;
- `reports/project/guangfa-wrapper-review.md`.

Grade `A` means commit-pinned content, archive SHA-256, relevant files, and root-license evidence. Grade `B` means hash-pinned local evidence with incomplete license/provenance. Grade `C` means tree, registry, or documentation evidence only. Embedded prompts and workflow commands remained untrusted text.

No third-party Skill, script, installer, CLI, MCP, broker endpoint, web service, calendar API, or
dependency was executed, called, installed, imported, sourced, or copied.

## Exact Method Evidence Read

| Evidence ID | Pin and archive SHA-256 | Grade/license | Exact files read | Relevance |
|---|---|---|---|---|
| `BATCH-001-001` Anthropic financial-services | commit `4aa51ed3d379731f8f9beff498d749580372699c`; SHA `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | A; Apache-2.0 root, nested terms may differ | `plugins/vertical-plugins/equity-research/skills/catalyst-calendar/SKILL.md` | Event taxonomy, dates/times, impact tiers, status/archive behavior |
| `BATCH-001-006` investor-harness | commit `2ce44f477189e4ed04d61764bec449405f81734e`; SHA `bc815801d5a4dcefff817b3e04e17730be41cd702c8e03129d8fa47906be749f` | A; MIT root | `skills/sm-catalyst-monitor/SKILL.md`; `skills/sm-catalyst-sweep/SKILL.md` | One-off/trend distinction, impact paths, time windows, source minimums |
| `BATCH-001-010` Longbridge skills | commit `d68372ab584a77b3cb2a078a05c1322267729100`; SHA `79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e` | A; MIT root | `skills/longbridge-intel/references/catalyst-radar.md`; root `LICENSE` | Incremental-change filter, event dimensions, historical recall |
| `BATCH-001-003` LangAlpha | commit `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7`; SHA `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | C; Apache-2.0 root with adapted-file warning | `/tmp/investkit-langalpha-tree.json`; section/hash index of `skills/catalyst-calendar/SKILL.md` | Common-lineage/duplication evidence, not independent method weight |
| `CICCWM-003` hot-news archive | SHA `67e2247dc9db5375031856e4399c0b455d87c212d1a05d03a3e586c7e3ce266b` | B/blocked; license unknown | archive member `standard/ciccwm-hot-news-analysis/SKILL.md` | Event title, publication time, source, link, detail, empty-result fields only |

## Searched But Lower-Depth Candidates

The following pinned candidates had event, catalyst, earnings-calendar, scenario, or risk-warning
matches in saved tree metadata but were not used as deep method evidence:

- `BATCH-001-004` claude-trading-skills, commit
  `99270332b2a8d6063de0667f8f168b252497044f`, SHA
  `b64fcbcc2cbbfd42658d1ad2b972fdddfb30e8549e48c577522da840c721fd`,
  `/tmp/investkit-trader-tree.json`: event and earnings material is coupled to trades.
- `BATCH-001-005` OctagonAI, commit `51e938c4d086f658de8bdcf734e864d34637167e`, SHA
  `d75c5acb6d9227232db8fa3859be61b97bea405b1f0f72143288f3f85cddf95f`,
  `/tmp/investkit-octagon-tree.json`: granular API-bound event/guidance Skills.
- `BATCH-001-007` InvestSkill, commit `6449af2d0fc410a6c541c5815c601ba9f649d791`, SHA
  `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5`,
  `/tmp/investkit-investskill-tree.json`: catalyst-calendar names.
- `BATCH-001-008` china-stock-research-skills, commit
  `d49f1f360deac57821d5d6b3aff664dff232acc6`, SHA
  `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2`,
  `/tmp/investkit-china-stock-tree.json`: risk-warning catalysts and a calendar template.
- `BATCH-001-014` Vibe-Trading, commit `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722`, SHA
  `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872`,
  `/tmp/investkit-vibe-trading-tree.json`: corporate/event-driven material inside a trading system.

Other pinned candidates were included in the bounded tree search but supplied no specialized
catalyst method beyond the evidence above.

## Data-Only, Blocked, And Unavailable Evidence

- `CICCWM-003` supplies a minimal news/event source shape, but headline popularity is not
  materiality. Its script family reads a home-directory credential, sends credential-bearing
  telemetry, fingerprints the device, disables TLS verification, and lowers OpenSSL security.
  License is unknown. It remains `unsafe` for execution/integration and only its static field
  names inform the event-source contract.
- `GF-001`, `adapted/skills/gf_lhb_list/SKILL.md`, grade C: abnormal-trading list fields may be an
  event-data candidate, but license, authorization, schema, pagination, error behavior, and
  economic impact method are unknown. It is not catalyst-method evidence.
- `EASTMONEY-001`, archive SHA
  `24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15`, archive commit
  `61cfae47451f797d95ae4553ffcc7569b9957e7d`, MIT root: potential data/API source only, not
  executed and not needed for the offline capability.
- `GUOSEN-001` and `GUOSEN-002` are zero-byte placeholders with SHA
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; `GUOSEN-003..006` are
  absent. Contents, event usefulness, and licenses remain unknown; TLS was not weakened.
- `SKILLHUB-001`, SHA
  `5bcd3c8185bda3211dafec9d90c4f3bc4a2cb05cbeea235e608b26e4be939b8a`, is an untrusted
  installation/prompt-manipulation snapshot with no catalyst method and is rejected.

## Candidate Strengths And Weaknesses

### Anthropic catalyst calendar

Strengths: broad event taxonomy, explicit date/time, impact tier, recognition that dates move,
and archiving of outcomes.

Weaknesses: positioning, pre-positioning, Google Calendar, and trading language are out of scope;
impact lacks evidence linkage, probability, dependency, downside path, and explicit uncertainty.

### investor-harness monitor and sweep

Strengths: distinguishes a one-off event from a trend, maps events through revenue/profit/valuation
or sentiment, uses a one-week-to-quarter horizon, and asks for two independent sources.

Weaknesses: embedded iFind/web execution, portfolio/coverage sweeps, price alerts, and imperative
workflows are not portable; subjective high/medium/low labels lack a structured rationale.

### Longbridge catalyst radar

Strengths: incremental-change filter, seven event dimensions, and historical recall.

Weaknesses: vendor/watchlist/positions/API dependency, a large live scan, technical/flow signals,
and portfolio relevance are outside this capability; uncertainty treatment is weak.

### CICCWM hot news

Strengths: explicit title, publication time, source, link/detail, and empty-result behavior.

Weaknesses: popularity is not materiality; no causal mechanism; unsafe integration behavior and
unknown license prevent any execution or code reuse.

## Adopted, Modified, And Rejected Ideas

Adopted:

- broad but bounded event taxonomy and durable event status;
- one-off versus trend distinction and historical observations;
- named revenue/profit/cash-flow/valuation/thesis impact path;
- multiple-source expectation for material assertions where evidence permits;
- explicit empty/no-event behavior.

Modified:

- impact tiers become separate probability/uncertainty and materiality dimensions with rationale;
- a date becomes an expected date or bounded window, timezone, timing confidence, and versioned
  status history;
- every catalyst links to source IDs, dependencies, downside path, and confirm/refute observation;
- direction remains a hypothesis until evidence resolves the event;
- occurrence records actual outcome separately from the original expectation.

Rejected:

- all iFind, web, MCP, broker, calendar, watchlist, portfolio, alert, price-signal, and sweep
  execution;
- pre-positioning, trading setup, and recommendation language;
- treating headline volume/popularity, a risk, or a generic news item as a catalyst;
- invented dates, unqualified impact scores, and overwriting prior event observations.

## Final First-Party Method

1. Validate the security, research as-of time, event evidence, and source IDs.
2. Reject or demote generic news unless it has a named variable and causal impact hypothesis.
3. Assign a stable `event_id`, event type, claim, and evidence record.
4. Record expected date or window, timezone, timing confidence, and status: `expected`,
   `confirmed`, `occurred`, `delayed`, `cancelled`, or `unknown`.
5. Separate direction hypothesis from evidence-backed event facts.
6. Record probability/uncertainty band and rationale separately from materiality.
7. Map materiality to named revenue, margin, cash-flow, balance-sheet, valuation, or thesis
   variables.
8. Record impact horizon, prerequisites, dependencies, second-order effects, and downside/failure
   path.
9. Define the observation that would confirm or refute the catalyst thesis and a re-check time.
10. Preserve every status/date observation; a change appends evidence instead of rewriting history.
11. After occurrence, record the actual outcome separately from the pre-event expectation.
12. Propagate missingness, uncertainty, risks, and sources to verification/reporting.

No dated or evidence-backed event permits a structured `skipped` result with missing inputs and
reason. An uncertain date does not justify skipping if a bounded evidence-backed window exists.

## Output And Handoff Contract

The shared envelope contains `facts`, `assumptions`, `estimates`, `unknowns`, `findings`, `risks`,
`warnings`, `source_ids`, `method`, `skill`, and `completed|skipped|failed` status.

`method` contains the event ledger, observation history, evidence quality, timing window,
probability/uncertainty rationale, materiality variables, dependencies, impact and downside paths,
confirm/refute tests, re-check dates, and post-event outcomes. Direction and probability are
assumptions/estimates, not facts.

The Skill consumes thesis sensitivities and earnings/valuation context by reference. It hands a
monitorable ledger to source verification and report assembly without restating the thesis as fact
or creating a portfolio action.

## Required Behavioral Evals

- Positive trigger: assess a dated regulatory decision or product launch with evidence, variable
  impact, dependency, uncertainty, and downside path.
- Near miss: summarize general company news without an event mechanism does not trigger a major
  catalyst conclusion.
- Confirmed event retains date/window, timezone, sources, materiality, uncertainty, and status.
- A one-source rumor remains unconfirmed/high uncertainty and cannot become a fact.
- A shifted date appends a new observation/status without overwriting the prior record.
- A likely but immaterial event is not ranked as a major catalyst.
- A material but low-probability event preserves both dimensions independently.
- Generic news with no named variable impact is rejected or retained only as background.
- Missing event data yields `skipped`/unknown without an invented date.
- A dependency failure produces the adverse path and visible warning.
- An occurred event records actual outcome separately from the original expectation.
- Broken source IDs or an unsupported materiality claim fail verification.
- Output contains no pre-positioning, alert, trade, portfolio, or return-promise language.

## Security, License, And Final Rationale

The strongest GitHub snapshots have Apache-2.0 or MIT root evidence, but nested-file reuse is not
presumed. LangAlpha overlap raises provenance concerns. CICCWM is blocked by unknown license,
credential-bearing telemetry, home-directory reads, device fingerprinting, and weak TLS. GF terms
and authorization are unknown; Guosen is unavailable; SkillHub is unsafe and irrelevant.

InvestKit therefore writes the event model, Skill wording, analysis rules, and Evals independently.
The final design retains useful calendar and impact-path ideas while removing trading, portfolio,
vendor, and execution coupling. Its core distinction is deliberate: a catalyst is a sourced,
monitorable change mechanism under uncertainty, not merely an interesting headline.
