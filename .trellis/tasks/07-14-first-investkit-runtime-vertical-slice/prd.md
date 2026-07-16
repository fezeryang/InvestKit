# Implement first InvestKit Runtime vertical slice

## Goal

Implement a Codex-first, fully offline InvestKit Agent Harness vertical slice. A user must be able to initialize an InvestKit project, install and discover governed first-party Skills, load versioned research standards, create and resume a structured research task, run a fictional-company research demo, produce durable artifacts and a non-trading Markdown report, and diagnose the local environment without network access, API keys, third-party execution, or `.trellis/` runtime dependencies.

## Owner-approved scope

The requirements in the 2026-07-13/14 owner instruction are complete and approved. There are no open product questions for this task. When this PRD and the product roadmap differ, this PRD controls M1 implementation and the difference is recorded under “Roadmap differences.”

## User journeys

1. As a Codex user in an empty project, I run `investkit init` and receive a usable, repeatable InvestKit project without losing existing files.
2. As a researcher, I run `investkit demo research` and receive a complete offline research task and report based only on clearly fictional demo data.
3. As a researcher in a later process, I run `investkit demo research --resume <task-id>` and recover the saved task without overwriting completed artifacts.
4. As an operator, I run `investkit doctor` and receive explicit `PASS`, `WARN`, and `FAIL` diagnostics plus a nonzero exit code for critical failures.

## Required commands

- `investkit init`
- `investkit doctor`
- `investkit demo research`
- `investkit demo research --resume <task-id>`

`investkit status` is optional and is not required. `add`, `update`, and `uninstall` must not be implemented as successful placeholders; help text may identify them as future lifecycle capabilities only.

## Runtime and packaging requirements

- Support exactly one host platform in this slice: `codex`.
- Preserve an adapter interface that can accept future platforms without creating empty Claude or Cursor adapters.
- Use Python 3.11+ with a `pyproject.toml` console entry point and no runtime third-party dependencies.
- Keep runtime code under `src/investkit/`; tests must not import `.trellis/`.
- Provide a local, offline installation path documented from zero.
- Runtime operations stay within the selected project root and the packaged/repository first-party source root.
- No network, API key, brokerage, transaction, order, funds-transfer, backtest, live-price, desktop, or frontend functionality.

## Authoritative product source

The following repository directories are first-party source boundaries:

- `skills/`
- `agents/`
- `workflows/`
- `specs/`
- `packages/`
- `workspace-template/`

The Codex target is `.agents/skills/`. It is generated installation state, never authoritative source. `third_party/raw/` and `adapted/skills/` must never be read as install sources, copied to the target, imported, or executed.

## `investkit init`

`init` must:

1. use the current working directory as project root;
2. create versioned machine-readable project configuration;
3. create a durable `workspace/research/` hierarchy;
4. copy or map only the six approved first-party core Skills from `skills/` to `.agents/skills/`;
5. discover and checksum first-party research specs;
6. create a real Codex adapter configuration;
7. create an installation manifest with source-to-target mappings and hashes;
8. never overwrite an existing user file;
9. be idempotent;
10. emit explicit `CREATE`, `SKIP`, and `WARN` results.

The configuration/manifest records at least InvestKit version, host platform, initialization time, source root/directories, installation target, installed Skills, source-to-target mapping, spec versions/checksums, and workspace path. It stores no credential or secret.

## Codex adapter

The single implemented adapter must:

- detect/describe the Codex project environment;
- select `.agents/skills/` as the target;
- install only the approved first-party core Skills;
- write only InvestKit-owned adapter configuration while preserving existing files;
- record ownership and source hashes;
- expose data needed by `doctor`.

## Research standards

Create and load these first-party standards:

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`
- `specs/financial-data-policy.md`
- `specs/valuation-policy.md`
- `specs/risk-policy.md`
- `specs/report-policy.md`

Each standard has an explicit version. Every research run writes `loaded-specs.json` with deterministic path, version, and SHA-256 checksum.

## First-party core Skills

Implement under canonical `skills/`:

- `security-identification`
- `company-research`
- `financial-statement-analysis`
- `valuation-analysis`
- `source-verification`
- `investment-report-writing`

Every Skill includes `SKILL.md` with trigger guidance, inputs, used specs, output contract, source requirements, risk boundaries, non-applicable cases, and a minimal test scenario. Automated tests verify all six contracts. Third-party text/code must not be copied.

## Offline Demo Provider

Implement an InvestKit-owned Provider interface and one offline provider with a clearly fictional listed security. It must provide:

- `identify_security`
- `get_security_profile`
- `get_financial_statements`
- `get_price_history`
- `get_valuation_inputs`
- `get_source_metadata`

Every response includes `as_of_date`, `currency`, `market`, `source`, a fixture version or retrieval timestamp, `is_demo: true`, and warnings. Missing values are explicit and handled. No report may describe fixture data as real-time data.

## Structured research task

Each new demo creates `workspace/research/<task-id>/` with at least:

```text
task.json
question.md
plan.json
loaded-specs.json
installed-skills.json
data/
sources.json
assumptions.json
findings.json
risks.json
run-log.json
report.md
```

The persisted state contains a unique ID, timestamps, current/final status, input question, data references, Skills, specs, intermediate results, warnings, final report, and completed/failed outcome. Valid transitions include `created → running → completed` and `created|running → failed`; failures retain a run log.

## Resume contract

`investkit demo research --resume <task-id>` must:

- validate the task ID and remain inside `workspace/research/`;
- read existing task, data, installed Skills, loaded specs, and step state;
- reject corrupt or materially incomplete tasks with an actionable error;
- skip already completed steps and preserve completed artifacts;
- append a resume event to the run log;
- complete only missing resumable steps, or report a completed task without rewriting its report/data.

No cloud or cross-device synchronization is included.

## Offline research workflow

Persist and execute this ordered flow:

1. identify the demo security;
2. load its profile;
3. load financial data;
4. perform fundamental analysis;
5. perform financial-statement analysis;
6. perform a basic valuation;
7. verify sources;
8. collect risks and unknowns;
9. generate a Markdown report;
10. persist all task artifacts.

The report includes: research subject, demo-data declaration, data date, executive summary, company overview, financial analysis, earnings quality, cash-flow and balance-sheet analysis, basic valuation, positive evidence, negative evidence, primary risks, assumptions, unknowns/to-verify, data sources, used Skills, loaded specs, generation time, and research boundary. It contains no real buy/sell instruction or deterministic-return promise.

## `investkit doctor`

Doctor must report `PASS`, `WARN`, or `FAIL` for:

- InvestKit version;
- host platform;
- project configuration;
- workspace existence and writability;
- first-party Skill source;
- Codex installation target;
- source-to-target mappings and hashes;
- required specs;
- required workflow;
- Demo Provider behavior;
- fixture completeness;
- forbidden/unapproved third-party installation evidence;
- likely sensitive information in InvestKit-owned config/task state;
- corrupt task records.

Any critical `FAIL` produces a nonzero exit code. Warnings alone do not.

## Security requirements

- Never read outside the selected project and first-party source roots.
- Never execute or import third-party scripts/assets.
- Never require or initiate network access.
- Never require an API key.
- Never depend on `.trellis/` at runtime.
- Never install from `third_party/raw/` or `adapted/skills/`.
- Validate task IDs and all filesystem destinations against path traversal.
- Preserve existing files; conflicts warn/fail rather than overwrite.
- Scan only InvestKit-owned state for common secret patterns; do not crawl unrelated user files.
- Do not weaken TLS, invoke shell commands, add telemetry, or expose credentials.

## Test requirements

Tests are written before implementation and cover:

### Init

- empty-directory initialization;
- repeat initialization;
- existing-file preservation;
- correct source-to-target mapping;
- exclusion of third-party and adapted Skills.

### Doctor

- healthy environment;
- missing Skill;
- missing spec;
- corrupt mapping;
- unwritable workspace;
- unexpected third-party installation marker;
- secret detection;
- corrupt task detection.

### Demo Provider

- fully offline behavior;
- interface/data-model validity;
- demo markers and warnings;
- date/currency/market/source completeness;
- missing-value handling.

### Research task and report

- task creation and unique IDs;
- state transitions and full workflow;
- failure recording;
- completed-task resume;
- corrupt/incomplete-task resume failure;
- preservation of completed artifacts;
- required report sections, sources, assumptions, risks, unknowns, and demo declaration;
- absence of real trading instructions and guaranteed-return language.

### Runtime boundary

- no project-external reads in normal operations;
- no network calls/API keys;
- no `.trellis/` imports or path dependencies;
- no third-party/adapted installation.

Achieve at least 80% statement coverage for runtime code with no skipped tests. Use standard-library `unittest`; Coverage.py may measure coverage in development but is not a runtime dependency.

## Acceptance commands

From a clean temporary project after local installation:

```bash
investkit init
investkit doctor
investkit demo research
investkit demo research --resume <task-id>
```

The commands must work offline and without API keys. README must document the exact zero-to-demo flow.

## Roadmap differences

- The roadmap's M1 says “one first-party core Skill”; this task requires six concrete core Skills.
- The roadmap allows any one reference adapter; this task fixes it to Codex.
- The roadmap's doctor contract is narrower; this task adds Provider/fixture, third-party-install, secret, corrupt-task, mapping, and writability checks.
- The roadmap describes restoration generically; this task requires the concrete `--resume <task-id>` interface.
- Target-product `add`/`update` lifecycle commands remain future work and must not become placeholders in M1.
- M2 authorized Provider integration remains a later milestone and is not pulled into this offline task.

These differences narrow or strengthen the first vertical slice and do not authorize additional platforms, live data, or third-party execution.

## Technical approach

- Python 3.11+ standard library with `src/` layout and `pyproject.toml` console script.
- Domain modules for configuration, filesystem safety, asset discovery/checksums, platform adapters, demo provider, task persistence, workflow/report generation, doctor, and CLI.
- JSON for machine-readable state and Markdown for questions/reports.
- Atomic writes for InvestKit-owned mutable files; copy-once semantics for user-visible installation artifacts.
- A manifest is the single source of installed-file ownership and source-to-target lineage.
- Pure deterministic analysis functions over fixture data; no model/API call is required.

## Decision (ADR-lite)

**Context:** The repository has no product runtime or package manager. Its only executable first-party tooling is Python-based Trellis, but `.trellis/` cannot be a Runtime dependency. The slice must install and run offline with minimal supply-chain surface.

**Decision:** Implement an independent Python 3.11+ package using only the standard library at runtime, setuptools packaging, a Codex adapter, JSON/Markdown persistence, and repository-owned asset roots. Test with `unittest` and measure with Coverage.py when available.

**Consequences:** The slice is easy to run offline and audit. Local editable installation is the primary documented developer path. Future packaged releases may add a build-time asset bundling step without changing the runtime contracts. No speculative multi-platform adapter or live Provider is created now.

## Implementation plan

1. Write contract and safety tests and demonstrate the initial red state.
2. Add package/CLI/configuration models and safe filesystem helpers.
3. Add the Codex adapter and idempotent `init` with manifest lineage.
4. Add versioned specs, six first-party Skills, the workflow definition, workspace template, and fictional fixture.
5. Add the offline Provider and deterministic analysis/report functions.
6. Add task persistence, lifecycle, failure recording, and resume.
7. Add doctor diagnostics and exit semantics.
8. Run focused tests, full tests, coverage, packaging/install, and end-to-end commands in fresh temporary projects.
9. Update README and write implementation/test reports.
10. Run Trellis check/spec-review, leave changes unpushed, and provide commit grouping recommendations.

## Definition of done

- All thirteen owner completion conditions are met.
- All tests pass with at least 80% runtime statement coverage.
- The four acceptance commands work in a fresh temporary project.
- A sample task path and artifacts are preserved for reporting without committing generated user state.
- `git diff --check` passes.
- No forbidden third-party, registry, Batch 001, report-analysis, `.claude/`, or `.cursor/` content is changed by implementation.
- No push, live Provider task, or multi-platform task is started.

## Out of scope

- Claude and Cursor adapters or multi-platform synchronization.
- Online/credentialed financial Providers and real market data.
- Third-party Skill installation, Batch 001 review, or raw asset execution.
- Brokerage connectivity, orders, funds transfer, trading automation, or return promises.
- Backtesting, quant packages, frontend/desktop applications, cloud sync.
- Functional `add`, `update`, or `uninstall` commands.

## Technical references

- `AGENTS.md`
- `docs/product/PRD-v0.1.md`
- `docs/product/architecture.md`
- `plans/product-development-roadmap.md`
- `docs/security/security-policy.md`
- `docs/skill-research/SOP.md`
- `docs/skill-research/taxonomy.md`
- `docs/skill-research/acceptance-criteria.md`
- `.trellis/spec/backend/index.md`
- `.trellis/spec/guides/cross-layer-thinking-guide.md`
- `research/repository-and-scope.md`
