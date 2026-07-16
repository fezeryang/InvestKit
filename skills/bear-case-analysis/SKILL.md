---
name: bear-case-analysis
description: Red-team a frozen investment thesis with an independent counter-thesis, disconfirming evidence, fragile assumptions, adverse causal mechanisms, observable failure signals, and two-sided falsifiers. Use when the user asks for a bear case, counter-thesis, adversarial thesis review, downside mechanism, or thesis killers. Do not use for generic risk-list extraction, DCF sensitivity, source auditing, report assembly, or a short/sell recommendation.
---

# Bear-Case Analysis

Version: 0.2.0

## Objective

Construct the strongest evidence-linked counter-case independently of the base thesis and define what would falsify both the original thesis and the bear case.

## Responsibility Boundary

Own the counter-thesis, fragile-assumption attacks, independent counterevidence, adverse mechanisms, earliest failure signals, severity/likelihood estimates, and bear-case killers. Do not rewrite the thesis, repeat its risk list, calculate a new target, audit all sources, or recommend an action.

## Positive Triggers

- “Red-team this frozen thesis and build the strongest independent bear case.”
- “Challenge the key assumptions with counterevidence, adverse causal paths, and thesis killers.”

## Near-Miss Negative Triggers

- “Extract the risk-factor headings from this filing.”
- “Run a DCF sensitivity table for WACC and terminal growth.”

## Inputs

Require a resolved security, as-of date, frozen thesis artifact and checksum, upstream structured results, source register, and risk/unknown records. Accept optional historical stress evidence and dated events when their source IDs resolve.

### Missing-Data Behavior

Record an explicit evidence-search gap when no independent counterevidence is available. Return `insufficient_evidence` in `method` rather than inventing adverse facts. Use `skipped` only when the thesis or every usable underlying artifact is absent; do not treat missing evidence as proof that the thesis is safe.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`
- `specs/financial-data-policy.md`
- `specs/valuation-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Validate identity, scope, as-of date, frozen thesis checksum, upstream statuses, and source IDs.
2. Isolate the thesis statement, pillars, assumptions, confirming evidence, unknowns, and falsifiers without editing them.
3. State the strongest neutral counter-thesis before assigning severity or likelihood.
4. Identify at least three fragile material assumptions and explain the dependency each creates.
5. Seek disconfirming evidence, conflicts, weak-source dependencies, and evidence not used as thesis confirmation.
6. Build adverse causal chains across applicable business, competitive, accounting, financial, valuation, management, event/regulatory, and data/model categories.
7. Define the earliest observable failure signals with condition, time window, and expected source.
8. Label severity and likelihood as estimates with rationale and material input IDs; avoid pseudo-precision.
9. Define evidence that would disprove the bear case, then preserve unresolved questions, risks, and warnings.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` envelope with distinct `facts`, `assumptions`, `estimates`, `unknowns`, `findings`, `risks`, `warnings`, and `source_ids`. Put the counter-thesis, fragile assumptions, counterevidence, mechanisms, failure signals, two-sided falsifiers, and input checksum in `method` per [the bear-case method contract](references/method-contract.md).

## Source Requirements

Counterevidence must resolve to persisted fact/source IDs with its source-quality and freshness decisions; conflicts, stale evidence, and low-quality evidence remain labeled. Independence requires at least one counterevidence source or upstream fact not used as thesis-confirming evidence, unless the result records `insufficient_evidence` and the exact gap.

## Risk and Non-Advice Boundaries

Disclose the intentionally adversarial method and keep severity/likelihood conditional. No brokerage connection, order placement, real-money action, short/sell instruction, position sizing, stop loss, deterministic downside target, replacement security, or return promise is permitted.

## Non-Applicable Cases

Do not use without a frozen thesis, for generic filing risk extraction, standalone valuation sensitivity, a source-only audit, or a portfolio decision. A difficult adverse case is not grounds to skip.

## Composition

Consume the frozen `investment-thesis` artifact and underlying evidence without mutating either. Emit an independent counter-case to `catalyst-analysis`, `source-verification`, and `investment-report`, preserving all upstream IDs and gaps.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test independent counterevidence, fragile assumptions, adverse causal chains, earliest failure signals, bear-case falsifiers, missing evidence, frozen-thesis integrity, and rejection of trading language.
