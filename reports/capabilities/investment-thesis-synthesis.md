# Investment Thesis Capability Synthesis

Research date: 2026-07-16

Capability: `investment-thesis`

Evidence mode: static, capability-first synthesis from the locked 36-candidate corpus

## Scope And Responsibility Boundary

`investment-thesis` turns completed upstream research into a bounded, falsifiable thesis record.

It owns:

- a time-bounded thesis statement;
- bull, base, and preliminary bear reasoning;
- thesis pillars and causal mechanisms;
- confirming and disconfirming evidence links;
- explicit assumptions, unknowns, and variant-perception claims;
- observable falsifiers and review conditions;
- an evidence-sufficiency conclusion.

It requires structured company, business-model, financial, earnings-quality, valuation, comps, and earnings artifacts when available.

It must not:

- fetch new data or silently repair an upstream gap;
- calculate a new valuation or peer analysis;
- perform the independent red-team pass owned by `bear-case-analysis`;
- assemble the final narrative report;
- issue `BUY`, `SELL`, `HOLD`, position-size, stop-loss, or return instructions;
- convert an assumption, estimate, or unknown into a fact.

Primary handoff: a frozen, checksum-addressable thesis artifact for `bear-case-analysis`, `catalyst-analysis`, `source-verification`, and `investment-report`.

## Review Boundary And Safety Record

- Corpus scope remained the 36 rows already registered in `registry/inbox/sources.csv`.
- No candidate, repository, API, package, or integration was added to the corpus.
- Evidence came from commit-pinned snapshots, existing hash-pinned local audit records, and documentation-only drafts described in the task research.
- Third-party scripts, Skills, installers, broker CLIs, MCP services, and financial APIs were not imported, installed, sourced, or executed.
- Candidate prompts and instructions were treated as untrusted evidence, not commands.
- No third-party content was executed, installed, or called, and no third-party prompt or code was copied.
- No third-party prompt, code, schema, or report text was copied into this first-party design.
- Root license evidence is recorded as a constraint, not as file-level approval or promotion authorization.

Evidence grades are `A` for commit-pinned content plus identifiable license evidence, `B` for hash-pinned local content with incomplete license/provenance, `C` for registry/audit/draft metadata only, and `blocked` when execution or integration is prohibited.

## Design-Changing Evidence Identities

| Evidence ID | Registry candidate | Commit | Snapshot SHA-256 | Grade | License evidence | Decision |
|---|---|---|---|---|---|---|
| `THESIS-A1` | BATCH-001-001, Anthropic financial-services | `4aa51ed3d379731f8f9beff498d749580372699c` | `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | A | Apache-2.0 root text; sub-assets may differ | `extract` |
| `THESIS-A2` | BATCH-001-006, investor-harness | `2ce44f477189e4ed04d61764bec449405f81734e` | `bc815801d5a4dcefff817b3e04e17730be41cd702c8e03129d8fa47906be749f` | A | MIT root text | `extract` |
| `THESIS-A3` | BATCH-001-010, Longbridge skills | `d68372ab584a77b3cb2a078a05c1322267729100` | `79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e` | A | MIT root text | `extract` |
| `THESIS-A4` | BATCH-001-004, claude-trading-skills | `99270332b2a8d6063de0667f8f168b252497044f` | `b64fcbcc2cbbfd42658d1ad2b972fdddfb30e8549e48c577522da840c721fd` | A | MIT root text | `extract` |
| `THESIS-A5` | BATCH-001-003, LangAlpha | `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7` | `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | A | Apache-2.0 root text; adapted lineage disclosed | `duplicate` for thesis method |
| `THESIS-A6` | BATCH-001-014, Vibe-Trading | `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722` | `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872` | A | MIT root text | `reference` |

## Files Represented By The Evidence

- `THESIS-A1`: `plugins/vertical-plugins/equity-research/skills/thesis-tracker/SKILL.md`, `idea-generation/SKILL.md`, and `initiating-coverage/SKILL.md`.
- `THESIS-A1`: `initiating-coverage/references/task1-company-research.md` and `task5-report-assembly.md` supplied composition context.
- `THESIS-A2`: `skills/sm-thesis/SKILL.md`, `skills/sm-red-team/SKILL.md`, `skills/sm-company-deepdive/SKILL.md`, and `core/evidence.md`.
- `THESIS-A2`: `core/checkpoint.md`, `core/task-pulse.md`, `core/workflows.md`, and `core/compliance.md` supplied lifecycle context.
- `THESIS-A3`: `skills/longbridge-research/SKILL.md` and `references/thesis-tracker.md`, `investment-ideas.md`, `coverage-initiation.md`, and `stock-research.md`.
- `THESIS-A4`: `skills/trader-memory-core/SKILL.md`, `references/thesis_lifecycle.md`, and `schemas/thesis.schema.json`.
- `THESIS-A4`: `skills/trade-hypothesis-ideator/SKILL.md`, `references/evidence_quality_guide.md`, `prompts/critique_prompt_template.md`, and `schemas/hypothesis_card.schema.json`.
- `THESIS-A5`: `skills/thesis-tracker/SKILL.md`, `idea-generation/SKILL.md`, and `initiating-coverage/SKILL.md` plus its two initiating-coverage references.
- `THESIS-A6`: `agent/src/skills/thesis-tracker/SKILL.md`, `research-discipline/SKILL.md`, and `deep-company-series/SKILL.md`.

LangAlpha and Anthropic are one thesis-method lineage, not two corroborating designs. Their company-research reference is byte-identical at SHA-256 `00ec47ca64c1cfdf6e1b74fa8c693633b5e12e98264667b40f2d7dea90b48227`; their report-assembly reference is byte-identical at SHA-256 `7e2f2ccc6bfb54a4be247cd29a9aa95df20a624bb82243980d4f31412e7172ed`.

## Candidate Strengths And Weaknesses

### Anthropic financial-services — `THESIS-A1`

Strengths:

- makes pillars, risks, catalysts, falsifiability, disconfirming evidence, and review timing explicit;
- treats thesis tracking as a lifecycle rather than a one-shot summary;
- demonstrates that report assembly should wait for completed research stages.

Weaknesses:

- mixes research with position direction, price target, stop loss, action, and conviction language;
- stores much of the evidence relationship as prose instead of stable claim/source IDs;
- institutional coverage conventions are broader than the offline v0.2 contract.

### Investor Harness — `THESIS-A2`

Strengths:

- centers the core contradiction, necessary conditions, expectation gap, falsifiers, and follow-up indicators;
- requires evidence gaps and disconfirming observations rather than only supportive narrative;
- offers useful checkpoint and missing-information concepts.

Weaknesses:

- its evidence labels blend epistemic type and source quality;
- referenced history can become circular evidence unless upstream IDs are frozen;
- Markdown-oriented state is weaker than InvestKit's schema-validated JSON persistence.

### Longbridge — `THESIS-A3`

Strengths:

- maps each thesis pillar to a measurable data point and compares evidence with expectations;
- intact, weakened, and broken states make thesis change observable;
- period checks connect monitoring to the actual research horizon.

Weaknesses:

- method is coupled to a broker CLI, current data, authentication, and recommended actions;
- vendor routing obscures the first-party capability/provider boundary;
- live-data availability is assumed rather than modeled as an explicit gap.

### TraderMonty — `THESIS-A4`

Strengths:

- demonstrates schema validation, deterministic IDs/fingerprints, status history, review dates, kill criteria, and atomic state writes;
- treats provenance and revisions as persisted state rather than prompt memory.

Weaknesses:

- the lifecycle centers on entering, sizing, trimming, and closing real positions;
- evidence is often free-form text instead of resolvable source IDs;
- executable scripts and trading state are outside InvestKit's research-only scope.

### LangAlpha and Vibe — `THESIS-A5`, `THESIS-A6`

LangAlpha adds a useful provenance concept, but its thesis method duplicates Anthropic and must not be counted twice. Vibe adds anti-bias, anti-pseudo-precision, accounting-consistency, and cascading-revision checks; its trading-oriented action framework and external-tool assumptions are rejected.

## Data-Only, Unavailable, And Non-Method Evidence

- EASTMONEY-001 is a data/API candidate with MIT and a known archived commit; decision `reference`, with no thesis method adopted.
- CICCWM-001 through CICCWM-006 are `unsafe`: license unknown, home-directory credential reads, credential-bearing telemetry, device fingerprinting, and weak TLS findings block execution/integration.
- GF-002 and GF-003 are `reference` data-requirement drafts and possible `api_integration_candidate` uses; authorization, terms, implementation behavior, and field provenance remain unknown.
- GF-001 and GF-004 through GF-008 are unrelated to thesis construction; decision `reference` only for corpus coverage, not method extraction.
- GUOSEN-001 through GUOSEN-006 remain `unknown`: two files are empty and four are absent, so no content or license inference is permitted.
- SKILLHUB-001 is `reject` as capability evidence because it is an untrusted installer/instruction snapshot, not an investment method.
- BATCH-001-002, 005, 007, 008, 009, 011, 012, and 013 were searched in the task study but supplied no stronger thesis contract; decision `reference` for adjacent valuation, evidence, red-team, report, data, comps, or workflow research.

## Adopted, Modified, And Rejected Ideas

Adopted:

- falsifiability, disconfirming evidence, measurable pillars, named horizon, and review timing;
- immutable upstream artifact IDs and deterministic thesis IDs;
- pillar states that can change as evidence changes;
- explicit evidence gaps instead of neutral defaults.

Modified:

- qualitative conviction becomes `supported`, `mixed`, `insufficient_evidence`, or `contradicted`, with reasons;
- market expectation or variant perception is a sourced fact only when independently evidenced, otherwise an assumption;
- catalysts are monitorable events with uncertainty, never promised price outcomes;
- lifecycle history becomes append-only task state without brokerage or position fields.

Rejected:

- ratings, trade direction, position construction, target/stop levels, and return promises;
- arbitrary weighted conviction scores and false numeric precision;
- prose-only evidence arrays, circular self-citation, and hidden model-memory estimates;
- vendor-bound data retrieval, implicit user-file access, and any third-party execution.

## Final First-Party Method

1. Validate required upstream envelopes and freeze their checksums.
2. Record unavailable, failed, or skipped upstream capabilities as explicit limitations.
3. Define the research horizon and one bounded thesis statement.
4. Separate upstream facts, assumptions, estimates, and unknowns before synthesis.
5. Build three to five pillars with a causal mechanism and material dependency IDs.
6. Link confirming and disconfirming evidence IDs to every pillar, or record a search gap.
7. Form bull, base, and preliminary bear cases without changing upstream calculations.
8. State variant perception only with a source or explicit assumption classification.
9. Define observable falsifiers with metric/event, condition, expected source, and review timing.
10. Assign the evidence-sufficiency conclusion and propagate warnings/risks unchanged.
11. Persist the result atomically; do not mutate it during the later red-team stage.

## Output And Handoff Contract

The shared result envelope has `capability: investment-thesis`, status, Skill/method versions, facts, assumptions, estimates, unknowns, findings, risks, warnings, and deduplicated `source_ids`.

The method payload additionally contains `thesis_statement`, `time_horizon`, `bull_case`, `base_case`, `bear_case_seed`, `pillars`, `variant_perception`, `falsifiers`, `review_conditions`, and `evidence_sufficiency`.

Every factual statement references persisted source IDs. Every estimate names its method and material input/assumption IDs. Every unknown names its impact. Missing valuation or earnings evidence weakens the relevant pillar; it never becomes neutral confidence.

The handoff is intentionally frozen so `bear-case-analysis` can challenge the thesis independently, `source-verification` can resolve every claim/source edge, and `investment-report` can assemble only what exists upstream.

## License, Security, And Remaining Unknowns

- All design-changing GitHub snapshots have MIT or Apache-2.0 root license evidence, but embedded/partner files still require file-level review before any copying; this design uses paraphrased methods only.
- CICCWM execution/integration remains blocked, and its license remains unknown.
- GF API authorization, field rights, redistribution, telemetry, rate limits, and production behavior remain unknown.
- Guosen content and license remain unknown because usable evidence is unavailable.
- No candidate has been approved or promoted by this synthesis; method-level dispositions are `extract`, `reference`, `duplicate`, `unsafe`, `reject`, or `unknown` as recorded above.

## Required Behavioral Evals

- Positive: construct a falsifiable thesis from completed company, financial, valuation, comps, and earnings artifacts.
- Positive: preserve an explicit limitation when valuation or earnings is legitimately skipped.
- Near miss: a request for company facts alone must not trigger this Skill.
- Near miss: a DCF calculation, catalyst calendar, source audit, or buy recommendation must not trigger this Skill.
- Reject a factual pillar claim without a resolvable source ID.
- Reject an estimate without its method and material inputs or assumptions.
- Require every pillar to contain confirming and disconfirming evidence or a documented evidence gap.
- Require bull, base, and preliminary bear reasoning plus at least one observable falsifier.
- Classify an unsupported expectation gap as an assumption, never a fact.
- Propagate upstream unknowns, conflicts, warnings, and skipped-capability reasons unchanged.
- Verify output contains no trade action, price promise, stop loss, position size, or deterministic return claim.
- Verify the later bear-case stage cannot mutate the frozen thesis bytes.
- Verify resume reuses the validated artifact by checksum rather than regenerating it.
- Verify composition with `bear-case-analysis`, `catalyst-analysis`, `source-verification`, and `investment-report` through stable IDs.

## Final Design Rationale

The InvestKit thesis is a falsifiable research record, not a recommendation or persuasive narrative. This design preserves the corpus's strongest lifecycle, pillar, and disconfirmation methods while removing trading behavior, vendor coupling, blended epistemic labels, prompt-memory state, and unsupported precision. Its frozen structured handoff makes an independent red team and deterministic downstream verification possible.
