from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.memory_extractor import extract_memories
from agents.semantic_confirmer import confirm_authority_changes
from agents.semantic_proposer import (
    SemanticProposerError,
    build_authority_change_prompt,
    parse_proposals,
    propose_authority_changes,
)


SCRATCH = Path(__file__).parent / "fixtures" / "path_a_dev_scratch_2026_07_01.json"


def _scratch_case(case_id: str) -> dict:
    cases = json.loads(SCRATCH.read_text())["cases"]
    return next(case for case in cases if case["id"] == case_id)


def _items(case: dict) -> list[dict]:
    return [item.to_dict() for item in extract_memories(case["text"])]


def test_prompt_pins_schema_enum_and_negative_boundary():
    case = _scratch_case("dev_scratch_supersession")
    prompt = build_authority_change_prompt(_items(case))

    assert "supersedes" in prompt
    assert "narrows_scope" in prompt
    assert "contradicts" in prompt
    assert "transfers_authority" in prompt
    assert "cited_evidence_span" in prompt
    assert "scope_terms" in prompt
    assert "return an empty proposals list" in prompt
    assert "privilege-tier" in prompt


def test_parse_proposals_accepts_exact_v0_schema():
    payload = json.dumps({
        "proposals": [
            {
                "type": "supersedes",
                "source_item_id": "M002",
                "target_item_id": "M001",
                "cited_evidence_span": "shared setup admin access is retired",
                "scope_terms": ["contractors", "admin"],
                "rationale": "Current rule retires the old shared setup account.",
                "confidence": "0.74",
            }
        ]
    })

    proposals = parse_proposals(payload)

    assert proposals == [
        {
            "type": "supersedes",
            "source_item_id": "M002",
            "target_item_id": "M001",
            "cited_evidence_span": "shared setup admin access is retired",
            "scope_terms": ["contractors", "admin"],
            "rationale": "Current rule retires the old shared setup account.",
            "confidence": 0.74,
        }
    ]


def test_parse_proposals_rejects_v1_or_unknown_relation_types():
    payload = json.dumps({
        "proposals": [
            {
                "type": "privilege_tier_override",
                "source_item_id": "M002",
                "target_item_id": "M001",
                "cited_evidence_span": "system wins",
                "scope_terms": ["policy"],
                "rationale": "v1 class must not enter v0",
                "confidence": 0.9,
            }
        ]
    })

    with pytest.raises(SemanticProposerError, match="unsupported relation type"):
        parse_proposals(payload)


def test_proposer_output_feeds_confirmer_on_dev_scratch():
    case = _scratch_case("dev_scratch_supersession")
    items = _items(case)

    def fake_provider(_prompt: str) -> str:
        return json.dumps({
            "proposals": [
                {
                    "type": "supersedes",
                    "source_item_id": "M002",
                    "target_item_id": "M001",
                    "cited_evidence_span": "shared setup admin access is retired",
                    "scope_terms": ["contractors", "admin"],
                    "rationale": "The current rule retires the shared admin account.",
                    "confidence": 0.74,
                }
            ]
        })

    proposed = propose_authority_changes(items, provider=fake_provider)
    confirmed = confirm_authority_changes(proposed["proposals"], items)

    assert proposed["engine"] == "injected"
    assert len(confirmed["findings"]) == 1
    assert confirmed["needs_human_judgment"] == []


def test_topic_mention_dev_scratch_can_return_empty_proposals():
    case = _scratch_case("dev_scratch_topic_mention_negative")
    items = _items(case)

    proposed = propose_authority_changes(items, provider=lambda _prompt: '{"proposals": []}')
    confirmed = confirm_authority_changes(proposed["proposals"], items)

    assert proposed["proposals"] == []
    assert confirmed["findings"] == []
    assert confirmed["needs_human_judgment"] == []
