# InvestKit Distribution

Status date: 2026-07-17

## Chosen model

GitHub is the authoritative source for code, documentation, issues, CI, and release
artifacts. The Python wheel and `investkit` CLI are the single execution kernel.
Platform integrations must call that kernel rather than copy provider or analysis
logic into platform-specific prompts.

```text
GitHub source and releases
        ↓
Python wheel / investkit CLI
        ↓
project-local evidence, tasks, reports and diagnostics
        ↓
Codex native Skills or any shell-capable AI platform
```

This provides one version, one security boundary, one persisted research format,
and one release-validation contract. Native platform adapters are additive projections and cannot
change investment methods, data-provider permissions, or trading prohibitions.

## Install from GitHub

Using `pipx`:

```bash
pipx install git+https://github.com/fezeryang/InvestKit.git
investkit --help
```

Using a virtual environment:

```bash
git clone https://github.com/fezeryang/InvestKit.git
cd InvestKit
python3 -m venv .venv
.venv/bin/python -m pip install --no-build-isolation --no-deps .
.venv/bin/investkit --help
```

Provider credentials belong in the initialized research project's private `.env`,
never in the cloned repository, command arguments, prompts, issue reports, or GitHub
Actions secrets unless a separately reviewed CI integration explicitly requires
them. Live research additionally requires `--allow-network`.

## AI platform support

| Platform | Supported integration | Current status |
|---|---|---|
| Codex | `investkit init` installs governed Skills under `.agents/skills`; CLI runs research | Native, tested |
| Claude Code | Invoke the installed `investkit` CLI from the project terminal | CLI-compatible; native adapter not yet claimed |
| Cursor | Invoke the installed `investkit` CLI from the project terminal | CLI-compatible; native adapter not yet claimed |
| Other AI environments | Invoke the CLI when a project-local terminal and Python 3.11+ are available | CLI-compatible within host permissions |

The repository's `.claude/` and `.cursor/` development helpers, if present, belong
to Trellis contributor workflow and are not InvestKit Runtime adapters.

## First use

```bash
mkdir my-investment-research
cd my-investment-research
investkit init
chmod 600 .env
investkit doctor
investkit research \
  --symbol 603868.SH \
  --question "分析公司的基本面、财务质量、行业相对估值、市场表现、催化剂与主要风险。" \
  --allow-network
```

Start from `.env.example` and configure only approved providers. Research tasks and
reports are durable project artifacts. InvestKit does not connect to brokerages,
place orders, transfer funds, or manage assets.

## Release gates

A GitHub release requires:

1. internal verification plus public build, installation, and offline product smoke checks passing from a clean checkout;
2. wheel build and clean virtual-environment installation passing;
3. secret and generated-artifact review;
4. version, changelog, documentation, and supported-platform claims aligned;
5. an explicit repository license selected by the owner;
6. an authenticated push and a verified GitHub CI run.

PyPI publication, native Claude/Cursor adapters, MCP delivery, hosted services, and
automatic updates are separate release decisions.
