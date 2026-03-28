# -*- coding: utf-8 -*-
"""Runtime event sinks."""


class NullEventSink:
    """No-op sink for runtime events."""

    def emit(self, event: dict):
        """Ignore event payloads."""
        return None


class CallbackEventSink:
    """Adapter around a callable callback."""

    def __init__(self, callback):
        self.callback = callback

    def emit(self, event: dict):
        self.callback(event)
