from __future__ import annotations

import json
from pathlib import Path

from agents.relation_store_gate import evaluate_store_request


FIXTURE_DIR = Path(__file__).parent / "fixtures"
STORE_AUTHORITY_FIXTURE = FIXTURE_DIR / "path_a_v3_store_authority_2026_07_13.json"
PROVENANCE_FIXTURE = FIXTURE_DIR / "path_a_v3_provenance_disjointness_2026_07_13.json"
AUTHORITY_ROOTS_FIXTURE = FIXTURE_DIR / "path_a_v3_authority_roots_2026_07_14.json"


def _cases(path: Path) -> list[dict]:
    return json.loads(path.read_text())["cases"]


def test_store_authority_frozen_cases_hold_separately():
    for case in _cases(STORE_AUTHORITY_FIXTURE):
        result = evaluate_store_request(case)
        expected = case["expected"]

        assert result["allowed"] is expected["allowed"], (case["id"], result)
        assert result["resulting_tier"] == expected["resulting_tier"], (case["id"], result)
        assert result["alarm_code"] == expected["alarm_code"], (case["id"], result)


def test_provenance_disjointness_frozen_cases_hold_separately():
    for case in _cases(PROVENANCE_FIXTURE):
        result = evaluate_store_request(case)
        expected = case["expected"]

        if "allowed_by_declared_path_gate" in expected:
            assert result["allowed"] is expected["allowed_by_declared_path_gate"], (case["id"], result)
            assert result["ceiling_note"] == expected["required_receipt"], (case["id"], result)
            assert result["actual_independence"] is expected["actual_independence"], (case["id"], result)
        else:
            assert result["allowed"] is expected["allowed"], (case["id"], result)
        assert result["alarm_code"] == expected["alarm_code"], (case["id"], result)
        assert result["receipts"]["declared_shared_nodes"] == expected["declared_shared_nodes"], (case["id"], result)


def test_authority_root_and_grant_lifecycle_frozen_cases_hold_separately():
    for case in _cases(AUTHORITY_ROOTS_FIXTURE):
        result = evaluate_store_request(case)
        expected = case["expected"]

        assert result["allowed"] is expected["allowed"], (case["id"], result)
        assert result["alarm_code"] == expected["alarm_code"], (case["id"], result)
        assert result["receipts"].get("root_receipt_id") == expected["root_receipt_id"], (case["id"], result)

