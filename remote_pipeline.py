from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


ENDPOINT_ENV = {
    "memory_extractor": "MEMORY_EXTRACTOR_URL",
    "authority_classifier": "AUTHORITY_CLASSIFIER_URL",
    "conflict_detector": "CONFLICT_DETECTOR_URL",
    "verification_gate": "VERIFICATION_GATE_URL",
    "authority_mapper": "AUTHORITY_MAPPER_URL",
    "report_writer": "REPORT_WRITER_URL",
}


# Upper bound on a single agent response. The largest real payload is the
# report, which is a small multiple of the input; this only stops a
# misbehaving or hijacked endpoint from exhausting web-service memory.
MAX_AGENT_RESPONSE_BYTES = 32 * 1024 * 1024
AGENT_TIMEOUT_SECONDS = 30


class RemoteAgentError(RuntimeError):
    """A remote agent call failed or returned an unusable response."""

    def __init__(self, agent: str, message: str) -> None:
        super().__init__(f"{agent} agent failed: {message}")
        self.agent = agent


def _post_json(url: str, payload: dict, agent: str = "remote") -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=AGENT_TIMEOUT_SECONDS) as response:
            raw = response.read(MAX_AGENT_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as error:
        detail = ""
        try:
            detail = str(json.loads(error.read(4096).decode("utf-8")).get("error", ""))
        except (ValueError, AttributeError, OSError):
            detail = ""
        message = f"http {error.code}"
        if detail:
            message += f": {detail[:240]}"
        raise RemoteAgentError(agent, message) from error
    except urllib.error.URLError as error:
        raise RemoteAgentError(agent, f"network error: {str(error.reason)[:240]}") from error
    except (TimeoutError, OSError) as error:
        raise RemoteAgentError(agent, f"connection error: {type(error).__name__}") from error
    if len(raw) > MAX_AGENT_RESPONSE_BYTES:
        raise RemoteAgentError(agent, "response exceeded size limit")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RemoteAgentError(agent, "response was not valid JSON") from error
    if not isinstance(data, dict):
        raise RemoteAgentError(agent, "response root was not a JSON object")
    return data


def _call(agent: str, payload: dict, field: str) -> dict:
    data = _post_json(_endpoint(agent), payload, agent)
    if field not in data:
        error = data.get("error")
        raise RemoteAgentError(agent, str(error)[:240] if error else f"response missing '{field}'")
    return data


def _endpoint(agent: str) -> str:
    value = os.environ.get(ENDPOINT_ENV[agent], "").strip()
    if not value:
        raise RuntimeError(f"Missing {ENDPOINT_ENV[agent]} for remote agent orchestration.")
    return value


def run_remote_audit(text: str) -> dict:
    extracted = _call("memory_extractor", {"text": text}, "items")
    classified = _call("authority_classifier", {"items": extracted["items"]}, "classifications")
    conflicts = _call(
        "conflict_detector",
        {"items": extracted["items"], "classifications": classified["classifications"]},
        "conflicts",
    )
    gates = _call(
        "verification_gate",
        {"classifications": classified["classifications"], "conflicts": conflicts["conflicts"]},
        "verification_gates",
    )
    mapped = _call(
        "authority_mapper",
        {"items": extracted["items"], "classifications": classified["classifications"]},
        "authority_map",
    )
    report = _call(
        "report_writer",
        {
            "items": extracted["items"],
            "classifications": classified["classifications"],
            "conflicts": conflicts["conflicts"],
            "verification_gates": gates["verification_gates"],
            "authority_map": mapped["authority_map"],
        },
        "report",
    )

    trace = [
        {"agent": "memory_extractor", "role": "Split raw instruction text into auditable memory items.", "output": {"items": len(extracted["items"])}},
        {"agent": "authority_classifier", "role": "Classify each memory by authority label, action type, and risk.", "output": {"classifications": len(classified["classifications"])}},
        {"agent": "conflict_detector", "role": "Find stale, loose, or conflicting authority patterns.", "output": {"findings": len(conflicts["conflicts"])}},
        {"agent": "verification_gate", "role": "Convert risks and conflicts into verification gates before action.", "output": {"gates": len(gates["verification_gates"])}},
        {"agent": "authority_mapper", "role": "Group governing memories by authority category.", "output": {"categories": len(mapped["authority_map"])}},
        {"agent": "report_writer", "role": "Summarize posture, recommendations, findings, gates, and authority map.", "output": {"posture": report["report"]["posture"]}},
    ]

    return {
        "report": report["report"],
        "trace": trace,
        "items": extracted["items"],
        "classifications": classified["classifications"],
        "authority_map": mapped["authority_map"],
        "conflicts": conflicts["conflicts"],
        "verification_gates": gates["verification_gates"],
    }
