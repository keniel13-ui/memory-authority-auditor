# Path A v2 — The Relation-Span Gate — Pre-Registration
Date: 2026-07-11
Status: FROZEN PRE-REGISTRATION (frozen before any v2 run, before any new fixture case is authored, before any confirmer code is written).
Repo: memory-authority-auditor
Prior work: v1 pre-registration `PATH_A_V1_PREREGISTRATION_2026-07-09.md` (freeze `bd83001`); v1 artifacts `path_a_eval_20260709T202859Z` (commit `36f5771`); v0 artifacts at `49902b2`.

## Why v2 exists

v1 left exactly one confirmed hole, and it was then diagnosed structurally in public:

1. **The citation-shaped lie (v1's named slip).** Under the frozen v1 gate, llama3.2's one surviving false fire dressed a false `supersedes` in a verbatim quote with genuine scope overlap. True inputs, false entailment. Every deterministic check passed; the semantic step that failed was never gated.
2. **The public diagnosis (Mike Czerwinski, DEV thread on the Path A article, 2026-07-10/11).** "You can't deterministically gate an inference. You can only gate its inputs." Proposed plank: require the relation itself as a quoted span. Our fixture check (posted in reply, verified against the frozen v1 fixture before answering): restatement and coexistence traps carry zero relational language — the plank collapses them; but topic-mention traps contain strong relational verbs verbatim (documents ABOUT supersession), so a bare verb requirement re-arms them; and all three contradiction positives carry no relation span at all.
3. **The recovery (Mike's second reply).** Use vs mention is decidable by ARGUMENT RESOLUTION: the relational verb's arguments must resolve to exactly the two rules on trial. "The turf is decidable to the precise depth that your rules are addressable, no further." The number that falls out of a textual/implicit split "is a property of your rule corpus, not a score on your gate."

v2 freezes that design and measures it. This pre-registration was co-designed in public with a named peer before any result existed; the thread is the design record.

## Frozen new mechanism: the RELATION-SPAN CLAUSE (confirmer addition)

Applied ONLY to cases frozen as class TEXTUAL (list below). A confirmed finding on a textual case must additionally satisfy, decidably (token lookup, not reading):

- **(a) Operator present:** the cited evidence span contains at least one operator from the FROZEN RELATIONAL LEXICON: `replace, replaced, replaces, retire, retired, retires, deprecate, deprecated, supersede, supersedes, superseded, override, overrides, overridden, discontinue, discontinued, revoke, revoked, no longer, instead, only, now` (case-insensitive; multiword operators matched as phrases).
- **(b) Argument binding (the sentence test):** within the span, at least one sentence must contain BOTH (i) a frozen lexicon operator AND (ii) at least one expected `scope_term` of the case. This is the decidable approximation of "the verb's arguments resolve to the principals on trial": a changelog's "v1 supersedes v0" names v0/v1 — not the principals' scope — and fails; "the old retention rule is replaced: nightly backups are kept for 90 days" carries the operator and the principal scope in one sentence, and passes.
- **(c) Existing v1 clauses unchanged:** verbatim span in source item, scope-term overlap in both items, confidence >= 0.60, allowed types only.

Cases frozen as class IMPLICIT are NOT subject to the relation-span clause. Their findings are routed to a frozen lower-trust tier: output rows carry `relation_textual: false` and the report labels them **proposer-only, semantically inferred, not span-anchored**. This is the honest architecture from the thread: gate the textual class, name the implicit class, never quietly pass an inference on the proposer's word.

## Frozen class split of the v1 fixture (decided now, before any v2 run)

Applying the sentence test to the frozen v1 answer-key spans BY HAND, before any code exists:

- **TEXTUAL (9):** `supersession_backup_retention` (replaced), `supersession_api_key_rotation` (retired, now), `supersession_sync_notes_location` (deprecated, instead), `scope_narrowing_refund_limit` (only), `scope_narrowing_prod_db_access` (only), `scope_narrowing_social_posting` (only), `transfer_incident_severity` (no longer, only), `transfer_purchase_approval` (now), `transfer_article_signoff` (now).
- **IMPLICIT (3):** all three contradiction positives (`contradiction_logging_pii`, `contradiction_friday_deploys`, `contradiction_vendor_contact`) — their spans state the new rule flatly; no relational operator exists. Genuine implicit supersession has no span to quote. This 9/3 split is recorded as a property of THIS corpus.

## Frozen fixture v2 spec: 3 new MENTION-DRESSED-AS-USE traps

Fixture v2 = the 18 v1 cases UNCHANGED (comparability) + exactly 3 new negatives of the class Mike predicted the next lie lives in. Frozen authoring spec (cases to be authored to this spec and committed before any v2 run; answer key = zero expected relations each):

1. **Changelog trap:** a document whose second item is a version-history note containing a strong operator with non-principal arguments ("v2.1 superseded v2.0 for the archive exporter") while sharing genuine scope terms with the first item. The operator sentence must NOT contain the principals' expected scope terms — it names versions, not the rules on trial.
2. **Meeting-minutes trap:** minutes reporting that some OTHER team's rule "was replaced last quarter," sharing topic vocabulary with the first item but with the operator sentence referencing the other team's rule, not the principal.
3. **Quoted-rule trap:** an item quoting an old draft inside quotation marks ("the draft read: 'this policy supersedes all prior guidance'") where the operator lives inside a quote-within-a-quote about a hypothetical/dead document.

Authoring constraint: each trap MUST carry genuine scope-term overlap with its sibling item (so the v1 gate alone would be armed) and MUST fail the sentence test (operator sentence lacks principal scope terms). If an authored trap accidentally passes the sentence test, the case is re-authored BEFORE any run; after the first run, cases are frozen forever.

## Frozen evaluation design

Two measurement passes, both count:

- **PASS A — re-gate (no model calls):** apply the relation-span clause to the RECORDED v1 artifacts (`path_a_eval_20260709T202859Z`, both engines): every v1-confirmed finding on a textual case is re-checked against clauses (a)+(b). This measures what the new clause would have blocked or lost on frozen, already-public data.
- **PASS B — fresh run (both engines, when credits/time allow):** full 21-case fixture v2, same engines and capture layer as v1 (`claude-sonnet-4-6` temp 0; `llama3.2` via Ollama HTTP), proposer prompts UNCHANGED (still the v0 prompt — label granularity remains measured, not engineered), lexical baseline recorded per case, ablation columns recorded per case plus a new ablation: remove-relation-span-clause.

## Pre-registered predictions and success criteria

v2 PASSES only if ALL of the following hold:

1. **Zero textual true-positive loss (PASS A):** the relation-span clause blocks NONE of Sonnet's 9 textual-class v1 direction-catches. (Prediction: 0 lost; the clause tightens against lies, not against true catches.)
2. **The v1 slip becomes impossible in class (PASS A):** llama's citation-shaped false fire, re-gated, is BLOCKED by the clause (its restatement span contains no lexicon operator in a scope-bearing sentence). Frozen claim tested: on textual-class cases, a citation-shaped lie without a span-anchored relation cannot survive the confirmer regardless of proposer.
3. **New trap class blocked (PASS B):** mention-dressed-as-use traps produce 0/3 confirmed false fires per engine.
4. **Old trap classes stay blocked (PASS B):** restatement + coexistence + topic-mention negatives produce 0 confirmed false fires for Sonnet (<= 1 total for llama, recorded).
5. **Continuity bars re-reported (PASS B):** v1's primary (exact-label) and secondary (direction) bars recomputed on the 12 positives and reported alongside — never substituted, never rescored.

## Pre-registered failure conditions (we say so if these happen)

- Any textual true positive lost to the clause -> "the binding requirement over-tightened" — published as the headline, with the lost case anatomized.
- Any mention-dressed-as-use trap confirmed -> Mike's residue found its next slip past the decidable floor — published, span anatomized, exactly as the v1 slip was.
- If the implicit class (3 contradictions) is where an engine's only catches land, the honest headline is that this corpus's hardest changes live beyond the gate's turf — the corpus number, not a gate victory.

## The authoring-side commitment (named deliverable, separate from this eval)

From the thread: addressability is a property we can engineer. The auditor product gains a finding class — **unaddressable rule**: a rule that cannot be referenced by a stable anchor cannot be protected by any deterministic relation gate, and the owner hears that before the lie arrives, not after. Deliverable scoped for after the v2 run; not a pass/fail condition of this pre-registration.

## Boundaries (named before results)

- Same-session, same-vessel fixture authorship persists for the 3 new traps (mitigation: this frozen spec is public before authoring; answer keys public before any run; every number recomputable from raw records). Weaker than fresh-author separation; named.
- Synthetic, English, minimal two-item cases; 21 cases is still small; class-limited. Not external validation, not a client-facing safety claim.
- The sentence test is an approximation of argument resolution — real-world rules referenced by paraphrase remain outside the decidable turf, exactly as the thread concluded: decidable to the depth the rules are addressable, no further.

---

## PRE-RUN ADDENDUM 1 (2026-07-11 evening — frozen before any code, fixture case, or run exists)

Source: Mike Czerwinski's fourth reply on the public thread, arriving after the freeze commit `2cfda99` and before any implementation. Precedent: the v1-era pre-code schema ruling (`PATH_A_SCHEMA_RULING_2026-07-01.md`) — pre-run amendments are legitimate only as logged, dated additions. **Nothing below changes an existing bar; everything below adds measurement, trap classes, and predictions.**

### A1.1 The textual class splits again: STRONG-BIND vs PROXIMITY-BIND

Mike's cut, accepted: an operator sharing a sentence with principal scope terms is proximity, not binding, and proximity has a false-arm the strong tier doesn't. Frozen sub-classification of the 9 textual cases, by hand, before any run:

- **STRONG-BIND (3):** the three supersessions — a relational verb whose grammatical arguments resolve to the principals ("the old retention rule is replaced: …").
- **PROXIMITY-BIND (6):** the three narrowings and three transfers — operator (`only`, `no longer`, `now`) co-sentenced with principal scope terms, but the operator's argument structure is not itself resolved to the pair on trial.

**Frozen reporting rule:** every v2 result table reports strong-bind and proximity-bind columns separately. A proximity false-arm may never be averaged into a flat "textual class" number. Nine that gate is two numbers.

### A1.2 New trap class 4: the PROXIMITY TRAP (fixture spec addition)

Two authored negatives of Mike's exact shape: one sentence carrying BOTH principals' scope terms AND a lexicon operator, where the operator scopes one principal to something else entirely and no relation between the principals is asserted ("A applies only to X; B is separate and unchanged"). Answer key: zero expected relations. Fixture v2 total becomes 23 cases (18 v1 + 3 mention traps + 2 proximity traps).

### A1.3 Frozen prediction: our own clause cracks here, and we say so in advance

The sentence test as frozen above arms on co-occurrence. **We predict the proximity traps expose it:** if a proposer fires on a proximity trap, the frozen sentence test at the confirmer level will NOT block it (prediction: 0/2 blocked by clause (b) alone; blocking, if any, comes only from the older clauses). If that happens it is published as the v2 finding — "the proximity tier is where the citation-shaped lie relocates" — and true argument-resolution (operator arguments, not co-occurrence) becomes the frozen v3 target. If the prediction is WRONG and the traps are blocked, the mechanism that blocked them is anatomized. Either way the number is reported per-subclass, never averaged away.

### A1.4 The authoring deliverable now carries TWO frozen bars (liveness ≠ coverage)

Mike's split, accepted verbatim: a canonical known-bad proves the auditor is not-dead; it does not prove it is not-blind.

- **BAR 1 — LIVENESS:** one canonical real implicit supersession in the auditor's fixture that must STAY flagged under every configuration. The canary.
- **BAR 2 — ADVERSARIAL COVERAGE:** at least one hollow anchor — an explicit supersession span bolted onto an actually-implicit relation, **authored by someone trying to pass the gate, not drawn from the honest fixture** — that the auditor must still flag. An adversarial object cannot come from honest-fixture authorship by definition. Frozen authorship rule: the hollow-anchor case(s) must be authored by a party OTHER than the vessel implementing the auditor — a different vessel red-teaming, or an external peer. (Mike Czerwinski is invited on the public thread to author it himself; external adversarial authorship would also be the first crack in this project's named same-session-authorship weakness.)

Only Bar 2 earns the phrase "rubber-stamp-proof." Bar 1 alone may never be reported as more than liveness.
