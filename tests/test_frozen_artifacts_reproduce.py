"""Recorded PASS A / re-gate artifacts must reproduce from the current code.

Each gate script is run inside a throwaway copy of the repository (so the real
``path_a_eval_artifacts/`` directory is never touched) and its fresh JSON
output is compared with the committed artifact after removing only run
metadata: ``generated_at``, ``generated_at_utc``, ``run_id``, and the
``YYYYMMDDTHHMMSSZ`` run slug inside strings.

This test never rewrites a recorded artifact. If it fails, either a change
altered a frozen gate (a research regression) or the artifact is historical
and only reproduces at the commit that recorded it. In the second case add it
to ``HISTORICAL_ONLY`` with the recording commit and the reason, rather than
regenerating the committed file.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).parents[1]
ARTIFACTS = ROOT / "path_a_eval_artifacts"
SLUG = re.compile(r"20\d{6}T\d{6}Z")
RUN_METADATA_KEYS = {"generated_at", "generated_at_utc", "run_id"}

# (script, extra args, committed artifact it must reproduce)
REPRODUCIBLE = [
    ("path_a_v2_regate.py", ["--recorded-artifact", "path_a_eval_artifacts/path_a_eval_20260712T003706Z.json"],
     "path_a_v2_pass_a_regate_20260712T005345Z.json"),
    ("path_a_v3_pass0_regate.py", [], "path_a_v3_pass0_regate_20260713T020447Z.json"),
    ("path_a_v3_carveout_c1_regate.py", [], "path_a_v3_carveout_c1_regate_20260713T034628Z.json"),
    ("path_a_v3_store_authority_pass_a.py", [], "path_a_v3_store_authority_pass_a_20260715T235136Z.json"),
    ("path_a_v3_silent_omission_pass_a.py", [], "path_a_v3_silent_omission_pass_a_20260716T022032Z.json"),
    ("path_a_v3_considered_set_pass_a.py", [], "path_a_v3_considered_set_pass_a_20260716T201138Z.json"),
    ("path_a_v3_imported_anchor_diff_pass_a.py", [], "path_a_v3_imported_anchor_diff_pass_a_20260722T002052Z.json"),
]

# Artifacts verified (2026-10-19) to reproduce byte-for-byte, modulo run
# metadata, only at the commit that recorded them. Documented here so the
# drift is visible instead of silently ignored.
HISTORICAL_ONLY = {
    "path_a_v3_carveout_c0_regate_20260713T034423Z.json": (
        "78d66a3: C0 baseline was recorded against the v2 gate; the later v3 carve-out guard "
        "intentionally changes C0 outcomes at HEAD"
    ),
    "path_a_v3_resource_mapping_receipt_v0_pass_a_20260722T014028Z.json": (
        "3292c98: later hardening added the rejected_mapping_receipts field to each result"
    ),
    "path_a_v3_anchor_contract_v0_pass_a_20260722T011623Z.json": (
        "9c6a967: a later commit reworded one source-local alias reason string"
    ),
}


def _normalize(value):
    if isinstance(value, dict):
        return {key: _normalize(child) for key, child in value.items() if key not in RUN_METADATA_KEYS}
    if isinstance(value, list):
        return [_normalize(child) for child in value]
    if isinstance(value, str):
        return SLUG.sub("<slug>", value)
    return value


@pytest.fixture(scope="module")
def workspace(tmp_path_factory) -> Path:
    target = tmp_path_factory.mktemp("repo") / "memory-authority-auditor"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".venv", "reports"),
    )
    return target


def _run(workspace: Path, script: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, script, *args],
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


@pytest.mark.parametrize("script, args, committed", REPRODUCIBLE, ids=[row[0] for row in REPRODUCIBLE])
def test_recorded_artifact_reproduces(workspace: Path, script: str, args: list[str], committed: str):
    out_dir = workspace / "path_a_eval_artifacts"
    before = set(out_dir.iterdir())
    completed = _run(workspace, script, args)
    assert completed.returncode == 0, completed.stderr
    created = sorted(path for path in set(out_dir.iterdir()) - before if path.suffix == ".json")
    assert len(created) == 1, created
    fresh = json.loads(created[0].read_text(encoding="utf-8"))
    recorded = json.loads((ARTIFACTS / committed).read_text(encoding="utf-8"))
    for path in set(out_dir.iterdir()) - before:
        path.unlink()
    assert _normalize(fresh) == _normalize(recorded)


def test_authority_runtime_pass_a_regenerates_byte_identical(workspace: Path):
    completed = _run(workspace, "authority_runtime_v0_pass_a.py", [])
    assert completed.returncode == 0, completed.stderr
    assert "11/11 frozen outcomes matched" in completed.stdout
    for name in ("authority_runtime_v0_pass_a_20260721.json", "authority_runtime_v0_pass_a_20260721.md"):
        assert (workspace / "path_a_eval_artifacts" / name).read_bytes() == (ARTIFACTS / name).read_bytes()


def test_authorityctl_flagship_receipts_regenerate_byte_identical(workspace: Path):
    completed = _run(
        workspace,
        "authorityctl.py",
        [
            "audit",
            "tests/fixtures/authority_runtime_v0_gwb_dns_replay_2026_07_21.json",
            "--case",
            "authority_runtime_ar1_real_gwb_stale_cutover",
            "--json-out",
            "path_a_eval_artifacts/authority_runtime_v0_gwb_stale_action_decision.json",
            "--markdown-out",
            "path_a_eval_artifacts/authority_runtime_v0_gwb_stale_action_decision.md",
        ],
    )
    # Exit code 3 is the documented BLOCK_STALE_ACTION outcome, not a crash.
    assert completed.returncode == 3, completed.stderr
    for name in (
        "authority_runtime_v0_gwb_stale_action_decision.json",
        "authority_runtime_v0_gwb_stale_action_decision.md",
    ):
        assert (workspace / "path_a_eval_artifacts" / name).read_bytes() == (ARTIFACTS / name).read_bytes()


def test_historical_only_list_points_at_committed_artifacts():
    for name in HISTORICAL_ONLY:
        assert (ARTIFACTS / name).is_file(), name
