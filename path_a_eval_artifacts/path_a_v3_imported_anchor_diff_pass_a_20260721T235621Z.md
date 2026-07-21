# Path A v3 Imported-Anchor Diff PASS A

Generated: `2026-07-21T23:56:21.577351Z`

Zero-model comparison of imported foreign events, fixture expected surfaces, proposer emissions, and shipped gate behavior.

## Summary

- Total cases: 5
- Matched: 5/5
- All cases matched: `True`
- Freeze commit: `b476cf3`
- Derivation policy: `same_scope_live_record_requires_authority_change_candidate`

## Per-Case Diff

### `path_a_v3_ia1_foreign_receipt_catches_so1_silence`

- Source frozen case: `path_a_v3_so1_full_silence_with_independent_footprint`
- Class: `imported_anchor_positive_silent_omission_catch`
- Imported alarm: `None`
- Derived / aligned / fixture-only / imported-only: `1 / 1 / 0 / 0`
- Missing from considered-set: `1`
- Unresolved events: `[]`
- Pre-ledger-birth events: `[]`
- Shipped silent-omission alarm: `undeclared_surface`
- Shipped considered-set alarm: `None`
- Cross-source identity break: `False`
- Matched frozen bar: `True`

### `path_a_v3_ia2_birth_date_recovery`

- Source frozen case: `path_a_v3_cs6_no_expected_set_decorative`
- Class: `imported_anchor_positive_birth_date_recovery`
- Imported alarm: `None`
- Derived / aligned / fixture-only / imported-only: `1 / 0 / 0 / 1`
- Missing from considered-set: `1`
- Unresolved events: `[]`
- Pre-ledger-birth events: `["foreign_ev_cs6_prebirth"]`
- Shipped silent-omission alarm: `None`
- Shipped considered-set alarm: `None`
- Cross-source identity break: `False`
- Matched frozen bar: `True`

### `path_a_v3_ia3_semantic_match_surface_id_break`

- Source frozen case: `path_a_v3_cs1_honest_full_considered_set`
- Class: `imported_anchor_negative_cross_source_identity`
- Imported alarm: `None`
- Derived / aligned / fixture-only / imported-only: `1 / 1 / 0 / 0`
- Missing from considered-set: `0`
- Unresolved events: `[]`
- Pre-ledger-birth events: `[]`
- Shipped silent-omission alarm: `None`
- Shipped considered-set alarm: `hole_in_considered_set`
- Cross-source identity break: `True`
- Matched frozen bar: `True`

### `path_a_v3_ia4_webhook_missing_scope`

- Source frozen case: `None`
- Class: `imported_anchor_negative_semantic_mapping`
- Imported alarm: `imported_anchor_unresolved`
- Derived / aligned / fixture-only / imported-only: `0 / 0 / 0 / 0`
- Missing from considered-set: `0`
- Unresolved events: `[{"event_id": "foreign_ev_ia4_activity", "reason": "missing_scope"}]`
- Pre-ledger-birth events: `[]`
- Shipped silent-omission alarm: `None`
- Shipped considered-set alarm: `None`
- Cross-source identity break: `False`
- Matched frozen bar: `True`

### `path_a_v3_ia5_expected_receipt_missing`

- Source frozen case: `None`
- Class: `imported_anchor_negative_receipt_integrity`
- Imported alarm: `imported_anchor_integrity_failure`
- Derived / aligned / fixture-only / imported-only: `0 / 0 / 0 / 0`
- Missing from considered-set: `0`
- Unresolved events: `[]`
- Pre-ledger-birth events: `[]`
- Shipped silent-omission alarm: `None`
- Shipped considered-set alarm: `None`
- Cross-source identity break: `False`
- Matched frozen bar: `True`
