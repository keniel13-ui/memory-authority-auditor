from __future__ import annotations

import json
from pathlib import Path

from agents.memory_extractor import extract_memories
from agents.semantic_confirmer import confirm_authority_change, confirm_authority_changes


FIXTURE = Path(__file__).parent / "fixtures" / "path_a_authority_change_v0_2026_07_01.json"


def _cases() -> list[dict]:
    return json.loads(FIXTURE.read_text())["cases"]


def _items(case: dict) -> list[dict]:
    return [item.to_dict() for item in extract_memories(case["text"])]


def test_frozen_path_a_positive_relations_confirm_against_local_evidence():
    positives = [case for case in _cases() if case["expected_relations"]]

    for case in positives:
        items = _items(case)
        for proposal in case["expected_relations"]:
            result = confirm_authority_change(proposal, items)
            assert result["confirmed"], (case["id"], result["reasons"])
            assert result["finding"]["relation_type"] == proposal["type"]


def test_frozen_path_a_topic_mentions_do_not_create_findings():
    negatives = [case for case in _cases() if not case["expected_relations"]]

    for case in negatives:
        result = confirm_authority_changes([], _items(case))
        assert result["findings"] == []
        assert result["needs_human_judgment"] == []


def test_hallucinated_or_uncited_proposals_route_to_human_judgment():
    case = next(case for case in _cases() if case["id"] == "path_a_supersession_password_rotation_v0")
    items = _items(case)

    bad_source = {
        "type": "supersedes",
        "source_item_id": "M999",
        "target_item_id": "M001",
        "required_evidence_terms": ["migration exception is retired"],
        "scope_terms": ["staging"],
    }
    bad_evidence = {
        "type": "supersedes",
        "source_item_id": "M002",
        "target_item_id": "M001",
        "required_evidence_terms": ["this phrase does not exist"],
        "scope_terms": ["staging"],
    }
    bad_scope = {
        "type": "supersedes",
        "source_item_id": "M002",
        "target_item_id": "M001",
        "required_evidence_terms": ["migration exception is retired"],
        "scope_terms": ["unrelated payroll scope"],
    }

    result = confirm_authority_changes([bad_source, bad_evidence, bad_scope], items)

    assert result["findings"] == []
    assert len(result["needs_human_judgment"]) == 3
    reasons = "\n".join(", ".join(entry["reasons"]) for entry in result["needs_human_judgment"])
    assert "source item does not exist" in reasons
    assert "required evidence terms not found" in reasons
    assert "no deterministic scope overlap" in reasons
