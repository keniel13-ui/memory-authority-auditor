from __future__ import annotations

import json
from pathlib import Path

from agents.considered_set_gate import evaluate_considered_set_case


FIXTURE = Path(__file__).parent / "fixtures" / "path_a_v3_considered_set_2026_07_16.json"


def _cases() -> list[dict]:
    return json.loads(FIXTURE.read_text())["cases"]


def test_considered_set_frozen_cases_match_future_bar():
    for case in _cases():
        result = evaluate_considered_set_case(case)
        expected = case["expected"]["future_bar"]

        assert result["allowed_clean_compliance"] is expected["allowed_clean_compliance"], (case["id"], result)
        assert result["alarm_code"] == expected["alarm_code"], (case["id"], result)
        assert result["missing_surface_ids"] == expected.get("missing_surface_ids", []), (case["id"], result)


def test_fabricated_declared_negative_uses_process_truth_not_proposer_word():
    case = next(row for row in _cases() if row["id"] == "path_a_v3_cs3_fabricated_declared_negative")

    result = evaluate_considered_set_case(case)

    assert result["allowed_clean_compliance"] is False
    assert result["alarm_code"] == "fabricated_declared_negative"
    assert result["receipts"]["fabricated_surface_id"] == "surf_cs3_authority"
    assert result["receipts"]["records_not_loaded"] == ["old_cs3", "new_cs3"]


def test_complete_considered_set_does_not_clear_declared_negative_against_footprint():
    case = next(row for row in _cases() if row["id"] == "path_a_v3_cs_sol1_declare_everything_surface_nothing")

    result = evaluate_considered_set_case(case)

    assert result["allowed_clean_compliance"] is False
    assert result["alarm_code"] == "declared_negative_contradicted_by_footprint"
    assert result["missing_surface_ids"] == []
    assert result["receipts"]["contradicted_surface_id"] == "surf_cssol1_authority"


def test_proposer_authored_expected_set_is_unfalsifiable_even_when_surface_is_declared():
    case = next(row for row in _cases() if row["id"] == "path_a_v3_cs_sol3_circular_expected_set_out_of_scope_laundering")

    result = evaluate_considered_set_case(case)

    assert result["allowed_clean_compliance"] is False
    assert result["alarm_code"] == "considered_set_unfalsifiable"
    assert result["receipts"]["expected_set_independent_of_proposer"] is False
    assert result["receipts"]["self_scoped_omitted_surface_ids"] == ["surf_cssol3_authority"]


def test_untyped_considered_set_is_schema_failure_not_soft_parsed():
    case = next(row for row in _cases() if row["id"] == "path_a_v3_cs8_untyped_considered_set")

    result = evaluate_considered_set_case(case)

    assert result["allowed_clean_compliance"] is False
    assert result["alarm_code"] == "considered_set_schema_failure"
