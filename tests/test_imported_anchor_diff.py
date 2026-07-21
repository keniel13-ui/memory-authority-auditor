from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from agents.imported_anchor_diff import evaluate_imported_anchor_case


FIXTURE = Path(__file__).parent / "fixtures" / "path_a_v3_imported_anchor_diff_2026_07_21.json"


def _cases() -> list[dict]:
    return json.loads(FIXTURE.read_text())["cases"]


def test_imported_anchor_frozen_cases_match_pass_bars():
    for case in _cases():
        result = evaluate_imported_anchor_case(case)
        expected = case["expected"]

        assert result["alarm_code"] == expected["alarm_code"], (case["id"], result)
        for count_name in (
            "derived_surface_count",
            "semantic_aligned_count",
            "fixture_only_count",
            "imported_only_count",
            "unresolved_event_count",
        ):
            assert result["receipts"][count_name] == expected[count_name], (case["id"], count_name, result)

        if "missing_from_considered_count" in expected:
            assert result["receipts"]["missing_from_considered_count"] == expected["missing_from_considered_count"]
        if "pre_ledger_birth_event_ids" in expected:
            assert result["pre_ledger_birth_event_ids"] == expected["pre_ledger_birth_event_ids"]
        if "unresolved_reasons" in expected:
            assert [row["reason"] for row in result["unresolved_events"]] == expected["unresolved_reasons"]
        if "silent_omission_alarm_code" in expected:
            assert (
                result["shipped_gate_receipts"]["silent_omission"]["alarm_code"]
                == expected["silent_omission_alarm_code"]
            )
        if "considered_set_alarm_code" in expected:
            assert (
                result["shipped_gate_receipts"]["considered_set"]["alarm_code"]
                == expected["considered_set_alarm_code"]
            )
        if "considered_set_identity_break" in expected:
            assert result["receipts"]["considered_set_identity_break"] is expected["considered_set_identity_break"]


def test_imported_surface_ids_are_not_copied_from_fixture_ids():
    case = next(row for row in _cases() if row["id"] == "path_a_v3_ia3_semantic_match_surface_id_break")

    result = evaluate_imported_anchor_case(case)

    assert result["derived_surfaces"][0]["surface_id"] == "imported::anchor_processor_cs1::foreign_ev_cs1_write"
    assert result["derived_surfaces"][0]["surface_id"] != case["fixture_expected_set"][0]["surface_id"]
    assert result["receipts"]["semantic_aligned_count"] == 1
    assert result["receipts"]["considered_set_identity_break"] is True


def test_missing_scope_preserves_event_without_fabricating_relation():
    case = next(row for row in _cases() if row["id"] == "path_a_v3_ia4_webhook_missing_scope")

    result = evaluate_imported_anchor_case(case)

    assert result["derived_surfaces"] == []
    assert result["unresolved_events"] == [{"event_id": "foreign_ev_ia4_activity", "reason": "missing_scope"}]


def test_foreign_label_without_external_producer_fails_provenance():
    case = deepcopy(next(row for row in _cases() if row["id"] == "path_a_v3_ia1_foreign_receipt_catches_so1_silence"))
    case["imported_anchor"]["producer_id"] = "proposer_p"

    result = evaluate_imported_anchor_case(case)

    assert result["alarm_code"] == "imported_anchor_provenance_failure"
    assert result["derived_surfaces"] == []


def test_ambiguous_census_target_stays_unresolved():
    case = deepcopy(next(row for row in _cases() if row["id"] == "path_a_v3_ia1_foreign_receipt_catches_so1_silence"))
    case["records"].append(
        {"record_id": "other_old_so1", "owner_id": "agent_c", "scope": "compliance.export_approval", "status": "live"}
    )

    result = evaluate_imported_anchor_case(case)

    assert result["alarm_code"] == "imported_anchor_unresolved"
    assert result["derived_surfaces"] == []
    assert result["unresolved_events"][0]["reason"] == "ambiguous_live_same_scope_target"
