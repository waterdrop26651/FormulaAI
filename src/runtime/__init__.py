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

def __getattr__(name):
    if name == "RuntimeEvalHarness":
        from .eval_harness import RuntimeEvalHarness

        return RuntimeEvalHarness
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "CallbackEventSink",
    "DocumentFormatRequest",
    "DocumentFormatResult",
    "NullEventSink",
    "RuntimeEvalHarness",
    "RunStage",
    "RunStatus",
    "RunStore",
    "RuntimeErrorCode",
    "StageRecord",
    "normalize_alignment",
    "normalize_template_rules",
]
