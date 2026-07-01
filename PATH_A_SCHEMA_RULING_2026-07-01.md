# Path A Schema Ruling

Status: binding implementation clarification, not a preregistration edit.

Date: 2026-07-01

Context: Fable reviewed the Path A proposer brief before implementation and caught a schema mismatch between the frozen preregistration and the existing deterministic confirmer.

## Ruling

The frozen preregistration controls.

`PATH_A_PREREGISTRATION_2026-07-01.md` already says the confirmer must check that the cited evidence span appears in the source item. The current code drifted from that by using `required_evidence_terms`.

This ruling fixes code to preregistration. It does not change the frozen claim, classes, success criteria, or failure criteria.

## Final Proposal Schema For V0

Each proposer output must use:

```json
{
  "type": "supersedes | narrows_scope | contradicts | transfers_authority",
  "source_item_id": "M001",
  "target_item_id": "M002",
  "cited_evidence_span": "verbatim substring from the source item",
  "scope_terms": ["shared", "scope"],
  "rationale": "short explanation",
  "confidence": 0.72
}
```

## Deterministic Confirmation Contract

A proposal becomes a finding only if all of these hold:

1. `type` is one of the four v0 relation types.
2. `source_item_id` exists.
3. `target_item_id` exists.
4. `cited_evidence_span` is present, non-empty after normalization, and appears as a substring of the source item text after normalization.
5. `scope_terms` contains at least one term that appears in both source and target item text.
6. `confidence >= 0.60`.

If any check fails, route the proposal to `needs_human_judgment` with the reason. Do not silently drop it and do not assert it as a finding.

## Confidence Threshold

The v0 threshold is frozen before evaluation:

```text
confidence < 0.60 -> needs_human_judgment
confidence >= 0.60 -> eligible for deterministic confirmation
```

This number is not a claim that confidence is calibrated. It is a routing threshold for v0 evaluation. It cannot move after seeing results.

## Negative Class Boundary

The deterministic confirmer does not prove relation truth. It verifies citation integrity and local scope overlap.

Topic-mention negatives are therefore a proposer-evaluation requirement:

- A correct proposer should not propose an authority-change relation for prose that only talks about supersession, contradiction, narrowing, or authority transfer.
- If a bad proposer emits a valid-looking topic-mention proposal with a present span and overlapping scope, the confirmer may confirm it.
- Do not claim the deterministic layer protects the negative class by itself.

## Key Handling Boundary

The proposer may read `ANTHROPIC_API_KEY` only from the runtime environment.

It must not:

- open a `.env` file by hardcoded path;
- reference `head-agent/.env` in committed code;
- print environment variables;
- log request headers;
- commit keys or runtime secrets.

If `ANTHROPIC_API_KEY` is not present in the runtime environment, fall back to the local path and record that the run was fallback-only.

## Evaluation Discipline

Kairos may create a separate dev scratch fixture set for prompt/interface iteration.

The frozen fixture packet from `123f720` is not a tuning surface. It should be used as a recorded evaluation event, not as the loop Kairos optimizes against.

Ka'el's independent checker pass should still include fresh never-seen cases after Kairos writes the implementation result.
