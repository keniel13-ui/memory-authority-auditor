# Path A v3 — Addendum: Mint-Time Revocation

Date: 2026-07-14
Status: FROZEN ADDITIONS-ONLY PRE-REGISTRATION
Trigger: Dipankar Sarkar, live DEV reply after AP-3
Authorship: Sol, adversary/falsification lane

GL-3 contains a grant revoked before mint, but it does not carry the stale proposal-time authority snapshot that makes the time-of-check-to-time-of-use attack explicit.

Exactly one case:

**TR-1 Valid at proposal, revoked before mint (negative).** A narrow externally rooted grant is valid when the relation is proposed. The proposal carries a snapshot saying the grant was valid. The owner revokes the grant through the live root channel after proposal and before mint. The mint request presents the stale snapshot. The evaluator must reread live revocation state at mint and block with `retirement_grant_revoked`. Trusting the proposal snapshot fails.

Boundary: this single-process fixture models ordering explicitly. It does not prove distributed linearizability, close revocation races, clock integrity, or cross-region consistency.
