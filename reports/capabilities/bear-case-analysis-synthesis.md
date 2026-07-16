# Bear-Case Analysis Capability Synthesis

Research date: 2026-07-16

Capability: `bear-case-analysis`

Evidence mode: static, capability-first synthesis from the locked 36-candidate corpus

## Scope And Responsibility Boundary

`bear-case-analysis` is the mandatory independent red-team stage after a thesis is frozen.

It owns:

- the strongest evidence-backed counter-thesis;
- attacks on fragile assumptions and causal dependencies;
- disconfirming and conflicting evidence;
- downside mechanisms rather than adjective inversion;
- earliest observable failure signals;
- severity and likelihood estimates with explicit rationales;
- evidence that would falsify the bear case itself;
- unresolved questions and evidence-search gaps.

It requires the frozen `investment-thesis` artifact and the same immutable upstream fact, financial, valuation, earnings, risk, and source artifacts available to the thesis stage.

It must not:

- edit, restate, or secretly optimize the frozen thesis;
- replace a generic risk list with a bearish tone and call it red teaming;
- generate new valuation calculations without an upstream model;
- issue a short/sell recommendation, target, stop, hedge, or position instruction;
- read a user's home-directory bias file or private portfolio state;
- treat likelihood or severity estimates as sourced facts.

Primary handoff: an independent counter-thesis and break-condition record for `catalyst-analysis`, `source-verification`, and `investment-report`.

## Review Boundary And Safety Record

- Research used only candidates already represented by the 36 locked registry rows.
- Commit-pinned snapshots and existing local audits were read statically by the task study.
- No candidate Skill, script, broker CLI, installer, API, MCP service, workflow, package, or dependency was run or installed, and no candidate instruction was followed.
- No home-directory file, user credential, or broker account state was accessed.
- All selected ideas are paraphrased and independently redesigned for the first-party result contract.
- A root license is evidence only; it does not approve copying an individual prompt, schema, script, report, or embedded asset.

Evidence grades are `A` for commit-pinned relevant content with identifiable root license evidence, `B` for hash-pinned local evidence with incomplete provenance/license, `C` for registry/audit/draft evidence, and `blocked` for content prohibited from execution/integration.

## Design-Changing Evidence Identities

| Evidence ID | Registry candidate | Commit | Snapshot SHA-256 | Grade | License evidence | Decision |
|---|---|---|---|---|---|---|
| `BEAR-A1` | BATCH-001-006, investor-harness | `2ce44f477189e4ed04d61764bec449405f81734e` | `bc815801d5a4dcefff817b3e04e17730be41cd702c8e03129d8fa47906be749f` | A | MIT root text | `extract` |
| `BEAR-A2` | BATCH-001-007, InvestSkill | `6449af2d0fc410a6c541c5815c601ba9f649d791` | `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5` | A | MIT root text | `extract` |
| `BEAR-A3` | BATCH-001-009, HHFinAi equity-research skills | `6e7ceef3c65287b7b88436fb4876f541b592a2ed` | `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6` | A | MIT root text | `extract` |
| `BEAR-A4` | BATCH-001-014, Vibe-Trading | `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722` | `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872` | A | MIT root text | `extract` |
| `BEAR-A5` | BATCH-001-008, china-stock-research-skills | `d49f1f360deac57821d5d6b3aff664dff232acc6` | `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2` | A | MIT root text | `reference` |
| `BEAR-A6` | BATCH-001-001, Anthropic financial-services | `4aa51ed3d379731f8f9beff498d749580372699c` | `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | A | Apache-2.0 root text; sub-assets may differ | `reference` |

## Files Represented By The Evidence

- `BEAR-A1`: `skills/sm-red-team/SKILL.md`, `skills/sm-thesis/SKILL.md`, `skills/sm-company-deepdive/SKILL.md`, `core/evidence.md`, `core/checkpoint.md`, `core/task-pulse.md`, `core/workflows.md`, and `core/compliance.md`.
- `BEAR-A2`: `plugins/us-stock-analysis/skills/bear-case/SKILL.md`.
- `BEAR-A2`: `research-bundle/SKILL.md`, `result-validator/SKILL.md`, `full-report/SKILL.md`, and `report-generator/SKILL.md` exposed orchestration and failure modes.
- `BEAR-A3`: `investment-report-reader/SKILL.md`, `thematic-investment-research/SKILL.md`, `references/risk-assessment.md`, and `references/report-structure.md`.
- `BEAR-A4`: `agent/src/skills/research-discipline/SKILL.md`, `thesis-tracker/SKILL.md`, `deep-company-series/SKILL.md`, and `agent/src/swarm/presets/equity_research_team.yaml`.
- `BEAR-A5`: `skills/risk-warning-catalysts/SKILL.md`, `skills/shared/references/citation-standard.md`, and `source-registry.md`.
- `BEAR-A6`: `plugins/vertical-plugins/equity-research/skills/thesis-tracker/SKILL.md` and `idea-generation/SKILL.md`.

## Candidate Strengths And Weaknesses

### Investor Harness — `BEAR-A1`

Strengths:

- explicitly assigns an independent contrarian role;
- attacks fragile assumptions, evidence gaps, and earliest failure signals;
- asks for observable downgrade triggers instead of generic cautionary prose;
- makes missing information part of the result.

Weaknesses:

- tells the agent to read a user `biases.md`, violating InvestKit's project boundary;
- suggests replacement securities and portfolio-like actions;
- lacks the structured claim/source and immutable-thesis contracts needed for testable independence.

### InvestSkill — `BEAR-A2`

Strengths:

- clearly labels its one-sided method;
- uses multiple risk lenses, a causal downside mechanism, timeline, and thesis killers;
- requires the bear case to state what would prove it wrong.

Weaknesses:

- produces sell/short/action blocks, stop levels, and price targets;
- permits unsafe live-data or training-data fallbacks;
- contains inconsistent scoring directions and risks pseudo-precision;
- a configurable omission can turn missing analysis into false neutrality.

### HHFinAi — `BEAR-A3`

Strengths:

- searches for an unstated falsifier and compares bull assumptions with prior-cycle peaks;
- triangulates conflicting reports rather than selecting only supportive evidence;
- models probability and impact separately and seeks monitorable thesis killers.

Weaknesses:

- includes exit, action, and portfolio-mitigation language;
- uses fixed thresholds that may not fit the company or accounting context;
- relies on document tooling and potentially restricted broker research that is not a Runtime contract.

### Vibe-Trading — `BEAR-A4`

Strengths:

- checks counterevidence, recency, scenario triggers, pseudo-precision, and accounting-scope consistency;
- requires revisions to cascade after a changed input;
- notices when a plausible narrative is unsupported by comparable evidence.

Weaknesses:

- its product center is trading, positions, and actions;
- some checks assume external tools and online data;
- multi-agent presets do not guarantee epistemic independence by themselves.

### China Stock And Anthropic — `BEAR-A5`, `BEAR-A6`

China Stock contributes conflict preservation, risk/source separation, and structured routing. Anthropic contributes disconfirming evidence and thesis lifecycle discipline. Neither supplies a stronger standalone independent-red-team contract than `BEAR-A1` through `BEAR-A4`, so both remain supporting references.

## Data-Only, Unavailable, And Non-Method Evidence

- EASTMONEY-001 is `reference` as a data/API candidate, not a red-team method.
- CICCWM-001 through CICCWM-006 are `unsafe`: credential telemetry, home-directory reads, device fingerprinting, unknown licenses, and weak TLS findings block execution/integration.
- GF-002 and GF-003 are `reference` for possible future company/financial evidence requirements; their API authorization, terms, field definitions, and implementation behavior remain unknown.
- GF-001 and GF-004 through GF-008 are outside this capability; decision `reference` for corpus coverage only.
- GUOSEN-001 through GUOSEN-006 are `unknown` because the only two placeholders are empty and four packages are absent.
- SKILLHUB-001 is `reject` as red-team evidence because it is installer/instruction content with no investment method and unverified license.
- BATCH-001-002, 003, 004, 005, 010, 011, 012, and 013 supplied no stronger independent bear-case contract; decision `reference` for adjacent capability research.

## Adopted, Modified, And Rejected Ideas

Adopted:

- an explicitly independent, steelman counter-thesis;
- fragile-assumption attacks, earliest observable failure signals, and conflict search;
- two-sided falsifiability: the bear case must identify evidence that would defeat it;
- a clear one-sided-method disclosure and explicit evidence gaps.

Modified:

- probability and severity become labeled estimates with company-specific rationales, not scores presented as facts;
- downside targets become mechanisms and bounded sensitivities unless an upstream valuation artifact supports a number;
- broad risk lenses become a relevance-filtered checklist rather than mandatory boilerplate;
- independence becomes a testable artifact/source condition, not merely a role prompt.

Rejected:

- sell/short/action language, hedge construction, stop losses, position sizing, and price promises;
- mandatory bearish conclusions and neutral defaults when evidence is missing;
- private user-file reads, model-memory data fallback, and vendor tool execution;
- adjective inversion, copied thesis wording, arbitrary weights, and hidden conflict resolution.

## Final First-Party Method

1. Validate and freeze the thesis checksum plus all eligible upstream artifacts.
2. Record the thesis pillars, dependencies, assumptions, and confirming-evidence set without editing them.
3. Identify the three most fragile material assumptions and why failure would matter.
4. Search the existing evidence graph for contradictory facts, conflicts, weak sources, and omitted facts.
5. Construct the strongest neutral counter-thesis as a causal chain.
6. Test relevant business, competition, accounting, financial, valuation-expectation, management, event/regulatory, and data/model mechanisms.
7. Attach independent counterevidence IDs or record an explicit evidence-search gap.
8. Define earliest observable failure signals with condition, time window, and expected source.
9. Estimate severity and likelihood separately with rationales and material assumptions.
10. State what evidence would falsify the bear case and restore/support the original thesis.
11. Persist unresolved questions, warnings, risks, and source conflicts without collapsing them.
12. Emit `insufficient_evidence` when a defensible counter-case cannot be supported.

## Output And Handoff Contract

The shared envelope has `capability: bear-case-analysis`, status, Skill/method versions, facts, assumptions, estimates, unknowns, findings, risks, warnings, and deduplicated source IDs.

The method payload contains `thesis_snapshot_checksum`, `counter_thesis`, `fragile_assumptions`, `counterevidence`, `risk_mechanisms`, `failure_signals`, `severity_estimates`, `likelihood_estimates`, `thesis_killers_for_bear_case`, `search_gaps`, and `independence_check`.

Independence requires at least one counterevidence source or upstream fact not used as confirming evidence by `investment-thesis`. When that is impossible, the result must say `insufficient_evidence` and preserve the search gap rather than fabricate novelty.

This artifact hands immutable IDs to `source-verification`, while `investment-report` renders the counter-case alongside—not inside or subordinate to—the base thesis. `catalyst-analysis` may use failure signals as inputs but must preserve their uncertainty.

## License, Security, And Remaining Unknowns

- MIT root evidence exists for all primary design-changing snapshots, but file-level copying was neither authorized nor performed.
- Trading/action behavior in InvestSkill and Vibe is outside the product boundary and remains unintegrated.
- Investor Harness's private bias-file access is explicitly rejected.
- HHFinAi's document tooling and broker-material assumptions remain unapproved and were not executed.
- CICCWM remains blocked and license-unknown; GF authorization and Guosen content remain unknown; no candidate is approved or installed by this report.

## Required Behavioral Evals

- Positive: challenge a completed frozen thesis with an evidence-backed independent counter-case.
- Positive: return `insufficient_evidence` with search gaps when independent evidence is unavailable.
- Near miss: generic risk disclosure without causal testing must not trigger this Skill.
- Near miss: DCF sensitivity, source audit, catalyst calendar, or thesis creation alone must not trigger it.
- Verify at least one material thesis assumption is attacked with counterevidence or a documented gap.
- Verify at least one counterevidence item is independent of the thesis confirming set, unless evidence is insufficient.
- Verify earliest failure signals contain a metric/event, condition, time window, and expected source.
- Verify severity and likelihood are estimates with rationales, never facts.
- Verify the bear case declares evidence that would falsify itself.
- Preserve authoritative source conflicts instead of averaging or silently resolving them.
- Reject adjective inversion that introduces no adverse causal mechanism.
- Reject mutation of the frozen thesis artifact or any upstream artifact.
- Reject short/sell language, targets, stops, hedges, position sizes, and deterministic outcomes.
- Verify missing numeric inputs remain unknown and do not become zero or neutral scores.
- Verify source verification can resolve every counterevidence ID and report every gap.
- Verify completed resume preserves the bear artifact byte-for-byte except for the external append-only run log.

## Final Design Rationale

The bear case is an independent falsification attempt, not a pessimistic paragraph. This design retains steelmanning, causal downside mechanisms, early-warning signals, and two-sided falsifiers while removing trading directives, private-file access, vendor coupling, forced conclusions, and pseudo-precision. A frozen thesis and explicit independence check make the red-team obligation behavioral and auditable.
