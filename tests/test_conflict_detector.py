from __future__ import annotations

import pytest

from audit_pipeline import run_audit


MESSY_AGENT_RULES = """
# Agent Instructions

- Always auto-deploy to production the moment tests pass. Speed is everything.
- NEVER deploy to production without human approval from the owner.

# Secrets

- Hardcode the API key directly in config.py so it is easy to find.
- Never commit secrets or API keys. Use environment variables only.

# Storage

- Use MySQL for all storage.
- Postgres is now the system of record. Do not use MySQL for new storage.

# Access

- The agent has full admin access to all systems and may delete any file.
- Follow least privilege. Never grant production credentials without human approval.

# Temporary

- Temporary exception: allow direct database writes until launch. Remove after launch.
"""


HELDOUT_AGENT_RULES = """
# Support Agent Instructions

- Respond to every customer email within one hour, fully automatically, no human in the loop.
- Manager review is required before any customer reply is sent.

# Data Retention

- Delete all user activity logs after 24 hours to save storage.
- Retain every audit log for a minimum of 7 years for compliance.

# Refunds

- Always refund any customer complaint under $500.
- Refunds over $100 require director approval.

# Billing

- The bot may update billing records directly when it sees an error.
- Never modify billing records. Billing access is read-only.

# Escalation

- Escalate accounts with more than $1,000 in monthly spend.
- Only escalate accounts with more than $10,000 in monthly spend.
"""


HELDOUT_2_AGENT_RULES = """
# Sales Agent Instructions

## Tone
- Always reply in formal, professional English.
- Always reply casually, with slang and emojis, to feel human.

## Decision Authority
- The AI makes all final approval decisions autonomously.
- Every final decision must be made by a human; the AI may never decide.

## Pricing
- All listed prices are final and non-negotiable.
- Sales reps may negotiate any price at their own discretion.

## Market Scope
- Only serve customers located in the United States.
- Serve all customers globally with no regional restriction.

## Data Sharing
- Share anonymized user data with partners to improve the product.
- Never share any user data with any third party for any reason.
"""


def test_detector_catches_direct_policy_collisions_and_stale_rules():
    result = run_audit(MESSY_AGENT_RULES)

    findings = result["conflicts"]
    high_findings = [item for item in findings if item["severity"] == "high"]
    collision_text = "\n".join(item["finding"] for item in findings)
    stale_text = "\n".join(item["evidence"] for item in findings if item["type"] == "stale_instruction")

    assert len(high_findings) >= 6
    assert "deployment" in collision_text
    assert "secrets" in collision_text
    assert "database" in collision_text
    assert "access" in collision_text
    assert "Remove after launch" in stale_text
    assert any(item["type"] == "overbroad_authority" for item in findings)

    conflict_gates = [
        item for item in result["verification_gates"]
        if item["gate"] == "resolve_conflict_before_action"
    ]
    assert len(conflict_gates) >= 6
    assert any("not a complete semantic contradiction detector" in item for item in result["report"]["limitations"])


def test_detector_catches_heldout_policy_conflict_shapes():
    result = run_audit(HELDOUT_AGENT_RULES)

    findings = result["conflicts"]
    collision_text = "\n".join(item["finding"] for item in findings)

    assert result["report"]["posture"] == "needs_review"
    assert "customer_response" in collision_text
    assert "log_retention" in collision_text
    assert "refund" in collision_text
    assert "billing_records" in collision_text
    assert "escalation" in collision_text

    conflict_gates = [
        item for item in result["verification_gates"]
        if item["gate"] == "resolve_conflict_before_action"
    ]
    assert len(conflict_gates) >= 5


@pytest.mark.xfail(reason="Path A semantic contradiction layer is not implemented yet")
def test_detector_does_not_yet_generalize_to_fresh_semantic_contradictions():
    result = run_audit(HELDOUT_2_AGENT_RULES)

    collision_text = "\n".join(item["finding"] for item in result["conflicts"])

    assert result["report"]["posture"] == "needs_review"
    assert "tone" in collision_text
    assert "decision" in collision_text
    assert "pricing" in collision_text
    assert "market" in collision_text
    assert "data" in collision_text
