from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from agents.anchor_contract import canonical_json, content_digest, evaluate_anchor_contract_case, surface_key


FIXTURE = Path(__file__).parent / "fixtures" / "path_a_v3_anchor_contract_v0_2026_07_21.json"


def _packet() -> dict:
    return json.loads(FIXTURE.read_text())


def _case(case_id: str) -> dict:
    return next(row for row in _packet()["cases"] if row["id"] == case_id)


def _actual_field(result: dict, field: str):
    if field == "surface_key":
        return result["surface_keys"][0] if result["surface_keys"] else None
    if field == "surface_payload":
        return result["derived_surfaces"][0]["surface_payload"] if result["derived_surfaces"] else None
    if field == "canonical_json":
        return canonical_json(result["derived_surfaces"][0]["surface_payload"])
    if field == "surface_keys":
        return result["surface_keys"]
    if field in result:
        return result[field]
    return result["receipts"].get(field)


def test_anchor_contract_frozen_cases_match_expected_bars():
    packet = _packet()
    for case in packet["cases"]:
        result = evaluate_anchor_contract_case(case, packet)
        for field, expected in case["expected"].items():
            assert _actual_field(result, field) == expected, (case["id"], field, result)


def test_every_included_semantic_field_changes_the_surface_key():
    base = _case("path_a_v3_ac1_two_routes_one_semantic_surface")["expected"]["surface_payload"]
    base_key = surface_key(base)
    mutations = {
        "schema": "authority_surface/v1",
        "authority_namespace": "tenant.other/compliance.export_approval",
        "kind": "metadata_note",
        "source_resource_id": "record:other-new",
        "target_resource_id": "record:other-old",
        "relation_type": "narrows_scope",
    }
    for field, value in mutations.items():
        changed = deepcopy(base)
        changed[field] = value
        assert surface_key(changed) != base_key, field


def test_provenance_fields_do_not_change_semantic_surface_key():
    base = _case("path_a_v3_ac1_two_routes_one_semantic_surface")["expected"]["surface_payload"]
    decorated = {
        **base,
        "event_id": "another-event",
        "event_source": "https://another.example",
        "event_time": "2099-01-01T00:00:00Z",
        "observed_time": "2099-01-02T00:00:00Z",
        "observer_id": "another-observer",
        "receipt_id": "another-receipt",
        "policy_id": "another-policy",
        "policy_version": "99.0.0",
        "reason": "different prose",
    }
    assert surface_key(decorated) == surface_key(base)


def test_swapping_direction_changes_surface_key():
    base = _case("path_a_v3_ac1_two_routes_one_semantic_surface")["expected"]["surface_payload"]
    swapped = deepcopy(base)
    swapped["source_resource_id"], swapped["target_resource_id"] = (
        swapped["target_resource_id"],
        swapped["source_resource_id"],
    )
    assert surface_key(swapped) != surface_key(base)


def test_canonical_profile_rejects_floating_point_values():
    with pytest.raises(ValueError):
        canonical_json({"confidence": 0.9})


def test_event_before_coverage_window_fails_loud():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_ac6_late_delivery_preserves_clocks"))
    case["event_overrides"]["event_time"] = "2026-05-01T00:00:00Z"
    case["event_overrides"]["observed_time"] = "2026-07-20T12:00:00Z"

    result = evaluate_anchor_contract_case(case, packet)

    assert result["alarm_code"] == "event_outside_coverage"
    assert result["derived_surfaces"] == []


def test_observed_time_before_event_time_fails_loud():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_ac6_late_delivery_preserves_clocks"))
    case["event_overrides"]["observed_time"] = "2026-07-20T09:59:59Z"

    result = evaluate_anchor_contract_case(case, packet)

    assert result["alarm_code"] == "event_time_integrity_failure"
    assert result["derived_surfaces"] == []


def test_duplicate_census_resource_identity_fails_before_target_selection():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_ac10_tampered_census_digest"))
    census = case["census_receipt"]
    census["resources"] = [deepcopy(census["resources"][0]), deepcopy(census["resources"][0])]
    census["census_digest"] = content_digest(
        {"authority_namespace": census["authority_namespace"], "resources": census["resources"]}
    )

    result = evaluate_anchor_contract_case(case, packet)

    assert result["alarm_code"] == "census_integrity_failure"
    assert result["receipts"]["target_selection_attempted"] is False
