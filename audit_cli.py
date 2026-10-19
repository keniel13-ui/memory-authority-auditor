from __future__ import annotations

import json
import sys
from pathlib import Path

import sentry_sdk

from audit_pipeline import run_audit
from observability import init_sentry


def _init_sentry() -> None:
    init_sentry()


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 audit_cli.py <memory-file>", file=sys.stderr)
        return 2

    _init_sentry()

    path = Path(sys.argv[1])
    with sentry_sdk.start_transaction(op="audit.run", name="audit pipeline") as txn:
        txn.set_data("input_file", str(path))
        result = run_audit(path.read_text(encoding="utf-8"))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

