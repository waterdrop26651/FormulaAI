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


def test_page_document_format_shows_download_button_immediately_after_success(monkeypatch):
    class SessionState(dict):
        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError as exc:
                raise AttributeError(name) from exc

        def __setattr__(self, name, value):
            self[name] = value

    class Context:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class Progress:
        def progress(self, value):
            return None

    class Empty:
        def text(self, value):
            return None

    class Uploaded:
        name = "input.docx"
        size = 1024

        def getvalue(self):
            return b"payload"

    class FakeStreamlit:
        def __init__(self):
            self.session_state = SessionState(
                language="zh",
                api_url="https://example.com",
                api_key="key",
                model="demo",
                uploaded_file=None,
                output_bytes=None,
                logs=[],
                header_footer_config={},
            )
            self.download_calls = []
            self.success_messages = []
            self.button_calls = 0

        def markdown(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def stop(self):
            raise AssertionError("st.stop should not be called")

        def columns(self, spec):
            count = spec if isinstance(spec, int) else len(spec)
            return [Context() for _ in range(count)]

        def subheader(self, *args, **kwargs):
            return None

        def file_uploader(self, *args, **kwargs):
            return Uploaded()

        def success(self, message, *args, **kwargs):
            self.success_messages.append(message)
            return None

        def selectbox(self, *args, **kwargs):
            return "测试模板"

        def expander(self, *args, **kwargs):
            return Context()

        def json(self, *args, **kwargs):
            return None

        def divider(self):
            return None

        def checkbox(self, *args, **kwargs):
            return False

        def text_input(self, *args, **kwargs):
            return ""

        def button(self, *args, **kwargs):
            self.button_calls += 1
            return self.button_calls == 1

        def download_button(self, **kwargs):
            self.download_calls.append(kwargs)
            return None

        def spinner(self, *args, **kwargs):
            return Context()

        def progress(self, *args, **kwargs):
            return Progress()

        def empty(self):
            return Empty()

        def error(self, *args, **kwargs):
            raise AssertionError("st.error should not be called")

        def container(self, *args, **kwargs):
            return Context()

        def text(self, *args, **kwargs):
            return None

        def rerun(self):
            raise AssertionError("st.rerun should not be required for showing the button")

    class FakeFormatManager:
        def get_template_names(self):
            return ["测试模板"]

        def get_template(self, name):
            return {"rules": {"正文": {"font": "宋体", "size": "小四", "alignment": "justify"}}}

    fake_st = FakeStreamlit()
    monkeypatch.setattr(web_app, "st", fake_st)
    monkeypatch.setattr(web_app, "FormatManager", FakeFormatManager)
    monkeypatch.setattr(web_app, "process_document", lambda *args, **kwargs: b"docx-bytes")

    web_app.page_document_format()

    assert fake_st.session_state.output_bytes == b"docx-bytes"
    assert len(fake_st.download_calls) == 1
    assert fake_st.download_calls[0]["data"] == b"docx-bytes"
