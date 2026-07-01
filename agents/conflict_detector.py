from __future__ import annotations

from dataclasses import dataclass
import re

from agents.memory_extractor import MemoryItem


@dataclass(frozen=True)
class PolicySignal:
    domain: str
    stance: str
    threshold: float | None = None


def _has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _money_values(text: str) -> list[float]:
    values: list[float] = []
    for match in re.finditer(r"\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)", text):
        values.append(float(match.group(1).replace(",", "")))
    return values


def _add_structural_signals(text: str, signals: list[PolicySignal]) -> None:
    """Extract cross-domain rule shapes instead of only memorized examples."""
    if _has_any(text, ["customer email", "customer response", "respond to every customer", "reply to customer", "reply", "email"]):
        domain = "customer_response"
        if _has_any(text, ["fully automatically", "no human", "without human", "no manager", "no review", "every customer"]):
            signals.append(PolicySignal(domain, "allow_automatic"))
        if _has_any(text, ["manager review", "human review", "approval", "before any reply", "before replying"]):
            signals.append(PolicySignal(domain, "require_review"))

    if _has_any(text, ["activity log", "audit log", "logs", "log"]):
        domain = "log_retention"
        if _has_any(text, ["delete", "after 24 hours", "save storage"]):
            signals.append(PolicySignal(domain, "delete"))
        if _has_any(text, ["retain", "minimum", "7 years", "compliance"]):
            signals.append(PolicySignal(domain, "retain"))

    if "refund" in text:
        domain = "refund"
        values = _money_values(text)
        threshold = values[0] if values else None
        if _has_any(text, ["always refund", "refund any", "automatically refund"]):
            signals.append(PolicySignal(domain, "allow_below", threshold))
        if _has_any(text, ["require director", "director approval", "manager approval", "approval"]):
            signals.append(PolicySignal(domain, "require_approval_above", threshold))

    if _has_any(text, ["billing record", "billing records", "billing"]):
        domain = "billing_records"
        if _has_any(text, ["may update", "can update", "write", "modify", "change"]):
            signals.append(PolicySignal(domain, "allow_write"))
        if _has_any(text, ["never modify", "do not modify", "read-only", "read only"]):
            signals.append(PolicySignal(domain, "prohibit_write"))

    if _has_any(text, ["escalate", "escalation"]):
        domain = "escalation"
        values = _money_values(text)
        if values:
            signals.append(PolicySignal(domain, "threshold", values[0]))


def _policy_signals(text: str) -> list[PolicySignal]:
    """Return deterministic policy signals for pairwise conflict checks.

    This intentionally stays conservative. It does not try to "understand" every
    sentence; it catches high-value contradictions that matter for agent safety:
    deploy authority, secret handling, datastore source of truth, and broad
    production/admin access.
    """
    signals: list[PolicySignal] = []

    if "deploy" in text:
        if _has_any(text, ["auto-deploy", "auto deploy", "moment tests pass", "immediately deploy"]):
            signals.append(PolicySignal("deployment", "allow_automatic"))
        if _has_any(text, ["never deploy", "do not deploy", "human approval", "approval before deploy"]):
            signals.append(PolicySignal("deployment", "require_human_approval"))

    if _has_any(text, ["api key", "secret", "token", "password", "credential"]):
        if (
            _has_any(text, ["hardcode", "frontend", "directly in config", "store the database password"])
            or ("commit" in text and not _has_any(text, ["never commit", "do not commit"]))
        ):
            signals.append(PolicySignal("secrets", "allow_exposure"))
        if _has_any(text, ["never commit", "do not commit", "do not hardcode", "env", ".env", "environment variable"]):
            signals.append(PolicySignal("secrets", "prohibit_exposure"))

    if _has_any(text, ["mysql", "postgres", "database", "system of record"]):
        if _has_any(text, ["mysql for all", "use mysql", "mysql is"]) and "do not use mysql" not in text:
            signals.append(PolicySignal("database", "mysql_required"))
        if _has_any(text, ["postgres is now", "postgres is the", "do not use mysql", "system of record"]):
            signals.append(PolicySignal("database", "postgres_required"))

    if _has_any(text, ["admin", "prod credential", "production credential", "full access", "delete any file", "grant every agent"]):
        if _has_any(text, ["full admin", "full access", "delete any file", "grant every agent", "by default"]):
            signals.append(PolicySignal("access", "broad_default_access"))
        if _has_any(text, ["least privilege", "human approval", "do not grant", "never grant", "approval required"]):
            signals.append(PolicySignal("access", "restricted_access"))

    _add_structural_signals(text, signals)
    return list(dict.fromkeys(signals))


CONFLICTING_STANCES = {
    "deployment": {frozenset({"allow_automatic", "require_human_approval"})},
    "secrets": {frozenset({"allow_exposure", "prohibit_exposure"})},
    "database": {frozenset({"mysql_required", "postgres_required"})},
    "access": {frozenset({"broad_default_access", "restricted_access"})},
    "customer_response": {frozenset({"allow_automatic", "require_review"})},
    "log_retention": {frozenset({"delete", "retain"})},
    "billing_records": {frozenset({"allow_write", "prohibit_write"})},
}


def _thresholds_conflict(left: PolicySignal, right: PolicySignal) -> bool:
    if left.domain != right.domain:
        return False
    if left.threshold is None or right.threshold is None:
        return False
    if left.domain == "escalation" and left.stance == right.stance == "threshold":
        return left.threshold != right.threshold
    if left.domain == "refund":
        pair = {left.stance, right.stance}
        if pair == {"allow_below", "require_approval_above"}:
            allow = left if left.stance == "allow_below" else right
            approval = left if left.stance == "require_approval_above" else right
            return approval.threshold < allow.threshold
    return False


def _conflict_finding(left: MemoryItem, right: MemoryItem, domain: str, left_stance: str, right_stance: str) -> dict:
    return {
        "severity": "high",
        "item_id": f"{left.id}, {right.id}",
        "type": "authority_collision",
        "finding": f"Conflicting governing instructions in {domain}: {left_stance} vs {right_stance}.",
        "evidence": f"{left.text} | {right.text}",
    }


def detect_conflicts(items: list[MemoryItem], classifications: list[dict]) -> list[dict]:
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
        if any(marker in text for marker in ["remove after", "remove this after", "until launch", "last month", "temporary exception", "old rule"]):
            findings.append({
                "severity": "high",
                "item_id": item.id,
                "type": "stale_instruction",
                "finding": "Instruction contains temporary or expiry language and should be checked against current policy.",
                "evidence": item.text
            })
        if _has_any(text, ["full admin access", "delete any file", "wipe any environment", "drop any database", "full production credentials by default"]):
            findings.append({
                "severity": "high",
                "item_id": item.id,
                "type": "overbroad_authority",
                "finding": "Instruction grants broad destructive or production authority and requires explicit narrowing before action.",
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

    signals_by_item = {item.id: _policy_signals(item.text.lower()) for item in items}
    seen_pairs: set[tuple[str, str, str]] = set()
    for idx, left in enumerate(items):
        for right in items[idx + 1:]:
            for left_signal in signals_by_item[left.id]:
                for right_signal in signals_by_item[right.id]:
                    if left_signal.domain != right_signal.domain:
                        continue
                    stance_pair = frozenset({left_signal.stance, right_signal.stance})
                    if (
                        stance_pair not in CONFLICTING_STANCES.get(left_signal.domain, set())
                        and not _thresholds_conflict(left_signal, right_signal)
                    ):
                        continue
                    key = (left.id, right.id, left_signal.domain)
                    if key in seen_pairs:
                        continue
                    seen_pairs.add(key)
                    findings.append(_conflict_finding(left, right, left_signal.domain, left_signal.stance, right_signal.stance))

    return findings
