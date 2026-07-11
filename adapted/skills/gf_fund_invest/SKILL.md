---
name: gf_fund_invest
description: Run Guangfa Securities historical fund investment plan simulations using the GF_SKILLS_APIKEY environment variable.
---

# Guangfa Securities Fund Investment Calculator

Use this skill when the user asks to simulate a fund fixed-investment plan across a historical interval, including ordinary investment, moving-average strategies, target take-profit, or trailing take-profit.

## Security

- Read the API key from `GF_SKILLS_APIKEY`.
- Never print, store, or commit the API key.
- Keep date ranges and frequency reasonable because detailed records can be large.

## Endpoint

POST `https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call`

Payload:

```json
{
  "service_name": "fund_invest",
  "tool_name": "finance_api_product_invest_compute_post",
  "args": {
    "tradeCode": "001643",
    "balance": 1000,
    "rate": "0",
    "startDate": "20200101",
    "endDate": "20250101",
    "enFundDate": "1",
    "strategyList": [
      {
        "prodAIRationType": "4",
        "prodIndexType": "0",
        "prodAverageType": "0",
        "expectIncomeRatio": "0.2"
      }
    ]
  }
}
```

## Inputs

- `tradeCode` string, required.
- `balance` number, required, per-period amount.
- `startDate`, `endDate` strings, required, `YYYYMMDD`.
- `rate` string, required: `0` monthly, `1` weekly, `2` daily, `3` biweekly.
- `enFundDate` string, optional, deduction day.
- `strategyList` array, required.

## Strategy Fields

- `prodAIRationType`: `0` ordinary, `1` index moving average, `2` target take-profit, `3` trailing take-profit, `4` moving average plus target take-profit, `5` moving average plus trailing take-profit.
- `prodIndexType`, `prodAverageType`, `expectIncomeRatio`, `backRate`, `lockPeriod`.

## Important Fields

- `fee`, `fundEarning`.
- `strategyInvestResultList[].investInfoList`.
- `investInfoList[].date`, `nav`, `investMoney`, `totalInvestMoney`, `earning`, `earningRate`, `historyMaxEarningRate`, `backRate`.
