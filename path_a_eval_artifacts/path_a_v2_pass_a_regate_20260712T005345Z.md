# Path A v2 PASS A Re-Gate

Run ID: `20260712T005345Z`
Recorded v1 artifact: `path_a_eval_artifacts/path_a_eval_20260712T003706Z.json`

No model calls were made. This applies the frozen v2 relation-span clause to the already recorded v1 findings.

## Engine Results

### anthropic

- textual direction catches before: `9/9`
- textual direction catches after relation-span: `9/9`
- textual true-positive losses: `0`
- implicit direction catches (reported lower-trust, not span-gated): `3/3`
- negative false fires before: `1`
- negative false fires after relation-span: `1`

| Case | v2 class | Confirmed before | Confirmed after | Note |
| --- | --- | ---: | ---: | --- |
| `path_a_v1_supersession_backup_retention` | textual | 1 | 1 | kept |
| `path_a_v1_supersession_api_key_rotation` | textual | 1 | 1 | kept |
| `path_a_v1_supersession_sync_notes_location` | textual | 1 | 1 | kept |
| `path_a_v1_scope_narrowing_refund_limit` | textual | 1 | 1 | kept |
| `path_a_v1_scope_narrowing_prod_db_access` | textual | 1 | 1 | kept |
| `path_a_v1_scope_narrowing_social_posting` | textual | 1 | 1 | kept |
| `path_a_v1_contradiction_logging_pii` | implicit | 1 | 0 | lower-trust implicit |
| `path_a_v1_contradiction_friday_deploys` | implicit | 1 | 1 | lower-trust implicit |
| `path_a_v1_contradiction_vendor_contact` | implicit | 1 | 0 | lower-trust implicit |
| `path_a_v1_transfer_incident_severity` | textual | 1 | 1 | kept |
| `path_a_v1_transfer_purchase_approval` | textual | 1 | 1 | kept |
| `path_a_v1_transfer_article_signoff` | textual | 1 | 1 | kept |
| `path_a_v1_topic_mention_training_workshop` | negative | 0 | 0 |  |
| `path_a_v1_topic_mention_changelog_history` | negative | 0 | 0 |  |
| `path_a_v1_topic_mention_research_abstract` | negative | 0 | 0 |  |
| `path_a_v1_restatement_export_approval` | negative | 0 | 0 |  |
| `path_a_v1_restatement_admin_2fa` | negative | 0 | 0 |  |
| `path_a_v1_coexistence_expenses_vs_talks` | negative | 0 | 0 |  |
| `path_a_v2_mention_use_changelog_archive_exporter` | negative | 0 | 0 |  |
| `path_a_v2_mention_use_meeting_minutes_vendor_access` | negative | 0 | 0 |  |
| `path_a_v2_mention_use_quoted_draft_incident_page` | negative | 0 | 0 |  |
| `path_a_v2_proximity_trap_expense_approval` | negative | 0 | 0 |  |
| `path_a_v2_proximity_trap_weekly_updates` | negative | 1 | 1 | false fire survived |

### local_llama3.2

- textual direction catches before: `4/9`
- textual direction catches after relation-span: `4/9`
- textual true-positive losses: `0`
- implicit direction catches (reported lower-trust, not span-gated): `1/3`
- negative false fires before: `5`
- negative false fires after relation-span: `1`

| Case | v2 class | Confirmed before | Confirmed after | Note |
| --- | --- | ---: | ---: | --- |
| `path_a_v1_supersession_backup_retention` | textual | 0 | 0 | miss/lost |
| `path_a_v1_supersession_api_key_rotation` | textual | 0 | 0 | miss/lost |
| `path_a_v1_supersession_sync_notes_location` | textual | 1 | 1 | kept |
| `path_a_v1_scope_narrowing_refund_limit` | textual | 1 | 1 | kept |
| `path_a_v1_scope_narrowing_prod_db_access` | textual | 0 | 0 | miss/lost |
| `path_a_v1_scope_narrowing_social_posting` | textual | 0 | 0 | miss/lost |
| `path_a_v1_contradiction_logging_pii` | implicit | 0 | 0 | lower-trust implicit |
| `path_a_v1_contradiction_friday_deploys` | implicit | 0 | 0 | lower-trust implicit |
| `path_a_v1_contradiction_vendor_contact` | implicit | 1 | 0 | lower-trust implicit |
| `path_a_v1_transfer_incident_severity` | textual | 1 | 1 | kept |
| `path_a_v1_transfer_purchase_approval` | textual | 0 | 0 | miss/lost |
| `path_a_v1_transfer_article_signoff` | textual | 1 | 1 | kept |
| `path_a_v1_topic_mention_training_workshop` | negative | 0 | 0 |  |
| `path_a_v1_topic_mention_changelog_history` | negative | 0 | 0 |  |
| `path_a_v1_topic_mention_research_abstract` | negative | 0 | 0 |  |
| `path_a_v1_restatement_export_approval` | negative | 1 | 0 | blocked by relation-span |
| `path_a_v1_restatement_admin_2fa` | negative | 1 | 0 | blocked by relation-span |
| `path_a_v1_coexistence_expenses_vs_talks` | negative | 0 | 0 |  |
| `path_a_v2_mention_use_changelog_archive_exporter` | negative | 1 | 0 | blocked by relation-span |
| `path_a_v2_mention_use_meeting_minutes_vendor_access` | negative | 0 | 0 |  |
| `path_a_v2_mention_use_quoted_draft_incident_page` | negative | 0 | 0 |  |
| `path_a_v2_proximity_trap_expense_approval` | negative | 1 | 1 | false fire survived |
| `path_a_v2_proximity_trap_weekly_updates` | negative | 1 | 0 | blocked by relation-span |

## Boundary

PASS A is a re-gate of frozen v1 artifacts. It measures the new deterministic clause only; it is not a fresh 21-case v2 model run.
