"""Relocalize images into an existing reconstruction."""

from __future__ import annotations

from pathlib import Path

from app.adapters.backend import require_backend_method
from app.adapters.registry import get_backend
from app.db.models import Task
from app.workers._task_io import read_state
from app.workers.tasks._registry import task_handler


@task_handler("relocalize")
def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    relocalize = require_backend_method(
        get_backend(),
        "relocalize",
        capability="relocalize.images",
    )
    return relocalize(
        model_path=Path(inputs["model_path"]),
        database_path=Path(inputs["database_path"]),
        image_root=Path(inputs["image_root"]),
        output_path=Path(inputs["output_path"]),
        image_ids=spec.get("image_ids") or [],
    )
