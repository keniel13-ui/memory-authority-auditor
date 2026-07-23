from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from agents.anchor_contract import content_digest
from agents.authority_runtime import action_key, evaluate_authority_case, render_decision_markdown


ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "authority_runtime_v0_gwb_dns_replay_2026_07_21.json"
CLI = ROOT / "authorityctl.py"


def _packet() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _case(packet: dict, case_id: str) -> dict:
    return deepcopy(next(case for case in packet["cases"] if case["id"] == case_id))


def _redigest(value: dict, field: str) -> None:
    value[field] = content_digest({key: child for key, child in value.items() if key != field})


def test_frozen_runtime_cases_match_every_expected_bar():
    packet = _packet()
    for case in packet["cases"]:
        result = evaluate_authority_case(case, packet)
        for field, expected in case["expected"].items():
            assert result[field] == expected, (case["id"], field, result)
        assert result["decision_digest"] == content_digest(
            {key: value for key, value in result.items() if key != "decision_digest"}
        )


def test_fixture_has_unique_cases_and_ar2_uses_only_causal_evidence():
    packet = _packet()
    case_ids = [case["id"] for case in packet["cases"]]
    assert len(case_ids) == len(set(case_ids)) == 11
    ar2 = _case(packet, "authority_runtime_ar2_transition_still_required")
    assert ar2["startup_claim_ref"] == "precut_startup_claim"
    assert ar2["mapping_case_ref"] == "precut_gwb_mapping"
    audit_time = packet["shared_objects"]["precut_startup_claim"]["audit_time"]
    mapping_request = packet["resource_mapping_packet"]["shared_objects"]["precut_gwb_mapping_request"]
    mapping_census = packet["resource_mapping_packet"]["shared_objects"]["precut_gwb_mapping_census"]
    state = packet["shared_objects"]["precut_squarespace_state"]
    manifest = packet["shared_objects"]["state_manifest_precut"]
    assert mapping_request["resolution_time"] <= audit_time
    assert mapping_census["observed_at"] <= audit_time
    assert state["observed_at"] <= audit_time
    assert manifest["coverage_end"] == manifest["observed_at"] == audit_time
    assert "<path>" not in json.dumps(packet["shared_objects"])


def test_real_replay_excerpts_exist_in_live_workspace_sources():
    packet = _packet()
    workspace = Path(os.environ.get("AUTHORITY_RUNTIME_WORKSPACE_ROOT", ROOT.parent))
    board = workspace / "CURRENT_STATE_BOARD.md"
    brain = workspace / "BRAIN_CURRENT.md"
    if not board.is_file() or not brain.is_file():
        pytest.skip(
            "live workspace provenance files are external to an isolated repository clone; "
            "set AUTHORITY_RUNTIME_WORKSPACE_ROOT to verify them"
        )
    action_excerpt = packet["shared_objects"]["base_action_receipt"]["source_excerpt"]
    completion_excerpt = packet["shared_objects"]["vercel_completion_state"]["source_excerpt"]
    assert action_excerpt in board.read_text(encoding="utf-8")
    assert completion_excerpt in brain.read_text(encoding="utf-8")


def test_action_key_changes_for_every_semantic_field():
    result = evaluate_authority_case(_packet()["cases"][0], _packet())
    base = result["canonical_action"]
    mutations = {
        "schema": "authority_action/v1",
        "authority_namespace": "client.other/dns.production",
        "kind": "different_transition",
        "resource_id": "domain:other.example",
        "operation": "nameserver_cutover",
        "from_state": "provider:other",
        "to_state": "provider:other-target",
    }
    for field, changed_value in mutations.items():
        changed = deepcopy(base)
        changed[field] = changed_value
        assert action_key(changed) != action_key(base), field


def test_action_key_ignores_provenance_decoration():
    result = evaluate_authority_case(_packet()["cases"][0], _packet())
    base = result["canonical_action"]
    decorated = {
        **base,
        "receipt_id": "different-receipt",
        "source_locator": "different-source",
        "issued_at": "2099-01-01T00:00:00Z",
        "comment": "different prose",
    }
    assert action_key(decorated) == action_key(base)


def test_case_id_does_not_change_runtime_decision():
    packet = _packet()
    original = _case(packet, "authority_runtime_ar1_real_gwb_stale_cutover")
    renamed = deepcopy(original)
    renamed["id"] = "outsider_supplied_name_with_no_runtime_branch"
    first = evaluate_authority_case(original, packet)
    second = evaluate_authority_case(renamed, packet)
    for field in (
        "decision",
        "decision_code",
        "action_key",
        "surface_key",
        "mapping_key",
        "canonical_resource_id",
        "controlling_state_receipt_ids",
        "mutation_authorized",
        "exit_code",
    ):
        assert second[field] == first[field]


def test_equal_authority_conflict_is_input_order_invariant():
    packet = _packet()
    case = _case(packet, "authority_runtime_ar4_equal_authority_conflict")
    forward = evaluate_authority_case(case, packet)
    case["state_receipt_refs"].reverse()
    reverse = evaluate_authority_case(case, packet)
    assert forward["decision"] == reverse["decision"] == "CONFLICT"
    assert forward["decision_code"] == reverse["decision_code"] == "equally_authoritative_state_conflict"
    assert forward["controlling_state_receipt_ids"] == reverse["controlling_state_receipt_ids"]


def test_unresolved_mapping_never_leaks_canonical_keys():
    packet = _packet()
    case = _case(packet, "authority_runtime_ar5_resource_alias_unresolved")
    result = evaluate_authority_case(case, packet)
    assert result["decision"] == "UNKNOWN"
    assert result["decision_code"] == "resource_identity_unresolved"
    assert result["canonical_resource_id"] is None
    assert result["mapping_key"] is None
    assert result["action_key"] is None
    assert result["surface_key"] is None


def test_action_tamper_fails_before_mapping_and_key_derivation():
    packet = _packet()
    case = _case(packet, "authority_runtime_ar1_real_gwb_stale_cutover")
    case["action_receipt_overrides"] = {"to_state": "provider:costume"}
    result = evaluate_authority_case(case, packet)
    assert result["decision"] == "UNKNOWN"
    assert result["decision_code"] == "action_receipt_integrity_failure"
    assert result["mapping_key"] is None
    assert result["action_key"] is None


def test_recomputed_source_class_costume_is_rejected_by_registry():
    packet = _packet()
    case = _case(packet, "authority_runtime_ar1_real_gwb_stale_cutover")
    state = deepcopy(packet["shared_objects"]["vercel_completion_state"])
    state["source_class"] = "historical_summary"
    _redigest(state, "receipt_digest")
    case.pop("state_receipt_refs")
    case["state_receipts"] = [state]
    result = evaluate_authority_case(case, packet)
    assert result["decision"] == "UNKNOWN"
    assert result["decision_code"] == "current_state_missing"
    assert result["controlling_state_receipt_ids"] == []
    assert result["ignored_state_receipt_ids"] == [state["receipt_id"]]
    assert any("source_class_unregistered_or_mismatched" in reason for reason in result["unknowns"])


def test_future_state_receipt_cannot_control_present_audit():
    packet = _packet()
    case = _case(packet, "authority_runtime_ar1_real_gwb_stale_cutover")
    state = deepcopy(packet["shared_objects"]["vercel_completion_state"])
    state["recorded_at"] = "2026-07-22T00:00:00Z"
    state["observed_at"] = "2026-07-22T00:00:00Z"
    _redigest(state, "receipt_digest")
    case.pop("state_receipt_refs")
    case["state_receipts"] = [state]
    result = evaluate_authority_case(case, packet)
    assert result["decision"] == "UNKNOWN"
    assert result["decision_code"] == "state_evidence_manifest_failure"
    assert any("outside manifest coverage" in reason for reason in result["unknowns"])


def test_target_state_without_exact_completion_binding_remains_unknown():
    packet = _packet()
    case = _case(packet, "authority_runtime_ar1_real_gwb_stale_cutover")
    state = deepcopy(packet["shared_objects"]["vercel_completion_state"])
    state["completion_action_key"] = None
    _redigest(state, "receipt_digest")
    case.pop("state_receipt_refs")
    case["state_receipts"] = [state]
    result = evaluate_authority_case(case, packet)
    assert result["decision"] == "UNKNOWN"
    assert result["decision_code"] == "target_state_unreceipted"
    assert result["mutation_authorized"] is False


def test_manifest_bound_later_receipt_cannot_be_silently_omitted():
    packet = _packet()
    case = _case(packet, "authority_runtime_ar11_later_completion_silently_omitted")
    result = evaluate_authority_case(case, packet)
    assert result["decision"] == "UNKNOWN"
    assert result["decision_code"] == "state_evidence_omission"
    assert result["controlling_state_receipt_ids"] == []
    assert result["mutation_authorized"] is False
    assert any("state:gwb_dns_vercel:20260720T2047" in reason for reason in result["unknowns"])


def test_unlisted_state_receipt_is_injection_not_extra_authority():
    packet = _packet()
    case = _case(packet, "authority_runtime_ar1_real_gwb_stale_cutover")
    case["state_receipt_refs"].append("precut_squarespace_state")
    result = evaluate_authority_case(case, packet)
    assert result["decision"] == "UNKNOWN"
    assert result["decision_code"] == "state_evidence_injection"
    assert any("state:gwb_dns_squarespace:20260710T2253" in reason for reason in result["unknowns"])


def test_recomputed_manifest_from_untrusted_observer_has_no_authority():
    packet = _packet()
    case = _case(packet, "authority_runtime_ar1_real_gwb_stale_cutover")
    manifest = deepcopy(packet["shared_objects"]["state_manifest_vercel"])
    manifest["observer_id"] = "submitted.agent.costume"
    _redigest(manifest, "manifest_digest")
    case.pop("state_evidence_manifest_ref")
    case["state_evidence_manifest"] = manifest
    result = evaluate_authority_case(case, packet)
    assert result["decision"] == "UNKNOWN"
    assert result["decision_code"] == "state_evidence_manifest_failure"
    assert any("configured trust root" in reason for reason in result["unknowns"])


def test_markdown_and_json_name_same_decision_keys_and_sources():
    packet = _packet()
    result = evaluate_authority_case(packet["cases"][0], packet)
    markdown = render_decision_markdown(result)
    for value in (
        result["decision"],
        result["decision_code"],
        result["action_key"],
        result["surface_key"],
        result["mapping_key"],
        "CURRENT_STATE_BOARD.md",
        "BRAIN_CURRENT.md",
        result["decision_digest"],
    ):
        assert value in markdown
    assert "does not execute DNS changes" in markdown


@pytest.mark.parametrize(
    ("case_id", "expected_exit", "expected_decision"),
    [
        ("authority_runtime_ar2_transition_still_required", 0, "ALLOW"),
        ("authority_runtime_ar1_real_gwb_stale_cutover", 3, "BLOCK_STALE_ACTION"),
        ("authority_runtime_ar4_equal_authority_conflict", 4, "CONFLICT"),
        ("authority_runtime_ar3_current_state_missing", 5, "UNKNOWN"),
    ],
)
def test_cli_exit_codes_and_receipt_files(tmp_path: Path, case_id: str, expected_exit: int, expected_decision: str):
    json_out = tmp_path / f"{case_id}.json"
    markdown_out = tmp_path / f"{case_id}.md"
    completed = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "audit",
            str(FIXTURE),
            "--case",
            case_id,
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
            "--format",
            "json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == expected_exit, completed.stderr
    stdout_receipt = json.loads(completed.stdout)
    file_receipt = json.loads(json_out.read_text(encoding="utf-8"))
    assert stdout_receipt == file_receipt
    assert file_receipt["decision"] == expected_decision
    assert expected_decision in markdown_out.read_text(encoding="utf-8")


def test_cli_refuses_unknown_case_without_writing_receipts(tmp_path: Path):
    json_out = tmp_path / "should-not-exist.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "audit",
            str(FIXTURE),
            "--case",
            "missing-case",
            "--json-out",
            str(json_out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 2
    assert "found 0" in completed.stderr
    assert not json_out.exists()
