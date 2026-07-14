from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from agents.relation_store_gate import evaluate_store_request


ROOT = Path(__file__).parent
FIXTURES = [
    ROOT / "tests" / "fixtures" / "path_a_v3_store_authority_2026_07_13.json",
    ROOT / "tests" / "fixtures" / "path_a_v3_provenance_disjointness_2026_07_13.json",
    ROOT / "tests" / "fixtures" / "path_a_v3_authority_roots_2026_07_14.json",
]
ARTIFACT_DIR = ROOT / "path_a_eval_artifacts"


def _expected_allowed(case: dict) -> bool:
    expected = case["expected"]
    if "allowed_by_declared_path_gate" in expected:
        return expected["allowed_by_declared_path_gate"]
    return expected["allowed"]


def _counts_toward_pass_bar(case: dict) -> bool:
    return case["expected"].get("counts_toward_pass_bar", True)


def _case_result(case: dict) -> dict:
    result = evaluate_store_request(case)
    expected = case["expected"]
    expected_allowed = _expected_allowed(case)
    expected_alarm = expected["alarm_code"]
    pass_bar_case = _counts_toward_pass_bar(case)
    matched = result["allowed"] is expected_allowed and result["alarm_code"] == expected_alarm
    if expected.get("resulting_tier") is not None:
        matched = matched and result["resulting_tier"] == expected["resulting_tier"]
    if expected.get("root_receipt_id") is not None:
        matched = matched and result["receipts"].get("root_receipt_id") == expected["root_receipt_id"]
    if expected.get("declared_shared_nodes") is not None:
        matched = matched and result["receipts"].get("declared_shared_nodes") == expected["declared_shared_nodes"]
    if expected.get("required_receipt") is not None:
        matched = matched and result.get("ceiling_note") == expected["required_receipt"]
    return {
        "case_id": case["id"],
        "class": case["class"],
        "counts_toward_pass_bar": pass_bar_case,
        "expected": expected,
        "actual": result,
        "matched_expected": matched,
    }


def _load_packets() -> list[dict]:
    packets = []
    for path in FIXTURES:
        packet = json.loads(path.read_text())
        packet["fixture_path"] = str(path.relative_to(ROOT))
        packets.append(packet)
    return packets


def build_artifact() -> dict:
    packets = _load_packets()
    case_results = []
    for packet in packets:
        for case in packet["cases"]:
            case_result = _case_result(case)
            case_result["packet"] = packet["packet"]
            case_results.append(case_result)

    pass_bar = [row for row in case_results if row["counts_toward_pass_bar"]]
    ceiling = [row for row in case_results if not row["counts_toward_pass_bar"]]
    return {
        "artifact": "path_a_v3_store_authority_pass_a",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "zero_model": True,
        "implementation": "agents.relation_store_gate.evaluate_store_request",
        "frozen_packets": [
            {
                "packet": packet["packet"],
                "fixture_path": packet["fixture_path"],
                "prereg_freeze_commit": packet["prereg_freeze_commit"],
                "case_count": len(packet["cases"]),
            }
            for packet in packets
        ],
        "summary": {
            "total_cases": len(case_results),
            "pass_bar_cases": len(pass_bar),
            "ceiling_cases_reported_separately": len(ceiling),
            "pass_bar_matched": sum(1 for row in pass_bar if row["matched_expected"]),
            "ceiling_matched": sum(1 for row in ceiling if row["matched_expected"]),
            "all_pass_bar_cases_matched": all(row["matched_expected"] for row in pass_bar),
            "all_reported_cases_matched": all(row["matched_expected"] for row in case_results),
        },
        "case_results": case_results,
    }


def _write_markdown(artifact: dict, path: Path) -> None:
    lines = [
        "# Path A v3 Store-Authority PASS A",
        "",
        f"Generated: `{artifact['generated_at']}`",
        "",
        "Zero-model run against frozen fixtures. This artifact evaluates deterministic store-side authority, promotion, grant-lifecycle, and declared-provenance checks only.",
        "",
        "## Summary",
        "",
        f"- Total cases: {artifact['summary']['total_cases']}",
        f"- Pass-bar cases: {artifact['summary']['pass_bar_cases']}",
        f"- Ceiling cases reported separately: {artifact['summary']['ceiling_cases_reported_separately']}",
        f"- Pass-bar matched: {artifact['summary']['pass_bar_matched']}/{artifact['summary']['pass_bar_cases']}",
        f"- Ceiling matched: {artifact['summary']['ceiling_matched']}/{artifact['summary']['ceiling_cases_reported_separately']}",
        f"- All pass-bar cases matched: `{artifact['summary']['all_pass_bar_cases_matched']}`",
        f"- All reported cases matched: `{artifact['summary']['all_reported_cases_matched']}`",
        "",
        "## Frozen Packets",
        "",
    ]
    for packet in artifact["frozen_packets"]:
        lines.append(f"- `{packet['packet']}` — `{packet['fixture_path']}` — freeze `{packet['prereg_freeze_commit']}` — {packet['case_count']} cases")
    lines.extend(["", "## Per-Case Results", ""])
    for row in artifact["case_results"]:
        actual = row["actual"]
        suffix = " (ceiling, not pass bar)" if not row["counts_toward_pass_bar"] else ""
        lines.extend(
            [
                f"### `{row['case_id']}`{suffix}",
                "",
                f"- Class: `{row['class']}`",
                f"- Expected allowed: `{_expected_allowed({'expected': row['expected']})}`",
                f"- Actual allowed: `{actual['allowed']}`",
                f"- Expected alarm: `{row['expected']['alarm_code']}`",
                f"- Actual alarm: `{actual['alarm_code']}`",
                f"- Resulting tier: `{actual['resulting_tier']}`",
                f"- Matched expected: `{row['matched_expected']}`",
                f"- Reasons: `{'; '.join(actual['reasons'])}`",
                f"- Receipts: `{json.dumps(actual.get('receipts', {}), sort_keys=True)}`",
                "",
            ]
        )
        if actual.get("ceiling_note"):
            lines.extend(
                [
                    f"- Ceiling note: `{actual['ceiling_note']}`",
                    f"- Actual independence: `{actual.get('actual_independence')}`",
                    "",
                ]
            )
    path.write_text("\n".join(lines))


def main() -> None:
    artifact = build_artifact()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ARTIFACT_DIR.mkdir(exist_ok=True)
    json_path = ARTIFACT_DIR / f"path_a_v3_store_authority_pass_a_{stamp}.json"
    md_path = ARTIFACT_DIR / f"path_a_v3_store_authority_pass_a_{stamp}.md"
    json_path.write_text(json.dumps(artifact, indent=2, sort_keys=True))
    _write_markdown(artifact, md_path)
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
