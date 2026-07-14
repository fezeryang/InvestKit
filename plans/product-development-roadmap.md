# InvestKit Product Development Roadmap

InvestKit is an installable investment-research AI Agent Harness for Codex, Claude, Cursor, and similar environments. It combines persistent investment standards, first-party Skills and Agents, data tools, deterministic research workflows, structured tasks, and a durable research workspace to turn general AI into a traceable, reproducible, and extensible investment-research workbench.

This is the product roadmap. Third-party asset research is a separate supporting track and must not block the first-party product slice.

## M0 — Product Definition Baseline

Status: documentation phase

- Fix the two-layer product definition.
- Define authoritative source and host-platform installation boundaries.
- Separate current `.trellis/` development tooling from the future InvestKit runtime.
- Define the first vertical slice and its deterministic acceptance criteria.

M0 does not implement product code.

## M1 — First Offline Harness Vertical Slice

M1 is the next development milestone. It proves one complete user path with one supported host-platform adapter and local fixtures.

### User path

```text
documented local install
→ investkit init
→ workspace/configuration and install manifest
→ core first-party Skill installed from skills/ and discovered
→ applicable specs/ loaded
→ investkit demo research
→ structured task and observable lifecycle
→ offline company fundamentals/financial/basic valuation/source workflow
→ risk and counter-case review
→ sourced report plus inputs/data/assumptions/run records
→ new process restores task context
→ investkit doctor validates the environment
```

### Required product components

- A locally installable `investkit` CLI artifact.
- One host-platform adapter.
- Versioned workspace configuration and installation manifest.
- One first-party core Skill under `skills/`.
- A minimal set of investment standards under `specs/`.
- One offline company-research workflow under `workflows/`.
- Structured task, run, source, assumption, context, and artifact persistence.
- A fixed local company fixture with resolvable source references.
- `init`, `demo research`, and `doctor` behavior.

### Deterministic acceptance

1. A clean supported environment can install a local build artifact and invoke `investkit`.
2. `investkit init` succeeds in an empty directory, creates versioned configuration/workspace state, records installed files, and does not silently overwrite user files when repeated.
3. The CLI installs one core Skill from canonical `skills/` into one adapter target, records its source version/hash and target mapping, and the Harness can enumerate it.
4. A run record identifies the exact investment-standard version loaded from `specs/`.
5. `investkit demo research` uses only a fixed local fixture; it does not call a financial data service, third-party API, `third_party/raw/`, or `adapted/skills/`.
6. Every demo creates a unique task with observable `created → running → completed` or `failed` state. Failure still produces a run record.
7. Key report claims resolve to local source snapshots. The artifact distinguishes facts, assumptions, estimates, model outputs, and unknowns and includes risk and counter-case sections.
8. A new process restores the research goal, state, inputs, sources, assumptions, runs, and artifacts by task identity without chat history or `.trellis/`.
9. `investkit doctor` exits successfully for a healthy workspace and checks CLI/config compatibility, adapter target, core Skill discovery, standards, workspace writeability, and task/run/artifact references.
10. Removing the installed core Skill or breaking an artifact reference makes `doctor` fail with an actionable diagnosis; diagnosis does not silently repair the workspace.
11. Repeated demos preserve prior tasks. Workflow step order, source set, and assumption schema are reproducible; generated prose need not be byte-identical.
12. The slice contains no brokerage, order, funds-transfer, hidden telemetry, secret, or automatic third-party installation behavior.

### M1 scope guard

M1 does not require three platform adapters, live financial data, a web UI, a marketplace, a service database, the complete Agent router, optional packages, or third-party candidate integration. “Offline” means no external research data/service dependency; it does not claim that the host model is air-gapped.

## M2 — First Authorized Data Provider

After the offline Harness contract is proven, select one authoritative broker or financial-data candidate whose license, authorization, and security conditions are comparatively clear. This milestone must:

1. statically study the API documentation and any bundled scripts without executing the originals;
2. record permitted data scope, terms, provenance, authentication, endpoints, pagination, limits, errors, and market-code conventions;
3. implement an InvestKit-owned Provider Adapter behind the unified data interface;
4. normalize data while retaining provider, source, time, market, currency, and field definitions;
5. add opt-in credential handling, caching, rate limiting, retries, and actionable errors;
6. add unit tests and controlled integration tests; and
7. require project-owner approval before the adapter enters the released first-party Provider source.

M2 may reuse only clearly licensed, attributed, security-reviewed code that passes isolated tests; first-party reimplementation is preferred. It must not execute original third-party scripts in user environments, enable a credentialed Provider by default, or expose trading/order operations.

## M3 — Cross-Platform Delivery Lifecycle

- Add Codex, Claude, and Cursor adapters beyond the M1 reference adapter.
- Make installation ownership explicit through a generated-file manifest.
- Add governed update and uninstall behavior.
- Preserve user research workspaces across updates and uninstall by default.
- Expand `doctor` across supported platform targets.

M3 must not redesign the M1 task, workflow, artifact, or standard contracts without a migration path.

## M4 — First-Party Research Expansion

- Industry and peer comparison.
- Earnings, announcements, news, and event workflows.
- Approved data tools with explicit provenance and permissions.
- Additional bounded research Agents and counter-case methods.
- Report and artifact types beyond the first company-research report.

## M5 — Optional Quant Package

- `investkit add quant` package lifecycle.
- Strategy specification and historical backtesting.
- Portfolio and risk analysis.
- Bias, cost, calendar, and reproducibility checks.

Quant remains research-only. It must not introduce brokerage connectivity or market execution.

## Supporting Track — Third-Party Asset Research

The candidate registry and Batch 001 static research remain a separate supporting track. Raw third-party assets are never installed or executed without review. Legally usable official APIs and interface specifications, professional methods, and clearly licensed code may be classified for methodology reference, Provider integration, or controlled code-reuse review and may become part of a tested first-party Provider, Skill, Workflow, or Reference after the applicable approvals. This track does not define product milestones and is not a prerequisite for M1.
