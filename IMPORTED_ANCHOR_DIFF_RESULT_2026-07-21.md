# Imported-Anchor Diff — Where the Route Works and Where It Breaks

Date: 2026-07-21
Status: LOCAL PASS A + B1/B2 MAKER REPAIR — five frozen cases matched; Grok narrow re-check still required before push
Freeze receipt: `b476cf3`

## Answer to nexus

An imported, foreign-authored event stream is useful, but it does not replace the fixture expected-set by itself.

It can anchor **occurrence** independently: the foreign source can prove that a write, receipt, notification, or counterparty action happened even when the local ledger did not record it. Under an explicit derivation rule and with a usable local resource census, that event can become an expected authority surface and can make proposer silence loud.

The route breaks when occurrence must become meaning. A raw event normally does not name the old authority-bearing record, the intended relation, or the canonical surface identity. Those come from a derivation policy and a resource census. If either is missing or ambiguous, the honest output is unresolved—not a fabricated `supersedes` relation.

## Same-case diff

| Case | Imported result | Fixture comparison | Shipped-gate receipt | What it proves |
|---|---|---|---|---|
| IA-1 / SO-1 | Derived `new_so1 → old_so1 / supersedes` | Semantic match: 1; fixture-only: 0; imported-only: 0 | Silent omission: `undeclared_surface` | A foreign receipt plus an exact census target can replace the fixture-required declaration for this case. |
| IA-2 / CS-6 | Derived one event dated before local-ledger birth | Semantic match: 0; imported-only: 1 | Surface is missing from proposer considered-set | Imported history can expose a birth-date hole that the fixture/local ledger did not name. |
| IA-3 / CS-1 | Derived the same authority surface with an imported ID | Semantic match: 1; missing semantically: 0 | Considered-set: `hole_in_considered_set` | Current exact-ID comparison cannot reconcile independently minted surface IDs. |
| IA-4 | Preserved webhook as unresolved (`missing_scope`) | No surface fabricated | No gate invoked | Activity evidence is not enough to infer authority semantics. |
| IA-5 | `imported_anchor_integrity_failure` | Empty stream not interpreted | No gate invoked | Missing required delivery is an integrity failure, not evidence that nothing happened. |

## The exact dependency chain

```text
foreign event
  proves occurrence
      + explicit derivation policy
      + local resource census with one unambiguous live same-scope target
  produces an authority-change surface
      + semantic identity reconciliation
  can be diffed against proposer considered-set / proposals
```

The imported author owns only the first link. The current prototype supplies the middle links locally and reports each one separately.

## Breakpoints

### 1. No independent resource-usage census

The imported event says `new_so1` was written in `compliance.export_approval`. It does not, by itself, identify `old_so1` as the one live authority record it challenges. The prototype resolves that target from `records`. In the frozen fixtures that census is hand-supplied. In deployment, obtaining and validating that census remains the largest missing component.

### 2. Event vocabulary is not authority vocabulary

`record_write`, `payment.updated`, or `notification.sent` establish activity. They do not automatically mean `supersedes`, `narrows_scope`, `transfers_authority`, or even `authority_change_candidate`. This prototype supports one declared policy only: a write with exactly one other live same-scope record becomes an authority-change candidate. Missing scope, zero targets, and multiple targets all stay unresolved.

### 3. Cross-source surface identity is not canonical

The fixture calls the CS-1 surface `surf_cs1_supersession`. The imported route honestly mints `imported::anchor_processor_cs1::foreign_ev_cs1_write`. Their semantic shapes are identical. The current considered-set gate compares only `surface_id`, so it reports a hole. Production needs a canonical semantic ID scheme or semantic matching with collision controls; copying fixture IDs into the importer would hide the problem rather than solve it.

### 4. Absence from a foreign stream is not world-clean

A stream can be incomplete because of delivery loss, retention, filtering, a late subscription, or suppression. IA-5 therefore blocks before deriving an empty set when a required receipt is missing. A present receipt still proves only the events it contains, not universal completeness.

### 5. Foreign-authored is not automatically independent

This comparator checks that the producer resolves outside the proposer process and that the anchor declares independence. That is a minimum provenance gate, not cryptographic proof. Shared control, collusion, compromised webhooks, and forged receipts remain outside this PASS A.

### 6. Birth-date recovery is specific, not complete

IA-2 proves that one foreign receipt from before the local-ledger start can add one missing surface. It does not prove the foreign source predates every relevant resource or retained every historical event. The result is a recovered surface, not a complete historical census.

## Implemented boundary

- Zero model calls.
- One derivation policy.
- No store mutation.
- No relation is silently inferred from an incomplete event.
- Imported IDs remain provenance-bound rather than fixture-bound.
- Existing gates are invoked only after a derived surface exists.
- Exact duplicate event receipts collapse to one derivation and remain visible in `duplicate_replay_event_ids`.
- One `event_id` carrying conflicting payloads stops derivation with `imported_anchor_event_identity_conflict`.
- Current suite after B1/B2 repair: 47 passed, 1 expected xfail.

## Grok PHASE 35 repair receipt

Grok's bounded attack on `b476cf3 -> 9b8af1b` found two blockers before push:

1. B1: an identical replay produced two derived rows with the same `surface_id`.
2. B2: one reused `event_id` could produce two different semantic surfaces under the same `surface_id`.

The narrow repair pre-scans event identity before any derivation. Identical event payloads sharing an ID are collapsed and counted as replay. Conflicting payloads sharing an ID invalidate the imported stream for that case; no partial surface set is emitted. Two regressions lock both paths. This is the PASS A event-identity floor, not the future canonical semantic `surface_key` promised for Anchor Contract v0.

## Smallest defensible next implementation

Do not broaden event types yet. First define a canonical semantic surface identity contract and add census receipts that state who observed each live record, at what time, and with what coverage window. Then rerun IA-1 through IA-5 with the fixture surface IDs removed entirely. That is the next test of whether the imported route is becoming deployable instead of merely fixture-compatible.
