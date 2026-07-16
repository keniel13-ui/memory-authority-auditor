from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


RETIRING_RELATION_TYPES = {"supersedes"}
EXTERNAL_AUTHORITY_CHANNELS = {"owner_console"}


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _index(rows: list[dict], key: str) -> dict[str, dict]:
    return {row[key]: row for row in rows if key in row}


def _actor(case: dict, actor_id: str | None) -> dict | None:
    if actor_id is None:
        return None
    return _index(case.get("actors", []), "actor_id").get(actor_id)


def _record(case: dict, record_id: str | None) -> dict | None:
    if record_id is None:
        return None
    return _index(case.get("records", []), "record_id").get(record_id)


def _requester_id(request: dict, fact: dict) -> str | None:
    return request.get("requester_id") or fact.get("asserted_by")


def _executor_id(request: dict, fact: dict) -> str | None:
    return request.get("executor_id") or request.get("actor_id") or fact.get("authenticated_by")


def _minted_at(request: dict, fact: dict) -> datetime | None:
    return _parse_time(request.get("minted_at") or fact.get("authenticated_at"))


def _roles(actor: dict | None) -> set[str]:
    return set((actor or {}).get("roles", []))


def _can_adjudicate(actor: dict | None) -> bool:
    return bool((actor or {}).get("can_adjudicate"))


def _capability_receipt(case: dict, receipt_id: str | None) -> dict | None:
    if not receipt_id:
        return None
    return _index(case.get("infrastructure_capability_receipts", []), "receipt_id").get(receipt_id)


def _valid_consent(
    case: dict,
    request: dict,
    fact: dict,
    requester_id: str | None,
) -> tuple[bool, dict | None, str | None, dict | None]:
    basis = fact.get("authority_basis") or {}
    if basis.get("kind") != "target_owner_consent":
        return False, None, None, None
    consent = _index(case.get("target_owner_consents", []), "consent_id").get(basis.get("ref"))
    target = _record(case, fact.get("target_record_id"))
    if not consent or not target:
        return False, consent, None, None
    if consent.get("owner_id") != target.get("owner_id"):
        return False, consent, None, None
    if "root_event_id" in consent:
        root_ok, root, root_alarm = _root_is_external(case, request, consent.get("root_event_id"))
        if not root_ok:
            return False, consent, root_alarm or "authority_root_not_external", root
    else:
        root = None
    grantee_ids = {value for value in (requester_id,) if value}
    if "requester_id" not in request and request.get("action") == "adjudicate_and_promote":
        grantee_ids.update(
            value
            for value in (_executor_id(request, fact), fact.get("asserted_by"), fact.get("authenticated_by"))
            if value
        )
    if consent.get("grantee_id") not in grantee_ids:
        return False, consent, "confused_deputy_retirement", root
    if consent.get("target_record_id") != fact.get("target_record_id"):
        return False, consent, None, root
    if consent.get("source_record_id") and consent.get("source_record_id") != fact.get("source_record_id"):
        return False, consent, None, root
    if consent.get("relation_type") != fact.get("relation_type"):
        return False, consent, None, root
    return True, consent, None, root


def _root_is_external(case: dict, request: dict, root_event_id: str | None) -> tuple[bool, dict | None, str | None]:
    if not root_event_id:
        return False, None, "authority_root_not_external"
    root = _index(case.get("authority_roots", []), "root_event_id").get(root_event_id)
    if not root:
        return False, None, "authority_root_not_external"
    if not root.get("resolves"):
        return False, root, "authority_root_not_external"
    if root.get("channel_id") not in EXTERNAL_AUTHORITY_CHANNELS:
        return False, root, "authority_root_not_external"
    if root.get("actor_id") not in root.get("channel_writable_by", []):
        return False, root, "authority_root_not_external"
    receipt = _capability_receipt(case, root.get("capability_receipt_id"))
    if receipt is not None:
        if not receipt.get("resolves"):
            return False, root, "authority_root_not_external"
        relation_component_id = request.get("relation_component_id")
        if relation_component_id in set(receipt.get("manifest_writable_by", [])):
            return False, root, "authority_channel_reachable_by_relation_writer"
        if relation_component_id in set(receipt.get("channel_write_principals", [])):
            return False, root, "authority_channel_reachable_by_relation_writer"
        if relation_component_id in set(receipt.get("signing_key_access_principals", [])):
            return False, root, "authority_channel_reachable_by_relation_writer"
    return True, root, None


def _valid_standing_rule(case: dict, request: dict, fact: dict, requester: dict | None) -> tuple[bool, dict | None, str | None]:
    basis = fact.get("authority_basis") or {}
    if basis.get("kind") != "standing_rule":
        return False, None, None
    rule = _index(case.get("standing_rules", []), "rule_id").get(basis.get("ref"))
    target = _record(case, fact.get("target_record_id"))
    if not rule or not target:
        return False, rule, None
    if rule.get("relation_type") != fact.get("relation_type"):
        return False, rule, None
    if rule.get("target_scope") != target.get("scope"):
        return False, rule, None
    if rule.get("grantee_role") not in _roles(requester):
        return False, rule, None
    if "requester_id" in request:
        has_exact_target = rule.get("target_record_id") == fact.get("target_record_id")
        has_exact_grantor = rule.get("grantor_id") == target.get("owner_id")
        has_external_root = bool(rule.get("root_event_id"))
        if not (has_exact_target and has_exact_grantor and has_external_root):
            return False, rule, "standing_rule_too_broad"
    return True, rule, None


def _valid_standing_grant(
    case: dict,
    request: dict,
    fact: dict,
    requester_id: str | None,
) -> tuple[bool, dict | None, str | None, dict | None]:
    basis = fact.get("authority_basis") or {}
    if basis.get("kind") != "standing_grant":
        return False, None, None, None
    grant = _index(case.get("standing_grants", []), "grant_id").get(basis.get("ref"))
    target = _record(case, fact.get("target_record_id"))
    if not grant or not target:
        return False, grant, None, None
    root_ok, root, root_alarm = _root_is_external(case, request, grant.get("root_event_id"))
    if not root_ok:
        return False, grant, root_alarm or "authority_root_not_external", root
    if grant.get("grantor_id") != target.get("owner_id"):
        return False, grant, None, root
    if grant.get("grantee_id") != requester_id:
        return False, grant, "confused_deputy_retirement", root
    if grant.get("target_record_id") != fact.get("target_record_id"):
        return False, grant, None, root
    if grant.get("relation_type") != fact.get("relation_type"):
        return False, grant, None, root
    minted = _minted_at(request, fact)
    expires = _parse_time(grant.get("expires_at"))
    if minted and expires and minted > expires:
        return False, grant, "retirement_grant_expired", root
    for revocation in case.get("revocations", []):
        if revocation.get("grant_id") != grant.get("grant_id"):
            continue
        revoked_at = _parse_time(revocation.get("revoked_at"))
        if minted and revoked_at and revoked_at <= minted:
            revoke_root = _index(case.get("authority_roots", []), "root_event_id").get(revocation.get("root_event_id"))
            return False, grant, "retirement_grant_revoked", revoke_root or root
    return True, grant, None, root


def _target_authority(case: dict, request: dict, fact: dict) -> dict:
    requester_id = _requester_id(request, fact)
    executor_id = _executor_id(request, fact)
    requester = _actor(case, requester_id)
    executor = _actor(case, executor_id)

    if fact.get("relation_type") not in RETIRING_RELATION_TYPES:
        return {"allowed": True, "authority_path": "non_retiring_relation"}

    consent_ok, consent, consent_alarm, consent_root = _valid_consent(case, request, fact, requester_id)
    if consent_ok:
        receipt = {"allowed": True, "authority_path": "target_owner_consent", "authority_receipt_id": consent["consent_id"]}
        if consent_root:
            receipt["root_receipt_id"] = consent_root.get("root_event_id")
            if consent_root.get("capability_receipt_id"):
                receipt["capability_receipt_id"] = consent_root.get("capability_receipt_id")
        return receipt
    if consent_alarm:
        receipt = {
            "allowed": False,
            "alarm_code": consent_alarm,
            "authority_path": "target_owner_consent",
            "authority_receipt_id": consent.get("consent_id") if consent else None,
        }
        if consent_root:
            receipt["root_receipt_id"] = consent_root.get("root_event_id")
            if consent_root.get("capability_receipt_id"):
                receipt["capability_receipt_id"] = consent_root.get("capability_receipt_id")
        return receipt

    rule_ok, rule, rule_alarm = _valid_standing_rule(case, request, fact, requester)
    if rule_ok:
        return {"allowed": True, "authority_path": "standing_rule", "authority_receipt_id": rule["rule_id"]}
    if rule_alarm:
        return {"allowed": False, "alarm_code": rule_alarm, "authority_path": "standing_rule"}

    grant_ok, grant, grant_alarm, root = _valid_standing_grant(case, request, fact, requester_id)
    if grant_ok:
        return {
            "allowed": True,
            "authority_path": "standing_grant",
            "authority_receipt_id": grant["grant_id"],
            "root_receipt_id": root.get("root_event_id") if root else grant.get("root_event_id"),
            "capability_receipt_id": root.get("capability_receipt_id") if root else None,
        }
    if grant_alarm:
        return {
            "allowed": False,
            "alarm_code": grant_alarm,
            "authority_path": "standing_grant",
            "authority_receipt_id": grant.get("grant_id") if grant else None,
            "root_receipt_id": root.get("root_event_id") if root else grant.get("root_event_id") if grant else None,
            "capability_receipt_id": root.get("capability_receipt_id") if root else None,
        }

    if executor_id and executor_id != requester_id and _can_adjudicate(executor):
        return {"allowed": False, "alarm_code": "target_retirement_unauthorized", "authority_path": "authenticated_without_target_authority"}
    return {"allowed": False, "alarm_code": "target_retirement_unauthorized", "authority_path": "none"}


def _claim(case: dict, claim_id: str | None) -> dict | None:
    if claim_id is None:
        return None
    return _index(case.get("tier2_claims", []), "claim_id").get(claim_id)


def _path(case: dict, path_id: str | None) -> dict | None:
    if path_id is None:
        return None
    return _index(case.get("provenance_paths", []), "path_id").get(path_id)


def _provenance_check(case: dict, fact: dict) -> dict:
    writer_path = _path(case, fact.get("writer_provenance_path_id"))
    arbiter_path = _path(case, fact.get("adjudicator_provenance_path_id"))
    if not writer_path and not arbiter_path:
        return {"allowed": True, "declared_shared_nodes": [], "provenance_path_ids": []}
    if not writer_path or not arbiter_path:
        return {"allowed": False, "alarm_code": "provenance_path_unresolved", "declared_shared_nodes": []}
    nodes = _index(case.get("provenance_nodes", []), "node_id")
    for node_id in writer_path.get("node_ids", []) + arbiter_path.get("node_ids", []):
        if not nodes.get(node_id, {}).get("resolves"):
            return {"allowed": False, "alarm_code": "provenance_path_unresolved", "declared_shared_nodes": []}
    shared = sorted(set(writer_path.get("node_ids", [])) & set(arbiter_path.get("node_ids", [])))
    if shared:
        return {
            "allowed": False,
            "alarm_code": "provenance_common_node",
            "declared_shared_nodes": shared,
            "provenance_path_ids": [writer_path["path_id"], arbiter_path["path_id"]],
        }
    result = {
        "allowed": True,
        "declared_shared_nodes": [],
        "provenance_path_ids": [writer_path["path_id"], arbiter_path["path_id"]],
    }
    if case.get("ground_truth_outside_candidate", {}).get("actual_shared_dependency"):
        result["ceiling_note"] = "declared disjointness did not reveal hidden common cause"
        result["actual_independence"] = False
    return result


def evaluate_store_request(case: dict) -> dict[str, Any]:
    request = case["request"]
    action = request["action"]
    fact = request.get("relation_fact_candidate")
    result: dict[str, Any] = {
        "case_id": case["id"],
        "action": action,
        "allowed": False,
        "resulting_tier": None,
        "alarm_code": None,
        "reasons": [],
        "receipts": {},
    }

    if action == "promote_claim" and fact is None:
        claim = _claim(case, request.get("claim_id"))
        result.update(
            {
                "allowed": False,
                "resulting_tier": claim.get("trust_tier") if claim else None,
                "alarm_code": "promotion_without_relation_fact",
                "reasons": ["tier-2 claim cannot become tier-1 without an authenticated relation fact"],
            }
        )
        return result

    if action == "governing_use":
        claim = _claim(case, request.get("claim_id"))
        if claim and claim.get("trust_tier") != "tier_1":
            result.update(
                {
                    "allowed": False,
                    "resulting_tier": claim.get("trust_tier"),
                    "alarm_code": "tier2_governing_use_blocked",
                    "reasons": ["governing consumers require tier-1 plus a resolvable authorized relation fact"],
                }
            )
            return result

    if fact is None:
        result.update({"alarm_code": "missing_relation_fact", "reasons": ["request has no relation fact candidate"]})
        return result

    if action == "adjudicate_and_promote":
        claim = _claim(case, request.get("claim_id"))
        executor = _actor(case, _executor_id(request, fact))
        if not _can_adjudicate(executor):
            result.update({"alarm_code": "adjudicator_not_authorized", "reasons": ["actor cannot adjudicate"]})
            return result
        if claim and fact.get("source_claim_id") != claim.get("claim_id"):
            result.update({"alarm_code": "promotion_claim_mismatch", "reasons": ["relation fact does not preserve source claim provenance"]})
            return result

    source = _record(case, fact.get("source_record_id"))
    target = _record(case, fact.get("target_record_id"))
    if not source or not target:
        result.update({"alarm_code": "record_pointer_unresolved", "reasons": ["source or target record does not resolve"]})
        return result

    authority = _target_authority(case, request, fact)
    result["receipts"].update({key: value for key, value in authority.items() if key.endswith("_id") or key == "authority_path"})
    if not authority["allowed"]:
        result.update(
            {
                "allowed": False,
                "resulting_tier": "tier_2" if action == "adjudicate_and_promote" else None,
                "alarm_code": authority.get("alarm_code") or "target_retirement_unauthorized",
                "reasons": [authority.get("alarm_code") or "target retirement authority did not resolve"],
            }
        )
        return result

    provenance = _provenance_check(case, fact)
    result["receipts"].update(
        {
            "declared_shared_nodes": provenance.get("declared_shared_nodes", []),
            "provenance_path_ids": provenance.get("provenance_path_ids", []),
        }
    )
    if "ceiling_note" in provenance:
        result["ceiling_note"] = provenance["ceiling_note"]
        result["actual_independence"] = provenance["actual_independence"]
    if not provenance["allowed"]:
        result.update(
            {
                "allowed": False,
                "resulting_tier": "tier_2" if action == "adjudicate_and_promote" else None,
                "alarm_code": provenance["alarm_code"],
                "reasons": [provenance["alarm_code"]],
            }
        )
        return result

    result.update(
        {
            "allowed": True,
            "resulting_tier": "tier_1",
            "alarm_code": None,
            "reasons": ["authorized relation fact may govern"],
            "relation_fact": fact,
        }
    )
    return result
