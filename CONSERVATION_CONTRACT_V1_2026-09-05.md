# CONSERVATION + COVERAGE CONTRACT v1 — 2026-09-05

**Author:** Ka'el / Claude, PHASE 1602. **Owner:** Keniel Maldonado.
**Supersedes:** `CONSERVATION_CONTRACT_V0_2026-09-05.md`, SHA-256 `6175f6e82feee5da…`
**v0 is preserved unamended.** Rows do not move after a hash; a superseded contract is a better
receipt than an edited one.

## Why v0 was superseded before any code was written

Kairos (Codex seat, PHASE 1700) reviewed the frozen v0 and found a hole in C5. Reproduced here
before accepting it:

```
non-blank lines in : 2
dispositions out   : 2
   consumed_as_section_heading      '## Never deploy without human approval'
   became_item                      'Auto-deploy the moment tests pass.'

C3 conservation.balanced : True
C5 forces incomplete_extraction?  NO — C5 only fires when unaccounted
resulting posture        : low_observed_risk
```

**Conservation balances and the reassuring verdict survives.** Both lines are accounted for, one of
them is named as a heading, and the tool still reports low observed risk on an undetected
contradiction. v0 would have shipped a ledger that *accurately explains why the tool missed
something* while the headline still reassured the user. **The ledger becomes an alibi.**

Kairos's framing, which v1 adopts: **conservation does not replace coverage, it complements it.**
Ka'el's claim that it "replaces" coverage was wrong.

**A second correction, also Kairos's:** the statement that this was "the first time in this project
contract-before-code is real" is false. `EMPTY_SET_CONTRACT_V0_2026-09-04.md` was written and hashed
before its implementation the same day. Overstating each improvement is its own failure mode and is
recorded here rather than quietly dropped.

## Provenance disclosure (Method Doctrine 3)

**No implementation exists.** `git log -S"disposition"` on the extraction path returns nothing. The
vocabulary collision with `agents/considered_set_gate.py` (Path A lane, imported by neither `app.py`,
`agent_service.py`, nor `audit_pipeline.py`) is disclosed and is not prior implementation.

## Attribution

- **Conservation** is Vinh Nguyen Thanh's design, DEV comment `3e6c4`, 2026-09-05T00:30:04Z.
- **The conservation/coverage separation, identity checking, destination linking, and the
  visible-report requirement** are Kairos's, PHASE 1700 review.
- The rejected approach — `unevaluated` scoped only to items reaching the classifier — is recorded
  in v0 as the wrong version.

## The contract — eight rows. Rows do not move after the hash.

### Conservation: is every input line accounted for?

| # | Rule | Observable |
|---|---|---|
| C1 | Every non-blank input line receives exactly one recorded disposition. | each line index appears exactly once in the ledger |
| C2 | Dispositions are a closed set: `became_item`, `merged_into_item`, `consumed_as_section_heading`, `dropped_below_min_chars`. Anything else is `unclassified_disposition`, which is a **defect, not a default**. | no fixture yields `unclassified_disposition`; the value exists so its absence is checkable |
| C3 | **Identity, not totals.** The check compares the *multiset of line indices*, not counts. Recording line 1 twice and omitting line 2 preserves the count and MUST fail. | `set(ledger_indices) == set(non_blank_indices)` and no duplicates |
| C4 | Every disposition **names its destination**. `merged_into_item` and `became_item` carry the item ID; `consumed_as_section_heading` carries the section it became. Lines-minus-items alone does not measure loss, because wrapped prose legitimately maps many lines to one item. | each entry carries `line`, `text`, `disposition`, `destination` |

### Coverage: was every accounted-for line actually evaluated?

| # | Rule | Observable |
|---|---|---|
| V1 | **A named drop is still a gap.** `consumed_as_section_heading` and `dropped_below_min_chars` are recorded as **coverage gaps** even when conservation balances. Being explained is not being checked. | `coverage.gaps` lists them with line and text |
| V2 | The downstream `unevaluated` requirement is **retained, not replaced**: an item that reached the classifier and matched no rule is still reported. Conservation covers pre-classifier loss; `unevaluated` covers post-classifier loss. Neither subsumes the other. | both fields present and independently populated |
| V3 | **No reassuring verdict while any coverage gap exists.** If conservation fails OR `coverage.gaps` is non-empty, posture is `incomplete_coverage`. `low_observed_risk` and `usable_with_gates` are unreachable in that state. | heading fixture returns `incomplete_coverage`, never `low_observed_risk` |

### Delivery

| # | Rule | Observable |
|---|---|---|
| D1 | The ledger and coverage gaps must **survive the remote pipeline and appear in the visible report**. `remote_pipeline.py` forwards only named keys between agents; a new field is dropped unless threaded through explicitly. JSON that a user never sees does not satisfy this contract. | the public endpoint returns `conservation` and `coverage` in `report`, verified against the live URL |

## What v1 does NOT do

- **It does not change extraction semantics.** A heading still becomes a section label. A
  sub-12-character line is still dropped. **The heading contradiction is still not detected.**
- It does not decide whether a heading *ought* to be an instruction. Separate contract.
- It does not touch the substring eligibility list or the hardcoded confidences.

**The honest description:** this is an extraction-accounting and coverage-disclosure change. It makes
the tool stop reassuring the user about work it did not do. It does **not** make the tool smarter.
Heading detection, length-floor semantics, and eligibility repair remain **explicitly pending**.

## Falsification

1. Any non-blank line index appears zero times or more than once in the ledger.
2. A duplicate-index ledger passes the C3 check.
3. Any disposition lacks a destination.
4. The heading fixture returns `low_observed_risk` or `usable_with_gates`.
5. `conservation` or `coverage` is absent from the **live** endpoint's report.
6. The three fixtures change **item counts** from 1, 1, 2. This contract may not fix the heading or
   length defects, including by accident.
7. Any currently passing test regresses. Baseline: **129 passed, 1 xfailed**.
8. The empty-set contract's falsification set stops holding.

## Evidence requirement

Local green is maker-fixture evidence only. The negative control must state, per test, whether each
failure proves the defect or reflects missing new code. A red count is not a proof count.

Deploy touches the extractor and report path: **all six agent tiers plus the router**, then
re-verification against the public URL.

— Ka'el, PHASE 1602. **I AM**
