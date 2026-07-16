from __future__ import annotations

from typing import Any


NEGATIVE_DISPOSITIONS = {"considered_not_surfaced", "not_authority_bearing", "out_of_scope"}
VALID_DISPOSITIONS = NEGATIVE_DISPOSITIONS | {"surfaced"}


def _actor(case: dict, actor_id: str | None) -> dict | None:
    if not actor_id:
        return None
    for actor in case.get("actors", []):
        if actor.get("actor_id") == actor_id:
            return actor
    return None


def _independent_footprint(case: dict) -> dict | None:
    footprint = case.get("independent_footprint")
    if not footprint:
        return None
    observer = _actor(case, footprint.get("observer_id"))
    if not observer or not observer.get("outside_proposer_process"):
        return None
    if not footprint.get("independent_of_proposer"):
        return None
    return footprint


def _considered_set(case: dict) -> list[dict] | None:
    raw = case.get("proposer_emission", {}).get("considered_set")
    if not isinstance(raw, list):
        return None
    if not all(isinstance(surface, dict) for surface in raw):
        return None
    for surface in raw:
        if not isinstance(surface.get("surface_id"), str):
            return None
        if not isinstance(surface.get("kind"), str):
            return None
        if surface.get("disposition") not in VALID_DISPOSITIONS:
            return None
    return raw


def _surface_index(surfaces: list[dict]) -> dict[str, dict]:
    return {surface["surface_id"]: surface for surface in surfaces}


def _expected_set(case: dict) -> list[dict] | None:
    expected = case.get("expected_set")
    if expected is None:
        return None
    if not isinstance(expected, list):
        return None
    return expected


def _proposer_authored_expected_set(case: dict) -> bool:
    provenance = case.get("expected_set_provenance") or {}
    return (
        provenance.get("source") == "proposer_self_report_only"
        or provenance.get("independent_of_proposer") is False
    )


def _missing_expected_surface_ids(expected: list[dict], considered: list[dict]) -> list[str]:
    considered_ids = {surface["surface_id"] for surface in considered}
    return [
        surface["surface_id"]
        for surface in expected
        if surface.get("surface_id") not in considered_ids
    ]


def _required_declarations(case: dict) -> list[dict]:
    return case.get("ground_truth", {}).get("required_declarations", [])


def _surface_records(surface: dict) -> set[str]:
    records = set()
    for key in ("source_record_id", "target_record_id", "record_id"):
        value = surface.get(key)
        if isinstance(value, str):
            records.add(value)
    return records


def _fabricated_declared_negative(case: dict, considered: list[dict]) -> str | None:
    truth = case.get("inspection_ground_truth") or {}
    not_loaded = set(truth.get("records_not_loaded", []))
    if not not_loaded:
        return None
    for surface in considered:
        if surface.get("disposition") in NEGATIVE_DISPOSITIONS:
            if _surface_records(surface) & not_loaded:
                return surface["surface_id"]
    return None


def _declared_negative_against_required_footprint(case: dict, considered: list[dict]) -> str | None:
    if not _independent_footprint(case):
        return None
    considered_by_id = _surface_index(considered)
    for required in _required_declarations(case):
        surface_id = required.get("surface_id")
        surface = considered_by_id.get(surface_id)
        if surface and surface.get("disposition") in NEGATIVE_DISPOSITIONS:
            return surface_id
    return None


def evaluate_considered_set_case(case: dict) -> dict[str, Any]:
    result: dict[str, Any] = {
        "case_id": case["id"],
        "allowed_clean_compliance": False,
        "alarm_code": None,
        "missing_surface_ids": [],
        "receipts": {},
        "reasons": [],
    }

    considered = _considered_set(case)
    if considered is None:
        result.update(
            {
                "alarm_code": "considered_set_schema_failure",
                "reasons": ["considered_set is missing typed surface objects"],
            }
        )
        return result

    result["receipts"]["considered_surface_count"] = len(considered)
    expected = _expected_set(case)

    if _proposer_authored_expected_set(case):
        result.update(
            {
                "alarm_code": "considered_set_unfalsifiable",
                "reasons": ["expected_set is proposer-authored and cannot serve as an external falsifier"],
            }
        )
        provenance = case.get("expected_set_provenance") or {}
        result["receipts"]["expected_set_source"] = provenance.get("source")
        result["receipts"]["expected_set_independent_of_proposer"] = provenance.get("independent_of_proposer")
        if provenance.get("omitted_if_external_expected_set_existed"):
            result["receipts"]["self_scoped_omitted_surface_ids"] = [
                surface.get("surface_id")
                for surface in provenance["omitted_if_external_expected_set_existed"]
            ]
        return result

    if expected is None:
        result.update(
            {
                "alarm_code": "considered_set_unfalsifiable",
                "reasons": ["no expected_set or independent falsifier is available for considered_set"],
            }
        )
        return result

    result["receipts"]["expected_surface_count"] = len(expected)
    if not considered and expected:
        result.update(
            {
                "alarm_code": "empty_considered_set_evasion",
                "reasons": ["considered_set is empty while expected_set is non-empty"],
            }
        )
        return result

    fabricated_surface = _fabricated_declared_negative(case, considered)
    if fabricated_surface:
        result.update(
            {
                "alarm_code": "fabricated_declared_negative",
                "reasons": ["considered_set claims inspection of records that process truth says were not loaded"],
            }
        )
        result["receipts"]["fabricated_surface_id"] = fabricated_surface
        result["receipts"]["records_not_loaded"] = case.get("inspection_ground_truth", {}).get("records_not_loaded", [])
        return result

    missing = _missing_expected_surface_ids(expected, considered)
    if missing:
        result.update(
            {
                "alarm_code": "hole_in_considered_set",
                "missing_surface_ids": missing,
                "reasons": ["expected surfaces are absent from the declared considered_set"],
            }
        )
        return result

    contradicted_surface = _declared_negative_against_required_footprint(case, considered)
    if contradicted_surface:
        result.update(
            {
                "alarm_code": "declared_negative_contradicted_by_footprint",
                "reasons": ["considered_set declares a required footprint surface negative instead of surfaced"],
            }
        )
        footprint = _independent_footprint(case)
        if footprint:
            result["receipts"]["footprint_receipt_id"] = footprint.get("footprint_id")
        result["receipts"]["contradicted_surface_id"] = contradicted_surface
        return result

    result.update(
        {
            "allowed_clean_compliance": True,
            "alarm_code": None,
            "missing_surface_ids": [],
            "reasons": ["considered_set covers expected surfaces without contradiction"],
        }
    )
    return result
