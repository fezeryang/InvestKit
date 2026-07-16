# Capability Synthesis: Comparable Companies Analysis

Research date: 2026-07-16
Target capability: `comps-analysis`
Study decision: `extract` methods, independently reimplement; adopt no candidate package

## Scope And Responsibility Boundary

`comps-analysis` owns peer consideration, inclusion/exclusion, operating comparability, metric
definition and period alignment, valid multiple distributions, relative implied ranges, and the
EV-to-equity bridge for those ranges.

It requires a resolved security, target-company financial facts, a candidate peer dataset,
market-data as-of dates, currencies, estimate vintages, and persisted source IDs.

It must not:

- perform a standalone intrinsic DCF;
- accept a peer because a vendor or hard-coded list labels it comparable;
- replace missing, zero, or negative denominators with zero-valued multiples;
- apply an automatic premium/discount or call a median “fair value”;
- turn relative valuation into an investment recommendation.

Its primary workflow handoff is a structured peer-relative result consumed by downstream thesis,
bear-case, source-verification, and report stages. A standalone later valuation can consume it,
but it never back-writes the already completed valuation artifact in `company-deep-dive`.

## Search Scope And Evidence Controls

All 36 existing registry entries were searched; no new source was collected. Governing evidence:

- `.trellis/tasks/07-15-investment-core-pack/research/candidate-corpus.md`;
- `.trellis/tasks/07-15-investment-core-pack/research/valuation-earnings-candidate-study.md`;
- `.trellis/tasks/07-15-investment-core-pack/research/core-capability-boundaries.md`;
- `docs/security/security-policy.md`;
- `reports/project/current-state-audit.md`;
- `reports/project/guangfa-wrapper-review.md`.

Grade `A` is commit-pinned content with snapshot SHA-256, relevant files, and root-license
evidence. Grade `B` is hash-pinned local evidence with incomplete provenance/license. Grade `C`
is registry, tree, or documentation evidence only. Similar files in several repositories are not
counted as independent validation when section/hash comparison shows common lineage.

The review was static. No third-party Skill, script, validator, package, installer, dependency,
broker endpoint, or API was executed or installed, and no raw prompt or code was copied.

## Exact Method Evidence Read

| Evidence ID | Pin and archive SHA-256 | Grade/license | Exact files read | Relevance |
|---|---|---|---|---|
| `BATCH-001-001` Anthropic financial-services | commit `4aa51ed3d379731f8f9beff498d749580372699c`; SHA `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | A; Apache-2.0 root, nested terms may differ | `plugins/vertical-plugins/financial-analysis/skills/comps-analysis/SKILL.md`; `plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/valuation-methodologies.md`; selected peer/implied-value sections of `.../references/task3-valuation.md` | Peer table, metric choice, statistics, source comments, implied value |
| `BATCH-001-002` finance-skills | commit `87f688e175321f17d3a39b5d69da9fcfe39eadfb`; SHA `8ef20bfa7f5bae9267a64b23f88af4227a5f21ed2d7bd7f31d5f04c76d792284` | A; MIT root | `plugins/market-analysis/skills/company-valuation/SKILL.md`; `references/relative_valuation.md`; `references/dcf.md` | Peer hierarchy, sector applicability, negative-denominator fallback, EV/equity logic |
| `BATCH-001-003` LangAlpha | commit `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7`; SHA `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | C; Apache-2.0 root, adapted-file warning | `/tmp/investkit-langalpha-tree.json`; section/hash index of `skills/comps-analysis/SKILL.md` | Shorter variant/common-lineage signal |
| `BATCH-001-012` Hermes comps-analysis | commit `07be37d996be7df1965441ca8bdacdb3f884c7e2`; SHA `601d8154ed7dff4fa31fe317a534f5562bd29cfc7c66dcaeec828569a16cea3c` | C; MIT root | `/tmp/investkit-hermes-tree.json`; section/hash index of `optional-skills/finance/comps-analysis/SKILL.md` | Near-duplicate spreadsheet/source-comment structure |

The Hermes-versus-Anthropic no-index comparison found only 33 insertions and 32 deletions across
the 662-line comps Skill. LangAlpha is a shorter version of the same family. This is a provenance
and duplication warning, not three independent confirmations of quality.

## Searched But Lower-Depth Candidates

Saved tree metadata was searched for peers, multiples, comparable-company, and relative-valuation
material. The following had names or adjacent content but no design-changing deep evidence:

- `BATCH-001-007` InvestSkill, commit `6449af2d0fc410a6c541c5815c601ba9f649d791`, SHA
  `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5`,
  `/tmp/investkit-investskill-tree.json`.
- `BATCH-001-008` china-stock-research-skills, commit
  `d49f1f360deac57821d5d6b3aff664dff232acc6`, SHA
  `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2`,
  `/tmp/investkit-china-stock-tree.json`.
- `BATCH-001-009` HHFinAi equity research, commit
  `6e7ceef3c65287b7b88436fb4876f541b592a2ed`, SHA
  `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6`,
  `/tmp/investkit-hhfin-tree.json`.
- `BATCH-001-005` OctagonAI, commit `51e938c4d086f658de8bdcf734e864d34637167e`, SHA
  `d75c5acb6d9227232db8fa3859be61b97bea405b1f0f72143288f3f85cddf95f`,
  `/tmp/investkit-octagon-tree.json`: sector/multiple data Skills, mainly API-bound.

The other pinned repositories were searched in the bounded corpus but supplied no stronger
peer-selection or relative-value method than the files above.

## Data-Only, Blocked, And Unavailable Evidence

- `GF-003`, `adapted/skills/gf_stock_valuation/SKILL.md`, grade C: exposes PE/PB percentiles and
  profitability, leverage, cash-flow, growth, and comparison fields. Units, definitions,
  restatement policy, peer rationale, implied-value method, license, authorization, and API terms
  are incomplete or unknown. It informs a future provider schema only.
- `CICCWM-002`, archive SHA
  `97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208`, grade B/blocked:
  `standard/ciccwm-stock-finance-analysis/SKILL.md` documents statement periods and field/missing
  semantics, but not a professional comps method. License is unknown; home credential reads and
  credential-bearing telemetry block integration.
- `EASTMONEY-001`, archive SHA
  `24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15`, commit
  `61cfae47451f797d95ae4553ffcc7569b9957e7d`, MIT root: data/API candidate only, not executed.
- `GUOSEN-002` is an unavailable zero-byte placeholder, SHA
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; license and method are
  unknown. No insecure acquisition retry was attempted.

## Candidate Strengths And Weaknesses

### Anthropic comps-analysis

Strengths: industry-specific metric selection, periods and units, medians/quartiles, input
citations, and explicit warnings for negative EBITDA or unsuitable peers.

Weaknesses: vendor/MCP priority is treated as data quality; `IFERROR(...,0)` can erase missingness;
some margin-order claims are false as universal rules; spreadsheet formatting overwhelms the
analytical contract.

### finance-skills relative valuation

Strengths: a peer hierarchy, sector-specific multiple applicability, fallbacks for negative EPS
or EBITDA, fiscal/currency cautions, and correct distinction between enterprise and equity value.

Weaknesses: hard-coded peers, automatic 10–30% premiums/discounts, and a rule that two methods
must agree within 15% invite false precision and confirmation bias.

### Hermes and LangAlpha variants

Strength: they corroborate that peer tables, source comments, and spreadsheet output are common
design needs.

Weakness: near-duplicate lineage means they add little independent evidence and increase the risk
of accidentally copying a prompt family.

## Adopted, Modified, And Rejected Ideas

Adopted:

- explicit industry/metric applicability;
- a durable considered-peer ledger with inclusion and exclusion reasons;
- medians, quartiles, range, sample size, source comments, and EV/equity bridge;
- separate handling of enterprise multiples and equity multiples.

Modified:

- peer selection becomes evidence-based across business model, revenue mix, geography, scale,
  growth, margins, capital structure, fiscal period, and accounting policy;
- denominator invalidity is per peer/per metric, allowing other valid metrics to survive;
- periods, estimate vintages, currencies, conversion date/source, and market-data timestamp are
  first-class fields;
- outlier handling and selected multiple require recorded rationale rather than a vendor default.

Rejected:

- all MCP, web, yfinance, broker, or vendor execution paths;
- `IFERROR(...,0)`, missing-to-zero coercion, and zero/negative denominator multiples;
- hard-coded peer lists, mechanical premiums/discounts, fixed method blends, and universal
  agreement thresholds;
- treating a sector multiple or median as proof of fair value or as a trade signal.

## Final First-Party Method

1. Validate the target security, target financial facts, units, periods, currencies, dates, and
   source IDs.
2. Build a considered-peer ledger before calculating multiples.
3. Assess each candidate on business model, revenue mix, geography, scale, growth, margin,
   capital structure, fiscal calendar, and accounting policy.
4. Record `included` or `excluded` with a durable reason; never silently drop a peer.
5. Define each metric and align LTM/NTM/annual periods and expectation vintages.
6. Match enterprise-value multiples with enterprise metrics and equity multiples with equity
   metrics.
7. Mark zero, negative, or missing denominators invalid for that peer/metric; never fill with zero.
8. Preserve currency-conversion source/date and market-data as-of time.
9. Calculate valid sample size, median, quartiles, range, and disclosed outlier treatment.
10. Choose applicable distributions with evidence-based rationale and no automatic premium.
11. Apply the distribution to the target metric and complete cash/debt/minority/preferred and
    non-operating-asset adjustments as relevant.
12. Report implied ranges, peer sensitivity, comparability limits, unknowns, and warnings.

No defensible peer set or comparable metric definitions permits a structured `skipped` result.
A missing or negative denominator for one peer is not a valid reason to skip the whole capability.

## Output And Handoff Contract

The shared envelope contains `facts`, `assumptions`, `estimates`, `unknowns`, `findings`, `risks`,
`warnings`, `source_ids`, `method`, `skill`, and `completed|skipped|failed` status.

`method` records the peer ledger, metric definitions, periods/vintages, invalid observations,
currency conversions, distributions, outlier policy, selected rationale, implied ranges, and
EV-to-equity bridge. Facts retain source IDs; selections and exclusions remain assumptions or
method decisions rather than facts.

A standalone later `valuation-analysis` run may consume this artifact by reference and preserve its
disagreement with DCF. In `company-deep-dive`, thesis and report reconcile it with the already
completed valuation artifact. Comps must not duplicate upstream financial facts or write an
overall investment conclusion.

## Required Behavioral Evals

- Positive trigger: choose defensible peers, calculate valid trading multiples, and derive a
  sourced relative-value range.
- Near miss: an intrinsic DCF-only question does not trigger comps.
- Negative EBITDA excludes only EV/EBITDA and records the peer/metric reason.
- Missing EPS never becomes zero; P/E remains unavailable for that observation.
- A conglomerate is excluded from a pure-play peer set with a durable rationale.
- Different fiscal year-ends require comparable LTM/NTM normalization or a visible warning.
- GAAP/adjusted and actual/estimate definitions are not mixed.
- Currency conversion and both source and as-of date survive into the result.
- Median and quartiles use only valid observations and expose sample size.
- A one-observation distribution is flagged as weak rather than presented as robust.
- No defensible peer set yields valid `skipped`, not a borrowed sector median.
- An optional standalone handoff to a later valuation retains source IDs and does not duplicate facts.
- Source-ID mutation or invalid denominator inclusion fails validation.
- Output contains no automatic premium, trade action, or deterministic return claim.

## Security, License, And Final Rationale

Root Apache-2.0 and MIT evidence exists for the strongest snapshots, but nested-file permission is
not assumed. The Anthropic/Hermes/LangAlpha overlap raises provenance risk. GF license and API
authorization are unknown. CICCWM is blocked by unknown license plus credential, telemetry, and
home-read findings. Unavailable Guosen content remains `unknown`.

The first-party Skill, schemas, calculations, and Evals are therefore written independently.
The design uses several sources for method ideas, rejects their unsafe data paths and mechanical
heuristics, preserves missingness, and makes comps a disciplined upstream method result rather
than a vendor table or investment recommendation.
