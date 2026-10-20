from __future__ import annotations

import json
import os
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from agents.authority_classifier import classify_items
from agents.authority_mapper import authority_map
from agents.conflict_detector import detect_conflicts
from agents.memory_extractor import extract_memories
from agents.report_writer import write_report
from agents.verification_gate import build_verification_gates
from http_json import REQUEST_SOCKET_TIMEOUT_SECONDS, RequestError, item_list, memory_items, read_json_object


ROLE = os.environ.get("AGENT_ROLE", "").strip()


def handle_role(payload: dict) -> dict:
    if ROLE == "memory_extractor":
        text = str(payload.get("text", "")).strip()
        if not text:
            raise ValueError("Provide text to extract.")
        items = extract_memories(text)
        return {"agent": ROLE, "items": [item.to_dict() for item in items]}

    if ROLE == "authority_classifier":
        items = memory_items(payload)
        if not items:
            raise ValueError("Provide extracted items to classify.")
        return {"agent": ROLE, "classifications": classify_items(items)}

    if ROLE == "conflict_detector":
        items = memory_items(payload)
        classifications = item_list(payload, "classifications")
        if not items or not classifications:
            raise ValueError("Provide items and classifications.")
        return {"agent": ROLE, "conflicts": detect_conflicts(items, classifications)}

    if ROLE == "verification_gate":
        classifications = item_list(payload, "classifications")
        conflicts = item_list(payload, "conflicts")
        if not classifications:
            raise ValueError("Provide classifications.")
        return {"agent": ROLE, "verification_gates": build_verification_gates(classifications, conflicts)}

    if ROLE == "authority_mapper":
        items = memory_items(payload)
        classifications = item_list(payload, "classifications")
        if not items or not classifications:
            raise ValueError("Provide items and classifications.")
        return {"agent": ROLE, "authority_map": authority_map(items, classifications)}

    if ROLE == "report_writer":
        items = item_list(payload, "items")
        classifications = item_list(payload, "classifications")
        conflicts = item_list(payload, "conflicts")
        gates = item_list(payload, "verification_gates")
        mapped_authority = item_list(payload, "authority_map")
        if not items or not classifications:
            raise ValueError("Provide items and classifications.")
        return {"agent": ROLE, "report": write_report(items, classifications, conflicts, gates, mapped_authority)}

    raise ValueError(f"Unknown or missing AGENT_ROLE: {ROLE}")


class Handler(BaseHTTPRequestHandler):
    timeout = REQUEST_SOCKET_TIMEOUT_SECONDS

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path != "/health":
            self._send_json({"error": "Not found"}, 404)
            return
        self._send_json({"ok": True, "agent": ROLE})

    def do_POST(self) -> None:
        try:
            payload = read_json_object(self.headers, self.rfile)
            self._send_json(handle_role(payload))
        except RequestError as error:
            self._send_json({"error": str(error), "agent": ROLE}, error.status)
        except ValueError as error:
            self._send_json({"error": str(error), "agent": ROLE}, 400)
        except Exception:
            # Internal failures are server errors, not client errors; keep the
            # detail in the service log instead of the response body.
            traceback.print_exc()
            self._send_json({"error": "Internal agent error.", "agent": ROLE}, 500)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving {ROLE or 'unknown'} agent on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
