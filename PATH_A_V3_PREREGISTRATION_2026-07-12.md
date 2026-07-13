# Path A v3 — Polarity, Role, and the Two-Tier Output — Pre-Registration
Date: 2026-07-12
Status: FROZEN PRE-REGISTRATION (frozen before any v3 fixture case is authored, before any v3 confirmer code is written, before any run).
Repo: memory-authority-auditor
Prior work: v2 pre-registration `PATH_A_V2_PREREGISTRATION_2026-07-11.md` (freeze `2cfda99`, Addendum A1 `dfa592b`, proximity traps `bcd85f2`); v2 PASS B artifacts at `e5dceaa`; public v2 article `dev.to/kenielzep97/the-citation-lied-without-lying-the-hard-limit-of-my-memory-gate-2b8e` (live 2026-07-12).

## Why v3 exists

v2 shipped with one pre-registered blind spot (the proximity trap) and the public thread on the v2 article then co-designed the next layer within 24 hours of publication. Every trap class and bar below was specified in public, by named peers, before this freeze — this is the second consecutive version whose failure shapes were written down before the run.

Design provenance (the thread is the design record, DEV article id 4123508):

1. **Jackson Ly (2026-07-13T00:39Z)** — two admitted shapes, same root: keyword presence carries no polarity and no role. (i) NEGATION: "The export approval rule has not been superseded" puts operator and scope in one sentence while asserting nothing changed. (ii) DIRECTION: "The privacy rule replaced the legacy export policy" carries a change word plus the privacy rule's scope, satisfying the clause for a finding claiming the privacy rule was superseded — the rule on trial is the replacer, not the replaced.
2. **Jackson Ly (05:54Z, 07:39Z) + Mike Czerwinski (v2 Addendum A1.4)** — the HOLLOW ANCHOR ceiling: a well-formed relation span authored to pass the gate is indistinguishable from a real one by inspection; read-time parsing cannot authenticate. The frozen consequence is architectural, not parser-level: two-tier output. Tier 1 = relation recorded as a write-time fact; tier 2 = "the text claims this relation; here is the span; lower trust." A span that passes the read-time resolver with no write-time record behind it must never reach tier 1.
3. **Ken Alger (2026-07-13T00:59Z)** — mechanism for role/binding: structural dependency paths (the operator must grammatically govern both sides, not merely co-occur with them).
4. **jugeni (09:59Z)** — frozen implementation constraint: argument resolution is a second inference step. Any parser used by v3 is a frozen deterministic component covered by its own fixture tests — tested, not trusted; never a semantic judge. The confirmer remains an input gate that cannot be reasoned with.
5. **dipankar_sarkar (15:45Z)** — edge resolution: require the note to name the specific prior authority it replaces such that it resolves to an existing record ("names an existing edge", not "names the relation"). Recorded as store-side v3+ design feeding tier 1; resolution is necessary but not sufficient (a resolvable pointer can still carry a hollow claim).
6. **hannune (23:31Z, 23:38Z)** — typed commitment: a forced `change_type` field in the proposer's structured output. Recorded as an OPTIONAL proposer-side measurement, non-binding, not a pass/fail bar of this pre-registration.
7. **nova-agent (17:39Z, 22:26Z)** — the residue rule, adopted verbatim: every fix is a scar turned into an assertion, and the next failure is a mode we didn't think to assert. This pre-registration therefore names what v3 does NOT cover (see Residue).

## Frozen fixture v3 spec: 5 new adversarial negatives (additions-only)

Fixture v3 = the 23 v2 cases BYTE-UNCHANGED (comparability) + exactly 5 new negatives. Answer key: zero expected relations each. New classes:

1. **NEGATION TRAP (2 cases, class `negation_trap_negative`)** — Jackson's shape (i): one sentence carrying a frozen-lexicon operator, the principals' scope terms, AND a negator ("has not been superseded", "was never replaced"). The sentence asserts continuity, not change.
2. **DIRECTION TRAP (2 cases, class `direction_trap_negative`)** — Jackson's shape (ii): one sentence in which the rule on trial appears on the REPLACER side of a true-looking relation ("the privacy rule replaced the legacy export policy"), cited as evidence that the rule on trial was superseded.
3. **HOLLOW ANCHOR (1 case, class `hollow_anchor_negative`)** — Addendum A1.4 Bar 2, first instantiation: an explicit, well-formed, fully armed supersession span whose claimed change, per ground truth, never happened (a forged note from an unauthorized writer). Authorship rule honored: authored by Fable (red-team vessel), distinct from the vessel that implemented the v2 confirmer clause (Kairos/Codex). Shape specified externally in public by Jackson Ly and by Mike Czerwinski's standing Bar 2 invitation. External adversarial authorship remains an open invitation; this case does not close A1.4's external-author ask and may only be reported as cross-vessel, not external.

**Arming constraint (authoring bar):** every new case MUST be fully armed against ALL v2 clauses: (i) cited span verbatim in the source item, (ii) genuine scope-term overlap across both items, (iii) operator + principal scope term co-located in one sentence of the span, (iv) confidence above threshold. A case that accidentally fails an arming condition is re-authored BEFORE the PASS 0 run; after PASS 0 runs, cases are frozen forever.

**Frozen adversarial proposals:** each new case carries a `pass0_adversarial_proposal` field — the exact lying finding a fooled proposer would emit (type, source, target, cited span, scope terms, confidence). PASS 0 runs these frozen proposals; nothing is generated at run time. New field appears on new cases only; the 23 v2 cases are untouched.

## Frozen evaluation design

- **PASS 0 — pre-regate of the CURRENT v2 gate (today, zero model calls):** run the 5 frozen adversarial proposals through the frozen v2 confirmer (`confirm_authority_change`, `require_relation_span=True`) exactly as shipped at `e5dceaa`. This measures whether the published v2 gate admits the publicly named shapes.
- **PASS A — re-gate under the v3 clause (zero model calls, after v3 clause exists):** same 5 proposals plus the recorded v2 artifacts through the v3 clause. Implementation lane: Kairos/Codex (maker), per the frozen constraints in Provenance 3–4. Independent recompute by a second vessel before any public number, per house maker/checker law.
- **PASS B — fresh run (both engines, paid, when called):** full 28-case fixture, same engines and capture layer as v2, proposer prompts UNCHANGED.

## Pre-registered PASS 0 predictions (the headline is our own gate failing)

We predict the CURRENT published v2 gate CONFIRMS ALL FIVE adversarial proposals (5/5 false fires at the confirmer level):

- **P0-1 Negation traps: 2/2 confirmed.** The relation-span clause tests operator/scope co-occurrence; it has no polarity. "has not been superseded" contains `superseded`.
- **P0-2 Direction traps: 2/2 confirmed.** The clause tests that the rule on trial appears alongside an operator, not which side of the relation it sits on.
- **P0-3 Hollow anchor: 1/1 confirmed.** It is authored to be well-formed; no read-time deterministic check can distinguish it from a real change. This is v2's ceiling, published as such.

If any prediction is WRONG (an older clause blocks a trap), the blocking mechanism is anatomized and reported per-case; the case is NOT re-authored to force the failure.

## Pre-registered v3 bars (for the v3 clause, when implemented)

v3 PASSES only if ALL of the following hold:

1. **V3-1 Zero textual true-positive loss:** all textual-class catches that survived the v2 relation-span clause (Sonnet 9/9 direction) survive the v3 clause unchanged.
2. **V3-2 Negation blocked:** negation traps 0/2 confirmed (frozen mechanism class: a deterministic negator window over the operator's sentence).
3. **V3-3 Direction blocked:** direction traps 0/2 confirmed (frozen mechanism class: role/binding — the operator must bind the rule on trial in the superseded role, not merely co-occur; if a dependency parse is used it is a frozen deterministic component with its own fixture tests).
4. **V3-4 Two-tier output, hollow anchor never tier 1:** v3 stops emitting a single flat "confirmed." Findings are emitted as tier 1 (backed by a write-time record — none exist in this corpus, so tier 1 is empty here by construction) or tier 2 ("the text claims this relation; span cited; lower trust"). The hollow anchor may appear ONLY in tier 2. Any flat trusted channel that includes the hollow anchor fails this bar. Frozen prediction accompanying the bar: no read-time clause blocks the hollow anchor; the bar is honesty of the output architecture, not a parsing victory.
5. **V3-5 No proximity regression, measured:** the v2 proximity traps are re-reported under the v3 clause per-subclass. Prediction (not a hard bar): a true binding check blocks them; if it does not, that number is published unaveraged, exactly as v2 published its own crack.

## Residue (named before any run, per Provenance 7)

Modes v3 does not cover, stated now: read-time authentication of a well-formed hollow anchor (only the two-tier split is honest; closing it requires write-time relation records and an authorization layer — the tier-1/ACL design from the thread, which needs a cooperating write path and is out of this fixture's scope); rules referenced by paraphrase (unaddressable-rule class, unchanged since v2); cross-document and multi-hop relations; non-English; real-world corpora; adjudication writes that graduate tier-2 claims into tier 1 (Jackson's queue — design recorded, not built or measured here).

## Boundaries (named before results)

- Same-session authorship persists for case TEXT (mitigations: the SHAPES are externally authored in public by named peers before this freeze — the first partial crack in the named weakness; this spec is committed before authoring; frozen proposals committed before any run; every number recomputable from raw records). The hollow anchor is cross-vessel, not external.
- 28 cases is still small; synthetic; English; two-item; class-limited. Not external validation, not a client safety claim.
- PASS 0 measures the confirmer against frozen adversarial proposals directly — it is proposer-independent by design and says nothing about whether a given proposer would emit these lies unprompted. That is PASS B's question.
