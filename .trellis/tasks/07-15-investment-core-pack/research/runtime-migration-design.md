# Runtime Migration Design

## Baseline

The current v0.1 Runtime is a dependency-free Python 3.11 package with one Codex adapter, six installed Skills, seven specs, a six-operation fictional Demo Provider, a ten-step workflow, durable JSON/Markdown artifacts, resume, doctor, and wheel acceptance coverage.

The v0.2 change must preserve those Harness properties while replacing the thin analytical path with a professional capability graph.

## Capability Set Decision

Install 13 governed first-party Skill directories:

- one Runtime prerequisite: `security-identification`;
- 12 Investment Core Skills named in the v0.2 PRD.

`company-research` and `investment-report-writing` are superseded by `company-deep-research` and `investment-report`. They should not remain in the fresh v0.2 install manifest. Existing user-owned files are never deleted automatically; update/uninstall migration remains outside this phase.

Skill source directories may contain `SKILL.md`, `references/`, and `agents/openai.yaml`. Initialization must copy every approved regular file in each allowlisted first-party Skill directory, preserve relative paths, reject symlinks/escapes, create once, and record a mapping/hash per file. The installation target remains a delivery copy, never authoritative source.

## Workflow Decision

Use 13 persisted steps:

```text
security-identification
company-deep-research
business-model-analysis
financial-statement-analysis
earnings-quality-analysis
valuation-analysis
comps-analysis
earnings-analysis
investment-thesis
bear-case-analysis
catalyst-analysis
source-verification
investment-report
```

This adds the omitted `earnings-analysis` to the user's suggested list so the demo exercises all 12 Core Skills. Data retrieval is performed by the analytical step that first needs the dataset; it is not represented as a fake Skill.

## Intermediate Artifact Decision

Keep every v0.1 required task artifact and add:

```text
capabilities/
  security-identification.json
  company-deep-research.json
  ...
  investment-report.json
```

Each file is a result envelope with:

- `capability`, `status`, `skill`, and `method`;
- `facts` with stable claim IDs and source IDs;
- `assumptions` with rationale and materiality;
- `estimates` with method and material inputs;
- `unknowns`, `findings`, `risks`, and `warnings`;
- `source_ids` as the union of direct references;
- optional `skip_reason` and `missing_inputs` when status is `skipped`.

`findings.json` becomes an index/summary of these results rather than an unrelated parallel schema. `sources.json`, `assumptions.json`, and `risks.json` remain normalized cross-capability views.

Completed-step resume validates that the corresponding capability file is present, regular, inside the task root, schema-valid, and consistent with the step. Completed-task resume verifies every capability result and preserves all result/data/report bytes. Failed-task resume skips only validated completed steps.

## Demo Provider Decision

Retain the six v0.1 operations and add only the offline data operations required by named Core capabilities:

- `get_peer_comparables` for comps;
- `get_earnings_history` for earnings/earnings quality;
- `get_catalyst_events` for catalyst analysis.

All responses keep the existing demo/provenance metadata contract. These extensions serve concrete capabilities and do not create a standalone Provider platform. No live implementation, credential flow, or network behavior is added.

## Analysis Module Decision

Split capability logic out of the monolithic workflow:

```text
src/investkit/capabilities/
  catalog.py      # allowlisted Skills, descriptions, trigger/Eval metadata
  contracts.py    # immutable/enforced capability result schema helpers
  analysis.py     # deterministic offline investment methods
```

Keep orchestration/persistence in `research/workflow.py` and narrative rendering in `research/report.py`.

The offline methods must implement useful bounded logic:

- company and business-model facts, segments, economics, moat/management/capital-allocation observations;
- income-statement, balance-sheet, cash-flow trends and health ratios;
- accrual ratio, cash conversion, working-capital and one-off earnings-quality checks;
- DCF base/bull/bear scenarios and WACC/terminal-growth sensitivity with guardrails;
- peer-multiple medians, exclusions, implied equity/share values, and comparability warnings;
- earnings surprise, guidance/expectations change, drivers, and missing transcript handling;
- bull/base/bear thesis, evidence, KPIs, assumptions, falsifiers, and mandatory red team;
- catalysts with date/certainty/materiality/dependency/downside fields;
- claim/source existence, quality, date, and freshness verification;
- a non-advice report assembled only from structured results.

No result may infer a missing numeric value or present an assumption/model output as fact.

## Trigger And Eval Decision

Codex ultimately selects a Skill from its frontmatter description semantically. Offline Runtime tests cannot invoke or score a hosted model, so v0.2 uses two complementary checks without overstating them:

1. Every Skill publishes precise trigger and near-miss guidance in `SKILL.md` and a compact machine-readable trigger contract in its direct reference data.
2. A deterministic catalog evaluator runs positive and difficult near-miss fixture questions and verifies the intended include/exclude rules.

These are metadata/routing contract Evals, not claims about a particular hosted model's accuracy. Full agent-model trigger evaluation remains a later controlled evaluation surface.

## Fixture Decision

Expand the fictional Aurora Lantern Works fixture with:

- segment economics and business-model attributes;
- management/capital-allocation observations;
- three comparable fictional peers, including at least one excluded peer;
- multi-period earnings actual/expectation/guidance data;
- dated fictional catalysts and explicit unknowns;
- source records capable of resolving every fact claim.

The fixture remains `is_demo: true`, offline, non-sensitive, and clearly non-live.

## Doctor Decision

Doctor additionally checks:

- the 13-Skill allowlist and every mapped Skill file/reference hash;
- the `company-deep-dive` ID/version and exact 13-step order;
- trigger/Eval contract readability;
- all required Demo Provider operations and metadata;
- capability artifact envelopes and their status rules;
- all fact source IDs resolve;
- every estimate declares method/inputs and every assumption is separate from facts;
- mandatory bear-case/source-verification/report results completed;
- no installed legacy, raw, adapted, or otherwise unapproved Skill is treated as first-party.

As in v0.1, unmanaged user Skills are warnings and doctor never repairs state.

## Compatibility And Limits

- Fresh v0.2 initialization and repeat initialization are required.
- v0.2 does not implement automatic migration/removal for a v0.1 initialized user project because update/uninstall ownership is explicitly out of scope.
- v0.1 task files are not silently rewritten. Doctor should report version/workflow incompatibility clearly when applicable.
- Runtime remains Codex-only, offline, dependency-free, and independent of `.trellis/`.
