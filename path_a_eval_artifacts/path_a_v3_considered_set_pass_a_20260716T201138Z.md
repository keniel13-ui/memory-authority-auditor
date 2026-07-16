# Path A v3 Considered-Set PASS A

Generated: `2026-07-16T20:11:38.683944Z`

Zero-model run against the frozen considered-set / proposer inspection-trace fixture.

## Summary

- Total cases: 11
- Matched: 11/11
- All cases matched: `True`

## Frozen Packet

- `path_a_v3_considered_set_2026_07_16` — `tests/fixtures/path_a_v3_considered_set_2026_07_16.json` — prereg freeze `e65e5e3` — fixture freeze `38d3774`

## Per-Case Results

### `CS-1` — `path_a_v3_cs1_honest_full_considered_set`

- Class: `considered_set_positive_honest_declaration`
- Expected clean compliance: `True`
- Actual clean compliance: `True`
- Expected alarm: `None`
- Actual alarm: `None`
- Expected missing surfaces: `[]`
- Actual missing surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 2, "expected_surface_count": 2}`
- Reasons: `considered_set covers expected surfaces without contradiction`

### `CS-2` — `path_a_v3_cs2_hole_in_considered_set`

- Class: `considered_set_negative_hole`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `hole_in_considered_set`
- Actual alarm: `hole_in_considered_set`
- Expected missing surfaces: `["surf_cs2_authority"]`
- Actual missing surfaces: `["surf_cs2_authority"]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 1, "expected_surface_count": 2}`
- Reasons: `expected surfaces are absent from the declared considered_set`

### `CS-3` — `path_a_v3_cs3_fabricated_declared_negative`

- Class: `considered_set_negative_forged_inspection`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `fabricated_declared_negative`
- Actual alarm: `fabricated_declared_negative`
- Expected missing surfaces: `[]`
- Actual missing surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 1, "expected_surface_count": 1, "fabricated_surface_id": "surf_cs3_authority", "records_not_loaded": ["old_cs3", "new_cs3"]}`
- Reasons: `considered_set claims inspection of records that process truth says were not loaded`

### `CS-4` — `path_a_v3_cs4_empty_considered_set_evasion`

- Class: `considered_set_negative_empty_evasion`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `empty_considered_set_evasion`
- Actual alarm: `empty_considered_set_evasion`
- Expected missing surfaces: `[]`
- Actual missing surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 0, "expected_surface_count": 1}`
- Reasons: `considered_set is empty while expected_set is non-empty`

### `CS-5` — `path_a_v3_cs5_declared_negative_vs_footprint`

- Class: `considered_set_negative_footprint_disagreement`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `declared_negative_contradicted_by_footprint`
- Actual alarm: `declared_negative_contradicted_by_footprint`
- Expected missing surfaces: `[]`
- Actual missing surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 1, "contradicted_surface_id": "surf_cs5_supersession", "expected_surface_count": 1, "footprint_receipt_id": "fp_cs5"}`
- Reasons: `considered_set declares a required footprint surface negative instead of surfaced`

### `CS-6` — `path_a_v3_cs6_no_expected_set_decorative`

- Class: `considered_set_boundary_unfalsifiable`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `considered_set_unfalsifiable`
- Actual alarm: `considered_set_unfalsifiable`
- Expected missing surfaces: `[]`
- Actual missing surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 3}`
- Reasons: `no expected_set or independent falsifier is available for considered_set`

### `CS-7` — `path_a_v3_cs7_considered_set_equals_proposals_only`

- Class: `considered_set_negative_collapse_costume`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `hole_in_considered_set`
- Actual alarm: `hole_in_considered_set`
- Expected missing surfaces: `["surf_cs7_authority"]`
- Actual missing surfaces: `["surf_cs7_authority"]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 1, "expected_surface_count": 2}`
- Reasons: `expected surfaces are absent from the declared considered_set`

### `CS-8` — `path_a_v3_cs8_untyped_considered_set`

- Class: `considered_set_negative_schema_failure`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `considered_set_schema_failure`
- Actual alarm: `considered_set_schema_failure`
- Expected missing surfaces: `[]`
- Actual missing surfaces: `[]`
- Matched expected: `True`
- Receipts: `{}`
- Reasons: `considered_set is missing typed surface objects`

### `CS-SOL-1` — `path_a_v3_cs_sol1_declare_everything_surface_nothing`

- Class: `considered_set_negative_complete_set_false_negative`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `declared_negative_contradicted_by_footprint`
- Actual alarm: `declared_negative_contradicted_by_footprint`
- Expected missing surfaces: `[]`
- Actual missing surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 2, "contradicted_surface_id": "surf_cssol1_authority", "expected_surface_count": 2, "footprint_receipt_id": "fp_cssol1"}`
- Reasons: `considered_set declares a required footprint surface negative instead of surfaced`

### `CS-SOL-2` — `path_a_v3_cs_sol2_over_declaration_flood_missing_required_surface`

- Class: `considered_set_negative_over_declaration_flood`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `hole_in_considered_set`
- Actual alarm: `hole_in_considered_set`
- Expected missing surfaces: `["surf_cssol2_authority"]`
- Actual missing surfaces: `["surf_cssol2_authority"]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 13, "expected_surface_count": 2}`
- Reasons: `expected surfaces are absent from the declared considered_set`

### `CS-SOL-3` — `path_a_v3_cs_sol3_circular_expected_set_out_of_scope_laundering`

- Class: `considered_set_negative_circular_scope_and_disposition_launder`
- Expected clean compliance: `False`
- Actual clean compliance: `False`
- Expected alarm: `considered_set_unfalsifiable`
- Actual alarm: `considered_set_unfalsifiable`
- Expected missing surfaces: `[]`
- Actual missing surfaces: `[]`
- Matched expected: `True`
- Receipts: `{"considered_surface_count": 2, "expected_set_independent_of_proposer": false, "expected_set_source": "proposer_self_report_only", "self_scoped_omitted_surface_ids": ["surf_cssol3_authority"]}`
- Reasons: `expected_set is proposer-authored and cannot serve as an external falsifier`
