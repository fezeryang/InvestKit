# Current Baseline and Inventory

Date: 2026-07-17

## Verified baseline

The current dirty v0.3 worktree is reusable rather than disposable. With the source
layout configured correctly, the complete suite passed:

```text
PYTHONPATH=src python3 -m pytest -q
186 passed, 509 subtests passed in 132.00s
```

Reusable surfaces include initialization and asset copying, Codex projection,
durable task storage, safe resume, Doctor, strict local research bundles, source
joins, 13 analytical capability implementations, and evidence-bounded reports.

The existing specification explicitly says that live acquisition, package
lifecycle, additional platform projections, and dynamic routing are not implemented.
Those are product gaps, not isolated defects in the 13 analytical methods.

## Exact first catalog scope

The initial catalog baseline contained 49 unique assets; the current runtime
catalog contains 50 after adding the governed first-party SSE Provider.

- 13 governed first-party Skills in `skills/`.
- 36 Batch 001 external candidates from `registry/inbox/sources.csv` and the matching
  governance CSV.
- The eight Guangfa drafts are representations of `GF-001` through `GF-008`, not
  eight additional candidates.

External groups:

- EASTMONEY: 1 archived repository candidate; static review incomplete.
- CICCWM: 6 raw archives; license unknown and static security risks identified.
- SKILLHUB: 1 reference snapshot, not an executable package.
- GUOSEN: 6 candidates; missing or invalid acquisition artifacts.
- Guangfa: 8 API wrapper drafts sharing one endpoint and environment key.
- BATCH URL candidates: 14 URL-only or reference candidates with incomplete review.

## Operational-state implications

The governance CSV currently uses valid decisions `reference` for three reference
candidates and `unknown` for most incomplete candidates. The Runtime must preserve
those honest decisions while adding an orthogonal execution state:

- `ready`: approved, installed first-party asset with a valid adapter.
- `credential_required`: executable design exists but an environment credential is
  absent; this does not itself grant network permission.
- `permission_required`: all other checks pass but explicit network/execution consent
  is absent.
- `review_required`: evidence or governance decision is incomplete.
- `unavailable`: the referenced artifact/service could not be acquired.
- `blocked`: safety, licensing, policy, or scope prevents execution.
- `reference_only`: intentionally non-executable material.
- `duplicate`: represented by another canonical asset.
- `error`: catalog or adapter configuration is internally inconsistent.

These states are not a promotion decision. The loader must never derive `ready`
from the mere existence of a file or URL.

## Baseline test-entry issue

Running `python3 -m pytest -q` directly from a source-layout checkout fails imports;
running with `PYTHONPATH=src` succeeds. Packaging/install tests cover installed use,
but developer instructions should make the correct source-tree command explicit or
pytest configuration should add the source path.
