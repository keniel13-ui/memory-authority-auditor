from __future__ import annotations

from agents.memory_extractor import MemoryItem


CATEGORIES = {
    "startup_source_of_truth": [
        "read brain_current", "read this first", "source of truth", "startup", "session protocol",
        "default source", "live source", "session start"
    ],
    "archive_access_constraints": [
        "do not full-read", "deep archive", "archive", "old briefs", "targeted rg",
        "do not burn context", "read only", "do not go further back"
    ],
    "active_project_constraints": [
        "do not treat", "paper / validation", "active front", "waiting for", "separate from",
        "do not mix", "current priority", "unless keniel explicitly"
    ],
    "budget_capability_constraints": [
        "credits", "budget", "tight", "do not expand", "no autonomous money", "monitoring / paper"
    ],
    "action_tool_constraints": [
        "codex handles", "use the notion", "update the log", "fetch this page", "emit structured",
        "dashboard runs", "runs on", "write", "delete", "restore"
    ],
    "verification_requirements": [
        "verify", "check when", "acknowledge", "confirm", "source hierarchy", "before repeating",
        "paper discipline", "validation", "settled", "clv"
    ],
    "collaboration_rules": [
        "challenge him", "do not validate blindly", "do not project", "read how", "shared channel",
        "collaboration rules"
    ]
}


def authority_map(items: list[MemoryItem], classifications: list[dict]) -> list[dict]:
    class_by_id = {item["id"]: item for item in classifications}
    mapped: dict[str, list[dict]] = {category: [] for category in CATEGORIES}

    for item in items:
        haystack = f"{item.section} {item.text}".lower()
        for category, phrases in CATEGORIES.items():
            if any(phrase in haystack for phrase in phrases):
                classification = class_by_id.get(item.id, {})
                mapped[category].append({
                    "item_id": item.id,
                    "section": item.section,
                    "text": item.text,
                    "authority_label": classification.get("authority_label", "unknown"),
                    "risk": classification.get("risk", "unknown")
                })

    result = []
    for category, entries in mapped.items():
        if not entries:
            continue
        result.append({
            "category": category,
            "label": category.replace("_", " ").title(),
            "items": entries,
            "count": len(entries)
        })
    return result

