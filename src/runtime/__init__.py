# -*- coding: utf-8 -*-
"""Runtime-layer helpers and orchestration."""

from .contracts import (
    DocumentFormatRequest,
    DocumentFormatResult,
    RunStage,
    RunStatus,
    RuntimeErrorCode,
    StageRecord,
)
from .events import CallbackEventSink, NullEventSink
from .run_store import RunStore
from .template_rules import normalize_alignment, normalize_template_rules

__all__ = [
    "CallbackEventSink",
    "DocumentFormatRequest",
    "DocumentFormatResult",
    "NullEventSink",
    "RunStage",
    "RunStatus",
    "RunStore",
    "RuntimeErrorCode",
    "StageRecord",
    "normalize_alignment",
    "normalize_template_rules",
]
