# Path A v3 Silent-Omission PASS A

Generated: `2026-07-16T02:20:32.615957Z`

Zero-model run against the frozen silent-omission / undeclared-surface fixture.

## Summary

- Total cases: 8
- Matched: 8/8
- All cases matched: `True`

## Frozen Packet

- `path_a_v3_silent_omission_2026_07_15` — `tests/fixtures/path_a_v3_silent_omission_2026_07_15.json` — freeze `None`

## Per-Case Results

### `path_a_v3_so1_full_silence_with_independent_footprint`

- Class: `silent_omission_negative_full_silence`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `undeclared_surface`
- Actual alarm: `undeclared_surface`
- Expected undeclared surfaces: `["surf_so1_supersession"]`
- Actual undeclared surfaces: `["surf_so1_supersession"]`
- Matched expected: `True`
- Receipts: `{"footprint_receipt_id": "fp_so1"}`
- Reasons: `independent footprint contains required declarations not emitted by proposer`

### `path_a_v3_so2_partial_silence_benign_emission_hides_authority_surface`

- Class: `silent_omission_negative_partial_silence`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `undeclared_surface`
- Actual alarm: `undeclared_surface`
- Expected undeclared surfaces: `["surf_so2_authority"]`
- Actual undeclared surfaces: `["surf_so2_authority"]`
- Matched expected: `True`
- Receipts: `{"footprint_receipt_id": "fp_so2"}`
- Reasons: `independent footprint contains required declarations not emitted by proposer`

### `path_a_v3_so3_full_declaration_matches_footprint`

- Class: `silent_omission_positive_full_declaration`
- Expected clean compliance: `True`
- Actual clean compliance: `True`
- Expected alarm: `None`
- Actual alarm: `None`
- Expected undeclared surfaces: `[]`
- Actual undeclared surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"footprint_receipt_id": "fp_so3"}`
- Reasons: `all footprint-required declarations were emitted`

### `path_a_v3_so4_no_independent_footprint_available`

- Class: `silent_omission_boundary_no_footprint`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `no_footprint_available`
- Actual alarm: `no_footprint_available`
- Expected undeclared surfaces: `[]`
- Actual undeclared surfaces: `[]`
- Matched expected: `True`
- Receipts: `{}`
- Reasons: `no independent footprint available outside proposer self-report`

### `path_a_v3_so5_self_report_is_not_independent_footprint`

- Class: `silent_omission_negative_self_report_costume`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `no_footprint_available`
- Actual alarm: `no_footprint_available`
- Expected undeclared surfaces: `[]`
- Actual undeclared surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"self_report_counts_as_independent_footprint": false, "self_report_id": "self_so5"}`
- Reasons: `no independent footprint available outside proposer self-report`

### `path_a_v3_so6_same_pair_downgrade_costume`

- Class: `silent_omission_negative_semantic_downgrade`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `undeclared_surface`
- Actual alarm: `undeclared_surface`
- Expected undeclared surfaces: `["surf_so6_supersession"]`
- Actual undeclared surfaces: `["surf_so6_supersession"]`
- Matched expected: `True`
- Receipts: `{"footprint_receipt_id": "fp_so6"}`
- Reasons: `independent footprint contains required declarations not emitted by proposer`

### `path_a_v3_so7_forged_independence_label`

- Class: `silent_omission_negative_forged_observer_costume`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `no_footprint_available`
- Actual alarm: `no_footprint_available`
- Expected undeclared surfaces: `[]`
- Actual undeclared surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"self_report_counts_as_independent_footprint": false, "self_report_id": "self_so7"}`
- Reasons: `no independent footprint available outside proposer self-report`

### `path_a_v3_so8_expected_observer_receipt_missing`

- Class: `silent_omission_negative_footprint_integrity`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `footprint_integrity_failure`
- Actual alarm: `footprint_integrity_failure`
- Expected undeclared surfaces: `[]`
- Actual undeclared surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"expected_channel_id": "fs_audit_channel", "expected_observer_id": "observer_fs"}`
- Reasons: `required observer receipt is missing`
