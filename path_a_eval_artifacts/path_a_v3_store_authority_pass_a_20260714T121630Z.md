# Path A v3 Store-Authority PASS A

Generated: `2026-07-14T12:16:30.224872Z`

Zero-model run against frozen fixtures. This artifact evaluates deterministic store-side authority, promotion, grant-lifecycle, and declared-provenance checks only.

## Summary

- Total cases: 17
- Pass-bar cases: 16
- Ceiling cases reported separately: 1
- Pass-bar matched: 16/16
- Ceiling matched: 1/1
- All pass-bar cases matched: `True`
- All reported cases matched: `True`

## Frozen Packets

- `path_a_v3_store_authority_2026_07_13` — `tests/fixtures/path_a_v3_store_authority_2026_07_13.json` — freeze `cadc430` — 8 cases
- `path_a_v3_provenance_disjointness_2026_07_13` — `tests/fixtures/path_a_v3_provenance_disjointness_2026_07_13.json` — freeze `fb30c2c` — 3 cases
- `path_a_v3_authority_roots_2026_07_14` — `tests/fixtures/path_a_v3_authority_roots_2026_07_14.json` — freeze `40ff5eb` — 6 cases

## Per-Case Results

### `path_a_v3_ra1_cross_owner_without_consent`

- Class: `retirement_authority_negative`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `target_retirement_unauthorized`
- Actual alarm: `target_retirement_unauthorized`
- Resulting tier: `None`
- Matched expected: `True`
- Reasons: `target_retirement_unauthorized`
- Receipts: `{"authority_path": "authenticated_without_target_authority"}`

### `path_a_v3_ra2_source_writer_self_authorizes`

- Class: `retirement_authority_negative`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `target_retirement_unauthorized`
- Actual alarm: `target_retirement_unauthorized`
- Resulting tier: `None`
- Matched expected: `True`
- Reasons: `target_retirement_unauthorized`
- Receipts: `{"authority_path": "authenticated_without_target_authority"}`

### `path_a_v3_ra3_explicit_target_owner_consent`

- Class: `retirement_authority_positive_owner_consent`
- Expected allowed: `True`
- Actual allowed: `True`
- Expected alarm: `None`
- Actual alarm: `None`
- Resulting tier: `tier_1`
- Matched expected: `True`
- Reasons: `authorized relation fact may govern`
- Receipts: `{"authority_path": "target_owner_consent", "authority_receipt_id": "consent_ra3_owner_a", "declared_shared_nodes": [], "provenance_path_ids": []}`

### `path_a_v3_ra4_standing_rule_authority`

- Class: `retirement_authority_positive_standing_rule`
- Expected allowed: `True`
- Actual allowed: `True`
- Expected alarm: `None`
- Actual alarm: `None`
- Resulting tier: `tier_1`
- Matched expected: `True`
- Reasons: `authorized relation fact may govern`
- Receipts: `{"authority_path": "standing_rule", "authority_receipt_id": "standing_rule_incident_admin", "declared_shared_nodes": [], "provenance_path_ids": []}`

### `path_a_v3_pi1_tupleless_direct_promotion`

- Class: `promotion_integrity_negative`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `promotion_without_relation_fact`
- Actual alarm: `promotion_without_relation_fact`
- Resulting tier: `tier_2`
- Matched expected: `True`
- Reasons: `tier-2 claim cannot become tier-1 without an authenticated relation fact`
- Receipts: `{}`

### `path_a_v3_pi2_governing_use_bypass`

- Class: `promotion_integrity_negative`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `tier2_governing_use_blocked`
- Actual alarm: `tier2_governing_use_blocked`
- Resulting tier: `tier_2`
- Matched expected: `True`
- Reasons: `governing consumers require tier-1 plus a resolvable authorized relation fact`
- Receipts: `{}`

### `path_a_v3_pi3_authenticated_authorized_promotion`

- Class: `promotion_integrity_positive`
- Expected allowed: `True`
- Actual allowed: `True`
- Expected alarm: `None`
- Actual alarm: `None`
- Resulting tier: `tier_1`
- Matched expected: `True`
- Reasons: `authorized relation fact may govern`
- Receipts: `{"authority_path": "target_owner_consent", "authority_receipt_id": "consent_pi3_owner_a", "declared_shared_nodes": [], "provenance_path_ids": []}`

### `path_a_v3_pi4_authenticated_but_unauthorized`

- Class: `promotion_integrity_negative`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `target_retirement_unauthorized`
- Actual alarm: `target_retirement_unauthorized`
- Resulting tier: `tier_2`
- Matched expected: `True`
- Reasons: `target_retirement_unauthorized`
- Receipts: `{"authority_path": "authenticated_without_target_authority"}`

### `path_a_v3_pd1_resolvable_disjoint_paths`

- Class: `provenance_disjointness_positive`
- Expected allowed: `True`
- Actual allowed: `True`
- Expected alarm: `None`
- Actual alarm: `None`
- Resulting tier: `tier_1`
- Matched expected: `True`
- Reasons: `authorized relation fact may govern`
- Receipts: `{"authority_path": "target_owner_consent", "authority_receipt_id": "consent_pd1", "declared_shared_nodes": [], "provenance_path_ids": ["writer_path_pd1", "arbiter_path_pd1"]}`

### `path_a_v3_pd2_declared_common_cause`

- Class: `provenance_disjointness_negative`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `provenance_common_node`
- Actual alarm: `provenance_common_node`
- Resulting tier: `tier_2`
- Matched expected: `True`
- Reasons: `provenance_common_node`
- Receipts: `{"authority_path": "target_owner_consent", "authority_receipt_id": "consent_pd2", "declared_shared_nodes": ["shared_vendor_feed"], "provenance_path_ids": ["writer_path_pd2", "arbiter_path_pd2"]}`

### `path_a_v3_pd3_hidden_white_label_common_cause` (ceiling, not pass bar)

- Class: `provenance_disjointness_adversarial_ceiling`
- Expected allowed: `True`
- Actual allowed: `True`
- Expected alarm: `None`
- Actual alarm: `None`
- Resulting tier: `tier_1`
- Matched expected: `True`
- Reasons: `authorized relation fact may govern`
- Receipts: `{"authority_path": "target_owner_consent", "authority_receipt_id": "consent_pd3", "declared_shared_nodes": [], "provenance_path_ids": ["writer_path_pd3", "arbiter_path_pd3"]}`

- Ceiling note: `declared disjointness did not reveal hidden common cause`
- Actual independence: `False`

### `path_a_v3_gl1_narrow_live_standing_grant`

- Class: `grant_lifecycle_positive`
- Expected allowed: `True`
- Actual allowed: `True`
- Expected alarm: `None`
- Actual alarm: `None`
- Resulting tier: `tier_1`
- Matched expected: `True`
- Reasons: `authorized relation fact may govern`
- Receipts: `{"authority_path": "standing_grant", "authority_receipt_id": "grant_gl1", "declared_shared_nodes": [], "provenance_path_ids": [], "root_receipt_id": "root_gl1"}`

### `path_a_v3_gl2_expired_standing_grant`

- Class: `grant_lifecycle_negative_expired`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `retirement_grant_expired`
- Actual alarm: `retirement_grant_expired`
- Resulting tier: `None`
- Matched expected: `True`
- Reasons: `retirement_grant_expired`
- Receipts: `{"authority_path": "standing_grant", "authority_receipt_id": "grant_gl2", "root_receipt_id": "root_gl2"}`

### `path_a_v3_gl3_revoked_standing_grant`

- Class: `grant_lifecycle_negative_revoked`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `retirement_grant_revoked`
- Actual alarm: `retirement_grant_revoked`
- Resulting tier: `None`
- Matched expected: `True`
- Reasons: `retirement_grant_revoked`
- Receipts: `{"authority_path": "standing_grant", "authority_receipt_id": "grant_gl3", "root_receipt_id": "root_gl3_revoke"}`

### `path_a_v3_cd1_confused_deputy_retirement`

- Class: `confused_deputy_negative`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `confused_deputy_retirement`
- Actual alarm: `confused_deputy_retirement`
- Resulting tier: `None`
- Matched expected: `True`
- Reasons: `confused_deputy_retirement`
- Receipts: `{"authority_path": "standing_grant", "authority_receipt_id": "grant_cd1_reviewer_only", "root_receipt_id": "root_cd1"}`

### `path_a_v3_ar1_self_minted_authority_root`

- Class: `authority_root_negative_self_minted`
- Expected allowed: `False`
- Actual allowed: `False`
- Expected alarm: `authority_root_not_external`
- Actual alarm: `authority_root_not_external`
- Resulting tier: `None`
- Matched expected: `True`
- Reasons: `authority_root_not_external`
- Receipts: `{"authority_path": "standing_grant", "authority_receipt_id": "grant_ar1", "root_receipt_id": "root_ar1"}`

### `path_a_v3_ar2_externally_rooted_owner_action`

- Class: `authority_root_positive_external`
- Expected allowed: `True`
- Actual allowed: `True`
- Expected alarm: `None`
- Actual alarm: `None`
- Resulting tier: `tier_1`
- Matched expected: `True`
- Reasons: `authorized relation fact may govern`
- Receipts: `{"authority_path": "standing_grant", "authority_receipt_id": "grant_ar2", "declared_shared_nodes": [], "provenance_path_ids": [], "root_receipt_id": "root_ar2"}`
