"""Optional Sentry setup shared by the audit CLI and the Path A eval runner.

Sentry stays off unless ``SENTRY_DSN`` is set. When it is on, personally
identifiable information (``send_default_pii``) is opt-in through
``SENTRY_SEND_DEFAULT_PII=1``: audited memory files can carry the private
material described in EXTERNAL_AUDIT_INTAKE.md, so the default must not widen
what leaves the machine.
"""

from __future__ import annotations

import os

import sentry_sdk

_TRUTHY = {"1", "true", "yes", "on"}


def sentry_options(environ: dict[str, str] | None = None) -> dict | None:
    env = os.environ if environ is None else environ
    dsn = env.get("SENTRY_DSN", "").strip()
    if not dsn:
        return None
    return {
        "dsn": dsn,
        "traces_sample_rate": 1.0,
        "send_default_pii": env.get("SENTRY_SEND_DEFAULT_PII", "").strip().lower() in _TRUTHY,
        "enable_logs": True,
        "release": env.get("SENTRY_RELEASE", "memory-authority-auditor@0.1.0"),
        "environment": env.get("SENTRY_ENVIRONMENT", "development"),
    }


def init_sentry() -> None:
    options = sentry_options()
    if options is not None:
        sentry_sdk.init(**options)
