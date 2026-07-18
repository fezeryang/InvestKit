# Dynamic Investment Research Harness

## Goal

Turn InvestKit from a fixed investment-research application into an installable,
Trellis-like Investment Research Agent Harness. The Harness must inventory every
provided asset, expose its honest operational state, dynamically select safe
capabilities for a research request, persist and resume the resulting task graph,
and support a symbol-first China A-share research path. `603868.SH` (Shanghai
Flyco Electrical Appliance Co., Ltd. / 飞科电器) is the first pinned acceptance case.

## What I already know

- The user explicitly chose this as the only product mainline and asked to start.
- The repository has 13 governed first-party research Skills, one governed
  first-party SSE Provider, and 36 external candidates in Batch 001, for 50
  catalogued assets in the current release scope.
- The current v0.3 worktree already provides reusable initialization, Codex
  projection, safe file boundaries, durable tasks, resume, Doctor, a normalized
  FileProvider, 13 research methods, and deterministic reports.
- The current workflow is fixed to 13 stages and cannot discover, diagnose, or
  route the 36 external candidates at runtime.
- Eight Guangfa drafts describe one credentialed HTTP endpoint and require
  `GF_SKILLS_APIKEY`; none currently has executable adapter code, response schemas,
  retry/rate-limit policy, authorization approval, or live-test evidence.
- CICCWM raw archives have static security findings and unknown licenses; Guosen
  candidates are unavailable or failed acquisitions. They must be visible but not
  executed.
- The correctly configured baseline is green: `PYTHONPATH=src python3 -m pytest -q`
  passed 186 tests and 509 subtests on 2026-07-17.

## Requirements

### 1. Runtime asset catalog is the source of truth

- Define a versioned, machine-readable asset manifest contract.
- Represent all 14 first-party assets and all 36 Batch 001 candidates exactly once.
- Each asset records stable ID, name, type, capabilities, source, governance
  decision, approval, operational state, adapter kind, dependencies, credential
  requirements, network policy, supported platforms, and evidence/reason.
- Enforce exactly one taxonomy type and one required governance decision per asset.
- Keep governance decision separate from runtime state. For example, an adapted
  provider may be `credential_required`; an unsafe raw package is `blocked`.
- Candidate presence never implies installation, approval, network permission, or
  execution permission.

### 2. Discoverability and diagnostics

- Add CLI commands to list assets and inspect one asset without initializing a
  research project.
- Support deterministic filtering by type, capability, decision, and state.
- Add machine-readable JSON output in addition to concise human output.
- Doctor validates catalog schema, uniqueness, dependency references, adapter
  references, credential availability, network/approval gates, and forbidden raw
  execution paths without making network calls or exposing secret values.
- All 50 assets must have a visible, truthful state; no candidate may silently
  disappear because it is unsafe, unavailable, duplicated, or not yet reviewed.

### 3. Adapter and dependency model

- Define explicit adapter families for Skill, Tool/MCP, Data Provider, Quant
  Module, Agent, Workflow, Template, and Reference assets.
- Route by required capabilities and dependency graph instead of hard-coding one
  universal 13-stage workflow.
- Preserve deterministic plans, capability artifacts, source joins, failure state,
  resume validation, and report evidence boundaries.
- The existing 13-stage company deep dive remains an available workflow profile,
  not the Harness architecture itself.
- Block cycles, missing dependencies, incompatible states, and unsafe adapters
  before task creation or network access.

### 4. Guangfa provider integration

- Implement a first-party, reviewed adapter boundary for the Guangfa API drafts;
  do not import or execute third-party raw code.
- Read `GF_SKILLS_APIKEY` from the environment only. Never persist or print it.
- Default to no network. Live requests require an explicit network permission flag
  and a catalog state that is approved for execution.
- Enforce HTTPS host allowlisting, bounded request/response sizes, timeouts, strict
  JSON, redacted errors, and test seams with offline fixtures.
- Promote stock identity/F10 and valuation/financial comparison (`GF-002` and
  `GF-003`) first because they are required by the equity-research vertical slice.
- Represent the remaining Guangfa assets in the same catalog and adapter family;
  their unavailable or non-equity paths remain diagnosable until separately
  approved and tested.

### 5. Symbol-first research

- Add `investkit research --symbol <symbol> --question <question>` with normalized
  exchange-qualified symbols such as `603868.SH`.
- Resolve the security identity before analytical execution and reject ambiguous or
  unsupported symbols without creating a misleading completed task.
- Build a dynamic plan from the requested research intent, available capabilities,
  dependencies, credentials, approval, and network permission.
- When required data is unavailable, return an actionable blocked/partial result
  that names the missing capability and how to satisfy it; never fabricate data.
- With approved provider access and offline mocked responses, `603868.SH` resolves
  to 飞科电器, produces sourced company/financial/valuation evidence, runs the
  applicable analytical capabilities, and produces a Chinese research report.
- A live end-to-end check is conditional on the user supplying/authorizing a valid
  credential and network access; offline contract tests are mandatory regardless.

### 6. Platform projection and lifecycle boundary

- Keep the catalog and execution contracts platform-neutral.
- Preserve the existing Codex projection and define adapter metadata needed for
  Claude and Cursor projections without claiming those projections are complete.
- Package add/update/uninstall must operate only on approved first-party/adapted
  assets and must never install from `third_party/raw/` directly.
- Full multi-platform lifecycle may be delivered in follow-on child tasks, but the
  manifest and adapter contracts in this task must not preclude it.

## Acceptance Criteria

- [x] A strict loader validates a versioned catalog containing exactly 50 unique
      assets: 14 first-party and 36 Batch 001 candidates.
- [x] Every asset has exactly one allowed type, one allowed decision, one runtime
      state, evidence, and complete execution-gate metadata.
- [x] `investkit assets list` and `investkit assets show <id>` support human and
      JSON output plus deterministic filters.
- [x] Unsafe CICCWM candidates report `blocked`; unavailable Guosen candidates
      report `unavailable`; reference-only candidates report `reference_only`;
      Guangfa candidates report an honest approval/credential state.
- [x] Doctor detects duplicate IDs, invalid decisions/states, unresolved
      dependencies, adapter mismatches, absent credentials, and any raw-path
      execution mapping without reading or printing a secret.
- [x] A dependency-aware planner selects only compatible, approved assets and
      returns a structured reason for every selected, skipped, or blocked asset.
- [x] Existing demo/imported research and resume behavior remains green.
- [x] Guangfa requests are fully mocked in tests; no test calls the live service.
- [x] Network calls require explicit permission, an allowed host, and an available
      environment credential.
- [x] `research --symbol 603868.SH` has an offline acceptance test resolving 飞科电器
      and producing source-joined analytical artifacts and a Chinese report.
- [x] The same command without credentials/network permission fails or degrades
      honestly with an actionable diagnostic and creates no false completed report.
- [ ] Runtime statement coverage remains at least 80%; full tests, packaging
      acceptance, and security checks pass.

## Definition of Done

- Tests are written before each implementation slice and include unit, integration,
  CLI, security, resume, and package-delivery coverage.
- Runtime docs, architecture, capability map, and operator instructions describe
  real behavior and clearly distinguish offline, credential-required, blocked, and
  live-verified states.
- No secret, raw third-party executable, brokerage integration, trade instruction,
  funds transfer, or return promise is introduced.
- The final readiness report maps every acceptance criterion to repeatable evidence
  and states whether live `603868.SH` research was actually verified.

## Technical Approach

Use a manifest-driven control plane above the existing research runtime:

```text
catalog -> policy/state evaluation -> intent/capability planner
        -> dependency graph -> typed adapters -> durable task execution
        -> evidence verification -> report -> doctor/resume
```

The catalog is descriptive and safe to load offline. Adapters are first-party code
referenced by stable IDs, never code paths supplied by candidate data. Planning is
pure and deterministic; execution is a separate permission-gated phase. Existing
fixed workflows become catalogued workflow profiles composed from capabilities.

## Decision (ADR-lite)

**Context:** The previous architecture treated the 13 analytical Skills as the
product. That made external providers and candidate assets invisible to the Runtime
and made symbol-first research impossible.

**Decision:** Adopt a manifest-driven modular monolith for the first Harness release.
Use one versioned catalog, typed in-process adapter interfaces, a deterministic
dependency planner, and explicit execution gates. Defer a plugin process boundary
until multiple approved third-party implementations actually require isolation.

**Consequences:** This reuses the secure v0.3 foundation and is testable offline.
Cataloguing all assets does not make all of them executable: blocked, unavailable,
reference-only, and credential-required are first-class successful integration
states. A future plugin/MCP host can implement the same adapter contract.

## Out of Scope

- Executing or installing any package directly from `third_party/raw/`.
- Bypassing license, approval, credential, or network consent gates.
- Brokerage connections, order placement, trade execution, position sizing,
  transaction signing, or guaranteed returns.
- Claiming live Guangfa success without an authorized credential and recorded test.
- Completing every fund, ETF, macro, news, and quant workflow in the first equity
  vertical slice; those assets must be catalogued and diagnosable now, then become
  executable through separately verified adapters.
- A graphical interface in this task.

## Research References

- [`research/current-baseline-and-inventory.md`](research/current-baseline-and-inventory.md)
  — reusable runtime baseline and the original 49-asset scope.
- [`research/manifest-driven-harness-design.md`](research/manifest-driven-harness-design.md)
  — control-plane design, execution states, security gates, and delivery slices.

## Implementation Plan

1. Catalog contract, 50-entry inventory, loader, CLI list/show, and Doctor checks.
2. Adapter protocols, policy evaluation, dependency planner, and dynamic plan CLI.
3. Guangfa HTTP boundary with offline fixtures and explicit permission gates.
4. Symbol-first `603868.SH` research acceptance using mocked provider evidence.
5. Packaging, migration compatibility, docs, security audit, and readiness report.

## Multi-source analysis closure amendment (2026-07-17)

The owner approved continuing from provider connectivity to an actually useful
investment-analysis loop. The next release slice must not add isolated Skills.
It must normalize approved CICCWM evidence into the same immutable research
bundle consumed by the existing 13-stage workflow.

### Scope

- Acquire a bounded current quote and recent daily history for the target symbol.
- Acquire CICCWM income, balance-sheet, cash-flow, and indicator responses and
  merge dated fields without replacing stronger source-backed values silently.
- Acquire bounded hot-news and Dragon-Tiger evidence, retaining dates, titles,
  source identity, relevance limitations, and vendor provenance.
- Preserve SSE identity as authoritative and reject any conflicting CICCWM code or
  name before creating a research task.
- Feed normalized prices and dated event evidence through the provider-neutral
  bundle into valuation, earnings/catalyst, bear-case, source-verification, and
  report stages.
- Treat market-wide hot news as context, not a company catalyst, unless the item
  explicitly identifies the target security. Treat absence from a Dragon-Tiger
  list as an observation gap, not proof of no abnormal trading.
- Decode and render text exactly once so reports contain no raw HTML entities or
  duplicated inherited warning blocks.

### Acceptance

- Offline fixtures cover strict parsing, identity checks, finite numbers, bounded
  history/news, deduplication, nonzero vendor errors, and missing evidence.
- CLI planning requires `CICCWM_API_KEY` and explicit network permission before
  selecting CICCWM assets; SSE-only and SSE+Guangfa paths continue to work.
- A mocked `603868.SH` run persists CICCWM source records, recent price history,
  statement fields, and relevant event evidence in the nine-operation bundle.
- A live `603868.SH` run succeeds with SSE + Guangfa + CICCWM, produces all 13
  artifacts, and reports unsupported DCF/consensus claims as unknown.
- Full tests and packaging checks remain green; no vendor script is executed and
  no credential or raw response is persisted outside the governed bundle.

## Technical Notes

- Python 3.11+, standard-library-only runtime remains the default constraint.
- Repository root and packaged `share/investkit` must deliver identical governed
  catalog assets.
- Relevant existing modules: `assets.py`, `cli.py`, `doctor.py`, `providers/`,
  `capabilities/`, `research/tasks.py`, and `research/workflow.py`.
- Relevant governance sources: `registry/inbox/sources.csv` and
  `registry/governance/batch-001-candidate-governance.csv`.
- The user has already confirmed the product direction and instructed implementation
  to begin; there is no remaining preference question blocking the first slice.

## Decision analytics scope amendment (2026-07-17)

- Complete annual-report parsing is not a product-readiness requirement. Original
  disclosures are optional escalation evidence for footnotes, accounting changes,
  unusual items, related-party matters, conflicts, and material claim verification.
- The next implementation slice prioritizes point-in-time industry comparison,
  licensed broker consensus and revisions, driver-based earnings forecasts, and
  an auditable DCF/comps/historical-band valuation range.
- Later governed packs cover market regimes and industry rotation; technical and
  factor research; bias- and cost-aware backtesting; portfolio construction,
  asset allocation and risk budgets; multi-asset contracts; and reliable intraday
  monitoring and alerts.
- Every capability requires an explicit data contract and acceptance evidence.
  Folder presence, a vendor API response, or generated prose is not completion.
- Brokerage connectivity, order staging/submission, transaction signing, funds
  transfer, and automatic asset management are permanently prohibited.

### First decision-intelligence slice completed (2026-07-17)

- Extended the backward-compatible bundle schema/template with optional structured
  forecast metadata, broker consensus, and industry benchmark records.
- Added validation and persisted analysis for forecast vintage/method/periods,
  consensus observation time/contributor count/dispersion, industry definition/
  sample/vintage/percentile, and non-guaranteed DCF target-value ranges.
- Added direct guard tests plus an end-to-end imported workflow/report test.
- Preserved the authenticated v0.2 Skill ledger instead of weakening migration
  validation; new method detail lives in versioned Runtime/spec contracts.
- Verification: 238 tests passed, JSON assets parse, Python modules compile, and
  `git diff --check` passes.

### Target-only live usability amendment (2026-07-17)

- A user no longer needs to choose a peer before starting useful A-share research.
  When Guangfa is ready, symbol mode automatically fuses target F10, PE/PB,
  provider industry averages, and historical percentiles.
- `valuation-analysis` completes a bounded `market-relative-valuation` when DCF
  inputs are absent but positive target/industry multiples are available. It emits
  no target-value range and retains DCF and licensed consensus as explicit unknowns.
- `--peer` remains optional and analyst-selected; the Harness never invents a
  defensible peer or claims an undisclosed industry sample size.
- Live target-only `603868.SH` acceptance completed with SSE, Guangfa, and CICCWM,
  no credential leakage, and Doctor exit code zero.
- Final regression: 241 tests passed; Python compilation, JSON parsing,
  `git diff --check`, and configured-credential artifact scanning all passed.
