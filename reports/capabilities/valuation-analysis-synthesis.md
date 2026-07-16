# Capability Synthesis: Valuation Analysis

Research date: 2026-07-16
Target capability: `valuation-analysis`
Study decision: `extract` methods, independently reimplement; adopt no candidate package

## Scope And Responsibility Boundary

`valuation-analysis` owns intrinsic scenario valuation, supported historical-valuation context,
method reconciliation, sensitivity analysis, and the EV-to-equity bridge.

It requires normalized financial history, explicit forecast drivers, capital structure, currency,
valuation date, and source IDs. It may consume a completed `comps-analysis` result in a standalone
reconciliation or from a prior task; the ordered workflow's current comps stage runs afterward.

It must not:

- select or curate peers;
- fetch live data or bind to a vendor;
- turn a missing input into zero or a generic default;
- issue a buy/sell instruction, deterministic target, or return promise;
- hide disagreement between DCF, historical context, and comps behind fixed weights.

Its primary handoff is a structured valuation result for `investment-thesis`,
`bear-case-analysis`, `catalyst-analysis`, and `investment-report`.

## Search Scope And Evidence Controls

The search covered all 36 existing rows in `registry/inbox/sources.csv`; it added no candidate.
The governing corpus and comparison record were:

- `.trellis/tasks/07-15-investment-core-pack/research/candidate-corpus.md`;
- `.trellis/tasks/07-15-investment-core-pack/research/valuation-earnings-candidate-study.md`;
- `.trellis/tasks/07-15-investment-core-pack/research/core-capability-boundaries.md`;
- `docs/security/security-policy.md`;
- `reports/project/current-state-audit.md`;
- `reports/project/guangfa-wrapper-review.md`.

Grade `A` means commit-pinned content, snapshot SHA-256, relevant files, and root-license evidence
were read. Grade `B` means hash-pinned local content with incomplete license/provenance. Grade `C`
means registry, tree, or documentation evidence only. Root licenses do not approve copying every
nested file.

No third-party script, prompt, installer, package, API, or dependency was executed, imported,
sourced, installed, or copied into first-party source during this synthesis.

## Exact Method Evidence Read

| Evidence ID | Pin and archive SHA-256 | Grade/license | Exact files read | Relevance |
|---|---|---|---|---|
| `BATCH-001-001` Anthropic financial-services | commit `4aa51ed3d379731f8f9beff498d749580372699c`; SHA `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | A; Apache-2.0 root, nested terms may differ | `plugins/vertical-plugins/financial-analysis/skills/dcf-model/SKILL.md`; `.../scripts/validate_dcf.py`; `plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/valuation-methodologies.md`; selected method/QC sections of `.../references/task3-valuation.md`; `plugins/agent-plugins/valuation-reviewer/agents/valuation-reviewer.md` | DCF chain, scenarios, sensitivity, valuation review, triangulation |
| `BATCH-001-002` finance-skills | commit `87f688e175321f17d3a39b5d69da9fcfe39eadfb`; SHA `8ef20bfa7f5bae9267a64b23f88af4227a5f21ed2d7bd7f31d5f04c76d792284` | A; MIT root | `plugins/market-analysis/skills/company-valuation/SKILL.md`; `references/dcf.md`; `references/relative_valuation.md`; `references/wacc_erp_rates.md`; `plugins/market-analysis/skills/saas-valuation-compression/SKILL.md` | Applicability, capital costs, DCF/relative split, failure cases |
| `BATCH-001-003` LangAlpha | commit `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7`; SHA `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | C; Apache-2.0 root with stated adapted Skills | `/tmp/investkit-langalpha-tree.json`; section/hash index of `skills/dcf-model/SKILL.md` | Duplication/provenance check, not independent method weight |
| `BATCH-001-011` Claude financial-model cookbook | commit `67ce644d33e5933f0bcc0b6eb4113df41bbf3a8f`; SHA `0a63b2cc4d1271dc59106cbfceff27ea244e0fb43868d72e00e8e307c80a4c37` | C; MIT root | `/tmp/investkit-cookbooks-tree.json` locating `skills/custom_skills/creating-financial-models/dcf_model.py` | Script existence only; stronger method evidence made code review unnecessary |
| `BATCH-001-012` Hermes comps-analysis | commit `07be37d996be7df1965441ca8bdacdb3f884c7e2`; SHA `601d8154ed7dff4fa31fe317a534f5562bd29cfc7c66dcaeec828569a16cea3c` | C; MIT root | `/tmp/investkit-hermes-tree.json`; section/hash index of `optional-skills/finance/dcf-model/SKILL.md` | Near-duplicate lineage signal, not a separate vote |

The Hermes-versus-Anthropic no-index comparison found only 34 insertions and 28 deletions across
the 1,270-line DCF Skill. LangAlpha also carries a closely overlapping structure. These facts
increase copy/provenance risk and prevent counting the three repositories as independent support.

## Searched But Lower-Depth Candidates

The following registered, commit-pinned snapshots were searched through saved tree metadata for
valuation-related names. Their content was not used as deep method evidence:

- `BATCH-001-007` InvestSkill, commit `6449af2d0fc410a6c541c5815c601ba9f649d791`, SHA
  `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5`,
  `/tmp/investkit-investskill-tree.json`: DCF and stock-valuation names only.
- `BATCH-001-008` china-stock-research-skills, commit
  `d49f1f360deac57821d5d6b3aff664dff232acc6`, SHA
  `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2`,
  `/tmp/investkit-china-stock-tree.json`: scenario/strategy material, not independently assessed.
- `BATCH-001-009` HHFinAi, commit `6e7ceef3c65287b7b88436fb4876f541b592a2ed`, SHA
  `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6`,
  `/tmp/investkit-hhfin-tree.json`: valuation-method references only.
- `BATCH-001-014` Vibe-Trading, commit `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722`, SHA
  `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872`,
  `/tmp/investkit-vibe-trading-tree.json`: valuation material embedded in a trading system.

`BATCH-001-004`, `005`, `006`, `010`, and `013` were also present in the bounded tree search but
showed no design-changing intrinsic-valuation method for this capability.

## Data-Only, Blocked, And Unavailable Evidence

- `GF-003`, `adapted/skills/gf_stock_valuation/SKILL.md`, grade C: documents PE/PB current,
  average, percentile, profitability, leverage, cash-flow, and report-period fields. License,
  authorization, metric definitions, restatement policy, API behavior, and terms are unknown.
  It is a data-contract reference only.
- `CICCWM-002`, archive SHA
  `97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208`, grade B/blocked:
  the member `standard/ciccwm-stock-finance-analysis/SKILL.md` informs periods, field names, and
  empty-value semantics. License is unknown; home-config credential access and credential-bearing
  telemetry block integration.
- `EASTMONEY-001`, archive SHA
  `24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15`, archive commit
  `61cfae47451f797d95ae4553ffcc7569b9957e7d`, MIT root: a possible data/API source, not a
  professional valuation method; it was not executed.
- `GUOSEN-002` is a zero-byte placeholder with SHA
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; content and license are
  unavailable. `GUOSEN-003..006` are absent. No TLS control was weakened to retrieve them.

## Candidate Strengths And Weaknesses

### Anthropic financial-services

Strengths: complete FCFF chain, explicit WACC, EV/equity bridge, bull/base/bear blocks, input
citations, terminal-value checks, and an odd sensitivity grid centered on base assumptions.

Weaknesses: it directs web/MCP and Python execution; some generic percentage bands appear as
rules; negative net debt can become a questionable negative WACC debt weight; its validator and
sheet-placement instructions disagree; ratings and upside language exceed InvestKit's boundary.

### finance-skills

Strengths: company-type applicability, DCF/relative separation, gross-debt WACC weights, SBC and
cyclicality cautions, banks/REIT exceptions, and negative-denominator fallbacks.

Weaknesses: yfinance installation/calls, stale hard-coded defaults, crude absolute-NWC forecasting,
arbitrary method weights and adjustments, an unjustified average of Gordon and exit terminal
values, and conflicting behavior when terminal growth is not below WACC.

### Initiating-coverage references

Strengths: top-down/bottom-up revenue drivers, target capital structure, peer-implied value, range,
and method reconciliation.

Weaknesses: precedent transactions and recommendation/target-price output are outside this slice;
fixed method weights are too readily presented.

## Adopted, Modified, And Rejected Ideas

Adopted:

- FCFF/UFCF construction with explicit input lineage;
- bull/base/bear scenario blocks and range presentation;
- EV-to-equity bridge and valuation-method reconciliation;
- source-aware terminal-value, formula, and sensitivity checks.

Modified:

- WACC uses market equity and gross interest-bearing debt or a documented target structure;
- historical multiples become point-in-time series with aligned definitions and dates;
- the sensitivity grid is odd-dimensional and its center must exactly reproduce base case;
- optional prior/standalone peer-relative output is consumed from `comps-analysis`, not recalculated here;
- exit-multiple terminal value is a separate cross-check, not an averaged answer.

Rejected:

- all raw data fetch, MCP, yfinance, Python execution, and vendor priority instructions;
- negative net debt as a negative WACC weight;
- silent terminal-growth caps or generic default assumptions;
- `IFERROR`/zero substitution, fixed valuation blends, mechanical premiums, and unsupported SaaS
  compression heuristics;
- ratings, trade actions, guaranteed returns, and deterministic price targets.

## Final First-Party Method

1. Validate security, fiscal periods, units, currencies, actual/estimate labels, and source IDs.
2. Register business-driver assumptions with rationale, materiality, and evidence linkage.
3. Forecast revenue, operating margin, tax, D&A, CapEx, and change in NWC.
4. Calculate UFCF as NOPAT + D&A - CapEx - change in NWC.
5. Calculate WACC from valid capital structure inputs; keep net debt out of WACC weighting.
6. Require positive diluted shares and `WACC > terminal growth` for every scenario and grid cell.
7. Calculate perpetuity-growth terminal value and a disclosed exit-multiple cross-check if valid.
8. Bridge EV to equity through cash, debt, minority interest, preferred stock, and material
   non-operating assets.
9. Run internally consistent bull/base/bear driver sets.
10. Run an odd sensitivity grid whose center reproduces the base result.
11. Add aligned historical-valuation context only when point-in-time definitions are comparable.
12. Reconcile DCF and historical context; when an optional prior/standalone comps artifact is supplied, preserve its disagreement. In `company-deep-dive`, thesis/report perform current-run comps reconciliation later.

Missing forecast drivers, capital structure, or shares produce explicit unknowns and a bounded
`skipped` or `failed` method. A partial result may state which methods could not run; it may not
manufacture a precise value.

## Output And Handoff Contract

The result uses the shared envelope: `facts`, `assumptions`, `estimates`, `unknowns`, `findings`,
`risks`, `warnings`, `source_ids`, `method`, `skill`, and `completed|skipped|failed` status.

`method` records scenario drivers, WACC components, terminal method, sensitivity axes/grid,
historical definitions, EV-to-equity items, and method-reconciliation notes. Every estimate names
its method and material input/assumption IDs.

The result may accept a prior/standalone `comps-analysis` artifact by reference and preserves its
source IDs. It hands range, sensitivities, limitations, and disagreement forward; it does not
rewrite financial facts, back-write a completed workflow stage, or create a thesis conclusion.

## Required Behavioral Evals

- Positive trigger: request a sourced base/bull/bear DCF with sensitivity and EV/equity bridge.
- Near miss: a request to select peers and calculate only trading multiples triggers comps, not
  valuation.
- Complete DCF: the center sensitivity cell equals the base value exactly.
- Invalid terminal relation: every cell with `WACC <= g` is rejected/skipped without mutating `g`.
- Negative net debt: equity value rises, but the WACC debt weight never becomes negative.
- Missing diluted shares: no per-share value is emitted; the gap and impact are explicit.
- Missing forecast driver or capital structure: no generic default silently creates precision.
- Cyclical fixture: normalized/mid-cycle inputs are explicit assumptions.
- Historical mismatch: inconsistent fiscal definitions remain unknown/warned and are not combined.
- DCF/comps disagreement: both ranges and the reason for divergence remain visible.
- Source mutation: an unresolved source ID fails result validation/source verification.
- Safety language: output contains no trade instruction, rating, or deterministic return claim.

## Security, License, And Final Rationale

The strongest repositories have root Apache-2.0 or MIT evidence, but nested provenance and the
LangAlpha/Hermes duplication pattern make direct copying inappropriate. GF authorization and
license remain unknown. CICCWM license is unknown and its audited credential, telemetry, and home
access behavior triggers stop-integration rules. Guosen evidence is unavailable.

InvestKit therefore independently writes the Skill, schemas, calculations, and Evals from the
capability requirements above. No raw third-party package is adopted. The final design combines
multiple method ideas, corrects their financial and safety defects, remains provider-neutral, and
keeps valuation subordinate to sourced research rather than trading action.
