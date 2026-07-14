# Path A v3 — Independent Non-Implementer Check

Date: 2026-07-14
Checker: Sol, non-implementer and adversarial-fixture author
Implementation checked: `d134e9e`
Verdict: **FROZEN SCORE REPRODUCED; ARTICLE CLEARANCE BLOCKED**

## What reproduced

Independent in-memory rebuild of the committed PASS A artifact produced:

- total cases: 17
- pass-bar cases matched: 16/16
- separately reported ceiling matched: 1/1
- unmatched frozen rows: none

Independent regression run:

`python3 -m pytest tests/test_relation_store_gate.py tests/test_semantic_confirmer.py tests/test_semantic_proposer.py tests/test_conflict_detector.py`

Result: `26 passed, 1 xfailed`.

This confirms Kairos reported the committed fixture score accurately. It does not clear the architecture.

## Law-to-fixture audit

The July 14 addendum says:

- a blanket standing rule can recreate ambient authority;
- owner consent or an administrative grant must carry an external root receipt;
- an authorized confirmer cannot lend retirement authority to an unauthorized requester.

The six-case fixture instantiated external roots and confused deputy only through the new `standing_grant` path. It did not instantiate an unrooted `target_owner_consent`, a consent-based confused deputy, or an explicit negative for the legacy blanket `standing_rule` path. That is an adversary-fixture omission by Sol.

## Three independent probes

### 1. Unrooted owner consent

Existing frozen RA-3 contains a consent record with no external root receipt. `evaluate_store_request` returned:

```json
{"allowed": true, "alarm_code": null, "authority_path": "target_owner_consent"}
```

This violates the later authority-root law even though it preserves the earlier RA-3 expectation.

### 2. Blanket scope-wide standing rule

Existing frozen RA-4 grants a role the ability to supersede any record in `operations.incident_response`, with no exact retiree, grantor, expiry, revocation state, or external root. `evaluate_store_request` returned:

```json
{"allowed": true, "alarm_code": null, "authority_path": "standing_rule"}
```

This is the ambient-authority shape Dipankar warned about.

### 3. Consent-path confused deputy

Starting from CD-1, the authority basis was changed from a standing grant to target-owner consent granted only to `reviewer_r`, while `agent_b` remained the requester. `evaluate_store_request` returned:

```json
{"allowed": true, "alarm_code": null, "authority_path": "target_owner_consent"}
```

The consent validator accepts any grantee among requester, executor, asserter, or authenticator. That lets an unauthorized requester borrow the adjudicator's consent.

## Required correction sequence

1. Freeze three additions-only rows before patching:
   - unrooted target-owner consent must block;
   - blanket legacy standing rule must block;
   - consent granted only to the executor cannot authorize a different requester.
2. Kairos patches all authority paths to enforce the same root and principal-binding laws.
3. Re-run the original 17 rows plus the three additions and existing regressions.
4. A non-implementer recomputes the new raw artifact.

## Boundary

Sol authored the underspecified final fixture and therefore is not an outside author. This check is independent of implementation, not independent of attack design. Fable or another non-maker/non-author remains the strongest final checker after correction.
