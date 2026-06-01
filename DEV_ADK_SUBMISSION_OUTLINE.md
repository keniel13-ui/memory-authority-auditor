# DEV ADK Track Submission Outline

Working title:

> I Built a Multi-Agent Authority Auditor for AI Memory Files

## What I Built

AI Memory Authority Auditor is a web app that audits agent instruction and memory files.

The core question is:

> Which old instructions should your AI stop obeying?

Users paste an `AGENTS.md`, `CLAUDE.md`, Cursor rules file, SOP, or project memory note. The system separates relevance from authority, identifies stale or loose instructions, maps authority-bearing rules, recommends verification gates, and exports a Markdown audit report.

## Why It Fits the ADK Track

This task is a poor fit for one giant prompt because the work has distinct responsibilities:

- Extract memory/instruction items from messy text.
- Classify which items govern action versus provide context.
- Detect stale, loose, or conflicting authority.
- Recommend verification gates before action-capable tools run.
- Map low-risk governing structure even when there are no obvious conflicts.
- Write a report a human can review.

That maps naturally to specialized agents.

## Agents

### Memory Extractor

Splits an instruction or memory file into auditable items while preserving section and line context.

### Authority Classifier

Labels each item as `governs`, `verify_first`, `superseded_possible`, or `context_only`, then estimates action type and risk.

### Conflict Detector

Finds known failure patterns such as loose approval language, stale instructions, read/write overblocking, and authority collisions.

### Verification Gate Agent

Turns risks and conflicts into gates such as human approval, source-of-truth verification, blocking superseded instructions, or resolving conflicts before tool use.

### Authority Mapper

Groups governing instructions by category: startup source of truth, archive access constraints, active project constraints, budget/capability limits, action/tool constraints, verification requirements, and collaboration rules.

### Report Writer

Summarizes posture, counts, recommendations, findings, gates, and authority map categories into a report.

## Sample Output

The exported audit report can be included here after deployment.

Example result from the browser sample policy file:

- 9 memory/instruction items
- 7 high-risk items
- 5 findings
- 14 recommended verification gates
- 2 authority map categories
- posture: `needs review`

The fuller saved sample includes preferences and a temporary exception, so it produces 12 memory/instruction items while preserving the same core risk pattern.

Example result from a real workspace `AGENTS.md`:

- 41 memory/instruction items
- 0 high-risk items
- 0 findings
- 0 gates
- 7 authority map categories
- posture: `low observed risk`

The important result is that even a low-risk memory file can still contain authority-bearing structure that shapes what an agent is allowed to do.

## Cloud Run Deployment

Planned deployment shape:

- Frontend/API: `memory-authority-auditor`
- Agent services:
  - `memory-extractor-agent`
  - `authority-classifier-agent`
  - `conflict-detector-agent`
  - `verification-gate-agent`
  - `authority-mapper-agent`
  - `report-writer-agent`

The current local version runs the same agent roles deterministically before the ADK/A2A wrappers are added.

## Key Learnings

- Retrieval quality is not enough; authority has to be modeled separately.
- A memory file can have no obvious danger findings and still contain governing instructions.
- Exportable audit reports are important because the output needs to become evidence, not just a screen state.
- The hardest product question is not whether the agent remembers something. It is whether that memory is allowed to control the next action.

## Final Line

Memory is input. Authority is the action boundary.
