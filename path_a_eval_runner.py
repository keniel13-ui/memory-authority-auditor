from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from agents.memory_extractor import extract_memories
from agents.semantic_confirmer import ALLOWED_RELATION_TYPES, CONFIDENCE_THRESHOLD, confirm_authority_changes
from agents.semantic_proposer import (
    SemanticProposerError,
    build_authority_change_prompt,
    call_anthropic,
    call_local_llama,
    parse_proposals,
)
from audit_pipeline import run_audit


FIXTURE = Path("tests/fixtures/path_a_authority_change_v0_2026_07_01.json")
ARTIFACT_DIR = Path("reports/path_a_eval")


SCORING_RULES = {
    "positive_caught": (
        "A positive case is caught only if the proposer emits at least one proposal that "
        "the deterministic confirmer turns into a confirmed finding whose "
        "(type, source_item_id, target_item_id) matches the fixture expected relation."
    ),
    "confidence": (
        "Fixture confidence values are replay placeholders and are never compared to model output. "
        "Proposal confidence is used only against the frozen 0.60 confirmer gate."
    ),
    "negative_pass": (
        "A topic-mention negative passes only if no confirmed forbidden finding is produced."
    ),
    "malformed": (
        "Malformed proposer output is counted per case and does not abort the run. "
        "Positive case with only malformed output is a miss. Negative case with malformed/no-parse "
        "output passes only if no forbidden confirmed finding results; malformed counts remain recorded."
    ),
    "positive_caught_direction": (
        "Secondary metric, frozen 2026-07-09 in PATH_A_V1_PREREGISTRATION before any v1 run: "
        "a positive is direction-caught if a confirmed finding matches the expected "
        "(source_item_id, target_item_id) pair with ANY allowed relation type. Confirmed findings "
        "always carry a verbatim citation and scope overlap by construction. The exact-label metric "
        "remains primary and may not be replaced by this one after results are seen."
    ),
}


def _utc_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _cases(fixture: Path) -> list[dict]:
    return json.loads(fixture.read_text())["cases"]


def _items(case: dict) -> list[dict]:
    return [item.to_dict() for item in extract_memories(case["text"])]


def _provider_for(engine: str) -> Callable[[str], str]:
    if engine == "anthropic":
        return call_anthropic
    if engine == "local_llama3.2":
        return call_local_llama
    raise ValueError(f"unsupported engine: {engine}")


def _proposal_triplet(proposal: dict) -> tuple[str, str, str]:
    return (
        proposal.get("type"),
        proposal.get("source_item_id"),
        proposal.get("target_item_id"),
    )


def _finding_triplet(finding: dict) -> tuple[str, str, str]:
    return (
        finding.get("relation_type"),
        finding.get("source_item_id"),
        finding.get("target_item_id"),
    )


def _expected_triplets(case: dict) -> set[tuple[str, str, str]]:
    return {_proposal_triplet(relation) for relation in case.get("expected_relations", [])}


def _forbidden_types(case: dict) -> set[str]:
    forbidden: set[str] = set()
    for entry in case.get("expected_no_relations", []):
        forbidden.update(entry.get("forbidden_types", []))
    return forbidden or set(ALLOWED_RELATION_TYPES)


def _parse_case_output(text: str) -> tuple[list[dict], list[str]]:
    try:
        return parse_proposals(text), []
    except SemanticProposerError as error:
        return [], [str(error)]


def _score_confirmed(case: dict, confirmed: dict) -> dict:
    expected = _expected_triplets(case)
    findings = confirmed["findings"]
    finding_triplets = {_finding_triplet(finding) for finding in findings}

    if expected:
        caught = expected <= finding_triplets
        expected_pairs = {(source, target) for (_rel, source, target) in expected}
        finding_pairs = {(source, target) for (_rel, source, target) in finding_triplets}
        direction_caught = expected_pairs <= finding_pairs
        return {
            "expected_positive": True,
            "caught": caught,
            "direction_caught": direction_caught,
            "missed": not caught,
            "negative_passed": None,
            "expected_triplets": sorted(expected),
            "confirmed_triplets": sorted(finding_triplets),
        }

    forbidden = _forbidden_types(case)
    forbidden_findings = [
        finding
        for finding in findings
        if finding.get("relation_type") in forbidden
    ]
    return {
        "expected_positive": False,
        "caught": None,
        "missed": None,
        "negative_passed": not forbidden_findings,
        "forbidden_types": sorted(forbidden),
        "forbidden_confirmed_count": len(forbidden_findings),
        "confirmed_triplets": sorted(finding_triplets),
    }


def _confirm_without_citation(proposals: list[dict], items: list[dict]) -> dict:
    """Ablation: ids/type/scope/confidence only; cited evidence span ignored."""
    items_by_id = {item["id"]: item for item in items}
    findings = []
    needs_human_judgment = []
    for proposal in proposals:
        reasons: list[str] = []
        source = items_by_id.get(proposal.get("source_item_id"))
        target = items_by_id.get(proposal.get("target_item_id"))
        relation_type = proposal.get("type")
        confidence = proposal.get("confidence")
        if relation_type not in ALLOWED_RELATION_TYPES:
            reasons.append("unsupported relation type")
        if source is None:
            reasons.append("source item does not exist")
        if target is None:
            reasons.append("target item does not exist")
        if not isinstance(confidence, int | float):
            reasons.append("missing or invalid confidence")
        elif float(confidence) < CONFIDENCE_THRESHOLD:
            reasons.append("confidence below v0 threshold")
        scope_terms = proposal.get("scope_terms", [])
        if source is not None and target is not None:
            source_text = " ".join(source["text"].lower().split())
            target_text = " ".join(target["text"].lower().split())
            if not scope_terms or not any(
                " ".join(term.lower().split()) in source_text
                and " ".join(term.lower().split()) in target_text
                for term in scope_terms
            ):
                reasons.append("no deterministic scope overlap between source and target")
        if reasons:
            needs_human_judgment.append({"proposal": proposal, "reasons": reasons})
            continue
        findings.append({
            "type": "semantic_authority_change_no_citation_ablation",
            "relation_type": relation_type,
            "source_item_id": source["id"],
            "target_item_id": target["id"],
            "scope_terms": scope_terms,
            "confidence": float(confidence),
        })
    return {
        "findings": findings,
        "needs_human_judgment": needs_human_judgment,
    }


def _score_remove_confirmer(case: dict, proposals: list[dict]) -> dict:
    expected = _expected_triplets(case)
    proposal_triplets = {_proposal_triplet(proposal) for proposal in proposals}
    if expected:
        return {
            "would_count_as_caught_without_confirmation": expected <= proposal_triplets,
            "proposal_triplets": sorted(proposal_triplets),
        }
    forbidden = _forbidden_types(case)
    forbidden_proposals = [
        proposal
        for proposal in proposals
        if proposal.get("type") in forbidden
    ]
    return {
        "would_false_fire_without_confirmation": bool(forbidden_proposals),
        "forbidden_proposal_count": len(forbidden_proposals),
        "proposal_triplets": sorted(proposal_triplets),
    }


def _lexical_result(case: dict) -> dict:
    result = run_audit(case["text"])
    conflicts = result["conflicts"]
    return {
        "finding_types": [conflict["type"] for conflict in conflicts],
        "stale_instruction_count": sum(1 for conflict in conflicts if conflict["type"] == "stale_instruction"),
        "missing_authority_layer": any(conflict["type"] == "missing_authority_layer" for conflict in conflicts),
    }


def run_engine(engine: str, cases: list[dict]) -> dict:
    provider = _provider_for(engine)
    case_results = []
    malformed_count = 0
    positives = 0
    positives_caught = 0
    positives_caught_direction = 0
    negatives = 0
    negatives_passed = 0
    remove_confirmer_false_fires = 0
    remove_citation_false_fires = 0

    for case in cases:
        items = _items(case)
        prompt = build_authority_change_prompt(items)
        raw_output = ""
        malformed_reasons: list[str] = []
        try:
            raw_output = provider(prompt)
            proposals, malformed_reasons = _parse_case_output(raw_output)
        except Exception as error:  # per-case malformed/degraded bucket, never abort the run
            proposals = []
            malformed_reasons = [f"{type(error).__name__}: {error}"]

        if malformed_reasons:
            malformed_count += 1

        confirmed = confirm_authority_changes(proposals, items)
        score = _score_confirmed(case, confirmed)
        no_confirmer = _score_remove_confirmer(case, proposals)
        no_citation = _score_confirmed(case, _confirm_without_citation(proposals, items))
        lexical = _lexical_result(case)

        if score["expected_positive"]:
            positives += 1
            positives_caught += int(score["caught"])
            positives_caught_direction += int(score["direction_caught"])
        else:
            negatives += 1
            negatives_passed += int(score["negative_passed"])
            remove_confirmer_false_fires += int(no_confirmer["would_false_fire_without_confirmation"])
            remove_citation_false_fires += int(not no_citation["negative_passed"])

        case_results.append({
            "case_id": case["id"],
            "class": case["class"],
            "malformed": bool(malformed_reasons),
            "malformed_reasons": malformed_reasons,
            "proposal_count": len(proposals),
            "proposals": proposals,
            "confirmed_findings": confirmed["findings"],
            "needs_human_judgment": confirmed["needs_human_judgment"],
            "score": score,
            "ablation_remove_confirmer": no_confirmer,
            "ablation_remove_citation_requirement": no_citation,
            "lexical_baseline_current_detector": lexical,
            "raw_output": raw_output,
        })

    return {
        "engine": engine,
        "summary": {
            "cases": len(cases),
            "positives": positives,
            "positives_caught": positives_caught,
            "positives_caught_direction": positives_caught_direction,
            "positive_misses": positives - positives_caught,
            "negatives": negatives,
            "negatives_passed": negatives_passed,
            "negative_false_fires": negatives - negatives_passed,
            "malformed_cases": malformed_count,
            "remove_confirmer_negative_false_fires": remove_confirmer_false_fires,
            "remove_citation_negative_false_fires": remove_citation_false_fires,
        },
        "cases": case_results,
    }


def _write_markdown(result: dict, path: Path) -> None:
    lines = [
        "# Path A v0 Evaluation Run",
        "",
        f"Run ID: `{result['run_id']}`",
        f"Fixture: `{result['fixture']}`",
        "",
        "## Frozen Scoring Rules",
        "",
    ]
    for key, value in result["scoring_rules"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Engine Results", ""])
    for engine in result["engines"]:
        summary = engine["summary"]
        lines.extend([
            f"### {engine['engine']}",
            "",
            f"- positives caught: `{summary['positives_caught']}/{summary['positives']}`",
            f"- positive misses: `{summary['positive_misses']}`",
            f"- negatives passed: `{summary['negatives_passed']}/{summary['negatives']}`",
            f"- negative false fires: `{summary['negative_false_fires']}`",
            f"- malformed cases: `{summary['malformed_cases']}`",
            f"- remove-confirmer negative false fires: `{summary['remove_confirmer_negative_false_fires']}`",
            f"- remove-citation negative false fires: `{summary['remove_citation_negative_false_fires']}`",
            "",
            "| Case | Class | Proposals | Confirmed | Malformed | Score |",
            "| --- | --- | ---: | ---: | --- | --- |",
        ])
        for case in engine["cases"]:
            score = case["score"]
            if score["expected_positive"]:
                score_text = "caught" if score["caught"] else "miss"
            else:
                score_text = "negative_pass" if score["negative_passed"] else "negative_false_fire"
            lines.append(
                f"| `{case['case_id']}` | {case['class']} | {case['proposal_count']} | "
                f"{len(case['confirmed_findings'])} | {case['malformed']} | {score_text} |"
            )
        lines.append("")
    lines.extend([
        "## Boundary",
        "",
        "This is a recorded eval artifact, not a public claim. Ka'el and Fable must re-verify from artifacts before interpretation.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engines", default="anthropic,local_llama3.2")
    parser.add_argument("--output-dir", default=str(ARTIFACT_DIR))
    parser.add_argument("--fixture", default=str(FIXTURE))
    args = parser.parse_args()

    run_id = _utc_slug()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fixture_path = Path(args.fixture)
    cases = _cases(fixture_path)
    engines = [engine.strip() for engine in args.engines.split(",") if engine.strip()]
    result = {
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixture": str(fixture_path),
        "scoring_rules": SCORING_RULES,
        "engines": [run_engine(engine, cases) for engine in engines],
        "boundary": "No public claim from this artifact until Ka'el and Fable re-verify.",
    }
    json_path = output_dir / f"path_a_eval_{run_id}.json"
    md_path = output_dir / f"path_a_eval_{run_id}.md"
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
