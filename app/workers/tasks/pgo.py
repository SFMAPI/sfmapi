"""Pose graph optimization."""

from __future__ import annotations

from pathlib import Path

from app.adapters.registry import get_backend
from app.db.models import Task
from app.storage.pose_graph_emit import emit_pose_graph_file
from app.workers._task_io import read_state


def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    out_path = Path(inputs["output_path"])
    backend = get_backend()
    result = backend.pose_graph_optimize(
        model_path=Path(inputs["model_path"]),
        output_path=out_path,
        spec=spec,
    )
    # The pose-graph sidecar is sfmapi-side post-processing — not
    # something a backend's optimize() call needs to know about. Read
    # the freshly-written model back through the backend so the emitter
    # gets a duck-typed reconstruction it can walk.
    rec = backend.read_reconstruction(out_path)
    emit_pose_graph_file(rec, out_path)
    return result
