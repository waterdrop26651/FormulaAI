# -*- coding: utf-8 -*-
"""Contracts for the runtime harness."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class RunStage(str, Enum):
    INIT = "INIT"
    INPUT_STAGED = "INPUT_STAGED"
    DOCUMENT_LOADED = "DOCUMENT_LOADED"
    TEMPLATE_RESOLVED = "TEMPLATE_RESOLVED"
    API_VALIDATED = "API_VALIDATED"
    STRUCTURE_HINTED = "STRUCTURE_HINTED"
    PROMPT_BUILT = "PROMPT_BUILT"
    AI_RESPONSE_RECEIVED = "AI_RESPONSE_RECEIVED"
    PLAN_VALIDATED = "PLAN_VALIDATED"
    HEADER_FOOTER_VALIDATED = "HEADER_FOOTER_VALIDATED"
    DOCUMENT_RENDERED = "DOCUMENT_RENDERED"
    OUTPUT_READY = "OUTPUT_READY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class RuntimeErrorCode(str, Enum):
    DOCUMENT_READ_FAILED = "DOCUMENT_READ_FAILED"
    TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
    INVALID_API_CONFIG = "INVALID_API_CONFIG"
    AI_REQUEST_FAILED = "AI_REQUEST_FAILED"
    AI_RESPONSE_INVALID = "AI_RESPONSE_INVALID"
    HEADER_FOOTER_INVALID = "HEADER_FOOTER_INVALID"
    FORMATTING_FAILED = "FORMATTING_FAILED"
    OUTPUT_NOT_FOUND = "OUTPUT_NOT_FOUND"
    RUNTIME_INTERNAL_ERROR = "RUNTIME_INTERNAL_ERROR"


@dataclass
class StageRecord:
    stage: RunStage
    status: RunStatus
    started_at: str
    ended_at: Optional[str] = None
    message: Optional[str] = None


@dataclass
class DocumentFormatRequest:
    source_name: str
    source_bytes: bytes
    template_name: str
    api_config: dict
    header_footer_config: dict
    language: Optional[str] = None
    template_rules: Optional[dict] = None


@dataclass
class DocumentFormatResult:
    status: RunStatus
    final_stage: RunStage
    run_id: str
    output_bytes: Optional[bytes] = None
    output_path: Optional[str] = None
    instruction_count: int = 0
    warnings: List[str] = field(default_factory=list)
    stage_history: List[StageRecord] = field(default_factory=list)
    error_code: Optional[RuntimeErrorCode] = None
    error_message: Optional[str] = None
