from __future__ import annotations

ALLOWED_RELATION_TYPES = {
    "supersedes",
    "narrows_scope",
    "contradicts",
    "transfers_authority",
}


def _norm(value: str) -> str:
    return " ".join(value.lower().split())


def _contains_all(text: str, terms: list[str]) -> bool:
    haystack = _norm(text)
    return all(_norm(term) in haystack for term in terms)


def _scope_overlaps(source_text: str, target_text: str, scope_terms: list[str]) -> bool:
    if not scope_terms:
        return False
    source = _norm(source_text)
    target = _norm(target_text)
    return any(_norm(term) in source and _norm(term) in target for term in scope_terms)


def confirm_authority_change(proposal: dict, items: list[dict]) -> dict:
    """Confirm an LLM-proposed authority-change relation against deterministic evidence.

    The proposer may interpret. This confirmer only checks local file evidence:
    valid item IDs, allowed relation type, evidence terms present in the source item,
    and at least one overlapping scope term across source and target. Anything that
    fails becomes needs_human_judgment, not a finding.
    """
    items_by_id = {item["id"]: item for item in items}
    source = items_by_id.get(proposal.get("source_item_id"))
    target = items_by_id.get(proposal.get("target_item_id"))
    relation_type = proposal.get("type")

    reasons: list[str] = []
    if relation_type not in ALLOWED_RELATION_TYPES:
        reasons.append("unsupported relation type")
    if source is None:
        reasons.append("source item does not exist")
    if target is None:
        reasons.append("target item does not exist")

    if reasons:
        return {
            "confirmed": False,
            "needs_human_judgment": True,
            "reasons": reasons,
            "proposal": proposal,
        }

    evidence_terms = proposal.get("required_evidence_terms", [])
    scope_terms = proposal.get("scope_terms", [])

    if not _contains_all(source["text"], evidence_terms):
        reasons.append("required evidence terms not found in source item")
    if not _scope_overlaps(source["text"], target["text"], scope_terms):
        reasons.append("no deterministic scope overlap between source and target")

    confirmed = not reasons
    return {
        "confirmed": confirmed,
        "needs_human_judgment": not confirmed,
        "reasons": reasons,
        "finding": (
            {
                "type": "semantic_authority_change",
                "relation_type": relation_type,
                "source_item_id": source["id"],
                "target_item_id": target["id"],
                "evidence": source["text"],
                "target": target["text"],
                "scope_terms": scope_terms,
            }
            if confirmed
            else None
        ),
        "proposal": proposal,
    }


def confirm_authority_changes(proposals: list[dict], items: list[dict]) -> dict:
    confirmed = []
    needs_human_judgment = []
    for proposal in proposals:
        result = confirm_authority_change(proposal, items)
        if result["confirmed"]:
            confirmed.append(result["finding"])
        else:
            needs_human_judgment.append({
                "proposal": proposal,
                "reasons": result["reasons"],
            })
    return {
        "findings": confirmed,
        "needs_human_judgment": needs_human_judgment,
    }
