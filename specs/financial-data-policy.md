# Financial Data Policy

Spec version: 1.0.0

## Normalization requirements

Financial data must retain period end, period type, accounting basis when known,
currency, units, source, as-of date, and warnings. Income statement, balance
sheet, and cash-flow fields must not be mixed without explicit definitions.

## Calculation rules

- Keep reported values separate from derived ratios and analyst adjustments.
- Use consistent periods for trend comparisons and disclose when comparability is
  uncertain.
- Treat `null` as unavailable, never as zero.
- State sign conventions for cash outflows such as capital expenditure.
- Reconcile earnings and operating cash flow before commenting on earnings
  quality.
- Identify exceptional, restated, or definitionally ambiguous items as unknowns.
- Preserve full precision in stored calculations; round only for presentation.

## Demo limitation

The bundled statements describe a fictional company and exist solely to test the
offline Harness. They are not live financial statements and cannot support a real
investment decision or trading instruction.
