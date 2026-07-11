# Batch 001 Raw Intake Manifest

Audit date: 2026-07-11

This manifest records intake evidence only. Everything below is untrusted and unreviewed. A local file timestamp is evidence of the file's filesystem modification time, not proof of the remote publication time or a complete acquisition log. No archive was extracted into the workspace or executed during this audit.

## Saved Archives And Snapshot

| Source ID | Source URL | Local path / filename | Bytes | SHA-256 | Local time evidence (+08:00) | Download status | License evidence |
|---|---|---|---:|---|---|---|---|
| CICCWM-001 | `https://cdnweb.ciccwm.com/zzt/static/skills/ciccwm-market-analysis.zip` | `third_party/raw/batch-001/ciccwm/CICCWM-001-ciccwm-market-analysis.zip` | 9,776 | `5058d49c9f26a09102c26ffec5ec7c89638ed3c109152cccd2510b947e70a779` | filesystem mtime `2026-07-11 20:14:21` | `saved_unreviewed` | `unknown`; no license file appears in the ZIP directory |
| CICCWM-002 | `https://cdnweb.ciccwm.com/zzt/static/skills/ciccwm-stock-finance-analysis.zip` | `third_party/raw/batch-001/ciccwm/CICCWM-002-ciccwm-stock-finance-analysis.zip` | 8,128 | `97fc680d8866734c32be65f5d5059f902b38435bf06df54af613cf352c84d208` | filesystem mtime `2026-07-11 20:14:43` | `saved_unreviewed` | `unknown`; no license file appears in the ZIP directory |
| CICCWM-003 | `https://cdnweb.ciccwm.com/zzt/static/skills/ciccwm-hot-news-analysis.zip` | `third_party/raw/batch-001/ciccwm/CICCWM-003-ciccwm-hot-news-analysis.zip` | 7,242 | `67e2247dc9db5375031856e4399c0b455d87c212d1a05d03a3e586c7e3ce266b` | filesystem mtime `2026-07-11 20:14:43` | `saved_unreviewed` | `unknown`; no license file appears in the ZIP directory |
| CICCWM-004 | `https://cdnweb.ciccwm.com/zzt/static/skills/ciccwm-etf-ranking-analysis.zip` | `third_party/raw/batch-001/ciccwm/CICCWM-004-ciccwm-etf-ranking-analysis.zip` | 13,208 | `fa8dcf999e1ea7cb48b3035a877a30242d1a252571feb47040dce878d11539f3` | filesystem mtime `2026-07-11 20:16:01` | `saved_unreviewed` | `unknown`; no license file appears in the ZIP directory |
| CICCWM-005 | `https://cdnweb.ciccwm.com/zzt/static/skills/ciccwm-tiger-list-analysis.zip` | `third_party/raw/batch-001/ciccwm/CICCWM-005-ciccwm-tiger-list-analysis.zip` | 9,643 | `c50fd92a2e35ff82baf66df74d0d8c14299bf1a4a582f9200bea8da7451f200a` | filesystem mtime `2026-07-11 20:15:59` | `saved_unreviewed` | `unknown`; no license file appears in the ZIP directory |
| CICCWM-006 | `https://cdnweb.ciccwm.com/zzt/static/skills/ciccwm-fund-product-info.zip` | `third_party/raw/batch-001/ciccwm/CICCWM-006-ciccwm-fund-product-info.zip` | 13,101 | `a0fcf5a4f9a9a0f97c21040dada1c86affc5283ff45bc702ac96c8ff2d5dfffe` | filesystem mtime `2026-07-11 20:15:59` | `saved_unreviewed` | `unknown`; no license file appears in the ZIP directory |
| EASTMONEY-001 | `https://github.com/meission/eastmoney` | `third_party/raw/batch-001/github/EASTMONEY-001-eastmoney.zip` | 30,649 | `24bfe27d67a92572c3c4df234997eabbcdbed0c7962cf81a566c6284efacbd15` | filesystem mtime `2026-07-11 20:14:27` | `saved_unreviewed`; GitHub branch archive, ZIP comment commit `61cfae47451f797d95ae4553ffcc7569b9957e7d` | MIT; `eastmoney-main/LICENSE` inside the archive |
| SKILLHUB-001 | `https://skillhub.cn/install/skillhub.md` | `third_party/raw/batch-001/skillhub/skillhub.md` | 2,769 | `5bcd3c8185bda3211dafec9d90c4f3bc4a2cb05cbeea235e608b26e4be939b8a` | filesystem mtime `2026-07-11 20:14:22` | `instruction_snapshot_saved_unreviewed`; not a Skill package | `unknown`; no license evidence in the snapshot |

## Guosen Failed Or Missing Acquisition

All six URLs failed TLS negotiation with OpenSSL 3 because unsafe legacy renegotiation was disabled. The project did not lower TLS security, disable certificate verification, or retry through an insecure transport. `needs_manual_acquisition` means a human must obtain and provenance-check the asset through an approved channel; it does not authorize a TLS downgrade.

| Source ID | Source URL | Expected local filename | Local evidence | Attempt time evidence (+08:00) | Current conclusion | License status |
|---|---|---|---|---|---|---|
| GUOSEN-001 | `https://www.guosen.com.cn/gs/xxskills/gs-stock-market-query.zip` | `GUOSEN-001-gs-stock-market-query.zip` | 0-byte failed placeholder; SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; not a valid archive | placeholder mtime `2026-07-11 20:16:31` | `needs_manual_acquisition` | `unknown`; package unavailable |
| GUOSEN-002 | `https://www.guosen.com.cn/gs/xxskills/gs-stock-financial-query.zip` | `GUOSEN-002-gs-stock-financial-query.zip` | 0-byte failed placeholder; SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; not a valid archive | placeholder mtime `2026-07-11 20:16:21` | `needs_manual_acquisition` | `unknown`; package unavailable |
| GUOSEN-003 | `https://www.guosen.com.cn/gs/xxskills/gs-economy-query.zip` | `GUOSEN-003-gs-economy-query.zip` | no local file | audit trail records attempt date `2026-07-11`; exact time `unknown` | `needs_manual_acquisition` | `unknown`; package unavailable |
| GUOSEN-004 | `https://www.guosen.com.cn/gs/xxskills/gs-smart-stock-picking.zip` | `GUOSEN-004-gs-smart-stock-picking.zip` | no local file | audit trail records attempt date `2026-07-11`; exact time `unknown` | `needs_manual_acquisition` | `unknown`; package unavailable |
| GUOSEN-005 | `https://www.guosen.com.cn/gs/xxskills/gs-fund-compare.zip` | `GUOSEN-005-gs-fund-compare.zip` | no local file | audit trail records attempt date `2026-07-11`; exact time `unknown` | `needs_manual_acquisition` | `unknown`; package unavailable |
| GUOSEN-006 | `https://www.guosen.com.cn/gs/xxskills/gs-etf-filter.zip` | `GUOSEN-006-gs-etf-filter.zip` | no local file | audit trail records attempt date `2026-07-11`; exact time `unknown` | `needs_manual_acquisition` | `unknown`; package unavailable |

## Static Risk Observations, Not Review Decisions

- All six CICCWM Python scripts read `~/.config/ciccwm/config.json`, outside the project directory, to obtain `CICCWM_API_KEY`.
- All six build a device fingerprint and asynchronously send usage telemetry to `https://webreport.ciccwm.com/zzt/fcgi/common.fcgi`; the telemetry payload includes the API key as `login_id` and local platform attributes.
- CICCWM-001, CICCWM-003, CICCWM-004, CICCWM-005, and CICCWM-006 disable hostname/certificate verification and lower OpenSSL security to `SECLEVEL=0`; CICCWM-001 also contains a `curl -k` subprocess fallback. CICCWM-002 uses a default SSL context but retains the home-directory read and telemetry behavior.
- These findings trigger the security policy's stop-automatic-integration conditions. They do not by themselves replace the required per-candidate processing decision, which remains `unknown` until review.
- The SkillHub file is an installation-instruction snapshot. It contains `curl ... | bash`, asks the Agent to change source preference and behavior, and instructs installation into user-level or project-level Skill directories. Treat every instruction as untrusted prompt content; none was followed.

## Actions Not Taken

- No third-party script, installer, package manager, Skill CLI, or network API was executed.
- No archive was installed or copied into a formal Skill directory.
- No API key was written to the repository or audit output.
- No Guosen download was retried by weakening TLS.
