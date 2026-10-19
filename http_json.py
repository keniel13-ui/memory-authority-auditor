"""Bounded JSON request parsing shared by the web app and the agent services.

Both servers are stdlib ``http.server`` handlers deployed as public,
unauthenticated Cloud Run services, so request parsing must not trust the
client: a forged ``Content-Length`` must not make the handler allocate an
unbounded buffer or block forever, and malformed bodies must produce a
client error instead of an internal server error.
"""

from __future__ import annotations

import json
import os
import socket
from typing import BinaryIO, Mapping

from item_proxy import MemoryItemProxy

DEFAULT_MAX_REQUEST_BYTES = 4 * 1024 * 1024
# Seconds a handler waits on a silent client socket before giving up. Applied
# as ``StreamRequestHandler.timeout`` so a stalled upload cannot pin a thread.
REQUEST_SOCKET_TIMEOUT_SECONDS = 30


class RequestError(ValueError):
    """A client-side request problem that maps to a 4xx response."""

    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.status = status


def max_request_bytes() -> int:
    raw = os.environ.get("MAX_REQUEST_BYTES", "").strip()
    if not raw:
        return DEFAULT_MAX_REQUEST_BYTES
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_MAX_REQUEST_BYTES
    return value if value > 0 else DEFAULT_MAX_REQUEST_BYTES


def read_json_object(headers: Mapping[str, str], rfile: BinaryIO, limit: int | None = None) -> dict:
    """Read and decode a JSON object body, enforcing a byte limit.

    A missing ``Content-Length`` is treated as an empty body, matching the
    previous behavior (handlers then answer with their own 400 message).
    """
    limit = max_request_bytes() if limit is None else limit
    raw_length = headers.get("Content-Length")
    if raw_length is None or str(raw_length).strip() == "":
        length = 0
    else:
        try:
            length = int(str(raw_length).strip())
        except ValueError as error:
            raise RequestError("Content-Length must be an integer.") from error
        if length < 0:
            raise RequestError("Content-Length must not be negative.")
    if length > limit:
        raise RequestError(f"Request body exceeds the {limit}-byte limit.", status=413)

    try:
        body = rfile.read(length) if length else b""
    except (TimeoutError, socket.timeout) as error:
        raise RequestError("Timed out waiting for the request body.", status=408) from error
    if len(body) != length:
        raise RequestError("Request body ended before Content-Length bytes were received.")
    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except UnicodeDecodeError as error:
        raise RequestError("Request body must be UTF-8 encoded JSON.") from error
    except json.JSONDecodeError as error:
        raise RequestError("Request body must be valid JSON.") from error
    if not isinstance(payload, dict):
        raise RequestError("Request body must be a JSON object.")
    return payload


def item_list(payload: dict, key: str = "items") -> list[dict]:
    """Return ``payload[key]`` as a list of objects or raise ``RequestError``."""
    value = payload.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise RequestError(f"'{key}' must be a list of objects.")
    return value


def memory_items(payload: dict) -> list[MemoryItemProxy]:
    """Build item proxies from ``payload['items']``, mapping bad shapes to 400."""
    try:
        return [MemoryItemProxy(item) for item in item_list(payload, "items")]
    except (TypeError, ValueError) as error:
        if isinstance(error, RequestError):
            raise
        raise RequestError(f"Invalid memory item: {error}") from error
