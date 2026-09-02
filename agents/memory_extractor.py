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


def extract_memories(text: str) -> list[MemoryItem]:
    section = "Unsectioned"
    items: list[MemoryItem] = []
    pending_paragraph: list[str] = []
    pending_start = 1

    def flush_paragraph() -> None:
      nonlocal pending_paragraph, pending_start
      content = " ".join(part.strip() for part in pending_paragraph if part.strip())
      if len(content) >= MIN_ITEM_CHARS:
          item_id = f"M{len(items) + 1:03d}"
          items.append(MemoryItem(item_id, content, section, pending_start, _signals_for(content, section)))
      pending_paragraph = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        section_match = SECTION_RE.match(line)
        if section_match:
            flush_paragraph()
            section = section_match.group(2).strip()
            continue

        item_match = ITEM_RE.match(line)
        if item_match:
            flush_paragraph()
            content = item_match.group(1).strip()
            item_id = f"M{len(items) + 1:03d}"
            items.append(MemoryItem(item_id, content, section, line_number, _signals_for(content, section)))
            continue

        if line.strip():
            if not pending_paragraph:
                pending_start = line_number
            pending_paragraph.append(line)
            if line.rstrip().endswith(TERMINAL_PUNCTUATION):
                flush_paragraph()
        else:
            flush_paragraph()

    flush_paragraph()
    return items

