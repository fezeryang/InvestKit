# InvestKit

InvestKit is an installable, offline-first investment-research AI Agent Harness. The current working tree contains the v0.1 Codex Harness baseline and the v0.2 Investment Core Pack, implemented and verified locally. This is not a claim of release or production readiness.

InvestKit is research software, not a trading bot. It does not connect to a brokerage, place orders, sign transactions, transfer funds, fetch live prices, or promise investment returns.

## What v0.2 adds

The immediate product milestone is capability-first: define professional research methods and structured evidence contracts before adding live-data infrastructure.

Initialization discovers one Runtime prerequisite, `security-identification`, and exactly 12 Investment Core Skills:

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

The `company-deep-dive` Workflow runs the prerequisite and all 12 Core Skills as 13 ordered stages:

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

Each stage writes a structured capability result. Facts, assumptions, estimates, unknowns, findings, risks, warnings, and source IDs remain distinct. The independent bear case and source-verification gate are mandatory before a completed report.

## Requirements

- Python 3.11 or newer.
- Setuptools 68 or newer when building from source.
- No Runtime third-party dependencies, API keys, or network access for the offline path.

The commands below use `--no-build-isolation` and `--no-deps` so pip does not try to download build or Runtime packages. Install the build backend in advance on a fully disconnected machine.

## Local installation

From the repository root, install the checkout in editable mode:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

Or build a self-contained wheel and install it into a separate environment:

```bash
python3 -m pip wheel --no-build-isolation --no-deps --wheel-dir dist .
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps \
  dist/investkit-0.2.0-py3-none-any.whl
```

On Windows, use `.venv\Scripts\python.exe` and `.venv\Scripts\investkit.exe`. A wheel carries read-only delivery copies below `share/investkit`; the repository-root `skills/`, `specs/`, `workflows/`, `fixtures/`, `agents/`, `packages/`, and `workspace-template/` directories remain authoritative source.

## Zero-to-demo flow

Create or enter an empty user project, then run:

```bash
source .venv/bin/activate
mkdir investkit-demo
cd investkit-demo

investkit init
investkit doctor
investkit demo research
```

`demo research` executes `company-deep-dive` against the fictional Aurora Lantern Works fixture and prints a task ID such as `demo-20260716T120000000000Z-a1b2c3d4e5`. Resume that exact task in a later process:

```bash
investkit demo research --resume \
  demo-20260716T120000000000Z-a1b2c3d4e5
investkit doctor
```

On Windows, activate with `.venv\Scripts\activate`. `init` and `doctor` use the current directory as the project root.

## What initialization creates

```text
.investkit/
  config.json
  install-manifest.json
.agents/
  investkit.json
  skills/
    <security-identification + 12 Core Skills>/
      SKILL.md
      agents/openai.yaml
      references/*
workspace/
  README.md
  research/
```

Initialization is create-once and idempotent. Identical files are reported as `SKIP`; a conflicting existing user file is preserved and reported as `WARN`, with a nonzero result when it blocks safe initialization. The manifest records one verified source-to-target mapping and SHA-256 hash per installed file. Unallowlisted, raw, adapted, or symlinked content is not a first-party install source.

## Durable research artifacts

Each run creates `workspace/research/<task-id>/` with the original v0.1 durable root plus v0.2 capability artifacts:

```text
task.json              question.md
plan.json              loaded-specs.json
installed-skills.json  data/*.json
sources.json           assumptions.json
findings.json          risks.json
run-log.json           report.md
capabilities/<stage-id>.json
```

Every completed or validly skipped stage has one capability envelope. A skip needs a reason and missing-input list; missing numeric data remains unknown and never becomes zero. Failures retain task, plan, completed-stage artifacts, and run evidence.

Resume validates the task ID, workflow order, result schemas, source IDs, and completed artifacts before skipping a stage. A completed-task resume preserves data, capability results, normalized indexes, and report bytes; only the append-only run log receives a resume event.

All bundled company, security, peer, earnings, catalyst, price, financial, and valuation values are fictional demo data marked `is_demo: true`. The report must disclose that the data is neither live nor real-time and must contain no buy/sell instruction or guaranteed-return language.

## Diagnostics

`investkit doctor` is read-only. It prints `PASS`, `WARN`, and `FAIL` checks and exits nonzero when a critical check fails. Its v0.2 contract covers:

- Runtime/configuration compatibility and the Codex adapter;
- workspace existence and writability;
- the exact 13-Skill allowlist and every nested installed-file hash;
- seven research-standard versions and checksums;
- the `company-deep-dive` identity and 13-stage order;
- offline Demo Provider and fixture metadata;
- capability-result schemas, completion/skip states, and source-ID resolution;
- mandatory bear-case, source-verification, and report stages;
- forbidden installation evidence and likely credentials without echoing values;
- task IDs, symlink boundaries, task/run records, resume state, and artifact integrity.

Unmanaged user-owned Codex Skills are warnings and are not modified. Doctor does not repair failures.

## Current limits and roadmap

The current Runtime supports one host adapter (`codex`) and the commands `init`, `doctor`, `demo research`, and `demo research --resume`. `add`, `update`, and `uninstall` remain future lifecycle capabilities. There is no frontend, cloud synchronization, live Provider, brokerage integration, backtest engine, or multi-platform synchronization in v0.2.

The planned capability order is:

```text
Investment Core Pack
→ Advanced Research Pack
→ Quant Pack
→ Portfolio & Risk Pack
→ capability-driven real-data Provider expansion
```

A future Provider must serve a named capability gap behind InvestKit's unified interface. Credentialed Providers remain opt-in, preserve provenance and vendor constraints, and never gain trading or funds-transfer authority.

See the honest current/future status of each research domain in [`docs/product/investment-capability-map.md`](docs/product/investment-capability-map.md).

## Source and development boundaries

Authoritative product source lives under `skills/`, `agents/`, `workflows/`, `specs/`, `packages/`, `fixtures/`, and `workspace-template/`. Platform paths such as `.agents/skills/` are generated installation state. `.trellis/` manages InvestKit development and is not imported, copied, or required by the Runtime.

Raw third-party material is untrusted research evidence. It is not installed or executed. Only governed, independently implemented first-party assets may enter the product source after the required provenance, license, security, testing, and owner-release review.

To run the local verification suite from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python3 -m unittest discover -s tests -v
```

This command is an instruction, not a claim about the current result. Product requirements and boundaries are documented in [`docs/product/PRD-v0.1.md`](docs/product/PRD-v0.1.md), [`docs/product/architecture.md`](docs/product/architecture.md), the [product roadmap](plans/product-development-roadmap.md), and [`docs/security/security-policy.md`](docs/security/security-policy.md).
