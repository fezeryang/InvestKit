# Business Model Analysis Capability Synthesis

Research date: 2026-07-16

Task: InvestKit v0.2 — Investment Core Pack

Decision: independently implement a first-party Agent Skill from cross-candidate method evidence.

## Outcome

The corpus supports a model-led capability that explains who pays, what value is delivered, how revenue becomes cash, which resources and channels are required, and where durability or fragility resides.

The synthesis uses order-to-cash state discipline from China-stock, conditional unit-economics families from Anthropic, filing anatomy and segment comparison from Octagon, and period/dimension normalization from Longbridge.

No candidate alone handles hybrid models, unavailable customer-level data, changed segment definitions, source lineage, missing-data skips, and downstream composition safely.

## Responsibility Boundary

Owns:

- payer, user, value proposition, product/service delivery, pricing basis, channel, and value-chain position;
- revenue-model classification and model-specific economics;
- product, segment, geography, and customer mix without combining incompatible dimensions;
- recurrence, concentration, cost/capital intensity, working-capital dependence, and cash-conversion mechanics;
- unit economics only when the model and inputs make them applicable;
- business-model strengths, fragilities, falsification indicators, and unknowns.

Does not own:

- general company history, governance, and source discovery;
- statement normalization or accounting-quality audit;
- full competitive-advantage, industry, or peer-comps studies;
- valuation, investment thesis, catalyst calendar, or report assembly;
- buy/sell actions, position advice, target returns, or universal health grades.

It consumes the company fact base plus normalized segment and financial evidence.

It hands revenue drivers, model-specific metrics, vulnerabilities, and missing inputs to financial, valuation, thesis, bear-case, and catalyst capabilities.

## Corpus Search And Evidence Grades

All 36 registered rows were searched; no intake scope was expanded.

All 14 commit-pinned GitHub trees were searched, while only the files named below were treated as method evidence.

Grade A means commit/hash-pinned content plus identifiable root-license evidence; it does not approve file copying.

Grade B means hash-pinned local evidence with incomplete provenance or license.

Grade C means registry metadata or draft description only.

## Exact Design-Changing Evidence

| Candidate | Exact source state | Files actually read | Design-changing evidence |
|---|---|---|---|
| BATCH-001-008 China-stock | commit d49f1f360deac57821d5d6b3aff664dff232acc6; snapshot SHA-256 4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2; MIT root; grade A | skills/business-decomposition-order-quality/SKILL.md, skills/strategy-business-transition/SKILL.md, skills/industry-competition-moat/SKILL.md | signed order, backlog, delivered revenue, and collected cash are different states; transition claims need falsifiable milestones |
| BATCH-001-001 Anthropic | commit 4aa51ed3d379731f8f9beff498d749580372699c; snapshot SHA-256 9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945; Apache-2.0 root with possible nested terms; grade A | plugins/vertical-plugins/private-equity/skills/unit-economics/SKILL.md | route metrics by revenue model; ARR bridge, retention, CAC/payback, concentration, recurring mix, and margin waterfall are conditional diagnostics |
| BATCH-001-005 OctagonAI | commit 51e938c4d086f658de8bdcf734e864d34637167e; snapshot SHA-256 d75c5acb6d9227232db8fa3859be61b97bea405b1f0f72143288f3f85cddf95f; MIT root; grade A | skills/sec-business-desc-analysis/SKILL.md, skills/revenue-product-segmentation/SKILL.md | filing business anatomy, value-chain and revenue-model taxonomy, disclosure comparison, and segment-share calculations |
| BATCH-001-010 Longbridge | commit d68372ab584a77b3cb2a078a05c1322267729100; snapshot SHA-256 79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e; MIT root; grade A | skills/longbridge-fundamentals/SKILL.md, skills/longbridge-fundamentals/references/main-business-analysis.md sections 1–355 and 592–654 | period/unit/split-dimension continuity, acquisition/disposal bridges, CR1/CR3/HHI, contribution to growth, and source controls |

## Strengths, Weaknesses, And Disposition

| Candidate | Strengths | Weaknesses and risks | InvestKit disposition |
|---|---|---|---|
| China-stock | Links segments, customers, margins, receivables, and cash; prevents orders/backlog from becoming revenue; uses observable transition milestones | Project-company and A-share bias; three overlapping Skills lack one cross-market schema; moat work can exceed this boundary | Adopt order-to-cash states and falsifiable milestones; route broader moat work downstream |
| Anthropic Unit Economics | Selects an economic model first; covers recurring revenue, cohorts, acquisition cost, concentration, margins, and hidden gross churn | SaaS benchmarks are not universal; public-company cohort data is often absent; score lacks provenance/confidence/missing-data rules | Adopt conditional metric families; require sourced benchmark context and skip inapplicable formulas |
| OctagonAI | Anchors analysis in disclosures and changes; separates product, customer, channel, geography, and regulation; tests segment contribution | Requires Octagon MCP; fixed concentration cutoffs ignore sectors; no formal missing-input or claim/source schema | Adopt questions/dimensions; independently implement over InvestKit facts without MCP or absolute labels |
| Longbridge | Distinguishes reporting dimensions; records period/unit/restatement/M&A continuity; calculates concentration and growth contribution transparently | Mandates vendor CLI/login/network/update; thresholds misclassify sectors; segment arithmetic alone cannot establish durability | Adopt normalization/decomposition; reject vendor routing, auto-update, and universal interpretations |

## Supporting, Data-Only, And Unavailable Evidence

BATCH-001-014 Vibe-Trading, commit 531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722 and snapshot SHA-256 8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872, reinforces caliber consistency and revision propagation but its publication/trading frame is rejected.

GF-002, adapted/skills/gf_stock_f10/SKILL.md, SHA-256 c07adbf7d094bb93e2d2ddceaed687480ca05444b97312d7daad4f64a219cfc0, can describe business scope and industry fields only.

GF-003, adapted/skills/gf_stock_valuation/SKILL.md, SHA-256 49421c138609516b44aa6680808143f786ade30eda532e21dc6ebbdb791a5588, identifies profitability, leverage, cash-flow, growth, year, and report-type fields.

Both Guangfa drafts are grade C: authorization, license, API terms, field definitions, units, restatement behavior, response schemas, and fixture behavior remain unknown.

EASTMONEY-001, archive commit 61cfae47451f797d95ae4553ffcc7569b9957e7d and SHA-256 24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15, is a data-interface candidate rather than a professional business-model method.

CICCWM-002, archive SHA-256 97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208, provides financial field semantics only; its license is unknown and execution is blocked.

GUOSEN-002 is zero-byte with SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

Guosen's absent content, licenses, and method quality remain unknown; unavailability is not evidence of either merit or defect.

No Provider is necessary for the offline Eval. A future adapter may be proposed only for a named missing datum.

## Adopted, Modified, And Rejected Design Ideas

Adopted:

- revenue-model routing before metric selection;
- distinct order, backlog, delivery, recognition, billing, and collection states;
- separate product, segment, geography, customer, and channel dimensions;
- conditional recurrence, cohort, take-rate, backlog, utilization, and unit-economics diagnostics;
- concentration and growth-contribution calculations with explicit inputs.

Modified:

- NDR, CAC, HHI, margins, and concentration become model outputs or contextual findings, not grades;
- sector thresholds require a cited benchmark and applicability statement;
- hybrid companies receive multiple model components and a reconciliation;
- missing customer/cohort data produces unknowns and skipped calculations, not averages;
- acquisitions, price, volume, mix, FX, and reclassification effects are separated where evidence permits.

Rejected:

- one universal “good business” score;
- training-data or industry-average imputation;
- vendor-exclusive source rules, MCP dependency, auto-update, and login instructions;
- combining business-model durability with final moat, valuation, or thesis conclusions;
- treating signed demand, backlog, revenue, and cash as interchangeable;
- buy/sell framing or pseudo-precise target outcomes.

## Final InvestKit Method

1. Validate identity, as-of date, company fact-base version, covered periods, currency, units, and source IDs.
2. Classify product, service, subscription, transaction/usage, advertising, licensing, project/order, financial-spread, or hybrid components.
3. Map payer versus user, value proposition, pricing basis, contract duration, channel, delivery mechanism, and value-chain position.
4. Normalize each disclosed reporting dimension independently and document definition changes.
5. Trace economic states from demand or contract through delivery, recognition, billing, working capital, and cash.
6. Analyze mix, concentration, contribution to growth, margins, capital intensity, and working-capital dependence where supported.
7. Apply only model-relevant metrics and record formulas, periods, denominators, sources, and applicability.
8. Separate organic, acquisition, price, volume, mix, FX, pull-forward, and accounting-classification drivers.
9. Identify durable mechanisms, fragile dependencies, falsification indicators, alternative explanations, and missing inputs.
10. Emit a partial completed result or justified skip without inventing absent customer, cohort, cost, or margin data.

## Output Contract And Handoffs

The standard capability envelope contains status plus distinct facts, assumptions, estimates, unknowns, findings, risks, warnings, source_ids, method, and Skill version.

Facts include typed business-model components and persisted source IDs.

Estimates include metric name, formula, input references, period, units, and applicability.

Unknowns state the missing evidence and which analysis was prevented.

Findings distinguish mechanism from interpretation and list supporting fact IDs.

Financial-statement-analysis receives reporting dimensions and operating-driver context but remains authoritative for accounting normalization.

Valuation-analysis receives revenue/cost drivers and business-specific scenario variables, not a preselected value.

Investment-thesis and bear-case-analysis receive strengths, fragilities, falsifiers, and material unknowns without a verdict.

## Security, License, And Honest Unknowns

MIT and Apache-2.0 root texts do not approve wholesale nested-file reuse.

Anthropic sub-asset terms and file-level compatibility require separate review before any code reuse.

Longbridge and Octagon network/tool instructions remain untrusted and were not followed.

CICCWM reads home-directory credentials and emits credential-bearing telemetry; five sibling packages also weaken TLS. Integration remains blocked.

Guangfa authorization, API terms, redistribution permission, and implementation behavior are unknown.

No credentialed Provider, API call, or general data platform is authorized by this synthesis.

## Non-Execution And No-Copy Proof

The research method was static text inspection recorded in the task study and existing audits.

No candidate script, Skill, installer, CLI, MCP, package manager, endpoint, or API was executed, installed, imported, sourced, or called.

No home-directory credential was read and no TLS control was weakened.

No raw file was copied into skills/, adapted/skills/, a host target, or Runtime code.

The final method is newly expressed from multiple candidates and InvestKit's evidence, persistence, and safety contracts; no prompt, code, or output template was copied wholesale.

## Required Evals

1. Positive trigger: analyze a fictional hybrid product-plus-subscription company.
2. Near miss: a pure three-statement ratio request must route to financial-statement-analysis.
3. Near miss: peer-multiple comparison must route to comps-analysis.
4. Payer/user distinction: advertising users must not be mislabeled as paying customers.
5. Order-state integrity: backlog must not be counted as delivered revenue or cash.
6. Missing cohort data: skip retention/LTV calculations while preserving other analysis.
7. Hybrid model: reconcile component economics without forcing a single SaaS template.
8. Dimension integrity: do not aggregate product and geography as one segment axis.
9. Definition change: break or bridge trends when segment definitions change.
10. Acquisition effect: separate acquired growth from organic growth when evidence exists.
11. Threshold safety: HHI or concentration values may be facts, but “high” requires context.
12. Formula integrity: every estimate records period, unit, inputs, and method.
13. Source integrity: every factual finding has persisted source IDs.
14. Handoff: valuation consumes drivers while financial analysis retains accounting authority.
15. Safety: no model output becomes a trade instruction or deterministic return claim.

## Final Rationale

Business-model-analysis should explain economic mechanics and their evidence-backed durability, not reward a familiar business archetype.

Conditional diagnostics, explicit state transitions, and honest missing data make the capability portable across sectors.

Its bounded handoffs keep financial accounting, valuation, thesis, and adversarial review independently testable.
