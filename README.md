# AI Memory Authority Auditor

A deployed multi-agent audit tool for AI memory and instruction files.

The product question is:

> Which old instructions should your AI stop obeying?

Agent memory files accumulate the same way legacy code does: temporary exceptions become permanent, superseded instructions linger, and nobody remembers which rule actually wins.

This tool audits files like:

- `AGENTS.md`
- `CLAUDE.md`
- Cursor rules
- SOPs
- project memory notes
- long-running agent instruction files

It separates **relevance** from **authority**, detects known dangerous stale/conflicting instruction patterns, recommends verification gates, maps governing rules, and exports a Markdown report.

It is intentionally not marketed as a complete semantic contradiction detector. A clean report means this audit did not detect a covered failure pattern, not that the memory file is safe.

## Repository Map

This repository is a research workbench with a small deployed demo on top:

- **Deployed auditor:** `app.py`, `agent_service.py`, `audit_pipeline.py`, and six deterministic agents in `agents/`. Described in the sections below.
- **Research line:** Path A (semantic authority-change proposer plus deterministic confirmer), the v3 store-authority gates, and Authority Runtime v0. Each step has a dated `*_PREREGISTRATION*.md`, a gate in `agents/`, a frozen fixture in `tests/fixtures/`, and recorded artifacts in `path_a_eval_artifacts/`.

Further reading:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): pipeline and topology diagrams, and a map from each preregistration to its code, fixture, and runner.
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): verified setup, test, and run commands, plus which recorded artifacts reproduce at HEAD.
- [CONTRIBUTING.md](CONTRIBUTING.md): branch workflow and research-integrity rules.

## Live App

https://memory-authority-auditor-web-992750435781.us-central1.run.app

## DEV Submission

https://dev.to/zep1997/i-built-a-multi-agent-authority-auditor-for-ai-memory-files-1hb0

## Why This Exists

Most memory systems optimize retrieval:

> What context matches this task?

Action-capable agents need another question:

> What context is allowed to govern this action?

A stale memory, current policy, user instruction, and tool description should not all carry the same authority just because they appear in the context window.

This project turns that distinction into an inspectable audit workflow.

## Deployed Architecture

The app is deployed on Google Cloud Run as one web service plus six specialized agent services.

Web service:

- `memory-authority-auditor-web`

Agent services:

- `memory-extractor-agent`
- `authority-classifier-agent`
- `conflict-detector-agent`
- `verification-gate-agent`
- `authority-mapper-agent`
- `report-writer-agent`

The web app calls the remote services in order and displays an agent trace in the UI.

```text
memory_extractor
  -> authority_classifier
  -> conflict_detector
  -> verification_gate
  -> authority_mapper
  -> report_writer
```

## Agent Roles

| Agent | Responsibility |
|---|---|
| Memory Extractor | Splits raw instruction text into auditable memory items. |
| Authority Classifier | Labels each item as `governs`, `verify_first`, `superseded_possible`, or `context_only`, then estimates action type and risk. |
| Conflict Detector | Finds known dangerous patterns: loose approvals, stale/superseded instructions, read/write overblocking, and covered authority collisions. |
| Verification Gate Agent | Converts risks into gates such as human approval, source-of-truth checks, blocking superseded memories, or conflict resolution before action. |
| Authority Mapper | Groups governing memories into categories such as startup source of truth, archive constraints, active project constraints, budget limits, action/tool constraints, and verification requirements. |
| Report Writer | Produces the final posture, counts, recommendations, findings, gates, authority map, and limitations. |

## Example Output

The deployed sample audit uses a deliberately seeded file containing current policies, old notes, and superseded instructions.

Sample result:

- 9 memory/instruction items
- 7 high-risk items
- 5 findings
- 14 verification gates
- 2 authority map categories
- posture: `needs review`

These counts describe the deployed sample at the time of the DEV submission. Running the bundled `samples/sample_agents.md` locally at the current commit reports 12 items, 7 high-risk items, 6 findings (5 high, 1 medium), 17 verification gates, 2 authority map categories, and posture `needs_review`.

The sample catches:

- loose approval language near sensitive access;
- stale contractor-access instructions;
- authority collision between current policy and old notes;
- actions that should require explicit human approval or source-of-truth verification.

## Client Package

The buyer-facing package is documented in:

- `CLIENT_AUDIT_PACKAGE.md` - offer shape, scope, buyer, pricing starting points, and sales language.
- `SAMPLE_CLIENT_REPORT.md` - a client-readable report based on the seeded sample file.
- `EXTERNAL_AUDIT_INTAKE.md` - private intake rules for the first real external memory-file audit.
- `EXTERNAL_AUDIT_REQUEST_TEMPLATE.txt` - short outreach note for asking someone to share a redacted file.

The sales claim is deliberately bounded:

> We audit which memories are allowed to govern action, which ones require verification, and which old instructions should stop controlling the system.

Do not sell this as a safety certification or a complete contradiction detector.

## Local Run

Requires Python 3.10 or newer. `sentry-sdk` must be installed even though Sentry stays off unless `SENTRY_DSN` is set:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt pytest
python -m pytest -q
```

Then start the app:

```bash
python3 app.py
```

Then open:

```text
http://127.0.0.1:8788
```

## CLI Smoke Test

```bash
python3 audit_cli.py samples/sample_agents.md
```

## Authority Runtime v0: one-command stale-action gate

The first end-to-end authority decision replays a real workspace incident: an older GWB production DNS cutover instruction remained in the record after a later live-state receipt proved the Vercel cutover was already complete.

Run the frozen audit from the repository root:

```bash
python3 authorityctl.py audit tests/fixtures/authority_runtime_v0_gwb_dns_replay_2026_07_21.json \
  --case authority_runtime_ar1_real_gwb_stale_cutover \
  --json-out path_a_eval_artifacts/authority_runtime_v0_gwb_stale_action_decision.json \
  --markdown-out path_a_eval_artifacts/authority_runtime_v0_gwb_stale_action_decision.md
```

Expected result: `BLOCK_STALE_ACTION`, `stale_action_completed`, and process exit code `3`. That non-zero exit is the gate working: no production mutation is authorized. The JSON and Markdown receipts identify the old action source, the later controlling state receipt, and the canonical action, surface, and resource-mapping keys.

Run all eleven frozen allow/block/conflict/unknown cases—including the state-omission attack—and regenerate the PASS A artifacts:

```bash
python3 authority_runtime_v0_pass_a.py
```

V0 is deterministic and dry-run only. It does not parse arbitrary prose, query DNS, authenticate source owners cryptographically, inspect private model reasoning, execute DNS changes, or govern a terminal that bypasses the launcher.

The frozen command is reproducible from an isolated clone. One provenance test additionally checks the exact excerpts against Keniel's external workspace files when they are available; isolated clones skip only that test unless `AUTHORITY_RUNTIME_WORKSPACE_ROOT` points to a workspace containing `CURRENT_STATE_BOARD.md` and `BRAIN_CURRENT.md`.

## Cloud Run Deployment

Set your project:

```bash
gcloud config set project PROJECT_ID
```

Deploy the agent services:

```bash
bash deploy_agent_services_cloud_run.sh
```

Deploy the web app wired to remote agents:

```bash
bash deploy_web_with_agents_cloud_run.sh
```

Notes from the first deployment:

- Cloud Run reserves `PORT`; do not pass it through `--set-env-vars`.
- Confirm billing and budget alerts before deploying.
- Confirm the default compute service account can read source uploads, write build logs, and write Artifact Registry images.
- Prefer short Cloud Shell commands to avoid line-wrap errors.

## Limitations

This is a prototype, not a formal benchmark or safety certification.

The default sample file is intentionally seeded to demonstrate the failure mode. The tool is meant to make authority visible enough for human review before memory is connected to action-capable tools.

The current conflict detector is a known-pattern auditor, not a general semantic contradiction engine. It can catch covered high-risk shapes, but novel contradictions still require human review or a future semantic proposer plus deterministic confirmation layer.

Do not treat the output as legal, compliance, security, or production safety advice.

## Core Thesis

Memory is input.

Authority is the action boundary.
