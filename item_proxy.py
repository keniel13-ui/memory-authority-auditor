from __future__ import annotations


class MemoryItemProxy:
    def __init__(self, data: dict) -> None:
        if not isinstance(data, dict):
            raise TypeError("memory item must be an object")
        signals = data.get("signals", [])
        if not isinstance(signals, list):
            raise TypeError("memory item 'signals' must be a list")
        self.id = str(data.get("id", ""))
        self.text = str(data.get("text", ""))
        self.section = str(data.get("section", ""))
        try:
            self.source_line = int(data.get("source_line", 0))
        except (TypeError, ValueError) as error:
            raise ValueError("memory item 'source_line' must be an integer") from error
        self.signals = list(signals)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "section": self.section,
            "source_line": self.source_line,
            "signals": self.signals,
        }
