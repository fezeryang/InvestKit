# Investment Core Acceptance Matrix

## Release Assets

| Contract | Proof |
|---|---|
| Exactly 12 Investment Core Skills plus `security-identification` prerequisite | Asset catalog assertion; fresh init manifest and target directory set |
| Every Core Skill has valid frontmatter, trigger/near-miss guidance, inputs, specs, ordered method, output/source/risk/composition contracts, and Evals | Static contract parser plus `quick_validate.py` for all 12 |
| Every Core Skill has a synthesis report | Exact report-name set under `reports/capabilities/`; required evidence/adopt/modify/reject/license sections |
| References resolve and are installed as governed delivery files | Source traversal test, manifest mapping/hash test, missing-reference failure test |
| No legacy low-quality Skill remains in fresh v0.2 install | Fresh target exact-set assertion; canonical release catalog excludes superseded names |

## Trigger And Method Evals

| Contract | Proof |
|---|---|
| Correct positive trigger | At least two realistic positive questions per Core Skill |
| Difficult negative/near-miss trigger | At least two finance-adjacent exclusions per Core Skill |
| Missing required inputs | Unit Eval records unknown/skip/failure without fabricated data |
| Analytical method is substantive | Capability-specific numeric/structural assertions, not file-existence checks |
| Facts, assumptions, estimates, and unknowns separate | Result-schema validator plus negative mutation tests |
| Fact sources resolve | Claim/source-ID join assertion and corrupt-source negative test |
| Risk and non-advice boundaries | Bear-case/risk fields required; report forbidden-language scan |

## Capability-Specific Assertions

| Capability | Minimum behavioral assertions |
|---|---|
| Company Deep Research | identity, company/segment facts, management/capital allocation, competitive context, explicit gaps |
| Business Model | customer/value proposition/revenue model/unit economics/moat/fragility; no valuation work |
| Financial Statements | multi-period statements, margins/growth, cash flow, leverage/liquidity, definitions/periods |
| Earnings Quality | accrual/cash conversion, working capital, one-offs/asset quality, missing-data warnings |
| Valuation | base/bull/bear DCF, WACC > terminal growth, EV-equity bridge, odd sensitivity grid centered on base |
| Comps | explicit peer selection/exclusion, metric comparability, invalid-denominator handling, median/implied range |
| Earnings | actual vs expectation, surprise, guidance change, drivers, missing transcript treated as unknown |
| Investment Thesis | bull/base synthesis, pillars, evidence, assumptions, KPIs, falsifiers, monitoring |
| Bear Case | independent disconfirming evidence, downside mechanisms, thesis killers, not copied bull prose |
| Catalysts | dated/windowed event, evidence, likelihood/uncertainty, materiality, dependency and downside path |
| Source Verification | source quality/date/freshness, claim coverage, conflicts, unresolved claims |
| Investment Report | composed only from result artifacts, balanced evidence, sources/assumptions/risks/unknowns, demo/non-advice disclosure |

## Workflow And Persistence

| Contract | Proof |
|---|---|
| Exact 13-step `company-deep-dive` order | Workflow asset and persisted plan assertion |
| One structured result per completed/skipped step | Exact `capabilities/*.json` set and schema validation |
| Missing data/skip propagates | Fixture variant with absent peers or earnings fields; downstream unknown/warning assertions |
| Bear case and source verification are mandatory | Workflow mutation/doctor negative tests |
| Task lifecycle survives failure | Controlled Provider failure retains task/plan/log and completed artifacts |
| Resume skips verified steps | Failed-run recovery and `resume-skipped` events |
| Completed resume is immutable | Byte hashes for data, capability results, findings, sources, assumptions, risks, report; only run log changes |
| Corruption and symlink escapes fail safely | Missing/corrupt capability, mismatched source ID, external symlink tests |

## Harness Regression

| Contract | Proof |
|---|---|
| Empty init and repeat init work | Existing init tests updated for nested Skill delivery |
| User files are not overwritten | Conflicting `SKILL.md` and nested reference tests |
| Doctor distinguishes PASS/WARN/FAIL | Healthy, unmanaged user Skill, and each critical mutation |
| Config/manifest remain machine-readable and secret-free | Schema/field assertions and redacted secret scan |
| Offline and dependency-free | Socket/URL entry points patched to fail; empty Runtime dependencies; no subprocess/network imports |
| No third-party install or execution | Forbidden source-root/mapping tests and installed exact-set assertion |
| `.trellis/` is not a Runtime dependency | source/import/static artifact scan plus wheel-only run |
| Wheel acceptance | Fresh isolated `init → doctor → demo → resume → doctor` |
| Quality floor | all tests green, no skips, Pyright green, compile/build green, statement coverage >=80%, `git diff --check` green |

## Product Documentation

| Contract | Proof |
|---|---|
| Capability map contains every requested category/item/status | Exact item/status parser test or documented audit |
| Roadmap makes Investment Core Pack the next stage | No standalone Provider milestone before Core/Advanced/Quant/Portfolio packs |
| Provider is subordinate infrastructure | PRD/architecture/roadmap consistency scan |
| README gives fresh v0.2 offline flow | Wheel acceptance commands match README |
| No later pack starts | No implementation/catalog claims for Advanced, Quant, Portfolio & Risk, or live Provider expansion |
