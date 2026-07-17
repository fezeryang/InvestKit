# CICCWM wrapper review

## Acquisition

The six user-authorized ZIP files were downloaded into
`third_party/raw/user-authorized-20260717/ciccwm/` and were not executed or
installed. They are untrusted review material.

## Decisions

| Package | Decision | Evidence / next action |
|---|---|---|
| market-analysis | unsafe | Imports `subprocess` and falls back to curl; requires a clean-room adapter. |
| stock-finance-analysis | adapt | Read-only data endpoint is identifiable, but source contains API-key action reporting. Strip telemetry before adaptation. |
| hot-news-analysis | adapt | Read-only news endpoint is identifiable; remove action reporting and fixed local config paths. |
| etf-ranking-analysis | adapt | Read-only ETF endpoint is identifiable; remove action reporting and enforce bounded parsing. |
| tiger-list-analysis | adapt | Read-only research endpoint is identifiable; remove action reporting and enforce bounded parsing. |
| fund-product-info | adapt | Read-only fund endpoint is identifiable; remove action reporting and enforce bounded parsing. |

## Shared risks

- API key variable is `CICCWM_API_KEY`; source scripts read a local OpenClaw
  configuration file and place the key into a Cookie header.
- Multiple scripts call a separate `webreport.ciccwm.com` endpoint and include
  the key as `login_id`. This is telemetry/credential disclosure outside the
  requested research operation and will not be carried into InvestKit.
- The original scripts use unbounded urllib responses, fixed local paths, and
  third-party implementation assumptions. They remain in raw quarantine only.

## Integration gate

The integration gate is complete for the clean-room client at
`src/investkit/providers/ciccwm.py`. It has offline contracts for all six
commands, credential gating, exact-host allowlisting, redirect refusal, strict
JSON, response bounds, and absence of telemetry. The raw archives remain blocked
and are never imported or executed.

Catalog decision for each of CICCWM-001 through CICCWM-006 is `adapt`. The
first-party adapter is approved for read-only, explicit-permission execution;
vendor code is not licensed or promoted. Vendor data terms still apply.

On 2026-07-17 the first live verification attempt stopped before network I/O
because the configured `CICCWM_API_KEY` contained a non-ASCII full-width colon.
After correcting the local configuration, live read-only verification returned
`ret=0` for market, finance, hot news, ETF ranking, Dragon-Tiger list, fund
search, and fund detail. Fund lookup correctly resolves a public six-digit fund
code to the vendor's internal product ID before requesting details. No credential
value was logged or stored by the project.
