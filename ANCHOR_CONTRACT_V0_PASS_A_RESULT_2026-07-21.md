# Anchor Contract v0 — Local PASS A Result

Date: 2026-07-21
Status: LOCAL MAKER PASS A — implementation complete against frozen packet; not independently attacked and not pushed
Freeze chain: `7eab8a8` (law) -> `9a6a67e` (12-case packet)

## Result

All twelve frozen cases match.

The implementation now separates five receipts that the Imported Anchor prototype previously collapsed:

1. event occurrence;
2. resource census;
3. source/time coverage;
4. derivation-policy identity;
5. derived semantic surface identity.

Two distinct observation routes in AC-1 carry different event IDs, sources, observers, and receipt chains yet converge on:

```text
surface:v0:sha256:5bfd2c56650319aa29a2657ecd04aa19e2eae44184cd14f27fcf0ce152f37d78
```

Their provenance remains separate in `supporting_event_receipt_ids`. The semantic key does not contain route or receipt identity.

## What is now enforced

- Canonical semantic payload with exactly six identity fields.
- RFC 8785-compatible canonical JSON for the frozen v0 profile.
- SHA-256 event, census, policy, and surface receipts.
- Relation and direction participate in identity.
- Event/provenance fields do not participate in semantic identity.
- Identical replay collapses; conflicting payload under one source/event ID fails.
- `event_time` and `observed_time` remain distinct.
- Event and observation must remain inside the declared coverage window.
- Pre-local-ledger events can derive only when foreign coverage includes them.
- Census digest is validated before target selection.
- Duplicate or ambiguous census identities fail loud.
- Source-local aliases without mapping receipts stay `resource_identity_unresolved`.
- A foreign label cannot override producer provenance.
- Missing `observed_time` is a schema failure, not zero-latency observation.
- Event type must be admitted by the bound policy.
- Event subject must equal the payload resource identity.
- Policy, census, and coverage receipts must bind the same authority namespace.
- Coverage cursors must form a valid forward interval.
- Census observation time must fall inside the coverage window.

## Frozen case outcomes

| Case | Outcome |
|---|---|
| AC-1 | Two routes -> one semantic key, two supporting receipts |
| AC-2 | `resource_identity_unresolved` |
| AC-3 | `supersedes` and `narrows_scope` produce different keys |
| AC-4 | Identical replay collapses once |
| AC-5 | `event_identity_conflict` |
| AC-6 | Two-hour delivery delay preserved; derivation allowed |
| AC-7 | Pre-ledger surface recovered without historical-completeness claim |
| AC-8 | `ambiguous_census_target` |
| AC-9 | `coverage_integrity_failure` |
| AC-10 | `census_integrity_failure` before target selection |
| AC-11 | `producer_provenance_failure` |
| AC-12 | `event_receipt_schema_failure` for missing `observed_time` |

## Verification

- Focused Anchor Contract tests: 13 passed.
- Full repository: 60 passed, 1 expected xfail.
- No case-ID branching in the implementation.
- Frozen preregistration and fixture were not edited by implementation.
- Imported Anchor, considered-set, and silent-omission behavior remains green.

## Honest boundary

This is a deterministic contract proof, not a production attestation system.

- Python canonicalization is restricted to the frozen v0 JSON profile; floating-point payloads are rejected rather than pretending full numeric JCS support.
- Digests detect mutation but do not authenticate the producer.
- `outside_proposer_process: true` is still a fixture assertion, not a verified signature.
- Coverage receipts bound a named source/window; they do not prove the world is complete.
- Resource alias success is deliberately unimplemented until a mapping-receipt law is frozen.
- No connector or real external ledger has been replayed.
- No relation-store mutation occurs.
- No public result is authorized.

The important advance is narrower and real: two sufficiently identified routes can now converge on one authority-surface identity without sharing fixture IDs, and every missing prerequisite stays loud instead of being rounded into confidence.

## Maker coherence hardening after first PASS

A local cross-receipt attack found five seams not exercised by the twelve headline cases: unapproved event types, subject/payload disagreement, namespace disagreement across receipts, reversed cursor intervals, and census observations outside coverage. All five originally derived or advanced too far. The implementation now blocks each with a focused regression. The frozen law and fixture remain unchanged; this is implementation hardening inside their existing receipt-coherence requirements.
