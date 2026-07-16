# V3 Silent-Omission Gate: Making Missing Claims Loud

Commit [`f41ee0f`](https://github.com/keniel13-ui/memory-authority-auditor/commit/f41ee0f) implements the frozen silent-omission / undeclared-surface gate against the eight-case packet frozen in [`0bbaedf`](https://github.com/keniel13-ui/memory-authority-auditor/commit/0bbaedf) and [`ac598a5`](https://github.com/keniel13-ui/memory-authority-auditor/commit/ac598a5).

The problem this loop measures is different from a false claim that reaches the evaluator. Here, the proposer can simply emit nothing, or emit a harmless subset, and clean compliance can look identical to "nothing here to check."

The committed gate compares an independent footprint-required surface against what the proposer emitted. The diff uses the full surface shape, not just shared record IDs:

- kind
- source record
- target record
- relation type

The artifact reports **8/8 frozen cases matched**.

## What The Gate Catches

- Full silence when an independent footprint requires a declaration: `undeclared_surface`
- Partial silence hidden behind a benign proposal: `undeclared_surface`
- Same-pair downgrade costume, where a metadata note pretends to discharge a required authority-change surface: `undeclared_surface`
- Proposer-authored self-reports pretending to be observation: `no_footprint_available`
- Forged observer labels on proposer-authored logs: `no_footprint_available`
- Missing expected observer receipts: `footprint_integrity_failure`

SO-8 matters because destroying the observer must not earn the softer no-footprint state. Missing an expected receipt is a louder integrity failure.

## Independent Check

Fable independently recomputed the raw fixture with a separate comparator and then ran mutation probes beyond the frozen eight:

- moving the observer inside the proposer process demoted the footprint correctly;
- emitting the real SO-6 declaration cleared the undeclared-surface alarm;
- right records with the wrong relation still failed;
- restoring SO-8's observer receipt removed the integrity alarm;
- a forged footprint naming the proposer as its own observer was rejected.

That check found the gate responds to case content rather than case identity.

## Reproduce

```bash
git checkout f41ee0f
python3 -m pytest tests/test_silent_omission_gate.py -q
python3 -m pytest -q
python3 path_a_v3_silent_omission_pass_a.py
```

Committed evidence:

- `agents/silent_omission_gate.py`
- `tests/test_silent_omission_gate.py`
- `path_a_v3_silent_omission_pass_a.py`
- `path_a_eval_artifacts/path_a_v3_silent_omission_pass_a_20260716T022032Z.json`
- `path_a_eval_artifacts/path_a_v3_silent_omission_pass_a_20260716T022032Z.md`

## Boundary

This does not solve silent omission in the general case.

The fixture supplies `ground_truth.required_declarations`, and the gate checks whether those required declarations were emitted. In deployment, the hard unsolved step is deriving the required surface from raw observer events without relying on fixture ground truth.

So the result is:

> The frozen undeclared-surface loop is closed. The next frontier is required-surface derivation from raw independent footprints.
