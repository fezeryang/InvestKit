---
name: gf_stock_valuation
description: Compare Guangfa Securities stock market cap, valuation, and financial indicators using the GF_SKILLS_APIKEY environment variable.
---

# Guangfa Securities Stock Valuation And Financial Comparison

Use this skill when the user asks to compare A-share valuation levels, market cap, PE/PB, industry averages, historical percentiles, profitability, capital structure, cash flow, or growth.

## Security

- Read the API key from `GF_SKILLS_APIKEY`.
- Never print, store, or commit the API key.
- Keep comparison lists short to avoid oversized responses.

## Endpoint

POST `https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`

## Tool 1: Market Cap And Valuation

```json
{
  "service_name": "quant",
  "tool_name": "common_basic_post",
  "args": {
    "stock_codes": ["SZ000776", "SZ000001"]
  }
}
```

Inputs:
- `stock_codes` array of uppercase exchange-prefixed codes such as `SZ000776` or `SH600000`.

Important fields:
- `basic.total_marketcap`: total market cap in 100 million CNY.
- `valuation.pettm`, `valuation.pettm_avg`, `valuation.pettm_percent`.
- `valuation.pb`, `valuation.pb_avg`, `valuation.pb_percent`.

## Tool 2: Financial Indicator Comparison

```json
{
  "service_name": "quant",
  "tool_name": "compare_indicator_post",
  "args": {
    "report_type": 9,
    "stock_codes": ["SZ000783", "SZ000776"],
    "year": "2025"
  }
}
```

Inputs:
- `report_type` integer: `1`, `6`, `9`, or `12`.
- `stock_codes` array of uppercase exchange-prefixed codes.
- `year` string such as `2025`.

Important fields include `roe`, `net_profit2totalincome`, `cashflow_oper2income`, `net_cashflow_oper2net_profit`, `equity2asset`, `liablity2asset`, `liab2equity`, `operate_income_yoy`, `net_profit_yoy`, and `total_asset_yoy`.
