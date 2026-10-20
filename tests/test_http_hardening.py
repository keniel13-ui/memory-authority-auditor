"""Regression tests for request parsing, remote orchestration, and Sentry defaults.

Each test names the failure mode it guards. Servers bind to 127.0.0.1 on an
ephemeral port and run in a daemon thread, so no network access is needed.
"""

from __future__ import annotations

import http.client
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import threading
import time

import pytest

import agent_service
import app
import remote_pipeline
from audit_pipeline import run_audit
from http_json import RequestError, read_json_object
from observability import sentry_options


ROOT = Path(__file__).parents[1]
SAMPLE = (ROOT / "samples" / "sample_agents.md").read_text(encoding="utf-8")


@pytest.fixture
def serve():
    servers = []

    def _start(handler_cls) -> int:
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        servers.append(server)
        return server.server_address[1]

    yield _start
    for server in servers:
        server.shutdown()
        server.server_close()


class QuietApp(app.Handler):
    def log_message(self, fmt, *args):
        pass


class QuietAgent(agent_service.Handler):
    def log_message(self, fmt, *args):
        pass


def _raw_post(port: int, path: str, headers: dict[str, str], body: bytes = b"") -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.putrequest("POST", path)
    for key, value in headers.items():
        conn.putheader(key, value)
    conn.endheaders()
    if body:
        conn.send(body)
    response = conn.getresponse()
    payload = json.loads(response.read().decode("utf-8"))
    conn.close()
    return response.status, payload


def _post_json(port: int, path: str, payload) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    return _raw_post(port, path, {"Content-Type": "application/json", "Content-Length": str(len(body))}, body)


# --- read_json_object unit behavior -------------------------------------------------


class _Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.requested: list[int] = []

    def read(self, n: int = -1) -> bytes:
        self.requested.append(n)
        return self.data if n < 0 else self.data[:n]


def test_oversized_content_length_is_rejected_before_reading():
    # Failure mode: a forged Content-Length made the handler allocate and wait
    # for an arbitrarily large body.
    reader = _Reader(b"{}")
    with pytest.raises(RequestError) as caught:
        read_json_object({"Content-Length": "999999999"}, reader, limit=1024)
    assert caught.value.status == 413
    assert reader.requested == []


def test_negative_content_length_is_rejected_not_read_to_eof():
    # Failure mode: int("-1") passed to rfile.read(-1) blocks until the client
    # closes the socket, pinning a server thread.
    reader = _Reader(b"{}")
    with pytest.raises(RequestError) as caught:
        read_json_object({"Content-Length": "-1"}, reader, limit=1024)
    assert caught.value.status == 400
    assert reader.requested == []


@pytest.mark.parametrize(
    "headers, body",
    [
        ({"Content-Length": "abc"}, b"{}"),
        ({"Content-Length": "8"}, b"not json"),
        ({"Content-Length": "2"}, b"\xff\xfe"),
        ({"Content-Length": "2"}, b"[]"),
        ({"Content-Length": "10"}, b"{}"),
    ],
)
def test_malformed_bodies_raise_client_errors(headers, body):
    with pytest.raises(RequestError) as caught:
        read_json_object(headers, _Reader(body), limit=1024)
    assert caught.value.status == 400


def test_missing_content_length_keeps_empty_body_behavior():
    assert read_json_object({}, _Reader(b""), limit=1024) == {}


# --- web app ----------------------------------------------------------------------


def test_app_audit_happy_path_matches_local_pipeline(serve):
    port = serve(QuietApp)
    status, payload = _post_json(port, "/api/audit", {"text": SAMPLE})
    assert status == 200
    assert payload == json.loads(json.dumps(run_audit(SAMPLE)))


@pytest.mark.parametrize(
    "path, payload",
    [
        ("/api/audit", ["not", "an", "object"]),
        ("/agents/authority-classifier", {"items": "M001"}),
        ("/agents/authority-classifier", {"items": [{"id": "M001", "source_line": "line seven"}]}),
        ("/agents/authority-classifier", {"items": [{"id": "M001", "signals": "approval"}]}),
        ("/agents/conflict-detector", {"items": [{"id": "M001"}], "classifications": ["governs"]}),
    ],
)
def test_app_rejects_malformed_payloads_with_400(serve, payload, path):
    # Failure mode: malformed client input surfaced as HTTP 500 with a raw
    # AttributeError/ValueError message.
    port = serve(QuietApp)
    status, body = _post_json(port, path, payload)
    assert status == 400, body
    assert "error" in body


def test_app_rejects_oversized_declared_body_with_413(serve, monkeypatch):
    monkeypatch.setenv("MAX_REQUEST_BYTES", "64")
    port = serve(QuietApp)
    status, body = _raw_post(port, "/api/audit", {"Content-Length": "100000"})
    assert status == 413
    assert "limit" in body["error"]


def test_app_hides_internal_exception_text(serve, monkeypatch, capsys):
    # Failure mode: unexpected exceptions echoed internal detail to the client.
    def boom(_text):
        raise RuntimeError("secret internal path /srv/config")

    monkeypatch.setattr(app, "run_audit", boom)
    port = serve(QuietApp)
    status, body = _post_json(port, "/api/audit", {"text": "- a rule"})
    assert status == 500
    assert body == {"error": "Internal server error."}


def test_stalled_body_times_out_instead_of_pinning_thread(serve, monkeypatch):
    # Failure mode: a client that declares a body and never sends it held the
    # handler thread forever (StreamRequestHandler.timeout defaults to None).
    monkeypatch.setattr(QuietApp, "timeout", 0.5)
    port = serve(QuietApp)
    with socket.create_connection(("127.0.0.1", port), timeout=10) as sock:
        sock.sendall(b"POST /api/audit HTTP/1.1\r\nHost: x\r\nContent-Length: 50\r\n\r\n{")
        started = time.monotonic()
        data = sock.recv(4096)
        elapsed = time.monotonic() - started
    assert elapsed < 5
    assert b" 408 " in data.split(b"\r\n", 1)[0]


# --- agent service ----------------------------------------------------------------


def test_agent_service_client_and_server_errors_are_distinguished(serve, monkeypatch):
    monkeypatch.setattr(agent_service, "ROLE", "authority_classifier")
    port = serve(QuietAgent)
    status, body = _post_json(port, "/", {"items": [1, 2]})
    assert status == 400
    assert body["agent"] == "authority_classifier"

    def boom(_items):
        raise KeyError("internal")

    monkeypatch.setattr(agent_service, "classify_items", boom)
    status, body = _post_json(port, "/", {"items": [{"id": "M001", "text": "x"}]})
    assert status == 500
    assert body == {"error": "Internal agent error.", "agent": "authority_classifier"}


# --- remote orchestration -----------------------------------------------------------


AGENT_PATHS = {
    "MEMORY_EXTRACTOR_URL": "/agents/memory-extractor",
    "AUTHORITY_CLASSIFIER_URL": "/agents/authority-classifier",
    "CONFLICT_DETECTOR_URL": "/agents/conflict-detector",
    "VERIFICATION_GATE_URL": "/agents/verification-gate",
    "AUTHORITY_MAPPER_URL": "/agents/authority-mapper",
    "REPORT_WRITER_URL": "/agents/report-writer",
}


def _point_agents_at(monkeypatch, port: int) -> None:
    for env, path in AGENT_PATHS.items():
        monkeypatch.setenv(env, f"http://127.0.0.1:{port}{path}")


def test_remote_pipeline_matches_local_pipeline(serve, monkeypatch):
    port = serve(QuietApp)
    _point_agents_at(monkeypatch, port)
    assert remote_pipeline.run_remote_audit(SAMPLE) == json.loads(json.dumps(run_audit(SAMPLE)))


class _FailingAgent(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        if self.path.endswith("classifier"):
            body = json.dumps({"error": "Provide extracted items to classify."}).encode()
            self.send_response(400)
        elif self.path.endswith("missing"):
            body = json.dumps({"agent": "memory_extractor"}).encode()
            self.send_response(200)
        else:
            body = json.dumps({"agent": "memory_extractor", "items": []}).encode()
            self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def test_remote_agent_http_error_names_the_agent(serve, monkeypatch):
    # Failure mode: a 400 from one agent surfaced as a bare urllib HTTPError
    # ("HTTP Error 400: Bad Request") with no hint which agent failed.
    port = serve(_FailingAgent)
    monkeypatch.setenv("MEMORY_EXTRACTOR_URL", f"http://127.0.0.1:{port}/extractor")
    monkeypatch.setenv("AUTHORITY_CLASSIFIER_URL", f"http://127.0.0.1:{port}/classifier")
    with pytest.raises(remote_pipeline.RemoteAgentError) as caught:
        remote_pipeline.run_remote_audit("- rule")
    assert caught.value.agent == "authority_classifier"
    assert "http 400" in str(caught.value)
    assert "Provide extracted items" in str(caught.value)


def test_remote_agent_missing_field_is_reported(serve, monkeypatch):
    # Failure mode: a malformed agent response raised KeyError: 'items'.
    port = serve(_FailingAgent)
    monkeypatch.setenv("MEMORY_EXTRACTOR_URL", f"http://127.0.0.1:{port}/missing")
    with pytest.raises(remote_pipeline.RemoteAgentError, match="missing 'items'"):
        remote_pipeline.run_remote_audit("- rule")


def test_remote_agent_unreachable_is_reported(monkeypatch):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        free_port = sock.getsockname()[1]
    monkeypatch.setenv("MEMORY_EXTRACTOR_URL", f"http://127.0.0.1:{free_port}/")
    with pytest.raises(remote_pipeline.RemoteAgentError) as caught:
        remote_pipeline.run_remote_audit("- rule")
    assert caught.value.agent == "memory_extractor"


def test_app_maps_remote_failures_to_502(serve, monkeypatch):
    agent_port = serve(_FailingAgent)
    monkeypatch.setenv("USE_REMOTE_AGENTS", "1")
    monkeypatch.setenv("MEMORY_EXTRACTOR_URL", f"http://127.0.0.1:{agent_port}/extractor")
    monkeypatch.setenv("AUTHORITY_CLASSIFIER_URL", f"http://127.0.0.1:{agent_port}/classifier")
    port = serve(QuietApp)
    status, body = _post_json(port, "/api/audit", {"text": "- rule"})
    assert status == 502
    assert body["error"].startswith("authority_classifier agent failed")


# --- Sentry defaults ----------------------------------------------------------------


def test_sentry_disabled_without_dsn():
    assert sentry_options({}) is None


def test_sentry_pii_is_opt_in():
    # Failure mode: send_default_pii=True was hardcoded, widening what leaves
    # the machine whenever SENTRY_DSN was set for a private memory-file audit.
    assert sentry_options({"SENTRY_DSN": "https://k@example.invalid/1"})["send_default_pii"] is False
    opted_in = sentry_options({"SENTRY_DSN": "https://k@example.invalid/1", "SENTRY_SEND_DEFAULT_PII": "1"})
    assert opted_in["send_default_pii"] is True
