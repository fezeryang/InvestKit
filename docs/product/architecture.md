# InvestKit Product Architecture

Status: v0.1 offline Codex Harness baseline and v0.2 Investment Core Pack implemented and verified locally. This document does not assert release or production readiness.

## Product Contract

InvestKit is an installable investment-research AI Agent Harness. It combines governed investment methods with the framework that installs, orchestrates, persists, restores, and diagnoses them.

| Layer | Responsibility | Current v0.2 surface |
|---|---|---|
| Investment capability | Perform bounded professional research | 12 Investment Core Skills plus security identification |
| Agent Harness | Install, select, orchestrate, persist, resume, and diagnose | Python CLI, Codex adapter, `company-deep-dive`, task workspace, doctor |
| Foundation | Preserve safety, evidence, and reproducibility | standards, source IDs, checksums, structured artifacts, offline fixture |

Neither top layer is optional. A prompt collection without the Harness is not InvestKit, and infrastructure without useful investment methods is not the product.

## Capability-First Dependency Direction

Research methods define data needs; Providers do not define the product roadmap.

```text
User research question
→ governed Workflow
→ first-party Skill method and output contract
→ named normalized data requirement
→ optional InvestKit Provider operation
→ approved source
```

A Skill must remain independent of vendor credentials, URLs, SDK response shapes, and brokerage behavior. The offline Demo Provider is sufficient for the v0.2 acceptance path. A future live adapter is justified only by a named capability gap.

## Authoritative Source And Installation

Repository-root product directories are authoritative:

```text
skills/              governed first-party Skill source
agents/              first-party Agent source or package boundary
workflows/           deterministic research workflows
specs/               versioned investment-research standards
fixtures/            first-party offline Eval data
packages/            future optional capability packages
workspace-template/  initialized user workspace template
```

Platform paths are generated targets, not source:

```text
.agents/skills/       current Codex Skill target
.claude/skills/       future adapter target
.cursor/              future adapter target
```

End-user-initiated CLI operations copy only explicitly allowlisted regular files. Each source/target mapping records a checksum. Existing conflicting user files are preserved, symlinks and root escapes are rejected, and unallowlisted folders are not discovered as release assets.

`third_party/raw/` is untrusted research evidence and `adapted/skills/` is a draft boundary. Neither is a Runtime dependency or install source.

## v0.2 Skill Catalog

The Runtime prerequisite is `security-identification`. The 12 Investment Core Skills are:

```text
company-deep-research
business-model-analysis
financial-statement-analysis
earnings-quality-analysis
valuation-analysis
comps-analysis
earnings-analysis
investment-thesis
bear-case-analysis
catalyst-analysis
source-verification
investment-report
```

Each Skill publishes precise positive and near-miss triggers, required/optional inputs, missing-data behavior, used specs, ordered method, output contract, source requirements, risk boundaries, composition handoffs, and Evals. Direct `references/` and `agents/openai.yaml` files are governed nested assets and are installed with the Skill.

## Company Deep Dive Workflow

`investkit demo research` runs the 13-stage `company-deep-dive` Workflow against first-party fictional data:

```text
security-identification
→ company-deep-research
→ business-model-analysis
→ financial-statement-analysis
→ earnings-quality-analysis
→ valuation-analysis
→ comps-analysis
→ earnings-analysis
→ investment-thesis
→ bear-case-analysis
→ catalyst-analysis
→ source-verification
→ investment-report
```

The order is part of the persisted contract. `bear-case-analysis` consumes a frozen thesis and produces an independent result. `source-verification` gates material claim/source relationships. `investment-report` assembles validated upstream material and may not introduce a new fact, estimate, source, risk, or conclusion.

## Structured Capability Handoffs

Each completed or validly skipped stage writes `capabilities/<stage-id>.json` with a shared envelope:

```json
{
  "schema_version": "1.0",
  "capability": "valuation-analysis",
  "status": "completed",
  "skill": {"name": "valuation-analysis", "version": "0.2.0"},
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

Allowed statuses are `completed`, `skipped`, and `failed`. A skipped result needs a non-empty reason and missing-input record. Facts require persisted source IDs; assumptions require rationale/materiality; estimates require method and material inputs; unknowns retain the gap and impact. Missing numeric data never becomes zero.

Downstream Skills consume upstream IDs rather than copying facts into an untraceable narrative. Warnings, risks, conflicts, and unknowns propagate by ID until explicitly resolved or reported.

## Investment Standards

Seven versioned files under `specs/` govern research principles, evidence, sources, financial data, valuation, risk, and reports. A task records the exact versions and checksums it loaded. Standards are selected by the Harness; they are not repeatedly pasted by the user.

## Provider Boundary

The v0.2 Demo Provider exposes the operations needed by the bounded offline Workflow:

```text
identify_security
get_security_profile
get_financial_statements
get_price_history
get_valuation_inputs
get_source_metadata
get_peer_comparables
get_earnings_history
get_catalyst_events
```

Every operation retains source, as-of date, market, currency, fixture version or retrieval time, `is_demo: true`, and warnings. Peer records retain inclusion/exclusion reasons; earnings records separate actuals, expectations, guidance, and transcript availability; catalyst records retain timing, evidence, materiality, and uncertainty.

Future adapters sit behind the same normalized interface:

```text
first-party Skill → unified interface → approved Provider adapter → authorized source
```

An adapter owns authentication, endpoints, pagination, rate limits, retries, error mapping, normalization, and provenance for one approved source. Credentials are opt-in and never enter Git, logs, reports, task artifacts, or unrelated Skills. Provider approval never grants order, transaction-signing, or funds-transfer authority.

## Durable Task And Workspace State

An initialized project stores configuration and installation ownership under `.investkit/` and user research under `workspace/research/<task-id>/`:

```text
task.json              question.md
plan.json              loaded-specs.json
installed-skills.json  data/*.json
sources.json           assumptions.json
findings.json          risks.json
run-log.json           report.md
capabilities/*.json
```

`task.json` and `plan.json` own lifecycle and stage state. Capability artifacts are written before a stage is marked complete. `sources.json`, `assumptions.json`, `findings.json`, and `risks.json` are normalized cross-capability views, not alternative untyped analyses.

Resume reconstructs work from durable files, not chat history. It validates task identity, workflow order, schemas, checksums, and source IDs before skipping a completed stage. A completed resume preserves all analytical and report bytes and appends only a run-log event. A corrupt or externally linked artifact fails closed.

## CLI, Adapter, And Diagnostics

The current public CLI surface is:

```text
investkit init
investkit doctor
investkit demo research
investkit demo research --resume <task-id>
```

The current adapter target is Codex. `add`, `update`, `uninstall`, Claude, Cursor, and other adapters remain future work rather than successful placeholders.

`doctor` is read-only. Its contract covers configuration, the exact Skill set and nested hashes, standards, Workflow identity/order, fixture metadata, capability envelopes, source resolution, mandatory stages, task integrity, symlink boundaries, forbidden mappings, and secret-safe diagnostics.

## End-To-End Runtime Flow

```text
explicit init
→ governed assets and manifest
→ user question and durable task
→ relevant standards and company-deep-dive plan
→ offline Provider records
→ 13 typed capability results
→ independent bear case
→ source-verification gate
→ report assembled from structured inputs
→ persisted context
→ later resume and doctor
```

## Permissions And Safety

The Runtime declares filesystem, network, credential, and installation boundaries. The default path is offline and constrained to the initialized project and governed first-party assets. There is no brokerage connection, order placement, transaction signing, funds transfer, hidden telemetry, guaranteed return, or automatic third-party execution.

Installation permission and research permission are separate. Candidate presence, static study, or an adaptation draft never makes an asset installable.

## Trellis Boundary

`.trellis/` manages the development of InvestKit. It is not the InvestKit Runtime, is not copied into initialized projects, and is not required to run or resume research. Current `.claude/` or `.cursor/` Trellis integration is likewise not evidence of an InvestKit platform adapter.

## Current State And Future Order

The working tree contains the v0.2 Skill catalog, deterministic capability modules, offline fixture/Provider surface, Workflow/persistence changes, and documentation. Verification is ongoing; this statement does not claim the whole suite is green or the package is released.

The capability roadmap is:

```text
Investment Core Pack
→ Advanced Research Pack
→ Quant Pack
→ Portfolio & Risk Pack
→ capability-driven real-data Provider expansion
→ broader platform delivery lifecycle
```

See [`investment-capability-map.md`](investment-capability-map.md) for item-level status. Live or credentialed Providers, product Agents, additional adapters, package lifecycle, brokerage connectivity, and trading behavior are not v0.2 capabilities.
