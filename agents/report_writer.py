from __future__ import annotations

from collections import Counter


def write_report(items: list[dict], classifications: list[dict], conflicts: list[dict], gates: list[dict], authority_map: list[dict]) -> dict:
    label_counts = Counter(item["authority_label"] for item in classifications)
    high_risk = [item for item in classifications if item["risk"] == "high"]
    severity_counts = Counter(item["severity"] for item in conflicts)

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
        f"Authority map categories: {len(authority_map)}."
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
    ]

    return {
        "posture": posture,
        "summary": summary,
        "recommendations": recommendations,
        "limitations": limitations,
        "counts": {
            "items": len(items),
            "labels": dict(label_counts),
            "risk_high": len(high_risk),
            "conflicts": dict(severity_counts),
            "gates": len(gates),
            "authority_categories": len(authority_map)
        }
    }
