from __future__ import annotations

import json
import sys
from pathlib import Path

from audit_pipeline import run_audit


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 audit_cli.py <memory-file>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    result = run_audit(path.read_text(encoding="utf-8"))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

