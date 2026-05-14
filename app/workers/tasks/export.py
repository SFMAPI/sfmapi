"""Export a reconstruction to PLY / NVM / COLMAP text/binary."""

from __future__ import annotations

from pathlib import Path

from app.adapters.backend import require_backend_method
from app.db.models import Task
from app.workers._task_io import read_state
from app.workers.backend_resolver import backend_for_stage
from app.workers.tasks._registry import task_handler


@task_handler("export")
def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    fmt = spec.get("format", "ply")
    out_path = Path(inputs["output_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    backend = backend_for_stage(spec)
    export = require_backend_method(
        backend,
        "export",
        capability=f"export.{fmt}",
    )
    return export(
        model_path=Path(inputs["model_path"]),
        output_path=out_path,
        format=fmt,
    )
