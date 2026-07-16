# Company Deep Research Capability Synthesis

Research date: 2026-07-16

Task: InvestKit v0.2 — Investment Core Pack

Decision: independently implement a source-led first-party Skill; do not install or thinly adapt one candidate.

## Outcome

The corpus supports a company dossier broader than a filing summary but narrower than business-model, accounting, valuation, thesis, and report capabilities.

The synthesis combines evidence layering and routing from China-stock, public-equity diligence questions from investor-harness, filing/source inventory from Anthropic, and revision discipline from Vibe-Trading.

No candidate alone supplies InvestKit's trigger boundary, claim/source IDs, missing-data semantics, result envelope, safe Runtime behavior, and handoffs.

## Responsibility Boundary

Owns:

- canonical identity, history, products, segments, customers, channels, geographies, and value-chain facts;
- management, governance, ownership, and capital-allocation facts;
- competitive, industry, regulatory, and material-disclosure context;
- dated source inventory, contradictions, research gaps, unresolved questions, and materiality-ranked findings.

Does not own:

- detailed revenue mechanics/unit economics, statement normalization, accounting quality, valuation, comps, thesis, catalysts, or report assembly;
- investment instructions, target prices, position sizing, or return promises.

It requires an unambiguous security identity and available source metadata.

It hands off a structured company fact base and source manifest.

## Search And Evidence Rules

All 36 rows in registry/inbox/sources.csv were searched; no candidate was added.

Tree metadata for all 14 registered GitHub snapshots was searched.

Only the files named below were treated as method evidence; tree-only, registry-only, unavailable, data-only, and duplicate evidence was labeled separately.

Grade A means commit/hash-pinned content plus root-license evidence, not file-reuse approval.

Grade B means hash-pinned local evidence with incomplete license/provenance; grade C means registry or draft-only evidence.

## Exact Design-Changing Evidence

| Candidate | Exact source state | Files actually read | Design-changing evidence |
|---|---|---|---|
| BATCH-001-008 China-stock | commit d49f1f360deac57821d5d6b3aff664dff232acc6; snapshot SHA-256 4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2; MIT root; grade A | skills/china-stock-research-orchestrator/SKILL.md, skills/business-decomposition-order-quality/SKILL.md, skills/strategy-business-transition/SKILL.md, skills/industry-competition-moat/SKILL.md | explicit facts/interpretation/open-questions layers, official-source priority, capability routing, and mergeable modules |
| BATCH-001-006 Investor Harness | commit 2ce44f477189e4ed04d61764bec449405f81734e; snapshot SHA-256 bc815801d5a4dcefff817b3e04e17730be41cd702c8e03129d8fa47906be749f; MIT root; grade A | skills/sm-company-deepdive/SKILL.md, core/preamble.md, core/evidence.md, relevant core/acceptance.md sections, core/compliance.md | nine diligence questions, revenue/profit drivers, peer differences, verification nodes, evidence labels, and missing-material list |
| BATCH-001-001 Anthropic | commit 4aa51ed3d379731f8f9beff498d749580372699c; snapshot SHA-256 9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945; Apache-2.0 root with possible nested terms; grade A | plugins/vertical-plugins/equity-research/skills/initiating-coverage/SKILL.md and plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/task1-company-research.md | staged inventory of filings, IR material, history, management, customers, competition, industry, and risks |
| BATCH-001-014 Vibe-Trading | commit 531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722; snapshot SHA-256 8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872; MIT root; grade A | agent/src/skills/deep-company-series/SKILL.md | caliber consistency, double-counting/source checks, anti-pseudo-precision, and cascade repair after a fact changes |

## Strengths, Weaknesses, And Disposition

| Candidate | Strengths | Weaknesses and risks | InvestKit disposition |
|---|---|---|---|
| China-stock | Keeps evidence classes separate; prioritizes official sources; routes adjacent work | A-share-specific; no machine envelope; URLs do not express claim IDs, freshness, or conflicts | Adopt evidence layers/routing; generalize markets and persist claim/source records |
| Investor Harness | Decision-relevant questions, evidence labels, verification nodes, and visible gaps | Preamble scans/creates user workspace files and requires tools; missing-data “do not start” blocks partial work; incompatible frontmatter | Adopt questions/evidence classes; replace side effects with Runtime task state and explicit unknowns |
| Anthropic | Broad recognizable coverage and useful filing/issuer-material prerequisites | “No prerequisites” conflicts with evidence needs; word quotas reward volume; no typed evidence schema; brand-based quality claims | Convert inventory into materiality-led sections with input gates; reject quotas and brand claims |
| Vibe-Trading | Best revision-cascade, consistency, double-count, and false-precision checks | Huge publication series, mixed valuation/trading scope, embedded tool behavior | Extract revision checklist; reject series orchestration and action language |

## Supporting, Duplicate, And Rejected Evidence

BATCH-001-007 InvestSkill was read at commit 6449af2d0fc410a6c541c5815c601ba9f649d791, snapshot SHA-256 758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5, file plugins/us-stock-analysis/skills/10k-digest/SKILL.md, MIT root.

Its filing-section inventory and stale-document checks are useful; its bullish/bearish and buy/hold/sell block is rejected.

BATCH-001-003 LangAlpha, commit 2459e569f28c6f0c2db7315ab6ed95a5c399f0e7 and snapshot SHA-256 13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6, contains skills/initiating-coverage/SKILL.md.

An exact diff found its body matched Anthropic while frontmatter and a derived-from license field differed; it is duplicate provenance, not an independent method vote.

BATCH-001-013 Deep-Research-skills, commit e5479f857f484cde13fe69d2f3ce8de7af193bc7 and snapshot SHA-256 44b3b02753d4ed1359ce13a12055cf75b3e415f68abbbe2626ded39e62001e8e, skills/research-codex-en/research-deep/SKILL.md, is generic web batching and is rejected as an investment-company method.

## Data/API-Only And Unavailable Evidence

GF-002, adapted/skills/gf_stock_f10/SKILL.md, SHA-256 c07adbf7d094bb93e2d2ddceaed687480ca05444b97312d7daad4f64a219cfc0, identifies company name, board, listing date, business scope, and industry fields.

GF-002 is grade C: license, API terms, authorization, field provenance, response schema, and fixture behavior are unknown.

EASTMONEY-001, archive commit 61cfae47451f797d95ae4553ffcc7569b9957e7d and SHA-256 24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15, can supply company facts but is a data/API candidate, not a research method.

CICCWM-003, archive SHA-256 67e2247dc9db5375031856e4399c0b455d87c212d1a05d03a3e586c7e3ce266b, is adjacent news data; its license is unknown and execution is blocked.

GUOSEN-002 is zero-byte with SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; GUOSEN-003 through GUOSEN-006 are absent.

Unavailable Guosen content permits no positive or negative method conclusion.

No Provider is required for the offline Eval; a future adapter may only serve a named data gap.

## Adopted, Modified, And Rejected Ideas

Adopted:

- typed evidence layers, official-source priority, and source inventory before synthesis;
- concrete questions on drivers, management, governance, competition, and verification;
- contradictions, gaps, and revision propagation as first-class outputs.

Modified:

- issuer/management assertions remain attributed unless corroborated;
- missing evidence yields partial completion or justified skip, never fallback;
- topic inventories become materiality-ranked rather than word-count driven;
- company/segment facts are handed off without pre-judging business-model durability.

Rejected:

- training-data substitution, uncited facts, and generic web research as investment method;
- user-directory scans, external tool mandates, vendor lock-in, and automatic file creation;
- buy/hold/sell scores, target values, position language, and duplicate evidence counting.

## Final InvestKit Method

1. Validate security identity, question, market, as-of date, and source bounds.
2. Build a source manifest with source ID, publisher, document type, period, publication/retrieval or fixture date, and freshness.
3. Extract typed identity/history, product, segment, customer/channel, geography, management/governance, capital-allocation, value-chain, competition, regulation, and risk records.
4. Keep management claims attributed unless independent evidence corroborates them.
5. Compare like-for-like periods and retain definition, restatement, and omission warnings.
6. Preserve contradictory claims with their source IDs rather than silently selecting one.
7. Separate facts, interpretations, assumptions, estimates, and unknowns.
8. Rank findings by materiality and evidence confidence.
9. Name the exact missing source or field required to resolve each important question.
10. Revalidate dependent findings when a material source fact changes.

## Output Contract And Handoffs

The capability envelope separates status, facts, assumptions, estimates, unknowns, findings, risks, warnings, source_ids, method, and Skill version.

Company facts carry persisted source IDs; management commentary retains attribution.

Unknowns identify the topic, evidence attempted, missing input, and downstream effect.

Business-model-analysis receives revenue-model and customer/segment facts without re-discovering identity.

Financial-statement-analysis receives filing, period, audit, and source metadata.

Thesis and bear-case capabilities receive management, governance, capital-allocation, competition, and open-question records without a verdict.

Source-verification can audit the exact claim lineage.

## Security, License, And Honest Unknowns

MIT or Apache-2.0 root evidence supports review, not automatic nested-file reuse; file-level compatibility and attribution remain separately reviewable.

CICCWM licenses are unknown and documented credential, telemetry, home-directory, device-fingerprint, and TLS behavior blocks execution/integration.

GF-002 authorization, license, API terms, and redistribution rights remain unknown.

Guosen content and licenses remain unknown because evidence is unavailable.

No raw candidate may be installed into skills/ or a host target.

## Non-Execution And No-Copy Attestation

This synthesis used static text and recorded local audits only.

No third-party Skill, script, installer, CLI, MCP, package, endpoint, or API was executed, imported, sourced, installed, or called.

No credential or user-home file was read and no TLS setting was weakened.

No raw asset was copied into first-party source, Runtime code, or installation targets.

The final method is newly expressed from multiple candidates and InvestKit-owned evidence/persistence/safety requirements; no prompt, code, formula, or template was copied wholesale.

## Required Evals

1. Positive: build a dossier from an identified security, annual filing, issuer profile, and governance fixture.
2. Near miss: “Calculate this company's DCF” routes to valuation-analysis.
3. Near miss: unit-economics analysis routes to business-model-analysis after fact-base creation.
4. Ambiguous identity fails or remains unresolved before company claims.
5. Missing management evidence produces unknowns, not invented biographies.
6. Management market-share claims remain attributed without corroboration.
7. Contradictory sources remain visible with conflict warnings.
8. Stale evidence records freshness and cannot be presented as current.
9. Changed segment definitions prevent false trend comparison.
10. A corrected material fact invalidates or updates dependent findings.
11. Every factual finding references persisted source IDs.
12. Missing data yields partial coverage, never training-data substitution.
13. Typed evidence classes remain separate in the output.
14. Business-model handoff preserves identity and source lineage.
15. No buy/sell, position, target-return, or guaranteed-return instruction appears.

## Final Rationale

Company-deep-research is a traceable fact-base producer, not an all-purpose equity report.

Its source coverage, contradiction handling, explicit gaps, and revision-safe handoffs make the downstream analytical pack composable and independently reviewable.
