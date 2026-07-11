---
name: gf_fund_detail
description: Query Guangfa Securities fund detail information using the GF_SKILLS_APIKEY environment variable.
---

# Guangfa Securities Fund Detail

Use this skill when the user asks for a fund's NAV, returns, risk level, subscription or redemption rules, manager, company, or fund evaluation.

## Security

- Read the API key from `GF_SKILLS_APIKEY`.
- Never print, store, or commit the API key.
- Query one fund at a time for detailed fund profiles.

## Endpoint

POST `https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`

Payload:

```json
{
  "service_name": "jijin_info",
  "tool_name": "finance-api_product_fund_detail_get",
  "args": {
    "tradeCode": "519002"
  }
}
```

## Inputs

- `tradeCode` string, required, fund trade code such as `519002`.

## Important Fields

- `tradeCode`, `chiName`, `secuAbbr`, `fundType`, `riskLevel`.
- `shareNav`, `return1w`, `return1m`, `return3m`, `return6m`, `return1y`, `return3y`, `returnTn`.
- `assetScale`, `fundManageCorp`, `contractEffDate`, `prodStatus`.
- `isAllowBuy`, `isAllowRedeem`, `min_share`, `min_share2`.
- `extraInfo.investTarget`, `extraInfo.riskReturnFeature`, `report`.
