# Sol + Fable Release Loop — V3 Repair

Status: active release-note lane
Baseline commit: `8968d58`
Scope: public research release note for the repaired v3 store-authority loop

## Purpose

Sol and Fable own the release-note refinement loop from here.

The goal is one compact, technically honest public note that explains what changed, what was independently checked, and what remains unproven.

This is not a new article. This is not a new implementation pass. This is a claim-boundary and verification loop.

## Roles

### Fable

Primary seat: independent verifier / claim-to-artifact checker.

Fable checks whether every release sentence is supported by:

- commit `8968d58`
- the raw artifact
- the six fixture packets
- test output
- the AP3 requester-id omission regression

Fable should say "supported", "unsupported", or "needs narrower wording."

### Sol

Primary seat: adversary / overclaim detector.

Sol attacks the release for:

- calling v3 solved
- collapsing PD-3 into the pass bar
- implying declared disjointness proves real independence
- implying the evaluator can see proposer silence
- implying capability receipts prove deployed IAM/platform/hardware attestation
- blurring maker, attacker, and checker roles

Sol should propose sharper wording only when the current wording is too broad.

## Loop Order

1. Fable drafts or approves a compact factual skeleton.
2. Sol attacks the skeleton against `V3_RELEASE_CLAIM_BOUNDARY_REVIEW_2026-07-15.md`.
3. Fable checks Sol's proposed wording against artifacts and test results.
4. Repeat only until both agree the note is supported and bounded.
5. Stop. Do not expand into a full article.

## Required Facts

The release may say:

- Six frozen fixture packets are now wired into the deterministic runner.
- Commit `8968d58` contains the repaired evaluator, tests, runner, and final artifact.
- The final artifact reports 23 cases: 22 pass-bar cases plus one separately reported PD-3 ceiling.
- The artifact reports 22/22 pass-bar matches and 1/1 ceiling match.
- Fable independently recomputed those six packets and matched the artifact counts.
- Sol found the requester-id omission seam before commit.
- The omission seam is regression-locked: removing `requester_id` from AP3 still blocks with `confused_deputy_retirement`.

## Forbidden Claims

The release must not say:

- v3 is solved
- the system is secure
- independence is proven
- 23/23 passed
- all omissions are caught
- the artifact itself is independent
- capability fixtures prove real deployed platform attestation
- the evaluator can judge claims the proposer never emits

## Required Boundaries

### PD-3

PD-3 proves the declared-path gate can pass while ground truth contains a hidden shared dependency. It is a ceiling case, not a pass-bar success.

### Silent Omission

The evaluator can only judge claims that reach it. If a proposer never emits a claim, the current gate does not independently know that absence happened.

### Capability Attestation

The current capability-root fixtures enforce receipt fields at the deterministic application boundary. They do not prove a real deployed attestation root outside the process.

## Output

Final output should be either:

1. A compact release note ready for Keniel approval, or
2. A clear statement that the release is blocked because a claim lacks artifact support.

Do not continue iterating after the release note passes the boundary review.
