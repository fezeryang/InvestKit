# Batch 001 Raw Intake Manifest

Date: 2026-07-11

This manifest records raw asset intake only. The archives are untrusted and must not be executed before static review.

## Saved Assets

| Source ID | Local path | SHA-256 |
|---|---|---|
| CICCWM-001 | `third_party/raw/batch-001/ciccwm/CICCWM-001-ciccwm-market-analysis.zip` | `5058d49c9f26a09102c26ffec5ec7c89638ed3c109152cccd2510b947e70a779` |
| CICCWM-002 | `third_party/raw/batch-001/ciccwm/CICCWM-002-ciccwm-stock-finance-analysis.zip` | `97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208` |
| CICCWM-003 | `third_party/raw/batch-001/ciccwm/CICCWM-003-ciccwm-hot-news-analysis.zip` | `67e2247dc9db5375031856e4399c0b455d87c212d1a05d03a3e586c7e3ce266b` |
| CICCWM-004 | `third_party/raw/batch-001/ciccwm/CICCWM-004-ciccwm-etf-ranking-analysis.zip` | `fa8dcf999e1ea7cb48b3035a877a30242d1a252571feb47040dce878d11539f3` |
| CICCWM-005 | `third_party/raw/batch-001/ciccwm/CICCWM-005-ciccwm-tiger-list-analysis.zip` | `c50fd92a2e35ff82baf66df74d0d8c14299bf1a4a582f9200bea8da7451f200a` |
| CICCWM-006 | `third_party/raw/batch-001/ciccwm/CICCWM-006-ciccwm-fund-product-info.zip` | `a0fcf5a4f9a9a0f97c21040dada1c86affc5283ff45bc702ac96c8ff2d5dfffe` |
| EASTMONEY-001 | `third_party/raw/batch-001/github/EASTMONEY-001-eastmoney.zip` | `24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15` |
| SKILLHUB-001 | `third_party/raw/batch-001/skillhub/skillhub.md` | `5bcd3c8185bda3211dafec9d90c4f3bc4a2cb05cbeea235e608b26e4be939b8a` |

## Blocked Downloads

| Source IDs | Reason |
|---|---|
| GUOSEN-001 through GUOSEN-006 | `www.guosen.com.cn` connected but failed TLS negotiation with OpenSSL 3: `unsafe legacy renegotiation disabled`. Automatic downgrade of TLS security was not performed. |

## Not Executed

- No third-party shell scripts were executed.
- `skillhub` CLI was not installed because the fetched install instructions require a pipe-to-shell installer and no local `skillhub` binary was present.
- No API keys were written to the repository.
