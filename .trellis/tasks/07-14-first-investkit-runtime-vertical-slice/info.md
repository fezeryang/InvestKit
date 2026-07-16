# Technical design: first InvestKit Runtime vertical slice

## Runtime data flow

```text
CLI
→ project-root boundary validation
→ config + install manifest
→ CodexAdapter
→ canonical skills/specs/workflow/fixture
→ DemoProvider
→ research workflow
→ task repository
→ report + run log
→ doctor validation
```

`.trellis/`, `third_party/raw/`, and `adapted/skills/` do not appear on this data path.

## Planned source layout

```text
pyproject.toml
src/investkit/
  __init__.py
  __main__.py
  assets.py
  cli.py
  config.py
  doctor.py
  errors.py
  filesystem.py
  models.py
  platforms/base.py
  platforms/codex.py
  providers/base.py
  providers/demo.py
  research/analysis.py
  research/report.py
  research/tasks.py
  research/workflow.py
skills/<six-core-skills>/SKILL.md
specs/<seven-standards>.md
workflows/offline-company-research.json
fixtures/demo/<fictional-security>.json
workspace-template/README.md
agents/README.md
packages/README.md
tests/
```

Exact module grouping may be simplified during implementation when doing so preserves the contracts and keeps files readable.

## Initialized project layout

```text
.investkit/
  config.json
  install-manifest.json
.agents/
  investkit.json
  skills/<six-installed-skills>/...
workspace/
  README.md
  research/<task-id>/...
```

## Ownership and overwrite policy

- Canonical source files are read-only inputs.
- The install manifest records relative source/target paths and SHA-256 hashes.
- New InvestKit-owned mutable JSON uses atomic temp-file replacement inside the project root.
- Installation/config files are create-once: identical files are skipped; differing existing files are preserved and reported as warnings or failures.
- Resume may update only `task.json` and `run-log.json` unless an earlier step is genuinely incomplete; completed report/data artifacts are not rewritten.

## Error and exit policy

- Expected user/configuration errors raise typed `InvestKitError` subclasses and render one concise message.
- `init` returns nonzero only when required initialization cannot be completed safely.
- `doctor` returns nonzero when any check is `FAIL`.
- Demo workflow exceptions write a failed task state/run event before returning nonzero.
- No exception output includes secrets or stack traces by default.

## Time and serialization

- UTC ISO-8601 timestamps with `Z` suffix.
- Stable, indented, UTF-8 JSON with sorted keys where deterministic comparison matters.
- Dates use `YYYY-MM-DD`.
- Checksums use lowercase SHA-256 hex.

## Security notes

- Resolve and validate every derived path with `Path.resolve()` plus ancestry checks.
- Accept only conservative task-ID characters.
- Never shell out from Runtime code.
- Do not import networking modules in the provider/workflow path.
- Secret scanning is restricted to InvestKit-owned state and reports only the file/check class, never the suspected value.
- Third-party detection relies on manifest/source lineage and InvestKit ownership markers; unrelated unmanaged Codex Skills are warnings, not automatically accused as malicious.

## Verification layers

1. Unit tests for models, provider, analysis, paths, spec/Skill contracts.
2. Integration tests for init, manifests, resume, failure persistence, and doctor faults.
3. CLI subprocess tests for exit codes/help/commands.
4. Fresh temporary-project acceptance flow after local package installation.
5. Coverage, `git diff --check`, forbidden-path scan, and runtime `.trellis` dependency scan.
