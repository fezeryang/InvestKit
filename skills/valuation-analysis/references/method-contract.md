# Valuation Method Contract

Version: 1.0

## DCF Scenario

Record named drivers, forecast periods, UFCF, WACC components, terminal growth, terminal value, present values, enterprise value, EV-to-equity bridge, diluted shares, per-share output, input IDs, and warnings for each of bear, base, and bull.

## Mandatory Guards

- Require `WACC > terminal growth` in every scenario and sensitivity cell.
- Require positive diluted shares for per-share output.
- Weight gross interest-bearing debt in WACC; apply net debt only in the equity bridge.
- Use an odd grid and reproduce base value exactly at its center.
- Keep an exit-multiple terminal value as a separate cross-check.

## Reconciliation

Record DCF, comparable-company, and historical ranges independently, their definition differences, disagreement, and limitations. Do not apply a fixed blend or automatic premium.
