---
name: gf_lhb_list
description: Query Guangfa Securities Dragon-Tiger list stocks for one trading date and market using the GF_SKILLS_APIKEY environment variable.
---

# Guangfa Securities Dragon-Tiger List

Use this skill when the user asks for A-share Dragon-Tiger list abnormal trading stocks by date and market.

## Security

- Read the API key from `GF_SKILLS_APIKEY`.
- Never print, store, or commit the API key.
- Query one trading date at a time unless the user explicitly asks for a broader batch.

## Endpoint

POST `https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`

Headers:
- `Content-Type: application/json`
- `Authorization: Bearer ${GF_SKILLS_APIKEY}`

Payload:

```json
{
  "service_name": "lhb",
  "tool_name": "lhb_aborttrade_market_date_get",
  "args": {
    "date": 20260313,
    "market": "sh"
  }
}
```

## Inputs

- `date` integer, required, `YYYYMMDD`.
- `market` string, required, `sh` for Shanghai or `sz` for Shenzhen.

## Important Fields

- `trdCode`: trading code.
- `secuSht`: security short name.
- `clsPrc`: close price.
- `dayChgRat`: daily percent change.
- `tnvVol` / `tnvVal`: volume / turnover.
- `items[].rsnSht`: listing reason.
- `items[].rsnCode`: listing reason code.
- `items[].beginDate` / `items[].endDate`: statistics window.

If data is empty, check that the date is a trading day and `market` is `sh` or `sz`.
