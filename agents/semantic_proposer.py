from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from typing import Callable

from agents.semantic_confirmer import ALLOWED_RELATION_TYPES


ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
PROPOSER_SCHEMA_FIELDS = {
    "type",
    "source_item_id",
    "target_item_id",
    "cited_evidence_span",
    "scope_terms",
    "rationale",
    "confidence",
}


class SemanticProposerError(RuntimeError):
    pass


def build_authority_change_prompt(items: list[dict]) -> str:
    item_lines = "\n".join(
        f"- {item['id']} [{item.get('section', 'Unsectioned')}]: {item['text']}"
        for item in items
    )
    relation_types = " | ".join(sorted(ALLOWED_RELATION_TYPES))
    return f"""You are proposing candidate authority-change relations between agent memory items.

You do not emit verdicts. A deterministic confirmer will judge your proposals.

Allowed relation types:
{relation_types}

Return ONLY valid JSON with this shape:
{{
  "proposals": [
    {{
      "type": "supersedes",
      "source_item_id": "M002",
      "target_item_id": "M001",
      "cited_evidence_span": "verbatim substring from the source item",
      "scope_terms": ["shared scope term"],
      "rationale": "short reason",
      "confidence": 0.72
    }}
  ]
}}

Rules:
- The cited_evidence_span must be copied from the source item text.
- scope_terms must describe the shared subject/scope and appear in both source and target.
- If the text only talks about supersession, contradiction, narrowing, or authority transfer as a topic, return an empty proposals list.
- Do not include privilege-tier or bitemporal relation classes in v0.
- If unsure, lower confidence instead of inventing a relation.

Items:
{item_lines}
"""


def _json_from_text(text: str) -> dict:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as error:
        raise SemanticProposerError("proposer returned non-json output") from error
    if isinstance(parsed, list):
        parsed = {"proposals": parsed}
    if not isinstance(parsed, dict):
        raise SemanticProposerError("proposer json root must be an object")
    return parsed


def _normalize_proposal(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise SemanticProposerError("proposal must be an object")
    missing = PROPOSER_SCHEMA_FIELDS - set(raw)
    if missing:
        raise SemanticProposerError(f"proposal missing required field(s): {sorted(missing)}")
    relation_type = str(raw["type"]).strip()
    if relation_type not in ALLOWED_RELATION_TYPES:
        raise SemanticProposerError(f"unsupported relation type: {relation_type}")
    scope_terms = raw["scope_terms"]
    if not isinstance(scope_terms, list) or not all(isinstance(term, str) for term in scope_terms):
        raise SemanticProposerError("scope_terms must be a list of strings")
    try:
        confidence = float(raw["confidence"])
    except (TypeError, ValueError) as error:
        raise SemanticProposerError("confidence must be numeric") from error
    return {
        "type": relation_type,
        "source_item_id": str(raw["source_item_id"]).strip(),
        "target_item_id": str(raw["target_item_id"]).strip(),
        "cited_evidence_span": str(raw["cited_evidence_span"]).strip(),
        "scope_terms": [term.strip() for term in scope_terms if term.strip()],
        "rationale": str(raw["rationale"]).strip(),
        "confidence": confidence,
    }


def parse_proposals(text: str) -> list[dict]:
    parsed = _json_from_text(text)
    proposals = parsed.get("proposals", [])
    if not isinstance(proposals, list):
        raise SemanticProposerError("proposals must be a list")
    return [_normalize_proposal(proposal) for proposal in proposals]


def _anthropic_text_from_response(payload: dict) -> str:
    chunks = payload.get("content", [])
    texts = [
        chunk.get("text", "")
        for chunk in chunks
        if isinstance(chunk, dict) and chunk.get("type") == "text"
    ]
    return "\n".join(texts).strip()


def call_anthropic(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SemanticProposerError("ANTHROPIC_API_KEY not present in runtime environment")
    body = json.dumps({
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1200,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    request = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise SemanticProposerError("anthropic proposer call failed") from error
    text = _anthropic_text_from_response(payload)
    if not text:
        raise SemanticProposerError("anthropic proposer returned no text")
    return text


def call_local_llama(prompt: str) -> str:
    try:
        completed = subprocess.run(
            ["ollama", "run", "llama3.2", prompt],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.SubprocessError) as error:
        raise SemanticProposerError("local llama proposer call failed") from error
    return completed.stdout.strip()


def propose_authority_changes(
    items: list[dict],
    provider: Callable[[str], str] | None = None,
) -> dict:
    prompt = build_authority_change_prompt(items)
    engine = "injected"
    if provider is None:
        if os.environ.get("ANTHROPIC_API_KEY"):
            provider = call_anthropic
            engine = "anthropic"
        else:
            provider = call_local_llama
            engine = "local_llama3.2"
    text = provider(prompt)
    return {
        "engine": engine,
        "proposals": parse_proposals(text),
    }
