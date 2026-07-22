from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from agents.resource_mapping import evaluate_resource_mapping_case, mapping_key


FIXTURE = Path(__file__).parent / "fixtures" / "path_a_v3_resource_mapping_receipt_v0_2026_07_21.json"


def _packet() -> dict:
    return json.loads(FIXTURE.read_text())


def _case(case_id: str) -> dict:
    return next(row for row in _packet()["cases"] if row["id"] == case_id)


def _actual_field(result: dict, field: str):
    if field in result:
        return result[field]
    return result["receipts"].get(field)


def test_resource_mapping_frozen_cases_match_expected_bars():
    packet = _packet()
    for case in packet["cases"]:
        result = evaluate_resource_mapping_case(case, packet)
        for field, expected in case["expected"].items():
            assert _actual_field(result, field) == expected, (case["id"], field, result)


def test_every_semantic_assertion_field_changes_mapping_key():
    packet = _packet()
    base = packet["shared_objects"]["base_assertion"]
    base_key = mapping_key(base)
    mutations = {
        "schema": "resource_mapping/v1",
        "mapping_kind": "successor_identity",
        "source_namespace": "gitlab",
        "source_resource_id": "github:456",
        "canonical_namespace": "tenant.other",
        "canonical_resource_id": "record:other",
        "authority_scope": "compliance.invoice_approval",
    }
    for field, value in mutations.items():
        changed = deepcopy(base)
        changed[field] = value
        assert mapping_key(changed) != base_key, field


def test_provenance_fields_do_not_change_mapping_key():
    packet = _packet()
    base = packet["shared_objects"]["base_assertion"]
    decorated = {
        **base,
        "receipt_id": "different-receipt",
        "issuer_id": "different-issuer",
        "grant_id": "different-grant",
        "issued_at": "2099-01-01T00:00:00Z",
        "effective_at": "2099-01-01T00:00:00Z",
        "expires_at": "2099-02-01T00:00:00Z",
        "evidence_receipt_ids": ["different-evidence"],
        "reason": "different prose",
    }
    assert mapping_key(decorated) == mapping_key(base)


def test_failure_never_leaks_canonical_identity_or_mapping_key():
    packet = _packet()
    for case in packet["cases"]:
        result = evaluate_resource_mapping_case(case, packet)
        if result["alarm_code"] is not None:
            assert result["resolution_state"] == "unresolved"
            assert result["mapping_key"] is None
            assert result["canonical_resource_id"] is None


def test_resolution_preserves_subject_and_resolution_clocks():
    packet = _packet()
    case = _case("path_a_v3_rm1_authorized_directional_resolution")
    result = evaluate_resource_mapping_case(case, packet)

    assert result["subject_time"] == "2026-07-20T10:00:00Z"
    assert result["resolution_time"] == "2026-07-20T12:00:00Z"
    assert result["subject_time"] != result["resolution_time"]


def test_unknown_mapping_receipt_reference_fails_loud():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    case["mapping_receipt_refs"] = ["missing-receipt"]

    result = evaluate_resource_mapping_case(case, packet)

    assert result["alarm_code"] == "mapping_receipt_integrity_failure"
    assert result["canonical_resource_id"] is None


def test_census_digest_is_checked_before_target_binding():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    case["census_ref"] = None
    case["census"] = deepcopy(packet["shared_objects"]["base_census"])
    case["census"]["resources"][1]["resource_id"] = "record:costume"

    result = evaluate_resource_mapping_case(case, packet)

    assert result["alarm_code"] == "mapping_census_integrity_failure"
    assert result["mapping_key"] is None


def test_mapping_receipt_cannot_outlive_its_authority_grant():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    grant = deepcopy(packet["shared_objects"]["base_grant"])
    grant["expires_at"] = "2026-07-30T00:00:00Z"
    from agents.anchor_contract import content_digest

    grant["grant_digest"] = content_digest({key: value for key, value in grant.items() if key != "grant_digest"})
    case["authority_grant_refs"] = []
    case["authority_grants"] = [grant]

    result = evaluate_resource_mapping_case(case, packet)

    assert result["alarm_code"] == "mapping_authority_failure"
    assert result["canonical_resource_id"] is None
