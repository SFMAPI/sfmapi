"""No-op task — used in tests to validate the runner pipeline."""

from __future__ import annotations

import time

from app.db.models import Task
from app.workers._task_io import read_extra


def run(task: Task) -> dict:
    sleep_for = read_extra(task, "sleep_for", 0.0)
    if sleep_for:
        time.sleep(float(sleep_for))
    return {"ok": True, "task_id": task.task_id}
