# Path A — Lexical Baseline Results

Date: 2026-07-01
Baseline commit context: after frozen pre-registration `441140d` and held-out packet `123f720`, before any Path A proposer implementation.
Fixture packet: `tests/fixtures/path_a_authority_change_v0_2026_07_01.json`

## Purpose

Measure the existing deterministic lexical detector against the frozen Path A held-out packet before building the semantic proposer. Path A must beat this baseline on both misses and false positives.

## Result Summary

The lexical baseline fails the Path A task.

- It does **not** identify any of the four real semantic authority-change relations as the correct relation type.
- It false-fires `stale_instruction` on both topic-mention negative cases.
- It also emits `missing_authority_layer` on several short fixture files, which is a separate covered-pattern warning and not evidence of semantic authority-change detection.

## Per-Case Results

| Case | Expected class | Lexical findings | Baseline read |
| --- | --- | --- | --- |
| `path_a_supersession_password_rotation_v0` | supersession | `missing_authority_layer` | Missed semantic supersession |
| `path_a_scope_narrowing_export_v0` | scope narrowing | none | Missed semantic narrowing |
| `path_a_direct_contradiction_auto_reply_v0` | direct contradiction | `missing_authority_layer` | Missed semantic contradiction |
| `path_a_authority_transfer_deploy_v0` | authority transfer | `missing_authority_layer` | Missed authority transfer |
| `path_a_topic_mention_negative_old_instructions_v0` | topic mention negative | `stale_instruction`, `missing_authority_layer` | False positive on topic mention |
| `path_a_topic_mention_negative_meta_fix_v0` | topic mention negative | two `stale_instruction`, `missing_authority_layer` | False positives on meta discussion |

## Boundary

This is not a failure of the whole auditor. It is the measured boundary of the existing Path B lexical layer on the frozen Path A task. The authority map, review queue, gates, and covered-pattern warnings still have value. This result only says the current detector is not a semantic authority-change layer.

## Implication

Path A has a real baseline to beat:

1. catch confirmed semantic authority-change relations with cited evidence,
2. avoid topic-mention false positives,
3. route unconfirmed proposals to `needs_human_judgment`,
4. preserve visible uncertainty instead of returning a clean green result.
