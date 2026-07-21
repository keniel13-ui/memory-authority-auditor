# Path A v3 — Imported-Anchor Diff Pre-registration

Date: 2026-07-21
Status: PRE-REGISTRATION — attack packet defined before comparator implementation
Public provenance: nexus-lab-zen proposed deriving the expected-set from a foreign-authored event stream and running it against the same cases as the fixture-supplied set. Keniel publicly committed to build the diff and identify where the imported route breaks.
Lane boundary: imported-anchor derivation and comparison only. No relation-store mutation, no model call, no article publication.

## Question under test

Can a foreign-authored event stream replace the fixture-supplied `expected_set` / `ground_truth.required_declarations` used by the considered-set and silent-omission gates?

The answer must distinguish three claims:

1. A foreign event can independently prove that something happened.
2. A deterministic policy can sometimes turn that event plus a local resource census into an authority-change surface.
3. The resulting surface can be compared with proposer declarations without importing fixture-only identity or semantic knowledge.

Success on the first claim does not imply success on the second or third.

## Frozen derivation rule

The first comparator may derive exactly one surface class:

- event kind: `record_write`
- event supplies: `record_id` and `scope`
- local census supplies: exactly one different record with the same scope and `status: live`
- configured policy: `same_scope_live_record_requires_authority_change_candidate`
- derived surface: `authority_change_candidate(source=written record, target=live same-scope record, relation=supersedes)`

The comparator must not guess when scope is absent, when no live same-scope record exists, or when more than one target exists. Those states stay unresolved.

Imported surface IDs must be minted from imported provenance (`anchor_id` + `event_id`), not copied from fixture expected-set IDs. Semantic comparison therefore uses the full surface shape, while a separate receipt records how the current considered-set gate behaves under its exact-ID rule.

## Frozen cases

### IA-1 — Foreign receipt catches the same SO-1 silence

Reuses the SO-1 record/proposer shape. A foreign record-write receipt plus the local census derives the same authority-change surface as the fixture-required declaration. Empty proposals must remain `undeclared_surface` when the derived surface is supplied to the shipped silent-omission gate.

### IA-2 — Foreign receipt reaches before the local ledger birth date

Reuses the CS-6 boundary shape, whose fixture expected-set is absent. A foreign receipt predating the declared local-ledger start identifies a write in the same scope as one live local record. The imported route must derive an authority surface and report it as imported-only. This is evidence that an imported source can recover a birth-date hole under the frozen rule; it is not proof of complete historical coverage.

### IA-3 — Same semantic surface, different identity

Reuses the authority surface in CS-1. The imported route derives the same semantic shape, and the proposer considered that shape, but their independently minted `surface_id` values differ. Semantic comparison must say aligned. The current considered-set gate, when handed the imported ID unchanged, is expected to report `hole_in_considered_set`. This freezes the cross-source identity-reconciliation break.

### IA-4 — Foreign webhook proves activity but lacks derivation fields

A foreign webhook contains a resource ID and action but no scope. The comparator must preserve the event as unresolved and must not invent a target or `supersedes` relation. This freezes the semantic-mapping break.

### IA-5 — Expected foreign receipt is missing

Policy required a foreign receipt before the proposer ran, but the receipt is absent. The comparator must report `imported_anchor_integrity_failure`, not an empty imported expected-set and not clean compliance. This freezes the delivery/coverage break.

## Pass bars

1. IA-1 derives one surface semantically equal to SO-1 ground truth and the existing silent-omission gate reports `undeclared_surface`.
2. IA-2 marks the source event as predating local-ledger birth and reports one imported-only authority surface.
3. IA-3 reports semantic alignment while preserving the current gate's exact-ID false hole as a separate receipt.
4. IA-4 reports `missing_scope`, derives zero surfaces, and never fabricates a target.
5. IA-5 reports integrity failure before interpreting an empty stream.
6. No case-ID branching is allowed.
7. Existing considered-set and silent-omission tests remain unchanged and green.

## What a PASS would and would not mean

A PASS would show that imported events can anchor occurrence and can sometimes produce a useful expected surface when an explicit derivation policy and enough census context exist.

It would not show that a foreign stream is complete, that delivery is reliable, that foreign authorship guarantees independence, that event vocabulary maps cleanly to authority semantics, or that two systems share canonical surface identity. Those are the expected breakpoints this diff is designed to name rather than conceal.
