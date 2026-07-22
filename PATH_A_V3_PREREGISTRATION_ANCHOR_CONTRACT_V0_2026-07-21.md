# Path A v3 — Anchor Contract v0 Pre-registration

Date: 2026-07-21
Status: PRE-REGISTRATION — contract and attacks defined before implementation
Prerequisite chain: `b476cf3` -> `9b8af1b` -> `98a8f1c` (Imported Anchor PASS A + replay/identity repair, remote-matched)
Lane boundary: contract freeze only. No implementation, no connector, no external replay, no article.

## Objective

Prove that two observation routes can independently derive the same authority surface without sharing fixture `surface_id` values, while keeping occurrence, resource census, coverage, derivation policy, and semantic identity as separate receipts.

The contract must never collapse these statements:

1. A foreign system recorded an event.
2. The observer covered the relevant namespace and time window.
3. A resource census identified the possible principals.
4. A versioned policy allowed one semantic derivation.
5. The derived semantic surface has a canonical cross-source identity.

The first four justify the fifth. None may be silently inferred from another.

## Standards profile

Anchor Contract v0 adopts existing infrastructure conventions where they are sufficient:

- CloudEvents 1.0-shaped event envelope: `specversion`, `id`, `source`, `type`, `subject`, time, content type, and data.
- OpenTelemetry time distinction: `event_time` is when the source says the event occurred; `observed_time` is when the importing observer received it.
- RFC 8785 JSON Canonicalization Scheme for canonical semantic payload bytes.
- SHA-256 for v0 content digests and semantic surface keys.

Sigstore/in-toto-style signed bundles and transparency-log inclusion are a later authenticity layer. V0 freezes digest integrity and provenance boundaries without claiming cryptographic producer identity.

## The five contract objects

### 1. Event receipt

Required fields:

- `specversion`
- `id`
- `source`
- `type`
- `subject`
- `event_time`
- `observed_time`
- `datacontenttype`
- `data`
- `data_digest`
- `producer_identity`

`data_digest` is SHA-256 over RFC 8785 canonical bytes of `data`. Reusing one event ID with a different canonical payload is `event_identity_conflict`. Identical replay collapses to one event receipt and remains visible in replay receipts.

### 2. Census receipt

Required fields:

- `receipt_id`
- `observer_id`
- `observed_at`
- `authority_namespace`
- `resources`
- `resource_aliases`
- `census_digest`

`census_digest` covers the canonical census payload (`authority_namespace` + ordered resource records). A digest mismatch is `census_integrity_failure` before derivation. Resource aliases do not become canonical merely because a source asserts them; an alias requires a receipted mapping or remains `resource_identity_unresolved`.

### 3. Coverage receipt

Required fields:

- `receipt_id`
- `observer_id`
- `authority_namespace`
- `coverage_start`
- `coverage_end`
- `local_ledger_started_at`
- `cursor_start`
- `cursor_end`
- `receipt_present`
- `coverage_claim`

Coverage is bounded to the named namespace and window. It is never a universal completeness claim. A missing required receipt is `coverage_integrity_failure`, not an empty expected-set. An event before local-ledger birth may still derive when the foreign coverage window includes it.

### 4. Derivation policy receipt

Required fields:

- `policy_id`
- `policy_version`
- `input_event_types`
- `authority_namespace`
- `rule`
- `unresolved_states`
- `policy_digest`

V0 supports one policy only: `same_scope_live_record_requires_authority_change_candidate`. A `record_write` plus exactly one other live same-scope canonical resource may derive `authority_change_candidate(source=written, target=live, relation=supersedes)`. Zero targets, multiple targets, unresolved aliases, missing scope, and integrity failures never guess.

### 5. Derived surface receipt

Required fields:

- `surface_key`
- `surface_payload`
- `supporting_event_receipt_ids`
- `census_receipt_id`
- `coverage_receipt_id`
- `policy_id`
- `policy_version`
- `derivation_state`
- `unresolved_reasons`

`surface_key` identifies semantics. Supporting receipt IDs preserve provenance and may differ across routes.

## Canonical surface identity law

The only fields included in the v0 semantic payload are:

```json
{
  "schema": "authority_surface/v0",
  "authority_namespace": "...",
  "kind": "authority_change_candidate",
  "source_resource_id": "...",
  "target_resource_id": "...",
  "relation_type": "supersedes"
}
```

The key is:

```text
surface:v0:sha256:<SHA-256(RFC8785(surface_payload))>
```

The key excludes event ID, event source, observer, timestamps, receipt IDs, policy ID, and prose reasons. Those fields explain derivation; including them would prevent cross-source convergence.

Changing semantic direction, resource identity, relation type, authority namespace, kind, or schema version must change the key. If the same key is ever presented with different canonical bytes, emit `surface_key_collision` and stop.

## Frozen attack cases

### AC-1 — Two systems, one semantic surface

Two foreign routes use different event/receipt IDs but resolve the same canonical resources, namespace, and relation. Both must emit the exact same `surface_key` while preserving distinct supporting receipts.

### AC-2 — Resource alias is not canonical identity

One route calls the new record `github:123`; the census knows `record:new-ac1`, but no receipted alias mapping exists. The contract must emit `resource_identity_unresolved`, not hash the source-local alias as if cross-system identity were solved.

### AC-3 — Same principals, different relation

Two semantic payloads share namespace, source, and target but differ only in relation (`supersedes` vs `narrows_scope`). Keys must differ.

### AC-4 — Identical event replay

An identical event receipt appears twice. One event and one derived surface remain; replay count is one.

### AC-5 — Event ID collision with different payload

The same source and event ID carry two individually well-formed but different payloads. Fail `event_identity_conflict`; derive nothing.

### AC-6 — Late delivery preserves both clocks

An event occurs two hours before it is observed but remains inside declared coverage. Derivation may proceed; the receipt must preserve both times and report delivery delay. Observed time must never overwrite event time.

### AC-7 — Birth-date recovery

Foreign event time predates the local-ledger birth date and falls inside the foreign coverage window. The route derives and marks `pre_local_ledger_birth: true`; it does not claim complete earlier history.

### AC-8 — Ambiguous census

Two live same-scope targets exist. Emit `ambiguous_census_target`; derive nothing.

### AC-9 — Missing coverage receipt

Policy required a coverage receipt, but it is absent. Emit `coverage_integrity_failure`; do not interpret an empty stream.

### AC-10 — Tampered census

Census payload does not match its declared digest. Emit `census_integrity_failure` before target selection.

### AC-11 — Foreign-label costume

The event labels itself foreign, but producer identity resolves to the proposer process. Emit `producer_provenance_failure`; derive nothing. V0 does not upgrade labels into independence.

### AC-12 — Missing observed time

Event time exists but `observed_time` is absent. Emit `event_receipt_schema_failure`. This prevents unknown receipt timing from masquerading as zero-latency observation.

## Pass bars

1. AC-1 produces one shared canonical key across two distinct observation routes.
2. AC-2 keeps unresolved resource aliases outside the keyspace.
3. AC-3 proves relation semantics participate in identity.
4. AC-4 and AC-5 retain the Imported Anchor replay/identity floor.
5. AC-6 preserves both clocks and computes delay without changing event time.
6. AC-7 recovers a bounded pre-ledger surface without claiming historical completeness.
7. AC-8 never chooses between ambiguous live targets.
8. AC-9 distinguishes missing coverage from an observed-empty window.
9. AC-10 validates census integrity before semantic derivation.
10. AC-11 resolves producer provenance rather than trusting labels.
11. AC-12 requires observed receipt time.
12. No case-ID branching.
13. Existing Imported Anchor, considered-set, silent-omission, and full-suite behavior remains green.

## Non-claims and permanent boundaries

- V0 does not prove the foreign producer is honest or uncompromised.
- V0 does not prove a coverage window captured every world event.
- V0 does not solve cross-system resource aliases without a separate mapping receipt.
- V0 does not derive authority meaning from arbitrary event types.
- V0 does not sign receipts or publish them to a transparency log.
- V0 does not mutate the relation store.
- V0 does not authorize a public result or article.

A PASS means two sufficiently identified routes can converge on semantic authority identity under one explicit policy while every missing prerequisite stays loud. It does not mean imported events have become ground truth.
