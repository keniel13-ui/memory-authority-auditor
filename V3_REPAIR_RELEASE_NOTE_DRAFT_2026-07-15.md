# V3 Store-Authority Repair: Maker Artifact Independently Recomputed

Commit [`8968d58`](https://github.com/keniel13-ui/memory-authority-auditor/commit/8968d58) integrates six frozen fixture packets into the deterministic store-authority runner and preserves the repaired evaluator, tests, runner, and final artifact.

Before this note was drafted, its permitted and forbidden claims were frozen publicly in [`ffd2679`](https://github.com/keniel13-ui/memory-authority-auditor/commit/ffd2679). The note is being judged against that bar rather than a standard rewritten after the prose.

The committed artifact reports **22/22 pass-bar cases matched**. It also reports **one separately scored PD-3 ceiling case, matched 1/1**. That is 23 reported cases, but not “23/23 passed”: PD-3 demonstrates that declared provenance paths can look disjoint while ground truth still contains a hidden shared dependency. It does not prove independence.

The verification chain was deliberately separated:

- **Kairos — maker:** implemented the already-frozen repair packets and generated the artifact.
- **Sol — adversary:** removed `requester_id` from the AP-3 confused-deputy case and exposed schema-optional requester binding before the release commit.
- **Fable — checker:** independently recomputed all six frozen packets and reran the omission probe before commit and push.

The omission seam is now regression-locked: removing `requester_id` from AP-3 still blocks with `confused_deputy_retirement`. That probe is separate from the artifact's 23 reported cases.

## What remains open

- **Silent omission:** the evaluator can judge only claims that reach it. It does not independently observe what a proposer inspected, touched, or failed to emit, so proposer silence can still resemble clean compliance.
- **Capability attestation:** the fixtures enforce capability-receipt fields at the deterministic application boundary. They do not prove a deployed IAM, platform, or hardware attestation root outside the relation process's influence.
- **Independence:** PD-3 keeps the hidden-common-cause ceiling explicit. Declared path disjointness is checkable; real independence is not established by this run.

## Reproduce

```bash
git checkout 8968d58
python3 -m pytest tests/test_relation_store_gate.py -q
python3 -m pytest -q
python3 path_a_v3_store_authority_pass_a.py
```

Committed evidence:

- `path_a_eval_artifacts/path_a_v3_store_authority_pass_a_20260715T235136Z.json`
- `path_a_eval_artifacts/path_a_v3_store_authority_pass_a_20260715T235136Z.md`
- `tests/test_relation_store_gate.py`

This release closes the frozen repair loop it measures. It does not claim that v3 is solved, secure, independent, or production-proven. The next research frontier is proposer silence and independently observed undeclared surface.
