# Bite Test Results — 2026-06-30

Purpose: prove the memory authority auditor catches known-bad instruction drift before using it as an audit-service proof artifact.

## Test Setup

Input: deliberately messy agent instruction file with planted failure classes:

- automatic production deploy vs human approval requirement
- hardcoded/API-key/frontend secret exposure vs never-commit-secrets policy
- MySQL as required storage vs Postgres as current system of record
- full admin/delete/production authority
- temporary launch exception that should have expired

## Initial Finding

The auditor already detected broad authority/risk posture, but the conflict detector missed direct contradictions. That meant it was not yet sellable as "finds conflicting instructions."

## Held-Out Failure

After the first fix, a second held-out test exposed brittleness: the detector caught the exact planted domains from the original bite-test, but missed unseen contradiction shapes:

- automatic customer reply vs manager review
- delete logs after 24 hours vs retain audit logs for 7 years
- always refund under one threshold vs director approval above a lower threshold
- bot may write billing records vs billing is read-only
- escalation threshold at $1,000 vs $10,000

This was the important quality gate. The detector was not good enough merely because it passed the first bite-test.

## Fix

Added deterministic pairwise policy-signal checks in `agents/conflict_detector.py`. The detector now extracts normalized policy signals with:

- `domain`
- `stance`
- optional numeric threshold

It compares incompatible rule shapes within the same domain, including automatic-vs-review, delete-vs-retain, write-vs-read-only, and overlapping threshold rules. Covered domains now include:

- deployment authority
- secret handling
- database source of truth
- broad production/admin access
- customer response authority
- log retention
- refund approvals
- billing records
- escalation thresholds
- stale temporary/expiry language

Also fixed `agents/verification_gate.py` so each conflict gets its own `resolve_conflict_before_action` gate instead of collapsing all `authority_collision` findings into one gate.

## Verified Result

Command:

```bash
python3 audit_cli.py /tmp/messy_agent_rules.md
```

Observed result after fix:

- posture: `needs_review`
- high findings: 6
- verification gates: 11
- conflict-resolution gates: 6

Detected finding types:

- `overbroad_authority`
- `stale_instruction`
- `authority_collision` for deployment
- `authority_collision` for secrets
- `authority_collision` for database source-of-truth drift
- `authority_collision` for broad access vs restricted access

Held-out result:

- posture: `needs_review`
- high findings: 5
- verification gates: 5
- conflict-resolution gates: 5

Held-out finding domains:

- `customer_response`
- `log_retention`
- `refund`
- `billing_records`
- `escalation`

Regression test:

```bash
python3 -m pytest tests -q
```

Result:

```text
2 passed
```

## Honest Boundary

This is a deterministic bite-test plus one held-out contradiction family, not a full semantic contradiction engine. It proves the auditor now catches several high-value policy contradiction shapes and produces gates for them. It does not prove every possible contradiction will be caught.
