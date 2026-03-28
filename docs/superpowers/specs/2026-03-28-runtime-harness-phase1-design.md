# FormulaAI Phase 1 Runtime Harness Design

## Context

FormulaAI already has a usable AI document-formatting flow, but the runtime contract is still implicit inside [`web_app.py`](/Users/Waterdrop/FormulaAI/web_app.py). The current path stages an uploaded `.docx`, loads a template, calls the model, parses model JSON, applies formatting, and returns output bytes. What it lacks is a first-class runtime layer with explicit stage boundaries, durable run metadata, consistent failure reporting, and harness-level tests.

This design defines the first runtime harness slice only. It does not introduce background jobs, a new CLI, or a full eval system.

## Goals

- Extract the current formatting orchestration out of [`web_app.py`](/Users/Waterdrop/FormulaAI/web_app.py) into a small runtime layer under `src/`.
- Make one formatting run an explicit object with typed request, result, stage history, and run metadata.
- Preserve the current user-visible behavior of the Streamlit app.
- Add a minimal run bundle with sanitized metadata and event logs.
- Add offline tests around the real orchestration seam.

## Non-Goals

- No asynchronous worker system.
- No provider-specific optimization work.
- No full corpus-based eval harness yet.
- No default persistence of raw uploaded documents, raw prompt text, or raw model responses.
- No change to the public entrypoint: `streamlit run web_app.py`.

## Current Problems

- The main runtime contract is embedded in [`process_document()`](/Users/Waterdrop/FormulaAI/web_app.py#L825).
- Stage boundaries are implicit; progress and logs are UI-local, not runtime-native.
- Per-run artifacts are ephemeral because the flow is wrapped in `TemporaryDirectory()`.
- The current logging path can expose sensitive payloads if reused as a run record.
- [`DocProcessor.apply_formatting()`](/Users/Waterdrop/FormulaAI/src/core/doc_processor.py#L88) returns only `True/False`, which hides partial failures.
- Existing tests cover core pieces, but not the full formatting orchestration seam.

## Chosen Approach

Add a thin `src/runtime/` layer that sits between Streamlit and the existing core modules.

The runtime layer owns:

- request/result contracts
- stage tracking
- sanitized per-run metadata
- orchestration of the current document-formatting flow

The existing core layer remains responsible for:

- template loading and validation
- AI prompt generation and response parsing
- document reading and formatting
- header/footer validation and application

This keeps the Phase 1 change small and preserves current behavior, while creating the harness seam required for later evals and richer runtime governance.

## Module Layout

Add the following modules:

- `src/runtime/__init__.py`
- `src/runtime/contracts.py`
- `src/runtime/template_rules.py`
- `src/runtime/document_format_harness.py`
- `src/runtime/run_store.py`
- `src/runtime/events.py`

Responsibilities:

- `contracts.py`
  - `DocumentFormatRequest`
  - `DocumentFormatResult`
  - `RunStage`
  - `RunStatus`
  - `StageRecord`
  - `RuntimeErrorCode`
- `template_rules.py`
  - shared template-rule normalization currently embedded in [`web_app.py`](/Users/Waterdrop/FormulaAI/web_app.py#L761)
- `document_format_harness.py`
  - orchestrates one run end to end
- `run_store.py`
  - creates `run_id`
  - creates runtime directories
  - writes `manifest.json`, `events.jsonl`, and optional `failure.json`
- `events.py`
  - stage event sink interface
  - Streamlit adapter for forwarding harness events into current UI logs

## Runtime Contracts

### `DocumentFormatRequest`

Fields:

- `source_name: str`
- `source_bytes: bytes`
- `template_name: str`
- `template_rules: dict | None`
- `api_config: dict`
- `header_footer_config: dict`
- `language: str | None`

Notes:

- `template_rules` may be pre-resolved by the caller or loaded by the harness from `template_name`.
- `api_config` remains compatible with [`AIConnector`](/Users/Waterdrop/FormulaAI/src/core/ai_connector.py).

### `DocumentFormatResult`

Fields:

- `status: RunStatus`
- `final_stage: RunStage`
- `output_bytes: bytes | None`
- `output_path: str | None`
- `instruction_count: int`
- `warnings: list[str]`
- `stage_history: list[StageRecord]`
- `error_code: RuntimeErrorCode | None`
- `error_message: str | None`
- `run_id: str`

### `StageRecord`

Fields:

- `stage: RunStage`
- `status: RunStatus`
- `started_at: str`
- `ended_at: str | None`
- `message: str | None`

## Stage Machine

Phase 1 uses a synchronous, single-pass stage machine.

Stages:

1. `INIT`
2. `INPUT_STAGED`
3. `DOCUMENT_LOADED`
4. `TEMPLATE_RESOLVED`
5. `API_VALIDATED`
6. `STRUCTURE_HINTED`
7. `PROMPT_BUILT`
8. `AI_RESPONSE_RECEIVED`
9. `PLAN_VALIDATED`
10. `HEADER_FOOTER_VALIDATED`
11. `DOCUMENT_RENDERED`
12. `OUTPUT_READY`
13. `COMPLETED`
14. `FAILED`

Transition policy:

- Each run starts at `INIT`.
- Each stage can transition only to the next stage or `FAILED`.
- `FAILED` is terminal.
- `COMPLETED` is terminal.

## Execution Flow

### 1. Input staging

- Create `run_id`.
- Create ephemeral temp workspace for the run.
- Write uploaded bytes to `input.docx`.
- Initialize per-run context and stage history.

### 2. Document loading

- Use [`DocProcessor.read_document()`](/Users/Waterdrop/FormulaAI/src/core/doc_processor.py#L49).
- Extract paragraph text with [`get_document_text()`](/Users/Waterdrop/FormulaAI/src/core/doc_processor.py#L75).
- Record paragraph count in run metadata.

### 3. Template resolution

- Load template via [`FormatManager`](/Users/Waterdrop/FormulaAI/src/core/format_manager.py).
- Normalize rules through `src/runtime/template_rules.py`.
- Fail clearly if the template is missing or structurally invalid.

### 4. API validation

- Reuse [`AIConnector.validate_config()`](/Users/Waterdrop/FormulaAI/src/core/ai_connector.py#L54).
- Keep this step explicit because it is part of the current shipping behavior.
- Record only sanitized metadata from this step.

### 5. Structure hinting

- Run [`StructureAnalyzer.analyze_text_features()`](/Users/Waterdrop/FormulaAI/src/core/structure_analyzer.py#L49).
- Run [`generate_structure_hints()`](/Users/Waterdrop/FormulaAI/src/core/structure_analyzer.py#L182).
- Phase 1 policy: advisory only, non-blocking.
- If hinting fails, add a warning and continue.

Rationale:

- This creates a runtime seam for future harness-guided prompting.
- It avoids making current formatting success depend on analyzer edge cases in Phase 1.

### 6. Prompt build

- Generate prompt with [`AIConnector.generate_prompt()`](/Users/Waterdrop/FormulaAI/src/core/ai_connector.py#L108).
- Phase 1 does not persist the raw prompt into the durable run bundle.

### 7. AI call

- Send the request with [`AIConnector.send_request()`](/Users/Waterdrop/FormulaAI/src/core/ai_connector.py#L215).
- Keep raw provider response in ephemeral memory/temp space only.

### 8. Plan validation

- Parse model output with [`AIConnector.parse_response()`](/Users/Waterdrop/FormulaAI/src/core/ai_connector.py#L394).
- Validate normalized structure with [`StructureAnalyzer.validate_structure()`](/Users/Waterdrop/FormulaAI/src/core/structure_analyzer.py#L244).
- Instruction count becomes part of run metadata.

### 9. Header/footer validation

- Rebuild config from dict with [`HeaderFooterConfig.from_dict()`](/Users/Waterdrop/FormulaAI/src/core/header_footer_config.py).
- Validate with [`HeaderFooterConfig.validate()`](/Users/Waterdrop/FormulaAI/src/core/header_footer_config.py).

### 10. Document render

- Call [`DocProcessor.apply_formatting()`](/Users/Waterdrop/FormulaAI/src/core/doc_processor.py#L88).
- Read generated file from disk.
- Return bytes to the caller.

### 11. Output ready / finalize

- Load output bytes.
- Write final manifest and event log.
- Clean temp workspace.

## Runtime Storage Design

Phase 1 uses a metadata-first run bundle.

Persistent layout:

```text
runtime/
  runs/
    YYYY/
      MM/
        DD/
          <run_id>/
            manifest.json
            events.jsonl
            failure.json        # failure only
            result.docx         # optional, disabled by default
  tmp/
    <run_id>/
      input.docx
      prompt.txt
      ai_response.json
      formatting_instructions.json
      output.docx
```

Policy:

- `runtime/runs/.../<run_id>/manifest.json` is required.
- `runtime/runs/.../<run_id>/events.jsonl` is required.
- `failure.json` exists only on failure.
- `result.docx` is optional and disabled by default.
- `runtime/tmp/<run_id>/` is always deleted at finalize time.

## Manifest Schema v1

```json
{
  "schema_version": "formulaai.run.v1",
  "run_id": "20260328T101256Z_ab12cd34",
  "created_at": "2026-03-28T10:12:56Z",
  "completed_at": "2026-03-28T10:13:31Z",
  "status": "success",
  "entrypoint": "web_app.process_document",
  "input": {
    "kind": "docx",
    "name_hash": "sha256:...",
    "size_bytes": 128440,
    "sha256": "sha256:...",
    "paragraph_count": 87,
    "char_count": 12893
  },
  "template": {
    "name": "学术论文-GB规范",
    "rules_count": 12
  },
  "ai": {
    "api_host": "api.example.com",
    "model": "glm-5",
    "timeout_sec": 300,
    "raw_prompt_persisted": false,
    "raw_response_persisted": false
  },
  "header_footer": {
    "header_enabled": true,
    "footer_enabled": false,
    "content_persisted": false
  },
  "result": {
    "element_count": 91,
    "output_persisted": false,
    "output_sha256": null
  },
  "warnings": [],
  "error": null
}
```

## Redaction Rules

The run bundle must never become a second copy of user content or provider secrets.

Redact or exclude:

- `api_key`
- `Authorization`
- bearer tokens
- cookies
- uploaded filenames in plain text
- absolute temp paths
- uploaded document bytes
- extracted paragraph text
- generated prompt text
- raw provider response text
- parsed `elements[].content`
- header/footer free text
- free-text template-generation input

Persist only:

- hashes
- counts
- stage timings
- sanitized host/model metadata
- sanitized error class/message
- warning summaries

## Logging Policy

Phase 1 introduces per-run `events.jsonl` and reduces reliance on the global rotating debug log.

Persistent logs must not include:

- prompt previews
- raw request payloads
- raw response previews
- parsed JSON fragments containing user text
- full config dumps

`events.jsonl` should contain only structured stage events such as:

- run created
- document loaded
- template resolved
- API validated
- plan parsed
- document rendered
- run failed

## Integration Points

### `web_app.py`

[`process_document()`](/Users/Waterdrop/FormulaAI/web_app.py#L825) becomes a thin wrapper:

- build `DocumentFormatRequest`
- invoke `DocumentFormatHarness.run()`
- map `DocumentFormatResult` to current UI behavior
- keep the existing function signature and returned `bytes`

The Streamlit pages remain UI-only. No `streamlit` import moves into `src/runtime`.

### `src/core`

No core module is moved in Phase 1.

Reused directly:

- [`AIConnector`](/Users/Waterdrop/FormulaAI/src/core/ai_connector.py)
- [`DocProcessor`](/Users/Waterdrop/FormulaAI/src/core/doc_processor.py)
- [`FormatManager`](/Users/Waterdrop/FormulaAI/src/core/format_manager.py)
- [`HeaderFooterConfig`](/Users/Waterdrop/FormulaAI/src/core/header_footer_config.py)
- [`StructureAnalyzer`](/Users/Waterdrop/FormulaAI/src/core/structure_analyzer.py)

### Compatibility

- Keep `streamlit run web_app.py` unchanged.
- Keep `config/` and `config/templates/` unchanged.
- Keep current i18n/error-message mapping in the Streamlit layer.
- Do not change packaging/bootstrap behavior in Phase 1.

## Error Model

Introduce `RuntimeErrorCode` so the harness can return typed failures while the UI keeps translating them into localized user messages.

Initial codes:

- `DOCUMENT_READ_FAILED`
- `TEMPLATE_NOT_FOUND`
- `INVALID_API_CONFIG`
- `AI_REQUEST_FAILED`
- `AI_RESPONSE_INVALID`
- `HEADER_FOOTER_INVALID`
- `FORMATTING_FAILED`
- `OUTPUT_NOT_FOUND`
- `RUNTIME_INTERNAL_ERROR`

## Minimum Test Plan

Phase 1 tests stay fully offline under `pytest`.

Add:

- `tests/test_document_format_harness.py`
  - happy path with fake AI and real output bytes
  - missing template
  - invalid API config
  - AI request failure
  - AI parse failure
  - invalid header/footer
  - missing output file
- `tests/test_web_app.py`
  - `normalize_template_rules()` alignment normalization
  - invalid rule skipping
- `tests/test_doc_processor.py`
  - one real `.docx` round-trip asserting output file creation and key formatting facts
- extend `tests/test_ai_connector.py`
  - repaired malformed JSON
  - alignment alias normalization
  - blank config rejection

What waits for Phase 2:

- corpus-based semantic quality evals
- real provider/network behavior
- Streamlit widget-level tests
- golden-document benchmark suite

## Acceptance Criteria

Phase 1 is complete when:

- there is a `src/runtime/` layer owning the formatting orchestration
- [`web_app.py`](/Users/Waterdrop/FormulaAI/web_app.py) no longer embeds the full formatting chain directly
- runs emit `manifest.json` and `events.jsonl`
- default run persistence does not store raw document/prompt/response content
- the full Phase 1 test suite runs offline
- there is at least one offline test that starts from uploaded `.docx` bytes and ends with readable output bytes
- UI behavior remains unchanged from the user’s perspective

## Implementation Slices

1. Add `src/runtime/contracts.py` and `src/runtime/template_rules.py`.
2. Add `src/runtime/run_store.py` and `src/runtime/events.py`.
3. Implement `src/runtime/document_format_harness.py` with the current execution order.
4. Add harness tests with fakes and one real `.docx` round-trip.
5. Convert [`process_document()`](/Users/Waterdrop/FormulaAI/web_app.py#L825) into a wrapper around the harness.
6. Update README and integration docs after the implementation lands.

## Risks

- [`DocProcessor`](/Users/Waterdrop/FormulaAI/src/core/doc_processor.py) rebuilds a new document instead of preserving original layout, so the harness must not imply layout fidelity that does not exist.
- [`StructureAnalyzer`](/Users/Waterdrop/FormulaAI/src/core/structure_analyzer.py) has index-consistency risks around blank paragraphs, so Phase 1 keeps it advisory.
- Formalizing stage failures may expose cases that are currently hidden behind degraded success.
- The existing global debug logger is too permissive for use as a canonical run record.

## Follow-On Work

Phase 2 will build on this seam with:

- replayable eval fixtures
- scored regression metrics
- golden output validation
- richer prompt/version comparison
- optional debug exports under explicit user control
