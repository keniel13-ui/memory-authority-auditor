# Imported Anchor — Grok Bounded Attack Result

**PHASE 35** — Grok/Aethar  
**Time:** 2026-07-21 ~8:20 PM EDT  
**Target:** freeze `b476cf3` → implementation `9b8af1b` (local, **not pushed**; `origin/main` = `29cb31c`)  
**Authority:** read-only attack; no edits, no push

## Where we are (board)

| Item | State |
|------|--------|
| Lane 1 | **George** — real dollar; waiting on materials / Invoice Fly |
| Lane 2 | **Imported Anchor → Anchor Contract v0** — PASS A local only |
| Freeze | `b476cf3` — prereg + 5-case fixture |
| Impl | `9b8af1b` — comparator + tests + PASS A artifact |
| Suite | **45 passed / 1 xfailed** (focused imported-anchor: 5 passed) |
| Push | **Blocked until this attack closes** |
| Article | **No** new article |
| SOL file | Still untracked, untouched |

Honest PASS A claim (matches maker result): foreign events can recover a pre-ledger surface and expose proposer silence **only** with an explicit derivation rule + unambiguous local census. Occurrence ≠ meaning. Foreign ≠ independent. Cross-source IDs currently break the considered-set gate (IA-3).

## Fingerprints (attack-time)

| Path | SHA-256 |
|------|---------|
| `agents/imported_anchor_diff.py` | `e124822d52d7e01f18b0e7d9837f37ec55a91b9a49f46de2d4432c367f5e64bd` |
| `tests/test_imported_anchor_diff.py` | `f501a317802d57dc5ded54fa97a311ad410038de9be2b4d6dc62b3bf2654fb10` |
| `tests/fixtures/path_a_v3_imported_anchor_diff_2026_07_21.json` | `6754bae34df3f24545a805a8e314d9e0a3254f4b7f02aae55c5413abe51eea5f` |

## Verdict

# **BLOCKING — 2 items**

Frozen IA-1…IA-5 **match** expected bars. Core honesty properties (ambiguous census, missing scope, missing receipt, forged internal producer, unsupported kind) **hold**.  
Two identity/cardinality bugs are real enough to **repair before push**.

---

### Attack matrix

| # | Attack | Result | Evidence |
|---|--------|--------|----------|
| 1 | Ambiguous census targets | **PASS** | Second live same-scope record → `ambiguous_live_same_scope_target`, zero derived |
| 2 | Zero live targets | **PASS** | `no_live_same_scope_target`, zero derived |
| 3 | Duplicate / replayed event | **BLOCK B1** | Same event twice → `derived_surface_count=2`, identical `surface_id` twice; semantic indexes collapse to 1 key while list length doubles |
| 4 | Empty-but-present stream | **PASS (intentional)** | `receipt_present=True`, `events=[]` → no integrity failure, 0 derived, reasons say evaluated under policy. Missing receipt still → `imported_anchor_integrity_failure` (IA-5). Empty present ≠ missing receipt |
| 5 | Forged independence (internal producer / flags false) | **PASS** | `imported_anchor_provenance_failure`, no derived |
| 6 | Timing / pre-ledger | **PASS + boundary** | Pre-`local_ledger_started_at` event recorded in `pre_ledger_birth_event_ids`. Missing `event.at` still derives; no separate `observed_time` (Anchor Contract gap, not silent false pass) |
| 7 | event_id collision, different semantics | **BLOCK B2** | Two events, same `event_id`, different `record_id` → **same** `surface_id` string, **different** semantic tuples. `surface_id` is not a unique identity |
| 8 | Unsupported event kind | **PASS** | `unsupported_event_kind`, no fabricated relation |
| 9 | IA-3 ID vs semantics | **PASS (named break)** | Semantic align 1; `considered_set_identity_break=True`; gate still `hole_in_considered_set` — frozen receipt of the problem, not a silent miss |
| 10 | Label-only provenance / unreceipted census | **BOUNDARY** | Documented; crypto/digest and census receipts are Anchor Contract v0, not this freeze’s false claim |

---

## Blocking items

### B1 — Duplicate events not collapsed

**Code:** `evaluate_imported_anchor_case` appends every successful derivation with no dedupe by `event_id` or semantic key (`imported_anchor_diff.py` loop ~L207–216).

**Probe:** Clone IA-1 event twice in `imported_anchor.events`.

**Observed:**  
`derived_surface_count=2`, both IDs `imported::anchor_platform_so1::foreign_ev_so1_write`.  
`missing_from_considered` semantic count stays 1 (dict index), so list vs set semantics diverge.

**Smallest fix:** Dedupe by `event_id` (and/or refuse duplicate `event_id` with integrity/unresolved alarm). Prefer: first wins + `duplicate_event_id` unresolved/warning, or hard fail if payloads differ.

**Regression:** duplicate identical event → one derived surface; duplicate `event_id` with differing payload → explicit alarm, not two silent rows.

### B2 — `surface_id` is not unique when `event_id` collides across different semantics

**Code:** `surface_id = f"imported::{anchor_id}::{event_id}"` only (`_derive_event_surface` ~L96–99).

**Probe:** Two `record_write` events, same `event_id`, different `record_id`, one live same-scope target.

**Observed:** Two surfaces, **identical** `surface_id`, different `(source_record_id, target_record_id, …)`.

**Smallest fix (PASS A scope):** Include a payload digest or semantic stub in `surface_id` **or** reject colliding `event_id` with different payloads.  
**Contract v0 scope (do not fake in PASS A):** separate provenance `event_id` from canonical `surface_key` (RFC 8785 hash of semantic tuple) as Kairos PHASE 732 described.

**Regression:** same `event_id` + different semantics → not two rows sharing one `surface_id` without alarm.

---

## Non-blocking (do not fail PASS A honesty)

- Empty present stream as “evaluated, zero surfaces” is coherent vs IA-5 missing receipt.
- Hardcoded `supersedes` under one policy is declared (`DERIVATION_POLICY`).
- No `observed_time` / coverage window yet — named next leap, not a silent overclaim.
- Fixture `records[]` census is hand-supplied — largest deploy gap, already in maker result.

---

## Alignment with Anchor Contract v0 sequence

Kairos PHASE 732 sequence is correct. After **B1/B2 repair**:

1. Re-run this attack (narrow) → then push freeze+impl if clean.  
2. Freeze Anchor Contract v0 objects (event receipt, census receipt, coverage window, derivation policy version, canonical surface key).  
3. Canonical `surface_key` via RFC 8785-style canonical JSON + hash.  
4. `event_time` + `observed_time` + coverage.  
5. CloudEvents-shaped envelope; innovate at authority derivation.  
6. Next adversarial packet (same semantics different systems, replay, late, multi-target, tamper, etc.).  
7. One real external replay (e.g. GitHub history) — only after identity contract exists.

**Still not:** new article, ten event types, broad webhooks, “foreign ⇒ independent,” push before repair.

**Lanes:** George = 1 when materials arrive; Anchor Contract = 2. Nothing else opens.

---

## Return for Kairos

1. Repair **B1** + **B2**.  
2. Add regressions.  
3. Re-call Grok for narrow re-check **or** state PASS if fingerprints only change for those fixes.  
4. Then push `b476cf3`…`9b8af1b` (+ repair commit).  
5. Do **not** start Contract v0 freeze until push gate is honest.

Grok lane: last used **35**; next **36**.  
No code edited in this attack.

— Grok/Aethar, PHASE 35
