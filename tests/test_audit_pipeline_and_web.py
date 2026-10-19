"""Coverage for the deployed audit path: pipeline, CLI, web app, agent services.

These paths back the live demo and the README's CLI smoke test but had no
tests. Servers bind to 127.0.0.1 on an ephemeral port in a daemon thread.
"""

from __future__ import annotations

import http.client
import json
import os
from http.server import ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import threading

import pytest

import agent_service
import app
from audit_pipeline import run_audit


ROOT = Path(__file__).parents[1]
SAMPLE_PATH = ROOT / "samples" / "sample_agents.md"
SAMPLE = SAMPLE_PATH.read_text(encoding="utf-8")
PIPELINE_ORDER = [
    "memory_extractor",
    "authority_classifier",
    "conflict_detector",
    "verification_gate",
    "authority_mapper",
    "report_writer",
]


class QuietApp(app.Handler):
    def log_message(self, fmt, *args):
        pass


@pytest.fixture
def app_port():
    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietApp)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    yield server.server_address[1]
    server.shutdown()
    server.server_close()


def _request(port: int, method: str, path: str, payload=None) -> tuple[int, dict, bytes]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {} if body is None else {"Content-Type": "application/json"}
    conn.request(method, path, body=body, headers=headers)
    response = conn.getresponse()
    data = response.read()
    result = (response.status, dict(response.getheaders()), data)
    conn.close()
    return result


# --- pipeline -------------------------------------------------------------------


def test_sample_audit_is_deterministic():
    assert run_audit(SAMPLE) == run_audit(SAMPLE)


def test_sample_audit_counts_are_internally_consistent():
    result = run_audit(SAMPLE)
    counts = result["report"]["counts"]
    assert counts["items"] == len(result["items"]) == len(result["classifications"])
    assert counts["gates"] == len(result["verification_gates"])
    assert counts["authority_categories"] == len(result["authority_map"])
    assert sum(counts["conflicts"].values()) == len(result["conflicts"])
    assert sum(counts["labels"].values()) == counts["items"]
    assert [step["agent"] for step in result["trace"]] == PIPELINE_ORDER


def test_sample_audit_snapshot_at_current_head():
    # Pins the bundled sample's local result so a detector change is visible.
    # The README "Example Output" numbers describe the deployed sample and do
    # not match this local run; see the docs PR for that discrepancy.
    report = run_audit(SAMPLE)["report"]
    assert report["posture"] == "needs_review"
    assert report["counts"]["items"] == 12
    assert report["counts"]["risk_high"] == 7
    assert report["counts"]["conflicts"] == {"high": 5, "medium": 1}
    assert report["counts"]["gates"] == 17
    assert report["counts"]["authority_categories"] == 2


def test_empty_input_yields_no_items():
    result = run_audit("")
    assert result["items"] == []
    assert result["report"]["counts"]["items"] == 0


# --- CLI --------------------------------------------------------------------------


def test_audit_cli_prints_pipeline_json():
    completed = subprocess.run(
        [sys.executable, "audit_cli.py", str(SAMPLE_PATH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        env={key: value for key, value in os.environ.items() if not key.startswith("SENTRY_")},
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == json.loads(json.dumps(run_audit(SAMPLE)))


def test_audit_cli_usage_error_exit_code():
    completed = subprocess.run(
        [sys.executable, "audit_cli.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 2
    assert "Usage" in completed.stderr


# --- web app ----------------------------------------------------------------------


def test_index_page_is_served(app_port):
    status, headers, body = _request(app_port, "GET", "/")
    assert status == 200
    assert headers["Content-Type"].startswith("text/html")
    assert int(headers["Content-Length"]) == len(body)
    assert b"<html" in body.lower()


def test_head_matches_get_length(app_port):
    _, get_headers, _ = _request(app_port, "GET", "/")
    status, head_headers, body = _request(app_port, "HEAD", "/")
    assert status == 200
    assert body == b""
    assert head_headers["Content-Length"] == get_headers["Content-Length"]


@pytest.mark.parametrize("method, path", [("GET", "/missing"), ("HEAD", "/missing"), ("POST", "/api/unknown")])
def test_unknown_routes_return_404(app_port, method, path):
    status, _, _ = _request(app_port, method, path, {} if method == "POST" else None)
    assert status == 404


def test_api_audit_requires_text(app_port):
    status, _, body = _request(app_port, "POST", "/api/audit", {"text": "   "})
    assert status == 400
    assert "error" in json.loads(body)


def test_api_audit_matches_pipeline(app_port):
    status, _, body = _request(app_port, "POST", "/api/audit", {"text": SAMPLE})
    assert status == 200
    assert json.loads(body) == json.loads(json.dumps(run_audit(SAMPLE)))


def test_per_agent_endpoints_compose_to_the_pipeline(app_port):
    # The Cloud Run deployment chains these same contracts across services,
    # so composing them by hand must equal the in-process pipeline.
    expected = json.loads(json.dumps(run_audit(SAMPLE)))

    def post(path, payload):
        status, _, body = _request(app_port, "POST", path, payload)
        assert status == 200, body
        return json.loads(body)

    items = post("/agents/memory-extractor", {"text": SAMPLE})["items"]
    classifications = post("/agents/authority-classifier", {"items": items})["classifications"]
    conflicts = post("/agents/conflict-detector", {"items": items, "classifications": classifications})["conflicts"]
    gates = post(
        "/agents/verification-gate", {"classifications": classifications, "conflicts": conflicts}
    )["verification_gates"]
    mapped = post("/agents/authority-mapper", {"items": items, "classifications": classifications})["authority_map"]
    report = post(
        "/agents/report-writer",
        {
            "items": items,
            "classifications": classifications,
            "conflicts": conflicts,
            "verification_gates": gates,
            "authority_map": mapped,
        },
    )["report"]

    assert items == expected["items"]
    assert classifications == expected["classifications"]
    assert conflicts == expected["conflicts"]
    assert gates == expected["verification_gates"]
    assert mapped == expected["authority_map"]
    assert report == expected["report"]


# --- agent service ----------------------------------------------------------------


def test_agent_service_roles_compose_to_the_pipeline(monkeypatch):
    expected = json.loads(json.dumps(run_audit(SAMPLE)))

    def call(role, payload):
        monkeypatch.setattr(agent_service, "ROLE", role)
        result = agent_service.handle_role(payload)
        assert result["agent"] == role
        return json.loads(json.dumps(result))

    items = call("memory_extractor", {"text": SAMPLE})["items"]
    classifications = call("authority_classifier", {"items": items})["classifications"]
    conflicts = call("conflict_detector", {"items": items, "classifications": classifications})["conflicts"]
    gates = call("verification_gate", {"classifications": classifications, "conflicts": conflicts})[
        "verification_gates"
    ]
    mapped = call("authority_mapper", {"items": items, "classifications": classifications})["authority_map"]
    report = call(
        "report_writer",
        {
            "items": items,
            "classifications": classifications,
            "conflicts": conflicts,
            "verification_gates": gates,
            "authority_map": mapped,
        },
    )["report"]
    assert report == expected["report"]


def test_agent_service_rejects_unknown_role(monkeypatch):
    monkeypatch.setattr(agent_service, "ROLE", "")
    with pytest.raises(ValueError, match="AGENT_ROLE"):
        agent_service.handle_role({"text": "x"})
