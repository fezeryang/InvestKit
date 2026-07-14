# InvestKit Product Architecture

Status: target product architecture; implementation has not started

## Product Contract

InvestKit is an installable investment-research AI Agent Harness for Codex, Claude, Cursor, and similar environments. It combines persistent investment standards, first-party Skills and Agents, data tools, deterministic research workflows, structured tasks, and a durable research workspace to turn general AI into a traceable, reproducible, and extensible investment-research workbench.

The architecture has two equally important layers and a shared persistence/security foundation.

| Layer | Responsibility | Examples |
|---|---|---|
| Investment capability | Perform professional investment-research work | Fundamentals, statements, valuation, peers, events, backtests, portfolios, risk, source verification, reports |
| Agent Harness framework | Install, select, orchestrate, persist, diagnose, update, and remove capabilities | CLI, adapters, standards, routing, workflows, tasks, context recovery, artifacts, package lifecycle |
| Foundation | Keep research safe, reproducible, and auditable | Workspace, lineage, permissions, run records, configuration, diagnostics |

## Source Architecture

These planned directories are the authoritative InvestKit product source:

```text
skills/              first-party Skill source
agents/              first-party specialized Agent source
workflows/           deterministic research workflow source
specs/               investment-research standards
packages/            optional capability packages
workspace-template/  initialized research workspace template
```

The repository currently contains only part of this target layout. A documented path is not a claim that its implementation already exists.

Platform paths are generated installation targets:

```text
.agents/skills/
.claude/skills/
.cursor/
<other platform-specific locations>
```

Authoritative released source flows one way through an end-user-initiated CLI adapter into a selected installation target. The project owner controls first-party release; the end user controls local installation. The CLI records source version and target mapping. Platform files are generated delivery artifacts and must not become the source of truth.

The repository's current `.claude/` and `.cursor/` files belong to Trellis development integration. Their presence does not mean InvestKit has been installed. Future InvestKit installation state must come from an InvestKit-owned installation manifest.

`third_party/raw/` contains untrusted evidence. `adapted/skills/` contains draft adaptation work. Neither is an installation source, and neither may be synchronized automatically into a platform target.

## Harness Components

### CLI and lifecycle

The InvestKit CLI owns explicit lifecycle operations:

- `investkit init`: initialize a workspace and selected platform adapter.
- `investkit doctor`: verify configuration, installed first-party capabilities, workspace structure, and recoverability.
- `investkit add <package>`: explicitly add an optional first-party capability package.
- `investkit update`: update governed first-party product assets while preserving user research state.
- Future uninstall behavior must remove generated installation artifacts without deleting user research by default.

### Platform adapters

Adapters translate authoritative InvestKit source into the conventions of Codex, Claude, Cursor, and other supported environments. An adapter may install Skills, Agents, commands, prompts, or configuration supported by that platform, but it must preserve common InvestKit semantics:

- the same investment standards;
- the same workflow identity;
- the same task and artifact references;
- explicit permissions and installation records;
- deterministic diagnostics.

The first vertical slice needs one adapter, not every platform.

### Investment standards

`specs/` is the source for persistent investment-research rules: evidence requirements, accounting definitions, valuation assumptions, source quality, risk language, counter-case review, and non-trading boundaries. The Harness loads only the standards relevant to the current task and workflow.

### Skills, Agents, and tools

- Skills package focused professional instructions and transformations.
- Agents own bounded research roles such as primary analyst, source verifier, or risk/counter-case reviewer.
- Tools provide data access or deterministic computation.
- Packages group optional capabilities without forcing every user to install them.

Routing chooses the smallest sufficient combination. A user should not need to select each component manually.

### Unified data interface and Provider Adapters

First-party Skills consume an InvestKit-owned data contract rather than a vendor-specific SDK:

```text
First-party InvestKit Skill
→ Unified InvestKit Data Interface
→ Provider Adapter
→ Authorized Broker or Financial API
```

The interface may expand through operations such as `identify_security`, `get_security_profile`, `get_price_history`, `get_financial_statements`, `get_valuation_metrics`, `get_company_filings`, `get_research_reports`, `get_market_news`, and `get_source_metadata`. Each Provider Adapter owns authentication, endpoints, pagination, rate limits, retries, error mapping, market-code conversion, normalization, and provenance for one approved source. Vendor identity, source time, retrieval time, currency, market, field definitions, and licensing limits survive normalization.

Official APIs, interface specifications, professional methods, and clearly licensed code found in authoritative third-party assets can inform a first-party Provider, Skill, Workflow, or Reference after static research and the required license, security, attribution, testing, and owner-release reviews. This is different from installing or directly executing an original third-party script, which remains prohibited by default. A small code reuse proposal needs explicit provenance and license records plus isolated tests; reimplementation is preferred.

Credentialed Providers are opt-in and read secrets only from environment variables or approved system credential storage. Credentials never enter source control, logs, reports, task artifacts, or unrelated Skills/Agents. Provider approval grants access only to declared research-data operations and never to trading, transaction signing, or funds transfer.

### Research workflows

`workflows/` defines ordered research behavior. A workflow declares required inputs, standards, Skills/Agents/tools, checkpoints, output contract, and persistence events. Workflows must record what ran and must fail visibly when required evidence is unavailable.

### Task lifecycle and context recovery

A research task is durable product state. At minimum it records:

- task identity, question, subject, status, and timestamps;
- selected workflow and capability versions;
- inputs, source references, and data lineage;
- assumptions, method choices, and unresolved questions;
- run events, warnings, and diagnostics;
- artifacts and their relationship to the task;
- compact recovery context for the next session.

Context recovery must reconstruct the research state from workspace files. It must not depend on hidden chat history.

### Research workspace

`workspace-template/` defines the user-owned persistent research space. The first implementation must choose and document an on-disk layout for configuration, tasks, sources, data, assumptions, runs, and artifacts. Update and uninstall operations must preserve this space unless the user explicitly requests deletion.

### Lineage and artifacts

Reports are only one artifact type. The workspace must retain enough evidence to reproduce how an artifact was produced:

- original input and source identity;
- normalized data and definitions;
- assumptions and transformations;
- workflow and capability versions;
- run timestamps and warnings;
- report or model outputs.

## End-to-End Runtime Flow

```text
User question
→ task creation
→ standard selection
→ Skill/Agent/tool routing
→ approved input acquisition or local read
→ source and data validation
→ research workflow
→ risk and counter-case review
→ sourced artifacts
→ persistence and context snapshot
→ later-session recovery
```

## Permissions And Safety

The Harness must declare and enforce permissions for network, filesystem, shell, credentials, and platform installation. Default research must remain inside the initialized workspace. Real trading, brokerage connectivity, transaction signing, and funds transfer are outside product scope.

Installation permission is separate from research permission. A third-party candidate or draft cannot become installable merely because it is present in the repository.

Candidate governance may add integration-purpose metadata—`reference_methodology`, `api_integration_candidate`, `code_reuse_candidate`, `blocked_execution`, or `approved_provider`—without collapsing review progress, disposition, and approval into one field. Execution may remain blocked while static extraction of API behavior is permitted and approval remains unrequested.

## Trellis: Development Tool Versus Product Reference

Two distinct relationships must not be conflated:

1. **Current development:** `.trellis/` manages the work of building InvestKit. Its tasks, specs, hooks, and journals belong to the repository development process.
2. **Product reference:** Trellis demonstrates a useful Harness shape—initialization, persistent rules, tasks, deterministic workflows, Agents, context recovery, artifacts, platform delivery, diagnostics, update, and uninstall.

`.trellis/` is not the InvestKit runtime.

InvestKit will implement investment-specific product behavior under the InvestKit CLI and source/workspace architecture. It must not expose `.trellis/` as the user runtime, require Trellis task files in initialized research spaces, or claim that current Trellis hooks implement InvestKit features.

## First Vertical Slice Boundary

The first slice implements one complete offline path rather than isolated components:

```text
init → install core first-party capability → load standards
→ create demo research task → run offline company workflow
→ save sources/data/assumptions/runs/report → restore context → doctor
```

Its architecture must prove eight properties: installable, initializable, Skill-discoverable, workflow-executable, task-persistent, context-recoverable, artifact-producing, and diagnosable.

Live data, third-party packages, multiple platform adapters, and optional quant capabilities follow after this contract is proven. The first live-data milestone selects one legally and operationally suitable authoritative source, statically studies its API materials, defines the authorized data scope, implements an InvestKit-owned Provider Adapter, normalizes provenance-rich data, adds cache/rate-limit/retry/error behavior and controlled tests, and requires project-owner approval before release in the first-party Provider source.

## Current State And Non-Claims

The repository currently has product/governance documentation, a first-party `skills/` source boundary, and third-party research records. It does not yet implement the InvestKit CLI, platform adapters, product Agents, research workflow runner, persistent workspace runtime, packages, or workspace template.

This architecture describes required target behavior. It does not claim that planned source directories, commands, or runtime components already exist. Third-party asset research is a supporting track and is not a dependency for the first offline vertical slice.
