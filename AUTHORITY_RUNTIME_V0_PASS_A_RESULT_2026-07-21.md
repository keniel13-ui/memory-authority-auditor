# Authority Runtime v0 — PASS A Result

Date: 2026-07-21
Status: LOCAL PASS A — candidate not yet pushed at time of this result
Prerequisite floor: `0899306`
Decision freeze: `82e5ed4`, clarified by `2878cfa`
Replay freeze: `9b8a1b6`; intermediate audit-time correction `13beae4`, superseded in this candidate by the causal pre-cutover mapping path
State-coverage addendum: `321aeb6`

## Outcome

Authority Runtime v0 now composes the existing Resource Mapping and Anchor Contract organs into one dry-run executable:

```text
startup claim
  -> action receipt integrity
  -> embedded Resource Mapping v0 evaluation
  -> canonical action + authority-surface identity
  -> state evidence manifest / considered-set gate
  -> authority + recency decision
  -> JSON + Markdown receipt
  -> deterministic process exit code
```

The real GWB replay emits:

- decision: `BLOCK_STALE_ACTION`
- code: `stale_action_completed`
- controlling receipt: `state:gwb_dns_vercel:20260720T2047`
- old action receipt: `action:gwb_dns_cutover:20260710`
- mutation authorized: false
- exit code: 3
- action key: `action:v0:sha256:f2c072a9cad1a412474402b59f334cc063603da9d87d3309180730f4928b87f7`
- surface key: `surface:v0:sha256:455749f0c6ee5a90f98ba2c9af5d95ccc17bfe2065202d01331d21ed6b43088f`
- mapping key: `mapping:v0:sha256:6ec860ac916f4801fff3cff06e709a13a8aac014a260b2a3e5eb25db4b937297`
- decision receipt: `sha256:92c3a9b357ca869dff438d371acc8463f85896e2d993f199d7938fd1f6288f20`

No DNS action is executed.

## Blocking finding caught before candidate commit

The first implementation matched the original ten-case freeze and the full suite passed, but an internal attack found that a July 21 caller could submit only the July 10 Squarespace receipt and silently omit the later Vercel completion receipt. The evaluator would correctly rank the incomplete packet and return `ALLOW`.

That was a real silent-omission hole, not a test gap. The repair added:

- a digest-bound state evidence manifest;
- configured trusted manifest observers;
- exact manifest-versus-submitted receipt-set comparison after replay collapse;
- `state_evidence_omission` and `state_evidence_injection` refusal states;
- a causal pre-cutover mapping/census path for the legitimate historical `ALLOW` case;
- AR-11, which proves the later completion receipt cannot disappear into an `ALLOW`.

## Frozen outcomes

All 11 match:

- 2 `ALLOW`
- 3 `BLOCK_STALE_ACTION`
- 1 `CONFLICT`
- 5 `UNKNOWN`

The `UNKNOWN` set preserves missing state, unresolved identity, evidence tamper, wrong resource/scope, and state-evidence omission as non-allow states.

## Verification

- focused Authority Runtime tests: 21 passed
- full repository suite: 101 passed, 1 expected xfail
- frozen outcomes: 11/11
- real source excerpts: present in `CURRENT_STATE_BOARD.md` and `BRAIN_CURRENT.md`
- JSON / Markdown decision agreement: tested
- CLI exit codes: 0 allow, 3 stale block, 4 conflict, 5 unknown
- case-ID independence: tested
- equal-authority input-order independence: tested
- action semantic-key mutation and provenance exclusion: tested
- untrusted authority-class costume: refused
- untrusted state-manifest observer costume: refused
- future evidence outside manifest coverage: refused
- target state without exact completion binding: unknown
- state omission and injection: refused

Commands:

```bash
python3 -m pytest -q tests/test_authority_runtime.py
python3 -m pytest -q
python3 authority_runtime_v0_pass_a.py
python3 authorityctl.py audit tests/fixtures/authority_runtime_v0_gwb_dns_replay_2026_07_21.json \
  --case authority_runtime_ar1_real_gwb_stale_cutover \
  --json-out path_a_eval_artifacts/authority_runtime_v0_gwb_stale_action_decision.json \
  --markdown-out path_a_eval_artifacts/authority_runtime_v0_gwb_stale_action_decision.md
```

The last command intentionally exits 3 because the gate blocks the stale action.

## Candidate fingerprints

- `agents/authority_runtime.py`: `317275e8a02df1f82526d232f1fa7ae241d76fd2bae3b19c4a6c740ca167a98b`
- `authorityctl.py`: `61eee7d9be0a28a24efabe719e7397f781eb96b119a6626e8cc7a082df59806f`
- `authority_runtime_v0_pass_a.py`: `e5422ec065356c636e0f6dc80479a28739f59a41a872669b85db01e40dabcd3b`
- `tests/test_authority_runtime.py`: `e05faa6409440f46bc636cf4a6435a669987565f28a1870bda7418e284340b05`
- frozen packet: `bd3f7c8501feada1e5c31306bbf38415bc51d5e85601f186d45ba4b19660f6ec`
- PASS A JSON: `d59a3be0ec49b912d103abe48b87a61c2687f25796f603d2f9ee686ee783604d`
- flagship JSON: `388548789719558c117cefb73e180caaa6c601fcd06cf2929f83d1f61f9355d2`

## Boundaries

- The manifest observer and receipt producers are policy-configured identities, not cryptographically authenticated principals.
- The runtime evaluates explicit receipt packets; it does not extract actions from arbitrary prose.
- The deterministic replay does not query current DNS.
- `ALLOW` means the frozen authority policy does not identify the action as stale; the runtime still performs no external action.
- A terminal that does not invoke or honor `authorityctl` is not governed by it.
- No connector fleet, dashboard, daemon, deployment, article, or commercial claim is authorized by this result.

PASS A means one real stale production action can now be refused by one reproducible command with a complete, inspectable receipt chain. It does not mean the configured sources are cryptographically honest or that every workspace action is covered.
