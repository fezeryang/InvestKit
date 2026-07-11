# Current Batch

## Batch 001

Company fundamentals, financial statements, and valuation-related candidate Skill research.

## Status

`sources_collected_review_not_started`

## Current Inputs

The registry contains 36 real candidate sources. Seven non-empty ZIP archives and one installation-instruction snapshot are present as untrusted raw evidence. Two zero-byte Guosen files are failed download placeholders; four additional Guosen sources have no local file.

Source registry:

```text
registry/inbox/sources.csv
```

Raw asset location:

```text
third_party/raw/batch-001/
```

## Planned Outputs

```text
registry/reviewed/batch-001/
reports/skills/batch-001/
reports/batches/batch-001-summary.md
reports/batches/batch-001-capability-matrix.csv
reports/batches/batch-001-duplicates.md
reports/batches/batch-001-recommendations.md
```

## Scope

Batch 001 should focus on assets related to:

- company fundamentals research;
- financial statement analysis;
- valuation;
- source verification for company reports.

## Operator Notes

Review has not started. Before review, confirm whether Batch 001 excludes ETF, news, and trading-oriented candidates, and resolve the manual acquisition path for Guosen sources. Add links to `registry/inbox/sources.csv`; place local files or archives under `third_party/raw/batch-001/`. Do not execute third-party scripts or weaken TLS verification.
