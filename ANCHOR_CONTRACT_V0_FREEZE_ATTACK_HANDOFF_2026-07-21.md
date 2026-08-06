# Anchor Contract v0 — Freeze Attack Handoff

Date: 2026-07-21
Requested seat: Grok/Aethar PHASE 37, read-only attack on the law and frozen packet before implementation
Target chain: `98a8f1c` -> `7eab8a8` (preregistration) -> `9a6a67e` (12-case fixture)
Push state: Contract commits local only; `origin/main` remains `98a8f1c`

## Candidate fingerprints

- `PATH_A_V3_PREREGISTRATION_ANCHOR_CONTRACT_V0_2026-07-21.md`: `7219232ea6cce83f264200dcc6130959bd567fa14a9134685c4941167bdb72ec`
- `tests/fixtures/path_a_v3_anchor_contract_v0_2026_07_21.json`: `d1e1b5dd24ed04ffd60f4f0684fb2e6e9a148c26b1f13052b21cee7b3da5303e`

## What is frozen

Five contract objects:

1. Event receipt
2. Census receipt
3. Coverage receipt
4. Derivation-policy receipt
5. Derived-surface receipt with canonical `surface_key`

One event type and one derivation policy only. Twelve cases cover cross-source convergence, unresolved aliases, relation-sensitive identity, replay, event-ID conflict, late observation, birth-date recovery, ambiguous census, missing coverage, census tamper, foreign-label costume, and missing `observed_time`.

No implementation exists. Do not grade code.

## Required attacks

1. Recompute every declared digest and both literal semantic keys independently. Use RFC 8785-compatible canonicalization for these string-only payloads, not the fixture's canonical string as the hash input by assumption.
2. Verify AC-1's two routes differ in provenance but converge only because all six semantic fields match.
3. Mutate each included semantic field individually—schema, namespace, kind, source, target, relation—and confirm the contract requires a different key.
4. Mutate excluded provenance fields—event ID/source/time/observer/receipt/policy/reason—and confirm the law requires the key to remain stable.
5. Attack directionality: swapping source and target must change the key.
6. Attack resource identity: determine whether AC-2 honestly names the need for a mapping receipt or accidentally permits source-local aliases into canonical identity.
7. Attack validation order. Each negative case must be otherwise valid enough to reach its named failure rather than failing earlier on an unrelated missing schema field.
8. Attack replay and ID collision against the repaired PASS A floor; the contract must not weaken `98a8f1c`.
9. Attack time: event time versus observed time, negative delay, late delivery, event outside coverage, and pre-ledger recovery. Name any missing frozen case or rule that implementation could exploit.
10. Attack coverage: missing receipt versus observed-empty window, cursor/window contradictions, and whether `coverage_claim` overstates completeness.
11. Attack census integrity: digest before target selection, multiple live targets, resource ordering, duplicate resource IDs, and alias conflicts.
12. Attack provenance: label-only foreign costume must fail, while the prereg must not overclaim that v0 proves external honesty or independence.
13. Confirm `surface_key_collision` is specified even though SHA-256 collision is not expected in the frozen cases.
14. Confirm no fixture ID, route ID, case ID, or receipt ID leaks into canonical semantic identity.
15. Confirm the packet stays bounded: no generalized connector, no new event family, no store mutation, no public claim.

## Independent recompute anchors

Expected base semantic payload:

```json
{"authority_namespace":"tenant.demo/compliance.export_approval","kind":"authority_change_candidate","relation_type":"supersedes","schema":"authority_surface/v0","source_resource_id":"record:new-ac1","target_resource_id":"record:old-ac1"}
```

Expected base key:

```text
surface:v0:sha256:5bfd2c56650319aa29a2657ecd04aa19e2eae44184cd14f27fcf0ce152f37d78
```

Expected relation mutation (`narrows_scope`) key:

```text
surface:v0:sha256:ef36ff3d3db6c5b124826fb6a98fe615aafa4a4649e15b08cf07e6a066af259f
```

## Return format

- PASS or BLOCKING
- Exact blockers separated from optional hardening
- State whether prereg, fixture, or both must change
- If blocking, give the smallest truthful freeze repair; do not implement it
- If PASS, authorize push of `7eab8a8..9a6a67e` and hand implementation back to Kairos

Do not edit the candidate. George remains interrupt priority if client materials arrive.
