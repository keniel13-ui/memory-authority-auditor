from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
from typing import Any


EVENT_REQUIRED_FIELDS = (
    "specversion",
    "id",
    "source",
    "type",
    "subject",
    "event_time",
    "observed_time",
    "datacontenttype",
    "data",
    "data_digest",
    "producer_identity",
)
CENSUS_REQUIRED_FIELDS = (
    "receipt_id",
    "observer_id",
    "observed_at",
    "authority_namespace",
    "resources",
    "resource_aliases",
    "census_digest",
)
COVERAGE_REQUIRED_FIELDS = (
    "receipt_id",
    "observer_id",
    "authority_namespace",
    "coverage_start",
    "coverage_end",
    "local_ledger_started_at",
    "cursor_start",
    "cursor_end",
    "receipt_present",
    "coverage_claim",
)
SURFACE_FIELDS = (
    "schema",
    "authority_namespace",
    "kind",
    "source_resource_id",
    "target_resource_id",
    "relation_type",
)


def _reject_unsupported_numbers(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("Anchor Contract v0 canonical payloads do not admit floating-point values")
    if isinstance(value, dict):
        for child in value.values():
            _reject_unsupported_numbers(child)
    elif isinstance(value, list):
        for child in value:
            _reject_unsupported_numbers(child)


def canonical_json(value: Any) -> str:
    """RFC 8785-compatible for the v0 profile's strings, booleans, integers, lists, and objects."""
    _reject_unsupported_numbers(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def canonical_surface_payload(surface: dict) -> dict[str, Any]:
    missing = [field for field in SURFACE_FIELDS if field not in surface]
    if missing:
        raise ValueError(f"surface payload missing required fields: {missing}")
    return {field: surface[field] for field in SURFACE_FIELDS}


def surface_key(surface: dict) -> str:
    payload = canonical_surface_payload(surface)
    return "surface:v0:" + content_digest(payload)


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _resolve_receipt(container: dict, kind: str, packet: dict) -> dict | None:
    direct = container.get(f"{kind}_receipt")
    if isinstance(direct, dict):
        return deepcopy(direct)

    ref = container.get(f"{kind}_ref")
    if not isinstance(ref, str):
        return None
    base = packet.get("shared_receipts", {}).get(ref)
    if not isinstance(base, dict):
        return None
    resolved = deepcopy(base)
    overrides = container.get(f"{kind}_overrides") or {}
    if isinstance(overrides, dict):
        resolved.update(deepcopy(overrides))
    return resolved


def _empty_result(case: dict) -> dict[str, Any]:
    return {
        "case_id": case["id"],
        "alarm_code": None,
        "derived_surfaces": [],
        "surface_keys": [],
        "missing_fields": [],
        "reasons": [],
        "receipts": {
            "derived_surface_count": 0,
            "route_receipt_count": 0,
            "unique_event_count": 0,
            "duplicate_replay_count": 0,
            "candidate_target_count": 0,
            "delivery_delay_seconds": None,
            "pre_local_ledger_birth": False,
            "historical_completeness_claimed": False,
            "event_time_preserved": False,
            "route_surface_keys_equal": None,
            "keys_differ": None,
            "target_selection_attempted": False,
            "must_not_treat_as_observed_empty": False,
            "labels_count_as_proof": False,
        },
    }


def _fail(result: dict, alarm_code: str, reason: str, *, missing_fields: list[str] | None = None) -> dict:
    result["alarm_code"] = alarm_code
    result["reasons"] = [reason]
    if missing_fields is not None:
        result["missing_fields"] = missing_fields
    return result


def _validate_event(result: dict, event: dict, policy: dict) -> dict | None:
    missing = [field for field in EVENT_REQUIRED_FIELDS if field not in event]
    if missing:
        return _fail(
            result,
            "event_receipt_schema_failure",
            "event receipt is missing required contract fields",
            missing_fields=missing,
        )
    if not isinstance(event.get("data"), dict):
        return _fail(result, "event_receipt_schema_failure", "event data must be an object")
    if event.get("specversion") != "1.0" or event.get("datacontenttype") != "application/json":
        return _fail(result, "event_receipt_schema_failure", "event envelope is outside the v0 profile")
    if event.get("type") not in policy.get("input_event_types", []):
        return _fail(result, "unsupported_event_type", "event type is not admitted by the derivation policy")
    if event.get("subject") != event["data"].get("record_id"):
        return _fail(result, "event_subject_mismatch", "event subject disagrees with the payload resource identity")
    if content_digest(event["data"]) != event.get("data_digest"):
        return _fail(result, "event_integrity_failure", "event data does not match its declared digest")
    producer = event.get("producer_identity") or {}
    if not producer.get("producer_id") or not producer.get("outside_proposer_process"):
        return _fail(
            result,
            "producer_provenance_failure",
            "event producer does not resolve outside the proposer process",
        )
    event_time = _parse_time(event.get("event_time"))
    observed_time = _parse_time(event.get("observed_time"))
    if event_time is None or observed_time is None:
        return _fail(result, "event_receipt_schema_failure", "event clocks must be valid timestamps")
    if observed_time < event_time:
        return _fail(result, "event_time_integrity_failure", "observed_time precedes event_time")
    return None


def _validate_policy(result: dict, policy: dict) -> dict | None:
    required = (
        "policy_id",
        "policy_version",
        "input_event_types",
        "authority_namespace",
        "rule",
        "unresolved_states",
        "policy_digest",
    )
    missing = [field for field in required if field not in policy]
    if missing:
        return _fail(result, "policy_schema_failure", "derivation policy receipt is incomplete", missing_fields=missing)
    payload = {key: value for key, value in policy.items() if key != "policy_digest"}
    if content_digest(payload) != policy["policy_digest"]:
        return _fail(result, "policy_integrity_failure", "derivation policy does not match its digest")
    return None


def _validate_coverage(result: dict, coverage: dict | None, event: dict) -> dict | None:
    if not coverage or coverage.get("receipt_present") is False:
        result["receipts"]["must_not_treat_as_observed_empty"] = True
        return _fail(result, "coverage_integrity_failure", "required coverage receipt is missing")
    missing = [field for field in COVERAGE_REQUIRED_FIELDS if field not in coverage]
    if missing:
        return _fail(result, "coverage_schema_failure", "coverage receipt is incomplete", missing_fields=missing)
    if coverage.get("coverage_claim") != "complete_for_named_source_namespace_and_cursor_window":
        return _fail(result, "coverage_integrity_failure", "coverage claim is absent or outside the v0 bounded profile")
    cursor_start = coverage.get("cursor_start")
    cursor_end = coverage.get("cursor_end")
    if (
        not isinstance(cursor_start, str)
        or not isinstance(cursor_end, str)
        or not cursor_start.isdigit()
        or not cursor_end.isdigit()
        or int(cursor_start) > int(cursor_end)
    ):
        return _fail(result, "coverage_integrity_failure", "coverage cursor interval is invalid")

    start = _parse_time(coverage.get("coverage_start"))
    end = _parse_time(coverage.get("coverage_end"))
    ledger_birth = _parse_time(coverage.get("local_ledger_started_at"))
    event_time = _parse_time(event.get("event_time"))
    observed_time = _parse_time(event.get("observed_time"))
    if not start or not end or not ledger_birth or not event_time or not observed_time or start > end:
        return _fail(result, "coverage_schema_failure", "coverage or event timestamps are invalid")
    if event_time < start or event_time > end:
        return _fail(result, "event_outside_coverage", "event time falls outside the declared coverage window")
    if observed_time > end:
        return _fail(result, "observation_outside_coverage", "observed time falls outside the declared coverage window")

    delay = int((observed_time - event_time).total_seconds())
    prior_delay = result["receipts"]["delivery_delay_seconds"]
    result["receipts"]["delivery_delay_seconds"] = delay if prior_delay is None else max(prior_delay, delay)
    result["receipts"]["event_time_preserved"] = True
    if event_time < ledger_birth:
        result["receipts"]["pre_local_ledger_birth"] = True
    return None


def _validate_census(result: dict, census: dict | None) -> dict | None:
    if not census:
        return _fail(result, "census_schema_failure", "census receipt is missing")
    missing = [field for field in CENSUS_REQUIRED_FIELDS if field not in census]
    if missing:
        return _fail(result, "census_schema_failure", "census receipt is incomplete", missing_fields=missing)
    payload = {
        "authority_namespace": census["authority_namespace"],
        "resources": census["resources"],
    }
    if content_digest(payload) != census.get("census_digest"):
        return _fail(result, "census_integrity_failure", "census payload does not match its declared digest")
    if _parse_time(census.get("observed_at")) is None:
        return _fail(result, "census_schema_failure", "census observed_at is not a valid timestamp")
    resources = census.get("resources")
    if not isinstance(resources, list) or not all(isinstance(resource, dict) for resource in resources):
        return _fail(result, "census_schema_failure", "census resources must be typed objects")
    for resource in resources:
        if not all(isinstance(resource.get(field), str) for field in ("resource_id", "scope", "status")):
            return _fail(result, "census_schema_failure", "census resource is missing typed identity, scope, or status")
    resource_ids = [resource.get("resource_id") for resource in census.get("resources", [])]
    if len(resource_ids) != len(set(resource_ids)):
        return _fail(result, "census_integrity_failure", "census contains duplicate resource identities")
    return None


def _event_signature(event: dict) -> tuple[Any, ...]:
    return (
        event.get("type"),
        event.get("subject"),
        event.get("event_time"),
        event.get("datacontenttype"),
        event.get("data_digest"),
    )


def _deduplicate_contexts(result: dict, contexts: list[dict]) -> tuple[list[dict], dict | None]:
    unique: list[dict] = []
    seen: dict[tuple[Any, Any], tuple[Any, ...]] = {}
    for context in contexts:
        event = context["event"]
        identity = (event.get("source"), event.get("id"))
        signature = _event_signature(event)
        prior = seen.get(identity)
        if prior is None:
            seen[identity] = signature
            unique.append(context)
        elif prior == signature:
            result["receipts"]["duplicate_replay_count"] += 1
        else:
            return [], _fail(
                result,
                "event_identity_conflict",
                "one source and event ID carry conflicting event payloads",
            )
    result["receipts"]["unique_event_count"] = len(unique)
    return unique, None


def _build_contexts(case: dict, packet: dict) -> list[dict]:
    if isinstance(case.get("routes"), list):
        return [
            {
                "route_id": route.get("route_id"),
                "event": _resolve_receipt(route, "event", packet),
                "census": _resolve_receipt(route, "census", packet),
                "coverage": _resolve_receipt(route, "coverage", packet),
            }
            for route in case["routes"]
        ]

    raw_events = case.get("event_receipts")
    if isinstance(raw_events, list):
        events = [_resolve_receipt(row, "event", packet) for row in raw_events]
    else:
        events = [_resolve_receipt(case, "event", packet)]
    census = _resolve_receipt(case, "census", packet)
    coverage = _resolve_receipt(case, "coverage", packet)
    return [
        {"route_id": case.get("route_id"), "event": event, "census": deepcopy(census), "coverage": deepcopy(coverage)}
        for event in events
    ]


def _evaluate_surface_key_only(case: dict, result: dict) -> dict:
    payloads = case.get("surface_payloads", [])
    keys = [surface_key(payload) for payload in payloads]
    result["surface_keys"] = keys
    result["receipts"]["keys_differ"] = len(keys) == len(set(keys))
    result["reasons"] = ["semantic payloads canonicalized without provenance fields"]
    return result


def evaluate_anchor_contract_case(case: dict, packet: dict) -> dict[str, Any]:
    result = _empty_result(case)

    if "surface_payloads" in case:
        return _evaluate_surface_key_only(case, result)

    policy = packet.get("derivation_policy") or {}
    failure = _validate_policy(result, policy)
    if failure:
        return failure

    contexts = _build_contexts(case, packet)
    if not contexts or any(not isinstance(context.get("event"), dict) for context in contexts):
        return _fail(result, "event_receipt_schema_failure", "event receipt is missing")

    for context in contexts:
        failure = _validate_event(result, context["event"], policy)
        if failure:
            return failure

    contexts, failure = _deduplicate_contexts(result, contexts)
    if failure:
        return failure

    by_key: dict[str, dict] = {}
    route_keys: list[str] = []
    for context in contexts:
        event = context["event"]
        coverage = context["coverage"]
        census = context["census"]

        failure = _validate_coverage(result, coverage, event)
        if failure:
            return failure
        failure = _validate_census(result, census)
        if failure:
            return failure
        if not (
            census["authority_namespace"]
            == coverage["authority_namespace"]
            == policy["authority_namespace"]
        ):
            return _fail(
                result,
                "receipt_namespace_mismatch",
                "event derivation receipts do not bind the same authority namespace",
            )
        census_observed = _parse_time(census["observed_at"])
        coverage_start = _parse_time(coverage["coverage_start"])
        coverage_end = _parse_time(coverage["coverage_end"])
        if not census_observed or not coverage_start or not coverage_end or not (
            coverage_start <= census_observed <= coverage_end
        ):
            return _fail(
                result,
                "census_time_integrity_failure",
                "census observation falls outside the declared coverage window",
            )

        data = event["data"]
        source_resource_id = data.get("record_id")
        scope = data.get("scope")
        if not isinstance(scope, str) or not scope:
            return _fail(result, "missing_scope", "event does not identify an authority scope")

        alias_claim = case.get("alias_claim")
        if alias_claim and alias_claim.get("source_resource_id") == source_resource_id:
            if not alias_claim.get("mapping_receipt"):
                return _fail(result, "resource_identity_unresolved", "source-local resource alias has no mapping receipt")
            source_resource_id = alias_claim["canonical_resource_id"]

        resources = census["resources"]
        live_targets = [
            resource
            for resource in resources
            if resource.get("status") == "live"
            and resource.get("scope") == scope
            and resource.get("resource_id") != source_resource_id
        ]
        result["receipts"]["target_selection_attempted"] = True
        result["receipts"]["candidate_target_count"] = len(live_targets)
        if not live_targets:
            return _fail(result, "no_live_same_scope_target", "census has no live same-scope target")
        if len(live_targets) > 1:
            return _fail(result, "ambiguous_census_target", "census has multiple live same-scope targets")

        payload = {
            "schema": packet["canonical_surface_identity"]["schema"],
            "authority_namespace": census["authority_namespace"],
            "kind": "authority_change_candidate",
            "source_resource_id": source_resource_id,
            "target_resource_id": live_targets[0]["resource_id"],
            "relation_type": "supersedes",
        }
        key = surface_key(payload)
        route_keys.append(key)
        existing = by_key.get(key)
        if existing and existing["surface_payload"] != payload:
            return _fail(result, "surface_key_collision", "one semantic key resolves to different canonical payloads")
        if existing:
            existing["supporting_event_receipt_ids"].append(event["id"])
        else:
            by_key[key] = {
                "surface_key": key,
                "surface_payload": payload,
                "supporting_event_receipt_ids": [event["id"]],
                "census_receipt_id": census["receipt_id"],
                "coverage_receipt_id": coverage["receipt_id"],
                "policy_id": policy["policy_id"],
                "policy_version": policy["policy_version"],
                "derivation_state": "derived",
                "unresolved_reasons": [],
            }

    result["derived_surfaces"] = list(by_key.values())
    result["surface_keys"] = list(by_key.keys())
    result["receipts"]["derived_surface_count"] = len(by_key)
    result["receipts"]["route_receipt_count"] = len(contexts)
    result["receipts"]["route_surface_keys_equal"] = len(route_keys) > 1 and len(set(route_keys)) == 1
    result["reasons"] = ["contract receipts validated and semantic surfaces derived"]
    return result
