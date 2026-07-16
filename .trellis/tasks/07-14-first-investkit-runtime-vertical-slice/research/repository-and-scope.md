# Repository and scope review

Reviewed: 2026-07-14

## Evidence inspected

- `AGENTS.md`
- `docs/product/PRD-v0.1.md`
- `docs/product/architecture.md`
- `plans/product-development-roadmap.md`
- `docs/security/security-policy.md`
- `docs/skill-research/SOP.md`
- `docs/skill-research/taxonomy.md`
- `docs/skill-research/acceptance-criteria.md`
- `tasks/current-batch.md`
- `.trellis/workflow.md`
- `.trellis/spec/backend/`
- `.trellis/spec/guides/`
- tracked repository tree and root package/config files

## Current implementation state

- No `package.json`, lockfile, `pyproject.toml`, requirements file, runtime `src/`, or test configuration exists.
- The only first-party executable implementation is the repository's Python Trellis development tooling.
- Product `agents/`, `workflows/`, `specs/`, `packages/`, and `workspace-template/` source directories do not yet exist.
- `skills/` currently contains only its governed-source README in tracked product state.
- Existing `.claude/` and `.cursor/` trees are local Trellis integration, not InvestKit Runtime.
- Third-party/adapted assets already exist but are out of scope and must not be read as implementation source.

## Language/package conclusion

There is no existing InvestKit Runtime language to continue. Python is the least-surprising repository-local choice because the development toolchain already assumes Python, the environment has Python 3.12/setuptools, and the vertical slice can use the standard library only. This is a new independent package, not an import or copy of `.trellis/`.

Selected baseline:

- Python 3.11+;
- `pyproject.toml` + setuptools console script;
- `src/investkit/` package layout;
- standard-library runtime dependencies only;
- standard-library `unittest`, with development coverage measurement when Coverage.py is available.

## Roadmap differences applied

- Six named Skills replace the roadmap's single generic core Skill for M1.
- Codex is the fixed adapter rather than an unspecified reference platform.
- Doctor and resume contracts are expanded to the owner-provided deterministic checks.
- `add`, `update`, and `uninstall` remain future capabilities and receive no placeholder implementation.
- The newly documented authorized live Provider milestone remains M2; no API, credential, or broker script enters M1.

## Supply-chain and data decision

No third-party dependency, script, prompt, fixture, or network service is needed. The demo company and all financial values will be freshly authored and conspicuously marked fictional. First-party Skill content will be written from the approved InvestKit contracts and not copied from `third_party/raw/` or `adapted/skills/`.
