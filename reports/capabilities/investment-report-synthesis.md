# Investment Report Capability Synthesis

Research date: 2026-07-16

Capability: `investment-report`

Evidence mode: static, capability-first synthesis from the locked 36-candidate corpus

## Scope And Responsibility Boundary

`investment-report` is the final deterministic assembler of validated research artifacts.

It owns:

- ordered Markdown assembly from structured capability envelopes;
- clear separation of facts, assumptions, estimates, unknowns, risks, and warnings;
- thesis, independent bear case, catalysts, conflicts, gaps, and source disclosure;
- stable claim/source references and source footnotes;
- report-level period, unit, arithmetic, and cross-section consistency checks;
- machine-readable completeness state;
- demo, as-of-date, generation-time, and non-advice disclosures.

It requires validated capability artifacts, the completed `source-verification` ledger, `sources.json`, task metadata, and loaded Skill/spec manifests.

It must not:

- conduct new research, fetch data, or calculate an absent analysis;
- invent or silently transform a fact, assumption, estimate, risk, source, or claim;
- hide an upstream conflict, unknown, warning, or skipped capability;
- treat fluent prose or visual polish as evidence confidence;
- issue a rating, trade instruction, target-return promise, or position recommendation;
- require a browser, CDN, PDF/DOCX generator, network, or API key.

Primary handoff: `report.md` plus a report result envelope suitable for task completion, resume validation, and `doctor`.

## Review Boundary And Safety Record

- Research stayed within the 36 candidates already in the locked registry corpus.
- The task study used commit-pinned snapshots, checked archive hashes, existing local audits, and documentation-only drafts.
- No third-party report generator, Skill, script, CLI, PDF helper, browser agent, broker API, installer, external chart, CDN asset, live quote, analyst document, credential, or user-private file was run or accessed.
- Candidate report templates and prompts were not copied; root license text is not authorization to copy embedded reports, partner data, or file-level content.
- The output design independently implements attributed method ideas against InvestKit's structured result contract.

Evidence grades are `A` for commit-pinned relevant content plus identifiable root license evidence, `B` for hash-pinned local content with incomplete provenance/license, `C` for registry/audit/draft evidence, and `blocked` for prohibited execution/integration.

## Design-Changing Evidence Identities

| Evidence ID | Registry candidate | Commit | Snapshot SHA-256 | Grade | License evidence | Decision |
|---|---|---|---|---|---|---|
| `REPORT-A1` | BATCH-001-001, Anthropic financial-services | `4aa51ed3d379731f8f9beff498d749580372699c` | `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | A | Apache-2.0 root text; sub-assets may differ | `extract` |
| `REPORT-A2` | BATCH-001-008, china-stock-research-skills | `d49f1f360deac57821d5d6b3aff664dff232acc6` | `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2` | A | MIT root text | `extract` |
| `REPORT-A3` | BATCH-001-010, Longbridge skills | `d68372ab584a77b3cb2a078a05c1322267729100` | `79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e` | A | MIT root text | `extract` |
| `REPORT-A4` | BATCH-001-014, Vibe-Trading | `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722` | `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872` | A | MIT root text | `extract` |
| `REPORT-A5` | BATCH-001-009, HHFinAi equity-research skills | `6e7ceef3c65287b7b88436fb4876f541b592a2ed` | `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6` | A | MIT root text | `reference` |
| `REPORT-A6` | BATCH-001-007, InvestSkill | `6449af2d0fc410a6c541c5815c601ba9f649d791` | `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5` | A | MIT root text | `reference` |
| `REPORT-A7` | BATCH-001-013, Deep-Research-skills | `e5479f857f484cde13fe69d2f3ce8de7af193bc7` | `44b3b02753d4ed1359ce13a12055cf75b3e415f68abbbe2626ded39e62001e8e` | A | MIT root text | `reference` |

## Files Represented By The Evidence

- `REPORT-A1`: `plugins/vertical-plugins/equity-research/skills/initiating-coverage/SKILL.md` and its `task1-company-research.md` and `task5-report-assembly.md` references.
- `REPORT-A2`: `skills/china-stock-research-orchestrator/SKILL.md`, `examples/full-report-flow.md`, `references/final-output-contract.md`, `skills/shared/references/citation-standard.md`, `source-registry.md`, and `research-output-template.md`.
- `REPORT-A3`: `skills/longbridge-research/SKILL.md`, `references/coverage-initiation.md`, `stock-research.md`, `skills/longbridge-earnings/references/full-report.md`, and `skills/longbridge-content/references/filing.md`.
- `REPORT-A4`: `agent/src/skills/report-generate/SKILL.md`, `research-discipline/SKILL.md`, `deep-company-series/SKILL.md`, and `agent/src/swarm/presets/equity_research_team.yaml`.
- `REPORT-A5`: `investment-report-reader/SKILL.md`, `thematic-investment-research/SKILL.md`, and `references/report-structure.md` and `risk-assessment.md`.
- `REPORT-A6`: `plugins/us-stock-analysis/skills/full-report/SKILL.md`, `report-generator/SKILL.md`, `result-validator/SKILL.md`, and `research-bundle/SKILL.md`.
- `REPORT-A7`: `skills/research-codex-en/research-report/SKILL.md`, `research/SKILL.md`, and `research-deep/SKILL.md`.

Anthropic's two initiating-coverage references are byte-identical to the LangAlpha lineage at SHA-256 `00ec47ca64c1cfdf6e1b74fa8c693633b5e12e98264667b40f2d7dea90b48227` and `7e2f2ccc6bfb54a4be247cd29a9aa95df20a624bb82243980d4f31412e7172ed`; duplicated lineage is not independent evidence.

## Candidate Strengths And Weaknesses

### Anthropic Financial Services — `REPORT-A1`

Strengths:

- enforces staged prerequisites and input verification before report assembly;
- checks source dates, model/report consistency, and scenario coverage;
- recommends writing the executive summary after the body;
- demonstrates that placeholder upstream work should not become polished downstream output.

Weaknesses:

- targets a 30–50 page DOCX with charts and external tools;
- requires a rating and price target and uses BUY/HOLD/SELL conventions;
- prose/report consistency checks are not a machine-readable no-new-claim gate.

### China Stock Research — `REPORT-A2`

Strengths:

- keeps facts, interpretation, open questions, monitoring indicators, valuation hooks, conflicts, and sources distinct;
- separates module outputs from orchestration and final assembly;
- requires source and citation discipline in the merged result.

Weaknesses:

- final output remains largely a prose contract;
- claim IDs and artifact-union checks are not enforced;
- market-specific source conventions need generalization.

### Longbridge — `REPORT-A3`

Strengths:

- reuses captured raw data rather than refetching during writing;
- enforces a single reporting period, actual/estimate notation, source-per-table, and arithmetic checks;
- connects report sections to structured research activities.

Weaknesses:

- is coupled to a broker CLI, current data, authentication, ratings, and targets;
- vendor-bound data routes are not a first-party report contract;
- live-data assumptions obscure missing-data and deterministic-offline behavior.

### Vibe-Trading — `REPORT-A4`

Strengths:

- detects pseudo-precision, inconsistent accounting bases, double counting, unfair peer comparisons, and absolute wording;
- requires corrections to cascade through dependent sections;
- provides useful final quality-gate concepts.

Weaknesses:

- report generation is part of a trading/action product;
- long-form templates and external tool assumptions exceed v0.2 scope;
- visual and narrative polish can dominate the structured evidence contract.

### HHFinAi, InvestSkill, And Deep Research — `REPORT-A5`–`REPORT-A7`

HHFinAi contributes triangulation, unstated-falsifier, and risk-disclosure checks. InvestSkill exposes useful validator and bundle concepts but also demonstrates unsafe action blocks, neutral defaults, and missing-data defects. Deep Research demonstrates structured batch/resume ideas but its report path can suppress uncertain fields. These are supporting or negative examples, not bases for direct adaptation.

## Data-Only, Unavailable, And Unsafe Evidence

- EASTMONEY-001 is `reference` as a data/API asset; no report method is adopted.
- CICCWM-001 through CICCWM-006 are `unsafe`: license unknown and local audit findings include home-directory credential access, credential telemetry, device fingerprinting, and weak TLS.
- GF-002 and GF-003 are `reference` for possible future sourced company/financial fields; API authorization, field definitions, provenance, response validation, and redistribution terms remain unknown.
- GF-001 and GF-004 through GF-008 are `reference` for corpus completeness only and do not affect report assembly.
- GUOSEN-001 through GUOSEN-006 are `unknown` because usable content is absent and license evidence is unavailable.
- SKILLHUB-001 is `reject` as report evidence because it is an untrusted installation-instruction snapshot, not a research-output method.
- BATCH-001-002, 003, 004, 005, 006, 011, and 012 supplied no stronger deterministic report contract; decision `reference` for adjacent capabilities.

## Adopted, Modified, And Rejected Ideas

Adopted:

- prerequisite gates, source-per-table, single-period consistency, summary-last, and correction-cascade checks;
- distinct facts, assumptions, estimates, unknowns, risks, conflicts, and skipped capabilities;
- explicit gaps and a machine-readable completeness state;
- offline Markdown as the canonical human-readable artifact.

Modified:

- institutional long-form templates become a compact structured report assembled from capability IDs;
- citation links become stable claim/source footnotes backed by the verification ledger;
- quality review becomes deterministic membership, arithmetic, period/unit, and dependency checks;
- narrative confidence becomes evidence disclosure rather than stylistic certainty.

Rejected:

- ratings, targets, buy/sell language, position instructions, and deterministic return claims;
- externally loaded charts, CDNs, browser/PDF/DOCX dependencies, and live-data refresh during assembly;
- neutral defaults for missing capabilities and omission of uncertain fields;
- any report generator that introduces a new number, source, assumption, estimate, risk, or conclusion.

## Final First-Party Method

1. Validate the exact `company-deep-dive` stage order and required capability artifacts.
2. Require completed `bear-case-analysis` and `source-verification` artifacts for a completed report.
3. Freeze input checksums and build the allowed union of claim, fact, assumption, estimate, risk, warning, unknown, and source IDs.
4. Determine the report as-of date, generation time, demo state, research boundary, and skipped-capability list.
5. Render body sections from structured artifacts in deterministic order.
6. Render thesis, bull/base reasoning, independent counter-thesis, catalysts, risks, assumptions, estimates, and unknowns without creating content.
7. Render stable source footnotes and verification states for material facts and tables.
8. Preserve authoritative conflicts and unresolved material claims visibly.
9. Check arithmetic, units, periods, accounting scope, peer comparability, scenario consistency, and duplicated values.
10. Write the executive summary only by selecting already-rendered, verified body findings.
11. Compare every emitted ID and numeric value with the allowed input union; fail on any new material.
12. Persist Markdown and the report result envelope atomically.

## Required Report Structure

The report includes research subject, prominent demo-data declaration, as-of date, executive summary, company and business-model overview, financial and earnings-quality analysis, valuation and comps, earnings/events, investment thesis, bull/base case, independent bear case, catalysts, positive and negative evidence, risks, assumptions, estimates, unknowns, skipped capabilities, source conflicts, source register, used Skills/specs, generation time, and research/non-advice boundary.

The report result envelope records `input_artifact_checksums`, `emitted_claim_ids`, `emitted_source_ids`, `section_statuses`, `validation_warnings`, and completeness state: `complete`, `complete_with_gaps`, or `failed_validation`.

A polished document with failed mandatory source or bear-case validation is `failed_validation`. A report with disclosed non-material or permitted skipped-capability gaps may be `complete_with_gaps`; it can never be silently labeled complete.

## Handoff And Determinism Rationale

The report is a view over persisted artifacts. Every rendered material statement, number, table row, risk, and footnote is addressable to the frozen input union. Completed resume can therefore byte-compare the Markdown and report envelope, while `doctor` can detect an invented claim, changed source, missing section, corrupt artifact, or external symlink without rerunning research.

## License, Security, And Remaining Unknowns

- MIT or Apache-2.0 root license evidence exists for design-changing snapshots; no third-party text, template, code, chart, or schema was copied, and LangAlpha/Anthropic duplicate lineage is not independent evidence.
- CICCWM remains blocked and license-unknown; GF rights/behavior and Guosen contents/licenses remain unknown.
- External analyst reports may carry copyright/data-use restrictions even when a repository's root code license is permissive; no candidate is approved, installed, or executed by this synthesis.

## Required Behavioral Evals

- Generate a report from structured artifacts only and compare emitted IDs with the exact input union.
- Fail if the report contains any new number, source, fact, assumption, estimate, risk, or conclusion.
- Require completed independent bear-case and source-verification stages.
- Include every permitted skipped capability and its reason/missing inputs.
- Include source conflicts, risks, assumptions, estimates, unknowns, warnings, and the demo declaration.
- Verify executive-summary statements already exist in completed body artifacts.
- Verify every material factual statement/table has stable claim/source references.
- Check arithmetic plus period, unit, currency, market, accounting-scope, and scenario consistency.
- Reject a report assembled from a stale or altered capability checksum.
- Mark mandatory source or bear-case failure as `failed_validation`, not complete.
- Verify no BUY/SELL/HOLD, target return, stop loss, position size, or deterministic promise appears.
- Verify no CDN, network, browser, PDF/DOCX tool, broker CLI, or API key is required.
- Verify missing data remains unknown and no skipped module becomes neutral evidence.
- Corrupt an upstream ID, source link, checksum, and symlink; resume and `doctor` must fail closed.
- Resume a completed task and byte-compare `report.md` and all analytical artifacts except `run-log.json`.
- Verify the complete offline Workflow produces the same report bytes from identical frozen inputs.

## Final Design Rationale

The report is a deterministic evidence view, not a final chance for the model to improvise. It combines the corpus's strongest prerequisite, citation, period, arithmetic, conflict, and revision checks while removing advice, vendor/tool coupling, hidden refreshes, uncertainty suppression, and style-driven confidence. The no-new-material gate preserves the exact boundary between research and presentation.
