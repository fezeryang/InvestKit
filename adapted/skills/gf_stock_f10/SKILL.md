---
name: gf_stock_f10
description: Query Guangfa Securities stock F10 basic company information using the GF_SKILLS_APIKEY environment variable.
---

# Guangfa Securities Stock F10 Basic Information

Use this skill when the user asks for basic listed-company facts such as full company name, board, listing date, business scope, or industry.

## Security

- Read the API key from `GF_SKILLS_APIKEY`.
- Never print, store, or commit the API key.
- Query one stock at a time unless the user requests a controlled batch.

## Endpoint

POST `https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`

Payload:

```json
{
  "service_name": "wechat_f10",
  "tool_name": "f10_basic_post",
  "args": {
    "code": "000776",
    "market": "SZ"
  }
}
```

## Inputs

- `code` string, required, numeric security code such as `000776`.
- `market` string, required, `SH` or `SZ`.

## Important Fields

- `compName`: company full name.
- `boardName`: board.
- `listDate`: listing date.
- `businessScope`: business scope.
- `industries`: industries.

If data is empty, check the code format, market casing, and code-market match.
