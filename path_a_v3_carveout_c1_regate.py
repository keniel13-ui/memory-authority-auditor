from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from agents.memory_extractor import extract_memories
from agents.semantic_confirmer import confirm_authority_change

DEFAULT_FIXTURE = Path("tests/fixtures/path_a_authority_change_v3_carveout_additions_2026_07_12.json")
DEFAULT_OUTPUT_DIR = Path("path_a_eval_artifacts")

PREDICTIONS = {
    "path_a_v3_carveout_export_approval_eu": {
        "prediction_id": "C1-1",
        "expected_confirmed": False,
        "label": "bounded negative blocked by carve-out clause",
    },
    "path_a_v3_universal_approval_all_regions": {
        "prediction_id": "C1-2",
        "expected_confirmed": True,
        "label": "universal positive survives carve-out clause",
    },
}


def _utc_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    fixture = json.loads(Path(args.fixture).read_text())
    cases = fixture["cases"]
    if {case["id"] for case in cases} != set(PREDICTIONS):
        raise SystemExit("fixture cases do not match frozen carve-out C1 predictions")

    rows = []
    for case in cases:
        items = [item.to_dict() for item in extract_memories(case["text"])]
        result = confirm_authority_change(case["c0_frozen_proposal"], items, require_relation_span=True)
        prediction = PREDICTIONS[case["id"]]
        confirmed = result["confirmed"]
        rows.append({
            "case_id": case["id"],
            "class": case["class"],
            "prediction_id": prediction["prediction_id"],
            "label": prediction["label"],
            "expected_confirmed_after_patch": prediction["expected_confirmed"],
            "confirmed_after_patch": confirmed,
            "expectation_held": confirmed == prediction["expected_confirmed"],
            "confirmer_result": result,
        })

    run_id = _utc_slug()
    artifact = {
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixture": args.fixture,
        "preregistration_addendum": "PATH_A_V3_PREREGISTRATION_ADDENDUM_CARVEOUT_2026-07-12.md",
        "prereg_freeze_commit": "b1d44f9",
        "fixture_commit": "48507de",
        "c0_baseline_commit": "78d66a3",
        "gate_under_test": "patched confirmer with bounded customer carve-out clause",
        "boundary": (
            "C1 only: the same two frozen c0_frozen_proposal objects are run after the "
            "carve-out defense. No fixture or prediction was changed after observing C0."
        ),
        "summary": {
            "cases": len(rows),
            "confirmed_after_patch": sum(int(row["confirmed_after_patch"]) for row in rows),
            "expectations_held": sum(int(row["expectation_held"]) for row in rows),
            "bounded_negative_blocked": not next(
                row["confirmed_after_patch"]
                for row in rows
                if row["case_id"] == "path_a_v3_carveout_export_approval_eu"
            ),
            "universal_positive_admitted": next(
                row["confirmed_after_patch"]
                for row in rows
                if row["case_id"] == "path_a_v3_universal_approval_all_regions"
            ),
        },
        "cases": rows,
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"path_a_v3_carveout_c1_regate_{run_id}.json"
    md_path = output_dir / f"path_a_v3_carveout_c1_regate_{run_id}.md"
    json_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    lines = [
        "# Path A v3 Carve-Out C1 Re-Gate",
        "",
        f"Run ID: `{run_id}`",
        f"Pre-registration addendum: `PATH_A_V3_PREREGISTRATION_ADDENDUM_CARVEOUT_2026-07-12.md` (freeze `b1d44f9`)",
        f"Fixture additions: `{args.fixture}` (commit `48507de`)",
        "C0 baseline commit: `78d66a3`",
        "",
        "The same two frozen `c0_frozen_proposal` objects were run after the carve-out defense. "
        "The fixture and predictions were not changed after C0.",
        "",
        "| Case | Class | Expected after patch | Confirmed after patch | Held |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['case_id']}` | {row['class']} | "
            f"{'CONFIRM' if row['expected_confirmed_after_patch'] else 'BLOCK'} | "
            f"{'CONFIRMED' if row['confirmed_after_patch'] else 'BLOCKED'} | "
            f"{'yes' if row['expectation_held'] else 'NO'} |"
        )
    lines.extend([
        "",
        "## Separate C1 Results",
        "",
        f"- EU-only bounded negative blocked: `{'yes' if artifact['summary']['bounded_negative_blocked'] else 'no'}`",
        f"- Universal all-regions positive admitted: `{'yes' if artifact['summary']['universal_positive_admitted'] else 'no'}`",
        "",
        "## Boundary",
        "",
        artifact["boundary"],
        "",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "json": str(json_path),
        "markdown": str(md_path),
        "summary": artifact["summary"],
        "cases": [
            {k: row[k] for k in ("case_id", "confirmed_after_patch", "expectation_held")}
            for row in rows
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
