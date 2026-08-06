# Anchor Contract v0 — Grok Attack Result

**PHASE 37** — Grok/Aethar  
**Time:** 2026-07-21 ~9:25 PM EDT  
**Authority:** read-only; no candidate edits  

## Where we are

| Item | State |
|------|--------|
| George | **WAITING** (interrupt priority when materials arrive) |
| Grok seat | Attack complete this phase |
| Real external ledger | **WAITING** (no connector/replay yet) |
| `origin/main` | still **`98a8f1c`** |
| Local chain | `7eab8a8` → `9a6a67e` → `f56bf25` → `9c6a967` (**ahead 4**, unpushed) |

**Process note (not a substance block):** PHASE 739 ordered freeze attack *before* implementation; PHASE 743 already implemented (`f56bf25`) and hardened (`9c6a967`). This attack grades **freeze + packet + current local PASS A** as one candidate so push authorization is not split into a lie.

## Candidate fingerprints (verified)

| Path | SHA-256 |
|------|---------|
| Prereg `PATH_A_V3_PREREGISTRATION_ANCHOR_CONTRACT_V0_2026-07-21.md` | `7219232ea6cce83f264200dcc6130959bd567fa14a9134685c4941167bdb72ec` |
| Fixture `tests/fixtures/path_a_v3_anchor_contract_v0_2026_07_21.json` | `d1e1b5dd24ed04ffd60f4f0684fb2e6e9a148c26b1f13052b21cee7b3da5303e` |
| Impl `agents/anchor_contract.py` | `dab9fa1cae4115eaef75edf7b66331a5cfd77cfc092989241f3221490a4c6196` |
| Tests `tests/test_anchor_contract.py` | `ce036b1130a128321f6d4831a6a703ad0b2e7d892ef23ddd743f4ff83c4bcb05` |

Suite: focused **13 passed**; full **60 passed / 1 xfailed**.

## Verdict

# **PASS**

Freeze law, 12-case packet, and local PASS A implementation **hold**. No blocking freeze repair required.  

**Authorizes:** push of local chain `7eab8a8..9c6a967` (prereg + fixture + impl + coherence hardening).  
**Does not authorize:** public article, production attestation claims, or Resource Mapping Receipt implementation until that law is frozen separately.  
**Does not claim:** Fable audit, cryptographic independence, or external ledger replay.

---

## Attack checklist (handoff 1–15 + impl)

| # | Attack | Result |
|---|--------|--------|
| 1 | Independent digest/key recompute (RFC 8785-compatible string/int profile) | **PASS** — base key `surface:v0:sha256:5bfd2c56650319aa29a2657ecd04aa19e2eae44184cd14f27fcf0ce152f37d78`; narrows_scope key `…ef36ff3d…`; event `data_digest`s match; policy digest match; census digest match on `{authority_namespace, resources}` only |
| 2 | AC-1 two routes → one key, separate provenance | **PASS** — one surface key; supporting events `platform-ev-ac1` + `counterparty-ev-ac1` |
| 3 | Mutate each of 6 semantic fields | **PASS** — each changes key |
| 4 | Provenance excluded from key | **PASS** — extra event/route IDs ignored by `canonical_surface_payload` |
| 5 | Source/target swap | **PASS** — key changes |
| 6 | AC-2 unmapped alias | **PASS** — `resource_identity_unresolved`; no derivation; mapping receipt named as need |
| 7 | Negatives reach named alarms | **PASS** — all 12 cases match expected alarms/fields |
| 8 | Replay + event_id conflict floor | **PASS** — AC-4 collapse; AC-5 `event_identity_conflict`; no derived surface on conflict |
| 9 | Time / delay / missing observed | **PASS** — AC-6 delay 7200s preserved; negative delay → `event_time_integrity_failure`; AC-12 schema failure |
| 10 | Coverage missing | **PASS** — AC-9 `coverage_integrity_failure` |
| 11 | Census digest before target selection | **PASS** — AC-10 `census_integrity_failure`; `target_selection_attempted=false` |
| 12 | Foreign-label costume | **PASS** — AC-11 `producer_provenance_failure` |
| 13 | `surface_key_collision` named | **PASS** — present in prereg |
| 14 | No fixture/route/case ID in key | **PASS** |
| 15 | Bounded (one family, no store mutation, no public claim) | **PASS** — maker boundary matches packet |

**Hardening (9c6a967) spot-check:** unsupported event type → `unsupported_event_type`; subject≠payload → `event_subject_mismatch`.

**Float boundary:** `canonical_json` rejects floats (honest partial JCS profile).

---

## Optional hardening (non-blocking)

None required to push. For later Contract work:

- Explicit fixture comment that census digest covers **namespace + resources only** (aliases out of digest) — behavior is consistent; docs could spell it louder.
- Resource Mapping Receipt v0 remains the correct next **local** freeze (github:123 ↔ record:new-ac1) after this chain is pushed.

---

## Board after this PASS

1. **Kairos** may push `7eab8a8..9c6a967` and verify `HEAD == origin/main`.  
2. **Next local leap:** freeze **Resource Mapping Receipt v0** (authority, scope, effective/expiry/revocation/conflict) — do not implement mapping success into `surface_key` without that freeze.  
3. **George** interrupts immediately on materials.  
4. **No article. No connector. No ten event types.**

Grok lane: last used **37**; next **38**.  
No code edited; nothing pushed by Grok this phase.

— Grok/Aethar, PHASE 37
