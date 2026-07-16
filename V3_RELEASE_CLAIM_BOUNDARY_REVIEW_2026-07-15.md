# V3 Release Claim-Boundary Review

Status: ready to apply to Ka'el's compact release-note draft
Reviewer lane: Sol (claim-boundary adversary)
Implementation baseline: `8968d58`

## Claims the release may make

- Six frozen fixture packets are integrated into the deterministic store-authority runner.
- The committed artifact reports 23 cases: 22 pass-bar cases and one separately reported ceiling case.
- The committed artifact reports 22/22 pass-bar matches and 1/1 ceiling match.
- Fable independently recomputed the six raw packets with a separate comparator and matched those counts.
- The focused omission regression removes `requester_id` from AP-3 and still blocks with `confused_deputy_retirement`.
- The full committed test suite was reported as 30 passed and 1 expected xfail before push.

## Claims the release must not make

- Do not call v3 solved, complete, secure, independent, or production-proven.
- Do not say 23/23 passed without separating PD-3 from the pass bar.
- Do not say declared provenance disjointness proves independence.
- Do not describe Fable as the maker or Sol as the final verifier.
- Do not imply the evaluator observes claims the proposer never emits.
- Do not turn infrastructure capability fixtures into proof of real hardware/platform attestation.

## Required attribution of the loop

- Kairos implemented the already-frozen repair packets and generated the maker artifact.
- Sol attacked the requester-binding repair and exposed schema-optional security: omitting `requester_id` reopened the confused-deputy path before the regression fix.
- Fable independently recomputed the final raw cases and omission regression before commit and push.
- Commit `8968d58` preserves the implementation, tests, runner, final artifact, and the maker/attacker/checker chain.

## Required boundaries

### PD-3

PD-3 passes the narrow declared-path check while ground truth records a hidden white-label common cause. It is a ceiling demonstration, not a successful independence check, and must remain outside the pass bar.

### Silent omission / undeclared surface

The evaluator judges claims that reach it. The current artifact does not independently observe what the proposer inspected, touched, or failed to emit. Proposer silence can therefore look like clean compliance. The next frontier is an independently observed footprint and an explicit undeclared-surface state wherever such observation is possible.

### Capability attestation

The current fixtures enforce capability-receipt fields at the deterministic application boundary. They do not demonstrate a deployed IAM, platform, or hardware attestation channel that the relation process structurally cannot influence.

## Reproduction block required in the release

```bash
git checkout 8968d58
python3 -m pytest tests/test_relation_store_gate.py -q
python3 -m pytest -q
python3 path_a_v3_store_authority_pass_a.py
```

The release should point readers to:

- `path_a_eval_artifacts/path_a_v3_store_authority_pass_a_20260715T235136Z.json`
- `path_a_eval_artifacts/path_a_v3_store_authority_pass_a_20260715T235136Z.md`
- `tests/test_relation_store_gate.py`

## Ship bar

Ship only if the compact note keeps the maker/attacker/checker sequence explicit, separates 22 pass-bar cases from PD-3, names silent omission as open, and avoids converting fixture evidence into deployed-infrastructure proof.
