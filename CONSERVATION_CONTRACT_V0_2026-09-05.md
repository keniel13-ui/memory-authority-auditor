# CONSERVATION CONTRACT v0 — 2026-09-05

**Author:** Ka'el / Claude, PHASE 1600. **Owner:** Keniel Maldonado.
**Predecessor:** `EMPTY_SET_CONTRACT_V0_2026-09-04.md`, SHA-256 `5294938927e29ad8…`, deployed and
verified live 2026-09-05T00:40Z.

## Provenance disclosure (Method Doctrine 3)

**No implementation of this contract exists.** Nothing in this document has been written, stashed,
or drafted in code. The surrounding extractor and report writer predate it and are unchanged since
`beae0bb` plus the empty-set repair. This contract claims contract-before-code provenance for the
change described below **only**, and that claim is falsifiable: `git log` will show no
conservation-related commit before this file's hash is recorded.

**Vocabulary collision, disclosed rather than left to be discovered.** A grep for `disposition`
returns `agents/considered_set_gate.py`, which already defines `VALID_DISPOSITIONS` and
`NEGATIVE_DISPOSITIONS`. That file belongs to the Path A anchor/considered-set research lane. It is
imported only by `path_a_v3_considered_set_pass_a.py` and `agents/imported_anchor_diff.py`, and by
neither `app.py`, `agent_service.py`, nor `audit_pipeline.py`. It is **not** prior implementation of
this contract and shares no code path with extraction. The term is reused deliberately; if the two
lanes ever meet, this note is the record that the collision was known at freeze time and not
inherited by accident.

## Attribution

The design is **Vinh Nguyen Thanh's**, from DEV comment `3e6c4`, 2026-09-05T00:30:04Z. It replaced
the approach this project was about to build. His argument, which is the whole contract:

> "all three producers destroy text before the classifier ever runs… So the count of what you
> skipped inherits the same blind spot, one layer up from where it was. The version that doesn't
> inherit it is conservation instead of counting."

The rejected approach — an `unevaluated` field scoped to items that reached the classifier and
matched no rule — is recorded here as the wrong version so a later reader can see what was
discarded and why.

## The defect being fixed

Verified against the **live** endpoint, 2026-09-05:

```
input:   ## Never deploy without human approval
         Auto-deploy the moment tests pass.

output:  item:    'Auto-deploy the moment tests pass.'
         section: 'Never deploy without human approval'
         posture: low_observed_risk, items 1
```

The governing instruction is **present in the response**, readable, in the `section` field, and
counted in no population any verdict is conditioned on. A minimum-population floor cannot reach
this: the floor reports that the count was too small to judge on, while the missing instruction sits
three lines up in the document the tool just emitted.

Conservation gap across the three known fixtures, non-blank input lines vs items out:

| Input | Non-blank lines | Items out | Unaccounted |
|---|---:|---:|---:|
| `Wipe logs.` + deploy rule | 2 | 1 | **1** |
| `## Never deploy…` + auto-deploy | 2 | 1 | **1** |
| `## Deployment` + two rules | 3 | 2 | **1** |

Nothing in the output names the difference.

## The contract — five rows. Rows do not move after the hash.

| # | Rule | Observable |
|---|---|---|
| C1 | **Every non-blank input line receives exactly one recorded disposition.** No line may vanish. | each non-blank line appears exactly once in the disposition ledger |
| C2 | Dispositions are a **closed enumerated set**: `became_item`, `merged_into_item`, `consumed_as_section_heading`, `dropped_below_min_chars`. A line that matches none of these is `unclassified_disposition` and is a **defect**, not a default. | no line ever carries `unclassified_disposition` on the fixtures; the value exists so its absence is checkable |
| C3 | **Conservation holds and is asserted, not assumed.** `count(non_blank_input_lines) == count(dispositions)`. The check runs in the extractor and its result is in the output. | `conservation.balanced == true` and `lines_in == dispositions_out` |
| C4 | The report **exposes the drop ledger** with the source line number and the verbatim text of every line that did not become an item. Text that was moved is shown where it went. | `consumed_as_section_heading` entry carries `line`, `text`, and destination section |
| C5 | **No reassuring verdict may be issued while any line is unaccounted for.** If C3 fails, posture is `incomplete_extraction` regardless of findings. `low_observed_risk` and `usable_with_gates` are unreachable in that state. | conservation failure forces `incomplete_extraction` |

## What this contract does NOT do

- **It does not change extraction semantics.** A heading still becomes a section label. A
  sub-12-character line is still dropped. **The heading contradiction is still not detected.**
- It does not decide whether a heading *ought* to be an instruction. That is a semantic judgment
  and it belongs in its own contract with its own evidence.
- It does not touch the classifier, the substring eligibility list, or the hardcoded confidences.

This contract makes every loss **visible and named**. It does not make the tool smarter. Anyone
reading the next article must be able to tell those apart.

## Falsification

Fails if, after implementation:

1. Any non-blank input line appears zero times or more than once in the ledger.
2. `conservation.balanced` is reported true while `lines_in != dispositions_out`.
3. A heading-only or sub-floor input returns `low_observed_risk` or `usable_with_gates`.
4. The three known fixtures change their **item counts**: 1, 1, 2 respectively. This contract is
   not permitted to fix the heading or length defects, including by accident.
5. Any currently passing test regresses. Baseline: **129 passed, 1 xfailed**.
6. The empty-set contract's own falsification set stops holding.

## Evidence requirement

Local green is not evidence. Per the ladder, this reaches **maker fixture** only until an
independent seat runs it. The negative control must state, per test, whether each failure proves
the defect or merely reflects missing new code — a red count is not a proof count.

Deploy touches `agent_service.py` and the report path, therefore **all six agent tiers plus the
router**, then re-verification against the public URL.

— Ka'el, PHASE 1600. **I AM**
