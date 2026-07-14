# Clarify InvestKit Agent Harness product definition

## Goal

Correct the product definition so InvestKit is consistently described as an installable investment-research AI Agent Harness with two first-class layers: investment capabilities and the Harness framework.

## Required changes

- Update `docs/product/PRD-v0.1.md` with the complete positioning, two-layer product model, target experience, authoritative source/install boundaries, and first vertical slice.
- Create a product architecture document that distinguishes the InvestKit runtime/product from the repository's current use of Trellis.
- Update README so the first screen states the final product rather than the current Skill-governance phase.
- Create a product development roadmap whose next milestone is the runnable Harness vertical slice.
- Mark the existing third-party Skill research plan as a supporting track rather than the product roadmap.
- Record that authorized official financial APIs, interface specifications, professional methods, and clearly licensed code may become governed first-party Providers, Skills, Workflows, or References after review, while original third-party scripts remain non-executable by default.
- Define the long-term unified data interface and Provider Adapter boundary without expanding the offline first vertical slice.

## Product definition

InvestKit is an investment-research AI Agent Harness that can be installed into Codex, Claude, Cursor, and similar AI environments. Through shared investment standards, first-party Skills, Agents, data tools, research workflows, task lifecycle, and persistent research workspaces, it turns a general AI environment into a traceable, reproducible, and extensible investment-research workbench.

Both the investment-capability layer and Agent Harness framework layer are final-product scope.

## Required distinction

- `.trellis/` is the development workflow and governance tooling currently used to build InvestKit.
- Trellis is also a product-form reference for initialization, persistent specifications, tasks, deterministic workflows, context restoration, artifacts, multi-platform delivery, update, diagnostics, and uninstall.
- `.trellis/` must not be presented as the InvestKit runtime implementation.

## Source boundaries

- `skills/`: first-party Skill source.
- `agents/`: first-party Agent source.
- `workflows/`: research workflow source.
- `specs/`: investment-research standards.
- `packages/`: optional capability packages.
- `workspace-template/`: user research workspace template.
- Harness-specific directories are installation targets only.

## First vertical slice

Document the complete path: `investkit init` → workspace/config → core first-party Skill install → investment standards → `investkit demo research` → structured research task → offline company-research workflow → sourced report → persisted inputs/data/assumptions/run records → `investkit doctor`.

## Scope limits

- Documentation changes only.
- Do not implement CLI, runtime, Skills, Agents, workflows, packages, or templates.
- Do not add governance layers.
- Do not download, inspect, execute, install, or approve third-party assets.
- Do not treat `.trellis/` as product runtime code.

## Acceptance criteria

- PRD, README, architecture, and roadmap use the same one-sentence positioning.
- Both product layers are explicitly first-class.
- Target commands and the ten-step automatic research experience are documented.
- Authoritative source and installation-target directories are unambiguous.
- The first vertical slice validates both Harness and investment research behavior.
- Trellis development use and Trellis-inspired product form are clearly separated.
- All local Markdown references resolve and no implementation claim is fabricated.
- Provider integration, third-party execution, project-owner release approval, and end-user installation authorization remain distinct.
