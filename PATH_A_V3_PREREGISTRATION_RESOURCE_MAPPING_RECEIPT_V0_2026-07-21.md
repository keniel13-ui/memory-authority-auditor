# Path A v3 — Resource Mapping Receipt v0 Pre-registration

Date: 2026-07-21
Status: PRE-REGISTRATION — law and attacks defined before implementation
Prerequisite chain: `7eab8a8` -> `9a6a67e` -> `f56bf25` -> `9c6a967` (Anchor Contract v0, remote-matched)
Lane boundary: mapping freeze only. No resolver implementation, connector, external replay, relation-store mutation, or article.

## Objective

Govern the exact point where a source-local resource identifier such as `github:123` may resolve to the canonical resource `record:new-ac1` used by Anchor Contract v0.

A mapping is not true because an event asserts it, two strings look related, or an adapter carries a trusted label. Resolution requires a digest-bound assertion, an authorized issuer, exact scope, two-clock temporal validity, an unrevoked receipt, a conflict-free active set, and a canonical target bound by the current census.

Resource Mapping Receipt v0 must keep these statements separate:

1. A source namespace uses a local identifier.
2. An issuer asserted a directional mapping to a canonical identifier.
3. A grant authorized that issuer to make this class of mapping in this exact scope.
4. The assertion was valid at the subject time and still admissible at resolution time.
5. The canonical target exists in the census used by the authority derivation.
6. The resolver applied one specific receipt and preserved why it was accepted or rejected.

Only all six together authorize replacement of the source-local identifier. None may be silently inferred from another.

## Standards profile

- RFC 8785 JSON Canonicalization Scheme for assertion, grant, policy, receipt, revocation, and key payload bytes.
- SHA-256 for v0 content digests and mapping keys.
- RFC 3339 timestamps with explicit offsets; fixture timestamps use `Z`.
- Anchor Contract v0 census receipts for canonical-target binding.

V0 freezes digest integrity and configured authority provenance. It does not claim signatures, key ownership, transparency-log inclusion, or cryptographic independence.

## The six contract objects

### 1. Mapping assertion

Required fields:

- `schema`
- `mapping_kind`
- `source_namespace`
- `source_resource_id`
- `canonical_namespace`
- `canonical_resource_id`
- `authority_scope`

V0 admits only `equivalent_identity`. The assertion is directional: it authorizes source-to-canonical resolution only. It does not authorize reverse lookup, transitive closure, or semantic equivalence outside the named scope.

### 2. Mapping authority grant

Required fields:

- `grant_id`
- `grantor_id`
- `grantee_id`
- `source_namespace`
- `canonical_namespace`
- `allowed_mapping_kinds`
- `authority_scope`
- `effective_at`
- `expires_at`
- `revoked_at`
- `grant_digest`

The grantor must appear in the frozen policy's configured trust roots. The receipt issuer must equal `grantee_id`. Source namespace, canonical namespace, mapping kind, and authority scope must match exactly in v0; wildcards and prefix inference are not admitted.

The grant must be active when the mapping receipt is issued. A missing, expired, revoked, tampered, or costume grant is `mapping_authority_failure` or `mapping_grant_integrity_failure`, never a weaker warning.

### 3. Mapping receipt

Required fields:

- `receipt_id`
- `issuer_id`
- `issued_at`
- `effective_at`
- `expires_at`
- `assertion`
- `assertion_digest`
- `authority_grant_id`
- `evidence_receipt_ids`
- `receipt_digest`

`assertion_digest` covers only the canonical assertion. `receipt_digest` covers every mapping-receipt field except itself, including the full assertion and its digest. Reusing one `receipt_id` with different canonical receipt bytes is `mapping_receipt_identity_conflict`. An identical replay collapses to one receipt and remains visible in replay receipts.

Receipt validity may not begin before issuance in v0. The grant must cover `issued_at`, and the mapping's `expires_at` may not exceed the grant's `expires_at`.

### 4. Revocation receipt

Required fields:

- `revocation_id`
- `mapping_receipt_id`
- `issuer_id`
- `revoked_at`
- `authority_grant_id`
- `reason_code`
- `revocation_digest`

The revoker must be the mapping issuer or the grantor named by the supporting authority grant. A valid revocation known at or before `resolution_time` blocks use of that mapping receipt. V0 takes the conservative path: a revoked receipt is inadmissible for both new and historical resolutions unless a later contract introduces versioned supersession semantics.

### 5. Resolution request and policy

Required request fields:

- `source_namespace`
- `source_resource_id`
- `required_canonical_namespace`
- `authority_scope`
- `subject_time`
- `resolution_time`
- `direction`

Required policy fields:

- `policy_id`
- `policy_version`
- `trusted_grantor_ids`
- `allowed_mapping_kinds`
- `resolution_rule`
- `unresolved_states`
- `policy_digest`

`subject_time` is the time whose resource identity is being evaluated, normally the imported event's `event_time`. `resolution_time` is when the resolver evaluates available receipts. A mapping must be issued and effective no later than `subject_time`, unexpired at `subject_time`, and unrevoked at `resolution_time`. Both clocks remain in the resolution receipt.

### 6. Mapping resolution receipt

Required fields:

- `resolution_state`
- `mapping_key`
- `source_namespace`
- `source_resource_id`
- `canonical_namespace`
- `canonical_resource_id`
- `authority_scope`
- `subject_time`
- `resolution_time`
- `mapping_receipt_id`
- `authority_grant_id`
- `census_receipt_id`
- `duplicate_replay_receipt_ids`
- `unresolved_reasons`

The resolution receipt is diagnostic provenance. It is not part of the canonical Anchor Contract surface key. On failure, `canonical_resource_id` and `mapping_key` remain null.

## Canonical mapping identity law

The only fields included in the v0 mapping-key payload are:

```json
{
  "schema": "resource_mapping/v0",
  "mapping_kind": "equivalent_identity",
  "source_namespace": "github",
  "source_resource_id": "github:123",
  "canonical_namespace": "tenant.demo",
  "canonical_resource_id": "record:new-ac1",
  "authority_scope": "compliance.export_approval"
}
```

The key is:

```text
mapping:v0:sha256:<SHA-256(RFC8785(mapping_assertion))>
```

The key excludes receipt ID, issuer, grant ID, timestamps, evidence IDs, census receipt ID, and prose reasons. Those fields establish admissibility and provenance; including them would make identical semantic mappings diverge across valid receipts.

Changing schema, mapping kind, either namespace, either resource identifier, or authority scope must change the key. If one mapping key is ever presented with different canonical assertion bytes, emit `mapping_key_collision` and stop.

## Resolution order

V0 evaluates in this order so a later stage cannot launder an earlier failure:

1. Validate policy digest and configured trust root.
2. Validate request schema, direction, and both clocks.
3. Validate census schema, digest, namespace, scope, and canonical target set.
4. Validate mapping receipt schema, assertion digest, and receipt digest.
5. Deduplicate identical receipt replays; stop on receipt-ID conflicts.
6. Validate the named authority grant, exact authority dimensions, and issuance-time validity.
7. Validate mapping subject-time validity and resolution-time revocation state.
8. Reject alias-to-alias targets and any active conflict for the source tuple.
9. Bind the canonical target to the current census.
10. Emit one resolution receipt; only `resolved` may replace the source-local identifier.

## Frozen attack cases

### RM-1 — Authorized directional resolution

One integrity-valid mapping receipt, backed by an active exact-scope authority grant, resolves `github:123` to census-bound `record:new-ac1`. The expected mapping key is frozen and may feed Anchor Contract AC-2 only through the resolution receipt.

### RM-2 — Unauthorized issuer

The mapping receipt issuer is not the authority grant's grantee. Emit `mapping_authority_failure`; resolve nothing.

### RM-3 — Scope mismatch

The request and mapping assertion name different authority scopes. Emit `mapping_scope_failure`; do not broaden by prefix, tenant, or prose similarity.

### RM-4 — Not effective at subject time

The mapping becomes effective after the imported event's `subject_time`. Emit `mapping_not_effective`; later observation does not rewrite earlier identity.

### RM-5 — Expired at subject time

The mapping expired before `subject_time`. Emit `mapping_expired`; resolve nothing.

### RM-6 — Revoked by resolution time

A valid revocation names the mapping receipt and is known before `resolution_time`. Emit `mapping_revoked`; do not reuse the mapping for historical resolution in v0.

### RM-7 — Conflicting active targets

Two otherwise valid active receipts map the same source namespace, source resource, and authority scope to different canonical resources. Emit `mapping_conflict`; choose neither, even if one receipt is newer.

### RM-8 — Reverse inference attempt

A request tries to resolve canonical-to-source from a source-to-canonical assertion. Emit `mapping_direction_failure`; equivalence wording does not create bidirectionality.

### RM-9 — Canonical target absent from census

The mapping is otherwise valid, but the canonical resource is absent from the bound census. Emit `mapping_target_unbound`; the mapping receipt cannot mint a census principal.

### RM-10 — Tampered receipt

A receipt field changes without a matching `receipt_digest`. Emit `mapping_receipt_integrity_failure` before authority or target selection.

### RM-11 — Identical receipt replay

The exact same mapping receipt appears twice. One mapping remains, one duplicate replay is recorded, and resolution succeeds once.

### RM-12 — Receipt ID conflict

The same `receipt_id` carries different canonical bytes. Emit `mapping_receipt_identity_conflict`; resolve nothing.

### RM-13 — Alias chain or cycle

A candidate maps the source alias to another source-local alias, including a two-receipt cycle. Emit `mapping_target_not_canonical`; v0 performs no recursive resolution.

### RM-14 — Grant integrity or time costume

The grant digest is invalid, the grantor is outside the configured roots, or the grant is not active at receipt issuance. Emit the matching grant integrity/authority failure before mapping resolution.

## Pass bars

1. RM-1 produces the frozen mapping key and a complete resolution receipt.
2. RM-2 and RM-14 prove authority comes from an integrity-valid exact grant, not a label.
3. RM-3 never broadens authority scope.
4. RM-4, RM-5, and RM-6 preserve subject-time and resolution-time distinctions.
5. RM-7 never picks a winner among conflicting active targets.
6. RM-8 proves mappings are directional.
7. RM-9 binds the canonical target to the current census.
8. RM-10 validates receipt integrity before semantic use.
9. RM-11 and RM-12 distinguish identical replay from identity conflict.
10. RM-13 rejects chains and cycles instead of guessing canonical identity.
11. Every failure leaves `mapping_key` and `canonical_resource_id` null.
12. No case-ID branching.
13. No mutation of the Anchor Contract fixture or law.
14. Existing Imported Anchor, Anchor Contract, considered-set, silent-omission, and full-suite behavior remains green.

## Non-claims and permanent boundaries

- V0 does not discover mappings automatically.
- V0 does not infer identity from matching names, URLs, labels, or content.
- V0 does not make `equivalent_identity` symmetric or transitive.
- V0 does not support alias chains, wildcards, scope prefixes, or probabilistic matching.
- V0 does not prove grantor key ownership or producer independence cryptographically.
- V0 does not prove a census is globally complete.
- V0 does not mutate the resource census, relation store, or source event.
- V0 does not authorize a connector, external replay, deployment, or public article.

A PASS means one source-local identifier may be replaced by one census-bound canonical identifier under a specific, digest-bound, time-bounded, unrevoked authority path. It does not mean source-local and canonical identifiers are universally interchangeable.
