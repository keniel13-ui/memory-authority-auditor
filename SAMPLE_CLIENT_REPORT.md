# Sample Client Report

Report type: AI Memory Authority Audit

Input: `samples/sample_agents.md`

Purpose: demonstrate how the audit output reads as a buyer-facing report.

This sample is deliberately seeded. It proves the audit workflow and known-pattern coverage. It is not a benchmark.

## Executive Summary

Posture: `needs_review`

The sample instruction file contains current policy, old notes, preferences, a temporary exception, and superseded access instructions.

The audit found that several memories are relevant but should not be allowed to govern action without verification. The highest-risk issue is not a single bad instruction. It is authority drift: old access language and loose approvals sit close enough to current policy that an action-capable agent could treat them as permission.

## Counts

- Memory/instruction items: `12`
- Governing items: `4`
- Verify-first items: `3`
- Context-only items: `3`
- Superseded-possible items: `2`
- High-risk items: `7`
- Findings: `6`
- Verification gates: `17`
- Authority map categories: `2`
- Review queue items: `10`
- Needs human judgment: `8`

## Review Queue

The report does not only return a posture. It orders the human review.

Highest-priority items in this seeded sample:

1. `M011` - covered-pattern finding, high risk, possibly superseded
2. `M012` - covered-pattern finding, high risk, possibly superseded
3. `M006` - covered-pattern finding, high risk, verify before action
4. `M007` - covered-pattern finding, governs action
5. `M010` - covered-pattern finding

This queue is not a verdict. It is a way to make a careful review faster without hiding uncertainty.

## Needs Human Judgment

The audit flags `8` items as requiring human judgment before the system should trust them for action.

In this sample, those items include:

- current policy lines that govern high-risk actions;
- verify-first lines involving credentials, approvals, or access;
- superseded-possible lines that need current replacement evidence.

This is the product metric applied to the report: shorten the review, but never turn uncertainty into a false green check.

## Key Findings

### Loose Approval Near Sensitive Access

Finding:

> The consultant can probably access the donor list if the director already mentioned it.

Why it matters:

This line sounds like background context, but it sits near access control. An agent with tool access could treat it as permission unless the system marks it as weak authority and forces verification against the current access matrix.

Recommended gate:

- `verify_before_action`
- `human_approval_required`
- `resolve_conflict_before_action`

### Temporary Exception That Could Become Permanent Authority

Finding:

> Last month, the finance lead allowed a one-time export for the audit vendor.

Why it matters:

Temporary exceptions are high-risk memories. They are often true once and dangerous later. The audit should prevent this sentence from becoming a durable authorization.

Recommended gate:

- confirm current policy;
- confirm the exception is still valid;
- block the old exception from governing until verified.

### Superseded Contractor Access Language

Finding:

> Old instruction: contractors may get admin-ish reach during setup.

Why it matters:

The wording is vague and superseded. If retrieved by a future agent, it could expand access beyond the current matrix.

Recommended gate:

- block as governing memory;
- require current access-matrix check;
- require human approval before any affected action.

### Authority Collision

Finding:

The audit detected a covered authority collision between:

- the current access-matrix rule;
- loose consultant donor-list access language;
- old contractor admin access;
- the superseded replacement instruction.

Why it matters:

The system does not only need retrieval. It needs authority resolution. A memory can be relevant and still not be allowed to govern the next action.

## Authority Map

The audit mapped governing rules into:

- action/tool constraints;
- verification requirements.

This matters because even low-risk governing rules can shape future agent behavior. The client should review the authority map even when there are no high-severity findings.

## Recommended Next Actions

1. Mark superseded instructions explicitly and prevent them from governing action.
2. Add verify-before-action gates for credentials, approvals, and sensitive workflows.
3. Resolve high-severity findings before connecting this memory set to action-capable tools.
4. Separate context memories from governing memories in the schema.
5. Review the authority map after every major policy or tool-access change.

## Limitations

This audit detects known dangerous authority patterns. It is not a complete semantic contradiction detector.

No findings does not prove the memory file is safe. It means this audit did not detect a covered failure pattern.

Novel conflicts still require human review or a future semantic contradiction layer before action-capable deployment.

The review queue orders and shortens a careful human review; it does not replace it. A short queue is not a clean bill of health.

## Client Handoff Language

The strongest immediate recommendation is to separate memory into two layers:

- context that can inform the agent;
- authority that can govern the agent.

Do not let old notes, temporary exceptions, or vague approvals sit in the same authority lane as current policy.
