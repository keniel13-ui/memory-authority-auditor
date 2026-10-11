from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from agents.authority_classifier import classify_items
from agents.authority_mapper import authority_map
from agents.conflict_detector import detect_conflicts
from agents.memory_extractor import extract_memories, extract_with_ledger
from agents.report_writer import write_report
from agents.verification_gate import build_verification_gates
from item_proxy import MemoryItemProxy


ROLE = os.environ.get("AGENT_ROLE", "").strip()


class MalformedPayload(ValueError):
    """The request itself is unusable: a required key is absent or has the wrong type.

    Distinct from an empty-but-well-formed payload. EMPTY_SET_CONTRACT_V0_2026-09-04 R1/R2:
    an empty extracted set is a verdict, not a client error. Before this class existed, every
    role raised a bare ValueError for both cases and the handler returned 400 for both, so a
    legitimate zero-item extraction was reported to the caller as a bad request and the web
    router then reported that to the user as a 500.
    """


def _require_list(payload: dict, key: str) -> list:
    """Return payload[key] as a list. Absent or wrong-typed is malformed; empty is not."""
    if key not in payload:
        raise MalformedPayload(f"Missing required key: {key}.")
    value = payload[key]
    if not isinstance(value, list):
        raise MalformedPayload(f"Key {key} must be a list, got {type(value).__name__}.")
    return value


def handle_role(payload: dict) -> dict:
    if ROLE == "memory_extractor":
        if "text" not in payload:
            raise MalformedPayload("Missing required key: text.")
        text = str(payload.get("text", "")).strip()
        if not text:
            raise MalformedPayload("Provide text to extract.")
        items, accounting = extract_with_ledger(text)
        # D1: the ledger must survive the remote pipeline. It is returned here so the
        # router can forward it to the report writer; a field that stops at this tier
        # never reaches the user and does not satisfy the contract.
        return {"agent": ROLE, "items": [item.to_dict() for item in items], "accounting": accounting}

    if ROLE == "authority_classifier":
        items = [MemoryItemProxy(item) for item in _require_list(payload, "items")]
        return {"agent": ROLE, "classifications": classify_items(items)}

    if ROLE == "conflict_detector":
        items = [MemoryItemProxy(item) for item in _require_list(payload, "items")]
        classifications = _require_list(payload, "classifications")
        return {"agent": ROLE, "conflicts": detect_conflicts(items, classifications)}

    if ROLE == "verification_gate":
        classifications = _require_list(payload, "classifications")
        conflicts = payload.get("conflicts", [])
        return {"agent": ROLE, "verification_gates": build_verification_gates(classifications, conflicts)}

    if ROLE == "authority_mapper":
        items = [MemoryItemProxy(item) for item in _require_list(payload, "items")]
        classifications = _require_list(payload, "classifications")
        return {"agent": ROLE, "authority_map": authority_map(items, classifications)}

    if ROLE == "report_writer":
        items = _require_list(payload, "items")
        classifications = _require_list(payload, "classifications")
        conflicts = payload.get("conflicts", [])
        gates = payload.get("verification_gates", [])
        mapped_authority = payload.get("authority_map", [])
        accounting = payload.get("accounting")
        return {"agent": ROLE, "report": write_report(items, classifications, conflicts, gates, mapped_authority, accounting)}

    raise ValueError(f"Unknown or missing AGENT_ROLE: {ROLE}")


class Handler(BaseHTTPRequestHandler):
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
        # EMPTY_SET_CONTRACT_V0 R2: only a malformed request is a client error. Previously this
        # returned 400 for every exception, which meant a legitimate empty extraction and a
        # genuine server fault were reported to the caller as the same thing.
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except (ValueError, UnicodeDecodeError) as error:
            self._send_json({"error": f"Unparseable request body: {error}", "agent": ROLE}, 400)
            return
        try:
            self._send_json(handle_role(payload))
        except MalformedPayload as error:
            self._send_json({"error": str(error), "agent": ROLE}, 400)
        except Exception as error:
            self._send_json({"error": str(error), "agent": ROLE}, 500)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving {ROLE or 'unknown'} agent on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
