from __future__ import annotations

import sentry_sdk

from agents.memory_extractor import extract_memories
from agents.authority_classifier import classify_items
from agents.conflict_detector import detect_conflicts
from agents.verification_gate import build_verification_gates
from agents.report_writer import write_report
from agents.authority_mapper import authority_map


@sentry_sdk.trace
def run_audit(text: str) -> dict:
    items = extract_memories(text)
    item_dicts = [item.to_dict() for item in items]
    classifications = classify_items(items)
    conflicts = detect_conflicts(items, classifications)
    gates = build_verification_gates(classifications, conflicts)
    mapped_authority = authority_map(items, classifications)
    report = write_report(item_dicts, classifications, conflicts, gates, mapped_authority)

    return {
        "report": report,
        "trace": [
            {
                "agent": "memory_extractor",
                "role": "Split raw instruction text into auditable memory items.",
                "output": {"items": len(item_dicts)}
            },
            {
                "agent": "authority_classifier",
                "role": "Classify each memory by authority label, action type, and risk.",
                "output": {"classifications": len(classifications)}
            },
            {
                "agent": "conflict_detector",
                "role": "Find stale, loose, or conflicting authority patterns.",
                "output": {"findings": len(conflicts)}
            },
            {
                "agent": "verification_gate",
                "role": "Convert risks and conflicts into verification gates before action.",
                "output": {"gates": len(gates)}
            },
            {
                "agent": "authority_mapper",
                "role": "Group governing memories by authority category.",
                "output": {"categories": len(mapped_authority)}
            },
            {
                "agent": "report_writer",
                "role": "Summarize posture, recommendations, findings, gates, and authority map.",
                "output": {"posture": report["posture"]}
            }
        ],
        "items": item_dicts,
        "classifications": classifications,
        "authority_map": mapped_authority,
        "conflicts": conflicts,
        "verification_gates": gates
    }
