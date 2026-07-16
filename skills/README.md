# Governed First-Party Skill Source

`skills/` is the authoritative source for first-party InvestKit Skills. Host paths such as `.agents/skills/` are generated installation targets, never the source of truth.

The v0.2 catalog contains one Runtime prerequisite, `security-identification`, and exactly 12 Investment Core Skills:

1. `company-deep-research`
2. `business-model-analysis`
3. `financial-statement-analysis`
4. `earnings-quality-analysis`
5. `valuation-analysis`
6. `comps-analysis`
7. `earnings-analysis`
8. `investment-thesis`
9. `bear-case-analysis`
10. `catalyst-analysis`
11. `source-verification`
12. `investment-report`

Each governed Skill directory contains `SKILL.md` and may contain direct files under `references/` and `agents/`. Initialization copies only allowlisted regular files, preserves their relative paths, rejects symlinks or root escapes, and records source/target checksums. Folder presence alone does not make an unallowlisted Skill installable.

The project owner controls first-party promotion and release. An end user authorizes installation through an explicit InvestKit CLI action. Raw or draft material is never copied or auto-installed into this directory or a platform target, and no file under `skills/` is installed merely because it exists.
