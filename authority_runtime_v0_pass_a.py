from __future__ import annotations

import hashlib
import json
from pathlib import Path

from agents.anchor_contract import content_digest
from agents.authority_runtime import evaluate_authority_case, render_decision_markdown


ROOT = Path(__file__).parent
FIXTURE = ROOT / "tests" / "fixtures" / "authority_runtime_v0_gwb_dns_replay_2026_07_21.json"
ARTIFACT_JSON = ROOT / "path_a_eval_artifacts" / "authority_runtime_v0_pass_a_20260721.json"
ARTIFACT_MD = ROOT / "path_a_eval_artifacts" / "authority_runtime_v0_pass_a_20260721.md"


def _validate_expected(case: dict, result: dict) -> None:
    for field, expected in case["expected"].items():
        actual = result.get(field)
        if actual != expected:
            raise AssertionError(f"{case['id']} {field}: expected {expected!r}, got {actual!r}")
    expected_digest = content_digest({key: value for key, value in result.items() if key != "decision_digest"})
    if result["decision_digest"] != expected_digest:
        raise AssertionError(f"{case['id']}: decision digest does not bind the full receipt")


def run() -> dict:
    fixture_bytes = FIXTURE.read_bytes()
    packet = json.loads(fixture_bytes)
    results = []
    for case in packet["cases"]:
        result = evaluate_authority_case(case, packet)
        _validate_expected(case, result)
        results.append(result)

    flagship = next(
        result for result in results if result["case_id"] == "authority_runtime_ar1_real_gwb_stale_cutover"
    )
    artifact = {
        "schema": "authority_runtime_pass_a/v0",
        "fixture": str(FIXTURE.relative_to(ROOT)),
        "fixture_sha256": "sha256:" + hashlib.sha256(fixture_bytes).hexdigest(),
        "case_count": len(results),
        "expected_match_count": len(results),
        "decision_counts": {
            decision: sum(result["decision"] == decision for result in results)
            for decision in ("ALLOW", "BLOCK_STALE_ACTION", "CONFLICT", "UNKNOWN")
        },
        "flagship_case_id": flagship["case_id"],
        "flagship_decision": flagship["decision"],
        "flagship_decision_code": flagship["decision_code"],
        "flagship_decision_digest": flagship["decision_digest"],
        "mutation_authorized": flagship["mutation_authorized"],
        "results": results,
    }
    ARTIFACT_JSON.write_text(
        json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    ARTIFACT_MD.write_text(render_decision_markdown(flagship), encoding="utf-8")
    return artifact


def main() -> int:
    artifact = run()
    print(
        "Authority Runtime v0 PASS A: "
        f"{artifact['expected_match_count']}/{artifact['case_count']} frozen outcomes matched; "
        f"flagship={artifact['flagship_decision']}; mutation_authorized={artifact['mutation_authorized']}"
    )
    print(f"JSON: {ARTIFACT_JSON.relative_to(ROOT)}")
    print(f"Markdown: {ARTIFACT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
