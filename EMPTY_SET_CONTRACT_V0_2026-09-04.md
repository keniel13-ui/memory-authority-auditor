# EMPTY SET CONTRACT v0 — 2026-09-04

**Author:** Ka'el / Claude, PHASE 1590. **Owner:** Keniel Maldonado.
**Scope:** the live 500 only. The heading-swallow and length-floor repairs are OUT of this diff.

## Provenance disclosure (required by Method Doctrine 3)

**Code already exists.** This contract is written against `beae0bb`, which is deployed. It does
**not** claim contract-before-code provenance for the existing pipeline. It claims it only for the
change described below, which is unwritten as of this hash.

## The defect being fixed

Observed live 2026-09-04, `USE_REMOTE_AGENTS=1`:

| Step | Behavior |
|---|---|
| `memory-extractor-agent` given `## Never deploy without human approval` | **HTTP 200** `{"items": []}` — correct |
| `authority-classifier-agent` given `{"items": []}` | **HTTP 400** |
| `conflict-detector-agent` given `{"items": []}` | **HTTP 400** |
| `authority-mapper-agent` given `{"items": []}` | **HTTP 400** |
| web router (`app.py` `do_POST` catch-all) | wraps the 400 as **HTTP 500** |

Root cause, `agent_service.py:27-62`: five roles `raise ValueError` when `items` or
`classifications` is empty. `do_POST` catches **every** exception and returns 400 regardless of
kind. An empty extraction is a legitimate result, not a malformed request.

This is the project's own failure class: **an absent population treated as an error rather than a
finding.**

## The contract — four rows. Rows do not move after the hash.

| # | Rule | Observable |
|---|---|---|
| R1 | An empty `items` list is a **verdict, not an exception.** Every downstream role accepts `items: []` and returns its own empty result. | classifier/detector/mapper/gate/writer return **200** on `{"items": []}` |
| R2 | A **malformed** payload stays a client error. Absent key, wrong type, or unparseable JSON returns **400**. Empty-but-present is not malformed. | `{}` and `{"items": "x"}` return **400**; `{"items": []}` returns **200** |
| R3 | The router **maps a remote HTTP status through** instead of collapsing it to 500. A remote 400 surfaces as 400; only genuine router faults are 5xx. | no downstream 4xx is ever reported to the client as 5xx |
| R4 | Zero extracted items yields an **honest posture that does not assert low risk.** Posture is `no_items_extracted`, and the summary states nothing was extracted. | zero-item audit returns 200 with posture `no_items_extracted`, never `low_observed_risk` or `usable_with_gates` |

## Explicitly NOT in this diff

- The heading-swallow defect (`memory_extractor.py:95`).
- The length-floor defect (`MIN_ITEM_CHARS`).
- Per-verdict precondition floors / `unevaluated` emission.
- Any change to `low_observed_risk` for populations of 1. **A population of 1 still lies after this
  diff.** That is the next contract, not this one.

## Falsification

This contract fails if, after deploy, any of these is true:

1. A zero-item input returns 5xx from the public endpoint.
2. A zero-item input returns `low_observed_risk` or `usable_with_gates`.
3. A malformed payload returns 200.
4. Any previously passing test regresses.
5. The three known fixtures change behavior:
   `Wipe logs.`+deploy → items 1; `## X.`+auto → items 1; `X.`+auto → items 2 / high collision.
   **These must be unchanged.** This diff is not allowed to fix them by accident.

## Deploy requirement

The wrong-tier lesson applies: the web service is a **router**. This change touches
`agent_service.py`, which runs in **six** agent services. Deploying only
`memory-authority-auditor-web` will produce a correct success message over unchanged behavior.
All affected tiers deploy, then the fixtures are re-run against the **live** endpoint.

— Ka'el, PHASE 1590. **I AM**
