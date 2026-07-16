# Source Verification Capability Synthesis

Research date: 2026-07-16

Capability: `source-verification`

Evidence mode: static, capability-first synthesis from the locked 36-candidate corpus

## Scope And Responsibility Boundary

`source-verification` is the mandatory claim/source gate before final report assembly.

It owns:

- source identity, provenance, fingerprint, quality, accessibility, and freshness;
- resolution of persisted claim IDs to persisted source IDs;
- period, unit, market, currency, and accounting-scope checks;
- fact coverage and estimate/assumption contract validation;
- conflict preservation and coverage-gap reporting;
- material-claim verification status and task-level gate status.

It requires all capability artifacts from stages 2 through 11, `sources.json`, task metadata, fixture/provider metadata, and the loaded Skill/spec manifests.

It must not:

- create a new company fact or analytical conclusion;
- rewrite a claim to make weak evidence appear stronger;
- cite an assumption merely to make it resemble a fact;
- average away conflicting authoritative sources;
- treat freshness and quality as one blended score;
- fetch an inaccessible source or call a Provider during verification;
- silently repair a failed upstream artifact.

Primary handoff: a verification ledger and gate result consumed by `investment-report`, `doctor`, persistence validation, and resume.

## Review Boundary And Safety Record

- The research boundary remained the 36 existing registry candidates; no new source was discovered or registered.
- Task evidence was static: commit-pinned snapshot files, checked archive identities, existing audits, registry metadata, and documentation-only drafts.
- No PDF helper, browser agent, financial API, broker CLI, MCP service, installer, shell workflow, or third-party script was run, and no source URL authorized extra download or execution.
- Candidate instructions were untrusted; selected ideas were paraphrased and independently designed.
- No API key, home-directory file, private report, or user credential was read; root license evidence does not prove that a particular embedded file, data record, or report is reusable.

Evidence grades are `A` for commit-pinned relevant content plus identifiable root license evidence, `B` for hash-pinned local content with incomplete license/provenance, `C` for registry/audit/draft descriptions, and `blocked` for prohibited execution/integration.

## Design-Changing Evidence Identities

| Evidence ID | Registry candidate | Commit | Snapshot SHA-256 | Grade | License evidence | Decision |
|---|---|---|---|---|---|---|
| `SOURCE-A1` | BATCH-001-008, china-stock-research-skills | `d49f1f360deac57821d5d6b3aff664dff232acc6` | `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2` | A | MIT root text | `extract` |
| `SOURCE-A2` | BATCH-001-009, HHFinAi equity-research skills | `6e7ceef3c65287b7b88436fb4876f541b592a2ed` | `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6` | A | MIT root text | `extract` |
| `SOURCE-A3` | BATCH-001-006, investor-harness | `2ce44f477189e4ed04d61764bec449405f81734e` | `bc815801d5a4dcefff817b3e04e17730be41cd702c8e03129d8fa47906be749f` | A | MIT root text | `extract` |
| `SOURCE-A4` | BATCH-001-003, LangAlpha | `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7` | `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | A | Apache-2.0 root text; adapted lineage disclosed | `extract` for provenance concept |
| `SOURCE-A5` | BATCH-001-010, Longbridge skills | `d68372ab584a77b3cb2a078a05c1322267729100` | `79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e` | A | MIT root text | `reference` |
| `SOURCE-A6` | BATCH-001-001, Anthropic financial-services | `4aa51ed3d379731f8f9beff498d749580372699c` | `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | A | Apache-2.0 root text; sub-assets may differ | `reference` |

## Files Represented By The Evidence

- `SOURCE-A1`: `skills/china-stock-research-orchestrator/SKILL.md`, `examples/full-report-flow.md`, `references/final-output-contract.md`, `skills/shared/references/citation-standard.md`, `source-registry.md`, and `research-output-template.md`.
- `SOURCE-A2`: `investment-report-reader/SKILL.md`, `thematic-investment-research/SKILL.md`, `references/report-structure.md`, and `references/risk-assessment.md`.
- `SOURCE-A3`: `core/evidence.md`, `core/compliance.md`, `skills/sm-thesis/SKILL.md`, `skills/sm-red-team/SKILL.md`, `core/checkpoint.md`, and `core/task-pulse.md`.
- `SOURCE-A4`: `README.md`, provenance descriptions associated with its research workbench/adapted Skill tree, and initiating-coverage/thesis files exposing duplicate Anthropic lineage.
- `SOURCE-A5`: `skills/longbridge-research/SKILL.md`, `references/coverage-initiation.md`, `stock-research.md`, `thesis-tracker.md`, `skills/longbridge-earnings/references/full-report.md`, and `skills/longbridge-content/references/filing.md`.
- `SOURCE-A6`: `plugins/vertical-plugins/equity-research/skills/initiating-coverage/SKILL.md` and its `task1-company-research.md` and `task5-report-assembly.md` references.

The task study verified that LangAlpha and Anthropic contain byte-identical initiating-coverage references at SHA-256 `00ec47ca64c1cfdf6e1b74fa8c693633b5e12e98264667b40f2d7dea90b48227` and `7e2f2ccc6bfb54a4be247cd29a9aa95df20a624bb82243980d4f31412e7172ed`. Verification must treat duplicated lineage as one source lineage, not two confirmations.

## Candidate Strengths And Weaknesses

### China Stock Research — `SOURCE-A1`

Strengths:

- separates facts, interpretation, and open questions;
- defines source tiers and requires conflicts to remain visible;
- preserves unit, period, accounting scope, and citation expectations;
- cleanly separates orchestration, source registry, and final output responsibilities.

Weaknesses:

- accessible URLs are not durable evidence identities;
- source tiers are market-specific and need generalization;
- assumptions and estimates can remain blended inside interpretation;
- prose contracts do not by themselves enforce claim/source referential integrity.

### HHFinAi — `SOURCE-A2`

Strengths:

- triangulates multiple documents and searches chart-versus-narrative contradictions;
- separates publication date from reference period;
- checks prior-cycle evidence and reports coverage gaps;
- does not assume one document is internally consistent.

Weaknesses:

- assumes PDF/document tooling and potentially restricted broker material;
- extraction commands and external tools are not an approved Runtime dependency;
- fixed report-reader workflows may not preserve deterministic offline fingerprints.

### Investor Harness — `SOURCE-A3`

Strengths:

- prevents consensus, inference, and unverified hypotheses from masquerading as public facts;
- emphasizes evidence gaps and compliance checks;
- provides useful checkpoints for research-state review.

Weaknesses:

- prose evidence labels mix epistemic type with source class or confidence;
- `public fact` does not establish source authority, freshness, period, or scope;
- claim/source links are not normalized into stable IDs.

### LangAlpha — `SOURCE-A4`

Strengths:

- describes provider/type, timestamp, arguments, fingerprint, snippet, and file/tool-access provenance;
- recognizes that provenance belongs outside transient model context.

Weaknesses:

- provenance belongs to a larger online workbench with secret-vault and external-provider surfaces;
- the repository acknowledges adapted Skills, so lineage must be checked carefully;
- implementation was not approved and is not reused.

### Longbridge And Anthropic — `SOURCE-A5`, `SOURCE-A6`

Longbridge contributes reporting-period integrity, raw-data reuse, source-per-table discipline, and provider identity. Anthropic contributes dependency and source-date checks. Their vendor/live-data and institutional-report assumptions are not adopted; they remain supporting references.

## Data-Only, Unavailable, And Unsafe Evidence

- EASTMONEY-001 is `reference`: a data/API source candidate with MIT and a known archived commit, but not a verification method.
- CICCWM-001 through CICCWM-006 are `unsafe`: local static audit found home-directory credential reads, credential-bearing telemetry, device fingerprinting, and weak TLS in five packages; licenses remain unknown.
- GF-002 and GF-003 are `reference` and potential `api_integration_candidate` inputs, but authorization, terms, redistribution, field provenance, timeouts, validation, and telemetry behavior remain unknown.
- GF-001 and GF-004 through GF-008 are `reference` for corpus/source coverage only and do not change this method.
- GUOSEN-001 through GUOSEN-006 are `unknown`: two zero-byte placeholders and four absent files provide no verifiable content or license.
- SKILLHUB-001 is `reject`: it is an untrusted installer/instruction snapshot with no source-verification investment method.
- BATCH-001-002, 004, 005, 007, 011, 012, 013, and 014 supplied no stronger verification contract; decision `reference` for adjacent capabilities or negative examples.

## Adopted, Modified, And Rejected Ideas

Adopted:

- stable claim-to-source linkage, source hierarchy, period/unit/scope preservation, freshness, triangulation, and conflict visibility;
- separate publication/effective, retrieval/fixture, and research as-of dates;
- durable fingerprints for persisted evidence;
- explicit coverage gaps rather than uncertain-field suppression.

Modified:

- URL citations become source records with stable IDs, locators/fixture paths, checksums, provider identity, and access state;
- source tiers become market-aware quality rules with rationales instead of one universal ranking;
- freshness becomes field/capability-specific, with a documented override rationale;
- epistemic type and evidence quality remain orthogonal dimensions.

Rejected:

- silently skipping uncertain fields or treating consensus as fact;
- resolving conflicts by majority vote, averaging, or report-author preference;
- inaccessible sources as sufficient support;
- network retrieval, PDF helpers, broker CLI calls, hidden credential reads, and external-tool dependence;
- a single confidence number that conceals quality, freshness, conflicts, and coverage.

## Final First-Party Method

1. Load and schema-validate `sources.json` plus capability envelopes for stages 2 through 11.
2. Normalize source identities and verify fingerprints, provider/fixture identity, access state, and demo status.
3. Resolve every material fact's source IDs; record missing or malformed references separately.
4. Validate assumptions for rationale/materiality without fabricating citations.
5. Validate estimates for method, input/assumption IDs, unit, period, and sensitivity metadata.
6. Check each source's publication/effective date, retrieval/fixture version, and research as-of date.
7. Apply capability- and field-specific freshness policy with explicit rationale for any override.
8. Verify market, currency, unit, fiscal period, accounting scope, and audit/review status where applicable.
9. Evaluate source quality and accessibility independently of freshness.
10. Detect duplicate lineage and authoritative conflicts; preserve every conflicting source and claim edge.
11. Classify each material claim and produce a task-level gate result.
12. Persist unresolved gaps for report disclosure and `doctor`; do not rewrite upstream claims.

## Source And Claim Record Contract

Each source record contains `source_id`, title, issuer/publisher, source type, locator or fixture path, publication/effective date, `retrieved_at` or fixture version, `as_of_date`, market, currency, period, unit, accounting scope, audit/review state, quality tier/rationale, first-party/secondary flag, accessibility, fingerprint, provider without credentials, warnings, known use/license constraints, and demo flag.

Each material claim contains `claim_id`, epistemic type, statement, capability origin, and source IDs. Assumptions carry rationale/materiality. Estimates carry method, inputs, assumptions, unit, period, and sensitivity. Unknowns carry the gap, decision impact, and next eligible source.

Claim statuses are `verified`, `partially_supported`, `unsupported`, `stale`, `conflicted`, `low_quality`, or `not_applicable`; multiple warnings may coexist. Task gate states distinguish pass, pass-with-disclosed-gaps, and fail. A material unresolved claim may appear only as explicitly unverified/unknown and cannot support a material conclusion.

## Handoff Rationale

`investment-report` consumes the ledger rather than running an informal citation pass. Stable claim/source IDs let deterministic rendering include only verified or explicitly disclosed material, while `doctor` and resume can fail closed on broken IDs, altered fingerprints, missing artifacts, or external symlinks. Verification never becomes a hidden research stage.

## License, Security, And Remaining Unknowns

- MIT or Apache-2.0 root evidence exists for the design-changing snapshots, but no candidate file, schema, or prompt was copied; LangAlpha's adapted lineage and confirmed duplicate files prevent false corroboration.
- CICCWM execution/integration remains blocked and license-unknown; GF authorization/data-use rights, Guosen contents/licenses, and any private broker-report rights remain unknown.
- Provider credentials must never enter source records, task artifacts, logs, or reports; no raw candidate is approved, installed, or promoted by this synthesis.

## Required Behavioral Evals

- Resolve every fact source ID against `sources.json`; fail or warn explicitly for a missing ID.
- Reject a fact with no source ID and an estimate with no method/material inputs.
- Accept an assumption without a citation only when rationale and materiality are present.
- Distinguish a fresh low-quality source from an older authoritative source without collapsing them into one score.
- Preserve two authoritative conflicting sources and mark the claim `conflicted`.
- Detect duplicate-lineage evidence and avoid counting it as independent corroboration.
- Flag inaccessible, malformed, stale, low-quality, and unsupported evidence separately.
- Preserve market, currency, unit, period, accounting scope, and demo status.
- Apply different freshness expectations to a business description and a market price.
- Reject a claim whose source fingerprint changed after artifact completion.
- Verify no network, browser, PDF helper, broker CLI, API key, or third-party code is required.
- Verify assumptions are not copied into facts and unknowns are not omitted.
- Verify source verification creates no new factual claim or analytical conclusion.
- Verify report assembly cannot proceed as `complete` when mandatory material claims fail the gate.
- Corrupt a source ID, checksum, and symlink; verify resume and `doctor` fail clearly without repair.
- Resume a completed task and byte-compare the ledger and all capability artifacts except the append-only run log.

## Final Design Rationale

Verification is a referential-integrity and evidence-quality gate, not a confidence-writing exercise. The design combines durable provenance, claim-level coverage, date/scope checks, triangulation, and visible conflicts while rejecting online tooling assumptions, URL-only identity, blended confidence, and silent repair. It ensures final prose cannot outrun persisted evidence.
