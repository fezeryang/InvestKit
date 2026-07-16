# InvestKit Product Development Roadmap

InvestKit develops investment capability before live-data infrastructure. A capability first defines its research method, evidence contract, missing-data behavior, and persistence needs; an optional Provider is added later only when a named capability requires data the offline path cannot supply.

Third-party asset research is a separate supporting track. It does not set product priorities or authorize installation, execution, copying, or live integration.

## M0 — Product Definition Baseline

Status: documented.

- Define InvestKit as both an investment-capability layer and an Agent Harness framework.
- Define authoritative first-party source and generated host-platform targets.
- Separate `.trellis/` development tooling from the InvestKit Runtime.
- Establish security, provenance, persistence, and non-trading boundaries.

## M1 — v0.1 First Offline Harness Vertical Slice

Status: implemented locally as the baseline; this status does not claim a current release or whole-suite verification result.

The v0.1 slice established one Codex-only, dependency-free, offline path:

```text
local install → investkit init → standards and governed Skills
→ investkit demo research → durable task and sourced report
→ resume in a later process → investkit doctor
```

It provides create-once initialization, a manifest, a fictional Demo Provider, durable research artifacts, safe resume, and read-only diagnostics. Live data, additional platform adapters, optional packages, brokerage connectivity, and trading remain outside the baseline.

## M2 — v0.2 Investment Core Pack

Status: implemented and verified locally in the current working tree; not released or production-ready.

The pack contains one Runtime prerequisite, `security-identification`, plus exactly 12 Investment Core Skills:

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

`investkit demo research` composes the prerequisite and all 12 Core Skills through the 13-stage `company-deep-dive` Workflow. Every completed or validly skipped stage writes a structured capability envelope. Facts, assumptions, estimates, unknowns, findings, risks, warnings, and source IDs remain separate; bear-case analysis and source verification are mandatory gates before report assembly.

Required outcomes:

- governed Skill contracts, direct method references, and positive/near-miss trigger Evals;
- deterministic offline company, financial, valuation, comps, earnings, thesis, red-team, catalyst, verification, and report behavior;
- one capability artifact per stage plus the durable v0.1 task root;
- missing-data, skip, failure, corruption, and resume behavior that never fabricates values;
- nested Skill installation mappings and checksums;
- capability map and product documentation aligned with actual local behavior;
- no network, API key, brokerage, third-party execution, or live-data claim.

The durable status taxonomy is documented in [`docs/product/investment-capability-map.md`](../docs/product/investment-capability-map.md).

## M3 — Advanced Research Pack

Status: planned after the Investment Core Pack.

- Dedicated industry, competitor, supply-chain, and thematic research.
- Full initiating-coverage and earnings-report formats.
- Deeper management, governance, and capital-allocation workflows.
- Historical valuation datasets and richer event/call analysis.
- Additional bounded research Agents where an Agent is the right product form.

## M4 — Quant Pack

Status: planned after the Advanced Research Pack.

- Factor research and strategy specification.
- Historical backtesting and validation.
- Bias, cost, calendar, benchmark, and reproducibility controls.
- Optional package lifecycle only after governed add/update behavior exists.

Quant remains research-only and cannot introduce brokerage or execution authority.

## M5 — Portfolio & Risk Pack

Status: planned after the Quant Pack.

- Portfolio review and exposure analysis.
- Correlation and concentration analysis.
- Research-only position-sizing frameworks with explicit assumptions.
- Scenario and stress testing.
- Portfolio-level risk artifacts distinct from the company-level bear case.

## M6 — Capability-Driven Real-Data Provider Expansion

Status: deferred until the Core, Advanced Research, Quant, and Portfolio & Risk capability contracts establish concrete data needs.

Provider work begins from a named capability gap, not from a general data-platform goal. For each approved adapter:

1. name the capability and required normalized fields;
2. statically review authorization, license, provenance, API behavior, security, and redistribution constraints;
3. implement an InvestKit-owned adapter behind the unified interface;
4. keep credentials opt-in and outside source, logs, reports, and task artifacts;
5. preserve provider identity, source time, retrieval time, market, currency, definitions, and warnings;
6. add cache, rate-limit, retry, and error behavior appropriate to that capability; and
7. require owner approval before first-party release.

No Provider may place orders, sign transactions, transfer funds, or turn research output into execution.

## M7 — Cross-Platform Delivery Lifecycle

Status: planned after the capability and installation contracts stabilize.

- Add Claude, Cursor, and other explicit adapters beyond Codex.
- Add governed package add, update, and uninstall behavior.
- Preserve user research workspaces and installation ownership.
- Expand diagnostics without changing common task, artifact, and evidence semantics.

## Supporting Track — Third-Party Asset Research

The locked candidate registry and static research may inform first-party methods, references, or future Provider requirements. Every candidate retains one explicit processing decision and honest license/security evidence. Raw third-party assets are never installed or executed as product code, and unavailable evidence remains `unknown`.
