# Independent Trellis Check — Investment Core Pack

Check date: 2026-07-16
Task: `07-15-investment-core-pack`
Verdict: **PASS for local v0.2 acceptance**; this is not a release or production-readiness decision.

## Scope And Safety

The check reconstructed the task contract from the PRD, acceptance matrix, referenced Trellis specs, capability studies, Runtime migration design, product/security documents, and current-batch record. It reviewed the first-party implementation, tests, packaged assets, Skill contracts, synthesis reports, workflow, persistence, doctor, report rendering, and documentation. No network service was called, no file below `third_party/raw/` was read or executed, no third-party dependency or Skill was installed, and no commit or push occurred.

## Acceptance Matrix

| Area | Result | Evidence |
|---|---|---|
| Governed Skill set | PASS | Exactly one Runtime prerequisite plus 12 Core Skills; 13 trees, 52 governed files, valid frontmatter, complete sections, resolvable references, versions, and package mappings. |
| Synthesis and provenance | PASS | Exactly 12 capability synthesis reports; bounded-corpus evidence, hashes/commits, explicit license and evidence gaps, independent first-party method decisions. Tree/index-only evidence is graded `C`. |
| Trigger and method Evals | PASS | Four trigger cases per Skill (two positive, two near-miss); substantive workflow/unit tests cover required and missing inputs, guardrails, result envelopes, and handoffs. |
| Capability behavior | PASS | Company/business/financial/quality/DCF/comps/earnings/thesis/bear/catalyst/source/report outputs satisfy the capability rows, including explicit unknowns and guarded invalid inputs. |
| Workflow and persistence | PASS | Exact 13-stage `company-deep-dive`; structured artifact per stage; mandatory bear case and verification; valid skips; failed-step continuation; completed resume immutability and artifact-hash enforcement. |
| Init and doctor | PASS | Empty and repeat init, user-file preservation, exact nested mapping hashes, PASS/WARN/FAIL mutations, secret redaction, symlink/path rejection, and completed-task integrity are covered and green. |
| Offline/security boundary | PASS | Runtime dependencies are empty; production source has no network/subprocess imports or dynamic execution; forbidden third-party roots are denylisted and never packaged or installed; high-confidence secret scan found no values. |
| Packaging | PASS | All 64 required delivery assets are mapped; fresh local wheel `investkit-0.2.0-py3-none-any.whl` installs with `--no-index --no-deps`; `pip check` is clean. |
| Documentation and roadmap | PASS | README, PRD, architecture, capability map, Skill source docs, and roadmap agree on local verification, non-release status, capability-first ordering, and Providers as subordinate future infrastructure. |
| Later-pack boundary | PASS | No Advanced, Quant, Portfolio/Risk, live Provider, trading, brokerage, or multi-platform implementation/catalog claim was added. |

## Defects Corrected During Check

- `earnings-quality-analysis` no longer serializes absent numeric inputs as facts; it reports explicit unknowns and calculates working-capital change only from complete comparable components.
- `comps-analysis` now emits inclusive quartiles, peer ranges, target implied equity/per-share ranges, a guarded EV-to-equity bridge, and weak-sample warnings.
- `doctor` now checks the complete immutable artifact-hash set for completed tasks while leaving only `run-log.json` append-only.
- Removed the unused, unexported legacy `src/investkit/research/analysis.py` module.
- Added and then hardened `scripts/quick_validate.py`: exact 13-Skill identity, exact four-file/two-directory governed trees, frontmatter/sections/version/links, required `openai.yaml` content and `$skill` default prompt, nonempty method contract, Eval schema `1.0`, and two positive/two near-miss cases.
- Aligned fixed workflow handoffs with valuation → comps → earnings; current-run reconciliation occurs downstream instead of back-writing valuation.
- Made source-quality and freshness behavior explicit in every governed Skill, normalized the verification gate to `pass | pass_with_disclosed_gaps | fail`, and corrected tree-only synthesis evidence grades.
- Clarified that v0.2 capability synthesis is separate from still-unstarted formal single-asset Batch-001 SOP review; no governance decision changed.
- Removed Trellis `_example` seed rows and ignored local build/coverage artifacts.

## Exact Verification Evidence

```text
PYTHONPATH=src python3 -m coverage run --source=src/investkit -m unittest discover -s tests -v
Ran 94 tests in 76.154s — OK (no skips)

python3 -m coverage report -m --fail-under=80
TOTAL 2838 statements, 450 missed, 84% — PASS

pyright src tests
0 errors, 0 warnings, 0 informations

python3 -m compileall -q src tests scripts
exit 0

python3 scripts/quick_validate.py
13 individual PASS results; PASS validated exactly 13 governed Skills

git diff --check
exit 0
```

The validator hardening followed a focused red/green cycle. Before implementation, all four mutations (bad default prompt, Eval schema `2.0`, empty method contract, and an unexpected governed file) were incorrectly accepted. After implementation:

```text
PYTHONPATH=src python3 -m unittest \
  tests.test_investment_core.SkillAndCatalogContractTests.test_quick_validate_accepts_exactly_the_thirteen_governed_skills \
  tests.test_investment_core.SkillAndCatalogContractTests.test_quick_validate_rejects_malformed_governed_files -v
Ran 2 tests in 0.432s — OK
```

Static checks also passed: stale status/evidence-grade/backward-handoff searches returned no matches; high-confidence credential patterns returned no matches; production source had no network/subprocess/dynamic-execution imports; both Trellis JSONL files parsed after seed removal; `pyproject.toml` declares `dependencies = []`. The only `third_party/raw` production-source match is the intentional doctor denylist constant.

## Fresh Wheel-Only Lifecycle

```text
python3 -m pip wheel . --no-deps --no-build-isolation \
  --wheel-dir /tmp/investkit-audit.WC7uaO/wheelhouse
Successfully built investkit-0.2.0-py3-none-any.whl
SHA-256 23f38c87ba11274d247ae6e88f78a3aeac758a0500fceb159cf8723dd5fd1f30

python3 -m venv /tmp/investkit-audit.WC7uaO/venv
/tmp/investkit-audit.WC7uaO/venv/bin/python -m pip install \
  --no-index --no-deps /tmp/investkit-audit.WC7uaO/wheelhouse/investkit-0.2.0-py3-none-any.whl
Successfully installed investkit-0.2.0

investkit init
52 governed Skill files plus Runtime/workspace state created

investkit init
All governed files reported identical SKIP; idempotent

investkit doctor
All critical checks PASS; one expected fixture-missingness WARN

investkit demo research
PASS task demo-20260716T152602456701Z-5d81252233

investkit demo research --resume demo-20260716T152602456701Z-5d81252233
PASS; same completed task/report

investkit doctor
All critical checks PASS; one expected fixture-missingness WARN

python -m pip check
No broken requirements found
```

## Residual Risks And Handoff

- The shared worktree remains intentionally dirty/untracked and the branch was already ahead of `origin/main`; this check did not stage, commit, reset, or push anything.
- Formal Batch-001 single-asset review, licensing approval, disposition, promotion, and any live Provider work remain pending and out of scope. Capability synthesis does not approve a third-party asset.
- The demo intentionally contains missing fixture fields, so doctor emits one non-critical completeness warning; tests require that missingness and its actionable warnings.
- Local verification establishes the task's acceptance contract, not real-data accuracy, release approval, operational security certification, or production readiness.

The Trellis task remains `in_progress` for owner handoff/archive rather than being marked complete automatically.
