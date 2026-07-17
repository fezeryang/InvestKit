# InvestKit Runtime Contract

## 1. Scope / Trigger

Use this contract when changing the InvestKit CLI, Codex adapter, first-party asset delivery, Demo or File Provider boundary, `company-deep-dive` orchestration, capability persistence, resume behavior, report assembly, doctor diagnostics, safe initialization migration, or wheel packaging.

The v0.3 Runtime target is Python 3.11+, standard-library-only at runtime, Codex-first, and fully offline. It preserves the v0.2 fictional demo and adds research over a validated project-local bundle; it does not acquire live data or provide trading behavior. This document owns the cross-layer delivery and execution contract. The [Investment Core Contract](./investment-core-contract.md) owns method-specific Skill, analysis, trigger-Eval, and report-evidence detail; do not duplicate those methods here.

### Owner-authorized live A-share amendment

The live A-share path remains standard-library-only and explicit-permission. SSE
owns security identity; Guangfa may add F10, relative valuation, and comparable
indicators; CICCWM may add bounded daily history, current market context,
vendor-defined statement fields, and target-linked news/Dragon-Tiger records.
Every live response must pass its first-party clean-room adapter and then a second
provider-neutral normalization boundary before the immutable bundle is persisted.
Raw vendor packages are never imported or executed.

Provider fusion rejects identity conflicts, duplicate dates, inconsistent row
widths, non-finite values, nonzero vendor/business status, oversized lists, and
unrelated event promotion. A hot-news or Dragon-Tiger item enters the event ledger
only when its structured security code equals the exchange-resolved target. Recent
return, realized volatility, and drawdown are descriptive context and must never be
rendered as a deterministic forecast or trading instruction.

Repository-root `skills/`, `specs/`, `workflows/`, `fixtures/`, `agents/`, `packages/`, and `workspace-template/` are the authoritative first-party source. A wheel carries a read-only delivery copy below `share/investkit`. `.agents/skills/` is an installation target. `.trellis/`, `third_party/raw/`, and `adapted/skills/` are never Runtime dependencies or install sources.

## 2. Signatures

### CLI

```text
investkit init
investkit doctor
investkit demo research
investkit demo research --resume <task-id>
```

`add`, `update`, and `uninstall` are not implemented commands in this contract.

### Python entry points and source discovery

```python
initialize_project(project_root, *, source_root=None) -> InitializationResult
run_doctor(project_root, *, source_root=None) -> DoctorReport
run_demo_research(project_root, source_root, *, provider=None) -> ResearchResult
resume_demo_research(project_root, task_id, source_root, *, provider=None) -> ResearchResult
CodexAdapter.detect_project(project_root) -> bool
CodexAdapter.describe(project_root) -> Mapping[str, Any]

default_source_root() -> Path
complete_source_root(value: str | Path) -> Path
discover_skill_files(source_root: Path, skill_name: str) -> tuple[Path, ...]
validate_capability_result(value: Mapping[str, Any], *, expected: str) -> None
```

### Offline Provider

The Provider contract exposes exactly these nine operations:

```python
identify_security(query)
get_security_profile(security_id)
get_financial_statements(security_id)
get_price_history(security_id)
get_valuation_inputs(security_id)
get_source_metadata(security_id)
get_peer_comparables(security_id)
get_earnings_history(security_id)
get_catalyst_events(security_id)
```

## 3. Contracts

### First-party asset set and installation

The exact prerequisite Skill is:

```text
security-identification
```

The exact 12 Investment Core Skills are:

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

Only this prerequisite-plus-Core allowlist is installable. Each of the 13 governed Skill trees contains the following relative files, and initialization preserves their relative paths below `.agents/skills/<skill-name>/`:

```text
SKILL.md
agents/openai.yaml
references/method-contract.md
references/trigger-evals.json
```

Discovery is deterministic, rejects symlinks and special files, and does not make an unallowlisted directory installable merely because it exists below `skills/`. The manifest records one source/target mapping and both SHA-256 values for every governed file, including nested files.

`default_source_root()` may discover either a checkout root or a wheel-delivered `share/investkit` root. Both candidates must pass `complete_source_root()` against the same complete asset set: all 13 Skill trees and nested governed files, seven versioned specs, `workflows/company-deep-dive.json`, the demo fixture, and the governed `agents/`, `packages/`, and `workspace-template/` files. An incomplete candidate is never accepted as a reduced mode.

> **Source-discovery gotcha**: checkout-root and wheel-delivered discovery must validate the same complete asset set. Adding a governed checkout asset without adding the corresponding wheel data-file rule creates a wheel-only failure even when checkout tests pass.

### Project configuration and manifest

`.investkit/config.json` records at least:

- `investkit_version`, `schema_version`, `host_platform`;
- `initialized_at`, `source_root`, `source_directories`;
- `installation_target`, `installed_skills`, `workspace_path`;
- `manifest_path`, `managed_by`.

`.investkit/install-manifest.json` additionally records:

- one source/target mapping per installed Skill file, including nested files;
- source and target SHA-256 values;
- seven spec path/version/SHA-256 records.

An identical existing file is `SKIP`. A differing existing file is preserved, produces `WARN`, and makes initialization nonzero when it blocks a required mapping. No credential or API key is a valid configuration field.

### Provider responses

Every one of the nine Demo Provider operations returns an object containing:

- `as_of_date`, `currency`, `market`, `source`;
- `fixture_version` or `retrieved_at`;
- `is_demo: true`;
- a non-empty `warnings` list;
- operation-specific payload fields.

Missing fixture values remain `null`/unknown and are explained by warnings. Demo values are never described as live or real-time. All nine operations must work with network entry points unavailable.

### Company Deep Dive, capability artifacts, and source joins

The exact `company-deep-dive` step order is:

```text
security-identification
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

Every completed or skipped step writes `capabilities/<step-id>.json`. Each capability envelope has these required top-level fields:

```text
schema_version, capability, status, skill, method,
facts, assumptions, estimates, unknowns, findings, risks,
warnings, source_ids
```

`status` is exactly `completed`, `skipped`, or `failed`. Facts carry stable IDs, statements, and non-empty `source_ids`; every referenced ID must join to a persisted record in `sources.json`. The envelope `source_ids` is the deduplicated union of its referenced sources. Source verification records unresolved, stale, low-quality, and conflicting evidence, and report assembly may emit only claim and source IDs already present in upstream structured results.

A skipped result requires non-empty `skip_reason` and `missing_inputs`, contains no fabricated analysis, and propagates the gap to dependent capabilities and the report. `bear-case-analysis`, `source-verification`, and `investment-report` must be completed for the overall demo task to complete. Method-specific rules and payload shapes remain in the [Investment Core Contract](./investment-core-contract.md).

### Research task lifecycle and resume

`workspace/research/<task-id>/` contains:

```text
task.json              question.md
plan.json              loaded-specs.json
installed-skills.json  data/*.json
capabilities/*.json    sources.json
assumptions.json        findings.json
risks.json              run-log.json
report.md
```

Valid lifecycle paths are `created -> running -> completed` and `created|running -> failed`. A failed step persists task, plan, and run-log failure state; it does not fabricate a completed capability artifact.

Completed-task resume first validates the saved workflow, snapshots, data, sources, capability envelopes and joins, mandatory stages, and report. It then appends only a resume event to `run-log.json`; all other completed-task bytes remain immutable.

Failed or otherwise incomplete resume validates durable outputs, reconstructs context from them, skips already-valid completed or skipped steps, and continues from the first failed/incomplete step. Corrupt existing artifacts cause an actionable error and are never silently overwritten.

Machine state uses UTF-8 JSON and UTC ISO-8601 timestamps ending in `Z`. Task IDs and every referenced path are constrained below the selected project root.

### Doctor validation

- Each check is exactly `PASS`, `WARN`, or `FAIL`; any `FAIL` makes `DoctorReport.exit_code` nonzero.
- Doctor is read-only and never repairs state.
- Doctor validates the complete first-party source set, the exact Skill allowlist and nested files, manifest mappings/hashes, seven specs, exact workflow order, all nine offline Provider operations, and installed target hashes.
- Completed-task checks validate capability envelopes, source joins, required stages, persisted artifacts, and non-advisory fictional-demo report boundaries.
- External symlinks, forbidden source lineage, corrupt task artifacts, missing governed files, hash mismatches, or a partial wheel asset root are failures.
- Unmanaged user-owned Codex Skills are warnings, not automatic accusations of compromise.
- Secret findings name only the InvestKit-owned path/check and never echo the suspected value.

### v0.2 wheel packaging contract

The v0.2 build configuration produces a package with Python modules plus data-file copies below `share/investkit` for all 13 governed Skill trees (including `agents/` and `references/`), seven specs, the exact workflow, demo fixture, agent/package metadata, and workspace template. It does not package `.trellis/`, `third_party/raw/`, or `adapted/skills/` as Runtime inputs.

Wheel acceptance is performed outside the checkout: build in a temporary tree, install with `--no-index --no-deps`, and run `init -> doctor -> demo research -> resume -> doctor`. Passing checkout-root execution alone is insufficient evidence that the wheel contract is complete. This describes the build and acceptance contract, not publication or release status.

### Environment keys

No environment key is required. A future credentialed Provider must define an explicit opt-in secret contract without changing the offline default.

## 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Checkout or wheel source candidate is missing any governed asset | Reject that candidate as incomplete; never enter a partial mode |
| Explicit source root resolves below `third_party/raw` or `adapted/skills` | Reject before reading or installing any asset |
| Derived path escapes the approved root or crosses a symlink | Reject before read/write |
| Unallowlisted directory exists below canonical `skills/` | Ignore it as a Runtime asset; do not install it |
| Governed nested Skill file is missing, special, or symlinked | Init/doctor nonzero; name the project-relative Skill tree without following it |
| Existing target file is identical | `SKIP` without changing bytes |
| Existing target file differs | Preserve it; `WARN`; nonzero when the required installation is blocked |
| Mapping path or source/target hash differs | Doctor `FAIL` |
| Any Provider operation attempts network access or returns an invalid envelope | Provider/doctor test failure; offline default remains intact |
| Workflow step order differs from the exact 13 IDs | Workflow load and doctor failure |
| Capability status/envelope is invalid | Resume/doctor failure |
| Fact source ID is absent from `sources.json` | Source-verification gap; completed-task validation and doctor failure |
| Skipped result lacks a reason or missing inputs | Result validation failure |
| Required bear-case, source-verification, or report stage is not completed | Overall completion and doctor failure |
| Provider method fails during a step | Persist failed task/plan/run state; do not emit a completed result |
| Valid failed/incomplete task is resumed | Preserve durable outputs and continue from the first failed/incomplete step |
| Existing durable output is corrupt | Resume error; do not overwrite it or later artifacts |
| Completed task is resumed | Validate first; append only a run-log event; preserve every other artifact byte |
| Likely secret exists in InvestKit-owned JSON/Markdown | Doctor `FAIL` without value disclosure |
| Wheel installation has no checkout assets | Discover and validate the complete `share/investkit` root or fail actionably |
| Network or API key is unavailable | Normal offline flow remains unaffected |

## 5. Good / Base / Bad Cases

### Good

- A fresh initialization installs the exact 13 Skill trees and all four governed files per tree, with one manifest mapping/hash record per file.
- Checkout-root and wheel-only runs discover equivalent complete assets and execute the same `init -> doctor -> demo research -> resume -> doctor` flow.
- A completed task has 13 schema-valid capability artifacts with resolved fact sources; completed resume changes only `run-log.json`.

### Base

- Peer data is absent. `comps-analysis` writes a valid skipped envelope with the reason and missing inputs, and downstream artifacts preserve and disclose the gap.
- A Provider step fails after earlier steps completed. Resume validates and reuses the earlier durable results, then restarts at the failed step.
- An unrelated user-managed Skill exists below `.agents/skills/`; doctor warns and preserves it.

### Bad

- Accepting a source root because `skills/` exists while nested Eval or agent files are missing.
- Adding a governed file to the checkout but omitting it from wheel data-file rules.
- Treating a missing numeric value as zero, inventing a report claim, or allowing a fact source ID that cannot join to `sources.json`.
- Rewriting a completed capability or report during resume.

## 6. Tests Required

- CLI parser/help proves only `init`, `doctor`, and nested `demo research` are runnable.
- Asset tests assert the exact prerequisite plus 12 Core names, all four governed files in every Skill tree, seven versioned specs, exact workflow asset, and forbidden-source rejection.
- Init tests cover empty, repeated, nested-file, conflict-preserving, mapping/hash, symlink, and unallowlisted-directory cases.
- Provider tests call all nine operations with network entry points patched to fail and assert common response fields plus operation payloads.
- Workflow tests assert the exact 13-step order, one valid completed/skipped capability artifact per durable step, mandatory completion gates, and failed-state persistence.
- Result/source tests assert required envelopes, fact-to-`sources.json` joins, deduplicated `source_ids`, valid skip reasons, missing-input propagation, and no-new-claim report assembly.
- Resume tests assert completed byte immutability except append-only `run-log.json`, failed-step continuation, corrupt-capability rejection, source-ID corruption rejection, and traversal/symlink boundaries.
- Doctor tests cover the complete source set, nested mappings/hashes, specs, workflow, all Provider operations, installed files, task artifacts, warning-only exit, secret redaction, and read-only behavior.
- Packaging tests build and install a wheel in an isolated temporary environment with no checkout asset access, then run `init -> doctor -> demo research -> resume -> doctor` and compare the validated asset inventory with checkout expectations.
- Full Runtime statement coverage is at least 80%.

Method-level valuation, comps, earnings, thesis, bear-case, catalyst, source-verification, report, and trigger-Eval assertions belong in the [Investment Core Contract](./investment-core-contract.md).

## 7. Wrong vs Correct

### Wrong

```python
# A directory marker accepts a partial checkout or wheel and hides packaging gaps.
for candidate in candidates:
    if (candidate / "skills").is_dir():
        return candidate
```

### Correct

```python
# Every discovery surface passes the same fail-closed complete-asset validator.
for candidate in candidates:
    try:
        return complete_source_root(candidate)
    except AssetValidationError:
        continue
raise AssetValidationError("InvestKit first-party assets are unavailable")
```

The same validator prevents checkout-only success from masking an incomplete wheel and keeps initialization, doctor, workflow execution, and packaging acceptance aligned.

## v0.3 Imported Real-Company Runtime Amendment

This amendment supersedes v0.2 wording where the selected Provider, schema assets,
version migration, or imported-task lifecycle is concerned. The v0.2 demo remains a
supported compatibility path.

### 1. Scope / Trigger

Apply this amendment when changing any of the following:

- `investkit research`, `run_research`, or `resume_research`;
- the versioned research-bundle schema/template or `FileProvider`;
- imported task snapshots, source joins, neutral reports, or imported doctor checks;
- checkout/wheel delivery of bundle assets;
- v0.2-to-v0.3 initialization migration.

Imported mode means that the user supplied a local, already-structured evidence
bundle. It does not mean that InvestKit fetched, verified, refreshed, licensed, or
guaranteed the underlying information. No imported-mode path may place trades,
connect to a brokerage, transfer funds, promise returns, or turn the report into a
buy/sell/hold instruction.

### 2. Signatures

```text
investkit research --input <project-local-path> --question <non-empty-text>
investkit research --resume <task-id>
investkit demo research [--resume <task-id>]
```

`--input` and `--resume` are mutually exclusive. `--question` is required with
`--input` and forbidden with `--resume`.

```python
load_research_bundle(
    project_root: str | Path,
    input_path: str | Path,
) -> ValidatedBundle

FileProvider(project_root: str | Path, input_path: str | Path)

run_research(
    project_root: str | Path,
    source_root: str | Path,
    *,
    input_path: str | Path,
    question: str,
) -> ResearchResult

resume_research(
    project_root: str | Path,
    task_id: str,
    source_root: str | Path,
) -> ResearchResult

initialize_project(
    project_root: str | Path,
    *,
    source_root: str | Path | None = None,
) -> InitializationResult

run_doctor(
    project_root: str | Path,
    *,
    source_root: str | Path | None = None,
) -> DoctorReport
```

### 3. Contracts

#### Bundle and File Provider

The governed assets are:

```text
schemas/research-bundle-v1.schema.json
schemas/research-bundle-v1.template.json
```

Both must exist in checkout and wheel source roots. The schema is Draft 2020-12.
Runtime validation is standard-library-only but must accept and reject the same
governed acceptance cases as the published schema.

A valid bundle describes exactly one security, contains exactly the nine Provider
operations, and has a non-empty source registry. Operation `source_ids` resolve to
that registry. Registry and operation source IDs are canonical non-empty strings
with no leading or trailing whitespace. Source metadata records publication/as-of/retrieval chronology,
quality, freshness, access notes, and license notes or explicit unknowns. Every
numeric JSON value is finite. Missing optional evidence is represented only by
explicit null/empty gaps and limitations; a source-free record cannot mix gaps with
positive assertions.

`load_research_bundle` accepts at most 2 MiB of strict UTF-8 JSON from a regular
file below the selected project root. It rejects absolute paths outside the root,
traversal, symlink components, special files, duplicate keys, non-finite values,
unsupported versions, unresolved/duplicate source IDs, inconsistent dates, and
credential-like keys or values. Error messages never echo suspected secrets.
Credential detection is shared across bundle loading, initialization, and Doctor;
it covers contextual secret assignments and common OpenAI, GitHub, GitLab, Slack,
Stripe, npm, Google, SendGrid, AWS, JWT, Basic/Bearer, and private-key forms without
mistaking ordinary task SHA-256 values for credentials.

`FileProvider` validates and reads the file once, retains canonical JSON bytes and
their SHA-256, serves defensive copies without later filesystem reads, performs no
network/subprocess activity, implements all nine Provider methods, and emits
`input_mode: imported`, `is_demo: false`, bundle version/hash, source IDs, and
non-empty warnings/limitations.

#### Imported task persistence and resume

Before analytical execution, imported mode persists canonical validated input at:

```text
workspace/research/<task-id>/input/research-bundle.json
```

`task.json` records `input_mode`, security query, original project-relative origin,
bundle version, canonical SHA-256, and snapshot path. The question remains exact in
machine state; `question.md` is a reversible escaped display that cannot inject raw
HTML, links, or images.

All data records, `sources.json`, capabilities, aggregates, logs, and the report
declare or preserve imported mode. On resume, the persisted snapshot is validated
and used to reconstruct `FileProvider`; the original input is neither required nor
reread. Before any resume event is appended, every existing provider-derived data
record and source registry must equal the snapshot-derived record. A completed
resume changes only `run-log.json`. A failed/incomplete resume reuses only validated
durable artifacts and never overwrites corruption. Before it appends a resume event,
it also deterministically recomputes each completed imported capability in plan
order from the immutable snapshot and verified predecessors; any byte-semantic
result mismatch is corruption.

#### Doctor

Doctor is read-only for healthy, stale, incomplete, corrupt, and read-only task
trees. For an imported task it validates mode/version, question display, lifecycle,
snapshot regularity/schema/hash, provider-derived data equality, source joins,
capabilities, aggregates, report disclosures, and artifact freshness. It recursively
`lstat`s the task tree without following entries and fails every symlink or special
file, including unexpected paths. Its bounded JSON reader rejects duplicate keys,
non-finite values, oversized input, and non-regular files. Freshness labels are
commentary: evidence older than the documented 180-day window relative to the
current Doctor date is warned from objective as-of/publication dates. Missing
price/peer/expectation/guidance/transcript/catalyst evidence is a disclosed
`WARN` when the persisted contract remains valid; unsafe paths, corruption,
advisory/trading language, or injected markup are `FAIL`. Diagnostics identify the
owned artifact/check without replaying untrusted content.

#### Safe v0.2-to-v0.3 initialization migration

Initialization classifies the complete project state before writing: fresh, current
v0.3, exact supported v0.2, recoverable interrupted migration, or rejectable mixed
state. Only InvestKit-owned v0.2 files whose bytes still match the exact legacy
ledger may be replaced. The exact v0.2 mapping and spec ledgers are authenticated by
release-pinned aggregate SHA-256 values rather than trusted from the mutable project
manifest. Every replacement and create is preflighted; a user-modified,
missing, symlinked, special, forged, secret-bearing, non-finite, or unknown mapping
aborts before mutation. Durable `workspace/research/` content is never migrated.
Writes are atomic and the v0.3 manifest is committed last. A recoverable interrupted
migration accepts only the exact old-or-new digest for each allowlisted owned path.

#### Packaging

The v0.3 wheel carries both bundle schema assets in addition to all v0.2 governed
assets. Acceptance runs outside the checkout and covers fresh init, doctor, demo,
imported real-issuer research, imported completed resume, and final doctor. The
acceptance bundle may be copied into the fresh project by the test; it is test
evidence rather than an implicit live data feed.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Input path escapes the project, traverses, crosses a symlink, or is non-regular | Reject before decoding; create no task |
| Input exceeds 2 MiB, is not strict UTF-8/JSON, has duplicate keys, or has NaN/Infinity | Reject deterministically; create no task |
| Bundle version/shape/identity/source registry is invalid | Reject with a bounded non-secret error |
| Operation references an unknown source or positive evidence has no source | Reject the entire bundle |
| Source-free operation mixes an asserted value with gaps | Reject; do not treat it as an evidenced record |
| Bundle/source dates run backward or into the future relative to bundle chronology | Reject |
| Credential-like key or value appears anywhere | Reject without echoing it |
| Source ID contains leading/trailing whitespace | Reject at the Provider boundary; never persist an unjoinable ID |
| Original input changes or is deleted after task creation | Resume from the canonical snapshot unchanged |
| Snapshot hash/schema/version differs from `task.json` | Resume/doctor fail before modifying the run log |
| Persisted data/source record differs from the snapshot-derived Provider record | Resume/doctor fail without overwrite |
| Imported evidence omits an optional analytical input | Emit explicit unknown/skip/warning; never infer zero or consensus |
| Failed resume contains a schema-valid rewritten completed capability | Reject before appending a resume event |
| Task tree contains any symlink/special file or strict JSON violation | Doctor/Runtime fail without following or mutating it |
| Imported report calls data independently verified or emits advice/trading/injected markup | Doctor/report validation fail |
| Exact supported v0.2 initialized state is unmodified | Atomically migrate owned metadata/assets; preserve workspace |
| Any legacy owned path is modified, unsafe, forged, or unmapped | Abort migration before all writes and report only safe path context |
| Migration is interrupted before manifest commit | Next init recovers only from exact old/new allowlisted digests |
| Wheel lacks either schema asset or another governed asset | Source discovery and wheel acceptance fail |

### 5. Good / Base / Bad Cases

#### Good

- A project-local Microsoft FY2025 bundle with SEC source records completes all 13
  workflow stages, calculates only supported metrics, identifies unavailable market
  and expectation evidence, and produces a source-joined imported-data report.
- Deleting the original bundle after completion does not affect resume; only the
  append-only run log changes.
- An untouched v0.2 project migrates, preserves its completed demo task byte-for-byte,
  and passes v0.3 doctor.

#### Base

- Price, peers, consensus, transcript, or catalysts are absent. Their operation
  records contain explicit gaps and limitations; affected methods skip or report
  unknowns while source verification and the report retain the limitation.
- A valid imported task is old relative to its as-of date. Doctor returns a stale
  warning and remains read-only.
- An incomplete task has valid prior artifacts. Resume reconstructs the Provider from
  its snapshot and continues at the first incomplete step.

#### Bad

- Reading the original input again during resume.
- Coercing absent consensus or price to zero, or inventing management commentary.
- Trusting a failed task's tampered `data/*.json` because no final hash manifest exists.
- Partially rewriting a v0.2 project before discovering a user-modified conflict.
- Describing the local-bundle path as live, current, independently verified, or
  production-ready.

### 6. Tests Required

- CLI tests cover both generic invocation shapes, ambiguous/empty arguments, demo
  compatibility, uninitialized projects, and safe errors.
- Bundle tests compare runtime and Draft 2020-12 schema outcomes for the template,
  real-issuer fixture, malformed types, duplicate/unresolved sources, chronological
  violations, source-free assertions, non-finite numbers, credentials, size, UTF-8,
  traversal, outside-root, symlink-parent/leaf, and special-file cases.
- FileProvider tests invoke all nine methods with network/subprocess entry points
  unavailable and verify immutable hash/version/source metadata and defensive copies.
- Workflow tests cover exact snapshot persistence, imported mode propagation,
  per-operation multi-source joins, neutral wording, report escaping/disclosures,
  deterministic completed-capability recomputation on failed resume, original-input
  mutation/deletion, and completed
  byte immutability except the run log.
- Doctor tests cover healthy/incomplete/stale/read-only imported tasks and mutations
  of snapshot, hash, schema, registry, data, capability, report, symlink, markup,
  action language, and secret-like state while proving no bytes or mtimes change.
- Migration tests cover fresh/current/exact-v0.2/interrupted/mixed classification,
  full conflict preflight, atomic manifest-last behavior, workspace immutability,
  forged mappings, non-finite/duplicate-key state, credentials, symlinks, and FIFO.
- Wheel-only acceptance covers both demo and imported real-issuer lifecycles with the
  checkout inaccessible.
- The full suite has no skips, Pyright has zero errors, Runtime statement coverage is
  at least 80%, and static network/subprocess/secret checks pass.

### 7. Wrong vs Correct

#### Wrong

```python
# Resume silently trusts mutable external input and already-persisted derived state.
provider = FileProvider(project_root, task["input"]["origin"])
context["financials"] = store.read_json(task_path, "data/financials.json")
```

#### Correct

```python
# Resume reconstructs from the immutable validated snapshot, then proves every
# present derived record still matches that Provider before appending a run event.
provider = FileProvider(project_root, task["input"]["snapshot"])
validate_snapshot_hash(provider.bundle_sha256, task["input"]["sha256"])
validate_persisted_provider_state(store, task_path, provider)
```

The snapshot is the durable trust root for imported execution; all downstream state
must remain reproducible from it and the governed analysis contract.
