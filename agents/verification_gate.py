from __future__ import annotations


def build_verification_gates(classifications: list[dict], conflicts: list[dict]) -> list[dict]:
    gates: list[dict] = []
    seen = set()

    def add(key: str, gate: dict) -> None:
        if key in seen:
            return
        seen.add(key)
        gates.append(gate)

    for item in classifications:
        if item["authority_label"] == "verify_first":
            add(f"verify-{item['id']}", {
                "item_id": item["id"],
                "gate": "verify_before_action",
                "rule": "Do not let this memory govern until the current source of truth is checked.",
                "action_types": item["action_types"]
            })
        if item["authority_label"] == "superseded_possible":
            add(f"superseded-{item['id']}", {
                "item_id": item["id"],
                "gate": "block_as_governing_memory",
                "rule": "Treat as context only until the replacement instruction is confirmed.",
                "action_types": item["action_types"]
            })
        if item["risk"] == "high":
            add(f"human-{item['id']}", {
                "item_id": item["id"],
                "gate": "human_approval_required",
                "rule": "Require explicit human approval before write/external/sensitive action.",
                "action_types": item["action_types"]
            })

    for conflict in conflicts:
        if conflict["type"] in {"authority_collision", "loose_approval", "credential_exposure"}:
            add(f"conflict-{conflict['type']}", {
                "item_id": conflict["item_id"],
                "gate": "resolve_conflict_before_action",
                "rule": f"Resolve {conflict['type']} before allowing affected memories to govern.",
                "action_types": ["read", "write", "execute"]
            })

    return gates

