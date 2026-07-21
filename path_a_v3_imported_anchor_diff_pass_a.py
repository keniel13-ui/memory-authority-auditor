from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from agents.imported_anchor_diff import evaluate_imported_anchor_case


ROOT = Path(__file__).parent
FIXTURE = ROOT / "tests" / "fixtures" / "path_a_v3_imported_anchor_diff_2026_07_21.json"
ARTIFACT_DIR = ROOT / "path_a_eval_artifacts"
FREEZE_COMMIT = "b476cf3"


def _case_result(case: dict) -> dict:
    actual = evaluate_imported_anchor_case(case)
    expected = case["expected"]
    checks = {
        "alarm_code": actual["alarm_code"] == expected["alarm_code"],
        "derived_surface_count": actual["receipts"]["derived_surface_count"] == expected["derived_surface_count"],
        "semantic_aligned_count": actual["receipts"]["semantic_aligned_count"] == expected["semantic_aligned_count"],
        "fixture_only_count": actual["receipts"]["fixture_only_count"] == expected["fixture_only_count"],
        "imported_only_count": actual["receipts"]["imported_only_count"] == expected["imported_only_count"],
        "unresolved_event_count": actual["receipts"]["unresolved_event_count"] == expected["unresolved_event_count"],
    }
    if "missing_from_considered_count" in expected:
        checks["missing_from_considered_count"] = (
            actual["receipts"]["missing_from_considered_count"] == expected["missing_from_considered_count"]
        )
    if "pre_ledger_birth_event_ids" in expected:
        checks["pre_ledger_birth_event_ids"] = (
            actual["pre_ledger_birth_event_ids"] == expected["pre_ledger_birth_event_ids"]
        )
    if "unresolved_reasons" in expected:
        checks["unresolved_reasons"] = (
            [row["reason"] for row in actual["unresolved_events"]] == expected["unresolved_reasons"]
        )
    if "silent_omission_alarm_code" in expected:
        checks["silent_omission_alarm_code"] = (
            actual["shipped_gate_receipts"]["silent_omission"]["alarm_code"]
            == expected["silent_omission_alarm_code"]
        )
    if "considered_set_alarm_code" in expected:
        checks["considered_set_alarm_code"] = (
            actual["shipped_gate_receipts"]["considered_set"]["alarm_code"]
            == expected["considered_set_alarm_code"]
        )
    if "considered_set_identity_break" in expected:
        checks["considered_set_identity_break"] = (
            actual["receipts"]["considered_set_identity_break"] is expected["considered_set_identity_break"]
        )
    return {
        "case_id": case["id"],
        "source_case_id": case.get("source_case_id"),
        "class": case["class"],
        "expected": expected,
        "actual": actual,
        "checks": checks,
        "matched_expected": all(checks.values()),
    }


def build_artifact() -> dict:
    packet = json.loads(FIXTURE.read_text())
    case_results = [_case_result(case) for case in packet["cases"]]
    return {
        "artifact": "path_a_v3_imported_anchor_diff_pass_a",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "zero_model": True,
        "implementation": "agents.imported_anchor_diff.evaluate_imported_anchor_case",
        "frozen_packet": {
            "packet": packet["packet"],
            "fixture_path": str(FIXTURE.relative_to(ROOT)),
            "prereg": packet["prereg"],
            "freeze_commit": FREEZE_COMMIT,
            "case_count": len(packet["cases"]),
            "derivation_policy": packet["derivation_policy"],
        },
        "summary": {
            "total_cases": len(case_results),
            "matched": sum(1 for row in case_results if row["matched_expected"]),
            "all_cases_matched": all(row["matched_expected"] for row in case_results),
        },
        "case_results": case_results,
    }


def _write_markdown(artifact: dict, path: Path) -> None:
    lines = [
        "# Path A v3 Imported-Anchor Diff PASS A",
        "",
        f"Generated: `{artifact['generated_at']}`",
        "",
        "Zero-model comparison of imported foreign events, fixture expected surfaces, proposer emissions, and shipped gate behavior.",
        "",
        "## Summary",
        "",
        f"- Total cases: {artifact['summary']['total_cases']}",
        f"- Matched: {artifact['summary']['matched']}/{artifact['summary']['total_cases']}",
        f"- All cases matched: `{artifact['summary']['all_cases_matched']}`",
        f"- Freeze commit: `{artifact['frozen_packet']['freeze_commit']}`",
        f"- Derivation policy: `{artifact['frozen_packet']['derivation_policy']}`",
        "",
        "## Per-Case Diff",
        "",
    ]
    for row in artifact["case_results"]:
        actual = row["actual"]
        shipped = actual["shipped_gate_receipts"]
        lines.extend(
            [
                f"### `{row['case_id']}`",
                "",
                f"- Source frozen case: `{row['source_case_id']}`",
                f"- Class: `{row['class']}`",
                f"- Imported alarm: `{actual['alarm_code']}`",
                f"- Derived / aligned / fixture-only / imported-only: `{actual['receipts']['derived_surface_count']} / {actual['receipts']['semantic_aligned_count']} / {actual['receipts']['fixture_only_count']} / {actual['receipts']['imported_only_count']}`",
                f"- Missing from considered-set: `{actual['receipts']['missing_from_considered_count']}`",
                f"- Unresolved events: `{json.dumps(actual['unresolved_events'], sort_keys=True)}`",
                f"- Pre-ledger-birth events: `{json.dumps(actual['pre_ledger_birth_event_ids'])}`",
                f"- Shipped silent-omission alarm: `{shipped.get('silent_omission', {}).get('alarm_code')}`",
                f"- Shipped considered-set alarm: `{shipped.get('considered_set', {}).get('alarm_code')}`",
                f"- Cross-source identity break: `{actual['receipts'].get('considered_set_identity_break', False)}`",
                f"- Matched frozen bar: `{row['matched_expected']}`",
                "",
            ]
        )
    path.write_text("\n".join(lines))


def main() -> None:
    artifact = build_artifact()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ARTIFACT_DIR.mkdir(exist_ok=True)
    json_path = ARTIFACT_DIR / f"path_a_v3_imported_anchor_diff_pass_a_{stamp}.json"
    md_path = ARTIFACT_DIR / f"path_a_v3_imported_anchor_diff_pass_a_{stamp}.md"
    json_path.write_text(json.dumps(artifact, indent=2, sort_keys=True))
    _write_markdown(artifact, md_path)
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
