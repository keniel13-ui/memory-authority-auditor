from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from agents.resource_mapping import evaluate_resource_mapping_case, mapping_key
from agents.anchor_contract import content_digest, evaluate_anchor_contract_case


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
    grant["grant_digest"] = content_digest({key: value for key, value in grant.items() if key != "grant_digest"})
    case["authority_grant_refs"] = []
    case["authority_grants"] = [grant]

    result = evaluate_resource_mapping_case(case, packet)

    assert result["alarm_code"] == "mapping_authority_failure"
    assert result["canonical_resource_id"] is None


def test_assertion_extra_or_untyped_fields_fail_before_resolution():
    packet = _packet()
    for mutation in ({"confidence": 1}, {"canonical_resource_id": 123}):
        case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
        receipt = deepcopy(packet["shared_objects"]["base_mapping_receipt"])
        receipt["assertion"].update(mutation)
        receipt["assertion_digest"] = content_digest(receipt["assertion"])
        receipt["receipt_digest"] = content_digest(
            {key: value for key, value in receipt.items() if key != "receipt_digest"}
        )
        case["mapping_receipt_refs"] = []
        case["mapping_receipts"] = [receipt]

        result = evaluate_resource_mapping_case(case, packet)

        assert result["alarm_code"] == "mapping_receipt_integrity_failure"
        assert result["canonical_resource_id"] is None


def test_costume_trust_root_fails_even_with_recomputed_grant_digest():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    grant = deepcopy(packet["shared_objects"]["base_grant"])
    grant["grantor_id"] = "tenant.demo.identity_costume"
    grant["grant_digest"] = content_digest({key: value for key, value in grant.items() if key != "grant_digest"})
    case["authority_grant_refs"] = []
    case["authority_grants"] = [grant]

    result = evaluate_resource_mapping_case(case, packet)

    assert result["alarm_code"] == "mapping_authority_failure"
    assert result["canonical_resource_id"] is None


def test_unrelated_malformed_revocation_cannot_poison_valid_mapping():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    case["revocation_receipts"] = [{"mapping_receipt_id": "some-other-receipt"}]

    result = evaluate_resource_mapping_case(case, packet)

    assert result["alarm_code"] is None
    assert result["canonical_resource_id"] == "record:new-ac1"


def test_two_authorized_receipts_for_same_semantic_target_are_support_not_conflict():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    second = deepcopy(packet["shared_objects"]["base_mapping_receipt"])
    second["receipt_id"] = "mapping-rm-second-support"
    second["receipt_digest"] = content_digest(
        {key: value for key, value in second.items() if key != "receipt_digest"}
    )
    case["mapping_receipt_refs"] = []
    case["mapping_receipts"] = [packet["shared_objects"]["base_mapping_receipt"], second]

    result = evaluate_resource_mapping_case(case, packet)

    assert result["alarm_code"] is None
    assert result["receipts"]["active_mapping_count"] == 2
    assert result["supporting_mapping_receipt_ids"] == ["mapping-rm-base", "mapping-rm-second-support"]


def test_resolved_mapping_receipt_closes_anchor_ac2_without_shared_surface_id():
    mapping_packet = _packet()
    anchor_fixture = Path(__file__).parent / "fixtures" / "path_a_v3_anchor_contract_v0_2026_07_21.json"
    anchor_packet = json.loads(anchor_fixture.read_text())
    mapping_case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    mapping_case["census_ref"] = None
    mapping_case["census"] = deepcopy(anchor_packet["shared_receipts"]["base_census"])
    mapping_result = evaluate_resource_mapping_case(mapping_case, mapping_packet)
    assert mapping_result["alarm_code"] is None

    anchor_case = deepcopy(
        next(case for case in anchor_packet["cases"] if case["id"] == "path_a_v3_ac2_unreceipted_resource_alias")
    )
    anchor_case["alias_claim"]["mapping_receipt"] = mapping_result
    anchor_result = evaluate_anchor_contract_case(anchor_case, anchor_packet)
    ac1 = next(case for case in anchor_packet["cases"] if case["id"] == "path_a_v3_ac1_two_routes_one_semantic_surface")

    assert anchor_result["alarm_code"] is None
    assert anchor_result["surface_keys"] == [ac1["expected"]["surface_key"]]
    assert anchor_result["derived_surfaces"][0]["surface_payload"]["source_resource_id"] == "record:new-ac1"


def test_anchor_rejects_truthy_but_incoherent_mapping_json():
    anchor_fixture = Path(__file__).parent / "fixtures" / "path_a_v3_anchor_contract_v0_2026_07_21.json"
    anchor_packet = json.loads(anchor_fixture.read_text())
    anchor_case = deepcopy(
        next(case for case in anchor_packet["cases"] if case["id"] == "path_a_v3_ac2_unreceipted_resource_alias")
    )
    anchor_case["alias_claim"]["mapping_receipt"] = {"resolution_state": "resolved"}

    result = evaluate_anchor_contract_case(anchor_case, anchor_packet)

    assert result["alarm_code"] == "resource_identity_unresolved"
    assert result["derived_surfaces"] == []


def test_anchor_bridge_rechecks_canonical_target_membership():
    mapping_packet = _packet()
    anchor_fixture = Path(__file__).parent / "fixtures" / "path_a_v3_anchor_contract_v0_2026_07_21.json"
    anchor_packet = json.loads(anchor_fixture.read_text())
    mapping_case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    mapping_case["census_ref"] = None
    mapping_case["census"] = deepcopy(anchor_packet["shared_receipts"]["base_census"])
    mapping_result = evaluate_resource_mapping_case(mapping_case, mapping_packet)
    assert mapping_result["alarm_code"] is None

    mapping_result["canonical_resource_id"] = "record:absent"
    forged_assertion = {
        "schema": "resource_mapping/v0",
        "mapping_kind": "equivalent_identity",
        "source_namespace": mapping_result["source_namespace"],
        "source_resource_id": mapping_result["source_resource_id"],
        "canonical_namespace": mapping_result["canonical_namespace"],
        "canonical_resource_id": mapping_result["canonical_resource_id"],
        "authority_scope": mapping_result["authority_scope"],
    }
    mapping_result["mapping_key"] = "mapping:v0:" + content_digest(forged_assertion)
    anchor_case = deepcopy(
        next(case for case in anchor_packet["cases"] if case["id"] == "path_a_v3_ac2_unreceipted_resource_alias")
    )
    anchor_case["alias_claim"]["canonical_resource_id"] = "record:absent"
    anchor_case["alias_claim"]["mapping_receipt"] = mapping_result

    result = evaluate_anchor_contract_case(anchor_case, anchor_packet)

    assert result["alarm_code"] == "resource_identity_unresolved"
    assert result["derived_surfaces"] == []


def test_expired_historical_receipt_cannot_poison_valid_active_mapping():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    case["mapping_receipt_refs"] = ["expired_mapping_receipt", "base_mapping_receipt"]

    result = evaluate_resource_mapping_case(case, packet)

    assert result["alarm_code"] is None
    assert result["canonical_resource_id"] == "record:new-ac1"
    assert result["receipts"]["candidate_receipt_count"] == 2
    assert result["receipts"]["active_mapping_count"] == 1
    assert result["rejected_mapping_receipts"] == [
        {
            "mapping_receipt_id": "mapping-rm-expired",
            "alarm_code": "mapping_expired",
            "reason": "mapping expired before subject time",
        }
    ]


def test_revoked_historical_receipt_cannot_poison_valid_reissue():
    packet = _packet()
    case = deepcopy(_case("path_a_v3_rm1_authorized_directional_resolution"))
    reissue = deepcopy(packet["shared_objects"]["base_mapping_receipt"])
    reissue["receipt_id"] = "mapping-rm-reissue"
    reissue["issued_at"] = "2026-07-20T09:30:00Z"
    reissue["effective_at"] = "2026-07-20T09:30:00Z"
    reissue["receipt_digest"] = content_digest(
        {key: value for key, value in reissue.items() if key != "receipt_digest"}
    )
    case["mapping_receipt_refs"] = []
    case["mapping_receipts"] = [packet["shared_objects"]["base_mapping_receipt"], reissue]
    case["revocation_receipt_refs"] = ["base_revocation"]

    result = evaluate_resource_mapping_case(case, packet)

    assert result["alarm_code"] is None
    assert result["mapping_receipt_id"] == "mapping-rm-reissue"
    assert result["receipts"]["active_mapping_count"] == 1
    assert result["rejected_mapping_receipts"][0]["alarm_code"] == "mapping_revoked"
