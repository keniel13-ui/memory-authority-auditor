from __future__ import annotations


class MemoryItemProxy:
    def __init__(self, data: dict) -> None:
        self.id = str(data.get("id", ""))
        self.text = str(data.get("text", ""))
        self.section = str(data.get("section", ""))
        self.source_line = int(data.get("source_line", 0))
        self.signals = list(data.get("signals", []))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "section": self.section,
            "source_line": self.source_line,
            "signals": self.signals,
        }
