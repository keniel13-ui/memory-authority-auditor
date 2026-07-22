# Path A v3 Anchor Contract v0 PASS A

Generated: `2026-07-22T01:16:23.627563Z`

Zero-model run against the frozen Anchor Contract v0 packet.

## Summary

- Total cases: 12
- Matched: 12/12
- All cases matched: `True`
- Preregistration: `7eab8a8`
- Fixture: `9a6a67e`

## Per-Case Results

### `path_a_v3_ac1_two_routes_one_semantic_surface`

- Class: `anchor_contract_positive_cross_source_convergence`
- Alarm: `None`
- Derived surfaces: `1`
- Surface keys: `["surface:v0:sha256:5bfd2c56650319aa29a2657ecd04aa19e2eae44184cd14f27fcf0ce152f37d78"]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "canonical_json": true, "derived_surface_count": true, "route_receipt_count": true, "route_surface_keys_equal": true, "surface_key": true, "surface_payload": true}`
- Reasons: `contract receipts validated and semantic surfaces derived`

### `path_a_v3_ac2_unreceipted_resource_alias`

- Class: `anchor_contract_negative_resource_identity`
- Alarm: `resource_identity_unresolved`
- Derived surfaces: `0`
- Surface keys: `[]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "derived_surface_count": true, "surface_key": true}`
- Reasons: `source-local resource alias has no mapping receipt`

### `path_a_v3_ac3_relation_changes_semantic_key`

- Class: `anchor_contract_positive_semantic_separation`
- Alarm: `None`
- Derived surfaces: `0`
- Surface keys: `["surface:v0:sha256:5bfd2c56650319aa29a2657ecd04aa19e2eae44184cd14f27fcf0ce152f37d78", "surface:v0:sha256:ef36ff3d3db6c5b124826fb6a98fe615aafa4a4649e15b08cf07e6a066af259f"]`
- Matched expected: `True`
- Checks: `{"keys_differ": true, "surface_keys": true}`
- Reasons: `semantic payloads canonicalized without provenance fields`

### `path_a_v3_ac4_identical_event_replay`

- Class: `anchor_contract_positive_replay_collapse`
- Alarm: `None`
- Derived surfaces: `1`
- Surface keys: `["surface:v0:sha256:5bfd2c56650319aa29a2657ecd04aa19e2eae44184cd14f27fcf0ce152f37d78"]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "derived_surface_count": true, "duplicate_replay_count": true, "unique_event_count": true}`
- Reasons: `contract receipts validated and semantic surfaces derived`

### `path_a_v3_ac5_event_id_payload_conflict`

- Class: `anchor_contract_negative_event_identity`
- Alarm: `event_identity_conflict`
- Derived surfaces: `0`
- Surface keys: `[]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "derived_surface_count": true}`
- Reasons: `one source and event ID carry conflicting event payloads`

### `path_a_v3_ac6_late_delivery_preserves_clocks`

- Class: `anchor_contract_positive_temporal_receipt`
- Alarm: `None`
- Derived surfaces: `1`
- Surface keys: `["surface:v0:sha256:5bfd2c56650319aa29a2657ecd04aa19e2eae44184cd14f27fcf0ce152f37d78"]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "delivery_delay_seconds": true, "derived_surface_count": true, "event_time_preserved": true}`
- Reasons: `contract receipts validated and semantic surfaces derived`

### `path_a_v3_ac7_pre_ledger_birth_recovery`

- Class: `anchor_contract_positive_birth_date_recovery`
- Alarm: `None`
- Derived surfaces: `1`
- Surface keys: `["surface:v0:sha256:5bfd2c56650319aa29a2657ecd04aa19e2eae44184cd14f27fcf0ce152f37d78"]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "derived_surface_count": true, "historical_completeness_claimed": true, "pre_local_ledger_birth": true}`
- Reasons: `contract receipts validated and semantic surfaces derived`

### `path_a_v3_ac8_ambiguous_census_targets`

- Class: `anchor_contract_negative_census_ambiguity`
- Alarm: `ambiguous_census_target`
- Derived surfaces: `0`
- Surface keys: `[]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "candidate_target_count": true, "derived_surface_count": true}`
- Reasons: `census has multiple live same-scope targets`

### `path_a_v3_ac9_missing_coverage_receipt`

- Class: `anchor_contract_negative_coverage_integrity`
- Alarm: `coverage_integrity_failure`
- Derived surfaces: `0`
- Surface keys: `[]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "derived_surface_count": true, "must_not_treat_as_observed_empty": true}`
- Reasons: `required coverage receipt is missing`

### `path_a_v3_ac10_tampered_census_digest`

- Class: `anchor_contract_negative_census_integrity`
- Alarm: `census_integrity_failure`
- Derived surfaces: `0`
- Surface keys: `[]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "derived_surface_count": true, "target_selection_attempted": true}`
- Reasons: `census payload does not match its declared digest`

### `path_a_v3_ac11_foreign_label_costume`

- Class: `anchor_contract_negative_producer_provenance`
- Alarm: `producer_provenance_failure`
- Derived surfaces: `0`
- Surface keys: `[]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "derived_surface_count": true, "labels_count_as_proof": true}`
- Reasons: `event producer does not resolve outside the proposer process`

### `path_a_v3_ac12_missing_observed_time`

- Class: `anchor_contract_negative_event_schema`
- Alarm: `event_receipt_schema_failure`
- Derived surfaces: `0`
- Surface keys: `[]`
- Matched expected: `True`
- Checks: `{"alarm_code": true, "derived_surface_count": true, "missing_fields": true}`
- Reasons: `event receipt is missing required contract fields`
