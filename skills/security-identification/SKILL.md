---
name: security-identification
description: Resolve a company, ticker, exchange code, or demo alias to one stable security identity before research. Use when the subject or listing is ambiguous or downstream work needs canonical identifiers. Do not use for valuation, company analysis, source auditing, or transaction requests after identity is already resolved.
---

# Security Identification

Version: 0.2.0

## Objective

Establish exactly one research subject, or preserve ambiguity explicitly, before any company claim or calculation is made.

## Responsibility Boundary

Own entity/listing resolution, legal name, ticker, market, exchange, security identifier, demo status, and ambiguity records. Do not perform company research, financial analysis, valuation, or trade routing.

## Positive Triggers

- “Resolve ALW and confirm which fictional listing the research should use.”
- “Identify the security from this company name, ticker, and exchange hint.”

## Near-Miss Negative Triggers

- “Calculate a three-scenario DCF for the already resolved security.”
- “Audit whether every claim in this completed report has a valid source.”

## Inputs

Require the user query and a bounded first-party Provider identity response. Accept optional market, exchange, currency, listing type, and prior identifier hints.

### Missing-Data Behavior

Return `skipped` with the missing identity inputs when no candidate is available. Return `failed` or an explicit ambiguity result when multiple candidates cannot be disambiguated. Never select a match from model memory.

## Used Specs

- `specs/research-principles.md`
- `specs/evidence-policy.md`
- `specs/source-policy.md`

## Analytical Procedure

1. Normalize the supplied name, ticker, exchange, and market hints without changing their meaning.
2. Inspect only the bounded Provider response and retain its source, date, fixture version, warnings, and demo marker.
3. Match legal entity and listing attributes; keep issuer identity distinct from security identity.
4. Reject unresolved collisions and record which additional field would disambiguate them.
5. Emit one stable canonical record and provenance when the match is unique.

## Output Contract

Use the shared capability envelope with `completed`, `skipped`, or `failed` status and separate `facts`, `assumptions`, `estimates`, `unknowns`, `risks`, and `warnings`. The method payload follows [the identity method contract](references/method-contract.md).

## Source Requirements

Every identity fact must reference a persisted Provider source ID. Preserve market, exchange, as-of date, fixture version, and `is_demo`; never map a fictional alias to a real security. Record source quality, prefer authoritative issuer/exchange/regulatory evidence, and test freshness against the requested research date. Stale or secondary-only identity evidence cannot silently resolve a material ambiguity.

## Risk and Non-Advice Boundaries

Stop on unresolved identity. No brokerage connection, order placement, real-money action, investment recommendation, price forecast, or return promise is permitted.

## Non-Applicable Cases

Do not use for a macro topic with no security, an unidentified basket that intentionally remains a basket, or any request to place a transaction.

## Composition

Emit the canonical security record consumed by every Investment Core Skill. Downstream capabilities must reject a missing or ambiguous identity rather than repairing it silently.

## Evals

Run the positive and difficult near-miss cases in [trigger Evals](references/trigger-evals.json). Verify ambiguity preservation, fictional labeling, stable IDs, and zero analytical claims beyond identity.
