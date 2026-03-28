# -*- coding: utf-8 -*-
"""Synchronous runtime harness for document formatting."""

import json
import shutil
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from src.core.ai_connector import AIConnector
from src.core.doc_processor import DocProcessor
from src.core.format_manager import FormatManager
from src.core.header_footer_config import HeaderFooterConfig
from src.core.structure_analyzer import StructureAnalyzer
from src.runtime.contracts import (
    DocumentFormatRequest,
    DocumentFormatResult,
    RunStage,
    RunStatus,
    RuntimeErrorCode,
    StageRecord,
)
from src.runtime.events import NullEventSink
from src.runtime.run_store import RunStore
from src.runtime.template_rules import normalize_template_rules


class HarnessFailure(Exception):
    """Internal exception carrying a typed, sanitized runtime failure."""

    def __init__(self, error_code, user_message, persisted_message=None):
        super().__init__(user_message)
        self.error_code = error_code
        self.user_message = user_message
        self.persisted_message = persisted_message or user_message


class DocumentFormatHarness:
    """Thin orchestration layer over the current formatting flow."""

    def __init__(
        self,
        runtime_dir="runtime",
        format_manager=None,
        doc_processor_factory=None,
        ai_connector_factory=None,
        structure_analyzer=None,
    ):
        self.run_store = RunStore(base_dir=runtime_dir)
        self.format_manager = format_manager or FormatManager()
        self.doc_processor_factory = doc_processor_factory or DocProcessor
        self.ai_connector_factory = ai_connector_factory or AIConnector
        self.structure_analyzer = structure_analyzer or StructureAnalyzer()

    def run(
        self,
        source_name,
        source_bytes,
        template_name,
        api_config,
        header_footer_config,
        template_rules=None,
        language=None,
        event_sink=None,
    ):
        request = DocumentFormatRequest(
            source_name=source_name,
            source_bytes=source_bytes,
            template_name=template_name,
            template_rules=template_rules,
            api_config=api_config,
            header_footer_config=header_footer_config or {},
            language=language,
        )
        return self._run_request(request, event_sink=event_sink or NullEventSink())

    def _run_request(self, request, event_sink):
        run_id, run_dir, temp_dir = self.run_store.create_run_dirs()
        stage_history = []
        warnings = []
        instruction_count = 0

        def iso_now():
            return datetime.now(timezone.utc).isoformat()

        def emit(stage, status, message=None, **extra):
            record = StageRecord(
                stage=stage,
                status=status,
                started_at=iso_now(),
                ended_at=iso_now(),
                message=message,
            )
            stage_history.append(record)
            payload = {
                "timestamp": iso_now(),
                "stage": stage.value,
                "status": status.value,
                "message": message,
            }
            payload.update(extra)
            event_sink.emit(payload)
            self.run_store.append_event(run_dir, payload)

        try:
            emit(RunStage.INIT, RunStatus.RUNNING, "run initialized")
            input_path = Path(temp_dir) / "input.docx"
            input_path.write_bytes(request.source_bytes)
            emit(RunStage.INPUT_STAGED, RunStatus.RUNNING, "input staged")

            doc_processor = self.doc_processor_factory()
            if not doc_processor.read_document(str(input_path)):
                raise HarnessFailure(RuntimeErrorCode.DOCUMENT_READ_FAILED, "document read failed")
            paragraphs = doc_processor.get_document_text()
            emit(
                RunStage.DOCUMENT_LOADED,
                RunStatus.RUNNING,
                f"{len(paragraphs)} paragraphs loaded",
                paragraph_count=len(paragraphs),
            )

            if request.template_rules is not None:
                template_rules = normalize_template_rules(request.template_rules)
            else:
                template = self.format_manager.get_template(request.template_name)
                if not template:
                    raise HarnessFailure(RuntimeErrorCode.TEMPLATE_NOT_FOUND, "template not found")
                template_rules = normalize_template_rules(template.get("rules", {}))
            emit(
                RunStage.TEMPLATE_RESOLVED,
                RunStatus.RUNNING,
                request.template_name,
                template_name=request.template_name,
            )

            ai_connector = self.ai_connector_factory(request.api_config)
            valid, error_msg = ai_connector.validate_config()
            if not valid:
                raise HarnessFailure(
                    RuntimeErrorCode.INVALID_API_CONFIG,
                    self._sanitize_error_message(RuntimeErrorCode.INVALID_API_CONFIG, error_msg),
                )
            emit(RunStage.API_VALIDATED, RunStatus.RUNNING, "api validated")

            try:
                features = self.structure_analyzer.analyze_text_features(paragraphs)
                self.structure_analyzer.generate_structure_hints(features)
            except Exception as exc:
                warnings.append(str(exc))
            emit(RunStage.STRUCTURE_HINTED, RunStatus.RUNNING, "structure hints ready")

            prompt = ai_connector.generate_prompt(paragraphs, template_rules)
            Path(temp_dir, "prompt.txt").write_text(prompt, encoding="utf-8")
            emit(RunStage.PROMPT_BUILT, RunStatus.RUNNING, "prompt built")

            success, response = ai_connector.send_request(prompt)
            if not success:
                raise HarnessFailure(
                    RuntimeErrorCode.AI_REQUEST_FAILED,
                    self._sanitize_error_message(RuntimeErrorCode.AI_REQUEST_FAILED, response),
                )
            Path(temp_dir, "ai_response.json").write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
            emit(RunStage.AI_RESPONSE_RECEIVED, RunStatus.RUNNING, "response received")

            success, formatting_instructions = ai_connector.parse_response(response)
            if not success:
                raise HarnessFailure(
                    RuntimeErrorCode.AI_RESPONSE_INVALID,
                    self._sanitize_error_message(RuntimeErrorCode.AI_RESPONSE_INVALID, formatting_instructions),
                )
            _, formatting_instructions = self.structure_analyzer.validate_structure(formatting_instructions)
            Path(temp_dir, "formatting_instructions.json").write_text(
                json.dumps(formatting_instructions, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            instruction_count = len(formatting_instructions.get("elements", []))
            emit(
                RunStage.PLAN_VALIDATED,
                RunStatus.RUNNING,
                f"{instruction_count} instructions",
                instruction_count=instruction_count,
            )

            hf_config = HeaderFooterConfig.from_dict(request.header_footer_config)
            is_valid_hf, hf_error = hf_config.validate()
            if not is_valid_hf:
                raise HarnessFailure(
                    RuntimeErrorCode.HEADER_FOOTER_INVALID,
                    self._sanitize_error_message(RuntimeErrorCode.HEADER_FOOTER_INVALID, hf_error),
                )
            emit(RunStage.HEADER_FOOTER_VALIDATED, RunStatus.RUNNING, "header/footer validated")

            render_report = doc_processor.apply_formatting(
                formatting_instructions,
                custom_save_path=str(temp_dir),
                header_footer_config=hf_config,
            )
            if isinstance(render_report, bool):
                render_report = {
                    "success": render_report,
                    "total_elements": instruction_count,
                    "processed_elements": instruction_count if render_report else 0,
                    "failed_elements": [],
                    "warnings": [],
                    "backup_path": None,
                    "output_file": doc_processor.get_output_file(),
                    "header_footer": {"attempted": bool(request.header_footer_config), "success": None, "error": None},
                }
            if not render_report.get("success"):
                raise HarnessFailure(RuntimeErrorCode.FORMATTING_FAILED, "document formatting failed")
            emit(RunStage.DOCUMENT_RENDERED, RunStatus.RUNNING, "document rendered")

            output_path = doc_processor.get_output_file()
            if not output_path or not Path(output_path).exists():
                raise HarnessFailure(RuntimeErrorCode.OUTPUT_NOT_FOUND, "output file not found")
            output_bytes = Path(output_path).read_bytes()
            emit(RunStage.OUTPUT_READY, RunStatus.RUNNING, "output ready")

            self.run_store.write_manifest(
                run_dir,
                {
                    "schema_version": "formulaai.run.v1",
                    "run_id": run_id,
                    "created_at": stage_history[0].started_at if stage_history else iso_now(),
                    "completed_at": iso_now(),
                    "status": "success",
                    "entrypoint": "web_app.process_document",
                    "input": {
                        "kind": "docx",
                        "name_hash": "sha256:" + sha256(request.source_name.encode("utf-8")).hexdigest(),
                        "size_bytes": len(request.source_bytes),
                        "sha256": "sha256:" + sha256(request.source_bytes).hexdigest(),
                        "paragraph_count": len(paragraphs),
                        "char_count": sum(len(paragraph) for paragraph in paragraphs),
                    },
                    "template": {
                        "name": request.template_name,
                        "rules_count": len(template_rules),
                    },
                    "ai": {
                        "api_host": self._api_host(request.api_config.get("api_url", "")),
                        "model": request.api_config.get("model", ""),
                        "timeout_sec": request.api_config.get("timeout", 300),
                        "raw_prompt_persisted": False,
                        "raw_response_persisted": False,
                    },
                    "header_footer": {
                        "header_enabled": bool(request.header_footer_config.get("enable_header")),
                        "footer_enabled": bool(request.header_footer_config.get("enable_footer")),
                        "content_persisted": False,
                    },
                    "result": {
                        "element_count": instruction_count,
                        "output_persisted": False,
                        "output_sha256": None,
                    },
                    "warnings": warnings,
                    "error": None,
                },
            )
            emit(RunStage.COMPLETED, RunStatus.SUCCEEDED, "completed")
            return DocumentFormatResult(
                status=RunStatus.SUCCEEDED,
                final_stage=RunStage.COMPLETED,
                run_id=run_id,
                output_bytes=output_bytes,
                output_path=None,
                render_report=render_report,
                instruction_count=instruction_count,
                warnings=warnings,
                stage_history=stage_history,
            )
        except HarnessFailure as exc:
            self.run_store.write_manifest(
                run_dir,
                {
                    "schema_version": "formulaai.run.v1",
                    "run_id": run_id,
                    "created_at": stage_history[0].started_at if stage_history else iso_now(),
                    "completed_at": iso_now(),
                    "status": "failed",
                    "entrypoint": "web_app.process_document",
                    "warnings": warnings,
                    "error": {
                        "code": exc.error_code.value,
                        "message": exc.persisted_message,
                    },
                },
            )
            Path(run_dir, "failure.json").write_text(
                json.dumps(
                    {"code": exc.error_code.value, "message": exc.persisted_message},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            emit(RunStage.FAILED, RunStatus.FAILED, exc.user_message)
            return DocumentFormatResult(
                status=RunStatus.FAILED,
                final_stage=RunStage.FAILED,
                run_id=run_id,
                instruction_count=instruction_count,
                render_report=locals().get("render_report"),
                warnings=warnings,
                stage_history=stage_history,
                error_code=exc.error_code,
                error_message=exc.user_message,
            )
        except Exception:
            generic_message = "runtime internal error"
            self.run_store.write_manifest(
                run_dir,
                {
                    "schema_version": "formulaai.run.v1",
                    "run_id": run_id,
                    "created_at": stage_history[0].started_at if stage_history else iso_now(),
                    "completed_at": iso_now(),
                    "status": "failed",
                    "entrypoint": "web_app.process_document",
                    "warnings": warnings,
                    "error": {
                        "code": RuntimeErrorCode.RUNTIME_INTERNAL_ERROR.value,
                        "message": generic_message,
                    },
                },
            )
            Path(run_dir, "failure.json").write_text(
                json.dumps(
                    {
                        "code": RuntimeErrorCode.RUNTIME_INTERNAL_ERROR.value,
                        "message": generic_message,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            emit(RunStage.FAILED, RunStatus.FAILED, generic_message)
            return DocumentFormatResult(
                status=RunStatus.FAILED,
                final_stage=RunStage.FAILED,
                run_id=run_id,
                instruction_count=instruction_count,
                render_report=locals().get("render_report"),
                warnings=warnings,
                stage_history=stage_history,
                error_code=RuntimeErrorCode.RUNTIME_INTERNAL_ERROR,
                error_message=generic_message,
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _api_host(self, api_url):
        sanitized = str(api_url or "").replace("https://", "").replace("http://", "")
        return sanitized.split("/")[0]

    def _sanitize_error_message(self, error_code, message):
        text = str(message or "").strip()
        if not text:
            return error_code.value.lower()
        for marker in ("响应:", "response:", "响应内容:", "response body:"):
            marker_index = text.lower().find(marker.lower())
            if marker_index != -1:
                text = text[:marker_index].strip(" ,;:")
        return text or error_code.value.lower()
