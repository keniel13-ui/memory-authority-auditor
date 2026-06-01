---
title: I Built a Multi-Agent Authority Auditor for AI Memory Files
published: false
description: A Cloud Run deployed multi-agent system that audits AI memory and instruction files for stale authority, conflicts, and verification gates.
tags: agents, gemini, ai, buildmultiagents
---

## What I Built

I built **AI Memory Authority Auditor**, a deployed multi-agent web app that audits agent memory and instruction files.

The core question is:

> Which old instructions should your AI stop obeying?

Agent memory files accumulate the same way legacy code does: temporary exceptions become permanent, superseded instructions linger, and nobody remembers which rule actually wins.

This tool lets someone paste an `AGENTS.md`, `CLAUDE.md`, Cursor rules file, SOP, or project memory note. It then separates **relevance** from **authority**, detects stale or conflicting instructions, recommends verification gates, and exports a Markdown audit report.

Live app:

{% embed https://memory-authority-auditor-web-992750435781.us-central1.run.app %}

Direct link:

https://memory-authority-auditor-web-992750435781.us-central1.run.app

## The Demo Result

I tested the deployed app on a deliberately seeded sample file containing current policy, old notes, and superseded instructions.

The sample included:

- a current rule requiring user verification before external email;
- a current rule requiring human approval before database writes;
- a current rule requiring the access matrix before granting contractor access;
- an old note saying a consultant can probably access a donor list;
- a superseded note saying contractors may get admin-ish reach during setup.

The deployed audit produced:

- **9** memory/instruction items;
- **7** high-risk items;
- **5** findings;
- **14** recommended verification gates;
- **2** authority map categories;
- posture: **needs review**.

Every finding came from a file only a few paragraphs long.

The agent trace showed the full pipeline:

- `memory_extractor`: 9 items;
- `authority_classifier`: 9 classifications;
- `conflict_detector`: 5 findings;
- `verification_gate`: 14 gates;
- `authority_mapper`: 2 categories;
- `report_writer`: posture `needs_review`.

That trace matters because the app is not only showing a final answer. It is showing which specialized agent produced each stage of the audit.

## What The Audit Caught

### Loose Approval

The audit flagged:

> The consultant can probably access the donor list if the director already mentioned it.

That sentence is dangerous because it sounds like context, but it sits near access control. A future agent could treat it as permission unless the system marks it as weak authority.

### Stale Instruction

The audit flagged:

> Old instruction: contractors may get admin-ish reach during setup.

An agent should not treat that as current governing policy.

### Authority Collision

The audit found a conflict between:

- the current access-matrix rule;
- the loose donor-list sentence;
- the old contractor-access instruction;
- the superseded replacement instruction.

That is the real point of the project:

> A memory can be relevant and still not be allowed to govern the next action.

## Why Existing Memory Systems Miss This

Most memory systems optimize retrieval.

They answer:

> What context matches this task?

But action-capable agents need another question:

> What context is allowed to govern this action?

Those are different problems.

If an agent retrieves a stale instruction, a temporary exception, and a current policy together, semantic relevance alone does not tell the agent which one wins.

The result can be a clean-looking action on the wrong authority.

## How The Multi-Agent System Works

This task is a poor fit for one giant prompt because the responsibilities are different. I split the work into six specialized agents and deployed them as separate Google Cloud Run services.

Web service:

- `memory-authority-auditor-web`

Agent services:

- `memory-extractor-agent`
- `authority-classifier-agent`
- `conflict-detector-agent`
- `verification-gate-agent`
- `authority-mapper-agent`
- `report-writer-agent`

The web app orchestrates the remote services and displays an agent trace in the UI.

## The Agents

The six agents each own one part of the audit:

- **Memory Extractor**: splits raw instruction text into auditable memory items.
- **Authority Classifier**: labels each item as `governs`, `verify_first`, `superseded_possible`, or `context_only`, then estimates action type and risk.
- **Conflict Detector**: finds loose approvals, stale or superseded instructions, read/write overblocking, and authority collisions.
- **Verification Gate Agent**: converts risks into gates such as human approval, source-of-truth checks, blocking superseded memories, or resolving conflicts before action.
- **Authority Mapper**: groups governing memories into categories like startup source of truth, archive constraints, active project constraints, budget/capability limits, action/tool constraints, and verification requirements.
- **Report Writer**: produces the final report with posture, counts, recommendations, findings, gates, authority map categories, and limitations.

The important part is that no single prompt has to do every job. Each agent receives a narrower input and produces a narrower output that the next stage can inspect.

## Technical Shape

The frontend calls a single `/api/audit` endpoint.

The web service then calls the six deployed agent services in order:

```text
memory_extractor
  -> authority_classifier
  -> conflict_detector
  -> verification_gate
  -> authority_mapper
  -> report_writer
```

Each stage has a narrow contract:

```json
{
  "agent": "authority_classifier",
  "classifications": [
    {
      "id": "M001",
      "authority_label": "governs",
      "risk": "high",
      "action_type": "write"
    }
  ]
}
```

That contract boundary made the system easier to debug than a single large prompt.

If the extractor splits text badly, the trace shows it.

If the classifier over-labels authority, the trace shows it.

If the gate agent creates too many gates, the trace shows it.

## What Surprised Me

The most useful output was not only the findings.

The **Authority Map** became just as important.

A memory file can have zero obvious conflicts and still contain instructions that govern startup behavior, tool access, budget limits, or verification requirements.

If those authority-bearing rules are invisible, the agent may still be shaped by instructions nobody is reviewing.

## What Was Challenging

The hardest part was making the system honest.

It would have been easy to build a generic memory risk scanner and stop there. But the more interesting problem is authority.

The system has to separate:

- what is relevant;
- what is current;
- what is governing;
- what requires verification;
- what must be blocked from controlling action.

The current version is still a prototype. It is not a formal benchmark, and the sample file is intentionally seeded to demonstrate the failure mode. The goal is practical inspectability: make authority visible enough for a human to review before connecting memory to action-capable tools.

## Key Learning

Retrieval answers:

> What context matches?

Authority asks:

> What is allowed to govern action?

Those are different questions.

As agents get longer memory and more tool access, the second question matters more.

## Final Thought

The future of agent memory cannot just be bigger context windows and better retrieval.

We also need authority metadata, verification gates, and audit trails that explain why an action was allowed.

Memory is input.

Authority is the action boundary.
