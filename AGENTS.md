<!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants working in this project.

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:
- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.

<!-- TRELLIS:END -->

# InvestKit Project Instructions

## Project Positioning

InvestKit is an installable investment-research AI Agent Harness for Codex, Claude, Cursor, and similar environments. It includes both professional investment capabilities and the Harness framework that installs, orchestrates, persists, restores, and diagnoses research work. It is not a real trading bot and must not connect to brokerages, place trades, transfer funds, or promise investment returns.

## Read Before Starting

Read the relevant files before each task:

- `docs/product/PRD-v0.1.md`
- `docs/skill-research/SOP.md`
- `docs/skill-research/taxonomy.md`
- `docs/skill-research/acceptance-criteria.md`
- `docs/security/security-policy.md`
- `tasks/current-batch.md`

## Third-Party Asset Rules

Everything under `third_party/raw/` is untrusted research material.

By default, do not:

- execute third-party scripts;
- install third-party dependencies;
- call third-party network services;
- read user files outside this project directory;
- copy code with unclear licensing;
- install raw Skills directly into a production Skill directory;
- write API keys into the repository or logs.

## Analysis Principles

Do not force every asset to become a Skill. Classify candidates as one of:

- Agent Skill
- Tool or MCP
- Data Provider
- Quant Module
- Agent
- Workflow
- Template
- Reference
- Reject

## Required Decisions

Every candidate asset must receive exactly one clear decision:

- `adopt`
- `adapt`
- `extract`
- `reference`
- `duplicate`
- `unsafe`
- `reject`
- `unknown`

## Honesty Requirements

- Do not fabricate licenses.
- Do not fabricate repository metadata.
- Do not fabricate test results.
- Mark uncertain information as `unknown`.
- Explain evidence for important conclusions.
- Preserve original sources and processing records.
