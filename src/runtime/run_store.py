# -*- coding: utf-8 -*-
"""Persistence helpers for runtime run metadata."""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class RunStore:
    """Create run directories and persist sanitized run metadata."""

    def __init__(self, base_dir="runtime"):
        self.base_dir = Path(base_dir)

    def create_run_dirs(self):
        now = datetime.now(timezone.utc)
        run_id = f"{now.strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}"
        run_dir = (
            self.base_dir
            / "runs"
            / now.strftime("%Y")
            / now.strftime("%m")
            / now.strftime("%d")
            / run_id
        )
        temp_dir = self.base_dir / "tmp" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        temp_dir.mkdir(parents=True, exist_ok=True)
        return run_id, run_dir, temp_dir

    def write_manifest(self, run_dir, payload):
        Path(run_dir, "manifest.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def append_event(self, run_dir, payload):
        with Path(run_dir, "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
