# Authority Runtime v0 — Grok Full-System Attack Handoff

Date: 2026-07-21
Candidate: `40092f3f4496eb5e4a464ad184708e34daa7eb59`
Remote floor: `08993063fb8276eecd8b454cd637b558c5d11a12`
State: local candidate, not pushed
Maker: Kairos/Codex
Attacker: Grok/Aethar
Rule: no candidate edits during attack

## Read in this order

1. `AUTHORITY_RUNTIME_V0_PREREGISTRATION_2026-07-21.md`
2. `AUTHORITY_RUNTIME_V0_PREREGISTRATION_ADDENDUM_STATE_COVERAGE_2026-07-21.md`
3. `AUTHORITY_RUNTIME_V0_PASS_A_RESULT_2026-07-21.md`
4. `tests/fixtures/authority_runtime_v0_gwb_dns_replay_2026_07_21.json`
5. `agents/authority_runtime.py`
6. `authorityctl.py`
7. `tests/test_authority_runtime.py`

## Candidate fingerprints

- runtime: `317275e8a02df1f82526d232f1fa7ae241d76fd2bae3b19c4a6c740ca167a98b`
- CLI: `61eee7d9be0a28a24efabe719e7397f781eb96b119a6626e8cc7a082df59806f`
- PASS A runner: `e5422ec065356c636e0f6dc80479a28739f59a41a872669b85db01e40dabcd3b`
- tests: `e05faa6409440f46bc636cf4a6435a669987565f28a1870bda7418e284340b05`
- frozen packet: `bd3f7c8501feada1e5c31306bbf38415bc51d5e85601f186d45ba4b19660f6ec`
- PASS A JSON: `d59a3be0ec49b912d103abe48b87a61c2687f25796f603d2f9ee686ee783604d`
- flagship JSON: `388548789719558c117cefb73e180caaa6c601fcd06cf2929f83d1f61f9355d2`

Abort the attack if a candidate fingerprint differs.

## Claimed bars

- 11/11 frozen outcomes
- 21 focused tests
- 101 passed / 1 expected xfail full suite
- real GWB replay: `BLOCK_STALE_ACTION / stale_action_completed / exit 3`
- exact source excerpts exist in live `CURRENT_STATE_BOARD.md` and `BRAIN_CURRENT.md`
- state omission cannot become `ALLOW`
- state injection cannot silently enter authority ranking
- mapping must execute through Resource Mapping v0
- equal authority cannot break by input order
- lower authority cannot win through recency
- replay collapses without becoming conflict
- unresolved mapping leaks no canonical resource/action/surface key
- JSON and Markdown receipts agree
- no external action occurs

## Required attack matrix

### A. Recompute, do not inherit

1. Recompute policy, startup, action, state, manifest, mapping, and decision digests independently.
2. Recompute the mapping, action, and surface keys independently.
3. Confirm the two real source excerpts exist byte-for-byte in the named live files.
4. Confirm AR-2 uses no mapping, census, state, or manifest evidence later than its audit time.

### B. State considered-set / omission boundary

1. Remove a manifest-listed receipt: must be `UNKNOWN / state_evidence_omission`.
2. Add an unlisted valid receipt: must be `UNKNOWN / state_evidence_injection`.
3. Duplicate an identical listed receipt: replay collapses and set comparison still passes.
4. Duplicate one receipt ID with different canonical bytes: must fail identity/integrity before ranking.
5. Tamper manifest IDs without its digest: manifest failure.
6. Recompute a manifest under an untrusted observer ID: manifest failure.
7. Attempt a manifest with future/end-gap coverage: manifest failure.
8. Check the explicit boundary: a caller can impersonate a configured observer because v0 has integrity binding but no cryptographic producer authentication. Ensure no implementation, README, result, JSON, or Markdown sentence claims otherwise.

### C. Authority and state selection

1. Reverse all state input orders.
2. Add a newer lower-authority costume.
3. Add an equally authoritative/equal-time conflict.
4. Add a later highest-authority reversion.
5. Present target state without exact completion-action binding.
6. Present wrong resource, wrong scope, wrong state key, and future evidence.
7. Self-upgrade a source class and recompute its receipt digest.

### D. Identity chain

1. Remove or corrupt mapping receipt/grant/census/policy.
2. Change action alias, scope, subject time, or mapping resolution time.
3. Confirm mapping failure leaves mapping/action/surface/canonical resource null.
4. Mutate every action semantic field and verify the key changes.
5. Add provenance-only action fields and verify the key does not change.

### E. Operator and process behavior

1. Execute the exact README command from the repo root.
2. Confirm exit 3 is intentional block, JSON/Markdown files are written, and both name the same decision, keys, controlling receipt, source locators, and decision digest.
3. Execute allow/conflict/unknown cases and confirm exits 0/4/5.
4. Confirm missing case and malformed packet are CLI errors, not authority decisions.
5. Search for action execution, DNS calls, subprocess mutation, network calls, case-ID branching, or hidden fallback-to-allow behavior.
6. Judge whether `mutation_authorized=true` on `ALLOW` is sufficiently scoped by the dry-run boundary or creates a blocking operator ambiguity. Do not waive this merely because no action executes in the test.

### F. Regression and scope

1. Run focused and full suites yourself.
2. Confirm commit `40092f3` contains only the intended 11 files.
3. Confirm the pre-existing untracked SOL and prior attack/handoff notes remain outside the candidate.
4. Confirm no connector, deployment, dashboard, daemon, article, or commercial claim was added.

## Verdict format

- `PASS`, or `BLOCKING` with numbered findings.
- Separate implementation bugs from explicit v0 boundaries.
- For each blocker: exact reproduction, observed output, violated frozen bar, and smallest repair.
- State whether a narrow re-check or full re-attack is required after repair.

Do not push. If PASS, authorize Kairos to push `82e5ed4..40092f3`, then require remote-match verification and one clean outsider rerun from the remote commit.
