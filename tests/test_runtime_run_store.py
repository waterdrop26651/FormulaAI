# -*- coding: utf-8 -*-
"""Tests for runtime run-store persistence."""

import json
from pathlib import Path

from src.runtime.run_store import RunStore


def test_run_store_creates_manifest_and_event_log(tmp_path: Path):
    store = RunStore(base_dir=tmp_path)

    run_id, run_dir, temp_dir = store.create_run_dirs()
    store.write_manifest(run_dir, {"run_id": run_id, "status": "running"})
    store.append_event(run_dir, {"stage": "INIT", "status": "running"})

    assert run_id
    assert run_dir.exists()
    assert temp_dir.exists()
    assert json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["run_id"] == run_id
    assert (run_dir / "events.jsonl").exists()
