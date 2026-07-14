# Governed First-Party Skill Source

`skills/` is the authoritative source directory for first-party InvestKit Skills, including versioned development of the core product capability.

Presence in `skills/` does not mean a Skill is installed or released. The project owner controls candidate promotion and first-party release. After a first-party Skill version is released, the end user authorizes local installation through an explicit `investkit init` or `investkit add` action; the CLI records the source-to-target mapping without requiring a new project-owner approval for each installation.

Never copy or auto-install content directly from `third_party/raw/` or `adapted/skills/` into this directory or a host-platform target. No file under `skills/` is installed automatically.
