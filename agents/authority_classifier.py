from __future__ import annotations

from agents.memory_extractor import MemoryItem


def classify_authority(item: MemoryItem) -> dict:
    text = item.text.lower()
    signals = set(item.signals)

    # Only flag as superseded when the extractor found genuine supersession language
    # (see SUPERSESSION_MARKERS). A bare mention of "old instructions" as a topic,
    # e.g. a tagline about finding old instructions, is not evidence of staleness.
    if "superseded" in signals:
        label = "superseded_possible"
        confidence = 0.88
    elif "credential" in signals:
        label = "verify_first"
        confidence = 0.82
    elif "temporary" in signals:
        label = "context_only"
        confidence = 0.74
    elif (
        "policy" in signals
        or "must" in text
        or "require" in text
        or "do not" in text
        or "read this file first" in text
        or "source of truth" in text
        or "use the notion" in text
        or "source of truth hierarchy" in text
        or "only through" in text
        or "paper / validation only" in text
        or "no autonomous money" in text
        or "unless keniel explicitly" in text
        or "codex handles" in text
        or "shared channel" in text
    ):
        label = "governs"
        confidence = 0.78
    elif "approval" in signals and ("probably" in text or "mentioned" in text):
        label = "verify_first"
        confidence = 0.7
    else:
        label = "context_only"
        confidence = 0.64

    action_types = []
    if any(word in text for word in ["answer", "status", "explain", "tell"]):
        action_types.append("read")
    if any(word in text for word in ["send", "email", "export", "grant", "write", "database", "reconcile"]):
        action_types.append("write")
    if any(word in text for word in ["run", "execute", "deploy"]):
        action_types.append("execute")
    if not action_types:
        action_types.append("read")

    risk = "low"
    if label in {"verify_first", "superseded_possible"}:
        risk = "medium"
    if any(word in text for word in ["password", "admin", "donor", "payment", "database", "external email", "access matrix", "granting contractor access"]):
        risk = "high"

    return {
        "id": item.id,
        "authority_label": label,
        "confidence": confidence,
        "action_types": action_types,
        "risk": risk,
        "reason": reason_for(label, item)
    }


def reason_for(label: str, item: MemoryItem) -> str:
    if label == "governs":
        return "Contains policy or requirement language that appears intended to constrain action."
    if label == "verify_first":
        return "Contains sensitive, credential, approval, or external-action signals that should not directly authorize action."
    if label == "superseded_possible":
        return "Contains old/superseded wording and should not govern without checking the current replacement."
    return "Useful as context, but it does not appear strong enough to govern action by itself."


def classify_items(items: list[MemoryItem]) -> list[dict]:
    return [classify_authority(item) for item in items]
