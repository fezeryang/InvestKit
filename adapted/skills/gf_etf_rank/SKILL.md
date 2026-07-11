---
name: gf_etf_rank
description: Query Guangfa Securities ETF ranking lists using the GF_SKILLS_APIKEY environment variable.
---

# Guangfa Securities ETF Rankings

Use this skill when the user asks for ETF gainers, losers, turnover, main capital flow, net subscriptions, or premium rankings.

## Security

- Read the API key from `GF_SKILLS_APIKEY`.
- Never print, store, or commit the API key.
- Use `size` and `page` to limit response volume.

## Endpoint

POST `https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`

Payload:

```json
{
  "service_name": "etf_rank",
  "tool_name": "finance-api_product_etf_rank_get",
  "args": {
    "type": 1,
    "size": 20
  }
}
```

## Inputs

- `type` integer, required: `1` gainers, `2` losers, `3` turnover, `4` main capital, `12` net subscription, `13` premium.
- `page` integer, optional, zero-based.
- `size` integer, optional.
- `sameIndexFilter` integer, optional, `1` on or `0` off.
- `continueRiseLimit` integer, optional.

## Important Fields

- `code`, `name`, `ext_name`.
- `exchange`: `101` Shanghai, `105` Shenzhen.
- `roc`, `fiveRoc`, `volume`, `cashFlow`, `turnover_rate`.
- `fundSize`, `trackIndexName`, `continueRiseDay`, `premium`.
