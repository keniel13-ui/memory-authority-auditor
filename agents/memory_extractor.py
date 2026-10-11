from __future__ import annotations

from dataclasses import dataclass, asdict
import re


@dataclass
class MemoryItem:
    id: str
    text: str
    section: str
    source_line: int
    signals: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


SECTION_RE = re.compile(r"^(#{1,3})\s+(.+)$")
ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.+)$")

# Genuine supersession language: the instruction flags its OWN staleness or names a
# replacement relationship. This intentionally excludes the bare noun phrase
# "old instruction(s)" used as a topic (e.g. a product tagline about finding old
# instructions), which is a mention, not evidence of being superseded.
SUPERSESSION_MARKERS = [
    "superseded",
    "replaced by",
    "replaced with",
    "no longer valid",
    "no longer applies",
    "no longer in effect",
    "deprecated",
    "obsolete",
    "outdated",
    "old instruction:",
    "old rule:",
    "do not follow this anymore",
    "stop following this",
]


def _signals_for(text: str, section: str) -> list[str]:
    haystack = f"{section} {text}".lower()
    signals: list[str] = []
    checks = {
        "policy": ["must", "require", "policy", "before", "do not", "never"],
        "credential": ["password", "token", "api key", "credential", "secret"],
        "approval": ["approval", "allowed", "permission", "authorize", "director", "lead"],
        "temporary": ["temporary", "one-time", "last month", "exception"],
        "superseded": SUPERSESSION_MARKERS,
        "access": ["access", "contractor", "admin", "matrix"],
        "financial": ["invoice", "payment", "finance", "reconcile"],
        "external_action": ["send", "email", "export", "grant", "write", "database"]
    }
    for signal, words in checks.items():
        if any(word in haystack for word in words):
            signals.append(signal)
    return signals


# A line that ends in terminal punctuation is a finished statement, so the next
# non-blank line starts a NEW instruction rather than continuing this one.
# Wrapped prose does not end its lines this way ("...check the artifact before"),
# which is why this separates instruction-per-line input without merging paragraphs.
#
# Defect this repairs (found 2026-08-31): two contradicting instructions on
# consecutive lines with no blank line between them were joined into a single item.
# The conflict detector then had a population of one and reported zero conflicts.
# The miss was in the population, not in the comparison.
TERMINAL_PUNCTUATION = (".", "!", "?")

# Minimum length for a fragment to count as an auditable item. Was 36, which
# silently discarded short high-risk instructions such as "Delete all logs."
# (16 chars) with no record that anything had been dropped. A floor that removes
# input without reporting it is an absence that reads as a pass.
MIN_ITEM_CHARS = 12


# CONSERVATION + COVERAGE CONTRACT v1, SHA-256 b9aada707453e9c2...
#
# C2: the closed set of dispositions. Every non-blank input line ends as exactly one of
# these. UNCLASSIFIED exists so that its ABSENCE is checkable — it is a defect marker,
# never a default. A line that reaches it means the enumeration is incomplete.
BECAME_ITEM = "became_item"
MERGED_INTO_ITEM = "merged_into_item"
CONSUMED_AS_SECTION_HEADING = "consumed_as_section_heading"
DROPPED_BELOW_MIN_CHARS = "dropped_below_min_chars"
UNCLASSIFIED_DISPOSITION = "unclassified_disposition"

VALID_LINE_DISPOSITIONS = (
    BECAME_ITEM,
    MERGED_INTO_ITEM,
    CONSUMED_AS_SECTION_HEADING,
    DROPPED_BELOW_MIN_CHARS,
    UNCLASSIFIED_DISPOSITION,
)

# V1: a named drop is still a gap. Being explained is not being checked. These two
# dispositions account for their line AND remove it from evaluation, so they must
# surface as coverage gaps even when conservation balances.
#
# This is the hole that killed contract v0 (caught by an independent seat before any
# code was written): under v0, a heading plus one instruction produced two dispositions
# for two lines, conservation balanced, and the tool still returned low_observed_risk on
# an undetected contradiction. The ledger accurately explained the miss while the
# headline reassured the user. A ledger that does that is an alibi.
COVERAGE_GAP_DISPOSITIONS = (CONSUMED_AS_SECTION_HEADING, DROPPED_BELOW_MIN_CHARS)


def extract_with_ledger(text: str) -> tuple[list[MemoryItem], dict]:
    """Extract items AND account for every non-blank input line.

    Returns (items, accounting) where accounting carries the per-line ledger, the
    conservation identity check, and the coverage gaps. `extract_memories` remains the
    item-only entry point so existing callers are unaffected.
    """
    section = "Unsectioned"
    items: list[MemoryItem] = []
    ledger: list[dict] = []
    pending: list[tuple[int, str]] = []

    def record(line_number: int, line_text: str, disposition: str, destination) -> None:
        # C4: every disposition names where the text went. Lines-minus-items cannot
        # measure loss on its own, because wrapped prose legitimately maps many lines
        # to one item.
        ledger.append(
            {
                "line": line_number,
                "text": line_text.strip(),
                "disposition": disposition,
                "destination": destination,
            }
        )

    def flush_paragraph() -> None:
        nonlocal pending
        if not pending:
            return
        content = " ".join(part.strip() for _, part in pending if part.strip())
        if len(content) >= MIN_ITEM_CHARS:
            item_id = f"M{len(items) + 1:03d}"
            items.append(
                MemoryItem(item_id, content, section, pending[0][0], _signals_for(content, section))
            )
            for index, (line_number, line_text) in enumerate(pending):
                record(
                    line_number,
                    line_text,
                    BECAME_ITEM if index == 0 else MERGED_INTO_ITEM,
                    item_id,
                )
        else:
            for line_number, line_text in pending:
                record(line_number, line_text, DROPPED_BELOW_MIN_CHARS, None)
        pending = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        section_match = SECTION_RE.match(line)
        if section_match:
            flush_paragraph()
            section = section_match.group(2).strip()
            record(line_number, line, CONSUMED_AS_SECTION_HEADING, section)
            continue

        item_match = ITEM_RE.match(line)
        if item_match:
            flush_paragraph()
            content = item_match.group(1).strip()
            item_id = f"M{len(items) + 1:03d}"
            items.append(
                MemoryItem(item_id, content, section, line_number, _signals_for(content, section))
            )
            record(line_number, line, BECAME_ITEM, item_id)
            continue

        if line.strip():
            pending.append((line_number, line))
            if line.rstrip().endswith(TERMINAL_PUNCTUATION):
                flush_paragraph()
        else:
            flush_paragraph()

    flush_paragraph()

    # C3: identity, not totals. A ledger recording line 1 twice and omitting line 2
    # preserves the count and must fail. Comparing sets alone would miss the duplicate,
    # so duplicates are checked separately.
    expected = [n for n, line in enumerate(text.splitlines(), start=1) if line.strip()]
    recorded = [entry["line"] for entry in ledger]
    duplicates = sorted({n for n in recorded if recorded.count(n) > 1})
    missing = sorted(set(expected) - set(recorded))
    unexpected = sorted(set(recorded) - set(expected))
    balanced = not duplicates and not missing and not unexpected

    gaps = [entry for entry in ledger if entry["disposition"] in COVERAGE_GAP_DISPOSITIONS]

    accounting = {
        "conservation": {
            "balanced": balanced,
            "lines_in": len(expected),
            "dispositions_out": len(ledger),
            "duplicate_lines": duplicates,
            "missing_lines": missing,
            "unexpected_lines": unexpected,
            "ledger": ledger,
        },
        "coverage": {
            "gaps": gaps,
            "gap_count": len(gaps),
            "evaluated_items": len(items),
        },
    }
    return items, accounting


def extract_memories(text: str) -> list[MemoryItem]:
    items, _ = extract_with_ledger(text)
    return items

