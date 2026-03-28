# -*- coding: utf-8 -*-
"""Tests for the offline runtime eval harness."""

import json
import shutil
from pathlib import Path

import src.runtime as runtime


ROOT_DIR = Path(__file__).resolve().parents[1]
FIXTURE_CASES_DIR = ROOT_DIR / "evals" / "cases"


def _copy_cases(tmp_path):
    target_dir = tmp_path / "cases"
    shutil.copytree(FIXTURE_CASES_DIR, target_dir)
    return target_dir


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_runtime_eval_harness_runs_cases_and_writes_summary(tmp_path):
    harness_cls = getattr(runtime, "RuntimeEvalHarness", None)
    assert harness_cls is not None

    cases_dir = _copy_cases(tmp_path)
    harness = harness_cls(runtime_dir=tmp_path / "runtime", eval_dir=tmp_path / "evals")

    suite_result = harness.run_suite(cases_dir)

    assert suite_result["cases_total"] == 3
    assert suite_result["cases_passed"] == 3
    assert suite_result["cases_failed"] == 0
    assert all(case_result["passed"] for case_result in suite_result["results"])

    wrapped_case = next(
        case_result for case_result in suite_result["results"] if case_result["case_id"] == "wrapped_alignment_success"
    )
    assert wrapped_case["actual"]["output_alignments"] == ["center", "justify"]
    assert wrapped_case["actual"]["output_paragraph_texts"] == ["论文标题", "这是正文。"]

    summary_path = Path(suite_result["summary_path"])
    assert summary_path.exists()
    results_path = summary_path.with_name("results.jsonl")
    assert results_path.exists()
    results_lines = results_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(results_lines) == 3

    summary = _read_json(summary_path)
    assert summary["schema_version"] == "formulaai.eval_suite.v1"
    assert summary["cases_total"] == 3
    assert summary["cases_passed"] == 3


def test_runtime_eval_harness_reports_mismatches_for_failed_expectations(tmp_path):
    harness_cls = getattr(runtime, "RuntimeEvalHarness", None)
    assert harness_cls is not None

    cases_dir = _copy_cases(tmp_path)
    broken_case_path = cases_dir / "basic_success.json"
    broken_case = _read_json(broken_case_path)
    broken_case["expect"]["instruction_count"] = 99
    broken_case_path.write_text(json.dumps(broken_case, ensure_ascii=False, indent=2), encoding="utf-8")

    harness = harness_cls(runtime_dir=tmp_path / "runtime", eval_dir=tmp_path / "evals")
    suite_result = harness.run_suite(cases_dir)

    assert suite_result["cases_total"] == 3
    assert suite_result["cases_passed"] == 2
    assert suite_result["cases_failed"] == 1

    failed_case = next(case_result for case_result in suite_result["results"] if case_result["case_id"] == "basic_success")
    assert failed_case["passed"] is False
    assert any(mismatch["field"] == "instruction_count" for mismatch in failed_case["mismatches"])


def test_runtime_eval_harness_cli_returns_non_zero_when_any_case_fails(tmp_path):
    harness_cls = getattr(runtime, "RuntimeEvalHarness", None)
    assert harness_cls is not None

    from src.runtime.eval_harness import main

    cases_dir = _copy_cases(tmp_path)
    broken_case_path = cases_dir / "wrapped_alignment_success.json"
    broken_case = _read_json(broken_case_path)
    broken_case["expect"]["output_alignments"] = ["left"]
    broken_case_path.write_text(json.dumps(broken_case, ensure_ascii=False, indent=2), encoding="utf-8")

    exit_code = main(
        [
            "--cases-dir",
            str(cases_dir),
            "--runtime-dir",
            str(tmp_path / "runtime"),
            "--eval-dir",
            str(tmp_path / "evals"),
        ]
    )

    assert exit_code == 1
    summaries = sorted((tmp_path / "evals").rglob("summary.json"))
    assert summaries
    summary = _read_json(summaries[-1])
    assert summary["cases_failed"] == 1
