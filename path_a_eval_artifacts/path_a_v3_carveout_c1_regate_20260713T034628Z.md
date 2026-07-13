# Path A v3 Carve-Out C1 Re-Gate

Run ID: `20260713T034628Z`
Pre-registration addendum: `PATH_A_V3_PREREGISTRATION_ADDENDUM_CARVEOUT_2026-07-12.md` (freeze `b1d44f9`)
Fixture additions: `tests/fixtures/path_a_authority_change_v3_carveout_additions_2026_07_12.json` (commit `48507de`)
C0 baseline commit: `78d66a3`

The same two frozen `c0_frozen_proposal` objects were run after the carve-out defense. The fixture and predictions were not changed after C0.

| Case | Class | Expected after patch | Confirmed after patch | Held |
| --- | --- | --- | --- | --- |
| `path_a_v3_carveout_export_approval_eu` | partial_supersession_negative | BLOCK | BLOCKED | yes |
| `path_a_v3_universal_approval_all_regions` | universal_scope_positive_control | CONFIRM | CONFIRMED | yes |

## Separate C1 Results

- EU-only bounded negative blocked: `yes`
- Universal all-regions positive admitted: `yes`

## Boundary

C1 only: the same two frozen c0_frozen_proposal objects are run after the carve-out defense. No fixture or prediction was changed after observing C0.
