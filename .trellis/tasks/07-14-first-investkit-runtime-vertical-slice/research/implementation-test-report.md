# InvestKit Runtime vertical-slice implementation and test report

Report date: 2026-07-15

## Scope delivered

The implementation provides the owner-approved Codex-first, Python 3.11+
vertical slice with no runtime third-party dependencies:

- locally installable `investkit` package and console command;
- idempotent, create-once `init` with a Codex adapter, project configuration,
  verified install manifest, six Skill mappings, and durable workspace;
- seven versioned research specs, six governed first-party Skills, the ordered
  offline workflow, and a clearly fictional first-party fixture;
- six-operation offline Demo Provider with normalized provenance, missing values,
  and warnings;
- structured research tasks, atomic JSON persistence, ordered run events,
  deterministic analysis/reporting, failure records, and safe resume;
- read-only `doctor` diagnostics with explicit `PASS`, `WARN`, and `FAIL` results;
- self-contained wheels carrying delivery copies of authoritative root assets
  under `share/investkit`.

No Claude/Cursor adapter, live or credentialed Provider, brokerage action,
transaction, funds transfer, network fetch, third-party execution, backtest,
frontend, or lifecycle placeholder was added.

## Runtime architecture

```text
CLI
→ validated repository or wheel asset root
→ project boundary + create-once initializer
→ Codex adapter + config/install manifest
→ Demo Provider + versioned specs/installed Skill snapshots
→ deterministic workflow and analysis
→ atomic task artifacts + run log + Markdown report
→ resume validation / doctor diagnostics
```

`src/investkit/assets.py` is the shared source contract for Skill/spec names,
version parsing, canonical workflow/fixture paths, and safe source-root discovery.
In a checkout it selects the authoritative repository root. In an installed
wheel it selects a complete delivery tree below the installation data prefix.
The Runtime does not import or resolve `.trellis/`, `third_party/raw/`, or
`adapted/skills/`.

## Initialization and ownership

`investkit init` uses the current directory as project root. It copies only the
six approved `SKILL.md` files into `.agents/skills/`, writes InvestKit-owned
configuration, copies the workspace README, creates `workspace/research/`, and
records source/target SHA-256 mappings plus spec versions/checksums. Existing
identical files are skipped. Differing files are preserved, reported, and cause a
nonzero result when the required installation cannot be completed safely.

The repository-root asset directories remain authoritative. Wheel data files are
release delivery artifacts and never reverse-sync into source.

## Research and resume behavior

Each demo creates a unique task with `created → running → completed` or `failed`
state and persists the required question, plan, loaded specs, installed Skills,
normalized data, source lineage, assumptions, findings, risks/unknowns, run log,
task record, and report. Source records identify the canonical fictional fixture,
its checksum, and the local normalized artifacts supporting the report.

Resume validates a conservative task ID, plan/workflow identity, question,
Skill/spec snapshots, completed-step artifacts, and source/installation checksums.
It skips completed steps and preserves their files. Completed-task resume changes
only the run log by appending an inspection event. Corrupt or materially
incomplete state fails with an actionable, secret-redacted error.

## Doctor coverage

Doctor checks:

1. Runtime/config version compatibility.
2. Project configuration ownership and structure.
3. Codex host selection and adapter configuration.
4. Configured first-party source lineage.
5. Workspace existence and mode/access writability.
6. Canonical first-party Skill sources.
7. Installed Codex Skills and unmanaged user-owned Skills.
8. Install-manifest structure.
9. Exact mapping paths and source/target checksums.
10. Seven required spec versions and checksums.
11. Offline workflow identity, version, and order.
12. All six Demo Provider operations and required metadata.
13. Explicit fixture missing values/warnings.
14. Forbidden/unapproved installation evidence.
15. Likely credentials in InvestKit-owned JSON, question, and report state without
    echoing suspected values.
16. Task IDs, symlink boundaries, task/plan/run-log structure, completed
    artifacts, report references, and data references/content.

Warnings alone exit zero. Any critical failure exits nonzero. Doctor does not
repair or overwrite state.

## Security findings addressed

- Task IDs and every derived task/source/project path are constrained to their
  approved root.
- Doctor rejects symlinked Skill/task paths that could escape the project and
  does not follow them for content reads.
- Common named and bare credential patterns are redacted from workflow errors;
  diagnostics identify only the affected owned path.
- Network calls, shell execution, telemetry, API keys, brokerage operations, and
  third-party/draft install sources are absent.
- Completed tasks fail diagnostics when required artifacts or referenced JSON
  data are missing or corrupt.

## Verification evidence

Final consolidated verification:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python3 -m unittest discover -s tests
Ran 47 tests in 17.875s — OK

COVERAGE_FILE=/tmp/investkit-final2.coverage \
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python3 -m coverage run --source=src/investkit \
  -m unittest discover -s tests
Ran 47 tests in 24.618s — OK

COVERAGE_FILE=/tmp/investkit-final2.coverage \
  python3 -m coverage report --show-missing --fail-under=80
TOTAL 1681 statements, 255 missed, 85% — PASS

pyright src tests
0 errors, 0 warnings, 0 informations

PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q src tests
PASS

git diff --check
PASS
```

The 47 tests comprise 7 first-party asset/Provider contracts, 25 CLI/init/doctor
contracts, 14 research/task/resume/report contracts, and 1 isolated packaging
contract. No test is skipped. Ruff was not installed, so no Ruff result is
claimed.

The packaging regression copies only release inputs to a temporary build tree,
builds a wheel without dependency downloads, installs it into a fresh virtual
environment, and runs `init`, `doctor`, `demo research`, and completed-task
`--resume` in a fresh project with no repository asset access.

The retained final wheel has SHA-256
`7c2c72e340af587c2a863a2d790da80724941730fd7d46e5b9f86f40d298d14b`.
It was installed with `--no-index --no-deps` into a new virtual environment.
The following commands all returned exit code 0 in a new project:

```text
investkit init
investkit doctor
investkit demo research
investkit demo research --resume demo-20260715T145722193554Z-bec26e7f59
```

Doctor reported no `FAIL` before or after the demo. Its single expected `WARN`
states that the fixture deliberately contains explicit missing values and
actionable warnings. The retained sample task is:

```text
/tmp/investkit-final-acceptance-20260715/project/workspace/research/
  demo-20260715T145722193554Z-bec26e7f59/
```

The task contains all required root artifacts and six normalized data JSON
files. A second completed-task resume left the report and all six data-file
SHA-256 values unchanged (`HASHES_PRESERVED=true`) while appending a resume
event to the run log.

Static verification found no Runtime import/path dependency on `.trellis/`, no
network or subprocess import in `src/investkit`, no runtime dependency in
`pyproject.toml`, and no hardcoded credential match. Generated `build/` and
`src/investkit.egg-info/` directories were removed after verification.

## Final acceptance status

**PASS — all thirteen owner completion conditions are met.**

1. The single Codex adapter implements project detection, description,
   installation target selection, configuration, and doctor integration.
2. `init` is safe to repeat and preserves conflicting user files.
3. Six first-party Skills are discovered from authoritative source and installed.
4. Seven versioned specs are loaded and recorded with checksums.
5. The offline demo research task completes.
6. All required task artifacts and normalized data are persisted.
7. Completed and incomplete tasks can be safely restored; corrupt tasks fail.
8. Doctor detects healthy, warning, and critical abnormal states.
9. All 47 tests pass with 85% Runtime statement coverage.
10. Runtime operation needs neither network access nor an API key.
11. Forbidden third-party/draft source roots are rejected before read/install;
    no third-party asset is executed or installed.
12. `.trellis/` is development tooling only and is not a Runtime dependency.
13. `README.md` documents installation, the complete demo, resume, diagnostics,
    artifacts, and current limitations.

The implementation remains uncommitted pending project-owner review and commit
group selection. Nothing was pushed.

## Current limitations

- Codex is the only host adapter.
- The only Provider is the bundled fictional offline dataset.
- Resume is local filesystem restoration; there is no cloud/cross-device sync.
- `add`, `update`, and `uninstall` are intentionally unavailable.
- No real security, market, company, price, financial, or valuation claim is made
  by the fixture or report.
