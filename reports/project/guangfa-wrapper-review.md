# Guangfa Wrapper Draft Review

Audit date: 2026-07-11
Review depth: documentation-only static gap review; no API call performed

## Shared Findings

- Source evidence is limited to the user-supplied API descriptions preserved in the tracked draft files and the common endpoint `POST https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`.
- License, API terms, redistribution permission, and official wrapper authorization are `unknown`.
- All wrappers require network access and `GF_SKILLS_APIKEY`; the drafts instruct use of an environment variable and contain no literal key.
- No wrapper contains a callable implementation or shell command. The intended HTTP-call mechanism, timeout, retry policy, redaction behavior, rate limits, and response validation are unspecified.
- Directory/frontmatter names use underscores, not the Codex hyphen-case convention.
- Inputs and selected response fields are documented, but there is no versioned formal output Schema.
- No offline fixtures, unit tests, contract tests, authorization tests, redaction tests, failure-mode tests, or approved live test procedure exist.
- Workspace status for all eight is `draft`; processing decision is `unknown`. Location under `adapted/skills/` is not approval or installation.

## Per-Wrapper Review

| Source / draft | Capability | Inputs | Intended output | Duplicate/overlap lead | Specific gaps |
|---|---|---|---|---|---|
| GF-001 / `gf_lhb_list` | Dragon-Tiger abnormal-trading list | date, market | Stock list and listing reasons | Strong intake-level overlap with CICCWM-005 | Authorization/license unknown; no output schema, implementation, bounded pagination contract, error taxonomy, or offline fixture |
| GF-002 / `gf_stock_f10` | Listed-company F10 facts | code, market | Company name, board, listing date, scope, industries | Partial overlap with CICCWM-002 and Eastmoney data candidates | No provenance per returned field, output schema, implementation, API error mapping, or fixture |
| GF-003 / `gf_stock_valuation` | Market-cap, valuation, financial comparison | stock codes, report type, year | PE/PB, percentiles, profitability, leverage, cash flow, growth | Strong overlap with CICCWM-002 and several URL-only equity-research candidates | Metric definitions/units and restatement policy incomplete; no output schema, implementation, validation, or tests |
| GF-004 / `gf_etf_rank` | ETF ranking | type, page, size, filters | Ranked ETF metrics | Strong overlap with CICCWM-004; partial with GUOSEN-006 | Out of stated Batch 001 core scope; pagination/rate-limit/error/output contracts absent |
| GF-005 / `gf_etf_search` | Multi-factor ETF screening | theme, return, drawdown, Sharpe, valuation, scale, sort | Filtered ETF list | Partial overlap with CICCWM-004 and GUOSEN-006 | Field spelling/units and filter grammar need formal validation; no schema, implementation, or boundary tests |
| GF-006 / `gf_etf_super_fund` | ETF abnormal fund-flow list | flow type | ETF flow observations and detail series | Partial overlap with GF-004 and ETF data candidates | Methodology and units are provider-defined but uncited; no schema, implementation, error handling, or fixtures |
| GF-007 / `gf_fund_detail` | Fund profile, NAV, returns, rules | trade code | Fund metadata, performance, transaction rules | Strong overlap with CICCWM-006; partial with GUOSEN-005 | Subscription/redemption fields could be mistaken for action capability; must remain research-only; no schema, implementation, or tests |
| GF-008 / `gf_fund_invest` | Historical fixed-investment simulation | fund, amount, dates, frequency, strategy | Fees and simulated earnings/history | No confirmed direct duplicate; adjacent to backtesting/strategy candidates | Assumptions, survivorship/cost caveats, date validation, non-advice wording, output schema, implementation, and deterministic fixtures absent |

## GF Endpoint And Credential Boundary

Every draft targets the same remote endpoint and therefore depends on a third-party service. Before any controlled test, the project needs documented authorization, data-use terms, endpoint ownership verification, rate limits, credential scope/rotation, logging/redaction rules, and a human-approved network test plan. `GF_SKILLS_APIKEY` must remain external to the repository and must never be included in fixtures or reports.

## Promotion Gate

No wrapper may move beyond `draft` until it has: official authorization/license evidence; hyphen-case naming; a minimal callable implementation in an approved architecture; strict input and response schemas; bounded timeouts/retries; secret redaction; explicit financial caveats; offline fixtures and negative tests; duplicate-resolution rationale; and a signed human approval record. The formal installation directory remains undecided.
