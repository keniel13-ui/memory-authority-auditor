from __future__ import annotations

from agents.memory_extractor import MemoryItem


def detect_conflicts(items: list[MemoryItem], classifications: list[dict]) -> list[dict]:
    by_id = {item.id: item for item in items}
    class_by_id = {item["id"]: item for item in classifications}
    findings: list[dict] = []

    for item in items:
        text = item.text.lower()
        classification = class_by_id[item.id]
        if classification["authority_label"] == "superseded_possible":
            findings.append({
                "severity": "high",
                "item_id": item.id,
                "type": "stale_instruction",
                "finding": "Instruction appears old or superseded and should not govern action.",
                "evidence": item.text
            })
        if "probably" in text and any(word in text for word in ["access", "export", "allowed", "grant"]):
            findings.append({
                "severity": "high",
                "item_id": item.id,
                "type": "loose_approval",
                "finding": "Loose approval language appears near sensitive action.",
                "evidence": item.text
            })
        if "password" in text and classification["authority_label"] != "verify_first":
            findings.append({
                "severity": "high",
                "item_id": item.id,
                "type": "credential_exposure",
                "finding": "Credential-like memory must verify current status before disclosure.",
                "evidence": item.text
            })
        if "before answering" in text and "invoice" in text and "reconcile" in text:
            findings.append({
                "severity": "medium",
                "item_id": item.id,
                "type": "read_write_overblock",
                "finding": "A write/process requirement may over-govern a read-only lookup.",
                "evidence": item.text
            })

    governing = [item for item in classifications if item["authority_label"] == "governs"]
    if not governing:
        findings.append({
            "severity": "medium",
            "item_id": None,
            "type": "missing_authority_layer",
            "finding": "No clear governing policy memories were detected.",
            "evidence": "The file may contain context without an authority hierarchy."
        })

    access_items = [item for item in items if "access" in item.text.lower() or "contractor" in item.text.lower()]
    if len(access_items) > 1:
        current_items = [item for item in access_items if "current access matrix" in item.text.lower()]
        loose_items = [item for item in access_items if "admin-ish" in item.text.lower() or "probably" in item.text.lower()]
        if current_items and loose_items:
            findings.append({
                "severity": "high",
                "item_id": ", ".join(item.id for item in loose_items),
                "type": "authority_collision",
                "finding": "Loose contractor access language conflicts with current access-matrix governance.",
                "evidence": " | ".join(item.text for item in access_items)
            })

    return findings

