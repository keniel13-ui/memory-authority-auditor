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
        "prediction_id": "C0-1",
        "predicted_confirmed": True,
        "label": "bounded negative admitted by unchanged v2 gate",
    },
    "path_a_v3_universal_approval_all_regions": {
        "prediction_id": "C0-2",
        "predicted_confirmed": True,
        "label": "universal positive admitted by unchanged v2 gate",
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
        raise SystemExit("fixture cases do not match frozen carve-out C0 predictions")

    rows = []
    for case in cases:
        items = [item.to_dict() for item in extract_memories(case["text"])]
        proposal = case["c0_frozen_proposal"]
        result = confirm_authority_change(proposal, items, require_relation_span=True)
        prediction = PREDICTIONS[case["id"]]
        confirmed = result["confirmed"]
        rows.append({
            "case_id": case["id"],
            "class": case["class"],
            "prediction_id": prediction["prediction_id"],
            "label": prediction["label"],
            "predicted_confirmed_by_v2_gate": prediction["predicted_confirmed"],
            "confirmed_by_v2_gate": confirmed,
            "prediction_held": confirmed == prediction["predicted_confirmed"],
            "expected_relations_count": len(case.get("expected_relations", [])),
            "expected_no_relations_count": len(case.get("expected_no_relations", [])),
            "extracted_items": items,
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
        "gate_under_test": "unchanged v2 confirmer incl. relation-span clause",
        "boundary": (
            "C0 only: zero model calls and no carve-out implementation. The two frozen "
            "c0_frozen_proposal objects were run directly against the unchanged v2 confirmer. "
            "Results are reported separately so the bounded negative and universal positive "
            "cannot be averaged together."
        ),
        "summary": {
            "cases": len(rows),
            "confirmed_by_v2_gate": sum(int(row["confirmed_by_v2_gate"]) for row in rows),
            "predictions_held": sum(int(row["prediction_held"]) for row in rows),
            "bounded_negative_admitted": next(
                row["confirmed_by_v2_gate"]
                for row in rows
                if row["case_id"] == "path_a_v3_carveout_export_approval_eu"
            ),
            "universal_positive_admitted": next(
                row["confirmed_by_v2_gate"]
                for row in rows
                if row["case_id"] == "path_a_v3_universal_approval_all_regions"
            ),
        },
        "cases": rows,
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"path_a_v3_carveout_c0_regate_{run_id}.json"
    md_path = output_dir / f"path_a_v3_carveout_c0_regate_{run_id}.md"
    json_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    lines = [
        "# Path A v3 Carve-Out C0 Pre-Regate",
        "",
        f"Run ID: `{run_id}`",
        f"Pre-registration addendum: `PATH_A_V3_PREREGISTRATION_ADDENDUM_CARVEOUT_2026-07-12.md` (freeze `b1d44f9`)",
        f"Fixture additions: `{args.fixture}` (commit `48507de`)",
        "",
        "No model calls were made. No carve-out implementation exists in this run. The two frozen "
        "`c0_frozen_proposal` objects were run directly against the unchanged v2 confirmer.",
        "",
        "| Case | Class | Prediction | v2 gate confirmed | Held |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['case_id']}` | {row['class']} | {row['prediction_id']} | "
            f"{'CONFIRMED' if row['confirmed_by_v2_gate'] else 'BLOCKED'} | "
            f"{'yes' if row['prediction_held'] else 'NO'} |"
        )
    lines.extend([
        "",
        "## Separate C0 Results",
        "",
        f"- EU-only bounded negative admitted: `{'yes' if artifact['summary']['bounded_negative_admitted'] else 'no'}`",
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
            {k: row[k] for k in ("case_id", "confirmed_by_v2_gate", "prediction_held")}
            for row in rows
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
