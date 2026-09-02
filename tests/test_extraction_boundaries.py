"""Regression tests for the 2026-08-31 extraction and coverage defects.

Both defects were found by an outside reader against the deployed service, not by
this suite. The suite was green while the service merged two contradicting
instructions into a single item and reported low observed risk. These tests exist
so that specific failure cannot return silently.
"""

from __future__ import annotations

from agents.authority_classifier import classify_items
from agents.conflict_detector import detect_conflicts
from agents.memory_extractor import MIN_ITEM_CHARS, extract_memories


CONTRADICTION = (
    "Current policy: verify the live artifact before publishing.\n"
    "Old note: publish immediately without checking."
)


def test_adjacent_instructions_do_not_merge_into_one_item():
    """The reported defect: two instructions on consecutive lines with no blank
    line between them were joined by the paragraph accumulator into a single
    item. The conflict detector then held a population of one and could not
    compare anything, so zero conflicts was a property of the population rather
    than of the instructions."""
    items = extract_memories(CONTRADICTION)
    assert len(items) == 2, f"expected 2 items, got {len(items)}: {[i.text for i in items]}"
    assert items[0].text == "Current policy: verify the live artifact before publishing."
    assert items[1].text == "Old note: publish immediately without checking."


def test_blank_line_separation_still_works():
    """The separator that already worked must keep working."""
    text = (
        "Current policy: verify the live artifact before publishing.\n\n"
        "Old note: publish immediately without checking."
    )
    assert len(extract_memories(text)) == 2


def test_wrapped_prose_is_not_split_at_the_line_break():
    """Guard against over-correction. A line that does not end in terminal
    punctuation is a wrapped sentence, not a finished instruction, and must stay
    joined to the line that follows it."""
    text = "The reviewer should check the artifact before\npublishing it to the public feed."
    items = extract_memories(text)
    assert len(items) == 1, f"wrapped prose split into {len(items)} items"
    assert "before publishing it" in items[0].text


def test_bulleted_instructions_still_separate():
    text = "- First rule here always applies.\n- Second rule contradicts it."
    assert len(extract_memories("# Rules\n" + text)) == 2


def test_short_high_risk_instruction_is_not_silently_discarded():
    """The floor was 36 characters, which dropped 'Delete all logs.' (16) with no
    record that anything had been removed. A length filter that deletes input
    without reporting it is an absence that reads as a pass."""
    assert MIN_ITEM_CHARS <= 16
    items = extract_memories("Delete all logs.")
    assert len(items) == 1
    assert items[0].text == "Delete all logs."


def test_governing_instruction_with_no_matching_rule_reports_uncovered_domain():
    """Every contradiction this detector can find lives in a hand-enumerated
    domain. An instruction outside those domains produces no signals, no pairs,
    and previously rendered as 'no conflicts' — indistinguishable from a file
    that was checked and found clean. It must now say it was not evaluated."""
    items = extract_memories(CONTRADICTION)
    findings = detect_conflicts(items, classify_items(items))
    kinds = {f["type"] for f in findings}
    assert "uncovered_domain" in kinds, f"expected uncovered_domain, got {kinds}"
    uncovered = next(f for f in findings if f["type"] == "uncovered_domain")
    assert "NOT evaluated" in uncovered["finding"]


def test_enumerated_domain_still_produces_a_real_collision():
    """The uncovered_domain finding must not replace real detection. A
    contradiction inside a listed domain still has to fire as high severity."""
    items = extract_memories(
        "Never deploy without human approval.\nAuto-deploy the moment tests pass."
    )
    findings = detect_conflicts(items, classify_items(items))
    collisions = [f for f in findings if f["type"] == "authority_collision"]
    assert collisions, f"deployment collision did not fire: {[f['type'] for f in findings]}"
    assert collisions[0]["severity"] == "high"
