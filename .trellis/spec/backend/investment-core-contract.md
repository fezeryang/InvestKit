# InvestKit Investment Core Contract

## 1. Scope / Trigger

Use this contract when adding or changing an Investment Core Skill, its trigger/Eval data, structured capability results, the `company-deep-dive` Workflow, Demo Provider datasets needed by those capabilities, report assembly, task resume validation, or doctor checks for v0.2.

This contract extends the v0.1 Runtime contract. The product order is capability first: define a professional research method and its data contract, then extend the offline Provider only when that named capability needs data. Do not build a Provider or data platform independently of a capability.

Canonical third-party evidence may inform design only through static, attributed synthesis. `third_party/raw/` and `adapted/skills/` remain forbidden Runtime sources.

## 2. Signatures

### Skill catalog

```python
RUNTIME_SKILLS: tuple[str, ...]
INVESTMENT_CORE_SKILLS: tuple[str, ...]

discover_skill_files(source_root: Path, skill_name: str) -> tuple[Path, ...]
evaluate_trigger(question: str, skill_name: str) -> bool
```

`RUNTIME_SKILLS` contains `security-identification` plus all 12 `INVESTMENT_CORE_SKILLS`. Only these names are installable first-party Skills.

### Capability results

```python
build_capability_result(
    capability: str,
    *,
    status: str,
    skill: Mapping[str, str],
    method: Mapping[str, Any],
    facts: Sequence[Mapping[str, Any]] = (),
    assumptions: Sequence[Mapping[str, Any]] = (),
    estimates: Sequence[Mapping[str, Any]] = (),
    unknowns: Sequence[Mapping[str, Any] | str] = (),
    findings: Sequence[Mapping[str, Any] | str] = (),
    risks: Sequence[Mapping[str, Any] | str] = (),
    warnings: Sequence[str] = (),
    skip_reason: str | None = None,
    missing_inputs: Sequence[str] = (),
) -> dict[str, Any]

validate_capability_result(value: Mapping[str, Any], *, expected: str) -> None
```

### Demo Provider additions

```python
get_peer_comparables(security_id: str) -> ProviderRecord
get_earnings_history(security_id: str) -> ProviderRecord
get_catalyst_events(security_id: str) -> ProviderRecord
```

The six v0.1 Provider operations remain available.

### User commands

The public CLI remains:

```text
investkit init
investkit doctor
investkit demo research
investkit demo research --resume <task-id>
```

`demo research` now executes `company-deep-dive`; it is not a placeholder or second command family.

## 3. Contracts

### Installed Skill set and files

- `security-identification` is a Runtime prerequisite, not one of the 12 Core Skills.
- Every Core Skill has a valid `SKILL.md`, precise positive and near-miss triggers, inputs, specs, ordered method, output contract, sources, risk/non-applicable boundaries, composition, and Evals.
- A Skill directory may contain approved regular files below `references/` and `agents/`; initialization installs the relative tree without following symlinks.
- The manifest records a mapping and SHA-256 for every installed file, not only `SKILL.md`.
- Unallowlisted directory names are never discovered merely because they exist below canonical `skills/`.

### Company Deep Dive order

The exact step IDs are:

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

Every completed or skipped step writes `capabilities/<step-id>.json`. A failed step persists its failure in plan/task/run state; it must not fabricate a completed result.

### Capability result

Required top-level fields:

```json
{
  "schema_version": "1.0",
  "capability": "valuation-analysis",
  "status": "completed",
  "skill": {"name": "valuation-analysis", "version": "0.2.0"},
  "method": {"name": "scenario-dcf", "version": "1.0"},
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

Rules:

- status is exactly `completed`, `skipped`, or `failed`;
- a fact has `id`, `statement`, and one or more persisted `source_ids`;
- an assumption has `id`, `statement`, `rationale`, and `materiality`;
- an estimate has `id`, `label`, `value`, `method`, and `input_ids` or explicit inputs;
- an unknown has a question/gap and impact; missing numeric data remains unknown;
- `source_ids` is the deduplicated union of referenced sources;
- `skipped` requires non-empty `skip_reason` and `missing_inputs` and must not masquerade as analysis;
- `completed` source verification, bear case, and report are mandatory in a completed demo task.

### Provider responses

Every operation, including the three additions, retains `as_of_date`, `currency`, `market`, `source`, `fixture_version` or `retrieved_at`, `is_demo: true`, and warnings. Peer records declare comparable/excluded status and reasons. Earnings records separate actual, expectation, guidance, and transcript availability. Catalyst records declare a date/window, evidence source, materiality, and uncertainty.

### Analysis safeguards

- DCF requires `WACC > terminal growth`, positive diluted shares, explicit forecast assumptions, EV-to-equity bridge, base/bull/bear cases, and an odd-dimension sensitivity grid whose center equals base assumptions.
- Comps excludes invalid denominators and records peer-selection/exclusion reasons, sample size, fiscal-period/metric comparability, and median calculations.
- Earnings quality separates accounting earnings from cash conversion and flags missing one-off/working-capital data.
- Thesis results contain confirming and disconfirming evidence plus falsifiers.
- Bear case is a mandatory independent red-team result, not a paragraph generated from the bull case.
- Source verification resolves claim source IDs and reports missing, stale, low-quality, or conflicting evidence.
- Reports never introduce facts, assumptions, estimates, risks, or sources absent from structured artifacts.

### Trigger Evals

Machine-readable Eval cases identify `expected_skills` and `excluded_skills`. Near misses share financial vocabulary with a Skill but require a different capability. Deterministic trigger evaluation verifies the metadata contract; it does not claim hosted-model accuracy.

### Environment keys

No API key or network environment key is required. v0.2 adds no credentialed Provider.

## 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Skill directory or mapped reference is missing | Init/doctor nonzero; name the missing project-relative path |
| Skill file is a symlink or escapes canonical/target root | Reject before reading or copying |
| Unallowlisted canonical Skill exists | Ignore as a release asset; do not install |
| Positive trigger case selects no intended Skill | Eval failure |
| Near-miss case selects excluded Skill | Eval failure |
| Capability status is unknown | Resume/doctor failure |
| Completed result lacks required envelope field | Resume/doctor failure |
| Fact source ID is absent from `sources.json` | Source verification warning/failure and doctor failure for completed task |
| Estimate omits method/material inputs | Result validation failure |
| Skipped result lacks reason/missing inputs | Result validation failure |
| Missing numeric input | Preserve unknown; skip bounded method or emit warning; never coerce to zero |
| DCF WACC is not greater than terminal growth | Valuation result warns/skips the invalid scenario; no infinite value |
| Comps peer denominator is zero/negative/missing | Exclude peer/metric with recorded reason |
| Earnings transcript is absent | Earnings result may complete with explicit unknown/warning; no invented call commentary |
| Bear-case or source-verification step omitted | Workflow/doctor failure |
| Completed step capability artifact is corrupt | Resume rejects; do not overwrite later artifacts |
| Completed task resume | Validate all capability/data/report bytes; append run event only |
| Third-party path appears as installed mapping | Doctor failure; no repair or execution |

## 5. Good / Base / Bad Cases

### Good

- A fresh init installs 13 allowlisted Skills and all their approved references, with one manifest mapping per file.
- A demo with complete fictional data produces 13 schema-valid capability artifacts, including a DCF sensitivity grid, comps exclusions, earnings expectation comparison, falsifiable thesis, independent bear case, and resolved sources.
- Completed resume changes only the append-only run log.

### Base

- Earnings transcript data is unavailable. `earnings-analysis` completes using actual/expectation/guidance fields, records the transcript as unknown, and avoids management-tone claims.
- One peer has negative EBITDA. Comps excludes its EV/EBITDA multiple while retaining valid metrics and the exclusion reason.
- A capability is genuinely inapplicable. It writes a valid `skipped` envelope and downstream Skills preserve the gap.

### Bad

- Treating a missing field as zero and producing a precise valuation.
- Copying one third-party Skill prompt into first-party source.
- Generating a report claim that has no claim ID/source ID in capability artifacts.
- Marking a placeholder result completed merely so resume can advance.

## 6. Tests Required

- Asset contract: exact 12 Core names plus the identification prerequisite; every Skill validates and every direct reference resolves.
- Trigger tests: positive and difficult near-miss cases for all 12 Skills; missing/ambiguous inputs.
- Result contract unit tests: fact/source, assumption, estimate, unknown, completed/skipped/failed validation.
- Analysis unit tests: statement ratios, accrual/cash conversion, DCF scenarios/sensitivity guards, peer exclusions/medians, earnings surprise/guidance, thesis falsifiers, bear case, catalyst uncertainty, and source resolution.
- Composition tests: outputs from company/business/financial/quality feed valuation/comps/earnings/thesis; report consumes only structured results.
- Workflow test: exact 13-step order, one artifact per step, mandatory stages, missing-data and skip propagation.
- Resume tests: completed immutability, failed-step restart, corrupt capability artifacts, source-ID corruption, and external symlink rejection.
- Init/doctor tests: nested Skill files, mapping hashes, missing reference, legacy/unmanaged Skill warning, and forbidden third-party mapping.
- Offline/security tests: network entry points fail closed; no API key, subprocess, third-party import/execute, outside-project read, or `.trellis/` Runtime dependency.
- Packaging acceptance: wheel-only fresh `init → doctor → demo → resume → doctor` and at least 80% Runtime statement coverage.

## 7. Wrong vs Correct

### Wrong

```python
# Missing data becomes a fact and the report can no longer distinguish evidence.
revenue = payload.get("revenue") or 0
result["findings"].append(f"Revenue was {revenue}")
```

### Correct

```python
revenue = payload.get("revenue")
if revenue is None:
    unknowns.append({
        "id": "unknown-revenue",
        "question": "What is reported revenue for the period?",
        "impact": "Growth, margins, and valuation cannot be finalized.",
    })
else:
    facts.append({
        "id": "fact-revenue",
        "statement": f"Reported revenue was {revenue}.",
        "source_ids": ["financial-statements"],
    })
```

The structured distinction lets source verification, downstream Skills, resume, doctor, and report assembly enforce the same evidence boundary.
