from __future__ import annotations

import json
import os
import urllib.request


ENDPOINT_ENV = {
    "memory_extractor": "MEMORY_EXTRACTOR_URL",
    "authority_classifier": "AUTHORITY_CLASSIFIER_URL",
    "conflict_detector": "CONFLICT_DETECTOR_URL",
    "verification_gate": "VERIFICATION_GATE_URL",
    "authority_mapper": "AUTHORITY_MAPPER_URL",
    "report_writer": "REPORT_WRITER_URL",
}


def _post_json(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _endpoint(agent: str) -> str:
    value = os.environ.get(ENDPOINT_ENV[agent], "").strip()
    if not value:
        raise RuntimeError(f"Missing {ENDPOINT_ENV[agent]} for remote agent orchestration.")
    return value


def run_remote_audit(text: str) -> dict:
    extracted = _post_json(_endpoint("memory_extractor"), {"text": text})
    classified = _post_json(_endpoint("authority_classifier"), {"items": extracted["items"]})
    conflicts = _post_json(
        _endpoint("conflict_detector"),
        {"items": extracted["items"], "classifications": classified["classifications"]},
    )
    gates = _post_json(
        _endpoint("verification_gate"),
        {"classifications": classified["classifications"], "conflicts": conflicts["conflicts"]},
    )
    mapped = _post_json(
        _endpoint("authority_mapper"),
        {"items": extracted["items"], "classifications": classified["classifications"]},
    )
    report = _post_json(
        _endpoint("report_writer"),
        {
            "items": extracted["items"],
            "classifications": classified["classifications"],
            "conflicts": conflicts["conflicts"],
            "verification_gates": gates["verification_gates"],
            "authority_map": mapped["authority_map"],
        },
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
