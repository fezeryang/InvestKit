# InvestKit

InvestKit is an installable, offline-first investment-research AI Agent Harness. The v0.3 working tree can analyze a user-supplied structured bundle or acquire an approved, permission-gated A-share evidence snapshot through the same 13-stage workflow used by the deterministic demo. It persists evidence, calculations, unknowns, risks, and a sourced report so the work can be inspected, resumed, and diagnosed later.

This is a bounded research capability, not a trading or production-release claim. Approved symbol mode currently fuses official SSE identity/announcement metadata with permission-gated Guangfa F10, financial-comparison, and relative-valuation data. InvestKit does not place orders, transfer funds, give individualized investment advice, or promise returns.

## Install from GitHub

The executable product is one Python 3.11+ CLI. Install it directly from the
authoritative GitHub repository:

```bash
pipx install git+https://github.com/fezeryang/InvestKit.git
investkit --help
```

Codex has a tested native Skill projection. Claude Code, Cursor, and other
shell-capable AI environments can use the same installed CLI without duplicating
investment logic or credentials. Native Claude/Cursor adapters are not yet claimed.
See [distribution and platform support](docs/product/distribution.md).

## What v0.3 can do

The current Codex-first Runtime provides three governed input modes:

- `demo`: the fictional Aurora Lantern Works fixture for deterministic evaluation;
- `imported`: a validated project-local JSON bundle prepared from lawful, dated evidence for one real issuer;
- `symbol`: approved Providers acquire and identity-check a point-in-time snapshot after explicit network permission.

Both modes run `company-deep-dive` in this order:

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

Every stage writes a structured capability result. Facts, assumptions, estimates, unknowns, findings, risks, warnings, and source IDs remain distinct. A method with insufficient evidence is skipped with explicit missing inputs or records an unknown; absent numbers are never silently converted to zero. The independent bear case and source-verification gate run before report assembly.

## Requirements and installation

- Python 3.11 or newer.
- Setuptools 68 or newer when building from source.
- No Runtime third-party dependency. Demo/imported paths stay offline; live Provider paths require an environment credential where applicable and `--allow-network`.

From the repository root, install the checkout in editable mode:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

Or build and install the v0.3 wheel into a separate environment:

```bash
python3 -m pip wheel --no-build-isolation --no-deps --wheel-dir dist .
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps \
  dist/investkit-0.3.0-py3-none-any.whl
```

The `--no-build-isolation`, `--no-deps`, and `--no-index` flags keep these examples offline; install the build backend in advance on a disconnected machine. On Windows, use `.venv\Scripts\python.exe` and `.venv\Scripts\investkit.exe`.

## Zero to real-company research

Store approved provider credentials in a private mode-600 `.env`, then run the target-only command:

```bash
investkit research \
  --symbol 603868.SH \
  --question "分析公司的基本面、财务质量、行业相对估值、市场表现、催化剂与主要风险。" \
  --allow-network
```

The Harness automatically uses every ready approved provider: SSE identity/announcements, Guangfa F10 and target/industry valuation, and CICCWM market, financial, news, and abnormal-trading evidence. Add `--peer 002032.SZ` only when the analyst has selected a defensible operating peer and wants comparative financials. All records are fused into one immutable bundle, all 13 capabilities run, and unsupported DCF, consensus, transcript, or catalyst inputs remain explicit unknowns. See the [Harness value proposition](docs/product/harness-value-proposition.md) for why this differs from invoking the underlying Skills directly.

For a fully offline user-supplied bundle, create an empty project, initialize it, and copy the published bundle template into that project:

```bash
source .venv/bin/activate
mkdir company-research
cd company-research

investkit init
investkit doctor
python -c "from pathlib import Path; from shutil import copy2; from investkit.assets import default_source_root; Path('inputs').mkdir(exist_ok=True); copy2(default_source_root() / 'schemas/research-bundle-v1.template.json', 'inputs/company.json')"
```

Edit `inputs/company.json` before running research. The shipped template is structurally usable but contains placeholders, not evidence for a real issuer. At minimum:

1. Replace the top-level version, creation/retrieval/as-of dates, currency, market, warnings, and exact security identity.
2. Create stable source records with publisher, exact title, type, locator, dates, quality, freshness, access notes, and license/reuse notes.
3. Populate all nine operation records. Each record has `data`, `source_ids`, and `warnings`; every source ID must resolve to the top-level registry.
4. Keep unsupported fields as explicit `null`, empty arrays, or recursively gap-only objects, and add limitations. Do not invent a price, forecast, WACC, peer set, consensus estimate, transcript, or catalyst to make an analysis run.
5. Remove credentials and secrets. Source locators are provenance metadata only; the Runtime does not fetch them.

The authoritative contract is [`schemas/research-bundle-v1.schema.json`](schemas/research-bundle-v1.schema.json), with an annotated starting point in [`schemas/research-bundle-v1.template.json`](schemas/research-bundle-v1.template.json). Input must be a UTF-8 JSON regular file no larger than 2 MiB inside the initialized project. Symlinks, root escapes, duplicate keys, unresolved source IDs, unsupported versions, invalid date ordering, non-finite numbers, and credential-like content fail closed.

Run the research question against the completed bundle:

```bash
investkit research \
  --input inputs/company.json \
  --question "What does the supplied evidence support about this company's financial durability, valuation limits, and key risks?"
```

The command prints a task ID such as `research-20260717T120000000000Z-a1b2c3d4e5` and the report path. Review the report together with the structured artifacts under `workspace/research/<task-id>/`; the report alone is not sufficient evidence for an investment decision.

Resume or inspect the imported task later, then diagnose the project:

```bash
investkit research --resume \
  research-20260717T120000000000Z-a1b2c3d4e5
investkit doctor
```

The validated input is snapshotted into the task before analysis. Resume uses that snapshot rather than the original mutable file, so changing or deleting `inputs/company.json` does not silently change prior research. A completed resume preserves analytical artifacts and the report and appends only a run-log event.

## Pinned Microsoft acceptance example

The repository includes [`fixtures/acceptance/microsoft-fy2025.json`](fixtures/acceptance/microsoft-fy2025.json), a pinned Microsoft Corporation FY2025 Form 10-K acceptance bundle. It contains two dated SEC/issuer-filing source records and reported FY2024–FY2025 financial facts. It intentionally omits current price, peers, forecasts, WACC, consensus expectations, guidance comparison, transcript evidence, and future catalysts.

From a checkout, copy it into an initialized project and run:

```bash
mkdir -p inputs
cp /path/to/InvestKit/fixtures/acceptance/microsoft-fy2025.json \
  inputs/microsoft-fy2025.json
investkit research \
  --input inputs/microsoft-fy2025.json \
  --question "What does the supplied FY2025 filing support about Microsoft's financial durability and risk?"
```

This example tests real-issuer identity, source joins, supported financial calculations, disclosed skips, persistence, resume, and doctor. It is historical as of 2025-06-30, was assembled with a 2026-07-16 retrieval timestamp, and is deliberately unsuitable for a current investment recommendation.

## Demo compatibility

The deterministic fictional path remains available:

```bash
investkit demo research
investkit demo research --resume \
  demo-20260717T120000000000Z-a1b2c3d4e5
```

Demo artifacts are marked `is_demo: true` and disclose that their company and values are fictional. Imported artifacts are marked `input_mode: imported`, identify the supplied issuer, and disclose that InvestKit did not independently fetch or guarantee the input.

## Durable artifacts

Each run creates `workspace/research/<task-id>/`:

```text
task.json              question.md
plan.json              loaded-specs.json
installed-skills.json  input/research-bundle.json  # imported mode only
data/*.json            capabilities/*.json
sources.json           assumptions.json
findings.json           risks.json
run-log.json           report.md
```

The task records the input mode, question, security query, source/Skill/spec snapshots, and—in imported mode—the canonical bundle hash and provenance. Resume validates persisted state before skipping completed work. Corrupt, externally linked, or source-inconsistent artifacts fail closed.

## Diagnostics and migration

`investkit doctor` is read-only. It reports `PASS`, `WARN`, and `FAIL` checks and exits nonzero for critical failures. In addition to installation, standards, Workflow, Skill hashes, and demo-fixture checks, v0.3 diagnostics validate imported bundle hashes and schema, source joins, Provider records, capability/report mode disclosures, task lifecycle, stale evidence warnings, and artifact boundaries. Doctor reports problems but does not repair them.

Running `investkit init` against an unmodified v0.2 initialized project performs the governed v0.3 ownership migration. InvestKit-owned files are updated only when their recorded prior hashes still match; conflicting user changes are preserved and reported instead of overwritten. Completed v0.2 demo tasks remain historical task artifacts rather than being rewritten.

## Current limits

v0.3 makes local and approved live real-company evidence usable. The current limits include:

- live acquisition currently covers SSE identity/announcement metadata, target-only Guangfa F10 and industry-relative PE/PB, optional peer comparative indicators, plus CICCWM prices, bounded financial history and target-linked event context; it does not yet provide reliable DCF inputs, transcripts, or licensed point-in-time consensus;
- no raw PDF/HTML/OCR/LLM extraction or cross-issuer normalization guarantee;
- no claim that user-supplied facts are accurate or independently corroborated;
- one host adapter (`codex`), with no completed Claude/Cursor delivery path;
- no package add/update/uninstall lifecycle, frontend, cloud sync, backtest engine, Quant Pack, or Portfolio & Risk Pack;
- no brokerage connectivity, trade execution, individualized advice, or return guarantee.

See the [product roadmap](docs/product/roadmap.md) and [capability map](docs/product/investment-capability-map.md) for the implemented boundary and next gates.

## Source and development boundaries

Repository-root `skills/`, `agents/`, `workflows/`, `specs/`, `schemas/`, `packages/`, `fixtures/`, and `workspace-template/` are authoritative first-party source. Wheels carry read-only delivery copies under `share/investkit`; `.agents/skills/` is generated installation state. `.trellis/` manages InvestKit development and is not a Runtime dependency.

Raw third-party material under `third_party/raw/` is untrusted research evidence. It is neither installed nor executed. Only governed, independently implemented first-party assets may enter product source after provenance, license, security, testing, and owner-release review.

To run the local test suite from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python3 -m unittest discover -s tests -v
```

This is a verification command, not a claim that a particular checkout has passed release gates. Product requirements and boundaries are documented in the [PRD](docs/product/PRD-v0.1.md), [architecture](docs/product/architecture.md), [roadmap](docs/product/roadmap.md), and [security policy](docs/security/security-policy.md).
