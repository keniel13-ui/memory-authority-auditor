# Path A v3 PASS 0 Pre-Regate

Run ID: `20260713T020447Z`
Pre-registration: `PATH_A_V3_PREREGISTRATION_2026-07-12.md` (freeze `27fe726`)
Fixture: `tests/fixtures/path_a_authority_change_v3_2026_07_12.json` (commit `f4cb6fb`)

No model calls were made. The five frozen adversarial proposals were run directly against the frozen v2 confirmer (all clauses, relation-span required).

| Case | Class | Prediction | Predicted | v2 gate confirmed | Held |
| --- | --- | --- | --- | --- | --- |
| `path_a_v3_negation_trap_export_approval` | negation_trap_negative | P0-1 | confirm | CONFIRMED | yes |
| `path_a_v3_negation_trap_guest_badge` | negation_trap_negative | P0-1 | confirm | CONFIRMED | yes |
| `path_a_v3_direction_trap_privacy_rule` | direction_trap_negative | P0-2 | confirm | CONFIRMED | yes |
| `path_a_v3_direction_trap_escalation_rule` | direction_trap_negative | P0-2 | confirm | CONFIRMED | yes |
| `path_a_v3_hollow_anchor_retention_purge` | hollow_anchor_negative | P0-3 | confirm | CONFIRMED | yes |

Summary: 5/5 adversarial proposals confirmed by the published v2 gate; 5/5 frozen predictions held.

## Boundary

PASS 0 only: zero model calls. Frozen adversarial proposals run directly against the frozen v2 confirmer. Proposer-independent by design; says nothing about whether a proposer would emit these lies unprompted.
