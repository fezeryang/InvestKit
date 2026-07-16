---
name: catalyst-analysis
description: Build a sourced, monitorable event ledger that separates timing confidence, probability, materiality, dependencies, impact mechanisms, downside paths, and post-event outcomes. Use when the user asks for catalyst analysis, a catalyst calendar, a regulatory or product event, or dated events that may change named thesis variables. Do not use for generic news summaries, undated risk lists, portfolio alerts, pre-positioning, or trade recommendations.
---

# Catalyst Analysis

Version: 0.2.0

## Objective

Translate evidence-backed events into monitorable change mechanisms without treating headlines, event probability, or expected direction as facts.

## Responsibility Boundary

Own stable event IDs, date/window and status history, evidence, uncertainty, materiality, dependencies, impact/downside paths, confirm/refute tests, and post-event outcomes. Do not summarize all news, restate the thesis, automate alerts/calendars, inspect positions, or recommend pre-positioning.

## Positive Triggers

- “Assess the regulatory decision as a catalyst with timing, evidence, dependency, and downside path.”
- “Create a catalyst calendar tied to revenue, margin, cash-flow, valuation, and thesis variables.”

## Near-Miss Negative Triggers

- “Summarize this week’s company headlines with no event-impact mechanism.”
- “List the company’s general long-term risks from the filing.”

## Inputs

Require a resolved security, research as-of time, event claim, dated source IDs, and named affected variable. Accept thesis sensitivities, earnings context, prior event observations, bounded date windows, and post-event evidence.

### Missing-Data Behavior

Preserve an uncertain date as a bounded window with timing confidence when evidence supports it. A rumor remains unconfirmed and high uncertainty. Use `skipped` with `skip_reason` and `missing_inputs` when there is no dated/windowed evidence-backed event; never invent a date, probability, or impact.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`
- `specs/financial-data-policy.md`
- `specs/risk-policy.md`

## Analytical Procedure

1. Validate security, as-of time, source IDs, event evidence, and the named affected variable.
2. Reject or demote generic news that lacks an identifiable causal impact hypothesis.
3. Assign a stable event ID, event type, claim, and append-only observation history.
4. Record expected date or bounded window, timezone, timing confidence, and `expected`, `confirmed`, `occurred`, `delayed`, `cancelled`, or `unknown` status.
5. Separate evidence-backed event facts from directional hypotheses and probability estimates.
6. Estimate uncertainty/probability with rationale independently from materiality.
7. Map materiality to named revenue, margin, cash-flow, balance-sheet, valuation, or thesis variables.
8. Record impact horizon, prerequisites, dependencies, second-order effects, and downside/failure path.
9. Define confirm/refute observations and the next re-check time.
10. Append date/status changes without overwriting history; after occurrence, record actual outcome separately from the original expectation.

## Output Contract

Return the shared `completed`, `skipped`, or `failed` envelope with distinct `facts`, `assumptions`, `estimates`, `unknowns`, `findings`, `risks`, `warnings`, and `source_ids`. Put the event ledger and observation history in `method` according to [the catalyst method contract](references/method-contract.md).

## Source Requirements

Event existence, date/window, and status require persisted source IDs and last-verification time. Label source quality and conflicts, and evaluate freshness against the event window and research as-of time; stale event evidence requires re-verification or an explicit warning. Direction, likelihood, and impact remain assumptions or estimates unless separately evidenced; a single weak rumor cannot become fact.

## Risk and Non-Advice Boundaries

Keep probability, timing confidence, and materiality separate and disclose adverse paths. No brokerage connection, order placement, real-money action, position inspection, alert automation, pre-positioning, trade instruction, target return, or deterministic price claim is permitted.

## Non-Applicable Cases

Do not use for generic headlines, undated structural risks, technical alerts, portfolio monitoring, or an event with no named impact variable. Do not skip merely because timing is uncertain when a defensible window exists.

## Composition

Consume earnings, thesis, bear-case, and valuation sensitivities by reference. Emit a monitorable event ledger to `source-verification` and `investment-report` without changing the thesis or creating portfolio action.

## Evals

Use [trigger Evals](references/trigger-evals.json). Test dated and windowed events, weak rumors, shifted dates, independent materiality/probability, dependency failure, generic news, missing events, and separate actual-versus-expected outcomes.
