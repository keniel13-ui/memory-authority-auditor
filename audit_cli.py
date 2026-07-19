from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import sentry_sdk

from audit_pipeline import run_audit


def _init_sentry() -> None:
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=1.0,
        send_default_pii=True,
        enable_logs=True,
        release=os.environ.get("SENTRY_RELEASE", "memory-authority-auditor@0.1.0"),
        environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
    )


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

