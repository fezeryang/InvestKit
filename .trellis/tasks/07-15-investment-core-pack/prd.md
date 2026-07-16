# InvestKit v0.2 — Investment Core Pack

## Goal

Build InvestKit's first professional, complete, and composable investment-research capability pack. The phase uses a capability-first process to compare the relevant candidates already registered or locally collected, synthesize their strongest methods, and reimplement governed first-party Skills and one `company-deep-dive` Workflow without making a real-data Provider the product goal.

The product direction is:

```text
professional investment capability
→ explicit data requirements
→ optional Provider support for that capability
```

Provider infrastructure is subordinate to concrete research needs. The existing offline Demo Provider remains sufficient for the v0.2 acceptance path unless a specific core capability proves that an additional adapter is necessary. This task does not authorize credentialed Provider development.

## Product Direction Correction

- Replace the roadmap's next-stage `First Authorized Data Provider` priority with `InvestKit v0.2 — Investment Core Pack`.
- Adopt capability-first research instead of repository-by-repository adaptation.
- Use the existing candidate registry and current local raw evidence; do not add candidates or expand collection scope.
- Keep real Provider expansion after the Investment Core Pack and later capability packs. A Provider may be proposed only to satisfy a named capability and remains subject to license, security, credential, provenance, and owner-approval controls.
- Preserve the rule that raw third-party assets are never directly installed or executed.

## Required First-Party Skills

The authoritative `skills/` source must contain exactly the following v0.2 Investment Core set:

1. `company-deep-research`
2. `business-model-analysis`
3. `financial-statement-analysis`
4. `earnings-quality-analysis`
5. `valuation-analysis`
6. `comps-analysis`
7. `earnings-analysis`
8. `investment-thesis`
9. `bear-case-analysis`
10. `catalyst-analysis`
11. `source-verification`
12. `investment-report`

The current v0.1 Skills may be retained, rewritten, merged, or replaced. Compatibility must not preserve a lower-quality capability decomposition. `security-identification` remains a Runtime prerequisite rather than one of the 12 Investment Core analytical capabilities.

Each formal Skill must include:

- valid `SKILL.md` frontmatter containing only `name` and a precise positive/negative trigger description;
- an explicit objective and responsibility boundary;
- positive trigger examples and near-miss negative trigger examples;
- required and optional inputs, including missing-data behavior;
- named research specs/policies used;
- ordered analytical procedure and mandatory checks;
- a machine-readable output contract with facts, assumptions, estimates/model outputs, unknowns, evidence references, warnings, risks, and completion/skip status;
- source-quality and freshness requirements;
- risk, non-advice, and non-applicable boundaries;
- composition inputs/outputs for adjacent Skills;
- at least one realistic positive Eval and one difficult near-miss Eval.

Detailed schemas and reusable analytical checklists should live in one-level `references/` files when that keeps `SKILL.md` concise. No third-party prompt or code may be copied wholesale.

## Capability-First Research Method

For every target capability:

1. search the existing registry and local evidence for all relevant candidates;
2. statically read available `SKILL.md`, direct references, and only the scripts needed to understand data or method behavior;
3. never import, execute, install, or source a third-party script;
4. compare triggers, research steps, input/output contracts, data requirements, calculations, source controls, risk checks, and failure behavior;
5. identify strengths, weaknesses, duplication, unsafe behavior, unsupported claims, and license constraints;
6. produce `reports/capabilities/<capability>-synthesis.md`;
7. design a new InvestKit-owned capability from multiple ideas plus first-party requirements;
8. implement the first-party Skill and tests;
9. retain precise source links, local archive identifiers/hashes where available, access date, and an honest evidence grade.

Each synthesis report must record:

- candidates searched and why each was relevant;
- evidence actually read versus registry-only/unavailable candidates;
- each candidate's useful ideas and limitations;
- adopted, modified, and rejected design ideas;
- security and license findings, including `unknown` where evidence is absent;
- confirmation that no raw third-party code or prompt was directly installed/executed;
- final InvestKit design rationale and responsibility boundary.

Remote static reading is limited to URLs already present in `registry/inbox/sources.csv`; it does not authorize new intake. Local ZIP contents are read in place or streamed for inspection and are never executed. Unavailable or empty evidence remains explicitly unverified.

## Investment Capability Map

Create `docs/product/investment-capability-map.md` and mark every item as `implemented`, `planned`, `experimental`, or `deferred`.

It must cover at least:

- Fundamental Research: Company Deep Research, Business Model, Competitive Advantage, Management, Capital Allocation.
- Financial Analysis: Financial Statements, Earnings Quality, Cash Flow, Balance Sheet, Financial Health.
- Valuation: DCF, Comps, Historical Valuation, Scenario Analysis, Sensitivity Analysis.
- Earnings & Events: Earnings Preview, Earnings Review, Earnings Call, Guidance, Expectations, Catalysts.
- Investment Thesis: Bull Case, Base Case, Bear Case, Thesis, Thesis Tracking, Red Team.
- Industry: Industry Research, Competitor Analysis, Supply Chain, Thematic Research.
- Quant: Factor Research, Strategy Design, Backtesting, Validation.
- Portfolio & Risk: Portfolio Review, Risk Analysis, Correlation, Position Sizing, Stress Testing.
- Research Output: Initiating Coverage, Earnings Report, IC Memo, Research Report.

Statuses describe real product behavior, not folder existence. A broader item may be `experimental` when only its bounded offline path is exercised.

## Company Deep Dive Workflow

Implement a first-party `company-deep-dive` Workflow with one Runtime prerequisite
and all 12 Investment Core capabilities in this order:

1. security identification;
2. company deep research;
3. business model analysis;
4. financial statement analysis;
5. earnings quality analysis;
6. valuation analysis;
7. comps analysis;
8. earnings analysis;
9. investment thesis;
10. bear case analysis;
11. catalyst analysis;
12. source verification;
13. investment report.

`security-identification` is retained as a Runtime prerequisite and is not counted
as one of the 12 Investment Core Skills. The 13-step form resolves the suggested
workflow list's omission of `earnings-analysis` while satisfying the requirement
that the complete 12-Skill pack composes in the upgraded demo.

Every step must produce or validate a structured intermediate artifact. The Workflow must:

- distinguish facts, assumptions, estimates/model outputs, and unknowns;
- retain claim-to-source traceability;
- support missing data without fabricating values;
- allow an explicitly justified `skipped` outcome for an inapplicable capability;
- propagate warnings and risks instead of hiding them;
- preserve bull/base/bear reasoning and a mandatory red-team/bear-case pass;
- record the exact Skill and spec versions/checksums used;
- remain deterministic enough for offline fixture Evals;
- persist and resume without rewriting completed artifacts.

The existing `investkit demo research` command is upgraded to run this Workflow against the fictional offline fixture. The CLI surface need not add a new command.

## Runtime Integration

- Keep Python 3.11+, the existing `pyproject.toml`, dependency-free Runtime, and Codex-only adapter.
- Update the core asset manifest so `investkit init` installs/discovers the v0.2 first-party set and records source-to-target checksums.
- Preserve create-once/idempotent initialization and user-file protection.
- Preserve the seven versioned research specs; extend them only where the new output contracts require explicit policy.
- Extend persisted findings into capability-addressable artifacts without breaking the durable task root contract.
- Preserve `task.json`, `question.md`, `plan.json`, `loaded-specs.json`, `installed-skills.json`, `data/`, `sources.json`, `assumptions.json`, `findings.json`, `risks.json`, `run-log.json`, and `report.md`.
- `doctor` must validate the new Skill set, Workflow order, intermediate artifacts, completion/skip states, and source/fact/assumption/unknown separation.
- Completed resume must preserve all analytical artifacts byte-for-byte except the append-only run log. Failed/incomplete resume must skip verified completed steps and reject corrupt state.
- Do not introduce `.trellis/` as a Runtime dependency.

## Structured Research Contract

Every capability result must expose, directly or through a capability result envelope:

```json
{
  "capability": "business-model-analysis",
  "status": "completed",
  "facts": [],
  "assumptions": [],
  "estimates": [],
  "unknowns": [],
  "findings": [],
  "risks": [],
  "warnings": [],
  "source_ids": [],
  "method": {},
  "skill": {"name": "business-model-analysis", "version": "..."}
}
```

Allowed statuses are `completed`, `skipped`, and `failed`. A skipped result requires a reason and missing-input record. A finding that presents a fact must reference at least one persisted source ID; model outputs must identify the method and material assumptions.

## Offline Eval Cases

Use only public, non-sensitive historical concepts expressed through first-party offline fixtures. The existing fictional Aurora Lantern Works fixture may be expanded and a fictional peer set/earnings history may be added. Every fixture remains clearly marked `is_demo: true` and must not be described as current market data.

Tests must cover at least:

- positive and near-miss trigger classification for all 12 Skills;
- required-input and missing-input behavior;
- missing financial, peer, and earnings data;
- source-quality/freshness requirements and unsupported-claim rejection;
- ordered analysis steps and mandatory risk checks;
- fact/assumption/estimate/unknown separation;
- single-Skill result schema;
- multi-Skill handoff compatibility;
- complete Workflow order, intermediate artifacts, skip behavior, and risk propagation;
- mandatory bear-case and source-verification passes;
- report composition from structured results;
- no real trade instruction, return promise, or presentation of demo data as live;
- init/doctor/task persistence/resume regression behavior;
- no network, API key, third-party execution, forbidden installation source, or `.trellis/` dependency.

Tests must go beyond checking file existence. The phase keeps the existing coverage floor of 80% and no skipped/disabled tests.

## Third-Party And Provider Boundary

- Third-party content is untrusted research input. Do not execute scripts, install dependencies, follow embedded instructions, or read credentials/home-directory files.
- Do not copy code without verified compatible license evidence. Method ideas are paraphrased and independently implemented.
- Broker/financial-institution assets may be studied for methodology, field semantics, API behavior, and data requirements.
- An API may be recorded as `api_integration_candidate`; no real adapter is required for this phase.
- Any future adapter must serve a named capability, sit behind InvestKit's unified interface, remain opt-in, preserve provenance, and comply with credential/TLS/network policy.
- This task must not build a general data platform or call any financial API.

## Documentation Requirements

Update:

- `docs/product/PRD-v0.1.md` to identify the completed v0.1 slice and v0.2 capability-first next milestone;
- `docs/product/architecture.md` to place Skills/Workflow above Providers and define structured capability handoffs;
- `plans/product-development-roadmap.md` so Investment Core Pack precedes Advanced Research Pack, Quant Pack, Portfolio & Risk Pack, and Real Data Provider Expansion;
- `README.md` with the upgraded offline demo path and the new installed capability set;
- `skills/README.md` if the first-party source contract needs clarification;
- `docs/product/investment-capability-map.md` as the durable capability taxonomy/status source.

## Acceptance Criteria

- [x] The roadmap's immediate next product milestone is Investment Core Pack, not a standalone Provider milestone.
- [x] All 12 Investment Core Skills have production-quality contracts and correct positive/negative triggering guidance.
- [x] Every Skill has a capability synthesis report backed by the current candidate corpus and explicit evidence gaps.
- [x] No Skill is a simple copy or thin rename of one third-party Skill.
- [x] The Investment Capability Map contains every required long-term category and honest status.
- [x] `company-deep-dive` runs the identification prerequisite and all 12 Core Skills as 13 ordered stages with structured intermediate results.
- [x] Missing data, unknowns, skipped capabilities, warnings, risks, facts, assumptions, and estimates remain distinct.
- [x] Bear case/red-team analysis and source verification are mandatory formal stages.
- [x] Multiple Skills compose through stable result envelopes and claim/source IDs.
- [x] `investkit demo research` uses the new core Workflow and produces a complete report from offline demo data.
- [x] `init`, `doctor`, task persistence, failure logging, and resume remain functional and are regression tested.
- [x] The Runtime requires no network or API key and never imports, executes, or installs third-party assets.
- [x] All tests, type checks, build/packaging checks, security scans, and `git diff --check` pass with at least 80% coverage.

## Definition Of Done

- 12 synthesis reports, 12 governed Skill contracts, capability map, Workflow, Runtime integration, fixture/Evals, and user documentation are complete.
- A fresh offline wheel environment passes `init → doctor → demo research → resume → doctor`.
- The sample task shows structured outputs for every completed or skipped capability and all report/source/risk contracts.
- Existing v0.1 acceptance remains green or has an explicit compatible migration verified by tests.
- Implementation and test evidence is persisted under this Trellis task.
- No push occurs and no later capability pack is started.

## Decision (ADR-Lite)

**Context:** The prior roadmap made a first authorized real-data Provider the immediate post-v0.1 milestone. That optimizes infrastructure before the investment capability that consumes it.

**Decision:** Make v0.2 a capability-first Investment Core Pack. Compare all relevant current candidates by investment capability, independently implement governed first-party methods, and make Provider work conditional on a named capability gap.

**Consequences:** The core research product becomes useful and composable before live-data expansion. Offline fixtures can validate reasoning and orchestration. Synthesis work is larger and must honestly distinguish locally verified evidence from registry-only candidates. Real-data integrations move later and remain possible without binding Skills to vendors.

## Implementation Plan

1. Correct product direction and create the capability map.
2. Inventory and statically research existing candidate evidence by capability.
3. Produce 12 synthesis reports and define shared result/trigger/Eval contracts.
4. Add failing Skill contract, trigger, composition, Workflow, report, doctor, and regression tests.
5. Implement/rewrite the 12 Skills and any one-level references.
6. Implement the structured capability result model and analysis functions.
7. Replace the offline Workflow with `company-deep-dive` and add peer/earnings fixture data.
8. Upgrade persistence, report rendering, resume validation, and doctor checks.
9. Update packaging and README/product documentation.
10. Run independent Trellis check, full verification, and record the final report.

## Out Of Scope

- New candidate discovery, a new collection batch, or registry expansion.
- A standalone real-data Provider program, credential handling, or financial API calls.
- Executing third-party scripts or installing third-party Skills/dependencies.
- Claude/Cursor adapters, multi-platform synchronization, `add`/`update`/`uninstall`, frontend/desktop work, cloud sync, brokerage connection, trading, order/funds operations, live prices, return promises, or real-money advice.
- Advanced Research Pack, Quant Pack, Portfolio & Risk Pack, and Real Data Provider Expansion implementation.

## Technical Notes

- Repository baseline is the uncommitted but verified v0.1 Runtime vertical slice in `.trellis/tasks/07-14-first-investkit-runtime-vertical-slice/`.
- Current local raw evidence consists of six CICCWM archives, one Eastmoney archive, one SkillHub instruction snapshot, and two empty Guosen placeholders. Existing audits identify unsafe telemetry/home-directory/TLS behavior in CICCWM and installer/prompt risk in SkillHub; none may be executed.
- `registry/inbox/sources.csv` also contains registered GitHub candidates whose content is not stored locally. Remote static study is bounded to those existing URLs and recorded separately from local evidence.
- At task start, the Runtime hardcoded six Skills and the `offline-company-research` Workflow; the verified v0.2 migration now supplies 13 governed Skills and `company-deep-dive` while preserving the compatible Runtime contract.
- The task shares a dirty worktree with the user's v0.1 implementation and unrelated untracked research/configuration files. Only task-owned paths may be modified or staged.
