# Establish Batch 001 launch governance

## Goal

Eliminate ambiguity in the status, routing, approval, and release location of the current 36 candidate assets so the repository can safely enter product development.

This is a short-term minimum-governance task. It is not third-party asset research and does not create an asset-management platform.

## Allowed deliverables

1. Assign every candidate exactly one route: `include_in_batch_001`, `defer_to_later_batch`, `blocked`, or `reference_only`.
2. Record separate `review_status`, `disposition`, and `approval_status` dimensions.
3. Define and populate a minimal machine-valid acquisition record with source URL, local filename, byte size, SHA-256, acquisition time, acquisition status, license status, and security warnings.
4. Define the project owner as the only approver; AI may recommend but never approve.
5. Define `skills/` as governed first-party release source. `.agents/skills/`, `.claude/skills/`, `.cursor/`, and similar harness paths are installation targets. Installation must be a later explicit action. `third_party/raw/` and `adapted/skills/` must never be auto-installed.
6. Produce a deterministic Batch 001 readiness checklist with exactly one result: `ready`, `ready_with_conditions`, or `not_ready`.

## Batch 001 scope

Only company fundamentals research, financial statement analysis, basic valuation, and source verification are in scope. Quantitative trading, technical analysis, portfolio management, live trading, brokerage connections, and market execution are deferred or blocked.

Routing is preliminary and based only on current evidence. Insufficient information must remain `unknown` and be deferred; no capability or license may be guessed.

## Prohibited work

- Downloading assets or dependencies.
- Executing third-party scripts or instructions.
- Installing SkillHub or any third-party Skill.
- Calling third-party APIs.
- Deep-reviewing or adapting existing Skills.
- Creating a marketplace, complex governance framework, or multi-level approval flow.
- Automatically installing any Skill or converting all candidates into Skills.

## Completion criteria

- All 36 source IDs appear exactly once in the governance routing data.
- Route, review status, disposition, and approval status use controlled values and validate mechanically.
- Current acquisition evidence validates mechanically without inventing missing facts.
- The owner-only approval rule and release/install boundaries are explicit.
- The readiness report answers which assets are included, deferred, blocked, or reference-only; which may be researched; which must not execute/install; where first-party Skill source lives; and when installation is allowed.
- Existing Schema, CSV, Markdown-reference, Git-ignore, secret, trading-boundary, and third-party-execution checks remain green.
- Changes are committed once as an independent task-specific commit, with no unrelated untracked files.

## Stop condition

After the minimum files, validation, and one independent commit are complete, stop. Do not begin candidate research or create another governance task.
