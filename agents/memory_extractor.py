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


def _signals_for(text: str, section: str) -> list[str]:
    haystack = f"{section} {text}".lower()
    signals: list[str] = []
    checks = {
        "policy": ["must", "require", "policy", "before", "do not", "never"],
        "credential": ["password", "token", "api key", "credential", "secret"],
        "approval": ["approval", "allowed", "permission", "authorize", "director", "lead"],
        "temporary": ["temporary", "one-time", "last month", "exception"],
        "superseded": ["superseded", "old instruction", "replaced by"],
        "access": ["access", "contractor", "admin", "matrix"],
        "financial": ["invoice", "payment", "finance", "reconcile"],
        "external_action": ["send", "email", "export", "grant", "write", "database"]
    }
    for signal, words in checks.items():
        if any(word in haystack for word in words):
            signals.append(signal)
    return signals


def extract_memories(text: str) -> list[MemoryItem]:
    section = "Unsectioned"
    items: list[MemoryItem] = []
    pending_paragraph: list[str] = []
    pending_start = 1

    def flush_paragraph() -> None:
      nonlocal pending_paragraph, pending_start
      content = " ".join(part.strip() for part in pending_paragraph if part.strip())
      if len(content) >= 36:
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
        else:
            flush_paragraph()

    flush_paragraph()
    return items

