# Path A — Semantic Authority-Change Layer — Pre-Registration
Date: 2026-07-01
Status: FROZEN PRE-REGISTRATION (frozen before Path A fixtures, implementation, and results).
Repo: memory-authority-auditor

## Why this exists (the motivating failure, self-documented)

The deterministic detector cannot tell an instruction that *has been superseded* from a sentence that merely *talks about supersession*. We watched this live twice on our own files:
1. It flagged the brand slogan "find the old instructions your AI should stop obeying" as a stale instruction (topic mention of "old instructions").
2. After we tightened the rule to require the word "superseded," the `2026-07-01` block we wrote into BRAIN_CURRENT.md — which *describes* the fix — tripped the detector on the word "superseded."

Every lexical patch shrinks the false-positive circle without closing it. That is the enumeration trap our own CLAIM series was built to expose. The distinction is semantic, so the fix must be semantic.

## The claim being pre-registered

A **proposer + deterministic-confirmer** layer can identify authority-change relations between instructions (one rule superseding, narrowing, contradicting, or transferring authority from another) that lexical detection misses, AND avoid firing on prose that only discusses those concepts, by:
- requiring every proposal to CITE the specific other instruction involved, and
- confirming that citation deterministically against the file, and
- routing anything it cannot confirm to `needs_human_judgment` instead of asserting it.

Success is measured the way Marcus Kim named it: does it shorten a careful human review WITHOUT hiding uncertainty. A clean pass is never treated as a safe verdict.

## Architecture (domain-general by design)

1. **Proposer (LLM — tiered: Anthropic Sonnet, local llama3.2 fallback).** Reads item pairs / the item set and proposes candidate authority-change relations. It is NOT hardcoded to supersession; it reasons generally about whether one instruction changes another's authority. Output for each proposal: `{type, source_item_id, target_item_id, cited_evidence_span, rationale, confidence}`. The LLM never emits a verdict; it proposes.
2. **Deterministic confirmer (the judge).** For each proposal, verifies deterministically: (a) the cited target item actually exists in the file, (b) the cited evidence span actually appears in the source item, (c) source and target overlap in scope. Only confirmed proposals become findings. This is the LLM=interpreter / deterministic=judge pattern (same as the Gino gate).
3. **Uncertainty surface.** Proposals the confirmer cannot verify (hallucinated citation, no scope overlap, low confidence) go to `needs_human_judgment` with the reason. Never silently dropped, never silently asserted.

## Scope discipline (broad engine, bounded claim)

- The ARCHITECTURE is general. The VALIDATED CLAIM for v0 is bounded to the pre-registered contradiction classes below, tested on a held-out set with known labels. We only claim what we tested; we widen with receipts.

### v0 contradiction classes (frozen)
1. **Supersession** — a later instruction replaces/deprecates an earlier one.
2. **Scope-narrowing** — a later instruction restricts an earlier grant.
3. **Direct contradiction** — two instructions give opposing directives on the same subject.
4. **Authority transfer** — decision/approval authority moves from one party to another.
5. **Topic-mention NEGATIVE class (must NOT fire)** — prose discussing supersession / contradiction / old instructions as a subject, including self-referential meta-text like our own BRAIN_CURRENT block. This class is the whole reason Path A exists; if it fires here, v0 fails.

## Held-out test discipline

- Authored test files with KNOWN answers, frozen before any run. NOT our own live workspace files (that would be adversarial narcissism / the enumeration trap).
- Each positive case names the exact source/target pair the confirmer must verify.
- The negative (topic-mention) cases are authored to look lexically tempting but carry no real authority-change relation.

## Pre-registered success criteria

- Catches the pre-registered positive relations (per class) with cited, confirmable evidence.
- Does NOT fire on the topic-mention negative class.
- Every finding carries a confirmed citation; zero findings without a verifiable citation.
- Unconfirmable proposals appear in `needs_human_judgment`, never as findings.
- Beats the lexical baseline (current detector) on the held-out set on both false positives and misses.
- Does not flood: review surface stays bounded to real signal.

## Pre-registered ablations (each must fail in the predicted way)

- Remove the confirmer → proposer alone over-fires (hallucinated / uncited relations leak).
- Remove the evidence-citation requirement → fabricated supersessions pass.
- Remove the uncertainty surface → unverifiable proposals become false confident findings.
- Local-fallback-only (no Sonnet) → measure and RECORD proposal degradation; do not hide it.

## Pre-registered failure conditions (we say so if these happen)

- If proposer+confirmer cannot beat the lexical baseline on the held-out set, Path A v0 fails.
- If it cannot avoid the topic-mention negatives, v0 fails (that was the entire point).
- If proposals cannot be reliably confirmed against cited evidence, the citation contract is wrong and must be redesigned before any claim.

## Boundary

Internal v0, class-limited. The general architecture is a design bet, not a proven general capability. No claim of complete semantic contradiction detection. No client-facing "safe" verdict. The deterministic Path B layer remains the floor; Path A adds proposed-and-confirmed findings on top, with uncertainty always visible.

## Engine note

Tiered: Anthropic Sonnet as primary proposer, local llama3.2 as fallback (credit-tight / sovereignty). Fallback degradation is a measured variable, not a hidden one. Requires an Anthropic key wired for the Sonnet path (pending).
