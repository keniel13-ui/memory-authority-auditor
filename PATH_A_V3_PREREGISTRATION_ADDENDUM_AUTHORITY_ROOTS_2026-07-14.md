# Path A v3 — Addendum: Grant Lifecycle, Confused Deputy, and Authority Roots

Date: 2026-07-14
Status: FROZEN ADDITIONS-ONLY PRE-REGISTRATION
Parent store-authority freeze: `cadc430`
Parent store-authority fixture: `903da11`
Authorship: Sol, adversary/falsification lane

This is the final authority-side attack packet before Kairos implements the store-authority defense. It is frozen before these fixture rows, authority-root code, grant-lifecycle code, confused-deputy code, or results exist. Prior freezes and fixtures remain byte-unchanged.

## Why this addendum exists

Dipankar Sarkar showed that RA-4's scope-wide standing rule can recreate ambient authority. The frozen positive has a role, relation type, and target scope, but no exact retiree, grantor, expiry, revocation state, or mint-time freshness check. He also named the confused-deputy path: a writer who cannot retire a target directly may try to make an authorized confirmer do it on the writer's behalf.

Mike Czerwinski pushed beneath the relation tuple. A consent or standing-rule record does not become authoritative merely because it resolves. If the same writable system can mint the record that grants its own authority, the laundering surface moved one hop. The chain must terminate in a root event the relation writer cannot forge or rewrite.

## Frozen minimal contract

- A standing grant identifies `grant_id`, `grantor_id`, `grantee_id` or role, exact target record, allowed relation type, issuance time, expiry time, and revocation state or a resolvable revocation event.
- Grant validity is checked at the relation mint time, not cached at policy-load time.
- The actor requesting retirement and the actor exercising retirement authority remain distinct principals. An authorized confirmer cannot lend its authority to an unauthorized requester.
- Owner consent or administrative grant carries a root receipt from a channel the relation writer cannot write. The fixture represents the channel and whether the root event resolves.
- A relation candidate cannot establish the authority of its own root receipt.

## Frozen fixture: exactly six cases

1. **GL-1 Narrow live standing grant (positive).** A grant from the target owner names the exact target, grantee, relation type, and unexpired window. It resolves to a valid external root event at mint time. Retirement may pass.
2. **GL-2 Expired standing grant (negative).** The same narrow grant expired before mint time. Retirement must block with a reason equivalent to `retirement_grant_expired`.
3. **GL-3 Revoked standing grant (negative).** The grant was valid when loaded but a root-channel revocation predates mint time. Retirement must block with a reason equivalent to `retirement_grant_revoked`. A cached earlier decision fails.
4. **CD-1 Confused deputy (negative).** Writer B lacks authority over A's target and asks an authorized confirmer to mint the edge on B's behalf. The confirmer's authority cannot substitute for the requester's missing authority. Must block with a reason equivalent to `confused_deputy_retirement`.
5. **AR-1 Self-minted authority root (negative).** Every record pointer resolves, but the consent or grant root was created through a channel writable by B or by the relation component itself. Must block with a reason equivalent to `authority_root_not_external`.
6. **AR-2 Externally rooted owner action (positive).** The target owner grants the exact retirement through a channel the relation writer cannot write; the root event resolves and predates mint time. Retirement may pass while preserving the root receipt.

## Frozen bars

- GL-1 and AR-2 pass through separate authority paths and preserve their root receipts.
- GL-2, GL-3, CD-1, and AR-1 all block with distinct structured reasons. They may not be averaged into a generic failure count.
- Expiry and revocation are evaluated against mint time on every request.
- Authentication, pointer resolution, or confirmer authority alone cannot rescue a failing negative.
- The existing eight store-authority cases, three provenance-disjointness cases, and prior regression tests remain unchanged.

## Sequence

1. Publish this addendum.
2. Sol authors and publishes the six frozen fixture rows without implementing or running the defense.
3. Kairos implements the complete frozen store-authority surface.
4. Kairos runs per-case PASS A plus existing regressions.
5. A non-implementing vessel independently recomputes the raw output before any public result or article ships.

## Boundary

An externally rooted action proves that the represented authority event came through a channel outside the relation writer's write power. It does not prove the human was wise, uncompromised, or uncoerced. Hardware compromise, stolen credentials, root-channel compromise, quorum authority, distributed revocation races, and delegated chains deeper than one grant remain outside this fixture.
