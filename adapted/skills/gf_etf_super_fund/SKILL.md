---
name: gf_etf_super_fund
description: Query Guangfa Securities ETF super-fund abnormal flow lists using the GF_SKILLS_APIKEY environment variable.
---

# Guangfa Securities ETF Super Fund Flow

Use this skill when the user asks which ETFs have large inflows, large outflows, sustained inflows, or sustained outflows.

## Security

- Read the API key from `GF_SKILLS_APIKEY`.
- Never print, store, or commit the API key.
- Query one abnormal-flow type at a time.

## Endpoint

POST `https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`

Payload:

```json
{
  "service_name": "etf-super-fund",
  "tool_name": "gfmiddle_eits_super_fund_etf_superfund_get",
  "args": {
    "type": "大幅流入"
  }
}
```

## Inputs

- `type` string, required: `大幅流入`, `大幅流出`, `持续流入`, or `持续流出`.

## Important Fields

- `etfcode`, `etfname`, `mktCd`, `tradeDate`.
- `fndNet`: daily net fund flow in 10,000 CNY.
- `fndNetPercent`: fund intensity percent.
- `estimatedFundingCost`, `capitalProfitMargin`.
- `details[].tradeDate`, `details[].fndNetIn`.
