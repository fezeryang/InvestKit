# InvestKit Repository Inventory

Inventory date: 2026-07-11

## Core Surfaces

| Surface | Purpose | Git state at audit start |
|---|---|---|
| `.trellis/` | Workflow, specs, tasks, journals | Core workflow/specs and three prior tasks tracked; runtime/developer/cache ignored |
| `.claude/`, `.cursor/` | Trellis skills, agents, commands, and lifecycle hooks | Untracked; settings invoke local Python hooks automatically |
| `docs/` | Product, research SOP/taxonomy/acceptance, security policy | Untracked |
| `registry/inbox/sources.csv` | Candidate intake | Tracked |
| `registry/schema/skill-record.schema.json` | Reviewed-record schema | Untracked |
| `registry/reviewed/`, `registry/approved/` | Review and approval records | Only untracked placeholders; no records |
| `third_party/raw/batch-001/manifest.md` | Raw intake evidence | Tracked |
| `third_party/raw/batch-001/**/*.zip` | Untrusted raw archives/placeholders | Ignored and untracked |
| `adapted/skills/` | Current draft wrapper workspace | Eight Guangfa drafts tracked |
| `reports/`, `tasks/`, `templates/`, `scripts/` | Reports, batch state, templates, maintenance policy | Untracked at audit start |

## Registry Candidates

Before cleanup the CSV had 37 data rows: 36 real candidates plus one example row (38 physical lines including the header). After cleanup it has 36 data rows (37 physical lines). This audit assigns the only honest provisional decision, `unknown`, to every candidate; it is not a completed review decision because no single-asset decision record exists.

| ID | Candidate | Intake status | Initial form hypothesis | Local evidence |
|---|---|---|---|---|
| EASTMONEY-001 | Eastmoney repository | `new` | Agent Skill collection / data tools | Non-empty ZIP, MIT license, archived commit known |
| CICCWM-001 | Market analysis | `new` | Agent Skill + data provider | Non-empty ZIP; license `unknown` |
| CICCWM-002 | Stock finance analysis | `new` | Agent Skill + data provider | Non-empty ZIP; license `unknown` |
| CICCWM-003 | Hot news analysis | `new` | Agent Skill + data provider | Non-empty ZIP; license `unknown` |
| CICCWM-004 | ETF ranking analysis | `new` | Agent Skill + data provider | Non-empty ZIP; license `unknown` |
| CICCWM-005 | Tiger-list analysis | `new` | Agent Skill + data provider | Non-empty ZIP; license `unknown` |
| CICCWM-006 | Fund product information | `new` | Agent Skill + data provider | Non-empty ZIP; license `unknown` |
| SKILLHUB-001 | Lingxi installation instructions | `new` | Reference / acquisition lead | Markdown snapshot only; not a package |
| GUOSEN-001 | Stock market query | `needs_manual_acquisition` | Unknown until acquired | 0-byte failed placeholder |
| GUOSEN-002 | Stock financial query | `needs_manual_acquisition` | Unknown until acquired | 0-byte failed placeholder |
| GUOSEN-003 | Economy query | `needs_manual_acquisition` | Unknown until acquired | No local file |
| GUOSEN-004 | Smart stock picking | `needs_manual_acquisition` | Unknown until acquired | No local file |
| GUOSEN-005 | Fund compare | `needs_manual_acquisition` | Unknown until acquired | No local file |
| GUOSEN-006 | ETF filter | `needs_manual_acquisition` | Unknown until acquired | No local file |
| GF-001 | Dragon-Tiger list wrapper | `draft` | MCP/tool wrapper documentation | Tracked draft `gf_lhb_list` |
| GF-002 | Stock F10 wrapper | `draft` | MCP/tool wrapper documentation | Tracked draft `gf_stock_f10` |
| GF-003 | Valuation/financial compare wrapper | `draft` | MCP/tool wrapper documentation | Tracked draft `gf_stock_valuation` |
| GF-004 | ETF ranking wrapper | `draft` | MCP/tool wrapper documentation | Tracked draft `gf_etf_rank` |
| GF-005 | ETF search wrapper | `draft` | MCP/tool wrapper documentation | Tracked draft `gf_etf_search` |
| GF-006 | ETF fund-flow wrapper | `draft` | MCP/tool wrapper documentation | Tracked draft `gf_etf_super_fund` |
| GF-007 | Fund detail wrapper | `draft` | MCP/tool wrapper documentation | Tracked draft `gf_fund_detail` |
| GF-008 | Fund investment calculator wrapper | `draft` | MCP/tool wrapper documentation | Tracked draft `gf_fund_invest` |
| BATCH-001-001 | Anthropic financial-services | `new` | Unknown until verified | URL only |
| BATCH-001-002 | finance-skills | `new` | Unknown until verified | URL only |
| BATCH-001-003 | LangAlpha | `new` | Unknown until verified | URL only |
| BATCH-001-004 | claude-trading-skills | `new` | Unknown until verified | URL only |
| BATCH-001-005 | OctagonAI skills | `new` | Unknown until verified | URL only |
| BATCH-001-006 | investor-harness | `new` | Unknown until verified | URL only |
| BATCH-001-007 | InvestSkill | `new` | Unknown until verified | URL only |
| BATCH-001-008 | china-stock-research-skills | `new` | Unknown until verified | URL only |
| BATCH-001-009 | claude-equity-research-skills | `new` | Unknown until verified | URL only |
| BATCH-001-010 | Longbridge skills | `new` | Unknown until verified | URL only |
| BATCH-001-011 | Financial-modeling cookbook | `new` | Template/reference hypothesis | URL only |
| BATCH-001-012 | Comps-analysis | `new` | Agent Skill hypothesis | URL only |
| BATCH-001-013 | Deep-Research-skills | `new` | Workflow/Agent Skill hypothesis | URL only |
| BATCH-001-014 | Vibe-Trading | `new` | Agent/quant/trading hypothesis | URL only |

Initial form hypotheses are routing hints, not taxonomy conclusions or processing decisions.

## Raw Asset Inventory

| Group | Files | Validity | Tracking |
|---|---:|---|---|
| CICCWM | 6 ZIPs | Non-empty ZIPs; static high-risk findings; licenses unknown | Ignored/untracked |
| Eastmoney | 1 ZIP | Non-empty ZIP; MIT license; commit in ZIP comment | Ignored/untracked |
| Guosen | 2 ZIP-named files | Both 0 bytes and invalid; four expected files absent | Ignored/untracked |
| SkillHub | 1 Markdown file | Installation-instruction snapshot, not a Skill | Tracked |

Detailed sizes, hashes, timestamps, URLs, and acquisition outcomes are in `third_party/raw/batch-001/manifest.md`.

## Draft Inventory

Eight Guangfa `SKILL.md` files exist under underscore-named directories. They are documentation-only API wrapper drafts: no call implementation, formal output schema, license/authorization evidence, error-handling contract, or offline test suite is present. See `reports/project/guangfa-wrapper-review.md`.

## Approval Inventory

- Reviewed structured records: 0.
- Single-asset reports: 0.
- Approved records: 0.
- Formally installed production Skills: no directory or promotion rule is defined.
- Candidates marked `approved`: 0.

## Automatic Execution Surfaces

`.claude/settings.json` invokes three local Trellis hook scripts on session start, sub-agent tool use, and user prompt submission. `.cursor/hooks.json` invokes local Trellis hooks on session start, sub-agent tool use, and before shell execution. These are project harness automation surfaces, not finance capability implementations. No hook reference to `third_party/raw/`, SkillHub installation, a package installer, or a finance API was found during static inspection. Because both platform directories are untracked, their inclusion and trust policy remain part of the governance-baseline decision.
