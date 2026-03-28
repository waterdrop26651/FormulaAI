# Runtime Eval Harness Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an offline, replayable eval harness for FormulaAI that reuses the runtime formatting flow and emits machine-readable suite results for local runs and CI.

**Architecture:** Add a small eval layer alongside `src/runtime/` that loads frozen JSON cases, replays AI responses through the existing runtime harness, reads sanitized run manifests, and aggregates assertions into one suite report. Keep Streamlit out of the eval path and keep all cases fully offline.

**Tech Stack:** Python, pytest, python-docx, existing `src/runtime/*` and `src/core/*` modules

---

### Task 1: Lock the Eval Contract With Tests

**Files:**
- Create: `tests/test_eval_harness.py`
- Create: `evals/cases/basic_success.json`
- Create: `evals/cases/wrapped_alignment_success.json`
- Create: `evals/cases/invalid_response.json`

- [ ] **Step 1: Write the failing tests**

```python
def test_runtime_eval_harness_runs_cases_and_writes_summary(tmp_path):
    ...


def test_runtime_eval_harness_reports_mismatches_for_failed_expectations(tmp_path):
    ...


def test_runtime_eval_harness_cli_returns_non_zero_when_any_case_fails(tmp_path):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_eval_harness.py -v`
Expected: FAIL with import error or missing `RuntimeEvalHarness`

- [ ] **Step 3: Write minimal fixture cases**

Create JSON cases that cover:
- runtime success with normalized `alignment`
- wrapped JSON content parsed by `AIConnector.parse_response()`
- invalid AI response shape that should map to `AI_RESPONSE_INVALID`

- [ ] **Step 4: Run test to verify it still fails for missing implementation**

Run: `pytest tests/test_eval_harness.py -v`
Expected: FAIL because eval harness implementation does not exist yet

### Task 2: Implement the Eval Harness Core

**Files:**
- Create: `src/runtime/eval_harness.py`
- Modify: `src/runtime/__init__.py`
- Test: `tests/test_eval_harness.py`

- [ ] **Step 1: Implement case loading and replay connector**

```python
class ReplayAIConnector(AIConnector):
    ...


class RuntimeEvalHarness:
    def load_cases(self, cases_dir):
        ...
```

- [ ] **Step 2: Implement case execution and summary generation**

```python
def run_suite(self, cases_dir):
    ...
```

- [ ] **Step 3: Run targeted tests**

Run: `pytest tests/test_eval_harness.py -v`
Expected: PASS for case loading and summary assertions

- [ ] **Step 4: Refine only what tests force**

Keep the implementation limited to offline replay, summary writing, and mismatch reporting.

### Task 3: Add a CLI Entry Point and Documentation

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Test: `tests/test_eval_harness.py`

- [ ] **Step 1: Add a thin CLI wrapper**

```python
def main(argv=None):
    ...
```

- [ ] **Step 2: Expose it as an installable script**

Add:

```toml
[project.scripts]
formulaai-eval = "src.runtime.eval_harness:main"
```

- [ ] **Step 3: Document the eval command**

Document:

```bash
formulaai-eval --cases-dir evals/cases
```

- [ ] **Step 4: Run targeted tests again**

Run: `pytest tests/test_eval_harness.py -v`
Expected: PASS including CLI exit-code checks

### Task 4: Run Full Verification

**Files:**
- Verify only

- [ ] **Step 1: Run the eval command**

Run: `python3 -m src.runtime.eval_harness --cases-dir evals/cases`
Expected: exit code `1` if the intentionally failing case is included, otherwise `0`

- [ ] **Step 2: Run the full test suite**

Run: `python3 -m pytest -q`
Expected: all tests pass

- [ ] **Step 3: Inspect generated summary artifact**

Check that `runtime/evals/<suite_id>/summary.json` exists and contains machine-readable per-case results.
