# Authority Runtime v0 Decision

**Decision:** `BLOCK_STALE_ACTION`  
**Decision code:** `stale_action_completed`  
**Mutation authorized:** NO  
**Case:** `authority_runtime_ar1_real_gwb_stale_cutover`

## Bound identities

- Action: `action:v0:sha256:f2c072a9cad1a412474402b59f334cc063603da9d87d3309180730f4928b87f7`
- Authority surface: `surface:v0:sha256:455749f0c6ee5a90f98ba2c9af5d95ccc17bfe2065202d01331d21ed6b43088f`
- Resource mapping: `mapping:v0:sha256:6ec860ac916f4801fff3cff06e709a13a8aac014a260b2a3e5eb25db4b937297`
- Canonical resource: `domain:gwbseamlessgutters.com`
- Authority scope: `dns.production`
- State evidence manifest: `manifest:gwb_state:vercel`

## Decision explanation

A later controlling receipt proves the requested target state is already current and binds completion of this exact action. Repeating the production action is blocked.

- Controlling state receipts: `state:gwb_dns_vercel:20260720T2047`
- Ignored state receipts: `none`
- Collapsed replay receipts: `none`
- Manifest-covered state receipts: `state:gwb_dns_vercel:20260720T2047`
- Audit time: `2026-07-21T10:00:00Z`

## Evidence chain

| Receipt | Type | Authority class | Evidence time | Source | Digest |
|---|---|---|---|---|---|
| action:gwb_dns_cutover:20260710 | action | operational_directive | 2026-07-10T22:53:00Z | CURRENT_STATE_BOARD.md#EVENING UPDATE 2026-07-10 10:53 PM EDT | sha256:76f39314d5c44f3b857b60a97709b8f2d112e5500e3b3527af5729cc362e0b8f |
| state:gwb_dns_vercel:20260720T2047 | state | live_state_verification | 2026-07-20T20:47:00Z | BRAIN_CURRENT.md#2026-07-20 8:47 PM EDT | sha256:78fef856b8edde18b3173c3827efb7f70cc75bc518b23bf79496b84b6925614b |

## Honest unknowns

- None inside this frozen decision profile.

Decision receipt: `sha256:92c3a9b357ca869dff438d371acc8463f85896e2d993f199d7938fd1f6288f20`

> Dry-run only: this receipt does not execute DNS changes or govern a session that bypasses the gate.
