from __future__ import annotations

ALLOWED_RELATION_TYPES = {
    "supersedes",
    "narrows_scope",
    "contradicts",
    "transfers_authority",
}
CONFIDENCE_THRESHOLD = 0.60


def _norm(value: str) -> str:
    return " ".join(value.lower().split())


def _contains_span(text: str, span: str) -> bool:
    normalized_span = _norm(span)
    if not normalized_span:
        return False
    return normalized_span in _norm(text)


def _proposal_confidence(proposal: dict) -> float | None:
    confidence = proposal.get("confidence")
    if not isinstance(confidence, int | float):
        return None
    return float(confidence)


def _scope_overlaps(source_text: str, target_text: str, scope_terms: list[str]) -> bool:
    if not scope_terms:
        return False
    source = _norm(source_text)
    target = _norm(target_text)
    return any(_norm(term) in source and _norm(term) in target for term in scope_terms)


def confirm_authority_change(proposal: dict, items: list[dict]) -> dict:
    """Confirm an LLM-proposed authority-change relation against deterministic evidence.

    The proposer may interpret. This confirmer only checks local file evidence:
    valid item IDs, allowed relation type, a non-empty cited evidence span present
    in the source item, enough confidence for v0 routing, and at least one
    overlapping scope term across source and target. Anything that fails becomes
    needs_human_judgment, not a finding.
    """
    items_by_id = {item["id"]: item for item in items}
    source = items_by_id.get(proposal.get("source_item_id"))
    target = items_by_id.get(proposal.get("target_item_id"))
    relation_type = proposal.get("type")
    confidence = _proposal_confidence(proposal)

    reasons: list[str] = []
    if relation_type not in ALLOWED_RELATION_TYPES:
        reasons.append("unsupported relation type")
    if source is None:
        reasons.append("source item does not exist")
    if target is None:
        reasons.append("target item does not exist")
    if confidence is None:
        reasons.append("missing or invalid confidence")
    elif confidence < CONFIDENCE_THRESHOLD:
        reasons.append("confidence below v0 threshold")

    if reasons:
        return {
            "confirmed": False,
            "needs_human_judgment": True,
            "reasons": reasons,
            "proposal": proposal,
        }

    cited_evidence_span = proposal.get("cited_evidence_span", "")
    scope_terms = proposal.get("scope_terms", [])

    if not _contains_span(source["text"], cited_evidence_span):
        reasons.append("missing or empty evidence citation")
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
                "cited_evidence_span": cited_evidence_span,
                "evidence": source["text"],
                "target": target["text"],
                "scope_terms": scope_terms,
                "confidence": confidence,
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
