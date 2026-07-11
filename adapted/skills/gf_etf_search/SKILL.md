---
name: gf_etf_search
description: Screen Guangfa Securities ETF lists by return, drawdown, Sharpe, valuation, scale, theme, and trading attributes using GF_SKILLS_APIKEY.
---

# Guangfa Securities ETF Multi-Factor Search

Use this skill when the user asks to find ETF candidates by theme, performance, risk, valuation temperature, size, T+0, margin eligibility, or sorting rules.

## Security

- Read the API key from `GF_SKILLS_APIKEY`.
- Never print, store, or commit the API key.
- Prefer 2 to 4 key filters and a bounded `limit`.

## Endpoint

POST `https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`

Payload:

```json
{
  "service_name": "etf_search",
  "tool_name": "finance_api_inclusive_etf_list_get",
  "args": {
    "trakType": "行业",
    "roc1m": "5~",
    "sort": "-roc1m",
    "limit": 20,
    "addRealTimeRoc": 1
  }
}
```

## Common Inputs

- `search`: fuzzy code or name.
- `type`: ETF type, for example `股票ETF` or `境外ETF`.
- `trakType`, `oneTrakName`: track category and primary theme.
- `tradeCode`: comma-separated trade codes.
- `tradeT0`, `marginTrade`: `1` for yes.
- `roc1w`, `roc1m`, `roc6m`, `roc1y`: interval percent-change filters.
- `return1m`, `return6m`, `return1y`, `return3y`: return filters.
- `maxDrawdown1m`, `maxDrawdown1y`: drawdown filters.
- `sharpRatio1y`, `sharpRatio3y`: Sharpe filters.
- `valuationResult`: `1` low, `2` middle, `3` high.
- `indexTempType`: `low`, `ord`, or `high`.
- `assetScale`, `start`, `limit`, `sort`.

## Important Fields

- `tradeCode`, `secuAbbr`, `extName`, `exchangeCode`.
- `fiInfoName`, `fiInfoCode`, `fundSize`, `assetScale`.
- `pe`, `pePercent`, `pb`, `pbPercent`.
- `roc`, `roc1w`, `roc1m`, `roc6m`, `roc1y`.
- `netMainForce1d`, `netMainForce5d`, `premium`.
- `indexTempType`, `trakName`, `trakType`.
