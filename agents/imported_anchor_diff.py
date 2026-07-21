from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any

from agents.considered_set_gate import evaluate_considered_set_case
from agents.silent_omission_gate import evaluate_silent_omission_case


DERIVATION_POLICY = "same_scope_live_record_requires_authority_change_candidate"
SEMANTIC_FIELDS = (
    "kind",
    "source_record_id",
    "target_record_id",
    "relation_type",
    "record_id",
)


def _actor(case: dict, actor_id: str | None) -> dict | None:
    if not actor_id:
        return None
    for actor in case.get("actors", []):
        if actor.get("actor_id") == actor_id:
            return actor
    return None


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _semantic_key(surface: dict) -> tuple[Any, ...]:
    return tuple(surface.get(field) for field in SEMANTIC_FIELDS)


def _semantic_receipt(surface: dict) -> dict[str, Any]:
    return {field: surface.get(field) for field in SEMANTIC_FIELDS if surface.get(field) is not None}


def _index_by_semantics(surfaces: list[dict]) -> dict[tuple[Any, ...], dict]:
    return {_semantic_key(surface): surface for surface in surfaces}


def _valid_foreign_provenance(case: dict, anchor: dict) -> bool:
    producer_id = anchor.get("producer_id")
    producer = _actor(case, producer_id)
    return bool(
        producer_id
        and producer
        and producer.get("outside_proposer_process")
        and anchor.get("outside_proposer_process")
        and anchor.get("independent_of_proposer")
    )


def _derive_event_surface(
    *,
    event: dict,
    records: list[dict],
    anchor_id: str,
) -> tuple[dict | None, str | None]:
    if event.get("kind") != "record_write":
        return None, "unsupported_event_kind"

    record_id = event.get("record_id")
    if not isinstance(record_id, str) or not record_id:
        return None, "missing_record_id"

    scope = event.get("scope")
    if not isinstance(scope, str) or not scope:
        return None, "missing_scope"

    live_same_scope = [
        record
        for record in records
        if record.get("status") == "live"
        and record.get("scope") == scope
        and record.get("record_id") != record_id
    ]
    if not live_same_scope:
        return None, "no_live_same_scope_target"
    if len(live_same_scope) > 1:
        return None, "ambiguous_live_same_scope_target"

    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        return None, "missing_event_id"

    return (
        {
            "surface_id": f"imported::{anchor_id}::{event_id}",
            "kind": "authority_change_candidate",
            "source_record_id": record_id,
            "target_record_id": live_same_scope[0]["record_id"],
            "relation_type": "supersedes",
            "imported_anchor_provenance": {
                "anchor_id": anchor_id,
                "event_id": event_id,
                "derivation_policy": DERIVATION_POLICY,
            },
        },
        None,
    )


def _empty_result(case: dict) -> dict[str, Any]:
    return {
        "case_id": case["id"],
        "alarm_code": None,
        "derived_surfaces": [],
        "semantic_aligned": [],
        "fixture_only": [],
        "imported_only": [],
        "missing_from_considered": [],
        "unresolved_events": [],
        "pre_ledger_birth_event_ids": [],
        "shipped_gate_receipts": {},
        "receipts": {
            "derivation_policy": DERIVATION_POLICY,
            "derived_surface_count": 0,
            "semantic_aligned_count": 0,
            "fixture_only_count": 0,
            "imported_only_count": 0,
            "missing_from_considered_count": 0,
            "unresolved_event_count": 0,
        },
        "reasons": [],
    }


def _run_shipped_gate_receipts(case: dict, derived: list[dict]) -> dict[str, Any]:
    receipts: dict[str, Any] = {}
    anchor = case["imported_anchor"]

    if case.get("run_shipped_silent_omission_gate"):
        silent_case = deepcopy(case)
        silent_case["ground_truth"] = {"required_declarations": deepcopy(derived)}
        silent_case["independent_footprint"] = {
            "footprint_id": anchor["anchor_id"],
            "observer_id": anchor["producer_id"],
            "observer_kind": "imported_foreign_event_stream",
            "independent_of_proposer": True,
            "events": deepcopy(anchor.get("events", [])),
        }
        receipts["silent_omission"] = evaluate_silent_omission_case(silent_case)

    if case.get("run_shipped_considered_set_gate"):
        considered_case = deepcopy(case)
        considered_case["expected_set"] = deepcopy(derived)
        considered_case["expected_set_provenance"] = {
            "source": "foreign_authored_event_stream",
            "authored_by": anchor["producer_id"],
            "independent_of_proposer": True,
        }
        receipts["considered_set"] = evaluate_considered_set_case(considered_case)

    return receipts


def evaluate_imported_anchor_case(case: dict) -> dict[str, Any]:
    result = _empty_result(case)
    anchor = case.get("imported_anchor") or {}
    result["receipts"]["anchor_id"] = anchor.get("anchor_id")
    result["receipts"]["producer_id"] = anchor.get("producer_id")

    if anchor.get("receipt_required") and not anchor.get("receipt_present"):
        result.update(
            {
                "alarm_code": "imported_anchor_integrity_failure",
                "reasons": ["a required foreign receipt is missing; an empty stream cannot be read as a clean world"],
            }
        )
        return result

    if not _valid_foreign_provenance(case, anchor):
        result.update(
            {
                "alarm_code": "imported_anchor_provenance_failure",
                "reasons": ["the imported stream does not resolve to an observer outside the proposer process"],
            }
        )
        return result

    anchor_id = anchor.get("anchor_id")
    if not isinstance(anchor_id, str) or not anchor_id:
        result.update(
            {
                "alarm_code": "imported_anchor_schema_failure",
                "reasons": ["imported anchor is missing a stable anchor_id"],
            }
        )
        return result

    records = case.get("records", [])
    derived: list[dict] = []
    unresolved: list[dict] = []
    pre_birth: list[str] = []
    ledger_birth = _parse_time(case.get("local_ledger_started_at"))

    for event in anchor.get("events", []):
        surface, reason = _derive_event_surface(event=event, records=records, anchor_id=anchor_id)
        if reason:
            unresolved.append({"event_id": event.get("event_id"), "reason": reason})
            continue
        if surface is not None:
            derived.append(surface)
            event_time = _parse_time(event.get("at"))
            if ledger_birth and event_time and event_time < ledger_birth:
                pre_birth.append(event["event_id"])

    fixture = case.get("fixture_expected_set") or []
    considered = case.get("proposer_emission", {}).get("considered_set") or []
    imported_by_semantics = _index_by_semantics(derived)
    fixture_by_semantics = _index_by_semantics(fixture)
    considered_by_semantics = _index_by_semantics(considered)

    aligned_keys = imported_by_semantics.keys() & fixture_by_semantics.keys()
    fixture_only_keys = fixture_by_semantics.keys() - imported_by_semantics.keys()
    imported_only_keys = imported_by_semantics.keys() - fixture_by_semantics.keys()
    missing_considered_keys = imported_by_semantics.keys() - considered_by_semantics.keys()

    result["derived_surfaces"] = derived
    result["semantic_aligned"] = [
        _semantic_receipt(imported_by_semantics[key]) for key in sorted(aligned_keys, key=str)
    ]
    result["fixture_only"] = [
        _semantic_receipt(fixture_by_semantics[key]) for key in sorted(fixture_only_keys, key=str)
    ]
    result["imported_only"] = [
        _semantic_receipt(imported_by_semantics[key]) for key in sorted(imported_only_keys, key=str)
    ]
    result["missing_from_considered"] = [
        _semantic_receipt(imported_by_semantics[key]) for key in sorted(missing_considered_keys, key=str)
    ]
    result["unresolved_events"] = unresolved
    result["pre_ledger_birth_event_ids"] = pre_birth
    result["shipped_gate_receipts"] = _run_shipped_gate_receipts(case, derived)

    counts = {
        "derived_surface_count": len(derived),
        "semantic_aligned_count": len(aligned_keys),
        "fixture_only_count": len(fixture_only_keys),
        "imported_only_count": len(imported_only_keys),
        "missing_from_considered_count": len(missing_considered_keys),
        "unresolved_event_count": len(unresolved),
    }
    result["receipts"].update(counts)

    considered_receipt = result["shipped_gate_receipts"].get("considered_set")
    if considered_receipt:
        semantic_match_exists = bool(derived) and not missing_considered_keys
        result["receipts"]["considered_set_identity_break"] = bool(
            semantic_match_exists and considered_receipt.get("alarm_code") == "hole_in_considered_set"
        )

    if unresolved:
        result["alarm_code"] = "imported_anchor_unresolved"
        result["reasons"] = ["one or more foreign events could not be mapped to an authority surface without guessing"]
    else:
        result["reasons"] = ["imported events were evaluated under the frozen derivation policy"]

    return result
