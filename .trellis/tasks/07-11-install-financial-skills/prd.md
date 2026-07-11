# Install financial skills and track Trellis

## Goal

Bring `.trellis/` into version control and intake the newly collected finance skill sources without committing secrets or directly executing unreviewed third-party code.

## Requirements

- Ensure `.trellis/` files are tracked, while runtime identity/cache files remain ignored.
- Register all user-provided finance skill sources in `registry/inbox/sources.csv`.
- Install safe, project-local wrapper skill drafts for the Guangfa Securities APIs described directly by the user under `adapted/skills/`.
- Do not write API keys or bearer tokens into tracked files, logs, scripts, or skill instructions.
- Preserve third-party GitHub/zip/SkillHub assets as candidates for static review before direct adoption, in line with `docs/security/security-policy.md`.

## Sources

- Eastmoney GitHub skill repo.
- CICCWM skill zip archives.
- SkillHub Lingxi smart stock selection install instructions.
- Guosen Securities skill zip archives.
- Guangfa Securities API descriptions supplied in the request.
- Batch 001 finance skill GitHub candidates.

## Acceptance

- `.trellis/` appears in `git status` as addable/tracked except files ignored by `.trellis/.gitignore`.
- `registry/inbox/sources.csv` contains the new sources and no secrets.
- Project-local Guangfa wrapper skill drafts exist under `adapted/skills/`.
- Task context is curated and task is started.
- Any external network/download result is reported without executing untrusted third-party code.
