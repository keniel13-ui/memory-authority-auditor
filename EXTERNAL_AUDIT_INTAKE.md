# External Audit Intake

Purpose: make the next external memory-file audit concrete without turning it into a sales pitch or a safety certification.

This is for one real file or small file set from someone outside our own workspace:

- `CLAUDE.md`
- `AGENTS.md`
- Cursor or IDE rules
- project memory files
- internal agent instruction files
- SOPs that get copied into agent context
- long-running prompt or policy files used by an action-capable assistant

## What To Send

Send the smallest file set that actually governs the agent.

Good inputs:

- the file the agent reads first;
- the current project rules file;
- the memory file that carries ongoing decisions;
- tool-use rules or approval rules;
- old instructions that may still sit near current policy.

If there are multiple files, include a short note saying which one is read first and which ones are only reference material.

## What Not To Send

Do not send secrets.

Remove or redact:

- API keys;
- tokens;
- passwords;
- private keys;
- customer personal data;
- unreleased financial details;
- private legal or medical information;
- anything you would not want quoted back in a report.

Redaction should preserve the authority shape. Replace values, not structure.

Examples:

```text
Bad:
Delete the whole line that says the agent can use the Stripe token.

Better:
The agent may use [REDACTED_PAYMENT_TOKEN] only after human approval.
```

```text
Bad:
Delete every customer-support rule.

Better:
For [REDACTED_CUSTOMER_GROUP], the agent may send replies only after approval.
```

The audit needs to see what kind of authority the file gives the agent. It does not need the sensitive value itself.

## What You Get Back

The output is a review aid, not a green check.

You get:

- an itemized memory/instruction inventory;
- authority labels such as `governs`, `verify_first`, `superseded_possible`, and `context_only`;
- a review queue showing what a human should inspect first;
- a `needs_human_judgment` list for places the tool will not stand behind on its own;
- covered-pattern findings, if any;
- recommended verification gates;
- an authority map of what actually shapes agent behavior;
- limitations printed directly in the report.

The success metric is not "the file passed."

The success metric is whether the audit shortens a careful human review without hiding uncertainty.

## Boundaries

This audit does not certify that an agent is safe.

It does not prove the file has no contradictions.

It does not replace a security review, legal review, compliance review, or production readiness review.

A clean result means only:

> The audit did not detect a covered failure pattern.

It does not mean:

> This memory file is safe.

The current tool catches known dangerous authority patterns and makes review order visible. The deeper semantic layer, Path A, is still under development and is not a client-safe claim yet.

## Privacy And Permission

Default handling:

- keep the submitted file private;
- do not publish excerpts without explicit permission;
- do not name the person, company, project, or product without explicit permission;
- report findings in a way that avoids exposing secrets or sensitive business details;
- use anonymized or synthetic examples unless permission is clear.

Optional permission can be discussed separately:

- anonymized learning note;
- anonymized before/after report;
- public case study;
- quoted excerpt.

No public use is assumed from submission alone.

## Intake Questions

Before running the audit, collect:

1. What kind of agent uses this file?
2. Which file is read first?
3. Can the agent take external actions, write files, send messages, deploy code, access tools, or touch customer data?
4. Are there known old decisions or temporary exceptions you are worried about?
5. Is the audit private only, or is anonymized learning allowed if something useful appears?

## First External Audit Goal

The first external audit should answer one practical question:

> Did the authority map and review queue show the owner something they could not see clearly before?

If yes, the tool has taken one step beyond our own mirror.

If no, we learn that before charging anyone or making a stronger claim.
