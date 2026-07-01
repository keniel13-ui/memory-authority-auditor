from __future__ import annotations

from collections import Counter

# Below this classifier confidence, the tool is not sure enough to stand behind the
# label on its own. Surfacing that (instead of hiding it under a posture) is the point:
# the auditor should shorten a careful human review, not replace it with a green check.
CONFIDENCE_FLOOR = 0.7


def _finding_item_ids(conflicts: list[dict]) -> set[str]:
    ids: set[str] = set()
    for conflict in conflicts:
        raw = conflict.get("item_id")
        if not raw:
            continue
        for part in str(raw).split(","):
            part = part.strip()
            if part:
                ids.add(part)
    return ids


def _review_priority(classification: dict, has_finding: bool) -> int:
    """Higher = a human should look at this sooner. Only items that carry authority
    weight enter the queue; uncertainty then AMPLIFIES that weight rather than
    manufacturing it, so a pile of low-confidence pure-context lines does not drown
    the signal (which would hide it, the opposite of the goal)."""
    score = 0
    if has_finding:
        score += 100
    if classification["risk"] == "high":
        score += 50
    score += {"superseded_possible": 40, "verify_first": 30, "governs": 20}.get(
        classification["authority_label"], 0
    )
    if "execute" in classification.get("action_types", []):
        score += 15
    if score > 0 and classification.get("confidence", 1.0) < CONFIDENCE_FLOOR:
        score += 25
    return score


def _review_reason(classification: dict, has_finding: bool) -> str:
    reasons: list[str] = []
    if has_finding:
        reasons.append("covered-pattern finding")
    if classification["risk"] == "high":
        reasons.append("high risk")
    label = classification["authority_label"]
    if label == "superseded_possible":
        reasons.append("possibly superseded")
    elif label == "verify_first":
        reasons.append("verify before action")
    elif label == "governs":
        reasons.append("governs action")
    if classification.get("confidence", 1.0) < CONFIDENCE_FLOOR:
        reasons.append("low classifier confidence, needs human judgment")
    if "execute" in classification.get("action_types", []):
        reasons.append("action-capable")
    return ", ".join(reasons) or "review as context"


def write_report(items: list[dict], classifications: list[dict], conflicts: list[dict], gates: list[dict], authority_map: list[dict]) -> dict:
    label_counts = Counter(item["authority_label"] for item in classifications)
    high_risk = [item for item in classifications if item["risk"] == "high"]
    severity_counts = Counter(item["severity"] for item in conflicts)

    # Marcus Kim metric (2026-07-01): order the human's review and surface uncertainty,
    # instead of returning a clean verdict. review_queue = what to look at first;
    # needs_human_judgment = where the tool will not stand behind its own label.
    finding_ids = _finding_item_ids(conflicts)
    items_by_id = {item["id"]: item for item in items}
    review_queue = []
    for classification in classifications:
        has_finding = classification["id"] in finding_ids
        priority = _review_priority(classification, has_finding)
        if priority <= 0:
            continue
        review_queue.append({
            "item_id": classification["id"],
            "priority": priority,
            "reason": _review_reason(classification, has_finding),
            "section": items_by_id.get(classification["id"], {}).get("section"),
            "confidence": classification.get("confidence"),
        })
    review_queue.sort(key=lambda entry: entry["priority"], reverse=True)

    needs_human_judgment = []
    for classification in classifications:
        label = classification["authority_label"]
        low_confidence = classification.get("confidence", 1.0) < CONFIDENCE_FLOOR
        if label in ("verify_first", "superseded_possible") or classification["risk"] == "high":
            reason = "authority type requires human judgment before action"
        elif label == "governs" and low_confidence:
            reason = "classifier is not confident this governing rule is current"
        else:
            continue
        needs_human_judgment.append({
            "item_id": classification["id"],
            "confidence": classification.get("confidence"),
            "reason": reason,
        })

    if severity_counts["high"]:
        posture = "needs_review"
    elif conflicts or gates:
        posture = "usable_with_gates"
    else:
        posture = "low_observed_risk"

    summary = [
        f"Detected {len(items)} memory/instruction item(s).",
        f"Authority labels: {dict(label_counts)}.",
        f"High-risk items: {len(high_risk)}.",
        f"Conflicts/findings: {len(conflicts)}.",
        f"Recommended verification gates: {len(gates)}.",
        f"Authority map categories: {len(authority_map)}.",
        f"Review queue: {len(review_queue)} item(s) ordered for human review first; "
        f"{len(needs_human_judgment)} flagged as needing human judgment."
    ]

    recommendations = []
    if label_counts["superseded_possible"]:
        recommendations.append("Mark superseded instructions explicitly and prevent them from governing action.")
    if label_counts["verify_first"]:
        recommendations.append("Add verify-before-action gates for credentials, approvals, and sensitive workflows.")
    if severity_counts["high"]:
        recommendations.append("Resolve high-severity conflicts before connecting this memory set to action-capable tools.")
    if not label_counts["governs"]:
        recommendations.append("Add a clear authority layer for active policies and current source-of-truth rules.")
    recommendations.append("Separate context memories from governing memories in the schema.")
    if authority_map:
        recommendations.append("Review the Authority Map even when no risk findings are present; low-risk governing rules still shape agent behavior.")

    limitations = [
        "This audit detects known dangerous authority patterns; it is not a complete semantic contradiction detector.",
        "No findings does not prove the memory file is safe. It means this audit did not detect a covered failure pattern.",
        "Novel conflicts still require human review or a future semantic contradiction layer before action-capable deployment.",
        "The review queue orders and shortens a careful human review; it does not replace it. A short queue is not a clean bill of health.",
    ]

    return {
        "posture": posture,
        "summary": summary,
        "recommendations": recommendations,
        "limitations": limitations,
        "review_queue": review_queue,
        "needs_human_judgment": needs_human_judgment,
        "counts": {
            "items": len(items),
            "labels": dict(label_counts),
            "risk_high": len(high_risk),
            "conflicts": dict(severity_counts),
            "gates": len(gates),
            "authority_categories": len(authority_map),
            "review_queue": len(review_queue),
            "needs_human_judgment": len(needs_human_judgment),
        }
    }
