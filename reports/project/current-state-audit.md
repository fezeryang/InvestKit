# InvestKit Current-State Audit

Audit date: 2026-07-11
Mode: static repository inspection and documentation correction only

## Outcome

InvestKit has the basic directories, policy text, registry, schema, and raw evidence needed to perform isolated static research. It is **not ready to start Batch 001 reproducibly**. The governing baseline is largely outside Git, the batch mixes candidates beyond its stated fundamentals/financial-statements/valuation scope, most collected packages lack verified license evidence, Guosen acquisition is incomplete, and no formal approved-Skill promotion path or approver is defined.

The corrected Batch 001 status is `sources_collected_review_not_started`. This is an intake/review status, not a processing decision and not an approval.

## Repository And Git State

- Branch: `main`; audit started from commit `842f5fa` (`Track Trellis and intake finance skills`).
- Git tracks Trellis workflow/specs, the previous Trellis tasks, the source CSV, the eight Guangfa wrapper drafts, the raw manifest, and the SkillHub instruction snapshot.
- Core governance and operator surfaces including `.gitignore`, `AGENTS.md`, `README.md`, `docs/`, `registry/schema/`, `reports/`, `tasks/`, `templates/`, `.claude/`, and `.cursor/` were untracked at audit start. A fresh clone at `842f5fa` therefore cannot reconstruct the working governance or harness baseline.
- Raw ZIP files are ignored by `.gitignore`; Trellis developer/runtime/cache state is ignored by `.trellis/.gitignore`. No raw archive is in the Git index.
- Existing unrelated untracked files were not staged or committed by this audit.

## Trellis State

- The previous current task, `07-11-install-financial-skills`, remains `in_progress` and is recorded as paused at the user's request; only its session pointer was cleared.
- This audit uses the independent `07-11-audit-investkit-project-state` task, status `in_progress`.
- `00-bootstrap-guidelines` and `07-11-initialize-investkit-skill-research` also remain `in_progress`. A future operator should decide whether they are active, paused, or stale; the audit did not alter them.

## Intake State

| Item | Count | State |
|---|---:|---|
| Real registry candidates | 36 | 22 `new`, 8 `draft`, 6 `needs_manual_acquisition` |
| Non-empty raw ZIP archives | 7 | 6 CICCWM + 1 Eastmoney; untrusted and unreviewed |
| Instruction snapshots | 1 | SkillHub installation text; untrusted prompt content, not a Skill package |
| Failed zero-byte placeholders | 2 | GUOSEN-001 and GUOSEN-002; not valid archives |
| Guosen sources without local files | 4 | GUOSEN-003 through GUOSEN-006 |
| Guangfa wrapper drafts | 8 | Documentation-only drafts under `adapted/skills/`; not approved or installed |
| Structured reviewed records | 0 | No candidate is research-complete |
| Approved records | 0 | No Skill is approved |

The registry originally contained one example row; it was removed. The prior `adapted` source status for all Guangfa entries incorrectly implied a processing outcome and was changed to `draft`. Guosen entries now explicitly require manual acquisition.

## Archive And Provenance Findings

- The manifest now records URL, local path/filename, byte size, SHA-256, local-time evidence, acquisition status, and license status per collected or attempted source.
- Eastmoney contains an MIT license. Its ZIP comment records archive commit `61cfae47451f797d95ae4553ffcc7569b9957e7d`.
- CICCWM archives contain no visible license file; license status is `unknown` for all six.
- Guosen files could not be obtained without encountering a legacy TLS renegotiation failure. Security settings were not weakened. The two zero-byte files are retained only as failed-attempt evidence.
- The Markdown manifest remains a human-readable record, not a schema-validated acquisition ledger. A future acquisition format is proposed in `plans/skill-research-phase-1.md`.

## Security Findings

### CICCWM packages — high risk for automatic integration

Static ZIP-content inspection found that all six scripts:

- read `~/.config/ciccwm/config.json`, outside the project boundary;
- obtain `CICCWM_API_KEY` from that file;
- derive a device fingerprint from host/platform data;
- asynchronously send telemetry to `webreport.ciccwm.com`, including the API key as `login_id` and local platform attributes.

Five packages (all except CICCWM-002) also disable certificate and hostname verification and lower OpenSSL security to `SECLEVEL=0`. CICCWM-001 contains a subprocess fallback using `curl -k`. These behaviors meet multiple stop-automatic-integration conditions in the security policy. Their processing decision remains `unknown` pending a human decision on whether isolated static review is worth continuing; nothing was executed.

### SkillHub snapshot — prompt and installer risk

The snapshot contains pipe-to-shell commands and instructions that attempt to change the Agent's source priority, installation behavior, and destination directories. It was treated as untrusted reference material. No CLI or Skill was installed and no instruction in the snapshot was followed.

### Secrets

No literal credential was intentionally written by this audit. Common secret-format scans found environment-variable names and placeholder examples, but no confirmed live key in the worktree (including statically read raw ZIP members), Git index, or reachable history. No known live-key fingerprint was available in this fresh context for an exact-fingerprint comparison. The raw CICCWM code's use of a credential in telemetry is a design finding; the raw archives themselves remain ignored and untracked.

## Investment And Execution Boundary

- The project contains no implementation that connects to a brokerage, submits an order, signs a transaction, or transfers funds.
- Trading-oriented candidates exist in the intake registry, but they are URLs/notes or untrusted raw evidence, not integrated capabilities.
- `scripts/` contains only a policy README and no automatic downloader, installer, or executor.
- The untracked Claude and Cursor harness configurations do auto-run project-local Trellis Python hooks on session, prompt/tool, or shell lifecycle events. Static inspection found those hooks wired to Trellis context/task handling, not to `third_party/raw/`; nevertheless, hook configuration is a supply-chain and automatic-execution surface that must be reviewed before it is committed or enabled.
- No reviewed record has decision `adopt`, no source has status `approved`, and `registry/approved/` contains no approved asset record.

## Corrections Made

- Reconciled Batch 001 status across README, PRD, current-batch document, and batch placeholders.
- Removed the CSV example row and corrected Guangfa/Guosen statuses.
- Expanded the raw manifest and preserved uncertain facts as `unknown`.
- Clarified in the SOP that processing decision, review status, workspace location, approval, and installation are distinct.
- Added repository inventory, context-gap analysis, Guangfa draft review, and Phase 1 planning artifacts.

## Required Decisions Before Batch 001 Starts

1. Whether to commit the full governance baseline (`AGENTS.md`, README, docs, schema, templates, reports, task description, and ignore rules).
2. Whether Batch 001 is limited to fundamentals, financial statements, valuation, and source verification, or also includes ETF, news, technical/trading, fund, and broad workflow candidates.
3. Whether CICCWM packages may proceed to isolated static review despite telemetry, home-directory access, credential transmission, and weak TLS behavior.
4. Which approved manual channel and provenance evidence will be used for Guosen assets.
5. Whether Guangfa has official authorization/license terms that permit wrapper use and adaptation.
6. Where approved Skills would live, who approves promotion, and what signed-off evidence is required.

Until those decisions are recorded, Batch 001 should remain `sources_collected_review_not_started`.
