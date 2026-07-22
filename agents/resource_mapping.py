from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any

from agents.anchor_contract import content_digest


ASSERTION_REQUIRED_FIELDS = (
    "schema",
    "mapping_kind",
    "source_namespace",
    "source_resource_id",
    "canonical_namespace",
    "canonical_resource_id",
    "authority_scope",
)
GRANT_REQUIRED_FIELDS = (
    "grant_id",
    "grantor_id",
    "grantee_id",
    "source_namespace",
    "canonical_namespace",
    "allowed_mapping_kinds",
    "authority_scope",
    "effective_at",
    "expires_at",
    "revoked_at",
    "grant_digest",
)
MAPPING_RECEIPT_REQUIRED_FIELDS = (
    "receipt_id",
    "issuer_id",
    "issued_at",
    "effective_at",
    "expires_at",
    "assertion",
    "assertion_digest",
    "authority_grant_id",
    "evidence_receipt_ids",
    "receipt_digest",
)
REVOCATION_REQUIRED_FIELDS = (
    "revocation_id",
    "mapping_receipt_id",
    "issuer_id",
    "revoked_at",
    "authority_grant_id",
    "reason_code",
    "revocation_digest",
)
REQUEST_REQUIRED_FIELDS = (
    "source_namespace",
    "source_resource_id",
    "required_canonical_namespace",
    "authority_scope",
    "subject_time",
    "resolution_time",
    "direction",
)
POLICY_REQUIRED_FIELDS = (
    "policy_id",
    "policy_version",
    "trusted_grantor_ids",
    "allowed_mapping_kinds",
    "resolution_rule",
    "unresolved_states",
    "policy_digest",
)


def canonical_mapping_assertion(assertion: dict) -> dict[str, Any]:
    missing = [field for field in ASSERTION_REQUIRED_FIELDS if field not in assertion]
    if missing:
        raise ValueError(f"mapping assertion missing required fields: {missing}")
    return {field: assertion[field] for field in ASSERTION_REQUIRED_FIELDS}


def mapping_key(assertion: dict) -> str:
    return "mapping:v0:" + content_digest(canonical_mapping_assertion(assertion))


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def _empty_result(case: dict) -> dict[str, Any]:
    return {
        "case_id": case["id"],
        "alarm_code": None,
        "resolution_state": "unresolved",
        "mapping_key": None,
        "source_namespace": None,
        "source_resource_id": None,
        "canonical_namespace": None,
        "canonical_resource_id": None,
        "authority_scope": None,
        "subject_time": None,
        "resolution_time": None,
        "mapping_receipt_id": None,
        "authority_grant_id": None,
        "census_receipt_id": None,
        "supporting_mapping_receipt_ids": [],
        "duplicate_replay_receipt_ids": [],
        "unresolved_reasons": [],
        "receipts": {
            "candidate_receipt_count": 0,
            "active_mapping_count": 0,
            "duplicate_replay_count": 0,
        },
    }


def _fail(result: dict, alarm_code: str, reason: str) -> dict:
    result["alarm_code"] = alarm_code
    result["resolution_state"] = "unresolved"
    result["mapping_key"] = None
    result["canonical_namespace"] = None
    result["canonical_resource_id"] = None
    result["mapping_receipt_id"] = None
    result["authority_grant_id"] = None
    result["unresolved_reasons"] = [reason]
    return result


def _resolve_shared(packet: dict, ref: Any) -> dict | None:
    if not isinstance(ref, str):
        return None
    value = packet.get("shared_objects", {}).get(ref)
    return deepcopy(value) if isinstance(value, dict) else None


def _resolve_single(case: dict, kind: str, packet: dict) -> dict | None:
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


def _resolve_rows(case: dict, packet: dict, *, plural: str, ref_key: str, override_key: str) -> list[dict]:
    rows: list[dict] = []
    direct_rows = case.get(plural)
    if isinstance(direct_rows, list):
        for row in direct_rows:
            if not isinstance(row, dict):
                rows.append({})
                continue
            if ref_key in row:
                resolved = _resolve_shared(packet, row.get(ref_key)) or {}
                overrides = row.get(override_key) or {}
                if isinstance(overrides, dict):
                    resolved.update(deepcopy(overrides))
                rows.append(resolved)
            else:
                rows.append(deepcopy(row))
        return rows

    refs = case.get(f"{plural[:-1]}_refs")
    if not isinstance(refs, list):
        refs = case.get(f"{plural}_refs")
    if isinstance(refs, list):
        return [_resolve_shared(packet, ref) or {} for ref in refs]
    return []


def _mapping_receipts(case: dict, packet: dict) -> list[dict]:
    direct = case.get("mapping_receipts")
    if isinstance(direct, list):
        return _resolve_rows(
            case,
            packet,
            plural="mapping_receipts",
            ref_key="receipt_ref",
            override_key="receipt_overrides",
        )
    refs = case.get("mapping_receipt_refs")
    return [_resolve_shared(packet, ref) or {} for ref in refs] if isinstance(refs, list) else []


def _authority_grants(case: dict, packet: dict) -> list[dict]:
    direct = case.get("authority_grants")
    if isinstance(direct, list):
        return _resolve_rows(
            case,
            packet,
            plural="authority_grants",
            ref_key="grant_ref",
            override_key="grant_overrides",
        )
    refs = case.get("authority_grant_refs")
    return [_resolve_shared(packet, ref) or {} for ref in refs] if isinstance(refs, list) else []


def _revocations(case: dict, packet: dict) -> list[dict]:
    refs = case.get("revocation_receipt_refs")
    if isinstance(refs, list):
        return [_resolve_shared(packet, ref) or {} for ref in refs]
    rows = case.get("revocation_receipts")
    return deepcopy(rows) if isinstance(rows, list) else []


def _validate_policy(result: dict, policy: dict) -> dict | None:
    missing = [field for field in POLICY_REQUIRED_FIELDS if field not in policy]
    if missing:
        return _fail(result, "mapping_policy_integrity_failure", "mapping policy is incomplete")
    payload = {key: value for key, value in policy.items() if key != "policy_digest"}
    if content_digest(payload) != policy.get("policy_digest"):
        return _fail(result, "mapping_policy_integrity_failure", "mapping policy does not match its digest")
    if not isinstance(policy.get("trusted_grantor_ids"), list) or not policy["trusted_grantor_ids"]:
        return _fail(result, "mapping_policy_integrity_failure", "mapping policy has no configured trust root")
    if not isinstance(policy.get("allowed_mapping_kinds"), list) or not policy["allowed_mapping_kinds"]:
        return _fail(result, "mapping_policy_integrity_failure", "mapping policy admits no mapping kind")
    if not all(isinstance(value, str) and value for value in policy["trusted_grantor_ids"]):
        return _fail(result, "mapping_policy_integrity_failure", "mapping policy trust roots are untyped")
    if not all(isinstance(value, str) and value for value in policy["allowed_mapping_kinds"]):
        return _fail(result, "mapping_policy_integrity_failure", "mapping policy mapping kinds are untyped")
    return None


def _validate_request(result: dict, request: dict | None) -> tuple[datetime, datetime] | dict:
    if not isinstance(request, dict):
        return _fail(result, "mapping_request_schema_failure", "mapping request is missing")
    missing = [field for field in REQUEST_REQUIRED_FIELDS if field not in request]
    if missing or not all(isinstance(request.get(field), str) and request[field] for field in REQUEST_REQUIRED_FIELDS):
        return _fail(result, "mapping_request_schema_failure", "mapping request is incomplete or untyped")

    result["source_namespace"] = request["source_namespace"]
    result["source_resource_id"] = request["source_resource_id"]
    result["authority_scope"] = request["authority_scope"]
    result["subject_time"] = request["subject_time"]
    result["resolution_time"] = request["resolution_time"]

    subject_time = _parse_time(request["subject_time"])
    resolution_time = _parse_time(request["resolution_time"])
    if subject_time is None or resolution_time is None or subject_time > resolution_time:
        return _fail(result, "mapping_request_schema_failure", "mapping request clocks are invalid")
    if request["direction"] != "source_to_canonical":
        return _fail(result, "mapping_direction_failure", "v0 mappings resolve source to canonical only")
    return subject_time, resolution_time


def _validate_census(result: dict, census: dict | None, request: dict, resolution_time: datetime) -> dict | None:
    required = (
        "receipt_id",
        "observer_id",
        "observed_at",
        "authority_namespace",
        "resources",
        "resource_aliases",
        "census_digest",
    )
    if not isinstance(census, dict) or any(field not in census for field in required):
        return _fail(result, "mapping_census_integrity_failure", "bound census is missing or incomplete")
    resources = census.get("resources")
    if not isinstance(resources, list) or not all(isinstance(resource, dict) for resource in resources):
        return _fail(result, "mapping_census_integrity_failure", "census resources are not typed objects")
    if not isinstance(census.get("resource_aliases"), list):
        return _fail(result, "mapping_census_integrity_failure", "census resource aliases are not a list")
    payload = {"authority_namespace": census["authority_namespace"], "resources": resources}
    if content_digest(payload) != census.get("census_digest"):
        return _fail(result, "mapping_census_integrity_failure", "bound census does not match its digest")
    resource_ids = [resource.get("resource_id") for resource in resources]
    if any(
        not all(isinstance(resource.get(field), str) and resource[field] for field in ("resource_id", "scope", "status"))
        for resource in resources
    ) or len(resource_ids) != len(set(resource_ids)):
        return _fail(result, "mapping_census_integrity_failure", "census resource identities are invalid or duplicated")
    observed_at = _parse_time(census.get("observed_at"))
    if observed_at is None or observed_at > resolution_time:
        return _fail(result, "mapping_census_integrity_failure", "census timing is invalid for this resolution")
    required_namespace = f"{request['required_canonical_namespace']}/{request['authority_scope']}"
    if census["authority_namespace"] != required_namespace:
        return _fail(result, "mapping_scope_failure", "request scope and bound census namespace differ")
    result["census_receipt_id"] = census["receipt_id"]
    return None


def _validate_mapping_receipt(result: dict, receipt: dict, policy: dict) -> dict | None:
    if any(field not in receipt for field in MAPPING_RECEIPT_REQUIRED_FIELDS):
        return _fail(result, "mapping_receipt_integrity_failure", "mapping receipt is incomplete")
    assertion = receipt.get("assertion")
    if not isinstance(assertion, dict) or any(field not in assertion for field in ASSERTION_REQUIRED_FIELDS):
        return _fail(result, "mapping_receipt_integrity_failure", "mapping assertion is incomplete")
    if set(assertion) != set(ASSERTION_REQUIRED_FIELDS) or not all(
        isinstance(assertion.get(field), str) and assertion[field] for field in ASSERTION_REQUIRED_FIELDS
    ):
        return _fail(result, "mapping_receipt_integrity_failure", "mapping assertion fields are not exact typed v0 semantics")
    for field in ("receipt_id", "issuer_id", "issued_at", "effective_at", "expires_at", "authority_grant_id"):
        if not isinstance(receipt.get(field), str) or not receipt[field]:
            return _fail(result, "mapping_receipt_integrity_failure", "mapping receipt identity or clocks are untyped")
    if assertion.get("schema") != "resource_mapping/v0":
        return _fail(result, "mapping_receipt_integrity_failure", "mapping assertion schema is outside v0")
    if assertion.get("mapping_kind") not in policy["allowed_mapping_kinds"]:
        return _fail(result, "mapping_receipt_integrity_failure", "mapping kind is not admitted by policy")
    if content_digest(canonical_mapping_assertion(assertion)) != receipt.get("assertion_digest"):
        return _fail(result, "mapping_receipt_integrity_failure", "mapping assertion does not match its digest")
    payload = {key: value for key, value in receipt.items() if key != "receipt_digest"}
    if content_digest(payload) != receipt.get("receipt_digest"):
        return _fail(result, "mapping_receipt_integrity_failure", "mapping receipt does not match its digest")
    if not isinstance(receipt.get("evidence_receipt_ids"), list) or not all(
        isinstance(value, str) and value for value in receipt["evidence_receipt_ids"]
    ):
        return _fail(result, "mapping_receipt_integrity_failure", "mapping evidence receipt IDs are untyped")
    issued_at = _parse_time(receipt.get("issued_at"))
    effective_at = _parse_time(receipt.get("effective_at"))
    expires_at = _parse_time(receipt.get("expires_at"))
    if not issued_at or not effective_at or not expires_at or effective_at < issued_at or effective_at >= expires_at:
        return _fail(result, "mapping_receipt_integrity_failure", "mapping receipt validity interval is invalid")
    return None


def _deduplicate_receipts(result: dict, receipts: list[dict]) -> tuple[list[dict], dict | None]:
    unique: list[dict] = []
    seen: dict[str, str] = {}
    for receipt in receipts:
        receipt_id = receipt["receipt_id"]
        signature = content_digest(receipt)
        prior = seen.get(receipt_id)
        if prior is None:
            seen[receipt_id] = signature
            unique.append(receipt)
        elif prior == signature:
            result["receipts"]["duplicate_replay_count"] += 1
            result["duplicate_replay_receipt_ids"].append(receipt_id)
        else:
            return [], _fail(
                result,
                "mapping_receipt_identity_conflict",
                "one mapping receipt ID carries conflicting canonical receipt bytes",
            )
    return unique, None


def _validate_grant(
    result: dict,
    grant: dict | None,
    receipt: dict,
    assertion: dict,
    policy: dict,
) -> dict | None:
    if not isinstance(grant, dict) or any(field not in grant for field in GRANT_REQUIRED_FIELDS):
        return _fail(result, "mapping_authority_failure", "named mapping authority grant is missing or incomplete")
    payload = {key: value for key, value in grant.items() if key != "grant_digest"}
    if content_digest(payload) != grant.get("grant_digest"):
        return _fail(result, "mapping_grant_integrity_failure", "mapping authority grant does not match its digest")
    string_fields = (
        "grant_id",
        "grantor_id",
        "grantee_id",
        "source_namespace",
        "canonical_namespace",
        "authority_scope",
        "effective_at",
        "expires_at",
    )
    if any(not isinstance(grant.get(field), str) or not grant[field] for field in string_fields):
        return _fail(result, "mapping_grant_integrity_failure", "mapping authority grant fields are untyped")
    if not isinstance(grant.get("allowed_mapping_kinds"), list) or not all(
        isinstance(value, str) and value for value in grant["allowed_mapping_kinds"]
    ):
        return _fail(result, "mapping_grant_integrity_failure", "mapping authority grant kinds are untyped")
    if grant.get("grantor_id") not in policy["trusted_grantor_ids"]:
        return _fail(result, "mapping_authority_failure", "mapping grantor is outside the configured trust roots")
    if grant.get("grantee_id") != receipt.get("issuer_id"):
        return _fail(result, "mapping_authority_failure", "mapping receipt issuer is not the authorized grantee")
    dimensions_match = (
        grant.get("source_namespace") == assertion.get("source_namespace")
        and grant.get("canonical_namespace") == assertion.get("canonical_namespace")
        and assertion.get("mapping_kind") in grant.get("allowed_mapping_kinds", [])
        and grant.get("authority_scope") == assertion.get("authority_scope")
    )
    if not dimensions_match:
        return _fail(result, "mapping_authority_failure", "mapping assertion exceeds its exact authority grant")

    issued_at = _parse_time(receipt.get("issued_at"))
    receipt_expires = _parse_time(receipt.get("expires_at"))
    grant_effective = _parse_time(grant.get("effective_at"))
    grant_expires = _parse_time(grant.get("expires_at"))
    grant_revoked = _parse_time(grant.get("revoked_at")) if grant.get("revoked_at") is not None else None
    if not issued_at or not receipt_expires or not grant_effective or not grant_expires or grant_effective >= grant_expires:
        return _fail(result, "mapping_authority_failure", "mapping authority grant timing is invalid")
    if issued_at < grant_effective or issued_at >= grant_expires or receipt_expires > grant_expires:
        return _fail(result, "mapping_authority_failure", "mapping receipt falls outside the authority grant window")
    if grant_revoked is not None and grant_revoked <= issued_at:
        return _fail(result, "mapping_authority_failure", "mapping authority grant was revoked before issuance")
    return None


def _validate_revocations(
    result: dict,
    revocations: list[dict],
    receipt: dict,
    grant: dict,
    resolution_time: datetime,
) -> dict | None:
    for revocation in revocations:
        if not isinstance(revocation, dict) or revocation.get("mapping_receipt_id") != receipt.get("receipt_id"):
            continue
        if any(field not in revocation for field in REVOCATION_REQUIRED_FIELDS):
            return _fail(result, "mapping_revocation_integrity_failure", "mapping revocation receipt is incomplete")
        payload = {key: value for key, value in revocation.items() if key != "revocation_digest"}
        if content_digest(payload) != revocation.get("revocation_digest"):
            return _fail(result, "mapping_revocation_integrity_failure", "mapping revocation does not match its digest")
        if revocation.get("authority_grant_id") != grant.get("grant_id") or revocation.get("issuer_id") not in {
            receipt.get("issuer_id"),
            grant.get("grantor_id"),
        }:
            return _fail(result, "mapping_revocation_authority_failure", "mapping revocation lacks authority")
        if not isinstance(revocation.get("reason_code"), str) or not revocation["reason_code"]:
            return _fail(result, "mapping_revocation_integrity_failure", "mapping revocation reason is untyped")
        revoked_at = _parse_time(revocation.get("revoked_at"))
        if revoked_at is None:
            return _fail(result, "mapping_revocation_integrity_failure", "mapping revocation time is invalid")
        if revoked_at <= resolution_time:
            return _fail(result, "mapping_revoked", "mapping receipt was revoked by resolution time")
    return None


def evaluate_resource_mapping_case(case: dict, packet: dict) -> dict[str, Any]:
    result = _empty_result(case)
    policy = packet.get("mapping_policy") or {}
    failure = _validate_policy(result, policy)
    if failure:
        return failure

    request = _resolve_single(case, "request", packet)
    request_times = _validate_request(result, request)
    if isinstance(request_times, dict):
        return request_times
    subject_time, resolution_time = request_times

    census = _resolve_single(case, "census", packet)
    failure = _validate_census(result, census, request, resolution_time)
    if failure:
        return failure

    receipts = _mapping_receipts(case, packet)
    if not receipts:
        return _fail(result, "resource_identity_unresolved", "no mapping receipt was supplied")
    for receipt in receipts:
        failure = _validate_mapping_receipt(result, receipt, policy)
        if failure:
            return failure
    receipts, failure = _deduplicate_receipts(result, receipts)
    if failure:
        return failure

    candidates = [
        receipt
        for receipt in receipts
        if receipt["assertion"].get("source_namespace") == request["source_namespace"]
        and receipt["assertion"].get("source_resource_id") == request["source_resource_id"]
    ]
    result["receipts"]["candidate_receipt_count"] = len(candidates)
    if not candidates:
        return _fail(result, "resource_identity_unresolved", "no mapping receipt matches the requested source identity")

    grants = _authority_grants(case, packet)
    grants_by_id: dict[str, dict] = {}
    for grant in grants:
        grant_id = grant.get("grant_id")
        if not isinstance(grant_id, str) or grant_id in grants_by_id:
            return _fail(result, "mapping_authority_failure", "authority grant identities are missing or duplicated")
        grants_by_id[grant_id] = grant
    revocations = _revocations(case, packet)

    active: list[tuple[dict, dict]] = []
    for receipt in candidates:
        assertion = receipt["assertion"]
        if assertion.get("authority_scope") != request["authority_scope"]:
            return _fail(result, "mapping_scope_failure", "mapping assertion scope differs from the resolution request")
        if assertion.get("canonical_namespace") != request["required_canonical_namespace"]:
            return _fail(result, "mapping_namespace_failure", "mapping canonical namespace differs from the request")

        grant = grants_by_id.get(receipt.get("authority_grant_id"))
        failure = _validate_grant(result, grant, receipt, assertion, policy)
        if failure:
            return failure

        issued_at = _parse_time(receipt["issued_at"])
        effective_at = _parse_time(receipt["effective_at"])
        expires_at = _parse_time(receipt["expires_at"])
        if issued_at > subject_time or effective_at > subject_time:
            return _fail(result, "mapping_not_effective", "mapping was not issued and effective at subject time")
        if expires_at <= subject_time:
            return _fail(result, "mapping_expired", "mapping expired before subject time")
        failure = _validate_revocations(result, revocations, receipt, grant, resolution_time)
        if failure:
            return failure
        active.append((receipt, grant))

    result["receipts"]["active_mapping_count"] = len(active)
    if not active:
        return _fail(result, "resource_identity_unresolved", "no active mapping remains")

    if any(
        receipt["assertion"]["canonical_namespace"] == receipt["assertion"]["source_namespace"]
        for receipt, _grant in active
    ):
        return _fail(result, "mapping_target_not_canonical", "v0 refuses alias-to-alias mapping chains or cycles")

    target_pairs = {
        (receipt["assertion"]["canonical_namespace"], receipt["assertion"]["canonical_resource_id"])
        for receipt, _grant in active
    }
    if len(target_pairs) != 1:
        return _fail(result, "mapping_conflict", "active mapping receipts disagree on the canonical target")

    selected_receipt, selected_grant = sorted(
        active,
        key=lambda row: (row[0]["issued_at"], row[0]["receipt_id"]),
    )[0]
    assertion = selected_receipt["assertion"]
    census_targets = {
        resource["resource_id"]
        for resource in census["resources"]
        if resource["scope"] == request["authority_scope"]
    }
    if assertion["canonical_resource_id"] not in census_targets:
        return _fail(result, "mapping_target_unbound", "canonical mapping target is absent from the bound census")

    result.update(
        {
            "alarm_code": None,
            "resolution_state": "resolved",
            "mapping_key": mapping_key(assertion),
            "canonical_namespace": assertion["canonical_namespace"],
            "canonical_resource_id": assertion["canonical_resource_id"],
            "mapping_receipt_id": selected_receipt["receipt_id"],
            "authority_grant_id": selected_grant["grant_id"],
            "supporting_mapping_receipt_ids": sorted(receipt["receipt_id"] for receipt, _grant in active),
            "unresolved_reasons": [],
        }
    )
    return result
