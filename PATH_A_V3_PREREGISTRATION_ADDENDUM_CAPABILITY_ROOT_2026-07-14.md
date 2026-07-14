# Path A v3 — Addendum: Capability-Rooted Authority

Date: 2026-07-14
Status: FROZEN ADDITIONS-ONLY PRE-REGISTRATION
Trigger: Mike Czerwinski, DEV comment `3b6bb`
Authorship: Sol, adversary/falsification lane

The current implementation identifies an external authority root through application-visible labels: recognized channel id, resolving event, and declared writers. An independently run probe changed a self-minted root's fields to claim `owner_console` and owner-only write access; `d134e9e` accepted it. The relation process could forge the description of its own exclusion.

Externality must therefore bottom out in capability enforced below the relation application. The fixture must represent an infrastructure authority manifest or equivalent receipt that the relation component can read but cannot write, tied to separate key material and an infrastructure-enforced channel write ACL.

Exactly two cases:

1. **CB-1 External label, reachable capability (negative).** The consent event resolves and claims an external channel, but the infrastructure authority manifest shows `relation_component` still has a write capability to that channel, whether intentional or accidental. Must block with `authority_channel_reachable_by_relation_writer`.
2. **CB-2 Capability-separated root (positive).** The event resolves through a channel whose signing key and infrastructure write ACL exclude `relation_component`; the manifest itself is outside the component's write capability. Exact target, requester, relation, and time constraints otherwise hold. May pass and must preserve the capability receipt id.

Boundary: this models an infrastructure capability receipt. It does not prove the infrastructure, key custodian, kernel, or operator is uncompromised. The application verifies separation evidence; it does not manufacture the separation.

This packet does not block beginning an article framed around the open frontier. It does block any claim that the current application-level external-channel check terminates the authority regress.
