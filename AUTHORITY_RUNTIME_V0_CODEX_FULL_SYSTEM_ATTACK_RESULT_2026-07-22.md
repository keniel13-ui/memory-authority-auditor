# Authority Runtime v0 — Codex Full-System Attack Result

Date: 2026-07-22
Candidate: `40092f3f4496eb5e4a464ad184708e34daa7eb59`
Remote floor before push: `08993063fb8276eecd8b454cd637b558c5d11a12`
Verdict: **PASS AFTER BOUNDED REPAIR**

## Independence boundary

This is a fresh source-first attack against the fingerprinted candidate, but it is a Codex attack of a Kairos/Codex-made artifact. It is not Grok/Aethar's signature and must not be represented as one. The technical matrix passed; the independent-seat strength is lower than the originally named Grok route.

## Candidate integrity

All handoff fingerprints matched:

- runtime: `317275e8a02df1f82526d232f1fa7ae241d76fd2bae3b19c4a6c740ca167a98b`
- CLI: `61eee7d9be0a28a24efabe719e7397f781eb96b119a6626e8cc7a082df59806f`
- PASS A runner: `e5422ec065356c636e0f6dc80479a28739f59a41a872669b85db01e40dabcd3b`
- tests: `e05faa6409440f46bc636cf4a6435a669987565f28a1870bda7418e284340b05`
- frozen packet: `bd3f7c8501feada1e5c31306bbf38415bc51d5e85601f186d45ba4b19660f6ec`
- PASS A JSON: `d59a3be0ec49b912d103abe48b87a61c2687f25796f603d2f9ee686ee783604d`
- flagship JSON: `388548789719558c117cefb73e180caaa6c601fcd06cf2929f83d1f61f9355d2`

Commit `40092f3` contains exactly the intended 11 files. The full six-commit range also contains the two preregistration documents frozen before implementation. Pre-existing SOL and prior attack/handoff notes remain untracked and outside the candidate.

## Recomputed evidence

- Independently recomputed runtime policy, startup, action, state, manifest, mapping policy, mapping grant, mapping receipt, mapping assertion, mapping census, action key, surface key, mapping key, and decision digests: match.
- Exact action and completion excerpts exist byte-for-byte in `CURRENT_STATE_BOARD.md` and `BRAIN_CURRENT.md`.
- AR-2 mapping resolution, census observation, state observation, manifest observation, and audit time remain causal; no later evidence enters its `ALLOW` decision.

## Adversarial matrix

- Omitted manifest-listed state receipt: `UNKNOWN / state_evidence_omission`.
- Injected unlisted state receipt: `UNKNOWN / state_evidence_injection`.
- Identical replay: collapses and preserves the base decision.
- Same receipt ID with different valid canonical bytes: `UNKNOWN / evidence_identity_conflict` before ranking.
- Manifest ID tamper without redigest: manifest failure.
- Redigested manifest under untrusted observer: manifest failure.
- Manifest end-gap: manifest failure.
- Reversed every multi-state frozen case: decisions and controlling/ignored identities remain invariant.
- Newer lower-authority costume: cannot outrank live verification.
- Equal-authority/equal-time disagreement: `CONFLICT`.
- Later highest-authority reversion: `ALLOW`.
- Target state without exact completion binding: `UNKNOWN`.
- Wrong resource, scope, state key, and future evidence: refused.
- Source-class self-upgrade with recomputed receipt digest: ineligible.
- Missing mapping receipt, grant, census, or valid policy: `UNKNOWN` with no canonical mapping/action/surface/resource leak.
- Mutated action alias, scope, subject time, or late mapping resolution: refused before canonical identity becomes authoritative.
- Every semantic action field changes the action key; provenance-only decoration does not.

## Operator behavior

- Focused suite: **21 passed**.
- Full suite: **101 passed / 1 expected xfail**.
- Frozen runner: **11/11** outcomes.
- Exact outsider command: `BLOCK_STALE_ACTION / stale_action_completed / exit 3`; JSON and Markdown written.
- Explicit CLI outcomes independently observed: `ALLOW=0`, `BLOCK_STALE_ACTION=3`, `CONFLICT=4`, `UNKNOWN=5`.
- Missing case and malformed packet: CLI error `2`; no decision receipt written for the missing case.
- Source scan found no network, DNS, subprocess mutation, action execution, case-ID decision branch, or hidden allow fallback.

## B1 — isolated-clone provenance test portability — CLOSED

The first archive of remote `40092f3` reproduced the decision command successfully, but `tests/test_authority_runtime.py::test_real_replay_excerpts_exist_in_live_workspace_sources` failed because it assumed Keniel's private `CURRENT_STATE_BOARD.md` and `BRAIN_CURRENT.md` existed one directory above every clone. That is true in the maker workspace and false for a real outsider.

Smallest repair: keep the exact live-source assertion when those external files exist, accept an explicit `AUTHORITY_RUNTIME_WORKSPACE_ROOT`, and skip only this provenance test when an isolated clone cannot possess the external workspace. The fixture's exact-byte digests and the runtime decision remain unconditional; the skip is limited to re-verifying private external source files an outsider was never given.

Required recheck: local focused/full suites, isolated-archive focused suite, and exact outsider command.

## Boundary judgment

`mutation_authorized=true` on `ALLOW` is not a blocker in this candidate because the CLI description, README, decision explanation, result boundary, and every Markdown receipt explicitly call the system dry-run and state that it executes no DNS change. The field means “the frozen policy allows the proposed action,” not “a mutation occurred.” Before any connector or enforcement integration, this should be renamed or wrapped so an operator cannot mistake a policy result for an executed or globally authorized mutation.

The configured observer/source identities are integrity-bound but not cryptographically authenticated. That limitation is stated consistently and remains an explicit v0 boundary, not a hidden implementation claim.

## Final judgment

Behavioral gate: **PASS**. The candidate can be pushed as the frozen six-commit research proof. Feature expansion remains frozen under the practical-value PIVOT; the next value test is transfer/external use, not another contract.
