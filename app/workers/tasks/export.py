"""Export a reconstruction to PLY / NVM / COLMAP text/binary."""

from __future__ import annotations

from pathlib import Path

from app.adapters.registry import get_backend
from app.db.models import Task
from app.workers._task_io import read_state


def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    fmt = spec.get("format", "ply")
    out_path = Path(inputs["output_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return get_backend().export(
        model_path=Path(inputs["model_path"]),
        output_path=out_path,
        format=fmt,
    )
