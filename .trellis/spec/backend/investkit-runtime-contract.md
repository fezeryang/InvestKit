# InvestKit Runtime Contract

## 1. Scope / Trigger

Use this contract when changing the InvestKit CLI, Codex adapter, first-party asset delivery, Demo Provider boundary, `company-deep-dive` orchestration, capability persistence, resume behavior, report assembly, doctor diagnostics, or wheel packaging.

The v0.2 Runtime target is Python 3.11+, standard-library-only at runtime, Codex-only, and fully offline. This document owns the cross-layer delivery and execution contract. The [Investment Core Contract](./investment-core-contract.md) owns method-specific Skill, analysis, trigger-Eval, and report-evidence detail; do not duplicate those methods here.

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
