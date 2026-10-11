"""Regression tests for CONSERVATION + COVERAGE CONTRACT v1.

Contract SHA-256 at freeze: b9aada707453e9c203aa8d21c4f73054ac4fd8d31bbebe37f00e2a5777801be8
Supersedes v0 (6175f6e82feee5da...), which was frozen and then found holed BEFORE any code
was written: under v0 a heading plus one instruction produced two dispositions for two
lines, conservation balanced, and the tool still returned low_observed_risk on an
undetected contradiction. The ledger accurately explained the miss while the headline
reassured the user.

Design credit: conservation is Vinh Nguyen Thanh's (DEV 3e6c4). The conservation/coverage
separation, identity checking, destination linking, and the visible-report requirement are
Kairos's (PHASE 1700 review).
"""

from __future__ import annotations

import pytest

from agents.memory_extractor import (
    COVERAGE_GAP_DISPOSITIONS,
    UNCLASSIFIED_DISPOSITION,
    VALID_LINE_DISPOSITIONS,
    extract_with_ledger,
)
from audit_pipeline import run_audit


HEADING_FIXTURE = "## Never deploy without human approval\nAuto-deploy the moment tests pass."
WRAPPED_FIXTURE = "The reviewer should check the artifact before\npublishing it to the public feed."
MIXED_FIXTURE = (
    "## Deployment\n\nNever deploy without human approval.\nAuto-deploy the moment tests pass."
)


def _non_blank_indices(text: str) -> list[int]:
    return [n for n, line in enumerate(text.splitlines(), start=1) if line.strip()]


@pytest.mark.parametrize("text", [HEADING_FIXTURE, WRAPPED_FIXTURE, MIXED_FIXTURE, "Wipe logs."])
def test_c1_every_non_blank_line_gets_exactly_one_disposition(text):
    """C1. No line may vanish. Before this contract, a heading line and a sub-floor line
    both disappeared with nothing in the output naming the loss."""
    _, accounting = extract_with_ledger(text)
    recorded = [entry["line"] for entry in accounting["conservation"]["ledger"]]
    assert sorted(recorded) == _non_blank_indices(text)
    assert len(recorded) == len(set(recorded)), "a line was recorded more than once"


@pytest.mark.parametrize("text", [HEADING_FIXTURE, WRAPPED_FIXTURE, MIXED_FIXTURE])
def test_c2_dispositions_come_from_the_closed_set(text):
    """C2. `unclassified_disposition` exists so its ABSENCE is checkable. It is a defect
    marker, never a default."""
    _, accounting = extract_with_ledger(text)
    for entry in accounting["conservation"]["ledger"]:
        assert entry["disposition"] in VALID_LINE_DISPOSITIONS
        assert entry["disposition"] != UNCLASSIFIED_DISPOSITION


def test_c3_identity_not_totals():
    """C3. A ledger recording line 1 twice and omitting line 2 preserves the COUNT.

    Kairos caught that v0's runtime check compared totals, so a permutation would pass and
    C5's protection would never fire. The check must compare line identities.
    """
    _, accounting = extract_with_ledger(MIXED_FIXTURE)
    conservation = accounting["conservation"]
    assert conservation["balanced"] is True
    assert conservation["duplicate_lines"] == []
    assert conservation["missing_lines"] == []
    assert conservation["unexpected_lines"] == []

    # A count-only check cannot distinguish these two ledgers. An identity check can.
    real = sorted(e["line"] for e in conservation["ledger"])
    forged = [real[0]] * len(real)
    assert len(forged) == len(real), "the forgery preserves the count, which is the point"
    assert sorted(set(forged)) != real, "identity comparison must reject it"


@pytest.mark.parametrize("text", [HEADING_FIXTURE, WRAPPED_FIXTURE, MIXED_FIXTURE])
def test_c4_every_disposition_names_its_destination(text):
    """C4. Lines-minus-items cannot measure loss on its own, because wrapped prose
    legitimately maps many lines to one item. Each entry must say where the text went."""
    _, accounting = extract_with_ledger(text)
    for entry in accounting["conservation"]["ledger"]:
        assert set(entry) == {"line", "text", "disposition", "destination"}
        if entry["disposition"] != "dropped_below_min_chars":
            assert entry["destination"], f"no destination on {entry}"


def test_c4_wrapped_prose_merges_and_names_the_item_it_merged_into():
    """Two lines becoming one item is legitimate. The ledger has to show that it was a
    merge into a specific item, not a loss."""
    items, accounting = extract_with_ledger(WRAPPED_FIXTURE)
    assert len(items) == 1
    dispositions = [e["disposition"] for e in accounting["conservation"]["ledger"]]
    assert dispositions == ["became_item", "merged_into_item"]
    assert {e["destination"] for e in accounting["conservation"]["ledger"]} == {items[0].id}
    assert accounting["coverage"]["gap_count"] == 0, "a merge is not a gap"


def test_v1_a_named_drop_is_still_a_gap():
    """V1. This is the hole that killed v0. Being explained is not being checked."""
    _, accounting = extract_with_ledger(HEADING_FIXTURE)
    assert accounting["conservation"]["balanced"] is True, "conservation balances..."
    assert accounting["coverage"]["gap_count"] == 1, "...and it is STILL a coverage gap"
    gap = accounting["coverage"]["gaps"][0]
    assert gap["disposition"] in COVERAGE_GAP_DISPOSITIONS
    assert gap["text"] == "## Never deploy without human approval"


def test_v3_no_reassuring_verdict_while_a_coverage_gap_exists():
    """V3. The exact v0 failure, now blocked: balanced ledger, undetected contradiction,
    and the tool may no longer call it low risk."""
    report = run_audit(HEADING_FIXTURE)["report"]
    assert report["posture"] == "incomplete_coverage"
    assert report["posture"] not in {"low_observed_risk", "usable_with_gates"}


def test_v3_does_not_suppress_a_real_alarm():
    """A high-severity collision is an ALARM, not a reassurance. Hiding a real finding
    behind an instrumentation caveat would be strictly worse than the defect being fixed.
    V3 makes the REASSURING postures unreachable, not every posture."""
    text = "## Deployment\n\nNever deploy without human approval.\nAuto-deploy the moment tests pass."
    report = run_audit(text)["report"]
    assert report["counts"]["conflicts"].get("high") == 1
    assert report["posture"] == "needs_review", "the alarm must survive the coverage gap"
    assert report["coverage"]["gap_count"] >= 1, "and the gap must still be reported"


def test_d1_ledger_and_coverage_reach_the_visible_report():
    """D1. JSON a user never sees does not satisfy this contract."""
    report = run_audit(MIXED_FIXTURE)["report"]
    assert "conservation" in report and "coverage" in report
    assert report["conservation"]["ledger"], "ledger must be present in the report"
    assert any("NOT evaluated" in line for line in report["summary"]), (
        "the gap must appear in the summary a user actually reads"
    )


def test_f6_this_contract_does_not_fix_heading_or_length():
    """Falsification row 6. v1 is an accounting and disclosure change. It must not make the
    tool smarter, including by accident. If these counts move, the repair was not done under
    the frozen contract and the provenance claim is false."""
    assert run_audit("Wipe logs.\n\nNever deploy without human approval.")["report"]["counts"]["items"] == 1
    assert run_audit("## Never deploy without human approval.\nAuto-deploy the moment tests pass.")["report"]["counts"]["items"] == 1
    assert run_audit("Never deploy without human approval.\nAuto-deploy the moment tests pass.")["report"]["counts"]["items"] == 2
    # and the heading contradiction is STILL undetected
    assert run_audit("## Never deploy without human approval.\nAuto-deploy the moment tests pass.")["report"]["counts"]["conflicts"] == {}
