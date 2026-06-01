from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from audit_pipeline import run_audit
from agents.authority_classifier import classify_items
from agents.authority_mapper import authority_map
from agents.conflict_detector import detect_conflicts
from agents.memory_extractor import extract_memories
from agents.report_writer import write_report
from agents.verification_gate import build_verification_gates
from item_proxy import MemoryItemProxy
from remote_pipeline import run_remote_audit


ROOT = Path(__file__).parent


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path != "/":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        body = (ROOT / "templates" / "index.html").read_bytes()
        self._send(200, body, "text/html; charset=utf-8")

    def do_HEAD(self) -> None:
        path = urlparse(self.path).path
        if path != "/":
            self.send_response(404)
            self.end_headers()
            return
        size = (ROOT / "templates" / "index.html").stat().st_size
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(size))
        self.end_headers()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        routes = {
            "/api/audit": self._handle_audit,
            "/agents/memory-extractor": self._handle_memory_extractor,
            "/agents/authority-classifier": self._handle_authority_classifier,
            "/agents/conflict-detector": self._handle_conflict_detector,
            "/agents/verification-gate": self._handle_verification_gate,
            "/agents/authority-mapper": self._handle_authority_mapper,
            "/agents/report-writer": self._handle_report_writer,
        }
        handler = routes.get(path)
        if handler is None:
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        try:
            handler(self._read_json())
        except Exception as error:
            body = json.dumps({"error": str(error)}).encode("utf-8")
            self._send(500, body, "application/json")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8") or "{}")

    def _send_json(self, data: dict, status: int = 200) -> None:
        self._send(status, json.dumps(data).encode("utf-8"), "application/json")

    def _handle_audit(self, payload: dict) -> None:
        text = str(payload.get("text", "")).strip()
        if not text:
            self._send_json({"error": "Paste an instruction or memory file to audit."}, 400)
            return
        if os.environ.get("USE_REMOTE_AGENTS", "").lower() in {"1", "true", "yes"}:
            self._send_json(run_remote_audit(text))
            return
        self._send_json(run_audit(text))

    def _handle_memory_extractor(self, payload: dict) -> None:
        text = str(payload.get("text", "")).strip()
        if not text:
            self._send_json({"error": "Provide text to extract."}, 400)
            return
        items = extract_memories(text)
        self._send_json({"agent": "memory_extractor", "items": [item.to_dict() for item in items]})

    def _handle_authority_classifier(self, payload: dict) -> None:
        items = [MemoryItemProxy(item) for item in payload.get("items", [])]
        if not items:
            self._send_json({"error": "Provide extracted items to classify."}, 400)
            return
        self._send_json({"agent": "authority_classifier", "classifications": classify_items(items)})

    def _handle_conflict_detector(self, payload: dict) -> None:
        items = [MemoryItemProxy(item) for item in payload.get("items", [])]
        classifications = payload.get("classifications", [])
        if not items or not classifications:
            self._send_json({"error": "Provide items and classifications."}, 400)
            return
        self._send_json({"agent": "conflict_detector", "conflicts": detect_conflicts(items, classifications)})

    def _handle_verification_gate(self, payload: dict) -> None:
        classifications = payload.get("classifications", [])
        conflicts = payload.get("conflicts", [])
        if not classifications:
            self._send_json({"error": "Provide classifications."}, 400)
            return
        self._send_json({"agent": "verification_gate", "verification_gates": build_verification_gates(classifications, conflicts)})

    def _handle_authority_mapper(self, payload: dict) -> None:
        items = [MemoryItemProxy(item) for item in payload.get("items", [])]
        classifications = payload.get("classifications", [])
        if not items or not classifications:
            self._send_json({"error": "Provide items and classifications."}, 400)
            return
        self._send_json({"agent": "authority_mapper", "authority_map": authority_map(items, classifications)})

    def _handle_report_writer(self, payload: dict) -> None:
        items = payload.get("items", [])
        classifications = payload.get("classifications", [])
        conflicts = payload.get("conflicts", [])
        gates = payload.get("verification_gates", [])
        mapped_authority = payload.get("authority_map", [])
        if not items or not classifications:
            self._send_json({"error": "Provide items and classifications."}, 400)
            return
        self._send_json({"agent": "report_writer", "report": write_report(items, classifications, conflicts, gates, mapped_authority)})

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main() -> None:
    port = int(os.environ.get("PORT", "8788"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving AI Memory Authority Auditor on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
