# Evidence Policy

Spec version: 1.0.0

## Claim classes

Every material claim must be traceable to one of these classes:

- **Fact:** directly supported by a cited source or normalized dataset.
- **Assumption:** chosen by the analyst or workflow and recorded with rationale.
- **Estimate:** derived from stated inputs and a reproducible method.
- **Model output:** produced by a named calculation and sensitive to its inputs.
- **Unknown:** unavailable, ambiguous, stale, or not verified.

## Minimum evidence record

An evidence record includes a stable source identifier, source title, as-of date,
retrieval or fixture version, market, currency when applicable, and the task
artifact that uses it. Conflicting sources remain visible and are not silently
reconciled.

## Quality rules

- A conclusion must not be stronger than its evidence.
- Company assertions are attributed to the company rather than treated as
  independently verified facts.
- Missing, stale, or definitionally inconsistent fields create warnings.
- Derived metrics identify their numerator, denominator, period, and units.
- Unsupported material claims are moved to unknowns or removed from the report.

Demo fixture records are valid only for exercising the offline workflow. They are
fictional evidence and must never be described as live or real-world observations.
