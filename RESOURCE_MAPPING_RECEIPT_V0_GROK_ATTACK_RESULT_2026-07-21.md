# Resource Mapping Receipt v0 — Grok Attack Result

**PHASE 38** — Grok/Aethar  
**Time:** 2026-07-21 ~10:05 PM EDT  
**Candidate HEAD:** `0899306`  
**Remote floor at attack start:** `origin/main == 9c6a967`  
**Authority:** read-only attack; push authorized on PASS

## Verdict

# **PASS**

All required matrix items hold. RM-13 census reachability correction is legitimate (intended alarm reachable; bar not weakened). Suite: Mapping **20**, Mapping+Anchor **33**, full **80 passed / 1 xfailed**.

## Fingerprints (match handoff)

| Path | SHA-256 |
|------|---------|
| Prereg | `85940597e3f144a9e6d80226a91cae6c09e0af89b9c6dcb28e7aa0a9c7f52728` |
| Fixture | `9a181a728833bddf2b64077a67307c2675bda932d667cde72f637b4418d9262f` |
| `agents/resource_mapping.py` | `a170d9c5c797d0df26e64a4e2ef940a749ad90f34006d3c7f0a3cd1f59a15edc` |
| `agents/anchor_contract.py` | `192b42d41184d83c3dcac2bff54af226f58b4712d36caffca24a8b3397106922` |
| `tests/test_resource_mapping.py` | `a3c752e95b00ea744b38ade18ca8259bd0c288dda0db0d27c514c96b7109e43b` |
| PASS A result md | `cd0c5995c70d5fb10d2989c3ef6aaf6392befe3def1347005a14fe757cd328f0` |
| PASS A artifact json | `f95c14a4e1dcab8cec6485901ba673bdcaf28ede86de629109e6acf919df1555` |

## Matrix (condensed)

| # | Result | Evidence |
|---|--------|----------|
| 1 Mapping key recompute | **PASS** | `mapping:v0:sha256:760b5c43822b288e1ada1f9425a7842ae52079ae9d0d5288baddf832590b83ef` |
| 2 Embedded digests | **PASS** | Policy + all shared grant/receipt/revocation/census digests recomputed |
| 3 Frozen 14/14 full expected fields | **PASS** | Every expected field matched |
| 4 Semantic field mutations | **PASS** | All 7 assertion fields change key |
| 5–12 Authority/time/active-set/replay/revocation/census/direction | **PASS** | RM-2…RM-14 alarms + null keys on failure |
| 13 Anchor bridge | **PASS** | RM-1 + AC-2 census closes AC-2; surface key = AC-1 exactly; truthy/altered mapping rejected |
| 14 Failure null key exposure | **PASS** | Failures leave `mapping_key` and `canonical_resource_id` null |
| 15 Suites | **PASS** | 20 / 33 / 80p+1x |

**Claims graded:** directional, exact-scope, grant-bound, dual clocks, active conflict only, census-bound target, mapping key vs provenance, AC-2 close without fixture surface ID, coherence-not-crypto — all honest.

**Non-claims preserved:** no discovery, no signatures, no transitive identity, no connector/replay/article.

## Post-PASS

Push `7b279a9..0899306` to match origin. Next strategic body (Authority Runtime) only after this floor is remote.

— Grok/Aethar, PHASE 38
