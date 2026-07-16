from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from agents.silent_omission_gate import evaluate_silent_omission_case


ROOT = Path(__file__).parent
FIXTURE = ROOT / "tests" / "fixtures" / "path_a_v3_silent_omission_2026_07_15.json"
ARTIFACT_DIR = ROOT / "path_a_eval_artifacts"


def _case_result(case: dict) -> dict:
    result = evaluate_silent_omission_case(case)
    expected = case["expected"]["future_bar"]
    matched = (
        result["allowed_clean_compliance"] is expected["allowed_clean_compliance"]
        and result["alarm_code"] == expected["alarm_code"]
        and result["undeclared_surface_ids"] == expected.get("undeclared_surface_ids", [])
    )
    if expected.get("footprint_receipt_id") is not None:
        matched = matched and result["receipts"].get("footprint_receipt_id") == expected["footprint_receipt_id"]
    return {
        "case_id": case["id"],
        "class": case["class"],
        "expected": expected,
        "actual": result,
        "matched_expected": matched,
    }


def build_artifact() -> dict:
    packet = json.loads(FIXTURE.read_text())
    case_results = [_case_result(case) for case in packet["cases"]]
    return {
        "artifact": "path_a_v3_silent_omission_pass_a",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "zero_model": True,
        "implementation": "agents.silent_omission_gate.evaluate_silent_omission_case",
        "frozen_packet": {
            "packet": packet["packet"],
            "fixture_path": str(FIXTURE.relative_to(ROOT)),
            "prereg": packet["prereg"],
            "prereg_freeze_commit": packet["prereg_freeze_commit"],
            "case_count": len(packet["cases"]),
            "adversary_authorship": packet.get("adversary_authorship", []),
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
        "# Path A v3 Silent-Omission PASS A",
        "",
        f"Generated: `{artifact['generated_at']}`",
        "",
        "Zero-model run against the frozen silent-omission / undeclared-surface fixture.",
        "",
        "## Summary",
        "",
        f"- Total cases: {artifact['summary']['total_cases']}",
        f"- Matched: {artifact['summary']['matched']}/{artifact['summary']['total_cases']}",
        f"- All cases matched: `{artifact['summary']['all_cases_matched']}`",
        "",
        "## Frozen Packet",
        "",
        f"- `{artifact['frozen_packet']['packet']}` — `{artifact['frozen_packet']['fixture_path']}` — freeze `{artifact['frozen_packet']['prereg_freeze_commit']}`",
        "",
        "## Per-Case Results",
        "",
    ]
    for row in artifact["case_results"]:
        actual = row["actual"]
        lines.extend(
            [
                f"### `{row['case_id']}`",
                "",
                f"- Class: `{row['class']}`",
                f"- Expected clean compliance: `{row['expected']['allowed_clean_compliance']}`",
                f"- Actual clean compliance: `{actual['allowed_clean_compliance']}`",
                f"- Expected alarm: `{row['expected']['alarm_code']}`",
                f"- Actual alarm: `{actual['alarm_code']}`",
                f"- Expected undeclared surfaces: `{json.dumps(row['expected'].get('undeclared_surface_ids', []))}`",
                f"- Actual undeclared surfaces: `{json.dumps(actual['undeclared_surface_ids'])}`",
                f"- Matched expected: `{row['matched_expected']}`",
                f"- Receipts: `{json.dumps(actual.get('receipts', {}), sort_keys=True)}`",
                f"- Reasons: `{'; '.join(actual['reasons'])}`",
                "",
            ]
        )
    path.write_text("\n".join(lines))


def main() -> None:
    artifact = build_artifact()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ARTIFACT_DIR.mkdir(exist_ok=True)
    json_path = ARTIFACT_DIR / f"path_a_v3_silent_omission_pass_a_{stamp}.json"
    md_path = ARTIFACT_DIR / f"path_a_v3_silent_omission_pass_a_{stamp}.md"
    json_path.write_text(json.dumps(artifact, indent=2, sort_keys=True))
    _write_markdown(artifact, md_path)
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
