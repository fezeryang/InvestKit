# InvestKit PRD v0.1

## 1. Product Definition

InvestKit is an installable investment-research AI Agent Harness for Codex, Claude, Cursor, and similar environments. It combines persistent investment standards, first-party Skills and Agents, data tools, deterministic research workflows, structured tasks, and a durable research workspace to turn general AI into a traceable, reproducible, and extensible investment-research workbench.

InvestKit is not merely a collection of finance Skills and not merely a report generator. The Harness framework is part of the product, not internal development tooling.

## 2. Product Problem

General AI environments can answer finance questions, but they do not provide a consistent investment-research operating system. Without a Harness, users must manually choose prompts and tools, restate standards in every session, reconstruct prior context, and decide where data, sources, assumptions, and outputs belong. Results are difficult to reproduce, audit, extend, or continue.

InvestKit solves that operating-system problem while also providing professional investment capabilities.

## 3. Target Users

- Investors and analysts who want a persistent AI research workspace.
- Research teams that need shared standards, traceable sources, and reproducible outputs.
- Builders who want to extend investment capabilities through first-party packages.
- AI operators deploying the same research behavior across Codex, Claude, Cursor, and other environments.

Users should not need to discover, understand, or manually install many individual Skills before they can begin research.

## 4. Two First-Class Product Layers

### 4.1 Investment Capability Layer

- Company fundamentals research.
- Financial statement analysis.
- Valuation.
- Industry and peer comparison.
- Earnings, announcements, news, and event research.
- Strategy design and historical backtesting.
- Portfolio and risk analysis.
- Source verification and data lineage.
- Sourced investment-research report generation.

These capabilities must distinguish facts, assumptions, estimates, model outputs, and unknowns. They must expose sources, data definitions, method limitations, and financial risks.

### 4.2 Agent Harness Framework Layer

- InvestKit CLI.
- Project and research-workspace initialization.
- Cross-platform installation and adaptation.
- First-party Skill installation and discovery.
- Persistent investment-standard injection.
- Agent registration and routing.
- Deterministic research workflows.
- Research-task lifecycle.
- Session context restoration.
- Research artifact storage.
- Source and data lineage.
- Environment diagnostics.
- Capability-package add, update, and uninstall lifecycle.
- Permission and security controls.

Neither layer is optional. Investment analysis without the Harness is not the complete product; a Harness without useful investment capability is also not the complete product.

## 5. Product Principles

- **One-command entry:** initialize a usable research workspace without manual Skill assembly.
- **Standards persist:** investment rules are loaded by the Harness rather than repeatedly pasted into prompts.
- **Skill-first composition:** professional capabilities are organized as discoverable first-party Skills and optional packages.
- **Deterministic orchestration:** research follows explicit tasks and workflows instead of ad hoc prompt chains.
- **Evidence before narrative:** data, sources, assumptions, and run records precede conclusions.
- **Durable research:** a later session can understand and continue earlier work.
- **Multi-platform delivery:** the same authoritative source can be installed into supported AI environments through explicit adapters.
- **Safe by design:** no real-money operations, silent installation, or unaudited third-party execution.

## 6. Target User Experience

The target CLI experience includes:

```bash
investkit init
investkit doctor
investkit add quant
investkit update
```

After initialization, a user asks an investment question directly inside the AI environment. InvestKit should then:

1. Create a structured research task.
2. Load the applicable investment standards.
3. Select the required Skills, Agents, and tools.
4. Acquire approved data or read supplied material.
5. Verify data definitions, dates, lineage, and sources.
6. Execute the research workflow.
7. Run risk review and a counter-case review.
8. Generate a sourced research report.
9. Persist inputs, data, assumptions, sources, outputs, and run records.
10. Restore enough context for a later session to continue the research.

The CLI commands above describe target product behavior. They are not implemented in the current repository state.

## 7. Authoritative Source And Installation Boundaries

The planned product source layout is:

- `skills/`: authoritative first-party Skill source.
- `agents/`: authoritative first-party Agent source.
- `workflows/`: authoritative research-workflow source.
- `specs/`: authoritative investment-research standards.
- `packages/`: optional capability packages such as `quant`.
- `workspace-template/`: template for initialized user research spaces.

Host-platform locations such as `.agents/skills/`, `.claude/skills/`, `.cursor/`, and other platform directories are installation targets, not authoritative source.

The project owner controls what may be promoted or released as first-party InvestKit source. The end user controls local installation of released capabilities through explicit InvestKit CLI operations such as `init` or `add`; the CLI records the source version and host-platform target. The product must not directly copy third-party raw assets into installation targets. `third_party/raw/` and `adapted/skills/` are never automatic installation sources.

## 8. Governed Provider And Third-Party Knowledge Boundary

InvestKit may benefit from authoritative broker and financial-institution assets without treating raw third-party packages as installable product code. Four uses must remain distinct:

1. use an authorized official API through an InvestKit Provider Adapter;
2. reference a professional analysis method and re-express it under InvestKit standards;
3. reuse a small, clearly licensed portion of code after provenance, license, security, attribution, and isolated-test review;
4. execute an original third-party script, which is prohibited by default.

The first three uses may be approved when their legal, security, and product conditions are satisfied. Raw third-party assets must not be installed or executed merely because they are present in the repository. Useful material should become governed first-party source through extraction, reimplementation, wrapping, testing, and project-owner release approval.

Financial-data access uses this dependency direction:

```text
First-party InvestKit Skill
→ Unified InvestKit Data Interface
→ Provider Adapter
→ Authorized Broker or Financial API
```

The unified interface may grow to include `identify_security`, `get_security_profile`, `get_price_history`, `get_financial_statements`, `get_valuation_metrics`, `get_company_filings`, `get_research_reports`, `get_market_news`, and `get_source_metadata`. Providers normalize vendor fields into InvestKit data models and preserve provider identity, source, retrieval time, market, currency, field definitions, and licensing constraints. Skills must not bind directly to vendor authentication, URLs, or response formats.

Credentialed Providers are disabled by default. They read secrets only from environment variables or approved system credential storage, use least privilege, never persist credentials in Git, logs, reports, or research tasks, and produce clear missing/expired/insufficient-permission errors. Provider approval never permits brokerage orders, transaction signing, funds transfer, or other execution functionality.

Candidate records may separately describe integration purposes such as `reference_methodology`, `api_integration_candidate`, `code_reuse_candidate`, `blocked_execution`, and `approved_provider`. These purpose/integration fields supplement rather than replace the existing review-status, disposition, and approval-status dimensions. For example, execution can remain blocked while approval is `not_requested` and static API research is allowed.

## 9. Research Workspace And Persistence

An initialized workspace must provide stable locations for:

- project configuration and installed capability metadata;
- structured research tasks and lifecycle state;
- user inputs and source snapshots;
- normalized data and lineage records;
- assumptions and method choices;
- workflow run records and diagnostics;
- draft and final research artifacts;
- compact context needed to resume later sessions.

The exact on-disk runtime layout is an implementation decision for the first vertical slice, but the data above is required product state rather than disposable chat history.

## 10. First Runnable Vertical Slice

The next development milestone must validate both product layers through one offline company-research path:

```text
investkit init
→ create workspace and configuration
→ install the first-party core Skill
→ load investment standards
→ investkit demo research
→ create a structured research task
→ run an offline company-research workflow
→ generate a sourced report
→ save inputs, data, assumptions, sources, artifacts, and run records
→ restore the task context
→ investkit doctor verifies the environment
```

The slice must demonstrate that InvestKit is installable, initializable, able to discover a Skill, able to run a workflow, able to save and restore a task, able to generate a research artifact, and able to diagnose its environment.

Offline fixtures are sufficient for this slice. Live data providers, optional packages, and third-party candidate integration are not required.

## 11. Trellis Relationship

This repository currently uses `.trellis/` to manage InvestKit development tasks, specifications, context, and session records. That is the development toolchain.

Trellis is also an important product-form reference: one-command initialization, persistent specification injection, structured tasks, deterministic workflows, Skill-first organization, specialized Agents, context recovery, artifact history, multi-platform delivery, diagnostics, update, and uninstall.

InvestKit does not copy Trellis's coding purpose, and `.trellis/` is not the InvestKit runtime. InvestKit must implement investment-specific equivalents under its own CLI, source directories, workflows, task model, and workspace format.

## 12. Safety And Investment Boundaries

- No brokerage connection, order placement, transaction signing, or funds transfer.
- No guaranteed-return claims or deterministic price predictions.
- No individualized financial advice presented as certainty.
- No automatic installation or execution of unaudited third-party assets.
- No hidden telemetry, secret leakage, or access outside declared workspace permissions.
- Backtests and estimates must expose assumptions, costs, biases, and limitations.

## 13. v0.1 Scope

v0.1 focuses on proving the Harness contract and one useful research workflow:

- CLI initialization and diagnostics.
- One supported platform adapter, with architecture that allows more.
- Core first-party Skill discovery and installation.
- Investment-standard loading.
- Structured research task creation and persistence.
- Offline company fundamentals, financial statement, basic valuation, and source-verification workflow.
- Sourced report and run-record generation.
- Context restoration.

## 14. Explicit Non-Goals For The First Slice

- A complete frontend application.
- An asset marketplace or third-party Skill platform.
- Live brokerage or trading integration.
- Live market-data-provider integration.
- Full quantitative, portfolio, or backtesting packages.
- Support for every AI environment in the first implementation.
- Deep review or installation of the current third-party candidate registry.

## 15. Product Success Standard

The first slice succeeds when a user can initialize InvestKit, run the offline research demo inside a supported AI environment, inspect a structured task and sourced report, restart in a later session, recover the research context, and receive a passing environment diagnosis—without manually installing individual Skills or relying on `.trellis/` as runtime infrastructure.

The broader product succeeds when additional investment capabilities and platform adapters can be added without breaking research standards, task persistence, lineage, safety, or reproducibility.
