# Earnings Quality Analysis Capability Synthesis

Research date: 2026-07-16

Task: InvestKit v0.2 — Investment Core Pack

Decision: independently implement an evidence-and-accounting-led first-party Skill; reject candidate scoring and trading blocks.

## Outcome

Earnings quality is a separate judgment layer over normalized multi-period statements, accounting policies, and footnotes.

It asks whether reported earnings are cash-backed, repeatable, and supported by defensible accounting, while preserving plausible alternative explanations and unknown evidence.

Vibe-Trading contributes diagnostic families, InvestSkill contributes filing and policy coverage, Octagon contributes detailed cash-flow and footnote questions, and China-stock contributes provenance plus causal risk paths.

No candidate provides calibrated fraud inference, safe missing-data behavior, or InvestKit's typed evidence/output contract.

## Responsibility Boundary

This capability owns:

- operating-cash-flow versus earnings, accruals, free-cash-flow conversion, and working-capital bridges;
- revenue-recognition policy, contract assets/liabilities, receivable/inventory behavior, returns, allowances, and concentration;
- recurring versus one-off earnings, non-GAAP reconciliation, and acquisition effects;
- capitalization/expense choices, reserves, impairments, goodwill/intangibles, leases, pensions, contingencies, and related parties;
- audit opinion, auditor changes, restatements, controls, policy changes, and critical estimates;
- supported positives, concerns, alternative explanations, follow-up evidence, confidence, and risk transmission.

It does not own:

- basic statement normalization or a general financial recap;
- actual-versus-consensus beat/miss, guidance, transcript, or market reaction;
- valuation, catalyst calendar, thesis verdict, report assembly, or trade action;
- a numerical fraud probability or claim that a red flag proves manipulation.

It requires normalized statement results and available filing/policy/footnote evidence.

Its handoff is a quality scorecard expressed as evidence-backed positives, concerns, unknowns, and causal risk paths, not one opaque score.

## Search And Evidence Rules

All 36 registered candidates were searched without expanding intake.

All 14 commit-pinned repository trees were searched; only the named selected files are treated as method evidence.

Grade A means commit/hash-pinned evidence and an identifiable root license, not blanket reuse approval.

Grade B means hash-pinned local evidence with incomplete license or provenance.

Grade C means registry/draft evidence only.

## Exact Design-Changing Evidence

| Candidate | Exact source state | Files actually read | Design-changing evidence |
|---|---|---|---|
| BATCH-001-014 Vibe-Trading | commit 531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722; snapshot SHA-256 8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872; MIT root; grade A | agent/src/skills/financial-statement/SKILL.md | accrual/cash conversion, receivable/inventory, non-recurring items, auditor, capitalization, goodwill, and return-decomposition questions |
| BATCH-001-007 InvestSkill | commit 6449af2d0fc410a6c541c5815c601ba9f649d791; snapshot SHA-256 758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5; MIT root; grade A | plugins/us-stock-analysis/skills/financial-report-analyst/SKILL.md | revenue recognition, non-GAAP, working capital, FCF, stock compensation, footnotes, related parties, estimates, auditors, restatements, and controls |
| BATCH-001-005 OctagonAI | commit 51e938c4d086f658de8bdcf734e864d34637167e; snapshot SHA-256 d75c5acb6d9227232db8fa3859be61b97bea405b1f0f72143288f3f85cddf95f; MIT root; grade A | skills/sec-cash-flow-review/SKILL.md, skills/sec-footnotes-analysis/SKILL.md, with skills/financial-health-scores/SKILL.md reviewed as rejected score evidence | working-capital components, cash sources, covenants, recognition policy, estimates, leases, contingencies, pensions, stock compensation, and policy-change comparison |
| BATCH-001-008 China-stock | commit d49f1f360deac57821d5d6b3aff664dff232acc6; snapshot SHA-256 4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2; MIT root; grade A | skills/financial-health/SKILL.md | filing linkage, audit status, fact/judgment separation, impairment, guarantee/refinancing unknowns, and explicit risk-transmission paths |

## Strengths, Weaknesses, And Disposition

| Candidate | Strengths | Weaknesses and risks | InvestKit disposition |
|---|---|---|---|
| Vibe-Trading | Broad, intuitive quality diagnostics and useful linkage to working capital and asset choices | Fixed cutoffs ignore sector, seasonality, loss periods, and scale; red-flag count is mislabeled as fraud probability | Adopt diagnostic families; reject cutoffs, composite counts, probabilities, and buy/avoid output |
| InvestSkill | Strong filing, recognition, adjustment, footnote, control, auditor, and multi-period coverage | Overstates that cash flow is hardest to manipulate; 5%/30%/80% thresholds and 21-point score are uncalibrated; contains a trading block | Adopt evidence checklist and change analysis; replace thresholds with contextual materiality and confidence |
| OctagonAI | Detailed cash and footnote categories; compares policies and exposes hidden obligations | Requires Octagon MCP; FCF/days formulas need exact definitions, average balances, and annualization; directional heuristics can fail | Adopt source questions and guarded calculations; independently implement without MCP |
| China-stock | Strong filing provenance, explicit unknowns, and causal stress paths | Mixes solvency with earnings quality; includes A-share overlays; provides no calibrated confidence method | Adopt evidence/risk-path structure; consume solvency facts without a composite quality verdict |

## Boundary And Supporting Evidence

BATCH-001-009 HHFin was read at commit 6e7ceef3c65287b7b88436fb4876f541b592a2ed, snapshot SHA-256 e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6, earnings-analysis/SKILL.md lines 1–360, MIT root evidence.

Its Parse/Compare cash-quality questions overlap partially, but consensus comparison, price context, scoring defaults, and position actions belong to earnings-analysis or are prohibited.

Missing expectations must not receive neutral defaults, and a quarterly beat is not proof of durable earnings quality.

BATCH-001-010 Longbridge, commit d68372ab584a77b3cb2a078a05c1322267729100 and snapshot SHA-256 79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e, supports average-assets accrual denominators and missing-statement degradation.

Its vendor CLI and network/update requirements are not adopted.

## Data/API-Only And Unavailable Evidence

CICCWM-002, archive SHA-256 97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208, provides statement and indicator fields but no defensible quality method.

Its license is unknown; scripts/finance_query.py reads a user-home credential and sends credential-bearing telemetry, so execution and integration are blocked.

EASTMONEY-001, archive commit 61cfae47451f797d95ae4553ffcc7569b9957e7d and SHA-256 24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15, can inform normalized statement retrieval and source metadata only.

GF-003, adapted/skills/gf_stock_valuation/SKILL.md, SHA-256 49421c138609516b44aa6680808143f786ade30eda532e21dc6ebbdb791a5588, names profitability, leverage, cash-flow, growth, year, and report-type fields.

GF-003 is grade C: authorization, license, API terms, units, definitions, restatement policy, schema, and fixture behavior are unknown.

GUOSEN-002 is zero-byte, SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; content and license are unavailable.

No Provider is required for the offline quality Eval, and none was implemented or called.

## Adopted, Modified, And Rejected Ideas

Adopted:

- multi-period cash-to-earnings and working-capital bridges;
- revenue-recognition, contract-balance, return/allowance, and concentration review;
- recurring/non-recurring and GAAP/non-GAAP reconciliation;
- capitalization, reserve, impairment, goodwill, obligation, and related-party review;
- auditor, restatement, control, and policy-change evidence;
- explicit alternative explanations and follow-up questions for every concern.

Modified:

- accrual, FCF, days, and conversion measures require definitions, average-balance rules, annualization policy, and valid denominators;
- materiality is contextual and source-backed rather than a universal percentage;
- each concern records evidence, counterevidence, alternative explanations, confidence, and downstream impact;
- negative earnings, seasonal builds, acquisitions, financial companies, and disclosed policy changes receive applicability guards;
- output is a transparent scorecard of records, not a single quality or fraud score.

Rejected:

- “cash is impossible or hardest to manipulate” as a certainty;
- red-flag counts as fraud probability or deterministic conclusion;
- silent neutral defaults, training-data fills, or industry-average imputation;
- provider-specific MCP/CLI/network execution;
- beat/miss, stock reaction, technical signal, buy/sell, position, or return language;
- treating one weak metric as proof of manipulation.

## Final InvestKit Method

1. Validate the normalized statement result, comparable periods, source IDs, audit state, and available filing/footnote coverage.
2. Record which required quality domains are present, absent, stale, or not applicable.
3. Analyze OCF-to-earnings, guarded accrual measures, defined FCF conversion, and the detailed working-capital bridge.
4. Test recognition policy and related balances, returns/allowances, concentration, and organic versus acquired growth.
5. Reconcile management adjustments and isolate asset sales, fair-value effects, tax items, restructuring, acquisition effects, and other non-recurring items.
6. Review capitalization, reserves, impairments, goodwill/intangibles, leases, pensions, contingencies, stock compensation, and related parties.
7. Review auditor opinion/change, restatements, controls, critical estimates, and accounting-policy changes.
8. Express each positive or concern with source-backed evidence, alternative explanations, required follow-up, confidence, and risk path.
9. Preserve missing footnotes or policies as unknowns and lower evidence confidence; never fill them.
10. Produce no fraud probability, trade action, or deterministic quality grade.

## Output Contract And Handoff Rationale

The capability envelope keeps facts, assumptions, estimates, unknowns, findings, risks, warnings, source_ids, method, status, and Skill version distinct.

Facts cite normalized statement or filing source IDs.

Estimates carry formulas, periods, inputs, denominator/annualization rules, and applicability.

Concerns contain evidence IDs, plausible alternative explanations, follow-up needs, confidence, and causal risk paths.

Unknowns identify missing policy, footnote, control, auditor, or period evidence and the blocked conclusion.

Investment-thesis consumes supported positives and concerns without treating either as certainty.

Bear-case-analysis consumes causal risk paths and unresolved accounting questions.

Earnings-analysis receives quality context but remains authoritative for event surprise, guidance, and expectations.

Source-verification can audit each quality finding back to persisted claim and source IDs.

## Security, License, And Honest Unknowns

MIT root texts allow further review but do not authorize wholesale copying of nested prompts or code.

File-level licensing and attribution must be separately confirmed before any reuse beyond paraphrased method ideas.

Octagon MCP and Longbridge tool instructions were treated as untrusted and not followed.

CICCWM's home-directory credential access and telemetry block integration; five sibling archives also weaken TLS.

Guangfa's official authorization, API terms, license, and redistribution rights remain unknown.

Guosen method content cannot be judged because it is unavailable.

## Non-Execution And Independent-Reimplementation Attestation

The candidate study and this report used static text plus existing local audits only.

No raw third-party Skill, script, installer, CLI, MCP, endpoint, dependency, or financial API was executed, imported, installed, sourced, or called.

No user-home credential was read and no TLS or certificate verification was weakened.

No raw content was copied into skills/, Runtime code, adapted assets, or host targets.

The method is newly written from multiple candidate ideas and InvestKit-owned evidence, safety, persistence, and handoff requirements; no prompt, code, scorecard, formula implementation, or output template was copied wholesale.

## Required Evals

1. Positive: profit rises while OCF falls as receivables and contract assets expand; trace the exact bridge.
2. Counterexample: documented seasonal inventory build remains a concern with an alternative explanation, not a fraud claim.
3. Near miss: consensus beat and guidance revision route to earnings-analysis.
4. Missing footnotes: complete a partial result with explicit policy unknowns and lower confidence.
5. Negative earnings: suppress meaningless cash-conversion percentages.
6. Acquisition year: separate acquired effects and avoid false organic-quality claims.
7. Non-GAAP: reconcile every adjustment and flag unsupported exclusions.
8. Revenue recognition: connect policy to contract balances and receivable behavior.
9. One-off gain: remove it from repeatability analysis but retain it as a reported fact.
10. Auditor/control event: cite the filing and avoid inferring fraud.
11. Alternative explanations: every material concern names at least one plausible counter-explanation or says none is supported.
12. Missing working-capital detail: do not fabricate the bridge.
13. Formula traceability: every estimate resolves to validated financial fact IDs.
14. Composition: thesis and bear-case receive quality records without an opaque score.
15. Safety: no fraud probability, buy/sell instruction, position action, or return promise appears.

## Final Rationale

Earnings-quality-analysis must be skeptical without becoming accusatory.

A transparent chain from normalized facts to diagnostics, alternatives, unknowns, and risk paths is more professional than thresholds or composite scores.

Keeping event surprise and trading language outside this capability preserves analytical and safety boundaries.
