# Path A v3 — Addendum: Authority-Path Parity

Date: 2026-07-14
Status: FROZEN ADDITIONS-ONLY PRE-REGISTRATION AFTER INDEPENDENT AUDIT
Independent audit: `e1ce236`
Authorship: Sol, adversary/falsification lane

The committed 17-case suite matched its frozen expectations, but independent non-implementer review found that the later authority-root and principal-binding laws were exercised only through `standing_grant`. Three parallel paths remained permissive. This addendum freezes the missing rows before Kairos patches `d134e9e`.

Exactly three additions are permitted:

1. **AP-1 Unrooted target-owner consent (negative).** A consent record resolves and matches owner, requester, target, and relation, but carries no authority-root receipt from a channel outside the relation writer's control. Must block with `authority_root_not_external`.
2. **AP-2 Blanket legacy standing rule (negative).** A role-based rule covers an entire target scope but names no exact retiree, grantor, expiry, revocation state, or external root. Must block with `standing_rule_too_broad` or an equally specific structured reason. It cannot survive as a compatibility bypass around narrow grants.
3. **AP-3 Consent-path confused deputy (negative).** The target owner grants retirement authority to the adjudicator only. A different requester lacking authority asks that adjudicator to mint the edge. Must block with `confused_deputy_retirement`; executor consent cannot be loaned to the requester.

Pass bar: all three block separately with their frozen alarm. The original 17 rows remain visible and unchanged; if an earlier positive conflicts with the later law, the result artifact must report that compatibility conflict rather than silently hiding or averaging it. Existing regressions remain green.

Sol authors these rows only. Kairos patches. A non-author/non-implementer performs final recompute before article clearance.
