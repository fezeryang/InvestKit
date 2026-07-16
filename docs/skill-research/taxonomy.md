# Skill Research Taxonomy

## Target Form Categories

| Category | Definition | Typical Input | Typical Output | Boundary |
|---|---|---|---|---|
| Agent Skill | A self-contained instruction package with `SKILL.md` and supporting files for an AI agent. | User task, source docs, local files. | Guided agent behavior, reports, transformations. | Must be installable or adaptable as an agent Skill. |
| MCP or Tool | A callable tool, MCP server, CLI, API wrapper, or utility used by agents. | Tool arguments, API credentials, files. | Structured data or tool actions. | Not necessarily a Skill; may need wrapper instructions. |
| Data Provider | A source or connector for market, company, filing, macro, or news data. | Symbols, dates, endpoints, credentials. | Datasets, records, feeds. | Data access is not analysis by itself. |
| Quant Module | Code or logic for indicators, factors, portfolios, optimization, or backtesting. | Prices, factors, strategies, parameters. | Metrics, signals, backtest results. | Must be evaluated for assumptions and data leakage. |
| Agent | A broader autonomous agent implementation. | Goals, tasks, tools, memory. | Multi-step actions or reports. | May exceed safe InvestKit scope if it executes actions. |
| Workflow | A repeatable process or orchestration pattern. | Asset list, task state, analyst intent. | Ordered steps, checklists, batch outputs. | May become SOP or template instead of Skill. |
| Template | A reusable report, prompt, schema, notebook, or document shape. | Facts, metrics, research notes. | Formatted output. | Does not perform research alone. |
| Reference | Documentation, examples, educational material, or method notes. | Reading context. | Human or AI guidance. | Used as source material, not installed as executable capability. |
| Reject | Asset unsuitable for InvestKit. | Any candidate. | Rejection reason. | Includes unsafe, irrelevant, unverifiable, or incompatible assets. |

## Investment Capability Categories

| Category | Definition | Typical Input | Typical Output | Boundary |
|---|---|---|---|---|
| Company fundamentals research | Reviews business model, segments, moat, management, customers, suppliers, and strategy. | Company name, ticker, filings, presentations. | Fundamental research notes. | Must separate facts from analyst opinion. |
| Financial statement analysis | Analyzes income statement, balance sheet, cash flow, margins, growth, leverage, and quality. | Financial statements, periods, restatements. | Ratios, trends, accounting observations. | Must flag missing definitions and accounting differences. |
| Valuation | Estimates value using DCF, comparables, multiples, asset value, or scenario analysis. | Forecasts, peers, discount rates, multiples. | Valuation range and assumptions. | Must not imply guaranteed price targets. |
| Industry and peer comparison | Compares companies, sectors, business models, metrics, and competitive position. | Peer list, sector data, metrics. | Peer tables, relative strengths and risks. | Peer selection assumptions must be explicit. |
| Earnings and announcements | Reviews earnings releases, calls, guidance, investor days, and corporate announcements. | Press releases, transcripts, filings. | Event summaries and implications. | Must distinguish company claims from verified data. |
| News and event analysis | Connects market, legal, product, macro, or geopolitical events to companies or sectors. | News articles, dates, affected entities. | Event timeline and risk notes. | Source quality and recency matter. |
| Macro research | Analyzes rates, inflation, GDP, commodities, currencies, policy, and cycles. | Macro time series, policy text, calendars. | Macro scenario notes. | Must avoid overclaiming causal certainty. |
| Technical analysis | Uses price, volume, trend, momentum, volatility, and chart patterns. | OHLCV data, indicators, windows. | Signals, levels, indicator summaries. | Must not be presented as deterministic prediction. |
| Factor research | Studies factor definitions, exposures, returns, risk, crowding, and robustness. | Security returns, fundamentals, factor formulas. | Factor diagnostics and results. | Must check lookahead bias and survivorship bias. |
| Strategy design | Translates research ideas into rules, hypotheses, and constraints. | Natural language hypothesis, universe, data. | Strategy specification. | Design is not proof of profitability. |
| Backtesting | Tests strategies on historical data. | Prices, events, rules, costs, calendars. | Performance metrics and diagnostics. | Must account for costs, bias, and sample limits. |
| Portfolio | Analyzes holdings, weights, exposures, allocation, and diversification. | Holdings, prices, benchmarks. | Allocation and exposure reports. | Must not trade or rebalance real accounts automatically. |
| Risk management | Measures drawdown, volatility, liquidity, concentration, scenario, and factor risks. | Portfolio, returns, factors, scenarios. | Risk report and limits. | Risk metrics are estimates, not guarantees. |
| Data acquisition | Retrieves or prepares financial, filing, market, macro, or news data. | Symbols, dates, endpoints, credentials. | Clean or raw datasets. | Must respect license and access restrictions. |
| Source verification | Checks citations, provenance, dates, filings, and data lineage. | URLs, files, claims, records. | Source audit and confidence notes. | Verification may still end with unknown. |
| Report generation | Produces sourced investment research reports. | Research notes, metrics, sources. | Structured report with citations and caveats. | Must not fabricate sources or results. |
