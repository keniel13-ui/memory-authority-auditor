# Resource Mapping Receipt v0 — Local PASS A Result

Date: 2026-07-21
Status: LOCAL MAKER PASS A — frozen packet satisfied; not independently attacked and not pushed
Freeze chain: `7b279a9` (law) -> `323de27` (14-case packet) -> `7f1ccba` (RM-13 census reachability correction)

## Result

All fourteen frozen cases match.

The implementation now governs the exact point where Anchor Contract v0 previously stopped at `resource_identity_unresolved`: a source-local alias may become a canonical resource only when one directional mapping is supported by an integrity-valid receipt, an exact authority grant, valid subject/resolution clocks, no effective revocation, no active target conflict, and a canonical target already present in the bound census.

The frozen positive path resolves:

```text
github:123
  -> record:new-ac1
  -> mapping:v0:sha256:760b5c43822b288e1ada1f9425a7842ae52079ae9d0d5288baddf832590b83ef
```

Receipt, issuer, grant, time, evidence, and census identities remain outside the mapping key. They decide whether the semantic mapping is admissible; they do not change what mapping the key identifies.

## What is now enforced

- Canonical mapping assertion with exactly seven semantic fields.
- RFC 8785-compatible canonical JSON and SHA-256 under the existing v0 profile.
- Directional source-to-canonical resolution only.
- Exact source namespace, canonical namespace, mapping kind, and authority scope.
- Configured grantor root and exact issuer/grantee binding.
- Grant validity at mapping-receipt issuance.
- Mapping issuance/effectivity/expiry at `subject_time`.
- Revocation status at `resolution_time`.
- Digest validation for policy, census, assertion, mapping receipt, authority grant, and revocation.
- Identical receipt replay collapse and conflicting receipt-ID rejection.
- Active target conflict refusal; no newest-wins shortcut.
- Canonical target binding to the current census.
- Alias-chain and same-namespace cycle refusal.
- Every failure leaves `mapping_key` and `canonical_resource_id` null.

## Frozen case outcomes

| Case | Outcome |
|---|---|
| RM-1 | Authorized `github:123` -> `record:new-ac1`; frozen mapping key |
| RM-2 | `mapping_authority_failure` |
| RM-3 | `mapping_scope_failure` |
| RM-4 | `mapping_not_effective` |
| RM-5 | `mapping_expired` |
| RM-6 | `mapping_revoked` |
| RM-7 | `mapping_conflict`; neither active target chosen |
| RM-8 | `mapping_direction_failure` |
| RM-9 | `mapping_target_unbound` |
| RM-10 | `mapping_receipt_integrity_failure` |
| RM-11 | Identical receipt replay collapses once; resolution succeeds |
| RM-12 | `mapping_receipt_identity_conflict` |
| RM-13 | `mapping_target_not_canonical`; no alias chain/cycle traversal |
| RM-14 | `mapping_grant_integrity_failure` |

## Freeze correction receipt

The first implementation run exposed one packet defect rather than an implementation defect: RM-13 requested canonical namespace `github` while reusing the `tenant.demo` census. The frozen resolution order correctly stopped at `mapping_scope_failure`, so the intended alias-chain boundary was unreachable.

Commit `7f1ccba` adds an integrity-valid `github/compliance.export_approval` census for RM-13 only. The expected alarm and implementation law did not change. The correction makes the pre-registered attack reachable instead of weakening the resolver to skip census validation.

## Verification

- Frozen packet: 14/14 expected outcomes.
- Initial focused Resource Mapping tests: 8 passed.
- Initial full repository at PASS A: 68 passed, 1 expected xfail.
- Run artifact: `path_a_eval_artifacts/path_a_v3_resource_mapping_receipt_v0_pass_a_20260722T014028Z.json`.
- Base mapping key independently recomputed from the canonical assertion.
- Every embedded policy, grant, assertion, receipt, revocation, and census digest recomputed and matched.
- No case-ID branching.
- Anchor Contract preregistration and fixture remain unchanged.

## Honest boundary

This is a local deterministic mapping contract, not an identity provider or production trust service.

- Digests detect mutation; they do not authenticate grantor key ownership.
- The configured trust-root identifier is policy input, not cryptographic independence.
- Evidence receipt IDs are preserved fixture references; their real-world meaning is not proven here.
- Mapping discovery, fuzzy matching, symmetric equivalence, transitive closure, alias chains, wildcards, and probabilistic identity are intentionally absent.
- The mapping resolver does not mutate the census, relation store, source event, or Anchor Contract fixture.
- The Anchor Contract handoff now rechecks resolution state, semantic key, event/source identity, authority scope, both clocks, census receipt identity, namespace, and canonical-target membership. This is coherence validation, not cryptographic authentication.
- No connector, external replay, deployment, or public article is authorized.

The advance is exact: the system can now distinguish an authorized canonical identity resolution from an assertion wearing the shape of one, and every unresolved path stays loud.

## Maker coherence hardening after first PASS

A local post-PASS attack closed six additional seams without changing the frozen law or expected outcomes:

- assertion objects must contain exactly the typed v0 semantic fields;
- configured grantor costumes fail even when their altered grant digest is internally consistent;
- malformed revocations for unrelated receipt IDs cannot poison a valid resolution;
- multiple authorized receipts for the same semantic target become supporting receipts, not a false conflict;
- Anchor Contract no longer accepts arbitrary truthy mapping JSON;
- the Anchor bridge independently rechecks semantic-key coherence and current census membership before AC-2 may derive.

Current verification after hardening: 15 focused Resource Mapping tests; 28 combined Resource Mapping + Anchor Contract tests; 75 passed / 1 expected xfail across the full repository.
