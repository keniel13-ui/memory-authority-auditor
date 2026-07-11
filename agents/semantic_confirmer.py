from __future__ import annotations

import re

ALLOWED_RELATION_TYPES = {
    "supersedes",
    "narrows_scope",
    "contradicts",
    "transfers_authority",
}
CONFIDENCE_THRESHOLD = 0.60
RELATION_SPAN_LEXICON = (
    "replace",
    "replaced",
    "replaces",
    "retire",
    "retired",
    "retires",
    "deprecate",
    "deprecated",
    "supersede",
    "supersedes",
    "superseded",
    "override",
    "overrides",
    "overridden",
    "discontinue",
    "discontinued",
    "revoke",
    "revoked",
    "no longer",
    "instead",
    "only",
    "now",
)


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


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _operator_pattern(operator: str) -> re.Pattern[str]:
    escaped = r"\s+".join(re.escape(part) for part in operator.split())
    return re.compile(rf"(?<!\w){escaped}(?!\w)", flags=re.IGNORECASE)


def _operators_in(text: str) -> list[str]:
    return [op for op in RELATION_SPAN_LEXICON if _operator_pattern(op).search(text)]


def relation_span_check(cited_evidence_span: str, scope_terms: list[str]) -> dict:
    """v2 relation-span clause.

    This is a deterministic input gate, not a semantic judge. A span passes only
    when one sentence contains both a frozen relation operator and one proposed
    scope term. Anything else is routed away from confirmed textual findings.
    """
    operators = _operators_in(cited_evidence_span)
    if not operators:
        return {
            "passed": False,
            "operators": [],
            "matching_sentence": None,
            "reason": "no frozen relation operator in cited evidence span",
        }
    normalized_terms = [_norm(term) for term in scope_terms if _norm(term)]
    for sentence in _sentences(cited_evidence_span):
        normalized_sentence = _norm(sentence)
        sentence_operators = _operators_in(sentence)
        sentence_terms = [term for term in normalized_terms if term in normalized_sentence]
        if sentence_operators and sentence_terms:
            return {
                "passed": True,
                "operators": sentence_operators,
                "matching_sentence": sentence,
                "scope_terms_matched": sentence_terms,
                "reason": None,
            }
    return {
        "passed": False,
        "operators": operators,
        "matching_sentence": None,
        "reason": "operator and scope term do not co-occur in one cited sentence",
    }


def confirm_authority_change(proposal: dict, items: list[dict], *, require_relation_span: bool = False) -> dict:
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
    relation_span = None
    if require_relation_span:
        relation_span = relation_span_check(cited_evidence_span, scope_terms)
        if not relation_span["passed"]:
            reasons.append(f"relation-span clause failed: {relation_span['reason']}")

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
                "relation_span": relation_span,
            }
            if confirmed
            else None
        ),
        "proposal": proposal,
    }


def confirm_authority_changes(
    proposals: list[dict],
    items: list[dict],
    *,
    require_relation_span: bool = False,
) -> dict:
    confirmed = []
    needs_human_judgment = []
    for proposal in proposals:
        result = confirm_authority_change(proposal, items, require_relation_span=require_relation_span)
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
