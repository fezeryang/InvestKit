# Skill 与数据 Provider 登记页

更新时间：2026-07-17

本页是用户提供的 Skill/API 清单的项目登记入口。登记不等于安装或授权；每个候选必须经过静态审查、许可证/数据条款确认和运行测试后，才能进入生产 Skill 目录。

## 凭据安全

用户消息中出现过中金财富、国信证券和广发证券的 API key。项目不保存、回显或写入这些值；它们应立即轮换，并仅通过运行环境中的秘密管理器注入。登记页只记录变量名：

- 中金财富：`CICCWM_API_KEY`
- 国信证券：`GUOSEN_APIKEY`（变量名待确认）
- 广发证券：`GF_SKILLS_APIKEY`
- 东方财富：`MX_APIKEY`

## 数据源登记

| 提供方 | 来源 | 覆盖范围 | 当前决定 | 当前状态 |
|---|---|---|---|---|
| 东方财富 | [meission/eastmoney](https://github.com/meission/eastmoney) | 行情、财务、公司资料、估值、搜索、选股 | adapt | 已完成受控客户端；需 `MX_APIKEY` 与数据条款确认 |
| 中金财富 | `cdnweb.ciccwm.com/zzt/static/skills/*.zip` | 行情、财务、热榜、ETF、龙虎榜、基金 | adapt | clean-room 只读适配已批准；六包真实调用通过；行情、四类财务和目标相关事件已进入统一研究 Bundle |
| 国泰海通灵犀 | `skillhub.cn` 的 `lingxi-smartstockselection-skill` | 智能选股、历史回测 | reject | 用户已从 InvestKit 范围移除；不安装、不适配、不预留凭据 |
| 国信证券 | `guosen.com.cn/gs/xxskills/*.zip` | 行情、财务、宏观、选股、基金、ETF | review | 原始压缩包未安装；需逐包静态审查与条款确认 |
| 广发证券 | `mcp-api.gf.com.cn/gf-skills/skills/mcp/call` | 龙虎榜、F10、估值财务、ETF、基金 | adapt | 八项受控能力已批准，并已完成真实只读 API 验证 |

本次授权后的取证记录：中金六个 ZIP 已进入隔离原始区并完成初审，详见 [ciccwm-wrapper-review.md](../../reports/project/ciccwm-wrapper-review.md)。国信六个 ZIP 因官网 TLS 旧式重协商导致安全下载失败，未使用 `-k` 绕过，状态保持 `unknown`/不可用。

## 广发证券 Skill 清单

已登记但不自动安装：

- `gf_lhb_list`：`lhb_aborttrade_market_date_get`
- `gf_stock_f10`：`wechat_f10 / f10_basic_post`
- `gf_stock_valuation`：`quant / common_basic_post`、`compare_indicator_post`
- `gf_etf_rank`：`etf_rank / finance-api_product_etf_rank_get`
- `gf_etf_search`：`etf_search / finance_api_inclusive_etf_list_get`
- `gf_etf_super_fund`：`etf-super-fund / gfmiddle_eits_super_fund_etf_superfund_get`
- `gf_fund_detail`：`jijin_info / finance-api_product_fund_detail_get`
- `gf_fund_invest`：`fund_invest / finance_api_product_invest_compute_post`

## 安装与审查规则

1. 原始第三方压缩包只进入 `third_party/raw/`，不直接复制到生产 Skill 目录，不执行其中脚本。
2. 每个候选必须在运行目录中有唯一决定：`adopt`、`adapt`、`extract`、`reference`、`duplicate`、`unsafe`、`reject` 或 `unknown`。
3. 网络调用必须使用环境变量凭据、精确 HTTPS 主机白名单、超时、响应大小限制、拒绝重定向和严格 JSON 校验。
4. 只有完成 API 授权、数据使用条款和离线/在线测试后，才可将 `review_required` 提升为 `approved`。

## 本次动作记录

- 已读取并遵循 SkillHub 官方安装说明：安装到当前 Agent 的 `.agents/skills` 或 `~/.codex/skills`，不使用默认 `./skills/`。
- 已确认当前环境没有 `skillhub` CLI，因此未执行未知安装脚本。
- 未保存任何 API key；用户应先轮换消息中暴露的凭据。

## 灵犀包审查记录

- SkillHub 搜索元数据显示版本 `1.0.4`，发布者为已认证的国泰海通证券股份有限公司。
- 2026-07-17 下载包 SHA-256：`7a4e6322cb9aa4d27091ad32284865a9aa936bc511f24ca57806128efd718640`。
- 包内只有 `SKILL.md`、`skill-entry.js`、`gateway-config.json`，没有 LICENSE。
- Skill 文档内部版本写为 `1.10.1`，与 SkillHub 元数据 `1.0.4` 不一致。
- 当前决定为 `unsafe`（直接安装/执行）；后续可在取得明确许可条款和独立灵犀 API key 后做 clean-room provider，不能把原脚本复制进生产 Skill 目录。
