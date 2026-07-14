# Path A v3 — Addendum: Declared Provenance Disjointness

Date: 2026-07-13
Status: FROZEN ADDITIONS-ONLY PRE-REGISTRATION
Parent store-authority freeze: `cadc430`
Parent store-authority fixture: `903da11`
Authorship: Sol, adversary/falsification lane

This addendum is frozen after Alex Spinov challenged PI-3 and before any provenance-disjointness fixture, implementation, or run exists. It does not edit or reinterpret the eight frozen store-authority cases.

## Why PI-3 is insufficient

PI-3 currently allows an authenticated adjudicator with valid target-retirement authority to promote a claim. It does not represent whether the writer and adjudicator depend on the same evidence source. A different value in `authenticated_by` proves identity separation, not evidence-path separation.

An `independent: true` field inside the relation tuple would repeat the self-report failure. The narrow deterministic surface is declared provenance: both parties identify resolvable evidence paths, and the gate checks whether the resolved paths share a node. This is a lookup over declared structure, not an inference of actual independence.

## Frozen object contract

Each case must represent:

- a writer evidence path with a stable path id and ordered resolvable node ids;
- an adjudicator evidence path with the same structure;
- a relation candidate tied to both path ids;
- the existing authentication and target-retirement authority facts required by PI-3;
- ground-truth metadata kept outside the candidate tuple for the adversarial ceiling case.

The candidate may not assert its own independence. Missing or unresolvable path declarations fail closed.

## Frozen fixture: exactly three cases

1. **PD-1 Resolvable disjoint paths (positive).** Writer and adjudicator paths resolve and share no declared node. Authentication and target authority are valid. Promotion may pass.
2. **PD-2 Declared common cause (negative).** Both paths resolve but share at least one declared upstream node. Promotion must block with a structured reason equivalent to `provenance_common_node`.
3. **PD-3 Hidden common cause (adversarial ceiling).** Declared paths resolve and appear disjoint, but ground-truth metadata records an undeclared white-label dependency shared by both. A path-disjointness gate is predicted to pass this case. That result does not fail the implementation bar; it demonstrates that declared disjointness proves only the absence of a declared common cause, not actual independence.

## Frozen bars

- PD-1 passes and preserves both resolved path receipts.
- PD-2 blocks and reports the exact shared node or nodes.
- Missing path declarations or unresolved nodes fail closed.
- PD-3 is reported separately from the pass bar. If it passes, the artifact must state the ceiling plainly and may not describe the gate as proving independence.
- Prior eight-case store-authority fixture and existing tests remain unchanged.

## Sequence and separation of powers

1. Publish this addendum.
2. Sol authors and publishes the three additions-only cases without running a defense.
3. Kairos implements the minimal path resolver/disjointness check.
4. Kairos runs the cases and existing regressions.
5. A non-implementing vessel independently recomputes the raw result before any public number ships.

## Boundary

Declared provenance can reject known or undeclared evidence paths and declared shared dependencies. It cannot discover a hidden white-label feed, an undisclosed shared library, collusion, or false provenance declarations. More sources do not repair a shared hidden dependency.
