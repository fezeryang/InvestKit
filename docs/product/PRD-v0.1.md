# InvestKit PRD v0.1

## 1. Product Background

General AI assistants can summarize finance content, but they usually lack a governed research workspace, repeatable Skill evaluation process, financial method boundaries, source tracking, and safety controls. InvestKit is designed to become an investment research AI capability package that can be installed into Codex-like environments.

## 2. One-Sentence Definition

InvestKit is a governed investment research AI capability package that helps AI agents analyze companies, filings, financial statements, valuation methods, strategies, backtests, portfolios, risks, and sourced reports without touching real funds.

## 3. Target Users

- Investment research project owners.
- Analysts evaluating public companies or industries.
- Builders curating finance-related AI Skills.
- Quant researchers prototyping natural-language strategy workflows.
- AI operators who need auditable third-party Skill governance.

## 4. Core Capabilities

- Company fundamentals research.
- Financial statement analysis.
- Company valuation.
- Industry and peer comparison.
- News, announcements, and regulatory filing research.
- Natural-language quantitative strategy design.
- Historical backtesting.
- Portfolio risk analysis.
- Sourced investment research report generation.

## 5. Current Skill Research Phase Goal

The current phase establishes the system for open-source finance Skill discovery, registration, research, evaluation, adaptation, and acceptance.

The goal is not to collect the largest number of assets. The goal is a research system that is:

- traceable;
- repeatable;
- batch-processable;
- comparable;
- auditable;
- extensible.

## 6. v0.1 Scope

- Define project context and safety boundaries.
- Create directory structure for source intake, raw assets, reviewed records, reports, templates, and adapted work.
- Define SOP for third-party Skill handling.
- Define taxonomy for asset type and investment capability classification.
- Define acceptance criteria for research completion.
- Define a structured Schema for reviewed records.
- Define Batch 001 intake and the gate for starting governed static review.

## 7. Explicit Non-Goals

- Connecting to real brokerages.
- Automatic order placement.
- Real-money operations.
- Guaranteed return claims.
- High-frequency trading.
- Executing unaudited third-party scripts.
- Installing third-party Skills directly into production.
- Building a complete frontend or trading application.

## 8. Investment Risk Boundary

InvestKit supports investment research, financial data analysis, historical backtesting, and simulated research. It must not present conclusions as certain, guaranteed, or individualized financial advice. Research outputs must distinguish facts, assumptions, estimates, model outputs, and unknowns.

## 9. Third-Party Asset Governance Principles

- Preserve original sources and raw assets.
- Treat raw assets as untrusted.
- Prefer static analysis before any execution.
- Record license status honestly.
- Record permissions requested by scripts, tools, prompts, and dependencies.
- Separate raw assets from adapted work.
- Keep structured records and human-readable reports in sync.

## 10. Product Success Standards

v0.1 succeeds when a future operator can add candidate links or local files and Codex can process them through a consistent workflow that records source, license, capability, dependency, permission, security, financial, duplicate, adaptation, and testing information without pretending unreviewed assets are approved.
