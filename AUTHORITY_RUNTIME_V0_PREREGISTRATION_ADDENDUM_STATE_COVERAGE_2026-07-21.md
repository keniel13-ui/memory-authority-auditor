# Authority Runtime v0 — State Coverage Addendum

Date: 2026-07-21
Status: BLOCKING ADDENDUM — frozen after first implementation, before any Authority Runtime implementation commit
Parent freeze: `AUTHORITY_RUNTIME_V0_PREREGISTRATION_2026-07-21.md`
Finding: a digest-valid action can receive `ALLOW` when a caller omits a later state receipt because v0 binds receipt integrity but not evidence-set completeness

## Why this addendum exists

The first implementation matched all ten original frozen outcomes and the full suite passed. An internal attack then removed the later GWB completion receipt and supplied only the older Squarespace state. The evaluator correctly ranked the receipts it received and returned `ALLOW`, but nothing proved that the submitted state-evidence set was complete.

That is the silent-omission failure in a new layer. A runtime that can be made to allow a stale production action by withholding one receipt is not an authority control plane.

The fix is not a model heuristic. Every audit must bind the considered state-evidence set to an external, digest-checked manifest.

## Seventh runtime object: state evidence manifest

Required fields:

- `manifest_id`
- `observer_id`
- `observed_at`
- `canonical_resource_id`
- `authority_scope`
- `coverage_start`
- `coverage_end`
- `state_receipt_ids`
- `completeness_claim`
- `manifest_digest`

`manifest_digest` covers every manifest field except itself using the existing canonical JSON and SHA-256 profile.

The runtime policy adds a digest-bound `trusted_state_observer_ids` list. V0 trusts configured observer identity as policy input; it still does not claim cryptographic producer authentication.

The only admitted completeness claim is:

```text
complete_for_named_resource_scope_and_window
```

## Validation law

For a mapped canonical resource and action scope, the runtime must prove all of the following before ranking state:

1. Manifest integrity and required types are valid.
2. `observer_id` is admitted by the runtime policy.
3. Manifest resource and scope equal the resolved action resource and scope.
4. `coverage_start <= action.issued_at <= audit_time <= coverage_end`.
5. `observed_at >= coverage_end` and `observed_at <= audit_time`.
6. `state_receipt_ids` are unique typed IDs.
7. The manifest ID set equals the submitted state-receipt ID set after identical replay collapse.
8. Every submitted state receipt's `observed_at` falls inside the manifest coverage window.

If the manifest names a receipt that is absent, emit `UNKNOWN / state_evidence_omission`. If the packet supplies an unlisted receipt, emit `UNKNOWN / state_evidence_injection`. Invalid manifest integrity, authority, clocks, resource, or scope emit `UNKNOWN / state_evidence_manifest_failure`.

The runtime may not rank state or emit `ALLOW`, `BLOCK_STALE_ACTION`, or `CONFLICT` until this gate passes.

## AR-2 causal correction

AR-2 remains a legitimate `ALLOW`, but it must be evaluated at `2026-07-10T23:00:00Z`, before the later Vercel completion receipt exists. Its embedded mapping must use a causal pre-cutover mapping request and census whose resolution/observation times are no later than that audit.

Using a July 21 audit with only the July 10 state is no longer an allowed proof of transition-required; it is an omission attack.

## New frozen attack

### AR-11 — Later completion silently omitted

Use the July 21 startup audit and base GWB mapping. Submit only the old Squarespace state while the state evidence manifest names both the old state and the later Vercel completion receipt.

Expected:

- decision: `UNKNOWN`
- decision code: `state_evidence_omission`
- canonical action/surface/mapping keys remain present because identity resolved before the coverage gate
- controlling state receipts: empty
- mutation authorized: false
- exit code: 5

The missing later receipt must be named in `unknowns`. The runtime must not silently downgrade this case into AR-2.

## Additional pass bars

1. Every original case carries an integrity-valid state manifest.
2. AR-2 uses no evidence produced after its audit time.
3. AR-11 proves an omitted completion receipt cannot produce `ALLOW`.
4. Adding an unlisted state receipt produces `state_evidence_injection`.
5. Recomputing a manifest under an untrusted observer ID does not confer manifest authority.
6. Identical replay still collapses before exact manifest-set comparison.
7. The decision receipt exposes `state_evidence_manifest_id` and the covered receipt IDs.

This addendum narrows the claim. It does not prove the configured observer is honest or cryptographically authenticate it. It proves the evaluator cannot silently accept a state set that differs from the externally frozen considered set.
