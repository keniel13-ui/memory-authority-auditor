from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from agents.semantic_confirmer import relation_span_check


TEXTUAL_CASE_IDS = {
    "path_a_v1_supersession_backup_retention",
    "path_a_v1_supersession_api_key_rotation",
    "path_a_v1_supersession_sync_notes_location",
    "path_a_v1_scope_narrowing_refund_limit",
    "path_a_v1_scope_narrowing_prod_db_access",
    "path_a_v1_scope_narrowing_social_posting",
    "path_a_v1_transfer_incident_severity",
    "path_a_v1_transfer_purchase_approval",
    "path_a_v1_transfer_article_signoff",
}

IMPLICIT_CASE_IDS = {
    "path_a_v1_contradiction_logging_pii",
    "path_a_v1_contradiction_friday_deploys",
    "path_a_v1_contradiction_vendor_contact",
}

DEFAULT_RECORDED_ARTIFACT = Path("path_a_eval_artifacts/path_a_eval_20260709T202859Z.json")
DEFAULT_OUTPUT_DIR = Path("path_a_eval_artifacts")


def _utc_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _expected_pairs(case_result: dict) -> set[tuple[str, str]]:
    score = case_result["score"]
    return {(source, target) for (_rel, source, target) in score.get("expected_triplets", [])}


def _finding_pair(finding: dict) -> tuple[str, str]:
    return finding.get("source_item_id"), finding.get("target_item_id")


def _regate_finding(finding: dict) -> dict:
    check = relation_span_check(
        finding.get("cited_evidence_span", ""),
        finding.get("scope_terms", []),
    )
    return {
        "finding": finding,
        "relation_span": check,
        "survives_relation_span": check["passed"],
    }


def _summarize_engine(engine: dict) -> dict:
    textual_cases = 0
    textual_direction_caught_before = 0
    textual_direction_caught_after = 0
    textual_true_positive_losses = []
    implicit_cases = 0
    implicit_direction_caught = 0
    negative_false_fires_before = 0
    negative_false_fires_after = 0
    cases = []

    for case_result in engine["cases"]:
        case_id = case_result["case_id"]
        score = case_result["score"]
        regated = [_regate_finding(finding) for finding in case_result["confirmed_findings"]]
        surviving = [entry for entry in regated if entry["survives_relation_span"]]
        case_row = {
            "case_id": case_id,
            "class": case_result["class"],
            "v2_class": (
                "textual"
                if case_id in TEXTUAL_CASE_IDS
                else "implicit"
                if case_id in IMPLICIT_CASE_IDS
                else "negative"
            ),
            "confirmed_before": len(case_result["confirmed_findings"]),
            "confirmed_after_relation_span": len(surviving),
            "regated_findings": regated,
        }

        if case_id in TEXTUAL_CASE_IDS:
            textual_cases += 1
            expected_pairs = _expected_pairs(case_result)
            before_pairs = {_finding_pair(finding) for finding in case_result["confirmed_findings"]}
            after_pairs = {_finding_pair(entry["finding"]) for entry in surviving}
            before = expected_pairs <= before_pairs
            after = expected_pairs <= after_pairs
            textual_direction_caught_before += int(before)
            textual_direction_caught_after += int(after)
            if before and not after:
                textual_true_positive_losses.append(case_id)
            case_row["textual_direction_caught_before"] = before
            case_row["textual_direction_caught_after"] = after
        elif case_id in IMPLICIT_CASE_IDS:
            implicit_cases += 1
            implicit_direction_caught += int(score.get("direction_caught", False))
            case_row["implicit_policy"] = (
                "not relation-span gated; report as proposer-only, semantically inferred, "
                "not span-anchored"
            )
        elif not score.get("expected_positive"):
            false_before = not score.get("negative_passed", True)
            false_after = bool(surviving)
            negative_false_fires_before += int(false_before)
            negative_false_fires_after += int(false_after)
            case_row["negative_false_fire_before"] = false_before
            case_row["negative_false_fire_after_relation_span"] = false_after

        cases.append(case_row)

    return {
        "engine": engine["engine"],
        "summary": {
            "textual_cases": textual_cases,
            "textual_direction_caught_before": textual_direction_caught_before,
            "textual_direction_caught_after_relation_span": textual_direction_caught_after,
            "textual_true_positive_losses": textual_true_positive_losses,
            "implicit_cases": implicit_cases,
            "implicit_direction_caught": implicit_direction_caught,
            "negative_false_fires_before": negative_false_fires_before,
            "negative_false_fires_after_relation_span": negative_false_fires_after,
        },
        "cases": cases,
    }


def _write_markdown(result: dict, path: Path) -> None:
    lines = [
        "# Path A v2 PASS A Re-Gate",
        "",
        f"Run ID: `{result['run_id']}`",
        f"Recorded v1 artifact: `{result['recorded_v1_artifact']}`",
        "",
        "No model calls were made. This applies the frozen v2 relation-span clause to the already recorded v1 findings.",
        "",
        "## Engine Results",
        "",
    ]
    for engine in result["engines"]:
        summary = engine["summary"]
        lines.extend([
            f"### {engine['engine']}",
            "",
            f"- textual direction catches before: `{summary['textual_direction_caught_before']}/{summary['textual_cases']}`",
            f"- textual direction catches after relation-span: `{summary['textual_direction_caught_after_relation_span']}/{summary['textual_cases']}`",
            f"- textual true-positive losses: `{len(summary['textual_true_positive_losses'])}`",
            f"- implicit direction catches (reported lower-trust, not span-gated): `{summary['implicit_direction_caught']}/{summary['implicit_cases']}`",
            f"- negative false fires before: `{summary['negative_false_fires_before']}`",
            f"- negative false fires after relation-span: `{summary['negative_false_fires_after_relation_span']}`",
            "",
            "| Case | v2 class | Confirmed before | Confirmed after | Note |",
            "| --- | --- | ---: | ---: | --- |",
        ])
        for case in engine["cases"]:
            note = ""
            if case["v2_class"] == "textual":
                note = "kept" if case.get("textual_direction_caught_after") else "miss/lost"
            elif case["v2_class"] == "implicit":
                note = "lower-trust implicit"
            elif case.get("negative_false_fire_before") and not case.get("negative_false_fire_after_relation_span"):
                note = "blocked by relation-span"
            elif case.get("negative_false_fire_after_relation_span"):
                note = "false fire survived"
            lines.append(
                f"| `{case['case_id']}` | {case['v2_class']} | {case['confirmed_before']} | "
                f"{case['confirmed_after_relation_span']} | {note} |"
            )
        lines.append("")
    lines.extend([
        "## Boundary",
        "",
        "PASS A is a re-gate of frozen v1 artifacts. It measures the new deterministic clause only; it is not a fresh 21-case v2 model run.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recorded-artifact", default=str(DEFAULT_RECORDED_ARTIFACT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    recorded_path = Path(args.recorded_artifact)
    recorded = json.loads(recorded_path.read_text())
    run_id = _utc_slug()
    result = {
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "recorded_v1_artifact": str(recorded_path),
        "preregistration": "PATH_A_V2_PREREGISTRATION_2026-07-11.md",
        "engines": [_summarize_engine(engine) for engine in recorded["engines"]],
        "boundary": "PASS A only: zero model calls, applies v2 relation-span clause to recorded v1 findings.",
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"path_a_v2_pass_a_regate_{run_id}.json"
    md_path = output_dir / f"path_a_v2_pass_a_regate_{run_id}.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    _write_markdown(result, md_path)
    print(json.dumps({
        "json": str(json_path),
        "markdown": str(md_path),
        "engines": [engine["summary"] | {"engine": engine["engine"]} for engine in result["engines"]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
