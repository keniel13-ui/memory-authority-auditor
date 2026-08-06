# Imported Anchor B1/B2 Narrow Re-check Handoff

Date: 2026-07-21
Target chain: `b476cf3` (freeze) -> `9b8af1b` (PASS A implementation) -> `98a8f1c` (B1/B2 repair)
Requested seat: Grok/Aethar PHASE 36, read-only narrow re-check
Push state: local only; `origin/main` remains `29cb31c`

## Attack findings being repaired

- B1: identical replay produced two derived rows with the same `surface_id`.
- B2: one reused `event_id` with different payloads produced different semantic surfaces under the same `surface_id`.

## Maker repair behavior

### B1 expected

Duplicate the IA-1 event byte-for-byte inside `imported_anchor.events`.

- `alarm_code` is `null`
- `derived_surface_count` is `1`
- `duplicate_replay_event_ids` is `["foreign_ev_so1_write"]`
- `duplicate_replay_count` is `1`
- exactly one derived `surface_id` exists

### B2 expected

Duplicate the IA-1 event ID but change its payload, such as `record_id`.

- `alarm_code` is `imported_anchor_event_identity_conflict`
- `derived_surfaces` is empty
- `event_identity_conflict_count` is `1`
- conflicting event ID is preserved in `event_identity_conflicts`
- no partial shipped-gate evaluation occurs

## Current fingerprints

- `agents/imported_anchor_diff.py`: `fe96a0496c55c14b2839379c10738824543d8c1f34fd8549f5d6e52afe65861a`
- `tests/test_imported_anchor_diff.py`: `ce35cc0eba834a4bdbd8337ab774d420074a64ebb71099bc080387cfd86ed47e`
- frozen fixture, unchanged: `6754bae34df3f24545a805a8e314d9e0a3254f4b7f02aae55c5413abe51eea5f`

## Reproduction

```bash
git diff b476cf3..98a8f1c -- agents/imported_anchor_diff.py tests/test_imported_anchor_diff.py
python3 -m pytest tests/test_imported_anchor_diff.py -q
python3 -m pytest -q
shasum -a 256 agents/imported_anchor_diff.py tests/test_imported_anchor_diff.py tests/fixtures/path_a_v3_imported_anchor_diff_2026_07_21.json
```

Expected tests:

- Focused: `7 passed`
- Full: `47 passed, 1 xfailed`
- Latest generated artifact: `path_a_eval_artifacts/path_a_v3_imported_anchor_diff_pass_a_20260722T002052Z.json`
- Frozen result: `5/5`, `all_cases_matched: true`

## Boundary

This repair closes event replay and event-ID collision only. It does not implement Contract v0 canonical semantic `surface_key`, signed provenance, census receipts, `observed_time`, or coverage windows. IA-3 must remain a named cross-source identity break until Contract v0.

Do not edit the candidate. Return PASS/BLOCK with exact reproduction evidence. Push remains blocked until this re-check returns.
