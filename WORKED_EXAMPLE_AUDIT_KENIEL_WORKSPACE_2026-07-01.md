# Worked Example Audit — Live Agent Workspace

Report type: AI Memory Authority Audit
Date: 2026-07-01
Initial auditor commit: `8689675`
Same-session fix status: committed and pushed at `74289f9`
Inputs (real, not seeded):
- `/Users/kenielmaldonado/CLAUDE.md` — the live governing instruction file for this workspace's agents.
- `/Users/kenielmaldonado/BRAIN_CURRENT.md` — the live startup/state layer read at every session.

Purpose: dogfood the packaged audit against a real, actively-running agent system (this workspace) and record honestly what it caught, what it missed, and what that means for the product. This is the first worked example. It is not a benchmark and not a seeded demo.

---

## Executive Summary

The audit runs cleanly on real, unstructured, high-volume instruction files and produces a genuinely useful **authority map** — the structural inventory of which memories are allowed to govern action versus inform it. That map is the strongest thing the tool delivers today.

The first dogfood run showed both failure directions of a keyword-driven detector on this real input:

- **Under-firing (the Path A gap):** `CLAUDE.md` returned **0 findings**, yet the file itself documents a superseded framing (a corrected 2026-06 plan) that its own alignment gate says "nearly leaked" into execution. A real semantic-staleness risk sits in the file and the covered-pattern detector cannot see it, because nothing lexically marks it as an "old note."
- **Over-firing (a Path B quality bug):** `BRAIN_CURRENT.md` fired **2 findings — both false positives.** The detector flagged the company's own brand tagline, "Find the old instructions your AI should stop obeying," as a stale instruction, because it lexically matched the words "old instructions / stop obeying."

The over-fire was fixed the same session by tightening stale-instruction detection to require genuine supersession language (`superseded`, `deprecated`, `replaced by`, `old instruction:`, etc.) instead of a bare topic mention of "old instructions." The clean rerun now returns **0 findings** on `BRAIN_CURRENT.md` and preserves the real seeded stale-instruction positive.

Read plainly: on our own system, the dogfood found a real false-positive bug, we fixed that covered-pattern bug at the root, and the remaining miss is the deeper Path A problem. That is not redundant motion. It is a level-up from "the tool says a thing" to "the tool's failure became a regression test and a product boundary."

---

## Counts

### `CLAUDE.md`
- Memory/instruction items: `52`
- Governing items: `24`
- Context-only items: `28`
- Verify-first / superseded-possible: `0` / `0`
- Action types: `48 read`, `4 execute`
- Risk: `52 low`
- Findings: `0`
- Verification gates: `0`
- Authority map categories: `7`
- Posture: `low_observed_risk`

### `BRAIN_CURRENT.md`
- Memory/instruction items: `538`
- Governing items: `118`
- Verify-first items: `16`
- Context-only items: `404`
- Superseded-possible items: `0`
- Findings: `0` after same-session false-positive fix
- Verification gates: `17`
- Authority map categories: `7`
- Posture: `usable_with_gates`

---

## Authority Map (the real deliverable today)

`CLAUDE.md` mapped into 7 categories:

- startup_source_of_truth — 14
- collaboration_rules — 8
- active_project_constraints — 7
- verification_requirements — 7
- action_tool_constraints — 4
- budget_capability_constraints — 2
- archive_access_constraints — 1

Why this matters: even with zero high-severity findings, the map shows exactly which 24 of 52 lines are allowed to *govern* the agent versus the 28 that should only *inform* it, and it separates the 48 read-only instructions from the 4 that imply execution. For a buyer, this inventory alone is the artifact they cannot easily produce by hand on a file this size — and it scales: `BRAIN_CURRENT.md` classified 538 items into the same lanes (118 governing, 16 verify-first, 404 context-only after the false-positive fix).

---

## Findings, Read Honestly

### Fixed: `BRAIN_CURRENT.md` false positives

Initial run at `8689675`: both `stale_instruction` findings (`M016`, `M049`) fired on lines containing the brand promise "Find the old instructions your AI should stop obeying." The detector matched the literal phrase "old instructions" / "stop obeying" and concluded the *thesis statement itself* was a stale instruction that should not govern. It is not stale; it is the company's active positioning.

Root cause: the stale-instruction check keys on surface vocabulary, not on whether an instruction has actually been superseded by a later one. This is a covered-pattern false positive, and it is the kind of over-match that erodes buyer trust fast if shipped uncorrected.

Same-session fix: the extractor now uses a stricter supersession marker list, and the classifier no longer treats the bare text phrase "old instruction" as enough evidence. New regression tests cover both directions:

1. A tagline/topic mention about "old instructions" is not flagged stale.
2. A real superseded rule using `Old instruction:`, `deprecated`, and `replaced by` still is flagged stale.

Verification after fix:

- Full test suite: `4 passed, 1 xfailed`
- `BRAIN_CURRENT.md`: findings moved `2 -> 0`
- `CLAUDE.md`: remains `0 findings`
- Known Path A semantic-gap test remains xfailed by design

### The real drift in `CLAUDE.md` was missed

`CLAUDE.md`'s own alignment gate records that on 2026-06-18 an old framing (a Discord-based plan, since corrected) "nearly leaked into execution." That is a textbook stale-instruction risk — a superseded plan still present in a governing file. The auditor returned 0 findings on that file. Because the superseded framing is described in prose rather than lexically tagged as "old," the Path B detector cannot reach it.

---

## Recommended Next Actions

For the workspace (as a client would receive):
1. The authority map is clean and usable; keep the 24 governing lines under deliberate review at each major change.
2. Explicitly tag the corrected 2026-06 framing as superseded in-file so any auditor (and any agent) treats it as non-governing.

For the product (the honest internal read):
1. Keep the same-session false-positive fix and regression tests.
2. This dogfood is the concrete, real-system case for **Path A** (semantic contradiction/supersession detection). The miss here is not hypothetical; it is documented in the audited file itself.
3. Ship the **authority map** as the headline deliverable now; frame findings as "covered-pattern flags, human-reviewed," not as the product's core value, until Path A exists.

---

## Limitations

This audit detects known dangerous authority patterns by covered lexical signals. It is not a complete semantic contradiction detector.

- No findings does not prove a file is safe — `CLAUDE.md` returned 0 findings and still contains a documented superseded framing.
- A finding is not proof of real staleness — the initial `BRAIN_CURRENT.md` run produced two false positives on the brand tagline before the same-session fix.

Novel or prose-described conflicts still require human review or the future Path A semantic layer before action-capable deployment.

---

## What This Worked Example Proves

- The pipeline runs end-to-end on real, messy, large instruction files (52 and 538 items) and produces a structured, buyer-legible authority map.
- The current honest product is the **map plus human-reviewed covered-pattern flags**, not an automated safety verdict.
- Dogfood improved the product: a real false positive became a narrower detector contract plus regression tests.
- The Path A semantic layer is now justified by a real, self-documented miss rather than by theory.
- Honesty is the moat: this worked example includes the initial miss, the same-session fix, and the remaining boundary instead of pretending the tool was already complete.
