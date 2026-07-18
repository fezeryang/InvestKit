# InvestKit Product Architecture

Status: v0.1 Harness foundation, v0.2 Investment Core Pack, and the v0.3 local real-company research path are represented in the working tree. This document describes the implemented boundary; it does not assert a public release, production readiness, current-data coverage, or investment suitability.

## Product contract

InvestKit combines governed investment methods with the Harness that installs, orchestrates, persists, restores, and diagnoses them.

| Layer | Responsibility | Current v0.3 surface |
|---|---|---|
| Investment capability | Perform bounded, evidence-led company research | security identification plus 12 Investment Core Skills in one 13-stage Workflow |
| Agent Harness | Install, select, orchestrate, persist, resume, and diagnose | Python CLI, Codex adapter, task workspace, immutable input snapshot, doctor |
| Data boundary | Supply normalized evidence without defining analytical methods | fictional `DemoProvider` and project-local read-only `FileProvider` |
| Foundation | Preserve safety, lineage, and reproducibility | standards, JSON bundle contract, source IDs, hashes, typed artifacts, offline operation |

A prompt collection without the Harness is not InvestKit, and infrastructure without useful investment methods is not the product.

## Capability-first dependency direction

Research methods define data needs; Providers do not define the product roadmap.

```text
User research question
→ governed company-deep-dive Workflow
→ first-party Skill method and output contract
→ normalized Provider operation
→ demo fixture or validated imported bundle
→ persisted source-linked result
```

Skills remain independent of vendor credentials, SDK response shapes, brokerage behavior, and a specific issuer. Imported evidence changes the inputs and wording, not the capability contract. Missing evidence propagates as an unknown or a disclosed skip rather than becoming an assumption merely to complete the Workflow.

## Authoritative source and installation

Repository-root product directories are authoritative:

```text
skills/              governed first-party Skill source
agents/              first-party Agent/package boundary
workflows/           deterministic research workflows
specs/               versioned investment-research standards
schemas/             imported research-bundle schema and template
fixtures/            fictional demo and pinned acceptance evidence
packages/            future optional capability packages
workspace-template/  initialized user workspace template
```

Platform paths such as `.agents/skills/` are generated targets, not source. `.claude/skills/` and `.cursor/` in this repository are not evidence of shipping Claude or Cursor adapters.

End-user-initiated initialization copies only explicitly allowlisted regular files. Source/target mappings carry checksums. Conflicting user files are preserved, symlinks and root escapes are rejected, and unallowlisted folders are never discovered as release assets. Locally quarantined third-party packages and draft adaptations are not Runtime dependencies, installation sources, or public release assets.

Wheels carry the same governed Runtime assets under `share/investkit`, including the JSON Schema and template. Asset discovery validates a complete checkout or wheel delivery tree before use.

## Public command surface

```text
investkit init
investkit doctor
investkit research --input <project-local-bundle.json> --question <text>
investkit research --resume <research-task-id>
investkit demo research
investkit demo research --resume <demo-task-id>
```

The generic `research` forms are mutually exclusive: a new imported run needs both `--input` and a non-empty `--question`; resume takes a task ID and no question. Mode-specific resume commands reject a task created by the other mode.

The current host adapter is Codex. Package `add`, `update`, and `uninstall`, additional platform adapters, and a graphical interface remain future work rather than successful placeholders.

## Provider-neutral research bundle

[`../../schemas/research-bundle-v1.schema.json`](../../schemas/research-bundle-v1.schema.json) publishes a closed JSON Schema Draft 2020-12 contract. [`../../schemas/research-bundle-v1.template.json`](../../schemas/research-bundle-v1.template.json) is a structurally valid, deliberately empty starting point.

A bundle describes exactly one security and includes:

- schema and dataset versions;
- creation, retrieval, and common as-of times;
- currency, market, imported status, and bundle-level warnings;
- one exact security identity with stable ID, ticker, legal name, exchange, and aliases;
- a source registry with stable IDs, provenance, timing, quality, freshness, access, and reuse notes; and
- records for every normalized Provider operation.

Each operation contains `data`, `source_ids`, and `warnings`. Source IDs must resolve to the top-level registry. An operation with no sources may contain only explicit gaps such as `null`, empty arrays, recursively gap-only objects, and non-empty limitations; it cannot smuggle unsupported positive facts into a source-free record.

The Runtime implementation uses the standard library to enforce the governed acceptance contract and does not depend on a network JSON Schema validator. It rejects unsupported versions and fields, duplicate JSON keys, invalid or non-finite numbers, inconsistent identities, unresolved source IDs, unsafe date chronology, and credential-like keys or values.

## FileProvider trust boundary

`FileProvider` is a read-only adapter for a validated local bundle. It accepts a bounded UTF-8 JSON regular file inside the initialized project and rejects symlink components, traversal/root escapes, special files, oversized input, and malformed content. It performs no network or subprocess operation.

Validation produces immutable canonical JSON bytes and a SHA-256 digest. The Provider serves defensive copies through the same nine operations as the demo:

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

Every imported record carries `input_mode: imported`, `is_demo: false`, bundle version/hash, as-of/retrieval metadata, operation-specific source IDs, and warnings. Empty price, peer, valuation, earnings-context, or catalyst evidence stays empty; a source locator is not fetched or independently verified by the Runtime.

This is the key v0.3 product boundary: InvestKit can perform reproducible research on structured real-issuer evidence, but acquisition and normalization of that evidence are still user responsibilities.

## Company Deep Dive Workflow

Both Provider modes run the versioned 13-stage `company-deep-dive` Workflow:

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

The order is persisted. `bear-case-analysis` consumes a frozen thesis and produces an independent result. `source-verification` checks material claim/source relationships. `investment-report` assembles validated upstream material and may not introduce a new fact, estimate, source, risk, or conclusion.

Reusable analysis is mode-neutral. Fictional disclosures remain restricted to demo artifacts. Imported analyses build available drivers, falsifiers, KPIs, risks, and conclusions from the supplied operation records; company-specific demo assumptions are not injected into a real issuer.

## Structured capability handoffs

Each completed or validly skipped stage writes `capabilities/<stage-id>.json` with the shared envelope:

```json
{
  "schema_version": "1.0",
  "capability": "valuation-analysis",
  "status": "skipped",
  "skill": {"name": "valuation-analysis", "version": "0.2.0"},
  "method": {},
  "facts": [],
  "assumptions": [],
  "estimates": [],
  "unknowns": [],
  "findings": [],
  "risks": [],
  "warnings": [],
  "source_ids": [],
  "skip_reason": "required valuation evidence was not supplied",
  "missing_inputs": ["current price", "forecast cash flows", "WACC"]
}
```

Allowed statuses are `completed`, `skipped`, and `failed`. A skip needs a reason and missing-input record. Facts require persisted source IDs; assumptions require rationale and materiality; estimates identify the method and material inputs; unknowns retain the gap and its analytical impact. Calculations reject non-finite output.

Downstream Skills consume upstream IDs rather than copying facts into an untraceable narrative. Warnings, risks, conflicts, and unknowns propagate by ID until explicitly resolved or reported. Operation-specific source sets are preserved so identity metadata can retain both filing-index and filing sources while financial facts retain the filing source alone.

## Durable task and input snapshot

An initialized project stores installation ownership under `.investkit/` and research under `workspace/research/<task-id>/`:

```text
task.json              question.md
plan.json              loaded-specs.json
installed-skills.json  input/research-bundle.json  # imported only
data/*.json            capabilities/*.json
sources.json           assumptions.json
findings.json           risks.json
run-log.json           report.md
```

For a new imported run, the validated canonical bundle is persisted before analytical execution. `task.json` records imported mode, original project-relative origin, snapshot path, dataset version, SHA-256, security query, and research question. The original input file is not consulted again during resume.

Resume reconstructs work from durable files, not chat history. It validates task identity, Workflow order/version, source and Skill/spec snapshots, bundle hash/schema/source joins, persisted Provider records, completed capability artifacts, and report boundaries before skipping work. A failed task resumes only incomplete stages after validating existing state. A completed resume preserves bundle, data, capability, index, and report bytes and appends one run-log event.

Corrupt files, unexpected data artifacts, source mismatches, unsafe links, and mode/version confusion fail closed.

## Reports and evidence semantics

An imported report names the legal issuer, ticker, question, as-of/retrieval context, dataset version, and source provenance. It states that the data was user-supplied/imported and not independently guaranteed by InvestKit. Source locators and titles are rendered as untrusted text/metadata rather than executable markup.

Report conclusions are bounded by supplied evidence. Missing price, forecasts, discount rates, peers, expectations, guidance, transcripts, or catalysts remain disclosed gaps. The report cannot turn a gap into neutral evidence, a deterministic price prediction, a buy/sell/hold instruction, a guaranteed return, a position-size directive, or an action on a brokerage account.

## Diagnostics

`investkit doctor` is read-only. It verifies configuration, the Codex adapter, installed Skill/spec/Workflow hashes, task and artifact boundaries, capability contracts, and source resolution without repairing state or requiring the network.

For imported tasks it also checks the persisted snapshot's raw/canonical hash and schema, security query, bundle-to-source and bundle-to-Provider joins, persisted operation records, mode disclosures, report provenance, and stale or incomplete evidence. Historical evidence can produce a warning while remaining structurally healthy; corruption or unsafe state produces a failure. Doctor never needs the original mutable bundle.

## Safe v0.2-to-v0.3 migration

`investkit init` classifies an existing project before writing. A recognized v0.2 installation can migrate only InvestKit-owned files whose current bytes still match the old recorded manifest. Desired v0.3 bytes are also accepted for safe interrupted-migration recovery. User-modified conflicts, unsafe paths, unsupported mixed versions, and invalid ownership records stop the migration without overwriting the conflicting file.

Writes are atomic and the new manifest is committed last. Workspace research is preserved. Completed v0.2 demo task artifacts remain immutable and diagnosable; legacy incomplete tasks are subject to their explicit version compatibility checks rather than silent rewriting.

## Pinned real-issuer acceptance

[`../../fixtures/acceptance/microsoft-fy2025.json`](../../fixtures/acceptance/microsoft-fy2025.json) pins Microsoft Corporation's FY2025 Form 10-K evidence. It exercises exact issuer identity, a two-source SEC registry, FY2024–FY2025 financial statements, supported calculations, operation-specific attribution, explicit gaps, report disclosures, resume immutability, and doctor.

It intentionally has no current price, peer set, forecast cash flows, WACC, consensus expectations, guidance comparison, transcript evidence, or future catalyst calendar. Valuation, comps, and catalyst stages therefore skip rather than fabricate inputs. The fixture proves deterministic behavior for one historical U.S. GAAP issuer; it does not prove current accuracy, cross-issuer normalization, automatic acquisition, investment merit, or production readiness.

## Permissions, safety, and non-claims

The supported Runtime paths are offline and constrained to governed first-party assets plus the initialized project. There is no brokerage connection, order placement, transaction signing, funds transfer, hidden telemetry, credential persistence, guaranteed return, or automatic third-party execution.

Installation permission and research permission are separate. Candidate presence, static study, an adaptation draft, or a source URL never makes an asset installable or authorizes network access.

Not implemented in v0.3:

- automatic SEC/vendor/market/news acquisition or live refresh;
- raw filing/PDF/HTML/OCR/LLM extraction;
- generalized cross-issuer accounting normalization guarantees;
- Claude/Cursor adapters and cross-platform synchronization;
- package add/update/uninstall lifecycle;
- Advanced Research, Quant, and Portfolio & Risk packs;
- brokerage or trade execution behavior.

## Contributor tooling boundary

Contributor development tooling is separate from the InvestKit Runtime, is not distributed to initialized projects, and is not required to run or resume research.

See [`investment-capability-map.md`](investment-capability-map.md) for item-level behavior and [`roadmap.md`](roadmap.md) for the next acquisition, platform, and release gates.
