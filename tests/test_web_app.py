# -*- coding: utf-8 -*-
"""Tests for web-app integration with the runtime harness."""

import web_app


def test_process_document_uses_runtime_harness(monkeypatch):
    called = {}
    logs = []

    class FakeResult:
        output_bytes = b"docx-bytes"
        instruction_count = 1
        error_message = None
        error_code = None

    class FakeHarness:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, **kwargs):
            called["kwargs"] = kwargs
            kwargs["event_sink"].emit({"stage": "DOCUMENT_LOADED", "paragraph_count": 2})
            kwargs["event_sink"].emit({"stage": "TEMPLATE_RESOLVED", "template_name": kwargs["template_name"]})
            kwargs["event_sink"].emit({"stage": "PROMPT_BUILT"})
            kwargs["event_sink"].emit({"stage": "AI_RESPONSE_RECEIVED"})
            return FakeResult()

    class Uploaded:
        name = "input.docx"

        def getvalue(self):
            return b"payload"

    monkeypatch.setattr(web_app, "DocumentFormatHarness", FakeHarness)
    monkeypatch.setattr(web_app, "add_log", lambda message, level="INFO": logs.append(message))
    web_app.st.session_state.language = "zh"

    result = web_app.process_document(
        Uploaded(),
        "测试模板",
        "https://example.com",
        "key",
        "demo",
        {},
    )

    assert result == b"docx-bytes"
    assert called["kwargs"]["template_name"] == "测试模板"
    assert called["kwargs"]["source_name"] == "input.docx"
    assert any("2" in message for message in logs)
    assert any("测试模板" in message for message in logs)


def test_process_document_translates_runtime_failure(monkeypatch):
    class FakeResult:
        output_bytes = None
        instruction_count = 0
        error_message = "missing url"
        error_code = web_app.RuntimeErrorCode.INVALID_API_CONFIG

    class FakeHarness:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, **kwargs):
            return FakeResult()

    class Uploaded:
        name = "input.docx"

        def getvalue(self):
            return b"payload"

    monkeypatch.setattr(web_app, "DocumentFormatHarness", FakeHarness)
    web_app.st.session_state.language = "zh"

    try:
        web_app.process_document(
            Uploaded(),
            "测试模板",
            "https://example.com",
            "key",
            "demo",
            {},
        )
    except ValueError as exc:
        assert "INVALID_API_CONFIG" not in str(exc)
        assert "missing url" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_normalize_template_rules_available_from_web_app():
    normalized = web_app.normalize_template_rules(
        {"正文": {"font": "宋体", "size": "小四", "alignment": "两端对齐"}}
    )

    assert normalized["正文"]["alignment"] == "justify"


def test_runtime_stage_progress_maps_runtime_stages_to_percentages():
    assert web_app.runtime_stage_progress("INIT") == 5
    assert web_app.runtime_stage_progress("DOCUMENT_LOADED") == 25
    assert web_app.runtime_stage_progress("PLAN_VALIDATED") == 70
    assert web_app.runtime_stage_progress("COMPLETED") == 100
    assert web_app.runtime_stage_progress("UNKNOWN") is None
