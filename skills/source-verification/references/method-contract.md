# Source Verification Method Contract

Version: 1.0

## Source Audit Record

Record source ID, identity, type, locator, publication/effective date, retrieval time or fixture version, as-of date, market/currency/period/unit/accounting scope where applicable, quality rationale, accessibility, checksum, provider, warnings, use constraints, and demo state.

## Claim Verification Record

Record claim ID, epistemic type, capability origin, source IDs, status, freshness decision, definition checks, conflicts, warnings, and decision impact. Allowed statuses are `verified`, `partially_supported`, `unsupported`, `stale`, `conflicted`, `low_quality`, and `not_applicable`.

## Verification Gate

Report material claim count, resolved fact count, unresolved IDs, conflict IDs, freshness exceptions, and `pass`, `pass_with_disclosed_gaps`, or `fail` gate state. A completed report cannot rely on a materially unsupported fact.

## Guards

Do not fabricate citations for assumptions, average away conflicts, treat freshness as quality, expose credentials, fetch undeclared sources, or modify upstream claims.
