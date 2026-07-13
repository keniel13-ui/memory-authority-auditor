from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from agents.memory_extractor import extract_memories
from agents.semantic_confirmer import confirm_authority_change

DEFAULT_FIXTURE = Path("tests/fixtures/path_a_authority_change_v3_2026_07_12.json")
DEFAULT_OUTPUT_DIR = Path("path_a_eval_artifacts")

# Frozen in PATH_A_V3_PREREGISTRATION_2026-07-12.md (commit 27fe726) before any
# fixture case or code existed: the current v2 gate is predicted to CONFIRM all
# five adversarial proposals. Confirmation = the prediction holding.
PREDICTIONS = {
    "path_a_v3_negation_trap_export_approval": {"predicted_confirmed": True, "prediction_id": "P0-1"},
    "path_a_v3_negation_trap_guest_badge": {"predicted_confirmed": True, "prediction_id": "P0-1"},
    "path_a_v3_direction_trap_privacy_rule": {"predicted_confirmed": True, "prediction_id": "P0-2"},
    "path_a_v3_direction_trap_escalation_rule": {"predicted_confirmed": True, "prediction_id": "P0-2"},
    "path_a_v3_hollow_anchor_retention_purge": {"predicted_confirmed": True, "prediction_id": "P0-3"},
}


def _utc_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    fixture = json.loads(Path(args.fixture).read_text())
    new_cases = [case for case in fixture["cases"] if case["id"] in PREDICTIONS]
    if len(new_cases) != len(PREDICTIONS):
        raise SystemExit(f"expected {len(PREDICTIONS)} frozen adversarial cases, found {len(new_cases)}")

    rows = []
    predictions_held = 0
    for case in new_cases:
        items = [item.to_dict() for item in extract_memories(case["text"])]
        proposal = case["pass0_adversarial_proposal"]
        result = confirm_authority_change(proposal, items, require_relation_span=True)
        confirmed = result["confirmed"]
        prediction = PREDICTIONS[case["id"]]
        held = confirmed == prediction["predicted_confirmed"]
        predictions_held += int(held)
        rows.append({
            "case_id": case["id"],
            "class": case["class"],
            "prediction_id": prediction["prediction_id"],
            "predicted_confirmed_by_v2_gate": prediction["predicted_confirmed"],
            "confirmed_by_v2_gate": confirmed,
            "prediction_held": held,
            "confirmer_result": result,
        })

    run_id = _utc_slug()
    artifact = {
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixture": args.fixture,
        "preregistration": "PATH_A_V3_PREREGISTRATION_2026-07-12.md",
        "prereg_freeze_commit": "27fe726",
        "fixture_commit": "f4cb6fb",
        "gate_under_test": "frozen v2 confirmer incl. relation-span clause, as shipped at e5dceaa",
        "boundary": (
            "PASS 0 only: zero model calls. Frozen adversarial proposals run directly against the "
            "frozen v2 confirmer. Proposer-independent by design; says nothing about whether a "
            "proposer would emit these lies unprompted."
        ),
        "summary": {
            "cases": len(rows),
            "confirmed_by_v2_gate": sum(int(r["confirmed_by_v2_gate"]) for r in rows),
            "predictions_held": predictions_held,
        },
        "cases": rows,
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"path_a_v3_pass0_regate_{run_id}.json"
    md_path = output_dir / f"path_a_v3_pass0_regate_{run_id}.md"
    json_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    lines = [
        "# Path A v3 PASS 0 Pre-Regate",
        "",
        f"Run ID: `{run_id}`",
        f"Pre-registration: `PATH_A_V3_PREREGISTRATION_2026-07-12.md` (freeze `27fe726`)",
        f"Fixture: `{args.fixture}` (commit `f4cb6fb`)",
        "",
        "No model calls were made. The five frozen adversarial proposals were run directly "
        "against the frozen v2 confirmer (all clauses, relation-span required).",
        "",
        "| Case | Class | Prediction | Predicted | v2 gate confirmed | Held |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['case_id']}` | {row['class']} | {row['prediction_id']} | "
            f"{'confirm' if row['predicted_confirmed_by_v2_gate'] else 'block'} | "
            f"{'CONFIRMED' if row['confirmed_by_v2_gate'] else 'BLOCKED'} | "
            f"{'yes' if row['prediction_held'] else 'NO'} |"
        )
    lines.extend([
        "",
        f"Summary: {artifact['summary']['confirmed_by_v2_gate']}/{len(rows)} adversarial proposals "
        f"confirmed by the published v2 gate; {predictions_held}/{len(rows)} frozen predictions held.",
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
