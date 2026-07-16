# Investment Thesis Method Contract

Version: 1.0

## Frozen Inputs

Record every upstream capability ID, status, artifact checksum, referenced fact/estimate/assumption/unknown ID, and unresolved warning. Never mutate an upstream result.

## Required Method Records

- Thesis: statement, time horizon, conclusion status, supporting IDs, and limiting unknown IDs.
- Cases: `bull`, `base`, and `bear_seed`, each with mechanism and evidence/input IDs.
- Pillars: ID, mechanism, confirming and disconfirming evidence IDs, assumptions, unknowns, KPI, review timing, and status.
- Falsifiers: observable metric/event, threshold or condition, expected source, and review window.
- Variant perception: sourced claim or explicitly material assumption.

## Completion Guards

Require at least one base-case pillar, explicit disconfirming evidence or a documented search gap for every pillar, and at least one observable falsifier. Missing material evidence yields `insufficient_evidence`; it never becomes a neutral score. Exclude ratings and trade actions.
