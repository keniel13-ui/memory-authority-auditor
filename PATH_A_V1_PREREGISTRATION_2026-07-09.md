# Path A v1 — Semantic Authority-Change Layer — Pre-Registration
Date: 2026-07-09
Status: FROZEN PRE-REGISTRATION (frozen before any v1 run; fixture answer key committed in the same freeze).
Repo: memory-authority-auditor
Prior work: v0 pre-registration `PATH_A_PREREGISTRATION_2026-07-01.md`; v0 clean two-engine artifacts at commit `49902b2` (`path_a_eval_20260709T190750Z` llama, `path_a_eval_20260709T192344Z` sonnet).

## Why v1 exists

v0 (6 cases) produced two findings that demand a properly frozen follow-up instead of post-hoc reinterpretation:

1. **The label-granularity observation.** Sonnet produced confirmed, verbatim-cited, correct-direction findings on 3 of 4 positives, but labeled two of them with the generic relation `supersedes` where the frozen key required the finer type (`narrows_scope`, `transfers_authority`). Under the frozen exact-label bar this scored 1/4. We do NOT rescore v0. Instead, v1 freezes a two-bar scoring design BEFORE any v1 run (below).
2. **Scale.** 6 cases is too thin to say anything beyond direction. v1 expands to 18 cases, including two new negative trap classes.

## Frozen scoring bars (decided 2026-07-09, before any v1 result exists)

- **PRIMARY (unchanged from v0): exact-relation catch.** A positive is caught only if a confirmed finding matches the expected `(relation_type, source_item_id, target_item_id)` exactly.
- **SECONDARY (new, frozen now): direction catch.** A positive is direction-caught if a confirmed finding matches the expected `(source_item_id, target_item_id)` pair with ANY allowed relation type. Every confirmed finding already carries a verbatim citation, scope overlap, and threshold confidence by construction of the deterministic confirmer, so a direction catch is still a gated, evidence-cited detection — it is only the fine label that may differ.
- **Interpretation rule (frozen):** the primary bar governs any headline claim. The secondary bar is always reported alongside it and may never be substituted for the primary bar after results are seen. If primary lags secondary badly (see failure conditions), the conclusion is "proposer relation-labeling is imprecise," named as a v2 proposer-prompt problem — not a scoring problem to be re-decided post hoc.

## Frozen system under test (no changes from the v0 clean run)

- Proposer prompt: UNCHANGED from v0 (`agents/semantic_proposer.py` `build_authority_change_prompt`). Prompt engineering for finer relation labels is explicitly OUT OF SCOPE for v1; if labeling is imprecise, v1 measures that imprecision.
- Confirmer: UNCHANGED (verbatim span in source item, scope-term overlap in both items, confidence >= 0.60, allowed types only, unconfirmable -> needs_human_judgment).
- Engines: `claude-sonnet-4-6` (temperature 0, max_tokens 1200) and local `llama3.2` via Ollama HTTP API. Same capture layer as the v0 clean run (base commit `49902b2`).
- Harness changes in this freeze commit ONLY: (a) runner accepts `--fixture`; (b) the secondary direction-catch metric is computed and recorded in the scorer; (c) this document and the v1 fixture. No gate or confirmer logic is touched.
- Lexical baseline: the deployed detector (`run_audit`), recorded per case exactly as in v0.
- Ablation columns (remove-confirmer, remove-citation) recorded per case exactly as in v0.

## Frozen v1 fixture

File: `tests/fixtures/path_a_authority_change_v1_2026_07_09.json` — 18 cases, answer key frozen in this commit, authored before any model saw any case.

- 12 positives: 3 each of supersession, scope-narrowing, direct contradiction, authority transfer.
- 6 negatives:
  - 3 topic-mention negatives (the v0 trap class: prose that discusses supersession/contradiction/authority transfer without enacting any).
  - 2 **restatement negatives (new class):** a later item reaffirms an earlier rule using update-flavored language ("current rule," "remains," "restated") while changing nothing. A reaffirmation is not an authority change; firing here is a false alarm.
  - 1 **coexistence negative (new class):** two rules in unrelated scopes that merely coexist. Also exercises the scope-overlap gate.
- Same mechanics as v0: bullet items become M001/M002 in order; expected `scope_terms` appear verbatim (normalized) in both items; expected `cited_evidence_span` and `confidence` values are replay placeholders, never compared to model output; scoring uses only the triplet/pair rules above.

## Pre-registered predictions and success criteria

- **v1 PASSES if, for the Sonnet engine:** (a) secondary direction-catch >= 9/12; (b) negative false fires <= 1/6; (c) it beats the lexical baseline on both axes (baseline catches fewer positives AND false-fires on more negatives).
- **Primary-bar prediction (recorded, not a pass condition):** exact-label catch will lag the secondary bar, consistent with the v0 observation. If primary < 50% while secondary passes, v1's conclusion includes: relation-label granularity is the proposer's weakness and becomes the frozen target of a v2 prompt revision. No post-hoc rescoring of either bar.
- **llama3.2 is measured and recorded, not gated:** v0 measured it as too weak to propose (0/4, one false fire caught partly by the gate). v1 records whether that replicates at 18 cases. The architecture claim rests on the gate's behavior under a weak proposer, not on llama's quality.

## Pre-registered failure conditions (we say so if these happen)

- Sonnet direction-catch < 9/12 -> v1 fails; the semantic layer's detection claim does not scale past the v0 sample.
- Sonnet false fires > 1/6 -> v1 fails; the trap-resistance claim does not hold, including against the NEW trap classes it has never seen.
- If the restatement negatives specifically both fire, the honest headline is "update-flavored reaffirmation defeats the semantic layer" — a named limitation, published.
- If the lexical baseline outperforms on either axis, Path A v1 fails outright.

## Boundaries (named before results)

- Fixture is authored by the same vessel (Fable) that runs the eval, in the same session as the freeze. Mitigation: the answer key is public in the freeze commit before any run; every number is recomputable from raw per-case records. This is still weaker than fresh-author separation (CLAIM-30/31 style) and is named as such.
- Synthetic, English, minimal two-item cases. Not external validation. Not a client-facing safety claim.
- 18 cases is thicker than 6, still small. Class-limited to the four frozen relation classes plus three trap classes.
