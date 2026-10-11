"""Regression tests for EMPTY_SET_CONTRACT_V0_2026-09-04.

Contract SHA-256 at freeze: 5294938927e29ad8bd658fc699774b71bdb7124978cc9482a68173dbf3c27d27

The defect: five agent roles raised a bare ValueError when `items` or `classifications` was
empty, and the request handler returned 400 for every exception. A legitimate zero-item
extraction was therefore reported to the caller as a bad request, and the web router wrapped
that as `500 {"error": "HTTP Error 400: Bad Request"}`. Observed live on the public endpoint
2026-09-04 for the input `## Never deploy without human approval`, which is an ordinary
instruction file.

An empty population is a verdict, not an exception. These tests exist so that specific
confusion cannot return silently.
"""

from __future__ import annotations

import importlib
import os

import pytest

from audit_pipeline import run_audit


EMPTY_PAYLOAD = {
    "items": [],
    "classifications": [],
    "conflicts": [],
    "verification_gates": [],
    "authority_map": [],
}

CONSUMER_ROLES = [
    "authority_classifier",
    "conflict_detector",
    "authority_mapper",
    "verification_gate",
    "report_writer",
]


def _service_for(role: str, monkeypatch):
    """Reload agent_service bound to a specific AGENT_ROLE."""
    monkeypatch.setenv("AGENT_ROLE", role)
    import agent_service

    return importlib.reload(agent_service)


@pytest.mark.parametrize("role", CONSUMER_ROLES)
def test_r1_empty_but_wellformed_payload_is_a_verdict_not_an_error(role, monkeypatch):
    """R1. Every downstream role accepts an empty list and returns its own empty result.

    This is the exact call that produced the live 500: the extractor correctly returned
    HTTP 200 with `{"items": []}`, and the next agent rejected it.
    """
    service = _service_for(role, monkeypatch)
    result = service.handle_role(dict(EMPTY_PAYLOAD))
    assert result["agent"] == role


@pytest.mark.parametrize("role", CONSUMER_ROLES)
def test_r2_missing_required_key_is_malformed(role, monkeypatch):
    """R2. Absent key stays a client error. Empty-but-present must not be confused with it."""
    service = _service_for(role, monkeypatch)
    with pytest.raises(service.MalformedPayload):
        service.handle_role({})


@pytest.mark.parametrize("role", CONSUMER_ROLES)
def test_r2_wrong_typed_key_is_malformed(role, monkeypatch):
    """R2. A string where a list belongs is malformed, and must not raise something the
    handler would report as a 500."""
    service = _service_for(role, monkeypatch)
    with pytest.raises(service.MalformedPayload):
        service.handle_role({"items": "not-a-list", "classifications": "not-a-list"})


def test_r3_remote_http_error_carries_its_status(monkeypatch):
    """R3. A downstream failure must carry the remote status so the router can map it through
    instead of collapsing every downstream fault into a 500."""
    import remote_pipeline

    assert hasattr(remote_pipeline, "RemoteAgentError")
    error = remote_pipeline.RemoteAgentError("http://agent.example", 400, "bad")
    assert error.status == 400
    assert error.agent_url == "http://agent.example"


def test_r4_zero_items_does_not_claim_low_risk():
    """R4. A population of zero cannot support a verdict about the file's contents.

    `low_observed_risk` and `usable_with_gates` both assert something about instructions that
    were never extracted.

    SUPERSEDED BY CONSERVATION+COVERAGE v1 (b9aada707453e9c2...): this test originally
    pinned the literal string `no_items_extracted`. v1's V3 returns `incomplete_coverage`
    for this input, because the heading line is now recorded as a coverage gap. The test's
    intent is unchanged and still holds; only the over-specified literal was wrong. The
    assertion below checks the intent (no reassuring verdict) rather than a string that a
    later contract is allowed to refine.
    """
    report = run_audit("## Never deploy without human approval")["report"]
    assert report["counts"]["items"] == 0
    assert report["posture"] not in {"low_observed_risk", "usable_with_gates"}
    assert report["posture"] in {"no_items_extracted", "incomplete_coverage"}


def test_r4_scope_boundary_population_of_one_is_deliberately_unfixed():
    """R4 explicitly does NOT cover a population of one.

    `Wipe logs.` is discarded by the length floor, leaving a single item and a
    `low_observed_risk` verdict on a pair that was never compared. That defect is real and is
    out of scope for this contract. This test pins the boundary so a later reader cannot
    mistake the empty-set repair for a fix of the collapsed-population defect.

    SUPERSEDED BY CONSERVATION+COVERAGE v1 (b9aada707453e9c2...): posture is now
    `incomplete_coverage`, because `Wipe logs.` is recorded as `dropped_below_min_chars`
    and V1 makes a named drop a coverage gap. **The boundary this test guards is
    unchanged and was re-verified**: the item count is still 1 and `conflicts` is still
    empty, so the collapsed-population defect is still NOT fixed. Only the reassuring
    label was removed. The assertions below check the boundary itself rather than the
    posture string, so they cannot be satisfied by a later contract quietly repairing
    extraction.
    """
    report = run_audit("Wipe logs.\n\nNever deploy without human approval.")["report"]
    assert report["counts"]["items"] == 1, "length-floor defect must remain unfixed here"
    assert report["counts"]["conflicts"] == {}, "contradiction must remain undetected here"
    assert report["posture"] not in {"low_observed_risk", "usable_with_gates"}


@pytest.mark.parametrize(
    "text,expected_items",
    [
        ("Wipe logs.\n\nNever deploy without human approval.", 1),
        ("## Never deploy without human approval.\nAuto-deploy the moment tests pass.", 1),
        ("Never deploy without human approval.\nAuto-deploy the moment tests pass.", 2),
    ],
)
def test_f5_known_fixtures_are_unchanged_by_this_repair(text, expected_items):
    """Falsification row 5. This diff is not allowed to change the known fixtures, including
    by accident. If the heading or length defect gets fixed here, it was not done under a
    frozen contract and the provenance claim would be false."""
    assert run_audit(text)["report"]["counts"]["items"] == expected_items
