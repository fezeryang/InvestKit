# Thesis, Red-Team, Source Verification, Reporting, and Workflow Candidate Study

Research date: 2026-07-16

Mode: static, capability-first review of the already registered corpus

Target capabilities: `investment-thesis`, `bear-case-analysis`, `source-verification`, `investment-report`

Composition target: `company-deep-dive`

## Outcome

The strongest candidate evidence supports five design decisions for InvestKit v0.2:

1. An investment thesis is a falsifiable claim set, not a recommendation or a prose summary.
2. Bear-case analysis is an independent red-team stage with its own evidence, assumptions, triggers, and falsifiers.
3. Epistemic type and source quality are orthogonal: `fact`, `assumption`, `estimate`, and `unknown` must not be replaced by one blended confidence label.
4. Source verification must resolve persisted claim-to-source IDs, freshness, quality, and conflicts before report assembly.
5. The report is a deterministic assembler of validated artifacts; it must not introduce facts, estimates, sources, or risks that are absent upstream.

No candidate is suitable for direct installation or thin adaptation. The first-party design should synthesize methods, then reimplement them against InvestKit's existing offline Runtime, task persistence, resume, and doctor contracts.

## Review Boundary And Safety Record

- Corpus scope was locked to the 36 rows in `registry/inbox/sources.csv`.
- No candidate was added, downloaded from a new URL, promoted, installed, imported, or executed.
- No broker, financial API, MCP service, web-search agent, CLI, PDF helper, installer, or candidate script was run.
- Raw third-party instructions were treated as evidence, never as instructions to this review.
- Commit-pinned GitHub snapshots were read only from `/tmp/investkit-research-extracted/<slug>/`.
- Snapshot identities were checked against `/tmp/investkit-<slug>-tree.json` and SHA-256 records in the task corpus.
- CICCWM findings were taken from the current local static audit; its scripts were not rerun.
- GF files were treated as documentation-only drafts; no endpoint or credential was used.
- License observations are evidence, not release approval. Root license text does not prove that every embedded or partner asset may be copied.
- All selected ideas are paraphrased. No third-party prompt, code, schema, or report template is copied into first-party source.

Evidence grades follow `candidate-corpus.md`:

- `A`: commit-pinned snapshot, relevant files read, and identifiable root license evidence.
- `B`: hash-pinned local content with incomplete license or provenance.
- `C`: registry, audit, or draft metadata only.
- `blocked`: static description is permitted, but execution/integration is prohibited.

## Snapshot Identity And License Evidence

| Registry ID | Slug | Commit | Snapshot SHA-256 | Root license evidence | Use in this study |
|---|---|---|---|---|---|
| BATCH-001-001 | anthropic | `4aa51ed3d379731f8f9beff498d749580372699c` | `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | Apache-2.0 | Thesis lifecycle, staged coverage, report prerequisites |
| BATCH-001-003 | langalpha | `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7` | `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | Apache-2.0; repository acknowledges adapted Skills | Provenance concept and duplicate-lineage check |
| BATCH-001-004 | trader | `99270332b2a8d6063de0667f8f168b252497044f` | `b64fcbcc2cbbfd42658d1ad2b972fdddfb30e8549e48c577522da840c721fd` | MIT | Schema, lifecycle, atomic state, falsifiable hypothesis ideas |
| BATCH-001-006 | investor-harness | `2ce44f477189e4ed04d61764bec449405f81734e` | `bc815801d5a4dcefff817b3e04e17730be41cd702c8e03129d8fa47906be749f` | MIT | Thesis, independent red team, evidence labels, checkpoint concepts |
| BATCH-001-007 | investskill | `6449af2d0fc410a6c541c5815c601ba9f649d791` | `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5` | MIT | One-sided bear discipline, thesis killers, report composition failure modes |
| BATCH-001-008 | china-stock | `d49f1f360deac57821d5d6b3aff664dff232acc6` | `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2` | MIT | Evidence layers, source tiers, conflicts, routing, merged output contract |
| BATCH-001-009 | hhfin | `6e7ceef3c65287b7b88436fb4876f541b592a2ed` | `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6` | MIT | Multi-report triangulation, unstated falsifier, risk taxonomy |
| BATCH-001-010 | longbridge | `d68372ab584a77b3cb2a078a05c1322267729100` | `79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e` | MIT | Capability routing, thesis-to-metric mapping, report period checks |
| BATCH-001-013 | deep-research | `e5479f857f484cde13fe69d2f3ce8de7af193bc7` | `44b3b02753d4ed1359ce13a12055cf75b3e415f68abbbe2626ded39e62001e8e` | MIT | Structured batch/resume idea and a negative example for unknown handling |
| BATCH-001-014 | vibe-trading | `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722` | `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872` | MIT | Bias check, revision gates, pseudo-precision and cross-report consistency |

The other pinned snapshots were tree-searched and hash-checked but did not change the four target capability designs: finance-skills (`87f688e...`), Octagon (`51e938c...`), Anthropic cookbooks (`67ce644...`), and Hermes (`07be37d...`). Their valuation, earnings, data, or comps methods are covered by adjacent capability studies.

### Duplicate-lineage finding

LangAlpha explicitly acknowledges adaptation from Anthropic's financial-services plugins. Static comparison confirmed:

- `initiating-coverage/references/task1-company-research.md` is byte-identical in both snapshots: SHA-256 `00ec47ca64c1cfdf6e1b74fa8c693633b5e12e98264667b40f2d7dea90b48227`.
- `initiating-coverage/references/task5-report-assembly.md` is byte-identical: SHA-256 `7e2f2ccc6bfb54a4be247cd29a9aa95df20a624bb82243980d4f31412e7172ed`.
- LangAlpha's thesis and idea Skills retain the same method body with provenance/frontmatter or tool-routing modifications.

Decision: count this as one methodological lineage, not independent corroboration. LangAlpha's per-turn provenance concept is considered separately; the duplicated prompts are not reused.

## Searched-Corpus Coverage

| Candidate(s) | Evidence reached | Relevance to this study | Result |
|---|---|---|---|
| EASTMONEY-001 | Local audit/manifest; MIT, commit known | Data/API repository, not thesis or report methodology | Briefly listed; defer to Provider/data work |
| CICCWM-001..006 | Current static audit; license unknown; blocked | Data access only; unsafe home access, credential telemetry, and weak TLS findings | `unsafe` for execution; no method adopted |
| SKILLHUB-001 | Local instruction snapshot/audit; license unknown | Installer/prompt behavior, no investment method | `reject` as capability evidence |
| GUOSEN-001..006 | Two empty placeholders and four absent; license/content unknown | Potential data support only | `unknown`; no inference from unavailable content |
| GF-001 | Draft metadata | Abnormal trading list; outside target methods | No adoption |
| GF-002 | Draft and wrapper audit | Company facts could support a future source record | `api_integration_candidate`; no Runtime work |
| GF-003 | Draft and wrapper audit | Valuation/financial fields may support upstream capabilities | `api_integration_candidate`; no Runtime work |
| GF-004..008 | Draft metadata | ETF/fund/ranking functions, not target methods | No adoption |
| BATCH-001-001 | Relevant Skill and references read | Strong staged coverage, thesis, report prerequisites | Extract/modify method ideas |
| BATCH-001-002 | Full tree searched | Valuation/data/earnings emphasis; no stronger thesis/report contract | Adjacent study only |
| BATCH-001-003 | Relevant Skill lineage, README, license read | Duplicate Anthropic lineage; useful provenance description | Mark duplicate; extract provenance idea only |
| BATCH-001-004 | Thesis Skill, lifecycle, schemas, evidence rubric read | Strong persistence mechanics but trading lifecycle | Extract state ideas; reject trade operations |
| BATCH-001-005 | Full tree searched | API-oriented analyst/market masters; no stronger target contract | Adjacent study only |
| BATCH-001-006 | Thesis, red team, deep dive, evidence and persistence docs read | Strong capability responsibilities and gap discipline | Extract/modify |
| BATCH-001-007 | Bear, validator, bundle/full report, report generator read | Strong red-team checklist; serious advice/missing-data defects | Extract selected methods; reject orchestration rules |
| BATCH-001-008 | Orchestrator, source/citation/output/risk docs read | Strongest evidence-layer and conflict-preservation design | Extract/modify |
| BATCH-001-009 | Report reader and risk/report references read | Strong triangulation, falsifier, and risk checks | Extract/modify |
| BATCH-001-010 | Research router, thesis, coverage/report references read | Provider-serving-capability example; strong period/source checks | Record as future adapter candidate; do not bind Skills |
| BATCH-001-011 | Full tree searched | Financial-model reference, not target method | Adjacent study only |
| BATCH-001-012 | Full tree searched | Comps method, not target method | Adjacent study only |
| BATCH-001-013 | Research/deep/report Skills read | Generic structured research and resume; unsafe install/execution assumptions | Extract resume concept; reject unknown suppression |
| BATCH-001-014 | Bias, thesis, report, deep-company, workflow preset read | Useful revision discipline; product/trading scope conflicts | Extract checks; keep execution blocked |

## Capability Synthesis: `investment-thesis`

### Strongest design-changing candidates

| Candidate | Strength | Limitation/risk | Idea decision |
|---|---|---|---|
| Anthropic thesis tracker | Requires pillars, risks, catalysts, falsifiability, disconfirming evidence, and a time-based scorecard | Includes position direction, target/stop-loss, action, and conviction language; prose state lacks source IDs | Adopt falsifiability and pillar tracking; reject trading actions |
| Investor Harness `sm-thesis` | Frames the core contradiction, necessary conditions, market-expectation gap, falsifiers, and follow-up indicators; separates fact, consensus, inference, and unverified hypothesis | Its evidence labels blend epistemic state with source class; referenced history can become circular evidence | Modify into typed facts/assumptions/estimates/unknowns with explicit source IDs |
| Longbridge thesis tracker | Maps each pillar to a measurable data point and compares actual evidence with expectations using intact/weakened/broken states | Hard-bound to broker CLI, current data, and a recommended action | Adopt pillar-to-metric evaluation; route data only through Provider records |
| TraderMonty thesis/hypothesis schemas | Shows value of schema validation, deterministic IDs/fingerprints, status history, review dates, kill criteria, atomic writes, and raw provenance | Lifecycle centers on entering, sizing, trimming, and closing real positions; evidence is only free-form strings | Extract state-integrity mechanics; reject all trade/position fields and scripts |

### First-party responsibility boundary

`investment-thesis` consumes validated upstream company, business-model, financial, quality, valuation, comps, and earnings artifacts. It does not fetch data, calculate a new valuation, issue a rating, or decide a trade.

Required output:

- one bounded thesis statement and a named time horizon;
- `bull_case`, `base_case`, and `bear_case_seed`, each linked to upstream fact/estimate IDs;
- three to five thesis pillars, each with mechanism, confirming evidence IDs, disconfirming evidence IDs, assumptions, unknowns, and status;
- explicit variant perception or expectation gap, marked as an assumption unless independently sourced;
- falsifiers with observable metric/event, threshold or condition, source path, and review timing;
- catalysts only as evidence-bearing events, never as promised price outcomes;
- overall conclusion status such as `supported`, `mixed`, `insufficient_evidence`, or `contradicted`;
- no `BUY`, `SELL`, `HOLD`, position size, stop loss, or return promise.

Missing data must weaken or block a pillar. It must never be filled with a neutral score or model-memory estimate.

### Adopt / modify / reject

- Adopt: falsifiability, explicit disconfirming evidence, measurable pillars, review dates, and raw provenance.
- Modify: qualitative conviction into a reproducible completeness/evidence assessment; market expectations into a sourced or explicitly assumed field.
- Reject: trade direction, position management, arbitrary weighted conviction scores, and prose-only evidence arrays.

## Capability Synthesis: `bear-case-analysis`

### Strongest design-changing candidates

| Candidate | Strength | Limitation/risk | Idea decision |
|---|---|---|---|
| Investor Harness `sm-red-team` | Explicitly independent contrarian role; attacks fragile assumptions, evidence gaps, earliest failure signals, and observable downgrade triggers | Forces reading a user `biases.md`; suggests replacement securities; no structured source contract | Adopt independent role and observable triggers; reject implicit user-file reads and alternatives |
| InvestSkill bear case | One-sided-disclosure banner, seven risk lenses, downside mechanism, timeline, and mandatory thesis-killers that would prove the bear wrong | Produces sell/short/action blocks, stop levels and price targets; live-data/training-data fallback is unsafe; scoring directions conflict | Extract risk lenses and thesis-killers; reject signals, actions, and fallback estimates |
| HHFinAi report reader/risk reference | Searches for an unstated falsifier, compares bull assumptions with prior-cycle peaks, triangulates conflicting reports, and models probability × impact with monitorable thesis killers | Includes action-triggering exits/portfolio mitigation and many fixed thresholds without company context | Adopt falsifier and contradiction checks; treat probabilities as estimates, not facts |
| Vibe research discipline/deep-company | Forces counterevidence, recency checks, scenario triggers, anti-pseudo-precision, accounting-scope consistency, and cascading revision after a changed input | Main repository is trading-oriented and includes action/position frameworks; some checks depend on external tools | Adopt revision checklist concepts; keep repository execution blocked |

### First-party responsibility boundary

`bear-case-analysis` is run after the thesis artifact exists but must receive a frozen snapshot of it. It should not share the thesis author's conclusion field or merely rewrite the existing risks.

Required output:

- the strongest counter-thesis in neutral research language;
- the three most fragile thesis assumptions and why each is fragile;
- independent counterevidence IDs, including conflicts and low-quality evidence warnings;
- risk mechanisms across relevant categories: business/competition, accounting/quality, financial, valuation expectations, management/capital allocation, event/regulatory, and data/model risk;
- earliest observable failure signals with metric/event, threshold/condition, time window, and expected source;
- severity and likelihood as labeled estimates with rationales, never pseudo-facts;
- `thesis_killers_for_bear_case`: evidence that would disprove the bear case;
- unresolved questions and missing inputs;
- no short recommendation, trade construction, price target, or action.

Independence is testable: the artifact must contain at least one counterevidence source or upstream fact not used as confirming evidence by `investment-thesis`, unless it returns `insufficient_evidence` with the search gap recorded.

### Adopt / modify / reject

- Adopt: steelman posture, earliest-failure signals, two-sided falsification, and explicit one-sided-method disclosure.
- Modify: fixed risk scores into reasoned estimates; downside target into bounded mechanism/sensitivity unless valuation inputs already support it.
- Reject: mandatory bearish signal, sell/short language, position/exit suggestions, and private bias-file access.

## Capability Synthesis: `source-verification`

### Strongest design-changing candidates

| Candidate | Strength | Limitation/risk | Idea decision |
|---|---|---|---|
| China Stock citation/source contracts | Separates facts, interpretation, and open questions; defines source tiers; preserves unit/period/accounting scope; requires conflicts to remain visible | Accessible links are not durable identities; source tiers are market-specific; assumptions and estimates are still combined under interpretation | Adopt boundaries and conflict rule; generalize quality taxonomy and source records |
| HHFinAi report reader | Multi-document triangulation, chart-vs-narrative contradiction detection, publication/reference dates, prior-cycle checks, and coverage-gap reporting | Assumes PDF tools and potentially copyrighted broker material; extraction commands are not an InvestKit Runtime contract | Adopt verification questions only; do not copy or run the tooling |
| Investor Harness evidence policy | Clearly prevents market consensus, inference, and unverified hypotheses from masquerading as facts | Labels are prose tags, not claim-source links; `public fact` says little about quality/freshness | Split epistemic type from evidence quality and persist both |
| LangAlpha provenance description | Records provider/type, timestamp, arguments, fingerprint, snippet, and file/tool accesses outside the model context | It belongs to a larger online workbench with secret-vault and external-provider surfaces; implementation was not approved | Extract the provenance fields; independently implement offline records |

### First-party responsibility boundary

`source-verification` validates persisted claims and sources; it does not conduct new company analysis or silently repair gaps.

Every persisted source should include:

- `source_id`, title, issuer/publisher, source type, direct locator or fixture path;
- publication/effective date, `retrieved_at` or fixture version, and research `as_of_date`;
- market, currency, period, unit, accounting scope, audit/review status when relevant;
- quality tier and rationale, first-party/secondary flag, and accessibility status;
- content fingerprint/checksum for persisted evidence;
- provider identity without credentials;
- warnings, license/use constraints when known, and demo flag.

Every material claim should include:

- `claim_id`, epistemic type, statement, capability origin, and source IDs;
- for facts, at least one resolvable source ID;
- for assumptions, rationale and materiality but no false source requirement;
- for estimates, method, inputs, assumptions, unit, period, and sensitivity;
- for unknowns, the gap, decision impact, and next eligible source.

Verification result categories should be `verified`, `partially_supported`, `unsupported`, `stale`, `conflicted`, `low_quality`, or `not_applicable`. A claim may have several warnings. Conflicts are never averaged away.

Freshness must be capability- and field-specific: a two-year-old business description and a two-year-old market price do not have the same validity. The source policy should define default windows and allow an explicit rationale override.

### Adopt / modify / reject

- Adopt: source hierarchy, direct claim linkage, period/unit/scope preservation, triangulation, freshness, and conflict visibility.
- Modify: URL-only citation into stable source records plus checksums; generic tiers into market-aware policy.
- Reject: silently skipping uncertain fields, treating consensus as fact, relying on inaccessible sources, and resolving conflicts by majority vote.

## Capability Synthesis: `investment-report`

### Strongest design-changing candidates

| Candidate | Strength | Limitation/risk | Idea decision |
|---|---|---|---|
| Anthropic initiating coverage/report assembly | Staged prerequisites, input verification, source dates, model/report consistency, scenario coverage, and writing the executive summary last | Optimizes for a 30-50 page DOCX, charts and external tools; requires rating/price target and recommends BUY/HOLD/SELL | Adopt prerequisite and assembly checks; reject format/length/advice requirements |
| China Stock final-output contract | Keeps facts, interpretation, open questions, monitoring indicators, valuation hooks, conflicts, and sources as distinct sections | Does not define a machine-readable artifact or enforce claim IDs | Adopt section semantics; source content from capability envelopes only |
| Longbridge earnings/report workflow | Reuses captured raw data, verifies a single reporting period, marks actual/estimate notation, requires a source per table, and checks math | Direct broker CLI/web dependence, ratings and price targets, live-data orientation | Adopt period/source consistency; keep Provider work subordinate and out of this phase |
| Vibe deep-company revision discipline | Detects pseudo-precision, inconsistent accounting bases, double counting, unfair peer comparison, absolute wording, and cascading errors after corrections | Long-form series and trading report generator are out of scope; tool execution is unapproved | Adopt final quality gates; reject report generator's action/rating template |

### First-party responsibility boundary

`investment-report` is the final assembler. It consumes only validated capability envelopes, `sources.json`, task metadata, and loaded Skill/spec manifests.

Required behavior:

- preserve the demo-data declaration, as-of date, generation time, and research boundary;
- include thesis, bull/base/bear reasoning, independent red-team findings, catalysts, risks, assumptions, estimates, unknowns, and sources;
- cite claim/source IDs or render stable source footnotes for every material factual statement and table;
- keep facts, assumptions, estimates, and unknowns visibly distinct;
- expose missing/skipped capabilities and their reasons;
- preserve conflicts rather than picking a winner without an upstream resolution record;
- check units, periods, accounting scope, peer comparability, arithmetic, and scenario consistency;
- write the executive summary only from the completed body artifacts;
- introduce no new claim, number, source, assumption, estimate, risk, or recommendation;
- produce Markdown offline with no CDN, browser, PDF, DOCX, network, or API dependency;
- contain no individualized buy/sell instruction, target-price promise, position size, or deterministic return claim.

The report completeness state should be machine-readable: `complete`, `complete_with_gaps`, or `failed_validation`. A polished document with unresolved mandatory source or bear-case failures must not be marked complete.

### Adopt / modify / reject

- Adopt: prerequisite gates, write-summary-last, source-per-table, revision/cascade checks, and explicit gaps.
- Modify: institutional report templates into a compact Markdown research artifact driven by structured IDs.
- Reject: ratings, trade actions, externally loaded charts, neutral defaults for missing modules, and style-based confidence inflation.

## `company-deep-dive` Composition Synthesis

### Candidate lessons

- China Stock provides the clearest orchestrator/module separation and the rule that merging must not collapse evidence layers.
- Anthropic initiating coverage shows the value of verified dependencies and refusing placeholder downstream artifacts.
- Investor Harness shows useful checkpoint, task pulse, archive, and missing-information concepts, but its Markdown state is less robust than InvestKit's existing JSON/atomic-write Runtime.
- TraderMonty shows schema validation, deterministic fingerprints, append-only histories, and atomic replacement, but its brokerage/position lifecycle is outside product scope.
- InvestSkill demonstrates why configurable depth and neutral defaults are unsafe: an omitted capability is not equivalent to neutral evidence.
- Deep Research demonstrates resume-by-existing-output, but its report generator drops uncertain fields; InvestKit must do the opposite and preserve unknowns.
- Vibe's multi-agent preset demonstrates explicit dependencies, but macro-to-sector-to-stock recommendation routing is not this Workflow and is rejected.

### First-party Workflow contract

The required order remains exact:

1. `security-identification`
2. `company-deep-research`
3. `business-model-analysis`
4. `financial-statement-analysis`
5. `earnings-quality-analysis`
6. `valuation-analysis`
7. `comps-analysis`
8. `earnings-analysis`
9. `investment-thesis`
10. `bear-case-analysis`
11. `catalyst-analysis`
12. `source-verification`
13. `investment-report`

Composition rules:

- Each stage writes `capabilities/<step-id>.json` using the shared result envelope.
- Upstream artifacts are read as immutable snapshots identified by checksum.
- A step may be `completed`, `skipped`, or `failed`; `skipped` requires reason and missing inputs.
- Missing numeric data remains unknown. It never becomes zero, a neutral score, or model memory.
- `investment-thesis` receives all analytical artifacts through stage 8.
- `bear-case-analysis` receives a frozen thesis plus upstream evidence, produces an independent artifact, and cannot edit the thesis.
- `catalyst-analysis` records events and uncertainties without turning them into price promises.
- `source-verification` checks every material claim/source relationship across stages 2-11.
- `investment-report` runs only after completed bear-case and source-verification artifacts; it consumes the verification result rather than performing silent fixes.
- A genuinely inapplicable analytical stage may be skipped, but bear case, source verification, and report are mandatory for a completed task.
- Warnings, risks, unknowns, and source conflicts propagate forward by ID; they are never flattened into prose and lost.

### Persistence and resume

Use the existing Runtime task root instead of importing another harness's workspace convention:

- `task.json` and `plan.json` remain authoritative lifecycle state.
- Capability files are atomically written, schema validated, and then marked complete.
- `run-log.json` appends start, completion, skip, failure, and resume events.
- Resume verifies task ID, expected stage order, artifact schema, checksums, and source IDs before skipping a completed stage.
- Resume never overwrites a verified completed artifact.
- A failed/incomplete stage can restart from its input snapshot; later stages remain pending.
- Completed resume changes only the append-only run log.
- Corrupt or externally linked artifacts fail closed and are surfaced by `doctor`.

## Shared Evals And Tests Implied By This Study

### `investment-thesis`

- Positive trigger: asks for a falsifiable thesis from completed company/financial/valuation work.
- Near miss: asks only for company facts, valuation math, a catalyst calendar, or a buy recommendation.
- Reject a fact without a source ID and an estimate without method/material inputs.
- Verify every pillar has confirming and disconfirming evidence or an explicit gap.
- Verify base/bull/bear reasoning and observable falsifiers.
- Verify missing valuation or earnings inputs produce `insufficient_evidence`, not neutral confidence.

### `bear-case-analysis`

- Positive trigger: challenge a completed thesis or construct an independent counter-case.
- Near miss: generic risk disclosure, sensitivity math, or source audit only.
- Verify at least one thesis assumption is attacked with independent evidence or a documented evidence gap.
- Verify earliest failure signals have an observable condition and source path.
- Verify the bear case also declares what would falsify it.
- Reject trade/short/sell language, position sizing, stop losses, and promises.

### `source-verification`

- Resolve all fact source IDs against `sources.json`.
- Flag missing, inaccessible, stale, low-quality, malformed, or conflicting evidence separately.
- Preserve unit, period, market, currency, accounting scope, and demo status.
- Test a fresh low-quality source versus an older authoritative source without collapsing them to one score.
- Test two authoritative sources that conflict; both must remain visible.
- Verify assumptions need rationale/materiality, not fabricated citations.

### `investment-report`

- Generate from structured artifacts only and compare emitted claim IDs with the input union.
- Fail if the report contains a number, source, assumption, estimate, or risk not in upstream artifacts.
- Include skipped capabilities, source conflicts, demo declaration, risks, assumptions, and unknowns.
- Verify arithmetic and period/unit consistency in all rendered tables.
- Verify independent bear case and source verification are present.
- Verify no trade instruction, target return, deterministic promise, CDN, or network dependency.

### Workflow and resume

- Assert exact 13-stage order and one artifact per stage.
- Exercise a complete fixture, missing peer data, missing earnings transcript, and an inapplicable/skipped capability.
- Corrupt a capability schema, checksum, source ID, and symlink; resume and doctor must fail clearly.
- Resume a completed task and byte-compare all artifacts except `run-log.json`.
- Resume an interrupted task and verify completed stages are not rerun.

## License, Security, And Disposition Summary

- Apache-2.0 or MIT root license text was present for every design-changing GitHub snapshot listed above.
- Root license presence does not authorize copying partner-built content, third-party data, report text, or embedded assets without file-level review.
- The LangAlpha/Anthropic duplicate lineage is explicitly recorded; it does not count twice.
- CICCWM remains `blocked_execution`/unsafe for integration; its license is unknown.
- GF authorization, terms, redistribution rights, and API behavior remain unknown.
- Guosen contents and licenses remain unknown because valid packages are unavailable.
- Longbridge is a credible `api_integration_candidate`, but its broker CLI, vendor-biased routing, live data, authentication, and trading-adjacent surfaces are not part of v0.2.
- InvestSkill, TraderMonty, and Vibe contain trading/action behavior that is outside InvestKit's research-only boundary.
- Deep Research and HHFinAi include installers, shell/Python workflows, or home-directory assumptions; none were executed or adopted.
- Final candidate disposition for this study is `extract` or `reference` at the method level only. There is no `adopt` decision for a raw Skill and no approval/promotion action.

## Files Actually Read

### Governing local evidence

- Task/spec: `.trellis/tasks/07-15-investment-core-pack/prd.md`, `.trellis/tasks/07-15-investment-core-pack/research/candidate-corpus.md`, `.trellis/spec/backend/investment-core-contract.md`.
- Registry: `registry/inbox/sources.csv`, `registry/governance/batch-001-candidate-governance.csv`.
- Audits: `reports/project/current-state-audit.md`, `reports/project/repository-inventory.md`, `reports/project/guangfa-wrapper-review.md`.
- Policy: `docs/skill-research/SOP.md`, `docs/skill-research/taxonomy.md`, `docs/skill-research/acceptance-criteria.md`, `docs/security/security-policy.md`, `tasks/current-batch.md`.

### Snapshot/tree evidence

- All 14 `/tmp/investkit-<slug>-tree.json` files were path-searched.
- All 14 `/tmp/investkit-research-corpus/<slug>.zip` files were SHA-256 checked.
- Root `LICENSE` and relevant `README.md` files were read for the design-changing candidates.

Anthropic (`BATCH-001-001`):

- `plugins/vertical-plugins/equity-research/skills/{thesis-tracker,idea-generation,initiating-coverage}/SKILL.md`.
- `plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/{task1-company-research,task5-report-assembly}.md`.

LangAlpha (`BATCH-001-003`):

- `README.md`, `LICENSE`, `skills/{thesis-tracker,idea-generation,initiating-coverage}/SKILL.md`.
- `skills/initiating-coverage/references/{task1-company-research,task5-report-assembly}.md`.

Investor Harness (`BATCH-001-006`):

- `README.md`, `LICENSE`, `skills/{sm-thesis,sm-red-team,sm-company-deepdive,sm-master}/SKILL.md`.
- `core/{evidence,preamble,postamble,checkpoint,task-pulse,workflows,compliance}.md`.

InvestSkill (`BATCH-001-007`):

- `LICENSE`, `plugins/us-stock-analysis/skills/{bear-case,research-bundle,result-validator,full-report,report-generator}/SKILL.md`.

China Stock Research (`BATCH-001-008`):

- `README.md`, `LICENSE`, `examples/full-report-flow.md`, `skills/china-stock-research-orchestrator/SKILL.md`.
- `skills/china-stock-research-orchestrator/references/final-output-contract.md`, `skills/shared/references/{citation-standard,source-registry,research-output-template}.md`, `skills/risk-warning-catalysts/SKILL.md`.

HHFinAi (`BATCH-001-009`):

- `README.md`, `LICENSE`, `investment-report-reader/SKILL.md`, `thematic-investment-research/SKILL.md`.
- `thematic-investment-research/references/{report-structure,risk-assessment}.md`.

Longbridge (`BATCH-001-010`):

- `LICENSE`, `skills/longbridge-research/SKILL.md`, `skills/longbridge-research/references/{investment-ideas,coverage-initiation,stock-research,thesis-tracker}.md`.
- `skills/longbridge-earnings/references/full-report.md`, `skills/longbridge-content/references/filing.md`.

TraderMonty (`BATCH-001-004`):

- `LICENSE`, `skills/trader-memory-core/SKILL.md`, `skills/trader-memory-core/references/thesis_lifecycle.md`, `skills/trader-memory-core/schemas/thesis.schema.json`.
- `skills/trade-hypothesis-ideator/SKILL.md`, `skills/trade-hypothesis-ideator/references/evidence_quality_guide.md`, `skills/trade-hypothesis-ideator/prompts/critique_prompt_template.md`, `skills/trade-hypothesis-ideator/schemas/hypothesis_card.schema.json`.

Deep Research (`BATCH-001-013`):

- `README.md`, `LICENSE`, `skills/research-codex-en/{research,research-deep,research-report}/SKILL.md`.

Vibe Trading (`BATCH-001-014`):

- `LICENSE`, `agent/src/skills/{research-discipline,thesis-tracker,report-generate,deep-company-series}/SKILL.md`.
- `agent/src/swarm/presets/equity_research_team.yaml`.

## Final Recommendation

Implement the four target Skills around one shared structured-claim contract, not four independent prose prompts. The decisive composition is:

```text
validated upstream capability artifacts
→ falsifiable investment thesis
→ independent bear-case red team
→ catalyst record
→ claim/source verification
→ deterministic report assembly
```

This preserves the strongest methods in the corpus while removing trading advice, vendor coupling, hidden file access, neutral defaults, unknown suppression, prompt duplication, and unverified report prose.
