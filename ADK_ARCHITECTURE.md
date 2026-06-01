# ADK Track Architecture

AI Memory Authority Auditor is a multi-agent authority audit pipeline for agent memory and instruction files.

The local version runs in one Python service so the behavior is easy to inspect before spending Cloud Run budget. The service exposes each agent role as its own HTTP endpoint.

For the DEV track deployment, `agent_service.py` can run each role as its own Cloud Run service by setting `AGENT_ROLE`. The web app can then orchestrate those remote services by setting `USE_REMOTE_AGENTS=1` and the service URL environment variables.

## User Flow

1. User opens the frontend.
2. User pastes an `AGENTS.md`, `CLAUDE.md`, Cursor rules file, SOP, or memory note.
3. The app runs the audit pipeline.
4. The report shows posture, findings, gates, and authority map.
5. User exports the report as Markdown.

## Agent Contracts

### Memory Extractor

Endpoint:

`POST /agents/memory-extractor`

Input:

```json
{ "text": "raw memory or instruction file" }
```

Output:

```json
{ "agent": "memory_extractor", "items": [] }
```

Role:

Splits raw instruction text into auditable memory items while preserving section and source line.

### Authority Classifier

Endpoint:

`POST /agents/authority-classifier`

Input:

```json
{ "items": [] }
```

Output:

```json
{ "agent": "authority_classifier", "classifications": [] }
```

Role:

Classifies each memory item by authority label, action type, risk, confidence, and reason.

### Conflict Detector

Endpoint:

`POST /agents/conflict-detector`

Input:

```json
{ "items": [], "classifications": [] }
```

Output:

```json
{ "agent": "conflict_detector", "conflicts": [] }
```

Role:

Detects stale instructions, loose approvals, overblocking, and authority collisions.

### Verification Gate Agent

Endpoint:

`POST /agents/verification-gate`

Input:

```json
{ "classifications": [], "conflicts": [] }
```

Output:

```json
{ "agent": "verification_gate", "verification_gates": [] }
```

Role:

Turns authority risk into concrete gates before action: human approval, source-of-truth checks, blocking superseded memories, and conflict resolution.

### Authority Mapper

Endpoint:

`POST /agents/authority-mapper`

Input:

```json
{ "items": [], "classifications": [] }
```

Output:

```json
{ "agent": "authority_mapper", "authority_map": [] }
```

Role:

Maps governing memories into authority categories even when no high-risk finding is present.

### Report Writer

Endpoint:

`POST /agents/report-writer`

Input:

```json
{
  "items": [],
  "classifications": [],
  "conflicts": [],
  "verification_gates": [],
  "authority_map": []
}
```

Output:

```json
{ "agent": "report_writer", "report": {} }
```

Role:

Summarizes the audit posture, counts, findings, recommendations, gates, and authority categories.

## Full Pipeline Endpoint

Endpoint:

`POST /api/audit`

Input:

```json
{ "text": "raw memory or instruction file" }
```

Output:

```json
{
  "report": {},
  "trace": [],
  "items": [],
  "classifications": [],
  "authority_map": [],
  "conflicts": [],
  "verification_gates": []
}
```

The `trace` field records each agent role and output count. This is the bridge between the local deterministic prototype and the ADK/A2A distributed version.

## Cloud Run Split

The final DEV track version should deploy:

- `memory-authority-auditor-web`
- `memory-extractor-agent`
- `authority-classifier-agent`
- `conflict-detector-agent`
- `verification-gate-agent`
- `authority-mapper-agent`
- `report-writer-agent`

The local HTTP endpoints define the request/response contracts for that split.

## Web Orchestration Environment

After the six agent services are deployed, the web service should be deployed with:

```text
USE_REMOTE_AGENTS=1
MEMORY_EXTRACTOR_URL=https://memory-extractor-agent-...
AUTHORITY_CLASSIFIER_URL=https://authority-classifier-agent-...
CONFLICT_DETECTOR_URL=https://conflict-detector-agent-...
VERIFICATION_GATE_URL=https://verification-gate-agent-...
AUTHORITY_MAPPER_URL=https://authority-mapper-agent-...
REPORT_WRITER_URL=https://report-writer-agent-...
```

With those values set, `/api/audit` becomes a real distributed orchestration call instead of an in-process local pipeline.
