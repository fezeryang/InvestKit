# Financial Statement Method Contract

Version: 1.0

## Normalized Fact

Record `id`, original and canonical labels, value, currency, scale, period start/end, fiscal type, accounting and consolidation bases, source IDs, and mapping confidence.

## Derived Estimate

Record formula ID/expression, input fact IDs, output unit, period alignment, denominator guard, applicability, and warnings.

## Mandatory Checks

- Compare like-for-like periods only.
- Preserve original and restated series.
- Skip calculations with missing, incompatible, negative, or near-zero denominators when the formula is unstable.
- Reconcile retained earnings through distributions and other equity movements, not a naive equality.

## Handoff

Output normalized statements, trends, calculations, anomalies, and missing fields. Do not assign a quality score or investment verdict.
