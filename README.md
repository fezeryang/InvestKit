# InvestKit

InvestKit is an installable investment-research AI Agent Harness for Codex, Claude, Cursor, and similar environments. It combines persistent investment standards, first-party Skills and Agents, data tools, deterministic research workflows, structured tasks, and a durable research workspace to turn general AI into a traceable, reproducible, and extensible investment-research workbench.

InvestKit is not just a collection of finance Skills and not just a report generator. Its Agent Harness framework and investment capabilities are both parts of the product.

## Target Experience

The planned product experience is:

```bash
investkit init
investkit doctor
investkit add quant
investkit update
```

After initialization, the user asks an investment question directly in the host AI environment. InvestKit creates a research task, loads investment standards, routes Skills/Agents/tools, validates data and sources, runs the workflow and counter-case review, generates research artifacts, persists evidence and run records, and restores the work in a later session.

These commands describe the target product. The CLI and runtime are not implemented yet.

## Two Product Layers

### Investment capability layer

- Company fundamentals and financial statement analysis.
- Valuation, industry, and peer comparison.
- Earnings, announcements, news, and event research.
- Strategy design, historical backtesting, portfolios, and risk.
- Source verification, data lineage, and research reports.

### Agent Harness framework layer

- CLI initialization, diagnostics, update, package add, and uninstall lifecycle.
- Cross-platform adapters and explicit first-party capability installation.
- Persistent investment standards.
- Skill/Agent/tool registration and routing.
- Deterministic research workflows and task lifecycle.
- Durable research workspace, artifacts, run records, and context restoration.
- Permission and security controls.

## First Runnable Product Slice

The next development milestone is one complete offline company-research path:

```text
investkit init
→ workspace and configuration
→ first-party core Skill installation and discovery
→ investment-standard loading
→ investkit demo research
→ structured research task
→ offline company-research workflow
→ sourced report and counter-case review
→ persisted inputs, data, assumptions, sources, artifacts, and run records
→ context restoration
→ investkit doctor
```

This slice must prove that InvestKit is installable, initializable, Skill-discoverable, workflow-executable, task-persistent, context-recoverable, artifact-producing, and diagnosable. It does not depend on third-party candidate assets or live financial APIs.

## Governed Future Data Integration

The first slice stays completely offline. Later research-data integrations will use InvestKit-owned Provider Adapters behind a unified data interface; first-party Skills will not embed a broker's credentials, URLs, or vendor-specific response formats.

Raw third-party assets may not be installed or executed without review. That restriction does not permanently exclude useful material from authoritative brokers or financial institutions: legally usable official APIs and interface specifications, professional research methods, and clearly licensed code may be statically studied, extracted, reimplemented or narrowly reused, tested, and approved into a first-party InvestKit Provider, Skill, Workflow, or Reference. Original third-party scripts remain non-executable by default, and credentialed Providers remain opt-in.

## Authoritative Product Source

The planned source boundaries are:

- `skills/`: first-party Skill source.
- `agents/`: first-party Agent source.
- `workflows/`: research workflow source.
- `specs/`: investment-research standards.
- `packages/`: optional capability packages.
- `workspace-template/`: user research-space template.

`.agents/skills/`, `.claude/skills/`, `.cursor/`, and other host-platform locations are installation targets, not authoritative source. The project owner controls first-party release; the end user authorizes local installation through an explicit InvestKit CLI operation.

`third_party/raw/` contains untrusted research material. `adapted/skills/` contains draft adaptation work. Neither may be installed automatically or copied directly into a host-platform target.

## Trellis Relationship

This repository currently uses `.trellis/` to help develop InvestKit: it manages development tasks, specifications, workflow state, and session records.

Trellis is also a reference for the desired product shape—one-command initialization, persistent rules, structured tasks, deterministic workflows, specialized Agents, context recovery, artifacts, multi-platform delivery, diagnostics, update, and uninstall.

These are separate facts. `.trellis/` is not the InvestKit runtime, and existing `.claude/` or `.cursor/` Trellis integration is not an InvestKit installation.

## Current Repository State

The repository currently contains product and governance documentation, a governed first-party `skills/` source boundary, a candidate-asset registry, and static research evidence. The InvestKit CLI, product Agents, research workflows, optional packages, workspace template, and host-platform adapters remain to be implemented.

Third-party asset research is a supporting track, not the product roadmap and not a dependency of the first runnable slice.

## Documentation

- `docs/product/PRD-v0.1.md`: product requirements.
- `docs/product/architecture.md`: target product architecture and Trellis boundary.
- `plans/product-development-roadmap.md`: product milestones and first vertical-slice acceptance.
- `docs/security/security-policy.md`: security and investment boundaries.
- `docs/skill-research/SOP.md`: third-party research procedure.
- `docs/governance/minimum-governance.md`: current candidate routing and installation gate.

## Safety Boundary

InvestKit does not connect to brokerages, place orders, sign transactions, transfer funds, promise returns, or present model outputs as certain investment advice. Research must preserve sources and distinguish facts, assumptions, estimates, model results, and unknowns.
