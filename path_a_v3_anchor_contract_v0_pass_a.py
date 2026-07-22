from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from agents.anchor_contract import canonical_json, evaluate_anchor_contract_case


ROOT = Path(__file__).parent
FIXTURE = ROOT / "tests" / "fixtures" / "path_a_v3_anchor_contract_v0_2026_07_21.json"
ARTIFACT_DIR = ROOT / "path_a_eval_artifacts"
PREREG_COMMIT = "7eab8a8"
FIXTURE_COMMIT = "9a6a67e"


def _actual_field(result: dict, field: str):
    if field == "surface_key":
        return result["surface_keys"][0] if result["surface_keys"] else None
    if field == "surface_payload":
        return result["derived_surfaces"][0]["surface_payload"] if result["derived_surfaces"] else None
    if field == "canonical_json":
        return canonical_json(result["derived_surfaces"][0]["surface_payload"])
    if field == "surface_keys":
        return result["surface_keys"]
    if field in result:
        return result[field]
    return result["receipts"].get(field)


def _case_result(case: dict, packet: dict) -> dict:
    actual = evaluate_anchor_contract_case(case, packet)
    checks = {
        field: _actual_field(actual, field) == expected
        for field, expected in case["expected"].items()
    }
    return {
        "case_id": case["id"],
        "class": case["class"],
        "expected": case["expected"],
        "actual": actual,
        "checks": checks,
        "matched_expected": all(checks.values()),
    }


def build_artifact() -> dict:
    packet = json.loads(FIXTURE.read_text())
    case_results = [_case_result(case, packet) for case in packet["cases"]]
    return {
        "artifact": "path_a_v3_anchor_contract_v0_pass_a",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "zero_model": True,
        "implementation": "agents.anchor_contract.evaluate_anchor_contract_case",
        "frozen_packet": {
            "packet": packet["packet"],
            "fixture_path": str(FIXTURE.relative_to(ROOT)),
            "prereg": packet["prereg"],
            "prereg_commit": PREREG_COMMIT,
            "fixture_commit": FIXTURE_COMMIT,
            "case_count": len(packet["cases"]),
            "contract_objects": list(packet["contract_objects"].keys()),
            "canonicalization": packet["standards_profile"]["canonicalization"],
            "digest": packet["standards_profile"]["digest"],
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
        "# Path A v3 Anchor Contract v0 PASS A",
        "",
        f"Generated: `{artifact['generated_at']}`",
        "",
        "Zero-model run against the frozen Anchor Contract v0 packet.",
        "",
        "## Summary",
        "",
        f"- Total cases: {artifact['summary']['total_cases']}",
        f"- Matched: {artifact['summary']['matched']}/{artifact['summary']['total_cases']}",
        f"- All cases matched: `{artifact['summary']['all_cases_matched']}`",
        f"- Preregistration: `{artifact['frozen_packet']['prereg_commit']}`",
        f"- Fixture: `{artifact['frozen_packet']['fixture_commit']}`",
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
                f"- Alarm: `{actual['alarm_code']}`",
                f"- Derived surfaces: `{actual['receipts']['derived_surface_count']}`",
                f"- Surface keys: `{json.dumps(actual['surface_keys'])}`",
                f"- Matched expected: `{row['matched_expected']}`",
                f"- Checks: `{json.dumps(row['checks'], sort_keys=True)}`",
                f"- Reasons: `{'; '.join(actual['reasons'])}`",
                "",
            ]
        )
    path.write_text("\n".join(lines))


def main() -> None:
    artifact = build_artifact()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ARTIFACT_DIR.mkdir(exist_ok=True)
    json_path = ARTIFACT_DIR / f"path_a_v3_anchor_contract_v0_pass_a_{stamp}.json"
    md_path = ARTIFACT_DIR / f"path_a_v3_anchor_contract_v0_pass_a_{stamp}.md"
    json_path.write_text(json.dumps(artifact, indent=2, sort_keys=True))
    _write_markdown(artifact, md_path)
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
