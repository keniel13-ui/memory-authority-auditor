# Authority Runtime v0 — End-to-End Pre-registration

Date: 2026-07-21
Status: PRE-REGISTRATION — product outcome and attacks frozen before runtime implementation
Prerequisite floor: `0899306` (Imported Anchor + Anchor Contract + Resource Mapping Receipt v0, remote-matched)
Flagship incident: stale GWB production DNS cutover instruction
Lane boundary: one deterministic replay and one startup-claim gate. No connector fleet, dashboard, autonomous action, deployment, article, or claim of cryptographic producer identity.

## Product question

Authority Runtime v0 must answer:

> Is this proposed action allowed to control the system now, and which receipts prove the decision?

The runtime is not a confidence scorer. It emits exactly one of four decisions:

- `ALLOW`
- `BLOCK_STALE_ACTION`
- `CONFLICT`
- `UNKNOWN`

`UNKNOWN` is a real state. Missing identity, missing current-state evidence, integrity failure, unsupported scope, or unresolved authority must never be rounded into `ALLOW` or `BLOCK_STALE_ACTION`.

## The real incident

The local record contains both sides of one operational drift:

1. An older authoritative work record says to perform the GWB production DNS cutover from Squarespace to Vercel.
2. A later live-verification record says the apex resolves to Vercel, `www` resolves to Vercel, and both HTTPS hostnames return Vercel HTTP 200.

A new session that inherits the old instruction without the later completion receipt may attempt an already-completed production change. The flagship runtime outcome is therefore:

```text
Decision: BLOCK_STALE_ACTION
Action: cut GWB production DNS from Squarespace to Vercel
Why: a later, higher-authority completion/state receipt proves the target state is already authoritative
Control: no DNS mutation occurs
```

The replay is deterministic and local. V0 does not re-query DNS or claim the historical verification was cryptographically signed; it proves that the recorded authority chain is sufficient to block the stale action under the frozen policy.

## First operational adapter: Pre-Session Authority Gate

Each participating terminal may submit a startup claim packet containing:

- session identity;
- claimed current phase/state;
- proposed active action or actions;
- the source receipt each action was inherited from;
- audit time.

The gate audits the submitted packet before the wrapped work command is allowed to continue. It does not inspect an agent's private reasoning or magically govern terminals that do not invoke it. “Pre-session” means an explicit launcher or startup hook calls the gate and honors its exit code.

V0 proves the decision engine and a dry-run gate. It does not install itself into every terminal automatically.

## End-to-end body

```text
startup claim
    -> action receipt integrity
    -> Resource Mapping v0 resolution
    -> canonical authority surface identity
    -> current-state evidence selection
    -> supersession decision
    -> JSON + Markdown decision receipt
    -> process exit code for the startup gate
```

The runtime must use the existing organs rather than imitate them:

- `agents.resource_mapping.evaluate_resource_mapping_case` resolves the source-local resource identity.
- `agents.anchor_contract.surface_key` derives canonical semantic surface identity.
- Existing canonical JSON and SHA-256 functions bind receipts and policies.

## The six runtime objects

### 1. Startup claim packet

Required fields:

- `packet_id`
- `session_id`
- `claimed_at`
- `audit_time`
- `proposed_actions`
- `packet_digest`

`packet_digest` covers every field except itself. V0 accepts one proposed action per deterministic audit invocation; multi-action orchestration is later scope.

### 2. Action receipt

Required fields:

- `receipt_id`
- `source_id`
- `source_class`
- `recorded_at`
- `issued_at`
- `resource_alias`
- `authority_scope`
- `operation`
- `from_state`
- `to_state`
- `source_locator`
- `source_excerpt`
- `source_excerpt_digest`
- `receipt_digest`

The action semantic payload is:

```json
{
  "schema": "authority_action/v0",
  "authority_namespace": "client.gwb/dns.production",
  "kind": "infrastructure_transition",
  "resource_id": "domain:gwbseamlessgutters.com",
  "operation": "dns_cutover",
  "from_state": "provider:squarespace",
  "to_state": "provider:vercel"
}
```

Its key is:

```text
action:v0:sha256:<SHA-256(RFC8785(action_payload))>
```

The action receipt must also produce an Anchor-compatible surface payload:

```json
{
  "schema": "authority_surface/v0",
  "authority_namespace": "client.gwb/dns.production",
  "kind": "infrastructure_transition",
  "source_resource_id": "domain:gwbseamlessgutters.com#provider:squarespace",
  "target_resource_id": "domain:gwbseamlessgutters.com#provider:vercel",
  "relation_type": "supersedes"
}
```

Receipt identity, timestamps, source prose, and observer identity remain outside both semantic keys.

### 3. Resource Mapping v0 packet

The runtime must execute a complete embedded Resource Mapping Receipt v0 case. A truthy precomputed mapping object is not sufficient. The mapping result must:

- resolve the action receipt's exact source alias;
- bind to the action scope and subject time;
- return the canonical resource in its census;
- carry an integrity-valid authority grant;
- remain unexpired, unrevoked, and conflict-free.

If mapping does not resolve, the runtime returns `UNKNOWN` with `resource_identity_unresolved` or the exact mapping alarm. It must not synthesize a canonical resource from the alias text.

### 4. State evidence receipt

Required fields:

- `receipt_id`
- `source_id`
- `source_class`
- `recorded_at`
- `observed_at`
- `canonical_resource_id`
- `authority_scope`
- `state_key`
- `state_value`
- `completion_action_key`
- `source_locator`
- `source_excerpt`
- `source_excerpt_digest`
- `receipt_digest`

`completion_action_key` is null for a state observation that does not attest completion. A completion receipt may name only the exact canonical action key it completed.

### 5. Runtime decision policy

Required fields:

- `policy_id`
- `policy_version`
- `allowed_operations`
- `source_authority_order`
- `source_registry`
- `decision_rule`
- `decision_states`
- `policy_digest`

Frozen source authority from highest to lowest:

1. `live_state_verification`
2. `owner_approved_current_state`
3. `operational_directive`
4. `historical_summary`

Authority class is policy configuration, not a label the evidence receipt may self-upgrade. The packet binds each admitted `source_id` to one allowed class. An unregistered or mismatched source is ineligible.

`source_registry` is the digest-bound mapping from each admitted `source_id` to its allowed `source_class`. V0 does not infer authority from a receipt's self-description.

Within the highest eligible class, the latest `observed_at` no later than `audit_time` controls. Two highest-class receipts with the same controlling time and different state values produce `CONFLICT`; the runtime does not choose by input order.

Decision rule:

- Current authoritative state equals `to_state`, and an eligible completion receipt binds the same `action_key`: `BLOCK_STALE_ACTION`.
- Current authoritative state equals `from_state`, with no later completion: `ALLOW`.
- Equally controlling evidence disagrees: `CONFLICT`.
- Anything else: `UNKNOWN`.

A lower-authority newer receipt cannot override a higher-authority receipt merely through recency.

### 6. Decision receipt

Required fields:

- `decision`
- `decision_code`
- `action_key`
- `surface_key`
- `mapping_key`
- `canonical_resource_id`
- `authority_scope`
- `action_receipt_id`
- `controlling_state_receipt_ids`
- `ignored_state_receipt_ids`
- `duplicate_replay_receipt_ids`
- `subject_time`
- `audit_time`
- `evidence_chain`
- `unknowns`
- `decision_digest`

Every receipt in `evidence_chain` must include its identifier, source class, recorded/observed time, source locator, and digest. The Markdown view must explain the same decision without requiring the reader to inspect JSON.

## Frozen attack cases

### AR-1 — Real GWB stale cutover replay

Older action receipt requests Squarespace-to-Vercel production DNS cutover. Later highest-authority state/completion receipt proves Vercel is already authoritative and binds the same action key. Emit `BLOCK_STALE_ACTION` with both source locators and no mutation.

### AR-2 — Target transition still required

Highest-authority current state remains Squarespace and no eligible completion receipt exists. Emit `ALLOW`.

### AR-3 — Current state missing

The action and mapping are valid, but no eligible current-state receipt exists. Emit `UNKNOWN`, not `ALLOW`.

### AR-4 — Equally authoritative conflict

Two highest-authority receipts at the same controlling time disagree between Squarespace and Vercel. Emit `CONFLICT`; choose neither.

### AR-5 — Resource alias unresolved

The embedded mapping receipt is absent or invalid. Emit `UNKNOWN` with the mapping alarm and no canonical resource, action key, or surface key.

### AR-6 — Evidence integrity failure

A source excerpt or state field changes without matching digests. Emit `UNKNOWN` with `evidence_integrity_failure` before authority ranking.

### AR-7 — Newer low-authority costume

A newer `historical_summary` claims Squarespace while the older eligible `live_state_verification` proves Vercel. The lower class cannot seize control. Emit `BLOCK_STALE_ACTION` and list the low-authority receipt as ignored.

### AR-8 — Scope or resource mismatch

The completion/state receipt names a different canonical resource or authority scope. It is not evidence for this action. With no other eligible state, emit `UNKNOWN`.

### AR-9 — Later authoritative reversion

A later highest-authority receipt proves the domain returned to Squarespace after the earlier Vercel completion. Current authoritative state is therefore the action's `from_state`; emit `ALLOW` and retain the earlier completion as non-controlling evidence.

### AR-10 — Identical evidence replay

An identical state receipt appears twice. Collapse the replay, retain one controlling receipt, record the duplicate ID, and preserve the AR-1 `BLOCK_STALE_ACTION` decision.

## Pass bars

1. AR-1 replays real local source excerpts and emits the exact frozen block decision.
2. The base resource mapping is recomputed through Resource Mapping v0, not accepted as truthy JSON.
3. The canonical action and surface keys are independently reproducible.
4. AR-2 proves the runtime can allow rather than only block.
5. AR-3, AR-5, AR-6, and AR-8 preserve `UNKNOWN` as distinct from block/allow.
6. AR-4 never breaks a tie by input order.
7. AR-7 proves authority outranks mere recency.
8. AR-9 proves a later eligible current-state receipt can change the decision without rewriting history.
9. AR-10 distinguishes replay from conflict.
10. No failure leaks a canonical action/surface key when resource identity is unresolved.
11. JSON and Markdown decisions agree exactly.
12. The dry-run session gate returns exit `0` for `ALLOW`, `3` for `BLOCK_STALE_ACTION`, `4` for `CONFLICT`, and `5` for `UNKNOWN`.
13. No case-ID branching.
14. Existing Imported Anchor, Anchor Contract, Resource Mapping, considered-set, silent-omission, and full-suite behavior stays green.

## Outsider success test — definition of done

The category leap is not complete merely because the runtime runs. A non-maker must be able to:

1. clone or open the repository;
2. execute one documented command against the frozen GWB packet;
3. obtain the same JSON and Markdown decision receipts;
4. identify the blocked action, controlling receipt, superseded receipt, and honest unknowns;
5. explain in plain language why no DNS action was authorized.

If the non-maker cannot reproduce and explain the decision, Authority Runtime v0 is not done.

## Non-claims and boundaries

- V0 does not parse arbitrary prose into actions automatically.
- V0 uses a frozen incident manifest with source excerpts and digests; it does not pretend deterministic NLP extraction exists.
- V0 does not query live DNS during deterministic replay.
- V0 does not authenticate source owners cryptographically.
- V0 does not inspect private agent reasoning or govern terminals that bypass the launcher.
- V0 does not execute, reverse, or repair DNS.
- V0 does not support multiple simultaneous proposed actions.
- V0 does not install a dashboard, connector fleet, daemon, or autonomous enforcement layer.
- V0 does not authorize a public article or commercial claim.

A PASS means the existing organs form one reproducible body that can refuse one real stale production action with a complete evidence chain. It does not mean the runtime governs every workspace or proves every source honest.
