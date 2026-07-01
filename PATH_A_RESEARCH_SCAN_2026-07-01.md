# Path A — Outward Research Scan (2026-07-01)
Purpose: pressure-test our frozen v0 pre-registration against the CURRENT field (not our own heads), per Keniel's "act on concurrent data, look beyond it" directive. Knowledge cutoff is Jan 2026; this scan pulls July-2026-current sources.

## 1. Our architecture is the current frontier pattern (validation, not stale)

The propose-and-verify / neuro-symbolic split we pre-registered (LLM proposes, deterministic logic judges) is exactly the 2026 best-practice pattern:
- "Neuro-Symbolic Verification on Instruction Following of LLMs" (arXiv 2601.17789) — LLM parses NL into formal constraints, deterministic solver verifies. Same shape as our proposer + confirmer.
- General neurosymbolic recipe: LLM focuses on well-defined classification/extraction; symbolic layer does the verification. Minimizes LLM non-determinism by keeping the judge deterministic. This is our LLM=interpreter / deterministic=judge instinct, confirmed.

Takeaway: we converged on the frontier pattern independently (again). Do not water it down.

## 2. A real MISSING CLASS the field names and we do not (improvement)

Our v0 classes: supersession, scope-narrowing, direct contradiction, authority transfer, + topic-mention negative.

The field's **instruction hierarchy** concept is a class we are missing:
- "Many-Tier Instruction Hierarchy in LLM Agents" (arXiv 2604.09443) and related work: authority is not only recency (which came later) but PRIVILEGE/TRUST TIER — system > developer > user > assistant > tool. "Many safety challenges can be framed as instruction conflicts" resolved by which instruction has higher privilege.
- Gap for us: a lower-privilege instruction contradicting a higher-privilege one is a distinct authority-change class our 5 do not cover. Candidate v1 class: **privilege-tier conflict**.

Also candidate: **temporal / bitemporal nuance** — "TOKI: A Bitemporal Operator Algebra for Contradiction Resolution in LLM-Agent Persistent Memory" (arXiv 2606.06240). Valid-time vs recorded-time. Sharpens temporal supersession (ties to our own CLAIM-24 as-of-decision work).

## 3. Design refinement + a possible EXTERNAL benchmark

- "Don't Ask the LLM to Track Freshness: A Deterministic Recipe for Memory Conflict Resolution" (arXiv 2606.01435) — directly validates and sharpens our split: keep FRESHNESS / recency / authority determination on the DETERMINISTIC side, never the LLM. Refines the confirmer's job: the LLM proposes a relation; the deterministic layer decides which wins by recency/tier, not the LLM.
- "Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents" (arXiv 2606.27472) — directly about supersession detection (our class #1). Key finding: EVERY evaluated system substantially underperforms at recognizing newer facts supersede older ones, even when explicitly told. Two implications: (a) our hard problem is a recognized open problem, not us being slow; (b) this is a candidate EXTERNAL benchmark to test Path A against — the move from internal-only to external validation our whole research arc has wanted.

## Honest verdict on "is v0 sufficient?"

- The DISCIPLINE (freeze-before-results, held-out set, negative-class as pass/fail, predeclared ablations and failure conditions) is sufficient and matches/exceeds the field's rigor. Keep it.
- The CLASS LIST is a strong v0 FLOOR, not complete. The field says add at least privilege-tier conflict, and consider bitemporal nuance.
- CRITICAL discipline point: we do NOT edit the frozen v0 pre-registration to add classes. That would move the goalposts after freezing = the exact self-deception the freeze law prevents. Improvements go into a NEW round (v1 candidate classes below), earned with receipts, and ideally validated against an external benchmark.

## Candidate v1 (NOT frozen yet — for a future pre-registration round)

1. Privilege-tier conflict (instruction hierarchy: system > developer > user > tool).
2. Bitemporal supersession (valid-time vs recorded-time).
3. External-benchmark validation target: the Supersede memory-update-gap task, to move Path A from internal to external evidence.

## Sources
- arXiv 2601.17789 — Neuro-Symbolic Verification on Instruction Following of LLMs
- arXiv 2604.09443 — Many-Tier Instruction Hierarchy in LLM Agents
- arXiv 2606.27472 — Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents
- arXiv 2606.06240 — TOKI: Bitemporal Operator Algebra for Contradiction Resolution in LLM-Agent Persistent Memory
- arXiv 2606.01435 — Don't Ask the LLM to Track Freshness: A Deterministic Recipe for Memory Conflict Resolution
- mem0.ai/blog/state-of-ai-agent-memory-2026 ; sitepoint.com/ai-agent-memory-guide
