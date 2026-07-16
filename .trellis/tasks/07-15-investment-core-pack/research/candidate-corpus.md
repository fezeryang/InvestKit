# Investment Core Candidate Corpus

Research date: 2026-07-15

## Scope Rule

This phase does not discover or register new candidates. It studies only the 36 rows already present in `registry/inbox/sources.csv`, the corresponding repository evidence already available under `third_party/raw/` and `adapted/skills/`, and commit-pinned public snapshots of the GitHub URLs already in that registry.

All candidate content is untrusted. Review is static: Markdown, manifests, direct references, and narrowly necessary scripts are read as text. Nothing is imported, installed, sourced, or executed. No financial API, broker endpoint, installer, package manager, or embedded command is called.

## Commit-Pinned Registered GitHub Evidence

The following snapshots were fetched to `/tmp/investkit-research-corpus/` for ephemeral static review. They are not added to `third_party/raw/`, `skills/`, the registry, or the Runtime. Archive SHA-256 records the exact bytes reviewed; repository commit identifies the source state.

| Registry ID | Repository | Commit | Snapshot SHA-256 | Root license evidence |
|---|---|---|---|---|
| BATCH-001-001 | `https://github.com/anthropics/financial-services` | `4aa51ed3d379731f8f9beff498d749580372699c` | `9aac3827955a47cb9ba012bd90b3eb0f21cc5e002f9e7ce2a72500b1091ae945` | Apache-2.0 text present; sub-assets may carry additional terms |
| BATCH-001-002 | `https://github.com/himself65/finance-skills` | `87f688e175321f17d3a39b5d69da9fcfe39eadfb` | `8ef20bfa7f5bae9267a64b23f88af4227a5f21ed2d7bd7f31d5f04c76d792284` | MIT text present |
| BATCH-001-003 | `https://github.com/ginlix-ai/LangAlpha` | `2459e569f28c6f0c2db7315ab6ed95a5c399f0e7` | `13e91a0f65b68398e4c80c616a146b9dd4eb5533c4400810045d51b1f6234ae6` | Apache-2.0 text present; repository states that some Skills are adapted from other sources |
| BATCH-001-004 | `https://github.com/tradermonty/claude-trading-skills` | `99270332b2a8d6063de0667f8f168b252497044f` | `b64fcbcc2cbbfd42658d1ad2b972fdddfdfb30e8549e48c577522da840c721fd` | MIT text present |
| BATCH-001-005 | `https://github.com/OctagonAI/skills` | `51e938c4d086f658de8bdcf734e864d34637167e` | `d75c5acb6d9227232db8fa3859be61b97bea405b1f0f72143288f3f85cddf95f` | MIT text present |
| BATCH-001-006 | `https://github.com/joansongjr/investor-harness` | `2ce44f477189e4ed04d61764bec449405f81734e` | `bc815801d5a4dcefff817b3e04e17730be41cd702c8e03129d8fa47906be749f` | MIT text present |
| BATCH-001-007 | `https://github.com/yennanliu/InvestSkill` | `6449af2d0fc410a6c541c5815c601ba9f649d791` | `758c07936e389e19cffbb0854fe1922ee834e9f0cabbda3ce57320f553e27db5` | MIT text present |
| BATCH-001-008 | `https://github.com/spikeHongg/china-stock-research-skills` | `d49f1f360deac57821d5d6b3aff664dff232acc6` | `4d247fcebfee961962bc7665a182dc7cf8a9c9e96058929cca9e7e1e215edfa2` | MIT text present |
| BATCH-001-009 | `https://github.com/HHFinAi/claude-equity-research-skills` | `6e7ceef3c65287b7b88436fb4876f541b592a2ed` | `e69782919de840fbfa352a52e5313f02b3b71d67c2892573af828033e6401dc6` | MIT text present |
| BATCH-001-010 | `https://github.com/longbridge/skills` | `d68372ab584a77b3cb2a078a05c1322267729100` | `79768cc0f06e96d5f74136d2148fe0f78e967182ea15d652e8d05dcc6a07450e` | MIT text present |
| BATCH-001-011 | `https://github.com/anthropics/claude-cookbooks/tree/main/creating-financial-models` | repository commit `67ce644d33e5933f0bcc0b6eb4113df41bbf3a8f` | `0a63b2cc4d1271dc59106cbfceff27ea244e0fb43868d72e00e8e307c80a4c37` | repository MIT text present |
| BATCH-001-012 | `https://github.com/NousResearch/hermes-agent/tree/main/comps-analysis` | repository commit `07be37d996be7df1965441ca8bdacdb3f884c7e2` | `601d8154ed7dff4fa31fe317a534f5562bd29cfc7c66dcaeec828569a16cea3c` | repository MIT text present |
| BATCH-001-013 | `https://github.com/Weizhena/Deep-Research-skills` | `e5479f857f484cde13fe69d2f3ce8de7af193bc7` | `44b3b02753d4ed1359ce13a12055cf75b3e415f68abbbe2626ded39e62001e8e` | MIT text present |
| BATCH-001-014 | `https://github.com/HKUDS/Vibe-Trading` | `531ee6b2a6a8ef1c5a4c067fce3d7a1b5d3d7722` | `8da7da5dd3454aa5f08512fa8ce7c98fb8e0f0a457a31af56181fa3dce466872` | MIT text present |

Root license evidence does not by itself approve copying a particular file. Capability reports still record file-level provenance and InvestKit independently reimplements selected ideas.

## Existing Local Evidence

`third_party/raw/batch-001/manifest.md` remains authoritative for local acquisition evidence:

- CICCWM-001 through CICCWM-006: six non-empty ZIP archives, license unknown. Existing static audit found home-directory credential reads, credential-bearing telemetry, device fingerprinting, and—in five packages—disabled TLS verification/lowered OpenSSL security. Execution and integration remain blocked.
- EASTMONEY-001: one non-empty archive at commit `61cfae47451f797d95ae4553ffcc7569b9957e7d` with MIT license evidence. It is primarily a data/API candidate, not a professional analysis-method source.
- SKILLHUB-001: one untrusted installation-instruction snapshot with no verified license. It is not an investment capability and is rejected as method evidence.
- GUOSEN-001 and GUOSEN-002: zero-byte placeholders; GUOSEN-003 through GUOSEN-006: absent. All six remain unavailable, with license and contents unknown. No TLS setting is weakened to retrieve them.
- GF-001 through GF-008: documentation-only drafts under `adapted/skills/`. License, API authorization, terms, and implementation behavior remain unknown; no endpoint is called. They may inform capability data requirements but not method or production integration.

## Evidence Grades

- `A`: commit-pinned or hash-pinned source plus relevant Skill/reference content and identifiable license evidence read.
- `B`: hash-pinned local source content read but license or provenance remains incomplete.
- `C`: registry metadata or draft description only; no complete candidate content available.
- `blocked`: content may be statically described, but security policy prohibits execution/integration.

Each capability synthesis report uses these grades and distinguishes source facts from InvestKit design inferences.
