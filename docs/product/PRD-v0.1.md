# InvestKit Product Requirements

Document status: v0.1 product baseline with the v0.2 Investment Core Pack amendment. The v0.1 offline Codex slice and v0.2 Investment Core Pack are implemented and verified locally. This is not a release or production-readiness claim.

## 1. Product Definition

InvestKit is an installable investment-research AI Agent Harness for Codex, Claude, Cursor, and similar environments. It combines persistent investment standards, first-party Skills and Agents, data tools, deterministic research workflows, structured tasks, and a durable research workspace.

InvestKit is neither a loose collection of finance prompts nor only a report generator. Professional investment capability and the Harness that installs, orchestrates, persists, restores, and diagnoses it are both first-class product layers.

## 2. Product Problem

General AI environments can answer finance questions, but they do not provide a consistent investment-research operating system. Users otherwise have to select prompts and tools, restate standards, reconstruct prior work, and decide where evidence and outputs belong. Results become difficult to reproduce, audit, continue, or extend.

InvestKit provides explicit methods, evidence contracts, workflows, task state, and source lineage so research can survive beyond one chat session.

## 3. Target Users

- Investors and analysts who want a persistent AI research workspace.
- Research teams that need shared standards, traceable sources, and reproducible outputs.
- Builders adding governed first-party capabilities or packages.
- AI operators delivering common research behavior across supported environments.

Users should not have to discover and manually assemble many individual Skills before useful research can begin.

## 4. Two Product Layers

### 4.1 Investment Capability Layer

- Company and business-model research.
- Financial statement and earnings-quality analysis.
- Valuation and comparable-company analysis.
- Earnings, guidance, catalyst, and event analysis.
- Falsifiable thesis and independent bear-case review.
- Source verification and sourced report assembly.
- Future advanced, quant, portfolio, and risk capabilities.

Capabilities distinguish facts, assumptions, estimates/model outputs, and unknowns. They expose sources, definitions, dates, method limitations, warnings, and financial risks.

### 4.2 Agent Harness Framework Layer

- InvestKit CLI and project initialization.
- Governed first-party asset installation/discovery.
- Persistent investment-standard loading.
- Deterministic Workflow execution.
- Structured research-task lifecycle and artifacts.
- Session-independent resume and context recovery.
- Source/data lineage and environment diagnostics.
- Future package add, update, uninstall, and additional platform adapters.

Neither layer is optional. Investment analysis without the Harness is incomplete; a Harness without useful investment methods is also incomplete.

## 5. Product Principles

- **Capability before infrastructure:** define the professional method and data contract before building a Provider.
- **One-command entry:** initialize a usable workspace without manual Skill assembly.
- **Standards persist:** the Harness loads relevant rules instead of relying on repeated prompts.
- **Evidence before narrative:** structured evidence, assumptions, estimates, and unknowns precede prose.
- **Deterministic orchestration:** tasks and Workflows replace ad hoc prompt chains.
- **Durable research:** a later process reconstructs work from files rather than hidden chat history.
- **Explicit installation ownership:** authoritative source and generated platform targets remain distinct.
- **Safe by design:** no real-money operation, silent installation, unaudited third-party execution, or return promise.

## 6. User And CLI Experience

The implemented offline command surface is:

```bash
investkit init
investkit doctor
investkit demo research
investkit demo research --resume <task-id>
```

Future target behavior includes explicit package add, update, and uninstall. These are not implemented as successful placeholders.

After initialization, InvestKit should:

1. create a structured research task;
2. load applicable investment standards;
3. select the governed Workflow and capabilities;
4. acquire approved input or read the offline fixture;
5. validate dates, definitions, lineage, and sources;
6. execute ordered analytical stages;
7. run independent counter-case and source-verification gates;
8. assemble a sourced report from structured results;
9. persist inputs, data, assumptions, sources, capability outputs, risks, and run records; and
10. restore enough state for a later process to continue safely.

## 7. Authoritative Source And Installation Boundaries

Authoritative first-party source lives under:

- `skills/`
- `agents/`
- `workflows/`
- `specs/`
- `fixtures/`
- `packages/`
- `workspace-template/`

Host locations such as `.agents/skills/`, `.claude/skills/`, and `.cursor/` are installation targets, not source. The project owner controls first-party promotion/release; the end user authorizes local installation through an explicit CLI action.

The installer copies only allowlisted regular files, preserves nested relative paths, protects conflicting user files, rejects symlinks/escapes, and records source/target checksums. `third_party/raw/` and `adapted/skills/` are never Runtime install sources.

## 8. v0.1 Offline Harness Baseline

v0.1 established the first local vertical slice:

```text
local install → init → Codex Skill target and standards
→ offline demo research → durable task and sourced report
→ later-process resume → doctor
```

The baseline owns create-once initialization, one Codex adapter, seven versioned research standards, a fictional Demo Provider, task lifecycle, report persistence, resume validation, and read-only diagnostics. It does not include live Providers, additional platform adapters, optional package lifecycle, backtesting, brokerage access, or trading.

v0.1 is the preserved Harness foundation for v0.2, not the immediate next product milestone.

## 9. v0.2 Immediate Milestone: Investment Core Pack

The immediate milestone is the Investment Core Pack, not a standalone real-data Provider.

The Runtime prerequisite is `security-identification`. The exact 12 Investment Core Skills are:

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

Each Skill requires:

- frontmatter containing only `name` and a precise positive/negative trigger description;
- objective and responsibility boundary;
- positive and difficult near-miss examples;
- required/optional inputs and missing-data behavior;
- named standards;
- ordered method and mandatory checks;
- shared machine-readable output contract;
- source-quality/freshness requirements;
- risk, non-advice, and non-applicable boundaries;
- adjacent composition handoffs; and
- positive and near-miss Evals.

Detailed schemas and checklists may live one level below `references/`. No third-party prompt or code is copied wholesale.

## 10. Company Deep Dive Workflow

`investkit demo research` executes `company-deep-dive` in this exact order:

1. `security-identification`
2. `company-deep-research`
3. `business-model-analysis`
4. `financial-statement-analysis`
5. `earnings-quality-analysis`
6. `valuation-analysis`
7. `comps-analysis`
8. `earnings-analysis`
9. `investment-thesis`
10. `bear-case-analysis`
11. `catalyst-analysis`
12. `source-verification`
13. `investment-report`

Every stage writes or validates a structured intermediate artifact. Missing data remains unknown; a genuinely inapplicable method may be `skipped` only with a reason and missing-input record. Warnings, risks, conflicts, and unknowns propagate forward rather than disappearing into prose.

The bear-case stage consumes a frozen thesis and produces an independent red-team artifact. Source verification resolves material claims before report assembly. The report may not introduce a fact, assumption, estimate, source, risk, or conclusion absent from upstream results.

## 11. Structured Result And Persistence Contract

Every capability result exposes:

```json
{
  "schema_version": "1.0",
  "capability": "business-model-analysis",
  "status": "completed",
  "skill": {"name": "business-model-analysis", "version": "0.2.0"},
  "method": {},
  "facts": [],
  "assumptions": [],
  "estimates": [],
  "unknowns": [],
  "findings": [],
  "risks": [],
  "warnings": [],
  "source_ids": []
}
```

Allowed statuses are `completed`, `skipped`, and `failed`. A fact needs at least one persisted source ID. An assumption needs rationale and materiality. An estimate names its method and material inputs. Unknowns record the gap and impact.

The durable task root preserves:

```text
task.json              question.md
plan.json              loaded-specs.json
installed-skills.json  data/*.json
sources.json           assumptions.json
findings.json          risks.json
run-log.json           report.md
capabilities/*.json
```

Resume validates completed artifacts before skipping them. A completed-task resume preserves all capability/data/index/report bytes and appends only a run event. Corrupt state and path escapes fail closed.

## 12. Capability-First Research And Provider Boundary

The v0.2 design process compares the locked candidate corpus by capability, records evidence actually read, and independently implements governed first-party methods. Raw third-party scripts, installers, Skills, broker CLIs, and APIs are not executed or installed.

Data dependency direction is:

```text
first-party Skill method
→ named normalized data requirement
→ unified InvestKit data interface
→ optional approved Provider adapter
```

The offline Demo Provider remains sufficient for v0.2. A future credentialed adapter must serve a named capability, preserve provenance and vendor constraints, remain opt-in, and pass license, security, authorization, secret, and owner-release gates. Provider approval never authorizes orders, transaction signing, funds transfer, or brokerage behavior.

## 13. Capability Map And Future Order

The durable item-level status source is [`investment-capability-map.md`](investment-capability-map.md). Status reflects actual local behavior rather than folder presence and does not imply live data or release readiness.

Future product order is:

```text
Investment Core Pack
→ Advanced Research Pack
→ Quant Pack
→ Portfolio & Risk Pack
→ capability-driven real-data Provider expansion
→ broader platform delivery lifecycle
```

## 14. Trellis Relationship

`.trellis/` manages InvestKit development tasks, specifications, and session records. It is not the InvestKit Runtime. Initialized projects use InvestKit-owned configuration, Workflows, tasks, and workspaces and do not depend on Trellis or hidden chat history.

## 15. Safety And Investment Boundaries

- No brokerage connection, order placement, transaction signing, or funds transfer.
- No guaranteed-return claim or deterministic price prediction.
- No individualized advice presented as certainty.
- No automatic installation or execution of unaudited third-party assets.
- No hidden telemetry, secret leakage, or undeclared filesystem access.
- No missing numeric input coerced to zero or neutral evidence.
- Backtests and estimates must expose assumptions, costs, bias, and limitations when those future capabilities exist.

## 16. Current Non-Claims And Success Standard

The current working tree does not claim live/current market data, Claude/Cursor support, product Agents, package add/update/uninstall, Advanced Research, Quant, Portfolio & Risk, brokerage connectivity, or trading behavior. v0.2 verification is ongoing; documentation must not be read as a whole-suite green result.

The Investment Core Pack succeeds when a fresh offline installation can initialize, diagnose, run the complete 13-stage fictional-company Workflow, inspect typed artifacts, resume without rewriting completed research, and diagnose persisted state—while preserving the v0.1 Harness guarantees and requiring no network, API key, third-party execution, or `.trellis/` dependency.
