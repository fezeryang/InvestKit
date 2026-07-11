# InvestKit

InvestKit is an investment research AI capability package for Codex-like AI environments. It is currently a research and governance workspace for discovering, registering, reviewing, evaluating, adapting, and accepting third-party finance-related Agent Skills and adjacent open-source assets.

InvestKit is not a trading robot. It does not connect to real brokerages, place orders, transfer money, promise returns, or provide guaranteed investment conclusions.

## Current Use

1. Find a potentially relevant Skill, repository, file, or archive.
2. Add its link to `registry/inbox/sources.csv`.
3. Put any local files into the matching raw batch folder, such as `third_party/raw/batch-001/`.
4. Do not manually execute scripts from those files.
5. Ask Codex to process the batch.
6. Read the summaries in `reports/batches/`.
7. Manually decide whether to approve further adaptation.

## What The Project Owner Does

- Collect links.
- Add short notes.
- Review AI-generated reports.
- Approve, reject, or request human re-review.

## What Codex Does

- Registers sources.
- Classifies assets.
- Performs static analysis.
- Checks licenses.
- Reviews security risks.
- Compares duplicate capabilities.
- Recommends adaptation paths.
- Recommends tests.
- Generates reports.

## Main Paths

- `docs/product/PRD-v0.1.md` defines the product and current phase.
- `docs/skill-research/SOP.md` defines the fixed review workflow.
- `docs/skill-research/taxonomy.md` defines classification standards.
- `docs/skill-research/acceptance-criteria.md` defines when research is complete.
- `docs/security/security-policy.md` defines safety boundaries.
- `registry/inbox/sources.csv` is where candidate sources are registered.
- `registry/schema/skill-record.schema.json` defines structured research records.
- `registry/governance/` records candidate routing, state, and acquisition evidence.
- `docs/governance/minimum-governance.md` defines the minimum owner-approval and release rules.
- `third_party/raw/` stores untrusted original assets.
- `adapted/` is a draft/adaptation workspace; files there are not approved or formally installed.
- `skills/` is the governed first-party release-source directory; installation is always a later explicit action.
- `reports/` stores single-asset and batch reports.
- `tasks/current-batch.md` describes the active batch.

## Current Batch

Batch 001 status is `sources_collected_review_not_started`: sources and raw evidence exist, but governed candidate review has not begun. Scope is locked to company fundamentals, financial statements, basic valuation, and source verification; out-of-scope candidates are deferred, blocked, or reference-only in the governance routing table.

Readiness is `ready_with_conditions`: first-party product development may begin, but no current candidate may be executed, installed, called, or promoted. See `reports/batches/batch-001-readiness.md`.
