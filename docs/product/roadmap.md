# InvestKit Product Roadmap

Status date: 2026-07-17

This roadmap separates implemented local research behavior from acquisition convenience, platform delivery, and release readiness. A milestone marked implemented in the working tree is not automatically released, production-ready, current, or suitable for an investment decision.

## Product sequencing rule

InvestKit defines research methods, evidence contracts, missing-data behavior, and persistence before adding a source adapter. Data acquisition is a producer of the normalized contract; it does not control analytical methods and never grants trading authority.

```text
method and evidence contract
→ normalized local bundle
→ deterministic research and durable review
→ approved acquisition producers
→ broader issuer evaluation
→ release and platform gates
```

## Completed local foundations

### v0.1 — Offline Harness baseline

Status: implemented locally.

- Explicit project initialization and ownership manifest.
- Codex adapter and governed first-party Skill installation.
- Versioned investment standards.
- Fictional Demo Provider, durable tasks, resume, and read-only doctor.
- No network, credential, brokerage, or third-party execution requirement.

### v0.2 — Investment Core Pack

Status: implemented locally.

- Security identification plus 12 Investment Core Skills.
- One deterministic 13-stage `company-deep-dive` Workflow.
- Structured facts, assumptions, estimates, unknowns, findings, risks, and warnings.
- Independent bear case and source-verification gates.
- Financial, earnings-quality, valuation, comps, earnings, thesis, catalyst, and report methods with explicit skip behavior.

### v0.3 — Real-Company Research MVP

Status: implemented in the working tree; release qualification remains a separate gate.

- Public `research --input ... --question ...` and imported-task resume commands.
- Closed Draft 2020-12 research-bundle schema and annotated template.
- Read-only, project-local File Provider with no network or subprocess behavior.
- Operation-specific multi-source lineage and neutral real-issuer analysis semantics.
- Canonical input snapshot and hash persisted before analysis; resume ignores later changes to the original file.
- Imported-task doctor checks for schema/hash/source/report/state corruption and historical/stale warnings.
- Conflict-preserving v0.2-to-v0.3 initialized-project migration.
- Checkout/wheel asset parity for the schema and template while preserving the demo path.
- Pinned Microsoft FY2025 acceptance evidence with supported financial calculations and intentional price, valuation, peer, consensus, transcript, and catalyst gaps.

The v0.3 boundary is useful but narrow: an analyst can research structured real-company evidence they prepare or obtain lawfully. InvestKit does not yet fetch, parse, refresh, or independently verify that evidence.

### Live A-share integration slice

Status: implemented and acceptance-tested for a bounded single-symbol workflow; not full-market or production-ready.

- Opt-in SSE, Guangfa, and clean-room CICCWM providers can acquire and normalize bounded identity, quote/history, F10, valuation, financial, news, and Dragon-Tiger evidence when the required credentials and network permission are available.
- One live `603868.SH` acceptance run completed the 13-stage workflow with three-provider provenance and honest unsupported consensus/DCF gaps.
- Provider planning, credentials, identity conflicts, finite-number checks, bounded payloads, immutable snapshots, resume, and doctor diagnostics are governed by the Harness.
- This slice does not prove all-symbol coverage, point-in-time consensus, full industry comparison, institution-grade uptime, or decision suitability.

## Next milestone — Decision Intelligence Core

Status: in progress. The first provider-neutral contract and analysis slice is implemented; licensed live consensus/industry acquisition and the complete decision layer remain pending.

The next milestone is not a full-annual-report parser. Normalized statements and key disclosures are the normal input; original filings are optional verification evidence for accounting-policy changes, footnotes, one-offs, related-party matters, conflicts, and high-impact claims.

Required work, in priority order:

1. Point-in-time industry comparison: common definitions, peer/industry medians, percentiles, growth, profitability, leverage, cash conversion, and valuation.
2. Broker consensus and revisions: contributor count, forecast dispersion, publication/as-of times, revision breadth, stale-data rules, and separation from company guidance and InvestKit estimates.
3. Auditable earnings forecasts: explicit operating drivers, bear/base/bull cases, estimate history, uncertainty ranges, and actual-versus-estimate attribution.
4. Valuation ensemble: guarded DCF/reverse DCF, comparable multiples, historical bands, scenario sensitivities, EV-to-equity bridge, and a target-value range whose assumptions and disagreements remain visible.
5. Evidence escalation: fetch or request original disclosure sections only when a material claim cannot be supported by normalized data or sources conflict.

Implemented first slice:

- Optional bundle records now carry a dated InvestKit forecast method/period ledger, a distinct point-in-time broker-consensus snapshot, and a named dated industry benchmark.
- Consensus validation requires a usable vintage, positive contributor count, fiscal periods, and valid dispersion bounds; it cannot be inferred from guidance or model estimates.
- Industry comparison requires classification, vintage, positive sample size, target/median definitions, and bounded percentile and emits target-minus-median evidence.
- DCF emits a persisted bear/base/bull per-share scenario range labeled as non-guaranteed and keeps missing consensus, forecast provenance, or historical bands explicit.

Market prices, consensus, filings, transcripts, news, peers, and proprietary fundamentals remain separate approved producers because they have different licenses, point-in-time semantics, and credential risks. No single producer makes a conclusion decision-ready.

## Broader issuer and research evaluation

Status: planned after the bounded live A-share integration slice.

- Add multiple issuers, sectors, fiscal calendars, accounting presentations, and incomplete-evidence profiles.
- Evaluate source conflicts, amendments/restatements, stale evidence, and cross-source definition alignment.
- Measure supported vs skipped capability coverage rather than rewarding prose completion.
- Add analyst review matrices for calculation accuracy, source attribution, overclaiming, and decision-unsuitable conclusions.
- Keep pinned offline fixtures so acquisition failures do not make core research tests nondeterministic.

This phase is needed before claiming generalized real-company normalization or robust current-company coverage.

## Release-readiness gate

Status: pending; not implied by implementation status.

A candidate release needs evidence for all of the following:

- full tests with no unexplained skips, type checks, coverage threshold, compilation, and static security/network/dependency checks;
- clean checkout and wheel flows for initialization, demo, imported run, resume, and final doctor without checkout-only assets;
- migration and rollback/failure evidence for unchanged, modified, interrupted, legacy-task, and unsafe project states;
- independent review of source semantics, unknown propagation, report safety, path boundaries, secret handling, and non-finite numeric behavior;
- version and documentation consistency, artifact inventory, changelog/release notes, and supported-platform declaration;
- owner approval of the exact release artifact and distribution action.

Passing local acceptance does not itself authorize publishing a package or labeling the project production-ready.

## Cross-platform delivery

Status: deferred until the Runtime, migration, and release contracts stabilize.

- Add explicit Claude, Cursor, and other adapter implementations.
- Preserve common Skill, Workflow, source, task, and report semantics across hosts.
- Add governed package add/update/uninstall lifecycle without overwriting user-owned assets.
- Test platform-specific path, permission, encoding, subprocess, and installation behavior.
- Avoid treating repository development helpers as shipping adapters.

## Capability expansion

Status: planned as explicit product stages after the Decision Intelligence Core.

1. Market Regime Pack: full-market industry rotation, macro regimes, liquidity, risk appetite, breadth, and market-state classification with point-in-time evidence.
2. Quant Pack: technical indicators, factor definitions, cross-sectional research, stock screening, strategy specification, and reproducibility.
3. Backtest Pack: point-in-time universes and fundamentals, delistings, survivorship and look-ahead controls, suspensions, corporate actions, price limits, capacity, slippage, fees, and tax assumptions.
4. Portfolio & Risk Pack: holdings, asset allocation, constrained research weights, exposure, correlation, concentration, risk budgets, scenario analysis, and stress testing.
5. Multi-Asset Pack: separate normalized contracts and market conventions for A shares, Hong Kong and US equities, bonds, futures, options, and FX; coverage is declared per venue and asset class rather than implied globally.
6. Monitoring & Reliability Pack: intraday freshness, schedules, alerts, retries, caching, provider fallback, reconciliation, observability, entitlement checks, and service-level evidence.

These remain research capabilities. They do not connect to brokerages, place trades, sign transactions, transfer funds, provide individualized advice as certainty, or promise returns.

### Permanent product boundary

Trade execution is not a future milestone. InvestKit must not connect to a brokerage, submit or stage orders, manage user funds, sign transactions, or automatically act on a portfolio recommendation. Portfolio weights and alerts are research outputs requiring human review.

## Supporting governance track

Third-party candidate research remains separate from product implementation. Raw assets are untrusted, are not executed or installed by default, and must retain provenance, license, security, decision, and review evidence. An adaptation draft or candidate decision does not make an asset approved first-party source.
