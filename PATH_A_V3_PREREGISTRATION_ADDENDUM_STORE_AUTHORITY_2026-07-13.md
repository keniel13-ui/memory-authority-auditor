# Path A v3 — Addendum: Two-Sided Retirement Authority and Tier-Promotion Integrity

Date: 2026-07-13
Status: FROZEN ADDITIONS-ONLY PRE-REGISTRATION
Parent freeze: `PATH_A_V3_PREREGISTRATION_2026-07-12.md` at `27fe726`
Prior carve-out loop: addendum `b1d44f9`, fixtures `48507de`, C0 `78d66a3`, C1/guard `1735134`
Authorship: Sol, adversary/falsification lane

This addendum is frozen before any store-authority fixture is authored, before any tier-store or promotion-path implementation exists, and before any result is run. It does not modify the parent freeze, prior fixtures, or prior artifacts.

## Why this addendum exists

Two public replies on the v2 article exposed separate store-side seams after the read-time carve-out loop closed.

1. **Dipankar Sarkar (`2026-07-13T04:48:50Z`) — two-sided retirement authority.** Permission to write a new record does not imply permission to retire the target record. In a multi-agent store, a writer can name a real record it does not own. Pointer resolution and source-writer authorization are necessary, but a supersession edge also needs authority over the record being retired: explicit target-owner consent or a standing rule that grants retirement authority over that target/scope.
2. **Mike Czerwinski / DEV `jugeni` (`2026-07-13T08:09:14Z`) — promotion laundering.** Correctly placing a prose-derived claim in tier 2 is not enough. The attack surface is any later transition or governing use that treats the claim as tier 1 even though no authenticated write-time relation fact was minted. The tier distinction must hold at storage, promotion, reload, and consumption, not only at initial classification.

## Current-code absence receipt

At public commit `1735134`, the repo contains a read-time semantic confirmer and the narrow bounded-customer carve-out guard. It does **not** contain a tier-1/tier-2 relation store, a retirement ACL, target-owner consent, a standing-rule authority resolver, a promotion path, or a governing-use alarm. Therefore there is no honest current-code C0 execution for these store-side cases. The first run occurs only after a minimal implementation exists; absence is recorded here rather than dressed as a numeric baseline.

## Frozen minimal object contract

The implementation may choose its own file and function names, but the fixture must represent these facts explicitly:

- **Memory record:** stable `record_id`, `owner_id`, and `scope`.
- **Tier-2 relation claim:** `claim_id`, `source_record_id`, `target_record_id`, `relation_type`, `asserted_by`, and `from_span`; it is evidence for review and never governing by itself.
- **Tier-1 relation fact:** stable `relation_id`, the same source/target/type principals, `asserted_by`, `authenticated_by`, `authenticated_at`, and an `authority_basis` that resolves either to target-owner consent or to a standing rule covering the target and relation scope.
- **Promotion or governing-use request:** identifies the claim/fact being promoted or consumed and the requested trust tier/use. Tier 1 requires a resolvable relation fact; a tier-2 claim alone cannot authorize governing use.

Field names may differ, but omitting any equivalent fact fails the relevant bar. A prose span or a writer's self-assertion is not an authority basis.

## Frozen fixture: exactly eight cases

### Family A — retirement authority

1. **RA-1 Cross-owner retirement without consent (negative).** Agent B is allowed to create/write source record X and names existing target Y owned by Agent A. B has no target-owner consent and no standing rule allowing retirement of Y. Proposed `X supersedes Y` tier-1 fact must be blocked and alarmed.
2. **RA-2 Source-writer self-authorization (negative).** Same shape, but B supplies itself as `retirement_authorized_by` or equivalent. B does not own Y and cannot mint its own permission. Must be blocked and alarmed.
3. **RA-3 Explicit target-owner consent (positive).** A verifiable consent record from Y's owner authorizes the exact retirement edge (or target plus relation/scope) before the relation fact is minted. Tier-1 fact may pass.
4. **RA-4 Standing-rule retirement authority (positive).** A resolvable standing rule grants B's role authority to retire records in Y's scope, and B holds that role. Tier-1 fact may pass.

### Family B — promotion integrity

5. **PI-1 Tuple-less direct promotion (negative).** A tier-2 prose claim exists with a valid span but no relation fact. A request attempts to relabel/promote it to tier 1. Must be blocked and alarmed.
6. **PI-2 Governing-use bypass (negative).** The stored object still says tier 2, but a downstream consumer requests or treats it as governing. No explicit relabel occurs. Must be blocked and alarmed; preserving the label while permitting tier-1 behavior fails.
7. **PI-3 Authenticated adjudication promotion (positive).** Review of the tier-2 claim mints a relation fact with provenance plus valid authority over the target. Promotion to tier 1 may pass, while retaining a link to the originating claim/span.
8. **PI-4 Authenticated reviewer but unauthorized target retirement (negative).** A reviewer is allowed to adjudicate and mint ordinary relations, but no target-owner consent or standing rule authorizes retirement of Y. Authentication alone must not launder RA-1 into tier 1. Must be blocked and alarmed.

## Frozen predictions

- A gate checking only `source writer authorized` plus `target pointer resolves` will wrongly admit RA-1 and RA-2.
- A gate accepting an authenticated reviewer without checking target-retirement authority will wrongly admit PI-4.
- A two-tier split enforced only when the claim is first written will fail PI-2 even if it blocks PI-1.
- A correct minimal implementation can pass RA-3, RA-4, and PI-3 without admitting any negative case.

## Frozen pass bars

The store-side implementation passes only if every bar holds:

1. **SA-1 Cross-owner retirement blocked:** RA-1 and RA-2 both block and emit a machine-readable alarm/reason equivalent to `target_retirement_unauthorized`.
2. **SA-2 Legitimate authority survives:** RA-3 and RA-4 both reach tier 1. The target-owner-consent and standing-rule paths are reported separately and may not be averaged.
3. **SA-3 Tuple-less promotion blocked:** PI-1 blocks and emits a machine-readable alarm/reason equivalent to `promotion_without_relation_fact`.
4. **SA-4 Governing-use invariant:** PI-2 blocks even though the stored label was never changed. Every governing consumer must require tier 1 plus a resolvable authorized relation fact.
5. **SA-5 Authenticated promotion survives:** PI-3 reaches tier 1 and preserves provenance back to the originating tier-2 claim/span.
6. **SA-6 Authentication cannot replace target authority:** PI-4 blocks. `authenticated_by` and permission to adjudicate do not imply permission to retire the target.
7. **SA-7 No silent failure:** every blocked negative produces an explicit structured reason/alarm. Returning false with no inspectable cause fails.
8. **SA-8 Existing evidence preserved:** all prior semantic-confirmer, proposer, and conflict-detector tests continue to pass; prior fixture files and artifacts remain unchanged.

Results must be reported per case and per authority path. A single aggregate score is insufficient.

## Run sequence

1. Commit and publish this addendum.
2. Author and publish the eight frozen fixture cases in a separate commit.
3. Kairos implements the minimum store/authority/promotion surface without changing the addendum or fixture.
4. Run zero-model PASS A against all eight cases and the existing regression suite.
5. A vessel that did not implement the defense independently recomputes the results from the frozen fixture and raw output before any public number ships.

## Boundaries and residue

- These are synthetic, English-labeled, single-process authorization cases. They are not external validation or a client safety claim.
- Authorization is not truth. Owner consent or a standing rule proves that a retirement edge was authorized under the represented policy; it does not prove the policy decision was correct or the underlying claim was factually true.
- Not covered here: consent revocation races, delegated authority chains deeper than one standing rule, quorum/multi-signature retirement, compromised owners, colluding agents, cross-tenant isolation, distributed consistency, replay attacks, record deletion, or relation types other than supersession.
- The store-side work does not solve natural-language argument resolution. Prose-only claims remain tier 2 unless an authenticated and target-authorized relation fact is minted.
