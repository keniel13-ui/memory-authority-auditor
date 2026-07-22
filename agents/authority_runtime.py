from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
from typing import Any

from agents.anchor_contract import content_digest, surface_key
from agents.resource_mapping import evaluate_resource_mapping_case


STARTUP_REQUIRED_FIELDS = (
    "packet_id",
    "session_id",
    "claimed_at",
    "audit_time",
    "proposed_actions",
    "packet_digest",
)
ACTION_REQUIRED_FIELDS = (
    "receipt_id",
    "source_id",
    "source_class",
    "recorded_at",
    "issued_at",
    "resource_alias",
    "authority_scope",
    "operation",
    "from_state",
    "to_state",
    "source_locator",
    "source_excerpt",
    "source_excerpt_digest",
    "receipt_digest",
)
STATE_REQUIRED_FIELDS = (
    "receipt_id",
    "source_id",
    "source_class",
    "recorded_at",
    "observed_at",
    "canonical_resource_id",
    "authority_scope",
    "state_key",
    "state_value",
    "completion_action_key",
    "source_locator",
    "source_excerpt",
    "source_excerpt_digest",
    "receipt_digest",
)
POLICY_REQUIRED_FIELDS = (
    "policy_id",
    "policy_version",
    "allowed_operations",
    "trusted_state_observer_ids",
    "source_authority_order",
    "source_registry",
    "decision_rule",
    "decision_states",
    "policy_digest",
)
STATE_MANIFEST_REQUIRED_FIELDS = (
    "manifest_id",
    "observer_id",
    "observed_at",
    "canonical_resource_id",
    "authority_scope",
    "coverage_start",
    "coverage_end",
    "state_receipt_ids",
    "completeness_claim",
    "manifest_digest",
)
DECISION_EXIT_CODES = {
    "ALLOW": 0,
    "BLOCK_STALE_ACTION": 3,
    "CONFLICT": 4,
    "UNKNOWN": 5,
}
DECISION_STATES = tuple(DECISION_EXIT_CODES)
ACTION_FIELDS = (
    "schema",
    "authority_namespace",
    "kind",
    "resource_id",
    "operation",
    "from_state",
    "to_state",
)


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _raw_digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _without_digest(value: dict, digest_field: str) -> dict:
    return {key: child for key, child in value.items() if key != digest_field}


def _resolve_shared(packet: dict, ref: Any) -> dict | None:
    if not isinstance(ref, str):
        return None
    value = packet.get("shared_objects", {}).get(ref)
    return deepcopy(value) if isinstance(value, dict) else None


def _resolve_single(case: dict, packet: dict, kind: str) -> dict | None:
    direct = case.get(kind)
    if isinstance(direct, dict):
        return deepcopy(direct)
    value = _resolve_shared(packet, case.get(f"{kind}_ref"))
    if value is None:
        return None
    overrides = case.get(f"{kind}_overrides") or {}
    if isinstance(overrides, dict):
        value.update(deepcopy(overrides))
    return value


def _resolve_state_receipts(case: dict, packet: dict) -> list[dict]:
    direct = case.get("state_receipts")
    if isinstance(direct, list):
        resolved: list[dict] = []
        for row in direct:
            if not isinstance(row, dict):
                resolved.append({})
                continue
            if "receipt_ref" in row:
                receipt = _resolve_shared(packet, row.get("receipt_ref")) or {}
                overrides = row.get("receipt_overrides") or {}
                if isinstance(overrides, dict):
                    receipt.update(deepcopy(overrides))
                resolved.append(receipt)
            else:
                resolved.append(deepcopy(row))
        return resolved

    refs = case.get("state_receipt_refs")
    if not isinstance(refs, list):
        return []
    return [_resolve_shared(packet, ref) or {} for ref in refs]


def _resolve_mapping_case(case: dict, packet: dict) -> tuple[dict | None, dict | None]:
    mapping_packet = packet.get("resource_mapping_packet")
    if not isinstance(mapping_packet, dict):
        return None, None
    direct = case.get("mapping_case")
    if isinstance(direct, dict):
        mapping_case = deepcopy(direct)
    else:
        ref = case.get("mapping_case_ref")
        base = mapping_packet.get("mapping_cases", {}).get(ref)
        if not isinstance(base, dict):
            return None, mapping_packet
        mapping_case = deepcopy(base)
    overrides = case.get("mapping_case_overrides") or {}
    if isinstance(overrides, dict):
        mapping_case.update(deepcopy(overrides))
    return mapping_case, mapping_packet


def _base_result(case: dict) -> dict[str, Any]:
    return {
        "schema": "authority_decision/v0",
        "case_id": case.get("id"),
        "decision": "UNKNOWN",
        "decision_code": "runtime_not_evaluated",
        "action_key": None,
        "surface_key": None,
        "mapping_key": None,
        "canonical_resource_id": None,
        "canonical_action": None,
        "canonical_surface": None,
        "authority_scope": None,
        "action_receipt_id": None,
        "mapping_receipt_id": None,
        "authority_grant_id": None,
        "state_evidence_manifest_id": None,
        "state_evidence_manifest_digest": None,
        "covered_state_receipt_ids": [],
        "controlling_state_receipt_ids": [],
        "ignored_state_receipt_ids": [],
        "duplicate_replay_receipt_ids": [],
        "subject_time": None,
        "audit_time": None,
        "evidence_chain": [],
        "unknowns": [],
        "mutation_authorized": False,
        "exit_code": DECISION_EXIT_CODES["UNKNOWN"],
        "decision_digest": None,
    }


def _finish(result: dict, decision: str, code: str, unknowns: list[str] | None = None) -> dict:
    result["decision"] = decision
    result["decision_code"] = code
    result["unknowns"] = sorted(set(unknowns or []))
    result["mutation_authorized"] = decision == "ALLOW"
    result["exit_code"] = DECISION_EXIT_CODES[decision]
    result["decision_digest"] = content_digest(_without_digest(result, "decision_digest"))
    return result


def _integrity_error(result: dict, code: str, reason: str) -> dict:
    return _finish(result, "UNKNOWN", code, [reason])


def _validate_policy(policy: dict) -> str | None:
    missing = [field for field in POLICY_REQUIRED_FIELDS if field not in policy]
    if missing:
        return f"runtime policy missing required fields: {missing}"
    if content_digest(_without_digest(policy, "policy_digest")) != policy.get("policy_digest"):
        return "runtime policy does not match its digest"
    if policy.get("decision_states") != list(DECISION_STATES):
        return "runtime policy decision states differ from the frozen v0 profile"
    if not isinstance(policy.get("allowed_operations"), list) or not all(
        isinstance(value, str) and value for value in policy["allowed_operations"]
    ):
        return "runtime policy operations are untyped"
    observers = policy.get("trusted_state_observer_ids")
    if not isinstance(observers, list) or not observers or len(observers) != len(set(observers)) or not all(
        isinstance(value, str) and value for value in observers
    ):
        return "runtime trusted state observers are invalid"
    order = policy.get("source_authority_order")
    if not isinstance(order, list) or not order or len(order) != len(set(order)) or not all(
        isinstance(value, str) and value for value in order
    ):
        return "runtime source authority order is invalid"
    registry = policy.get("source_registry")
    if not isinstance(registry, dict) or not registry or any(
        not isinstance(source_id, str)
        or not source_id
        or source_class not in order
        for source_id, source_class in registry.items()
    ):
        return "runtime source registry is invalid"
    return None


def _validate_startup(startup: dict | None) -> tuple[datetime | None, str | None]:
    if not isinstance(startup, dict):
        return None, "startup claim is missing"
    missing = [field for field in STARTUP_REQUIRED_FIELDS if field not in startup]
    if missing:
        return None, f"startup claim missing required fields: {missing}"
    if content_digest(_without_digest(startup, "packet_digest")) != startup.get("packet_digest"):
        return None, "startup claim does not match its digest"
    if not all(isinstance(startup.get(field), str) and startup[field] for field in ("packet_id", "session_id")):
        return None, "startup claim identity is untyped"
    proposed = startup.get("proposed_actions")
    if not isinstance(proposed, list) or len(proposed) != 1 or not isinstance(proposed[0], str) or not proposed[0]:
        return None, "v0 requires exactly one typed proposed action"
    claimed_at = _parse_time(startup.get("claimed_at"))
    audit_time = _parse_time(startup.get("audit_time"))
    if claimed_at is None or audit_time is None or claimed_at > audit_time:
        return None, "startup claim clocks are invalid"
    return audit_time, None


def _validate_receipt_integrity(receipt: dict | None, required: tuple[str, ...]) -> str | None:
    if not isinstance(receipt, dict):
        return "receipt is missing"
    missing = [field for field in required if field not in receipt]
    if missing:
        return f"receipt missing required fields: {missing}"
    excerpt = receipt.get("source_excerpt")
    if not isinstance(excerpt, str) or _raw_digest(excerpt) != receipt.get("source_excerpt_digest"):
        return "source excerpt does not match its exact-byte digest"
    if content_digest(_without_digest(receipt, "receipt_digest")) != receipt.get("receipt_digest"):
        return "receipt does not match its canonical digest"
    return None


def _evidence_row(receipt: dict, receipt_type: str) -> dict[str, Any]:
    return {
        "receipt_id": receipt["receipt_id"],
        "receipt_type": receipt_type,
        "source_id": receipt["source_id"],
        "source_class": receipt["source_class"],
        "recorded_at": receipt["recorded_at"],
        "issued_at": receipt.get("issued_at"),
        "observed_at": receipt.get("observed_at"),
        "source_locator": receipt["source_locator"],
        "digest": receipt["receipt_digest"],
    }


def _canonical_action(mapping: dict, action: dict) -> dict[str, str]:
    return {
        "schema": "authority_action/v0",
        "authority_namespace": f"{mapping['canonical_namespace']}/{action['authority_scope']}",
        "kind": "infrastructure_transition",
        "resource_id": mapping["canonical_resource_id"],
        "operation": action["operation"],
        "from_state": action["from_state"],
        "to_state": action["to_state"],
    }


def action_key(action_payload: dict) -> str:
    missing = [field for field in ACTION_FIELDS if field not in action_payload]
    if missing:
        raise ValueError(f"action payload missing required fields: {missing}")
    canonical = {field: action_payload[field] for field in ACTION_FIELDS}
    return "action:v0:" + content_digest(canonical)


def _canonical_surface(action_payload: dict) -> dict[str, str]:
    return {
        "schema": "authority_surface/v0",
        "authority_namespace": action_payload["authority_namespace"],
        "kind": action_payload["kind"],
        "source_resource_id": f"{action_payload['resource_id']}#{action_payload['from_state']}",
        "target_resource_id": f"{action_payload['resource_id']}#{action_payload['to_state']}",
        "relation_type": "supersedes",
    }


def _validate_action(
    result: dict,
    action: dict | None,
    startup: dict,
    policy: dict,
    audit_time: datetime,
) -> str | None:
    failure = _validate_receipt_integrity(action, ACTION_REQUIRED_FIELDS)
    if failure:
        return failure
    assert action is not None
    if any(
        not isinstance(action.get(field), str) or not action[field]
        for field in (
            "receipt_id",
            "source_id",
            "source_class",
            "authority_scope",
            "operation",
            "from_state",
            "to_state",
            "source_locator",
        )
    ):
        return "action receipt fields are untyped"
    alias = action.get("resource_alias")
    if not isinstance(alias, dict) or set(alias) != {"source_namespace", "source_resource_id"} or any(
        not isinstance(alias.get(field), str) or not alias[field]
        for field in ("source_namespace", "source_resource_id")
    ):
        return "action resource alias is invalid"
    if startup["proposed_actions"] != [action["receipt_id"]]:
        return "startup claim and action receipt identity differ"
    if action["operation"] not in policy["allowed_operations"]:
        return "action operation is outside the runtime policy"
    if policy["source_registry"].get(action["source_id"]) != action["source_class"]:
        return "action source class is not authorized by the runtime registry"
    issued_at = _parse_time(action.get("issued_at"))
    recorded_at = _parse_time(action.get("recorded_at"))
    if issued_at is None or recorded_at is None or issued_at > recorded_at or recorded_at > audit_time:
        return "action receipt clocks are invalid for the audit"
    result["action_receipt_id"] = action["receipt_id"]
    result["authority_scope"] = action["authority_scope"]
    result["subject_time"] = action["issued_at"]
    result["evidence_chain"].append(_evidence_row(action, "action"))
    return None


def _validate_mapping(
    result: dict,
    case: dict,
    packet: dict,
    action: dict,
    audit_time: datetime,
) -> dict | None:
    mapping_case, mapping_packet = _resolve_mapping_case(case, packet)
    if not isinstance(mapping_case, dict) or not isinstance(mapping_packet, dict):
        _finish(result, "UNKNOWN", "resource_identity_unresolved", ["embedded resource mapping case is missing"])
        return None
    mapping = evaluate_resource_mapping_case(mapping_case, mapping_packet)
    if mapping.get("resolution_state") != "resolved":
        _finish(
            result,
            "UNKNOWN",
            mapping.get("alarm_code") or "resource_identity_unresolved",
            mapping.get("unresolved_reasons") or ["resource identity did not resolve"],
        )
        return None
    alias = action["resource_alias"]
    mapping_time = _parse_time(mapping.get("resolution_time"))
    coherent = (
        mapping.get("source_namespace") == alias["source_namespace"]
        and mapping.get("source_resource_id") == alias["source_resource_id"]
        and mapping.get("authority_scope") == action["authority_scope"]
        and mapping.get("subject_time") == action["issued_at"]
        and mapping_time is not None
        and mapping_time <= audit_time
    )
    if not coherent:
        _finish(
            result,
            "UNKNOWN",
            "mapping_context_mismatch",
            ["resolved mapping does not bind the action alias, scope, subject time, and audit time"],
        )
        return None
    result["mapping_key"] = mapping["mapping_key"]
    result["canonical_resource_id"] = mapping["canonical_resource_id"]
    result["mapping_receipt_id"] = mapping["mapping_receipt_id"]
    result["authority_grant_id"] = mapping["authority_grant_id"]
    return mapping


def _validate_and_deduplicate_states(
    result: dict,
    receipts: list[dict],
    policy: dict,
    audit_time: datetime,
) -> tuple[list[dict] | None, list[str]]:
    unique: list[dict] = []
    seen: dict[str, str] = {}
    ineligible_reasons: list[str] = []
    for receipt in receipts:
        failure = _validate_receipt_integrity(receipt, STATE_REQUIRED_FIELDS)
        if failure:
            _integrity_error(result, "evidence_integrity_failure", failure)
            return None, []
        if any(
            not isinstance(receipt.get(field), str) or not receipt[field]
            for field in (
                "receipt_id",
                "source_id",
                "source_class",
                "recorded_at",
                "observed_at",
                "canonical_resource_id",
                "authority_scope",
                "state_key",
                "state_value",
                "source_locator",
            )
        ) or (
            receipt.get("completion_action_key") is not None
            and (not isinstance(receipt["completion_action_key"], str) or not receipt["completion_action_key"])
        ):
            _integrity_error(result, "evidence_integrity_failure", "state receipt fields are untyped")
            return None, []
        observed_at = _parse_time(receipt["observed_at"])
        recorded_at = _parse_time(receipt["recorded_at"])
        if observed_at is None or recorded_at is None or observed_at > recorded_at:
            _integrity_error(result, "evidence_integrity_failure", "state receipt clocks are invalid")
            return None, []
        receipt_id = receipt["receipt_id"]
        signature = content_digest(receipt)
        if receipt_id in seen:
            if seen[receipt_id] != signature:
                _integrity_error(
                    result,
                    "evidence_identity_conflict",
                    "one state receipt ID carries conflicting canonical bytes",
                )
                return None, []
            result["duplicate_replay_receipt_ids"].append(receipt_id)
            continue
        seen[receipt_id] = signature
        unique.append(receipt)
        result["evidence_chain"].append(_evidence_row(receipt, "state"))
        registered_class = policy["source_registry"].get(receipt["source_id"])
        if registered_class != receipt["source_class"]:
            ineligible_reasons.append(f"{receipt_id}:source_class_unregistered_or_mismatched")
        elif recorded_at > audit_time or observed_at > audit_time:
            ineligible_reasons.append(f"{receipt_id}:future_evidence")
    return unique, ineligible_reasons


def _validate_state_manifest(
    result: dict,
    manifest: dict | None,
    receipts: list[dict],
    policy: dict,
    canonical_resource_id: str,
    authority_scope: str,
    subject_time: datetime,
    audit_time: datetime,
) -> dict | None:
    if not isinstance(manifest, dict):
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            "state evidence manifest is missing",
        )
    missing_fields = [field for field in STATE_MANIFEST_REQUIRED_FIELDS if field not in manifest]
    if missing_fields:
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            f"state evidence manifest missing required fields: {missing_fields}",
        )
    if content_digest(_without_digest(manifest, "manifest_digest")) != manifest.get("manifest_digest"):
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            "state evidence manifest does not match its digest",
        )
    if any(
        not isinstance(manifest.get(field), str) or not manifest[field]
        for field in (
            "manifest_id",
            "observer_id",
            "observed_at",
            "canonical_resource_id",
            "authority_scope",
            "coverage_start",
            "coverage_end",
            "completeness_claim",
        )
    ):
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            "state evidence manifest fields are untyped",
        )
    if manifest["observer_id"] not in policy["trusted_state_observer_ids"]:
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            "state evidence manifest observer is outside the configured trust root",
        )
    if manifest["completeness_claim"] != "complete_for_named_resource_scope_and_window":
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            "state evidence manifest does not carry the exact bounded completeness claim",
        )
    if (
        manifest["canonical_resource_id"] != canonical_resource_id
        or manifest["authority_scope"] != authority_scope
    ):
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            "state evidence manifest resource or scope differs from the resolved action",
        )
    coverage_start = _parse_time(manifest["coverage_start"])
    coverage_end = _parse_time(manifest["coverage_end"])
    observed_at = _parse_time(manifest["observed_at"])
    if (
        coverage_start is None
        or coverage_end is None
        or observed_at is None
        or not (coverage_start <= subject_time <= audit_time <= coverage_end <= observed_at <= audit_time)
    ):
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            "state evidence manifest clocks do not cover the action through the audit time",
        )
    manifest_ids = manifest.get("state_receipt_ids")
    if (
        not isinstance(manifest_ids, list)
        or not all(isinstance(value, str) and value for value in manifest_ids)
        or len(manifest_ids) != len(set(manifest_ids))
        or manifest_ids != sorted(manifest_ids)
    ):
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            "state evidence manifest receipt IDs must be unique, typed, and sorted",
        )
    result["state_evidence_manifest_id"] = manifest["manifest_id"]
    result["state_evidence_manifest_digest"] = manifest["manifest_digest"]
    result["covered_state_receipt_ids"] = list(manifest_ids)

    actual_ids = sorted(receipt["receipt_id"] for receipt in receipts)
    missing_receipts = sorted(set(manifest_ids) - set(actual_ids))
    injected_receipts = sorted(set(actual_ids) - set(manifest_ids))
    if missing_receipts:
        return _finish(
            result,
            "UNKNOWN",
            "state_evidence_omission",
            [f"manifest-bound state receipt is missing: {receipt_id}" for receipt_id in missing_receipts],
        )
    if injected_receipts:
        return _finish(
            result,
            "UNKNOWN",
            "state_evidence_injection",
            [f"submitted state receipt is absent from the manifest: {receipt_id}" for receipt_id in injected_receipts],
        )
    outside_coverage = sorted(
        receipt["receipt_id"]
        for receipt in receipts
        if not (
            coverage_start <= _parse_time(receipt["observed_at"]) <= coverage_end
        )
    )
    if outside_coverage:
        return _integrity_error(
            result,
            "state_evidence_manifest_failure",
            f"state receipts fall outside manifest coverage: {outside_coverage}",
        )
    return None


def _select_state(
    result: dict,
    receipts: list[dict],
    policy: dict,
    canonical_resource_id: str,
    authority_scope: str,
    audit_time: datetime,
) -> tuple[list[dict], str | None]:
    rank = {source_class: index for index, source_class in enumerate(policy["source_authority_order"])}
    eligible: list[dict] = []
    mismatch_seen = False
    for receipt in receipts:
        registered_class = policy["source_registry"].get(receipt["source_id"])
        observed_at = _parse_time(receipt["observed_at"])
        recorded_at = _parse_time(receipt["recorded_at"])
        matches_surface = (
            receipt["canonical_resource_id"] == canonical_resource_id
            and receipt["authority_scope"] == authority_scope
            and receipt["state_key"] == "dns_provider"
        )
        if not matches_surface:
            mismatch_seen = True
        if (
            registered_class != receipt["source_class"]
            or observed_at is None
            or recorded_at is None
            or observed_at > audit_time
            or recorded_at > audit_time
            or not matches_surface
        ):
            result["ignored_state_receipt_ids"].append(receipt["receipt_id"])
            continue
        eligible.append(receipt)

    if not eligible:
        result["ignored_state_receipt_ids"] = sorted(set(result["ignored_state_receipt_ids"]))
        result["duplicate_replay_receipt_ids"] = sorted(result["duplicate_replay_receipt_ids"])
        return [], "state_scope_mismatch" if mismatch_seen else "current_state_missing"

    best_rank = min(rank[receipt["source_class"]] for receipt in eligible)
    strongest = [receipt for receipt in eligible if rank[receipt["source_class"]] == best_rank]
    latest_time = max(_parse_time(receipt["observed_at"]) for receipt in strongest)
    controlling = [receipt for receipt in strongest if _parse_time(receipt["observed_at"]) == latest_time]
    controlling_ids = {receipt["receipt_id"] for receipt in controlling}
    for receipt in eligible:
        if receipt["receipt_id"] not in controlling_ids:
            result["ignored_state_receipt_ids"].append(receipt["receipt_id"])
    controlling.sort(key=lambda receipt: receipt["receipt_id"])
    result["controlling_state_receipt_ids"] = [receipt["receipt_id"] for receipt in controlling]
    result["ignored_state_receipt_ids"] = sorted(set(result["ignored_state_receipt_ids"]))
    result["duplicate_replay_receipt_ids"] = sorted(result["duplicate_replay_receipt_ids"])
    return controlling, None


def evaluate_authority_case(case: dict, packet: dict) -> dict[str, Any]:
    """Evaluate one frozen single-action authority decision without executing the action."""
    result = _base_result(case)
    policy = packet.get("runtime_policy") or {}
    policy_failure = _validate_policy(policy)
    if policy_failure:
        return _integrity_error(result, "runtime_policy_integrity_failure", policy_failure)

    startup = _resolve_single(case, packet, "startup_claim")
    audit_time, startup_failure = _validate_startup(startup)
    if startup_failure or audit_time is None or startup is None:
        return _integrity_error(
            result,
            "startup_claim_integrity_failure",
            startup_failure or "startup audit time is unavailable",
        )
    result["audit_time"] = startup["audit_time"]

    action = _resolve_single(case, packet, "action_receipt")
    action_failure = _validate_action(result, action, startup, policy, audit_time)
    if action_failure or action is None:
        return _integrity_error(
            result,
            "action_receipt_integrity_failure",
            action_failure or "action receipt is unavailable",
        )

    mapping = _validate_mapping(result, case, packet, action, audit_time)
    if mapping is None:
        return result

    canonical_action = _canonical_action(mapping, action)
    canonical_surface = _canonical_surface(canonical_action)
    result["canonical_action"] = canonical_action
    result["action_key"] = action_key(canonical_action)
    result["canonical_surface"] = canonical_surface
    result["surface_key"] = surface_key(canonical_surface)

    states = _resolve_state_receipts(case, packet)
    validated, ineligible_reasons = _validate_and_deduplicate_states(result, states, policy, audit_time)
    if validated is None:
        return result
    manifest = _resolve_single(case, packet, "state_evidence_manifest")
    manifest_failure = _validate_state_manifest(
        result,
        manifest,
        validated,
        policy,
        mapping["canonical_resource_id"],
        action["authority_scope"],
        _parse_time(action["issued_at"]),
        audit_time,
    )
    if manifest_failure is not None:
        return manifest_failure
    controlling, selection_failure = _select_state(
        result,
        validated,
        policy,
        mapping["canonical_resource_id"],
        action["authority_scope"],
        audit_time,
    )
    if selection_failure:
        return _finish(result, "UNKNOWN", selection_failure, ineligible_reasons or [selection_failure])

    state_values = {receipt["state_value"] for receipt in controlling}
    if len(state_values) != 1:
        return _finish(result, "CONFLICT", "equally_authoritative_state_conflict")

    current_state = next(iter(state_values))
    if current_state == action["to_state"]:
        completion_bound = any(
            receipt["completion_action_key"] == result["action_key"] for receipt in controlling
        )
        if completion_bound:
            return _finish(result, "BLOCK_STALE_ACTION", "stale_action_completed")
        return _finish(
            result,
            "UNKNOWN",
            "target_state_unreceipted",
            ["target state is current but no controlling receipt binds completion of this action"],
        )
    if current_state == action["from_state"]:
        return _finish(result, "ALLOW", "transition_required")
    return _finish(
        result,
        "UNKNOWN",
        "unsupported_current_state",
        [f"current state {current_state!r} is neither the action source nor target state"],
    )


def _escape_markdown(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_decision_markdown(result: dict) -> str:
    authorization = "YES — dry-run policy allows the proposed action" if result["mutation_authorized"] else "NO"
    lines = [
        "# Authority Runtime v0 Decision",
        "",
        f"**Decision:** `{result['decision']}`  ",
        f"**Decision code:** `{result['decision_code']}`  ",
        f"**Mutation authorized:** {authorization}  ",
        f"**Case:** `{result.get('case_id')}`",
        "",
        "## Bound identities",
        "",
        f"- Action: `{result.get('action_key')}`",
        f"- Authority surface: `{result.get('surface_key')}`",
        f"- Resource mapping: `{result.get('mapping_key')}`",
        f"- Canonical resource: `{result.get('canonical_resource_id')}`",
        f"- Authority scope: `{result.get('authority_scope')}`",
        f"- State evidence manifest: `{result.get('state_evidence_manifest_id')}`",
        "",
        "## Decision explanation",
        "",
    ]
    explanations = {
        "stale_action_completed": "A later controlling receipt proves the requested target state is already current and binds completion of this exact action. Repeating the production action is blocked.",
        "transition_required": "The controlling receipt proves the source state is still current. The dry-run gate allows the proposed transition but does not execute it.",
        "equally_authoritative_state_conflict": "Equally controlling receipts disagree. The runtime refuses to choose by input order.",
    }
    lines.append(explanations.get(result["decision_code"], "The runtime lacks a complete, coherent authority chain and preserves the decision as unknown."))
    lines.extend(
        [
            "",
            f"- Controlling state receipts: `{', '.join(result['controlling_state_receipt_ids']) or 'none'}`",
            f"- Ignored state receipts: `{', '.join(result['ignored_state_receipt_ids']) or 'none'}`",
            f"- Collapsed replay receipts: `{', '.join(result['duplicate_replay_receipt_ids']) or 'none'}`",
            f"- Manifest-covered state receipts: `{', '.join(result['covered_state_receipt_ids']) or 'none'}`",
            f"- Audit time: `{result.get('audit_time')}`",
            "",
            "## Evidence chain",
            "",
            "| Receipt | Type | Authority class | Evidence time | Source | Digest |",
            "|---|---|---|---|---|---|",
        ]
    )
    for receipt in result["evidence_chain"]:
        evidence_time = receipt.get("observed_at") or receipt.get("issued_at") or receipt.get("recorded_at")
        lines.append(
            "| {receipt_id} | {receipt_type} | {source_class} | {time} | {source} | {digest} |".format(
                receipt_id=_escape_markdown(receipt["receipt_id"]),
                receipt_type=_escape_markdown(receipt["receipt_type"]),
                source_class=_escape_markdown(receipt["source_class"]),
                time=_escape_markdown(evidence_time),
                source=_escape_markdown(receipt["source_locator"]),
                digest=_escape_markdown(receipt["digest"]),
            )
        )
    if not result["evidence_chain"]:
        lines.append("| none | — | — | — | — | — |")
    lines.extend(["", "## Honest unknowns", ""])
    if result["unknowns"]:
        lines.extend(f"- {unknown}" for unknown in result["unknowns"])
    else:
        lines.append("- None inside this frozen decision profile.")
    lines.extend(
        [
            "",
            f"Decision receipt: `{result['decision_digest']}`",
            "",
            "> Dry-run only: this receipt does not execute DNS changes or govern a session that bypasses the gate.",
            "",
        ]
    )
    return "\n".join(lines)
