# Path A v3 Carve-Out C0 Pre-Regate

Run ID: `20260713T034423Z`
Pre-registration addendum: `PATH_A_V3_PREREGISTRATION_ADDENDUM_CARVEOUT_2026-07-12.md` (freeze `b1d44f9`)
Fixture additions: `tests/fixtures/path_a_authority_change_v3_carveout_additions_2026_07_12.json` (commit `48507de`)

No model calls were made. No carve-out implementation exists in this run. The two frozen `c0_frozen_proposal` objects were run directly against the unchanged v2 confirmer.

| Case | Class | Prediction | v2 gate confirmed | Held |
| --- | --- | --- | --- | --- |
| `path_a_v3_carveout_export_approval_eu` | partial_supersession_negative | C0-1 | CONFIRMED | yes |
| `path_a_v3_universal_approval_all_regions` | universal_scope_positive_control | C0-2 | CONFIRMED | yes |

## Separate C0 Results

- EU-only bounded negative admitted: `yes`
- Universal all-regions positive admitted: `yes`

## Boundary

C0 only: zero model calls and no carve-out implementation. The two frozen c0_frozen_proposal objects were run directly against the unchanged v2 confirmer. Results are reported separately so the bounded negative and universal positive cannot be averaged together.
