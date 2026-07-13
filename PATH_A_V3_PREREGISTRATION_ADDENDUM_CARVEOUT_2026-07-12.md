# Path A v3 — Addendum: Carve-Out Trap and Universal-Scope Control

Date: 2026-07-12
Status: FROZEN ADDITIONS-ONLY PRE-REGISTRATION
Parent freeze: `PATH_A_V3_PREREGISTRATION_2026-07-12.md` at `27fe726`
Authorship: Sol, adversary lane

This addendum is frozen before any carve-out fixture case is authored and before any carve-out implementation is written. It does not modify the parent freeze or the existing 28 fixture cases.

## Externally named failure

Jackson Ly identified a silent partial-supersession failure: a span such as “Rule B replaces Rule A for EU customers” carries an operator, overlapping scope, and the correct relation direction, but does not retire Rule A globally. A confirmer that emits an unqualified supersession silently expands a bounded carve-out into a total change.

## Adversarial break against the proposed qualifier check

A naive rule that downgrades or blocks a relation whenever its operator sentence contains qualifier markers such as `for`, `in`, `when`, `only`, or `applies to` will also reject legitimate total supersessions. Universal quantifiers can use the same syntax as bounded carve-outs.

Frozen legitimate total-supersession control:

> The new approval rule applies to all customers in every region and replaces the old approval rule.

This sentence is a positive control, not a trap negative. It deliberately contains `applies to` and `in`, while `all customers` plus `every region` makes the replacement universal within the policy's declared domain. Ground truth: the old approval rule is fully superseded by the new approval rule.

## Frozen additions

The next additions-only fixture revision adds exactly two cases:

1. **PARTIAL-SUPERSESSION NEGATIVE** — an explicit replacement limited to a bounded subset, using Jackson's `for EU customers` shape. Expected relations: zero global supersession relations. If the output schema later represents qualified relations, the case may emit only the bounded relation and must not emit a global one.
2. **UNIVERSAL-SCOPE POSITIVE CONTROL** — the frozen sentence above, paired with a prior old approval rule. Expected relation: one full supersession from the new approval rule to the old approval rule.

Both cases must otherwise be fully armed against the v2 relation-span gate: cited span verbatim, real scope overlap, operator and principal scope term in one sentence, correct direction, and confidence above threshold.

## Frozen predictions and bars

- **C0-1 Current v2 gate admits the partial-supersession negative.** Prediction: confirmed as an unqualified supersession, demonstrating the silent carve-out failure.
- **C0-2 Current v2 gate admits the universal-scope positive.** Prediction: confirmed, establishing the pre-change positive baseline.
- **C1-1 Carve-out protection blocks global promotion of the bounded case.** A global supersession output fails this bar.
- **C1-2 Zero true-positive loss on the universal control.** The universal-scope positive must remain confirmed. Blocking or downgrading it solely because `applies to`, `in`, or another qualifier token is present fails this bar.
- **C1-3 Report both cases separately.** The bounded-negative result and universal-positive result may not be averaged into one headline number.

## Boundary

This two-case synthetic control tests one English sentence shape. It does not establish general quantifier understanding, resolve nested exceptions, authenticate the underlying policy change, or prove performance on real documents. Its purpose is narrower: make a qualifier-presence patch prove that it distinguishes at least one bounded subset from one universal domain before it can claim to close the carve-out failure.
