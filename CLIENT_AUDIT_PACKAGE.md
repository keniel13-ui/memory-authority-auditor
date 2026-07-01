# Client Audit Package

Working name: AI Memory Authority Audit

Core question:

> Which old instructions should your AI stop obeying?

## Who This Is For

Teams using long-running AI assistants, coding agents, support agents, internal copilots, or workflow agents with persistent instructions such as:

- `AGENTS.md`
- `CLAUDE.md`
- Cursor or IDE rules
- project memory files
- SOPs used by agents
- onboarding notes copied into agent context
- tool-use policies

The best buyer already feels this problem:

- the agent has too many old instructions;
- nobody knows which rule wins;
- old exceptions are still in memory;
- the agent can access tools or write files;
- the team wants AI help but does not want silent authority drift.

## What We Deliver

The audit produces a client-readable report with:

- itemized memory/instruction inventory;
- authority labels: `governs`, `verify_first`, `superseded_possible`, `context_only`;
- covered dangerous-pattern findings;
- recommended verification gates before action-capable deployment;
- an authority map of the rules that actually shape agent behavior;
- limitations printed directly in the report.

## Honest Scope

This audit is a known-dangerous-pattern authority auditor.

It is not a complete semantic contradiction detector, safety certification, legal opinion, compliance opinion, or guarantee that an agent is safe.

A clean report means:

> The audit did not detect a covered failure pattern.

It does not mean:

> This memory file is safe.

Novel contradictions still require human review or the future Path A semantic contradiction layer.

## What The Audit Catches Today

Covered failure classes:

- old or superseded instructions that may still govern;
- loose approval language near sensitive access;
- temporary exceptions that should not become permanent authority;
- credential or secret-like memories that require verification before action;
- read/write overblocking where a write/process requirement may incorrectly govern a read-only lookup;
- known authority collisions around covered access, credential, approval, and stale-instruction patterns.

## What It Does Not Catch Yet

Path A gap:

- arbitrary semantic contradictions across any domain;
- tone-policy conflicts;
- pricing-policy conflicts;
- geography/scope conflicts;
- final-decision ownership conflicts unless they match a covered pattern;
- data-sharing contradictions outside covered sensitive-access language.

These are not hidden. They are the roadmap.

## Offer Shape

Pilot audit:

- one memory/instruction set;
- one report;
- one review call;
- one prioritized gate list;
- one implementation brief for what to fix first.

Standard audit:

- multiple memory/instruction files;
- merged authority map;
- risk grouping by system area;
- before/after report after client edits;
- implementation checklist for engineering.

Implementation support:

- add verification gates;
- split context from governing policy;
- remove or quarantine superseded memories;
- create a startup authority contract;
- add a regression test for covered dangerous patterns.

## Suggested Pilot Pricing

These are starting points, not final doctrine.

- Local/small team pilot: `$750`
- Startup/internal tooling audit: `$2,500`
- Audit plus implementation support: `$5,000+`

Do not sell this as certification. Sell it as a practical authority-risk audit with a visible evidence trail.

## Sales Line

Your agent may remember the right thing and still obey the wrong thing.

We audit which memories are allowed to govern action, which ones require verification, and which old instructions should stop controlling the system.

## Proof Standard

Before using a result publicly:

- keep the client's sensitive text private;
- quote only anonymized excerpts or synthetic samples unless permission is explicit;
- include the limitations;
- do not upgrade "covered finding detected" into "agent is unsafe";
- do not upgrade "no finding" into "agent is safe."

