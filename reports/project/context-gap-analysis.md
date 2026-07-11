# New-Session Context Gap Analysis

Audit date: 2026-07-11

## Can A Fresh Codex Session Understand The Project?

| Question | Current answer | Evidence / gap |
|---|---|---|
| What is InvestKit? | Yes in this worktree | README and PRD clearly define a governed investment-research capability package, not a trading bot. Both were untracked at audit start. |
| What must never happen? | Yes in this worktree | AGENTS and the security policy prohibit unreviewed execution, secret leakage, brokerage actions, and funds transfer. These governance files were untracked. |
| How are candidates processed? | Mostly | SOP, taxonomy, acceptance criteria, schema, and templates exist, but most are not reconstructible from Git. |
| What is Batch 001's current state? | Yes after this audit | `sources_collected_review_not_started` is now consistent across operator and placeholder documents. |
| What does `draft` or `adapt` mean? | Partly | SOP now separates review status from processing decision. A formal registry-status vocabulary/schema is still missing. |
| Does `adapted/skills/` mean approved? | No | SOP and README now identify it as a draft workspace. The directory name remains easy to misread. |
| Where do approved Skills go? | Unknown | No approved installation directory, promotion command, or ownership rule has been selected. |
| Who approves a Skill? | Unknown | No role, person, review quorum, or sign-off record is defined. |
| Can raw sources be reproduced? | Partly | Manifest has URLs/hashes/times/statuses, but no schema, HTTP receipt, tool version, redirect chain, or standard acquisition log. Guosen is incomplete. |
| Are licenses known? | Mostly no | Eastmoney has MIT evidence; CICCWM, Guosen, SkillHub, Guangfa, and URL-only candidates remain unknown/unverified. |
| Is Batch 001 scope coherent? | No | The stated scope is fundamentals/financial statements/valuation/source verification, but intake includes ETF, news, fund, technical/trading, general agent, and workflow assets. |
| Can review results be validated? | Structurally, yes | A Draft 2020-12 schema exists, but there are no reviewed JSON records and no repository-owned validation command. |
| Can a fresh clone reproduce this state? | No | Critical governance, harness, and audit surfaces are untracked; raw ZIPs are intentionally ignored; no external artifact-store procedure exists. |
| What runs automatically in supported harnesses? | Partly | Untracked Claude/Cursor configs invoke local Trellis hooks. The hooks do not target raw assets, but there is no committed harness trust/review statement. |

## Status Vocabulary Gap

Two dimensions are now documented:

- processing decision: `adopt`, `adapt`, `extract`, `reference`, `duplicate`, `unsafe`, `reject`, or `unknown`;
- intake/review status: currently observed `new`, `draft`, and `needs_manual_acquisition`, plus batch status `sources_collected_review_not_started`.

The second dimension is not backed by a schema or transition table. Future work should define allowed values, ownership, transition conditions, and whether batch status and source status use separate vocabularies.

## Provenance And License Gaps

- The manifest relies partly on filesystem mtimes; they are not authenticated acquisition timestamps.
- Only Eastmoney has a precise archived commit and license evidence.
- URL-only GitHub entries have no pinned commit, archive hash, author verification, or license snapshot.
- CICCWM package provenance is URL + local hash, but licensing is unknown and behavior conflicts with policy.
- Guosen requires a human-approved acquisition channel and a record of who supplied each file.
- Guangfa requires official API authorization/terms evidence before any wrapper can move beyond draft.

## Governance Gaps That Block Promotion

1. Formal approved-Skill directory and isolation boundary.
2. Named approval owner and evidence/sign-off format.
3. Status vocabulary and state transitions.
4. License compatibility policy, not just license detection.
5. Acquisition manifest schema and artifact retention/retrieval policy.
6. Definition of acceptable network access, telemetry, and credential handling for data providers.
7. Offline test fixture rules and output-schema requirements.
8. Scope decision for Batch 001.
9. Review and tracking policy for project-local harness hooks, skills, agents, and commands.

## Minimum Context Baseline For A New Session

A reproducible fresh session needs the following committed together: `AGENTS.md`, `.gitignore`, README, product PRD, research SOP/taxonomy/acceptance criteria, security policy, registry schema, source registry, current batch document, templates, raw manifest (without raw binaries), audit reports, and any approved project-local harness configuration. Raw binaries should remain ignored and be restored only through an approved, hash-checked artifact process.

## User Decisions Needed

- Commit the governance baseline now or keep it local.
- Narrow Batch 001 or explicitly broaden it.
- Permit isolated static continuation for CICCWM or reject it at intake.
- Select the Guosen acquisition channel.
- Obtain Guangfa authorization/license evidence.
- Select the approved Skill directory and approver.
