"""Re-triangulation against an existing database."""

from __future__ import annotations

from pathlib import Path

from app.adapters.registry import get_backend
from app.db.models import Task
from app.workers._task_io import read_inputs
from app.workers.tasks._registry import task_handler


@task_handler("triangulate")
def run(task: Task) -> dict:
    inputs = read_inputs(task)
    return get_backend().triangulate(
        model_path=Path(inputs["model_path"]),
        database_path=Path(inputs["database_path"]),
        image_root=Path(inputs["image_root"]),
        output_path=Path(inputs["output_path"]),
    )
