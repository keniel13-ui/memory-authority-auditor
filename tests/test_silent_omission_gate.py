from __future__ import annotations

import json
from pathlib import Path

from agents.silent_omission_gate import evaluate_silent_omission_case


FIXTURE = Path(__file__).parent / "fixtures" / "path_a_v3_silent_omission_2026_07_15.json"


def _cases() -> list[dict]:
    return json.loads(FIXTURE.read_text())["cases"]


def test_silent_omission_frozen_cases_match_future_bar():
    for case in _cases():
        result = evaluate_silent_omission_case(case)
        expected = case["expected"]["future_bar"]

        assert result["allowed_clean_compliance"] is expected["allowed_clean_compliance"], (case["id"], result)
        assert result["alarm_code"] == expected["alarm_code"], (case["id"], result)
        assert result["undeclared_surface_ids"] == expected.get("undeclared_surface_ids", []), (case["id"], result)
        if expected.get("footprint_receipt_id") is not None:
            assert result["receipts"].get("footprint_receipt_id") == expected["footprint_receipt_id"], (case["id"], result)


def test_same_pair_metadata_note_does_not_discharge_authority_surface():
    case = next(row for row in _cases() if row["id"] == "path_a_v3_so6_same_pair_downgrade_costume")

    result = evaluate_silent_omission_case(case)

    assert result["allowed_clean_compliance"] is False
    assert result["alarm_code"] == "undeclared_surface"
    assert result["undeclared_surface_ids"] == ["surf_so6_supersession"]


def test_expected_observer_suppression_is_louder_than_no_footprint_available():
    case = next(row for row in _cases() if row["id"] == "path_a_v3_so8_expected_observer_receipt_missing")

    result = evaluate_silent_omission_case(case)

    assert result["allowed_clean_compliance"] is False
    assert result["alarm_code"] == "footprint_integrity_failure"
    assert result["undeclared_surface_ids"] == []
