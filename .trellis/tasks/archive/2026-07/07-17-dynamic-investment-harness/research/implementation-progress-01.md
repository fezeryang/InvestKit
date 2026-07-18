# Implementation Progress 01: Catalog, Planner, and Guangfa Boundary

Date: 2026-07-17

## Delivered

- Strict `schemas/runtime-asset-catalog-v1.json` with 14 first-party and 36
  candidate entries, including the governed SSE announcement Provider.
- Profile expansion plus fail-closed validation for schema fields, duplicate JSON
  keys/IDs, enums, execution gates, dependency references, and dependency cycles.
- `investkit assets list`, `show`, and pure offline `plan` commands with human and
  JSON output.
- Doctor checks for catalog integrity and credential/execution-gate availability.
- Pure policy evaluation that cannot bypass review, blocked, or unavailable states
  by supplying a credential or network permission.
- Dependency-aware deterministic planning with selected, considered, and blocked
  explanations.
- First-party Guangfa client boundary for F10, valuation, and financial comparison:
  strict A-share symbols, environment-only credential, explicit network consent,
  endpoint allowlist, redirect denial, timeout/size limits, strict JSON, injected
  offline transport, and secret-safe errors.

## Evidence

Initial baseline before the new slice:

```text
186 passed, 509 subtests passed
```

Full suite after catalog and planner:

```text
201 passed, 565 subtests passed in 225.33s
```

Focused suite after the Guangfa boundary:

```text
54 passed, 137 subtests passed in 39.57s
```

No live API request was made. `GF-002` and `GF-003` remain `review_required` and
`not_requested`, so the planner correctly refuses to select them even if a caller
claims to possess a credential and grants network permission.

## Remaining mainline

- Normalize mocked Guangfa F10/valuation/financial responses into the Provider
  evidence contract.
- Define the typed adapter registry and frozen dynamic task-plan persistence.
- Extend the now-working `research --symbol` path beyond official announcement
  metadata into governed filing-content and market-data acquisition.
- Complete governance evidence before changing GF-002/GF-003 from review-required.
- Run coverage, wheel-only, Doctor, security, resume, and readiness verification.
