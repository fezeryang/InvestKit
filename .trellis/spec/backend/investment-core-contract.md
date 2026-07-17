# InvestKit Investment Core Contract

## 1. Scope / Trigger

Use this contract when adding or changing an Investment Core Skill, its trigger/Eval data, structured capability results, the `company-deep-dive` Workflow, Demo or File Provider datasets needed by those capabilities, report assembly, task resume validation, or doctor checks.

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
- A structured InvestKit forecast records method, as-of date, and forecast periods. Broker consensus remains a separate point-in-time record requiring observation time, positive contributor count, period definitions, valid low/high dispersion bounds, and optional revision evidence; it is never inferred from guidance or an InvestKit estimate.
- An industry benchmark requires a named classification, as-of date, positive constituent count, and per-metric target, industry median, percentile, and aligned definition. Missing vintage or definitions invalidate the benchmark rather than degrading it into a generic sector comparison.
- Completed DCF output exposes a bear/base/bull per-share scenario range explicitly labeled as non-guaranteed; original disclosures remain optional escalation evidence rather than a prerequisite for normalized forecast and valuation analysis.
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

## v0.3 Imported-Evidence Analysis Amendment

This amendment supersedes v0.2 demo-specific language when reusable capability
methods receive imported evidence. Demo-specific fixture warnings remain required in
demo mode.

### 1. Scope / Trigger

Use this amendment when changing imported-mode capability analysis, operation-to-
capability input composition, source attribution, unknown/skip semantics, finite
calculations, source verification, or report claims.

The analytical boundary is evidence-led: a capability may transform validated facts
and explicit assumptions, but it may not fill missing company characteristics,
management commentary, market expectations, guidance, transcript content, price,
peers, catalysts, or valuation inputs from generic knowledge or demo prose.

### 2. Signatures

The public capability dispatcher remains provider-neutral:

```python
analyze_capability(
    capability: str,
    inputs: Mapping[str, Any],
) -> dict[str, Any]

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

validate_capability_result(
    value: Mapping[str, Any],
    *,
    expected: str,
) -> None
```

Workflow composition passes the complete relevant Provider-operation records and
their source sets; a capability must not select only the first source ID.

### 3. Contracts

#### Neutral reusable analysis

- Reusable methods branch on `input_mode`; only demo mode may call evidence fictional
  or name the demo issuer.
- Company profile facts such as management, capital allocation, competitive
  position, payer/customer structure, and value proposition exist only when the
  profile record supplies them. Absence produces a named unknown with impact, not a
  fact, finding, risk, or default narrative.
- Earnings expectation, guidance, and transcript commentary exist only when their
  respective fields are supplied. A missing expectation cannot become zero or a
  consensus assumption and cannot yield a beat/miss comparison.
- Thesis drivers, falsifiers, KPIs, and bear mechanisms are constructed from
  persisted company, financial, valuation, price, earnings, catalyst, and explicit
  profile evidence. They never inject Aurora-specific tender, municipal-payer,
  backlog, input-cost, or other fixed operating narratives.

#### Source attribution

Every fact, sourced finding, and sourced risk carries the deduplicated complete
source set of the Provider records used to produce it. Source order is canonical and
does not affect the result. Identity may join all sources supporting the identity
record; a financial ratio joins the full financial-operation set; a valuation result
joins every active price and valuation-input source; a cross-capability thesis claim
joins the union of the upstream evidence it actually uses.

The capability envelope `source_ids` is the sorted/deduplicated union of every source
reference in facts, findings, and risks. Every ID must resolve to `sources.json`.
Completed findings and risks, like facts, require a non-empty stable ID, statement,
and one or more persisted source IDs.
Source verification examines facts, findings, and risks, preserves all registry
records, and reports missing, unresolved, stale, low-quality, conflicting, or
source-free claims without inventing resolution. A user-supplied freshness adjective
cannot override dates: source verification derives a stale condition when an
as-of/publication date is more than 180 days older than that source's persisted
retrieval date.

#### Numerical integrity and missing inputs

All input numbers and every emitted numeric estimate, calculation, scenario, and
sensitivity cell are finite JSON numbers. Division requires a finite nonzero
denominator. DCF additionally requires positive shares and `WACC > terminal growth`.
Invalid or absent inputs produce unknowns, warnings, exclusions, or a valid skipped
result; they never produce `NaN`, Infinity, zero-filled evidence, or false precision.

Calculations supported by a financial bundle may include statement margins,
cash-conversion/accrual measures, and free cash flow when their named inputs exist.
Period labels alone are not financial evidence and produce a valid skip with no
calculation finding. Finding copy is assembled from diagnostics actually calculated;
available working-capital/current-liquidity fields may not be described as missing.
Valuation, comps, earnings surprise, guidance comparison, and catalyst timing remain
unknown/skipped when their required evidence is absent. A completed stage may still
be analytically limited when it explicitly records those gaps; mandatory bear-case,
source-verification, and report stages must remain contract-valid.

A source-free explicit-gap profile produces valid company/business skips rather than
an exception. An imported thesis requires actual persisted operating drivers or
calculated estimates, analytical findings, and disconfirming risk evidence; it never
uses a generic operating-performance fallback. When that evidence is absent, thesis
and bear case are valid disclosed skips, source verification still completes, and a
bounded `complete_with_gaps` report may be assembled. If the thesis completes, the
independent bear case must complete before reporting; demo mode retains its mandatory
completed bear-case gate.

#### Imported report boundary

The report names the security/company, analyst question, as-of date, project-relative
input provenance, and material limitations. It states that evidence was imported and
not independently guaranteed. It emits only structured upstream claims and source
IDs, escapes untrusted Markdown/HTML/URI syntax, and contains no buy/sell/hold action
recommendation, guaranteed return, deterministic price prediction, brokerage action,
or funds-transfer instruction. Ordinary issuer names such as “Best Buy” and benign
phrases such as “Market Data” are not false positives; action language is evaluated
in investment-instruction context. The boundary covers both English and Chinese
buy/sell/hold/build-position/increase/reduce-position/stop-loss/action wording.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Profile omits management/capital allocation/competition/payer/value proposition | Emit explicit unknowns; no fact/finding/risk about the absent topic |
| Source-free profile contains only explicit gaps | Company and business-model stages skip with reasons; workflow does not fail |
| Financial periods contain labels but no finite statement values | Financial and earnings-quality stages skip; emit no calculation claim |
| Earnings expectation is absent | No surprise/beat/miss comparison and no consensus assumption |
| Guidance or transcript is absent | Record the bundle-not-supplied gap; no management-tone claim |
| Price or valuation inputs are absent | Skip bounded valuation or emit unknown; never substitute zero |
| Peer denominator is missing, non-finite, zero, or invalid | Exclude that peer/metric with a reason |
| WACC, growth, shares, or forecast guard fails | No DCF estimate/sensitivity output; disclose invalid/missing inputs |
| Calculation would emit NaN or Infinity | Reject/skip the result before persistence |
| One operation has multiple source IDs | Preserve their complete deduplicated set on every derived claim |
| Input source order changes | Capability semantics and canonical source attribution remain unchanged |
| Fact/finding/risk references unknown source | Capability validation/workflow/doctor fail |
| Source verification finds stale/low-quality/conflicting evidence | Preserve it and disclose the issue; do not silently drop or resolve it |
| Upstream evidence has no real thesis driver/finding/disconfirming risk | Thesis and bear case skip; never inject a generic fallback |
| Imported report contains raw HTML, Markdown link/image injection, unsafe URI, or investment action instruction | Escape/neutralize at assembly and fail doctor if unsafe text persists |

### 5. Good / Base / Bad Cases

#### Good

- Microsoft FY2025 10-K financials produce supported margin, cash-conversion, and
  free-cash-flow calculations, each joined to the SEC filing/index sources actually
  carried by the relevant operation.
- Identity supported by both a filing index and filing record retains both sources,
  independent of source order.
- A report distinguishes verified filing facts, derived calculations, explicit
  unknowns, method limitations, and research-only conclusions.

#### Base

- The issuer bundle supplies filings but no price, forecast, peers, consensus,
  guidance, transcript, or catalysts. The 13-stage workflow remains auditable:
  supported methods complete, unsupported methods skip or emit unknowns, and the
  final report clearly states why it is not a complete investment decision basis.
- A profile provides a product description but no competitive assessment. The
  product description may be a fact; competitive position remains unknown.
- Two sources support one period. Every resulting financial fact retains both; no
  preferred-source policy is invented by list order.

#### Bad

- Emitting “management is disciplined” because capital allocation fields are absent.
- Treating missing expectations as `0` and reporting a positive surprise.
- Using only `source_ids[0]` for a multi-source calculation.
- Persisting `Infinity` because terminal growth equals or exceeds WACC.
- Reusing demo-specific payer, tender, backlog, or cost narratives for an imported
  issuer.

### 6. Tests Required

- Imported analysis tests prove neutral wording and explicit unknowns for every
  absent profile, expectation, guidance, transcript, price, peer, and catalyst field.
- Sparse/gap-only tests cover source-free profile data, period-label-only financials,
  identity-only upstream evidence, conditional bear-case gating, and a completed
  report whose skips contain none of the removed generic fallback prose.
- Multi-source tests cover identity, profile, financial, price/valuation, earnings,
  catalyst, thesis, bear case, and source verification; source-order permutations
  must produce equivalent source sets.
- Numerical tests cover non-finite contract inputs/outputs, zero or invalid
  denominators, DCF guards, finite sensitivity cells, and no `NaN`/Infinity in any
  persisted machine artifact.
- Source-verification tests resolve facts, findings, and risks against the complete
  registry and retain stale, low-quality, contradiction, and unresolved evidence,
  including an old objective date mislabeled `current`.
- Report tests cover issuer identity/question/as-of/provenance/limitations,
  imported/non-guaranteed disclosure, no-new-claims, neutral research language,
  Best Buy/Market Data false-positive regressions, and markup/unsafe-URI/action-
  instruction rejection.
- Real-issuer acceptance verifies supported Microsoft FY2025 formulas against the
  pinned bundle, all intentionally absent evidence as unknown/skipped, all 13 stage
  artifacts, source joins, completed resume immutability, and doctor.
- Demo regression tests retain fictional disclosure and prior deterministic results.

### 7. Wrong vs Correct

#### Wrong

```python
# The first source wins and a missing expectation becomes a false comparison.
source_id = earnings["source_ids"][0]
expectation = earnings.get("expectation") or 0
findings.append({
    "statement": f"EPS surprise was {actual - expectation}",
    "source_ids": [source_id],
})
```

#### Correct

```python
sources = canonical_source_union(earnings["source_ids"])
expectation = earnings.get("expectation")
if expectation is None:
    unknowns.append({
        "question": "What market expectation applied to this period?",
        "impact": "No earnings surprise comparison can be made.",
    })
else:
    findings.append({
        "statement": describe_finite_surprise(actual, expectation),
        "source_ids": sources,
    })
```

Missing evidence changes the conclusion boundary; it never changes the evidence into
a convenient default.
