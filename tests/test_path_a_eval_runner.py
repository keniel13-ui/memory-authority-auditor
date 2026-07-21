from __future__ import annotations

import path_a_eval_runner as runner


def _positive_case() -> dict:
    return {
        "id": "malformed_positive",
        "class": "positive",
        "text": "A newer instruction supersedes an older instruction.",
        "expected_relations": [
            {
                "type": "supersedes",
                "source_item_id": "M002",
                "target_item_id": "M001",
            }
        ],
        "expected_no_relations": [],
    }


def _negative_case() -> dict:
    return {
        "id": "malformed_negative",
        "class": "negative",
        "text": "Two instructions mention the same topic without changing authority.",
        "expected_relations": [],
        "expected_no_relations": [{"forbidden_types": ["supersedes"]}],
    }


def _stub_eval_dependencies(monkeypatch, outputs: list[str]) -> None:
    pending = iter(outputs)
    monkeypatch.setattr(runner, "_provider_for", lambda _engine: lambda _prompt: next(pending))
    monkeypatch.setattr(runner, "_items", lambda _case: [])
    monkeypatch.setattr(runner, "build_authority_change_prompt", lambda _items: "prompt")
    monkeypatch.setattr(
        runner,
        "confirm_authority_changes",
        lambda _proposals, _items: {"findings": [], "needs_human_judgment": []},
    )
    monkeypatch.setattr(runner, "_lexical_result", lambda _case: {})


def test_malformed_positive_and_negative_are_preserved_but_unscored(monkeypatch, tmp_path):
    _stub_eval_dependencies(monkeypatch, ["bad positive", "bad negative"])
    monkeypatch.setattr(
        runner,
        "_parse_case_output",
        lambda _text: ([], ["invalid proposer JSON"]),
    )

    result = runner.run_engine("anthropic", [_positive_case(), _negative_case()])

    assert result["summary"] == {
        "cases": 2,
        "scored_cases": 0,
        "unscored_malformed_cases": 2,
        "positives": 0,
        "positives_caught": 0,
        "positives_caught_direction": 0,
        "positive_misses": 0,
        "negatives": 0,
        "negatives_passed": 0,
        "negative_false_fires": 0,
        "malformed_cases": 2,
        "remove_confirmer_negative_false_fires": 0,
        "remove_citation_negative_false_fires": 0,
    }
    assert [case["case_id"] for case in result["cases"]] == [
        "malformed_positive",
        "malformed_negative",
    ]
    assert all(case["malformed"] for case in result["cases"])
    assert all(not case["included_in_aggregates"] for case in result["cases"])
    assert [case["raw_output"] for case in result["cases"]] == ["bad positive", "bad negative"]
    assert all(case["malformed_reasons"] == ["invalid proposer JSON"] for case in result["cases"])
    assert all(
        case["score"]["aggregate_exclusion_reason"] == "malformed_proposer_output"
        for case in result["cases"]
    )
    assert result["cases"][0]["score"]["caught"] is None
    assert result["cases"][0]["score"]["missed"] is None
    assert result["cases"][1]["score"]["negative_passed"] is None
    unscored_ablation = {
        "unscored": True,
        "reason": "malformed_proposer_output",
    }
    assert all(
        case["ablation_remove_confirmer"] == unscored_ablation
        for case in result["cases"]
    )
    assert all(
        case["ablation_remove_citation_requirement"] == unscored_ablation
        for case in result["cases"]
    )

    markdown_path = tmp_path / "malformed.md"
    runner._write_markdown(
        {
            "run_id": "focused-regression",
            "fixture": "in-memory",
            "scoring_rules": runner.SCORING_RULES,
            "engines": [result],
        },
        markdown_path,
    )
    markdown = markdown_path.read_text()
    assert "scored cases: `0/2`" in markdown
    assert "malformed cases excluded from aggregates: `2`" in markdown
    assert (
        "| `malformed_negative` | negative | 0 | 0 | True | unscored_malformed |"
        in markdown
    )
    assert runner.PUBLICATION_AUDIT_BOUNDARY in markdown
    assert "Fable" not in markdown


def test_well_formed_case_still_scores_beside_malformed_exclusion(monkeypatch):
    _stub_eval_dependencies(monkeypatch, ["bad positive", "valid negative"])
    monkeypatch.setattr(
        runner,
        "_parse_case_output",
        lambda text: ([], ["invalid proposer JSON"]) if text.startswith("bad") else ([], []),
    )

    result = runner.run_engine("anthropic", [_positive_case(), _negative_case()])

    assert result["summary"]["cases"] == 2
    assert result["summary"]["scored_cases"] == 1
    assert result["summary"]["unscored_malformed_cases"] == 1
    assert result["summary"]["positives"] == 0
    assert result["summary"]["negatives"] == 1
    assert result["summary"]["negatives_passed"] == 1
    assert result["summary"]["negative_false_fires"] == 0
    assert result["cases"][0]["included_in_aggregates"] is False
    assert result["cases"][1]["included_in_aggregates"] is True
    assert result["cases"][1]["score"]["aggregate_exclusion_reason"] is None
    assert (
        result["cases"][1]["ablation_remove_confirmer"][
            "would_false_fire_without_confirmation"
        ]
        is False
    )
    assert (
        result["cases"][1]["ablation_remove_citation_requirement"]["negative_passed"]
        is True
    )
