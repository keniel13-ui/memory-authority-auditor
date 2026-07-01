# Audit Scope And Roadmap — 2026-06-30

Purpose: record the architecture decision after bite-testing the memory authority auditor.

## What Happened

The first conflict-detector hardening passed the known bite-test. A second held-out family also passed after structural policy-signal extraction was added.

Then a third fresh held-out family failed:

- formal tone vs casual tone
- AI final decision authority vs human-only final decisions
- final prices vs negotiable prices
- United States only vs global customer scope
- anonymized partner data sharing vs never share user data

The detector returned no findings on that third family. That exposed the enumeration trap: adding a new rule family after every failure can make tests pass without creating a genuinely general contradiction detector.

## Decision

Do **not** market the current tool as "finds all conflicting instructions."

Path chosen:

- **Ship scope:** known dangerous-pattern authority auditor.
- **Moat path:** future semantic contradiction layer that proposes `(subject, directive, polarity, scope)` conflicts across arbitrary domains, then requires deterministic/evidence-backed confirmation.
- **Rejected path:** keep enumerating new contradiction categories until the test suite looks good.

## Current Honest Claim

The auditor separates relevance from authority, identifies covered high-risk patterns, maps governing rules, and recommends verification gates before action-capable deployment.

It does **not** prove a memory file is safe. "No findings" means no covered pattern was detected.

## Path A Architecture Sketch

Future semantic layer:

1. Extract normalized claims from each instruction:
   - subject
   - action/directive
   - polarity (`must`, `may`, `must_not`, `requires_human`, `automatic`)
   - scope/threshold
   - evidence span
2. Propose same-subject conflicts where directives are incompatible.
3. Deterministically confirm only when evidence spans support the conflict.
4. Report unresolved/low-confidence cases as "requires human review," not as detected conflicts.
5. Maintain a held-out suite of unseen domains before claiming generalization.

## Current Quality Gate

Before selling or publicly positioning this tool, keep the claim bounded:

- Good: "finds known dangerous stale/authority patterns and produces gates."
- Bad: "finds all conflicts in your agent memory."
- Bad: "proves your agent memory is safe."

