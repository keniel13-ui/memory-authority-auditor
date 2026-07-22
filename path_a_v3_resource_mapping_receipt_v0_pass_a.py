from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from agents.resource_mapping import evaluate_resource_mapping_case


ROOT = Path(__file__).parent
FIXTURE = ROOT / "tests" / "fixtures" / "path_a_v3_resource_mapping_receipt_v0_2026_07_21.json"
ARTIFACT_DIR = ROOT / "path_a_eval_artifacts"


def _actual_field(result: dict, field: str):
    if field in result:
        return result[field]
    return result["receipts"].get(field)


def main() -> int:
    packet = json.loads(FIXTURE.read_text())
    rows = []
    matches = 0
    for case in packet["cases"]:
        result = evaluate_resource_mapping_case(case, packet)
        checks = {
            field: _actual_field(result, field) == expected
            for field, expected in case["expected"].items()
        }
        matches += int(all(checks.values()))
        rows.append(
            {
                "case_id": case["id"],
                "class": case["class"],
                "expected": case["expected"],
                "actual": result,
                "checks": checks,
                "matches_expected": all(checks.values()),
            }
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact = {
        "run_id": f"path_a_v3_resource_mapping_receipt_v0_pass_a_{timestamp}",
        "fixture": str(FIXTURE.relative_to(ROOT)),
        "prereg": packet["prereg"],
        "packet_status": packet["status"],
        "cases": len(rows),
        "matches": matches,
        "all_match": matches == len(rows),
        "mapping_key": rows[0]["actual"]["mapping_key"],
        "rows": rows,
        "non_claims": packet["non_claims"],
    }
    ARTIFACT_DIR.mkdir(exist_ok=True)
    output = ARTIFACT_DIR / f"path_a_v3_resource_mapping_receipt_v0_pass_a_{timestamp}.json"
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"artifact": str(output), "cases": len(rows), "matches": matches, "all_match": artifact["all_match"]}, indent=2))
    return 0 if artifact["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
